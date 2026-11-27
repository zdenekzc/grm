#!/bin/env python

import os, sys, re
import tty, termios

# --------------------------------------------------------------------------

# http://github.com/magmax/python-readchar

LF = "\x0a"
CR = "\x0d"
SPACE = "\x20"
ESC = "\x1b"
TAB = "\x09"

# CTRL
CTRL_A = "\x01"
CTRL_B = "\x02"
CTRL_C = "\x03"
CTRL_D = "\x04"
CTRL_E = "\x05"
CTRL_F = "\x06"
CTRL_G = "\x07"
CTRL_H = "\x08"
CTRL_I = TAB
CTRL_J = LF
CTRL_K = "\x0b"
CTRL_L = "\x0c"
CTRL_M = CR
CTRL_N = "\x0e"
CTRL_O = "\x0f"
CTRL_P = "\x10"
CTRL_Q = "\x11"
CTRL_R = "\x12"
CTRL_S = "\x13"
CTRL_T = "\x14"
CTRL_U = "\x15"
CTRL_V = "\x16"
CTRL_W = "\x17"
CTRL_X = "\x18"
CTRL_Y = "\x19"
CTRL_Z = "\x1a"

# common
BACKSPACE = "\x7f"

# cursors
UP = "\x1b\x5b\x41"
DOWN = "\x1b\x5b\x42"
LEFT = "\x1b\x5b\x44"
RIGHT = "\x1b\x5b\x43"

# navigation keys
INSERT = "\x1b\x5b\x32\x7e"
SUPR = "\x1b\x5b\x33\x7e"
HOME = "\x1b\x5b\x48"
END = "\x1b\x5b\x46"
PAGE_UP = "\x1b\x5b\x35\x7e"
PAGE_DOWN = "\x1b\x5b\x36\x7e"

# funcion keys
F1 = "\x1b\x4f\x50"
F2 = "\x1b\x4f\x51"
F3 = "\x1b\x4f\x52"
F4 = "\x1b\x4f\x53"
F5 = "\x1b\x5b\x31\x35\x7e"
F6 = "\x1b\x5b\x31\x37\x7e"
F7 = "\x1b\x5b\x31\x38\x7e"
F8 = "\x1b\x5b\x31\x39\x7e"
F9 = "\x1b\x5b\x32\x30\x7e"
F10 = "\x1b\x5b\x32\x31\x7e"
F11 = "\x1b\x5b\x32\x33\x7e"
F12 = "\x1b\x5b\x32\x34\x7e"

# SHIFT+_
SHIFT_TAB = "\x1b\x5b\x5a"

# other
CTRL_ALT_SUPR = "\x1b\x5b\x33\x5e"

# ALT+_
ALT_A = "\x1b\x61"

# CTRL+ALT+_
CTRL_ALT_A = "\x1b\x01"

# aliases
ENTER = LF
DELETE = SUPR

INTERRUPT_KEYS = [CTRL_C]

def readchar() -> str:
    """Reads a single character from the input stream.
    Blocks until a character is available."""

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr( fd)
    term = termios.tcgetattr (fd)
    try:
        term [3] &= ~(termios.ICANON | termios.ECHO | termios.IGNBRK | termios.BRKINT)
        termios.tcsetattr (fd, termios.TCSAFLUSH, term)

        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr (fd, termios.TCSADRAIN, old_settings)
    return ch


def readkey() -> str:
    """Get a keypress. If an escaped key is pressed, the full sequence is
    read and returned as noted in `_posix_key.py`."""

    c1 = readchar()

    if c1 in INTERRUPT_KEYS:
       raise KeyboardInterrupt

    if c1 != "\x1B":
        return c1

    c2 = readchar()
    if c2 not in "\x4F\x5B":
        return c1 + c2

    c3 = readchar()
    if c3 not in "\x31\x32\x33\x35\x36":
        return c1 + c2 + c3

    c4 = readchar()
    if c4 not in "\x30\x31\x33\x34\x35\x37\x38\x39":
        return c1 + c2 + c3 + c4

    c5 = readchar()
    return c1 + c2 + c3 + c4 + c5

# --------------------------------------------------------------------------


class FindLocation :

   def __init__ (self) :
      self.directory = ""
      self.location = ""
      self.dbg = ""

   def modifyLine (self, line, keyword) :
       self.dbg = keyword
       pattern = "(.*\s)?(\S*):(\d\d*)(:|\.)(.*)"
       # pattern = "(.*\s)?(\S*):(\d\d*)(:|\.)(\d\d*)(-.*)?:(\s*" + keyword + ":)(.*)"
       pattern = "(.*\s)?(\S*):(\d\d*)(:|\.)(\d\d*)(-(\d\d*)\.(\d\d*))?:(\s*" + keyword + ":)(.*)"
       m = re.search (pattern, line)
       if m :
          self.location = os.path.join (self.directory, m.group (2)) + ":" + m.group (3)
          self.dbg = "FOUND"

   def directoryLine (self, line) :
       pattern = "Entering directory '([^']*)'"
       m = re.search (pattern, line)
       if m :
          self.directory = m.group (1)

   # -- Python trace --

   def pythonLine (self, line) :
       pattern = "  File (.*), line ([0-9]*)(, in (.*))?"
       m = re.match (pattern, line)
       if m :
          fileName = m.group (1)
          line =  m.group (2)
          if fileName.startswith ('"') and fileName.endswith ('"') :
             fileName = fileName [ 1 : -1 ]
          self.location = fileName + ":" + line

   def findLocation (self, line) :
       self.location = ""
       self.dbg = ""

       if line.find ("fatal error:") >= 0 :
          self.modifyLine (line, "fatal error") # clang
       elif line.find ("error:") >= 0 :
          self.modifyLine (line, "error")
       elif line.find ("warning:") >= 0 :
          self.modifyLine (line, "warning")
       elif line.find ("debug:") >= 0 :
          self.modifyLine (line, "debug")
       elif line.find ("info:") >= 0 :
          self.modifyLine (line, "info")
       elif line.find ("Entering directory ") >= 0 :
          self.directoryLine (line)
       elif line.find ("Leaving directory ") >= 0 :
          self.directory = ""
       elif line.startswith ("  File ") :
          self.pythonLine (line)

       return self.location

# --------------------------------------------------------------------------

def send_line (line_num, col_num, width, line) :
    "line_num, col_num from 0"

    """
    print ("\033[" + str (line_num+1) + ";1H", sep = "", end = "") # go to line
    line = line [ col_num : ]
    while len (line) < width :
       line = line + " "
    line = line [ : width]
    print (line, end = "")
    return
    """

    inx = 0
    cnt = len (line)

    attr_start = -1
    attr_end = -1

    text_start = -1
    text_end = -1

    col = 0

    while inx < cnt :
       if text_start == -1 :
          while inx < cnt and line [inx] == '\033' :
             attr_start = inx
             while inx < cnt and line [inx] != 'm' :
                inx = inx + 1
             inx = inx + 1
             attr_end = inx

       if inx < cnt :
          if col == col_num :
             text_start = inx
          if line [inx] == '\t' :
             add = 0
             while col % 8 != 0 :
                col = col + 1
                add = add + 1
             if add != 0 :
                line = line [ : inx] + (add+1) * ' ' + line [inx+1 : ]
                cnt = len (line)
          else :
             col = col + 1
          inx = inx + 1
          if col == col_num + width :
             text_end = inx

    rest = col_num + width - col

    if text_end == -1 :
       text_end = cnt

    print ("\033[" + str (line_num+1) + ";1H", sep = "", end = "") # go to line
    if attr_start != -1 :
       print (line [attr_start : attr_end], end = "")
       # print (attr_start, " ", attr_end, " ", sep = "", end = "")
       # for c in line [attr_start : attr_end] :
       #     print (hex (ord (c)), " ", sep= "", end = "")
    if text_start != -1 :
       print (line [text_start : text_end], end = "")
    if rest > 0 :
       print ("\033[0m", rest * ' ', sep="", end = "")

# --------------------------------------------------------------------------

def clean_line (line) :
    result = ""
    cnt = len (line)
    inx = 0
    while inx < cnt :
       while inx < cnt and line [inx] == '\033' :
          while inx < cnt and line[inx] != 'm' :
             inx = inx + 1
          inx = inx + 1
       if inx < cnt :
          result= result + line [inx]
          inx = inx + 1
    return result

# --------------------------------------------------------------------------

lines = [ ]

def display () :
   top = 0
   left = 0
   selected = 0
   cnt = len (lines)

   fd = sys.stdin.fileno ()

   locObj = FindLocation ()

   search_down = False
   search_up = False

   msg = ""
   note = ""

   done = False
   while not done :
       location = ""

       # h, w = termios.tcgetwinsize (fd)
       w, h = os.get_terminal_size()
       h = h-1

       again = True
       while again :

          print ("\033[0J", end="") # clear screen
          print ("\033[1;1H", sep = "", end = "") # go to line
          print ("\033[0m", sep = "", end = "") # normal text

          inx = 0
          while inx < h :
              if top + inx < cnt :
                 text = lines [top + inx]
              else :
                 text = ""

              if inx == selected :
                 text = clean_line (text)
                 location = locObj.findLocation (text)
                 text = "\033[37;41m" + text # white on red
                 text = text + "\033[0m" # normal text

              send_line (inx, left, w, text)
              inx = inx + 1

          text = "       \tscreen " + str (w) + " x " + str (h) + " top = " + str (top)
          text = text + " left = " + str (left) + " selected = " + str (selected)
          text = text + " " + msg + " " + note + " " + locObj.dbg + " " + location
          text = "\033[37;44m" + text # white on blue
          send_line (h, 0, w, text)

          print ("", sep="", end="", flush=True)

          again = False
          if search_up :
             if location != "" :
                search_up = False
             else :
                if selected > 0 :
                   selected = selected - 1
                else :
                   top = top - 1
                if top >= 0 :
                   again = True
          if search_down :
             if location != "" :
                search_down = False
             else :
                if selected < h-1 :
                   selected = selected + 1
                else :
                   top = top + 1
                if top < cnt-h :
                   again = True

       key = readkey ()
       note = ""
       msg = "KEY ="
       for c in key :
          msg = msg + " " + hex (ord (c))

       if key == 'q' :
          done = True

       if key == F7 :
          note = "SEARCH UP"
          search_up = True
          if selected > 0 :
             selected = selected - 1
          else :
             top = top - 1

       if key == F8 :
          note = "SEARCH DOWN"
          search_down = True
          if selected < h-1 :
             selected = selected + 1
          else :
             top = top + 1

       if key == 'u' or key == UP :
          if selected > 0 :
             selected = selected - 1
          else :
             top = top - 1
          note = "UP"
       if key == 'd' or key == DOWN :
          if selected < h-1 :
             selected = selected + 1
          else :
             top = top + 1
          note = "DOWN"
       if key == 'l' or key == LEFT :
          left = left - 1
          note = "LEFT"
       if key == 'r' or key == RIGHT :
          left = left + 1
          note = "RIGHT"
       if key == 'h' or key == HOME :
          top = 0
          left = 0
          selected = 0
          note = "HOME"
       if key == 'e' or key == END :
          top = cnt - h
          selected = h-1
          note = "END"
       if key == 'p' or key == PAGE_UP :
          top = top - h
          note = "PAGE UP"
       if key == 'n' or key == PAGE_DOWN :
          top = top + h
          note = "PAGE DOWN"
       if key == F5 :
          top = top - 1
          note = "SCROLL UP"
       if key == F6 :
          top = top + 1
          note = "SCROLL DOWN"

       if key == ENTER :
          if location != "" :
             os.system ("mcedit " + location)

       if top > cnt-h :
          top = cnt-h
       if top < 0 :
          top = 0

       if left < 0 :
          left = 0

       if selected > h-1 :
          selected = h-1
       if selected < 0 :
          selected = 0

# --------------------------------------------------------------------------

if 1 :
   # NO for line in sys.stdin :
   for line in open (0, "r") :
       line = line.rstrip ()
       lines.append (line)
       # print (line, end = "")
   sys.stdin.close ()
   sys.stdin = open ("/dev/tty", "r")

if 0 :
   for line in open (3, "r") :
       line = line.rstrip ()
       lines.append (line)

if 0 :
   line = 4*"0123456789"
   lines = ["abc", "def", "klm"] + 5 * [ line ] + ["xyz"] + [line]

if 0 :
   for line in open ("test.txt", "r") :
       line = line.rstrip ()
       lines.append (line)

if 0 :
   print (80*'-')
   for line in lines :
       print (line)
   print (80*'-')

try :
    display ()
finally:
    print ("\033[0m")

# --------------------------------------------------------------------------

"""
for line in open (3, "r") :

cat test.txt | python filter.py 3<&0- </dev/tty
valac lexer.vala pas_parser.vala  2>&1 | python filter.py 3<&0- </dev/tty
valac lexer.vala pas_parser.vala --color 2>&1 | python filter.py 3<&0- </dev/tty

last character in 3<&0- is minus
http://www.gnu.org/software/bash/manual/html_node/Redirections.html#Moving-File-Descriptors

"""

"""
gcc ... --color-always | less -R
less command, open keybord, file ttyin.c
https://askubuntu.com/questions/678915/whats-the-difference-between-and-in-bash
"""

"""
for line in open (0, "r") :
NOT for line in sys.stdin :

sys.stdin.close ()
sys.stdin = open ("/dev/tty", "r")

clear ; valac lexer.vala --color 2>&1 | python filter.py
"""

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
