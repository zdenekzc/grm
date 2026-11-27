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
    pascal  generátor (pparser/pproduct) existuje, runtime ne:
            textio.pas potřebuje unit BinIO, který v repozitáři není
    cpp     generátor (cparser/cproduct) existuje, runtime ne:
            vygenerovaný .h potřebuje lexer.h, který v repozitáři není

Vygenerované parsery berou grammar přes stejná nastavení jako menu akce
"to Vala Parser" v IDE. Příklady (tests/parsers/<name>_<case>.<ext>)
se kopírují do data/; .expected se bere z tests/parsers/, pokud pro
daný jazyk existuje, jinak se při prvním běhu zapíše (--record vynutí
přepsání). run.sh porovnává výstup binárky s .expected bez koncových
odřádkování (stejná normalizace jako v tomto testu).

Spuštění (wrappery nastavují --lang):

    python3 tests/test_parser_in_vala.py        # vala balíček
    python3 tests/test_parser_in_python.py      # python balíček
    python3 tests/test_parser_in.py --lang all  # všechny jazyky

Bez valacu se vala balíček přeskočí (SKIP, exit 0).
"""

from __future__ import print_function

import os, sys, glob, subprocess, argparse, shutil

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
      "run" : run_vala,
      "run_cmd" : "./{name}_test.bin",
      "cases" : {"pas" : True, "cmm" : True},
      "skip_cases" : { },
      # existence valacu se testuje až v main ()
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
      "generate" : None,
      "write_main" : None,
      "support" : [ ],
      "build" : None,
      "run" : None,
      "run_cmd" : "./{name}_test.bin",
      "cases" : {"pas" : True, "cmm" : True},
      "skip_cases" : { },
      # lang/cpp/lexer.h + lexer.c (C lexér s preprocesorem) už existují,
      # ale lexer.h/lexer.c potřebují externí lex.h, inp.h, out.h z
      # projektu c-parser (gitlab.fjfi.cvut.cz/culikzde/c-parser), a
      # vygenerovaný Parser : public Lexer potřebuje C++ třídu Lexer
      # (obdobu lang/vala/textio.vala) — ta v repozitáři není
      "check" : ("chybí runtime pro cpp: lang/cpp/lexer.c potřebuje "
                 "externí lex.h/inp.h/out.h (projekt c-parser) a "
                 "vygenerovaný Parser : public Lexer potřebuje C++ "
                 "třídu Lexer (obdoba lang/vala/textio.vala)"),
   },
}

# ---------------------------------------------------------------------------

def build_run_sh (lang, lang_cfg, enabled, out_dir) :
   """Sestaví run.sh: build blok (valac), běhové funkce a smyčku přes
   data/*.enabled — jméno gramatiky vezme z prefixu souboru."""

   ext = lang_cfg ["ext"]
   build_lines = [ ]
   run_lines = [ ]
   data_globs = [ ]

   for name, start, ext_, basic in enabled :
      if lang_cfg ["build"] != None :
         build_lines.append ("echo \"== build " + name + " ==\"")
         # hlášky C kompilátoru jdou do build.log, vypíší se jen při
         # selhání — úspěšný build je tichý
         build_lines.append ("if ! valac -q textio.vala " + name +
            "_parser." + ext + " " + name + "_product." + ext + " " +
            name + "_main." + ext + " -o " + name + "_test.bin " +
            "> build.log 2>&1 ; then cat build.log ; exit 1 ; fi")
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

   if lang == "vala" and \
      subprocess.run (["which", "valac"], capture_output = True).returncode != 0 :
      print ("SKIP: valac not found")
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
         print ("NOTE    " + name + ": " + NOTE_CMM_PYTHON)
         continue
      print ("-- " + name + " --")

      grammar = openGrammar (grammar_path)
      lang_cfg ["generate"] (grammar, name, out_dir)
      print ("generated " + name + "_parser." + ext + ", " +
             name + "_product." + ext)
      lang_cfg ["write_main"] (name, start,
                               BASIC_STUB if basic else "", out_dir)
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
               build_vala (name, out_dir)
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
         # .expected pro vala se dědí z tests/parsers/, pro ostatní
         # jazyky se při prvním běhu zapíše (--record vynutí přepsání)
         old_path = os.path.join (SRC_DIR, case + ".expected")
         if not os.path.isfile (expected_path) and os.path.isfile (old_path) \
            and lang == "vala" :
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
                   help = "languages to run: vala, python, pascal, cpp, all")
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
