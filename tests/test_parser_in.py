#!/usr/bin/env python3
"""
test_parser_in.py — balíčkující verze testu generovaných parserů
(nahrazuje tests/test_parsers.py).

Pro každý jazyk vznikne v _output/ samostatný, samostatně spustitelný
balíček _output/parser_in_<jazyk>/, který obsahuje všechno, co uživatel
ke spuštění potřebuje, a může si to prohlédnout na jednom místě:

    _output/parser_in_vala/
       pas_parser.vala     vygenerovaný parser   (grm/cparser.py)
       pas_product.vala    vygenerovaný product  (grm/cproduct.py)
       pas_main.vala       main, který parser spojí s productem
       textio.vala         podpůrný zdroj (lang/vala/textio.vala)
       cmm_parser.vala     ... totéž pro druhou gramatiku ...
       pas_test.bin        přeložená binárka (přeloží i run.sh)
       data/               testovací vstupní data + .expected soubory
       run.sh              skript: sestaví vše a spustí na všech datech

Jazyky:

    vala    CParser/CProduct (vala = True) + lang/vala/textio.vala,
            binárky přes valac — plně funkční (nahrazuje test_parsers)
    python  ToParser/ToProduct (základní generátory produkují Python),
            podpůrné zdroje code/lexer.py, input.py, output.py;
            funguje pro pas.g i cmm.g (cmm_quicksort vynechán, viz
            NOTE_QUICKSORT)
    csharp  CParser/CProduct (csharp = True) + lang/csharp/textio.cs,
            binárky přes mcs/mono; funguje pro pas.g i cmm.g
            (cmm_quicksort vynechán jako u pythonu)
    cpp     CParser/CProduct (cpp = True) + lang/cpp/utils (TextInput/
            EnvInput/TextOutput) s adaptérem parser_lexer.h, g++;
            funguje pro pas.g i cmm.g (cmm_quicksort vynechán)
    java    CParser/CProduct (java = True) + lang/java/textio.java,
            javac/java; funguje pro pas.g i cmm.g (cmm_quicksort
            vynechán)
    pascal  generátor (pparser/pproduct) existuje, runtime ne:
            textio.pas má jen TTextInput/TTextOutput pro data, ne
            zdrojový lexér s nextToken/mark/rewind

Vygenerované parsery berou grammar přes stejná nastavení jako menu akce
"to Vala Parser" v IDE. Příklady (tests/parsers/<name>_<case>.<ext>)
se kopírují do data/; .expected se bere z tests/parsers/, pokud pro
daný jazyk existuje, jinak se při prvním běhu zapíše (--record vynutí
přepsání). run.sh porovnává výstup binárky s .expected bez koncových
odřádkování (stejná normalizace jako v tomto testu).

Spuštění (wrappery nastavují --lang):

    python3 tests/test_parser_in_vala.py        # vala balíček
    python3 tests/test_parser_in_python.py      # python balíček
    python3 tests/test_parser_in_csharp.py      # csharp balíček
    python3 tests/test_parser_in_cpp.py         # cpp balíček
    python3 tests/test_parser_in_java.py        # java balíček
    python3 tests/test_parser_in.py --lang all  # všechny jazyky

Bez valacu (resp. mcs/mono pro csharp, g++ pro cpp, javac/java pro java)
se balíček přeskočí (SKIP, exit 0).
"""

from __future__ import print_function

import os, sys, glob, re, subprocess, argparse, shutil

# ---------------------------------------------------------------------------
# Cesty: k modulům generátoru musí být v sys.path grm/ i code/
# (stejné pořadí jako v tests/test_generate.py).

HERE = os.path.dirname (os.path.abspath (__file__))
ROOT = os.path.abspath (os.path.join (HERE, ".."))
for sub in ["grm", "code"] :
   path = os.path.join (ROOT, sub)
   if path not in sys.path :
      sys.path.insert (0, path)
if ROOT not in sys.path :
   sys.path.insert (0, ROOT)

from grammar import Grammar
from cparser import CParser
from cproduct import CProduct
import toparser
import toproduct

sys.path.insert (0, HERE)
from test_t_examples import _GREEN, _RED, _RESET

# ---------------------------------------------------------------------------

SRC_DIR = os.path.join (ROOT, "tests", "parsers")
OUT_BASE = os.path.join (ROOT, "_output")

# pas.g nedeklaruje bázovou třídu struktur (base_name default CmmBasic) —
# hlavní program pro vala ji dostane jako stub přímo do souboru.
# (Python generátor bázovou třídu doplňuje sám, stub nepotřebuje.)

BASIC_STUB = """
/* stub of the structure base class (not declared in pas.g) */
public class CmmBasic
{
   public int src_file = 0;
   public int src_line = 0;
   public int src_column = 0;
}
"""

VALA_MAIN_TEMPLATE = """
{basic}
void main (string[] args)
{{
   var p = new Parser ();
   p.openFile (args [1]);
   p.nextToken ();
   var tree = p.parse_{start} ();
   var prod = new Product ();
   prod.send_{start} (tree);
   print ("%s", prod.toString ());
}}
"""

# C#: generated parser/product are in a namespace (the generator emits
# "namespace <ns>"), while textio.cs (Lexer, Output) is in the global
# namespace and resolves from inside ParserIn the same way.
CSHARP_NS = "ParserIn"

CSHARP_BASIC_STUB = """
public class CmmBasic
{
   public int src_file = 0;
   public int src_line = 0;
   public int src_column = 0;
}
"""

CSHARP_MAIN_TEMPLATE = """using System;
using {ns};

{basic}
class Program
{{
   static void Main (string [] args)
   {{
      Parser p = new Parser ();
      p.openFile (args [0]);
      p.nextToken ();
      var tree = p.parse_{start} ();
      Product prod = new Product ();
      prod.send_{start} (tree);
      Console.Write (prod.toString ());
   }}
}}
"""

# C++: generated parser/product use the current-API runtime from
# lang/cpp/utils (TextInput/EnvInput/TextOutput). parser_lexer.h adapts
# EnvInput for the generated parser (queued nextToken, readIdent from
# tokenKind); pas.g needs a CmmBasic stub (cmm.g declares its own).
CPP_UTILS = ["collection.h", "containers.h", "conv.cc", "conv.h",
             "dictionary.h", "envio.cc", "envio.h", "inf.cc", "inf.h",
             "ioexception.h", "msglevel.h", "parser_lexer.h", "sequence.h",
             "std.h", "str.cc", "str.h", "textio.cc", "textio.h"]

CPP_MAIN_TEMPLATE = """#include <iostream>
#include <string>

#include "{name}_parser.h"
#include "{name}_product.h"

int main (int argc, char * argv [])
{{
   if (argc < 2) return 1;
   Parser p;
   p.open (argv [1]);
   p.nextToken ();
   {ret} tree = p.parse_{start} ();
   Product prod;
   prod.send_{start} (tree);
   cout << prod.toString ();
   return 0;
}}
"""

# Java: runtime lang/java/textio.java (Lexer + Output) is in the same
# package as the generated parser; each grammar is compiled into its own
# <name>_classes directory (the generated classes are all named Parser /
# Product). pas.g needs a CmmBasic stub (cmm.g declares its own).
JAVA_NS = "parserin"

JAVA_BASIC_STUB = """
class CmmBasic
{
   public int src_file = 0;
   public int src_line = 0;
   public int src_column = 0;
}
"""

JAVA_MAIN_TEMPLATE = """package {ns};

{basic}
class Main
{{
   public static void main (String [] args)
   {{
      Parser p = new Parser ();
      p.openFile (args [0]);
      p.nextToken ();
      {ret} tree = p.parse_{start} ();
      Product prod = new Product ();
      prod.send_{start} (tree);
      System.out.print (prod.toString ());
   }}
}}
"""

# Lexer v code/lexer.py čte první token už v openFile (), proto main
# volá nextToken () až uvnitř parse_* metod — po openFile se žádný
# nextToken () nedělá (na rozdíl od vala mainu výše).
PYTHON_MAIN_TEMPLATE = """import sys

from {name}_parser import Parser
from {name}_product import Product

p = Parser ()
p.openFile (sys.argv [1])
tree = p.parse_{start} ()
prod = Product ()
prod.openString ()
prod.send_{start} (tree)
sys.stdout.write (prod.closeString ())
"""

RUN_SH_TEMPLATE = """#!/bin/sh
# run.sh — sestaví a spustí vygenerované parsery na testovacích datech.
# Balíček vytvořil tests/test_parser_in_{lang}.py; spuštění:  sh run.sh
#
# Porovnání: stdout běhu se porovná s data/<pripad>.expected
# (bez koncových odřádkování, stejná normalizace jako v testu).

cd "$(dirname "$0")" || exit 1

ok=0
fail=0
tmp=$(mktemp) || exit 1
trap 'rm -f "$tmp"' EXIT

run_case () {{ # $1 = jméno běhové funkce, $2 = data, $3 = očekávání
   out=$($1 "$2" 2>/dev/null)
   printf '%s' "$out" > "$tmp"
   if cmp -s "$tmp" "$3" ; then
      echo "OK      $(basename "$2")"
      ok=$((ok + 1))
   else
      echo "FAIL    $(basename "$2")"
      fail=$((fail + 1))
   fi
}}

{build_block}

{run_block}

echo "== run =="
{data_block}
echo
echo "summary: $ok ok, $fail fail"
test "$fail" -eq 0
"""

# ---------------------------------------------------------------------------

# Gramatiky: (jméno, cesta, startovací pravidlo, přípona příkladů,
#  vala main potřebuje stub bázové třídy)

TESTS = [
   ("pas", "tests/grammar/pas.g", "module_decl", ".pas", True),
   ("cmm", "cmm/cmm.g",           "declaration_list", ".cc", False),
]

# grammars whose structure base class (CmmBasic) is not declared in the
# grammar itself — the C++ lexer header adds the stub for them
BASIC_GRAMMAR = { name : basic for name, _, _, _, basic in TESTS }

# ---------------------------------------------------------------------------

def openGrammar (grammar_path) :
   grammar = Grammar ()
   grammar.openFile (os.path.join (ROOT, grammar_path))
   grammar.parseRules ()
   grammar.close ()
   return grammar

# ---------------------------------------------------------------------------

def generate_vala (grammar, name, out_dir) :
   parser_path = os.path.join (out_dir, name + "_parser.vala")
   product_path = os.path.join (out_dir, name + "_product.vala")

   p = CParser ()
   p.vala = True
   p.set_consts ()
   p.parser_header = name + "_parser"
   p.open (parser_path)
   p.parserVala (grammar, "")
   p.close ()

   q = CProduct ()
   q.vala = True
   q.set_consts ()
   q.parser_header = name + "_parser"
   q.ns = ""
   q.open (product_path)
   q.productVala (grammar)
   q.close ()

def generate_python (grammar, name, out_dir) :
   parser_path = os.path.join (out_dir, name + "_parser.py")
   product_path = os.path.join (out_dir, name + "_product.py")

   p = toparser.ToParser ()
   p.open (parser_path)
   p.parserFromGrammar (grammar)
   p.close ()

   q = toproduct.ToProduct ()
   q.open (product_path)
   q.productFromGrammar (grammar, name + "_parser")
   q.close ()

def generate_csharp (grammar, name, out_dir) :
   parser_path = os.path.join (out_dir, name + "_parser.cs")
   product_path = os.path.join (out_dir, name + "_product.cs")

   p = CParser ()
   p.csharp = True
   p.set_consts ()
   p.parser_header = name + "_parser"
   p.open (parser_path)
   p.parserCSharp (grammar, CSHARP_NS)
   p.close ()

   q = CProduct ()
   q.csharp = True
   q.set_consts ()
   q.parser_header = name + "_parser"
   q.ns = CSHARP_NS
   q.open (product_path)
   q.productCSharp (grammar)
   q.close ()

def generate_cpp (grammar, name, out_dir) :
   parser_h = name + "_parser.h"
   parser_cpp = name + "_parser.cpp"
   product_h = name + "_product.h"
   product_cpp = name + "_product.cpp"

   p = CParser ()
   p.cpp = True
   p.set_consts ()
   p.lexer_header = "parser_lexer.h"
   p.lexer_name = "ParserLexer"
   p.class_name = "Parser"
   p.mark_type = "InputItem *"
   p.parser_header = parser_h
   p.open (os.path.join (out_dir, parser_h))
   p.parserHeader (grammar, parser_h)
   p.close ()
   p.open (os.path.join (out_dir, parser_cpp))
   p.parserCode (grammar)
   p.close ()

   q = CProduct ()
   q.cpp = True
   q.set_consts ()
   q.class_name = "Product"
   q.super_name = "TextOutput"
   q.parser_header = parser_h
   q.product_header = product_h
   q.open (os.path.join (out_dir, product_h))
   q.productHeader (grammar, product_h)
   q.close ()
   q.open (os.path.join (out_dir, product_cpp))
   q.productCode (grammar)
   q.close ()

def generate_java (grammar, name, out_dir) :
   parser_path = os.path.join (out_dir, name + "_parser.java")
   product_path = os.path.join (out_dir, name + "_product.java")

   p = CParser ()
   p.java = True
   p.set_consts ()
   p.class_name = "Parser"
   p.open (parser_path)
   p.parserJava (grammar, JAVA_NS)
   p.close ()

   q = CProduct ()
   q.java = True
   q.set_consts ()
   q.class_name = "Product"
   q.super_name = "Output"
   q.ns = JAVA_NS
   q.open (product_path)
   q.productJava (grammar)
   q.close ()

# ---------------------------------------------------------------------------

def write_vala_main (name, start, basic, out_dir) :
   main_path = os.path.join (out_dir, name + "_main.vala")
   with open (main_path, "w") as f :
      f.write (VALA_MAIN_TEMPLATE.format (basic = basic, start = start))
   return main_path

def write_python_main (name, start, basic, out_dir) :
   main_path = os.path.join (out_dir, name + "_main.py")
   with open (main_path, "w") as f :
      f.write (PYTHON_MAIN_TEMPLATE.format (name = name, start = start))
   return main_path

def write_csharp_main (name, start, basic, out_dir) :
   main_path = os.path.join (out_dir, name + "_main.cs")
   with open (main_path, "w") as f :
      f.write (CSHARP_MAIN_TEMPLATE.format (ns = CSHARP_NS, basic = basic,
                                            start = start))
   return main_path

def write_cpp_main (name, start, basic, out_dir) :
   # return type of the start rule from the generated parser header
   header_path = os.path.join (out_dir, name + "_parser.h")
   with open (header_path) as f :
      header = f.read ()
   m = re.search (r"\n\s*([A-Za-z_][\w:<>* ]*?)\s+parse_" + start + r"\s*\(",
                  header)
   ret = m.group (1).strip () if m else "CmmBasic *"

   main_path = os.path.join (out_dir, name + "_main.cpp")
   with open (main_path, "w") as f :
      f.write (CPP_MAIN_TEMPLATE.format (name = name, start = start, ret = ret))
   return main_path

def write_java_main (name, start, basic, out_dir) :
   # return type of the start rule from the generated parser
   parser_path = os.path.join (out_dir, name + "_parser.java")
   with open (parser_path) as f :
      parser = f.read ()
   m = re.search (r"\n\s*(?:public\s+)?([A-Za-z_][\w.]*)\s+parse_" +
                  start + r"\s*\(", parser)
   ret = m.group (1) if m else "CmmBasic"

   main_path = os.path.join (out_dir, name + "_main.java")
   with open (main_path, "w") as f :
      f.write (JAVA_MAIN_TEMPLATE.format (ns = JAVA_NS, basic = basic,
                                          start = start, ret = ret))
   return main_path

# ---------------------------------------------------------------------------

def build_vala (name, out_dir) :
   """Přeloží parser + product + main valacem; binárka <name>_test.bin
   vzniká v balíčku, takže ji uživatel vidí vedle zdrojů."""

   binary = name + "_test.bin"
   cmd = ["valac", "-q", "textio.vala",
          name + "_parser.vala", name + "_product.vala", name + "_main.vala",
          "-o", binary]
   try :
      proc = subprocess.run (cmd, capture_output = True, text = True,
                             timeout = 300, cwd = out_dir)
   except subprocess.TimeoutExpired :
      raise RuntimeError ("valac timed out (300 s)")
   if proc.returncode != 0 :
      raise RuntimeError ("valac failed:\n" + proc.stderr [-2000:])
   return binary

def run_vala (out_dir, name, data_path) :
   proc = subprocess.run ([os.path.join (out_dir, name + "_test.bin"),
                           data_path], capture_output = True, text = True,
                          timeout = 30, cwd = ROOT)
   return proc.stdout

def build_csharp (name, out_dir) :
   """Přeloží parser + product + main a runtime mcs; binárka
   <name>_test.exe vzniká v balíčku vedle zdrojů."""

   binary = name + "_test.exe"
   cmd = ["mcs", "-out:" + binary, "textio.cs",
          name + "_parser.cs", name + "_product.cs", name + "_main.cs"]
   try :
      proc = subprocess.run (cmd, capture_output = True, text = True,
                             timeout = 300, cwd = out_dir)
   except subprocess.TimeoutExpired :
      raise RuntimeError ("mcs timed out (300 s)")
   if proc.returncode != 0 :
      raise RuntimeError ("mcs failed:\n" + proc.stderr [-2000:])
   return binary

def run_csharp (out_dir, name, data_path) :
   proc = subprocess.run (["mono", os.path.join (out_dir, name + "_test.exe"),
                           data_path], capture_output = True, text = True,
                          timeout = 30, cwd = ROOT)
   return proc.stdout

def build_cpp (name, out_dir) :
   """Přeloží parser + product + main a C++ runtime g++; binárka
   <name>_test.bin vzniká v balíčku vedle zdrojů."""

   binary = name + "_test.bin"
   cmd = ["g++", "-std=c++20", "-w"]
   if BASIC_GRAMMAR.get (name, False) :
      cmd.append ("-DPARSER_BASIC_STUB")
   cmd += ["-I.", name + "_parser.cpp", name + "_product.cpp",
           name + "_main.cpp", "textio.cc", "envio.cc", "str.cc", "conv.cc",
           "inf.cc", "-o", binary]
   try :
      proc = subprocess.run (cmd, capture_output = True, text = True,
                             timeout = 300, cwd = out_dir)
   except subprocess.TimeoutExpired :
      raise RuntimeError ("g++ timed out (300 s)")
   if proc.returncode != 0 :
      raise RuntimeError ("g++ failed:\n" + proc.stderr [-2000:])
   return binary

def run_cpp (out_dir, name, data_path) :
   proc = subprocess.run ([os.path.join (out_dir, name + "_test.bin"),
                           data_path], capture_output = True, text = True,
                          timeout = 30, cwd = ROOT)
   return proc.stdout

def build_java (name, out_dir) :
   """Přeloží parser + product + main + runtime do <name>_classes;
   každá gramatika má vlastní adresář, protože generované třídy se
   jmenují Parser/Product."""

   classes = name + "_classes"
   cmd = ["javac", "-d", classes, "-encoding", "UTF-8", "textio.java",
          name + "_parser.java", name + "_product.java", name + "_main.java"]
   try :
      proc = subprocess.run (cmd, capture_output = True, text = True,
                             timeout = 300, cwd = out_dir)
   except subprocess.TimeoutExpired :
      raise RuntimeError ("javac timed out (300 s)")
   if proc.returncode != 0 :
      raise RuntimeError ("javac failed:\n" + proc.stderr [-2000:])
   return classes

def run_java (out_dir, name, data_path) :
   proc = subprocess.run (["java", "-cp", os.path.join (out_dir, name + "_classes"),
                           JAVA_NS + ".Main", data_path],
                          capture_output = True, text = True,
                          timeout = 30, cwd = ROOT)
   return proc.stdout

def run_python (out_dir, name, data_path) :
   proc = subprocess.run ([sys.executable,
                           os.path.join (out_dir, name + "_main.py"),
                           data_path], capture_output = True, text = True,
                          timeout = 30, cwd = ROOT)
   return proc.stdout

# ---------------------------------------------------------------------------

# NOTE_QUICKSORT: proč se cmm_quicksort.cc v balíčcích neopakuje.
# Vygenerovaný parser má sémantické predikáty (is_expression, is_mul, ...)
# jen jako stuby (vrací False) — v reálném použití (cmm/cmm.g → C--
# compiler) je implementuje cmm_comp.CmmCustomCompiler. Příkazy typu
# `x = 1 + 2 * 3;` proto holý parser neumí rozeznat od deklarací.
# cmm_min.cc je proto úmyslně jen deklarace (parsery ho zvládnou ve
# všech jazycích); quicksort zůstává jako příklad pro vala, kde se
# degradovaný parse (GLib criticals, parse pokračuje) zaznamenal do
# .expected. Python error () místo toho vyhodí LexerException, takže
# pro python se quicksort vynechává.

NOTE_QUICKSORT = ("cmm_quicksort vynecháno: příkazy (x = 1 + 2 * 3;) "
   "potřebují reálné predikáty (is_expression, ...) — holý parser je "
   "má jen jako stuby; vala zde zachycuje degradovaný parse, python "
   "error () končí výjimkou")

LANGS = {
   "vala" : {
      "title" : "vala (cparser/cproduct, valac)",
      "dir" : "parser_in_vala",
      "ext" : "vala",
      "generate" : generate_vala,
      "write_main" : write_vala_main,
      # (zdroj v repozitáři, jméno v balíčku)
      "support" : [("lang/vala/textio.vala", "textio.vala")],
      "build" : build_vala,
      "build_cmd" : "valac -q textio.vala {name}_parser.{ext} " +
                    "{name}_product.{ext} {name}_main.{ext} " +
                    "-o {name}_test.bin",
      "run" : run_vala,
      "run_cmd" : "./{name}_test.bin",
      "cases" : {"pas" : True, "cmm" : True},
      "skip_cases" : { },
      "tools" : ["valac"],
      "basic_stub" : BASIC_STUB,
      # výstupy vala se shodují s tests/parsers/*.expected
      "inherit_expected" : True,
      "check" : None,
   },
   "python" : {
      "title" : "python (toparser/toproduct, code/lexer.py)",
      "dir" : "parser_in_python",
      "ext" : "py",
      "generate" : generate_python,
      "write_main" : write_python_main,
      "support" : [("code/lexer.py", "lexer.py"),
                   ("code/input.py", "input.py"),
                   ("code/output.py", "output.py")],
      "build" : None,
      "run" : run_python,
      "run_cmd" : "python3 {name}_main.py",
      "cases" : {"pas" : True, "cmm" : True},
      # quicksort obsahuje příkazy — viz NOTE_QUICKSORT
      "skip_cases" : {"cmm" : ("cmm_quicksort",)},
      "check" : None,
   },
   "csharp" : {
      "title" : "csharp (cparser/cproduct, mcs/mono)",
      "dir" : "parser_in_csharp",
      "ext" : "cs",
      "generate" : generate_csharp,
      "write_main" : write_csharp_main,
      "support" : [("lang/csharp/textio.cs", "textio.cs")],
      "build" : build_csharp,
      "build_cmd" : "mcs -out:{name}_test.exe textio.cs " +
                    "{name}_parser.cs {name}_product.cs {name}_main.cs",
      "run" : run_csharp,
      "run_cmd" : "mono {name}_test.exe",
      "cases" : {"pas" : True, "cmm" : True},
      # quicksort obsahuje příkazy — viz NOTE_QUICKSORT
      "skip_cases" : {"cmm" : ("cmm_quicksort",)},
      "tools" : ["mcs", "mono"],
      "basic_stub" : CSHARP_BASIC_STUB,
      # C# product (CProduct) dává stejný výstup jako vala
      "inherit_expected" : True,
      "check" : None,
   },
   "java" : {
      "title" : "java (cparser/cproduct, javac/java)",
      "dir" : "parser_in_java",
      "ext" : "java",
      "generate" : generate_java,
      "write_main" : write_java_main,
      "support" : [("lang/java/textio.java", "textio.java")],
      "build" : build_java,
      "build_cmd" : "javac -d {name}_classes -encoding UTF-8 textio.java " +
                    "{name}_parser.java {name}_product.java {name}_main.java",
      "run" : run_java,
      "run_cmd" : "java -cp {name}_classes parserin.Main",
      "cases" : {"pas" : True, "cmm" : True},
      # quicksort obsahuje příkazy — viz NOTE_QUICKSORT
      "skip_cases" : {"cmm" : ("cmm_quicksort",)},
      "tools" : ["javac", "java"],
      "basic_stub" : JAVA_BASIC_STUB,
      # Java product (CProduct) dává stejný výstup jako vala
      "inherit_expected" : True,
      "check" : None,
   },
   "pascal" : {
      "title" : "pascal (pparser/pproduct, fpc)",
      "dir" : "parser_in_pascal",
      "ext" : "pas",
      "generate" : None,
      "write_main" : None,
      "support" : [ ],
      "build" : None,
      "run" : None,
      "run_cmd" : "./{name}_test.bin",
      "cases" : {"pas" : True, "cmm" : True},
      "skip_cases" : { },
      # binio.pas už v lang/pascal/ je, ale generovaný parser extends
      # Lexer (pparser.py generuje nextToken / mark / rewind / readIdent
      # volání) — třídu Lexer v Pascalu (obdobu lang/vala/textio.vala)
      # nikdo nenapsal; textio.pas má jen TTextInput/TTextOutput
      # pro čtení/zápis dat, ne zdrojový lexér
      "check" : ("chybí runtime pro pascal: generovaný parser je "
                 "class (Lexer), ale lexér s nextToken/mark/rewind "
                 "(obdoba lang/vala/textio.vala) v lang/pascal/ není — "
                 "textio.pas má jen TTextInput/TTextOutput pro data"),
   },
   "cpp" : {
      "title" : "cpp (cparser/cproduct, g++)",
      "dir" : "parser_in_cpp",
      "ext" : "cpp",
      "generate" : generate_cpp,
      "write_main" : write_cpp_main,
      "support" : [("lang/cpp/utils/" + f, f) for f in CPP_UTILS] +
                  [("tests/grammar/pas_decl.h", "pas_decl.h")],
      "build" : build_cpp,
      "build_cmd" : "g++ -std=c++20 -w {flags} -I. " +
                    "{name}_parser.cpp {name}_product.cpp {name}_main.cpp " +
                    "textio.cc envio.cc str.cc conv.cc inf.cc " +
                    "-o {name}_test.bin",
      "run" : run_cpp,
      "run_cmd" : "./{name}_test.bin",
      "cases" : {"pas" : True, "cmm" : True},
      # quicksort obsahuje příkazy — viz NOTE_QUICKSORT
      "skip_cases" : {"cmm" : ("cmm_quicksort",)},
      "tools" : ["g++"],
      # C++ TextOutput formátuje (mezery, odsazení), takže .expected
      # se pro cpp zapisuje zvlášť, nedědí se z vala
      "check" : None,
   },
}

# ---------------------------------------------------------------------------

def build_run_sh (lang, lang_cfg, enabled, out_dir) :
   """Sestaví run.sh: build blok (build_cmd), běhové funkce a smyčku přes
   data/*.enabled — jméno gramatiky vezme z prefixu souboru."""

   ext = lang_cfg ["ext"]
   build_lines = [ ]
   run_lines = [ ]
   data_globs = [ ]

   for name, start, ext_, basic in enabled :
      if lang_cfg ["build"] != None :
         build_lines.append ("echo \"== build " + name + " ==\"")
         # hlášky kompilátoru jdou do build.log, vypíší se jen při
         # selhání — úspěšný build je tichý
         flags = "-DPARSER_BASIC_STUB" if BASIC_GRAMMAR.get (name, False) else ""
         build_cmd = lang_cfg ["build_cmd"].format (name = name, ext = ext,
                                                   flags = flags)
         build_lines.append ("if ! " + build_cmd +
            " > build.log 2>&1 ; then cat build.log ; exit 1 ; fi")
         build_lines.append ("rm -f build.log")
      run_cmd = lang_cfg ["run_cmd"].format (name = name)
      run_lines.append ("run_" + name + " () { " + run_cmd + " \"$1\" ; }")
      data_globs.append ("data/*" + ext_)

   data_block = "\n".join (
      "for data in " + glob_ + " ; do\n" +
      "   base=$(basename \"$data\")\n" +
      "   run_case \"run_${base%%_*}\" \"$data\" \"data/${base%.*}.expected\"\n" +
      "done" for glob_ in data_globs)

   text = RUN_SH_TEMPLATE.format (lang = lang,
                                  build_block = "\n".join (build_lines),
                                  run_block = "\n".join (run_lines),
                                  data_block = data_block)
   path = os.path.join (out_dir, "run.sh")
   with open (path, "w") as f :
      f.write (text)
   os.chmod (path, 0o755)
   return path

# ---------------------------------------------------------------------------

def run_language (lang, lang_cfg, verbose, record) :
   """Sestaví celý balíček pro jeden jazyk a spustí testovací příklady.
   Vrací (ok, total, failures)."""

   print ()
   print ("== " + lang + " == " + lang_cfg ["title"])

   for tool in lang_cfg.get ("tools", [ ]) :
      if subprocess.run (["which", tool], capture_output = True).returncode != 0 :
         print ("SKIP: " + tool + " not found")
         return 0, 0, [ ]

   if lang_cfg ["check"] != None :
      print ("SKIP: " + lang_cfg ["check"])
      return 0, 0, [ ]

   out_dir = os.path.join (OUT_BASE, lang_cfg ["dir"])
   if os.path.isdir (out_dir) :
      shutil.rmtree (out_dir)
   os.makedirs (out_dir)
   data_dir = os.path.join (out_dir, "data")
   os.makedirs (data_dir)

   ext = lang_cfg ["ext"]
   enabled = [ ]   # (name, start, ext_, basic) pro run.sh
   ok = 0
   total = 0
   failures = [ ]

   for name, grammar_path, start, ext_, basic in TESTS :
      if not lang_cfg ["cases"].get (name, False) :
         print ("NOTE    " + name + ": tato gramatika není pro " +
                lang + " v balíčku")
         continue
      print ("-- " + name + " --")

      grammar = openGrammar (grammar_path)
      lang_cfg ["generate"] (grammar, name, out_dir)
      print ("generated " + name + "_parser." + ext + ", " +
             name + "_product." + ext)
      lang_cfg ["write_main"] (name, start,
                               lang_cfg.get ("basic_stub", "") if basic else "",
                               out_dir)
      enabled.append ((name, start, ext_, basic))

      for src, dst in lang_cfg ["support"] :
         shutil.copyfile (os.path.join (ROOT, src),
                          os.path.join (out_dir, dst))

      pattern = os.path.join (SRC_DIR, name + "_*" + ext_)
      for example_path in sorted (glob.glob (pattern)) :
         case = os.path.splitext (os.path.basename (example_path)) [0]
         if case in lang_cfg ["skip_cases"].get (name, ()) :
            print ("NOTE    " + case + ": " + NOTE_QUICKSORT)
            continue
         shutil.copyfile (example_path,
                          os.path.join (data_dir, os.path.basename (example_path)))

         if lang_cfg ["build"] != None :
            try :
               lang_cfg ["build"] (name, out_dir)
            except RuntimeError as e :
               print (_RED + "BUILD FAIL: " + str (e) + _RESET)
               failures.append (lang + "/" + case)
               break

         total = total + 1
         try :
            actual = lang_cfg ["run"] (out_dir, name,
                                       os.path.join (data_dir, os.path.basename (example_path)))
         except subprocess.TimeoutExpired :
            print (_RED + "TIMEOUT    " + case + _RESET)
            failures.append (lang + "/" + case)
            continue

         expected_path = os.path.join (data_dir, case + ".expected")
         # .expected pro vala/csharp se dědí z tests/parsers/, pro ostatní
         # jazyky se při prvním běhu zapíše (--record vynutí přepsání)
         old_path = os.path.join (SRC_DIR, case + ".expected")
         if not os.path.isfile (expected_path) and os.path.isfile (old_path) \
            and lang_cfg.get ("inherit_expected", False) :
            shutil.copyfile (old_path, expected_path)

         if record or not os.path.isfile (expected_path) :
            with open (expected_path, "w") as f :
               f.write (actual.rstrip ("\n"))
            print ("recorded  ", case)
            ok = ok + 1
            continue

         with open (expected_path) as f :
            expected = f.read ()
         if actual.rstrip ("\n") == expected.rstrip ("\n") :
            print (_GREEN + "OK         " + case + _RESET)
            ok = ok + 1
         else :
            print (_RED + "FAIL       " + case + _RESET)
            if verbose :
               import difflib
               diff = difflib.unified_diff (
                  expected.splitlines (True), actual.splitlines (True),
                  "expected", "actual")
               sys.stdout.writelines (diff)
            failures.append (lang + "/" + case)

   if enabled :
      run_sh = build_run_sh (lang, lang_cfg, enabled, out_dir)
      print ("wrote " + os.path.relpath (run_sh, ROOT))

   print (_GREEN + "package: " + os.path.relpath (out_dir, ROOT) + _RESET)
   return ok, total, failures

# ---------------------------------------------------------------------------

def main (argv = None) :
   if argv == None :
      argv = sys.argv [1 :]

   p = argparse.ArgumentParser (description = __doc__)
   p.add_argument ("-v", "--verbose", action = "store_true",
                   help = "print diffs of the failing cases")
   p.add_argument ("--record", action = "store_true",
                   help = "(re)write the .expected files instead of comparing")
   p.add_argument ("--lang", action = "store", default = "vala",
                   help = "languages to run: vala, python, csharp, cpp, java, pascal, all")
   args = p.parse_args (argv)

   langs = sorted (LANGS.keys ()) if args.lang == "all" else [ args.lang ]
   for lang in langs :
      if lang not in LANGS :
         print (_RED + "unknown language: " + lang + _RESET)
         return 2

   started_ok = 0
   started_total = 0
   failures = [ ]
   for lang in langs :
      ok, total, lang_failures = run_language (lang, LANGS [lang],
                                               args.verbose, args.record)
      started_ok = started_ok + ok
      started_total = started_total + total
      failures = failures + lang_failures

   print ()
   summary = ("summary: " + str (started_ok) + "/" + str (started_total) +
              " ok")
   if started_ok == started_total and started_total > 0 :
      print (_GREEN + summary + _RESET)
   else :
      print (_RED + summary + " (" + str (started_total - started_ok) +
             " failed)" + _RESET)
      for f in failures :
         print ("  " + f)
   return started_total - started_ok

if __name__ == "__main__" :
   sys.exit (main ())
