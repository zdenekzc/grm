#ifndef PAS_PARSER_H
#define PAS_PARSER_H

#include "lexer.h"
#include "pas_decl.h"
#include <string>
#include <vector>
using std::string;
using std::vector;

class TBasic;
class TExpr;
class TBinaryExpr;
class TComponentsItem;
class TParamItem;
class TModule;
class TLabelIdent;
class TQualName;
class TContName;
class TType;
class TAliasType;
class TStringType;
class TFileType;
class TInxItem;
class TInxList;
class TArgItem;
class TArgSect;
class TElemSect;
class TElemItem;
class TStructSect;
class TIdentExpr;
class TIntValueExpr;
class TFltValueExpr;
class TStrValueExpr;
class TNilExpr;
class TStructExpr;
class TNotExpr;
class TPlusExpr;
class TMinusExpr;
class TAdrExpr;
class TSetExpr;
class TSuperExpr;
class TStringExpr;
class TIndexExpr;
class TCallExpr;
class TDerefExpr;
class TFieldExpr;
class TStat;
class TGotoStat;
class TBlockStat;
class TStatSeq;
class TIfStat;
class TCaseStat;
class TCaseSect;
class TCaseItem;
class TWhileStat;
class TRepeatStat;
class TForStat;
class TWithStat;
class TWithSect;
class TWithItem;
class TRaiseStat;
class TTryStat;
class TFinallyPart;
class TExceptPart;
class TOnSect;
class TOnItem;
class TEmptyStat;
class TAssignStat;
class TCallStat;
class TLabeledTStat;
class TParamIdent;
class TParamSect;
class TClassType;
class TInterfaceType;
class TInterfaceSect;
class TIntefaceItem;
class TComponetsSect;
class TDeclGroup;
class TDeclSect;
class TFieldItem;
class TFieldDecl;
class TPropertyDecl;
class TEnumType;
class TEnumSect;
class TEnumItem;
class TArrayType;
class TIndexTypeSect;
class TIndexTypeItem;
class TRecordType;
class TFieldDeclGroup;
class TPointerType;
class TSetType;
class TClassOfType;
class TProcType;
class TSubrangeType;
class TLabelDecl;
class TLabelSect;
class TConstDecl;
class TConstSect;
class TTypeDecl;
class TTypeSect;
class TVarItem;
class TVarDecl;
class TVarSect;
class TProcDecl;
class TImportItem;
class TImportSect;
class TUnitModule;
class TProgramModule;
class TLibraryModule;
class TTermExpr;
class TSimpleExpr;
class TCompleteExpr;

enum CmmSymbol
{
   eos,
   identifier,
   number,
   real_number,
   character_literal,
   string_literal,
   separator,
   end_of_line,
   LPAREN,
   RPAREN,
   STAR,
   PLUS,
   COMMA,
   MINUS,
   DOT,
   RANGE,
   SLASH,
   COLON,
   ASSIGN,
   SEMICOLON,
   LESS,
   LESS_OR_EQUAL,
   UNEQUAL,
   EQUAL,
   GREATER,
   GREATER_OR_EQUAL,
   ADDRESS,
   LBRACKET,
   RBRACKET,
   ARROW,
   keyword_abstract,
   keyword_and,
   keyword_array,
   keyword_as,
   keyword_automated,
   keyword_begin,
   keyword_case,
   keyword_cdecl,
   keyword_class,
   keyword_const,
   keyword_constructor,
   keyword_default,
   keyword_destructor,
   keyword_div,
   keyword_do,
   keyword_downto,
   keyword_dynamic,
   keyword_else,
   keyword_end,
   keyword_except,
   keyword_external,
   keyword_file,
   keyword_finalization,
   keyword_finally,
   keyword_for,
   keyword_forward,
   keyword_function,
   keyword_goto,
   keyword_if,
   keyword_implementation,
   keyword_implements,
   keyword_in,
   keyword_inherited,
   keyword_initialization,
   keyword_inline,
   keyword_interface,
   keyword_is,
   keyword_label,
   keyword_library,
   keyword_mod,
   keyword_nil,
   keyword_nodefault,
   keyword_not,
   keyword_object,
   keyword_of,
   keyword_on,
   keyword_or,
   keyword_out,
   keyword_override,
   keyword_packed,
   keyword_pascal,
   keyword_private,
   keyword_procedure,
   keyword_program,
   keyword_property,
   keyword_protected,
   keyword_public,
   keyword_published,
   keyword_raise,
   keyword_read,
   keyword_record,
   keyword_register,
   keyword_repeat,
   keyword_safecall,
   keyword_set,
   keyword_shl,
   keyword_shr,
   keyword_stdcall,
   keyword_stored,
   keyword_string,
   keyword_then,
   keyword_to,
   keyword_try,
   keyword_type,
   keyword_unit,
   keyword_until,
   keyword_uses,
   keyword_var,
   keyword_virtual,
   keyword_while,
   keyword_with,
   keyword_write,
   keyword_xor
};

enum TFce
{
   UnknownExp,
   MulExp,
   RDivExp,
   DivExp,
   ModExp,
   ShlExp,
   ShrExp,
   AndExp,
   AsExp,
   AddExp,
   SubExp,
   OrExp,
   XorExp,
   EqExp,
   NeExp,
   LtExp,
   GtExp,
   LeExp,
   GeExp,
   InExp,
   IsExp
};

enum TAccess
{
   PrivateAccess,
   ProtectedAccess,
   PublicAccess,
   PublishedAccess,
   AutomatedAccess
};

enum TStyle
{
   ProcedureStyle,
   FunctionStyle,
   ConstructorStyle,
   DestructorStyle
};

enum TCall
{
   RegisterCall,
   PascalCall,
   CdeclCall,
   StdcallCall,
   SafecallCall
};

enum TParamMode
{
   VarParam,
   ConstParam,
   OutParam,
   ValueParam
};

enum TDeclTag
{
};

enum TModuleKind
{
};

class Parser : public Lexer
{
public:
   CmmSymbol token;
   TLabelIdent * parse_label_ident ();
   TQualName * parse_qualified_name ();
   TContName * parse_cont_name ();
   TType * parse_ifc_type ();
   TType * parse_param_type ();
   TType * parse_result_type ();
   TAliasType * parse_simple_alias_type ();
   TStringType * parse_simple_string_type ();
   TFileType * parse_simple_file_type ();
   TInxItem * parse_index_expr_item ();
   TInxList * parse_index_expr_list ();
   TArgItem * parse_arg_item ();
   TArgSect * parse_arg_list ();
   TElemSect * parse_elem_sect ();
   TElemItem * parse_elem_item ();
   TStructSect * parse_struct_item ();
   TStructSect * parse_struct_sect ();
   TIdentExpr * parse_ident_expr ();
   TIntValueExpr * parse_int_value_expr ();
   TFltValueExpr * parse_float_value_expr ();
   TStrValueExpr * parse_string_value_expr ();
   TNilExpr * parse_nil_expr ();
   TStructExpr * parse_sub_expr ();
   TNotExpr * parse_not_expr ();
   TPlusExpr * parse_plus_expr ();
   TMinusExpr * parse_minus_expr ();
   TAdrExpr * parse_adr_expr ();
   TSetExpr * parse_set_expr ();
   TSuperExpr * parse_super_expr ();
   TStringExpr * parse_string_type_expr ();
   TExpr * parse_variable ();
   TExpr * parse_reference ();
   TIndexExpr * parse_index_expr (TExpr * store);
   TCallExpr * parse_call_expr (TExpr * store);
   TDerefExpr * parse_deref_expr (TExpr * store);
   TFieldExpr * parse_field_expr (TExpr * store);
   TExpr * parse_factor ();
   TExpr * parse_term ();
   TExpr * parse_simple_expr ();
   TExpr * parse_expr ();
   TGotoStat * parse_goto_stat ();
   TBlockStat * parse_begin_stat ();
   TStatSeq * parse_stat_list ();
   TStat * parse_inner_stat ();
   TIfStat * parse_if_stat ();
   TCaseStat * parse_case_stat ();
   TCaseSect * parse_case_sect ();
   TCaseItem * parse_case_item ();
   TWhileStat * parse_while_stat ();
   TRepeatStat * parse_repeat_stat ();
   TForStat * parse_for_stat ();
   TWithStat * parse_with_stat ();
   TWithSect * parse_with_sect ();
   TWithItem * parse_with_item ();
   TRaiseStat * parse_raise_stat ();
   TTryStat * parse_try_stat ();
   TFinallyPart * parse_finally_part ();
   TExceptPart * parse_except_part ();
   TOnSect * parse_on_sect ();
   TOnItem * parse_on_item ();
   TEmptyStat * parse_empty_stat ();
   TStat * parse_simple_stat ();
   TAssignStat * parse_assign_stat (TExpr * store);
   TCallStat * parse_call_stat (TExpr * store);
   TLabeledTStat * parse_labeled_stat ();
   TStat * parse_stat ();
   TParamIdent * parse_param_ident ();
   TParamItem * parse_param_item ();
   TParamSect * parse_formal_param_list ();
   TParamSect * parse_property_param_list ();
   TClassType * parse_class_type ();
   TInterfaceType * parse_interface_type ();
   TInterfaceSect * parse_interface_sect ();
   TIntefaceItem * parse_interface_item ();
   TComponetsSect * parse_components_sect ();
   TComponentsItem * parse_components_item ();
   TComponentsItem * parse_components_first_item ();
   TDeclGroup * parse_member_sect ();
   TDeclSect * parse_member_decl ();
   TFieldItem * parse_field_ident ();
   TFieldDecl * parse_field_decl ();
   TProcDecl * parse_method_decl ();
   TPropertyDecl * parse_property_decl ();
   TEnumType * parse_enum_type ();
   TEnumSect * parse_enum_sect ();
   TEnumItem * parse_enum_item ();
   TStringType * parse_string_type ();
   TArrayType * parse_array_type ();
   TIndexTypeSect * parse_index_type_sect ();
   TIndexTypeItem * parse_index_type_item ();
   TRecordType * parse_record_type ();
   TFieldDeclGroup * parse_field_sect ();
   TPointerType * parse_pointer_type ();
   TSetType * parse_set_type ();
   TFileType * parse_file_type ();
   TClassOfType * parse_class_of_type ();
   TProcType * parse_proc_type ();
   TSubrangeType * parse_range_type ();
   TAliasType * parse_alias_type ();
   TType * parse_type ();
   TLabelDecl * parse_label_decl ();
   TLabelSect * parse_label_sect ();
   TConstDecl * parse_const_decl ();
   TConstSect * parse_const_sect ();
   TTypeDecl * parse_type_decl ();
   TTypeSect * parse_type_sect ();
   TVarItem * parse_var_item ();
   TVarDecl * parse_var_decl ();
   TVarSect * parse_var_sect ();
   TProcDecl * parse_proc_head (TProcDecl * result);
   TProcDecl * parse_proc_decl ();
   TProcDecl * parse_proc_external (TProcDecl * result);
   TProcDecl * parse_proc_intf_decl ();
   TDeclSect * parse_intf_decl ();
   TDeclGroup * parse_intf_decl_part ();
   TDeclSect * parse_decl ();
   TDeclGroup * parse_decl_part ();
   TImportItem * parse_import_item ();
   TImportSect * parse_import_sect ();
   TUnitModule * parse_unit_decl ();
   TProgramModule * parse_program_decl ();
   TLibraryModule * parse_library_decl ();
   TModule * parse_module_decl ();
   bool test_1 ();
   bool test_2 ();
   bool test_3 ();
   bool test_4 ();
   bool test_label_ident ();
   bool test_range_type ();
   bool test_simple_expr ();
   bool test_term ();
   bool test_factor ();
   bool test_int_value_expr ();
   bool test_float_value_expr ();
   bool test_string_value_expr ();
   bool test_not_expr ();
   bool test_plus_expr ();
   bool test_minus_expr ();
   bool test_adr_expr ();
   bool test_nil_expr ();
   bool test_set_expr ();
   bool test_elem_sect ();
   bool test_elem_item ();
   bool test_expr ();
   bool test_string_type_expr ();
   bool test_reference ();
   bool test_variable ();
   bool test_ident_expr ();
   bool test_sub_expr ();
   bool test_super_expr ();
   bool test_index_expr ();
   bool test_index_expr_list ();
   bool test_index_expr_item ();
   bool test_call_expr ();
   bool test_arg_list ();
   bool test_arg_item ();
   bool test_deref_expr ();
   bool test_field_expr ();
   bool test_enum_type ();
   bool test_enum_sect ();
   bool test_enum_item ();

   inline bool isSymbol (CmmSymbol sym)
   {
         return token == sym;
   }

   inline void checkSymbol (CmmSymbol sym)
   {
         if (token != sym)
         {
            stop (tokenToString (sym) + " expected");
         }
         nextToken ();
   }

   inline bool testSymbols (const unsigned char table [ ])
   {
         int pos = token / 8;
         int bit = token % 8;
         return table [pos]  &  (1 << bit);
   }

   inline void stop (string msg)
   {
         error (msg);
   }

   inline void stop_str ()
   {
         stop ("Unexpected " + tokenToString (token));
   }

   void lookupKeyword ();
   void processSeparator ();
   string tokenToString (CmmSymbol value);
   void translate ();
   void storeLocation (CmmBasic * item);
   virtual void on_ident_expr (TIdentExpr * item);
   virtual void on_field_expr (TFieldExpr * item);
   virtual void on_param (TParamIdent * item);
   virtual void add_param (TParamItem * item);
   virtual void open_class (TClassType * item);
   virtual void close_class (TClassType * item);
   virtual void open_interface (TInterfaceType * item);
   virtual void close_interface (TInterfaceType * item);
   virtual void on_field (TFieldItem * item);
   virtual void add_field (TFieldDecl * item);
   virtual void open_proc (TProcDecl * item);
   virtual void close_proc (TProcDecl * item);
   virtual void simple_type (CmmBasic * item);
   virtual void on_const (TConstDecl * item);
   virtual void add_const (TConstDecl * item);
   virtual void on_type (TTypeDecl * item);
   virtual void add_type (TTypeDecl * item);
   virtual void on_var (TVarItem * item);
   virtual void add_var (TVarDecl * item);
   virtual void on_proc (TProcDecl * item);
   virtual void on_begin_proc (TProcDecl * item);
   virtual void on_end_proc (TProcDecl * item);
   virtual void on_tail_proc (TProcDecl * item);
   virtual void on_import (TImportItem * item);
   virtual void open_module (CmmBasic * item);
   virtual void on_module (CmmBasic * item);
   virtual void close_module (CmmBasic * item);
   Parser ();
};

class TBasic : public CmmBasic
{
public:
   int src_file;
   int src_line;
   int src_column;

   inline TBasic () :
      src_file (0),
      src_line (0),
      src_column (0)
   {
   }

   inline virtual TBasic * conv_TBasic ()
   {

         return this;
   }
};

class TExpr : public CmmBasic
{
public:
   TFce fce;

   inline TExpr () :
      fce (TFce (0))
   {
   }

   inline virtual TBinaryExpr * conv_TBinaryExpr ()
   {

         return NULL;
   }

   inline virtual TIdentExpr * conv_TIdentExpr ()
   {
         return NULL;
   }

   inline virtual TIntValueExpr * conv_TIntValueExpr ()
   {
         return NULL;
   }

   inline virtual TFltValueExpr * conv_TFltValueExpr ()
   {
         return NULL;
   }

   inline virtual TStrValueExpr * conv_TStrValueExpr ()
   {
         return NULL;
   }

   inline virtual TNilExpr * conv_TNilExpr ()
   {
         return NULL;
   }

   inline virtual TStructExpr * conv_TStructExpr ()
   {
         return NULL;
   }

   inline virtual TNotExpr * conv_TNotExpr ()
   {
         return NULL;
   }

   inline virtual TPlusExpr * conv_TPlusExpr ()
   {
         return NULL;
   }

   inline virtual TMinusExpr * conv_TMinusExpr ()
   {
         return NULL;
   }

   inline virtual TAdrExpr * conv_TAdrExpr ()
   {
         return NULL;
   }

   inline virtual TSetExpr * conv_TSetExpr ()
   {
         return NULL;
   }

   inline virtual TSuperExpr * conv_TSuperExpr ()
   {
         return NULL;
   }

   inline virtual TStringExpr * conv_TStringExpr ()
   {
         return NULL;
   }

   inline virtual TIndexExpr * conv_TIndexExpr ()
   {
         return NULL;
   }

   inline virtual TCallExpr * conv_TCallExpr ()
   {
         return NULL;
   }

   inline virtual TDerefExpr * conv_TDerefExpr ()
   {
         return NULL;
   }

   inline virtual TFieldExpr * conv_TFieldExpr ()
   {
         return NULL;
   }

   inline virtual TTermExpr * conv_TTermExpr ()
   {
         return NULL;
   }

   inline virtual TSimpleExpr * conv_TSimpleExpr ()
   {
         return NULL;
   }

   inline virtual TCompleteExpr * conv_TCompleteExpr ()
   {
         return NULL;
   }

   inline virtual TExpr * conv_TExpr ()
   {
         return this;
   }
};

class TBinaryExpr : public TExpr
{
public:
   TExpr * left;
   TExpr * right;

   inline TBinaryExpr () :
      left (NULL),
      right (NULL)
   {
   }

   inline virtual TBinaryExpr * conv_TBinaryExpr ()
   {

         return this;
   }
};

class TComponentsItem : public CmmBasic
{
public:
   TAccess acs;
   TDeclGroup * members;

   inline TComponentsItem () :
      acs (TAccess (0)),
      members (NULL)
   {
   }

   inline virtual TComponentsItem * conv_TComponentsItem ()
   {

         return this;
   }
};

class TParamItem : public CmmBasic
{
public:
   TParamMode mode;
   vector < TParamIdent * > items;
   TType * typ;
   TExpr * ini;

   inline TParamItem () :
      mode (TParamMode (0)),
      items (),
      typ (NULL),
      ini (NULL)
   {
   }

   inline virtual TParamItem * conv_TParamItem ()
   {

         return this;
   }
};

class TModule : public CmmBasic
{
public:
   TImportSect * intf_imports;
   TImportSect * impl_imports;
   TDeclGroup * intf_decl;
   TDeclGroup * impl_decl;
   TStatSeq * init;
   TStatSeq * finish;

   inline TModule () :
      intf_imports (NULL),
      impl_imports (NULL),
      intf_decl (NULL),
      impl_decl (NULL),
      init (NULL),
      finish (NULL)
   {
   }

   inline virtual TUnitModule * conv_TUnitModule ()
   {

         return NULL;
   }

   inline virtual TProgramModule * conv_TProgramModule ()
   {
         return NULL;
   }

   inline virtual TLibraryModule * conv_TLibraryModule ()
   {
         return NULL;
   }

   inline virtual TModule * conv_TModule ()
   {
         return this;
   }
};

class TLabelIdent : public CmmBasic
{
public:
   string id;

   inline TLabelIdent () :
      id ("")
   {
   }

   inline virtual TLabelIdent * conv_TLabelIdent ()
   {

         return this;
   }
};

class TQualName : public CmmBasic
{
public:
   string id;
   vector < TContName * > items;

   inline TQualName () :
      id (""),
      items ()
   {
   }

   inline virtual TQualName * conv_TQualName ()
   {

         return this;
   }
};

class TContName : public CmmBasic
{
public:
   string id;

   inline TContName () :
      id ("")
   {
   }

   inline virtual TContName * conv_TContName ()
   {

         return this;
   }
};

class TType : public CmmBasic
{
public:

   inline TType ()
   {
   }

   inline virtual TAliasType * conv_TAliasType ()
   {

         return NULL;
   }

   inline virtual TStringType * conv_TStringType ()
   {
         return NULL;
   }

   inline virtual TFileType * conv_TFileType ()
   {
         return NULL;
   }

   inline virtual TClassType * conv_TClassType ()
   {
         return NULL;
   }

   inline virtual TInterfaceType * conv_TInterfaceType ()
   {
         return NULL;
   }

   inline virtual TEnumType * conv_TEnumType ()
   {
         return NULL;
   }

   inline virtual TArrayType * conv_TArrayType ()
   {
         return NULL;
   }

   inline virtual TRecordType * conv_TRecordType ()
   {
         return NULL;
   }

   inline virtual TPointerType * conv_TPointerType ()
   {
         return NULL;
   }

   inline virtual TSetType * conv_TSetType ()
   {
         return NULL;
   }

   inline virtual TClassOfType * conv_TClassOfType ()
   {
         return NULL;
   }

   inline virtual TProcType * conv_TProcType ()
   {
         return NULL;
   }

   inline virtual TSubrangeType * conv_TSubrangeType ()
   {
         return NULL;
   }

   inline virtual TType * conv_TType ()
   {
         return this;
   }
};

class TAliasType : public TType
{
public:
   TQualName * alias_name;

   inline TAliasType () :
      alias_name (NULL)
   {
   }

   inline virtual TAliasType * conv_TAliasType ()
   {

         return this;
   }
};

class TStringType : public TType
{
public:
   TExpr * lim;

   inline TStringType () :
      lim (NULL)
   {
   }

   inline virtual TStringType * conv_TStringType ()
   {

         return this;
   }
};

class TFileType : public TType
{
public:
   TType * elem;

   inline TFileType () :
      elem (NULL)
   {
   }

   inline virtual TFileType * conv_TFileType ()
   {

         return this;
   }
};

class TInxItem : public CmmBasic
{
public:
   TExpr * ref;

   inline TInxItem () :
      ref (NULL)
   {
   }

   inline virtual TInxItem * conv_TInxItem ()
   {

         return this;
   }
};

class TInxList : public CmmBasic
{
public:
   vector < TInxItem * > items;

   inline TInxList () :
      items ()
   {
   }

   inline virtual TInxList * conv_TInxList ()
   {

         return this;
   }
};

class TArgItem : public CmmBasic
{
public:
   TExpr * value;
   TExpr * width;
   TExpr * digits;

   inline TArgItem () :
      value (NULL),
      width (NULL),
      digits (NULL)
   {
   }

   inline virtual TArgItem * conv_TArgItem ()
   {

         return this;
   }
};

class TArgSect : public CmmBasic
{
public:
   vector < TArgItem * > items;

   inline TArgSect () :
      items ()
   {
   }

   inline virtual TArgSect * conv_TArgSect ()
   {

         return this;
   }
};

class TElemSect : public CmmBasic
{
public:
   vector < TElemItem * > items;

   inline TElemSect () :
      items ()
   {
   }

   inline virtual TElemSect * conv_TElemSect ()
   {

         return this;
   }
};

class TElemItem : public CmmBasic
{
public:
   TExpr * low;
   TExpr * high;

   inline TElemItem () :
      low (NULL),
      high (NULL)
   {
   }

   inline virtual TElemItem * conv_TElemItem ()
   {

         return this;
   }
};

class TStructSect : public CmmBasic
{
public:
   string name;
   TExpr * value;
   vector < TStructSect * > items;

   inline TStructSect () :
      name (""),
      value (NULL),
      items ()
   {
   }

   inline virtual TStructSect * conv_TStructSect ()
   {

         return this;
   }
};

class TIdentExpr : public TExpr
{
public:
   string name;

   inline TIdentExpr () :
      name ("")
   {
   }

   inline virtual TIdentExpr * conv_TIdentExpr ()
   {

         return this;
   }
};

class TIntValueExpr : public TExpr
{
public:
   string value;

   inline TIntValueExpr () :
      value ("")
   {
   }

   inline virtual TIntValueExpr * conv_TIntValueExpr ()
   {

         return this;
   }
};

class TFltValueExpr : public TExpr
{
public:
   string value;

   inline TFltValueExpr () :
      value ("")
   {
   }

   inline virtual TFltValueExpr * conv_TFltValueExpr ()
   {

         return this;
   }
};

class TStrValueExpr : public TExpr
{
public:
   string value;

   inline TStrValueExpr () :
      value ("")
   {
   }

   inline virtual TStrValueExpr * conv_TStrValueExpr ()
   {

         return this;
   }
};

class TNilExpr : public TExpr
{
public:

   inline TNilExpr ()
   {
   }

   inline virtual TNilExpr * conv_TNilExpr ()
   {

         return this;
   }
};

class TStructExpr : public TExpr
{
public:
   TExpr * value;

   inline TStructExpr () :
      value (NULL)
   {
   }

   inline virtual TStructExpr * conv_TStructExpr ()
   {

         return this;
   }
};

class TNotExpr : public TExpr
{
public:
   TExpr * param;

   inline TNotExpr () :
      param (NULL)
   {
   }

   inline virtual TNotExpr * conv_TNotExpr ()
   {

         return this;
   }
};

class TPlusExpr : public TExpr
{
public:
   TExpr * param;

   inline TPlusExpr () :
      param (NULL)
   {
   }

   inline virtual TPlusExpr * conv_TPlusExpr ()
   {

         return this;
   }
};

class TMinusExpr : public TExpr
{
public:
   TExpr * param;

   inline TMinusExpr () :
      param (NULL)
   {
   }

   inline virtual TMinusExpr * conv_TMinusExpr ()
   {

         return this;
   }
};

class TAdrExpr : public TExpr
{
public:
   TExpr * param;

   inline TAdrExpr () :
      param (NULL)
   {
   }

   inline virtual TAdrExpr * conv_TAdrExpr ()
   {

         return this;
   }
};

class TSetExpr : public TExpr
{
public:
   TElemSect * list;

   inline TSetExpr () :
      list (NULL)
   {
   }

   inline virtual TSetExpr * conv_TSetExpr ()
   {

         return this;
   }
};

class TSuperExpr : public TExpr
{
public:
   string name;

   inline TSuperExpr () :
      name ("")
   {
   }

   inline virtual TSuperExpr * conv_TSuperExpr ()
   {

         return this;
   }
};

class TStringExpr : public TExpr
{
public:
   TExpr * param;

   inline TStringExpr () :
      param (NULL)
   {
   }

   inline virtual TStringExpr * conv_TStringExpr ()
   {

         return this;
   }
};

class TIndexExpr : public TExpr
{
public:
   TExpr * left;
   TInxList * list;

   inline TIndexExpr () :
      left (NULL),
      list (NULL)
   {
   }

   inline virtual TIndexExpr * conv_TIndexExpr ()
   {

         return this;
   }
};

class TCallExpr : public TExpr
{
public:
   TExpr * func;
   TArgSect * list;

   inline TCallExpr () :
      func (NULL),
      list (NULL)
   {
   }

   inline virtual TCallExpr * conv_TCallExpr ()
   {

         return this;
   }
};

class TDerefExpr : public TExpr
{
public:
   TExpr * param;

   inline TDerefExpr () :
      param (NULL)
   {
   }

   inline virtual TDerefExpr * conv_TDerefExpr ()
   {

         return this;
   }
};

class TFieldExpr : public TExpr
{
public:
   TExpr * param;
   string name;

   inline TFieldExpr () :
      param (NULL),
      name ("")
   {
   }

   inline virtual TFieldExpr * conv_TFieldExpr ()
   {

         return this;
   }
};

class TStat : public CmmBasic
{
public:

   inline TStat ()
   {
   }

   inline virtual TGotoStat * conv_TGotoStat ()
   {

         return NULL;
   }

   inline virtual TBlockStat * conv_TBlockStat ()
   {
         return NULL;
   }

   inline virtual TIfStat * conv_TIfStat ()
   {
         return NULL;
   }

   inline virtual TCaseStat * conv_TCaseStat ()
   {
         return NULL;
   }

   inline virtual TWhileStat * conv_TWhileStat ()
   {
         return NULL;
   }

   inline virtual TRepeatStat * conv_TRepeatStat ()
   {
         return NULL;
   }

   inline virtual TForStat * conv_TForStat ()
   {
         return NULL;
   }

   inline virtual TWithStat * conv_TWithStat ()
   {
         return NULL;
   }

   inline virtual TRaiseStat * conv_TRaiseStat ()
   {
         return NULL;
   }

   inline virtual TTryStat * conv_TTryStat ()
   {
         return NULL;
   }

   inline virtual TEmptyStat * conv_TEmptyStat ()
   {
         return NULL;
   }

   inline virtual TAssignStat * conv_TAssignStat ()
   {
         return NULL;
   }

   inline virtual TCallStat * conv_TCallStat ()
   {
         return NULL;
   }

   inline virtual TLabeledTStat * conv_TLabeledTStat ()
   {
         return NULL;
   }

   inline virtual TStat * conv_TStat ()
   {
         return this;
   }
};

class TGotoStat : public TStat
{
public:
   TLabelIdent * goto_lab;

   inline TGotoStat () :
      goto_lab (NULL)
   {
   }

   inline virtual TGotoStat * conv_TGotoStat ()
   {

         return this;
   }
};

class TBlockStat : public TStat
{
public:
   TStatSeq * body_seq;

   inline TBlockStat () :
      body_seq (NULL)
   {
   }

   inline virtual TBlockStat * conv_TBlockStat ()
   {

         return this;
   }
};

class TStatSeq : public CmmBasic
{
public:
   vector < TStat * > items;

   inline TStatSeq () :
      items ()
   {
   }

   inline virtual TStatSeq * conv_TStatSeq ()
   {

         return this;
   }
};

class TIfStat : public TStat
{
public:
   TExpr * cond_expr;
   TStat * then_stat;
   TStat * else_stat;

   inline TIfStat () :
      cond_expr (NULL),
      then_stat (NULL),
      else_stat (NULL)
   {
   }

   inline virtual TIfStat * conv_TIfStat ()
   {

         return this;
   }
};

class TCaseStat : public TStat
{
public:
   TExpr * case_expr;
   TCaseSect * case_list;
   TStatSeq * else_seq;

   inline TCaseStat () :
      case_expr (NULL),
      case_list (NULL),
      else_seq (NULL)
   {
   }

   inline virtual TCaseStat * conv_TCaseStat ()
   {

         return this;
   }
};

class TCaseSect : public CmmBasic
{
public:
   vector < TCaseItem * > items;

   inline TCaseSect () :
      items ()
   {
   }

   inline virtual TCaseSect * conv_TCaseSect ()
   {

         return this;
   }
};

class TCaseItem : public CmmBasic
{
public:
   TElemSect * sel_list;
   TStat * sel_stat;

   inline TCaseItem () :
      sel_list (NULL),
      sel_stat (NULL)
   {
   }

   inline virtual TCaseItem * conv_TCaseItem ()
   {

         return this;
   }
};

class TWhileStat : public TStat
{
public:
   TExpr * cond_expr;
   TStat * body_stat;

   inline TWhileStat () :
      cond_expr (NULL),
      body_stat (NULL)
   {
   }

   inline virtual TWhileStat * conv_TWhileStat ()
   {

         return this;
   }
};

class TRepeatStat : public TStat
{
public:
   TStatSeq * body_seq;
   TExpr * until_expr;

   inline TRepeatStat () :
      body_seq (NULL),
      until_expr (NULL)
   {
   }

   inline virtual TRepeatStat * conv_TRepeatStat ()
   {

         return this;
   }
};

class TForStat : public TStat
{
public:
   TExpr * var_expr;
   TExpr * from_expr;
   bool incr;
   TExpr * to_expr;
   TStat * body_stat;

   inline TForStat () :
      var_expr (NULL),
      from_expr (NULL),
      incr (false),
      to_expr (NULL),
      body_stat (NULL)
   {
   }

   inline virtual TForStat * conv_TForStat ()
   {

         return this;
   }
};

class TWithStat : public TStat
{
public:
   TWithSect * with_list;
   TStat * body_stat;

   inline TWithStat () :
      with_list (NULL),
      body_stat (NULL)
   {
   }

   inline virtual TWithStat * conv_TWithStat ()
   {

         return this;
   }
};

class TWithSect : public CmmBasic
{
public:
   vector < TWithItem * > items;

   inline TWithSect () :
      items ()
   {
   }

   inline virtual TWithSect * conv_TWithSect ()
   {

         return this;
   }
};

class TWithItem : public CmmBasic
{
public:
   TExpr * expr;

   inline TWithItem () :
      expr (NULL)
   {
   }

   inline virtual TWithItem * conv_TWithItem ()
   {

         return this;
   }
};

class TRaiseStat : public TStat
{
public:
   TExpr * raise_expr;

   inline TRaiseStat () :
      raise_expr (NULL)
   {
   }

   inline virtual TRaiseStat * conv_TRaiseStat ()
   {

         return this;
   }
};

class TTryStat : public TStat
{
public:
   TStatSeq * body_seq;
   TFinallyPart * finally_branch;
   TExceptPart * except_branch;

   inline TTryStat () :
      body_seq (NULL),
      finally_branch (NULL),
      except_branch (NULL)
   {
   }

   inline virtual TTryStat * conv_TTryStat ()
   {

         return this;
   }
};

class TFinallyPart : public CmmBasic
{
public:
   TStatSeq * finally_seq;

   inline TFinallyPart () :
      finally_seq (NULL)
   {
   }

   inline virtual TFinallyPart * conv_TFinallyPart ()
   {

         return this;
   }
};

class TExceptPart : public CmmBasic
{
public:
   TOnSect * on_list;
   TStatSeq * else_seq;

   inline TExceptPart () :
      on_list (NULL),
      else_seq (NULL)
   {
   }

   inline virtual TExceptPart * conv_TExceptPart ()
   {

         return this;
   }
};

class TOnSect : public CmmBasic
{
public:
   vector < TOnItem * > items;
   bool semicolon;

   inline TOnSect () :
      items (),
      semicolon (false)
   {
   }

   inline virtual TOnSect * conv_TOnSect ()
   {

         return this;
   }
};

class TOnItem : public CmmBasic
{
public:
   string on_ident;
   TType * on_type;
   TStat * body_stat;

   inline TOnItem () :
      on_ident (""),
      on_type (NULL),
      body_stat (NULL)
   {
   }

   inline virtual TOnItem * conv_TOnItem ()
   {

         return this;
   }
};

class TEmptyStat : public TStat
{
public:

   inline TEmptyStat ()
   {
   }

   inline virtual TEmptyStat * conv_TEmptyStat ()
   {

         return this;
   }
};

class TAssignStat : public TStat
{
public:
   TExpr * left_expr;
   TExpr * right_expr;

   inline TAssignStat () :
      left_expr (NULL),
      right_expr (NULL)
   {
   }

   inline virtual TAssignStat * conv_TAssignStat ()
   {

         return this;
   }
};

class TCallStat : public TStat
{
public:
   TExpr * call_expr;

   inline TCallStat () :
      call_expr (NULL)
   {
   }

   inline virtual TCallStat * conv_TCallStat ()
   {

         return this;
   }
};

class TLabeledTStat : public TStat
{
public:
   TLabelIdent * lab;
   TStat * body;

   inline TLabeledTStat () :
      lab (NULL),
      body (NULL)
   {
   }

   inline virtual TLabeledTStat * conv_TLabeledTStat ()
   {

         return this;
   }
};

class TParamIdent : public CmmBasic
{
public:
   string name;

   inline TParamIdent () :
      name ("")
   {
   }

   inline virtual TParamIdent * conv_TParamIdent ()
   {

         return this;
   }
};

class TParamSect : public CmmBasic
{
public:
   vector < TParamItem * > items;

   inline TParamSect () :
      items ()
   {
   }

   inline virtual TParamSect * conv_TParamSect ()
   {

         return this;
   }
};

class TClassType : public TType
{
public:
   TType * parent;
   TInterfaceSect * ifc_list;
   TComponetsSect * components;

   inline TClassType () :
      parent (NULL),
      ifc_list (NULL),
      components (NULL)
   {
   }

   inline virtual TClassType * conv_TClassType ()
   {

         return this;
   }
};

class TInterfaceType : public TType
{
public:
   TInterfaceSect * ifc_list;
   TComponetsSect * components;

   inline TInterfaceType () :
      ifc_list (NULL),
      components (NULL)
   {
   }

   inline virtual TInterfaceType * conv_TInterfaceType ()
   {

         return this;
   }
};

class TInterfaceSect : public CmmBasic
{
public:
   vector < TIntefaceItem * > items;

   inline TInterfaceSect () :
      items ()
   {
   }

   inline virtual TInterfaceSect * conv_TInterfaceSect ()
   {

         return this;
   }
};

class TIntefaceItem : public CmmBasic
{
public:
   TType * ifc;

   inline TIntefaceItem () :
      ifc (NULL)
   {
   }

   inline virtual TIntefaceItem * conv_TIntefaceItem ()
   {

         return this;
   }
};

class TComponetsSect : public CmmBasic
{
public:
   vector < TComponentsItem * > items;

   inline TComponetsSect () :
      items ()
   {
   }

   inline virtual TComponetsSect * conv_TComponetsSect ()
   {

         return this;
   }
};

class TDeclGroup : public CmmBasic
{
public:
   vector < TDeclSect * > items;

   inline TDeclGroup () :
      items ()
   {
   }

   inline virtual TDeclGroup * conv_TDeclGroup ()
   {

         return this;
   }
};

class TDeclSect : public CmmBasic
{
public:

   inline TDeclSect ()
   {
   }

   inline virtual TFieldDecl * conv_TFieldDecl ()
   {

         return NULL;
   }

   inline virtual TPropertyDecl * conv_TPropertyDecl ()
   {
         return NULL;
   }

   inline virtual TLabelSect * conv_TLabelSect ()
   {
         return NULL;
   }

   inline virtual TConstSect * conv_TConstSect ()
   {
         return NULL;
   }

   inline virtual TTypeSect * conv_TTypeSect ()
   {
         return NULL;
   }

   inline virtual TVarSect * conv_TVarSect ()
   {
         return NULL;
   }

   inline virtual TProcDecl * conv_TProcDecl ()
   {
         return NULL;
   }

   inline virtual TDeclSect * conv_TDeclSect ()
   {
         return this;
   }
};

class TFieldItem : public CmmBasic
{
public:
   string name;

   inline TFieldItem () :
      name ("")
   {
   }

   inline virtual TFieldItem * conv_TFieldItem ()
   {

         return this;
   }
};

class TFieldDecl : public TDeclSect
{
public:
   vector < TFieldItem * > items;
   TType * typ;

   inline TFieldDecl () :
      items (),
      typ (NULL)
   {
   }

   inline virtual TFieldDecl * conv_TFieldDecl ()
   {

         return this;
   }
};

class TPropertyDecl : public TDeclSect
{
public:
   string name;
   TParamSect * param_list;
   TType * typ;
   TExpr * a_read;
   TExpr * a_write;
   bool a_stored;
   bool a_default;
   bool a_nodefault;
   TInterfaceSect * a_implements;
   bool a_def_array;

   inline TPropertyDecl () :
      name (""),
      param_list (NULL),
      typ (NULL),
      a_read (NULL),
      a_write (NULL),
      a_stored (false),
      a_default (false),
      a_nodefault (false),
      a_implements (NULL),
      a_def_array (false)
   {
   }

   inline virtual TPropertyDecl * conv_TPropertyDecl ()
   {

         return this;
   }
};

class TEnumType : public TType
{
public:
   TEnumSect * elements;

   inline TEnumType () :
      elements (NULL)
   {
   }

   inline virtual TEnumType * conv_TEnumType ()
   {

         return this;
   }
};

class TEnumSect : public CmmBasic
{
public:
   vector < TEnumItem * > items;

   inline TEnumSect () :
      items ()
   {
   }

   inline virtual TEnumSect * conv_TEnumSect ()
   {

         return this;
   }
};

class TEnumItem : public CmmBasic
{
public:
   string name;

   inline TEnumItem () :
      name ("")
   {
   }

   inline virtual TEnumItem * conv_TEnumItem ()
   {

         return this;
   }
};

class TArrayType : public TType
{
public:
   TIndexTypeSect * index_list;
   TType * elem;

   inline TArrayType () :
      index_list (NULL),
      elem (NULL)
   {
   }

   inline virtual TArrayType * conv_TArrayType ()
   {

         return this;
   }
};

class TIndexTypeSect : public CmmBasic
{
public:
   vector < TIndexTypeItem * > items;

   inline TIndexTypeSect () :
      items ()
   {
   }

   inline virtual TIndexTypeSect * conv_TIndexTypeSect ()
   {

         return this;
   }
};

class TIndexTypeItem : public CmmBasic
{
public:
   TType * index;

   inline TIndexTypeItem () :
      index (NULL)
   {
   }

   inline virtual TIndexTypeItem * conv_TIndexTypeItem ()
   {

         return this;
   }
};

class TRecordType : public TType
{
public:
   bool a_packed;
   TFieldDeclGroup * fields;

   inline TRecordType () :
      a_packed (false),
      fields (NULL)
   {
   }

   inline virtual TRecordType * conv_TRecordType ()
   {

         return this;
   }
};

class TFieldDeclGroup : public CmmBasic
{
public:
   vector < TFieldDecl * > items;

   inline TFieldDeclGroup () :
      items ()
   {
   }

   inline virtual TFieldDeclGroup * conv_TFieldDeclGroup ()
   {

         return this;
   }
};

class TPointerType : public TType
{
public:
   TType * elem;

   inline TPointerType () :
      elem (NULL)
   {
   }

   inline virtual TPointerType * conv_TPointerType ()
   {

         return this;
   }
};

class TSetType : public TType
{
public:
   TType * elem;

   inline TSetType () :
      elem (NULL)
   {
   }

   inline virtual TSetType * conv_TSetType ()
   {

         return this;
   }
};

class TClassOfType : public TType
{
public:
   TType * elem;

   inline TClassOfType () :
      elem (NULL)
   {
   }

   inline virtual TClassOfType * conv_TClassOfType ()
   {

         return this;
   }
};

class TProcType : public TType
{
public:
   TStyle style;
   TCall call_conv;
   TParamSect * param_list;
   TType * answer;
   bool of_object;

   inline TProcType () :
      style (TStyle (0)),
      call_conv (TCall (0)),
      param_list (NULL),
      answer (NULL),
      of_object (false)
   {
   }

   inline virtual TProcType * conv_TProcType ()
   {

         return this;
   }
};

class TSubrangeType : public TType
{
public:
   TExpr * low;
   TExpr * high;

   inline TSubrangeType () :
      low (NULL),
      high (NULL)
   {
   }

   inline virtual TSubrangeType * conv_TSubrangeType ()
   {

         return this;
   }
};

class TLabelDecl : public CmmBasic
{
public:
   TLabelIdent * name;

   inline TLabelDecl () :
      name (NULL)
   {
   }

   inline virtual TLabelDecl * conv_TLabelDecl ()
   {

         return this;
   }
};

class TLabelSect : public TDeclSect
{
public:
   vector < TLabelDecl * > items;

   inline TLabelSect () :
      items ()
   {
   }

   inline virtual TLabelSect * conv_TLabelSect ()
   {

         return this;
   }
};

class TConstDecl : public CmmBasic
{
public:
   string name;
   TType * typ;
   TExpr * val;

   inline TConstDecl () :
      name (""),
      typ (NULL),
      val (NULL)
   {
   }

   inline virtual TConstDecl * conv_TConstDecl ()
   {

         return this;
   }
};

class TConstSect : public TDeclSect
{
public:
   vector < TConstDecl * > items;

   inline TConstSect () :
      items ()
   {
   }

   inline virtual TConstSect * conv_TConstSect ()
   {

         return this;
   }
};

class TTypeDecl : public CmmBasic
{
public:
   string name;
   TType * typ;

   inline TTypeDecl () :
      name (""),
      typ (NULL)
   {
   }

   inline virtual TTypeDecl * conv_TTypeDecl ()
   {

         return this;
   }
};

class TTypeSect : public TDeclSect
{
public:
   vector < TTypeDecl * > items;

   inline TTypeSect () :
      items ()
   {
   }

   inline virtual TTypeSect * conv_TTypeSect ()
   {

         return this;
   }
};

class TVarItem : public CmmBasic
{
public:
   string name;

   inline TVarItem () :
      name ("")
   {
   }

   inline virtual TVarItem * conv_TVarItem ()
   {

         return this;
   }
};

class TVarDecl : public CmmBasic
{
public:
   vector < TVarItem * > items;
   TType * typ;
   TExpr * ini;

   inline TVarDecl () :
      items (),
      typ (NULL),
      ini (NULL)
   {
   }

   inline virtual TVarDecl * conv_TVarDecl ()
   {

         return this;
   }
};

class TVarSect : public TDeclSect
{
public:
   vector < TVarDecl * > items;

   inline TVarSect () :
      items ()
   {
   }

   inline virtual TVarSect * conv_TVarSect ()
   {

         return this;
   }
};

class TProcDecl : public TDeclSect
{
public:
   TStyle style;
   TCall call_conv;
   bool a_virtual;
   bool a_dynamic;
   bool a_override;
   bool a_abstract;
   bool a_static;
   TQualName * proc_name;
   TParamSect * param_list;
   TType * answer;
   bool a_forward;
   bool external_spec;
   bool a_inline;
   TDeclGroup * local;
   TStatSeq * body;
   bool a_external;
   TExpr * a_lib;

   inline TProcDecl () :
      style (TStyle (0)),
      call_conv (TCall (0)),
      a_virtual (false),
      a_dynamic (false),
      a_override (false),
      a_abstract (false),
      a_static (false),
      proc_name (NULL),
      param_list (NULL),
      answer (NULL),
      a_forward (false),
      external_spec (false),
      a_inline (false),
      local (NULL),
      body (NULL),
      a_external (false),
      a_lib (NULL)
   {
   }

   inline virtual TProcDecl * conv_TProcDecl ()
   {

         return this;
   }
};

class TImportItem : public CmmBasic
{
public:
   string name;
   string path;

   inline TImportItem () :
      name (""),
      path ("")
   {
   }

   inline virtual TImportItem * conv_TImportItem ()
   {

         return this;
   }
};

class TImportSect : public CmmBasic
{
public:
   vector < TImportItem * > items;

   inline TImportSect () :
      items ()
   {
   }

   inline virtual TImportSect * conv_TImportSect ()
   {

         return this;
   }
};

class TUnitModule : public TModule
{
public:
   string name;
   bool no_begin;

   inline TUnitModule () :
      name (""),
      no_begin (false)
   {
   }

   inline virtual TUnitModule * conv_TUnitModule ()
   {

         return this;
   }
};

class TProgramModule : public TModule
{
public:
   string name;

   inline TProgramModule () :
      name ("")
   {
   }

   inline virtual TProgramModule * conv_TProgramModule ()
   {

         return this;
   }
};

class TLibraryModule : public TModule
{
public:
   string name;

   inline TLibraryModule () :
      name ("")
   {
   }

   inline virtual TLibraryModule * conv_TLibraryModule ()
   {

         return this;
   }
};

class TTermExpr : public TBinaryExpr
{
public:

   inline TTermExpr ()
   {
   }

   inline virtual TTermExpr * conv_TTermExpr ()
   {

         return this;
   }
};

class TSimpleExpr : public TBinaryExpr
{
public:

   inline TSimpleExpr ()
   {
   }

   inline virtual TSimpleExpr * conv_TSimpleExpr ()
   {

         return this;
   }
};

class TCompleteExpr : public TBinaryExpr
{
public:

   inline TCompleteExpr ()
   {
   }

   inline virtual TCompleteExpr * conv_TCompleteExpr ()
   {

         return this;
   }
};


#endif //PAS_PARSER_H
