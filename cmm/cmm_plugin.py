
# cmm_plugin.py

from __future__ import print_function

import os, sys, importlib, inspect

from util import import_qt_modules
import_qt_modules (globals ())

from util import opts
from env import CodePlugin

# --------------------------------------------------------------------------

class Plugin (CodePlugin) :

   def __init__ (self, main_window) :
       super (Plugin, self).__init__ (main_window)

       if 0 :
          menu = self.win.addTopMenu (self.mod.title)

          act = QAction ("C-- Make", self.win)
          act.setShortcut ("F11")
          act.triggered.connect (self.cmmCompile)
          menu.addAction (act)

          act = QAction ("C-- Build", self.win)
          act.setShortcut ("F12")
          act.triggered.connect (self.cmmBuild)
          menu.addAction (act)

   # -----------------------------------------------------------------------

   def cmmCompile (self) :
       "called from tools.cfg menu item"
       self.onlyParser ()

   def cmmBuild (self) :
       "called from tools.cfg menu item"
       self.onlyParser (rebuild = True)

   # -----------------------------------------------------------------------

   def setup (self) :
       "setup grammar, parser and compiler file name"

       self.grammarFileName = "cmm/cmm.g"

       # self.parserFileName = self.win.outputFileName ("cmm_parser.py")
       # self.productFileName = self.win.outputFileName ("cmm_product.py")

       self.basicCompilerFileName = "cmm/cmm_comp.py"

       self.compilerFileName = "cmm/cmm_comp.py"
       # self.compilerClassName = "CmmCompiler"
       # self.compilerClassName = "CmmQtCompiler"
       self.compilerClassName = "CmmCustomCompiler" # parameter from tools.ini
       self.compilerFuncName = "compile_program" # parameter from tools.ini

       self.extensionFileNames = [ "cmm/cmm_instr.py" , "cmm/cmm_generate.py"  ]
       # self.extensionFileNames = [ "cmm/cmm_kit.py", "cmm/cmm_set.py", "cmm/cmm_instr.py" , "cmm/cmm_generate.py"  ]

       self.cppWriterFileName = "cmm/c2cpp.py"
       # self.cppClassName = "ToCpp"
       # self.cppClassName = "ToQtCpp"
       self.cppClassName = "ToCustomCpp"

       self.cppSimpleClassName = "ToCpp"

       self.pythonWriterFileName = "cmm/c2py.py"
       # self.pythonClassName = "ToPy"
       # self.pythonClassName = "ToExtPy"
       # self.pythonClassName = "ToQtPy"
       self.pythonClassName = "ToCustomPy"

       # self.pythonSimpleClassName = "ToPy"

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
