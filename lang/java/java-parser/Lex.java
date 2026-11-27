
package cacao.src;

public class Lex extends Const
{

  /* ------------------------------------------------------------- */

  private static final char QUOTE1 = '\'';
  private static final char QUOTE2 = '"';
  private static final char BACKSLASH = '\\';
  private static final char CR = '\r';
  private static final char LF = '\n';

  private char ch;
  private char nextCh;
  private boolean slash;
  private StringBuffer buf;

  public int sy;
  public String val;

  /* ------------------------------------------------------------- */

  public Lex ()
  {
  }

  void error (String msg)
  {
     // throw new Exception ("Compiler error: " + msg); /* !! */
  }

  void bug ()
  {
     error ("Internal error");
  }

  void checkSymbol (int par)
  {
     if (sy!=par) error ("Unexpected symbol");
     nextSymbol ();
  }

  void checkSemicolon ()
  {
     if (sy!=SEMICOLON) error ("Semicolon expected");
     nextSymbol ();
  }

  /* ------------------------------------------------------------- */

  private void readChar ()
  {
     nextCh = ch;
     /* !! read ch */
  }

  private void nextChar ()
  {
     readChar ();

     if (ch==BACKSLASH && nextCh=='u')
     {
        readChar (); // skip '\'

        while (ch == 'u')
           readChar ();

        int n = 0;
        for (int i = 1; i<4; i++)
        {
            int d = 0;
            if (ch>='0' && ch<='9')
               d = ch - '0';
            else if (ch>='A' && ch<='F')
               d = ch - 'A' + 10;
            else if (ch>='a' && ch<='f')
               d = ch - 'a' + 10;
            else
               error ("Invalid Unicode escape");
            n = n << 4 + d;
        }

        ch = (char) n;
     }
  }

  /* ------------------------------------------------------------- */

  private void space ()
  {
     slash = false;
     boolean stop = false;

     while (! stop)
     {
        /* space, horizontal tab, form feed, end of line */
        if (ch==' ' || ch=='\t' || ch=='\f' || ch==CR || ch==LF)
        {
           nextChar ();
        }
        else if (ch != '/')
        {
           stop = true;
        }
        else
        {
           nextChar (); // skip '/'

           if (ch == '/')
           {
              /* single line comment */
              while (ch!=CR && ch !=LF)
                 nextChar ();
           }
           else if (ch == '*')
           {
              /* comment */
              nextChar (); // skip '*'

              do
              {
                 while (ch != '*') nextChar (); // skip other characters then '*'
                 nextChar (); // skip '*'
              }
              while (ch == '/');

              nextChar (); // skip '/'
           }
           else
           {
              /* slash */
              slash = true;
              stop = false;
           }

        } // end of if
     } // end of while
  }

  /* ------------------------------------------------------------- */

  private void keyword ()
  {
     // keyword, null or boolean literal

     val = buf.toString();

     int a = 0;
     int b = keywords.length-1;

     while (a <= b)
     {
        int c = (a+b)/2;
        int cmp = val.compareTo (keywords[c]);
        if (cmp < 0)
           b = c-1;
        else if (cmp > 0)
           a = c+1;
        else
        {
           sy = ABSTRACT + c; // result
           b = a-1; // end of loop
        }
     }
  }

  /* ------------------------------------------------------------- */

  private void number ()
  {
     sy = NUMBER;
     boolean hex = false;

     if (ch == '0')
     {
        nextChar (); // store zero

        if (ch=='x' || ch=='X')
        {
           /* hexadecimal */
           nextChar (); // store letter

           int cnt = 0;
           while (ch>='0' && ch<='9' || ch<='a' && ch<='f' || ch>='A' && ch<='F')
           {
              cnt ++;
              nextChar ();
           }

           if (cnt==0) error ("Hexadecimal digit expected");
           hex = true;
        }
        else
        {
           /* octal, zero or float */
           while (ch>='0' && ch<='9')
              nextChar ();
        }
     }
     else
     {
        /* decimal or float */
        while (ch>='0' && ch<='9')
           nextChar ();
     }

     /* long suffix */
     if (ch=='l' || ch=='L')
        nextChar ();

     /* optional decimal part */
     else if (!hex)
         optDecimalPart ();
  }

  private void partialDecimalNumber ()
  {
     /* decimal point already stored */
     /* current cgaracter is decimal digit */
     sy = FLT;

     while (ch>='0' && ch<='9')
        nextChar ();

     optExponentPart ();
  }

  private void optDecimalPart ()
  {
     /* decimal part */
     if (ch == '.')
     {
        sy = FLT;
        nextChar (); /* store decimal point */

        while (ch>='0' && ch<='9')
           nextChar ();
     }

     optExponentPart ();
  }

  private void optExponentPart ()
  {
     /* exponent */
     if (ch=='e' || ch=='E')
     {
        sy = FLT;
        nextChar (); // store letter

        if (ch=='+' || ch=='-')
           nextChar ();

        if (ch<'0' || ch>'9')
           error ("Digit expected");

        while (ch>='0' && ch<='9')
           nextChar ();
     }

     /* float suffix */
     if (ch=='f' || ch =='F' || ch == 'd' || ch == 'D')
     {
        sy = FLT;
        nextChar ();
     }
  }

  /* ------------------------------------------------------------- */

  private void escape ()
  {
     nextChar (); // store backslash

     if (ch>='0' && ch<='7')
     {
        int len = 0;
        int max = (ch<='3') ? 3 : 2;

        while (ch>='0' && ch<='7' && len < max)
        {
           nextChar ();
           len ++;
        }
     }
     else
     {
        switch (ch)
        {
           case 'b':
           case 't':
           case 'n':
           case 'f':
           case 'r':
           case QUOTE1:
           case QUOTE2:
           case BACKSLASH:
              nextChar ();
              break;
        }
     }
  }

  /* ------------------------------------------------------------- */

  private void select2 (int s1, char c2, int s2)
  {
     nextChar (); // skip first character

     if (ch == c2)
     {
        nextChar (); // skip second character
        sy = s2;
     }
     else
     {
        sy = s1;
     }
  }

  private void select3 (int s1, char c2, int s2, char c3, int s3)
  {
     nextChar (); // skip first character

     if (ch == c3)
     {
        nextChar (); // skip second character
        sy = s3;
     }
     else if (ch == c2)
     {
        nextChar (); // skip second character
        sy = s2;
     }
     else
     {
        sy = s1;
     }
  }

  private void less ()
  {
     nextChar (); // skip '<'

     if (ch == '<')
     {
        nextChar (); // skip second '<'

        if (ch == '=')
        {
           nextChar ();
           sy = SHLASSIGN; // '<<='
        }
        else
        {
           sy = SHL; // '<<'
        }
     }

     else if (ch == '=')
     {
        nextChar (); // skip '='
        sy = LESSEQUAL; // '<='
     }

     else sy = LESS; // '<'
  }

  private void greater ()
  {
     nextChar (); // skip '>'

     if (ch == '>')
     {
        nextChar (); // skip second '>'

        if (ch == '>')
        {
           nextChar (); // skip third '>'

           if (ch == '=')
           {
              nextChar (); // skip '='
              sy = SHRASSIGN; // '>>>='
           }
           else sy = SHR; // '>>>'
        }

        else if (ch == '=')
        {
           nextChar (); // skip '='
           sy = SARASSIGN; // '>>='
        }
        else sy = SAR; // '>>'
     }

     else if (ch == '=')
     {
        nextChar (); // skip '='
        sy = GREATEREQUAL; // '>='
     }

     else sy = GREATER; // '>'
  }

  /* ------------------------------------------------------------- */

  void nextSymbol ()
  {
     /* clear buffer */
     buf.setLength (0);

     /* skip white space and comments */
     space ();

     /* SLASH */
     if (slash)
     {
        select2 (DIV, '=', DIVASSIGN);
     }

     /* IDENTIFIER */
     else if (Character.isJavaIdentifierStart (ch))
     {
        nextChar ();

        while (Character.isJavaIdentifierPart (ch))
           nextChar ();

        sy = IDENT;
     }

     /* NUMBER */
     else if (ch>='0' && ch<='9')
        number ();

     /* PERIOD */
     else if (ch=='.')
     {
        nextChar ();

        if (ch>='0' && ch<='9')
           partialDecimalNumber ();
        else
           sy = PERIOD;
     }

     /* STRING */
     else if (ch==QUOTE2)
     {
        nextChar (); // store quote

        while (ch != QUOTE2)
        {
           if (ch==CR || ch==LF)
              error ("String exceeds line");
           else if (ch == BACKSLASH)
              escape ();
           else
              nextChar ();
        }

        nextChar (); // store quote
        sy=STR;
     }

     /* CHARACTER */
     else if (ch==QUOTE1)
     {
        nextChar (); // store quote

        if (ch==QUOTE1 || ch==CR || ch==LF)
           error ("Bad character constant");
        else if (ch == BACKSLASH)
           escape ();
        else
           nextChar (); // store character

        nextChar (); // store quote
        sy=CHR;
     }

     /* SPECIAL SYMBOL */
     else
     {
        switch (ch)
        {
           case '(': sy=LPAR;      nextChar (); break;
           case ')': sy=RPAR;      nextChar (); break;
           case '[': sy=LBRACK;    nextChar (); break;
           case ']': sy=RBRACK;    nextChar (); break;
           case '{': sy=LBRACE;    nextChar (); break;
           case '}': sy=RBRACE;    nextChar (); break;
           case ';': sy=SEMICOLON; nextChar (); break;
           case ',': sy=COMMA;     nextChar (); break;
           case '~': sy=BITNOT;    nextChar (); break;
           case '?': sy=QUESTION;  nextChar (); break;
           case ':': sy=COLON;     nextChar (); break;

           case '<': less ();    break;
           case '>': greater (); break;

           case '+': select3 (PLUS,  '=', ADDASSIGN,  '+', DPLUS);  break;
           case '-': select3 (MINUS, '=', SUBASSIGN,  '-', DMINUS); break;
           case '*': select2 (MUL,   '=', MULASSIGN);               break;
           case '%': select2 (MOD,   '=', MODASSIGN);               break;
           case '&': select3 (AND,   '=', ANDASSIGN,  '&', LOGAND); break;
           case '|': select3 (OR,    '=', ORASSIGN,   '|', LOGOR);  break;
           case '^': select2 (XOR,   '=', XORASSIGN);               break;

           case '=': select2 (ASSIGN, '=', EQUAL); break;
           case '!': select2 (LOGNOT, '=', NOTEQUAL); break;

           default:  error ("Unknown symbol"); break;
        }
     }

     /* covert to string */
     val = buf.substring (0); /* !? */

     /* keyword */
     if (sy == IDENT) keyword ();
  }

}

