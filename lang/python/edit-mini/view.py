#!/usr/bin/env python
#!/usr/bin/env python

import sys, os

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from util import *

from grep import GrepDialog
from window import MainWindow

# --------------------------------------------------------------------------

class ViewWindow (MainWindow):

   def __init__ (self, parent) :
       super (ViewWindow, self).__init__ (parent)

       self.grep_dialog = GrepDialog (self)

       # resizeMainWindow (self)

       # project menu

       self.runMenu = self.addTopMenu ("&Project")
       menu = self.runMenu

       act = QAction ("Run Python", self)
       act.setIcon (findIcon ("text-x-python"))
       act.setShortcut ("F7")
       act.triggered.connect (self.run_python)
       menu.addAction (act)

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

   def run_python_file (self) :
       editor = self.getEditor ()
       if editor != None :
          self.checkModifiedOnDisk (editor)
          exe = sys.executable + " -u"   # unbuffered, so output appears immediately
          self.runCommand (exe + " " + editor.getFileName ())

   def run_cpp_file (self) :
       "Compile current C/C++ file with gcc/g++ and run the result."
       editor = self.getEditor ()
       if editor != None :
          self.checkModifiedOnDisk (editor)
          fileName = editor.getFileName ()
          options  = readEmbeddedOptions (fileName)   # from `// compile : ...`
          compiler = "g++" if fileName.endswith ((".cc", ".cpp", ".cxx")) else "gcc"
          binary   = os.path.splitext (fileName) [0]
          self.runCommand (compiler + " " + options + " " + fileName + " -o " + binary + " && " + binary)

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
       msg = ("edit-mini — minimal PyQt5 text editor\n\n"
              "Python " + sys.version.split () [0] + ", Qt " + qVersion () + "\n\n"
              "Project menu: run a file, grep across files\n"
              "The programming IDE with clang completion, build tools and\n"
              "containers lives in the ide-mini directory.")
       QMessageBox.about (self, "About edit-mini", msg)

# --------------------------------------------------------------------------

def run (initial_files = None) :
    """Launch the editor application. Callers can pass a list of files to
    open at startup; if None, the editor starts with an empty buffer."""

    app = QApplication (sys.argv)

    app.setStyleSheet ("QTabBar::tab:selected {color: blue }"
                       "QWidget {font-size: 12pt}"
                       "Editor {font-family: \"Luxi Mono\" ; font-size: 14pt}"
                       )

    win = ViewWindow (None)
    win.show ()

    # Print the full call stack on uncaught exceptions, keep the editor running.
    def excepthook (exc_type, exc_value, exc_tb) :
        print_traceback (exc_type, exc_value, exc_tb)
    sys.excepthook = excepthook

    if not opts.no_redirect :
       win.info.redirectOutput ()

    for f in (initial_files or [ ]) :
        win.loadFile (f)

    app.exec_ ()

    if not opts.no_redirect :
       win.info.stopRedirect ()


if __name__ == "__main__" :
    run ()

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
