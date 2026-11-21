#!/usr/bin/env python
#!/usr/bin/env python

import sys, os, importlib

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from util import *

# work_dir = os.getcwd ()
work_dir = os.path.abspath (sys.path [0])
# The application lives in view/, the shared modules one level up.
module_dirs = [ os.path.join ("..", "qtdesigner"),
                os.path.join ("..", "code"),
                os.path.join ("..", "grm"),
                os.path.join ("..", "cmm") ]

for local_dir in module_dirs :
    sys.path.insert (1, os.path.join (work_dir, local_dir)) # Debian 10, Python 2

# from input import indexToFileName, fileNameToIndex

from edit import Editor, FindBox, Bookmark
from grep import GrepDialog
# from tools import middleMenuItems, MenuItem
from tree import Tree, TreeItem
from window import MainWindow

# --------------------------------------------------------------------------

class ViewWindow (MainWindow):

   def __init__ (self, parent) :
       super (ViewWindow, self).__init__ (parent)

       # Menu commands run from the project root: the example paths in
       # tools.ini are relative to it, even when the IDE is started from
       # view/ (path on sys.path [0] is the view/ directory itself).
       self.info.work_dir = os.path.dirname (os.path.abspath (sys.path [0]))

       self.grep_dialog = GrepDialog (self)

       # resizeMainWindow (self)

       # project menu

       self.runMenu = self.addTopMenu ("&Project")
       # self.runMenu.aboutToShow.connect (lambda: menuItemsByExtension (self, self.runMenu))
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

       act = QAction ("Run Python", self)
       act.setIcon (findIcon ("text-x-python"))
       act.setShortcut ("F7")
       act.triggered.connect (self.run_python)
       menu.addAction (act)

       # act = QAction ("Run C++", self)
       # act.setIcon (findIcon ("text-x-c++src"))
       # act.setShortcut ("F8")
       # act.triggered.connect (self.run_cpp)
       # menu.addAction (act)

       # act = QAction ("Debug C++", self)
       # act.setIcon (findIcon ("kbugbuster"))
       # act.triggered.connect (self.debug_cpp)
       # menu.addAction (act)

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

       # window and tabs menu

       self.additionalMenuItems ()

       # tools menu

       self.toolsMenu = self.addTopMenu ("&Tools")

       for title, script in [
           ("Test &Generate (iced-x86)", "test_generate.py"),
           ("Test &LLVM",                "test_llvm.py"),
           ("Test &.t Examples",         "test_t_examples.py"),
           ("Test &Set Examples",        "test_set.py"),
       ] :
           act = QAction (title, self)
           act.setIcon (findIcon ("system-run"))
           act.triggered.connect (lambda checked = False, s = script :
                                  self.run_test_suite (s))
           self.toolsMenu.addAction (act)

       self.toolsMenu.addSeparator ()

       act = QAction ("Qt &Designer", self)
       act.setIcon (findIcon ("applications-development"))
       act.triggered.connect (self.open_qt_designer)
       self.toolsMenu.addAction (act)

       # (Container and Kubernetes submenus removed — their
       # tools/container-tools and tools/kube-tools scripts are not part
       # of this repository.)

       # Code-tooling plugins (top-level &Grammar and &C-- menus).
       # Imports are lazy so a missing dependency in grm/cmm doesn't
       # crash the whole editor — the menu is just absent.
       try :
          from gram_plugin import installGrammarPlugin
          installGrammarPlugin (self)
       except Exception as e :
          print ("gram_plugin not loaded:", e)
       try :
          from cmm_plugin import installCmmPlugin
          installCmmPlugin (self)
       except Exception as e :
          print ("cmm_plugin not loaded:", e)

       # &Examples menu populated from tools.ini (t-examples, C-- examples, set).
       try :
          from tools_ini import installExamplesMenu
          installExamplesMenu (self)
       except Exception as e :
          print ("tools.ini menu not loaded:", e)

       # help menu

       self.helpMenu = self.addTopMenu ("&Help")

       for title, url in [
           ("&Python Documentation",  "https://docs.python.org/3/"),
           ("&Qt Documentation",      "https://doc.qt.io/qt-5/"),
           ("Py&Qt5 Documentation",   "https://www.riverbankcomputing.com/static/Docs/PyQt5/"),
       ] :
           act = QAction (title, self)
           act.setIcon (findIcon ("help-browser"))
           act.triggered.connect (lambda checked = False, u = url, t = title : self.openHelpUrl (u, t))
           self.helpMenu.addAction (act)

       self.helpMenu.addSeparator ()

       act = QAction ("&About", self)
       act.triggered.connect (self.showAbout)
       self.helpMenu.addAction (act)

       # status bar

       exe = sys.executable
       if sys.dont_write_bytecode :
          exe = exe + " -B"
       ver = sys.version_info
       inf = str (ver[0]) + "." + str (ver[1]) + "." + str (ver[2])
       self.showStatus (exe + ", Python " + inf + ", Qt " + qVersion ())

   # Project menu

   def configure (self) :
       self.runCommand ("./configure")

   def build (self) :
       self.runCommand ("make")

   def run (self) :
       self.runCommand ("make run")

   def debug (self) :
       self.runCommand ("make debug")

   def clean (self) :
       self.runCommand ("make clean")

   def install (self) :
       self.runCommand ("make install")

   def findInFiles (self) :
       self.showTab (self.grep)
       self.grep_dialog.openDialog (self.getEditor ())

   def run_python (self) :
       editor = self.getEditor ()
       if editor != None :
          # self.checkModifiedOnDisk (editor)
          self.info.clearOutput ()
          text = editor.toPlainText ()
          print ("source code:", text)
          print ("result:")
          exec (text)

   def runCommand (self, cmd) :
       "Run a shell command; stdout/stderr are streamed into the bottom panel."
       self.info.clearOutput ()
       print ("RUN:", cmd)
       self.info.runCommandString (cmd)

   def make (self) :
       self.runCommand ("make")

   def run_python_file (self) :
       editor = self.getEditor ()
       if editor != None :
          self.checkModifiedOnDisk (editor)
          exe = sys.executable + " -u"   # unbuffered, so output appears immediately
          self.runCommand (exe + " " + editor.getFileName ())

   def outputBinary (self, fileName) :
       "Map src 'foo/bar.cc' -> '_output/bar.bin' (.exe on Windows)."
       base = os.path.splitext (os.path.basename (fileName)) [0]
       ext  = ".exe" if os.name == "nt" else ".bin"
       return "_output/" + base + ext

   def run_cpp_file (self) :
       "Compile current C/C++ file with gcc/g++ and run the result."
       editor = self.getEditor ()
       if editor != None :
          self.checkModifiedOnDisk (editor)
          fileName = editor.getFileName ()
          options  = readEmbeddedOptions (fileName)   # from `// compile : ...`
          compiler = "g++" if fileName.endswith ((".cc", ".cpp", ".cxx")) else "gcc"
          binary   = self.outputBinary (fileName)
          self.runCommand (compiler + " " + options + " " + fileName + " -o " + binary + " && " + binary)

   def run_test_suite (self, script) :
       "Run one of the tests/ suites; output streams into the Info panel."
       path = os.path.join (os.path.dirname (os.path.abspath (sys.path [0])),
                            "tests", script)
       self.runCommand (sys.executable + " " + path)

   def debug_cpp_file (self) :
       editor = self.getEditor ()
       if editor != None :
          self.checkModifiedOnDisk (editor)
          fileName = editor.getFileName ()
          options  = readEmbeddedOptions (fileName)
          binary   = self.outputBinary (fileName)
          compiler = "g++" if fileName.endswith ((".cc", ".cpp", ".cxx")) else "gcc"
          self.runCommand (compiler + " -g " + options + " " + fileName + " -o " + binary + " && gdb --batch -ex run -ex bt " + binary)

   def open_qt_designer (self) :
       "Launch Qt Designer; if current editor holds a .ui file, open it there."
       from qt_designer import openQtDesigner
       editor = self.getEditor ()
       ui_file = ""
       if editor != None :
          fileName = editor.getFileName ()
          if fileName.lower ().endswith (".ui") and os.path.isfile (fileName) :
             ui_file = fileName
       openQtDesigner (self, ui_file)

   # Properties

   def showProperties (self, data) :
       self.prop.showProperties (data)
       self.showTab (self.prop)

   # Help menu

   def openHelpUrl (self, url, title) :
       "Open url in a reusable Help tab inside firstTabWidget (uses WebEngine)."
       try :
          from PyQt5.QtWebEngineWidgets import QWebEngineView
       except ImportError as e :
          print ("PyQt5 WebEngine not available:", e)
          print ("Install: dnf install python3-pyqt5-webengine"
                 "  or  apt install python3-pyqt5.qtwebengine")
          return
       view = getattr (self, "_help_view", None)
       if view is None :
          view = QWebEngineView (self)
          self._help_view = view
          inx = self.firstTabWidget.addTab (view, "Help")
       else :
          inx = self.firstTabWidget.indexOf (view)
          if inx < 0 :
             inx = self.firstTabWidget.addTab (view, "Help")
       self.firstTabWidget.setTabText    (inx, "Help: " + title.replace ("&", ""))
       self.firstTabWidget.setTabToolTip (inx, url)
       view.load (QUrl (url))
       self.firstTabWidget.setCurrentIndex (inx)

   def showAbout (self) :
       msg = ("10-edit — minimal PyQt5 editor\n\n"
              "Python " + sys.version.split () [0] + ", Qt " + qVersion () + "\n"
              "Project menu: gcc build, run and debug")
       QMessageBox.about (self, "About 10-edit", msg)

# --------------------------------------------------------------------------

# Compiled artifacts (g++/JIT inputs, generated parsers, .bin outputs)
# all land in ./_output/. Created at startup so Project menu actions can
# write into it without checking. The .bin extension on Linux executables
# makes `rm _output/*.bin` a clean rule for makefiles.
output_dir = os.path.join (os.path.abspath (sys.path [0]), "_output")
os.makedirs (output_dir, exist_ok = True)

app = QApplication (sys.argv)

app.setStyleSheet ("QTabBar::tab:selected {color: blue }"
                   "QWidget {font-size: 12pt}"
                   "Editor {font-family: \"Luxi Mono\" ; font-size: 14pt}"
                   # "QToolTip { color: #000; background-color: yellow; border 1px solid}"
                   )

win = ViewWindow (None)
win.show ()

# Print the full call stack on uncaught exceptions, but keep the editor running.
# print_traceback (from util) walks back through caller frames so we see WHICH
# function was running when the error occurred, not just the failure point.
def excepthook (exc_type, exc_value, exc_tb) :
    print_traceback (exc_type, exc_value, exc_tb)

sys.excepthook = excepthook

# Redirect stdout/stderr into the bottom Info panel (also keeps original stream).
if not opts.no_redirect :
   win.info.redirectOutput ()

"open files"
win.loadFile ("examples/example.py")
win.loadFile ("examples/tree.py")
win.loadFile ("tools/llvm-tools/example.cc")

app.exec_ ()

if not opts.no_redirect :
   win.info.stopRedirect ()

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
