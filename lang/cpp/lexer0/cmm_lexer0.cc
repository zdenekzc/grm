
/* lexer0.cc */

#include "cmm_lexer0.h"

#ifdef ENABLE_TRACE
//   #include "trace.h"
#endif

#include <map>
#include <cassert>
#include <cstring>

#include <fstream>
#include <sstream>

using std::map;
using std::ifstream;
using std::ofstream;
using std::istringstream;
// using std::memcpy;
// using std::noskipws;
// using std::hex;
// using std::endl;
// using std::cerr;
// using std::streamsize;

/* ---------------------------------------------------------------------- */

typedef Lexer TCharInput;
typedef Lexer TMixedInput;
typedef Lexer TRewindInput;
typedef Lexer TTextInput;
typedef Lexer TEnvInput;
typedef Output TTextOutput;

inline void reset (ostringstream & storage)
{
   storage.str ("");
   storage.clear ();
}

/* ---------------------------------------------------------------------- */

const char cr = '\r';
const char lf = '\n';
// const char tab = '\t';
const char quote1 = '\'';
const char quote2 = '\"';
const char backslash = '\\';

/* ---------------------------------------------------------------------- */

inline bool isLetter (char ch)
{
   return (ch >= 'A' && ch <= 'Z') ||
          (ch >= 'a' && ch <= 'z') ||
          (ch == '_');
}

inline bool isUpperCaseLetter (char ch)
{
   return (ch >= 'A' && ch <= 'Z') || (ch == '_');
}

inline bool isDigit (char ch)
{
   return ch >= '0' && ch <= '9';
}

inline bool isOctal (char ch)
{
   return ch >= '0' && ch <= '7';
}

inline bool isHexDigit (char ch)
{
   return (ch >= '0' && ch <= '9') ||
          (ch >= 'a' && ch <= 'f') ||
          (ch >= 'A' && ch <= 'F');
}

inline bool isLetterOrDigit (int ch)
{
   return isLetter (ch) || isDigit (ch);
}

/* ---------------------------------------------------------------------- */

template <typename T>
inline string NumToStr (T num)
{
   ostringstream stream;
   stream << num;
   return stream.str ();
}
template <typename T>
inline void StrToNum (string txt, T & result, bool & ok)
// txt ... input value
// ok == true ... conversion succeded
// result ... converted value, assigned only when ok == true
{
   T n;
   istringstream stream (txt);
   stream >> std::noskipws;

   if (txt.length () > 2 && txt[0] == '0' && (txt[1] == 'x' || txt[1] == 'X'))
   {
      char c1;
      char c2;
      stream >> c1 >> c2 >> std::hex; // skip two characters and set hex
   }

   stream >> n;
   ok = (stream.eof () && ! stream.fail ());

   if (ok)
      result = n;

   // ok == false, nothing is assigned to result
}

template <typename T>
inline bool StrToNum (string txt, T & result)
{
   bool ok;
   StrToNum (txt, result, ok);
   return ok;
}

/* ---------------------------------------------------------------------- */

inline string IntToStr (int value)
// convert int to string
{
   return NumToStr (value);
}

inline void StrToInt (string txt, int & result, bool & ok)
// convert string to int
// txt ... input value
// ok == true ... conversion succeded
// result ... converted value, assigned only when ok == true
{
   StrToNum (txt, result, ok);
}

inline bool StrToInt (string txt, int & result)
// returns ok from previous function
{
   bool ok;
   StrToInt (txt, result, ok);
   return ok;
}

/* ---------------------------------------------------------------------- */

const char hex_digit [16+1] = "0123456789abcdef";

inline string charToStr (char c) { return string (1, c); } // convert one character to string

string quoteChrContent (char value)
{
   string result = "";

   unsigned char ch = value;

   if (ch < ' ' || ch == 128 || ch >= 255)
   {
      result = '\\';
      switch (ch)
      {
         case '\a': result = result + 'a'; break;
         case '\b': result = result + 'b'; break;
         case '\f': result = result + 'f'; break;
         case '\n': result = result + 'n'; break;
         case '\r': result = result + 'r'; break;
         case '\t': result = result + 't'; break;
         case '\v': result = result + 'v'; break;

         default:
            result = result + 'x' + hex_digit [ch >> 4] + hex_digit [ch & 15];
            break;
      }
   }
   else
   {
      if (ch == '\\' || ch == '"')
         result = charToStr ('\\') + value;
      else
         result = value;
   }

   return result;
}

string quoteStrContent (const string value)
{
   int len = value.length ();

   bool simple = true;
   for (int i = 0; i < len && simple; i++)
   {
      unsigned char ch = value [i];
      if (ch < ' ' || ch == '\\' || ch == '"' || ch == 128 || ch >= 255)
         simple = false;
   }

   if (simple)
   {
      return value;
   }
   else
   {
      string result = "";

      for (int i = 0; i < len; i++)
         result += quoteChrContent (value [i]);

      return result;
   }
}

string quoteStr (const string value, char quote = quote2)
{
   return quote + quoteStrContent (value) + quote;
}

string quoteChr (char value, char quote = quote1)
{
   return quote + quoteStrContent (charToStr (value)) + quote;
}

/* ---------------------------------------------------------------------- */

void show_message (MessageLevel level,
                   string msg, string file_name, int line, int column)
{
}

/******************************* FILE NAMES *******************************/

typedef map <string, int> StringMap;
typedef map <int, string> IntMap;

// global variables
static StringMap FileNameDict;
static IntMap FileNumberDict;
static int last_index = 0;

void clearFileNames ()
{
   FileNameDict.clear ();
   FileNumberDict.clear ();
}

int storeFileName (string file_name)
{
   int index = 0;

   if (FileNameDict.find (file_name) != FileNameDict.end ())
   {
      index = FileNameDict [file_name];
   }
   else
   {
      last_index ++;
      index = last_index;
      FileNameDict [file_name] = index;
      FileNumberDict [index] = file_name;
   }

   return index;
}

string recallFileName (int index)
{
   if (FileNumberDict.find (index) != FileNumberDict.end ())
   {
      return FileNumberDict [index];
   }
   else
   {
      return "";
   }

   // return empty string if file index is not dictionay
   // important for __FILE__ macro expansion
}

int recallFileIndex (string file_name)
{
   if (FileNameDict.find (file_name) != FileNameDict.end ())
   {
      return FileNameDict [file_name];
   }
   else
   {
      return 0;
   }
}

/********************************** LEXER *********************************/

Lexer::Lexer ():
   inpStream (NULL),
   bufPos (0),
   bufLen (0),
   // ignore buf
   releaseStream (false),

   fileInx (0),
   linePos (0),
   colPos (0),
   charPos (0),

   tokenFileInx (0),
   tokenLinePos (0),
   tokenColPos (0),
   tokenCharPos (0),

   inpCh (0),
   prevCh (0),
   prevEol (false),
   inpEof (false),

   positionInitialized (false),

   tokenKind (startToken),
   tokenText (""),
   tokenVal (""),
   tokenSym (0)
{
}

Lexer::~Lexer ()
{
   if (releaseStream && inpStream != NULL)
   {
      delete inpStream;
      inpStream = NULL;
   }
}

void Lexer::Init ()
{
   bufPos = 0;
   bufLen = 0;
   // do not change already initialized inpStream, fileName and releaseStream

   inpCh = 0;
   prevCh = 0;
   prevEol = false;
   inpEof = false;

   if (! positionInitialized)
   {
      linePos = 1;
      colPos = 0;
      charPos = 0;

      tokenLinePos = 1;
      tokenColPos = 0;
      tokenCharPos = 0;
   }

   tokenKind = startToken;
   tokenText = "";
   tokenVal = "";
   tokenSym = 0;
   // actual = NO_SYMBOL;

   // read first character
   nextCh ();
   nextToken ();
}

string TCharInput::getFileName ()
{
   return recallFileName (fileInx);
}

void TCharInput::setFileName (const string file_name)
{
   fileInx = storeFileName (file_name);
}

/* ---------------------------------------------------------------------- */

void TCharInput::openStream (istream & stream)
{
   inpStream = & stream;
   assert (inpStream != NULL);
   Init ();
}

void TCharInput::openString (string text)
{
   istringstream * tmp = new istringstream (text);
   releaseStream = true;
   openStream (*tmp);
}

void TCharInput::open (string name)
{
   setFileName (name);

   ifstream * tmp = new ifstream;
   tmp->open (name.c_str ());

   if (!tmp->good ())
   {
      error ("Cannot open " + name);
      delete tmp;
   }
   else
   {
      releaseStream = true;
      openStream (*tmp);
   }
}

/* ---------------------------------------------------------------------- */

void TCharInput::readBuf ()
{
   assert (inpStream != NULL);
   if (! inpStream->good ()) // important for string streams
   {
       bufLen = 0;
   }
   else
   {
      inpStream->read (static_cast <char *> (static_cast <void *> (& buf)), bufSize);
      bufLen = inpStream->gcount ();
   }
   bufPos = 0;
}

void TCharInput::readData (void * adr, size_t size)
{
   size_t step;
   assert (bufPos >= 0);
   assert (bufPos <= bufLen);

   assert (bufLen >= 0);
   assert (bufLen <= bufSize);

   while (size > 0)
   {
      if (bufPos >= bufLen)
      {
         readBuf ();
         if (bufLen == 0)
            error ("End of file");
      }

      step = bufLen - bufPos;
      if (step > size)
         step = size;

      assert (step > 0);
      assert (step <= size);

      assert (bufPos >= 0);
      assert (bufPos + step <= bufLen);

      assert (bufLen >= 0);
      assert (bufLen <= bufSize);

      std::memcpy (adr, & buf[bufPos], step);
      bufPos += step;
      size -= step;

      adr = (void *) ((char *) (adr) + step);

      assert (size >= 0);
   }
}

void TCharInput::getCh ()
{
   // assert (bufPos >= 0);
   // assert (bufPos <= bufLen);

   // assert (bufLen >= 0);
   // assert (bufLen <= bufSize);

   if (bufPos >= bufLen)
   {
      if (inpEof)
      {
          error ("End of file");
      }
      else
      {
         readBuf ();
         inpEof = (bufLen == 0);
      }
   }

   if (inpEof)
   {
      inpCh = 0;
   }
   else
   {
      // assert (bufPos >= 0);
      // assert (bufPos < bufLen);

      // assert (bufLen >= 0);
      // assert (bufLen <= bufSize);

      inpCh = (char) (buf[bufPos]);
      bufPos ++;
   }

   // assert (bufPos >= 0);
   // assert (bufPos <= bufLen);

   // assert (bufLen >= 0);
   // assert (bufLen <= bufSize);

   if (prevEol)
   {
      linePos ++;
      colPos = 0;
      prevEol = false;
   }

   if (inpCh == cr)
   {
      prevEol = true;
      colPos ++;
   }
   else if (inpCh == lf)
   {
      if (prevCh != cr)
      {
         prevEol = true;
         colPos ++;
     }
   }
   else
   {
      colPos ++;
   }

   charPos ++;
   prevCh = inpCh;
}

/* ---------------------------------------------------------------------- */

void TCharInput::message (MessageLevel level, string msg)
{
   string file_name = getFileName ();
   int line = getTokenLine();
   int column = getTokenCol();

   // show position

   string txt = "";

   if (file_name != "")
   {
      txt = file_name + ":";
      if (line != 0) // !?
         txt = txt + IntToStr (line) + ":";
   }
   else
   {
      if (line != 0)
         txt = "line " + IntToStr (line) + ":";
   }

   if (column != 0)
      txt = txt + IntToStr (column) + ":";
      // emacs - column number, without any space, with colon

   // show message

   if (txt != "")
      txt = txt + " ";

   switch (level)
   {
      case DebugLevel:
         txt = txt + "debug: ";
         break;

      case InfoLevel:
         txt = txt + "info: ";
         break;

      case WarningLevel:
         txt = txt + "warning: ";
         break;

      case ErrorLevel:
         txt = txt + "error: ";
         break;
   }

   txt = txt + msg;

   std::cerr << txt << std::endl;

   if (level == ErrorLevel)
   {
      #ifdef ENABLE_TRACE
         trace (); // show stack trace (before throwing exception)
      #endif

      throw LexerException (msg, file_name, line, column);
   }
}

void TCharInput::debug (const string msg)
{
   message (InfoLevel, msg);
}

void TCharInput::info (const string msg)
{
   message (InfoLevel, msg);
}

void TCharInput::warning (const string msg)
{
   message (WarningLevel, msg);
}

void TCharInput::error (const string msg)
{
   message (ErrorLevel, msg);
}

/******************************* TEXT INPUT *******************************/

void TTextInput::nextCh ()
{
   // NO value_storage.put (inpCh); // token characters
   text_storage.put (inpCh); // characters from original source
   getCh ();
}

void TTextInput::textCh ()
// characters in string literals
{
   // NO value_storage.put (inpCh);
   text_storage.put (inpCh);

   getCh ();
}

/* ---------------------------------------------------------------------- */

void TTextInput::getIdent ()
{
   while (isLetterOrDigit (inpCh))
      nextCh ();

   tokenText = text_storage.str ();
   tokenVal = "";
   tokenSym = 0;
   tokenKind = identToken;
}

void TTextInput::getNumber ()
{
   bool hex = false;
   bool any_digit = false;
   bool floating_point = false;

   if (inpCh == '0')
   {
      nextCh (); // first digit
      any_digit = true;

      if (inpCh == 'x' || inpCh == 'X')
      {
         nextCh (); // store 'x'
         hex = true;
         while (isHexDigit (inpCh))
            nextCh ();
      }
   }

   if (! hex)
   {
      while (isDigit (inpCh))
      {
         any_digit = true;
         nextCh ();
      }

      if (inpCh == '.')
      {
         nextCh (); // decimal point
         floating_point = true;

         while (isDigit (inpCh))
         {
            any_digit = true;
            nextCh ();
         }
      }

      if (any_digit && (inpCh == 'E' || inpCh == 'e'))
      {
         nextCh ();
         floating_point = true;

         if (inpCh == '+' || inpCh == '-')
            nextCh ();

         if (! isDigit (inpCh))
            error ("Digit expected");

         while (isDigit (inpCh))
            nextCh ();
      }
   }

   if (any_digit)
   {
      if (floating_point)
         while (inpCh == 'f' || inpCh == 'F' || inpCh == 'l' || inpCh == 'L')
            nextCh ();
      else
         while (inpCh == 'u' || inpCh == 'U' || inpCh == 'l' || inpCh == 'L')
            nextCh ();
   }

   if (any_digit)
   {
      tokenText = text_storage.str ();
      tokenVal = "";
      tokenSym = 0;

      tokenKind = numberToken;
   }
   else
   {
      storeSeparator ('.');
   }
}

char TTextInput::character ()
// read one C-style character
{
  if (inpCh != backslash)             // simple character
  {
     char last = inpCh;
     textCh ();
     return last;
  }
  else                                // escape sequence
  {
     textCh ();                       // skip backslash

     if (isOctal (inpCh))             // octal
     {
        int n = 0;
        int cnt = 1;
        while (isOctal (inpCh) && cnt <= 3)
        {
           n = n*8 + inpCh-'0';
           cnt++;
           textCh ();
        }
        return char (n);
     }

     else if (inpCh == 'x' || inpCh == 'X')     // hex
     {
        textCh ();
        int n = 0;
        while (isHexDigit (inpCh))
        {
           int d;
           if (inpCh >= 'A' && inpCh <= 'F')
              d = inpCh - 'A' + 10;
           else if (inpCh >= 'a' && inpCh <= 'f')
              d = inpCh - 'a' + 10;
           else
              d = inpCh - '0';
           n = n*16 + d;
           textCh ();
        }
        return char (n);
     }
     else
     {
        char last = inpCh;
        textCh ();
        switch (last)                 // other
        {
           case 'a': return '\a';
           case 'b': return '\b';
           case 'f': return '\f';
           case 'n': return '\n';
           case 'r': return '\r';
           case 't': return '\t';
           case 'v': return '\v';

           case quote1:    return last;
           case quote2:    return last;
           case backslash: return last;
           case '?':       return last;

           default:        return last;
        }
     }
  }
}

void TTextInput::getChar ()
{
   textCh (); // skip quote

   // if (inpCh == quote1)
   //    error ("Empty character constant");

   while (inpCh != quote1)
   {
      if (inpEof || inpCh == cr || inpCh == lf)
         error ("character constant exceeds line");

      char c;

      c = character ();

      value_storage.put (c);
   }

   textCh (); // skip quote

   tokenText = text_storage.str (); // with quotes and escape sequences
   tokenVal = value_storage.str (); // value without quotes and escape sequences
   tokenSym = 0;
   tokenKind = charToken;
}

void TTextInput::getString ()
{
   textCh (); // skip quote

   while (inpCh != quote2)
   {
      if (inpEof || inpCh == cr || inpCh == lf)
         error ("String exceeds line");

      char c;

      c = character ();

      value_storage.put (c);
   }

   textCh (); // skip quote

   tokenText = text_storage.str (); // string with quotes and escape sequences
   tokenVal = value_storage.str (); // value without quotes and escape sequences
   tokenSym = 0;
   tokenKind = stringToken;
}

/* ---------------------------------------------------------------------- */

void TTextInput::storeSeparator (char ch)
{
   text_storage.put (ch);

   tokenText = ch;
   tokenVal = "";
   tokenSym = ch; // important
   tokenKind = separatorToken;
 }

void TTextInput::getSeparator ()
{
   char c = inpCh;
   nextCh ();
   storeSeparator (c);
}

/* ---------------------------------------------------------------------- */

void TTextInput::nextToken ()
{
   reset (text_storage);
   reset (value_storage);

   again:

   tokenFileInx = fileInx;
   tokenLinePos = linePos;
   tokenColPos  = colPos;
   tokenCharPos = charPos;

   if (inpEof)                                 // END OF FILE
   {
      tokenText = "";
      tokenVal = "";
      tokenSym = 0;
      tokenKind = eofToken;
   }

   else if (inpCh <= ' ')                      // WHITE SPACE, END OF LINE
   {
      while (! inpEof && inpCh <= ' ')
         getCh ();

      goto again;
   }

   else if (inpCh == '/')                      // COMMENT (or slash)
   {
      bool slash = false;
      getCh (); // skip slash

      if (! inpEof && inpCh == '/')            // SINGLE LINE COMMENT
      {
         while (! inpEof && inpCh != cr && inpCh != lf)
            getCh ();
      }

      else if (! inpEof && inpCh == '*')       // COMMENT
      {
         getCh (); // skip asterisk

         char prev = ' ';
         while (! inpEof && ! (prev == '*' && inpCh == '/'))
         {
            prev = inpCh;
            getCh ();
         }

         if (! inpEof)
            getCh (); // skip slash
      }
      else slash = true; // SLASH

      if (slash)
         storeSeparator ('/');
      else
         goto again;
   }

   else if (isLetter (inpCh))                  // IDENTIFIER
      getIdent ();

   else if (isDigit (inpCh))                   // NUMBER
      getNumber ();

   else if (inpCh == '.')                      // NUMBER or PERIOD
      getNumber ();

   else if (inpCh == quote1)                   // CHARACTER
      getChar ();

   else if (inpCh == quote2)                   // STRING
      getString ();

   else                                        // SEPARATOR
      getSeparator ();

   translate (); // convert keywords and separators
}


/* ---------------------------------------------------------------------- */

bool TTextInput::isIdent (string par)
{
   return (tokenKind == identToken) && (tokenText == par);
}

bool TTextInput::isSeparator (char par)
{
   return (tokenKind == separatorToken) && (tokenSym == par);
}

/* ---------------------------------------------------------------------- */

void TTextInput::checkIdent (string par)
{
   if (tokenKind != identToken || tokenText != par)
      // error (par + " expected");
      error (par + " expected and found " + quoteStr (tokenText));
   nextToken ();
}

void TTextInput::checkSeparator (char par)
{
   if (tokenKind != separatorToken || tokenSym != par)
   {
      // error (charToStr (par) + " expected");
      error (charToStr (par) + " expected and found " + quoteStr (tokenText));
   }
   nextToken ();
}

void TTextInput::checkEof ()
{
   if (tokenKind != eofToken)
      error ("End of file expected");
}

/* ---------------------------------------------------------------------- */

string TTextInput::readIdent ()
{
   string result;
   if (tokenKind != identToken)
      error ("Identifier expected");
   result = tokenText;
   nextToken ();
   return result;
}

string TTextInput::readNumber ()
{
   string result;
   if (tokenKind != numberToken)
      error ("Number expected");
   result = tokenText;
   nextToken ();
   return result;
}

char TTextInput::readChar ()
{
   char result;
   if (tokenKind != charToken)
      error ("character constant expected");
   result = tokenSym;
   nextToken ();
   return result;
}

string TTextInput::readString ()
{
   string result;
   if (tokenKind != stringToken)
      error ("String expected");
   result = tokenVal;
   nextToken ();
   return result;
}

/* ---------------------------------------------------------------------- */

bool TTextInput::readBool ()
{
   bool result = false;

   if (isIdent ("true"))
   {
      nextToken ();
      result = true;
   }
   else if (isIdent ("false"))
   {
      nextToken ();
      result = false;
   }
   else
   {
      error ("Boolean value expected");
   }

   return result;
}

string TTextInput::readSignedNumber ()
{
   bool minus;
   string result;

   minus = false;
   if (tokenKind == separatorToken && tokenSym == '-')
   {
      minus = true;
      nextToken ();
   }

   result = readNumber ();

   if (minus)
      result = '-' + result;
   return result;
}

string TTextInput::readValue ()
{
   string result;

   if (isSeparator ('-') || tokenKind == numberToken)
   {
      result = readSignedNumber ();
   }
   else if (tokenKind == identToken)
   {
      result = readIdent ();
      while (isSeparator ('.'))
      {
          nextToken ();
          string id = readIdent ();
          result = result + "." + id;
      }
   }
   else if  (tokenKind == stringToken || tokenKind == charToken )
   {
      result = tokenVal;
      nextToken ();
   }
   else
   {
      error ("Identifier, number, character or string expected");
   }

   return result;
}

/* ---------------------------------------------------------------------- */

int TTextInput::readInt ()
{
   int result = 0;
   string txt = readSignedNumber ();
   bool ok;
   StrToNum (txt, result, ok);
   if (!ok)
      error ("Integer expected");
   return result;
}

long TTextInput::readLong ()
{
   long result = 0;
   string txt = readSignedNumber ();
   bool ok;
   StrToNum (txt, result, ok);
   if (!ok)
      error ("Long integer expected");
   return result;
}

unsigned int TTextInput::readUInt ()
{
   unsigned int result = 0;
   string txt = readSignedNumber ();
   bool ok;
   StrToNum (txt, result, ok);
   if (!ok)
      error ("Unsigned integer expected");
   return result;
}

unsigned long TTextInput::readULong ()
{
   unsigned long result = 0;
   string txt = readSignedNumber ();
   bool ok;
   StrToNum (txt, result, ok);
   if (!ok)
      error ("Unsinged long integer expected");
   return result;
}

float TTextInput::readFloat ()
{
   float result = 0;
   string txt = readSignedNumber ();
   bool ok;
   StrToNum (txt, result, ok);
   if (!ok)
      error ("Float expected");
   return result;
}

double TTextInput::readDouble ()
{
   double result = 0;
   string txt = readSignedNumber ();
   bool ok;
   StrToNum (txt, result, ok);
   if (!ok)
      error ("Double expected");
   return result;
}

/****************************** TEXT OUTPUT *******************************/

Output::Output ():
   text_storage (),
   fileName (),
   showMsg (true),
   startLine (false),
   skipEmptyLine (false),
   addEmptyLine (false),
   ignoreEol (false),
   indentation (0),
   linePos (0),
   colPos (0)
{
}

Output::~Output ()
{
   // NO store ();
}

void TTextOutput::Init ()
{
   reset (text_storage); // important for repeated open

   indentation = 0;
   startLine = true;
   skipEmptyLine = false;
   addEmptyLine = false;
   ignoreEol = false;

   linePos = 1;
   colPos = 0;
}

void TTextOutput::open (string name)
{
   setFileName (name);
   Init ();
}

/* ---------------------------------------------------------------------- */

void TTextOutput::message (MessageLevel level, const string msg)
{
   // message (level, msg, fileName, linePos, colPos);
}

/* ---------------------------------------------------------------------- */

void TTextOutput::debug (const string msg)
{
   message (InfoLevel, msg);
}

void TTextOutput::info (const string msg)
{
   message (InfoLevel, msg);
}

void TTextOutput::warning (const string msg)
{
   message (WarningLevel, msg);
}

void TTextOutput::error (const string msg)
{
   message (ErrorLevel, msg);
}

/* ---------------------------------------------------------------------- */

void TTextOutput::setIndent (int i)
{
   indentation = i;
}

void TTextOutput::indent ()
{
   indentation += 3;
}

void TTextOutput::unindent ()
{
   indentation -= 3;
}

/* ---------------------------------------------------------------------- */

void TTextOutput::putPlainChr (char c)
{
   text_storage.put (c);

   if (c == lf)
   {
      linePos ++;
      colPos = 0;
   }
   else
   {
      colPos ++;
   }
}

void TTextOutput::putPlainSpaces (int n)
{
   text_storage << string (n, ' ');
   colPos += n;
}

void TTextOutput::putPlainStr (const string s)
{
   text_storage << s;
   colPos += s.length (); // no line feed checking
}

void TTextOutput::putPlainData (void * adr, size_t len)
{
   text_storage.write ((const char *) adr, len);
   // no line and column numbers
}

void TTextOutput::putPlainEol ()
{
   // putPlainChr (cr);
   putPlainChr (lf);
}

/* ---------------------------------------------------------------------- */

void TTextOutput::openLine ()
{
   if (addEmptyLine && ! skipEmptyLine)
      putPlainEol ();

   addEmptyLine = false;
   skipEmptyLine = false;

   putPlainSpaces (indentation);
   startLine = false;
}

void TTextOutput::closeLine ()
{
   startLine = true;
}

/* ---------------------------------------------------------------------- */

void TTextOutput::put (const string s)
{
   if (s != "")
   {
      if (startLine)
         openLine ();

      putPlainStr (s);
   }
}

void TTextOutput::putChr (char c)
{
   if (startLine)
      openLine ();

   putPlainChr (c);
}

void TTextOutput::putSpaces (int n)
{
   if (n != 0)
   {
      if (startLine)
         openLine ();

      putPlainSpaces (n);
  }
}

void TTextOutput::putEol ()
{
   if (ignoreEol)
   {
      putPlainChr (' ');
   }
   else
   {
      putPlainEol ();
      closeLine ();
   }
}

void TTextOutput::putCondEol ()
{
   // finish not empty line
   if (! startLine)
      putEol ();
}

void TTextOutput::putLn (const string s)
{
   put (s);
   putEol ();
}

/* ---------------------------------------------------------------------- */

void TTextOutput::emptyLine ()
{
   if (! startLine)
      putEol ();

   addEmptyLine = true;
}

void TTextOutput::noEmptyLine ()
{
   skipEmptyLine = true;
}

/* ---------------------------------------------------------------------- */

void TTextOutput::putBool (bool value)
{
   if (value)
      put ("true");
   else
      put ("false");
}

void TTextOutput::putChar (char value)
{
    put (quoteChr (value, quote1));
}

void TTextOutput::putString (string value)
{
    put (quoteStr (value, quote2));
}

void TTextOutput::putInt (int value)
{
    put (NumToStr (value));
}

void TTextOutput::putLong (long value)
{
    put (NumToStr (value));
}

void TTextOutput::putUInt (unsigned int value)
{
    put (NumToStr (value));
}

void TTextOutput::putULong (unsigned long value)
{
    put (NumToStr (value));
}

void TTextOutput::putFloat (float value)
{
    put (NumToStr (value));
}

void TTextOutput::putDouble (double value)
{
    put (NumToStr (value));
}

/* ---------------------------------------------------------------------- */

#if 0
void Output::send (string s)
{
   // add optional space and print string
   char c = ' ';
   if (s.length () >= 1) c = s[0];

   if (c == '.' || c == ',' || c == ';' || c == ')' || c == ']' ) space = false;

   if (space && skip_spaces) putChr (' ');
   put (s);

   space = true;
   if (c == '(' || c == '[' || c == '.' || c == '#') space = false;
}

/* ---------------------------------------------------------------------- */

void Output::style_space ()
{
   space = true;
}

void Output::style_no_space ()
{
   space = false;
}

void Output::style_new_line ()
{
   // finish line and start new one
   if ((! comments || generated_area) && ! skip_newlines)
   {
      send_cond_eol (); // quoted stencils - use send, not print
   }
}

void Output::style_empty_line ()
{
   // add one empty line
   send_cond_eol (); // quoted stencils - use send, not print
   add_empty_line = true;
}

void Output::style_no_empty_line ()
{
   // wait until end of line and then add empty line
   if (! skip_newlines)
      ignore_empty_line = true;
}

/* ---------------------------------------------------------------------- */

void Output::style_indent ()
{
   // indent recomendation
   style_new_line ();
   indent ();
}

void Output::style_unindent ()
{
   // unindent recomendation
   unindent ();
   style_new_line ();
}
#endif

/* ---------------------------------------------------------------------- */

string Output::toString ()
{
   return text_storage.str ();
}

/* ---------------------------------------------------------------------- */

void Output::writeText ()
{
   ofstream f (fileName);
   if (! f.good ())
   {
      error ("Cannot open file for writing: " + fileName);
   }
   else
   {
      string text = text_storage.str ();
      f << text;

      f.close ();
      if (! f.good ())
         error ("Error writing file: " + fileName); // simple error form inf.h
   }
}

/* ---------------------------------------------------------------------- */

bool Output::compare ()
{
   bool equal = false;

   ifstream f (fileName);
   if (f.good ())
   {
      ostringstream buffer;
      buffer << f.rdbuf();
      string file_text = buffer.str ();

      string local_text = text_storage.str ();
      equal = file_text == local_text;
      f.close ();
   }

   return equal;
}

/* ---------------------------------------------------------------------- */

void Output::store ()
{
   bool equal = compare ();

   if (! equal)
   {
      writeText ();
      info ("writing " + fileName);
   }
   else
   {
      if (showMsg)
         info ("not modified " + fileName);
   }
}

/* ---------------------------------------------------------------------- */
