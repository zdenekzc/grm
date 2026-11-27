/* conv.cc */

/* prevody cisel - nahrada sablon NumToStr a StrToNum z utils/conv.h
   (puvodne ostringstream / istringstream)

   chovani odpovida puvodnimu istringstream >> noskipws:
   bez uvodnich mezer, nepovinne znamenko, alespon jedna cislice, cely text,
   preteceni => chyba, zaporne cislo pro unsigned => modulo (jako strtoul),
   0x / 0X na zacatku => sestnactkove cislice */

#include "conv.h"
#include "str.h" // charToStr
#include <cstdio> // snprintf
#include <cstdlib> // strtod

OPEN_NAMESPACE

/* ---------------------------------------------------------------------- */

string ULongToStr (unsigned long num)
{
   string result = "";
   do
   {
      result = charToStr ('0' + num % 10) + result;
      num = num / 10;
   }
   while (num != 0);
   return result;
}

string LongToStr (long num)
{
   if (num < 0)
      return "-" + ULongToStr (- (unsigned long) num); // i LONG_MIN
   else
      return ULongToStr (num);
}

string DoubleToStr (double num)
{
   char buf [64];
   snprintf (buf, sizeof (buf), "%g", num); // ostream: precision 6, %g
   string result = buf;
   return result;
}

/* ---------------------------------------------------------------------- */

static bool ReadInteger (string txt, unsigned long & value, bool & negative)
// absolutni hodnota a znamenko, false pri chybe nebo preteceni unsigned long
{
   int len = txt.length ();
   int inx = 0;
   unsigned long base = 10;

   value = 0;
   negative = false;

   if (len > 2 && txt[0] == '0' && (txt[1] == 'x' || txt[1] == 'X'))
   {
      base = 16;
      inx = 2;
   }

   if (inx < len && (txt[inx] == '+' || txt[inx] == '-'))
   {
      negative = (txt[inx] == '-');
      inx ++;
   }

   if (inx >= len)
      return false; // zadna cislice

   while (inx < len)
   {
      char c = txt[inx];
      unsigned long d;
      if (c >= '0' && c <= '9')
         d = c - '0';
      else if (base == 16 && c >= 'a' && c <= 'f')
         d = c - 'a' + 10;
      else if (base == 16 && c >= 'A' && c <= 'F')
         d = c - 'A' + 10;
      else
         return false;

      if (value > (ULONG_MAX - d) / base)
         return false; // preteceni

      value = value * base + d;
      inx ++;
   }

   return true;
}

void StrToLong (string txt, long & result, bool & ok)
{
   unsigned long value;
   bool negative;
   ok = ReadInteger (txt, value, negative);
   if (ok)
   {
      if (negative)
      {
         if (value > (unsigned long) LONG_MAX + 1)
            ok = false;
         else
            result = - (long) (value - 1) - 1; // i LONG_MIN
      }
      else
      {
         if (value > (unsigned long) LONG_MAX)
            ok = false;
         else
            result = value;
      }
   }
}

void StrToULong (string txt, unsigned long & result, bool & ok)
{
   unsigned long value;
   bool negative;
   ok = ReadInteger (txt, value, negative);
   if (ok)
   {
      if (negative)
         result = - value;
      else
         result = value;
   }
}

void StrToUInt (string txt, unsigned int & result, bool & ok)
{
   unsigned long value;
   bool negative;
   ok = ReadInteger (txt, value, negative);
   if (ok && value > UINT_MAX)
      ok = false;
   if (ok)
   {
      if (negative)
         result = - (unsigned int) value;
      else
         result = value;
   }
}

void StrToDouble (string txt, double & result, bool & ok)
{
   const char * s = txt.c_str ();
   char * end = NULL;
   ok = (txt.length () > 0 && s[0] != ' ' && s[0] != '\t' && s[0] != '\n');
   if (ok)
   {
      double value = strtod (s, & end);
      ok = (end != NULL && * end == 0);
      if (ok)
         result = value;
   }
}

/* ---------------------------------------------------------------------- */

CLOSE_NAMESPACE
