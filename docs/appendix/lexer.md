# Lexical Analyzer

A program (in the Python language) reading the individual characters of
source text written in the C language
and creating a sequence of lexical symbols.

The lexical symbols are identifiers, integers, real numbers, string
constants in single or double quotes, and separators.

The individual lexical symbols are read by the **nextToken** function.
The kind of the symbol is stored in the variable **token**
(*identifier, number, real_number, character_literal, string_literal,
separator*).
The concrete value is stored in the variable **tokenText**.

http://gitlab.fjfi.cvut.cz/culikzde/simple-view/-/blob/master/tutorial/mini-parser/mini_lexer.py
http://gitlab.fjfi.cvut.cz/culikzde/simple-view/-/blob/master/tutorial/easy-grammar/easy_lexer.py

A lexer in the C language: https://gitlab.fjfi.cvut.cz/culikzde/c-parser/-/blob/master/lex.cc

```python
from __future__ import print_function
import os

class LexerException (Exception) :
   pass

class Lexer (object) :
   eos = 0 # end of source
   identifier = 1
   number = 2 # integer
   real_number = 3 # float or double
   character_literal = 4 # string with sigle quotes
   string_literal = 5 # double quoted string
   separator = 6

   def __init__ (self) :
       super (Lexer, self).__init__ ()
       self.reset ()

   def reset (self) :
       self.fileName = ""
       self.source = ""
       self.sourceLen = 0

       self.charLineNum = 1
       self.charColNum = 1
       self.charByteOfs = 0

       self.tokenLineNum = 1
       self.tokenColNum = 1
       self.tokenByteOfs = 0

       self.ch = '\0'
       self.token = self.eos
       self.tokenText = ""
       self.tokenValue = ""

   # -----------------------------------------------------------------------

   def openFile (self, fileName) :
       self.reset ()
       self.fileName = os.path.abspath (fileName)
       f = open (self.fileName, "r")
       self.source = f.read ()
       self.sourceLen = len (self.source)
       self.nextChar () # read first character
       self.nextToken () # read first token

   def close (self) :
       pass

   # -----------------------------------------------------------------------

   def nextChar (self) :
       if self.charByteOfs < self.sourceLen :
          self.ch = self.source [self.charByteOfs]
          self.charByteOfs = self.charByteOfs + 1
          if self.ch == '\n' :
             self.charLineNum = self.charLineNum + 1
             self.charColNum = 0
          elif self.ch != '\r' :
             self.charColNum = self.charColNum + 1
       else :
          self.ch = '\0'

   # -----------------------------------------------------------------------

   def backStep (self) :
       self.tokenColNum = self.tokenColNum - 1
       self.tokenByteOfs = self.tokenByteOfs - 1

   def getPosition (self) :
       txt = self.fileName + ":" + str (self.tokenLineNum) + ":" + str (self.tokenColNum)
       return txt

   def info (self, text) :
       print (self.getPosition () + ": info: " + text)

   def warning (self, text) :
       print (self.getPosition () + ": warning: " + text)

   def error (self, text) :
       raise LexerException (self.getPosition () + ": error: " + text + ", tokenText=" + self.tokenText)

   # -----------------------------------------------------------------------

   def isLetter (self, c) :
       return c >= 'A' and c <= 'Z' or c >= 'a' and c <= 'z' or c == '_'

   def isDigit (self, c) :
       return c >= '0' and c <= '9'

   def isLetterOrDigit (self, c) :
       return self.isLetter (c) or self.isDigit (c)

   # -----------------------------------------------------------------------

   def comment_eol (self) :
       txt = ""

       while self.ch != '\0' and self.ch != '\r' and self.ch != '\n' :
          txt += self.ch
          self.nextChar ()

       self.comment_directive (txt)

   def comment_two_marks (self, mark1, mark2) :
       prev = ' '
       while self.ch != '\0' and not (prev == mark1 and self.ch == mark2) :
          prev = self.ch
          self.nextChar ()
       if self.ch == mark2 :
          self.nextChar () # skip mark2
       else :
          self.error ("Unterminated comment")

   # -----------------------------------------------------------------------

   def checkDigit (self) :
       if not self.isDigit (self.ch) :
          self.error ("Digit expected")

   def digits (self) :
       while self.isDigit (self.ch) :
          self.tokenText = self.tokenText + self.ch
          self.nextChar ()

   # -----------------------------------------------------------------------

   def numericToken (self) :
       self.token = self.number
       self.digits ()
       if self.ch == '.' :
          self.decimalToken ()
          self.token = self.real_number
          self.tokenText = self.tokenText + self.ch # store '.'
          self.nextChar () # skip '.'
          self.checkDigit ()
          self.digits ()
       if self.ch == 'e' or self.ch == 'E' :
          self.token = self.real_number
          self.tokenText = self.tokenText + self.ch # store 'e'
          self.nextChar () # skip 'e'
          if self.ch == '+' or self.ch == '-' :
             self.tokenText = self.tokenText + self.ch # store '+' or '-'
             self.nextChar () # skip '+' or '-'
          self.checkDigit ()
          self.digits ()

   # -----------------------------------------------------------------------

   def stringChar (self) :
       if self.ch != '\\' :
          c = self.ch
          self.nextChar ()
          return c
       else :
          self.nextChar () # skip backslash
          c = self.ch
          self.nextChar ()
          return c

   # -----------------------------------------------------------------------

   def nextToken (self) :
       self.token = self.eos
       self.tokenText = ""

       slash = False
       whiteSpace = True

       while whiteSpace and self.ch != '\0' :
          while self.ch != '\0' and self.ch <= ' ' :
             self.nextChar ()

          whiteSpace = False
          if self.ch == '/' :
             self.nextChar () # skip '/'
             if self.ch == '/' :
                self.nextChar () # skip '/'
                self.comment_eol ()
                whiteSpace = True # check again for white space
             elif self.ch == '*' :
                self.nextChar () # skip '*'
                self.comment_two_marks ('*', '/')
                whiteSpace = True # check again for white space
             else :
                slash = True # produce '/' token

       self.tokenLineNum = self.charLineNum
       self.tokenColNum = self.charColNum
       self.tokenByteOfs = self.charByteOfs

       if slash :
          self.token = self.separator
          self.tokenText = '/'
          self.backStep ()
          self.processSeparator ()

       elif self.ch == '\0' :
          self.token = self.eos

       elif self.isLetter (self.ch) :
          self.token = self.identifier
          while self.isLetterOrDigit (self.ch) :
             self.tokenText = self.tokenText + self.ch
             self.nextChar ()

       elif self.isDigit (self.ch) :
          self.numericToken ()

       elif self.ch == '\'' :
          self.token = self.character_literal
          self.nextChar ()
          while self.ch != '\0' and self.ch != '\r' and self.ch != '\n' and self.ch != '\'' :
             self.tokenText = self.tokenText + self.stringChar ()
          if self.ch != '\'' :
             self.error ("Unterminated string")
          self.nextChar ()

       elif self.ch == '\"' :
          self.token = self.string_literal
          self.nextChar ()
          while self.ch != '\0' and self.ch != '\r' and self.ch != '\n' and self.ch != '\"' :
             self.tokenText = self.tokenText + self.stringChar ()
          if self.ch != '\"' :
             self.error ("Unterminated string")
          self.nextChar ()

       else :
          self.token = self.separator
          self.tokenText = self.ch
          self.nextChar ()
          self.processSeparator ()

       if self.token == self.identifier :
          "convert identifier to keyword"
          self.lookupKeyword ()

   def lookupKeyword (self) :
       pass

   def processSeparator (self) :
       if self.tokenText == "<" or self.tokenText == ">" :
          if self.ch == "=" :
             self.tokenText = self.tokenText + self.ch
             self.nextChar ()
```

Literature: Chapter 4.1 http://inf.ethz.ch/personal/wirth/CompilerConstruction/CompilerConstruction1.pdf
