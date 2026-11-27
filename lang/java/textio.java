/* textio.java - Java port of the textio lexer API (the same contract as
   lang/vala/textio.vala and lang/csharp/textio.cs).

   The generated Java parsers (grm/cparser.py --java) subclass Lexer.
   All classes are in the same Java package as the generated parser
   (see ParserIn in tests/test_parser_in.py).

   Token fields:
     tokenKind  nameToken, numberToken, realToken, charToken,
                stringToken, separatorToken, eofToken
     tokenTxt   original token text — string/char literals WITH quotes
                and raw escape sequences
     tokenVal   literal value — without quotes, escapes decoded
     tokenSym   the separator character

   mark () / rewind (pos) snapshot the full scanner state, so the
   generated predicates (test_N) can backtrack over already read tokens.
*/

package parserin;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;

class Lexer
{
   private String source = "";   // source code
   private int sourceLen = 0;

   private int fileInx = 0;   // file index
   private int lineNum = 1;  // line number (from 1)
   private int colNum = 1;   // column number (from 1)
   private int byteOfs = 0;  // byte offset (from 0)

   protected char inpCh;     // current input character
   private boolean slash = false;

   public static final int eofToken = 0;
   public static final int nameToken = 1;
   public static final int numberToken = 2;
   public static final int realToken = 3;
   public static final int charToken = 4;
   public static final int stringToken = 5;
   public static final int separatorToken = 6;

   public int tokenKind = eofToken;
   public String tokenTxt = "";  // original token text
   public String tokenVal = "";  // literal value
   public char tokenSym;         // separator character

   public int tokenLine;         // token start line
   public int tokenCol;          // token start column

   /* scanner position at the start of the current token — mark () /
      rewind () replay the token from here, so nextToken () re-runs
      translate () and the parser's token is re-derived */

   private int prevOfs = 0;
   private int prevLine = 1;
   private int prevCol = 1;
   private char prevCh = 0;

   private static final char NUL = 0;
   private static final char CR = '\r';
   private static final char LF = '\n';
   private static final char QUOTE1 = '\'';
   private static final char QUOTE2 = '\"';
   private static final char BACKSLASH = '\\';

   /* state snapshots for mark () / rewind () */

   private static class State
   {
      int ofs;
      int line;
      int col;
      char ch;
   }

   private ArrayList<State> marks = new ArrayList<State> ();

   public Lexer ()
   {
   }

   /* --- input --------------------------------------------------------- */

   public void openString (String text)
   {
      source = text;
      sourceLen = text.length ();
      fileInx = 0;
      lineNum = 1;
      colNum = 1;
      byteOfs = 0;
      inpCh = NUL;
      marks.clear ();
      nextCh ();
   }

   public void openFile (String path)
   {
      try
      {
         openString (Files.readString (Path.of (path)));
      }
      catch (IOException e)
      {
         error ("Cannot open file: " + path);
      }
   }

   /* --- error --------------------------------------------------------- */

   public void error (String msg)
   {
      throw new RuntimeException (tokenLine + ":" + tokenCol + ": error: " + msg);
   }

   /* --- token position ------------------------------------------------- */

   public int getTokenFileInx () { return fileInx; }
   public int getTokenLine ()    { return tokenLine; }
   public int getTokenCol ()     { return tokenCol; }

   /* --- mark / rewind --------------------------------------------------- */

   public int mark ()
   {
      State s = new State ();
      s.ofs = prevOfs;
      s.line = prevLine;
      s.col = prevCol;
      s.ch = prevCh;
      marks.add (s);
      return marks.size () - 1;
   }

   public void rewind (int pos)
   {
      State s = marks.get (pos);
      byteOfs = s.ofs;
      lineNum = s.line;
      colNum = s.col;
      inpCh = s.ch;

      /* re-lex the token: the full nextToken () pipeline runs again,
         including the virtual translate (), so the grammar symbol
         (token in the generated parser) is re-derived instead of
         staying stale after a failed trial parse */

      nextToken ();
   }

   /* --- basic character input ------------------------------------------- */

   protected void nextCh ()
   {
      if (byteOfs < sourceLen)
      {
         inpCh = source.charAt (byteOfs);
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
      tokenTxt = tokenTxt + c;
   }

   private void putVal (char c)
   {
      tokenVal = tokenVal + c;
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
         case '0': putVal ((char) 0); break;
         case 'b': putVal ('\b'); break;
         case 'f': putVal ('\f'); break;
         case 'n': putVal ('\n'); break;
         case 'r': putVal ('\r'); break;
         case 't': putVal ('\t'); break;
         case 'v': putVal ((char) 0x0B); break;
         default:  putVal (e);    break; // quotes, backslash, unknown
      }
      nextCh ();
   }

   /* --- white space and comments ---------------------------------------- */

   private void space ()
   {
      slash = false;
      boolean stop = false;

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

               boolean closed = false;
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
      boolean hex = false;

      if (inpCh == '0')
      {
         storeChar (); // store zero

         if (inpCh == 'x' || inpCh == 'X')
         {
            /* hexadecimal */
            storeChar (); // store letter

            int cnt = 0;
            while (Character.digit (inpCh, 16) >= 0)
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

   public void translate ()
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
      else if (Character.isLetter (inpCh) || inpCh == '_')
      {
         /* identifier or keyword */
         while (Character.isLetterOrDigit (inpCh) || inpCh == '_')
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

   public String readIdent (String msg)
   {
      String result;
      if (tokenKind != nameToken)
         error (msg);
      result = tokenTxt;
      nextToken ();
      return result;
   }

   public String readIdent ()
   {
      return readIdent ("Identifier expected");
   }

   public String readNumber ()
   {
      String result;
      if (tokenKind != numberToken)
         error ("Number expected");
      result = tokenTxt;
      nextToken ();
      return result;
   }

   public String readReal ()
   {
      String result;
      if (tokenKind != realToken)
         error ("Real number expected");
      result = tokenTxt;
      nextToken ();
      return result;
   }

   public String readString ()
   {
      String result;
      if (tokenKind != stringToken)
         error ("String expected");
      result = tokenVal; // without quotes
      nextToken ();
      return result;
   }

   public String readCharAsString ()
   {
      String result;
      if (tokenKind != charToken)
         error ("Character constant expected");
      result = tokenVal; // without quotes
      nextToken ();
      return result;
   }

   public String readQuotedString ()
   {
      String result;
      if (tokenKind != stringToken)
         error ("String expected");
      result = tokenTxt; // with quotes
      nextToken ();
      return result;
   }

   public String readQuotedCharAsString ()
   {
      String result;
      if (tokenKind != charToken)
         error ("Character constant expected");
      result = tokenTxt; // with quotes
      nextToken ();
      return result;
   }
}

/* ---------------------------------------------------------------------- */

class Output
{
   private StringBuilder buffer = new StringBuilder ();

   public Output ()
   {
   }

   public String toString ()
   {
      return buffer.toString ();
   }

   public void clear ()
   {
      buffer.setLength (0);
   }

   public void error (String msg)
   {
      throw new RuntimeException (msg);
   }

   public void send (String s)
   {
      buffer.append (s);
   }

   public void putChar (char c)
   {
      buffer.append (c);
   }

   public void putChar (String s)
   {
      buffer.append (s);
   }

   public void putString (String s)
   {
      buffer.append (s);
   }

   public void style_indent ()      { }
   public void style_unindent ()    { }
   public void style_no_space ()    { }
   public void style_new_line ()    { }
   public void style_empty_line ()  { }
}
