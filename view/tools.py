# tools.py

from __future__ import print_function

import os, sys, re, subprocess, traceback, importlib

use_webkit = True
use_webengine = True
use_dbus = True
use_xlib = True

from util import *
import_qt_modules (globals ())

if use_pyside2 or use_pyside6 :
   # http://www.pythonguis.com/faq/pyqt6-vs-pyside6/
   from PySide6.QtCore import Signal as pyqtSignal, Slot as pyqtSlot

if use_webkit :
   names = [ "QtWebKit" ]
   if not use_qt4 :
      names = names + [ "QtWebKitWidgets" ]
   use_webkit = optional_qt_modules (globals (), names)
   if use_webkit :
      use_webengine = False

if use_webengine :
   use_webengine = optional_qt_modules (globals (), ["QtWebEngine", "QtWebEngineWidgets" ])

if use_dbus :
   use_dbus = optional_qt_module (globals (), "QtDBus")

if use_xlib :
   try :
      import Xlib
      import Xlib.display
      import Xlib.XK
      import time
   except :
      use_xlib = False
      print ("missing Xlib")

from util import use_python3, opts
from util import findColor, findIcon, Text, qstring_to_str, qstring_starts_with, qstring_ends_with, simple_bytearray_to_str
from tree import branchContinue
from settings import *

# --------------------------------------------------------------------------

stop_redirect = False

class Redirect (object) :
   def __init__ (self, target, original) :
       self.target = target
       self.original = original
       self.buffer = ""

   def put (self, text) :
       self.target.commandOneLine (text)

   def send_buffer (self) :
       if self.buffer != "" :
          self.put (self.buffer)
          self.buffer = ""

   def write (self, text) :
       self.original.write (text)
       if not stop_redirect :
          try:
             text = self.buffer + text
             inx = text.find ("\n")
             while inx > 0 :
                line = text [ : inx ]
                self.put (line)
                text = text [ inx + 1 : ]
                inx = text.find ("\n")

             self.buffer = text
          except :
              self.original.write ("\n")
              self.original.write ("EXCEPTION during stdout or stderr redirect")

   def flush (self) :
       self.original.flush ()
       if not stop_redirect :
          self.send_buffer ()

   def close (self) :
       if not stop_redirect :
          self.send_buffer ()

# --------------------------------------------------------------------------

class Info (QPlainTextEdit) :

   def __init__ (self, win) :
       super (Info, self).__init__ (win)
       self.win = win
       self.setLineWrapMode (QPlainTextEdit.NoWrap)

       self.process = None

       self.directory = ""
       self.buffer = ""

       self.red = findColor ("red")
       self.green = findColor ("green")
       self.blue = findColor ("blue")
       self.gray = findColor ("gray")
       self.norm = findColor ("ink")
       self.brown = findColor ("brown")
       self.orange = findColor ("orange")
       self.yellow = findColor ("yellow")
       self.cornflowerblue = findColor ("cornflowerblue")

   # -- redirect output --

   def redirectOutput (self) :
       sys.stdout = Redirect (self, sys.stdout)
       sys.stderr = Redirect (self, sys.stderr)

   def stopRedirect (self) :
       global stop_redirect
       stop_redirect = True

   # -- color output --

   def colorText (self) :
       cursor = self.textCursor ()

       format = cursor.charFormat ()
       format.setForeground (self.blue)
       cursor.setCharFormat (format)

       cursor.insertText ("blue line\n")

       format = cursor.charFormat ()
       format.setForeground (self.red)
       cursor.setCharFormat (format)

       cursor.insertText ("red line")

   def setColor (self, cursor, color) :
       format = cursor.charFormat ()
       format.setForeground (color)
       cursor.setCharFormat (format)

   def setNote (self, cursor, note) :
       format = cursor.charFormat ()
       format.setProperty (Text.locationProperty, note)
       cursor.setCharFormat (format)

   def clearNote (self, cursor) :
       format = cursor.charFormat ()
       format.clearProperty (Text.locationProperty)
       cursor.setCharFormat (format)

   # -- gcc options --

   def gccLine (self, cursor, line) :
       cont = False
       for word in line.split () :
           style = False

           if not cont :
              if word.endswith (".c") or  word.endswith (".cc") or word.endswith (".cpp") :
                 self.setColor (cursor, self.brown)
                 style = True

           if not cont :
              if word.startswith ("-I") :
                 self.setColor (cursor, self.green)
                 style = True
              elif word.startswith ("-D") or word.startswith ("-U") :
                 self.setColor (cursor, self.orange)
                 style = True
              elif word.startswith ("-L") :
                 self.setColor (cursor, self.cornflowerblue)
                 style = True
              elif word.startswith ("-l") :
                 self.setColor (cursor, self.blue)
                 style = True
              elif word.startswith ("-o") :
                 self.setColor (cursor, self.red)
                 style = True

           next_cont = style and len (word) == 2

           cursor.insertText (word)

           if style and not next_cont or cont :
              self.setColor (cursor, self.norm)

           cont = next_cont

           cursor.insertText (" ")

   # -- make output --

   def modifyLine (self, cursor, line, keyword) :
       pattern = "(.*\s)?(\S*):(\d\d*)(:(\d\d*))?:(\s*" + keyword + ":)(.*)"
       m = re.search (pattern, line)
       if m :
          mark = os.path.join (self.directory, m.group (2)) + ":" + m.group (3)
          if m.group (4) != None :
             mark = mark + ":" + m.group (5)

          self.setNote (cursor, mark)

          if m.group (1) != None :
             cursor.insertText (m.group (1))

          self.setColor (cursor, self.blue)
          cursor.insertText (m.group (2))
          self.setColor (cursor, self.norm)
          cursor.insertText (":")

          self.setColor (cursor, self.green)
          cursor.insertText (m.group (3))
          self.setColor (cursor, self.norm)

          if m.group (4) != None :
              cursor.insertText (":")
              self.setColor (cursor, self.gray)
              cursor.insertText (m.group (5))

          self.setColor (cursor, self.red)
          cursor.insertText (m.group (6))

          self.setColor (cursor, self.orange)
          cursor.insertText (m.group (7))
          self.setColor (cursor, self.norm)

          self.clearNote (cursor)  # before end of line, otherwise format is not changed
       else :
          self.setColor (cursor, self.brown)
          cursor.insertText (line)
          self.setColor (cursor, self.norm)

   def directoryLine (self, cursor, line) :
       pattern = "Entering directory '([^']*)'"
       m = re.search (pattern, line)
       if m :
          self.directory = m.group (1)
          self.setColor (cursor, self.orange)
       else :
          self.setColor (cursor, self.brown)
       cursor.insertText (line)
       self.setColor (cursor, self.norm)

   # -- Python trace --

   def pythonLine (self, cursor, line) :
       pattern = "  File (.*), line ([0-9]*)(, in (.*))?"
       m = re.match (pattern, line)
       if m :
          fileName = m.group (1)
          line =  m.group (2)
          if fileName.startswith ('"') and fileName.endswith ('"') :
             fileName = fileName [ 1 : -1 ]
          mark = fileName + ":" + line
          self.setNote (cursor, mark)

          cursor.insertText ("File ")
          self.setColor (cursor, self.blue)
          cursor.insertText (m.group (1))
          self.setColor (cursor, self.norm)

          cursor.insertText (", line ")
          self.setColor (cursor, self.green)
          cursor.insertText (m.group (2))
          self.setColor (cursor, self.norm)

          if m.group (4) != None :
             cursor.insertText (", in ")
             self.setColor (cursor, self.orange)
             cursor.insertText (m.group (4))
             self.setColor (cursor, self.norm)

          self.clearNote (cursor) # before end of line, otherwise format is not changed
       else :
          self.setColor (cursor, self.brown)
          cursor.insertText (line)
          self.setColor (cursor, self.norm)

   def commandOneLine (self, line) :
       cursor = self.textCursor ()
       cursor.movePosition (QTextCursor.End)

       if not use_python3 :
          line = line.decode ("ascii", "ignore")

       if line.find ("fatal error:") >= 0 :
          self.modifyLine (cursor, line, "fatal error") # clang
       elif line.find ("error:") >= 0 :
          self.modifyLine (cursor, line, "error")
       elif line.find ("warning:") >= 0 :
          self.modifyLine (cursor, line, "warning")
       elif line.find ("debug:") >= 0 :
          self.modifyLine (cursor, line, "debug")
       elif line.find ("info:") >= 0 :
          self.modifyLine (cursor, line, "info")
       elif line.find ("Entering directory ") >= 0 :
          self.directoryLine (cursor, line)
       elif line.find ("Leaving directory ") >= 0 :
          self.directory = ""
          cursor.insertText (line)
       elif line.startswith ("  File ") :
          self.pythonLine (cursor, line)
       elif line.find ("gcc") >= 0 or line.find ("g++") >= 0 or line.find ("clang") >= 0 or line.find ("clang++") >= 0 :
          self.gccLine (cursor, line)
       else :
          cursor.insertText (line)
       cursor.insertText ("\n")

   def commandAddText (self, text) :
       sys.stdout.write (text)
       sys.stdout.flush ()
       if opts.no_redirect :
          for c in text :
              if c == '\n' :
                 self.commandOneLine (self.buffer)
                 self.buffer = ""
              else :
                 self.buffer = self.buffer + c
       self.ensureCursorVisible ()
       qApp.processEvents () # important

   def commandFinishText (self, text) :
       self.commandAddText (text)
       if opts.no_redirect :
          if self.buffer != "" :
             self.commandOneLine (self.buffer)
             self.buffer = ""
       self.ensureCursorVisible ()
       qApp.processEvents ()

   def commandReadyRead (self) :
       text = simple_bytearray_to_str (self.process.readAll ())
       self.commandAddText (text)

   def commandDataFinished (self) :
       text = simple_bytearray_to_str (self.process.readAll ())
       self.commandFinishText (text)

   # -- mouse click --

   def mousePressEvent (self, e) :
       cursor = self.cursorForPosition (mouse_event_pos (e))
       cursor.select (QTextCursor.WordUnderCursor)
       format = cursor.charFormat ()
       mark = str (format.stringProperty (Text.locationProperty))
       if mark != "" :
          (fileName, line, column) = self.getLocation (mark)
          if fileName != None :
             self.goToLocation (fileName, line, column)
             modifiers = e.modifiers ()
             # buttons = e.buttons ()
             if modifiers & Qt.MetaModifier:
                self.goToKDevelop (fileName, line, column)
       super (Info, self).mousePressEvent (e)

   def getLocation (self, mark) :
       pattern = "([^:]*)(:([0-9]*)(:([0-9]*))?)?"
       m = re.match (pattern, mark)
       if m :
          fileName = m.group (1)
          line = m.group (3)
          column = m.group (5)
          if line == None or line == "" :
             line = 0
          else :
             line = int (line)
          if column == None or column == "" :
             column = 0
          else :
             column = int (column)
          # print ("file:", fileName)
          # print ("line:",  line)
          # print ("column:", column)
       else :
          fileName = None
          line = 0
          column = 0
       return (fileName, line, column)

   def goToLocation (self, fileName, line, column) :
       if self.win != "" :
          self.win.loadFile (fileName, line, column)

   def goToKDevelop (self, fileName, line, column) :
       pass

   def goToNotepad (self, fileName, line, column) :
       pass

   def goToQtCreator (self, fileName, line, column) :
       pass

   # -- jump to next mark --

   def jumpToPrevMark (self) :
       cursor = self.textCursor ()
       cursor.movePosition (QTextCursor.StartOfLine)
       stop = False
       found = False
       while not stop and not found:
          if not cursor.movePosition (QTextCursor.Up) :
             stop = True
          if cursor.charFormat ().hasProperty (Text.locationProperty) :
             found = True
          if cursor.atStart () :
             stop = True

       if found :
          cursor.movePosition (QTextCursor.EndOfLine, QTextCursor.KeepAnchor)

       self.setTextCursor (cursor)
       self.ensureCursorVisible ()

       if found :
          mark = str (cursor.charFormat ().stringProperty (Text.locationProperty))
          (fileName, line, column) = self.getLocation (mark)
          self.goToLocation (fileName, line, column)
          self.win.showStatus ("")
       else :
          self.win.showStatus ("Begin of file")

   def jumpToNextMark (self) :
       cursor = self.textCursor ()
       cursor.movePosition (QTextCursor.StartOfLine)
       stop = False
       found = False
       while not stop and not found:
          if not cursor.movePosition (QTextCursor.NextBlock) :
             stop = True
          if cursor.charFormat ().hasProperty (Text.locationProperty) :
             found = True
          if cursor.atEnd () :
             stop = True

       if found :
          cursor.movePosition (QTextCursor.EndOfLine, QTextCursor.KeepAnchor)

       self.setTextCursor (cursor)
       self.ensureCursorVisible ()

       if found :
          mark = str (cursor.charFormat ().stringProperty (Text.locationProperty))
          (fileName, line, column) = self.getLocation (mark)
          self.goToLocation (fileName, line, column)
          self.win.showStatus ("")
       else :
          self.win.showStatus ("End of file")

   def jumpToFirstMark (self) :
       cursor = self.textCursor ()
       cursor.movePosition (QTextCursor.Start)
       self.setTextCursor (cursor)
       self.jumpToNextMark ()

   def jumpToLastMark (self) :
       cursor = self.textCursor ()
       cursor.movePosition (QTextCursor.End)
       self.setTextCursor (cursor)
       self.jumpToPrevMark ()

   def scrollUp (self) :
       self.verticalScrollBar ().triggerAction (QAbstractSlider.SliderSingleStepSub)

   def scrollDown (self) :
       self.verticalScrollBar ().triggerAction (QAbstractSlider.SliderSingleStepAdd)

# http://stackoverflow.com/questions/26500429/qtextedit-and-colored-bash-like-output-emulation
# http://stackoverflow.com/questions/22069321/realtime-output-from-a-subprogram-to-stdout-of-a-pyqt-widget

# --------------------------------------------------------------------------

class InfoWithTools (Info) :

   def __init__ (self, win) :
       super (InfoWithTools, self).__init__ (win)
       self.work_dir = ""
       self.env_dict = { }
       self.stopClear = 0

   def readCd (self, desc) :
       "cd"
       if desc.cd != "" :
          self.work_dir = desc.cd

   def readSet (self, desc) :
       "set"
       for text in desc.set :
           answer = text.split ("=", 1)
           name = answer [0]
           value = answer [1]
           name = name.strip ()
           value = value.strip ()
           self.env_dict [name] = value
           # print ("SET", name + "=" + value)

   def readEnvironment (self, env_name) :

       for desc in self.win.conf.command_list :
           if desc.title == env_name :

              "env"
              for env in desc.env :
                 self.readEnvironment (env); # read other environment

              "cd"
              self.readCd (desc)

              "set"
              self.readSet (desc)

   def showUrl (self, url, title = "") :
       if self.win != None and ( use_webengine or use_webkit ) :
          widget = WebWin (self.win)
          self.win.firstTabWidget.addTab (widget, title)
          self.win.firstTabWidget.setCurrentWidget (widget)
          widget.load (QUrl (url))

   def runCommandString (self, cmd) :
       self.process = QProcess (self.win)

       if self.work_dir != "" :
          self.process.setWorkingDirectory (self.work_dir)

       env = QProcessEnvironment.systemEnvironment () # important
       for name in self.env_dict :
           value = self.env_dict [name]
           env.insert (name, value)
           # print ("SET", name + "=" + value)
       self.process.setProcessEnvironment (env)

       # self.process.setProcessChannelMode (QProcess.ForwardedChannels)
       self.process.setProcessChannelMode (QProcess.MergedChannels)
       self.process.readyRead.connect (self.commandReadyRead)
       self.process.finished.connect (self.commandDataFinished)

       print ("RUN", cmd)
       self.process.start ("/bin/sh", [ "-c", cmd ] ) # !?

       self.win.process_list.append (self.process)
       self.process.finished.connect (lambda param1, param2, self=self, process=self.process: self.forgetProcess (process))

   def forgetProcess (self, process) :
       self.win.process_list.remove (process)

   def runPythonFunc (self, f, addWin, param) :
       result = None
       if addWin :
          if param != "" :
             result = f (self.win, param)
          else :
             result = f (self.win)
       else :
          if param != "" :
             result = f (param)
          else :
             result = f ()
       return result

   def runPythonMethod (self, m, cls, func, addWin, param) :
       result = None
       if m != None and (cls != "" or func != "") :
          # cls and func are not empty ... add window to class, add parameters to func
          # cls is empty ... add parameters to func
          # func is empty ... add parameters to cls
          if cls != "" :
             c = getattr (m, cls)
             if func != "" :
                c = self.runPythonFunc (c, addWin, "")
                f = getattr (c, func)
                result = self.runPythonFunc (f, False, param)
             else :
                result = self.runPythonFunc (c, addWin, param)
          else :
             f = getattr (m, func)
             result = self.runPythonFunc (f, addWin, param)
       return result

   def runPythonModule (self, module, cls, func, addWin, param) :
       m = self.win.loadModule (module)
       self.runPythonMethod (m, cls, func, addWin, param)

   def runPluginModule (self, desc) :
       mod = self.win.plugin_map [desc.plugin]

       if mod.module == None :
          # print ("LOAD PLUGIN ON CLICK", mod.title)
          mod.module = self.win.loadModule (mod.module_name)

       "call plugin class constructor"
       activatePlugin (self.win, mod)

       if desc.func == "" :
          # print ("CALL", mod.title,  "function runPluginCommand")
          mod.cls.runPluginCommand (desc)
       else :
          # print ("CALL", mod.title, "function", desc.func)
          "only call one function"
          fce = getattr (mod.cls, desc.func)
          fce ()

   def runCommandObject (self, desc, fileName = "") :

       # !? self.win.info.clearOutput ()
       # !? self.win.unloadModules ()

       # print ("RUN GROUP", group)
       self.work_dir = ""
       self.env_dict = { }

       "env"
       if desc.env != "" :
          self.readEnvironment (desc.env)

       "cd"
       self.readCd (desc)

       "set"
       self.readSet (desc)


       "url"
       url = firstValidUrl (desc.url)

       "title"
       title = desc.title

       "cmd"
       cmd = desc.cmd
       if desc.python_cmd :
          exe = sys.executable
          if sys.dont_write_bytecode :
             exe = exe + " -B"
          exe = exe + " -u" # unbuffered
          cmd = exe + " " + cmd

       "addFileName"
       addFileName = desc.addFileName
       if fileName != "" :
          addFileName = True

       "param"
       param = desc.param

       if addFileName :
          if fileName == "" :
             e = self.win.getEditor ()
             fileName = e.getFileName ()
          if cmd != "" :
             if cmd.find ("$") != -1 :
                cmd = cmd.replace ("$", fileName)
             else :
                cmd = cmd + " " + fileName
          else :
             param = fileName

       "askFileName"
       if desc.askFileName != "":
          if use_py2_qt4 :
             param = dialog_to_str (QFileDialog.getOpenFileName (self, "Open File for " + title, desc.askFileName))
          else :
             dlg_url = QUrl.fromLocalFile (desc.askFileName)
             dlg_url, dlg_mask = QFileDialog.getOpenFileUrl (self, "Open File for " + title, dlg_url)
             param = dlg_url.toLocalFile ()
          if param == "" :
             param = askFileName

       if url != "" :
          # print ("URL", url)
          self.showUrl (url, title)

       elif cmd != "" :
          "cmd"
          try :
              if self.work_dir != "" :
                 save_dir = os.getcwd ()
                 os.chdir (self.work_dir)
              print ("work_dir", self.work_dir)
              self.runCommandString (cmd)
          finally :
              if self.work_dir != "" :
                  os.chdir (save_dir)
       else :
          "plugin, load, loaded_module, module, cls, func, addWin"
          try :
             if self.work_dir != "" :
                sys.path.insert (0, self.work_dir)
                # do not change current directory when importing Python module

             for load in desc.load :
                 self.win.loadModule (load)

             if desc.module != "" :
                self.runPythonModule (desc.module, desc.cls, desc.func, desc.addWin, param)

             elif desc.plugin != "" : # only when  module == "" and loaded_module == ""
                self.runPluginModule (desc)

             else :
                print ("Unknown command")

          except :
             # print ("RUN GROUP EXCEPTION")
             traceback.print_exc ()
          finally :
             # print ("RUN GROUP FINALLY")
             if self.work_dir != "" :
                del sys.path [0]

   # -- run --

   def runCommandByName (self, command_name, fileName = "") :
       for desc in self.win.conf.command_list :
           if desc.title == command_name :
              self.runCommandObject (desc, fileName)

   def stop (self) :
       self.process.terminate ()

   def resetCleaning (self) :
       self.stopClear = 0

   def disableCleaning (self) :
       self.stopClear = self.stopClear + 1

   def enableCleaning (self) :
       self.stopClear = self.stopClear - 1

   def clearOutput (self) :
       if self.stopClear <= 0 :
          self.clear ()

   # -- mouse click --

   def goToNotepad (self, fileName, line, column) :
       if os.name == "nt" :
          print ("NOTEPAD", fileName, "line:", line)
          cmd = "\"" + "C:\\Program Files\\NotepadPlusPlus\\notepad++.exe" + "\""
          os.system (cmd + " " + fileName + " -l" + str (line) + " -c" + str (column))
       else :
          print ("KATE", fileName, "line:", line)
          cmd = "kate" + " " + fileName + " -l" + str (line) + " -c" + str (column)
          subprocess.Popen (cmd, shell = True)

   def goToQtCreator (self, fileName, line, column) :
       print ("QTCREATOR", fileName, "line:", line)
       cmd = "qtcreator" + " -client " + fileName + ":" + str (line) + ":" + str (column)
       subprocess.Popen (cmd, shell = True)

   def goToKDevelop (self, fileName, line, column) :

       fileName = os.path.abspath (fileName)
       print ("KDEVELOP", fileName, "line:", line)
       line = line - 1
       if use_dbus :
          connection = QDBusConnection.sessionBus()
          serviceNames = connection.interface().registeredServiceNames().value();
          prefix = "org.kdevelop.kdevelop-"
          found = False
          for name in serviceNames :
              if qstring_starts_with (name, prefix) :
                 # print ("SERVICE", name)
                 ifc = QDBusInterface (name, "/org/kdevelop/DocumentController", "", connection)
                 ifc.call ("openDocumentSimple", fileName, line, column)
                 found = True
                 if use_xlib :
                    pid_str = qstring_to_str (name) [ len (prefix) : ]
                    pid = int (pid_str)
                    # print ("window with pid", pid)
                    activateWindowByPid (pid)
                 else :
                    print ("Missing xlib")
          if not found :
             print ("KDevelop application not found")
       else :
          print ("Missing dbus")

# --------------------------------------------------------------------------

class ClickAction (QAction) :

    def __init__ (self, win, desc) :
        super (ClickAction, self).__init__ (win)
        self.win = win
        self.desc = desc

        "title, shortcut, tooltip, icon"

        if desc.title != "" :
           self.setText (desc.title)

        if desc.shortcut != "" :
           self.setShortcut (desc.shortcut)

        if desc.tooltip != "" :
           self.setToolTip (desc.tooltip)
           self.setStatusTip (desc.tooltip)

        if desc.icon != "" :
           icon = findIcon (desc.icon)
           if icon != None :
              self.setIcon (icon)

        "file extension"
        if desc.ext != "" :
           has_ext = self.win.hasExtension (self.win.getEditor(), desc.ext)
           self.setEnabled (has_ext)
           self.ext = desc.ext

        "alternatively use 'param' for title and tooltip"
        if desc.title == "" :
           if desc.param != "" :
              self.setText (os.path.basename (desc.param))

        if desc.tooltip == "" :
           if desc.param != "" :
              self.setToolTip (desc.param)
              self.setStatusTip (desc.param)

        "disable item when web browser is missing"
        if len (desc.url) != 0 :
           if not use_webkit and not use_webengine :
              self.setEnabled (False)

        self.triggered.connect (self.click)

    def click (self) :
        self.win.info.runCommandObject (self.desc)

# --------------------------------------------------------------------------

def menuItemsByExtension (win, menu) :
    "enable or disable menu items according to editor file name extension"
    edit = win.getEditor()
    for act in menu.actions () :
        if getattr (act, "ext", "") != "" :
           has_ext = win.hasExtension (edit, act.ext)
           act.setEnabled (has_ext)
           # print (act.text (), has_ext)

# --------------------------------------------------------------------------

def refreshMenu (conf) :
    win = conf.win
    menu = None
    plugin = ""
    for desc in conf.menu_list :
        if isinstance (desc, MenuData) :
           menu = None
           plugin = desc.plugin
           menu = win.menu_bar_items.get (desc.title, None)
           if menu == None :
              menu = win.addTopMenu (desc.title) # add menu to menu_bar_items
        elif isinstance (desc, MenuSeparator) :
           act = menu.addSeparator ()
           # addDynamicItem (conf, menu, act)
        else :
           if plugin != ""  :
              if desc.plugin == "" :
                 desc.plugin = plugin
           act = ClickAction (win, desc)
           menu.addAction (act)
           # addDynamicItem (conf, menu, act)
           desc._action_ = act

def middleMenuItems (conf) :
    win = conf.win
    for desc in conf.menu_list :
        if isinstance (desc, MenuData) :
           if desc.middle :
              win.addTopMenu (desc.title) # add menu to menu_bar_items

# --------------------------------------------------------------------------

def refreshToolbar (conf) :
    desc_list = [ ]

    for desc in conf.menu_list :
        if isinstance (desc, MenuItem) and  desc.toolbar != 0  and desc._action_ != None :
           desc_list.append (desc)

    for desc in conf.shortcut_list :
        if desc.toolbar != 0 and desc._action_ != None :
           desc_list.append (desc)

    desc_list.sort (key = lambda item : item.toolbar)

    win = conf.win
    for desc in desc_list :
        win.toolbar.addAction (desc._action_)

# --------------------------------------------------------------------------

def refreshConfig (conf) :
    if readConfig (conf) :
       refreshModulePath (conf)
       refreshPlugins (conf)
       refreshColors (conf)
       refreshColorTables (conf)
       refreshIcons (conf)
       refreshMenu (conf)
       refreshToolbar (conf)

# --------------------------------------------------------------------------

def refreshPlugins (conf) :
    "called by reloadConfig, only fill plugin_map"
    win = conf.win
    win.plugin_map = { }

    for mod in conf.plugin_list :
       if mod.key != "" :
          win.plugin_map [mod.key] = mod

# --------------------------------------------------------------------------

def createPluginMenus (win) :
    "create plugin menu items, called during main window initalization"
    for mod in win.conf.plugin_list :
        if mod.title != "" :
           try :
              setupPluginMenu (win, mod)
           except :
              print (mod.title + " not loaded")

def createOnePluginMenu (win, title, module_name, cls_name, key) :
    "used by main window to create Grammar menu"
    mod = PluginData ()
    mod.title = title
    mod.module_name = module_name
    mod.cls_name = cls_name
    mod.key = key
    # mod.reread_menu = False
    # mod.reload_module = False
    setupPluginMenu (win, mod)

def setupPluginMenu (win, mod) :
    if mod.menu == None :
       # print ("ADD MENU", mod.title)
       mod.menu = win.addTopMenu (mod.title)
       # if mod.reread_menu :
       #    mod.menu.aboutToShow.connect (lambda : aboutToShowPluginMenu (win, mod))

    if mod.key != "" :
       win.plugin_map [mod.key] = mod

    # if not mod.reload_module :
       # print ("LOAD PLUGIN ON STARTUP", mod.title)
    mod.module = win.loadModule (mod.module_name)
    activatePlugin (win, mod)

def aboutToShowPluginMenu (win, mod) :
    # print ("ABOUT TO SHOW", mod.title)
    "refresh opening menu"
    win.reloadConfig ()

def activatePlugin (win, mod) :
    # extra parameter for CodePlugin
    win.current_mod = mod

    "call plugin class constructor"
    ctor = getattr (mod.module, mod.cls_name)
    mod.cls = ctor (win)

    win.current_mod = None

# --------------------------------------------------------------------------

def HtmlTree (tree, dom) :
    branch = TreeItem (tree)
    branch.obj = dom
    branch.setText (0, dom.tagName ())
    branch.setForeground (0, findColor ("blue"))

    branch.continue_func = lambda : HtmlItems (branch, dom)
    return branch

def HtmlItems (branch, dom) :
    for name in dom.attributeNames () :
        value = dom.attribute (name)
        node = TreeItem (branch)
        node.setText (0, name + "=" + value)
        node.setForeground (0, findColor ("orange"))

    item = dom.firstChild ()
    while not item.isNull () :
       HtmlTree (branch, item)
       item = item.nextSibling ()

# do not move HtmlTree to code_tree
# tools.py is used in standalone window.py (without code_tree)

# --------------------------------------------------------------------------

class WebWin (QWidget) :

    def __init__ (self, win) :
        super (WebWin, self).__init__ (win)
        self.win = win

        if use_webkit :
           self.view = QWebView (self)
        else :
           self.view = QWebEngineView (self)

        self.progress = 0

        self.view.loadFinished.connect (self.adjustLocation)
        self.view.titleChanged.connect (self.adjustTitle)
        self.view.loadProgress.connect (self.setProgress)
        self.view.loadFinished.connect (self.finishLoading)

        self.locationEdit = QLineEdit (self)
        self.locationEdit.setSizePolicy (QSizePolicy.Expanding,
                                         self.locationEdit.sizePolicy().verticalPolicy())
        self.locationEdit.returnPressed.connect (self.changeLocation)

        toolBar = QToolBar ()
        if use_webkit :
           toolBar.addAction (self.view.pageAction (QWebPage.Back))
           toolBar.addAction (self.view.pageAction (QWebPage.Forward))
           toolBar.addAction (self.view.pageAction (QWebPage.Reload))
           toolBar.addAction (self.view.pageAction (QWebPage.Stop))
        else :
           toolBar.addAction (self.view.pageAction (QWebEnginePage.Back))
           toolBar.addAction (self.view.pageAction (QWebEnginePage.Forward))
           toolBar.addAction (self.view.pageAction (QWebEnginePage.Reload))
           toolBar.addAction (self.view.pageAction (QWebEnginePage.Stop))
        toolBar.addWidget (self.locationEdit)

        layout = QVBoxLayout ()
        self.setLayout (layout)
        layout.addWidget (toolBar)
        layout.addWidget (self.view)

    def load (self, url) :
        self.view.load (url)

    def adjustLocation (self) :
        self.locationEdit.setText (str (self.view.url().toString()))

    def changeLocation (self) :
        url = QUrl.fromUserInput (self.locationEdit.text ())
        self.view.load (url)
        self.view.setFocus ()

    def adjustTitle (self) :
        if 0 < self.progress < 100:
           self.setWindowTitle ("%s (%s%%)" % (self.view.title(), self.progress))
        else:
           self.setWindowTitle (self.view.title())

    def setProgress (self, p) :
        self.progress = p
        self.adjustTitle ()

    def finishLoading (self) :
        self.progress = 100
        self.adjustTitle ()
        if use_webkit :
           self.showTree ()

    def showTree (self) :
        dom = self.view.page().mainFrame().documentElement()
        branch = HtmlTree (None, dom)
        branchContinue (branch)
        self.win.addNavigatorData (self, branch)

# https://github.com/Werkov/PyQt4/blob/master/examples/webkit/fancybrowser/fancybrowser.py

# --------------------------------------------------------------------------

class NameValue :
    def __init__ (self, name0, value0) :
       self.name = name0
       self.value = value0
       self.is_win_id = False

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
