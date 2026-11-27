
/* str.cc */

#include "str.h"
// #include "conv.h"

#if 0
   #include "inf.h" // only for test_normalize_path
#endif

#include <malloc.h> // function malloc
#include <string.h> // function memcpy

OPEN_NAMESPACE

/* ---------------------------------------------------------------------- */

/*
string charsToStr (const char * c)
{
   if (c == NULL)
      return "";
   else
      return string (strdup (c));
}
*/

char * strToChars (const string s)
{
   int len = s.length ();
   char * p = static_cast <char *> (malloc (len + 1));
   memcpy (p, s.c_str (), len);
   p [len] = 0;
   return p;
}

string bufToStr (const char * buf, int len)
{
   return string (buf, len);
}

/* ---------------------------------------------------------------------- */

string upperCase (string s)
{
   int len = s.length ();
   for (int i = 0; i<len; i ++)
   {
      char c = s[i];
      if (c >= 'a' && c <= 'z')
      {
         c = c - 'a' + 'A';
         s[i] = c;
      }
   }
   return s;
}

string lowerCase (string s)
{
   int len = s.length ();
   for (int i = 0; i<len; i ++)
   {
      char c = s[i];
      if (c >= 'A' && c <= 'Z')
      {
         c = c - 'A' + 'a';
         s[i] = c;
      }
   }
   return s;
}

string firstUpperCase (string s)
{
   if (s.length () != 0)
      s[0] = UpCase (s[0]);
   return s;
}

string firstLowerCase (string s)
{
   if (s.length () != 0)
      s[0] = LoCase (s[0]);
   return s;
}

/* ---------------------------------------------------------------------- */

bool isValidIdent (const string value)
{
   bool result = false;
   int len = value.length ();

   if (len != 0)
   {
      result = isLetter (value [0]);

      for (int i = 1; i<len && result; i++)
         if (! isLetterOrDigit (value [i]))
            result = false;
   }

   return result;
}

bool isValidNumber (const string value)
{
   int len = value.length ();

   bool result = (len > 0);
   for (int i = 0; i < len && result; i++)
      if (! isDigit (value [i]))
         result = false;

   return result;
}

/* ---------------------------------------------------------------------- */

inline bool is_WhiteSpace (int n)
{
   return n == ' ' ||
          n == '\n' ||
          n == '\r' ||
          n == '\x09';
}

string trim (const string s)
{
   int len = s.length ();
   while (len > 0 && is_WhiteSpace (s[len-1]))
      len --;

   int ofs = 1;
   while (ofs <= len && is_WhiteSpace (s[ofs-1]))
      ofs ++;

   return s.substr (ofs-1, 1+len-ofs);
}

string trimLeft (const string s)
{
   int len = s.length ();

   int ofs = 1;
   while (ofs <= len && is_WhiteSpace (s[ofs-1]))
      ofs ++;

   return s.substr (ofs-1, 1+len-ofs);
}

string trimRight (const string s)
{
   int len = s.length ();
   while (len > 0 && is_WhiteSpace (s[len-1]))
      len --;

   return s.substr (0, len);
}

/* ---------------------------------------------------------------------- */

bool hasPrefixChar (const string value, char prefix)
{
   int len = value.length ();
   return len > 1 &&  value [0] == prefix;
}

string removePrefixChar (const string value, char prefix)
{
   int len = value.length ();
   if (len > 1 && value [0] == prefix)
      return value.substr (1);
   else
      return value;
}

bool hasPrefix (const string value, const string prefix)
{
   int len = value.length ();
   int pref_len = prefix.length ();

   return len > pref_len &&
          value.substr (0, pref_len) == prefix;
}

string removePrefix (const string value, const string prefix)
{
   int len = value.length ();
   int pref_len = prefix.length ();

   if (len > pref_len &&
       value.substr (0, pref_len) == prefix)

      return value.substr (pref_len);
   else
      return value;
}

/* ---------------------------------------------------------------------- */

bool hasWordPrefixChar (const string value, char prefix)
{
   int len = value.length ();

   return len > 1 && value [0] == prefix && isUpperCaseLetter (value [1]);
}

string removeWordPrefixChar (const string value, char prefix)
{
   int len = value.length ();
   if (len > 1 && value [0] == prefix && isUpperCaseLetter (value [1]))
      return value.substr (1);
   else
      return value;
}

bool hasWordPrefix (const string value, const string prefix)
{
   int len = value.length ();
   int pref_len = prefix.length ();

   return len > pref_len &&
          value.substr (0, pref_len) == prefix &&
          isUpperCaseLetter (value [pref_len]);
}

string removeWordPrefix (const string value, const string prefix)
{
   int len = value.length ();
   int pref_len = prefix.length ();

   if (len > pref_len &&
       value.substr (0, pref_len) == prefix &&
       isUpperCaseLetter (value [pref_len]))

      return value.substr (pref_len);
   else
      return value;
}

/* ---------------------------------------------------------------------- */

bool hasSuffixChar (const string value, char suffix)
{
   int len = value.length ();
   return len > 1 && value [len-1] == suffix;
}

string removeSuffixChar (const string value, char suffix)
{
   int len = value.length ();
   if (len > 1 && value [len-1] == suffix)
      return value.substr (0, len-1);
   else
      return value;
}

bool hasSuffix (const string value, const string suffix)
{
   int len = value.length ();
   int suffix_len = suffix.length ();

   return len > suffix_len &&
          value.substr (len-suffix_len) == suffix;
}

string removeSuffix (const string value, const string suffix)
{
   if (hasSuffix (value, suffix))
      return value.substr (0, value.length () - suffix.length ());
   else
      return value;
}

/* ---------------------------------------------------------------------- */

string replaceChars (string s, char c1, char c2)
{
   int len = s.length ();
   for (int i = 0; i < len; i++)
      if (s[i] == c1)
         s[i] = c2;
   return s;
}

string removeChars (const string s, char c)
{
   string result = "";
   int len = s.length ();

   for (int i = 0; i<len; i ++)
   {
      if (s[i] != c)
         result += s[i];
   }

   return result;
}

/* ---------------------------------------------------------------------- */

string replaceSpaces (const string s)
{
   return replaceChars (s, ' ', '_');
}

string removeSpaces (const string s)
{
   return removeChars (s, ' ');
}

/* ---------------------------------------------------------------------- */

string addUnderlines (const string s)
{
   // add '_' between lower case and upper case letters

   string result = "";

   bool underline = false;
   int len = s.length ();

   for (int i = 0; i<len; i ++)
   {
      char c = s[i];

      if (c >= 'A' && c <= 'Z')
      {
         if (underline)
            result += '_';
         c = c - 'A' + 'a'; // to lower case
         underline = false;
      }
      else if (c >= 'a' && c <= 'z')
         underline = true;
      else
         underline = false;

      result += c;
   }

   return result;
}

string removeUnderlines (const string s)
{
   // remove '_' and convert next character to upper case
   string result = "";

   int len = s.length ();
   bool upc = false;

   for (int i = 0; i < len; i ++)
   {
      char c = s[i];

      if (c == '_')
         upc = true;
      else
      {
         if (upc && c >= 'a' && c <= 'z')
            c = c - 'a' + 'A'; // to upper case

         result = result + c;
         upc = false;
      }
   }

   return result;
}

/* ---------------------------------------------------------------------- */

string removePath (string s)
{
   string::size_type inx = s.rfind ('/');

   if (inx != string::npos) // if found
      s = s.substr (inx+1);

   return s;
}

string extractPath (string s)
{
   string::size_type inx = s.rfind ('/');

   if (inx != string::npos) // if found
      s = s.substr (0, inx);
   else
      s = "";

   return s;
}

string addSlash (string s)
{
   int len = s.length ();
   if (len > 0 && s[len-1] != '/')
      return s + '/';
   else
      return s;
}

string removeLastSlash (string s)
{
   int len = s.length ();
   if (len > 1 && s[len-1] == '/')
      return s.substr (0, len-1);
   else
      return s;
}

string addSubdir (const string dir_name, const string file_name)
{
   if (dir_name == "")
      return file_name;
   else if (file_name == "")
      return dir_name;
   else if (hasPrefixChar (file_name, '/'))
      return removeLastSlash (dir_name) + file_name;
   else
      return addSlash (dir_name) + file_name;
}

/* ---------------------------------------------------------------------- */

string addNamespace (string a, string b)
{
   if (a == "")
      return b;
   else if (a == "::")
      return "::" + b;
   else
      return removeSuffix (a, "::") + "::" + b;
   // removeSuffix recognize suffix only when first parameter is longer then second
}

/* ---------------------------------------------------------------------- */

string joinIdentifiers (string a, string b)
{
   // join identifiers with '_'
   // or convert first chatacter of second parameter to upper case

   if (a != "" && b != "") // one empty => nothing to do
   {
      char aa = a [a.length () - 1]; // last character from a
      char bb = b[0]; // first character from b

      // any underline => join with underline
      if (a.find ('_') != string::npos || b.find ('_') != string::npos)
      {
         if (aa != '_' && bb != '_') // do not repeat underlines
            a = a + '_';
      }
      else
      {
         // convert to uppercase
         if (bb >= 'a' && bb <='z')
            b[0] = UpCase (bb);
      }
   }

   return a + b;
}

/* ---------------------------------------------------------------------- */

string replaceTwoColons (const string s, char replacement)
{
   string result = "";
   int len = s.length ();

   if (len > 0)
   {
      char last_char = s[0];

      for (int i = 1; i<len; i ++)
      {
         char c = s[i];

         if (last_char == ':' && c == ':')
            last_char = replacement;
         else
         {
            result = result + last_char;
            last_char = c;
         }
      }

      result = result + last_char;
   }
   return result;
}

/* ---------------------------------------------------------------------- */

string removeAsterisk (string value)
{
   int len = value.length ();

   while (len > 0 && value [len-1] == ' ') len --; // skip spaces

   if (len > 0 && value [len-1] == '*')
   {
      len --; // skip asterisk
      while (len > 0 && value [len-1] == ' ') len --;  // skip spaces
   }

   return Head (value, len);
}

/* ---------------------------------------------------------------------- */

string modifyIdentifier (string s)
{
   int len = s.length ();

   if (len == 0)
      s = "_";
   else
   {
      if (! isLetter (s[0]))
         s[0] = '_';

      for (int i = 1; i < len; i++)
         if (! isLetterOrDigit (s[i]))
            s[i] = '_';
   }

   return s;
}

string modifyFileName (string s)
{
   int len = s.length ();

   if (len == 0)
      s = "_"; // empty string -> underline
   else
   {
      if (! isLetterOrDigit (s[0]))
         s[0] = '_'; // first character -> underline

      for (int i = 1; i < len; i++)
         if (! isLetterOrDigit (s[i]) || s[i] == '_')
            s[i] = '-'; // next characters -> dash
   }

   return s;
}

string headerIdentifier (const string prefix, const string file_name)
{
   return "__" + upperCase (modifyIdentifier (prefix + "_" + removePath (file_name))) + "__";
}

/* ---------------------------------------------------------------------- */

string quoteChrContent (char value)
{
   static const char hex [16+1] = "0123456789abcdef";

   string result = "";

   unsigned char ch = value;

   if (ch < ' ' || ch == 128 || ch >= 255)
   {
      result = '\\';
      switch (ch)
      {
         case '\a': result = result + 'a'; break;
         case '\b': result = result + 'b'; break;
         case '\f': result = result + 'f'; break;
         case '\n': result = result + 'n'; break;
         case '\r': result = result + 'r'; break;
         case '\t': result = result + 't'; break;
         case '\v': result = result + 'v'; break;

         default:
            result = result + 'x' + hex [ch >> 4] + hex [ch & 15];
            break;
      }
   }
   else
   {
      if (ch == '\\' || ch == '"')
         result = charToStr ('\\') + value;
      else
         result = value;
   }

   return result;
}

string quoteStrContent (const string value)
{
   int len = value.length ();

   bool simple = true;
   for (int i = 0; i < len && simple; i++)
   {
      unsigned char ch = value [i];
      if (ch < ' ' || ch == '\\' || ch == '"' || ch == 128 || ch >= 255)
         simple = false;
   }

   if (simple)
   {
      return value;
   }
   else
   {
      string result = "";

      for (int i = 0; i < len; i++)
         result += quoteChrContent (value [i]);

      return result;
   }
}

string quoteStr (const string value, char quote)
{
   return quote + quoteStrContent (value) + quote;
}

string quoteChr (char value, char quote)
{
   return quote + quoteStrContent (charToStr (value)) + quote;
}

string escapeStr (const string value)
{
   int len = value.length ();

   bool simple = true;
   for (int i = 0; i < len && simple; i++)
   {
      unsigned char ch = value [i];
      if (ch < ' ' || ch == 128 || ch >= 255)
         simple = false;
   }

   if (simple)
   {
      return value;
   }
   else
   {
      string result = "";

      for (int i = 0; i < len; i++)
      {
         unsigned char ch = value [i];
         if (ch < ' ' || ch == 128 || ch >= 255)
            result += quoteChrContent (ch);
         else
            result += ch;
      }

      return result;
   }
}

/* ---------------------------------------------------------------------- */

string removeQuotes (const string value, char quote)
{
   string result = value;

   int len = value.length ();
   if (len >= 2 && value [0] == quote && value [len-1] == quote)
   {
      result = "";
      int inx = 0;
      if (value [0] == quote) inx = 1; /* skip first quote */
      int max = len-1;
      if (value [len-1] == quote) max = len-2; /* skip last quote */

      while (inx <= max)
      {
         char ch = value [inx];

         if (ch != backslash || inx == max) /* simple character */
         {
            result += ch;
            inx ++;
         }
         else                               /* escape sequence */
         {
            inx ++;                         /* skip backslash */
            ch = value [inx];

            if (isOctal (ch))               /* octal */
            {
               int n = 0;
               int cnt = 1;
               while (isOctal (ch) && cnt <= 3 && inx <= max)
               {
                  n = n * 8 + ch - '0';
                  cnt ++;
                  inx ++;
                  ch = value [inx];
               }
               result += (char) n;  // cecko: (char) n - cmm nezna char (n)
            }

            else if (ch =='x' || ch =='X')  /* hex */
            {
               inx ++;
               int n = 0;
               while (isHexDigit (ch) && inx <= max)
               {
                  int d;
                  if (ch >= 'A' && ch <= 'F')
                     d = ch - 'A' + 10;
                  else if (ch >= 'a' && ch <= 'f')
                     d = ch - 'a' + 10;
                  else
                     d = ch - '0';
                  n = n * 16 + d;
                  inx ++;
                  ch = value [inx];
               }
               result += (char) n;  // cecko: (char) n - cmm nezna char (n)
            }
            else
            {
               char n;
               switch (ch)                  /* other */
               {
                  case 'a': n = '\a'; break;
                  case 'b': n = '\b'; break;
                  case 'f': n = '\f'; break;
                  case 'n': n = '\n'; break;
                  case 'r': n = '\r'; break;
                  case 't': n = '\t'; break;
                  case 'v': n = '\v'; break;

                  case quote1:
                  case quote2:
                  case backslash:
                  case '?':
                  default:
                     n = ch; break;
               }

               result += n;
               inx ++;
               ch = value [inx];
            }
         }
      } /* end of loop */
   }

   return result;
}

/* ---------------------------------------------------------------------- */

string trimLines (const string s)
// remove leading and trailing white spaces and empty lines
{
   int len = s.length ();

   int inx = 0;
   bool finish = false;
   while (inx < len && ! finish)
   {
      // skip white spaces
      while (inx < len && is_WhiteSpace (s[inx]))
         inx ++;

      // skip end of line
      if (inx < len && s[inx] == cr)
      {
         inx ++;
         if (inx < len && s[inx] == lf) inx ++;
      }
      else if (inx < len && s[inx] == lf)
         inx ++;
      else
         finish = true;
   }

   int start = inx;

   inx = len-1; // last character
   finish = false;
   while (start <= inx && ! finish)
   {
      // skip white spaces
      while (start <= inx && is_WhiteSpace (s[inx]))
         inx --;

      // skip end of line
      if (start <= inx && s[inx] == lf)
      {
         inx --;
         if (start <= inx && s[inx] == cr) inx --;
      }
      else if (start <= inx && s[inx] == cr)
         inx --;
      else
         finish = true;
   }

   int stop = inx;

   if (start <= stop)
      return s.substr (start, stop-start+1);
   else
      return "";
}

/* ---------------------------------------------------------------------- */

string RemoveEndOfLine (string s)
// remove trailing cr and lf
{
   int len = s.length ();
   int inx = len - 1;
 
   if (inx >= 0 && s[inx] == lf)
   {
      inx --;
      if (inx  >= 0 && s[inx] == cr) inx --;
   }

   if (inx < len-1)
      return s.substr (0, inx+1);
   else
      return s;
}
  
/* ---------------------------------------------------------------------- */

string normalizeLines (const string value)
// change end of line to line feed characters
{
   string s = value;

   int len = s.length ();
   int inx = 0;
   int max = 0;
   while (inx < len)
   {
      if (s[inx] == cr)
      {
         s[max] = lf; // store line feed
         max ++;
         inx ++;

         if (inx < len && s[inx] == lf) inx ++;
      }
      else
      {
         if (max != inx)
            s[max] = s[inx];
         max ++;
         inx ++;
      }
   }

   return s.substr (0, max);
}

/* ---------------------------------------------------------------------- */

string normalizePath (const string s)
// remove ".",  ".." and "//"
{
   string result = s; // reserve space
   int n = 0; // number of characters in output variable

   enum kind_t
   {
      none, // result variable is empty
      abs,  // result starting with '/'
      rel,  // result starting with '.'
      up,   // result starting with '..'
      name  // result starting with name
   };

   kind_t kind = none;
   int level = 0; // number of directory names in output variable

   int len = s.length ();
   int i = 0;

   while (i < len)
   {
      // get characters, up to next slash
      int start = i;
      while (i < len && s[i] != '/') i++;
      int step = i-start;
      i ++;

      bool dupl = false; // true => add directory name to result variable

      if (step == 0) // "/"
      {
         if (kind == none)
         {
            assert (n <= len);
            result[n] = '/';
            n ++;
            kind = abs; // starting absolute path
         }
      }
      else if (step == 1 && s[start] == '.') // "."
      {
         if (kind == none)
         {
            assert (n+1 <= len);
            result[n] = '.';
            n ++;
            kind = rel;  // starting relative path
         }
      }
      else if (step == 2 && s[start] == '.' && s[start+1] == '.') // ".."
      {
         if (kind == none)
         {
            kind = up;  // starting path
            dupl = true;
         }
         else if (level == 0)
         {
            // level is zero => name could be removed from result variable

            assert (kind != name);

            if (kind == abs)
            {
               // strange result "/.."
               dupl = true; // write two dots
            }
            else if (kind == rel)
            {
               // "." --> ".."
               n --; // remove "."
               assert (n == 0);
               kind = up;
               dupl = true; // write two dots
            }
            else if (kind == up)
            {
               dupl = true; // write two dots
            }
         }
         else if (level > 0)
         {
             level --;

             // remove one directory
             while (n > 0 && result[n-1] != '/')
                n --;

             if (level > 0)
             {
                assert (n > 0);
                n --; // skip slash
             }
             else
             {
                if (kind == name)
                {
                   kind = rel; // result staring with "."
                   // write one dot
                   assert (n == 0);
                   assert (n+1 <= len);
                   result[n] = '.';
                   n ++;
                }
                else if (kind == abs)
                {
                   // nothing to do
                }
                else if (kind == rel)
                {
                   assert (n > 0);
                   n --; // skip slash
                }
                else if (kind == up)
                {
                   assert (n > 0);
                   n --; // skip slash
                }
             }
         }
      }
      else
      {
         dupl = true; // add name to result variable
         level ++; // some name which cold be removed

         if (kind == none)
            kind = name;
      }

      if (dupl)
      {
         if (n == 0 || (n == 1 && result[0] == '/'))
         {
           // nothing
         }
         else
         {
            assert (n+1 <= len);
            result[n] = '/';
            n ++;
         }

         assert (n+step <= len);
         for (int k = start; k < start+step; k++)
         {
            result[n] = s[k];
            n ++;
         }
      }

      #if 0
      string txt = "";
      if (kind == abs) txt = "ABS";
      else if (kind == rel) txt = "REL";
      else if (kind == up) txt = "UP";
      else if (kind == name) txt = "NAME";
      info (Head (s, i) + " ~~> " + Head (result, n) + "    " + txt + " (level=" + IntToStr (level) + ")");
      #endif
   }

   result = Head (result, n);
   return result;
}

#if 0
void tst (string dir, string answer)
{
   // info ("TEST " + dir);
   string dir2 = normalizePath (dir);

   #if 0
      info ("(1) " + dir);
      info ("(2) " + dir2);
      if (dir2 !=  answer)
         info ("BAD");
      info ("");
   #else
      if (dir2 !=  answer)
      {
         info ("(1) " + dir);
         info ("(2) " + dir2);
         info ("BAD");
         info ("EXPECTED " + answer);
         info ("");
      }
   #endif
}

void test_normalize_path ()
{
   tst ("/", "/");
   tst ("//", "/");
   tst ("///", "/");
   tst ("./", ".");
   tst ("~", "~");
   tst ("", "");
   tst ("/a/b/c/", "/a/b/c");
   tst ("/a/b/c/.", "/a/b/c");
   tst ("/a/b/c/..", "/a/b");
   tst ("/a//b", "/a/b");
   tst ("/a/./b", "/a/b");
   tst ("/a/b/../c", "/a/c");
   tst ("/a/../b", "/b");

   tst ("/a/b/c/", "/a/b/c");
   tst ("/a//b/c/", "/a/b/c");

   tst ("/a/b//c/./d/n/../e", "/a/b/c/d/e");
   tst ("/a/b//c/./d/n/m/../e/..", "/a/b/c/d/n");

   tst ("/a/../bee/../cee", "/cee");

   tst ("/a/../../", "/..");
   tst ("./../../", "../..");

   tst ("/.", "/");
   tst ("/..", "/..");

   tst ("/./a", "/a");
   tst ("/../a", "/../a");

   tst ("/.././a", "/../a");
   tst ("/../../a", "/../../a");

   tst (".", ".");
   tst ("..", "..");

   tst ("./a", "./a");
   tst ("../a", "../a");

   tst (".././a", "../a");
   tst ("../../a", "../../a");

   tst ("/./a/b/c/", "/a/b/c");

   tst ("/a/b/c/../../../f", "/f");
   tst ("/a/b/c/../../../../f", "/../f");

   tst ("/a/b/c/../d/../../f", "/a/f");
   tst ("/a/b/c/../d/../../../f", "/f");
   tst ("/a/b/c/../d/../../../../f", "/../f");

   tst ("./a/b/", "./a/b");
   tst ("./a/b/..", "./a");
   tst ("./../", "..");
   tst ("./../..", "../..");
   tst ("./a/../", ".");
   tst ("./a/../../", "..");
   tst ("./a/../b", "./b");
   tst ("./a/b/../..", ".");
   tst ("./a/b/../../..", "..");
   tst ("./a/b/../../c", "./c");
   tst ("./a/../../b", "../b");
   tst ("./a/../../b/..", "..");
   tst ("./a/../../b/../..", "../..");

   tst ("./a/b/c/../d/../../f", "./a/f");
   tst ("./a/b/c/../d/../../../f", "./f");
   tst ("./a/b/c/../d/../../../../f", "../f");

   tst ("a/b/", "a/b");
   tst ("a/b/..", "a");

   tst ("a/../b", "./b");
   tst ("a/../../b", "../b");
}
#endif

CLOSE_NAMESPACE
