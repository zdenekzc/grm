
/* envio.cc */

#include "envio.h"

#include "str.h" // const lf, ...
#include "conv.h" // StrToULong, IntToStr, ...
#include "inf.h" // function info

#include <string.h>  // function memcpy
#include <cstdio>    // fopen, fclose

#define DUPL_OUTPUT

OPEN_NAMESPACE

/************************** INCLUDE DIRECTORIES ***************************/

InclDir::InclDir () :
   name (),
   kind (normal_incl),
   next (NULL)
{
}

InclDirectories::InclDirectories () :
   first_dir (NULL),
   last_dir (NULL)
{
}

InclDirectories::~InclDirectories ()
{
   InclDir * item = first_dir;
   while (item != NULL)
   {
      InclDir * tmp = item->next;
      delete item;
      item = tmp;
   }
   first_dir = NULL;
   last_dir = NULL;
}

/* ---------------------------------------------------------------------- */

void InclDirectories::insInclDir (string name, InclKind kind)
{
   assert (this != NULL);

   InclDir * item = new InclDir ();
   item->name = name;
   item->kind = kind;

   item->next = NULL;

   if (first_dir == NULL)
   {
      assert (last_dir == NULL);
      first_dir = item;
      last_dir = item;
   }
   else
   {
      assert (last_dir != NULL);
      last_dir->next = item;
      last_dir = item;
   }
}

void InclDirectories::addInclDir (string name, InclKind kind)
{
   InclDir * item = first_dir;
   while (item != NULL && item->name != name)
      item = item->next;

   if (item == NULL)
      insInclDir (name, kind);
}

/* ---------------------------------------------------------------------- */

void InclDirectories::copyFrom (InclDirectories & source)
{
   InclDir * item = source.first_dir;
   while (item != NULL)
   {
      insInclDir (item->name, item->kind);
      item = item->next;
   }
}

/* ---------------------------------------------------------------------- */

inline bool FileExists (string file_name)
{
   FILE * f = fopen (file_name.c_str (), "rb");
   bool found = (f != NULL);
   if (found)
      fclose (f);

   return found;
}

inline bool ItemFound (InclDir * item, string name, bool system_file)
{
   bool result = false;

   bool allowed;

   if (system_file)
      allowed = (item->kind != user_incl);
   else
      allowed = (item->kind != system_incl);

   if (allowed)
   {
      string file_name = addSlash (item->name) + name;

      // debug ("try " + file_name);
      if (FileExists (file_name))
      {
         // debug ("found " + file_name);
         result = true;
      }
   }

   return result;
}

/* ---------------------------------------------------------------------- */

string InclDirectories::findInclFile (string name,
                                       bool system_file,
                                       string include_next,
                                       bool show_incl_next)
{
   assert (this != NULL);
   string result = ""; // when not found
   // debug ("findInclFile " + name);

   if (! hasPrefixChar (name, '/'))
   {
      bool found = false;
      InclDir * item = first_dir;

      while (item != NULL && ! found)
      {
         // debug ("item " + item->name);
         bool allowed;

         if (system_file)
            allowed = (item->kind != user_incl);
         else
            allowed = (item->kind != system_incl);

         if (allowed)
         {
            string file_name = addSlash (item->name) + name;

            // debug ("try findInclFile " + file_name);
            if (FileExists (file_name))
            {
               debug ("findInclFile found " + file_name);
               if (include_next != "")
               {
                  if (show_incl_next)
                     info ("Found " + file_name + ", switching to  " + include_next);
                  name = include_next; // search again (possibly another file name)
                  include_next = "";
               }
               else
               {
                  found = true;
                  result = file_name;
               }
            }
         }
         item = item->next;
      }
   }

   if (result == "") debug ("findInclFile missing " + name);
   return result;
}

string InclDirectories::lookupInclFile (string name,
                                         string dir,
                                         bool system_file,
                                         string include_next,
                                         bool show_incl_next)
{
   string result = "";

   string local_name = addSubdir (dir, name);
   // debug ("lookupInclFile " + local_name + ", next: " + include_next);

   if (! system_file && FileExists (local_name))
   {
      if (include_next != "")
      {
         if (show_incl_next)
            info  ("Found " + local_name + ", switching to  " + include_next);
         name = include_next; // search again (possibly another file name)
         include_next = "";
         result = findInclFile (name, system_file, include_next, show_incl_next);
      }
      else
      {
         result = local_name;
      }
   }
   else
   {
      result = findInclFile (name, system_file, include_next, show_incl_next);
   }

   // debug ("end of lookupInclFile " + result);
   return result;
}

/************************** CONDITIONAL SYMBOLS ***************************/

CondParam::CondParam () :
   name (),
   multi (false),
   next (NULL)
{
}

/* ---------------------------------------------------------------------- */

CondSymbol::CondSymbol () :
   name (),
   value (""),
   with_params (false),
   local_param (false),
   orig_value (""),
   first_param (NULL),
   last_param (NULL),
   prev (NULL),
   next (NULL),
   above (NULL),
   left (NULL),
   right (NULL),
   fileName (),
   fileInx (0),
   linePos (0),
   colPos (0),
   charPos (0)
{
}

void CondSymbol::deleteParameters ()
{
   CondParam * item = first_param;
   while (item != NULL)
   {
      CondParam * tmp = item->next;
      delete item;
      item = tmp;
   }
   first_param = NULL;
   last_param = NULL;
}

CondSymbol::~CondSymbol ()
{
   deleteParameters ();

   if (above != NULL)
   {
      above->removeTree (this);

      if (prev != NULL)
         prev->next = next;
      else
         above->first_symbol = next;

      if (next != NULL)
         next->prev = prev;
      else
         above->last_symbol = prev;

      above = NULL;
      prev = NULL;
      next = NULL;
   }
}

/* ---------------------------------------------------------------------- */

CondSymbols::CondSymbols () :
   first_symbol (NULL),
   last_symbol (NULL),
   root (NULL)
{
}

CondSymbols::~CondSymbols ()
{
   CondSymbol * item = first_symbol;
   while (item != NULL)
   {
      CondSymbol * tmp = item->next;
      item->above = NULL; // do not unlink from list and tree, everything is deleted
      delete item;
      item = tmp;
   }

   first_symbol = NULL;
   last_symbol = NULL;
   root = NULL;
}

/* ---------------------------------------------------------------------- */

/* unbalanced binary search tree: left < name <= right */

void CondSymbols::insTree (CondSymbol * item)
{
   item->left = NULL;
   item->right = NULL;

   if (root == NULL)
   {
      root = item;
   }
   else
   {
      CondSymbol * p = root;
      bool cont = true;
      while (cont)
      {
         if (item->name < p->name)
         {
            if (p->left == NULL) { p->left = item; cont = false; }
            else p = p->left;
         }
         else
         {
            // equal names to the right => searchSymbol finds older symbol first
            if (p->right == NULL) { p->right = item; cont = false; }
            else p = p->right;
         }
      }
   }
}

void CondSymbols::replaceChild (CondSymbol * parent, CondSymbol * old_item, CondSymbol * new_item)
{
   if (parent == NULL)
      root = new_item;
   else if (parent->left == old_item)
      parent->left = new_item;
   else
      parent->right = new_item;
}

void CondSymbols::removeTree (CondSymbol * item)
{
   // find item and its parent
   CondSymbol * parent = NULL;
   CondSymbol * p = root;
   while (p != NULL && p != item)
   {
      parent = p;
      if (item->name < p->name)
         p = p->left;
      else
         p = p->right;
   }

   if (p != NULL)
   {
      if (item->left == NULL)
      {
         replaceChild (parent, item, item->right);
      }
      else if (item->right == NULL)
      {
         replaceChild (parent, item, item->left);
      }
      else
      {
         // two children: replace item with successor (minimum of right subtree)
         CondSymbol * succ_parent = item;
         CondSymbol * succ = item->right;
         while (succ->left != NULL)
         {
            succ_parent = succ;
            succ = succ->left;
         }

         if (succ_parent != item)
         {
            succ_parent->left = succ->right;
            succ->right = item->right;
         }
         succ->left = item->left;

         replaceChild (parent, item, succ);
      }
   }

   item->left = NULL;
   item->right = NULL;
}

/* ---------------------------------------------------------------------- */

void CondSymbol::insParam (string name, bool multi)
{
   assert (this != NULL);

   CondParam * item = new CondParam;
   item->name = name;
   item->multi = multi;
   item->next = NULL;

   if (first_param == NULL)
   {
      assert (last_param == NULL);
      first_param = item;
      last_param = item;
   }
   else
   {
      assert (last_param != NULL);
      last_param->next = item;
      last_param = item;
   }
}

void CondSymbols::insSymbol (CondSymbol * item)
{
   assert (this != NULL);
   assert (item != NULL);

   item->prev = last_symbol;
   item->next = NULL;
   item->above = this;

   if (first_symbol == NULL)
   {
      assert (last_symbol == NULL);
      first_symbol = item;
      last_symbol = item;
   }
   else
   {
      assert (last_symbol != NULL);
      last_symbol->next = item;
      last_symbol = item;
   }

   insTree (item);
}

/* ---------------------------------------------------------------------- */

CondSymbol * CondSymbols::searchSymbol (string name)
{
   assert (this != NULL);
   CondSymbol * item = root;
   while (item != NULL && item->name != name)
   {
      if (name < item->name)
         item = item->left;
      else
         item = item->right;
   }
   return item;
}

string CondSymbols::recallSymbol (string name)
{
   CondSymbol * item = searchSymbol (name);

   if (item == NULL)
      return "";
   else
      return item->value;
}

/* ---------------------------------------------------------------------- */

void CondSymbol::copyCondParametersFrom (CondSymbol * source)
{
   assert (source != NULL);
   CondParam * item = source->first_param;
   while (item != NULL)
   {
      insParam (item->name, item->multi);
      item = item->next;
   }
}

void CondSymbols::copyFrom (CondSymbols & source)
{
   CondSymbol * item = source.first_symbol;
   while (item != NULL)
   {
      CondSymbol * tmp = new CondSymbol;

      tmp->name = item->name;
      tmp->value = item->value;

      tmp->fileName = item->fileName;
      tmp->linePos = item->linePos;
      tmp->colPos = item->colPos;
      tmp->charPos = item->charPos;

      tmp->copyCondParametersFrom (item);

      insSymbol (tmp);

      item = item->next;
   }
}

/* ---------------------------------------------------------------------- */

bool CondSymbols::isDefinedSymbol (string name)
{
   CondSymbol * item = searchSymbol (name);
   return item != NULL;
}

CondSymbol * CondSymbols::defineNewSymbol (string name, string value)
{
   CondSymbol * item = searchSymbol (name);

   if (item == NULL)
   {
      item = new CondSymbol;
      item->name = name;
      item->value = value;
      insSymbol (item);
   }
   else
   {
      item->deleteParameters ();
      item->value = value;
   }

   return item;
}

void CondSymbols::defineSymbolWithParams (string name, string params, string value)
{
   CondSymbol * item = defineNewSymbol (name, value);

   if (params != "")
   {
      item->with_params = true; // important

      int inx = 0;
      int len = params.length ();

      while (inx < len)
      {
         int start = inx;

         while (inx < len && params [inx] != ',')
            inx ++;

         string s = params.substr (start, inx-start);
         s = trim (s);
         // debug ("Define Item " + name + " with parameter " + s);
         item->insParam (s);

         if (inx < len && params [inx] == ',')
            inx ++;
      }
   }
}

void CondSymbols::defineSymbol (string name, string value)
{
   defineNewSymbol (name, value);
}

void CondSymbols::undefineSymbol (string name)
{
   CondSymbol * item = searchSymbol (name);
   if (item != NULL)
      delete item;
}

/************************** ENVIRONMENT VARIABLES *************************/

EnvVar::EnvVar () :
   name (),
   value (),
   next (NULL)
{
}

EnvVariables::EnvVariables () :
   first_var (NULL),
   last_var (NULL)
{
}

EnvVariables::~EnvVariables ()
{
   EnvVar * item = first_var;
   while (item != NULL)
   {
      EnvVar * tmp = item->next;
      delete item;
      item = tmp;
   }
   first_var = NULL;
   last_var = NULL;
}

/* ---------------------------------------------------------------------- */

void EnvVariables::insVariable (string name, string value)
{
   // debug (PtrToStr (this) + " AddPathVar " + name + " = " + value);
   assert (this != NULL);

   EnvVar * item = new EnvVar ();
   item->name = name;
   item->value = value;

   if (first_var == NULL)
   {
      assert (last_var == NULL);
      first_var = item;
      last_var = item;
   }
   else
   {
      assert (last_var != NULL);
      last_var->next = item;
      last_var = item;
   }
}

EnvVar * EnvVariables::searchVariable (string name)
{
   assert (this != NULL);
   EnvVar * item = first_var;
   while (item != NULL && item->name != name)
      item = item->next;
   return item;
}

void EnvVariables::addVariable (string name, string value)
{
   EnvVar * item = searchVariable (name);
   if (item == NULL)
      insVariable (name, value);
   else
      item->value = value;
}

string EnvVariables::recallVariable (string name)
{
   EnvVar * item = searchVariable (name);
   if (item == NULL)
      return "";
   else
      return item->value;
}

void EnvVariables::copyFrom (EnvVariables & source)
{
   EnvVar * item = source.first_var;
   while (item != NULL)
   {
      insVariable (item->name, item->value);
      item = item->next;
   }
}

/* ---------------------------------------------------------------------- */

#if 0
string EnvVariables::translateVariable (string name)
// resolve variable names in following strings $(variable)/relative_path
{
   string::size_type len = name.length ();

   if (len > 1 && name[0] == '$')
   {
      string key = "";
      string tail = "";

      if (name[1] == '(')
      {
         string::size_type inx = 2;
         while (inx < len && name [inx] != ')')
            inx ++;

         if (inx > 2 && inx < len)
         {
            key = name.substr (2, inx-2);
            tail = name.substr (inx+1);
         }
      }
      else
      {
         string::size_type inx = 1;
         while (inx < len && isLetter (name [inx]))
            inx ++;

         if (inx > 1)
         {
            key = name.substr (1, inx-1);
            tail = name.substr (inx);
         }
      }

      if (key != "")
      {
         EnvVar * item = searchVariable (key);
         if (item != NULL)
            name = removeLastSlash (item->value) + tail;
      }
   }

   // debug (" result is " + name);
   return name;
}
#endif

/******************************* USED FILES *******************************/

UsedFile::UsedFile () :
   name (),
   next (NULL)
{
}

UsedFiles::UsedFiles () :
   first_file (NULL),
   last_file (NULL)
{
}

UsedFiles::~UsedFiles ()
{
   UsedFile * item = first_file;
   while (item != NULL)
   {
      UsedFile * tmp = item->next;
      delete item;
      item = tmp;
   }
   first_file = NULL;
   last_file = NULL;
}

/* ---------------------------------------------------------------------- */

void UsedFiles::insUsedFile (string name)
{
   assert (this != NULL);

   UsedFile * item = new UsedFile ();
   item->name = name;
   item->next = NULL;

   if (first_file == NULL)
   {
      assert (last_file == NULL);
      first_file = item;
      last_file = item;
   }
   else
   {
      assert (last_file != NULL);
      last_file->next = item;
      last_file = item;
   }
}

void UsedFiles::copyFrom (UsedFiles & source)
{
   UsedFile * item = source.first_file;
   while (item != NULL)
   {
      insUsedFile (item->name);
      item = item->next;
   }
}

/* ---------------------------------------------------------------------- */

void UsedFiles::addUsedFile (string name)
{
   UsedFile * item = first_file;
   while (item != NULL && item->name != name)
      item = item->next;

   if (item == NULL)
      insUsedFile (name);
}

/*************************** CONDITIONAL LEVELS ***************************/

CondLevel::CondLevel () :
   value (false),
   done (false),
   prev (NULL),
   next (NULL)
{
}

CondLevels::CondLevels () :
   first_level (NULL),
   last_level (NULL),
   current_level (NULL),
   level (0)
{
}

CondLevels::~CondLevels()
{
   CondLevel * item = first_level;
   while (item != NULL)
   {
      CondLevel * tmp = item->next;
      delete item;
      item = tmp;
   }
   first_level = NULL;
   last_level = NULL;
   current_level = NULL;
   level = 0;
}

/* ---------------------------------------------------------------------- */

void CondLevels::insCondLevel (CondLevel * item)
{
   assert (this != NULL);
   assert (item != NULL);

   item->prev = last_level;

   if (first_level == NULL)
   {
      assert (last_level == NULL);
      first_level = item;
      last_level = item;
   }
   else
   {
      assert (last_level != NULL);
      last_level->next = item;
      last_level = item;
   }
}

/* ---------------------------------------------------------------------- */

const int cond_level_max = 128; // only for loop detection
const int sub_level_max = 32; // only for loop detection

void CondLevels::addCondLevel (bool value)
{
   // look for unused item
   if (current_level == NULL)
      current_level = first_level;
   else
      current_level = current_level->next;

   if (current_level == NULL)
   {
      // allocate new item
      current_level = new CondLevel;
      insCondLevel (current_level);
   }

   current_level->value = value;
   current_level->done = false;

   level ++;
}

void CondLevels::removeCondLevel ()
{
   assert (current_level != NULL);
   current_level = current_level->prev; // old item may be reused later
   level --;
}

void CondLevels::removeAllLevels ()
{
   current_level = NULL;
   level = 0;
   // other items may be reused later
}

bool CondLevels::calculate ()
{
   bool result = true;

   if (current_level != NULL)
   {
      CondLevel * item = first_level;
      while (item != current_level && result)
      {
         assert (item != NULL);
         if (! item->value)
            result = false;
         item = item->next;
      }

      if (result && ! item->value)
         result = false;
   }

   return result;
}

/******************************** OPTIONS *********************************/

EnvOptions::EnvOptions ():

   lowerCaseIdentifiers (false),
   upperCaseIdentifiers (false),

   pascalNumbers (false),
   pascalStrings (false),

   pascalComments (false),
   semicolonComments (false),
   hashComments (false),

   textLines (false),

   reportComments (false),
   reportLineCont (false),
   reportSpaces (false),
   reportEol (false),

   hashDirectives (true), /* <-- */
   atDirectives (false),
   dollarDirectives (false),

   keepEmptySections (false),
   keepUnusedSections (false),

   requireSymbolDefinition (false),
   tolerateMissingEndOfLine (false),

   reportIncludes (false),
   ignoreIncludes (false),
   tolerateIncludes (false),
   tolerateOnlySystemIncludes (false),

   ignoreWarningDirectives (false),
   ignoreErrorDirectives (false),

   ignoreUnknownDirectives (false),

   ignoreMacroExpansion (false),

   showInclDirectories (false),
   showInclNext (false),
   showIncludes (false),
   showDefinitions (false),
   showMacroExpansion (false),
   showExpansionDetails (false),
   showOtherDirectives (false),
   showTokens (false)
{ }

/******************************* SUB INPUT ********************************/

SubInput::SubInput ():
   prev (NULL),
   next (NULL),
   title (),
   orig_include_name (),
   is_include_file (false),
   is_nested_file (false),
   add_new_line (false),
   add_final_token (false),
   save_real_input (NULL),
   guard_state (before_guard),
   guard_level (0),
   guard_name ("")
{
}

SubInput::~SubInput ()
{
}

/* ---------------------------------------------------------------------- */

StrSubInput::StrSubInput ():
   inx (0),
   value ()
{
}

StrSubInput::~StrSubInput ()
{
}

void StrSubInput::readBuf ()
{
   bufPos = 0;
   bufLen = 0;

   int len = value.length ();
   if (inx < len)
   {
      bufLen = len - inx;

      if (bufLen > bufSize)
         bufLen = bufSize;

      memcpy (buf, value.c_str () + inx, bufLen);

      inx += bufLen;
   }
}

/******************************* ENV INPUT ********************************/

EnvInput::EnvInput ():

   first_input (NULL),
   real_input (NULL),
   input (NULL),

   sub_level (0),
   line_cont (0),
   inside_directive (false),

   condTable (),
   condValue (true),

   compound_separators (false),

   symbols (),
   incl_directories (),
   used_files (),

   // variables (),
   opt ()
{
   openSubInput (new SubInput); // !? delete
   real_input = input;
   input->save_real_input = real_input;
}

EnvInput::~EnvInput ()
{
   // delete input streams
   while (input != NULL)
      cleanSubInput ();

  Finish ();
}

/* ---------------------------------------------------------------------- */

void EnvInput::checkEnd ()
{
   if (input != NULL && input->prev != NULL)
      error ("Remaining nested input");

   if (! inpEof)
      error ("Remaining text");
}

void EnvInput::showPositions ()
{
   SubInput * temp = input;

   string msg = "";

   if (temp != NULL)
   {
      // current position
      msg = "Source code position";
      // msg += " in " + temp->getInfo ();
      show_info (msg, recallFileName(temp->tokenFileInx), temp->tokenLinePos, temp->tokenColPos);

      msg = temp->getMsg (); // message from inner level
      // msg += " in " + temp->getInfo ();
      temp = temp->prev;
   }

   // outer positions
   while (temp != NULL)
   {
      // msg += " in " + temp->getInfo ();
      show_info (msg, recallFileName(temp->tokenFileInx), temp->tokenLinePos, temp->tokenColPos);

      msg = temp->getMsg (); // message from inner level
      // msg += " in " + temp->getInfo ();
      temp = temp->prev;
   }
}

/* ---------------------------------------------------------------------- */

void EnvInput::Init ()
{
   // original method
   TextInput::Init ();

   condTable.removeAllLevels ();
   condValue = true;

   // do not read first character, already done by TextInput::Init ()
}

void EnvInput::Finish ()
{
}

void EnvInput::explain (string cls, string id, string txt)
{
   info (txt);
}

/* ---------------------------------------------------------------------- */

void EnvInput::setStartToken ()
{
   tokenKind = startToken;
   tokenTxt = "";
   tokenVal = "";
   tokenSym = 0;
}

void EnvInput::setSpaceToken (const string txt)
{
   tokenKind = spaceToken;
   tokenTxt = txt;
   tokenVal = "";
   tokenSym = 0;
}

void EnvInput::setStringToken (const string txt)
{
   tokenKind = stringToken;
   tokenTxt = txt;
   tokenVal = "";
   tokenSym = 0;
}

void EnvInput::setNumberToken (const string txt)
{
   tokenKind = numberToken;
   tokenTxt = txt;
   tokenVal = "";
   tokenSym = 0;
}

void EnvInput::setIncludeDirectiveToken (const string txt)
{
   tokenKind = includeDirectiveToken;
   // NO tokenTxt = "#include " + quoteStr (txt) + lf;
   tokenTxt = "#include " + txt;
   tokenVal = txt;
   tokenSym = 0;
}

void EnvInput::setUnusedDirectiveToken (const string txt)
{
   tokenKind = unusedDirectiveToken;
   tokenTxt = txt;
   tokenVal = "";
   tokenSym = 0;
}

void EnvInput::setProcessedDirectiveToken ()
{
   tokenKind = processedDirectiveToken;
   tokenTxt = "";
   tokenVal = "";
   tokenSym = 0;
}

/* ---------------------------------------------------------------------- */

void EnvInput::getSimpleToken () // @@
{
   // NO assert (tokenKind != eofToken);
   assert (input != NULL);

   while (input->inpEof &&
          ! input->add_new_line &&
          ! input->add_final_token &&
          // ! input->is_nested_file &&
          input != first_input)
   {
      // close include file or macro
      closeSubInput ();

      inpCh = input->inpCh;
      inpEof = input->inpEof;
   }

   // store token position
   input->tokenFileInx = input->fileInx;
   input->tokenLinePos = input->linePos;
   input->tokenColPos  = input->colPos;
   input->tokenCharPos = input->charPos;

   value_storage.reset ();
   text_storage.reset ();

   if (inpEof)                                     // END OF FILE
   {
      tokenTxt = "";
      tokenVal = "";
      tokenSym = 0;

      if (input != NULL && input->add_new_line)
      {
         tokenKind = eolToken;
         tokenTxt = charToStr (lf);
         input->add_new_line = false;
      }
      else if (input != NULL && input->add_final_token)
      {
         tokenKind = finalToken;
         input->add_final_token = false;
      }
      else
      {
         if (tokenKind == stopToken || tokenKind == eofToken)
            error ("Unexpected end of source");

         if (input != NULL && input->prev != NULL)
            tokenKind = stopToken;
         else
            tokenKind = eofToken;
      }
   }

   else if (isLetter (inpCh))                      // IDENTIFIER
      getIdent (opt.lowerCaseIdentifiers,
                opt.upperCaseIdentifiers);

   else if (isDigit (inpCh))                       // NUMBER
      getNumber (opt.pascalNumbers);

   else if (inpCh == '.')                          // NUMBER or PERIOD
      getNumber (opt.pascalNumbers);

   else if (inpCh == quote1)                       // CHARACTER
      getChar (opt.pascalStrings);

   else if (inpCh == quote2 )                      // STRING
      getString (opt.pascalStrings);

   else if (inpCh == '`' && opt.textLines)         // EXT LINE
      getTextLine ();

   else if (inpCh == '/')                          // COMMENT (or slash)
   {
      if (opt.pascalComments)
         getPascalComment ();
      else
         getComment ();
   }

   else if (inpCh == '{' && opt.pascalComments)    // COMMENT
      getPascalComment ();

   else if (inpCh == '(' && opt.pascalComments)    // COMMENT (or asterisk)
      getPascalComment ();

   else if (inpCh == '#' && opt.hashComments)      // COMMENT
      getLineComment ();

   else if (inpCh == ';' && opt.semicolonComments) // COMMENT
      getLineComment ();

   else if (inpCh == cr || inpCh == lf)            // END OF LINE
      getEol ();

   else if (inpCh <= ' ')                          // WHITE SPACE
   {
      assert (! inpEof);
      assert (! input->inpEof);
      getSpace ();
   }

   else if (inpCh == backslash)                    // BACKSLASH
      getBackslash ();

   else                                            // SEPARATOR
      getSeparator ();

   #if 0
   if (opt.showExpansionDetails)
      info ("getSimpleToken: " +  tokenKindToStr (tokenKind) + " " + quoteStr (tokenTxt) +
            ", next character is " + quoteStr (charToStr (inpCh)));
   #endif
}

/* ---------------------------------------------------------------------- */

void EnvInput::openSubInput (SubInput * item) // @@
{
   if (first_input == NULL)
   {
      assert (input == NULL);
      first_input = item;
      item->prev = NULL;
   }
   else
   {
      item->prev = input;
      input->next = item;
   }

   item->next = NULL;
   input = item;

   inp = input;
   #if 0
   if (opt.showExpansionDetails)
      info ("opening sub input: " + quoteStr (item->getInfo ()));
   #endif

   sub_level ++;
   if (sub_level > sub_level_max)
      error ("Too many nested includes or macros");

   input->Init ();
   inpCh = input->inpCh;
   inpEof = input->inpEof; // important

   if (input->is_include_file)
   {
      real_input = input;
      openingInclude ();
   }

   input->save_real_input = real_input;
}

void EnvInput::cleanSubInput ()
{
   assert (input != NULL);

   // remove input stream from list of include files
   CharInput * tmp = input;
   input = input->prev;

   if (input == NULL)
      first_input = NULL;
   else
      input->next = NULL;

   delete tmp;

   inp = input;
   sub_level --;

   // important
   if (input == NULL)
   {
      inpCh = 0;
      inpEof = true;
      real_input = NULL;
   }
   else
   {
      inpCh = input->inpCh;
      inpEof = input->inpEof;
      real_input = input->save_real_input;
   }
}

void EnvInput::closeSubInput ()
{
   assert (input != NULL);

   #if 0
   if (opt.showExpansionDetails)
   {
      info ("closing sub input: " + quoteStr (input->getInfo ()));
      info ("next character: " + quoteStr (charToStr (input->extra_character)));
   }
   #endif

   if (input->is_include_file)
   {
      closingInclude ();

      if (opt.showIncludes)
         explain ("include_directive", "closing",  input->getFileName ());
   }

   cleanSubInput ();
}

/* ---------------------------------------------------------------------- */

string EnvInput::translatePath (string name)
// resolve symbol names and variable names in following strings $(variable)/relative_path
{
   #if 0
   str_size_type len = name.length ();

   if (len > 1 && name[0] == '$')
   {
      string key = "";
      string tail = "";

      if (name[1] == '(' || name[1] == '{')
      {
         char stop = (name[1] == '(') ? ')' : '}';

         str_size_type inx = 2;
         while (inx < len && name [inx] != stop)
            inx ++;

         if (inx > 2 && inx < len)
         {
            key = Substr (name, 2, inx-2);
            tail = Tail (name, inx+1);
         }
      }
      else
      {
         str_size_type inx = 1;
         while (inx < len && isLetter (name [inx]))
            inx ++;

         if (inx > 1)
         {
            key = Substr (name, 1, inx-1);
            tail = Tail (name, inx);
         }
      }

      if (key != "")
      {
         CondSymbol * s = symbols.searchSymbol (key);
         if (s != NULL)
            name = removeLastSlash (s->value) + tail;
         else
         {
            EnvVar * v = variables.searchVariable (key);
            if (v != NULL)
               name = removeLastSlash (v->value) + tail;
         }
      }
   }
   #endif

   return name;
}

/* ---------------------------------------------------------------------- */

void EnvInput::openInclude (string file_name, string orig_name)
{
   SubInput * item = new SubInput ();
   item->open (file_name);

   item->is_include_file = true;
   item->orig_include_name = orig_name;
   item->add_new_line = true; // finish last line

   openSubInput (item);

   used_files.addUsedFile (file_name);

   nextCh (); // read first character

   // !? !! setStartToken (); // formal first token
}

void EnvInput::include (string file_name)
{
   openInclude (file_name, removePath (file_name));
}

void EnvInput::openText (const string text, bool add_stop)
{
   StrSubInput * item = new StrSubInput (); // !? delete
   item->is_include_file = false;
   item->add_final_token = add_stop;
   item->value = text;

   if (input != NULL)
   {
      // copy location
      item->positionInitialized = true;

      item->fileInx = input->fileInx;
      item->linePos = input->linePos;
      item->colPos  = input->colPos;
      item->charPos = input->charPos;

      item->tokenFileInx = input->fileInx;
      item->tokenLinePos = input->linePos;
      item->tokenColPos  = input->colPos;
      item->tokenCharPos = input->charPos;
   }

   openSubInput (item);
   getCh (); // skip current character (is stored as extra_character)
             // use getCh, not nextCh ... character should not be stored into duplicated input

   // !? !! setStartToken (); // formal first token
}

void EnvInput::OpenNested (string file_name)
{
   SubInput * item = new SubInput (); // !? delete
   item->open (file_name);
   item->is_nested_file = true;

   openSubInput (item);
   used_files.addUsedFile (file_name);
   getCh (); // skip current character (is stored as extra_character)
             // use getCh, not nextCh ... character should not be stored into duplicated input
}

void EnvInput::CloseNested ()
{
   while (input != NULL && ! input->is_nested_file) closeSubInput ();

   if (input == NULL || ! input->is_nested_file) warning ("error closing nested file");
   closeSubInput();
}

void EnvInput::openMacro (SubInput * item, bool add_stop)
{
   assert (input != NULL);
   assert (real_input != NULL);

   item->is_include_file = false;
   item->add_final_token = add_stop;

   openSubInput (item);

   getCh (); // skip current character (is stored as extra_character)
             // use getCh, not nextCh ... character should not be stored into duplicated input

   // !? !! setStartToken (); // formal first token
}

/* ---------------------------------------------------------------------- */

CondSymbol * EnvInput::localSearchSymbol (const string name)
{
   CondSymbol * symbol = NULL;

   if (input != NULL)
      symbol = input->local_symbols.searchSymbol (name);

   if (symbol == NULL)
   {
      symbol = symbols.searchSymbol (name);
   }

   return symbol;
}

CondSymbol * EnvInput::macroSearchSymbol (StrSubInput * macro_input, const string name)
{
   CondSymbol * symbol =
      macro_input->local_symbols.searchSymbol (name);

   if (symbol == NULL)
      symbol = localSearchSymbol (name);

   return symbol;
}

string EnvInput::readParameter (bool multi) // @@
{
   TextStorage orig_stream; // original value for current parametr
   int level = 0; // level of nested parenthesis
   bool inside = false; // true => after some non-empty token
   bool tail = false; // true => add one space before next tokem

   // inpCh is first character of current parameter
   // tokenKind, tokenTxt is old token

   #if 0
   if (opt.showExpansionDetails)
      info ("... begin parameter " + param->name + " = " +
            tokenKindToStr (tokenKind) + " " + quoteStr (tokenTxt) +
            ", next character is " + quoteStr (charToStr (inpCh)) );
   #endif

   while (level > 0 || ! ( ( ! multi && inpCh == ',' ) || inpCh == ')') )
   {
      // now read first parameter token
      getSimpleToken ();

      if (isSeparator ('(')) level ++;
      if (isSeparator (')')) level --;

      if (tokenKind == spaceToken ||
          tokenKind == commentToken ||
          tokenKind == lineContToken ||
          tokenKind == startToken ||
          tokenKind == stopToken ||
          tokenKind == finalToken ||
          tokenKind == eofToken)
      {
         if (inside) // skip leading spaces
            tail = true; // only one space
      }
      else
      {
         if (tail)
            orig_stream.put (' '); // previous space

         #if 0
         if (opt.showExpansionDetails)
            info ("... raw parameter token " + tokenKindToStr (tokenKind) + " " + quoteStr (tokenTxt) + ", level " + IntToStr (level));
         #endif

         orig_stream.put_str (tokenTxt); // collect parameter value

         tail = false;
         inside = true;
      }
   }

   #if 0
   if (opt.showExpansionDetails)
      info ("... raw parameter value " + param->name + " = " + orig_stream.to_string ());
   #endif

   return orig_stream.to_string ();
}

string EnvInput::expandParameter (const string orig_value) // @@
{
   if (dupl_input)
   {
      dupl_input_level ++;
      addRemark ("->");
   }

   openText (orig_value, true);

   resolveSymbol (); // skip macro name or right parenthesis (after opening sub-input)

   TextStorage expanded_stream;

   while (tokenKind != startToken &&
          tokenKind != stopToken &&
          tokenKind != finalToken &&
          tokenKind != eofToken)
   {
      #if 0
      if (opt.showExpansionDetails)
         info ("... collect parameter token " +
               tokenKindToStr (tokenKind) + " " + quoteStr (tokenTxt) +
               ", input = " + input->getInfo());
      #endif
      expanded_stream.put_str (tokenTxt);

      resolveSymbol ();
   }

   closeSubInput ();

   if (tokenKind == finalToken)
   {
      getSimpleToken (); // skip finalToken
   }
   else
   {
      #if 0
      if (opt.showExpansionDetails)
         info ("on " + tokenKindToStr (tokenKind) + " " + quoteStr (tokenTxt) + ", input = " + input->getInfo());
      #endif
      showPositions ();
      error ("finalToken expected - internal bug");
   }

   if (dupl_input)
      dupl_input_level --;

   return expanded_stream.to_string ();
}

void EnvInput::expandParameters (StrSubInput * macro_input, CondSymbol * symbol) // @@
{
   getSimpleToken (); // skip macro name, move to left parenthesis
   assert (isSeparator ('('));
   // NO getSimpleToken (); // keep left parenthesis

   CondParam * param = symbol->first_param;
   bool finish = false;

   if (param == NULL)
      getSimpleToken (); // skip left parenthesis, important

   #if 0
   if (opt.showExpansionDetails)
      if (param == NULL)
         info ("macro with zero parameters " +  symbol->name);
      else
         info ("macro with some parameters " +  symbol->name);
   #endif

   while (param != NULL && ! finish)
   {
      // inpCh is first character of current parameter
      // tokenKind, tokenTxt is old token

      // expand one parameter
      string orig_value = readParameter (param->multi);
      string expanded_value = expandParameter (orig_value);

      // store parameter value
      CondSymbol * sym = macro_input->local_symbols.defineNewSymbol (param->name, expanded_value);
      sym->local_param = true;
      sym->orig_value = orig_value;

      if (opt.showExpansionDetails)
         explain ("macro_param", "parameter", symbol->name + "." + param->name + " = " + expanded_value);

      param = param->next;

      // check comma (parameter separator)
      if (param != NULL)
      {
         if (param->multi && isSeparator (')'))
         {
            // special case multi parameter, but without value
            CondSymbol * sym = macro_input->local_symbols.defineNewSymbol (param->name, "");
            sym->local_param = true;
            finish = true;  // end of loop
         }

         if (! finish && ! isSeparator (','))
         {
            #if 0
            if (opt.showExpansionDetails)
               info ("on " + tokenKindToStr (tokenKind) + " " + quoteStr (tokenTxt));
            #endif
            error ("',' expected (in macro expansion of " + symbol->name + "." + param->name + ")");
         }
         // NO getSimpleToken (); // keep comma as current token
      }
   }

   if (! isSeparator (')'))
   {
      #if 0
      if (opt.showExpansionDetails)
         info ("on " + tokenKindToStr (tokenKind) + " " + quoteStr (tokenTxt));
      #endif
      error ("')' expected (in macro expansion of " + symbol->name + ")");
   }
   // NO getSimpleToken (); // keep right parenthesis token on input
}

string EnvInput::compoundItem (StrSubInput * macro_input, const string name)
{
   string result;

   CondSymbol * symbol = macro_input->local_symbols.searchSymbol (name);

   if (symbol == NULL)
      result = name;
   else if (symbol->local_param)
      result = symbol->orig_value;
   else
      result = symbol->value;

   if (opt.showExpansionDetails)
      explain ("macro_detail", "compound item", name + " --> " + result);

   return result;
}

void EnvInput::stringSymbol (StrSubInput * macro_input) // @@
{
   getSimpleToken (); // skip hash mark

   if (tokenKind != nameToken)
      error ("Identifier expected after hash mark");

   string name = tokenTxt;
   CondSymbol * symbol = macroSearchSymbol (macro_input, name);

   if (symbol == NULL)
   {
      error ("Undefined symbol after hash mark: " + name);
   }
   else
   {
      if (dupl_input)
      {
         dupl_input_level ++;
         addRemark ("~~>");
      }

      string t = "";

      if (symbol->local_param)
         t = quoteStr (symbol->orig_value); // use non-expanded parameter value
      else
         t = quoteStr (symbol->value);

      openText (t, false);
      getSimpleToken (); // skip original token

      if (dupl_input)
         dupl_input_level --;

      if (opt.showExpansionDetails)
         explain ("macro_detail", "string", t);
   }
}

void EnvInput::compoundSymbol (StrSubInput * macro_input) // @@
{
   getSimpleToken ();

   // spaces around hash mark(s) are removed during macro definitions

   if (opt.hashDirectives && isSeparator ('#'))
   {
      stringSymbol (macro_input);
   }
   else
   {
      // inpCh ... next character after current token

      if (condValue &&
          tokenKind == nameToken &&
          opt.hashDirectives &&
          inpCh == '#')
      {
         /* collect values from concatenated symbols */
         string compound_value = compoundItem (macro_input, tokenTxt);

         while (inpCh == '#')
         {
            getSimpleToken (); // read first hash mark

            if (inpCh != '#')
            {
               // error ("Two hash marks expected: " + quoteStr (charToStr (inpCh)));
               stringSymbol (macro_input);
            }
            else
            {
                getSimpleToken ();  // read second hash mark

                getSimpleToken (); // read next token (identifier)

                // NO if (tokenKind != nameToken)
                //    error ("Identifier expected after hash marks: "+ quoteStr (tokenTxt));
            }

            compound_value += compoundItem (macro_input, tokenTxt);
         }

         if (dupl_input)
         {
            dupl_input_level ++;
            addRemark ("~~>");
         }

         /* lookup compound symbol */
         CondSymbol * symbol = localSearchSymbol (compound_value);

         if (symbol != NULL)
         {
            compound_value = symbol->value;
            if (opt.showExpansionDetails)
               explain ("macro_detail", "compound symbol", symbol->name + " --> " + symbol->value);
         }

         /* use collected value as new input */
         openText (compound_value, false);

         getSimpleToken (); // skip previous identifier
                            // do it after openText, otherwise one token after compound name is lost
         if (dupl_input)
            dupl_input_level --;
      }
   }
}

void EnvInput::expandAgain (CondSymbol * symbol, StrSubInput * macro_input) // @@
{
   TextStorage expanded_stream;

   openText (symbol->value, true);

   compoundSymbol (macro_input); // skip right parenthesis (after openMacro)

   while (tokenKind != startToken &&
          tokenKind != stopToken &&
          tokenKind != finalToken &&
          tokenKind != eofToken)
   {
      CondSymbol * sym = NULL;

      // search in local symbols
      if (tokenKind == nameToken)
         sym = macro_input->local_symbols.searchSymbol (tokenTxt);

      if (sym != NULL)
         expanded_stream.put_str (sym->value);
      else
         expanded_stream.put_str (tokenTxt);

      compoundSymbol (macro_input);
   }

   closeSubInput ();

   assert (tokenKind == finalToken);
   // NO getSimpleToken (); // keep finalToken

   macro_input->value = expanded_stream.to_string (); // store pre-expanded text
}

void EnvInput::expandSymbol (CondSymbol * symbol) // @@
{
   if (opt.showMacroExpansion)
      explain ("macro_use", "use", defineToText (symbol));

   StrSubInput * macro_input = new StrSubInput (); // !? delete
   macro_input->title = symbol->name;
   macro_input->value = symbol->value; // value for "not function like" macros

   // copy location
   macro_input->positionInitialized = true;

   macro_input->fileInx = symbol->fileInx;
   macro_input->linePos = symbol->linePos;
   macro_input->colPos  = symbol->colPos;
   macro_input->charPos = symbol->charPos;

   macro_input->tokenFileInx = symbol->fileInx;
   macro_input->tokenLinePos = symbol->linePos;
   macro_input->tokenColPos  = symbol->colPos;
   macro_input->tokenCharPos = symbol->charPos;

   // without parameters, leave macro name as current token
   // with parameters, leave right parenthesis as current token
   // skip this token after sub-input is opened

   bool only_macro_name = false;

   // parameters
   if (symbol->with_params)
   {
      // skip spaces
      while (! inpEof && inpCh <= ' ' && inpCh != cr && inpCh != lf)
         nextCh ();

      if (inpCh != '(')
         // spaces after symbol name are ignored
         only_macro_name = true;
      else
         expandParameters (macro_input, symbol);
   }

   if (only_macro_name)
   {
      delete macro_input;
      macro_input = NULL;
   }
   else
   {
      if (dupl_input)
      {
         dupl_input_level ++;
         addRemark ("-->");
      }

      // expand parameters and compund names in macro
      expandAgain (symbol, macro_input);

      if (dupl_input)
         addRemark ("--->");

      if (opt.showMacroExpansion)
         explain ("macro_expansion", "expansion", macro_input->value);

      if (dupl_input)
         dupl_input_level --;

      // expand macro
      openMacro (macro_input, false);

      resolveSymbol (); // skip right parenthesis (after openMacro)
                        // use resolveSymbol to expand following token
   }
}

void EnvInput::resolveSymbol () // @@
{
   // read macro identifier with parameters ( or read one another token )

   getSimpleToken ();

   #if 0
   if (opt.showExpansionDetails)
      info ("resolveSymbol: " + quoteStr (tokenTxt));
   #endif

   if (tokenKind == nameToken && condValue)
   {
      // search symbol definition
      string symbol_name = tokenTxt;
      CondSymbol * symbol = NULL;
      if (! opt.ignoreMacroExpansion)
      {
         if (symbol_name == "__FILE__")
            setStringToken (quoteStr (recallFileName (real_input->tokenFileInx)));
            // first_input - original source file_name
            // input - possible macro in another file
         else if (symbol_name == "__LINE__")
            setStringToken (IntToStr (real_input->tokenLinePos));
         else
            symbol = localSearchSymbol (symbol_name);
      }

      // check recursion
      if (symbol != NULL)
      {
         SubInput * temp = input;
         while (temp != NULL)
         {
            if (symbol_name == temp->title)
               symbol = NULL; // no recursion allowed
            temp = temp->prev;
         }
      }

      // selective expansion (e.g. only in directives, or not for some names)
      if (symbol != NULL && ! symbol->local_param && ! expandMacro (symbol))
         symbol = NULL;

      // read parameters and expand macro
      if (symbol != NULL)
         expandSymbol (symbol);
   }

   #if 0
      if (opt.showExpansionDetails)
         info ("resolveSymbol next character " + quoteStr (charToStr (inpCh)));
   #endif
}

/* ---------------------------------------------------------------------- */

void EnvInput::skipSpaces ()
{
   while (tokenKind == spaceToken ||
          tokenKind == commentToken ||
          tokenKind == lineContToken)
   {
      getSimpleToken ();
   }
}

void EnvInput::checkEndOfLine ()
{
   skipSpaces ();

   if (! opt.tolerateMissingEndOfLine)
      if (tokenKind != eolToken &&
          tokenKind != stopToken &&
          tokenKind != eofToken)
      {
         error ("End of line (after directive) expected"
                ", tokenTxt = " + tokenTxt +
                ", tokenKind = " + tokenKindToStr (tokenKind));
      }
}

/********************************** DEFINE ********************************/

bool EnvInput::threeDots ()
{
   bool result;
   if (compound_separators)
   {
       result = isSeparatorToken() && tokenTxt == "...";
       if (result)
          getSimpleToken ();
   }
   else
   {
      result = isSeparator ('.');

      if (result)
      {
         getSimpleToken ();

         if (! isSeparator ('.'))
            error ("'...' expected");

         getSimpleToken ();

         if (! isSeparator ('.'))
            error ("'...' expected");

         getSimpleToken ();
      }
   }
   return result;
}

void EnvInput::defineParameter (CondSymbol * symbol)
{
   string name = "";
   bool multi = false;

   if (threeDots ())
   {
       name = "__VA_ARGS__";
       multi = true;
   }
   else
   {
      if (tokenKind != nameToken)
         error ("Parameter identifier expected");

      name = tokenTxt;
      getSimpleToken (); // skip parameter name
      skipSpaces ();

      if (threeDots ())
      {
         multi = true;
         skipSpaces ();
      }
   }

   // debug ("defineParameter " + name);
   symbol->insParam (name, multi);
}

string EnvInput::parametersToText (CondSymbol * symbol)
{
   string txt = "";

   if (symbol->with_params)
   {
      txt += "(";
      CondParam * param = symbol->first_param;
      while (param != NULL)
      {
         if (param->multi)
            txt += "...";
         else
            txt += param->name;

         param = param->next;

         if (param != NULL)
            txt += ",";
      }
      txt += ")";
   }

   return txt;
}

string EnvInput::defineToText (CondSymbol * symbol)
{
   string txt = symbol->name +parametersToText(symbol) + " ";
   // txt += + "--> ";
   txt += symbol->value;
   return txt;
}

void EnvInput::defineDirective ()
{
   int cont_count = 0;
   getSimpleToken (); // skip define
   skipSpaces ();

   if (tokenKind != nameToken)
      error ("Identifier expected");

   CondSymbol * symbol = new CondSymbol ();
   symbol->name = tokenTxt;

   // debug ("defineDirective " + tokenTxt);

   symbol->with_params = (inpCh == '('); // parenthesis without space
   getSimpleToken (); // skip symbol name
   skipSpaces ();

   if (symbol->with_params)
   {
      getSimpleToken (); // skip '('
      skipSpaces ();

      if (! isSeparator (')'))
      {
         defineParameter (symbol);
         while (isSeparator (','))
         {
            if (symbol->last_param->multi)
               error ("'...' must be last parameter");
            getSimpleToken ();
            skipSpaces ();
            defineParameter (symbol);
         }
      }

      if (! isSeparator (')'))
         error ("')' expected (in macro definition))");

      getSimpleToken ();
      skipSpaces ();
   }

   assert (input != NULL);
   symbol->fileName = input->getFileName ();
   symbol->fileInx = input->fileInx;
   symbol->linePos = input->linePos;
   symbol->colPos  = input->colPos;
   symbol->charPos = input->charPos;

   // collect value, trim white spaces
   bool inside = false;
   bool space = false;
   bool ignore_space = false;
   string value = "";

   while (tokenKind != eolToken &&
          tokenKind != stopToken &&
          tokenKind != finalToken &&
          tokenKind != eofToken)
   {
      if (tokenKind == lineContToken)
         cont_count ++;

      if (tokenKind == spaceToken || tokenKind == commentToken || tokenKind == lineContToken)
      {
         if (inside) // skip leading spaces
            space = true;
      }
      else
      {
         if (tokenTxt == "#") // !?
            ignore_space = true; // ignore space before ##

         if (space && ! ignore_space)
            value += " ";

         value += tokenTxt;

         inside = true;
         space = false;
         ignore_space = (tokenTxt == "#" || tokenTxt == "##"); // ignore space after # or ##
      }

      // skip trailing space
      getSimpleToken ();
   }

   symbol->value = value;

   if (condValue) // is it valid source section
   {
      assert (input != NULL);
      symbols.undefineSymbol (symbol->name);
      symbols.insSymbol (symbol);

      if (opt.showDefinitions)
         explain ("directive", "define", defineToText (symbol));
   }
   else
   {
      delete symbol; // !?
   }
}

void EnvInput::undefDirective ()
{
   getSimpleToken (); // skip undef
   skipSpaces ();

   if (tokenKind != nameToken)
      error ("Identifier expected");

   if (condValue) // is it valid source section
   {
      symbols.undefineSymbol (tokenTxt);

      if (opt.showDefinitions)
         explain ("directive", "undef", tokenTxt);
   }

   getSimpleToken (); // skip symbol name
   checkEndOfLine ();
}

/****************************** EXPRESSIONS *******************************/

void EnvInput::getExprToken () // @@
{
   again:

   resolveSymbol ();

   if (tokenKind == lineContToken) line_cont ++;

   if (tokenKind == startToken) goto again;
   if (tokenKind == stopToken) goto again;
   if (tokenKind == commentToken) goto again;
   if (tokenKind == lineContToken) goto again;
   if (tokenKind == spaceToken) goto again;
}

/* ---------------------------------------------------------------------- */

bool EnvInput::twoSeparators (char c1, char c2)
{
    bool result;
    if (compound_separators)
    {
       result = isSeparatorToken () &&
                tokenTxt.length () == 2 &&
                tokenTxt [0] == c1 &&
                tokenTxt [1] == c2;
    }
    else
    {
       result = isSeparator (c1) && (inpCh == c2);
    }
    return result;
}

void EnvInput::skipTwoSeparators ()
{
   getExprToken ();
   if (! compound_separators)
      getExprToken ();
}

bool EnvInput::condSymbolDefined ()
{
   if (tokenKind != nameToken || tokenTxt == "defined")
      error ("Identifier of conditional symbol expected");

   // search identifier
   CondSymbol * symbol = localSearchSymbol (tokenTxt);
   bool result = (symbol != NULL);

   getExprToken (); // skip identifier

   return result;
}

int EnvInput::condIdent (bool cont)
{
   if (tokenKind != nameToken || tokenTxt == "defined")
      error ("Identifier of conditional symbol expected");

   // search identifier
   CondSymbol * symbol = localSearchSymbol (tokenTxt);

   // !? !! BUG
   if (symbol != NULL && isValidIdent (symbol->value))
      symbol = localSearchSymbol (symbol->value);

   int result = 0;

   if (symbol == NULL)
   {
      if (opt.requireSymbolDefinition && cont)
         error ("Unknown conditional symbol: " + tokenTxt);
         // cont == false => symbol need not exist
   }
   else
   {
      bool ok;
      StrToInt (symbol->value, result, ok);
      if (! ok && opt.requireSymbolDefinition && cont)
         error ("Numeric conditional symbol expected: " + tokenTxt + " (" + symbol->value + ")");
   }

   getExprToken (); // skip identifier

   if (! cont)
   {
      // macro parameters of possible undefined macro identifier
      if (isSeparator ('('))
      {
         getExprToken (); // skip left parenthesis

         int level = 0;
         while ( level > 0 || ! isSeparator (')') )
         {
            if (isSeparator ('(')) level ++;
            if (isSeparator (')')) level --;

            getExprToken (); // next token
         }

         if (! isSeparator (')'))
            error ("')' expected");

         getExprToken (); // skip right parenthesis
      }
   }

   return result;
}

/* ---------------------------------------------------------------------- */

int EnvInput::condHasInclude ()
{
   // __has_include ("file") or __has_include (<file>), file name without macro expansion
   getSimpleToken (); // skip __has_include
   skipSpaces ();

   if (! isSeparator ('('))
      error ("'(' expected (in __has_include)");

   getSimpleToken (); // skip parenthesis
   skipSpaces ();

   string name = "";
   bool system_file = false;

   if (tokenKind == stringToken)
   {
      name = tokenVal;
      getSimpleToken (); // skip string
   }
   else if (isSeparator ('<'))
   {
      system_file = true;
      getSimpleToken (); // skip '<'
      while (tokenKind != eolToken &&
             tokenKind != stopToken &&
             tokenKind != finalToken &&
             tokenKind != eofToken &&
             ! isSeparator ('>'))
      {
         name = name + tokenTxt;
         getSimpleToken ();
      }

      if (! isSeparator ('>'))
         error ("'>' expected (in __has_include)");

      getSimpleToken (); // skip '>'
   }
   else
   {
      error ("File name expected (in __has_include)");
   }

   skipSpaces ();
   if (! isSeparator (')'))
      error ("')' expected (in __has_include)");

   getExprToken (); // skip parenthesis, expand symbol

   assert (real_input != NULL);
   string dir = extractPath (real_input->getFileName ());
   string found = incl_directories.lookupInclFile (name, dir, system_file);

   if (found != "")
      return 1;
   else
      return 0;
}

/* ---------------------------------------------------------------------- */

int EnvInput::condSimpleExpr (bool cont)
{
   int result = 0;

   if (tokenKind == numberToken)
   {
      string txt = tokenTxt;
      int len = txt.length ();
      int inx = len;

      while (inx > 1 &&
             (txt [inx-1] == 'l' ||
              txt [inx-1] == 'L' ||
              txt [inx-1] == 'u' ||
              txt [inx-1] == 'U' ))
      {
         inx--;
      }

      if (inx < len)
         txt = Head (txt, inx);

      bool ok = StrToIntOk (txt, result);
      if (! ok)
      {
         unsigned long temp;
         StrToULong (txt, temp, ok);
         if (ok)
            result = temp;
         else
            error ("Invalid number: " + txt);
      }
      getExprToken (); // skip number
   }
   else if (tokenKind == nameToken)
   {
      if (tokenTxt == "defined")
      {
         getSimpleToken (); // skip defined, no macro expansion
         skipSpaces ();

         if (isSeparator ('('))
         {
            getSimpleToken (); // skip parenthesis, no macro expansion
            skipSpaces ();

            result = condSymbolDefined ();
            if (! isSeparator (')'))
               error ("')' expected (in defined)");

            getExprToken (); // skip parenthesis, expand symbol
         }
         else
         {
            result = condSymbolDefined ();
         }
      }
      else if ((tokenTxt == "__has_include" || tokenTxt == "__has_include_next") &&
               localSearchSymbol (tokenTxt) == NULL)
      {
         result = condHasInclude ();
      }
      else
      {
          result = condIdent (cont);

          #if 0
          if (! cont) // read possible macro arguments
          {
             if (isSeparator ('('))
             {
                int level = 1;

                while (level > 0)
                {
                   getSimpleToken (); // skip parenthesis, no macro expansion

                   if (isSeparator ('('))
                      level ++;

                   if (isSeparator (')'))
                      level --;
                }

                getExprToken (); // skip parenthesis, expand symbol
             }
          }
          #endif
      }
   }
   else if (isSeparator ('!'))
   {
      getExprToken (); // skip exclamation mark
      result = ! condSimpleExpr (cont);
   }
   else if (isSeparator ('~'))
   {
      getExprToken (); // skip exclamation mark
      result = ~ condSimpleExpr (cont);
   }
   else if (isSeparator ('-'))
   {
      getExprToken (); // skip unary minus
      result = - condSimpleExpr (cont);
   }
   else if (isSeparator ('+'))
   {
      getExprToken (); // skip unary plus
      result = condSimpleExpr (cont);
   }
   else if (isSeparator ('('))
   {
      getExprToken (); // skip left parenthesis
      result = condExpression (cont);
      if (! isSeparator (')'))
         error ("')' expected (in subexpression): " + tokenTxt);
      getExprToken (); // skip right parenthesis
   }
   else error ("Simple conditional expression expected: " + tokenTxt);
                // ", tokenTxt = " + tokenTxt +
                // ", tokenKind = " + tokenKindToStr (tokenKind));

   return result;
}

int EnvInput::condFactor (bool cont)
{
   int result = condSimpleExpr (cont);

   while (isSeparator ('*') || isSeparator ('/') || isSeparator ('%'))
   {
      char mark = tokenSym;
      getExprToken ();

      int temp = condSimpleExpr (cont);

      // !?
      if (mark == '*')
      {
         result = result * temp;
      }
      else
      {
         if (temp == 0)
         {
            if (cont)
               error ("Zero divide");
            result = 0; // value is not used (cont == false)
         }
         else if (mark == '/')
            result = result / temp;
         else
            result = result % temp;
      }
   }

   return result;
}

int EnvInput::condTerm (bool cont)
{
   int result = condFactor (cont);

   while (isSeparator ('+') || isSeparator ('-'))
   {
      char mark = tokenSym;
      getExprToken ();

      int temp = condFactor (cont);

      if (mark == '+')
         result = result + temp;
      else
         result = result - temp;
   }

   return result;
}

int EnvInput::condShift (bool cont)
{
   int result = condTerm (cont);

   while (twoSeparators ('<', '<') || twoSeparators ('>', '>'))
   {
      char left = twoSeparators ('<', '<');
      skipTwoSeparators ();

      int temp = condTerm (cont);

      if (left)
         result = result << temp;
      else
         result = result >> temp;
   }

   return result;
}

int EnvInput::condRel (bool cont)
{
   int result = condShift (cont);

   while (isSeparator ('<') || isSeparator ('>'))
   {
      char mark = tokenSym;
      getExprToken (); // skip first

      char mark2 = ' ';
      if (isSeparator ('='))
      {
         mark2 = tokenSym;
         getExprToken (); // skip second
      }

      int temp = condShift (cont);

      if (mark == '<')
      {
         if (mark2 == '=')
            result = (result <= temp);
         else
            result = (result < temp);
      }
      else
      {
         if (mark2 == '=')
            result = (result >= temp);
         else
            result = (result > temp);
      }
   }

   return result;
}

int EnvInput::condEq (bool cont)
{
   int result = condRel (cont);

   while (twoSeparators ('=', '=') || twoSeparators ('!', '=') )
   {
      bool eq = twoSeparators ('=', '=');
      skipTwoSeparators ();

      int temp = condRel (cont);

      if (eq)
         result = (result == temp);
      else
         result = (result != temp);
   }

   return result;
}

int EnvInput::condAnd (bool cont)
{
   int result = condEq (cont);

   while (isSeparator ('&') && ! twoSeparators ('&', '&'))
   {
      getExprToken (); // skip &

      int temp = condEq (cont);
      result = result & temp;
   }

   return result;
}

int EnvInput::condXor (bool cont)
{
   int result = condAnd (cont);

   while (isSeparator ('^'))
   {
      getExprToken (); // skip ^

      int temp = condAnd (cont);
      result = result ^ temp;
   }

   return result;
}

int EnvInput::condOr (bool cont)
{
   int result = condXor (cont);

   while (isSeparator ('|') && ! twoSeparators ('|', '|'))
   {
      getExprToken (); // skip |

      int temp = condXor (cont);
      result = result | temp;
   }

   return result;
}

int EnvInput::condLogAnd (bool cont)
{
   int result = condOr (cont);

   while (twoSeparators ('&', '&'))
   {
      skipTwoSeparators ();

      int temp = condOr (cont && result);
      result = result && temp;
   }

   return result;
}

int EnvInput::condLogOr (bool cont)
{
   int result = condLogAnd (cont);

   while (twoSeparators ('|', '|'))
   {
      skipTwoSeparators ();

      int temp = condLogAnd (cont && ! result);
      result = result || temp;
   }

   return result;
}

int EnvInput::condExpression (bool cont)
{
   int result = condLogOr (cont);

   if (isSeparator ('?'))
   {
      // debug ("QUESTION mark");
      getExprToken (); // skip

      // getSimpleToken();
      int branch1 = condLogOr (cont && result);

      // DO NOT USE checkSeparator (which uses getToken)
      if (! isSeparator (':'))
         error ("Colon expected");

      // debug ("COLON");
      getExprToken (); // skip

      int branch2 = condLogOr (cont && ! result);

      result = result ? branch1 : branch2;
   }

   return result;
}

/************************* CONDITIONAL DIRECTIVES *************************/

void EnvInput::condDirective (bool inv, bool only_symbol)
{
   bool value;

   if (only_symbol)
   {
      getSimpleToken (); // skip if, no macro expansion
      skipSpaces ();

      if (real_input->guard_state == open_guard)
      {
         // second part of first ifndef
         real_input->guard_name = tokenTxt; // remember variable name
         real_input->guard_state = inside_guard;
      }

      value = condSymbolDefined ();
   }
   else
   {
      getExprToken (); // skip if and expand next symbol
      value = condExpression (condValue); // be tolerant to unknown symbols and macros, when condValue == false
   }

   if (inv)
      value = ! value;

   if (condTable.level+1 > cond_level_max)
      error ("Too many nested conditional directives");

   condTable.addCondLevel (value);

   if (opt.showOtherDirectives)
      explain ("branch_directive", inv ? "ifndef" : "ifdef", "");

   checkEndOfLine ();
}

/* ---------------------------------------------------------------------- */

void EnvInput::ifDirective ()
{
   condDirective (false, false); // condDirective (inversion, only_symbol)
}

void EnvInput::ifdefDirective ()
{
   condDirective (false, true);
}

void EnvInput::ifndefDirective ()
{
   if (real_input->guard_state == before_guard)
   {
      // first ifndef encountered
      real_input->guard_state = open_guard;
      real_input->guard_level = condTable.level + 1;
   }

   condDirective (true, true);
}

void EnvInput::elifDirective ()
{
   if (real_input->guard_state == inside_guard &&
       condTable.level == real_input->guard_level)
   {
      real_input->guard_state = wrong_guard;
      // first ifndef cannot have elif
   }

   if (condTable.current_level == NULL)
      error ("elif directive without if directive");

   if (condTable.current_level->value)
      condTable.current_level->done = true;

   if (condTable.current_level->done)
   {
      // only read condition and skip following conditional section
      // debug ("Before reading expression");
      getExprToken (); // skip elif and expand next symbol
      condExpression (false);
      condTable.current_level->value = false;
      // debug ("After reading expression");
   }
   else
   {
      // debug ("Before expression");
      condValue = true; // importat, turn on conditional compilation (before reading first macro symbol)
      getExprToken (); // skip elif and expand next symbol
      condTable.current_level->value = condExpression ();
      // debug ("After expression");
   }

   if (opt.showOtherDirectives)
      explain ("branch_directive", "elif", "");

   checkEndOfLine ();
}

void EnvInput::elseDirective ()
{
   if (real_input->guard_state == inside_guard &&
      condTable.level == real_input->guard_level)
   {
      real_input->guard_state = wrong_guard;
      // first ifndef cannot have else
   }

   getSimpleToken (); // skip else

   if (condTable.current_level == NULL)
      error ("else directive without if directive");

   if (condTable.current_level->value)
      condTable.current_level->done = true;

   condTable.current_level->value = ! condTable.current_level->done;

   if (opt.showOtherDirectives)
      explain ("branch_directive", "else", "");

   checkEndOfLine ();
}

void EnvInput::endifDirective ()
{
   if (real_input->guard_state == inside_guard &&
       condTable.level == real_input->guard_level)
   {
      real_input->guard_state = close_guard;
      // last endif encountered
   }

   getSimpleToken (); // skip endif

   if (condTable.current_level == NULL)
      error ("endif directive without if directive");
   else
      condTable.removeCondLevel ();

   if (opt.showOtherDirectives)
      explain ("branch_directive", "endif", "");

   checkEndOfLine ();
}

/******************************** INCLUDE *********************************/

void EnvInput::includeDirective (bool include_next) // @@
{
   if (! condValue)
   {
      getSimpleToken (); // skip include
      skipSpaces ();
   }

   if (condValue) // valid source section
   {
      // skip spaces
      while (! inpEof && inpCh <= ' ' && inpCh != cr && inpCh != lf)
         nextCh ();

      bool simple = (inpCh == quote2 || inpCh == '<');

      // simple == false => expand macro names
      // #define _MULTIARCH_HEADER(arch,name) <arch-name>
      // #include _MULTIARCH_HEADER(i386,name)

      // simple == true => do not expand macro names within < >
      // #define linux 1
      // #include <linux/limits.h>

      if (simple)
         getSimpleToken ();
      else
         getExprToken (); // skip include and expand next symbol

      // check only if enabled input, important for <file name>

      string symbolic_name = "";
      string exact_name = "";
      string name = "";
      bool   system_dir = false;

      if (tokenKind == stringToken)
      {
         symbolic_name = tokenTxt;
         exact_name = tokenTxt;
         name = tokenVal;
      }
      else if (isSeparator ('<'))
      {
         if (simple)
            getSimpleToken ();
         else
            getExprToken (); // skip '<'

         exact_name = "<";

         while (tokenKind != eolToken &&
                tokenKind != stopToken &&
                tokenKind != finalToken &&
                tokenKind != eofToken &&
                ! isSeparator ('>'))
         {
            name = name + tokenTxt;
            exact_name = exact_name + tokenTxt;
            if (simple)
               getSimpleToken ();
            else
               getExprToken (); // store character also into input_storage
         }

         exact_name = exact_name + ">";

         if (! isSeparator ('>'))
            error ("'>' expected");

         symbolic_name = '<' + name + '>';
         system_dir = true;
      }
      else
      {
         error ("File name expected: " + tokenTxt);
      }

      getSimpleToken ();
      checkEndOfLine (); // check end of line, but do not move to another line
      inside_directive = false; // stop reporting end of line

      // if (opt.showIncludes)
      //    explain ("include_directive", "include", symbolic_name);

      string orig_name = name;

      if (! opt.reportIncludes)
      {
         if (! opt.ignoreIncludes && ! opt.reportIncludes)
         {
            assert (input != NULL);
            assert (real_input != NULL);
            string dir = extractPath (real_input->getFileName ());

            name = translatePath (name);
            if (! include_next)
            {
               // debug ("Searching " + name);
               name = incl_directories.lookupInclFile (name, dir, system_dir);
            }
            else
            {
               string this_file_name = input->orig_include_name;
               string next_file_name = name;
               if (opt.showInclNext)
                  explain ("include_directive", "include_next", this_file_name + " and then " + next_file_name);
               name = incl_directories.lookupInclFile (this_file_name, dir, system_dir, next_file_name, opt.showInclNext);
               if (opt.showInclNext && name != "")
                  explain ("include_directive", "include_next_found", name);
            }

            if (name == "" && (! opt.tolerateIncludes || (opt.tolerateOnlySystemIncludes && ! system_dir)))
               error ("Cannot open include file: " + symbolic_name);
         }
         else
         {
            name = "";
         }
      }

      if (name == "")
      {
         unknownInclude (symbolic_name);
         if (opt.showIncludes)
            explain ("include_directive", "include", symbolic_name);
      }
      else if (opt.reportIncludes)
      {
         // report include directive (without processing)
         // setIncludeDirectiveToken (name); // (with translated file name)
         setIncludeDirectiveToken (exact_name); // (with file name in quotes or angle parenthesis)
      }
      else
      {
         name = queryInclude (name); // optional file name transformation

         // empty name => skip include file
         // ( used for already processed files )

         if (name != "")
         {
            if (opt.showIncludes)
               explain ("include_directive", "opening", symbolic_name);
            openInclude (name, orig_name);
         }
      }
   }
}

/**************************** OTHER DIRECTIVES ****************************/

/* cecko: #line N "soubor" - nasledujici radek je radek N souboru (cmm.bin: predzpracovana
   prekladova jednotka se sablonami z hlavicek, chyby hlasi puvodni soubor a radek) */
void EnvInput::lineDirective ()
{
   getSimpleToken (); // skip line
   skipSpaces ();
   int n = 0;
   bool ok = false;
   if (tokenKind == numberToken) StrToInt (tokenTxt, n, ok);
   if (! ok)
   {
      error ("Line number expected");
      return;
   }
   getSimpleToken ();
   skipSpaces ();
   string file = "";
   if (tokenKind == stringToken)
   {
      file = tokenTxt;
      if (file.length () >= 2 && file [0] == '"' && file [file.length () - 1] == '"')
         file = file.substr (1, file.length () - 2);
      getSimpleToken ();
      skipSpaces ();
   }
   if (condValue && inp != NULL)
   {
      inp->linePos = n;   // konec radku direktivy uz precten
      if (file != "") inp->fileInx = storeFileName (file);
   }
}

void EnvInput::pragmaDirective ()
{
   // string name1 = tokenTxt;
   getSimpleToken (); // skip pragma
   skipSpaces ();

   string name2 = tokenTxt;
   // no GetInnerToken (); // skip name

   if (! customPragma (name2))
   {
      // read remaining text
      string txt;
      while (tokenKind != eolToken &&
             tokenKind != stopToken &&
             tokenKind != finalToken &&
             tokenKind != eofToken)
      {
         txt = txt + tokenTxt;
         getSimpleToken ();
      }
   }

   if (opt.showOtherDirectives)
      explain ("directive", "pragma", "");
}

/* ---------------------------------------------------------------------- */

void EnvInput::warningDirective ()
{
   getSimpleToken (); // skip name
   skipSpaces ();

   string txt;

   while (tokenKind != eolToken &&
          tokenKind != stopToken &&
          tokenKind != finalToken &&
          tokenKind != eofToken)
   {
      txt = txt + tokenTxt;
      getSimpleToken ();
   }

   if (condValue && ! opt.ignoreWarningDirectives)
      warning (txt);

   if (opt.showOtherDirectives)
      explain ("directive", "warning", txt);
}

void EnvInput::errorDirective ()
{
   getSimpleToken (); // skip name
   skipSpaces ();

   string txt;

   while (tokenKind != eolToken && tokenKind != stopToken && tokenKind != eofToken)
   {
      txt = txt + tokenTxt;
      getSimpleToken ();
   }

   if (condValue && ! opt.ignoreErrorDirectives)
      error (txt);

   if (opt.showOtherDirectives)
      explain ("directive", "error", txt);
}

void EnvInput::includeDirDirective ()
{
   // info ("INCLUDE DIR DIRECTIVE");

   getSimpleToken (); // skip include_dir
   skipSpaces ();

   if (tokenKind != stringToken)
      error ("String expected");

   if (condValue) // is it valid source section
   {
      // info ("INCLUDE DIR " + tokenVal);
      incl_directories.addInclDir (tokenVal);
   }

   getSimpleToken (); // skip symbol name
   checkEndOfLine ();
}

/* ---------------------------------------------------------------------- */

void EnvInput::extraCh ()
{
   tokenTxt += inpCh; // !?
   tokenSym = 0; // multi character

   #ifdef DUPL_OUTPUT
      if (dupl_output)
         output_storage.put (inpCh);
   #endif

   nextCh ();
}

string EnvInput::getGuardSymbol ()
{
   // !? !!
   if (real_input->guard_state == after_guard)
      return real_input->guard_name;
   else
      return "";
}

/******************************* GET OKEN ********************************/

void EnvInput::getToken ()
{
   assert (input != NULL);
   input->prevFileInx = input->tokenFileInx;
   input->prevLinePos = input->tokenLinePos;
   input->prevColPos  = input->tokenColPos;
   input->prevCharPos = input->tokenCharPos;

   again:

   resolveSymbol (); // read one token

   string name = "";

   if ((isSeparator ('#') && opt.hashDirectives && ! twoSeparators ('#', '#')) || // !?
       (isSeparator ('@') && opt.atDirectives) ||
       (isSeparator ('$') && opt.dollarDirectives))
   {
      assert (input != NULL);
      int SaveFileInx = input->tokenFileInx;
      int SaveLinePos = input->tokenLinePos;
      int SaveColPos  = input->tokenColPos;
      int SaveCharPos = input->tokenCharPos;

      if (opt.keepUnusedSections)
      {
         dupl_directives = true;
         directive_storage.put_str (tokenTxt);
      }

      line_cont = 0;
      inside_directive = true; // report end of line

      getSimpleToken (); // skip hash mark ( and comments )
      skipSpaces ();

      if (tokenKind != eolToken)
      {
         if (tokenKind != nameToken)
            error ("Directive name expected");

         name = tokenTxt;

         // info ("Directive: " + name);

         if (name == "define")
            defineDirective ();

         else if (name == "undef")
            undefDirective ();

         else if (name == "if")
            ifDirective ();

         else if (name == "ifdef")
            ifdefDirective ();

         else if (name == "ifndef")
            ifndefDirective ();

         else if (name == "elif")
            elifDirective ();

         else if (name == "else")
            elseDirective ();

         else if (name == "endif")
            endifDirective ();

         else if (name == "include")
            includeDirective ();

         else if (name == "include_next")
            includeDirective (true);

         else if (name == "pragma")
            pragmaDirective ();

         else if (name == "line")
            lineDirective ();

         else if (name == "warning")
            warningDirective ();

         else if (name == "error")
            errorDirective ();

         else if (name == "include_dir")
            includeDirDirective ();

         else if (name == "tolerate_includes")
            {  opt.tolerateIncludes = true;  getSimpleToken (); checkEndOfLine();}

         else if (customDirective (name))
               /* nothing */ ;

         else if (! opt.ignoreUnknownDirectives)
               error ("Unknown directive: " + name);
      }

      inside_directive = false; // stop reporting end of line

      string directive_text = "";
      if (opt.keepUnusedSections)
      {
         directive_text = directive_storage.to_string ();
         directive_storage.reset ();
         dupl_directives = false;
      }

      assert (input != NULL);
      input->tokenFileInx = SaveFileInx;
      input->tokenLinePos = SaveLinePos;
      input->tokenColPos  = SaveColPos;
      input->tokenCharPos = SaveCharPos;

      // calculate value
      condValue = condTable.calculate ();

      // set tokenKind, ... (if not already assigned)
      if (tokenKind != includeDirectiveToken)
      {
          if (opt.keepUnusedSections)
          {
             setUnusedDirectiveToken (directive_text);
          }
          else if (opt.keepEmptySections)
          {
             string txt = "";
             for (int i = 1; i <= line_cont+1; i++)
                txt += lf;
             setUnusedDirectiveToken (txt);
          }
          else
          {
             setProcessedDirectiveToken ();
          }
      }
   }

   // ifdef ... endif guard
   if (real_input->guard_state == before_guard ||
       real_input->guard_state == after_guard)
   {
      if (tokenKind != startToken &&
          tokenKind != commentToken &&
          tokenKind != lineContToken &&
          tokenKind != spaceToken &&
          tokenKind != unusedDirectiveToken &&
          tokenKind != eolToken &&
          tokenKind != stopToken &&
          tokenKind != finalToken &&
          tokenKind != eofToken)
      {
         real_input->guard_state = wrong_guard;
         // only "empty" tokens alowed before first ifdef or after last endif
      }
   }

   if (real_input->guard_state == close_guard)
   {
      real_input->guard_state = after_guard; // after last endif
   }

   // evaluate condition
   if (! condValue)
   {
      if (tokenKind == eofToken)
         error ("Unterminated conditional directive");

      if (! opt.keepUnusedSections)
         if (! opt.keepEmptySections || tokenKind != eolToken)
            goto again;

      tokenKind = unusedDirectiveToken; // change token type
   }

   if (tokenKind == startToken)     goto again;
   if (tokenKind == stopToken)      goto again;
   if (tokenKind == processedDirectiveToken) goto again;

   #ifdef DUPL_OUTPUT
      if (dupl_output)
      {
         #if 0
         output_storage.put_str (quoteStr(tokenTxt));
         if (tokenTxt == "\n")
            output_storage.put ('\n');
         else
            output_storage.put (' ');
         #endif

         output_storage.put_str (tokenTxt);
      }
   #endif

   if (opt.reportSpaces)
   {
      if ((tokenKind == eolToken && ! opt.reportEol) ||
          (tokenKind == commentToken && ! opt.reportComments) ||
          (tokenKind == lineContToken && ! opt.reportLineCont))
       {
          setSpaceToken (" "); // transform token to space
       }
   }

   if (tokenKind == spaceToken    && ! opt.reportSpaces)   goto again;
   if (tokenKind == commentToken  && ! opt.reportComments) goto again;
   if (tokenKind == lineContToken && ! opt.reportLineCont) goto again;
   if (tokenKind == eolToken      && ! opt.reportEol && ! inside_directive) goto again;

   translate ();

   if (opt.showTokens)
      explain ("token", "token", tokenKindToStr (tokenKind) + " " + quoteStr (tokenTxt) /* + " " + quoteChr (tokenSym) */ );
}

/* ---------------------------------------------------------------------- */

CLOSE_NAMESPACE
