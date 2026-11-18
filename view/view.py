#!/usr/bin/env python

from __future__ import print_function

import time
start_time = time.time ()

import sys, os, importlib

from util import *
from util import import_qt_modules
import_qt_modules (globals ())

"""
if use_pyqt5 :
   from PyQt5.QtCore import *
   from PyQt5.QtGui import *
   from PyQt5.QtWidgets import *
elif use_pyqt4 :
   from PyQt4.QtCore import *
   from PyQt4.QtGui import *
"""

# work_dir = os.getcwd ()
work_dir = os.path.abspath (sys.path [0])
module_dirs = [ "code", "grm", "cmm" ]

if use_pyqt6 :
   module_dirs.append ("highlight/highlight6")
elif use_pyqt5 :
   module_dirs.append ("highlight/highlight5")
elif use_pyqt4 :
   module_dirs.append ("highlight/highlight4")

for local_dir in module_dirs :
    if 1 :
       sys.path.insert (1, os.path.join (work_dir, local_dir)) # Debian 10, Python 2
    else :
       sys.path.insert (1, local_dir)

sys.path.insert (1, "_output")
# do not add "_output" with absolute path directory, otherwise loadModule does not work

from input import indexToFileName, fileNameToIndex


from edit import Editor, FindBox, Bookmark
from grep import GrepDialog
from options import Notes, ActionList
from settings import ConfigData, initConfig
from tools import ( refreshConfig, refreshMenu, refreshToolbar,
                    createOnePluginMenu, createPluginMenus,
                    middleMenuItems, menuItemsByExtension, MenuItem )
from tree import Tree, TreeItem, branchContinue
from window import CentralWindow, CentralApplication

import input
import output
from lexer import Lexer, readEmbeddedOptions

from input_support import Support
from output_sections import Sections
from output_simple import SimpleSections

from code_tree import GrammarTree, CompilerTree, lookupCompilerData, IdentifierTree, PythonTree

"read tools.cfg"
conf = initConfig (os.path.join (work_dir, "tools.cfg"))

"add module paths"
refreshModulePath (conf)

from llvm_tree import llvm_tree
from qt_tree import qt_tree

from design import load_ui, qt_designer, qt_designer_python_plugin, designer_window, designer_tabs

from debug import debug_with_lldb, debug_step_over, debug_step_into, debug_step_out, debug_toggle_breakpoint, debug_add_watch

# --------------------------------------------------------------------------

class ViewWindow (CentralWindow):

   def initTabWidget (self) :
       # design
       try :
          if use_area :
             self.design = GraphicsWithPalette (self)
             self.firstTabWidget.addTab (self.design, "Design")

          if use_builder :
             self.builder = BuilderWithPalette (self)
             self.firstTabWidget.addTab (self.builder, "Builder")

       except :
          pass

   def __init__ (self, parent, appl, conf) :
       super (ViewWindow, self).__init__ (parent)

       "store main window in util module"
       set_win (self)

       "application"
       self.appl = appl
       appl.win = self

       "configuration"
       self.conf = conf
       conf.win = self

       refreshColors (self.conf)
       refreshColorTables (self.conf)
       refreshIcons (self.conf)

       self.current_mod = None # extra parameter for CodePlugin

       self.owned_objects = [ ]

       self.last_python = "" # last generated python source
       self.last_cpp = "" # last generated C++ source

       self.plugin_map = { }

       self.currentProject = None
       self.currentInclude = None

       self.compiler_data = None
       self.project_files = { }

       self.grep_dialog = GrepDialog (self)

       if not use_pyside2 : # !?
          input.supportGenerator = self
       output.sectionGenerator = self

       self.initTabWidget ()
       resizeMainWindow (self)

       # project menu

       self.runMenu = self.addTopMenu ("&Project")
       self.runMenu.aboutToShow.connect (lambda: menuItemsByExtension (self, self.runMenu))
       menu = self.runMenu

       act = QAction ("Configure", self)
       act.setIcon (findIcon ("run-build-configure"))
       act.triggered.connect (self.configure)
       menu.addAction (act)

       act = QAction ("&Build", self)
       act.setIcon (findIcon ("run-build"))
       act.triggered.connect (self.build)
       menu.addAction (act)

       act = QAction ("&Make", self)
       # act.setShortcut ("F7")
       act.triggered.connect (self.make)
       menu.addAction (act)

       act = QAction ("&Run", self)
       # act.setShortcut ("F8")
       act.setIcon (findIcon ("system-run"))
       act.triggered.connect (self.run)
       menu.addAction (act)

       act = QAction ("&Debug", self)
       # act.setShortcut ("F9")
       act.setIcon (findIcon ("debug-step-into"))
       act.triggered.connect (self.debug)
       menu.addAction (act)

       act = QAction ("Install", self)
       act.setIcon (findIcon ("run-build-install"))
       act.triggered.connect (self.install)
       menu.addAction (act)

       act = QAction ("Clean", self)
       act.setIcon (findIcon ("run-build-clean"))
       act.triggered.connect (self.clean)
       menu.addAction (act)

       menu.addSeparator ()

       act = QAction ("C--", self)
       act.setIcon (findIcon ("virtualbox-vmdk"))
       act.ext = ".t"
       # act.setShortcut ("Shift+F6")
       act.setShortcut ("F9")
       act.triggered.connect (self.translate_cmm)
       menu.addAction (act)

       act = QAction ("Run Python", self)
       act.setIcon (findIcon ("text-x-python"))
       act.setShortcut ("F7")
       act.triggered.connect (self.run_python)
       menu.addAction (act)

       act = QAction ("Run C++", self)
       act.setIcon (findIcon ("text-x-c++src"))
       act.setShortcut ("F8")
       act.triggered.connect (self.run_cpp)
       menu.addAction (act)

       act = QAction ("Debug C++", self)
       act.setIcon (findIcon ("kbugbuster"))
       act.triggered.connect (self.debug_cpp)
       menu.addAction (act)

       menu.addSeparator ()

       act = QAction ("Run &Python File", self)
       act.setIcon (findIcon ("text-x-python"))
       act.setShortcut ("Shift+F7")
       act.triggered.connect (self.run_python_file)
       menu.addAction (act)

       act = QAction ("Run &C++ File", self)
       act.setIcon (findIcon ("text-x-c++src"))
       act.setShortcut ("Shift+F8")
       act.triggered.connect (self.run_cpp_file)
       menu.addAction (act)

       act = QAction ("&Debug C++ File", self)
       act.setIcon (findIcon ("kbugbuster"))
       act.setShortcut ("Shift+F9")
       act.triggered.connect (self.debug_cpp_file)
       menu.addAction (act)

       menu.addSeparator ()

       act = QAction ("&Debug with LLDB", self)
       act.setIcon (findIcon ("debug-run"))
       # act.setShortcut ("F9")
       act.triggered.connect (self.on_debug_with_lldb)
       menu.addAction (act)

       act = QAction ("Step &Over", self)
       act.setIcon (findIcon ("debug-step-over"))
       # act.setShortcut ("F10")
       act.triggered.connect (debug_step_over)
       menu.addAction (act)

       act = QAction ("Step &Into", self)
       act.setIcon (findIcon ("debug-step-into"))
       # act.setShortcut ("F11")
       act.triggered.connect (debug_step_into)
       menu.addAction (act)

       act = QAction ("Step O&ut", self)
       act.setIcon (findIcon ("debug-step-out"))
       # act.setShortcut ("F12")
       act.triggered.connect (debug_step_out)
       menu.addAction (act)

       act = QAction ("Add Breakpoint", self)
       act.setIcon (findIcon ("breakpoint"))
       act.triggered.connect (debug_toggle_breakpoint)
       menu.addAction (act)

       act = QAction ("Add Watch", self)
       act.triggered.connect (debug_add_watch)
       menu.addAction (act)

       menu.addSeparator ()

       act = QAction ("Load UI (QUiLoader or QFormBuilder)", self)
       act.setIcon (findIcon ("dialog-transform"))
       act.ext = ".ui"
       act.triggered.connect (lambda: load_ui (self, self.getEditorFileName ()))
       menu.addAction (act)

       act = QAction ("Qt Designer (C++ Plugin)", self)
       act.setIcon (findIcon ("designer-qt5"))
       act.ext = ".ui"
       act.triggered.connect (lambda: qt_designer (self, self.getEditorFileName ()))
       menu.addAction (act)

       act = QAction ("Qt Designer (Python Plugin)", self)
       act.setIcon (findIcon ("designer-qt5"))
       act.setShortcut ("Shift+F12")
       act.ext = ".ui"
       act.triggered.connect (lambda: qt_designer_python_plugin (self, self.getEditorFileName ()))
       menu.addAction (act)

       act = QAction ("Designer Window", self)
       act.setIcon (findIcon ("window-duplicate"))
       act.ext = ".ui"
       act.triggered.connect (lambda: designer_window (self, self.getEditorFileName ()))
       menu.addAction (act)

       act = QAction ("Designer Tabs", self)
       act.setIcon (findIcon ("window-duplicate"))
       act.ext = ".ui"
       act.triggered.connect (lambda: designer_tabs (self, self.getEditorFileName ()))
       menu.addAction (act)

       menu.addSeparator ()

       act = QAction ("&Grep", self)
       act.setShortcut ("F2")
       act.setIcon (findIcon ("system-search"))
       act.triggered.connect (self.findInFiles)
       menu.addAction (act)

       act = QAction ("&Stop", self)
       act.setShortcut ("Ctrl+Esc")
       act.setIcon (findIcon ("process-stop"))
       act.triggered.connect (self.info.stop)
       menu.addAction (act)

       # grammar menu

       createOnePluginMenu (self, "&Grammar", "gram_plugin", "GrammarPlugin", "gram")

       # C -- menu and additional plugins

       createPluginMenus (self)

       middleMenuItems (conf) # add menu items

       # settings menu

       self.settingsMenu = self.addTopMenu ("&Settings")
       menu = self.settingsMenu

       menu.addSeparator ()

       act = QAction ("&Notes ...", self)
       act.triggered.connect (self.showNotesDialog)
       act.setIcon (findIcon ("redhat-accessories"))
       act.setShortcut ("F1")
       menu.addAction (act)

       # window and tabs menu

       self.additionalMenuItems ()

       # tools menu

       self.toolsMenu = self.addTopMenu ("&Tools")
       self.toolsMenu.aboutToShow.connect (lambda: menuItemsByExtension (self, self.toolsMenu))

       # help menu

       self.helpMenu = self.addTopMenu ("&Help")
       self.helpMenu.aboutToShow.connect (lambda: menuItemsByExtension (self, self.helpMenu))

       refreshMenu (self.conf) # add menu items

       # additional toolbar buttons and shortcuts

       ActionList (self) # process shortcuts

       refreshToolbar (self.conf) # add toolbar buttons

       # status bar

       exe = sys.executable
       if sys.dont_write_bytecode :
          exe = exe + " -B"
       ver = sys.version_info
       inf = str (ver[0]) + "." + str (ver[1]) + "." + str (ver[2])
       self.showStatus (exe + ", Python " + inf + ", Qt " + qVersion ())

   # Project menu

   def configure (self) :
       self.info.runCommandByName ("configure")

   def build (self) :
       self.info.runCommandByName ("build")

   def make (self) :
       self.info.runCommandByName ("make")

   def run (self) :
       self.info.runCommandByName ("run")

   def debug (self) :
       self.info.runCommandByName ("debug")

   def clean (self) :
       self.info.runCommandByName ("clean")

   def install (self) :
       self.info.runCommandByName ("install")

   def findInFiles (self) :
       self.showTab (self.grep)
       self.grep_dialog.openDialog (self.getEditor ())

   def translate_cmm (self) :
       editor = self.getEditor ()
       if self.hasExtension (editor, ".t") :
          self.checkModifiedOnDisk (editor)
          self.info.clearOutput ()

          desc = MenuItem ()
          desc.plugin = "cmm"
          desc.param = editor.getFileName ()
          self.info.runCommandObject (desc)

   def run_python (self) :
       fileName = self.last_python
       if fileName != "" :
          editor = self.getEditor ()
          if editor != None :
             self.checkModifiedOnDisk (editor)
          self.info.clearOutput ()
          self.info.runCommandByName ("run-python", fileName)

   def run_cpp (self) :
       fileName = self.last_cpp
       if fileName != "" :
          editor = self.getEditor ()
          if editor != None :
             self.checkModifiedOnDisk (editor)
          self.info.clearOutput ()
          options = readEmbeddedOptions (fileName)

          if options.startswith ("-") :
             self.precompile_header ()
             self.info.runCommandByName ("run-cpp", fileName + " " + options)
          else :
             os.system (options)

   def debug_cpp (self) :
       fileName = self.last_cpp
       if fileName != "" :
          editor = self.getEditor ()
          if editor != None :
             self.checkModifiedOnDisk (editor)
          self.info.clearOutput ()
          options = readEmbeddedOptions (fileName)
          self.info.runCommandByName ("debug-cpp", fileName + " " + options)

   def run_python_file (self) :
       editor = self.getEditor ()
       if editor != None :
          self.checkModifiedOnDisk (editor)
          self.info.clearOutput ()
          self.info.runCommandByName ("run-python")

   def run_cpp_file (self) :
       editor = self.getEditor ()
       if editor != None :
          self.checkModifiedOnDisk (editor)
          self.info.clearOutput ()
          fileName = editor.getFileName ()
          options = readEmbeddedOptions (fileName)
          if options.startswith ("-") :
             self.info.runCommandByName ("run-cpp", fileName + " " + options)
          else :
             os.system (options)

   def debug_cpp_file (self) :
       editor = self.getEditor ()
       if editor != None :
          self.checkModifiedOnDisk (editor)
          self.info.clearOutput ()
          fileName = editor.getFileName ()
          options = readEmbeddedOptions (fileName)
          self.info.runCommandByName ("debug-cpp", fileName + " " + options)

   # LLDB

   def on_debug_with_lldb (self) :
       fileName = "_output/run.bin"
       debug_with_lldb (win, fileName)

   # Qt module

   def on_qt_tree (self) :
       qt_tree (self)

   # Clang

   def on_llvm_tree (self) :
       # fileName = "plain/simple.cc"
       fileName = "plain/simple-qt.cc"
       # fileName = "examples/read/example.cc"
       llvm_tree (self, fileName)

   # Settings menu

   def showNotesDialog (self) :
       Notes (self).show ()

   # Properties

   def showProperties (self, data) :
       self.prop.showProperties (data)
       self.showTab (self.prop)

   # Project

   def initProject (self, prj) :
       # unloadModules ()
       self.info.resetCleaning ()
       self.info.clearOutput ()
       self.classes.clear ()
       self.tree.clear ()
       self.variables.clear ()
       self.input.clear ()
       self.project_files = { }
       for edit in self.editors.values () :
           self.navigator.releaseNavigator (edit)
       if isinstance (prj, Editor) :
          fileName = prj.getFileName ()
          text = os.path.basename (fileName)
          node = TreeItem (self.project, text)
          node.setToolTip (0, fileName)
          node.setIcon (0, findIcon ("folder"))
          node.src_file = fileNameToIndex (fileName)
          node.obj = prj
       elif isinstance (prj, str) :
          node = TreeItem (self.project, prj)
          node.setIcon (0, findIcon ("folder"))
          node.src_file = fileNameToIndex (prj)
       else :
          node = None # !?
       self.currentProject = node
       self.currentInclude = node
       return node

   def joinProject (self, param) :
       if isinstance (param, str) :
          fileName = param
          edit = None
       else :
          edit = param
          fileName = edit.getFileName ()
       if fileName in self.project_files :
          node = self.project_files [fileName]
       else :
          text = os.path.basename (fileName)
          node = TreeItem (self.currentProject, text)
          self.project_files [fileName] = node
          node.setToolTip (0, fileName)
          node.setIcon (0, findIcon ("document-open"))
          node.src_file = fileNameToIndex (fileName)
          if edit != None :
             node.obj = edit
             edit.setExtraSelections ([ ]) # clear attributes
       return node

   def projectOpenInclude (self, fileName) :
       text = os.path.basename (fileName)
       node = TreeItem (self.currentInclude, text)
       node.setToolTip (0, "include " + fileName)
       node.setIcon (0, findIcon ("document"))
       "text-x-generic"
       node.src_file = fileNameToIndex (fileName)
       node.obj = self.loadFile (fileName) # open file if editor does not exists
       self.currentInclude = node

   def projectCloseInclude (self) :
       if self.currentInclude != self.currentProject and self.currentInclude != None :
          self.currentInclude = self.currentInclude.parent ()

   # Clases

   def showClasses (self, data, activate = False) :
       IdentifierTree (self.classes, data)
       # self.classes.expandAll ()
       if activate :
          self.showTab (win.classes)

   # Tree

   def displayPythonCode (self, editor) :
       fileName =  editor.getFileName ()
       node = TreeItem (self.tree, "Python code " + os.path.basename (fileName))
       node.src_file = fileNameToIndex (fileName)
       node.addIcon ("code")
       node.continue_func = lambda : PythonTree (node, editor)
       branchContinue (node)

   def displayGrammarData (self, editor, grammar, module = None) :
       editor.compiler_data = grammar # for findCompilerData
       fileName =  editor.getFileName ()
       fileInx = fileNameToIndex (fileName)
       node = TreeItem (self.tree, "grammar " + os.path.basename (fileName))
       node.src_file = fileInx
       node.obj = grammar
       return GrammarTree (node, grammar, fileInx, module)

   def displayCompilerData (self, editor, data) :
       self.compiler_data = data
       editor.compiler_data = data
       fileName =  editor.getFileName ()
       node = TreeItem (self.tree, "compiler data " + os.path.basename (fileName))
       node.src_file = fileNameToIndex (fileName)
       # node.src_line = 0 # !?
       # node.src_step = 0 # !?
       CompilerTree (node, data)

   def findCompilerData (self, editor, line, col) :
       self.showTab (self.tree)
       lookupCompilerData (self.tree, editor, line, col)

   def displayFileItem (self, fileName) :
       branch = TreeItem (self.tree, "output " + os.path.basename (fileName))
       branch.src_file = fileNameToIndex (fileName)
       return branch

   # Variables

   def showVariable (self, text, data) :
       node = TreeItem (self.variables, text)
       node.obj = data
       # data.link_tree_node = node

   # Navigator

   def addNavigatorData (self, editor, data) :
       editor.navigator_data = data

       sideTabs = self.navigator.parentWidget ()
       if isinstance (sideTabs, QStackedWidget) :
          sideTabs = sideTabs.parentWidget ()

       if sideTabs.currentWidget() == self.navigator :
          self.showTab (self.classes) # !? refresh tab
          self.showTab (self.navigator)

   # Memo and References

   def showMemo (self, editor, name) :
       self.memo.showMemo (editor, name)

   def showReferences (self, editor, name) :
       self.references.showReferences (editor, name)

   # Input files

   def inputFile (self, fileName) :
       edit = self.refreshFile (fileName)
       if edit == None :
          raise  IOError ("File not found: " + fileName)
       # if edit.isModified () :
       #    edit.saveFile ()
       return edit

   def rebuildFile (self, source, target) :
       return not os.path.isfile (target) or os.path.getmtime (source) > os.path.getmtime (target)

   def createSupport (self, parser) :
       # print ("createSupport", fileName)
       # edit = self.inputFile (fileName)
       return Support (self, parser)

   def resetEditorStyle (self, edit) :
       # reset colors and properties, keep extra selection (bookmarks)
       edit.lastCursor = None
       cursor = edit.textCursor ()
       line = cursor.blockNumber () # remember line and column
       column = columnNumber (cursor)

       cursor.select (QTextCursor.Document) # select all
       cursor.setCharFormat (QTextCharFormat ())
       cursor.clearSelection () # unselect all

       cursor.movePosition (QTextCursor.Start)
       cursor.movePosition (QTextCursor.NextBlock, QTextCursor.MoveAnchor, line) # restore line and column
       cursor.movePosition (QTextCursor.NextCharacter, QTextCursor.MoveAnchor, column)
       edit.setTextCursor (cursor)

   # Output files

   def createDir (self, fileName) :
       dirName = os.path.dirname (fileName)
       if not os.path.isdir (dirName) :
          os.makedirs (dirName)

   def outputFileName (self, fileName, extension = "", with_subdir = False) :
       if not with_subdir :
          fileName = os.path.basename (fileName)
       fileName = os.path.join ("_output", fileName)
       if extension != "" :
          fileName, ext = os.path.splitext (fileName)
          if fileName.find ('-') >= 0 and extension.startswith ('_') :
             extension = extension.replace ('_', '-')
          fileName = fileName + extension
       fileName = os.path.abspath (fileName)
       self.createDir (fileName)
       return fileName

   def createSections (self, outputFileName, with_simple = False) :
       outputEdit = self.rewriteFile (outputFileName) # empty output file
       outputEdit.closeWithoutQuestion = True
       self.joinProject (outputEdit)

       # add node to tree window
       # tree_branch = self.displayFileItem (outputFileName)

       # add node to navigator window
       branch = TreeItem (None)
       branch.setText (0, os.path.basename (outputFileName))
       self.addNavigatorData (outputEdit, branch) # make branch visible in navigator

       if with_simple :
          # add section nodes to navigator tree
          sections = SimpleSections (branch, outputEdit)
       else :
          # add section also to text properties
          sections = Sections (branch, outputEdit)
       return sections

   # Modules

   def loadModule (self, fileName) :
       return loadModule (fileName)

   # Plugin interface

   def addView (self, title, widget) :
       inx = self.firstTabWidget.addTab (widget, title)
       self.firstTabWidget.setCurrentIndex (inx)

   def addMenuItem (self, top_menu, title, func, shortcut = "") :
       menu = self.addTopMenu (top_menu) # find or create top level menu
       act = QAction (title, self)
       if shortcut != "" :
          act.setShortcut (shortcut)
       act.triggered.connect (func)
       menu.addAction (act)

   def addObject (self, obj) :
       self.owned_objects.append (obj)

   def fileNameToIndex (self, fileName) :
       return fileNameToIndex (fileName)

   def readFile (self, fileName) :
       edit = self.loadFile (fileName)
       # edit = self.refreshFile (fileName)
       return qstring_to_str (edit.toPlainText ())

   def treeBranch (self, text = "") :
       node = TreeItem (self.tree, text)
       self.showTab (self.tree)
       self.tree.setCurrentItem (node)
       return node

   def treeItem (self, above, text = "") :
       node = TreeItem (above, text)
       return node

   # Utilities

   def runPython (self, fileName) :
       self.info.runCommandByName ("run-python", fileName)

   def showHtml (self, fileName) :
       self.info.runCommandByName ("show-html", fileName)

   def showPreview (self, fileName) :
       self.info.runCommandByName ("show-preview", fileName)

   def showPdf (self, fileName) :
       self.info.runCommandByName ("show-pdf", fileName)

   def showLout (self, fileName, toPdf = False) :
       # create PDF or PostScript file

       subdir = os.path.dirname (fileName)
       save_dir = os.getcwd ()
       os.chdir (subdir)

       localName = os.path.basename (fileName) # local file name

       if toPdf :

          pdfFileName, ext = os.path.splitext (localName)
          pdfFileName = pdfFileName + ".pdf"

          os.system ("lout" + " " +  localName + " -PDF -o " + pdfFileName)
          self.showPdf (pdfFileName)

       else :

          psFileName, ext = os.path.splitext (localName)
          psFileName = psFileName + ".ps"

          # dnf install lout
          os.system ("lout" + " " +  localName + " -o " + psFileName)
          # lout also creates .li file in current directory

          self.showPdf (psFileName)

       os.chdir (save_dir)

# --------------------------------------------------------------------------

if not use_py2_qt4 and not opts.no_hook :
   import traceback

   original_excepthook = sys.excepthook
   # install handler for exceptions
   sys.excepthook = print_traceback

   # import faulthandler
   # faulthandler.enable ()
   # gdb -ex r --args python view.py

# --------------------------------------------------------------------------

if opts.no_notify :
   app = QApplication (sys.argv)
else :
   app = CentralApplication (sys.argv)

setApplStyle (app)

win = ViewWindow (None, app, conf)
win.show ()

if not opts.no_redirect :
   win.info.redirectOutput ()

"open files"
for desc in win.conf.open_list :
    win.loadFile (desc.name)
for name in open_args :
    win.loadFile (name)

msg = win.statusBar().currentMessage()
msg = msg + ", " + "%.2f" % (time.time() - start_time) + " s"
win.showStatus (msg)

if use_qt6 :
   # app.exec () # python 2 => syntax error
   getattr (app, "exec") ()
else :
   app.exec_ ()

if not opts.no_redirect :
   win.info.stopRedirect ()

if not use_py2_qt4 and not opts.no_hook :
   sys.excepthook = original_excepthook

if use_python3 :
   import atexit
   # atexit._run_exitfuncs()
   atexit._clear ()

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
