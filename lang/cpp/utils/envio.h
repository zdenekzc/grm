
/* envio.h */

/* Input / Output */

#ifndef __ENVIO_H__
#define __ENVIO_H__

#include "textio.h"

OPEN_NAMESPACE

/* ---------------------------------------------------------------------- */

enum InclKind
{
   normal_incl, // used by include <file_name> and include "file_name"
   system_incl, // only for include <file_name>
   user_incl    // only for include "file_name"
};

struct InclDir
{
   string name;
   InclKind kind;
   InclDir * next;

   InclDir ();
};

struct InclDirectories
{
   InclDir * first_dir;
   InclDir * last_dir;

   void insInclDir (string name, InclKind kind = normal_incl);
   void addInclDir (string name, InclKind kind = normal_incl);

   string findInclFile (string name,
                        bool system_file = false,
                        string include_next = "",
                        bool show_incl_next = false);

   string lookupInclFile (string name,
                          string dir = "",
                          bool system_file = false,
                          string include_next = "",
                          bool show_incl_next = false);

   void copyFrom (InclDirectories & source);

   InclDirectories ();
   ~ InclDirectories ();
};

/* ---------------------------------------------------------------------- */

struct CondSymbols;

struct CondParam
{
   string name;
   bool multi; // true => ... parameter
   CondParam * next;

   CondParam ();
};

struct CondSymbol
{
   string name;
   string value;

   bool with_params; // function like macro, defined with (possible empty) parameter list

   bool local_param; // used as local macro parameter
   string orig_value; // non-expanded parameter value

   CondParam * first_param;
   CondParam * last_param;

   CondSymbol * prev; // list in order of definition
   CondSymbol * next;
   CondSymbols * above;

   CondSymbol * left;  // unbalanced binary search tree (by name), only for searchSymbol
   CondSymbol * right; // left < name <= right (equal names to the right)

   string fileName; // location of symbol defininiton
   int fileInx;
   int linePos;
   int colPos;
   int charPos;

   void insParam (string name, bool multi = false);
   void copyCondParametersFrom (CondSymbol * source);
   void deleteParameters ();

   CondSymbol ();
   ~ CondSymbol ();
};

struct CondSymbols
{
   CondSymbol * first_symbol;
   CondSymbol * last_symbol;

   CondSymbol * root; // binary search tree

   void insTree (CondSymbol * item);
   void replaceChild (CondSymbol * parent, CondSymbol * old_item, CondSymbol * new_item);
   void removeTree (CondSymbol * item);

   void insSymbol (CondSymbol * item);

   CondSymbol * searchSymbol (string name);
   string recallSymbol (string name);

   CondSymbol * defineNewSymbol (string name, string value);

   bool isDefinedSymbol (string name);
   void defineSymbolWithParams (string name, string params, string value);
   void defineSymbol (string name, string value);
   void undefineSymbol (string name);

   void copyFrom (CondSymbols & source);

   CondSymbols ();
   ~ CondSymbols ();
};

/* ---------------------------------------------------------------------- */

struct EnvVar
{
   string name;
   string value;
   EnvVar * next;

   EnvVar ();
};

struct EnvVariables
{
   EnvVar * first_var;
   EnvVar * last_var;

   void insVariable (string name, string value);
   void addVariable (string name, string value);

   EnvVar * searchVariable (string name);
   string recallVariable (string name);

   // string translateVariable (string name);

   void copyFrom (EnvVariables & source);

   EnvVariables ();
   ~ EnvVariables ();
};

/* ---------------------------------------------------------------------- */

struct UsedFile
{
   string name;
   UsedFile * next;

   UsedFile ();
};

struct UsedFiles
{
   UsedFile * first_file;
   UsedFile * last_file;

   void insUsedFile (string name);
   void addUsedFile (string name);

   void copyFrom (UsedFiles & source);

   UsedFiles ();
   ~ UsedFiles ();
};

/* ---------------------------------------------------------------------- */

struct CondLevel
{
   bool value; // true => valid branch
   bool done; // true => some valid branch already evaluated

   CondLevel * prev;
   CondLevel * next;

   CondLevel ();
};

struct CondLevels
{
   CondLevel * first_level;
   CondLevel * last_level;

   CondLevel * current_level;

   int level;

   void insCondLevel (CondLevel * item);

   void addCondLevel (bool value);
   void removeCondLevel ();
   void removeAllLevels ();
   bool calculate ();

   CondLevels ();
   ~ CondLevels ();
};

/* ---------------------------------------------------------------------- */

enum EnvGuard
{
   before_guard, // before first ifndef
   open_guard,   // first ifndef encountered
   inside_guard, // after first ifndef
   close_guard,  // last endif encountered
   after_guard,  // after corresponding endif
   wrong_guard   // file is not written in ifndef ... endif form
};

/* ---------------------------------------------------------------------- */

struct EnvOptions
{
   bool lowerCaseIdentifiers; // true => conver identifiers to lower case
   bool upperCaseIdentifiers; // true => conver identifiers to upper case

   bool pascalNumbers; // true => require digit before and after decimal point
   bool pascalStrings; // true => strings with single quote

   bool pascalComments; // true => (* ... *) and { ... } comments
   bool semicolonComments; // true => from semicolon to end of line is comment
   bool hashComments; // true => from hash mark to end of line is comment

   bool textLines; // true => from reverse apostrophe ` to end of line is text literal

   bool reportComments; // true => produce comment tokens
   bool reportLineCont; // true => produce line continuation tokens (e.g. in macro definitions)
   bool reportSpaces; // true => produce white space tokens
   bool reportEol; // true => produce end of line tokens

   bool hashDirectives;   // true => directives starts with hash mark (normal situation)
   bool atDirectives;     // true => directives can start with @ mark (not used in C language)
   bool dollarDirectives; // true => directives can start with $ mark (not used in C language)

   bool keepEmptySections; // true => add empty lines in place of unused conditional sections
   bool keepUnusedSections; // true => report unused conditional sections as 'unusedDirectiveToken'

   bool requireSymbolDefinition; // false => unknown conditional symbols are defined as zero
   bool tolerateMissingEndOfLine; // false => require end of line after directive

   bool reportIncludes; // true => produce tokens for include directives
   bool ignoreIncludes; // true => do not read include files, write original directive to output
   bool tolerateIncludes; // true => if include file is not found, write original directive to output
   bool tolerateOnlySystemIncludes; // with tolerateIncludes: only <file_name>, missing "file_name" is an error

   bool ignoreWarningDirectives; // true => warning directives are ignored
   bool ignoreErrorDirectives; // true => error and warning directives are ignored

   bool ignoreUnknownDirectives; // true => unknown directives are ignored

   bool ignoreMacroExpansion; // true => do not expand macros

   bool showInclDirectories; // true => print information when new include directories is added
   bool showInclNext; // true => print information about include_next
   bool showIncludes; // true => print inform when include file is opened and close
   bool showDefinitions; // true => print information when define directives are encountered
   bool showMacroExpansion; // true => inform when macro is expanded
   bool showExpansionDetails; // true => inform when macro is expanded
   bool showOtherDirectives; // true => print information about other directives
   bool showTokens; // true => inform about each token

   EnvOptions ();
};

/* ---------------------------------------------------------------------- */

class SubInput : public CharInput
{
   public:
      CondSymbols local_symbols; // macro parameters

      SubInput * prev;
      SubInput * next;

      string title; // macro name, check for recursion
      string orig_include_name; // original include file name, without additional directory

      bool is_include_file;
      bool is_nested_file;

      bool add_new_line;
      bool add_final_token;

      SubInput * save_real_input; // file input (not macro input)

      EnvGuard guard_state; // ifndef ... endif guard
      int guard_level;
      string guard_name;

      virtual string getMsg () { return "included from this position"; }
      virtual string getInfo () { return getFileName (); }

      SubInput ();
      virtual ~ SubInput ();
};

class StrSubInput : public SubInput
{
   private:
      int inx; // position in 'value' variable

   public:
      string value; // read source text from this variable

      virtual void readBuf ();

      virtual string getMsg () { return "called from this position"; }
      virtual string getInfo () { return value; }

      StrSubInput ();
      virtual ~ StrSubInput ();
};

/* ---------------------------------------------------------------------- */

class EnvInput : public TextInput
{
   private:
      SubInput * first_input; // original file or string input (not include or macro)
      SubInput * real_input; // original file, string or include input (not macro input)
      SubInput * input; // current character stream

      int sub_level;

      int line_cont; // count directive lines, only for opt.keepEmptySections

      bool inside_directive; // true => report line end

   protected:
      CondLevels condTable; // nested conditional branches
      bool condValue; // calculated result

   public:
      bool compound_separators; // multi character separators

   public:
      CondSymbols symbols;
      InclDirectories incl_directories;
      UsedFiles used_files;

      // EnvVariables variables;
      EnvOptions opt;

      string compiler_options;

   public:
      bool getCondValue () { return condValue; }
      bool insideDirective () { return inside_directive; } // true => #if, #elif, #include ...

      void saveOptions (EnvOptions & state) { state = opt; }
      void restoreOptions (EnvOptions & state) { opt = state; }

      string translatePath (string name);
      void getSimpleToken ();

   private:

      void openSubInput (SubInput * item);
      void closeSubInput ();
      void cleanSubInput ();

   public:

      void openInclude (string file_name, string orig_name);
      void openMacro (SubInput * item, bool add_stop = false);
      void openText (const string text, bool add_stop = false);
      void OpenNested (string file_name);
      void CloseNested ();

      void extraCh (); // used by multi-character separators

      CondSymbol * localSearchSymbol (const string name);
      CondSymbol * macroSearchSymbol (StrSubInput * macro_input, const string name);

      string readParameter (bool multi);
      string expandParameter (const string orig_value);
      void   expandParameters (StrSubInput * macro_input, CondSymbol * symbol);

      string compoundItem (StrSubInput * macro_input, const string name);
      void   stringSymbol (StrSubInput * macro_input);
      void   compoundSymbol (StrSubInput * macro_input);

      void expandAgain (CondSymbol * symbol, StrSubInput * macro_input);
      void expandSymbol (CondSymbol * symbol);
      void resolveSymbol ();

      void skipSpaces ();
      void checkEndOfLine ();

      bool threeDots ();
      void defineParameter (CondSymbol * symbol);

      bool twoSeparators (char c1, char c2);
      void skipTwoSeparators ();
      bool condSymbolDefined ();

      int condIdent (bool cont);
      int condHasInclude ();
      int condSimpleExpr (bool cont);
      int condFactor (bool cont);
      int condTerm (bool cont);
      int condShift (bool cont);
      int condRel (bool cont);
      int condEq (bool cont);
      int condAnd (bool cont);
      int condXor (bool cont);
      int condOr (bool cont);
      int condLogAnd (bool cont);
      int condLogOr (bool cont);
      int condExpression (bool cont = true);

   protected:
      void getExprToken ();

      void defineDirective ();
      void undefDirective ();
      void condDirective (bool inv, bool only_symbol);
      void ifDirective ();
      void ifdefDirective ();
      void ifndefDirective ();
      void elifDirective ();
      void elseDirective ();
      void endifDirective ();
      void includeDirective (bool include_next = false);
      void pragmaDirective ();
      void lineDirective ();   // cecko: #line N "soubor" (cmm - predzpracovany text)
      void warningDirective ();
      void errorDirective ();
      void includeDirDirective ();

   protected:
      virtual void Init ();
      virtual void Finish ();
      virtual void explain (string cls, string id, string txt);

      void setStartToken ();
      void setSpaceToken (const string txt);
      void setStringToken (const string txt);
      void setNumberToken (const string txt);
      void setIncludeDirectiveToken (const string txt);
      void setUnusedDirectiveToken (const string txt);
      void setProcessedDirectiveToken ();

      // selective macro expansion: false => symbol is not expanded, identifier is kept as token
      // (called for each defined macro, also inside directives - see insideDirective)
      virtual bool expandMacro (CondSymbol * symbol) { return true; }

      virtual bool customDirective (const string name) { return false; }
      virtual bool customPragma (const string name) { return false; }

      virtual string queryInclude (const string file_name) { return file_name; }
      virtual void unknownInclude (const string file_name) { }

      virtual void openingInclude () { }
      virtual void closingInclude () { }

   public:
      string getGuardSymbol ();
      void include (string file_name);

      string parametersToText (CondSymbol * symbol);
      string defineToText (CondSymbol * symbol);

   public:
      virtual void getToken ();

      void checkEnd ();
      void showPositions ();

      EnvInput ();
      virtual ~EnvInput ();
};

class EnvOutput : public TextOutput
{
};

CLOSE_NAMESPACE

#endif /* __ENVIO_H__ */
