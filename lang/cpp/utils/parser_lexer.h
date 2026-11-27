/* parser_lexer.h - Lexer for cparser.py --cpp generated parsers.

   EnvInput (envio.h) provides the token stream: tokenKind/tokenTxt/tokenVal/
   tokenSym, virtual translate (), mark ()/rewind (), getTokenFileInx/Line/Col ().
   The generated parser keeps its grammar symbol in `token' (set by translate),
   so tokens must be read through RewindInput::retrieve (): that keeps the
   queue used by mark ()/rewind () and re-runs translate () on replay.
   readIdent () in TextInput tests the old InputSymbol `symbol', so the
   read* methods used by the generated parser are overridden here. */

#ifndef PARSER_LEXER_H
#define PARSER_LEXER_H

#include "envio.h"

/* pas.g does not declare its structure base class; build with
   -DPARSER_BASIC_STUB to add it (cmm.g declares CmmBasic itself). */
#ifdef PARSER_BASIC_STUB
class CmmBasic
{
   public:
      int src_file;
      int src_line;
      int src_column;
};
#endif

class ParserLexer : public EnvInput
{
   public:
      ParserLexer () { }
      virtual ~ ParserLexer () { }

      /* queued nextToken: unlike TextInput::nextToken (), retrieve () keeps
         the mark/rewind queue and re-runs translate () from the queue */
      void nextToken () { retrieve (); }

      string readIdent (string msg = "Identifier expected")
      {
         string result;
         if (tokenKind != nameToken)
            error (msg);
         result = tokenTxt;
         nextToken ();
         return result;
      }

      string readNumber ()
      {
         string result;
         if (tokenKind != numberToken)
            error ("Number expected");
         result = tokenTxt;
         nextToken ();
         return result;
      }

      string readReal ()
      {
         string result;
         if (tokenKind != realToken)
            error ("Real number expected");
         result = tokenTxt;
         nextToken ();
         return result;
      }

      string readQuotedString ()
      {
         string result;
         if (tokenKind != stringToken)
            error ("String expected");
         result = tokenTxt; // with quotes
         nextToken ();
         return result;
      }

      string readQuotedCharAsString ()
      {
         string result;
         if (tokenKind != charToken)
            error ("Character constant expected");
         result = tokenTxt; // with quotes
         nextToken ();
         return result;
      }
};

#endif /* PARSER_LEXER_H */
