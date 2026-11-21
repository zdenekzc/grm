#!/usr/bin/env python3
"""
test_llvm.py — testy pro cmm/cmm_llvm.py (LLVM backend).

Překládá a spouští C-- programy z tests/examples/ celým kompilátorem:

    tests/examples/<name>.cc
       │
       │  cmm_parser.py (parsíř) + cmm_comp.py (sémantika)
       ▼
    sémantický strom — uzly mají item_decl, item_type, …
       │
       │  cmm_llvm.py (LLVM IR přes llvmlite, MCJIT)
       ▼
    spuštění main () — kontrola návratu i programového výstupu

Každý příklad musí doběhnout (main returned: ...) a skončit očekávaným
řádkem ("O.K.", u btree poslední vložená hodnota 800).

Při překladu vznikají v _output/llvm/ soubory <program>.ll (LLVM IR),
kopie zdrojáku <program>.cc a spustitelný <program>.bin (objekt
zlinkovaný gcc — lze spustit přímo, např. _output/llvm/dama.bin).

C-- příklady dictionary.cc, sequence.cc a strings.cc se netestují —
potřebují šablony a std::string, které C-- neumí; classes.cc se
přeloží a spustí, ale backend neumí konstruktory, takže počítá špatně.

Spuštění:

    python3 tests/test_llvm.py                # tichý souhrn
    python3 tests/test_llvm.py -v             # + IR, assembly, výstup
"""

from __future__ import print_function

import os, sys, io, ctypes, contextlib, tempfile

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
import cmm_comp, cmm_set, cmm_llvm

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

# ---------------------------------------------------------------------------
# Test runner — přeloží a spustí jeden příklad.

def run_example (name, expected_last, verbose = False) :
   """Přelož tests/examples/<name>.cc přes cmm_comp + cmm_llvm,
   spusť main () a zkontroluj návrat i poslední řádek výstupu."""
   path = os.path.join (ROOT, "tests", "examples", name + ".cc")

   compiler = cmm_comp.CmmCustomCompiler ()
   compiler.foreign_modules = [sys.modules [m] for m in sys.modules
      if m.startswith ("PyQt") or m.startswith ("PySide")]
   compiler.extension_modules = [ sys.modules ["cmm_set"],
                                  sys.modules ["cmm_llvm"] ]
   # Stub hlavičky (stdio.h, stdlib.h, ...) pro #include v C-- zdrojácích.
   compiler.addInclDir (os.path.join (ROOT, "cmm", "include"))

   buf = io.StringIO ()
   olddir = os.getcwd ()
   try :
      os.chdir (ROOT)   # backend ukládá do _output/llvm/ (gitignored)
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
               cmm_llvm.InstructionsModule (compiler).compile ()
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

   print ("Running %d examples through the LLVM backend%s ..." %
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
