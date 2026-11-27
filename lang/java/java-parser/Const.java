
package cacao.src;

public class Const
{

  public static final int IDENT  = 1;
  public static final int NUMBER = 2;
  public static final int FLT    = 3;
  public static final int STR    = 4;
  public static final int CHR    = 5;

  /* ------------------------------------------------------------- */

  private static final int fs = 20;

  public static final int LPAR      = fs + 0; // '('
  public static final int RPAR      = fs + 1; // ')'
  public static final int LBRACE    = fs + 2; // '{'
  public static final int RBRACE    = fs + 3; // '}'
  public static final int LBRACK    = fs + 4; // '['
  public static final int RBRACK    = fs + 5; // ']'
  public static final int SEMICOLON = fs + 6; // ';'
  public static final int COMMA     = fs + 7; // ','
  public static final int PERIOD    = fs + 8; // '.'

  public static final int ASSIGN   = fs +  9; // '='
  public static final int LESS     = fs + 10; // '<'
  public static final int GREATER  = fs + 11; // '>'
  public static final int LOGNOT   = fs + 12; // '!'
  public static final int BITNOT   = fs + 13; // '~'
  public static final int QUESTION = fs + 14; // '?'
  public static final int COLON    = fs + 15; // ':'

  public static final int EQUAL        = fs + 16; // '=='
  public static final int LESSEQUAL    = fs + 17; // '<='
  public static final int GREATEREQUAL = fs + 18; // '>='
  public static final int NOTEQUAL     = fs + 19; // '!='
  public static final int LOGAND       = fs + 20; // '&&'
  public static final int LOGOR        = fs + 21; // '||'
  public static final int DPLUS        = fs + 22; // '++'
  public static final int DMINUS       = fs + 23; // '--'

  public static final int PLUS  = fs + 24; // '+'
  public static final int MINUS = fs + 25; // '-'
  public static final int MUL   = fs + 26; // '*'
  public static final int DIV   = fs + 27; // '/'
  public static final int AND   = fs + 28; // '&'
  public static final int OR    = fs + 29; // '|'
  public static final int XOR   = fs + 30; // '^'
  public static final int MOD   = fs + 31; // '%'
  public static final int SHL   = fs + 32; // '<<'
  public static final int SAR   = fs + 33; // '>>'
  public static final int SHR   = fs + 34; // '>>>'

  public static final int ADDASSIGN = fs + 35; // '+='
  public static final int SUBASSIGN = fs + 36; // '-='
  public static final int MULASSIGN = fs + 37; // '*='
  public static final int DIVASSIGN = fs + 38; // '/='
  public static final int ANDASSIGN = fs + 39; // '&='
  public static final int ORASSIGN  = fs + 40; // '|='
  public static final int XORASSIGN = fs + 41; // '^='
  public static final int MODASSIGN = fs + 42; // '%='
  public static final int SHLASSIGN = fs + 43; // '<<='
  public static final int SARASSIGN = fs + 44; // '>>='
  public static final int SHRASSIGN = fs + 45; // '>>>='

  /* ------------------------------------------------------------- */

  public static final String keywords [] =
  { "abstract",     "boolean",      "break",        "byte",
    "case",         "catch",        "char",         "class",
    "const",        "continue",     "default",      "do",
    "double",       "else",         "extends",      "false",
    "final",        "finally",      "float",        "for",
    "goto",         "if",           "implements",   "import",
    "instanceof",   "int",          "interface",    "long",
    "native",       "new",          "null",         "package",
    "private",      "protected",    "public",       "return",
    "short",        "static",       "super",        "switch",
    "synchronized", "this",         "throw",        "throws",
    "transient",    "true",         "try",          "void",
    "volatile",     "while" };

  private static final int fk = fs + 50;

  public static final int ABSTRACT = fk + 0;
  public static final int BOOLEAN = fk + 1;
  public static final int BREAK = fk + 2;
  public static final int BYTE = fk + 3;
  public static final int CASE = fk + 4;
  public static final int CATCH = fk + 5;
  public static final int CHAR = fk + 6;
  public static final int CLASS = fk + 7;
  public static final int CONST = fk + 8;
  public static final int CONTINUE = fk + 9;
  public static final int DEFAULT = fk + 10;
  public static final int DO = fk + 11;
  public static final int DOUBLE = fk + 12;
  public static final int ELSE = fk + 13;
  public static final int EXTENDS = fk + 14;
  public static final int FALSE = fk + 15;
  public static final int FINAL = fk + 16;
  public static final int FINALLY = fk + 17;
  public static final int FLOAT = fk + 18;
  public static final int FOR = fk + 19;
  public static final int GOTO = fk + 20;
  public static final int IF = fk + 21;
  public static final int IMPLEMENTS = fk + 22;
  public static final int IMPORT = fk + 23;
  public static final int INSTANCEOF = fk + 24;
  public static final int INT = fk + 25;
  public static final int INTERFACE = fk + 26;
  public static final int LONG = fk + 27;
  public static final int NATIVE = fk + 28;
  public static final int NEW = fk + 29;
  public static final int NULL = fk + 30;
  public static final int PACKAGE = fk + 31;
  public static final int PRIVATE = fk + 32;
  public static final int PROTECTED = fk + 33;
  public static final int PUBLIC = fk + 34;
  public static final int RETURN = fk + 35;
  public static final int SHORT = fk + 36;
  public static final int STATIC = fk + 37;
  public static final int SUPER = fk + 38;
  public static final int SWITCH = fk + 39;
  public static final int SYNCHRONIZED = fk + 40;
  public static final int THIS = fk + 41;
  public static final int THROW = fk + 42;
  public static final int THROWS = fk + 43;
  public static final int TRANSIENT = fk + 44;
  public static final int TRUE = fk + 45;
  public static final int TRY = fk + 46;
  public static final int VOID = fk + 47;
  public static final int VOLATILE = fk + 48;
  public static final int WHILE = fk + 49;

  /* ------------------------------------------------------------- */

  private static final int fe = fk+60;

  public static final int FCE  = fe + 0;  // function call
  public static final int DIM  = fe + 1;  // dimension []
  public static final int CAST = fe + 2;  // cast ()
  public static final int INC  = fe + 3;  // post increment
  public static final int DEC  = fe + 4;  // post decrement

  public static final int LABEL_STAT       = fe + 5;  // label statement
  public static final int EMPTY_STAT       = fe + 6;  // empty statement
  public static final int DECLARATION_STAT = fe + 7;  // variable declaration
  public static final int EXPRESSION_STAT  = fe + 8;  // expression statement
  public static final int BLOCK_STAT       = fe + 9;  // block

  public static final int FOR_INIT         = fe + 10;
  public static final int FOR_CONDITION    = fe + 11;
  public static final int FOR_UPDATE       = fe + 12;

  public static final int FIELD_DECL       = fe + 13;  // field declaration
  public static final int METHOD_DECL      = fe + 14;  // method declaration
  public static final int CONSTRUCTOR_DECL = fe + 15;  // constructor
  public static final int INITIALIZER_DECL = fe + 16;  // class initializer

  public static final int EOS = fe + 17;  // end of source
}
