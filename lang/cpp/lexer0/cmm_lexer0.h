
#ifndef _LEXER0_H_
#define _LEXER0_H_

#include <string>
#include <iostream>
#include <sstream>
using std::string;
using std::istream;
using std::ostringstream;

/* ---------------------------------------------------------------------- */

typedef unsigned char byte;

/* ---------------------------------------------------------------------- */

int storeFileName (string file_name);

string recallFileName (int index);
int    recallFileIndex (string file_name);

void clearFileNames ();

/* ---------------------------------------------------------------------- */

enum MessageLevel
{
   DebugLevel,    // debugging
   InfoLevel,     // information ( program start, stop, ... ) (not included in message summary)
   WarningLevel,  // warning about possible mistake
   ErrorLevel     // error
};

/* ---------------------------------------------------------------------- */

enum TokenKind
{
   startToken,     // formal first token

   identToken,     // identifier
   numberToken,    // number
   charToken,      // character in single quotes
   stringToken,    // string in double quotes
   separatorToken, // single character separator

   eofToken        // end of file
};

/* ---------------------------------------------------------------------- */

class LexerException : public std::exception
{
   public:
      string msg;
      string filename;
      int line;
      int column;

      LexerException
      (
         const string p_msg,
         const string p_filename = "",
         int p_line = 0,
         int p_column = 0
      )
      throw ()
      :
         msg (p_msg),
         filename (p_filename),
         line (p_line),
         column (p_column)
      {
         /* nothing */
      }

      virtual ~ LexerException () throw () { }

      string getMessage ()  { return msg; }
      string getFilename () { return filename; }
      int    getLine ()     { return line; }
      int    getColumn ()   { return column; }

      virtual const char * what () const throw ()
      {
         string txt = msg;
         return txt.c_str ();
      }
};

/* ---------------------------------------------------------------------- */

class Lexer
{
   public:
      Lexer ();
      virtual ~ Lexer ();

   protected:
      static const size_t bufSize = 4 * 1024;

      istream * inpStream;

      size_t bufPos;
      size_t bufLen;
      byte buf [bufSize];

      bool releaseStream;

   protected:
      int fileInx; // file number
      int linePos; // line counter
      int colPos;  // column counter
      int charPos; // character counter

      int tokenFileInx;
      int tokenLinePos;
      int tokenColPos;
      int tokenCharPos;

      char inpCh; // current input character
      char prevCh; // previous character (for end of line detection)
      bool prevEol; // end of line detected (but linePos will be incremented with next character)
      bool inpEof; // end of source text

      bool positionInitialized;

   protected:
      ostringstream text_storage;
      ostringstream value_storage;

   public:
      TokenKind tokenKind;

      string tokenText; // original token
      string tokenVal; // value of string
      char   tokenSym; // value of separator

   protected:
      virtual void Init ();

      virtual void readBuf ();
      void readData (void * adr, size_t size);

      void getCh ();
      void message (MessageLevel level, string msg);

   public:
      void open (string file_name);
      void openStream (istream & stream);
      void openString (string text);
      void close () { }

      string getFileName ();
      void setFileName (const string file_name);

   public:
      void debug (const string msg);
      void info (const string msg);
      void warning (const string msg);
      void error (const string msg);

   public:
      int getTokenFileInx () { return tokenFileInx; }
      int getTokenLine () { return tokenLinePos; }
      int getTokenCol() { return tokenColPos; }

   protected:
      void nextCh ();
      void textCh ();
      void spaceCh ();

      char character ();

      void getIdent ();
      void getNumber ();
      void getChar ();
      void getString ();

      void storeSeparator (char ch);
      virtual void getSeparator ();

      virtual void translate () { } // convert keywords and separators

   public:
      void nextToken ();


      bool isIdent () { return tokenKind == identToken; }
      bool isNumber () { return tokenKind == numberToken; }
      bool isChar () { return tokenKind == charToken; }
      bool isString () { return tokenKind == stringToken; }
      bool isSeparator () { return tokenKind == separatorToken; }
      bool isEof () { return tokenKind == eofToken; }

      bool isIdent (const string par);
      bool isSeparator (char par);

      void checkIdent (const string par);
      void checkSeparator (char par);
      void checkEof ();

      string readIdent ();
      char   readChar ();
      string readNumber ();
      string readString ();

      bool   readBool ();

      string readSignedNumber (); // including minus sign
      string readValue (); // identifier, number, character or string

      int    readInt ();
      long   readLong ();

      unsigned int  readUInt ();
      unsigned long readULong ();

      float  readFloat ();
      double readDouble ();
};

/* ---------------------------------------------------------------------- */

class Output
{
   protected:
      ostringstream text_storage;

   private:
      string fileName;
      bool showMsg;

   protected:
      bool startLine;
      bool skipEmptyLine;
      bool addEmptyLine;
      bool ignoreEol;

   private:
      int indentation;

   public:
      int linePos;
      int colPos;

   protected:
      virtual void Init ();
      virtual void Finish () { }

   public:
      void open (string name);
      void close () { Finish (); }

      string getFileName () { return fileName; }
      void setFileName (const string p_filename) { fileName = p_filename; }

      bool compare ();
      void store ();
      void writeText ();

      string toString ();

   protected:
      virtual void message (MessageLevel level, const string msg);

   public:
      void debug (const string msg);
      void info (const string msg);
      void warning (const string msg);
      void error (const string msg);

   public:
      int  getIndent () { return indentation; }
      void setIndent (int i);

      void indent ();
      void unindent ();

      void incIndent () { indent (); }
      void decIndent () { unindent (); }

   protected:
      void putPlainChr (char c);
      void putPlainSpaces (int n);
      void putPlainStr (const string s);
      void putPlainData (void * adr, size_t len);
      void putPlainEol ();

      virtual void openLine ();
      virtual void closeLine ();

   public:
      void put (const string s);
      void putChr (char c);
      void putSpaces (int n);
      void putEol ();
      void putCondEol ();
      void putLn (const string s);

      void emptyLine ();
      void noEmptyLine ();

      void putBool (bool value);

      void putChar (char value);
      void putString (string value);

      void putInt (int value);
      void putLong (long value);

      void putUInt (unsigned int value);
      void putULong (unsigned long value);

      void putFloat (float value);
      void putDouble (double value);

      void readFrom (const string file_name);

   public:
      void send (string s);

   public:
      void style_space ();
      void style_no_space ();
      void style_new_line ();
      void style_empty_line ();
      void style_no_empty_line ();
      void style_indent ();
      void style_unindent ();

   public:
      Output ();
      virtual ~ Output ();
};

/* ---------------------------------------------------------------------- */

#endif /* _LEXER0_H__ */
