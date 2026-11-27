
/* textio.cc */

#include "textio.h"

#include "str.h" // const lf, ...
#include "conv.h" // StrToLong, IntToStr, ...
#include "dictionary.h"
#include "inf.h" // function info

#include <string.h> // function memcpy
#include <cstdio> // fopen, fread, fwrite, fclose

#define DUPL_INPUT
#define DUPL_DIRECTIVES


OPEN_NAMESPACE

/******************************* FILE NAMES *******************************/

// global variables

static Dictionary <string, int> FileNameDict;
static Dictionary <int, string> FileNumberDict;
static int last_index = 0;

void clearFileNames ()
{
   FileNameDict.clear ();
   FileNumberDict.clear ();
}

int storeFileName (string file_name)
{
   // const char * c = file_name.c_str ();
   // c = strdup (c);
   // file_name = c;

   int index = 0;

   if (FileNameDict.contains (file_name))
   {
      index = FileNameDict.get (file_name);
   }
   else
   {
      last_index ++;
      index = last_index;
      FileNameDict.store (file_name, index);
      FileNumberDict.store (index, file_name);
   }

   return index;
}

string recallFileName (int index)
{
   return FileNumberDict.get (index);
   // return empty string if file index is not dictionay
   // important for __FILE__ macro expansion
}

int recallFileIndex (string file_name)
{
   return FileNameDict.get (file_name);
}

/****************************** TOKEN TYPES *******************************/

string tokenKindToStr (TokenKind kind)
{
   static string table [] =
   {
      "startToken",

      "nameToken",
      "numberToken",
      "realToken",
      "charToken",
      "stringToken",
      "separatorToken",

      "spaceToken",
      "commentToken",
      "lineContToken",
      "eolToken",

      "textLineToken",

      "unusedDirectiveToken",
      "includeDirectiveToken",
      "processedDirectiveToken",

      "stopToken",
      "finalToken",
      "eofToken"
   };

   const int lim = sizeof (table) / sizeof (table [0]);
   assert (eofToken == lim-1);

   string result;

   if (kind >= 0 && kind < lim)
      result = table [kind];
   else
      result = "tokenKind (" + IntToStr (kind) + ")";

   return result;
}

/******************************* TEXT STORAGE *******************************/

TextBlock::TextBlock () :
   len (0),
   buf (),
   next (NULL)
{
}

/* ---------------------------------------------------------------------- */

TextStorage::TextStorage () :
   first (NULL),
   last (NULL),
   first_free (NULL),
   last_free (NULL),
   byte_count (0),
   output (NULL),
   out_pos (0)
   // enable_msg (true)
{
   insertBlock (new TextBlock ()); // always at least one item
}

TextStorage::~TextStorage ()
{
   TextBlock * item = first;
   while (item != NULL)
   {
      TextBlock * tmp = item->next;
      delete item;
      item = tmp;
   }

   first = NULL;
   last = NULL;

   item = first_free;
   while (item != NULL)
   {
      TextBlock * tmp = item->next;
      delete item;
      item = tmp;
   }

   first_free = NULL;
   last_free = NULL;
   byte_count = 0;
}

/* ---------------------------------------------------------------------- */

void TextStorage::reset ()
{
   // link all items to free

   if (first != NULL)
   {
      if (first_free == NULL)
      {
         assert (last_free == NULL);
         first_free = first;
         last_free = last;
      }
      else
      {
         assert (last_free != NULL);
         last_free->next = first;
         last_free = last;
      }
   }

   first = NULL;
   last = NULL;
   byte_count = 0;

   output = NULL;
   out_pos = 0;

   // set one item as current
   newBlock ();
   // assert (first_free != NULL);
   // insertBlock (freeBlock ());
}

/* ---------------------------------------------------------------------- */

void TextStorage::insertBlock (TextBlock * item)
{
   assert (item != NULL);

   assert (item->next == NULL);
   assert (item->len == 0);

   if (first == NULL)
   {
      assert (last == NULL);
      first = item;
      last = item;
   }
   else
   {
      assert (last != NULL);
      last->next = item;
      last = item;
   }
}

/* ---------------------------------------------------------------------- */

TextBlock * TextStorage::freeBlock ()
{
   TextBlock * result = first_free;
   assert (result != NULL);

   if (result->next == NULL)
   {
      assert (last_free == result);
      first_free = NULL;
      last_free = NULL;
   }
   else
   {
      assert (last_free != NULL);
      first_free = result->next;
   }

   result->len = 0;
   result->next = NULL;

   #ifdef DEBUG
      // not necessary
      memset (result->data, 0, sizeof (result->data));
   #endif

   return result;
}

/* ---------------------------------------------------------------------- */

void TextStorage::newBlock ()
{
   // assert (last != NULL);
   // assert (last->len == last->max);

   if (first_free != NULL)
   {
      // get free item from queue
      insertBlock (freeBlock ());
   }
   else
   {
      // allocate new item
      insertBlock (new TextBlock ());
   }
}

void TextStorage::put (char c)
{
   // info ("put " + quoteStr (charToStr (c)));
   assert (last != NULL);

   if (last->len == last->max)
      newBlock ();

   assert (last->len < last->max);
   last->buf [last->len] = c;
   last->len ++;
   byte_count ++;
}

void TextStorage::put_str (const string s)
{
   int inx = 0;
   int len = s.length ();
   const char * txt = s.c_str ();

   while (inx < len)
   {
      if (last->len == last->max)
         newBlock ();

      int space = last->max - last->len;
      assert (space > 0);

      int step = len - inx;
      if (step > space)
         step = space;

      memcpy (& last->buf [last->len], & txt [inx], step);

      inx += step;
      last->len += step;
      assert (last->len <= last->max);
   }

   byte_count = byte_count + len;
}

void TextStorage::put_line (const string s)
{
   put_str (s);
   // put (cr);
   put (lf);
}

void TextStorage::put_data (void * adr, size_t len)
{
   assert (adr != NULL);
   size_t inx = 0;
   char * array = (char *) adr;

   while (inx < len)
   {
      if (last->len == last->max)
         newBlock ();

      int space = last->max - last->len;
      assert (space > 0);

      int step = len - inx;
      if (step > space)
         step = space;

      memcpy (& last->buf [last->len], & array [inx], step);

      inx += step;
      last->len += step;
      assert (last->len <= last->max);
   }

   byte_count = byte_count + len;
}

void TextStorage::put_chars (char c, int len)
{
   int inx = 0;
   while (inx < len)
   {
      if (last->len == last->max)
         newBlock ();

      int space = last->max - last->len;
      assert (space > 0);

      int step = len - inx;
      if (step > space)
         step = space;

      memset (& last->buf [last->len], c, step);

      inx += step;
      last->len += step;
      assert (last->len <= last->max);
   }

   if (len > 0)
      byte_count = byte_count + len;   // cecko: chybelo (length () nesouhlasila s textem)
}

/* ---------------------------------------------------------------------- */

bool TextStorage::empty ()
{
   return first == NULL || first->len == 0;
}

string TextStorage::to_string ()
{
   string result = "";
   int size = 0;

   // calculate length
   TextBlock * item = first;
   while (item != NULL)
   {
      size = size + item->len;
      item = item->next;
   }

   result.reserve (size);

   // copy value
   item = first;
   while (item != NULL)
   {
      result += bufToStr (item->buf, item->len);
      item = item->next;
   }

   // info ("str " + result);
   // info ("size " + IntToStr (size));
   return result;
}

string TextStorage::inc_string ()
{
   string result = "";
   int size = 0;

   if (output == NULL)
      output = first;

   // calculate length
   TextBlock * item = output;
   if (item != NULL)
   {
      size = size + item->len-out_pos;
      item = item->next;
   }
   while (item != NULL)
   {
      size = size + item->len;
      item = item->next;
   }

   result.reserve (size);

   // copy value
   item = output;
   if (item != NULL)
   {
      result += bufToStr (&item->buf [out_pos], item->len - out_pos);
      // & is important, otherwise same repeated characters are added
      item = item->next;
   }
   while (item != NULL)
   {
      result += bufToStr (item->buf, item->len);
      item = item->next;
   }

   output = last;
   out_pos = output->len;

   return result;
}

/* text od pozice pos do konce - z ulozeneho textu se odebere (bloky za pozici se uvolni) */
string TextStorage::cut_from (int pos)
{
   string result = "";
   if (pos < 0 || pos >= byte_count)
      return result;

   // blok s pozici pos
   int start = 0;
   TextBlock * item = first;
   while (item != NULL && start + item->len <= pos)
   {
      start = start + item->len;
      item = item->next;
   }
   if (item == NULL)
      return result;

   int offset = pos - start;
   result = bufToStr (&item->buf [offset], item->len - offset);
   TextBlock * rest = item->next;
   while (rest != NULL)
   {
      result += bufToStr (rest->buf, rest->len);
      rest = rest->next;
   }

   // zkratit: blok s pozici, dalsi bloky do seznamu volnych
   rest = item->next;
   item->len = offset;
   item->next = NULL;
   last = item;
   while (rest != NULL)
   {
      TextBlock * next = rest->next;
      rest->len = 0;
      rest->next = NULL;
      if (last_free == NULL) first_free = rest; else last_free->next = rest;
      last_free = rest;
      rest = next;
   }
   byte_count = pos;
   output = NULL;   // inc_string od zacatku
   out_pos = 0;
   return result;
}

/* ---------------------------------------------------------------------- */

void TextStorage::write (const string file_name)
{
   FILE * f = fopen (file_name.c_str (), "wb");
   if (f == NULL)
   {
      error ("Cannot open file for writing: " + file_name); // simple error form inf.h
      return;
   }

   bool ok = true;
   TextBlock * item = first;
   while (item != NULL)
   {
      if (item->len > 0 && fwrite (item->buf, 1, item->len, f) != (size_t) item->len)
         ok = false;
      item = item->next;
   }

   if (fclose (f) != 0)
      ok = false;
   if (! ok)
      error ("error writing file: " + file_name); // simple error form inf.h
}

/* ---------------------------------------------------------------------- */

bool TextStorage::compare (const string file_name)
// true => soubor existuje a ma stejny obsah (stejna delka i data)
{
   bool equal = false;

   FILE * f = fopen (file_name.c_str (), "rb");
   if (f != NULL)
   {
      equal = true;
      char data [TextBlock::max];

      TextBlock * item = first;
      while (equal && item != NULL)
      {
         int len = item->len;
         assert (len <= TextBlock::max);
         if (len > 0)
         {
            size_t count = fread (data, 1, len, f);
            if (count != (size_t) len || memcmp (data, item->buf, len) != 0)
               equal = false;
         }
         item = item->next;
      }

      if (equal && fread (data, 1, 1, f) != 0)
         equal = false; // soubor je delsi

      fclose (f);
   }

   return equal;
}

/********************************* QUEUE **********************************/

/* InputItem */

InputItem::InputItem () :
   symbol (0),
   kind (startToken),
   token_text (""),
   token_val (""),
   token_sym (' '),

   inp_ch (0),
   inp_started (false),
   inp_eof (false),

   file_num (0),
   line_num (0),
   col_num (0),

   next (NULL),
   prev_comment (NULL),
   next_token (NULL)
{ }

void InputItem::clear ()
{
   file_num = 0;
   line_num = 0;
   col_num = 0;

   symbol = 0;
   kind = startToken;
   token_text = "";

   // do not change 'next' field
   prev_comment = NULL;
   next_token = NULL;
}

/* InputQueue */

void InputQueue::insertLast (InputItem * item)
{
   // assert (this != NULL);
   assert (item != NULL);
   assert (item->next == NULL);

   item->next = NULL;

   if (last != NULL)
      last->next = item;
   else
      first = item;

   last = item;
}

InputItem * InputQueue::removeFirst ()
{
   InputItem * p = first;
   assert (p != NULL);

   first = p->next;

   if (first == NULL)
      last = NULL;

   p->next = NULL; // important
   return p;
}

void InputQueue::insertLastFree (InputItem * item)
{
   // assert (this != NULL);
   assert (item != NULL);
   assert (item->next == NULL);

   item->next = NULL;

   if (last_free != NULL)
      last_free->next = item;
   else
      first_free = item;

   last_free = item;
}

InputItem * InputQueue::removeFirstFree ()
{
   InputItem * p = first_free;
   assert (p != NULL);

   first_free = p->next;

   if (first_free == NULL)
      last_free = NULL;

   p->next = NULL; // important
   return p;
}

void InputQueue::removeAll ()
{
   InputItem * p = first;
   while (p != NULL)
   {
      InputItem * t = p;
      p = p->next;
      delete t;
   }

   first = NULL;
   last = NULL;

   p = first_free;
   while (p != NULL)
   {
      InputItem * t = p;
      p = p->next;
      delete t;
   }

   first_free = NULL;
   last_free = NULL;
}

InputQueue::~InputQueue ()
{
   removeAll ();
}

InputQueue::InputQueue () :
   first (NULL),
   last (NULL),
   first_free (NULL),
   last_free (NULL)
{ }

/******************************* CHAR INPUT *******************************/

CharInput::CharInput ():
   inpFile (NULL),
   inpText (""),
   inpTextPos (0),
   inpTextMode (false),
   bufPos (0),
   bufLen (0),
   // ignore buf

   fileInx (0),
   linePos (0),
   colPos (0),
   charPos (0),

   tokenFileInx (0),
   tokenLinePos (0),
   tokenColPos (0),
   tokenCharPos (0),

   prevFileInx (0),
   prevLinePos (0),
   prevColPos (0),
   prevCharPos (0),

   inpCh (0),
   prevCh (0),
   prevEol (false),
   inpEof (false),

   positionInitialized (false)
{
}

CharInput::~CharInput ()
{
   closeInput ();
}

void CharInput::Init ()
{
   bufPos = 0;
   bufLen = 0;
   // do not change already initialized inpFile, inpText and fileName

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
}

string CharInput::getFileName ()
{
   return recallFileName (fileInx);
}

void CharInput::setFileName (const string file_name)
{
   fileInx = storeFileName (file_name);
}

/* ---------------------------------------------------------------------- */

void CharInput::closeInput ()
{
   if (inpFile != NULL)
   {
      fclose (inpFile);
      inpFile = NULL;
   }
   inpText = "";
   inpTextPos = 0;
   inpTextMode = false;
}

void CharInput::openString (string text)
{
   closeInput ();
   inpText = text;
   inpTextPos = 0;
   inpTextMode = true;
   Init ();
}

void CharInput::open (string name)
{
   setFileName (name);
   closeInput ();

   inpFile = fopen (name.c_str (), "rb");

   if (inpFile == NULL)
      error ("Cannot open " + name);
   else
      Init ();
}

/* ---------------------------------------------------------------------- */

void CharInput::readBuf ()
{
   assert (inpFile != NULL || inpTextMode);
   bufLen = 0;
   if (inpFile != NULL)
   {
      bufLen = fread (buf, 1, bufSize, inpFile);
   }
   else
   {
      size_t len = inpText.length ();
      if (inpTextPos < len)
      {
         bufLen = len - inpTextPos;
         if (bufLen > bufSize)
            bufLen = bufSize;
         memcpy (buf, inpText.c_str () + inpTextPos, bufLen);
         inpTextPos += bufLen;
      }
   }
   bufPos = 0;
}

void CharInput::readData (void * adr, size_t size)
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

      memcpy (adr, & buf[bufPos], step);
      bufPos += step;
      size -= step;

      adr = (void *) ((char *) (adr) + step);

      assert (size >= 0);
   }
}

void CharInput::getCh ()
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

void CharInput::message (MessageLevel level, const string msg)
{
   global_message (level, msg, getFileName (), linePos, colPos);
}

void CharInput::debug (const string msg)
{
   message (debugLevel, msg);
}

void CharInput::info (const string msg)
{
   message (infoLevel, msg);
}

void CharInput::note (const string msg)
{
   message (noteLevel, msg);
}

void CharInput::warning (const string msg)
{
   message (warningLevel, msg);
}

void CharInput::mistake (const string msg)
{
   message (mistakeLevel, msg);
}

void CharInput::flaw (const string msg)
{
   message (flawLevel, msg);
}

void CharInput::error (const string msg)
{
   message (errorLevel, msg);
}

void CharInput::abort (const string msg)
{
   message (abortLevel, msg);
}

/****************************** MIXED INPUT *******************************/

MixedInput::MixedInput ():
   inp (NULL),

   inpCh (0),
   inpStarted (false),
   inpEof (false),

   noMessages (0),

   tokenKind (startToken),

   tokenTxt (""),
   tokenVal (""),
   tokenSym (0),

   anyWhiteSpace (false)
{
}

MixedInput::~MixedInput ()
{
   if (inp != NULL)
   {
      delete inp;
      inp = NULL;
   }
}

/* ---------------------------------------------------------------------- */

void MixedInput::Init ()
{
   // inpCh = 0;
   // inpEof = false;

   assert (inp != NULL);
   inp->Init ();

   inpCh = inp->inpCh;
   inpStarted = false;
   inpEof = inp->inpEof;

   // do not read first character, already called by TextInput::Init ()

   symbol = NO_SYMBOL;
   tokenKind = startToken;
   tokenTxt = "";
   tokenVal = "";
   tokenSym = 0;
   anyWhiteSpace = false;
}

/* ---------------------------------------------------------------------- */

void MixedInput::openString (string text)
{
   if (inp == NULL)
      inp = new CharInput;

   inp->openString (text);
   Init (); // after open, important
}

void MixedInput::open (string name)
{
   if (inp == NULL)
      inp = new CharInput;

   inp->open (name);
   Init (); // after open, important
}

/* ---------------------------------------------------------------------- */

void MixedInput::getCh ()
{
   assert (inp != NULL);
   inp->getCh ();

   inpCh = inp->inpCh;
   inpEof = inp->inpEof;
   inpStarted = true;

   // info ("character: " + quoteStr (charToStr (inpCh)));
}

/* ---------------------------------------------------------------------- */

string MixedInput::getFileName ()
{
   assert (inp != NULL);
   return inp->getFileName ();
}

void MixedInput::setFileName (const string p_filename)
{
   assert (inp != NULL);
   inp->setFileName (p_filename);
}

#if 0
int MixedInput::getTokenFileInx ()
{
   assert (inp != NULL);
   return inp->tokenFileInx;
}

int MixedInput::getTokenLine ()
{
   assert (inp != NULL);
   return inp->tokenLinePos;
}

int MixedInput::getTokenCol ()
{
   assert (inp != NULL);
   return inp->tokenColPos;
}
#endif

void MixedInput::setTokenFileInx (int p_file_inx)
{
   assert (inp != NULL);
   inp->tokenFileInx = p_file_inx;
}

void MixedInput::setTokenLine (int p_line)
{
   assert (inp != NULL);
   inp->tokenLinePos = p_line;
}

void MixedInput::setTokenCol (int p_col)
{
   assert (inp != NULL);
   inp->tokenColPos = p_col;
}

/* ---------------------------------------------------------------------- */

void MixedInput::eliminateMessages ()
{
    assert (noMessages >= 0);
    noMessages ++;
}

void MixedInput::restoreMessages ()
{
    noMessages --;
    assert (noMessages >= 0);
}

/* ---------------------------------------------------------------------- */

void MixedInput::message (MessageLevel level, const string msg)
{
   string file_name = "";
   int line = 0;
   int column = 0;

   if (inp != NULL)
   {
      #if 0
      file_name = inp->getFileName ();
      line = inp->linePos;
      column = inp->colPos;
      #endif

      file_name = recallFileName (inp->tokenFileInx);
      line = inp->tokenLinePos;
      column = inp->tokenColPos;
   }

   if (noMessages == 0)
   {
       global_message (level, msg, file_name, line, column);
   }
   else
   {
      if (level == flawLevel || level == errorLevel)
         raise_error (msg, file_name, line, column, false);
         // stop parsing (originally exception, nobody catches it except main)

      if (level == abortLevel)
         global_message (abortLevel, msg, file_name, line, column);
   }
}

/* ---------------------------------------------------------------------- */

void MixedInput::debug (const string msg)
{
   message (debugLevel, msg);
}

void MixedInput::info (const string msg)
{
   message (infoLevel, msg);
}

void MixedInput::note (const string msg)
{
   message (noteLevel, msg);
}

void MixedInput::warning (const string msg)
{
   message (warningLevel, msg);
}

void MixedInput::mistake (const string msg)
{
   message (mistakeLevel, msg);
}

void MixedInput::flaw (const string msg)
{
   message (flawLevel, msg);
}

void MixedInput::error (const string msg)
{
   message (errorLevel, msg);
}

void MixedInput::abort (const string msg)
{
   message (abortLevel, msg);
}

/**************************** LOOK AHEAD INPUT ****************************/

RewindInput::RewindInput ():

   mark_level (0),

   present (NULL),
   queue (),

   comments (false)
{
}

RewindInput::~RewindInput ()
{
}

/* ---------------------------------------------------------------------- */

void RewindInput::Init ()
{
   MixedInput::Init ();

   queue.removeAll (); // !?

   mark_level = 0;

   present = NULL;
}

/* ---------------------------------------------------------------------- */

void RewindInput::stop (string msg)
{
   error (msg + ", tokenKind=" + tokenKindToStr (tokenKind) + ", tokenTxt=" + tokenTxt +
                ", symbol = " + IntToStr (symbol) + ", symbol = " + conv (symbol));

}

void RewindInput::stopUnexpected ()
{
   if (tokenKind == eofToken)
      stop ("Unexpected end of source text");
   else
      stop ("Unexpected token " + conv (symbol));
}

/* ---------------------------------------------------------------------- */

void RewindInput::pick ()
{
   assert (present != NULL);

   symbol = present->symbol;
   tokenKind = present->kind;

   tokenTxt = present->token_text;
   tokenVal = present->token_val;
   tokenSym = present->token_sym;

   inpCh = present->inp_ch;
   inpStarted = present->inp_started;
   inpEof = present->inp_eof;

   tokenVal = ""; // !? clean
   tokenSym = ' '; // !? clean

   setTokenFileInx (present->file_num);
   setTokenLine (present->line_num);
   setTokenCol (present->col_num);

   // info ("pick " + conv (symbol) + " " + tokenTxt);
}

/* ---------------------------------------------------------------------- */

void RewindInput::remember ()
{
   assert (present != NULL);

   present->symbol = symbol;
   present->kind = tokenKind;

   present->token_text = tokenTxt;
   present->token_val = tokenVal;
   present->token_sym = tokenSym;

   present->inp_ch = inpCh;
   present->inp_started = inpStarted;
   present->inp_eof = inpEof;

   present->file_num = getTokenFileInx ();
   present->line_num = getTokenLine ();
   present->col_num = getTokenCol ();

   // info ("remember " + conv (symbol) + " " + tokenTxt);
}

/* ---------------------------------------------------------------------- */

#if 0
void RewindInput::read ()
{
   bool done = false;

   while (! done)
   {
      getToken ();

      if (tokenKind != commentToken &&
          tokenKind != spaceToken &&
          tokenKind != eolToken  &&
          tokenKind != unusedDirectiveToken )
      {
         done = true;
      }
   }
}
#endif

#if 1
void RewindInput::read ()
{
   InputItem * stop = queue.last; // previous token
   InputItem * start = NULL;
   bool done = false;

   while (! done)
   {
      getToken ();

      if (tokenKind != commentToken &&
          tokenKind != spaceToken &&
          tokenKind != eolToken  &&
          tokenKind != unusedDirectiveToken )
      {
         done = true;
      }

      if (done || comments)
      {
         // add new item into queue
         if (queue.first_free != NULL)
         {
            present = queue.removeFirstFree ();
            present->clear ();
         }
         else
         {
            present = new InputItem;
         }
         queue.insertLast (present);
      }

      // if (done)
      //    translate ();

      // store token
      if (done || comments)
         remember ();

      if (start == NULL)
         start = present;
   }

   // pointer to previous comment
   present->prev_comment = start;

   // link previous token
   if (stop != NULL)
      stop->next_token = present;

}
#endif

#if 0
void RewindInput::read ()
{
   InputItem * stop = queue.last; // previous token
   InputItem * start = NULL;
   bool done = false;

   while (! done)
   {
      getToken ();

      if (tokenKind != commentToken &&
          tokenKind != spaceToken &&
          tokenKind != eolToken  &&
          tokenKind != unusedDirectiveToken )
      {
         done = true;
      }

      if ((done || comments) && mark_level != 0)
      {
         // add new item into queue
         if (queue.first_free != NULL)
         {
            present = queue.removeFirstFree ();
            present->clear ();
         }
         else
         {
            present = new InputItem;
         }
         queue.insertLast (present);
      }

      // if (done)
      //    translate ();

      if (mark_level != 0)
      {
         // store token
         if (done || comments)
            remember ();

         if (start == NULL)
            start = present;
      }
   }

   if (mark_level != 0)
   {
      // pointer to previous comment
      present->prev_comment = start;

      // link previous token
      if (stop != NULL)
         stop->next_token = present;
   }

}
#endif

/* ---------------------------------------------------------------------- */

void RewindInput::retrieve ()
{
   if (present != NULL)
   {
      // !? !!
      #if 0
      if (! comments && mark_level == 0) // no locations, notes and not in mark/rewind
      {
         // move present item to free list
         assert (present == queue.first);
         InputItem * item = queue.removeFirst ();
         item->prev_comment = NULL;
         item->next_token = NULL;
         queue.insertLastFree (item);

         // set actual item
         present = queue.first;
      }
      else
      #endif
      {
         // move to actual item
         present = present->next_token;
      }
   }

   if (present == NULL)
   {
      // read next token
      read ();
   }
   else
   {
      // use item from queue
      pick ();
   }
}

/* ---------------------------------------------------------------------- */

InputItem * RewindInput::mark ()
// remember current position
{
   // info ("mark");
   mark_level ++;
   return present;
}

void RewindInput::rewind (InputItem * pos)
// return to previous position
{
   // info ("rewind");
   mark_level --;
   present = pos;
   retrieve ();
}

void RewindInput::skipRewind ()
{
   // info ("skipRewind");
   mark_level --;
   // !?
}

/* ---------------------------------------------------------------------- */

void RewindInput::checkSymbol (InputSymbol s)
// compare token and read next token
{
   if (symbol != s)
   {
      stop (quoteStr (conv (s)) + " expected");
   }

   retrieve ();
}

InputSymbol RewindInput::LA (int i)
{
   InputSymbol result;

   if (i == 1)
   {
      result = symbol;
   }
   else
   {
      // !? not efficient
      InputItem * inx = mark ();
      for (int k = 1; k <= i-1; k++)
         retrieve ();
      result = symbol;
      rewind (inx);
   }

   // info ("LA (" + IntToStr (i) + ")  = " + conv (result));
   return result;
}

/******************************* TEXT INPUT *******************************/

TextInput::TextInput ():

   dupl_input (false),
   dupl_output (false),
   dupl_input_level (0),

   dupl_directives (false),

   text_storage (),
   value_storage (),

   input_storage (),
   output_storage (),

   directive_storage ()
{
}

TextInput::~TextInput ()
{
}

/* ---------------------------------------------------------------------- */

void TextInput::Init ()
{
   // original method
   RewindInput::Init ();

   text_storage.reset ();

   dupl_directives = false;
   directive_storage.reset ();

   input_storage.reset ();
   output_storage.reset ();

   // not necessary
   value_storage.reset ();

   // read first character
   nextCh ();
}

/* ---------------------------------------------------------------------- */

string ShowChr (char c)
{
   if (c >= ' ' && c <= 127)
      return charToStr (c);
   if (c == lf)
      return quoteStrContent (charToStr (c)) + charToStr (c);
   else
      return quoteStrContent (charToStr (c));
}

void TextInput::nextCh ()
{
   // NO value_storage.put (inpCh); // token characters
   text_storage.put (inpCh); // characters from original source

   #ifdef DUPL_DIRECTIVES
      if (dupl_directives && inpStarted)
         directive_storage.put (inpCh);
   #endif

   #ifdef DUPL_INPUT
      if (dupl_input && inpStarted && dupl_input_level == 0)
         input_storage.put (inpCh);
         // input_storage.put_str (ShowChr (inpCh));
   #endif

   getCh ();
}

void TextInput::textCh ()
// characters in string literals
{
   // NO value_storage.put (inpCh);
   text_storage.put (inpCh);

   #ifdef DUPL_DIRECTIVES
      if (dupl_directives && inpStarted)
         directive_storage.put (inpCh);
   #endif

   #ifdef DUPL_INPUT
      if (dupl_input && inpStarted && dupl_input_level == 0)
         input_storage.put (inpCh);
         // input_storage.put_str (ShowChr (inpCh));
   #endif

   getCh ();
}

void TextInput::spaceCh ()
// characters in comments and white spaces
{
   // NO value_storage.put (inpCh);
   text_storage.put (inpCh);

   #ifdef DUPL_DIRECTIVES
      if (dupl_directives && inpStarted)
         directive_storage.put (inpCh);
   #endif

   #ifdef DUPL_INPUT
      if (dupl_input && inpStarted && dupl_input_level == 0)
         input_storage.put (inpCh);
         // input_storage.put_str (ShowChr (inpCh));
   #endif

   getCh ();
}

void TextInput::addRemark (string txt)
// preprocessing remark
{
   #ifdef DUPL_INPUT
      // if (dupl_input)
      //    input_storage.put_str (txt);
   #endif
}

/* ---------------------------------------------------------------------- */

void TextInput::getIdent (bool to_lower_case, bool to_upper_case)
{
   while (isLetterOrDigit (inpCh))
      nextCh ();

   tokenTxt = text_storage.to_string ();
   tokenVal = "";
   tokenSym = 0;
   tokenKind = nameToken;

   if (to_lower_case)
     tokenTxt = lowerCase (tokenTxt);

   if (to_upper_case)
     tokenTxt = upperCase (tokenTxt);
}

void TextInput::getNumber (bool pascal_number)
{
   bool hex = false;
   bool any_digit = false;
   bool floating_point = false;

   if (inpCh == '0' && ! pascal_number)
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
   else if (inpCh == '$' && pascal_number)
   {
      nextCh (); // store '$'
      hex = true;

      while (isHexDigit (inpCh))
      nextCh ();
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

         if (pascal_number)
         {
            if (!any_digit && isDigit (inpCh))
               error ("Missing digit before decimal point");
            if (any_digit && ! isDigit (inpCh))
               error ("Digit after decimal point expected");
         }

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

   if (any_digit && ! pascal_number)
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
      tokenTxt = text_storage.to_string ();
      tokenVal = "";
      tokenSym = 0;

      if (floating_point)
         tokenKind = realToken;
      else
         tokenKind = numberToken;
   }
   else
   {
      if (pascal_number && inpCh == '.')
         storeLongSeparator ("..");
      else
         storeSeparator ('.');
   }
}

char TextInput::character ()
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
        return (char) n;  // cecko: (char) n - cmm nezna char (n)
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
        return (char) n;  // cecko: (char) n - cmm nezna char (n)
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

// read one Pascal-style character
char TextInput::pascalCharacter (char pascal_quote)
{
  if (inpCh == pascal_quote)
     textCh ();                       // skip backslash

  char last = inpCh;
  textCh ();
  return last;
}

void TextInput::getChar (bool pascal_string)
{
   textCh (); // skip quote

   // if (inpCh == quote1)
   //    error ("Empty character constant");

   while (inpCh != quote1)
   {
      if (inpEof || inpCh == cr || inpCh == lf)
         error ("character constant exceeds line");

      char c;

      if (pascal_string)
         c = pascalCharacter (quote1);
      else
         c = character ();

      value_storage.put (c);
   }

   textCh (); // skip quote

   tokenTxt = text_storage.to_string (); // with quotes and escape sequences
   tokenVal = value_storage.to_string (); // value without quotes and escape sequences
   tokenSym = 0;
   tokenKind = charToken;

   if (pascal_string)
      tokenKind = stringToken;
}

void TextInput::getString (bool pascal_string)
{
   textCh (); // skip quote

   while (inpCh != quote2)
   {
      if (inpEof || inpCh == cr || inpCh == lf)
         error ("String exceeds line");

      char c;

      if (pascal_string)
         c = pascalCharacter (quote2); // accept double quoted strings
      else
         c = character ();

      value_storage.put (c);
   }

   textCh (); // skip quote

   tokenTxt = text_storage.to_string (); // string with quotes and escape sequences
   tokenVal = value_storage.to_string (); // value without quotes and escape sequences
   tokenSym = 0;
   tokenKind = stringToken;
}

void TextInput::getTextLine ()
{
   textCh (); // skip apostrophe

   while (! inpEof && (inpCh != cr) && (inpCh != lf))
   {
      value_storage.put (inpCh);
      textCh ();
   }

   tokenTxt = text_storage.to_string ();
   tokenVal = value_storage.to_string (); // without first apostrophe
   tokenSym = 0;
   tokenKind = textLineToken;
}


string TextInput::readRestOfLine ()
{
   while (! inpEof && (inpCh != cr) && (inpCh != lf))
   {
      value_storage.put (inpCh);
      textCh ();
   }

   tokenTxt = text_storage.to_string ();
   tokenVal = value_storage.to_string (); // without first apostrophe
   tokenSym = 0;
   tokenKind = textLineToken;

   // !? if (opt.showTokens)
   // !?   info ("token: " + tokenKindToStr (tokenKind) + " " + quoteStr (tokenTxt) /* + " " + quoteChr (tokenSym) */ );

   return tokenVal; // without first character
}

/* ---------------------------------------------------------------------- */

void TextInput::storeSeparator (char ch)
{
   text_storage.put (ch);

   tokenTxt = ch;
   tokenVal = "";
   tokenSym = ch; // important
   tokenKind = separatorToken;
 }

void TextInput::storeLongSeparator (string s)
{
   text_storage.put_str (s);

   tokenTxt = s;
   tokenVal = "";
   tokenSym = 0; // !?
   tokenKind = separatorToken;
 }

void TextInput::getSeparator ()
{
   char c = inpCh;
   nextCh ();
   storeSeparator (c);
}

/* ---------------------------------------------------------------------- */

void TextInput::getSpace ()
{
   while (! inpEof && inpCh <= ' ' && inpCh != cr && inpCh != lf) // WHITE SPACE
      spaceCh ();

   tokenTxt = text_storage.to_string ();
   tokenVal = "";
   tokenSym = 0;
   tokenKind = spaceToken;

   anyWhiteSpace = true;
}

void TextInput::getBackslash ()
{
   assert (inpCh == backslash);
   spaceCh ();

   if (! inpEof && (inpCh == cr || inpCh == lf))
   {
      spaceCh ();

      tokenTxt = text_storage.to_string ();
      tokenVal = "";
      tokenSym = 0;
      tokenKind = lineContToken;
   }
   else
   {
      storeSeparator (backslash);
   }
}

void TextInput::getEol ()
{
   if (! inpEof && inpCh == cr)
      spaceCh (); // skip cr

   if (! inpEof && inpCh == lf)
      spaceCh (); // skip lf

   tokenTxt = text_storage.to_string ();
   tokenVal = "";
   tokenSym = 0;
   tokenKind = eolToken;
}

/* ---------------------------------------------------------------------- */

void TextInput::skipLine ()
{
   while (! inpEof && inpCh != cr && inpCh != lf)
      spaceCh ();
}

void TextInput::getLineComment ()
{
   skipLine ();

   tokenTxt = text_storage.to_string ();
   tokenVal = "";
   tokenSym = 0;
   tokenKind = commentToken;
}

void TextInput::getComment ()
{
   bool slash = false;

   assert (inpCh == '/');
   spaceCh (); // skip slash

   if (! inpEof && inpCh == '/') // SINGLE LINE COMMENT
   {
      skipLine ();
   }

   else if (! inpEof && inpCh == '*')  // COMMENT
   {
      spaceCh (); // skip asterisk

      char prev = ' ';
      while (! inpEof && ! (prev == '*' && inpCh == '/'))
      {
         prev = inpCh;
         spaceCh ();
      }

      if (! inpEof)
         spaceCh (); // skip slash
   }

   else slash = true; // SLASH

   if (slash)
   {
      storeSeparator ('/');
   }
   else
   {
      tokenTxt = text_storage.to_string ();
      tokenVal = "";
      tokenSym = 0;
      tokenKind = commentToken;
      anyWhiteSpace = true;
   }
}

void TextInput::getPascalComment ()
{
   bool slash = false;
   bool parenthesis = false;

   if (inpCh == '/')
   {
      spaceCh (); // skip slash

      if (! inpEof && inpCh == '/') // SINGLE LINE COMMENT
         skipLine ();
      else
         slash = true;
   }
   else if (inpCh == '{')
   {
      spaceCh (); // skip braces

      while (! inpEof && inpCh != '}')
         spaceCh ();

      if (! inpEof)
      spaceCh (); // skip braces
   }
   else if (inpCh == '(')
   {
      spaceCh (); // skip parenthesis

      if (! inpEof && inpCh == '*') // COMMENT
      {
         spaceCh (); // skip asterisk

         char prev = ' ';
         while (! inpEof && ! (prev == '*' && inpCh == ')'))
         {
            prev = inpCh;
            spaceCh ();
         }

         if (! inpEof)
            spaceCh (); // skip parenthesis
      }
      else parenthesis = true; // PARENTHESIS
   }

   if (slash)
      storeSeparator ('/');
   else if (parenthesis)
      storeSeparator ('(');
   else
   {
      tokenTxt = text_storage.to_string ();
      tokenVal = "";
      tokenSym = 0;
      tokenKind = commentToken;
   }
}

/* ---------------------------------------------------------------------- */

void TextInput::getTokenValue ()
{
   value_storage.reset ();
   text_storage.reset ();

   if (inpEof)                                 // END OF FILE
   {
      tokenTxt = "";
      tokenVal = "";
      tokenSym = 0;
      tokenKind = eofToken;
   }

   else if (isLetter (inpCh))                  // IDENTIFIER
      getIdent (false, false);

   else if (isDigit (inpCh))                   // NUMBER
      getNumber (false);

   else if (inpCh == '.')                      // NUMBER or PERIOD
      getNumber (false);

   else if (inpCh == quote1)                   // CHARACTER
      getChar (false);

   else if (inpCh == quote2)                   // STRING
      getString (false);

   else if (inpCh == '/')                      // COMMENT (or slash)
      getComment ();

   else if (inpCh == cr || inpCh == lf)        // END OF LINE
      getEol ();

   else if (inpCh <= ' ')                      // WHITE SPACE
      getSpace ();

   else if (inpCh == backslash)                // BACKSLASH
      getBackslash ();

   else                                        // SEPARATOR
      getSeparator ();
}

/* ---------------------------------------------------------------------- */

void TextInput::getToken ()
// simple TextInput::getToken, redefined in TEnvInput::getToken
{
   assert (inp != NULL);

   inp->prevFileInx = inp->tokenFileInx;
   inp->prevLinePos = inp->tokenLinePos;
   inp->prevColPos  = inp->tokenColPos;
   inp->prevCharPos = inp->tokenCharPos;

   again:

   // store token position
   assert (inp != NULL);
   inp->tokenFileInx = inp->fileInx;
   inp->tokenLinePos = inp->linePos;
   inp->tokenColPos  = inp->colPos;
   inp->tokenCharPos = inp->charPos;

   getTokenValue ();

   if (tokenKind == startToken) goto again;
   if (tokenKind == commentToken) goto again;
   if (tokenKind == lineContToken) goto again;
   if (tokenKind == spaceToken) goto again;
   if (tokenKind == eolToken) goto again;
}

void MixedInput::translate ()
{
   symbol = NO_SYMBOL;

   switch (tokenKind)
   {
      case nameToken:
         symbol = keyword (tokenTxt);
         if (symbol == NO_SYMBOL)
            symbol = IDENT;
         break;

      case numberToken:
         symbol = NUMBER;
         break;

      case realToken:
         symbol = REAL_NUMBER;
         break;

      case charToken:
         symbol = CHAR_LITERAL;
         break;

      case stringToken:
         symbol = STRING_LITERAL;
         break;

      case separatorToken:
         symbol = delimiter ();
         if (symbol == NO_SYMBOL)
         {
            symbol = SEPARATOR;
            // error ("Unknown separator " + tokenTxt);
         }
         break;

      default: ;
   }

   // info ("TRANSLATE tokenTxt= " + tokenTxt + ", symbol = " + IntToStr (symbol) + ", symbol = " + conv (symbol));
}

/* ---------------------------------------------------------------------- */

bool TextInput::nextSeparator (char par)
{
   while (! inpEof && inpCh <= ' ' && inpCh != cr && inpCh != lf) // WHITE SPACE
      spaceCh ();
   return inpCh == par;
}

/* ---------------------------------------------------------------------- */

string TextInput::inputAsString ()
{
   return input_storage.to_string ();
}

string TextInput::outputAsString ()
{
   return output_storage.to_string ();
}

TextStorage * TextInput::inputAsStorage ()
{
   return & input_storage;
}

TextStorage * TextInput::outputAsStorage ()
{
   return & output_storage;
}

/* ---------------------------------------------------------------------- */

void TextInput::checkName (string s)
{
   if (tokenKind != nameToken || tokenTxt != s)
      // error (s + " expected");
      error (s + " expected and found " + quoteStr (tokenTxt));
   getToken ();
}

void TextInput::checkSeparator (char c)
{
   if (tokenKind != separatorToken || tokenSym != c)
   {
      // error (charToStr (c) + " expected");
      error (charToStr (c) + " expected and found " + quoteStr (tokenTxt));
   }
   getToken ();
}

void TextInput::checkEof ()
{
   if (tokenKind != eofToken)
      error ("End of file expected");
}

/* ---------------------------------------------------------------------- */

string TextInput::readName ()
{
   string result;
   if (tokenKind != nameToken)
      error ("Identifier expected");
   result = tokenTxt;
   getToken ();
   return result;
}

string TextInput::readNumber ()
{
   string result;
   if (tokenKind != numberToken)
      error ("Number expected");
   result = tokenTxt;
   getToken ();
   return result;
}

string TextInput::readReal ()
{
   string result;
   if (tokenKind != realToken)
      error ("Real number expected");
   result = tokenTxt;
   getToken ();
   return result;
}

char TextInput::readChar ()
{
   char result;
   if (tokenKind != charToken)
      error ("Character constant expected");
   result = tokenVal [0];
   getToken ();
   return result;
}

string TextInput::readCharAsString ()
{
   string result;
   if (tokenKind != charToken)
      error ("Character constant expected");
   result = tokenVal; // without quotes
   getToken ();
   return result;
}

string TextInput::readQuotedCharAsString ()
{
   string result;
   if (tokenKind != charToken)
      error ("Character constant expected");
   result = tokenTxt; // with quotes
   getToken ();
   return result;
}

string TextInput::readString ()
{
   string result;
   if (tokenKind != stringToken)
      error ("String expected");
   result = tokenVal; // without quotes
   getToken ();
   return result;
}

string TextInput::readQuotedString ()
{
   string result;
   if (tokenKind != stringToken)
      error ("String expected");
   result = tokenTxt; // with quotes
   getToken ();
   return result;
}

/* ---------------------------------------------------------------------- */

void TextInput::checkIdent (string s)
{
   if (symbol != IDENT || tokenTxt != s)
      // error (s + " expected");
      error (s + " expected and found " + quoteStr (tokenTxt));
   getToken ();
}

string TextInput::readIdent ()
{
   string result;
   if (symbol != IDENT)
      error ("Identifier expected");
   result = tokenTxt;
   // cout << "READ IDENT " << result << endl;
   getToken ();
   return result;
}

/* ---------------------------------------------------------------------- */

bool TextInput::readBool ()
{
   bool result = false;

   if (isIdent ("true"))
   {
      getToken ();
      result = true;
   }
   else if (isIdent ("false"))
   {
      getToken ();
      result = false;
   }
   else
   {
      error ("Boolean value expected");
   }

   return result;
}

string TextInput::readSignedNumber ()
{
   bool minus;
   string result;

   minus = false;
   if (tokenKind == separatorToken && tokenSym == '-')
   {
      minus = true;
      getToken ();
   }

   result = readNumber ();

   if (minus)
      result = '-' + result;
   return result;
}

string TextInput::readValue ()
{
   string result;

   if (isSeparator ('-') || tokenKind == numberToken)
   {
      result = readSignedNumber ();
   }
   else if (tokenKind == nameToken)
   {
      result = readIdent ();
      while (isSeparator ('.'))
      {
          getToken ();
          string id = readIdent ();
          result = result + "." + id;
      }
   }
   else if  (tokenKind == stringToken || tokenKind == charToken )
   {
      result = tokenVal;
      getToken ();
   }
   else
   {
      error ("Identifier, number, character or string expected");
   }

   return result;
}

/* ---------------------------------------------------------------------- */

signed char TextInput::readSignedChar ()
{
   signed char result = 0;
   string txt = readSignedNumber ();
   bool ok;
   long n = 0;
   StrToLong (txt, n, ok);
   if (ok && (n < SCHAR_MIN || n > SCHAR_MAX))
      ok = false;
   if (ok)
      result = n;
   if (!ok)
      error ("Integer expected");
   return result;
}

short TextInput::readShort ()
{
   short result = 0;
   string txt = readSignedNumber ();
   bool ok;
   long n = 0;
   StrToLong (txt, n, ok);
   if (ok && (n < SHRT_MIN || n > SHRT_MAX))
      ok = false;
   if (ok)
      result = n;
   if (!ok)
      error ("Integer expected");
   return result;
}

int TextInput::readInt ()
{
   int result = 0;
   string txt = readSignedNumber ();
   bool ok;
   StrToInt (txt, result, ok);
   if (!ok)
      error ("Integer expected");
   return result;
}

long TextInput::readLong ()
{
   long result = 0;
   string txt = readSignedNumber ();
   bool ok;
   StrToLong (txt, result, ok);
   if (!ok)
      error ("Long integer expected");
   return result;
}

unsigned char TextInput::readUChar ()
{
   unsigned char result = 0;
   string txt = readSignedNumber ();
   bool ok;
   unsigned int n = 0;
   StrToUInt (txt, n, ok);
   if (ok && n > UCHAR_MAX)
      ok = false;
   if (ok)
      result = n;
   if (!ok)
      error ("Integer expected");
   return result;
}

unsigned short TextInput::readUShort ()
{
   unsigned short result = 0;
   string txt = readSignedNumber ();
   bool ok;
   unsigned int n = 0;
   StrToUInt (txt, n, ok);
   if (ok && n > USHRT_MAX)
      ok = false;
   if (ok)
      result = n;
   if (!ok)
      error ("Integer expected");
   return result;
}

unsigned int TextInput::readUInt ()
{
   unsigned int result = 0;
   string txt = readSignedNumber ();
   bool ok;
   StrToUInt (txt, result, ok);
   if (!ok)
      error ("Unsigned integer expected");
   return result;
}

unsigned long TextInput::readULong ()
{
   unsigned long result = 0;
   string txt = readSignedNumber ();
   bool ok;
   StrToULong (txt, result, ok);
   if (!ok)
      error ("Unsinged long integer expected");
   return result;
}

float TextInput::readFloat ()
{
   float result = 0;
   string txt = readSignedNumber ();
   bool ok;
   double n = 0;
   StrToDouble (txt, n, ok);
   if (ok)
      result = n;
   if (!ok)
      error ("Float expected");
   return result;
}

double TextInput::readDouble ()
{
   double result = 0;
   string txt = readSignedNumber ();
   bool ok;
   StrToDouble (txt, result, ok);
   if (!ok)
      error ("Double expected");
   return result;
}

/****************************** TEXT OUTPUT *******************************/

TextOutput::TextOutput ():
   text_storage (),
   fileName (),
   showMsg (true),
   startLine (false),
   skipEmptyLine (false),
   addEmptyLine (false),
   ignoreEol (false),
   addSpace (false),
   skipSpace (false),
   indentation (0),
   linePos (0),
   colPos (0)
{
}

TextOutput::~TextOutput ()
{
   // NO store ();
}

void TextOutput::Init ()
{
   text_storage.reset (); // important for repeated open

   indentation = 0;
   startLine = true;
   skipEmptyLine = false;
   addEmptyLine = false;
   ignoreEol = false;
   skipSpace = false;
   addSpace = false;

   linePos = 1;
   colPos = 0;
}

void TextOutput::open (string name)
{
   setFileName (name);
   Init ();
}

void TextOutput::setFileName (const string p_filename)
{
    fileName = p_filename;
    fileInx = storeFileName (fileName);
}

void TextOutput::enableOutputMessages (bool value)
{
   showMsg = value;
}

/* ---------------------------------------------------------------------- */

void TextOutput::message (MessageLevel level, const string msg)
{
   global_message (level, msg, fileName, linePos, colPos);
}

/* ---------------------------------------------------------------------- */

void TextOutput::debug (const string msg)
{
   message (debugLevel, msg);
}

void TextOutput::info (const string msg)
{
   message (infoLevel, msg);
}

void TextOutput::note (const string msg)
{
   message (noteLevel, msg);
}

void TextOutput::warning (const string msg)
{
   message (warningLevel, msg);
}

void TextOutput::mistake (const string msg)
{
   message (mistakeLevel, msg);
}

void TextOutput::flaw (const string msg)
{
   message (flawLevel, msg);
}

void TextOutput::error (const string msg)
{
   message (errorLevel, msg);
}

void TextOutput::abort (const string msg)
{
   message (abortLevel, msg);
}

/* ---------------------------------------------------------------------- */

void TextOutput::setIndent (int i)
{
   indentation = i;
}

void TextOutput::indent ()
{
   indentation += 3;
}

void TextOutput::unindent ()
{
   indentation -= 3;
}

/* ---------------------------------------------------------------------- */

void TextOutput::putPlainChr (char c)
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

void TextOutput::putPlainSpaces (int n)
{
   text_storage.put_chars (' ', n);
   colPos += n;
}

void TextOutput::putPlainStr (const string s)
{
   text_storage.put_str (s);
   colPos += s.length (); // no line feed checking
}

void TextOutput::putPlainData (void * adr, size_t len)
{
   text_storage.put_data (adr, len);
   // no line and column numbers
}

void TextOutput::putPlainEol ()
{
   // putPlainChr (cr);
   putPlainChr (lf);
}

/* ---------------------------------------------------------------------- */

void TextOutput::openLine ()
{
   if (addEmptyLine && ! skipEmptyLine)
      putPlainEol ();

   addEmptyLine = false;
   skipEmptyLine = false;

   putPlainSpaces (indentation);
   startLine = false;

   addSpace = false;
   skipSpace = false;
}

void TextOutput::closeLine ()
{
   startLine = true;
}

/* ---------------------------------------------------------------------- */

void TextOutput::put (const string s)
{
   if (s != "")
   {
      if (startLine)
         openLine ();

      putPlainStr (s);
   }
}

void TextOutput::putChr (char c)
{
   if (startLine)
      openLine ();

   putPlainChr (c);
}

void TextOutput::putSpaces (int n)
{
   if (n != 0)
   {
      if (startLine)
         openLine ();

      putPlainSpaces (n);
  }
}

void TextOutput::putEol ()
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

void TextOutput::putCondEol ()
{
   // finish not empty line
   if (! startLine)
      putEol ();
}

void TextOutput::putLn (const string s)
{
   put (s);
   putEol ();
}

/* ---------------------------------------------------------------------- */

void TextOutput::emptyLine ()
{
   if (! startLine)
      putEol ();

   addEmptyLine = true;
}

void TextOutput::noEmptyLine ()
{
   skipEmptyLine = true;
}

/* ---------------------------------------------------------------------- */

void TextOutput::suspendEol ()
{
   ignoreEol = true;
}

void TextOutput::resumeEol ()
{
   ignoreEol = false;
}

/* ---------------------------------------------------------------------- */

void TextOutput::send (string s)
{
   // add optional space and print string

   char c = ' ';
   if (s.length () >= 1) c = s[0];

   if (c == ',' || c == ';' || c == ')' || c == ']' || c == '.' || s == "->") addSpace = false;

   if (addSpace && ! skipSpace && ! startLine) put (" ");
   put (s);

   addSpace = true;
   skipSpace = false;
   if (c == '(' || c == '[' || c == '.' || s == "->") addSpace = false;
}

void TextOutput::sendeol ()
{
   putEol ();
}

void TextOutput::sendln (string s)
{
   send (s);
   sendeol ();
}

/* ---------------------------------------------------------------------- */

void TextOutput::style_space ()
{
   addSpace = true;
}

void TextOutput::style_no_space ()
{
   skipSpace = true;
}

/* ---------------------------------------------------------------------- */

void TextOutput::style_new_line ()
{
   // finish line and start new one
   putCondEol ();
}

void TextOutput::style_empty_line ()
{
   // add one empty line
   emptyLine ();
}

void TextOutput::style_no_empty_line ()
{
   // ignore style_empty_line ()
   noEmptyLine ();
}

/* ---------------------------------------------------------------------- */

void TextOutput::style_indent ()
{
   style_new_line ();
   indent ();
}

void TextOutput::style_unindent ()
{
   unindent ();
   style_new_line ();
}

/* ---------------------------------------------------------------------- */

void TextOutput::putBool (bool value)
{
   if (value)
      put ("true");
   else
      put ("false");
}

void TextOutput::putChar (char value)
{
    put (quoteChr (value, quote1));
}

void TextOutput::putString (string value)
{
    put (quoteStr (value, quote2));
}

void TextOutput::putInt (int value)
{
    put (IntToStr (value));
}

void TextOutput::putLong (long value)
{
    put (LongToStr (value));
}

void TextOutput::putUInt (unsigned int value)
{
    put (ULongToStr (value));
}

void TextOutput::putULong (unsigned long value)
{
    put (ULongToStr (value));
}

void TextOutput::putFloat (float value)
{
    put (DoubleToStr (value));
}

void TextOutput::putDouble (double value)
{
    put (DoubleToStr (value));
}
/* ---------------------------------------------------------------------- */

/*
void TextOutput::putBlock (const string txt)
{
   string::size_type inx = 0;
   string::size_type len = txt.length ();

   while (inx < len)
   {
      string::size_type start = inx;

      while (inx < len && txt[inx] != cr && txt[inx] != lf)
         inx ++;

      if (inx > start)
         put (txt.substr (start, inx-start));

      if (inx < len && (txt[inx] == cr || txt[inx] == lf))
      {
         putEol ();
         if (txt[inx] == cr)
         {
            inx ++;
            if (inx < len && txt[inx] == lf) inx ++;
         }
         else
         {
            inx ++;
         }
      }
   }
}
*/

/* ---------------------------------------------------------------------- */

/*
void TextOutput::putStorage (TextStorage * storage)
{
   assert (storage != NULL);
   TextBlock * item = storage->first;
   while (item != NULL)
   {
      putPlainData (item->buf, item->len);
      item = item->next;
   }
}
*/

/* ---------------------------------------------------------------------- */

/*
void TextOutput::readFrom (const string file_name)
{
   ifstream f (file_name.c_str ());

   if (f.good ())
   {
      bool done = false;
      while (! done)
      {
         char data [TextBlock::max];
         f.read (data, sizeof (data));
         streamsize count = f.gcount ();

         if (count > 0)
            putPlainData (data, count);
         else
            done = true;
      }
   }
}
*/

/* ---------------------------------------------------------------------- */

void TextOutput::writeText ()
{
   text_storage.write (fileName);
}

/* ---------------------------------------------------------------------- */

void TextOutput::store ()
{
   bool equal = text_storage.compare (fileName);

   if (! equal)
   {
      text_storage.write (fileName);
      if (showMsg)
         info ("writing " + fileName); // simple info form inf.h
   }
   else
   {
      if (showMsg)
         info ("not modified " + fileName); // simple info form inf.h
   }
}

/* ---------------------------------------------------------------------- */

string TextOutput::toString ()
{
   return text_storage.to_string ();
}

/* vlozeni textu na pozici pos (napr. deklarace pred uz vypsany prikaz) */
void TextOutput::insertText (int pos, const string s)
{
   string tail = text_storage.cut_from (pos);
   text_storage.put_str (s);
   text_storage.put_str (tail);
}

string TextOutput::incString ()
{
   return text_storage.inc_string ();
}

/* ---------------------------------------------------------------------- */

/*
void TextOutput::retrieve_content (TextStorage & param)
{
    param.first = text_storage.first;
    param.last = text_storage.last;

    text_storage.first = NULL;
    text_storage.last = NULL;

    // text_storage.output = NULL;
    // text_storage.out_pos = 0;

    text_storage.reset ();
}

void TextOutput::append_content (TextStorage & param)
{
    if (param.first != NULL)
    {
        if (text_storage.first != NULL)
            text_storage.last->next = param.first;
        else
            text_storage.first = param.first;

        text_storage.last = param.last;

        param.first = NULL;
        param.last = NULL;
    }
}
*/

/* ---------------------------------------------------------------------- */

CLOSE_NAMESPACE
