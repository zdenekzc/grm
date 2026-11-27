/* OUT.C - line-by-line output (to the driver via ifc.h: showOutLine) */

#include <stdlib.h>
#include <string.h>

#include "inp.h"
#include "out.h"

#include "ifc.h"

/********************************* OUTPUT *********************************/

static int    indent;           /* number of spaces at the start of the line */
static char * OutLine = NULL;   /* output line (terminated by zero) */
static size_t OutLen = 0;       /* number of characters in OutLine */
static size_t OutCap = 0;       /* size of OutLine */

static void OutAppend (const char * txt, size_t len)
{
  if (OutLen + len + 1 > OutCap)
  {
     size_t cap = OutCap ? OutCap : 256;
     while (OutLen + len + 1 > cap) cap *= 2;
     char * p = (char *) realloc (OutLine, cap);
     if (p == NULL) showError ("Out of memory (output line)");
     OutLine = p;
     OutCap = cap;
  }
  memcpy (OutLine + OutLen, txt, len);
  OutLen += len;
  OutLine [OutLen] = 0;
}

static void OutClear (void)
{
  OutLen = 0;
  if (OutLine != NULL) OutLine [0] = 0;
}

void OpenOut (void)
/* open output file */
{
  clearOutLines (); /* clear output window */
  indent = 0;
  OutClear ();
}

void CloseOut (void)
/* close output file */
{
  PutEol ();
}

/****************************** INDENTATION *******************************/

void Indent (void)
/* increase number of spaces at the start of the line */
{
  if (indent==0)
     indent = 2;
  else
     indent += 3;
}

void Unindent (void)
/* decrease number of spaces at the start of the line */
{
  if (indent<3)
     indent = 0;
  else
     indent -= 3;
}

/********************************** PUT ***********************************/

static void IndentLine (void)
{
  if (OutLen == 0)
  {
     int i;
     for (i = 1; i <= indent; i++)
        OutAppend (" ", 1);
  }
}

void PutEol (void)
{
  showOutLine (OutLine != NULL ? OutLine : "");
  OutClear ();
}

void PutChr (char c)
{
  if (c != CR && c != LF)
  {
     IndentLine ();
     OutAppend (&c, 1);
  }
  if (c == LF) PutEol ();
}

void PutStr (char * txt)
{
  IndentLine ();
  OutAppend (txt, strlen (txt));
}
