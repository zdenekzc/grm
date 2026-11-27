/* LEXER.CC */

/**************************************************************************/
/*                                                                        */
/*               Lexical Analysis with Preprocessor                       */
/*                                                                        */
/**************************************************************************/

/*
   Alternativa k lex.c se zpracovanim direktiv preprocesoru (viz lexer.h).
   Myslenky prevzaty z utils/textio.cc a utils/envio.cc, napsano v jazyce C.

   Vrstvy:
     1. vstup       - zasobnik urovni: hlavni text (inp.c), vlozene soubory,
                      rozvinuta makra, pomocne texty (argumenty, tela maker)
     2. RawToken    - symboly preprocesoru (identifikator, cislo, retezec,
                      znak, oddelovac, konec radky) i s puvodnim textem
     3. ExpToken    - rozvijeni maker
     4. DirToken    - direktivy (# na zacatku radky) a podminene preklady
     5. NextSymbol  - prevod na SYMBOL a hodnoty IdentVal, NumVal, StrVal, ChrVal
*/

#include <string.h> /* memset, strcmp */
#include <stdlib.h> /* malloc, realloc, free, strtoul */
#include <stdio.h>  /* fopen, snprintf */
#include <ctype.h>

#include "inp.h"
#include "out.h"
#include "lexer.h"

SYMBOL     sy;           /* zpracovavany symbol */

IDENT_TYP  IdentVal;     /* identifikator */
NUM_TYP    NumVal;       /* cislo (jako posloupnost znaku) */
STR_TYP    StrVal;       /* retezec (bez uvozovek) */
char       ChrVal;       /* znak */

bool       l_suffix;     /* znacky na konci cisla */
bool       u_suffix;
bool       f_suffix;

#define isletter(c)  (isalpha(c) || ((c)=='_'))
#define islod(c)     (isalpha(c) || ((c)=='_') || isdigit(c))
#define isoctal(c)   ((c) >= '0' && (c) <= '7')

#define LEVEL_MAX    64     /* vnoreni souboru a maker */
#define PARAM_MAX    64     /* pocet parametru makra */
#define COND_MAX     64     /* vnoreni #if */
#define INCL_MAX     32     /* pocet adresaru pro #include */
#define TOKEN_SIZE   1024   /* delka jednoho symbolu preprocesoru */
#define PATH_SIZE    1024   /* delka jmena souboru */

/******************************** MESSAGES ********************************/

static void LexErrorArg (const char * msg, const char * arg);
static void LexError (const char * msg);

static void * Alloc (size_t size)
{
  void * p = malloc (size);
  if (p == NULL) LexError ("Out of memory");
  memset (p, 0, size);
  return p;
}

static char * StrDup (const char * s)
{
  char * p = (char *) Alloc (strlen (s) + 1);
  strcpy (p, s);
  return p;
}

/****************************** TEXT BUFFER *******************************/

/* retezec promenne delky */

typedef struct
{
  char * s;
  int    len;
  int    cap;
}
  TEXT;

static void TextInit (TEXT * t)
{
  t->s = NULL;
  t->len = 0;
  t->cap = 0;
}

static void TextAddChr (TEXT * t, char c)
{
  if (t->len + 2 > t->cap)
  {
     t->cap = (t->cap == 0) ? 64 : 2 * t->cap;
     t->s = (char *) realloc (t->s, t->cap);
     if (t->s == NULL) LexError ("Out of memory");
  }
  t->s [t->len] = c;
  t->len ++;
  t->s [t->len] = 0;
}

static void TextAddStr (TEXT * t, const char * s)
{
  while (*s != 0)
  {
     TextAddChr (t, *s);
     s ++;
  }
}

static const char * TextStr (TEXT * t)
/* obsah (i prazdny retezec) */
{
  return (t->s == NULL) ? "" : t->s;
}

static char * TextGet (TEXT * t)
/* vrati obsah, uvolneni pameti je na volajicim */
{
  if (t->s == NULL) return StrDup ("");
  char * s = t->s;
  TextInit (t);
  return s;
}

static void TextFree (TEXT * t)
{
  free (t->s);
  TextInit (t);
}

static char LastChr (TEXT * t)
{
  return (t->len == 0) ? 0 : t->s [t->len-1];
}

/********************************* MACROS *********************************/

typedef struct MACRO_REC MACRO;

struct MACRO_REC
{
  char *  name;
  char *  body;                /* telo makra, symboly oddelene nejvyse jednou mezerou */
  int     param_cnt;           /* -1 => makro bez zavorek */
  char *  params [PARAM_MAX];
  bool    variadic;            /* posledni parametr je ... */
  bool    predefined;          /* z LexDefine, InitLex makro neruší */
  MACRO * next;
};

static MACRO * Macros = NULL;

static MACRO * FindMacro (const char * name)
{
  MACRO * m = Macros;
  while (m != NULL && strcmp (m->name, name) != 0)
     m = m->next;
  return m;
}

static void FreeMacro (MACRO * m)
{
  free (m->name);
  free (m->body);
  for (int i = 0; i < m->param_cnt; i++)
     free (m->params [i]);
  free (m);
}

static void RemoveMacros (bool all)
/* all == false => zrus jen makra definovana ve zdrojovem textu */
{
  MACRO * * p = &Macros;
  while (*p != NULL)
  {
     MACRO * m = *p;
     if (all || ! m->predefined)
     {
        *p = m->next;
        FreeMacro (m);
     }
     else
        p = &m->next;
  }
}

static void RemoveMacro (const char * name)
{
  MACRO * * p = &Macros;
  while (*p != NULL)
  {
     MACRO * m = *p;
     if (strcmp (m->name, name) == 0)
     {
        *p = m->next;
        FreeMacro (m);
        return;
     }
     p = &m->next;
  }
}

static void AddMacro (MACRO * m)
{
  RemoveMacro (m->name);
  m->next = Macros;
  Macros = m;
}

static int ParamIndex (MACRO * m, const char * name)
/* poradi parametru, -1 => neni parametr */
{
  for (int i = 0; i < m->param_cnt; i++)
     if (strcmp (m->params [i], name) == 0)
        return i;
  return -1;
}

/********************************** INPUT *********************************/

enum
{
  LEVEL_MAIN,   /* hlavni text - cte se pomoci inp.c (ch, NextChar) */
  LEVEL_FILE,   /* soubor z #include */
  LEVEL_MACRO,  /* rozvinute makro */
  LEVEL_TEXT    /* pomocny text, na konci vraci PP_END */
};

typedef struct
{
  int     kind;
  char *  text;       /* obsah (krome LEVEL_MAIN) */
  int     len;
  int     pos;
  char *  file_name;  /* LEVEL_MAIN, LEVEL_FILE */
  int     line;       /* LEVEL_FILE: cislo radky */
  bool    bol;        /* zacatek radky */
  bool    eol_sent;   /* LEVEL_FILE: na konci souboru jiz byl ohlasen konec radky */
  MACRO * macro;      /* LEVEL_MACRO: rozvijene makro (zakaz rekurze) */
}
  LEVEL;

static LEVEL Levels [LEVEL_MAX];
static int   LevelCnt = 0;

static char * MainFileName = NULL;

static char * IncludeDirs [INCL_MAX];
static int    IncludeCnt = 0;

static void PushLevel (int kind, char * text, char * file_name, MACRO * macro)
{
  if (LevelCnt >= LEVEL_MAX)
  {
     free (text);
     free (file_name);
     LexError ("Too many nested include files or macros");
  }

  LEVEL * t = &Levels [LevelCnt];
  memset (t, 0, sizeof (LEVEL));
  t->kind = kind;
  t->text = text;
  t->len = (text == NULL) ? 0 : strlen (text);
  t->pos = 0;
  t->file_name = file_name;
  t->line = 1;
  t->bol = true;
  t->eol_sent = false;
  t->macro = macro;
  LevelCnt ++;
}

static void PopLevel (void)
{
  LevelCnt --;
  LEVEL * t = &Levels [LevelCnt];
  free (t->text);
  free (t->file_name);
  t->text = NULL;
  t->file_name = NULL;
}

static LEVEL * Top (void)
{
  return &Levels [LevelCnt-1];
}

static LEVEL * CurrentFile (void)
/* nejvyssi uroven, ktera je souborem */
{
  int i = LevelCnt-1;
  while (i > 0 && Levels[i].kind != LEVEL_FILE)
     i --;
  return &Levels [i];
}

static int CurrentLine (void)
{
  LEVEL * f = CurrentFile ();
  return (f->kind == LEVEL_MAIN) ? InpLineNum : f->line;
}

const char * LexCurrentFile (void)
{
  if (LevelCnt <= 0) return NULL;
  LEVEL * f = CurrentFile ();
  return (f->kind == LEVEL_MAIN) ? NULL : f->file_name;
}

int LexCurrentLine (void)
{
  if (LevelCnt <= 0) return InpLineNum;
  return CurrentLine ();
}

static bool MacroActive (MACRO * m)
/* makro se prave rozviji */
{
  for (int i = 0; i < LevelCnt; i++)
     if (Levels[i].kind == LEVEL_MACRO && Levels[i].macro == m)
        return true;
  return false;
}

static bool AtEnd (void)
{
  LEVEL * t = Top ();
  if (t->kind == LEVEL_MAIN)
     return ch == NUL;
  else
     return t->pos >= t->len;
}

static char Cur (void)
/* aktualni znak */
{
  LEVEL * t = Top ();
  if (t->kind == LEVEL_MAIN)
     return ch;
  else
     return (t->pos < t->len) ? t->text [t->pos] : NUL;
}

static void Adv (void)
/* posun na dalsi znak */
{
  LEVEL * t = Top ();
  if (t->kind == LEVEL_MAIN)
  {
     if (ch != NUL) NextChar ();
  }
  else if (t->pos < t->len)
  {
     if (t->text [t->pos] == LF) t->line ++;
     t->pos ++;
  }
}

static void LexErrorArg (const char * msg, const char * arg)
/* chybove hlaseni, ve vlozenem souboru se pridava jmeno souboru a radka */
{
  char buf [PATH_SIZE + 256];
  buf [0] = 0;

  if (LevelCnt > 0)
  {
     LEVEL * f = CurrentFile ();
     if (f->kind == LEVEL_FILE)
        snprintf (buf, sizeof (buf), "%s:%d: ", f->file_name, f->line);
  }

  strncat (buf, msg, sizeof (buf) - strlen (buf) - 1);
  if (arg != NULL)
  {
     strncat (buf, ": ", sizeof (buf) - strlen (buf) - 1);
     strncat (buf, arg, sizeof (buf) - strlen (buf) - 1);
  }

  Error (buf);
}

static void LexError (const char * msg)
{
  LexErrorArg (msg, NULL);
}

/************************** PREPROCESSOR TOKENS ***************************/

enum
{
  PP_IDENT,
  PP_NUMBER,
  PP_STRING,
  PP_CHAR,
  PP_PUNCT,
  PP_NEWLINE,
  PP_END,     /* konec pomocneho textu (LEVEL_TEXT) */
  PP_EOF
};

typedef struct
{
  int  kind;
  char text [TOKEN_SIZE];
  int  len;
  bool space;     /* pred symbolem byla mezera */
  bool bol;       /* prvni symbol na radce souboru */
  int  line;
}
  PPTOKEN;

static PPTOKEN Back;               /* vraceny symbol (RawToken) */
static bool    BackValid = false;

static bool    SkipMode = false;   /* preskakovana cast - tolerantni k chybam */
static bool    InDirective = false;/* uvnitr direktivy - konec radky je dulezity */
static bool    PendingSpace = false; /* mezera pred nazvem makra */

static void TokAdd (PPTOKEN * t, char c)
{
  if (t->len >= TOKEN_SIZE-1) LexError ("Token too long");
  t->text [t->len] = c;
  t->len ++;
  t->text [t->len] = 0;
}

static void TokAddCur (PPTOKEN * t)
{
  TokAdd (t, Cur ());
  Adv ();
}

static void Literal (PPTOKEN * t, char quote)
/* retezec nebo znak, i s uvozovkami a escape sekvencemi */
{
  TokAddCur (t); /* uvozovka */

  for (;;)
  {
     char c = Cur ();
     if (c == quote)
     {
        TokAddCur (t);
        return;
     }
     else if (AtEnd () || c == LF)
     {
        if (SkipMode) return;
        if (quote == QUOTE2)
           LexError ("String exceeds line");
        else
           LexError ("Bad character constant");
     }
     else if (c == BACKSLASH)
     {
        Adv ();
        if (Cur () == LF)
           Adv (); /* pokracovani na dalsi radce */
        else
        {
           TokAdd (t, BACKSLASH);
           if (! AtEnd ()) TokAddCur (t);
        }
     }
     else
        TokAddCur (t);
  }
}

static void PpNumber (PPTOKEN * t)
/* cislo v sirsim smyslu (pp-number), kontrola az v NextSymbol */
{
  char last = 0;
  for (;;)
  {
     char c = Cur ();
     if (islod (c) || c == '.' ||
         ((c == '+' || c == '-') && (last == 'e' || last == 'E')))
     {
        last = c;
        TokAddCur (t);
     }
     else
        break;
  }
}

static const char * Punct2 [] =
{
  "++", "+=", "--", "-=", "->", "*=", "/=", "%=", "&&", "&=",
  "||", "|=", "^=", "==", "!=", "<=", "<<", ">=", ">>", "::", "##",
  NULL
};

static void Punctuation (PPTOKEN * t)
/* oddelovac, prvni znak jiz je v t */
{
  char first = t->text [0];
  char c = Cur ();

  for (int i = 0; Punct2 [i] != NULL; i++)
     if (Punct2[i][0] == first && Punct2[i][1] == c)
     {
        TokAddCur (t);
        if ((first == '<' || first == '>') && c == first && Cur () == '=')
           TokAddCur (t); /* <<= >>= */
        return;
     }

  if (strchr ("+-*/%&|^=!<>:#.,;()[]{}~?", first) == NULL && ! SkipMode)
     LexErrorArg ("Unknown symbol", t->text);
}

static void RawToken (PPTOKEN * t)
/* precti jeden symbol preprocesoru (bez rozvoje maker) */
{
  if (BackValid)
  {
     *t = Back;
     BackValid = false;
     return;
  }

  t->len = 0;
  t->text [0] = 0;
  t->space = PendingSpace;
  t->bol = false;
  PendingSpace = false;

  for (;;)
  {
     LEVEL * top = Top ();

     if (AtEnd ())
     {
        if (top->kind == LEVEL_MAIN)
        {
           t->kind = PP_EOF;
           t->line = CurrentLine ();
           return;
        }
        else if (top->kind == LEVEL_TEXT)
        {
           t->kind = PP_END;
           return;
        }
        else if (top->kind == LEVEL_FILE && ! top->eol_sent)
        {
           /* soubor bez konce radky na posledni radce */
           top->eol_sent = true;
           t->kind = PP_NEWLINE;
           return;
        }
        else
        {
           PopLevel (); /* konec vlozeneho souboru nebo makra */
           t->space = true;
           continue;
        }
     }

     char c = Cur ();

     if (c == LF)                                  /* END OF LINE */
     {
        Adv ();
        top->bol = true;
        t->kind = PP_NEWLINE;
        TokAdd (t, LF);
        return;
     }

     if (c <= ' ')                                 /* SPACE */
     {
        Adv ();
        t->space = true;
        continue;
     }

     if (c == BACKSLASH)                           /* LINE CONTINUATION */
     {
        Adv ();
        if (Cur () == CR) Adv ();
        if (Cur () == LF)
           Adv ();
        else if (! SkipMode)
           LexErrorArg ("Unknown symbol", "\\");
        t->space = true;
        continue;
     }

     bool bol = top->bol && (top->kind == LEVEL_MAIN || top->kind == LEVEL_FILE);
     t->line = CurrentLine ();

     if (c == '/')                                 /* COMMENT or SLASH */
     {
        Adv ();
        if (Cur () == '/')
        {
           while (! AtEnd () && Cur () != LF)
              Adv ();
           t->space = true;
           continue;
        }
        else if (Cur () == '*')
        {
           Adv ();
           char prev = ' ';
           while (! (prev == '*' && Cur () == '/'))
           {
              if (AtEnd ()) LexError ("Unterminated comment");
              prev = Cur ();
              Adv ();
           }
           Adv (); /* '/' */
           t->space = true;
           continue;
        }
        else
        {
           TokAdd (t, '/');
           t->kind = PP_PUNCT;
           Punctuation (t);
        }
     }

     else if (isletter (c))                        /* IDENTIFIER */
     {
        t->kind = PP_IDENT;
        while (islod (Cur ()))
           TokAddCur (t);
     }

     else if (isdigit (c))                         /* NUMBER */
     {
        t->kind = PP_NUMBER;
        PpNumber (t);
     }

     else if (c == '.')                            /* PERIOD, DOTS, NUMBER */
     {
        TokAddCur (t);
        if (isdigit (Cur ()))
        {
           t->kind = PP_NUMBER;
           PpNumber (t);
        }
        else if (Cur () == '.')
        {
           TokAddCur (t);
           if (Cur () == '.')
              TokAddCur (t);
           else if (! SkipMode)
              LexErrorArg ("Unknown symbol", "..");
           t->kind = PP_PUNCT;
        }
        else
           t->kind = PP_PUNCT;
     }

     else if (c == QUOTE2)                         /* STRING */
     {
        t->kind = PP_STRING;
        Literal (t, QUOTE2);
     }

     else if (c == QUOTE1)                         /* CHARACTER */
     {
        t->kind = PP_CHAR;
        Literal (t, QUOTE1);
     }

     else                                          /* SPECIAL SYMBOL */
     {
        t->kind = PP_PUNCT;
        TokAddCur (t);
        Punctuation (t);
     }

     t->bol = bol;
     top->bol = false;
     return;
  }
}

static void UnreadToken (PPTOKEN * t)
{
  Back = *t;
  BackValid = true;
}

static bool IsPunct (PPTOKEN * t, const char * s)
{
  return t->kind == PP_PUNCT && strcmp (t->text, s) == 0;
}

static bool IsEol (PPTOKEN * t)
{
  return t->kind == PP_NEWLINE || t->kind == PP_EOF || t->kind == PP_END;
}

static bool CouldMerge (char a, char b)
/* symboly by se po spojeni bez mezery mohly slit do jednoho */
{
  const char * p = "+-*/%&|^=!<>:#.";
  if ((islod (a) || a == '.') && (islod (b) || b == '.')) return true;
  if (a != 0 && b != 0 && strchr (p, a) != NULL && strchr (p, b) != NULL) return true;
  return false;
}

static void AddToken (TEXT * out, const char * s, bool space)
/* pridej symbol do textu, mezeru jen kdyz byla ve zdroji nebo je nutna */
{
  if (*s == 0) return;
  if (out->len > 0 && (space || CouldMerge (LastChr (out), s [0])))
     TextAddChr (out, ' ');
  TextAddStr (out, s);
}

/**************************** MACRO EXPANSION *****************************/

static void ExpToken (PPTOKEN * t);

typedef struct
{
  int    cnt;
  int    cap;
  char * * text;
  bool * space;
}
  TOKLIST;

static void Tokenize (const char * s, TOKLIST * list)
/* rozdel text na symboly */
{
  PPTOKEN t;

  list->cnt = 0;
  list->cap = 0;
  list->text = NULL;
  list->space = NULL;

  if (BackValid) LexError ("Internal error (Tokenize)");
  PushLevel (LEVEL_TEXT, StrDup (s), NULL, NULL);

  RawToken (&t);
  while (t.kind != PP_END)
  {
     if (list->cnt >= list->cap)
     {
        list->cap = (list->cap == 0) ? 16 : 2 * list->cap;
        list->text = (char * *) realloc (list->text, list->cap * sizeof (char *));
        list->space = (bool *) realloc (list->space, list->cap * sizeof (bool));
        if (list->text == NULL || list->space == NULL) LexError ("Out of memory");
     }
     list->text [list->cnt] = StrDup (t.text);
     list->space [list->cnt] = t.space;
     list->cnt ++;
     RawToken (&t);
  }

  PopLevel ();
}

static void FreeTokList (TOKLIST * list)
{
  for (int i = 0; i < list->cnt; i++)
     free (list->text [i]);
  free (list->text);
  free (list->space);
}

static char * ExpandText (const char * s)
/* text s rozvinutymi makry (argument makra) */
{
  PPTOKEN t;
  TEXT out;
  TextInit (&out);

  PushLevel (LEVEL_TEXT, StrDup (s), NULL, NULL);

  ExpToken (&t);
  while (t.kind != PP_END)
  {
     AddToken (&out, t.text, t.space);
     ExpToken (&t);
  }

  PopLevel ();
  return TextGet (&out);
}

static void Stringify (TEXT * out, const char * s)
/* operator # */
{
  TextAddChr (out, QUOTE2);
  while (*s != 0)
  {
     if (*s == QUOTE2 || *s == BACKSLASH)
        TextAddChr (out, BACKSLASH);
     TextAddChr (out, *s);
     s ++;
  }
  TextAddChr (out, QUOTE2);
}

static char * Substitute (MACRO * m, TEXT args [])
/* telo makra s dosazenymi argumenty, operatory # a ## */
{
  TOKLIST b;
  TEXT out;
  bool glue = false;

  Tokenize (m->body, &b);
  TextInit (&out);

  for (int i = 0; i < b.cnt; i++)
  {
     char * s = b.text [i];
     bool space = b.space [i];
     char * expanded = NULL;
     TEXT str;
     const char * val;

     TextInit (&str);

     if (strcmp (s, "##") == 0)
     {
        if (i == 0 || i == b.cnt-1)
           LexErrorArg ("'##' cannot appear at either end of macro", m->name);
        glue = true;
        continue;
     }

     if (m->param_cnt >= 0 && strcmp (s, "#") == 0)
     {
        int p = (i+1 < b.cnt) ? ParamIndex (m, b.text [i+1]) : -1;
        if (p < 0)
           LexErrorArg ("'#' is not followed by a macro parameter", m->name);
        Stringify (&str, TextStr (&args [p]));
        val = TextStr (&str);
        i ++;
     }
     else
     {
        int p = (m->param_cnt >= 0) ? ParamIndex (m, s) : -1;
        if (p < 0)
           val = s;
        else if (glue || (i+1 < b.cnt && strcmp (b.text [i+1], "##") == 0))
           val = TextStr (&args [p]); /* u ## se argument nerozvijí */
        else
           val = expanded = ExpandText (TextStr (&args [p]));
     }

     if (glue)
        TextAddStr (&out, val); /* ## - spojeni bez mezery */
     else
        AddToken (&out, val, space);
     glue = false;

     free (expanded);
     TextFree (&str);
  }

  FreeTokList (&b);
  return TextGet (&out);
}

static void PeekToken (PPTOKEN * t)
/* dalsi symbol bez rozvoje maker, mimo direktivu preskakuje konce radek */
{
  RawToken (t);
  while (t->kind == PP_NEWLINE && ! InDirective)
     RawToken (t);
}

static int CollectArgs (MACRO * m, TEXT args [])
/* precti argumenty makra, leva zavorka jiz byla prectena */
{
  PPTOKEN t;
  int cnt = 0;
  int depth = 0;
  bool space = false;

  TextInit (&args [0]);

  for (;;)
  {
     RawToken (&t);

     if (t.kind == PP_EOF || t.kind == PP_END || (t.kind == PP_NEWLINE && InDirective))
        LexErrorArg ("Unterminated macro call", m->name);

     if (t.kind == PP_NEWLINE)
     {
        space = true;
        continue;
     }

     if (IsPunct (&t, "("))
        depth ++;
     else if (IsPunct (&t, ")"))
     {
        if (depth == 0) break;
        depth --;
     }
     else if (IsPunct (&t, ",") && depth == 0 &&
              ! (m->variadic && cnt == m->param_cnt-1))
     {
        cnt ++;
        if (cnt >= PARAM_MAX) LexErrorArg ("Too many macro arguments", m->name);
        TextInit (&args [cnt]);
        space = false;
        continue;
     }

     if (args[cnt].len > 0 && (space || t.space))
        TextAddChr (&args [cnt], ' ');
     TextAddStr (&args [cnt], t.text);
     space = false;
  }

  cnt ++;

  if (m->param_cnt == 0 && cnt == 1 && args[0].len == 0)
     cnt = 0; /* F () */

  if (m->variadic && cnt == m->param_cnt-1)
  {
     TextInit (&args [cnt]); /* prazdny ... */
     cnt ++;
  }

  if (cnt != m->param_cnt)
  {
     for (int i = 0; i < cnt; i++)
        TextFree (&args [i]);
     LexErrorArg ("Wrong number of macro arguments", m->name);
  }

  return cnt;
}

static void QuoteFileName (PPTOKEN * t, const char * name)
{
  TEXT s;
  TextInit (&s);
  Stringify (&s, name);
  t->kind = PP_STRING;
  t->len = 0;
  t->text [0] = 0;
  for (int i = 0; i < s.len; i++)
     TokAdd (t, s.s [i]);
  TextFree (&s);
}

static void ExpToken (PPTOKEN * t)
/* precti symbol a rozvin makra */
{
  for (;;)
  {
     RawToken (t);

     if (t->kind != PP_IDENT || SkipMode)
        return;

     if (strcmp (t->text, "__LINE__") == 0)
     {
        t->kind = PP_NUMBER;
        snprintf (t->text, TOKEN_SIZE, "%d", t->line);
        t->len = strlen (t->text);
        return;
     }

     if (strcmp (t->text, "__FILE__") == 0)
     {
        LEVEL * f = CurrentFile ();
        QuoteFileName (t, f->file_name == NULL ? "" : f->file_name);
        return;
     }

     MACRO * m = FindMacro (t->text);
     if (m == NULL || MacroActive (m))
        return;

     char * text;

     if (m->param_cnt < 0)
     {
        text = Substitute (m, NULL);
     }
     else
     {
        PPTOKEN n;
        PeekToken (&n);
        if (! IsPunct (&n, "("))
        {
           UnreadToken (&n); /* jmeno makra s parametry bez zavorky */
           return;
        }

        TEXT args [PARAM_MAX];
        int cnt = CollectArgs (m, args);
        text = Substitute (m, args);
        for (int i = 0; i < cnt; i++)
           TextFree (&args [i]);
     }

     PushLevel (LEVEL_MACRO, text, NULL, m);
     PendingSpace = t->space;
  }
}

/******************************* DIRECTIVES *******************************/

typedef struct
{
  bool active;    /* tato vetev se preklada */
  bool taken;     /* nektera vetev jiz byla vybrana */
  bool else_seen;
}
  COND;

static COND Conds [COND_MAX];
static int  CondCnt = 0;

static bool CondActive (void)
{
  return CondCnt == 0 || Conds[CondCnt-1].active;
}

static void PushCond (bool value)
{
  if (CondCnt >= COND_MAX) LexError ("Too many nested #if directives");
  bool parent = CondActive ();
  Conds[CondCnt].active = parent && value;
  Conds[CondCnt].taken = ! parent || value; /* v neaktivni casti se zadna vetev nevybere */
  Conds[CondCnt].else_seen = false;
  CondCnt ++;
}

static void SkipLine (void)
/* preskoc zbytek direktivy */
{
  PPTOKEN t;
  bool save = SkipMode;
  SkipMode = true;
  do RawToken (&t); while (! IsEol (&t));
  SkipMode = save;
}

static void EndOfLine (void)
{
  PPTOKEN t;
  RawToken (&t);
  if (! IsEol (&t))
     LexErrorArg ("End of line expected after directive", t.text);
}

/* ---------------------------------------------------------------------- */

static void DirDefine (void)
{
  PPTOKEN t;
  TEXT body;

  RawToken (&t);
  if (t.kind != PP_IDENT) LexError ("Macro name expected");

  MACRO * m = (MACRO *) Alloc (sizeof (MACRO));
  m->name = StrDup (t.text);
  m->param_cnt = -1;
  m->body = NULL;

  if (Cur () == '(') /* zavorka hned za jmenem => makro s parametry */
  {
     RawToken (&t); /* ( */
     m->param_cnt = 0;
     RawToken (&t);
     if (! IsPunct (&t, ")"))
        for (;;)
        {
           if (m->param_cnt >= PARAM_MAX) LexErrorArg ("Too many macro parameters", m->name);

           if (IsPunct (&t, "..."))
           {
              m->params [m->param_cnt ++] = StrDup ("__VA_ARGS__");
              m->variadic = true;
              RawToken (&t);
           }
           else if (t.kind == PP_IDENT)
           {
              if (ParamIndex (m, t.text) >= 0) LexErrorArg ("Duplicate macro parameter", t.text);
              m->params [m->param_cnt ++] = StrDup (t.text);
              RawToken (&t);
              if (IsPunct (&t, "...")) /* GNU: jmeno... */
              {
                 m->variadic = true;
                 RawToken (&t);
              }
           }
           else
              LexErrorArg ("Macro parameter expected", m->name);

           if (IsPunct (&t, ")"))
              break;
           if (! IsPunct (&t, ",") || m->variadic)
              LexErrorArg ("')' expected in macro parameters", m->name);
           RawToken (&t);
        }
     RawToken (&t);
  }
  else
     RawToken (&t);

  /* telo makra */
  TextInit (&body);
  while (! IsEol (&t))
  {
     if (body.len > 0 && t.space)
        TextAddChr (&body, ' ');
     TextAddStr (&body, t.text);
     RawToken (&t);
  }
  m->body = TextGet (&body);

  AddMacro (m);
}

static void DirUndef (void)
{
  PPTOKEN t;
  RawToken (&t);
  if (t.kind != PP_IDENT) LexError ("Macro name expected");
  RemoveMacro (t.text);
  EndOfLine ();
}

/* ---------------------------------------------------------------------- */

static char * ReadFile (const char * name)
/* obsah souboru, NULL => soubor neexistuje */
{
  FILE * f = fopen (name, "rb");
  if (f == NULL) return NULL;

  TEXT s;
  TextInit (&s);
  int c;
  while ((c = fgetc (f)) != EOF)
     if (c != 0) TextAddChr (&s, (char) c);
  fclose (f);

  return TextGet (&s);
}

static void JoinPath (char * buf, const char * dir, const char * name)
{
  if (name [0] == '/' || dir == NULL || dir [0] == 0)
     snprintf (buf, PATH_SIZE, "%s", name);
  else if (dir [strlen (dir) - 1] == '/')
     snprintf (buf, PATH_SIZE, "%s%s", dir, name);
  else
     snprintf (buf, PATH_SIZE, "%s/%s", dir, name);
}

static void FileDir (char * buf, const char * file_name)
/* adresar souboru */
{
  buf [0] = 0;
  if (file_name == NULL) return;
  const char * slash = strrchr (file_name, '/');
  if (slash == NULL) return;
  int len = slash - file_name + 1;
  if (len >= PATH_SIZE) len = PATH_SIZE - 1;
  memcpy (buf, file_name, len);
  buf [len] = 0;
}

static bool TryInclude (const char * dir, const char * name)
{
  char path [PATH_SIZE];
  JoinPath (path, dir, name);
  char * text = ReadFile (path);
  if (text == NULL) return false;
  PushLevel (LEVEL_FILE, text, StrDup (path), NULL);
  return true;
}

static void DirInclude (void)
{
  PPTOKEN t;
  TEXT name;
  bool system;

  TextInit (&name);
  RawToken (&t);

  if (t.kind == PP_STRING)
  {
     system = false;
     t.text [t.len-1] = 0;
     TextAddStr (&name, t.text + 1);
  }
  else if (IsPunct (&t, "<"))
  {
     system = true;
     RawToken (&t);
     while (! IsPunct (&t, ">"))
     {
        if (IsEol (&t)) LexError ("'>' expected in #include");
        if (name.len > 0 && t.space) TextAddChr (&name, ' ');
        TextAddStr (&name, t.text);
        RawToken (&t);
     }
  }
  else
     LexError ("File name expected after #include");

  EndOfLine ();

  bool found = false;

  if (! system)
  {
     char dir [PATH_SIZE];
     FileDir (dir, CurrentFile ()->file_name);
     found = TryInclude (dir, TextStr (&name));
  }

  for (int i = 0; i < IncludeCnt && ! found; i++)
     found = TryInclude (IncludeDirs [i], TextStr (&name));

  if (! found && ! system)
  {
     char msg [PATH_SIZE];
     snprintf (msg, sizeof (msg), "%s", TextStr (&name));
     TextFree (&name);
     LexErrorArg ("Cannot open include file", msg);
  }

  /* nenalezene systemove soubory (<stdio.h>, ...) se ignoruji */

  TextFree (&name);
}

/****************************** EXPRESSIONS *******************************/

/* vyrazy v #if a #elif */

static PPTOKEN ET;  /* aktualni symbol vyrazu */

static void ENext (void)
{
  ExpToken (&ET);
}

static long ECond (bool eval);

static char DecodeChar (const char * * p);

static long ENumber (const char * s)
{
  char buf [TOKEN_SIZE];
  strcpy (buf, s);

  int len = strlen (buf);
  while (len > 0 && strchr ("uUlL", buf [len-1]) != NULL)
     len --;
  buf [len] = 0;

  char * end;
  long v = (long) strtoul (buf, &end, 0);
  if (len == 0 || *end != 0) LexErrorArg ("Bad number in #if", s);
  return v;
}

static long EPrimary (bool eval)
{
  long v = 0;

  if (ET.kind == PP_NUMBER)
  {
     v = ENumber (ET.text);
     ENext ();
  }
  else if (ET.kind == PP_CHAR)
  {
     const char * p = ET.text + 1;
     v = DecodeChar (&p);
     ENext ();
  }
  else if (ET.kind == PP_IDENT)
  {
     if (strcmp (ET.text, "defined") == 0)
     {
        bool par = false;
        RawToken (&ET); /* bez rozvoje maker */
        if (IsPunct (&ET, "("))
        {
           par = true;
           RawToken (&ET);
        }
        if (ET.kind != PP_IDENT) LexError ("Identifier expected after defined");
        v = (FindMacro (ET.text) != NULL ||
             strcmp (ET.text, "__LINE__") == 0 ||
             strcmp (ET.text, "__FILE__") == 0);
        if (par)
        {
           RawToken (&ET);
           if (! IsPunct (&ET, ")")) LexError ("')' expected after defined");
        }
     }
     else if (strcmp (ET.text, "true") == 0)
        v = 1;
     else
        v = 0; /* nedefinovany identifikator */
     ENext ();
  }
  else if (IsPunct (&ET, "("))
  {
     ENext ();
     v = ECond (eval);
     if (! IsPunct (&ET, ")")) LexError ("')' expected in #if expression");
     ENext ();
  }
  else if (IsPunct (&ET, "!")) { ENext (); v = ! EPrimary (eval); }
  else if (IsPunct (&ET, "~")) { ENext (); v = ~ EPrimary (eval); }
  else if (IsPunct (&ET, "-")) { ENext (); v = - EPrimary (eval); }
  else if (IsPunct (&ET, "+")) { ENext (); v = EPrimary (eval); }
  else
     LexErrorArg ("Bad expression in #if", IsEol (&ET) ? "end of line" : ET.text);

  return v;
}

static int EPriority (PPTOKEN * t)
{
  static const char * ops [] =
  {
     "*", "/", "%", "+", "-", "<<", ">>", "<", "<=", ">", ">=",
     "==", "!=", "&", "^", "|", "&&", "||", NULL
  };
  static const int prio [] =
  {
     10, 10, 10, 9, 9, 8, 8, 7, 7, 7, 7,
     6, 6, 5, 4, 3, 2, 1
  };

  if (t->kind != PP_PUNCT) return 0;
  for (int i = 0; ops [i] != NULL; i++)
     if (strcmp (t->text, ops [i]) == 0)
        return prio [i];
  return 0;
}

static long EBinary (int min_prio, bool eval)
{
  long a = EPrimary (eval);

  for (;;)
  {
     int p = EPriority (&ET);
     if (p == 0 || p < min_prio) return a;

     char op [4];
     strcpy (op, ET.text);
     ENext ();

     if (strcmp (op, "&&") == 0)
     {
        long b = EBinary (p+1, eval && a);
        a = a && b;
     }
     else if (strcmp (op, "||") == 0)
     {
        long b = EBinary (p+1, eval && ! a);
        a = a || b;
     }
     else
     {
        long b = EBinary (p+1, eval);

        if      (strcmp (op, "*")  == 0) a = a * b;
        else if (strcmp (op, "+")  == 0) a = a + b;
        else if (strcmp (op, "-")  == 0) a = a - b;
        else if (strcmp (op, "<<") == 0) a = a << b;
        else if (strcmp (op, ">>") == 0) a = a >> b;
        else if (strcmp (op, "<")  == 0) a = a < b;
        else if (strcmp (op, "<=") == 0) a = a <= b;
        else if (strcmp (op, ">")  == 0) a = a > b;
        else if (strcmp (op, ">=") == 0) a = a >= b;
        else if (strcmp (op, "==") == 0) a = a == b;
        else if (strcmp (op, "!=") == 0) a = a != b;
        else if (strcmp (op, "&")  == 0) a = a & b;
        else if (strcmp (op, "^")  == 0) a = a ^ b;
        else if (strcmp (op, "|")  == 0) a = a | b;
        else /* / % */
        {
           if (b == 0)
           {
              if (eval) LexError ("Division by zero in #if");
              a = 0;
           }
           else if (strcmp (op, "/") == 0)
              a = a / b;
           else
              a = a % b;
        }
     }
  }
}

static long ECond (bool eval)
{
  long c = EBinary (1, eval);

  if (IsPunct (&ET, "?"))
  {
     ENext ();
     long x = ECond (eval && c);
     if (! IsPunct (&ET, ":")) LexError ("':' expected in #if expression");
     ENext ();
     long y = ECond (eval && ! c);
     c = c ? x : y;
  }

  return c;
}

static bool IfExpression (void)
/* vyhodnot vyraz az do konce radky */
{
  bool save = SkipMode;
  SkipMode = false;

  ENext ();
  long v = ECond (true);
  if (! IsEol (&ET))
     LexErrorArg ("End of line expected after #if expression", ET.text);

  SkipMode = save;
  return v != 0;
}

/* ---------------------------------------------------------------------- */

static bool IfdefSymbol (bool active)
{
  PPTOKEN t;
  RawToken (&t);
  if (t.kind != PP_IDENT)
  {
     if (active) LexError ("Macro name expected");
     if (! IsEol (&t)) SkipLine ();
     return false;
  }
  bool result = FindMacro (t.text) != NULL;
  if (active) EndOfLine (); else SkipLine ();
  return result;
}

static void Directive (void)
/* '#' na zacatku radky jiz byl precten */
{
  PPTOKEN t;
  bool active = CondActive ();

  InDirective = true;
  SkipMode = ! active;

  RawToken (&t);

  if (IsEol (&t))
     ; /* prazdna direktiva */

  else if (t.kind != PP_IDENT)
  {
     if (active) LexErrorArg ("Directive name expected", t.text);
     SkipLine ();
  }

  else if (strcmp (t.text, "if") == 0)
  {
     bool value = false;
     if (active)
        value = IfExpression ();
     else
        SkipLine ();
     PushCond (value);
  }

  else if (strcmp (t.text, "ifdef") == 0)
     PushCond (IfdefSymbol (active));

  else if (strcmp (t.text, "ifndef") == 0)
     PushCond (! IfdefSymbol (active));

  else if (strcmp (t.text, "elif") == 0)
  {
     if (CondCnt == 0) LexError ("#elif without #if");
     COND * c = &Conds [CondCnt-1];
     if (c->else_seen) LexError ("#elif after #else");
     if (c->taken)
     {
        c->active = false;
        SkipLine ();
     }
     else
     {
        c->active = IfExpression ();
        c->taken = c->active;
     }
  }

  else if (strcmp (t.text, "else") == 0)
  {
     if (CondCnt == 0) LexError ("#else without #if");
     COND * c = &Conds [CondCnt-1];
     if (c->else_seen) LexError ("#else after #else");
     c->else_seen = true;
     c->active = ! c->taken;
     c->taken = true;
     SkipLine ();
  }

  else if (strcmp (t.text, "endif") == 0)
  {
     if (CondCnt == 0) LexError ("#endif without #if");
     CondCnt --;
     SkipLine ();
  }

  else if (! active)
     SkipLine ();

  else if (strcmp (t.text, "define") == 0)
     DirDefine ();

  else if (strcmp (t.text, "undef") == 0)
     DirUndef ();

  else if (strcmp (t.text, "include") == 0)
     DirInclude ();

  else if (strcmp (t.text, "error") == 0)
  {
     TEXT msg;
     TextInit (&msg);
     RawToken (&t);
     while (! IsEol (&t))
     {
        AddToken (&msg, t.text, t.space);
        RawToken (&t);
     }
     char buf [256];
     snprintf (buf, sizeof (buf), "%s", TextStr (&msg));
     TextFree (&msg);
     LexErrorArg ("#error", buf);
  }

  else if (strcmp (t.text, "pragma") == 0 ||
           strcmp (t.text, "line") == 0 ||
           strcmp (t.text, "warning") == 0)
     SkipLine ();

  else
     LexErrorArg ("Unknown directive", t.text);

  InDirective = false;
  SkipMode = false;
}

static void DirToken (PPTOKEN * t)
/* symbol po zpracovani direktiv a podminenych prekladu */
{
  for (;;)
  {
     bool active = CondActive ();
     SkipMode = ! active;

     if (active)
        ExpToken (t);
     else
        RawToken (t);

     SkipMode = false;

     if (t->bol && IsPunct (t, "#"))
     {
        Directive ();
        continue;
     }

     if (t->kind == PP_EOF)
     {
        if (CondCnt > 0) LexError ("Unterminated #if");
        return;
     }

     if (! active || t->kind == PP_NEWLINE)
        continue;

     return;
  }
}

/********************************** INIT **********************************/

static PPTOKEN Ahead;              /* symbol prectenty dopredu (spojovani retezcu) */
static bool    AheadValid = false;

void LexFileName (const char * name)
{
  free (MainFileName);
  MainFileName = (name == NULL) ? NULL : StrDup (name);
}

void LexIncludeDir (const char * dir)
{
  if (IncludeCnt >= INCL_MAX) LexError ("Too many include directories");
  IncludeDirs [IncludeCnt ++] = StrDup (dir);
}

void LexDefine (const char * name, const char * value)
{
  MACRO * m = (MACRO *) Alloc (sizeof (MACRO));
  m->name = StrDup (name);
  m->body = StrDup (value == NULL ? "1" : value);
  m->param_cnt = -1;
  m->predefined = true;
  AddMacro (m);
}

void LexUndefine (const char * name)
{
  RemoveMacro (name);
}

void LexClear (void)
{
  RemoveMacros (true);
  while (IncludeCnt > 0)
     free (IncludeDirs [-- IncludeCnt]);
}

void InitLex (void)
{
  /* musi byt zavolano az po OpenInp () */

  while (LevelCnt > 0)
     PopLevel ();
  PushLevel (LEVEL_MAIN, NULL, MainFileName == NULL ? NULL : StrDup (MainFileName), NULL);

  RemoveMacros (false); /* makra z predchoziho prekladu */

  BackValid = false;
  AheadValid = false;
  SkipMode = false;
  InDirective = false;
  PendingSpace = false;
  CondCnt = 0;

  sy = (SYMBOL) 0;
  CLR_ARR (IdentVal);
  CLR_ARR (NumVal);
  CLR_ARR (StrVal);
  ChrVal = 0;
  l_suffix = false;
  u_suffix = false;
  f_suffix = false;

  NextSymbol ();  /* read first symbol */
}

/**************************** LEXICAL ANALYSIS ****************************/

/* keyword table */

typedef struct
{
  char t [17];
  SYMBOL s;
}
  KEYWORD_REC;

#define KEYWORD_MAX 50
static KEYWORD_REC KeywordTab [KEYWORD_MAX] = /* serazeno podle abecedy */
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

/* oddelovace */

typedef struct
{
  char t [6];
  SYMBOL s;
}
  SPECREC;

#define SPECMAX 53
static SPECREC SpecTab [SPECMAX] =
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

/* ---------------------------------------------------------------------- */

static void Identifier (const char * s)
{
  int a, b, c, cmp;

  if (strlen (s) >= IDENT_SIZE) LexError ("Identifier too long");
  strcpy (IdentVal, s);
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

  /* NULL, pokud neni definovano jako makro (stejne jako v lex.c) */
  if (strcmp (IdentVal, "NULL") == 0)
     sy = NULLPTR_;
}

/* ---------------------------------------------------------------------- */

static const char * NP; /* pozice ve zpracovavanem cisle */

static void Digits (void)
/* digit <digit> */
{
  if (!isdigit(*NP)) LexError ("Digit expected");
  while (isdigit(*NP)) NP++;
}

static void Exponent (void)
{
  if (*NP=='e' || *NP=='E')
  {
     sy = FLT;
     NP++;                              /* e | E */
     if (*NP=='+' || *NP=='-')
        NP++;                           /* + | - */
     Digits ();                         /* digit <digit> */
  }
}

static void FloatSuffix (void)
{
  if (*NP=='f' || *NP=='F')
  {
     NP++;
     f_suffix = true;
  }
  else if (*NP=='l' || *NP=='L')
  {
     NP++;
     l_suffix = true;
  }
}

static void IntSuffix (void)
{
  if (*NP=='l' || *NP=='L')
  {
     NP++;
     l_suffix = true;
     if (*NP=='l' || *NP=='L') NP++;   /* LL = L (long long = long) */
     if (*NP=='u' || *NP=='U')
     {
        NP++;
        u_suffix = true;
     }
  }
  else if (*NP=='u' || *NP=='U')
  {
     NP++;
     u_suffix = true;
     if (*NP=='l' || *NP=='L')
     {
        NP++;
        l_suffix = true;
        if (*NP=='l' || *NP=='L') NP++;   /* ULL */
     }
  }
}

static void Number (const char * s)
{
  if (strlen (s) >= NUM_SIZE) LexError ("Number is too long");
  strcpy (NumVal, s);

  sy = NUM;
  l_suffix = false;
  u_suffix = false;
  f_suffix = false;
  NP = s;

  if (*NP == '.')                       /* cislo zacinajici teckou */
  {
     sy = FLT;
     NP++;
     Digits ();
     Exponent ();
     FloatSuffix ();
  }
  else if (NP[0]=='0' && (NP[1]=='x' || NP[1]=='X')) /* Hexadecimal number */
  {
     NP += 2;
     if (!isxdigit (*NP)) LexError ("Hexadecimal digit expected");
     while (isxdigit (*NP)) NP++;
     IntSuffix ();
  }
  else                                  /* Decimal or octal number */
  {
     while (isdigit (*NP)) NP++;        /* <digit> */

     if (*NP=='.')
     {
        sy = FLT;
        NP++;                           /* '.' */
        if (isdigit (*NP)) Digits ();   /* digit <digit> */
     }

     Exponent ();                       /* e|E  +|- digit <digit> */

     if (sy==FLT)
        FloatSuffix ();                 /* f | F | l | L */
     else
     {
        /* kontrola osmickovych cisel */
        if (s[0] == '0')
           for (const char * p = s+1; isdigit (*p); p++)
              if (*p > '7') LexError ("Bad octal number");

        IntSuffix ();                   /* pripony */
     }
  }

  if (*NP != 0) LexErrorArg ("Bad number", s);
}

/* ---------------------------------------------------------------------- */

static char DecodeChar (const char * * p)
/* read one C-style character */
{
  int  n, d;
  int  cnt;
  char last;
  const char * s = *p;

  if (*s!=BACKSLASH)                  /* simple character */
  {
     last = *s;
     *p = s+1;
     return last;
  }

  s++;                                /* skip backslash */

  if (isoctal (*s))                   /* octal */
  {
     n = 0;
     cnt = 1;
     while (isoctal (*s) && cnt<=3)
     {
        n = n*8 + *s-'0';
        cnt++;
        s++;
     }
     *p = s;
     return (char) n;
  }

  if (*s=='x' || *s=='X')             /* hex */
  {
     s++;
     n = 0;
     while (isxdigit (*s))
     {
        if (*s >= 'A' && *s <= 'F')
           d = *s - 'A' + 10;
        else if (*s >= 'a' && *s <= 'f')
           d = *s - 'a' + 10;
        else
           d = *s - '0';
        n = n*16+d;
        s++;
     }
     *p = s;
     return (char) n;
  }

  last = *s;
  if (last != 0) s++;
  *p = s;

  switch (last)                       /* other */
  {
     case 'a': return '\a';
     case 'b': return '\b';
     case 'f': return '\f';
     case 'n': return '\n';
     case 'r': return '\r';
     case 't': return '\t';
     case 'v': return '\v';
     default:  return last;           /* ' " \ ? */
  }
}

static int StrLen; /* delka retezce v StrVal */

static void AppendString (const char * s)
/* pridej obsah retezcove konstanty (s uvozovkami) do StrVal */
{
  const char * p = s+1;
  while (*p != QUOTE2 && *p != 0)
  {
     if (StrLen>=STR_SIZE-1) LexError ("String too long");
     StrVal[StrLen] = DecodeChar (&p);
     StrLen++;
  }
  StrVal[StrLen] = 0;
}

static void GetToken (PPTOKEN * t)
{
  if (AheadValid)
  {
     *t = Ahead;
     AheadValid = false;
  }
  else
     DirToken (t);
}

static void StringLiteral (PPTOKEN * t)
{
  StrLen = 0;
  AppendString (t->text);

  /* sousedni retezce se spoji: "abc" "def" */
  for (;;)
  {
     GetToken (&Ahead);
     if (Ahead.kind != PP_STRING)
     {
        AheadValid = true;
        break;
     }
     AppendString (Ahead.text);
  }

  sy = STR;
}

static void CharLiteral (const char * s)
{
  const char * p = s+1;
  if (*p==QUOTE1 || *p==0)
     LexError ("Bad character constant");
  ChrVal = DecodeChar (&p);
  if (*p!=QUOTE1)
     LexError ("Bad character constant");
  sy = CHR;
}

static void Punctuator (const char * s)
{
  for (int i=0; i<SPECMAX; i++)
     if (strcmp (s, SpecTab[i].t) == 0 && SpecTab[i].s != IDENT)
     {
        sy = SpecTab[i].s;
        return;
     }
  LexErrorArg ("Unknown symbol", s);
}

static void RawNextSymbol (void);

/* symbol; X::jmeno s prostorem jmen X => jmeno (decl.c - NamespaceQual) */
void NextSymbol (void)
{
  RawNextSymbol ();
  if (sy == IDENT) NamespaceQual ();
}

static void RawNextSymbol (void)
{
  PPTOKEN t;

  if (ReplaySymbol != NULL)   /* prehravani ulozenych symbolu (decl.c) */
  {
     ReplaySymbol ();
     return;
  }

  GetToken (&t);

  switch (t.kind)
  {
     case PP_EOF:    sy = EOS; break;
     case PP_IDENT:  Identifier (t.text); break;
     case PP_NUMBER: Number (t.text); break;
     case PP_STRING: StringLiteral (&t); break;
     case PP_CHAR:   CharLiteral (t.text); break;
     case PP_PUNCT:  Punctuator (t.text); break;
     default:        LexError ("Internal error (NextSymbol)"); break;
  }
}

/************************** CHECK CURRENT SYMBOL **************************/

static void SymToStr (SYMBOL par, STR_TYP s)
/* prevod symbolu na retezec znaku */
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
/* zobraz symbol na vystupu */
{
   STR_TYP txt;
   SymToStr (par, txt);
   PutStr (txt);
}

void PutCurrentSymbol (void)
/* zobraz prave zpracovavany symbol na vystupu */
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

  /* ohlaseni chyby pokud sy <> par */
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
