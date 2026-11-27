//
/* textio.h */

/* Text Input / Output */

#ifndef __PROG_TEXTIO_H__
#define __PROG_TEXTIO_H__

#include "std.h"
#include "msglevel.h" // type MessageLevel

#include <cstdio> // FILE

OPEN_NAMESPACE

/* ---------------------------------------------------------------------- */

int storeFileName (string file_name);

string recallFileName (int index);
int    recallFileIndex (string file_name);

void clearFileNames ();

/* ---------------------------------------------------------------------- */

typedef int InputSymbol;

/* ---------------------------------------------------------------------- */

enum TokenKind
{
   startToken,     // formal first token

   nameToken,      // identifier or keyword
   numberToken,    // number
   realToken,      // real number
   charToken,      // character in single quotes
   stringToken,    // string in double quotes
   separatorToken, // single character separator

   spaceToken,     // white space
   commentToken,   // comment
   lineContToken,  // back-slash as line continuation mark
   eolToken,       // end of line

   textLineToken,  // text lines started with apostrophe

   unusedDirectiveToken,    // section skiped by preprocesor (when keepEmptySections or keepUnusedSections)
   includeDirectiveToken,   // include directive (used when reportIncludes == true)
   processedDirectiveToken, // already processed directive

   stopToken,      // formal last token
   finalToken,     // end of macro expansion
   eofToken        // end of file
};

string tokenKindToStr (TokenKind kind);

/* ---------------------------------------------------------------------- */

class InputItem
{
   public:
      InputSymbol symbol;
      TokenKind kind;
      string token_text;
      string token_val;
      char token_sym;

      char inp_ch;
      bool inp_started;
      bool inp_eof;

   public:
      int file_num;
      int line_num;
      int col_num;

   public:
      InputItem * next;

      InputItem * prev_comment;
      InputItem * next_token; // next valid token ( not comment or space )

   public:
      bool is_comment ()
      {
         return kind == commentToken ||
                kind == spaceToken ||
                kind == eolToken ||
                kind == unusedDirectiveToken;
      }

      void clear ();

      InputItem ();
      friend class InputQueue;
};

class InputQueue
{
   public:
      InputItem * first;
      InputItem * last;

      InputItem * first_free;
      InputItem * last_free;

   public:
      void insertLast (InputItem * item);
      InputItem * removeFirst ();

      void insertLastFree (InputItem * item);
      InputItem * removeFirstFree ();

      void removeAll ();

   public:
      InputQueue ();
      virtual ~ InputQueue ();
      friend class InputItem;
};

typedef InputItem * InputItemPtr;

/* ---------------------------------------------------------------------- */

class TextBlock
{
   public:
      static const int max = 4 * 1024;

      int len;
      char buf [max];

      TextBlock * next;

      TextBlock ();
};

class TextStorage
{
   private:
      TextBlock * first;
      TextBlock * last;

      TextBlock * first_free;
      TextBlock * last_free;

      int byte_count;

      TextBlock * output;
      int out_pos;

   private:
      void insertBlock (TextBlock * item);
      TextBlock * freeBlock ();
      void newBlock ();

   public:
      void put (char c);
      void put_str (const string s);
      void put_chars (char c, int n);
      void put_data (void * adr, size_t len);

      void put_line (const string s);

      bool empty ();
      int length () { return byte_count; }
      string to_string ();
      string inc_string ();
      string cut_from (int pos);   // text od pozice pos (odebere se)

      void write (const string file_name);
      bool compare (const string file_name);

      void reset ();

      TextStorage ();
      ~ TextStorage ();

      friend class TextOutput;
};

/* ---------------------------------------------------------------------- */

class CharInput
{
   protected:
      static const size_t bufSize = 4 * 1024;

      FILE * inpFile;      // vstup ze souboru (open)
      string inpText;      // vstup z retezce (openString)
      size_t inpTextPos;
      bool inpTextMode;

      size_t bufPos;
      size_t bufLen;
      unsigned char buf [bufSize];

   public:
      int fileInx; // file number
      int linePos; // line counter
      int colPos;  // column counter
      int charPos; // character counter

      int tokenFileInx;
      int tokenLinePos;
      int tokenColPos;
      int tokenCharPos;

      int prevFileInx;
      int prevLinePos;
      int prevColPos;
      int prevCharPos;

      char inpCh; // current input character
      char prevCh; // previous character (for end of line detection)
      bool prevEol; // end of line detected (but linePos will be incremented with next character)
      bool inpEof; // end of source text

      bool positionInitialized;

   public:
      virtual void Init ();

      virtual void readBuf ();
      void readData (void * adr, size_t size);

      void getCh ();

      void message (MessageLevel level, const string msg);

   public:
      void open (string file_name);
      void openString (string text);
      void closeInput ();

      string getFileName ();
      void setFileName (const string file_name);

   public:
      void debug (const string msg);
      void info (const string msg);
      void note (const string msg);
      void warning (const string msg);
      void mistake (const string msg);
      void flaw (const string msg);
      void error (const string msg);
      void abort (const string msg);

   public:
      CharInput ();
      virtual ~ CharInput ();

      friend class TextInput;
      friend class MixedInput;
      friend class EnvInput;
      friend class EnvOutput;
};

/* ---------------------------------------------------------------------- */

class MixedInput
{
   public:
      static const int NO_SYMBOL = 0;
      static const int IDENT = 1;
      static const int NUMBER = 2;
      static const int REAL_NUMBER = 3;
      static const int CHAR_LITERAL = 4;
      static const int STRING_LITERAL = 5;
      static const int SEPARATOR = 5;

   protected:
      CharInput * inp;

      char inpCh;  // current inpput character
      bool inpStarted; // true => inpCh contains valid character
      bool inpEof; // end of source text

      int noMessages; // noMessages > 0 => suppress messages

   protected:
      virtual void Init ();
      virtual void Finish () { }
      void getCh ();

      void setTokenFileInx (int p_file_inx);
      void setTokenLine (int p_line);
      void setTokenCol (int p_col);

      virtual void message (MessageLevel level, const string msg);

   public:
      void open (string name);
      void openString (string text);

      void close () { Finish (); }

      string getFileName ();
      void setFileName (const string file_name);

      int getTokenFileInx () { return (inp == NULL) ? 0 : inp->tokenFileInx; }
      int getTokenLine () { return (inp == NULL) ? 0 : inp->tokenLinePos; }
      int getTokenCol() { return (inp == NULL) ? 0 : inp->tokenColPos; }
      int getTokenPos () { return (inp == NULL) ? 0 : inp->tokenCharPos; }

      int getPrevFileInx () { return (inp == NULL) ? 0 : inp->prevFileInx; }
      int getPrevLine () { return (inp == NULL) ? 0 : inp->prevLinePos; }
      int getPrevCol() { return (inp == NULL) ? 0 : inp->prevColPos; }
      int getPrevPos () { return (inp == NULL) ? 0 : inp->prevCharPos; }

      int getFileInx () { return (inp == NULL) ? 0 : inp->fileInx; }
      int getLine () { return (inp == NULL) ? 0 : inp->linePos; }
      int getCol() { return (inp == NULL) ? 0 : inp->colPos; }
      int getPos () { return (inp == NULL) ? 0 : inp->charPos; }

      void eliminateMessages ();
      void restoreMessages ();

      void debug (const string msg);
      void info (const string msg);
      void note (const string msg);
      void warning (const string msg);
      void mistake (const string msg);
      void flaw (const string msg);
      void error (const string msg);
      void abort (const string msg);

   public:
      InputSymbol symbol;
      TokenKind tokenKind;

      string tokenTxt; // original token
      string tokenVal; // value of string
      char   tokenSym; // value of separator

      bool   anyWhiteSpace; // true => space or comment encountered (sticky bit)

   public:
      virtual string conv (InputSymbol sym) { return "???"; }
      virtual InputSymbol delimiter () { return NO_SYMBOL; }
      virtual InputSymbol keyword (string s) { return NO_SYMBOL; }
      virtual void translate ();
      virtual void getToken () { }

   public:
      MixedInput ();
      virtual ~ MixedInput ();
};

/* ---------------------------------------------------------------------- */

class RewindInput : public MixedInput
{
   public:
      int mark_level;

      InputItem * present;
      InputQueue queue;

      bool comments;

   public:
      inline bool isSymbol (InputSymbol s) // test current symbol
      {
         return symbol == s;
      }

      inline bool testSymbols (const unsigned char table []) // test current symbol with table
      {
         int pos = symbol / 8;
         int bit = symbol % 8;
         return table [pos] & (1 << bit);
      }

   public:
      InputSymbol LA (int i);
      void checkSymbol (InputSymbol s);

   private:
      void pick (); // recall from queue
      void remember (); // store data to queue
      void read (); // read new token
      void retrieve (); // read new token or recall from queue

   public:
      InputItem * mark ();
      void rewind (InputItem * pos);
      void skipRewind ();

      void stop (string msg);
      void stopUnexpected ();

      void saveTrace () { eliminateMessages (); }
      void restoreTrace () { restoreMessages (); }

   protected:
      virtual void Init ();

   public:
      RewindInput ();
      virtual ~ RewindInput ();
};

/* ---------------------------------------------------------------------- */

class TextInput : public RewindInput
{
   public:
      bool dupl_input;
      bool dupl_output;
      unsigned char dupl_input_level;

   protected:
      bool dupl_directives;

   protected:
      TextStorage text_storage;
      TextStorage value_storage;

      TextStorage input_storage;
      TextStorage output_storage;

      TextStorage directive_storage;

   public:
      string inputAsString ();
      string outputAsString ();

      TextStorage * inputAsStorage ();
      TextStorage * outputAsStorage ();

   protected:
      virtual void Init ();

      void nextCh ();
      void textCh ();
      void spaceCh ();

      void addRemark (string txt);

      char character ();
      char pascalCharacter (char pascal_quote);

      void getIdent (bool to_lower_case, bool to_upper_case);
      void getNumber (bool pascal_number);
      void getChar (bool pascal_string);
      void getString (bool pascal_string);

      void storeSeparator (char ch);
      void storeLongSeparator (string s);
      virtual void getSeparator ();

      void skipLine ();
      void getComment ();
      void getPascalComment ();
      void getLineComment ();

      void getTextLine ();

      void getSpace ();
      void getBackslash ();
      void getEol ();

      void getTokenValue ();

   public:
      virtual void getToken ();
      void nextToken () { getToken (); }

      bool isNameToken () { return tokenKind == nameToken; }
      bool isNumber () { return tokenKind == numberToken; }
      bool isReal () { return tokenKind == realToken; }
      bool isChar () { return tokenKind == charToken; }
      bool isString () { return tokenKind == stringToken; }
      bool isSeparatorToken () { return tokenKind == separatorToken; }
      bool isSpace () { return tokenKind == spaceToken; }
      bool isEol ()  { return tokenKind == eolToken; }
      bool isEof () { return tokenKind == eofToken; }

      bool isName (const string s) { return (tokenKind == nameToken) && (tokenTxt == s); }
      bool isSeparator (char c) { return (tokenKind == separatorToken) && (tokenSym == c); }
      bool isLongSeparator (string s) { return (tokenKind == separatorToken) && (tokenTxt == s); }

      void checkName (const string s);
      void checkSeparator (char c);
      void checkEof ();

      string readName ();
      string readNumber ();
      string readReal ();
      char   readChar ();
      string readString ();

      string readCharAsString ();
      string readQuotedCharAsString ();
      string readQuotedString ();

      // name ... identifier or keyword
      // ident ... identifier
      bool isIdentToken () { return symbol == IDENT; }
      bool isIdent (const string s) {return (symbol == IDENT) && (tokenTxt == s); }
      void checkIdent (const string s);
      string readIdent ();

      bool nextSeparator (char c);

      bool   readBool ();

      string readSignedNumber (); // including minus sign
      string readValue (); // identifier, number, character or string

      signed char readSignedChar ();
      short       readShort ();
      int         readInt ();
      long        readLong ();

      unsigned char  readUChar ();
      unsigned short readUShort ();
      unsigned int   readUInt ();
      unsigned long  readULong ();

      float  readFloat ();
      double readDouble ();

      string readRestOfLine ();

      TextInput ();
      virtual ~ TextInput ();
};

/* ---------------------------------------------------------------------- */

class TextOutput
{
   protected:
      TextStorage text_storage;

   private:
      string fileName;
      bool showMsg;

   protected:
      bool startLine;
      bool skipEmptyLine;
      bool addEmptyLine;
      bool ignoreEol;
      bool addSpace;
      bool skipSpace;

   private:
      int indentation;

   public:
      int fileInx;
      int linePos;
      int colPos;

   protected:
      virtual void Init ();
      virtual void Finish () { }

   public:
      void open (string name);
      void close () { Finish (); }

      string getFileName () { return fileName; }
      void setFileName (const string p_filename);

      void enableOutputMessages (bool value); // only for store and writeText

      void store ();
      void writeText ();

      string toString ();
      int textLength () { return text_storage.length (); }
      string cutText (int pos) { return text_storage.cut_from (pos); }   // text od pos (odebere se)
      void insertText (int pos, const string s);   // vlozi text na pozici pos (stav vystupu se nemeni)
      string incString ();

      void reset () { text_storage.reset (); }

   protected:
      virtual void message (MessageLevel level, const string msg);

   public:
      void debug (const string msg);
      void info (const string msg);
      void note (const string msg);
      void warning (const string msg);
      void mistake (const string msg);
      void flaw (const string msg);
      void error (const string msg);
      void abort (const string msg);

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

      void suspendEol ();
      void resumeEol ();

      void send (string s);
      void sendeol ();
      void sendln (string s);

      void style_space ();
      void style_no_space ();
      void style_new_line ();
      void style_empty_line ();
      void style_no_empty_line ();
      void style_indent ();
      void style_unindent ();

      void putBool (bool value);

      void putChar (char value);
      void putString (string value);

      void putInt (int value);
      void putLong (long value);

      void putUInt (unsigned int value);
      void putULong (unsigned long value);

      void putFloat (float value);
      void putDouble (double value);

      // void putBlock (const string s);
      // void putStorage (TextStorage * s);
      // void readFrom (const string file_name);

      // void retrieve_content (TextStorage & param);
      // void append_content (TextStorage & param);

   public:
      TextOutput ();
      virtual ~ TextOutput ();
};

/* ---------------------------------------------------------------------- */

CLOSE_NAMESPACE

#endif /* __PROG_TEXTIO_H__ */
