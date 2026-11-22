/* textio.vala — Vala port of the textio lexer API (gibbon/src/utils/textio.*).

   The generated Vala parsers (grm/cparser.py --vala) subclass Lexer:

       var p = new Parser ();        // Parser : Lexer
       p.openString (source);
       p.nextToken ();               // lexical scan + translate ()
       var tree = p.parse_program (); // <start rule>

   Token fields (the same meaning as in the C++ textio):
     tokenKind  TokenKind enum value (nameToken, numberToken, realToken,
                charToken, stringToken, separatorToken, eofToken, ...)
     tokenTxt   original token text — string/char literals WITH quotes
                and raw escape sequences
     tokenVal   literal value — without quotes, escapes decoded
     tokenSym   the separator character
     inpCh      the current input character (lookahead for long separators)

   Literals (the same contract as the C++ textio):
     readIdent ()                tokenTxt, advanced (nameToken)
     readNumber () / readReal () tokenTxt, advanced
     readQuotedCharAsString ()   tokenTxt with quotes, advanced
     readQuotedString ()         tokenTxt with quotes, advanced

   mark () / rewind (pos) snapshot the full scanner state, so the
   generated predicates (test_N) can backtrack over already read tokens.
*/

public enum TokenKind
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

   unusedDirectiveToken,    // section skipped by preprocessor
   includeDirectiveToken,   // include directive
   processedDirectiveToken, // already processed directive

   stopToken,      // formal last token
   finalToken,     // end of macro expansion
   eofToken        // end of file
}

public errordomain LexerError
{
   LEXER_ERROR
}

/* ---------------------------------------------------------------------- */

public class Lexer
{
   private string source = "";   // source code
   private int sourceLen = 0;

   private int fileInx = 0;   // file index
   private int lineNum = 1;  // line number (from 1)
   private int colNum = 1;   // column number (from 1)
   private int byteOfs = 0;  // byte offset (from 0)

   protected char inpCh;     // current input character
   private bool slash = false;

   public TokenKind tokenKind;
   public string tokenTxt = "";  // original token text
   public string tokenVal = "";  // literal value
   public char tokenSym;         // separator character

   public int tokenLine;         // token start line
   public int tokenCol;           // token start column

   /* scanner position at the start of the current token — mark () /
      rewind () replay the token from here, so nextToken () re-runs
      translate () and the parser's `token' is re-derived, not restored
      from a stale value (the same trick as prev* in the Python lexer
      and the InputItem queue in the C++ textio) */

   private int prevOfs = 0;
   private int prevLine = 1;
   private int prevCol = 1;
   private char prevCh = '\0';

   private const char NUL = '\0';
   private const char CR = '\r';
   private const char LF = '\n';
   private const char QUOTE1 = '\'';
   private const char QUOTE2 = '\"';
   private const char BACKSLASH = '\\';

   /* state snapshots for mark () / rewind () */

   private class State
   {
      public int ofs;
      public int line;
      public int col;
      public char ch;
   }

   private State [] marks = new State [0];

   public Lexer ()
   {
   }

   /* --- input --------------------------------------------------------- */

   public void openString (string text)
   {
      source = text;
      sourceLen = text.length;
      fileInx = 0;
      lineNum = 1;
      colNum = 1;
      byteOfs = 0;
      nextCh ();
   }

   public void openFile (string path)
   {
      try
      {
         string content;
         GLib.FileUtils.get_contents (path, out content);
         openString (content);
      }
      catch (Error e)
      {
         error ("Cannot open file: " + path);
      }
   }

   /* --- error --------------------------------------------------------- */

   public void error (string msg)
   {
      throw new LexerError.LEXER_ERROR ("%d:%d: error: %s".printf (tokenLine, tokenCol, msg));
   }

   /* --- token position ------------------------------------------------- */

   public int getTokenFileInx () { return fileInx; }
   public int getTokenLine ()    { return tokenLine; }
   public int getTokenCol ()    { return tokenCol; }

   /* --- mark / rewind --------------------------------------------------- */

   public int mark ()
   {
      State s = new State ();
      s.ofs = prevOfs;
      s.line = prevLine;
      s.col = prevCol;
      s.ch = prevCh;
      marks += s;
      return marks.length - 1;
   }

   public void rewind (int pos)
   {
      State s = marks [pos];
      byteOfs = s.ofs;
      lineNum = s.line;
      colNum = s.col;
      inpCh = s.ch;

      /* re-lex the token: the full nextToken () pipeline runs again,
         including the virtual translate (), so the grammar symbol
         (`token' in the generated parser) is re-derived instead of
         staying stale after a failed trial parse */

      nextToken ();
   }

   /* --- basic character input ------------------------------------------- */

   protected void nextCh ()
   {
      if (byteOfs < sourceLen)
      {
         inpCh = source [byteOfs];
         byteOfs++;

         if (inpCh == LF)
         {
            lineNum++;
            colNum = 0;
         }
         else if (inpCh != CR)
         {
            colNum++;
         }
      }
      else
      {
         inpCh = NUL;
      }
   }

   private void putTxt (char c)
   {
      tokenTxt = tokenTxt + c.to_string ();
   }

   private void putVal (char c)
   {
      tokenVal = tokenVal + c.to_string ();
   }

   private void storeChar ()
   {
      putTxt (inpCh);
      putVal (inpCh);
      nextCh ();
   }

   /* raw escape sequence into tokenTxt (backslash + char),
      decoded value into tokenVal */

   private void storeEscape ()
   {
      putTxt (BACKSLASH);
      nextCh (); // skip backslash, inpCh = escape character

      char e = inpCh;
      putTxt (e);
      switch (e)
      {
         case '0': putVal ('\0'); break;
         case 'b': putVal ('\b'); break;
         case 'f': putVal ('\f'); break;
         case 'n': putVal ('\n'); break;
         case 'r': putVal ('\r'); break;
         case 't': putVal ('\t'); break;
         case 'v': putVal ('\v'); break;
         default:  putVal (e);    break; // quotes, backslash, unknown
      }
      nextCh ();
   }

   /* --- white space and comments ---------------------------------------- */

   private void space ()
   {
      slash = false;
      bool stop = false;

      while (!stop)
      {
         /* space, horizontal tab, form feed, end of line */
         if (inpCh == ' ' || inpCh == '\t' || inpCh == '\f' || inpCh == CR || inpCh == LF)
         {
            nextCh ();
         }
         else if (inpCh != '/')
         {
            stop = true;
         }
         else
         {
            nextCh (); // skip '/'

            if (inpCh == '/')
            {
               /* single line comment */
               while (inpCh != CR && inpCh != LF && inpCh != NUL)
               {
                  nextCh ();
               }
            }
            else if (inpCh == '*')
            {
               /* multi line comment */
               nextCh (); // skip '*'

               bool closed = false;
               while (!closed)
               {
                  if (inpCh == NUL)
                     error ("Unterminated comment");
                  else if (inpCh == '*')
                  {
                     nextCh (); // skip '*'
                     if (inpCh == '/')
                     {
                        nextCh (); // skip '/'
                        closed = true;
                     }
                  }
                  else
                     nextCh ();
               }
            }
            else
            {
               /* slash as separator */
               slash = true;
               stop = true;
            }
         }
      }
   }

   /* --- numbers ----------------------------------------------------------- */

   private void numeric ()
   {
      tokenKind = numberToken;
      bool hex = false;

      if (inpCh == '0')
      {
         storeChar (); // store zero

         if (inpCh == 'x' || inpCh == 'X')
         {
            /* hexadecimal */
            storeChar (); // store letter

            int cnt = 0;
            while (inpCh.isxdigit ())
            {
               cnt++;
               storeChar ();
            }

            if (cnt == 0)
               error ("Hexadecimal digit expected");
            hex = true;
         }
         else
         {
            /* octal, zero or float */
            while (inpCh >= '0' && inpCh <= '9')
               storeChar ();
         }
      }
      else
      {
         /* decimal or float */
         while (inpCh >= '0' && inpCh <= '9')
            storeChar ();
      }

      /* long suffix */
      if (inpCh == 'l' || inpCh == 'L')
         storeChar ();
      /* optional decimal part */
      else if (!hex)
         optDecimalPart ();
   }

   private void optDecimalPart ()
   {
      /* decimal part */
      if (inpCh == '.')
      {
         tokenKind = realToken;
         storeChar (); /* store decimal point */

         while (inpCh >= '0' && inpCh <= '9')
            storeChar ();
      }

      optExponentPart ();
   }

   private void optExponentPart ()
   {
      /* exponent */
      if (inpCh == 'e' || inpCh == 'E')
      {
         tokenKind = realToken;
         storeChar (); // store letter

         if (inpCh == '+' || inpCh == '-')
            storeChar ();

         if (inpCh < '0' || inpCh > '9')
            error ("Digit expected");

         while (inpCh >= '0' && inpCh <= '9')
            storeChar ();
      }

      /* float suffix */
      if (inpCh == 'f' || inpCh == 'F' || inpCh == 'd' || inpCh == 'D')
      {
         tokenKind = realToken;
         storeChar ();
      }
   }

   /* --- the main scanner --------------------------------------------------- */

   public virtual void translate ()
   {
      // translated by the generated parser (tokenKind -> grammar symbol)
   }

   public void nextToken ()
   {
      tokenTxt = "";
      tokenVal = "";
      tokenKind = eofToken;

      /* skip white space and comments */
      space ();

      /* remember the scanner position at the token start (for rewind) */
      prevOfs = byteOfs;
      prevLine = lineNum;
      prevCol = colNum;
      prevCh = inpCh;

      tokenLine = lineNum;
      tokenCol = colNum;

      if (slash)
      {
         /* slash as separator */
         tokenKind = separatorToken;
         tokenSym = '/';
         tokenTxt = "/";
         tokenVal = "/";
      }
      else if (inpCh == NUL)
      {
         /* end of file */
         tokenKind = eofToken;
      }
      else if (inpCh.isalpha () || inpCh == '_')
      {
         /* identifier or keyword */
         while (inpCh.isalnum () || inpCh == '_')
            storeChar ();
         tokenKind = nameToken;
      }
      else if (inpCh >= '0' && inpCh <= '9')
      {
         /* number */
         numeric ();
      }
      else if (inpCh == QUOTE2)
      {
         /* string literal — tokenTxt with quotes, tokenVal decoded */
         putTxt (QUOTE2);
         nextCh (); // skip opening quote

         while (inpCh != QUOTE2)
         {
            if (inpCh == CR || inpCh == LF)
               error ("String exceeds line");
            else if (inpCh == NUL)
               error ("Unexpected end of file in string");
            else if (inpCh == BACKSLASH)
               storeEscape ();
            else
               storeChar ();
         }

         nextCh (); // skip closing quote
         putTxt (QUOTE2);
         tokenKind = stringToken;
      }
      else if (inpCh == QUOTE1)
      {
         /* character literal — tokenTxt with quotes, tokenVal decoded */
         putTxt (QUOTE1);
         nextCh (); // skip opening quote

         if (inpCh == QUOTE1 || inpCh == CR || inpCh == LF || inpCh == NUL)
            error ("Bad character constant");
         else if (inpCh == BACKSLASH)
            storeEscape ();
         else
            storeChar (); // store character

         if (inpCh != QUOTE1)
            error ("Unterminated character constant");
         nextCh (); // skip closing quote
         putTxt (QUOTE1);
         tokenKind = charToken;
      }
      else
      {
         /* single character separator */
         tokenKind = separatorToken;
         tokenSym = inpCh;
         storeChar ();
      }

      translate ();
   }

   /* --- literal reading (the textio contract) ------------------------------ */

   public string readIdent (string msg = "Identifier expected")
   {
      string result;
      if (tokenKind != nameToken)
         error (msg);
      result = tokenTxt;
      nextToken ();
      return result;
   }

   public string readNumber ()
   {
      string result;
      if (tokenKind != numberToken)
         error ("Number expected");
      result = tokenTxt;
      nextToken ();
      return result;
   }

   public string readReal ()
   {
      string result;
      if (tokenKind != realToken)
         error ("Real number expected");
      result = tokenTxt;
      nextToken ();
      return result;
   }

   public string readString ()
   {
      string result;
      if (tokenKind != stringToken)
         error ("String expected");
      result = tokenVal; // without quotes
      nextToken ();
      return result;
   }

   public string readCharAsString ()
   {
      string result;
      if (tokenKind != charToken)
         error ("Character constant expected");
      result = tokenVal; // without quotes
      nextToken ();
      return result;
   }

   public string readQuotedString ()
   {
      string result;
      if (tokenKind != stringToken)
         error ("String expected");
      result = tokenTxt; // with quotes
      nextToken ();
      return result;
   }

   public string readQuotedCharAsString ()
   {
      string result;
      if (tokenKind != charToken)
         error ("Character constant expected");
      result = tokenTxt; // with quotes
      nextToken ();
      return result;
   }
}

/* ---------------------------------------------------------------------- */

public class Output
{
   private GLib.StringBuilder buffer = new GLib.StringBuilder ();

   public Output ()
   {
   }

   public string toString ()
   {
      return buffer.str;
   }

   public void clear ()
   {
      buffer.truncate (0);
   }

   public void error (string msg)
   {
      throw new LexerError.LEXER_ERROR (msg);
   }

   public void send (string s)
   {
      buffer.append (s);
   }

   public void putChar (string s)
   {
      buffer.append (s);
   }

   public void putString (string s)
   {
      buffer.append (s);
   }

   public void style_indent ()      { }
   public void style_unindent ()    { }
   public void style_no_space ()    { }
   public void style_new_line ()    { }
   public void style_empty_line ()  { }
}

/* ---------------------------------------------------------------------- */

// kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
