# tools.py

import os, sys, re, subprocess, traceback, importlib, fcntl, ctypes

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

try :
   from PyQt5.QtWebEngine import *
   from PyQt5.QtWebEngineWidgets import *
   use_webengine = True
except :
   use_webengine = False

from util import *

# --------------------------------------------------------------------------

# ANSI CSI escape: \x1b[<params><final>. We style only Select-Graphic-Rendition
# (the final byte "m"); other CSI codes — cursor movement, erase-in-line etc.
# — are recognized and stripped so they don't show up as garbage.
ANSI_CSI_RE = re.compile (r"\x1b\[([0-9;?]*)([A-Za-z])")

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

       self.work_dir = ""
       self.env_dict = { }
       self.stopClear = 0

       self.red = findColor ("red")
       self.green = findColor ("green")
       self.blue = findColor ("blue")
       self.gray = findColor ("gray")
       self.norm = findColor ("ink")
       self.brown = findColor ("brown")
       self.orange = findColor ("orange")
       self.yellow = findColor ("yellow")
       self.cornflowerblue = findColor ("cornflowerblue")

       # ANSI SGR color maps. Picked so output is legible on a light editor
       # background (e.g. "white" foreground -> ink so it's visible).
       self._ansi_basic = {
           30: self.norm,                 # black  -> default ink
           31: self.red,
           32: self.green,
           33: self.brown,                # dim yellow -> brown (visible)
           34: self.blue,
           35: findColor ("darkMagenta"),
           36: findColor ("darkCyan"),
           37: self.gray,                 # white on white bg -> gray
       }
       self._ansi_bright = {
           90: self.gray,
           91: self.red,
           92: self.green,
           93: self.orange,
           94: self.cornflowerblue,
           95: findColor ("magenta"),
           96: findColor ("cyan"),
           97: self.norm,                 # bright white -> ink
       }

   # -- redirect output --

   def redirectOutput (self) :
       sys.stdout = Redirect (self, sys.stdout)
       sys.stderr = Redirect (self, sys.stderr)

   def stopRedirect (self) :
       global stop_redirect
       stop_redirect = True

   # -- fd-level capture (Unix) --
   #
   # Catches writes that bypass Python's sys.stdout — e.g. C printf and
   # std::cout from the in-process JIT or ctypes calls.  Wrap a block of
   # foreign-code execution between startCaptureFd() / stopCaptureFd().

   def startCaptureFd (self) :
       if getattr (self, "_cap_active", False) :
          return
       sys.stdout.flush ()
       sys.stderr.flush ()

       # silence Python-level Redirect so prints aren't emitted twice (once via
       # fd 1 -> pipe and again via Redirect.put -> commandOneLine)
       global stop_redirect
       self._cap_save_stop = stop_redirect
       stop_redirect = True

       self._cap_orig_stdout = os.dup (1)
       self._cap_orig_stderr = os.dup (2)

       self._cap_read_fd, self._cap_write_fd = os.pipe ()
       flags = fcntl.fcntl (self._cap_read_fd, fcntl.F_GETFL)
       fcntl.fcntl (self._cap_read_fd, fcntl.F_SETFL, flags | os.O_NONBLOCK)

       os.dup2 (self._cap_write_fd, 1)
       os.dup2 (self._cap_write_fd, 2)

       self._cap_line_buf = ""
       self._cap_notifier = QSocketNotifier (self._cap_read_fd, QSocketNotifier.Read, self)
       self._cap_notifier.activated.connect (lambda *_args : self._drainCaptureFd ())
       self._cap_active   = True

   def _drainCaptureFd (self) :
       if not getattr (self, "_cap_active", False) :
          return
       if getattr (self, "_cap_in_drain", False) :
          # processEvents() / commandOneLine can re-enter via the notifier;
          # ignore re-entry — the outer call's read loop will collect everything.
          return
       self._cap_in_drain = True
       try :
          text = self._cap_line_buf
          while True :
             try :
                chunk = os.read (self._cap_read_fd, 4096)
             except (BlockingIOError, OSError) :
                break
             if not chunk :
                break
             text = text + chunk.decode ("utf-8", "replace")
          while True :
             inx = text.find ("\n")
             if inx < 0 :
                break
             self.commandOneLine (text [:inx])
             text = text [inx + 1 :]
          self._cap_line_buf = text
          self.ensureCursorVisible ()
       finally :
          self._cap_in_drain = False

   def stopCaptureFd (self) :
       if not getattr (self, "_cap_active", False) :
          return

       # ask libc to flush its FILE* buffers before we tear down the pipe
       try :
          ctypes.CDLL (None).fflush (None)
       except OSError :
          pass

       # restore real fds first so any later prints go to the terminal again
       os.dup2 (self._cap_orig_stdout, 1)
       os.dup2 (self._cap_orig_stderr, 2)
       os.close (self._cap_orig_stdout)
       os.close (self._cap_orig_stderr)
       os.close (self._cap_write_fd)

       # drain whatever is still in the pipe
       self._drainCaptureFd ()

       if self._cap_line_buf != "" :
          self.commandOneLine (self._cap_line_buf)
          self._cap_line_buf = ""

       self._cap_notifier.setEnabled (False)
       self._cap_notifier.deleteLater ()
       os.close (self._cap_read_fd)

       global stop_redirect
       stop_redirect = self._cap_save_stop
       self._cap_active = False

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

   # -- ANSI SGR renderer --
   #
   # Many CLI tools (gcc, grep --color, ls --color, lldb, cmake, podman …)
   # emit ANSI CSI escape sequences to color their output. Programs usually
   # detect a real TTY and skip colors when writing to a QProcess pipe —
   # runCommandString() therefore sets FORCE_COLOR / CLICOLOR_FORCE to opt
   # in. _insertAnsi() translates those sequences into Qt char formats.

   def _applyAnsiCodes (self, fmt, codes) :
       i = 0
       while i < len (codes) :
           c = codes [i]
           if c == 0 :                    # reset
              fmt.setForeground (self.norm)
              fmt.setFontWeight (QFont.Normal)
              fmt.setFontItalic (False)
              fmt.setFontUnderline (False)
           elif c == 1 :                  # bold
              fmt.setFontWeight (QFont.Bold)
           elif c == 3 :                  # italic
              fmt.setFontItalic (True)
           elif c == 4 :                  # underline
              fmt.setFontUnderline (True)
           elif c == 22 : fmt.setFontWeight  (QFont.Normal)
           elif c == 23 : fmt.setFontItalic  (False)
           elif c == 24 : fmt.setFontUnderline (False)
           elif c == 39 : fmt.setForeground  (self.norm)
           elif c in self._ansi_basic :
              fmt.setForeground (self._ansi_basic [c])
           elif c in self._ansi_bright :
              fmt.setForeground (self._ansi_bright [c])
           elif c == 38 and i + 2 < len (codes) and codes [i + 1] == 5 :
              # 256-color: 38;5;N
              fmt.setForeground (self._ansi256 (codes [i + 2]))
              i += 2
           elif c == 38 and i + 4 < len (codes) and codes [i + 1] == 2 :
              # Truecolor: 38;2;R;G;B
              fmt.setForeground (QColor (codes [i + 2], codes [i + 3], codes [i + 4]))
              i += 4
           # 40-47 / 100-107 (background) and others are ignored on purpose.
           i += 1

   def _ansi256 (self, n) :
       if n < 8 :
          return self._ansi_basic.get (30 + n, self.norm)
       if n < 16 :
          return self._ansi_bright.get (90 + (n - 8), self.norm)
       if n < 232 :
          n = n - 16
          levels = [0, 95, 135, 175, 215, 255]
          return QColor (levels [(n // 36) % 6],
                         levels [(n // 6) % 6],
                         levels [n % 6])
       v = 8 + (n - 232) * 10
       return QColor (v, v, v)

   def _insertAnsi (self, cursor, text) :
       "Insert `text` honoring ANSI SGR escapes; non-SGR CSI is stripped."
       fmt = QTextCharFormat ()
       fmt.setForeground (self.norm)
       pos = 0
       for m in ANSI_CSI_RE.finditer (text) :
           if m.start () > pos :
              cursor.setCharFormat (fmt)
              cursor.insertText (text [pos : m.start ()])
           if m.group (2) == "m" :
              params = m.group (1)
              if params == "" :
                 codes = [0]
              else :
                 codes = [int (c) for c in params.split (";") if c != ""]
                 if not codes :
                    codes = [0]
              self._applyAnsiCodes (fmt, codes)
           pos = m.end ()
       if pos < len (text) :
          cursor.setCharFormat (fmt)
          cursor.insertText (text [pos :])
       # Reset cursor format so the following "\n" and next line start clean.
       cursor.setCharFormat (QTextCharFormat ())

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
       pattern = r"(.*\s)?(\S*):(\d\d*)(:(\d\d*))?:(\s*" + keyword + ":)(.*)"
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

       # If the line carries ANSI SGR escapes (from gcc, grep --color, ls,
       # lldb, cmake, podman, …) honor them verbatim and skip the keyword
       # heuristics below — the tool's own coloring is more specific.
       if "\x1b[" in line :
          self._insertAnsi (cursor, line)
          cursor.insertText ("\n")
          return

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

   # -- run external command --

   def runCommandString (self, cmd) :
       self.process = QProcess (self.win)

       if self.work_dir != "" :
          self.process.setWorkingDirectory (self.work_dir)

       env = QProcessEnvironment.systemEnvironment () # important
       for name in self.env_dict :
           value = self.env_dict [name]
           env.insert (name, value)
           # print ("SET", name + "=" + value)

       # Opt the subprocess into colored output even though we're a pipe.
       # Broadly respected: FORCE_COLOR (Node + many JS/Rust CLIs),
       # CLICOLOR_FORCE (BSD ls, fd, bat). gcc needs -fdiagnostics-color=always
       # on the command line; set GCC_COLORS so the palette is sensible when
       # the user does turn it on.
       if not env.contains ("FORCE_COLOR")    : env.insert ("FORCE_COLOR", "1")
       if not env.contains ("CLICOLOR_FORCE") : env.insert ("CLICOLOR_FORCE", "1")
       if not env.contains ("GCC_COLORS") :
          env.insert ("GCC_COLORS",
              "error=01;31:warning=01;35:note=01;36:caret=01;32:"
              "locus=01:quote=01")

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

   def stop (self) :
       self.process.terminate ()

   def clearOutput (self) :
       if self.stopClear <= 0 :
          self.clear ()

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
