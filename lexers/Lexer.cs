using System;

namespace SharpView
{
    public class Lexer
    {
        private string source = ""; // source code
        private int sourceLen = 0;

        private int fileInx = 0; // file index
        private int lineNum = 1; // line number (from 1)
        private int colNum = 1;  // column number (from 1)
        private int byteOfs = 0; // byte offset (from 0)
		
        protected char ch;
        private bool slash = false;
	
		public int tokenKind;
        public string tokenText;
        public string tokenValue;
      
        private const char NUL = '\0';
        private const char CR = '\r';
        private const char LF = '\n';
        private const char QUOTE1 = '\'';
        private const char QUOTE2 = '\"';
        private const char BACKSLASH = '\\';

        protected const int eos = 0;
		protected const int identifier = 1;
		protected const int number = 2;
		protected const int real_number = 3;
		protected const int character_literal = 4;
		protected const int string_literal = 5;
		protected const int separator = 6;
		
        public Lexer ()
        {
        }
      
		public int getTokenFileInx () { return fileInx; } 
		public int getTokenLine () { return lineNum; } 
		public int getTokenCol () { return colNum; } 

		public string readChar () { return ""; }

        /* ---------------------------------------------------------------- */
      
        public void error (string msg)
        {
            throw new Exception(msg);
        }
          
        protected void nextCh ()
        {
            if (byteOfs < sourceLen)
            {
                ch = source [byteOfs];
                byteOfs++;
            
                if (ch == LF)
                {
                    lineNum ++;
                    colNum = 0;
                } 
                else if (ch != CR)
                {
                    colNum ++;
                }
            } 
            else
            {
                ch = NUL;
            }
        }
    
        private void putChar (char c)
        {
            tokenText += c;
        }
      
        private void storeChar ()
        {
            putChar (ch);
            nextCh ();
        }
      
        /* ----------------------------------------------------------------- */

        private void space ()
        {
            slash = false;
            bool stop = false;

            while (!stop)
            {
                /* space, horizontal tab, form feed, end of line */
                if (ch == ' ' || ch == '\t' || ch == '\f' || ch == CR || ch == LF)
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
                        while (ch != CR && ch != LF)
                        {
                            nextCh ();
                        }
                    } 
                    else if (ch == '*')
                    {
                        /* comment */
                        nextCh (); // skip '*'

                        do
                        {
                            while (ch != '*')
                            {
                                nextCh (); // skip other characters then '*'
                            }
                            nextCh (); // skip '*'
                        } while (ch == '/');

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

        private void numeric ()
        {
            tokenKind = number;
            bool hex = false;

            if (ch == '0')
            {
                storeChar (); // store zero

                if (ch == 'x' || ch == 'X')
                {
                    /* hexadecimal */
                    storeChar (); // store letter

                    int cnt = 0;
                    while (ch >= '0' && ch <= '9' || ch <= 'a' && ch <= 'f' || ch >= 'A' && ch <= 'F')
                    {
                        cnt++;
                        storeChar ();
                    }

                    if (cnt == 0)
                        error ("Hexadecimal digit expected");
                    hex = true;
                } else
                {
                    /* octal, zero or float */
                    while (ch >= '0' && ch <= '9')
                        storeChar ();
                }
            } else
            {
                /* decimal or float */
                while (ch >= '0' && ch <= '9')
                    storeChar ();
            }

            /* long suffix */
            if (ch == 'l' || ch == 'L')
                storeChar ();

            /* optional decimal part */
            else if (!hex)
                optDecimalPart ();
        }

        private void optDecimalPart ()
        {
            /* decimal part */
            if (ch == '.')
            {
                tokenKind = real_number;
                storeChar (); /* store decimal point */

                while (ch >= '0' && ch <= '9')
                    storeChar ();
            }

            optExponentPart ();
        }

        private void optExponentPart ()
        {
            /* exponent */
            if (ch == 'e' || ch == 'E')
            {
                tokenKind = real_number;
                storeChar (); // store letter

                if (ch == '+' || ch == '-')
                    storeChar ();

                if (ch < '0' || ch > '9')
                    error ("Digit expected");

                while (ch >= '0' && ch <= '9')
                    storeChar ();
            }

            /* float suffix */
            if (ch == 'f' || ch == 'F' || ch == 'd' || ch == 'D')
            {
                tokenKind = real_number;
                storeChar ();
            }
        }

        /* ------------------------------------------------------------- */

        private bool isHex ()
        {
            return (ch >= '0' && ch <= '9' || ch <= 'a' && ch <= 'f' || ch >= 'A' && ch <= 'F');
        }
     
        private int hexValue ()
        {
            if (ch >= '0' && ch <= '9')
                return ch - '0';
            else if (ch <= 'a' && ch <= 'f')
                return ch - 'a' + 10;
            else if (ch >= 'A' && ch <= 'F')
                return ch - 'A' + 10;
            else
                return 0;
        }
     
        private void escape ()
        {
            nextCh (); // skip backslash
            switch (ch)
            {
                case '0':
                    putChar ('\0');
                    nextCh ();
                    break;
              
                case 'x':
                case 'u':
                    {
                        bool exact = (ch == 'u');
                        int sum = 0;
                        int cnt = 0;
                        while (isHex () && cnt < 4)
                        {
                            sum = 16 * sum + hexValue ();
                            cnt++;
                        }
                        if (exact && cnt < 4)
                            error ("Hex digit expected");
                        putChar ((char)sum);
                        nextCh ();
                    }
                    break;
              
                case 'b':
                    putChar ('\b');
                    nextCh ();
                    break;
                case 'f':
                    putChar ('\f');
                    nextCh ();
                    break;
                case 'n':
                    putChar ('\n');
                    nextCh ();
                    break;
                case 'r':
                    putChar ('\r');
                    nextCh ();
                    break;
                case 't':
                    putChar ('\t');
                    nextCh ();
                    break;
                case 'v':
                    putChar ('\v');
                    nextCh ();
                    break;
                case QUOTE1:
                    putChar (QUOTE1);
                    nextCh ();
                    break;
                case QUOTE2:
                    putChar (QUOTE2);
                    nextCh ();
                    break;
                case BACKSLASH:
                    putChar (BACKSLASH);
                    nextCh ();
                    break;
              
                default: 
                    error ("unknown escape sequence");
                    break;
            }
        }

        /* ------------------------------------------------------------- */

        public void nextToken ()
        {
            tokenKind = eos;
            tokenText = "";
        
            /* skip white space and comments */
            space ();
  
            /* SLASH */
            if (slash)
            {
               tokenKind = separator;
               tokenText = "/";
            }

            /* IDENTIFIER */
            if (Char.IsLetter (ch) || ch == '_')
            {
                nextCh ();

                while (Char.IsLetterOrDigit (ch) || ch == '_')
                    nextCh ();

                tokenKind = identifier;
            }

            /* NUMBER */
            else if (ch >= '0' && ch <= '9')
            {
                numeric ();
            }

            /* STRING */
            else if (ch == QUOTE2)
            {
                nextCh (); // store quote

                while (ch != QUOTE2)
                {
                    if (ch == CR || ch == LF)
                        error ("String exceeds line");
                    else if (ch == BACKSLASH)
                        escape ();
                    else
                        storeChar ();
                }

                nextCh (); // skip quote
                tokenKind = string_literal;
            }

            /* CHARACTER */
            else if (ch == QUOTE1)
            {
                nextCh (); // skip quote

                if (ch == QUOTE1 || ch == CR || ch == LF)
                    error ("Bad character constant");
                else if (ch == BACKSLASH)
                    escape ();
                else
                    storeChar (); // store character

                nextCh (); // skip quote
                tokenKind = character_literal;
            }

            /* SPECIAL SYMBOL */
            else
            {
                tokenKind = separator;
                storeChar ();
            }
        }
    
        /* ---------------------------------------------------------------------- */

        public bool isIdentifier ()
        {
            return tokenKind == identifier;
        }

        public bool isNumber ()
        {
            return tokenKind == number;
        }

        public bool isReal ()
        {
            return tokenKind == real_number;
        }

        public bool isCharacter ()
        {
            return tokenKind == character_literal;
        }

        public bool isString ()
        {
            return tokenKind == string_literal;
        }

        public bool isSeparator (char value)
        {
            return (tokenKind == separator) && (tokenText == value.ToString ());
        }

        public bool isKeyword (string value)
        {
            return (tokenKind == identifier) && (tokenText == value);
        }

        public bool isEndOsSource ()
        {
            return tokenKind == string_literal;
        }

        /* ---------------------------------------------------------------------- */

        private string quoteStr (string value)
        {
            return QUOTE2 + value + QUOTE2;
        }
        
        public void checkSeparator (char value)
        {
            if (tokenKind != separator || tokenText != value.ToString ())
            {
                // error (value.ToString () + " expected");
                error (value.ToString () + " expected and found " + quoteStr (tokenText));
            }
            nextToken ();
        }

        public void checkKeyword (string value)
        {
            if (tokenKind != identifier || tokenText != value)
               // error (value + " expected");
               error (value + " expected and found " + quoteStr (tokenText));
            nextToken ();
        }

        public void checkEndOfSource ()
        {
            if (tokenKind != eos)
                error ("End of file expected");
        }

        /* ---------------------------------------------------------------------- */

        public string readIdentifier (string msg /* = "Identifier expected" */)
        {
            string result;
            if (tokenKind != identifier)
                error (msg);
            result = tokenText;
            nextToken ();
            return result;
        }

        public string readIdentifier ()
        {
            return readIdentifier ("Identifier expected");
        }

        public string readNumber ()
        {
            string result;
            if (tokenKind != number)
                error ("Number expected");
            result = tokenText;
            nextToken ();
            return result;
        }

        public string readReal ()
        {
            string result;
            if (tokenKind != number)
                error ("Number expected");
            result = tokenText;
            nextToken ();
            return result;
        }

        public string readCharacter ()
        {
            // char result;
            string result;
            if (tokenKind != character_literal)
                error ("Character literal expected");
            // result = tokenText[0];
            result = tokenText;
            nextToken ();
            return result;
        }
        
        public string readString ()
        {
            string result;
            if (tokenKind != string_literal)
                error ("String literal expected");
            result = tokenText;
            nextToken ();
            return result;
        }

		public bool testSymbols (byte [] set) { return false; } // !?
		public int mark () { return 0; } // !?
		public void rewind (int pos) { } // !?

		/* ---------------------------------------------------------------------- */

        /*
        bool readBool ()
        {
            bool result = false;

            if (isIdent ("true"))
            {
                nextToken ();
                result = true;
            } else if (isIdent ("false"))
            {
                nextToken ();
                result = false;
            } else
            {
                error ("Boolean value expected");
            }

            return result;
        }
        */

        /*
        string readSignedNumber ()
        {
            bool minus;
            string result;

            minus = false;
            if (token == separator && tokenText == "-")
            {
                minus = true;
                nextToken ();
            }

            result = readNumber ();

            if (minus)
                result = '-' + result;
            return result;
        }
        */

        /*
        string readValue ()
        {
            string result = "";

            if (isSeparator ('-') || token == number)
            {
                result = readSignedNumber ();
            } 
            else if (token == identifier)
            {
                result = readIdentifier ();
                while (isSeparator ('.'))
                {
                    nextToken ();
                    string id = readIdentifier ();
                    result = result + "." + id;
                }
            } 
            else if (token == string_literal || token == character_literal)
            {
                result = tokenValue;
                nextToken ();
            } 
            else
            {
                error ("Identifier, number, character or string expected");
            }

            return result;
        }
        */

        /*
        int readNumber ()
        {
            int result = 0;
            string txt = readSignedNumber ();
            bool ok;
            ok = int.TryParse (txt, out result);
            if (!ok)
                error ("Integer expected");
            return result;
        }
        */

        /*
        double readReal ()
        {
            double result = 0;
            string txt = readSignedNumber ();
            bool ok;
            ok = double.TryParse (txt, out result);
            if (!ok)
                error ("Double expected");
            return result;
        }
        */

	}

	/* ------------------------------------------------------------- */

    public class Output
	{
		public Output () { }

		public void error (string msg)
		{
			throw new Exception(msg);
		}

		public void send (string s)
		{
		}

		public void putChar (string s)
		{
		}

		public void putString (string s)
		{
		}

		public void style_indent ()	{ }
		public void style_unindent () { }
		public void style_no_space () { }
		public void style_new_line () { }
		public void style_empty_line () { }

	}
}
