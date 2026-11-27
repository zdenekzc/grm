
/* LEX.H */

/**************************************************************************/
/*                                                                        */
/*                            Lexical Analysis                            */
/*                                                                        */
/**************************************************************************/

#ifndef LEX_H
#define LEX_H

#include <stddef.h>   /* size_t */
#ifndef __cplusplus
#include <stdbool.h>  /* bool for C */
#endif

#ifdef __cplusplus
extern "C" {   /* front-end is plain C (decl.c, ...); g++ (instr.cc, test_instr.cc) */
#endif

#define QUOTE1    '\''
#define QUOTE2    '\"'
#define BACKSLASH '\\'

#define IDENT_SIZE 80
typedef char IDENT_TYP [IDENT_SIZE]; /* identifiers */

#define STR_SIZE 256
typedef char STR_TYP [STR_SIZE]; /* character strings */

#define NUM_SIZE 32
typedef char NUM_TYP [NUM_SIZE]; /* numeric constants */

enum SYMBOL
{
    AUTO_,
    BREAK_,
    CASE_,
    CHAR_,
    CONST_,
    CONTINUE_,
    DEFAULT_,
    DO_,
    DOUBLE_,
    ELSE_,
    ENUM_,
    EXTERN_,
    FLOAT_,
    FOR_,
    GOTO_,
    IF_,
    INT_,
    LONG_,
    REGISTER_,
    RETURN_,
    SHORT_,
    SIGNED_,
    SIZEOF_,
    STATIC_,
    STRUCT_,
    SWITCH_,
    TYPEDEF_,
    UNION_,
    UNSIGNED_,
    VOID_,
    VOLATILE_,
    WHILE_,

    /* C++ */
    BOOL_,
    FALSE_,
    INLINE_,
    NEW_,
    NULLPTR_,
    TRUE_,
    CLASS_,
    PRIVATE_,
    PROTECTED_,
    PUBLIC_,
    THIS_,
    VIRTUAL_,
    STATIC_CAST_,       /* static_cast <T> (e), (T) e - cast node */
    REINTERPRET_CAST_,
    CONST_CAST_,
    DYNAMIC_CAST_,
    FRIEND_,
    DELETE_,

    PLUS,         /* +  */
    MINUS,        /* -   */
    ASTERISK,     /* *   */
    SLASH,        /* /   */
    PERIOD,       /* .   */
    COMMA,        /* ,   */
    COLON,        /* :   */
    SEMICOLON,    /* ;   */
    EQUAL,        /* ==  */
    LESS,         /* <   */
    GREATER,      /* >   */
    UNEQUAL,      /* !=  */
    LESSEQUAL,    /* <=  */
    GREATEREQUAL, /* >=  */
    ARROW,        /* ->  */
    ASSIGN,       /* =   */
    LPAR,         /* (   */
    RPAR,         /* )   */
    LBRACK,       /* [   */
    RBRACK,       /* ]   */

    LBRACE,       /* {   */
    RBRACE,       /* }   */
    TILDA,        /* ~   */
    PERCENT,      /* %   */
    CARET,        /* ^   */
    AND,          /* &   */
    BAR,          /* |   */
    QUESTION,     /* ?   */

    DPLUS,        /* ++  */
    DMINUS,       /* --  */
    DCOLON,       /* ::  */
    DOTS,         /* ... */

    SHL,          /* <<  */
    SHR,          /* >>  */
    LOGNOT,       /* !   */
    LOGAND,       /* &&  */
    LOGOR,        /* ||  */

    MULASSIGN,    /* *=  */
    DIVASSIGN,    /* /=  */
    MODASSIGN,    /* %=  */
    ADDASSIGN,    /* +=  */
    SUBASSIGN,    /* -=  */
    SHLASSIGN,    /* <<= */
    SHRASSIGN,    /* >>= */
    ANDASSIGN,    /* &=  */
    ORASSIGN,     /* |=  */
    XORASSIGN,    /* ^=  */

    IDENT,        /* identifier */
    NUM,          /* number */
    FLT,          /* floating point number */
    STR,          /* string    "" */
    CHR,          /* character '' */

    /* expressions */

    FCE,          /* function call */
    ADR,          /* unary & */
    DEREF,        /* unary * */
    UNARYPLUS,    /* unary + */
    UNARYMINUS,   /* unary - */
    UNARYNOT,     /* unary ~ */

    /* statements */

    SIM,          /* simple statement: expression or null */
    LAB,          /* label */
    DECL,         /* declaration */

    EOS           /* end of source */
};

#ifndef __cplusplus
typedef enum SYMBOL SYMBOL;  /* C: enum tags are not implicit types */
#endif

#define SYMBOL_MAX EOS /* last symbol */

#define OR       BAR
#define XOR      CARET
#define NOT      TILDA
#define MOD      PERCENT

extern SYMBOL    sy;           /* symbol being processed */

extern IDENT_TYP IdentVal;     /* identifier */
extern NUM_TYP   NumVal;       /* number (as a sequence of characters) */
extern STR_TYP   StrVal;       /* string (without quotes) */
extern char      ChrVal;       /* character */

extern bool      l_suffix;     /* suffixes at the end of a number */
extern bool      u_suffix;
extern bool      f_suffix;     

/* replay of stored symbols (decl.c: method bodies inside a class are processed
   only at the end of the class); != NULL => NextSymbol calls this function instead of reading input */
extern void (*ReplaySymbol) (void);
void NamespaceQual (void);   /* decl.c: X::name => name (namespace X) */

/* position for error messages: current (included) file and line in it;
   LexCurrentFile returns NULL when the main text is being read (lex.c always NULL) */
const char * LexCurrentFile (void);
int          LexCurrentLine (void);

/* position of the symbol being replayed (decl.c - method bodies inside a class) */
extern const char * ReplayFile;
extern int          ReplayLine;

void InitLex     (void);       /* initialization - reads the first symbol */
void NextSymbol  (void);       /* read next symbol */
void CheckSymbol (SYMBOL par); /* check whether the given symbol is next in the input */

void PutSymbol (SYMBOL par);   /* show symbol in the output */
void PutCurrentSymbol (void);  /* show the symbol being processed in the output */

/******************************* UTILITIES ********************************/

#define CLR_ARR(x) memset (x, 0, sizeof (x));
#define CLR_REC(x) memset (&(x), 0, sizeof (x));

void strmov (char * a, size_t size, char * b);
void stradd (char * a, size_t size, char * b);

#ifdef __cplusplus
}
#endif

#endif
