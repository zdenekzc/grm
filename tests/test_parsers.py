#!/usr/bin/env python3
"""
test_parsers.py — end-to-end test of the generated Vala parsers.

For every grammar in TESTS (tests/grammar/pas.g, cmm/cmm.g):

    <grammar>.g
       │  grm/cparser.py + grm/cproduct.py (--vala, the same settings
       │  as the Grammar menu action "to Vala Parser")
       ▼
    _output/parsers/<name>_parser.vala + <name>_product.vala
       │  valac + lang/vala/textio.vala + <name>_main.vala
       ▼
    _output/parsers/<name>_test (binary)

The binary parses an example source and prints the product output
(Product.toString). Each example in tests/parsers/<name>_<case>.<ext>
has a stored expected output tests/parsers/<name>_<case>.expected;
the test runs the binary on the example and compares stdout.

The examples are the inputs verified during the Vala backend work:
small Pascal modules (program / var / const+type / strings+reals) and
C-- programs (a minimal main and quicksort.cc without the #include
lines, which the C-style lexer does not read).

Generated .vala files, binaries and run outputs land in
_output/parsers/ (gitignored); examples and .expected files are
committed. valac takes a while on the bigger grammars (tens of
seconds), that is the price of the full pipeline.

Spuštění:

    python3 tests/test_parsers.py             # tichý souhrn
    python3 tests/test_parsers.py -v          # + výpis rozdílů
    python3 tests/test_parsers.py --record    # (pře)zapisuje .expected

Without valac the test prints SKIP and exits 0 (Vala is optional).
"""

from __future__ import print_function

import os, sys, glob, subprocess, argparse, time

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

sys.path.insert (0, HERE)
from test_t_examples import _GREEN, _RED, _RESET

# ---------------------------------------------------------------------------

OUT_DIR = os.path.join (ROOT, "_output", "parsers")
SRC_DIR = os.path.join (ROOT, "tests", "parsers")
TEXTIO = os.path.join (ROOT, "lang", "vala", "textio.vala")

# pas.g nedeklaruje bázovou třídu struktur (base_name default
# CmmBasic) — hlavní program ji dostane jako stub přímo do souboru.
BASIC_STUB = """
/* stub of the structure base class (not declared in pas.g) */
public class CmmBasic
{
   public int src_file = 0;
   public int src_line = 0;
   public int src_column = 0;
}
"""

MAIN_TEMPLATE = """
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

TESTS = [
   # (jméno, cesta ke gramatice, startovací pravidlo, přípona příkladů,
   #  stub bázové třídy v mainu)
   ("pas", "tests/grammar/pas.g", "module_decl", ".pas", BASIC_STUB),
   ("cmm", "cmm/cmm.g",           "declaration_list", ".cc", ""),
]

# ---------------------------------------------------------------------------

def generate_vala (name, grammar_path) :
   """Vygeneruje <name>_parser.vala a <name>_product.vala do OUT_DIR
   (cparser/cproduct s vala = True, stejné nastavení jako menu akce
   'to Vala Parser'). Vrací (parser_path, product_path)."""

   parser_path = os.path.join (OUT_DIR, name + "_parser.vala")
   product_path = os.path.join (OUT_DIR, name + "_product.vala")

   grammar = Grammar ()
   grammar.openFile (os.path.join (ROOT, grammar_path))
   grammar.parseRules ()
   grammar.close ()

   p = CParser ()
   p.vala = True
   p.set_consts ()
   p.parser_header = name + "_parser"
   p.open (parser_path)
   p.parserVala (grammar, "")
   p.close ()
   print ("generated", os.path.relpath (parser_path, ROOT))

   q = CProduct ()
   q.vala = True
   q.set_consts ()
   q.parser_header = name + "_parser"
   q.ns = ""
   q.open (product_path)
   q.productVala (grammar)
   q.close ()
   print ("generated", os.path.relpath (product_path, ROOT))

   return parser_path, product_path


def build_binary (name, parser_path, product_path, start, basic) :
   """Složí main (se stubem bázové třídy, pokud gramatika nedeklaruje
   vlastní) a přeloží vše valacem. Vrací cestu k binárce."""

   main_path = os.path.join (OUT_DIR, name + "_main.vala")
   with open (main_path, "w") as f :
      f.write (MAIN_TEMPLATE.format (basic = basic, start = start))

   binary = os.path.join (OUT_DIR, name + "_test")
   cmd = ["valac", "-q", TEXTIO, parser_path, product_path,
          main_path, "-o", binary]
   try :
      proc = subprocess.run (cmd, capture_output = True, text = True,
                             timeout = 300, cwd = ROOT)
   except subprocess.TimeoutExpired :
      raise RuntimeError ("valac timed out (300 s)")
   if proc.returncode != 0 :
      raise RuntimeError ("valac failed:\n" + proc.stderr [-2000:])
   print ("built", os.path.relpath (binary, ROOT))
   return binary


def run_case (binary, example_path) :
   """Spustí binárku na příkladu; vrací stdout (stderr ignorujeme —
   GLib hlásí 'uncaught error' u chybných pokusů predikátů, to při
   zpětném navracení tokenu patří k chování pipeline)."""

   proc = subprocess.run ([binary, example_path], capture_output = True,
                          text = True, timeout = 30, cwd = ROOT)
   return proc.stdout

# ---------------------------------------------------------------------------

def main () :
   p = argparse.ArgumentParser (description = __doc__)
   p.add_argument ("-v", "--verbose", action = "store_true",
                   help = "print diffs of the failing cases")
   p.add_argument ("--record", action = "store_true",
                   help = "(re)write the .expected files instead of comparing")
   args = p.parse_args ()

   if subprocess.run (["which", "valac"], capture_output = True).returncode != 0 :
      print ("SKIP: valac not found")
      sys.exit (0)

   if not os.path.isdir (OUT_DIR) :
      os.makedirs (OUT_DIR)

   started = time.time ()
   ok = 0
   total = 0
   failures = [ ]

   for name, grammar_path, start, ext, basic in TESTS :
      print ("== " + name + " ==")
      try :
         parser_path, product_path = generate_vala (name, grammar_path)
         binary = build_binary (name, parser_path, product_path, start, basic)
      except RuntimeError as e :
         print (_RED + "BUILD FAIL: " + str (e) + _RESET)
         continue

      pattern = os.path.join (SRC_DIR, name + "_*" + ext)
      for example_path in sorted (glob.glob (pattern)) :
         case = os.path.splitext (os.path.basename (example_path)) [0]
         expected_path = os.path.join (SRC_DIR, case + ".expected")
         total = total + 1
         try :
            actual = run_case (binary, example_path)
         except subprocess.TimeoutExpired :
            print (_RED + "TIMEOUT    " + case + _RESET)
            failures.append (case)
            continue

         if args.record :
            with open (expected_path, "w") as f :
               f.write (actual)
            print ("recorded  ", case)
            ok = ok + 1
            continue

         if os.path.isfile (expected_path) :
            with open (expected_path) as f :
               expected = f.read ()
         else :
            print (_RED + "MISSING   " + case + " (no .expected, run --record)"
                   + _RESET)
            failures.append (case)
            continue

         if actual.rstrip ("\n") == expected.rstrip ("\n") :
            print (_GREEN + "OK         " + case + _RESET)
            ok = ok + 1
         else :
            print (_RED + "FAIL       " + case + _RESET)
            if args.verbose :
               import difflib
               diff = difflib.unified_diff (
                  expected.splitlines (True), actual.splitlines (True),
                  "expected", "actual")
               sys.stdout.writelines (diff)
            failures.append (case)

   elapsed = time.time () - started
   print ()
   summary = ("summary: " + str (ok) + "/" + str (total) +
              " ok in " + ("%.1f" % elapsed) + " s")
   if ok == total and total > 0 :
      print (_GREEN + summary + _RESET)
   else :
      print (_RED + summary + " (" + str (total - ok) + " failed)" + _RESET)
   sys.exit (total - ok)

if __name__ == "__main__" :
   main ()

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
