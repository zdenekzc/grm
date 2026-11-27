/* LEXER.H */

/**************************************************************************/
/*                                                                        */
/*               Lexical Analysis with Preprocessor                       */
/*                                                                        */
/**************************************************************************/

/*
   Alternativa k lex.c - stejne rozhrani (lex.h: sy, IdentVal, NumVal, ...,
   InitLex, NextSymbol, CheckSymbol, ...), navic zpracovava direktivy
   preprocesoru:

      #define, #undef               makra bez parametru i s parametry,
                                    operatory # a ##, __VA_ARGS__
      #if, #ifdef, #ifndef,
      #elif, #else, #endif          podminene preklady, vyrazy s defined
      #include "soubor"             hleda v adresari zdrojoveho souboru
                                    a v adresarich z LexIncludeDir
      #include <soubor>             jen v adresarich z LexIncludeDir,
                                    nenalezene soubory se ignoruji
                                    (napr. <stdio.h>, jako v lex.c)
      #error                        chyba prekladu
      #pragma, #line, #warning      ignoruji se

      __LINE__, __FILE__            preddefinovana makra

   Do programu se prilinkuje bud lex.c, nebo lexer.c.
*/

#ifndef LEXER_H
#define LEXER_H

#include <stddef.h> /* size_t (v lex.h) */
#include "lex.h"

#ifdef __cplusplus
extern "C" {   /* front-end je v cistem C (decl.c, ...); g++ (instr.cc, test_instr.cc) */
#endif

void LexFileName   (const char * name);   /* jmeno zdrojoveho souboru (pro #include "..." a __FILE__) */
void LexIncludeDir (const char * dir);    /* pridej adresar pro #include (jako -I) */
void LexDefine     (const char * name, const char * value); /* makro bez parametru (jako -D) */
void LexUndefine   (const char * name);
void LexClear      (void);                /* zrus adresare a makra z LexDefine */

/* LexCurrentFile, LexCurrentLine - viz lex.h */

#ifdef __cplusplus
}
#endif

#endif
