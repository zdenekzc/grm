/* INP.C - input and error reporting (text supplied by the driver, ifc.h) */

#include <string.h>

#include "inp.h"
#include "out.h"

#include "ifc.h"

char   ch;         /* character being processed */
int    InpPos;     /* position in input text */
int    InpColNum;  /* column number */
int    InpLineNum; /* line number */

static const char * InpTxt;  /* input text */
static int          InpLen;  /* length of input text */

/********************************* INPUT **********************************/

void OpenInp (void)
{
  InpTxt = getInpText (); /* text from the driver */
  if (InpTxt == NULL) InpTxt = "";
  InpLen = strlen (InpTxt);
  InpPos = 0;

  InpColNum = 0;
  InpLineNum = 1;

  NextChar (); /* read first character */
}

/* ---------------------------------------------------------------------- */

void CloseInp (void)
{
  /* nothing in our case */
}

/* ---------------------------------------------------------------------- */

void NextChar (void)
{
  if (InpPos < InpLen)
  {
     ch = InpTxt [InpPos]; /* read one character */
     InpPos ++;

     InpColNum ++; /* column number */
     if (ch == LF)
     {
        InpLineNum ++; /* line number */
        InpColNum = 0;
     }
  }

  else if (InpPos == InpLen)
  {
     ch = NUL; /* character 0 - end of input text */
     InpPos ++;
  }

  else
  {
     Error ("End of source"); /* end of input text has already been reported */
  }
}

/***************************** ERROR MESSAGES *****************************/

void Error (char * msg)
{
  showError (msg);
}
