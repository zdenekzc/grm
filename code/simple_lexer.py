
# simple_lexer.py

import os

# --------------------------------------------------------------------------

fileNames = [ "" ] # list of file names, index 0 ... empty file name

def indexToFileName (inx) :
    global fileNames
    if inx < 0 :
       return ""
    else :
       return fileNames [inx]

def fileNameToIndex (name) :
    global fileNames
    if not name in fileNames :
       fileNames.append (name)
    return fileNames.index (name)

# --------------------------------------------------------------------------

def quoteString (s, quote = '"') :
    result = ""
    length = len (s)
    inx = 0
    for c in s :
       if c >= ' ' and ord (c) < 127:
          if c == '\"' : # double quote
             result += "\\" + c
          elif c == '\''  :  # single quote
             result += "\\" + c
          elif c == '\\' : # backslash
             result += "\\" + c
          else :
             result += c
       elif ord (c) <= 255:
          if c == '\a' :   result += "\\a"
          elif c == '\b' : result += "\\b"
          elif c == '\f' : result += "\\f"
          elif c == '\n' : result += "\\n"
          elif c == '\r' : result += "\\r"
          elif c == '\t' : result += "\\t"
          elif c == '\v' : result += "\\v"
          elif c == '\0' and inx == length-1 :
             result += "\\0"
          else :
             result += "\\x" + "{:02x}".format (ord (c))
       else :
          result += "\\u" + "{:04x}".format (ord (c))
       inx = inx + 1
    return quote + result + quote

# --------------------------------------------------------------------------

class Separators (object) :
   def __init__ (self) :
       self.value = -1  # -1 ... substring is not a valid symbol
                        # value >= 0 ... token kind
       self.items = { } # another symbols with same prefix
                        # dictionary of Separators ( keys ... first character )

# --------------------------------------------------------------------------

class Lexer (object) :
   eos = 0
   identifier = 1
   number = 2
   real_number = 3
   character_literal = 4
   string_literal = 5
   separator = 6
   end_of_line = 7

   def __init__ (self) :
       super (Lexer, self).__init__ () # problem with reloaded lexer module
       self.reset ()

   def reset (self) :

       self.charFileInx = 0
       self.charLineNum = 1
       self.charColNum = 1
       self.charByteOfs = 0 # character offset (from 0)

       self.tokenFileInx = 0
       self.tokenLineNum = 1
       self.tokenColNum = 1
       self.tokenByteOfs = 0 # token (in self.token)

       self.prevFileInx = 0
       self.prevLineNum = 1
       self.prevColNum = 1
       self.prevByteOfs = 0 # previous token
       self.prevEndOfs = 0

       self.ch = '\0'
       self.token = self.eos
       self.tokenText = ""
       self.tokenValue = ""

   # -----------------------------------------------------------------------

   def openFile (self, fileName) :
       fileName = os.path.abspath (fileName)
       self.charFileInx = fileNameToIndex (fileName)

       f = open (fileName, "r")
       self.source = f.read ()
       self.sourceLen = len (self.source)
       f.close ()

       self.nextChar ()
       self.nextToken ()

   def openString (self, sourceText) :
       self.source = str (sourceText) # optionaly conversion from QString
       self.sourceLen = len (self.source)

       self.nextChar ()
       self.nextToken ()

   # -----------------------------------------------------------------------

   def getPosition (self) :
       return indexToFileName (self.charFileInx) + ":" + str (self.charLineNum) + ":" + str (self.charColNum)

   def info (self, text) :
       print (self.getPosition () + ": info: " + text)

   def warning (self, text) :
       print (self.getPosition () + ": warning: " + text)

   def error (self, text) :
       raise LexerException (self.getPosition () + ": error: " + text + ", tokenText=" + self.tokenText)

   # -----------------------------------------------------------------------

   def nextChar (self) :
       if self.charByteOfs < self.sourceLen :
          self.ch = self.source [self.charByteOfs]
          self.charByteOfs = self.charByteOfs + 1
          if self.ch == '\n' :
             self.charLineNum = self.charLineNum + 1
             self.charColNum = 1
          elif self.ch != '\r' :
             self.charColNum = self.charColNum + 1
       else :
          self.ch = '\0'

   # -----------------------------------------------------------------------

   def isLetter (self, c) :
       return c >= 'A' and c <= 'Z' or c >= 'a' and c <= 'z' or c == '_'

   def isDigit (self, c) :
       return c >= '0' and c <= '9'

   def isOctDigit (self, c) :
       return c >= '0' and c <= '7'

   def isHexDigit (self, c) :
       return c >= 'A' and c <= 'F' or c >= 'a' and c <= 'f' or c >= '0' and c <= '9'

   def isLetterOrDigit (self, c) :
       return self.isLetter (c) or self.isDigit (c)

   # -----------------------------------------------------------------------

   def comment_eol (self) :
       txt = ""
       while self.ch != '\0' and self.ch != '\r' and self.ch != '\n' :
          txt += self.ch
          self.nextChar ()

   def comment (self, mark1) :
       txt = ""
       while self.ch != '\0' and self.ch != mark1 :
          txt += self.ch
          self.nextChar ()
       if self.ch == mark1 :
          self.nextChar () # skip mark1
       else :
          self.error ("Unterminated comment")

   def comment2 (self, mark1, mark2) :
       txt = ""
       prev = ' '
       while self.ch != '\0' and not (prev == mark1 and self.ch == mark2) :
          txt += self.ch
          prev = self.ch
          self.nextChar ()
       if self.ch == mark2 :
          self.nextChar () # skip mark2
       else :
          self.error ("Unterminated comment")

   def checkDigit (self) :
       if not self.isDigit (self.ch) :
          self.error ("Digit expected")

   def digits (self) :
       while self.isDigit (self.ch) :
          self.tokenText = self.tokenText + self.ch
          self.nextChar ()

   def stringChar (self) :
       if self.ch != '\\' :
          c = self.ch
          self.nextChar ()
          return c
       else :
          self.nextChar () # skip backslash

          if self.ch >= '0' and self.ch <= '7' :
             cnt = 1
             c = 0
             while self.ch >= '0' and self.ch <= '7' and cnt <= 3 :
                c = 8 * c  + ord (self.ch) - ord ('0')
                cnt = cnt + 1
                self.nextChar ()
             return chr (c)

          elif self.ch == 'x' or self.ch == 'X' :
             self.nextChar ()
             c = 0
             cnt = 1
             while self.ch >= '0' and self.ch <= '9' or self.ch >= 'A' and self.ch <= 'Z' or self.ch >= 'a' and self.ch <= 'z' and cnt <= 2 :
                if self.ch >= '0' and self.ch <= '9' :
                   n = ord (self.ch) - ord ('0')
                elif self.ch >= 'A' and self.ch <= 'Z' :
                   n = ord (self.ch) - ord ('A') + 10
                else :
                   n = ord (self.ch) - ord ('a') + 10
                c = 16 * c  + n
                cnt = cnt + 1
                self.nextChar ()
             return chr (c % 255)

          elif self.ch == 'a' :
             c = '\a'
          elif self.ch == 'b' :
             c =  '\b'
          elif self.ch == 'f' :
             c =  '\f'
          elif self.ch == 'n' :
             c =  '\n'
          elif self.ch == 'r' :
             c =  '\r'
          elif self.ch == 't' :
             c =  '\t'
          elif self.ch == 'v' :
             c =  '\v'
          elif self.ch == "'" or self.ch == '"'  or self.ch == '?' :
             c = self.ch
          else :
             c = self.ch # same

          self.nextChar ()
          return c

   def quoteString (self, s, quote = '"') :
       return quoteString (s, quote)

   def lookupKeyword (self) :
       pass

   def processSeparator (self) :
       pass

   def backStep (self) :
       self.tokenColNum = self.tokenColNum - 1
       self.tokenByteOfs = self.tokenByteOfs - 1

   # -----------------------------------------------------------------------

   def numericToken (self) :
       self.token = self.number
       cont = True
       if self.ch == '0' :
          self.tokenText = self.tokenText + self.ch
          self.nextChar ()
          if self.ch == 'x' :
             self.tokenText = self.tokenText + self.ch
             self.nextChar ()
             while self.isHexDigit (self.ch) :
                self.tokenText = self.tokenText + self.ch
                self.nextChar ()
             cont = False
          else :
             if self.isOctDigit (self.ch) :
                cont = False
             while self.isOctDigit (self.ch) :
                self.tokenText = self.tokenText + self.ch
                self.nextChar ()
       if cont :
          self.digits ()
          if self.ch == '.' :
             self.decimalToken ()
          self.exponentToken ()

   def decimalToken (self) :
       self.token = self.real_number
       self.tokenText = self.tokenText + self.ch # store '.'
       self.nextChar () # skip '.'
       # NO self.checkDigit ()
       self.digits ()

   def exponentToken (self) :
       if self.ch == 'e' or self.ch == 'E' :
          self.token = self.real_number
          self.tokenText = self.tokenText + self.ch # store 'e'
          self.nextChar () # skip 'e'
          if self.ch == '+' or self.ch == '-' :
             self.tokenText = self.tokenText + self.ch # store '+' or '-'
             self.nextChar () # skip '+' or '-'
          self.checkDigit ()
          self.digits ()
       if self.token == self.real_number :
          if self.ch == 'f' or self.ch == 'F' :
             self.nextChar ()
       else :
          if self.ch == 'l' or self.ch == 'L' :
             self.nextChar ()
          if self.ch == 'u' or self.ch == 'U' :
             self.nextChar ()
          if self.ch == 'l' or self.ch == 'L' :
             self.nextChar ()

   def nextToken (self) :
       self.token = self.eos
       self.tokenText = ""

       slash = False
       stop = False
       whiteSpace = True

       while whiteSpace and self.ch != '\0' and not stop :
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
                self.comment2 ('*', '/')
                whiteSpace = True # check again for white space
             else :
                slash = True # produce '/' token

       self.tokenFileInx = self.charFileInx
       self.tokenLineNum = self.charLineNum
       self.tokenColNum = self.charColNum
       self.tokenByteOfs = self.charByteOfs

       if slash :
          self.token = self.separator
          self.tokenText = '/'
          self.backStep ()
          self.processSeparator ()

       elif stop :
          self.token = self.end_of_line

       elif self.ch == '\0' :
          self.token = self.eos

       elif self.isLetter (self.ch) :
          self.token = self.identifier
          while self.isLetterOrDigit (self.ch) :
             self.tokenText = self.tokenText + self.ch
             self.nextChar ()
          # NO self.lookupKeyword ()

       elif self.ch == '@' and self.at_keywords :
          self.token = self.identifier
          while self.isLetterOrDigit (self.ch) or self.ch == '@' :
             self.tokenText = self.tokenText + self.ch
             self.nextChar ()
          # NO self.lookupKeyword ()

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
          # NO self.tokenText = quoteString (self.tokenText, '\'' )

       elif self.ch == '\"' :
          self.token = self.string_literal
          self.nextChar ()
          while self.ch != '\0' and self.ch != '\r' and self.ch != '\n' and self.ch != '\"' :
             self.tokenText = self.tokenText + self.stringChar ()
          if self.ch != '\"' :
             self.error ("Unterminated string")
          self.nextChar ()
          # NO self.tokenText = quoteString (self.tokenText)

       else :
          self.token = self.separator
          self.tokenText = self.ch
          first_ch = self.ch
          self.nextChar ()
          if first_ch == '.' and self.isDigit (self.ch) :
             self.decimalToken ()
             self.exponentToken ()
          elif first_ch != '#' :
             self.processSeparator ()

   # -----------------------------------------------------------------------

   def isEndOfSource (self) :
       return self.token == self.eos

   def isIdentifier (self) :
       return self.token == self.identifier

   def isNumber (self) :
       return self.token == self.number

   def isReal (self) :
       return self.token == self.real_number

   def isString (self) :
       return self.token == self.string_literal

   def isCharacter (self) :
       return self.token == self.character_literal

   def isSeparator (self, value) :
       # return self.token == self.separator and self.tokenText == value
       return self.token != self.string_literal and self.token != self.character_literal and self.tokenText == value

   def isKeyword (self, value) :
       return self.token == self.identifier and self.tokenText == value

   # -----------------------------------------------------------------------

   def readIdentifier (self, msg = "Identifier expected") :
       if not self.isIdentifier () :
          self.error (msg)
       value = self.tokenText
       self.nextToken ()
       return value

   def readNumber (self) :
       if not self.isNumber () :
          self.error ("Number expected")
       value = self.tokenText
       self.nextToken ()
       return value

   def readReal (self) :
       if not self.isReal () :
          self.error ("Real number expected")
       value = self.tokenText
       self.nextToken ()
       return value

   def readString (self) :
       if not self.isString () :
          self.error ("String literal expected")
       value = self.tokenText
       self.nextToken ()
       return value

   def readCharacter (self) :
       if not self.isCharacter () :
          self.error ("Character literal expected")
       value = self.tokenText
       self.nextToken ()
       return value

   # -----------------------------------------------------------------------

   def tokenToText (self) :
       if self.isCharacter () :
          return quoteString (self.tokenText, "'")
       elif self.isString () :
          return quoteString (self.tokenText)
       else :
          return self.tokenText

   # -----------------------------------------------------------------------

   def checkSeparator (self, value) :
       if not self.isSeparator (value) :
          self.error (value + " expected")
       self.nextToken ()

   def checkKeyword (self, value) :
       if not self.isKeyword (value) :
          self.error (value + " expected")
       self.nextToken ()

   # -----------------------------------------------------------------------

   def check (self, value) :
       if self.tokenText != value :
          self.error (value + " expected")
       self.nextToken ()

   def checkToken (self, value) :
       if self.token != value :
          self.error (self.tokenToString (value) + " expected")
       self.nextToken ()

   def tokenToString (self, value) :
       return "token " + str (value)

# --------------------------------------------------------------------------

if __name__ == "__main__" :
    lexer = Lexer ()
    lexer.openFile ("../pas/pas.g")

    if 0 :
       for i in range (4) :
          print (lexer.tokenText)
          lexer.nextToken ()

       print ("---")

    while not lexer.isEndOfSource () :
       print (lexer.tokenText, end = " ")
       lexer.nextToken ()

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
