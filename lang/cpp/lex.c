
/* LEX.C */

/**************************************************************************/
/*                                                                        */
/*                            Lexical Analysis                            */
/*                                                                        */
/**************************************************************************/

#include <string.h> /* memset, strcmp */
#include <ctype.h> /* size_t */

#include "inp.h"
#include "out.h"
#include "lex.h"

SYMBOL     sy;           /* symbol being processed */

IDENT_TYP  IdentVal;     /* identifier */
NUM_TYP    NumVal;       /* number (as a sequence of characters) */
STR_TYP    StrVal;       /* string (without quotes) */
char       ChrVal;       /* character */

bool       l_suffix;     /* suffixes at the end of a number */
bool       u_suffix;
bool       f_suffix;

static int NumLen;       /* length of number */

/********************************** INIT **********************************/

void InitLex (void)
{
  /* must be called only after OpenInp () */

  sy = (SYMBOL) 0;
  CLR_ARR (IdentVal);
  CLR_ARR (NumVal);
  CLR_ARR (StrVal);
  ChrVal = 0;
  l_suffix = false;
  u_suffix = false;
  f_suffix = false;
  NumLen = 0;

  NextSymbol ();  /* read first symbol */
}

/**************************** LEXICAL ANALYSIS ****************************/

#define isletter(c)  (isalpha(c) || ((c)=='_'))
#define islod(c)     (isalpha(c) || ((c)=='_') || isdigit(c))
#define isoctal(c)   ((c) >= '0' && (c) <= '7')

/* keyword table */

typedef struct
{
  char t [17];
  SYMBOL s;
}
  KEYWORD_REC;

#define KEYWORD_MAX 50
KEYWORD_REC KeywordTab [KEYWORD_MAX] =
{
  {"auto",AUTO_},
  {"bool",BOOL_},
  {"break",BREAK_},
  {"case",CASE_},
  {"char",CHAR_},
  {"class",CLASS_},
  {"const",CONST_},
  {"const_cast",CONST_CAST_},
  {"continue",CONTINUE_},
  {"default",DEFAULT_},
  {"delete",DELETE_},
  {"do",DO_},
  {"double",DOUBLE_},
  {"dynamic_cast",DYNAMIC_CAST_},
  {"else",ELSE_},
  {"enum",ENUM_},
  {"extern",EXTERN_},
  {"false",FALSE_},
  {"float",FLOAT_},
  {"for",FOR_},
  {"friend",FRIEND_},
  {"goto",GOTO_},
  {"if",IF_},
  {"inline",INLINE_},
  {"int",INT_},
  {"long",LONG_},
  {"new",NEW_},
  {"nullptr",NULLPTR_},
  {"private",PRIVATE_},
  {"protected",PROTECTED_},
  {"public",PUBLIC_},
  {"register",REGISTER_},
  {"reinterpret_cast",REINTERPRET_CAST_},
  {"return",RETURN_},
  {"short",SHORT_},
  {"signed",SIGNED_},
  {"sizeof",SIZEOF_},
  {"static",STATIC_},
  {"static_cast",STATIC_CAST_},
  {"struct",STRUCT_},
  {"switch",SWITCH_},
  {"this",THIS_},
  {"true",TRUE_},
  {"typedef",TYPEDEF_},
  {"union",UNION_},
  {"unsigned",UNSIGNED_},
  {"virtual",VIRTUAL_},
  {"void",VOID_},
  {"volatile",VOLATILE_},
  {"while",WHILE_}
};

static void SortKeywordTab (void)
{
  bool ok;
  int i;
  KEYWORD_REC r;

  do
  {
     ok = true;
     for (i=0; i<KEYWORD_MAX-1; i++)
        if (strcmp (KeywordTab[i].t, KeywordTab[i+1].t) > 0)
        {
           ok = false;
           r = KeywordTab[i];
           KeywordTab[i] = KeywordTab[i+1];
           KeywordTab[i+1] = r;
        }
  }
  while (!ok);
}

/* ---------------------------------------------------------------------- */

static void Store (void)
/* store one character to 'NumDup' */
{
  if (NumLen>=NUM_SIZE-1) Error("Number is too long");
  NumVal[NumLen]=ch;
  NumLen++;
  NextChar();
}

static void Digits (void)
/* digit <digit> */
{
  if (!isdigit(ch)) Error("Digit expected");
  while (isdigit(ch)) Store ();
}

static void Exponent (void)
{
  if (ch=='e' || ch =='E')
  {
     sy = FLT;
     Store ();                          /* e | E */
     if (ch=='+' || ch =='-')
        Store ();                       /* + | - */
     Digits ();                         /* digit <digit> */
  }
}

static void FloatSuffix ()
{
  if (ch=='f' || ch =='F')
  {
     Store ();
     f_suffix = true;
  }
  else if (ch=='l' || ch =='L' )
  {
     Store ();
     l_suffix = true;
  }
}

/* suffixes of an integer:  L, LL (= L), U, UL, ULL, LU */
static void HexSuffix (void)
{
  if (ch=='l' || ch=='L')
  {
     Store ();
     l_suffix = true;
     if (ch=='l' || ch=='L') Store ();
     if (ch=='u' || ch=='U') { Store (); u_suffix = true; }
  }
  else if (ch=='u' || ch=='U')
  {
     Store ();
     u_suffix = true;
     if (ch=='l' || ch=='L')
     {
        Store ();
        l_suffix = true;
        if (ch=='l' || ch=='L') Store ();
     }
  }
}

static void Number (void)
{
  sy = NUM;
  NumLen = 0;
  l_suffix = false;
  u_suffix = false;
  f_suffix = false;

  Store ();                         /* digit */

  if (ch=='x'||ch=='X')             /* Hexadecimal number */
  {
     Store ();
     while (isxdigit (ch)) Store ();
     HexSuffix ();                    /* 0x7fffffffLL, 0xffUL */
     if (isalnum (ch))
        Error ("Hexadecimal digit expected");
  }
  else                                        /* Decimal or octal number */
  {
     while (isdigit (ch)) Store ();           /* <digit> */

     if (ch=='.')
     {
        sy = FLT;
        Store ();                             /* '.' */
        if (isdigit (ch)) Digits ();          /* digit <digit> */
     }

     Exponent ();                             /* e|E  +|- digit <digit> */

     if (sy==FLT) FloatSuffix ();             /* f | F | l | L */

     if (sy==NUM)
     {
        /* check of octal numbers */
        if (NumVal[0] == '0')
        {
           for (int i=1; i<NumLen; i++)
              if (NumVal[i] > '7') Error ("Bad octal number");
        }

        /* suffixes */
        if (ch=='l' || ch=='L')
        {
           Store ();
           l_suffix = true;
           if (ch=='l' || ch=='L') Store ();   /* LL = L (long long = long) */

           if (ch=='u' || ch=='U')
           {
              Store ();
              u_suffix = true;
           }
        }
        else if (ch=='u' || ch=='U')
        {
           Store ();
           u_suffix = true;

           if (ch=='l' || ch=='L')
           {
              Store ();
              l_suffix = true;
              if (ch=='l' || ch=='L') Store ();   /* ULL */
           }
        }
     }
  }

  NumVal [NumLen] = 0; /* end the string */
}

static void Fraction (void)
/* number starting with a decimal point */
{
  sy = FLT;
  NumVal [0] = '.'; /* the dot has already been read */
  NumLen = 1;
  l_suffix = false;
  u_suffix = false;
  f_suffix = false;

  while (isdigit (ch))
     Digits ();

  Exponent ();
  FloatSuffix ();

  NumVal [NumLen] = 0;
}

static void Identifier (void)
{
  int len, a, b, c, cmp;

  len = 0;
  while (islod(ch))   /* letter <lod> */
  {
     if (len>=IDENT_SIZE-1) Error ("Identifier too long");
     IdentVal[len] = ch;
     len ++;
     NextChar ();
  }
  IdentVal[len] = 0;
  sy = IDENT;

  /* RESERWED WORD */
  a = 1;
  b = KEYWORD_MAX;
  while (a<=b)
  {
     c = (a+b)/2;   /* a <= c < b */
     cmp = strcmp (IdentVal,KeywordTab[c-1].t);
     if (cmp < 0)
        b = c-1;
     else if (cmp > 0)
        a = c+1;
     else
     {
        sy = KeywordTab[c-1].s;
        return;
     }
  }

  /* macro NULL (we have no preprocessor) */
  if (strcmp (IdentVal, "NULL") == 0)
     sy = NULLPTR_;
}

static char Character (void)
/* read one C-style character */
{
  int  n, d;
  int  cnt;
  char last;

  if (ch!=BACKSLASH)                  /* simple character */
  {
     last = ch;
     NextChar ();
     return last;
  }
  else                                /* escape sequence */
  {
     NextChar ();                     /* skip backslash */

     if (isoctal (ch))                /* octal */
     {
        n = 0;
        cnt = 1;
        while (isoctal (ch) && cnt<=3)
        {
           n = n*8+ch-'0';
           cnt++;
           NextChar ();
        }
        return (char) n;
     }

     else if (ch=='x' || ch=='X')     /* hex */
     {
        NextChar ();
        n = 0;
        while (isxdigit (ch))
        {
            if (ch >= 'A' && ch <= 'F')
               d = ch - 'A' + 10;
            else if (ch >= 'a' && ch <= 'f')
               d = ch - 'a' + 10;
            else
               d = ch - '0';
           n = n*16+d;
           NextChar ();
        }
        return (char) n;
     }

     else
     {
        last = ch;
        NextChar ();
        switch (last)                 /* other */
        {
           case 'a': return '\a';
           case 'b': return '\b';
           case 'f': return '\f';
           case 'n': return '\n';
           case 'r': return '\r';
           case 't': return '\t';
           case 'v': return '\v';

           case QUOTE1:    return last;
           case QUOTE2:    return last;
           case BACKSLASH: return last;
           case '?':       return last;

           default:        return last;
        }
     }
  }
}

static void Select2 (SYMBOL s, char c2, SYMBOL s2)
{
  if (ch==c2)
  {
     NextChar ();
     sy = s2;
  }
  else sy = s;
}

static void Select3 (SYMBOL s, char c2, SYMBOL s2, char c3, SYMBOL s3)
{
  if (ch==c2)
  {
    NextChar ();
    sy=s2;
  }
  else if (ch==c3)
  {
    NextChar ();
    sy=s3;
  }
  else sy=s;
}

static void Select (SYMBOL s, char c2, SYMBOL s2, char c3, SYMBOL s3, SYMBOL s4)
{
  if (ch==c2)
  {
    NextChar ();
    sy=s2;
  }
  else if (ch==c3)
  {
    NextChar ();
    sy=s3;

    if (ch=='=')
    {
       NextChar ();
       sy=s4;
    }
  }
  else sy=s;
}

void Select4 (SYMBOL s, char c2, SYMBOL s2, char c3,
                                 SYMBOL s3, char c4, SYMBOL s4)
{
  if (ch==c2)
  {
    NextChar ();
    sy=s2;
  }
  else if (ch==c3)
  {
    NextChar ();
    sy=s3;
  }
  else if (ch==c4)
  {
    NextChar ();
    sy=s4;
  }
  else sy=s;
}

/* ---------------------------------------------------------------------- */

const char * LexCurrentFile (void) { return NULL; }
int LexCurrentLine (void) { return InpLineNum; }

static void RawNextSymbol (void);

/* symbol; X::name with namespace X => name (decl.c - NamespaceQual) */
void NextSymbol (void)
{
  RawNextSymbol ();
  if (sy == IDENT) NamespaceQual ();
}

static void RawNextSymbol (void)
{
  char prev;
  bool quit;
  char old;

  if (ReplaySymbol != NULL)   /* replay of stored symbols (decl.c) */
  {
     ReplaySymbol ();
     return;
  }

  again:

  /* SPACE */
  if (ch<=' ' && ch!=NUL)
  {
     NextChar ();
     goto again;
  }

  /* COMMENT */
  else if (ch == '/')
  {
     NextChar (); /* skip '/' */

     if (ch == '/') /* comment with two slashes */
     {
        while (ch != LF)
           NextChar ();
        goto again;
     }

     else if (ch == '=') /* /= */
     {
        NextChar ();
        sy = DIVASSIGN;
     }

     else if (ch != '*') /* ordinary slash */
        sy = SLASH;

     else /* comment with slash and asterisk */
     {
        NextChar (); /* skip '*' */

        prev = ' ';
        while (prev != '*' || ch != '/')
        {
           prev = ch;
           NextChar ();
        }

        NextChar (); /* skip '/' */
        goto again;
     }
  }

  /* PREPROCESSOR - directives (#include ...) are skipped */
  else if (ch == '#')
  {
     while (ch != LF && ch != NUL)
        NextChar ();
     goto again;
  }

  /* IDENTIFIER */
  else if (isletter(ch))
     Identifier ();

  /* PERIOD */
  else if (ch=='.')
  {
     NextChar (); /* skip first dot */

     if (isdigit (ch)) /* number starting with a dot */
     {
        Fraction ();
     }
     else if (ch=='.') /* more dots */
     {
        NextChar (); /* skip second dot */
        if (ch=='.') /* three dots */
        {
           NextChar ();
           sy = DOTS;
        }
        else /* only two dots */
        {
           Error ("Unknown symbol");
        }
     }
     else /* one dot */
        sy = PERIOD;
  }

  /* NUMBER */
  else if (isdigit (ch))
     Number ();

  /* STRING */
  else if (ch==QUOTE2)
  {
     int len;

     NextChar (); /* skip quote */
     len = 0;
     quit = false;

     while (!quit)
     {
        if (ch==QUOTE2)
           quit = true;
        else if (ch==LF)
        {
           if (len>0 && StrVal[len-1]==BACKSLASH)
           {
              len --; /* skip backslash */
              NextChar ();
           }
           else
              Error ("String exceeds line");
        }
        else
        {
           if (len>=STR_SIZE-1) Error ("String too long");
           StrVal[len] = Character ();
           len++;
        }
     }

     NextChar (); /* skip quote */

     StrVal[len] = 0;
     sy=STR;
  }

  /* CHARACTER */
  else if (ch==QUOTE1)
  {
     NextChar (); /* skip quote */

     if (ch==QUOTE1 || ch==LF)
        Error ("Bad character constant");
     ChrVal = Character ();

     if (ch!=QUOTE1)
        Error ("Bad character constant");
     NextChar (); /* skip quote */

     sy=CHR;
  }

  /* END OF SOURCE TEXT */
  else if (ch==NUL)
  {
     sy = EOS;
  }

  /* SPECIAL SYMBOL */
  else
  {
    old = ch;
    NextChar ();

    switch (old) {
      case '+': Select3 (PLUS, '+', DPLUS, '=', ADDASSIGN); break;
      case '-': Select4 (MINUS, '-', DMINUS, '=', SUBASSIGN, '>', ARROW); break;
      case '*': Select2 (ASTERISK, '=', MULASSIGN); break;
      case '/': Select2 (SLASH, '=', DIVASSIGN); break;
      case '.': sy=PERIOD; break;
      case ',': sy=COMMA; break;
      case ':': Select2 (COLON, ':', DCOLON); break;
      case ';': sy=SEMICOLON; break;
      case '(': sy=LPAR; break;
      case ')': sy=RPAR; break;
      case '[': sy=LBRACK; break;
      case ']': sy=RBRACK; break;
      case '{': sy=LBRACE; break;
      case '}': sy=RBRACE; break;
      case '^': Select2 (CARET, '=', XORASSIGN); break;
      case '=': Select2 (ASSIGN, '=', EQUAL); break;
      case '!': Select2 (LOGNOT, '=', UNEQUAL); break;
      case '%': Select2 (PERCENT, '=', MODASSIGN); break;
      case '&': Select3 (AND, '&', LOGAND, '=', ANDASSIGN); break;
      case '|': Select3 (BAR, '|', LOGOR, '=', ORASSIGN); break;
      case '~': sy=TILDA; break;
      case '?': sy=QUESTION; break;
      case '<': Select (LESS,'=', LESSEQUAL, '<', SHL, SHLASSIGN); break;
      case '>': Select (GREATER,'=',GREATEREQUAL, '>', SHR, SHRASSIGN); break;

      default: Error("Unknown symbol"); break;
    }
  }
}

/************************** CHECK CURRENT SYMBOL **************************/

/* tables for converting symbols back to character strings - for debugging */

typedef struct
{
  char t [6];
  SYMBOL s;
}
  SPECREC;

#define SPECMAX 53
SPECREC SpecTab [SPECMAX] =
  {
    {"+",PLUS},
    {"-",MINUS},
    {"*",ASTERISK},
    {"/",SLASH},
    {".",PERIOD},
    {",",COMMA},
    {":",COLON},
    {";",SEMICOLON},
    {"<",LESS},
    {">",GREATER},
    {"<=",LESSEQUAL},
    {">=",GREATEREQUAL},
    {"(",LPAR},
    {")",RPAR},
    {"[",LBRACK},
    {"]",RBRACK},

    {"==",EQUAL},
    {"!=",UNEQUAL},
    {"->",ARROW},
    {"=",ASSIGN},

    {"{",LBRACE},
    {"}",RBRACE},
    {"...",DOTS},

    {"++",DPLUS},
    {"--",DMINUS},
    {"::",DCOLON},
    {"~",TILDA},
    {"!",LOGNOT},
    {"%",PERCENT},
    {"<<",SHL},
    {">>",SHR},
    {"&",AND},
    {"^",CARET},
    {"|",BAR},
    {"&&",LOGAND},
    {"||",LOGOR},
    {"?",QUESTION},

    {"*=",MULASSIGN},
    {"/=",DIVASSIGN},
    {"%=",MODASSIGN},
    {"+=",ADDASSIGN},
    {"-=",SUBASSIGN},
    {"<<=",SHLASSIGN},
    {">>=",SHRASSIGN},
    {"&=",ANDASSIGN},
    {"|=",ORASSIGN},
    {"^=",XORASSIGN},

    {"IDENT",IDENT},
    {"NUM",NUM},
    {"FLT",FLT},
    {"STR",STR},
    {"CHR",CHR},

    {"EOS",EOS}
  };

static void SymToStr (SYMBOL par, STR_TYP s)
/* conversion of symbol to character string */
{
  int i;

  for (i=1; i<=KEYWORD_MAX; i++)
     if (par == KeywordTab[i-1].s)
     {
        strmov (s, sizeof (STR_TYP), KeywordTab[i-1].t);
        return;
     }

  for (i=1; i<=SPECMAX; i++)
     if (par == SpecTab[i-1].s)
     {
        strmov (s, sizeof (STR_TYP), SpecTab[i-1].t);
        return;
     }

  strmov (s, sizeof (STR_TYP), "???");
}

void PutSymbol (SYMBOL par)
/* show symbol in the output */
{
   STR_TYP txt;
   SymToStr (par, txt);
   PutStr (txt);
}

void PutCurrentSymbol (void)
/* show the symbol being processed in the output */
{
  switch (sy)
  {
     case IDENT:
        PutStr ("Ident (");
        PutStr (IdentVal);
        PutStr (")");
        break;

     case NUM:
        PutStr ("Num (");
        PutStr (NumVal);
        PutStr (")");
        break;

     case FLT:
        PutStr ("Flt (");
        PutStr (NumVal);
        PutStr (")");
        break;

     case STR:
        PutStr ("Str (");
        PutStr (StrVal);
        PutStr (")");
        break;

     case CHR:
        PutStr ("Chr (");
        PutChr (ChrVal);
        PutStr (")");
        break;

     default:
        PutSymbol (sy);
        break;
  }
}

void CheckSymbol (SYMBOL par)
{
  STR_TYP msg;

  /* report error if sy <> par */
  if (sy != par)
  {
     switch (par)
     {
        case IDENT: strmov (msg, sizeof (msg), "Identifier"); break;
        case NUM:   strmov (msg, sizeof (msg), "Number"); break;
        case FLT:   strmov (msg, sizeof (msg), "Floating point number"); break;
        case STR:   strmov (msg, sizeof (msg), "String"); break;
        case CHR:   strmov (msg, sizeof (msg), "Character constant"); break;
        default:    SymToStr (par, msg); break;
     }
     stradd (msg, sizeof (msg), " expected");
     Error (msg);
  }

  NextSymbol();  /* skip symbol */
}

/******************************* UTILITIES ********************************/

void strmov (char * a, size_t size, char * b)
/* move string */
{
   strncpy (a, b, size-1);
}

void stradd (char * a, size_t size, char * b)
/* append string */
{
   strncat (a, b, size-1);
}
