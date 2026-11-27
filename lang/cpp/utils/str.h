
#ifndef __PROG_STR_H__
#define __PROG_STR_H__

#include "std.h"

OPEN_NAMESPACE

/* characters */

const char cr = '\r';
const char lf = '\n';
const char tab = '\t';
const char quote1 = '\'';
const char quote2 = '\"';
const char backslash = '\\';

const string two_quotes = "\"\"";

inline bool isLetter (char ch)
{
   return (ch >= 'A' && ch <= 'Z') ||
          (ch >= 'a' && ch <= 'z') ||
          (ch == '_');
}

inline bool isUpperCaseLetter (char ch)
{
   return (ch >= 'A' && ch <= 'Z') || (ch == '_');
}

inline bool isDigit (char ch)
{
   return ch >= '0' && ch <= '9';
}

inline bool isOctal (char ch)
{
   return ch >= '0' && ch <= '7';
}

inline bool isHexDigit (char ch)
{
   return (ch >= '0' && ch <= '9') ||
          (ch >= 'a' && ch <= 'f') ||
          (ch >= 'A' && ch <= 'F');
}

inline bool isLetterOrDigit (int ch)
{
   return isLetter (ch) || isDigit (ch);
}

inline char UpCase (char ch)
{
   if (ch >= 'a' && ch <= 'z')
      return ch - 'a' + 'A';
   else
      return ch;
}

inline char LoCase (char ch)
{
   if (ch >= 'A' && ch <= 'Z')
      return ch - 'A' + 'a';
   else
      return ch;
}

/* stl */

typedef string::size_type str_size_type;
const str_size_type str_npos = string::npos;

inline string Head (const string s, int i)
{
   // first i characters
   return s.substr (0, i);
}

inline string Tail (const string s, int i)
{
   // skip first i characters
   int len = s.length ();
   if (i > len)
      return "";
   else
      return s.substr (i);
}

inline string Substr (const string s, int start, int size)
{
   // 'size' characters from 'start' position
   int len = s.length ();
   if (start > len)
      return "";
   else
      return s.substr (start, size);
}

inline string Left (const string s, int i)
{
   // first i characters
   return Head (s, i);
}

inline string Right (const string s, int i)
{
   // last i characters
   int len = s.length ();
   if (i > len)
      return "";
   else
      return s.substr (len-i, i);
}

inline string Middle (const string s, int start, int size)
{
   // 'size' characters from 'start' position
   return Substr (s, start, size);
}

inline string Skip (const string s, int i)
{
   // skip first i characters
   return Tail (s, i);
}

inline string Subrange (const string s, int start, int stop)
{
   // characters from 'start' position to 'stop' position
   int len = s.length ();
   if (start < 0) start = 0;
   if (stop < 0) start = 0;

   if (start > len || stop < start)
      return "";
   else
      return s.substr (start, stop-stop+1);
}

inline str_size_type findChr (const string s, char c)
{
   return s.find (c);
}

inline str_size_type rfindChr (const string s, char c)
{
   return s.rfind (c);
}

inline str_size_type findSubstr (const string s, const string t)
{
   return s.find (t);
}

inline bool containsChar (const string s, const char t)
{
   return s.find (t) != string::npos;
}

inline bool containsSubstr (const string s, const string t)
{
   return s.find (t) != string::npos;
}

inline string charToStr (char c) { string s = ""; s += c; return s; } // convert one character to string
inline string charsToStr (const char * c) { string s = ""; if (c != NULL) s = c; return s; } // convert char pointer to string
char * strToChars (const string s); // convert string to char pointer
string bufToStr (const char * buf, int len); // len characters from buf (string (buf, len))

/* strings */

string quoteChrContent (char value);
string quoteStrContent (const string value); // convert to C-style string literal, without outer quotes
string escapeStr (const string value); // convert nonprintable characters
string quoteStr (const string value, char quote = quote2); // convert to C-style string literal
string quoteChr (char c, char quote = quote1); // convert to C-style character literal
string removeQuotes (const string value, char quote = quote2); // convert from C-style

string upperCase (string s); // convert to upper case
string lowerCase (string s); // convert to lower case

string firstUpperCase (string s); // convert first character to upper case
string firstLowerCase (string s); // convert first character to lower case

bool isValidIdent (const string value); // is it valid identifier
bool isValidNumber (const string value); // is it sequence of digits

string trim (const string s); // remove leading and trailing white spaces
string trimLeft (const string s); // remove leading white spaces
string trimRight (const string s); // remove trailing white spaces

bool   hasPrefix (const string value, const string prefix);
bool   hasPrefixChar (const string value, char prefix);
string removePrefix (const string value, const string prefix); // remove prefix (if present)
string removePrefixChar (const string value, char prefix);

bool   hasWordPrefix (const string value, const string prefix);
bool   hasWordPrefixChar (const string value, char prefix);
string removeWordPrefix (const string value, const string prefix);
string removeWordPrefixChar (const string value, char prefix);

bool   hasSuffix (const string value, const string suffix);
bool   hasSuffixChar (const string value, char suffix);
string removeSuffix (const string value, const string suffix); // remove suffix (if present)
string removeSuffixChar (const string value, char suffix);

string replaceChars (string s, char c1, char c2); // replace c1 with c2
string removeChars (const string s, char c); // remove characters c

string replaceSpaces (const string s); // replaces spaces with underlines
string removeSpaces (const string s); // remove spaces

string addUnderlines (const string s); // add '_' between lower case and upper case letters
string removeUnderlines (const string s); // remove '_' and convert next character to upper case

string removePath (string s); // remove last '/' and preceding characters
string extractPath (string s); // remove characters after last '/'

string addSlash (string s); // add '/' (if not already present)
string removeLastSlash (string s); // remove last '/' (if present and length is greater than one)

string addSubdir (const string dir_name, const string file_name);
// combine directory and file name

string addNamespace (string a, string b);
// concatenate namespace (if present) and identifier (a::b)

string joinIdentifiers (string a, string b);
// join identifiers with '_' or convert first chatacter of second parameter to upper case

string replaceTwoColons (const string s, char c);
// replace '::' with character c

string removeAsterisk (string value);
// remove trailling spaces and one asterisk

string modifyIdentifier (string s);
// replace invalid characters with underlines

string modifyFileName (string s);
// replace leading invalid character with undeline, other with '-'

string headerIdentifier (const string prefix, const string file_name);
// identifier for ifdef directive in header file (__PREFIX_FILE_NAME__)

string trimLines (const string s);
// remove leading and trailing white spaces and empty lines

string RemoveEndOfLine (string s);
// remove trailing cr and lf

string normalizeLines (const string s);
// change end of line to line feed characters

string normalizePath (const string s);
// remove ".",  ".." and "//"

void test_normalize_path ();

CLOSE_NAMESPACE

#endif /* __PROG_STR_H__ */
