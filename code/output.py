
# output.py

from __future__ import print_function

import sys, time
from io import StringIO, BytesIO

from input import quoteString

sectionGenerator = None

# jump marks
sourceMark = 1
pythonMark = 2
codeMark = 3
headerMark = 4

parserMark = 2
productMark = 3

# --------------------------------------------------------------------------

use_python3 = ( sys.version_info >= (3,) ) # do not import util

class Output (object) :

   def __init__ (self) :
       self.redirect = None
       self.outputFile = sys.stdout
       self.outputStack = [ ]
       self.sectionStack = [ ]
       self.sections = None
       self.console = False

       self.indentation = 0
       self.addSpace = False
       self.extraSpace = False
       self.startLine = True
       self.addEmptyLine = False
       self.noEmptyLine = False

       # self.initialize ()

   # def initialize (self) :

   # -----------------------------------------------------------------------

   def open (self, fileName, with_sections = False, with_simple = False, with_mark = 0) :

       # if with_mark != 0 :
       #    if not with_sections and not with_simple :
       #       with_sections = True

       # NO self.initialize ()

       if (with_sections or with_simple) and sectionGenerator != None :
          self.sections = sectionGenerator.createSections (fileName, with_simple)
          self.sections.open ()
       else :
          if fileName == "" or  fileName == "-":
             self.console = True
             self.outputFile = sys.stdout
          else :
             self.outputFile = open (fileName, "w")

       self.setJumpMark (with_mark)

   def close (self) :
       if self.sections != None :
          self.sections.close ()
       else :
          if not self.console :
             self.outputFile.close ()
       self.outputFile = sys.stdout

   def write (self, txt) :
       if self.sections != None :
          self.sections.write (txt)
       else :
          self.outputFile.write (txt)

   def openFile (self, fileName, with_sections = False, with_simple = False, with_mark = 0) :
       self.open (fileName, with_sections = with_sections,  with_simple = with_simple, with_mark = with_mark)

   # -----------------------------------------------------------------------

   def openString (self) :
       self.outputStack.append (self.outputFile) # remember outputFile
       self.sectionStack.append (self.sections) # change sections to None

       if use_python3 :
          self.outputFile = StringIO ()
       else :
          self.outputFile = BytesIO ()

       self.sections = None # necessary, otherwise text is added directly to editor

   def closeString (self) :
       result = self.outputFile.getvalue ()
       self.outputFile.close ()

       self.outputFile = self.outputStack.pop () # restore outputFile
       self.sections = self.sectionStack.pop () # restore outputFile
       return result

   # -----------------------------------------------------------------------

   def indent (self) :
       if self.redirect != None :
          self.redirect.indent ()
       self.indentation = self.indentation + 3

   def unindent (self) :
       if self.redirect != None :
          self.redirect.unindent ()
       self.indentation = self.indentation - 3

   def incIndent (self) :
       self.indent ()

   def decIndent (self) :
       self.unindent ()

   # -----------------------------------------------------------------------

   # put

   def beforePut (self) :
       if self.startLine :
          if self.addEmptyLine and not self.noEmptyLine :
             if self.redirect == None :
                self.write ("\n")
          self.write (" " * self.indentation)
          self.startLine = False
          self.addEmptyLine = False
          self.noEmptyLine = False

   def put (self, txt) :
       if txt != "" :
          self.beforePut ()
          if self.redirect != None :
             self.redirect.put (txt)
          else :
             self.write (txt)

   def putEol (self) :
       self.startLine = True
       self.addSpace = False
       self.extraSpace = False
       if self.redirect != None :
          self.redirect.putEol ()
       else :
          self.write ("\n")

   def putCondEol (self) :
       if not self.startLine :
          if self.redirect == None :
             self.putEol ()

   def putLn (self, txt = "") :
       if txt != "":
          self.put (txt)
       self.putEol ()

   # -----------------------------------------------------------------------

   # send

   def isLetterOrDigit (self, c) :
       return c >= 'A' and c <= 'Z' or c >= 'a' and c <= 'z' or c >= '0' and c <= '9' or c == '_'

   def beforeSend (self, txt) :
       if self.startLine :
          self.addSpace = False
          self.extraSpace = False

       c = txt [0]
       if c == ',' or c == ';' or c == ')' or c == ']' :
          self.extraSpace = False
       if not self.isLetterOrDigit (c) :
          self.addSpace = False

       if self.addSpace or self.extraSpace :
          self.put (" ")
          # txt = " " + txt

   def afterSend (self, txt) :
       c = txt [-1]
       self.addSpace = self.isLetterOrDigit (c)
       self.extraSpace = c != '(' and c != '['

   def send (self, txt) :
       if txt != "" :
          if self.redirect != None :
             self.redirect.send (txt)
          else :
             self.beforeSend (txt)
             self.put (txt)
             self.afterSend (txt)

   def sendChr (self, txt) :
       self.send (quoteString (txt, "'"))

   def sendStr (self, txt) :
       self.send (quoteString (txt))

   # -----------------------------------------------------------------------

   def no_space (self) :
       if self.redirect != None :
          self.redirect.no_space ()
       else :
          self.extraSpace = False

   def new_line (self) :
       if self.redirect != None :
          self.redirect.new_line ()
       else :
          self.putCondEol ()

   def empty_line (self) :
       if self.redirect != None :
          self.redirect.empty_line ()
       else :
          self.putCondEol ()
          self.addEmptyLine = True

   def no_empty_line (self) :
       if self.redirect != None :
          self.redirect.no_empty_line ()
       else :
          self.noEmptyLine = True

   # -----------------------------------------------------------------------

   def style_indent (self) :
       if self.redirect != None :
          self.redirect.style_indent ()
       else :
          self.putCondEol ()
          self.indent ()

   def style_unindent (self) :
       if self.redirect != None :
          self.redirect.style_unindent ()
       else :
          self.unindent ()
          self.putCondEol ()

   def style_no_space (self) :
       self.no_space ()

   def style_new_line (self) :
       self.new_line ()

   def style_empty_line (self) :
       self.empty_line ()

   def style_no_empty_line (self) :
       self.no_empty_line ()

   # -----------------------------------------------------------------------

   # sections

   def setSections (self, sections_param) :
       self.sections = sections_param

   def openSection (self, obj) :
       if self.sections != None and self.redirect == None:
          self.sections.openSection (obj)

   def closeSection (self) :
       if self.sections != None and self.redirect == None :
          self.sections.closeSection ()

   def simpleSection (self, obj) :
       if self.sections != None and self.redirect == None :
          self.sections.simpleSection (obj)

   def setInk (self, ink) :
       if self.sections != None and self.redirect == None :
          self.sections.setInk (ink)

   def setPaper (self, paper) :
       if self.sections != None and self.redirect == None :
          self.sections.setPaper (paper)

   def addToolTip (self, text, tooltip) :
       if self.sections != None and self.redirect == None :
          self.sections.addToolTip (text, tooltip)

   def addDefinition (self, text, defn) :
       if self.sections != None and self.redirect == None :
          self.beforeSend (text)
          self.beforePut ()
          self.sections.addDefinition (text, defn)
          self.afterSend (text)
       else :
          self.send (text)

   def addUsage (self, text, usage) :
       if self.sections != None  and self.redirect == None :
          if text != "" :
             self.beforeSend (text)
          self.beforePut ()
          self.sections.addUsage (text, usage)
          if text != "" :
             self.afterSend (text)
       else :
          self.send (text)

   def setJumpMark (self, mark) :
       if self.sections != None  and self.redirect == None :
          self.sections.jumpMark = mark

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
