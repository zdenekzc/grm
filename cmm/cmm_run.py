
# cmm_run.py

from __future__ import print_function

import os, sys, optparse

work_dir = os.path.abspath (sys.path [0])
sys.path.insert (1, os.path.join (work_dir, "..", "view")) # util
sys.path.insert (2, os.path.join (work_dir, "..", "code"))
sys.path.insert (3, os.path.join (work_dir, "..", "grm"))

cmm_dir = os.path.join (work_dir, "..", "cmm")
# The generated parser and product live directly in cmm/ and are kept in
# git (they are the backbone of the compiler).
tmp_dir = work_dir

# sys.path.insert (4, cmm_dir)
sys.path.insert (4, tmp_dir)
# print ("sys.path", sys.path)

# --------------------------------------------------------------------------

options = optparse.OptionParser (usage = "usage: %prog [options] input_file")
options.add_option ("-o", "--output", dest="output", default = "", action="store", help="Output directory")

(opts, args) = options.parse_args ()

if len (args) == 0 :
   options.error ("Missing input file name")
if len (args) > 1 :
   options.error ("Too many input file names")

inputFileName = args [0]

out_dir = opts.output
if out_dir == "" :
   out_dir = "."

# --------------------------------------------------------------------------

grammarFileName = os.path.join (cmm_dir, "cmm.g")

parserFileName = os.path.join (tmp_dir, "cmm_parser.py")
productFileName = os.path.join (tmp_dir, "cmm_product.py")

cppOutputFileName = os.path.join (out_dir, inputFileName + ".cpp") # original_file_name.original_extension.cpp
pythonOutputFileName = os.path.join (out_dir, inputFileName + ".py")

# --------------------------------------------------------------------------

def rebuildFile (source, target) :
    return not os.path.isfile (target) or os.path.getmtime (source) > os.path.getmtime (target)

if (rebuildFile (grammarFileName, parserFileName) or
    rebuildFile (grammarFileName, productFileName) ) :

   import grammar, toparser, toproduct

   grammar_data = grammar.Grammar ()
   grammar_data.openFile (grammarFileName)

   parser_generator = toparser.ToParser ()
   parser_generator.open (parserFileName)
   parser_generator.parserFromGrammar (grammar_data)
   parser_generator.close ()
   print ("Parser written to", parserFileName)

   parserModuleName, ext = os.path.splitext (os.path.basename (parserFileName))

   product_generator = toproduct.ToProduct ()
   product_generator.open (productFileName)
   product_generator.productFromGrammar (grammar_data, parserModuleName)
   product_generator.close ()
   print ("Product written to", productFileName)

# --------------------------------------------------------------------------

import util

foreign_modules = [ ]

for m in sys.modules :
   if m.startswith ("PyQt") or m.startswith ("PySide") :
      foreign_modules.append (sys.modules [m])

import cmm_comp, c2cpp, c2py, cmm_set, cmm_llvm, cmm_generate

compiler = cmm_comp.CmmCustomCompiler ()
compiler.foreign_modules = foreign_modules
compiler.extension_modules = [ sys.modules ["cmm_set"],
                               sys.modules ["cmm_llvm"],
                               sys.modules ["cmm_generate"] ]

compiler.openFile (inputFileName)
compiler.compile_program ()
compiler_data = compiler.global_scope
compiler.close ()

cpp_generator = c2cpp.ToCustomCpp ()
cpp_generator.compiler = compiler
cpp_generator.foreign_modules = compiler.foreign_modules

cpp_generator.open (cppOutputFileName)
cpp_generator.send_program (compiler_data)
cpp_generator.close ()
print ("C++ code written to", cppOutputFileName)

python_generator = c2py.ToCustomPy ()
python_generator.compiler = compiler
python_generator.foreign_modules = compiler.foreign_modules

python_generator.open (pythonOutputFileName)
python_generator.send_program (compiler_data)
python_generator.close ()
print ("Python code written to", pythonOutputFileName)

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
