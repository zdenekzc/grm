using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Drawing;

namespace SharpView
{
    public class Parser0 : Lexer
    {
        public Parser0()
        {
        }
        
        public void readClass ()
        {
            checkKeyword ("class");
            checkSeparator ('{');
            while (! isSeparator ('}'))
            {
               string type = readIdentifier ("Type name expected");
               string name = readIdentifier ("Variable identifier expected");
               checkSeparator (';');
            }
            checkSeparator ('}');
        }
        
        public void readData ()
        {
            string type_name = readIdentifier ("");
            string block_name = "";
            if (isIdentifier ())
                block_name = readIdentifier ("");
           
            checkSeparator ('{');
            while (! isSeparator ('}'))
            {
               string name = readIdentifier ("Variable identifier expected");
               checkSeparator ('=');

               string value = "";
               if (isIdentifier ())
                   value = readIdentifier ("");
               else if (isNumber ())
                   value = readNumber ();
               else if (isReal ())
                   value = readReal ();
               else if (isCharacter ())
                   value = readCharacter ();
               else if (isString ())
                  value = readString ();
               else
                   error ("Value expected");
               
               checkSeparator (';');
            }
            checkSeparator ('}');
        }
    }
}
