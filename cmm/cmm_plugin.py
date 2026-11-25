
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

   def currentFile (self) :
       "File name of the active editor, or None with a status message."
       editor = self.win.getEditor ()
       if editor == None :
          print ("no editor open")
          return None
       return editor.getFileName ()

   def cmmCompile (self) :
       "C-- Compile menu item: compile the current .cc through env.py."
       fileName = self.currentFile ()
       if fileName != None :
          self.comp (fileName)

   def cmmBuild (self) :
       "C-- Rebuild menu item: like Compile, forces parser regeneration."
       fileName = self.currentFile ()
       if fileName != None :
          self.comp (fileName, rebuild = True)

   def cmmRun (self) :
       """C-- Run menu item: compile the current file, generate the
       Python and C++ outputs and run the Python one."""
       fileName = self.currentFile ()
       if fileName != None :
          self.comp (fileName)
          self.try_to_python ()
          self.try_to_cpp ()

   # -----------------------------------------------------------------------

   def setup (self) :
       "setup grammar, parser and compiler file name"

       # absolute: the IDE may run from any working directory
       root = os.path.dirname (os.path.dirname (os.path.abspath (__file__)))
       self.grammarFileName = os.path.join (root, "cmm", "cmm.g")

       # self.parserFileName = self.win.outputFileName ("cmm_parser.py")
       # self.productFileName = self.win.outputFileName ("cmm_product.py")

       self.basicCompilerFileName = os.path.join (root, "cmm", "cmm_comp.py")

       self.compilerFileName = self.basicCompilerFileName
       # self.compilerClassName = "CmmCompiler"
       # self.compilerClassName = "CmmQtCompiler"
       self.compilerClassName = "CmmCustomCompiler" # parameter from tools.ini
       self.compilerFuncName = "compile_program" # parameter from tools.ini

       # stub headers (stdio.h, ...) for #include in C-- sources, the
       # same directory cmm_iced.py / cmm_run.py pass to addInclDir
       self.compilerOptions = "-I " + os.path.join (root, "cmm", "include")

       self.extensionFileNames = [ os.path.join (root, "cmm", "cmm_llvm.py"),
                                    os.path.join (root, "cmm", "cmm_generate.py") ]
       # self.extensionFileNames = [ "cmm/cmm_kit.py", "cmm/cmm_set.py", "cmm/cmm_llvm.py" , "cmm/cmm_generate.py"  ]

       self.cppWriterFileName = os.path.join (root, "cmm", "c2cpp.py")
       # self.cppClassName = "ToCpp"
       # self.cppClassName = "ToQtCpp"
       self.cppClassName = "ToCustomCpp"

       self.cppSimpleClassName = "ToCpp"

       self.pythonWriterFileName = os.path.join (root, "cmm", "c2py.py")
       # self.pythonClassName = "ToPy"
       # self.pythonClassName = "ToExtPy"
       # self.pythonClassName = "ToQtPy"
       self.pythonClassName = "ToCustomPy"

       # self.pythonSimpleClassName = "ToPy"

# --------------------------------------------------------------------------

def installCmmPlugin (win) :
    """Register a top-level &C-- menu on `win` (the plugin class wraps
    code/env.py CodePlugin — parser generation plus the C-- compiler)."""
    plugin = Plugin (win)
    menu = win.addTopMenu ("&C--")

    act = QAction ("C-- &Compile", win)
    act.setShortcut ("F11")
    act.triggered.connect (plugin.cmmCompile)
    menu.addAction (act)

    act = QAction ("C-- &Run", win)
    act.setShortcut ("F12")
    act.triggered.connect (plugin.cmmRun)
    menu.addAction (act)

    return menu

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
