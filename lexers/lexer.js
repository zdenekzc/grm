class Lexer
{
    constructor (source)
    {
       this.source = source;
       this.sourceLen = this.source.length;
       this.file_name = "";
       this.reset ();
       this.nextChar ();
       this.nextToken ();
    }

    reset ()
    {
       this.eos = 0;
       this.identifier = 1;
       this.number = 2;
       this.real_number = 3;
       this.character_literal = 4;
       this.string_literal = 5;
       this.separator = 6;
       this.end_of_line = 7;

       this.charFileInx = 0;
       this.charLineNum = 1;
       this.charColNum = 1;
       this.charByteOfs = 0; // character offset (from 0)

       this.tokenFileInx = 0;
       this.tokenLineNum = 1;
       this.tokenColNum = 1;
       this.tokenByteOfs = 0; // token (in this.token)

       this.prevFileInx = 0;
       this.prevLineNum = 1;
       this.prevColNum = 1;
       this.prevByteOfs = 0; // previous token
       this.prevEndOfs = 0;

       this.ch = '\0';
       this.token = this.eos;
       this.tokenText = "";
       this.tokenValue = "";
   }

   /* ------------------------------------------------------------------- */

   getFileName ()
   {
       return this.file_name;
   }

   setFileName (name)
   {
       this.file_name = name;
   }

   /* ------------------------------------------------------------------- */

   getPosition ()
   {
       return this.getFileName () + ":" + this.tokenLineNum + ":" + this.tokenColNum;
   }

   info (text)
   {
       print (this.getPosition () + ": info: " + text);
   }

   warning (text)
   {
       print (this.getPosition () + ": warning: " + text);
   }

   error (text)
   {
       // raise LexerException (this.getPosition () + ": error: " + text + ", tokenText=" + this.tokenText);
   }

   /* ------------------------------------------------------------------- */

   nextChar ()
   {
       if (this.charByteOfs < this.sourceLen)
       {
          this.ch = this.source [this.charByteOfs];
          this.charByteOfs = this.charByteOfs + 1;
          if (this.ch == '\n')
          {
             this.charLineNum = this.charLineNum + 1;
             this.charColNum = 1;
          }
          else if (this.ch != '\r')
          {
             this.charColNum = this.charColNum + 1;
          }
       }
       else
       {
          this.ch = '\0';
       }
       // print ("nextChar: " + this.ch);
       // console.log (this);
   } // end of nextChar

   /* ------------------------------------------------------------------- */

   isLetter (c)
   {
       return c >= 'A' && c <= 'Z' || c >= 'a' && c <= 'z' || c == '_';
   }

   isDigit (c)
   {
       return c >= '0' && c <= '9';
   }

   isOctDigit (c)
   {
       return c >= '0' && c <= '7';
   }

   isHexDigit (c)
   {
       return c >= 'A' && c <= 'F' || c >= 'a' && c <= 'f' || c >= '0' && c <= '9';
   }

   isLetterOrDigit (c)
   {
       return this.isLetter (c) || this.isDigit (c);
   }

   /* ------------------------------------------------------------------- */

   comment_eol ()
   {
       var txt = "";
       while (this.ch != '\0' && this.ch != '\r' && this.ch != '\n')
       {
          txt += this.ch;
          this.nextChar ();
       }
   }

   comment (mark1)
   {
       var txt = "";
       while (this.ch != '\0' && this.ch != mark1)
       {
          txt += this.ch;
          this.nextChar ();
       }
       if (this.ch == mark1)
       {
          this.nextChar () // skip mark1
       }
       else
       {
          this.error ("Unterminated comment");
       }
   }

   comment2 (mark1, mark2)
   {
       var txt = "";
       var prev = ' ';
       while (this.ch != '\0' && ! (prev == mark1 && this.ch == mark2))
       {
          txt += this.ch;
          prev = this.ch;
          this.nextChar ();
       }
       if (this.ch == mark2)
       {
          this.nextChar (); //skip mark2
       }
       else
       {
          this.error ("Unterminated comment");
       }
   }

   /* ------------------------------------------------------------------- */

   checkDigit ()
   {
       if (! this.isDigit (this.ch))
       {
          this.error ("Digit expected");
       }
   }

   digits ()
   {
       while (this.isDigit (this.ch))
       {
          this.tokenText = this.tokenText + this.ch;
          this.nextChar ();
       }
   }

   stringChar ()
   {
       if (this.ch != '\\')
       {
          var c = this.ch;
          this.nextChar ();
          return c;
       }
       else
       {
          this.nextChar (); // skip backslash

          if (this.ch >= '0' && this.ch <= '7')
          {
             var cnt = 1;
             var c = 0
             while (this.ch >= '0' && this.ch <= '7' && cnt <= 3)
             {
                c = 8 * c  + ord (this.ch) - ord ('0');
                cnt = cnt + 1;
                this.nextChar ();
             }
             return chr (c);
          }
          else if (this.ch == 'x' || this.ch == 'X')
          {
             this.nextChar ();
             var c = 0;
             var cnt = 1;
             while (this.ch >= '0' && this.ch <= '9' || this.ch >= 'A' && this.ch <= 'Z' || this.ch >= 'a' && this.ch <= 'z' && cnt <= 2)
             {
                if( this.ch >= '0' && this.ch <= '9')
                {
                   n = ord (this.ch) - ord ('0');
                }
                else if (this.ch >= 'A' && this.ch <= 'Z')
                {
                   n = ord (this.ch) - ord ('A') + 10;
                }
                else
                {
                   n = ord (this.ch) - ord ('a') + 10;
                }
                c = 16 * c  + n;
                cnt = cnt + 1;
                this.nextChar ();
             }
             return chr (c % 255)
          }
          else if (this.ch == 'a')
             c = '\a';
          else if (this.ch == 'b')
             c =  '\b';
          else if (this.ch == 'f')
             c =  '\f';
          else if (this.ch == 'n')
             c =  '\n';
          else if (this.ch == 'r')
             c =  '\r';
          else if (this.ch == 't')
             c =  '\t';
          else if (this.ch == 'v')
             c =  '\v';
          else if (this.ch == "'" || this.ch == '"' || this.ch == '?')
             c = this.ch;
          else
             c = this.ch; // same

          this.nextChar ();
          return c;
       }
   }

   /* ------------------------------------------------------------------- */

   lookupKeyword ()
   {
   }

   processSeparator ()
   {
   }

   backStep ()
   {
       this.tokenColNum = this.tokenColNum - 1;
       this.tokenByteOfs = this.tokenByteOfs - 1;
   }

   /* ------------------------------------------------------------------- */

   numericToken ()
   {
       this.token = this.number;
       var cont = true;
       if (this.ch == '0')
       {
          this.tokenText = this.tokenText + this.ch;
          this.nextChar ();
          if (this.ch == 'x')
          {
             this.tokenText = this.tokenText + this.ch;
             this.nextChar ();
             while (this.isHexDigit (this.ch))
             {
                this.tokenText = this.tokenText + this.ch;
                this.nextChar ();
             }
             cont = false
          }
          else
          {
             if (this.isOctDigit (this.ch))
             {
                cont = False
             }
             while (this.isOctDigit (this.ch))
             {
                this.tokenText = this.tokenText + this.ch;
                this.nextChar ();
             }
          }
       }
       if (cont)
       {
          this.digits ();
          if (this.ch == '.')
          {
             this.decimalToken ();
          }
          this.exponentToken ()
       }
       this.numericSuffix ();
   }

   decimalToken ()
   {
       this.token = this.real_number;
       this.tokenText = this.tokenText + this.ch; // store '.'
       this.nextChar (); // skip '.'
       // NO this.checkDigit ()
       this.digits ();
   }

   exponentToken ()
   {
       if (this.ch == 'e' || this.ch == 'E')
       {
          this.token = this.real_number;
          this.tokenText = this.tokenText + this.ch; // store 'e'
          this.nextChar (); // skip 'e'
          if (this.ch == '+' || this.ch == '-')
          {
             this.tokenText = this.tokenText + this.ch; // store '+' || '-'
             this.nextChar (); // skip '+' || '-'
          }
          this.checkDigit ();
          this.digits ();
       }
   }

   numericSuffix ()
   {
       if (this.token == this.real_number)
       {
          if (this.ch == 'f' || this.ch == 'F')
          {
             this.nextChar ()
          }
       }
       else
       {
          if (this.ch == 'l' || this.ch == 'L')
             this.nextChar ();
          if (this.ch == 'u' || this.ch == 'U')
             this.nextChar ();
          if (this.ch == 'l' || this.ch == 'L')
             this.nextChar ();
       }
   }

   /* ------------------------------------------------------------------- */

   nextToken ()
   {
       this.token = this.eos;
       this.tokenText = "";

       var slash = false;
       var stop = false;
       var whiteSpace = true;

       while (whiteSpace && this.ch != '\0' && ! stop)
       {
          while (this.ch <= " " && this.ch != '\0')
          {
             this.nextChar ();
          }

          whiteSpace = false;
          if (this.ch == '/')
          {
             this.nextChar (); // skip '/'
             if (this.ch == '/')
             {
                this.nextChar (); // skip second  '/'
                this.comment_eol ();
                whiteSpace = true;  // check again for white space
             }
             else if (this.ch == '*')
             {
                this.nextChar (); // skip '*'
                this.comment2 ('*', '/');
                whiteSpace = true; // check again for white space
             }
             else
             {
                slash = true; // produce '/' token
             }
          }
       }

       this.tokenFileInx = this.charFileInx;
       this.tokenLineNum = this.charLineNum;
       this.tokenColNum = this.charColNum;
       this.tokenByteOfs = this.charByteOfs;

       if (slash)
       {
          this.token = this.separator;
          this.tokenText = '/';
          this.backStep ();
          this.processSeparator ();
       }

       else if (stop)
       {
          this.token = this.end_of_line;
       }

       else if (this.ch == '\0')
       {
          this.token = this.eos;
       }

       else if (this.isLetter (this.ch))
       {
           this.token = this.identifier;
           while (this.isLetterOrDigit (this.ch))
           {
               this.tokenText = this.tokenText + this.ch;
               this.nextChar ()
           }
           this.lookupKeyword ();
       }


       else if (this.isDigit (this.ch))
       {
          this.numericToken ()
       }

       else if (this.ch == '\'')
       {
          this.token = this.character_literal;
          this.nextChar ();
          while (this.ch != '\0' && this.ch != '\r' && this.ch != '\n' && this.ch != '\'')
          {
             this.tokenText = this.tokenText + this.stringChar ();
          }
          if (this.ch != '\'')
          {
             this.error ("Unterminated string");
          }
          this.nextChar ();
       }

       else if (this.ch == '\"')
       {
          this.token = this.string_literal;
          this.nextChar ();
          while (this.ch != '\0' && this.ch != '\r' && this.ch != '\n' && this.ch != '\"')
          {
             this.tokenText = this.tokenText + this.stringChar ();
          }
          if (this.ch != '\"')
          {
             this.error ("Unterminated string");
          }
          this.nextChar ();
       }

       else
       {
           this.token = this.separator;
           this.tokenText = this.ch;
           this.nextChar ();
       }
    } // end of nextToken

}; // end of class
