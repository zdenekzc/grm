#!/usr/bin/env python3
"""
test_generate.py — testy pro cmm/cmm_generate.py (iced-x86 backend).

Překládá a spouští C-- programy z tests/examples/ celým kompilátorem:

    tests/examples/<name>.cc
       │
       │  cmm_parser.py (parsíř) + cmm_comp.py (sémantika)
       ▼
    sémantický strom — uzly mají item_decl, item_type, …
       │
       │  cmm_generate.py (genezace x86_64 přes iced-x86, mmap, ctypes)
       ▼
    spuštění main () — kontrola návratu i programového výstupu

Každý příklad musí doběhnout (main returned: 0) a skončit očekávaným
řádkem ("O.K.", u btree poslední vložená hodnota 800).

Při překladu vznikají v _output/generate/ soubory <program>.asm
(dis-asm listing), kopie zdrojáku <program>.cc a spouštěč
<program>.sh (spustí příklad přes cmm/cmm_iced.py). Surový .bin se
neukládá — kód má zapecované absolutní adresy libc funkcí, samostatně
by nespustil.

C-- příklady dictionary.cc, sequence.cc a strings.cc se netestují —
potřebují šablony a std::string, které C-- neumí; classes.cc se
přeloží a spustí, ale backend neumí konstruktory, takže počítá špatně.

Spuštění:

    python3 tests/test_generate.py            # tichý souhrn
    python3 tests/test_generate.py -v         # + výstup programů
"""

from __future__ import print_function

import os, sys, io, re, ctypes, contextlib, tempfile

# ---------------------------------------------------------------------------
# Cesty: testovací soubor leží v tests/, k modulům musíme nahoru.
# grm/ musí být v sys.path PŘED code_base — repo modul, ne stdlib `code`
# (stejné pořadí jako v cmm/cmm_run.py).

HERE = os.path.dirname (os.path.abspath (__file__))
ROOT = os.path.abspath (os.path.join (HERE, ".."))
for sub in ["", "grm", "code", "view", "cmm"] :
   path = os.path.join (ROOT, sub) if sub else ROOT
   if path not in sys.path :
      sys.path.insert (0, path)

import util   # PyQt5: foreign Qt třídy pro kompilátor (QVariant, ...)
import cmm_comp, cmm_set, cmm_generate

# ---------------------------------------------------------------------------
# Testované příklady a jejich očekávaný poslední řádek výstupu.

EXAMPLES = [
   # (jméno, očekávaný poslední řádek programového výstupu)
   ("avl",       "O.K."),
   ("btree",     "800"),
   ("dama",      "O.K."),
   ("heapsort",  "O.K."),
   ("jezdec",    "O.K."),
   ("quicksort", "O.K."),
   ("veze",      "O.K."),
]

# Hlášky backendu/kompilátoru na stdout, které nejsou programovým výstupem.
NOISE = ("STRUCT ", "VARIABLE ", "FUNCTION ", "EXTERN ", "globals at ",
         "emitted ", "listing, source copy", "main returned:")

def program_lines (captured) :
   """Programový výstup = captured bez hlášek backendu a bez dis-asm
   řádků ('  00007f…: push rbp')."""
   result = [ ]
   for line in captured.splitlines () :
      if re.match (r"^\s+[0-9a-f]{16}:", line) :
         continue
      if line.startswith (NOISE) :
         continue
      result.append (line)
   return [line for line in result if line.strip ()]

# ---------------------------------------------------------------------------
# Test runner — přeloží a spustí jeden příklad.

def run_example (name, expected_last, verbose = False) :
   """Přelož tests/examples/<name>.cc přes cmm_comp + cmm_generate,
   spusť main () a zkontroluj návrat (0) i poslední řádek výstupu."""
   path = os.path.join (ROOT, "tests", "examples", name + ".cc")

   compiler = cmm_comp.CmmCustomCompiler ()
   compiler.foreign_modules = [sys.modules [m] for m in sys.modules
      if m.startswith ("PyQt") or m.startswith ("PySide")]
   compiler.extension_modules = [ sys.modules ["cmm_set"],
                                  sys.modules ["cmm_generate"] ]
   # Stub hlavičky (stdio.h, stdlib.h, ...) pro #include v C-- zdrojácích.
   compiler.addInclDir (os.path.join (ROOT, "cmm", "include"))

   buf = io.StringIO ()
   olddir = os.getcwd ()
   try :
      os.chdir (ROOT)   # backend ukládá do _output/generate/ (gitignored)
      # Programový výstup (printf nativního kódu) jde přímo na fd 1,
      # Python-level redirect_stdout ho nezachytí — přesměrujeme fd 1
      # do temp file; po běhu libc streams flushneme přes ctypes.
      with tempfile.TemporaryFile (mode = "w+") as prog_out :
         old_fd1 = os.dup (1)
         try :
            os.dup2 (prog_out.fileno (), 1)
            with contextlib.redirect_stdout (buf) :
               compiler.openFile (path)
               compiler.compile_program ()
               cmm_generate.GenerateModule (compiler).compile ()
         finally :
            # Flush libc streamů JEŠTĚ při přesměrovaném fd 1, pak vrátit.
            ctypes.CDLL (None).fflush (None)
            os.dup2 (old_fd1, 1)
            os.close (old_fd1)
         prog_out.seek (0)
         program_output = prog_out.read ()
   finally :
      os.chdir (olddir)
   captured = buf.getvalue ()

   if verbose :
      sys.stdout.write (captured)
      sys.stdout.write (program_output)

   returned = None
   for line in captured.splitlines () :
      if line.startswith ("main returned:") :
         returned = line.split (":") [1].strip ()

   lines = [line for line in program_output.splitlines () if line.strip ()]
   last = lines [-1] if lines else "(no output)"

   ok = (returned is not None) and (last == expected_last)
   marker = "PASS" if ok else "FAIL"
   print ("  [%s] %-12s main returned %s, last line %r (expected %r)"
          % (marker, name, returned, last, expected_last))
   return ok

# ---------------------------------------------------------------------------

def main () :
   verbose = "-v" in sys.argv or "--verbose" in sys.argv

   print ("Running %d examples through the iced-x86 backend%s ..." %
          (len (EXAMPLES), " (verbose)" if verbose else ""))

   passed = 0
   for name, expected_last in EXAMPLES :
      if run_example (name, expected_last, verbose) :
         passed += 1

   total = len (EXAMPLES)
   print ()
   print ("%d / %d passed" % (passed, total))
   sys.exit (0 if passed == total else 1)

if __name__ == "__main__" :
   main ()

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
