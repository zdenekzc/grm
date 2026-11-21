# cmm_iced.py — CLI: přelož .cc a spusť přes nativní backend.
#
# Uzávěr nad cmm_comp + backend: žádné .cpp/.py výstupy jako cmm_run.py,
# jen překlad a rovnou spuštění. Výchozí backend je iced-x86
# (cmm_generate.GenerateModule — kód do RWX paměti přes mmap); s
# --llvm se jde přes LLVM (cmm_llvm.InstructionsModule — MCJIT).
# Oba backendy ukládají artefakty do _output/generate/ resp. _output/llvm/.
#
# Volání: python3 cmm/cmm_iced.py examples/dama.cc
#         python3 cmm/cmm_iced.py --llvm examples/dama.cc

from __future__ import print_function

import os, sys, optparse

work_dir = os.path.abspath (sys.path [0])
sys.path.insert (1, os.path.join (work_dir, "..", "view")) # util
sys.path.insert (2, os.path.join (work_dir, "..", "code"))
sys.path.insert (3, os.path.join (work_dir, "..", "grm"))

cmm_dir = work_dir

options = optparse.OptionParser (usage = "usage: %prog [options] input_file")
options.add_option ("--llvm", dest = "backend", action = "store_const",
   const = "llvm", default = "iced",
   help = "run through the LLVM backend instead of iced-x86")
(opts, args) = options.parse_args ()

if len (args) == 0 :
   options.error ("Missing input file name")
if len (args) > 1 :
   options.error ("Too many input file names")

inputFileName = args [0]

# util.py si při importu parsuje sys.argv sám (zná jen -o); --llvm
# nezná, tak ho načas z argv odstraníme a po importu vrátíme.
saved_argv = sys.argv
sys.argv = [a for a in sys.argv if a != "--llvm"]

# --------------------------------------------------------------------------

import util   # PyQt5: foreign Qt třídy pro kompilátor (QVariant, ...)
sys.argv = saved_argv

foreign_modules = [sys.modules [m] for m in sys.modules
   if m.startswith ("PyQt") or m.startswith ("PySide")]

import cmm_comp, cmm_set, cmm_generate, cmm_llvm

compiler = cmm_comp.CmmCustomCompiler ()
compiler.foreign_modules = foreign_modules
compiler.extension_modules = [ sys.modules ["cmm_set"],
                               sys.modules ["cmm_generate"],
                               sys.modules ["cmm_llvm"] ]
# Stub hlavičky (stdio.h, stdlib.h, ...) pro #include v C-- zdrojácích.
compiler.addInclDir (os.path.join (cmm_dir, "include"))

compiler.openFile (inputFileName)
compiler.compile_program ()
print ("COMPILE OK")

# Vygeneruj nativní kód a spusť main (); backend uloží artefakty do
# _output/generate/ (iced) resp. _output/llvm/ (LLVM).
if opts.backend == "llvm" :
   cmm_llvm.InstructionsModule (compiler).compile ()
else :
   cmm_generate.GenerateModule (compiler).compile ()

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
