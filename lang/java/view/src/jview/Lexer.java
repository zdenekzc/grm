
package jview;

public class Lexer
{

  /* ------------------------------------------------------------- */

  private static final char QUOTE1 = '\'';
  private static final char QUOTE2 = '"';
  private static final char BACKSLASH = '\\';
  private static final char CR = '\r';
  private static final char LF = '\n';

  protected static final int eos = 0;
  protected static final int identifier = 1;
  protected static final int number = 2;
  protected static final int real_number = 3;
  protected static final int character_literal = 4;
  protected static final int string_literal = 5;
  protected static final int separator = 6;
  protected static final int end_of_line = 7;

  protected char ch;
  public int tokenKind = eos;
  public String tokenText;
  public String tokenValue;
  
  public int getTokenFileInx () { return 0; }
  public int getTokenLine () { return 0; }
  public int getTokenCol () { return 0; }
      
  private boolean slash;
  private StringBuffer buf;

  /* ------------------------------------------------------------- */

  public Lexer () {  }
  
  public String readIdentifier () { return ""; }
  public String readNumber () { return ""; }
  public String readString () { return ""; }
  public String readChar () { return ""; }
  
  public boolean testSymbols (short [] set) { return false; }
  
  public int mark () { return 0; }
  public void rewind (int pos) { }
  
  void error (String msg)
  {
     // throw new Exception ("Compiler error: " + msg); /* !! */
  }

  /* ------------------------------------------------------------- */

  protected void nextCh ()
  {
     readChar ();

     if (ch==BACKSLASH && ch=='u')
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
           nextCh ();
        }
        else if (ch != '/')
        {
           stop = true;
        }
        else
        {
           nextCh (); // skip '/'

           if (ch == '/')
           {
              /* single line comment */
              while (ch!=CR && ch !=LF)
                 nextCh ();
           }
           else if (ch == '*')
           {
              /* comment */
              nextCh (); // skip '*'

              do
              {
                 while (ch != '*') nextCh (); // skip other characters then '*'
                 nextCh (); // skip '*'
              }
              while (ch == '/');

              nextCh (); // skip '/'
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

  /*
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
           tokenKind = ABSTRACT + c; // result
           b = a-1; // end of loop
        }
     }
  }

  /* ------------------------------------------------------------- */

  private void number ()
  {
     tokenKind = number;
     boolean hex = false;

     if (ch == '0')
     {
        nextCh (); // store zero

        if (ch=='x' || ch=='X')
        {
           /* hexadecimal */
           nextCh (); // store letter

           int cnt = 0;
           while (ch>='0' && ch<='9' || ch<='a' && ch<='f' || ch>='A' && ch<='F')
           {
              cnt ++;
              nextCh ();
           }

           if (cnt==0) error ("Hexadecimal digit expected");
           hex = true;
        }
        else
        {
           /* octal, zero or float */
           while (ch>='0' && ch<='9')
              nextCh ();
        }
     }
     else
     {
        /* decimal or float */
        while (ch>='0' && ch<='9')
           nextCh ();
     }

     /* long suffix */
     if (ch=='l' || ch=='L')
        nextCh ();

     /* optional decimal part */
     else if (!hex)
         optDecimalPart ();
  }

  private void partialDecimalNumber ()
  {
     /* decimal point already stored */
     /* current cgaracter is decimal digit */
     tokenKind = real_number;

     while (ch>='0' && ch<='9')
        nextCh ();

     optExponentPart ();
  }

  private void optDecimalPart ()
  {
     /* decimal part */
     if (ch == '.')
     {
        tokenKind = real_number;
        nextCh (); /* store decimal point */

        while (ch>='0' && ch<='9')
           nextCh ();
     }

     optExponentPart ();
  }

  private void optExponentPart ()
  {
     /* exponent */
     if (ch=='e' || ch=='E')
     {
        tokenKind = real_number;
        nextCh (); // store letter

        if (ch=='+' || ch=='-')
           nextCh ();

        if (ch<'0' || ch>'9')
           error ("Digit expected");

        while (ch>='0' && ch<='9')
           nextCh ();
     }

     /* float suffix */
     if (ch=='f' || ch =='F' || ch == 'd' || ch == 'D')
     {
        tokenKind = real_number;
        nextCh ();
     }
  }

  /* ------------------------------------------------------------- */

  private void escape ()
  {
     nextCh (); // store backslash

     if (ch>='0' && ch<='7')
     {
        int len = 0;
        int max = (ch<='3') ? 3 : 2;

        while (ch>='0' && ch<='7' && len < max)
        {
           nextCh ();
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
              nextCh ();
              break;
        }
     }
  }

  /* ------------------------------------------------------------- */

  /*
  private void select2 (int s1, char c2, int s2)
  {
     nextCh (); // skip first character

     if (ch == c2)
     {
        nextCh (); // skip second character
        tokenKind = s2;
     }
     else
     {
        tokenKind = s1;
     }
  }

  private void select3 (int s1, char c2, int s2, char c3, int s3)
  {
     nextCh (); // skip first character

     if (ch == c3)
     {
        nextCh (); // skip second character
        tokenKind = s3;
     }
     else if (ch == c2)
     {
        nextCh (); // skip second character
        tokenKind = s2;
     }
     else
     {
        tokenKind = s1;
     }
  }

  private void less ()
  {
     nextCh (); // skip '<'

     if (ch == '<')
     {
        nextCh (); // skip second '<'

        if (ch == '=')
        {
           nextCh ();
           tokenKind = SHLASSIGN; // '<<='
        }
        else
        {
           tokenKind = SHL; // '<<'
        }
     }

     else if (ch == '=')
     {
        nextCh (); // skip '='
        tokenKind = LESSEQUAL; // '<='
     }

     else tokenKind = LESS; // '<'
  }

  private void greater ()
  {
     nextCh (); // skip '>'

     if (ch == '>')
     {
        nextCh (); // skip second '>'

        if (ch == '>')
        {
           nextCh (); // skip third '>'

           if (ch == '=')
           {
              nextCh (); // skip '='
              tokenKind = SHRASSIGN; // '>>>='
           }
           else tokenKind = SHR; // '>>>'
        }

        else if (ch == '=')
        {
           nextCh (); // skip '='
           tokenKind = SARASSIGN; // '>>='
        }
        else tokenKind = SAR; // '>>'
     }

     else if (ch == '=')
     {
        nextCh (); // skip '='
        tokenKind = GREATEREQUAL; // '>='
     }

     else tokenKind = GREATER; // '>'
  }
  */

  /* ------------------------------------------------------------- */

  void nextToken ()
  {
     /* clear buffer */
     buf.setLength (0);

     /* skip white space and comments */
     space ();

     /* SLASH */
     if (slash)
     {
        // select2 (DIV, '=', DIVASSIGN);
     }

     /* IDENTIFIER */
     else if (Character.isJavaIdentifierStart (ch))
     {
        nextCh ();

        while (Character.isJavaIdentifierPart (ch))
           nextCh ();

        tokenKind = identifier;
     }

     /* NUMBER */
     else if (ch>='0' && ch<='9')
        number ();

     /* PERIOD */
     else if (ch=='.')
     {
        nextCh ();

        if (ch>='0' && ch<='9')
           partialDecimalNumber ();
        else
           tokenKind = separator;
     }

     /* STRING */
     else if (ch==QUOTE2)
     {
        nextCh (); // store quote

        while (ch != QUOTE2)
        {
           if (ch==CR || ch==LF)
              error ("String exceeds line");
           else if (ch == BACKSLASH)
              escape ();
           else
              nextCh ();
        }

        nextCh (); // store quote
        tokenKind = string_literal;
     }

     /* CHARACTER */
     else if (ch==QUOTE1)
     {
        nextCh (); // store quote

        if (ch==QUOTE1 || ch==CR || ch==LF)
           error ("Bad character constant");
        else if (ch == BACKSLASH)
           escape ();
        else
           nextCh (); // store character

        nextCh (); // store quote
        tokenKind = character_literal;
     }

     /* SPECIAL SYMBOL */
     /*
     else
     {
        switch (ch)
        {
           case '(': tokenKind=LPAR;      nextCh (); break;
           case ')': tokenKind=RPAR;      nextCh (); break;
           case '[': tokenKind=LBRACK;    nextCh (); break;
           case ']': tokenKind=RBRACK;    nextCh (); break;
           case '{': tokenKind=LBRACE;    nextCh (); break;
           case '}': tokenKind=RBRACE;    nextCh (); break;
           case ';': tokenKind=SEMICOLON; nextCh (); break;
           case ',': tokenKind=COMMA;     nextCh (); break;
           case '~': tokenKind=BITNOT;    nextCh (); break;
           case '?': tokenKind=QUESTION;  nextCh (); break;
           case ':': tokenKind=COLON;     nextCh (); break;

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
     */

     /* covert to string */
     tokenText = buf.substring (0); /* !? */

     /* keyword */
     // if (tokenKind == identifier) keyword ();
  }

}
