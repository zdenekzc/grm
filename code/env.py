
# env.py

from __future__ import print_function

import os, sys, copy, importlib, traceback, inspect

from util import import_qt_modules
import_qt_modules (globals ())

from util import use_pyside6, use_pyside2, use_pyqt6, use_pyqt5, use_python3, opts, find_qt_modules
from util import print_complete_traceback, findColor, findIcon

from tree import TreeItem

from input import fileNameToIndex, indexToFileName, quoteString
from output import sourceMark, pythonMark, codeMark, headerMark, parserMark, productMark

import lexer
import monitor
import code

import symbols
import grammar

import toparser
import toproduct

import cparser
import cproduct

# import pparser
# import pproduct

# --------------------------------------------------------------------------

class CodePlugin (QObject) :

   def __init__ (self, main_window) :
       super (CodePlugin, self).__init__ (main_window)
       self.win = main_window
       self.mod = self.win.current_mod

       self.grammarFileName = "" # "cmm/cmm.g"

       self.parserFileName = "" # self.win.outputFileName ("cmm_parser.py")
       self.productFileName = "" # self.win.outputFileName ("cmm_product.py")

       self.cppParserFileName = "" # self.win.outputFileName ("cmm_parser.cpp")
       self.cppProductFileName = "" # self.win.outputFileName ("cmm_product.cpp")

       self.pasParserFileName = "" # self.win.outputFileName ("cmm_parser.pas")
       self.pasProductFileName = "" # self.win.outputFileName ("cmm_product.pas")

       self.basicCompilerFileName = "" # "cmm/cmm_comp.py"

       self.compilerFileName = "" # "cmm/cmm_comp.py"
       self.compilerClassName = "" # "CmmCustomCompiler"
       self.compilerFuncName = "" # "compile_program"

       self.cppWriterFileName = "" # "cmm/c2cpp.py"
       self.cppClassName = "" # "ToCustomCpp"
       self.cppSimpleClassName = "" # "ToCpp"

       self.pythonWriterFileName = "" # "cmm/c2py.py"
       self.pythonClassName = "" # "ToCustomPy"
       self.pythonSimpleClassName = "" # "ToPy"

       self.module = "" # Python module
       self.cls = "" # class

       self.func = "" # function
       self.outputSuffix = ""
       self.addBuilder = False

       self.sourceFileName = ""
       self.sourceFileNames = [ ]

       self.enableMonitor = False
       self.compilerOptions = ""
       self.ignore_all_includes = False
       self.fast_output = False
       self.clang_import = False
       # self.example_number = 0

       self.foreign_modules = find_qt_modules ()

       self.extensionFileNames = [ ] # "cmm/cmm_set.py"

       self.attribute_modules = [ ]

       module_names = [ ]
       # module_names = [ "cmm/cmm_view.py" ]
       for name in module_names :
           module = self.win.loadModule (name)
           self.attribute_modules.append (module)

       # variables
       self.grammar_data = None
       self.parserModuleName = ""

       self.compiler_module = None
       self.compiler = None
       self.compile_ok = False
       self.compiler_data = None
       self.global_scope = None
       self.display = None

       self.cmm_generator = None
       self.cmm_simple_generator = None
       self.python_generator = None
       self.display_cnt = 0

   # -----------------------------------------------------------------------

   def setup (self) :
       "setup grammar, parser and compiler file name"
       pass

   # -----------------------------------------------------------------------

   def start (self, fileName) :
       "open new project"

       self.sourceFileName = fileName

       self.sourceEdit = self.win.inputFile (self.sourceFileName)
       self.win.initProject (self.sourceEdit)
       # self.win.info.resetCleaning ()
       # self.win.info.clearOutput ()

   # -----------------------------------------------------------------------

   def buildParser (self, rebuild = False) :
       "generate parser module and product module"

       if self.parserFileName == "" :
          self.parserFileName = self.win.outputFileName (self.grammarFileName, "_parser.py")

       if self.productFileName == "" :
          self.productFileName = self.win.outputFileName (self.grammarFileName, "_product.py")

       if ( rebuild or
            self.win.rebuildFile (self.grammarFileName, self.parserFileName) or
            self.win.rebuildFile (self.grammarFileName, self.productFileName) ) :

            # parser

            print ("generating parser")
            self.win.showStatus ("generating parser")

            grammar_data = grammar.Grammar ()
            grammar_data.openFile (self.grammarFileName)
            grammar_data.show_tree = True # report new objects to Monitor class

            parser_generator = toparser.ToParser ()
            parser_generator.open (self.parserFileName, with_simple = True, with_mark = parserMark)
            parser_generator.parserFromGrammar (grammar_data)
            parser_generator.close ()

            grammarEdit = self.win.inputFile (self.grammarFileName)
            self.win.joinProject (grammarEdit)
            self.win.addNavigatorData (grammarEdit, grammar_data)
            self.win.displayGrammarData (grammarEdit, grammar_data, grammar)

            parserEdit = self.win.reloadFile (self.parserFileName)
            self.win.joinProject (parserEdit)
            self.win.displayPythonCode (parserEdit)

            print ("parser O.K.")

            # product

            parserModuleName, ext = os.path.splitext (os.path.basename (self.parserFileName))

            product_generator = toproduct.ToProduct ()
            product_generator.open (self.productFileName, with_simple = True, with_mark = productMark)
            product_generator.productFromGrammar (grammar_data, parserModuleName)
            product_generator.close ()

            productEdit = self.win.reloadFile (self.productFileName)
            self.win.joinProject (productEdit)
            self.win.displayPythonCode (productEdit)

            print ("product O.K.")
            self.win.showStatus ("")

            self.grammar_data = grammar_data
            self.parserModuleName = parserModuleName

   # -----------------------------------------------------------------------

   def buildCParser (self, rebuild = False, lang = "") :

       if self.cppParserFileName == "" :
          self.cppParserFileName = self.win.outputFileName (self.grammarFileName, "_parser.cpp")

       if self.cppProductFileName == "" :
          self.cppProductFileName = self.win.outputFileName (self.grammarFileName, "_product.cpp")

       if ( rebuild or
            self.win.rebuildFile (self.grammarFileName, self.cppParserFileName) or
            self.win.rebuildFile (self.grammarFileName, self.cppProductFileName) ) :

            # parser

            print ("generating parser")
            self.win.showStatus ("generating parser")

            grammar_data = grammar.Grammar ()
            grammar_data.openFile (self.grammarFileName)
            # grammar_data.show_tree = True # report new objects to Monitor class

            grammar_data.parseRules ()

            name, ext = os.path.splitext (self.cppParserFileName)
            parserHeaderName = name + ".hpp"
            parserInclName = os.path.basename (parserHeaderName)

            parser_generator = cparser.CParser ()
            if  lang != "" :
                setattr (parser_generator, lang, True)
            else :
                parser_generator.cpp = True
            parser_generator.set_consts ()

            parser_generator.lexer_header = "lexer0.h"
            parser_generator.parser_header = parserInclName
            parser_generator.symbol_name = "CmmSymbol"
            parser_generator.base_name = "CmmBasic"
            parser_generator.class_name = "Parser"

            parser_generator.open (parserHeaderName, with_simple = True, with_mark = parserMark)
            parser_generator.parserHeader (grammar_data)
            parser_generator.close ()

            parser_generator.open (self.cppParserFileName, with_simple = True, with_mark = parserMark)
            parser_generator.parserCode (grammar_data)
            parser_generator.close ()

            grammarEdit = self.win.inputFile (self.grammarFileName)
            self.win.joinProject (grammarEdit)
            self.win.addNavigatorData (grammarEdit, grammar_data)
            self.win.displayGrammarData (grammarEdit, grammar_data, grammar)

            parserHeaderEdit = self.win.reloadFile (parserHeaderName)
            self.win.joinProject (parserHeaderEdit)

            parserEdit = self.win.reloadFile (self.cppParserFileName)
            self.win.joinProject (parserEdit)

            print ("Parser O.K.")

            # product

            name, ext = os.path.splitext (self.cppProductFileName)
            productHeaderName = name + ".hpp"
            productInclName = os.path.basename (productHeaderName)

            product_generator = cproduct.CProduct ()
            if  lang != "" :
                setattr (parser_generator, lang, True)
            else :
                product_generator.cpp = True
            product_generator.set_consts ()

            product_generator.parser_header = parserInclName
            product_generator.product_header = productInclName
            product_generator.class_name = "Product"

            product_generator.open (productHeaderName, with_simple = True, with_mark = productMark)
            product_generator.productHeader (grammar_data)
            product_generator.close ()

            product_generator.open (self.cppProductFileName, with_simple = True, with_mark = productMark)
            product_generator.productCode (grammar_data)
            product_generator.close ()

            productHeaderEdit = self.win.reloadFile (productHeaderName)
            self.win.joinProject (productHeaderEdit)

            productEdit = self.win.reloadFile (self.cppProductFileName)
            self.win.joinProject (productEdit)

            print ("Product O.K.")
            self.win.showStatus ("")

            self.grammar_data = grammar_data
            # self.parserModuleName = parserModuleName

   # -----------------------------------------------------------------------

   def compile (self) :
       "compiler module"

       self.win.last_python = ""
       self.win.last_cpp = ""

       # build parameters
       input = lexer.Lexer ()
       input.ignore_all_includes = True
       input.openFile (self.sourceFileName)
       input.close ()

       self.win.loadModule (self.parserFileName)
       self.win.loadModule (self.productFileName)

       if self.basicCompilerFileName != "" and self.basicCompilerFileName != self.compilerFileName :
          self.win.loadModule (self.basicCompilerFileName)

       if self.compilerFileName == "" :
          self.compilerFileName = self.parserFileName
          if self.compilerClassName == "" :
             self.compilerClassName = "Parser"

       if self.cppSimpleClassName == "" :
          self.cppSimpleClassName = self.cppClassName

       if self.pythonSimpleClassName == "" :
          self.pythonSimpleClassName = self.pythonClassName

       # if self.reuse_compiler and self.compiler != None :
       #    compiler_module = self.compiler_module
       #    compiler = self.compiler
       # else :
       compiler_module = self.win.loadModule (self.compilerFileName)
       compiler = getattr (compiler_module, self.compilerClassName)
       compiler = compiler () # create instance

       compiler.builder = self
       compiler.win = self.win
       compiler.compiler_module = compiler_module
       compiler.foreign_modules = self.foreign_modules
       compiler.attribute_modules = self.attribute_modules

       if not hasattr (compiler, "extension_modules") :
          compiler.extension_modules = [ ]
       for name in self.extensionFileNames :
          compiler.extension_modules.append (self.win.loadModule (name))

       if self.enableMonitor :
          monitor_module = self.win.loadModule ("monitor")
          compiler.monitor = monitor_module.Monitor (self.win)

       if self.compilerOptions != "" :
          compiler.readOption (self.compilerOptions)

       if self.ignore_all_includes :
          compiler.ignore_all_includes = True

       if self.clang_import :
          compiler.clang_import = True

       # print ("SOURCE FILE NAME", self.sourceFileName)
       # print ("SOURCE FILE NAMES", self.sourceFileNames)
       fileNames = []
       if self.sourceFileName != "" :
           fileNames.append (self.sourceFileName)
       for fileName in self.sourceFileNames :
           fileNames.append (fileName)
           # print ("FILENAMES", fileName)

       ok = True
       result = None
       for fileName in fileNames :
           if ok :
              print ("COMPILE", fileName)
              try :
                 if fileName != self.sourceFileName :
                    self.win.joinProject (fileName)
                 compiler.openFile (fileName, with_support = True)
                 # compiler.compile_program ()
                 func = getattr (compiler, self.compilerFuncName)
                 result = func ()
              except Exception as e:
                 # print ("COMPILE EXCEPTION")
                 print_complete_traceback ()
                 ok = False
              finally :
                 # print ("COMPILE FINALY")
                 compiler.close ()

       if not hasattr (compiler, "global_scope") :
          compiler.global_scope = result

       if not hasattr (compiler, "display") :
          compiler.display = [ ]

       self.win.showClasses (compiler.global_scope)
       if len (self.sourceFileNames) == 0 :
          self.win.addNavigatorData (self.sourceEdit, compiler.global_scope)
          self.win.displayCompilerData (self.sourceEdit, compiler.global_scope)

       self.win.showVariable ("builder", self)
       self.win.showVariable ("compiler_module", compiler_module)
       self.win.showVariable ("compiler", compiler)
       self.win.showVariable ("global_scope", compiler.global_scope)
       self.win.showVariable ("display", compiler.display)

       self.compiler_module = compiler_module
       self.compiler = compiler
       self.compile_ok = ok
       self.compiler_data = compiler.global_scope # tkit plugin
       self.global_scope = compiler.global_scope
       self.display = compiler.display

       self.win.last_scope = compiler.global_scope # !?

       if ok :
          print ("compilation O.K.")

   # -----------------------------------------------------------------------

   def create_cmm_generator (self) :
       if self.cmm_generator == None :

          tool_module = self.win.loadModule (self.cppWriterFileName)
          tool_object = getattr (tool_module, self.cppClassName)
          tool_object = tool_object () # create instance

          # tool_object.builder = self
          tool_object.compiler = self.compiler
          # tool_object.win = self.win
          # tool_object.python = False

          self.cmm_generator = tool_object

       return self.cmm_generator

   def create_cmm_simple_generator (self) :
       if self.cmm_simple_generator == None :

          tool_module = self.win.loadModule (self.cppWriterFileName)
          tool_object = getattr (tool_module, self.cppSimpleClassName)
          tool_object = tool_object () # create instance

          # tool_object.builder = self
          tool_object.compiler = self.compiler
          # tool_object.win = self.win
          # tool_object.python = False

          self.cmm_simple_generator = tool_object

       return self.cmm_simple_generator

   def create_python_generator (self) :
       if self.python_generator == None :

          tool_module = self.win.loadModule (self.pythonWriterFileName)
          tool_object = getattr (tool_module, self.pythonSimpleClassName)
          tool_object = tool_object () # create instance

          # tool_object.builder = self
          tool_object.compiler = self.compiler
          # tool_object.win = self.win
          # tool_object.python = True

          self.python_generator = tool_object

       return self.python_generator

   # -----------------------------------------------------------------------

   def to_cpp (self) :
       tool_module = self.win.loadModule (self.cppWriterFileName)
       tool_object = getattr (tool_module, self.cppClassName)
       tool_object = tool_object () # create instance

       # tool_object.builder = self
       tool_object.compiler = self.compiler
       tool_object.win = self.win # important ... outputFileName
       # tool_object.python = False

       input_data = self.global_scope

       outputSuffix = "_output.cpp"
       outputFileName = self.win.outputFileName (self.sourceFileName, outputSuffix)

       tool_object.open (outputFileName, with_sections = not self.fast_output, with_mark = codeMark)
       tool_object.foreign_modules = self.foreign_modules

       tool_object.send_program (input_data)
       tool_object.close ()

       if self.fast_output :
          self.win.loadFile (outputFileName) # output file without colors
          self.win.joinProject (outputFileName)

       self.win.loadFile (self.sourceFileName) # show tab with source

       self.win.last_cpp = outputFileName # !?

       print ("run product O.K.")


   def to_python (self) :
       tool_module = self.win.loadModule (self.pythonWriterFileName)
       tool_object = getattr (tool_module, self.pythonClassName)
       tool_object = tool_object () # create instance

       # tool_object.builder = self
       tool_object.compiler = self.compiler
       tool_object.win = self.win # important ... outputFileName
       # tool_object.python = True

       input_data = self.global_scope

       outputSuffix = "_output.py"
       outputFileName = self.win.outputFileName (self.sourceFileName, outputSuffix)

       tool_object.open (outputFileName, with_sections = not self.fast_output, with_mark = pythonMark)
       # tool_object.foreign_modules = self.foreign_modules

       tool_object.send_program (input_data)
       tool_object.close ()

       if self.fast_output :
          self.win.loadFile (outputFileName) # output file without colors
          self.win.joinProject (outputFileName)

       self.win.loadFile (self.sourceFileName) # show tab with source

       self.win.last_python = outputFileName

       print ("C++ to Python O.K.")

       self.win.runPython (outputFileName)

   def try_to_cpp (self) :
       if self.compile_ok :
          try :
             ok = False
             self.to_cpp ()
             # print ("TRY TO CPP - O.K.")
             ok = True
          except Exception as e:
             # print ("TRY TO CPP - EXCEPTION")
             print_complete_traceback ()
          self.compile_ok = ok

   def try_to_python (self) :
       if self.compile_ok :
          try :
             ok = False
             self.to_python ()
             ok = True
          except Exception as e:
             print_complete_traceback ()
          self.compile_ok = ok

   # -----------------------------------------------------------------------

   # run tool

   def toolObject (self, moduleName = "", className = "") :
       if moduleName in sys.modules :
          tool_module = sys.modules [__name__] # cmm_plugin module
       else :
          tool_module = self.win.loadModule (moduleName)

       if moduleName == "" and className == "" :
          tool_object = self # cmm_instance class
       elif className == "" :
          tool_object = tool_module
       else :
          tool_object = getattr (tool_module, className)
          # if inspect.isclass (tool_object) or inspect.isfunction (tool_object) :
          if inspect.isclass (tool_object) :
             tool_object = tool_object ()

       return tool_object


   def tool (self, input_data = None, moduleName = "", className = "", funcName = "", outputSuffix = "", msg = "", addBuilder = False) :
       "load tool module, create tool object, run tool method"

       if input_data == None :
          input_data = self.global_scope

       if funcName == "" :
          funcName = "send_program"

       if outputSuffix == "" :
          outputSuffix = "_tool_output.py"

       if msg == "" :
          msg = "O.K."

       outputFileName = self.win.outputFileName (self.sourceFileName, outputSuffix)
       # self.toolOutputFileName = outputFileName

       tool_object = self.toolObject (moduleName, className)

       if funcName == "" :
          tool_func = tool_object
       else :
          tool_func = getattr (tool_object, funcName)

       if addBuilder :
          tool_func (self)
       else :
          if hasattr (tool_object, "open") :
             tool_object.open (outputFileName, with_sections = True)
          # tool_object.foreign_modules = self.compiler.foreign_modules

          tool_func (input_data)

          if hasattr (tool_object, "close") :
             tool_object.close ()

       # file is already displayed and joined to project by open ( ..., with_sections = True )
       # do not reload, otherwise color highlighting is lost

       # outputEdit = self.win.reloadFile (outputFileName)
       # self.win.joinProject (outputEdit)
       # self.win.displayFileItem (outputFileName)

       # self.win.loadFile (self.sourceFileName) # show tab with source

       print (msg)
       return outputFileName

   # -----------------------------------------------------------------------

   def onlyParser (self, rebuild = False) :
       # self.recall ()
       self.setup ()
       self.start (self.grammarFileName)
       self.buildParser (rebuild)

   def onlyCParser (self, rebuild = False) :
       # self.recall ()
       self.setup ()
       self.start (self.grammarFileName)
       self.buildCParser (rebuild)

   def comp (self, fileName, rebuild = False) :
       # self.recall ()
       self.setup ()
       self.start (fileName)
       self.buildParser (rebuild)
       self.compile ()

   def run (self) :
       self.try_to_cpp ()
       self.try_to_python ()

   # -----------------------------------------------------------------------

   def runPluginCommand (self, desc) :

       self.setup ()

       rebuild = False
       self.start (desc.param)

       # if len (input_self.sourceFileNames) != 0 :
       #    self.sourceFileNames = input_self.sourceFileNames

       "module, cls, func, outputSuffix, addBuilder"
       self.module = desc.module
       self.cls = desc.cls
       self.func = desc.func
       self.outputSuffix = ""

       if desc.enableMonitor :
          self.enableMonitor = True

       if desc.compilerOptions != "" :
          self.compilerOptions = desc.compilerOptions + " " + desc.compilerOptions

       if desc.ignore_all_includes :
          self.ignore_all_includes = True

       if desc.fast_output :
          self.fast_output = True

       if desc.clang_import :
          self.clang_import = True

       self.win.info.disableCleaning () # keep all messages

       if getattr (self, "plugin_function", None) != None :
          self.plugin_function (self)
       else :
          self.buildParser (rebuild)

          if self.cppParserFileName != "" :
             self.buildCParser (rebuild)

          if self.pasParserFileName != "" :
             self.buildPasParser (rebuild)

          self.compile ()

          if self.pythonWriterFileName != "" and self.pythonClassName != "-" :
             self.try_to_python ()

          if self.cppWriterFileName != "" and self.cppClassName != "-" :
             self.try_to_cpp ()

       if self.compile_ok :
          if self.module != "" or self.cls != "" or self.func != "" :
             self.tool (moduleName = self.module, className = self.cls, funcName = self.func,
                        outputSuffix = self.outputSuffix, addBuilder = self.addBuilder)

       self.win.info.enableCleaning ()

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
