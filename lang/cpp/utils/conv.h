
#ifndef __PROG_CONV_H__
#define __PROG_CONV_H__

#include "std.h"
#include <climits>

OPEN_NAMESPACE

/* ---------------------------------------------------------------------- */

/* prevody cisel (konkretni funkce misto sablon NumToStr, StrToNum, NumToHex)

   StrTo... : txt ... vstupni text (bez mezer, znamenko, cislice desitkove
                      nebo sestnactkove za 0x / 0X)
              ok == true ... prevod se podaril (cely text, bez preteceni)
              result ... vysledek, prirazen jen pri ok == true */

string LongToStr (long num);
string ULongToStr (unsigned long num);
string DoubleToStr (double num);

void StrToLong (string txt, long & result, bool & ok);
void StrToULong (string txt, unsigned long & result, bool & ok);
void StrToUInt (string txt, unsigned int & result, bool & ok);
void StrToDouble (string txt, double & result, bool & ok);

/* ---------------------------------------------------------------------- */

inline string BoolToStr (bool value) // convert bool to string
{
   return value ? "true" : "false";
}

inline void StrToBool (string txt, bool & result, bool & ok) // convert string to boolean
{
   if (txt == "true")
   {
      result = true;
      ok = true;
   }
   else if (txt == "false")
   {
      result = false;
      ok = true;
   }
   else
   {
      ok = false;
   }
}

inline bool StrToBoolOk (string txt, bool & result)
{
   bool ok;
   StrToBool (txt, result, ok);
   return ok;
}

/* ---------------------------------------------------------------------- */

/* ---------------------------------------------------------------------- */

inline string IntToStr (int value)
// convert int to string
{
   return LongToStr (value);
}

inline void StrToInt (string txt, int & result, bool & ok)
// convert string to int
// txt ... input value
// ok == true ... conversion succeded
// result ... converted value, assigned only when ok == true
{
   long n = 0;
   StrToLong (txt, n, ok);
   if (ok && (n < INT_MIN || n > INT_MAX))
      ok = false;
   if (ok)
      result = n;
}

inline bool StrToIntOk (string txt, int & result)
// returns ok from previous function
{
   bool ok;
   StrToInt (txt, result, ok);
   return ok;
}

/* ---------------------------------------------------------------------- */

struct conv_table_t
{
   int index;
   const char * text;
};

string EnumToStr (int value, int count, const conv_table_t * table);

void StrToEnum (string txt,
                int count, const conv_table_t * table,
                int & result,
                bool & ok);

bool StrToEnumOk (string txt,
                int count, const conv_table_t * table,
                int & result);

/* ---------------------------------------------------------------------- */

string BitsToStr (unsigned int value, int count, const conv_table_t * table);

void StrToBits (string txt,
                int count, const conv_table_t * table,
                unsigned int & result,
                bool & ok);

bool StrToBitsOk (string txt,
                int count, const conv_table_t * table,
                unsigned int & result);

/* ---------------------------------------------------------------------- */

string PtrToStr (void * p);

/* ---------------------------------------------------------------------- */

CLOSE_NAMESPACE

#endif /* __PROG_CONV_H__ */
