#ifndef ___CMM_CMM_PARSER_H
#define ___CMM_CMM_PARSER_H

#include "lexer.h"
#include <string>
#include <vector>
using std::string;
using std::vector;

class CmmBasic;
class CmmCommon;
class CmmExpr;
class CmmName;
class CmmUnaryExpr;
class CmmBinaryExpr;
class CmmStat;
class CmmDecl;
class CmmSimpleItem;
class CmmDeclarator;
class CmmPtrSpecifier;
class CmmContSpecifier;
class CmmTemplateParam;
class CmmExtensionStat;
class CmmSimpleName;
class CmmGlobalName;
class CmmDestructorName;
class CmmCompoundName;
class CmmTemplateName;
class CmmIntValue;
class CmmRealValue;
class CmmCharValue;
class CmmStringValue;
class CmmStringCont;
class CmmThisExpr;
class CmmLambdaExpr;
class CmmSubexprExpr;
class CmmSignalSlotExpr;
class CmmModernCastExpr;
class CmmTypeIdExpr;
class CmmIndexExpr;
class CmmCallExpr;
class CmmFieldExpr;
class CmmPtrFieldExpr;
class CmmPostIncExpr;
class CmmPostDecExpr;
class CmmExprList;
class CmmIncExpr;
class CmmDecExpr;
class CmmDerefExpr;
class CmmAddrExpr;
class CmmPlusExpr;
class CmmMinusExpr;
class CmmBitNotExpr;
class CmmLogNotExpr;
class CmmSizeofExpr;
class CmmNewExpr;
class CmmNewTypeId;
class CmmNewArrayLimit;
class CmmDeleteExpr;
class CmmEmptyStat;
class CmmCompoundStat;
class CmmIfStat;
class CmmWhileStat;
class CmmDoStat;
class CmmForStat;
class CmmSwitchStat;
class CmmCaseStat;
class CmmDefaultStat;
class CmmBreakStat;
class CmmContinueStat;
class CmmReturnStat;
class CmmGotoStat;
class CmmSimpleStat;
class CmmDeclSpec;
class CmmConstSpecifier;
class CmmVolatileSpecifier;
class CmmTypeSpec;
class CmmTypeName;
class CmmPointerDeclarator;
class CmmReferenceDeclator;
class CmmCvSpecifier;
class CmmBasicDeclarator;
class CmmEmptyDeclarator;
class CmmNestedDeclarator;
class CmmArrayDeclarator;
class CmmFunctionDeclarator;
class CmmPtrSpecifierSect;
class CmmStatSect;
class CmmSimpleDecl;
class CmmDotsParam;
class CmmTypeId;
class CmmInitializer;
class CmmInitItem;
class CmmInitSimple;
class CmmInitList;
class CmmAttr;
class CmmAttrGroup;
class CmmAttrSect;
class CmmNamespaceDecl;
class CmmUsingDecl;
class CmmExternDecl;
class CmmTypedefDecl;
class CmmFriendDecl;
class CmmEnumDecl;
class CmmEnumSect;
class CmmEnumItem;
class CmmClassDecl;
class CmmMemberVisibility;
class CmmBaseSect;
class CmmBaseItem;
class CmmCtorInitializer;
class CmmMemberInitializer;
class CmmConvSpec;
class CmmSpecialFuction;
class CmmTemplateDecl;
class CmmStencilDecl;
class CmmTemplateParamSect;
class CmmTemplateTypeParam;
class CmmTemplateNormalParam;
class CmmTemplateArgSect;
class CmmTemplateArg;
class CmmTryStat;
class CmmHandlerSect;
class CmmHandlerItem;
class CmmThrowExpr;
class CmmExceptionSect;
class CmmExceptionItem;
class CmmCastExpr;
class CmmPtrMemExpr;
class CmmMulExpr;
class CmmAddExpr;
class CmmShiftExpr;
class CmmRelExpr;
class CmmEqExpr;
class CmmAndExpr;
class CmmXorExpr;
class CmmOrExpr;
class CmmAndAndExpr;
class CmmOrOrExpr;
class CmmAssignExpr;
class CmmCommaExpr;

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
   LOG_NOT,
   UNEQUAL,
   MOD,
   MOD_ASSIGN,
   BIT_AND,
   LOG_AND,
   BIT_AND_ASSIGN,
   LPAREN,
   RPAREN,
   STAR,
   MUL_ASSIGN,
   PLUS,
   INC,
   PLUS_ASSIGN,
   COMMA,
   MINUS,
   DEC,
   MINUS_ASSIGN,
   ARROW,
   ARROW_STAR,
   DOT,
   DOT_STAR,
   DOTS,
   SLASH,
   DIV_ASSIGN,
   COLON,
   SCOPE,
   SEMICOLON,
   LESS,
   SHL,
   SHL_ASSIGN,
   LESS_OR_EQUAL,
   ASSIGN,
   EQUAL,
   GREATER,
   GREATER_OR_EQUAL,
   SHR,
   SHR_ASSIGN,
   QUESTION,
   LBRACKET,
   literal_1,
   RBRACKET,
   literal_2,
   BIT_XOR,
   BIT_XOR_ASSIGN,
   LBRACE,
   BIT_OR,
   BIT_OR_ASSIGN,
   LOG_OR,
   RBRACE,
   BIT_NOT,
   keyword_bool,
   keyword_break,
   keyword_case,
   keyword_catch,
   keyword_char,
   keyword_class,
   keyword_const,
   keyword_const_cast,
   keyword_continue,
   keyword_default,
   keyword_delete,
   keyword_do,
   keyword_double,
   keyword_dynamic_cast,
   keyword_else,
   keyword_enum,
   keyword_explicit,
   keyword_extern,
   keyword_float,
   keyword_for,
   keyword_friend,
   keyword_goto,
   keyword_if,
   keyword_inline,
   keyword_int,
   keyword_long,
   keyword_mutable,
   keyword_namespace,
   keyword_new,
   keyword_operator,
   keyword_override,
   keyword_private,
   keyword_protected,
   keyword_public,
   keyword_register,
   keyword_reinterpret_cast,
   keyword_return,
   keyword_short,
   keyword_signed,
   keyword_sizeof,
   keyword_static,
   keyword_static_cast,
   keyword_stencil,
   keyword_struct,
   keyword_switch,
   keyword_template,
   keyword_this,
   keyword_throw,
   keyword_try,
   keyword_typedef,
   keyword_typeid,
   keyword_typename,
   keyword_union,
   keyword_unsigned,
   keyword_using,
   keyword_virtual,
   keyword_void,
   keyword_volatile,
   keyword_wchar_t,
   keyword_while
};

enum CmmKind
{
   simpleName,
   globalName,
   destructorName,
   compoundName,
   templateName,
   specialName,
   incExpr,
   decExpr,
   derefExpr,
   addrExpr,
   plusExpr,
   minusExpr,
   bitNotExpr,
   logNotExpr,
   sizeofExpr,
   newExpr,
   deleteExpr,
   throwExpr,
   castExpr,
   dotMemberExpr,
   arrowMemberExpr,
   mulExpr,
   divExpr,
   modExpr,
   customMulExpr,
   addExpr,
   subExpr,
   customAddExpr,
   shlExpr,
   shrExpr,
   ltExpr,
   gtExpr,
   leExpr,
   geExpr,
   eqExpr,
   neExpr,
   bitAndExpr,
   bitXorExpr,
   bitOrExpr,
   logAndExpr,
   logOrExpr,
   assignExpr,
   addAssignExpr,
   subAssignExpr,
   mulAssignExpr,
   divAssignExpr,
   modAssignExpr,
   shlAssignExpr,
   shrAssignExpr,
   andAssignExpr,
   xorAssignExpr,
   orAssignExpr,
   condExpr,
   commaExpr,
   intValue,
   realValue,
   charValue,
   stringValue,
   thisExpr,
   lambdaExpr,
   subexprExpr,
   signalSlotExpr,
   modernCastExpr,
   typeIdExpr,
   indexExpr,
   callExpr,
   fieldExpr,
   ptrFieldExpr,
   postIncExpr,
   postDecExpr,
   declSpec,
   constSpec,
   volatileSpec,
   typeSpec,
   typeName,
   simpleItem,
   simpleDecl,
   namespaceDecl,
   usingDecl,
   externDecl,
   typedefDecl,
   friendDecl,
   enumDecl,
   classDecl,
   visibilityDecl,
   templateDecl,
   stencilDecl,
   extensionStat,
   emptyStat,
   compoundStat,
   ifStat,
   whileStat,
   doStat,
   forStat,
   switchStat,
   caseStat,
   defaultStat,
   breakStat,
   continueStat,
   returnStat,
   gotoStat,
   simpleStat,
   dotsParam,
   tryStat
};

enum CmmDeclaratorKind
{
   pointerDeclarator,
   referenceDeclarator,
   basicDeclarator,
   emptyDeclarator,
   nestedDeclarator,
   arrayDeclarator,
   functionDeclarator
};

enum CmmPtrKind
{
};

enum CmmContKind
{
};

enum CmmTemplateParamKind
{
   templateTypeParam,
   templateCommonParam
};

enum CmmModernCastExprCast_kind
{
   dynamicCast,
   staticCast,
   constCast,
   reinterpreterCast
};

enum CmmClassDeclStyle
{
   classStyle,
   structStyle,
   unionStyle
};

enum CmmMemberVisibilityAccess
{
   privateAccess,
   protectedAccess,
   publicAccess
};

enum CmmBaseItemAccess
{
   privateBase,
   protectedBase,
   publicBase,
   unknownBase
};

class Parser : public Lexer
{
public:
   CmmSymbol token;
   CmmSimpleName * parse_simple_name ();
   CmmName * parse_global_variant ();
   CmmGlobalName * parse_global_name ();
   CmmName * parse_base_variant ();
   CmmName * parse_base_name ();
   CmmDestructorName * parse_destructor_name ();
   CmmName * parse_cont_variant ();
   CmmCompoundName * parse_cont_name (CmmName * store);
   CmmTemplateName * parse_template_name (CmmName * store);
   CmmName * parse_field_name ();
   CmmName * parse_qualified_name ();
   CmmName * parse_new_qualified_name ();
   CmmExpr * parse_primary_expr ();
   CmmName * parse_ident_expr ();
   CmmIntValue * parse_int_value ();
   CmmRealValue * parse_real_value ();
   CmmCharValue * parse_char_value ();
   CmmStringValue * parse_string_value ();
   CmmStringCont * parse_string_value_cont ();
   CmmThisExpr * parse_this_expr ();
   CmmLambdaExpr * parse_lambda_expr ();
   CmmSubexprExpr * parse_subexpr_expr ();
   CmmExpr * parse_postfix_start ();
   CmmSignalSlotExpr * parse_signal_slot_expr ();
   CmmModernCastExpr * parse_modern_cast_expr ();
   CmmTypeIdExpr * parse_typeid_expr ();
   CmmExpr * parse_postfix_expr ();
   CmmIndexExpr * parse_index_expr (CmmExpr * store);
   CmmCallExpr * parse_call_expr (CmmExpr * store);
   CmmFieldExpr * parse_field_expr (CmmExpr * store);
   CmmPtrFieldExpr * parse_ptr_field_expr (CmmExpr * store);
   CmmPostIncExpr * parse_post_inc_expr (CmmExpr * store);
   CmmPostDecExpr * parse_post_dec_expr (CmmExpr * store);
   CmmExprList * parse_expr_list ();
   CmmExpr * parse_unary_expr ();
   CmmIncExpr * parse_inc_expr ();
   CmmDecExpr * parse_dec_expr ();
   CmmDerefExpr * parse_deref_expr ();
   CmmAddrExpr * parse_addr_expr ();
   CmmPlusExpr * parse_plus_expr ();
   CmmMinusExpr * parse_minus_expr ();
   CmmBitNotExpr * parse_bit_not_expr ();
   CmmLogNotExpr * parse_log_not_expr ();
   CmmSizeofExpr * parse_sizeof_expr ();
   CmmNewExpr * parse_allocation_expr ();
   CmmNewTypeId * parse_new_type_id ();
   CmmNewArrayLimit * parse_allocation_array_limit ();
   CmmDeleteExpr * parse_deallocation_expr ();
   CmmExpr * parse_cast_expr ();
   CmmExpr * parse_pm_expr ();
   CmmExpr * parse_multiplicative_expr ();
   CmmExpr * parse_additive_expr ();
   CmmExpr * parse_shift_expr ();
   CmmExpr * parse_relational_expr ();
   CmmExpr * parse_equality_expr ();
   CmmExpr * parse_and_expr ();
   CmmExpr * parse_exclusive_or_expr ();
   CmmExpr * parse_inclusive_or_expr ();
   CmmExpr * parse_logical_and_expr ();
   CmmExpr * parse_logical_or_expr ();
   CmmExpr * parse_assignment_expr ();
   CmmExpr * parse_colon_expr ();
   CmmExpr * parse_comma_expr ();
   CmmExpr * parse_expr ();
   CmmExpr * parse_const_expr ();
   CmmStat * parse_stat ();
   CmmStat * parse_nested_stat ();
   CmmStat * parse_tail_stat ();
   CmmEmptyStat * parse_empty_stat ();
   CmmCompoundStat * parse_compound_stat ();
   CmmIfStat * parse_if_stat ();
   CmmWhileStat * parse_while_stat ();
   CmmDoStat * parse_do_stat ();
   CmmForStat * parse_for_stat ();
   CmmSwitchStat * parse_switch_stat ();
   CmmCaseStat * parse_case_stat ();
   CmmDefaultStat * parse_default_stat ();
   CmmBreakStat * parse_break_stat ();
   CmmContinueStat * parse_continue_stat ();
   CmmReturnStat * parse_return_stat ();
   CmmGotoStat * parse_goto_stat ();
   CmmStat * parse_flexible_stat ();
   CmmSimpleStat * parse_simple_stat (CmmExpr * store);
   CmmDeclSpec * parse_decl_specifier ();
   CmmConstSpecifier * parse_const_specifier ();
   CmmVolatileSpecifier * parse_volatile_specifier ();
   CmmTypeSpec * parse_type_specifier ();
   CmmTypeName * parse_type_name ();
   CmmExpr * parse_type_specifiers ();
   CmmPointerDeclarator * parse_pointer_declarator ();
   CmmReferenceDeclator * parse_reference_declarator ();
   CmmCvSpecifier * parse_cv_specifier_list ();
   CmmBasicDeclarator * parse_basic_declarator ();
   CmmEmptyDeclarator * parse_empty_declarator ();
   CmmNestedDeclarator * parse_nested_declarator ();
   CmmArrayDeclarator * parse_array_declarator (CmmDeclarator * store);
   CmmFunctionDeclarator * parse_function_declarator (CmmDeclarator * store);
   CmmDeclarator * parse_entry_declarator ();
   CmmDeclarator * parse_continue_declarator ();
   CmmDeclarator * parse_declarator ();
   CmmDeclarator * parse_simple_declarator ();
   CmmDeclarator * parse_common_declarator ();
   CmmDeclarator * parse_constructor_declarator ();
   CmmPtrSpecifierSect * parse_ptr_specifier_list ();
   CmmStatSect * parse_parameter_declaration_list ();
   CmmStat * parse_parameter_declaration ();
   CmmSimpleStat * parse_value_parameter (CmmExpr * store);
   CmmSimpleDecl * parse_plain_parameter (CmmExpr * store);
   CmmSimpleItem * parse_parameter_item ();
   CmmDotsParam * parse_dots_parameter ();
   CmmTypeId * parse_type_id ();
   CmmInitializer * parse_initializer ();
   CmmInitItem * parse_initializer_item ();
   CmmInitSimple * parse_simple_initializer ();
   CmmInitList * parse_initializer_list ();
   CmmAttr * parse_attr_item ();
   CmmAttrGroup * parse_attr_group ();
   CmmAttrSect * parse_attr_list ();
   CmmSimpleDecl * parse_simple_declaration (CmmExpr * store);
   CmmSimpleItem * parse_simple_item ();
   CmmSimpleDecl * parse_constructor_declaration (CmmExpr * store);
   CmmSimpleItem * parse_constructor_item ();
   CmmStat * parse_condition ();
   CmmSimpleDecl * parse_condition_declaration (CmmExpr * store);
   CmmSimpleItem * parse_condition_item ();
   CmmSimpleStat * parse_condition_value (CmmExpr * store);
   CmmStatSect * parse_declaration_list ();
   CmmStat * parse_declaration ();
   CmmNamespaceDecl * parse_namespace_declaration ();
   CmmUsingDecl * parse_using_declaration ();
   CmmExternDecl * parse_extern_declaration ();
   CmmTypedefDecl * parse_typedef_declaration ();
   CmmFriendDecl * parse_friend_declaration ();
   CmmEnumDecl * parse_enum_declaration ();
   CmmEnumSect * parse_enum_list ();
   CmmEnumItem * parse_enumerator ();
   CmmClassDecl * parse_class_declaration ();
   CmmMemberVisibility * parse_member_visibility ();
   CmmStat * parse_member_item ();
   CmmStatSect * parse_member_list ();
   CmmBaseSect * parse_base_specifier_list ();
   CmmBaseItem * parse_base_specifier ();
   CmmCtorInitializer * parse_ctor_initializer ();
   CmmMemberInitializer * parse_member_initializer ();
   CmmConvSpec * parse_conversion_specifiers ();
   CmmSpecialFuction * parse_special_function ();
   CmmTemplateDecl * parse_template_declaration ();
   CmmStencilDecl * parse_stencil_declaration ();
   CmmStatSect * parse_stencil_member_list ();
   CmmTemplateParamSect * parse_template_param_list ();
   CmmTemplateParam * parse_template_param ();
   CmmTemplateTypeParam * parse_template_type_param ();
   CmmTemplateNormalParam * parse_template_normal_param ();
   CmmTemplateArgSect * parse_template_arg_list ();
   CmmTemplateArg * parse_template_arg ();
   CmmTryStat * parse_try_stat ();
   CmmHandlerSect * parse_handler_list ();
   CmmHandlerItem * parse_handler ();
   CmmThrowExpr * parse_throw_expr ();
   CmmExceptionSect * parse_exception_specification ();
   CmmExceptionItem * parse_exception_specification_item ();

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
   virtual void on_binary_expr (CmmBasic * item);
   virtual bool is_binary_expression (CmmBasic * item);
   virtual bool is_postfix_expression (CmmBasic * item);
   virtual bool is_cast_expression (CmmBasic * item);
   virtual void on_ident_expr (CmmName * item);
   virtual void on_int_value (CmmIntValue * item);
   virtual void on_real_value (CmmRealValue * item);
   virtual void on_char_value (CmmCharValue * item);
   virtual void on_string_value (CmmStringValue * item);
   virtual void on_this_expr (CmmThisExpr * item);
   virtual void on_subexpr_expr (CmmSubexprExpr * item);
   virtual void on_modern_cast_expr (CmmModernCastExpr * item);
   virtual void on_typeid_expr (CmmTypeIdExpr * item);
   virtual void on_type_name (CmmTypeName * item);
   virtual void on_type_specifier (CmmTypeSpec * item);
   virtual void on_const_specifier (CmmConstSpecifier * item);
   virtual void on_volatile_specifier (CmmVolatileSpecifier * item);
   virtual void on_decl_specifier (CmmDeclSpec * item);
   virtual void on_index_expr (CmmIndexExpr * item);
   virtual void on_call_expr (CmmCallExpr * item);
   virtual void on_field_expr (CmmFieldExpr * item);
   virtual void on_ptr_field_expr (CmmPtrFieldExpr * item);
   virtual void on_post_inc_expr (CmmPostIncExpr * item);
   virtual void on_post_dec_expr (CmmPostDecExpr * item);
   virtual void on_bit_not_expr (CmmBitNotExpr * item);
   virtual void on_inc_expr (CmmIncExpr * item);
   virtual void on_dec_expr (CmmDecExpr * item);
   virtual void on_deref_expr (CmmDerefExpr * item);
   virtual void on_addr_expr (CmmAddrExpr * item);
   virtual void on_plus_expr (CmmPlusExpr * item);
   virtual void on_minus_expr (CmmMinusExpr * item);
   virtual void on_log_not_expr (CmmLogNotExpr * item);
   virtual void on_sizeof_expr (CmmSizeofExpr * item);
   virtual void on_allocation_expr (CmmNewExpr * item);
   virtual void on_deallocation_expr (CmmDeleteExpr * item);
   virtual void on_throw_expr (CmmThrowExpr * item);
   virtual void on_base_name (CmmName * item);
   virtual void on_cont_name (CmmCompoundName * item);
   virtual void on_template_name (CmmTemplateName * item);
   virtual bool is_template_name (CmmName * item);
   virtual bool is_signal_slot (CmmBasic * item);
   virtual void on_middle_bit_not_expr (CmmBitNotExpr * item);
   virtual bool is_mul (CmmBasic * item);
   virtual bool is_add (CmmBasic * item);
   virtual void on_expr (CmmExpr * item);
   virtual void on_open_compound_statement (CmmCompoundStat * item);
   virtual void on_declaration (CmmBasic * item);
   virtual void on_close_compound_statement (CmmCompoundStat * item);
   virtual void on_open_if_statement (CmmIfStat * item);
   virtual void on_close_if_statement (CmmIfStat * item);
   virtual void on_open_while_statement (CmmWhileStat * item);
   virtual void on_close_while_statement (CmmWhileStat * item);
   virtual void on_open_for_statement (CmmForStat * item);
   virtual void on_close_for_statement (CmmForStat * item);
   virtual void on_open_switch_statement (CmmSwitchStat * item);
   virtual void on_close_switch_statement (CmmSwitchStat * item);
   virtual void on_open_flexible_stat ();
   virtual bool is_expression (CmmExpr * item);
   virtual bool is_constructor (CmmExpr * item);
   virtual void on_open_simple_stat (CmmSimpleStat * item);
   virtual void on_open_expr_block (CmmSimpleStat * item);
   virtual void on_close_expr_block (CmmSimpleStat * item);
   virtual void on_simple_statement (CmmSimpleStat * item);
   virtual void on_middle_decl_specifier (CmmDeclSpec * item);
   virtual void on_simple_declarator (CmmDeclarator * item);
   virtual bool is_value_parameter (CmmExpr * item);
   virtual void on_open_simple_declaration (CmmSimpleDecl * item);
   virtual void on_simple_item (CmmSimpleDecl * item);
   virtual void on_open_function (CmmSimpleDecl * item);
   virtual void on_close_function (CmmSimpleDecl * item);
   virtual void on_simple_declaration (CmmSimpleDecl * item);
   virtual void on_open_constructor_declaration (CmmSimpleDecl * item);
   virtual void on_start_namespace (CmmNamespaceDecl * item);
   virtual void on_namespace (CmmNamespaceDecl * item);
   virtual void on_open_namespace (CmmNamespaceDecl * item);
   virtual void on_close_namespace (CmmNamespaceDecl * item);
   virtual void on_stop_namespace (CmmNamespaceDecl * item);
   virtual void on_using (CmmUsingDecl * item);
   virtual void on_typedef (CmmTypedefDecl * item);
   virtual void on_start_enum (CmmEnumDecl * item);
   virtual void on_enum (CmmEnumDecl * item);
   virtual void on_open_enum (CmmEnumDecl * item);
   virtual void on_close_enum (CmmEnumDecl * item);
   virtual void on_stop_enum (CmmEnumDecl * item);
   virtual void on_enum_item (CmmEnumItem * item);
   virtual void on_start_class (CmmClassDecl * item);
   virtual void on_class (CmmClassDecl * item);
   virtual void on_open_class (CmmClassDecl * item);
   virtual void on_close_class (CmmClassDecl * item);
   virtual void on_stop_class (CmmClassDecl * item);
   virtual void on_member_visibility (CmmMemberVisibility * item);
   virtual void on_start_member_item (CmmStatSect * item);
   virtual void on_member_initializer (CmmMemberInitializer * item);
   virtual void on_template_declaration (CmmTemplateDecl * item);
   virtual void on_stencil_params (CmmStencilDecl * item);
   virtual void on_open_stencil (CmmStencilDecl * item);
   virtual void on_close_stencil (CmmStencilDecl * item);
   virtual void on_stencil_declaration (CmmStencilDecl * item);
   Parser ();
};

class CmmBasic
{
public:
   int src_file;
   int src_line;
   int src_column;

   inline CmmBasic () :
      src_file (0),
      src_line (0),
      src_column (0)
   {
   }

   inline virtual CmmCommon * conv_CmmCommon ()
   {

         return NULL;
   }

   inline virtual CmmExpr * conv_CmmExpr ()
   {
         return NULL;
   }

   inline virtual CmmName * conv_CmmName ()
   {
         return NULL;
   }

   inline virtual CmmUnaryExpr * conv_CmmUnaryExpr ()
   {
         return NULL;
   }

   inline virtual CmmBinaryExpr * conv_CmmBinaryExpr ()
   {
         return NULL;
   }

   inline virtual CmmStat * conv_CmmStat ()
   {
         return NULL;
   }

   inline virtual CmmDecl * conv_CmmDecl ()
   {
         return NULL;
   }

   inline virtual CmmSimpleItem * conv_CmmSimpleItem ()
   {
         return NULL;
   }

   inline virtual CmmExtensionStat * conv_CmmExtensionStat ()
   {
         return NULL;
   }

   inline virtual CmmSimpleName * conv_CmmSimpleName ()
   {
         return NULL;
   }

   inline virtual CmmGlobalName * conv_CmmGlobalName ()
   {
         return NULL;
   }

   inline virtual CmmDestructorName * conv_CmmDestructorName ()
   {
         return NULL;
   }

   inline virtual CmmCompoundName * conv_CmmCompoundName ()
   {
         return NULL;
   }

   inline virtual CmmTemplateName * conv_CmmTemplateName ()
   {
         return NULL;
   }

   inline virtual CmmIntValue * conv_CmmIntValue ()
   {
         return NULL;
   }

   inline virtual CmmRealValue * conv_CmmRealValue ()
   {
         return NULL;
   }

   inline virtual CmmCharValue * conv_CmmCharValue ()
   {
         return NULL;
   }

   inline virtual CmmStringValue * conv_CmmStringValue ()
   {
         return NULL;
   }

   inline virtual CmmThisExpr * conv_CmmThisExpr ()
   {
         return NULL;
   }

   inline virtual CmmLambdaExpr * conv_CmmLambdaExpr ()
   {
         return NULL;
   }

   inline virtual CmmSubexprExpr * conv_CmmSubexprExpr ()
   {
         return NULL;
   }

   inline virtual CmmSignalSlotExpr * conv_CmmSignalSlotExpr ()
   {
         return NULL;
   }

   inline virtual CmmModernCastExpr * conv_CmmModernCastExpr ()
   {
         return NULL;
   }

   inline virtual CmmTypeIdExpr * conv_CmmTypeIdExpr ()
   {
         return NULL;
   }

   inline virtual CmmIndexExpr * conv_CmmIndexExpr ()
   {
         return NULL;
   }

   inline virtual CmmCallExpr * conv_CmmCallExpr ()
   {
         return NULL;
   }

   inline virtual CmmFieldExpr * conv_CmmFieldExpr ()
   {
         return NULL;
   }

   inline virtual CmmPtrFieldExpr * conv_CmmPtrFieldExpr ()
   {
         return NULL;
   }

   inline virtual CmmPostIncExpr * conv_CmmPostIncExpr ()
   {
         return NULL;
   }

   inline virtual CmmPostDecExpr * conv_CmmPostDecExpr ()
   {
         return NULL;
   }

   inline virtual CmmIncExpr * conv_CmmIncExpr ()
   {
         return NULL;
   }

   inline virtual CmmDecExpr * conv_CmmDecExpr ()
   {
         return NULL;
   }

   inline virtual CmmDerefExpr * conv_CmmDerefExpr ()
   {
         return NULL;
   }

   inline virtual CmmAddrExpr * conv_CmmAddrExpr ()
   {
         return NULL;
   }

   inline virtual CmmPlusExpr * conv_CmmPlusExpr ()
   {
         return NULL;
   }

   inline virtual CmmMinusExpr * conv_CmmMinusExpr ()
   {
         return NULL;
   }

   inline virtual CmmBitNotExpr * conv_CmmBitNotExpr ()
   {
         return NULL;
   }

   inline virtual CmmLogNotExpr * conv_CmmLogNotExpr ()
   {
         return NULL;
   }

   inline virtual CmmSizeofExpr * conv_CmmSizeofExpr ()
   {
         return NULL;
   }

   inline virtual CmmNewExpr * conv_CmmNewExpr ()
   {
         return NULL;
   }

   inline virtual CmmDeleteExpr * conv_CmmDeleteExpr ()
   {
         return NULL;
   }

   inline virtual CmmEmptyStat * conv_CmmEmptyStat ()
   {
         return NULL;
   }

   inline virtual CmmCompoundStat * conv_CmmCompoundStat ()
   {
         return NULL;
   }

   inline virtual CmmIfStat * conv_CmmIfStat ()
   {
         return NULL;
   }

   inline virtual CmmWhileStat * conv_CmmWhileStat ()
   {
         return NULL;
   }

   inline virtual CmmDoStat * conv_CmmDoStat ()
   {
         return NULL;
   }

   inline virtual CmmForStat * conv_CmmForStat ()
   {
         return NULL;
   }

   inline virtual CmmSwitchStat * conv_CmmSwitchStat ()
   {
         return NULL;
   }

   inline virtual CmmCaseStat * conv_CmmCaseStat ()
   {
         return NULL;
   }

   inline virtual CmmDefaultStat * conv_CmmDefaultStat ()
   {
         return NULL;
   }

   inline virtual CmmBreakStat * conv_CmmBreakStat ()
   {
         return NULL;
   }

   inline virtual CmmContinueStat * conv_CmmContinueStat ()
   {
         return NULL;
   }

   inline virtual CmmReturnStat * conv_CmmReturnStat ()
   {
         return NULL;
   }

   inline virtual CmmGotoStat * conv_CmmGotoStat ()
   {
         return NULL;
   }

   inline virtual CmmSimpleStat * conv_CmmSimpleStat ()
   {
         return NULL;
   }

   inline virtual CmmDeclSpec * conv_CmmDeclSpec ()
   {
         return NULL;
   }

   inline virtual CmmConstSpecifier * conv_CmmConstSpecifier ()
   {
         return NULL;
   }

   inline virtual CmmVolatileSpecifier * conv_CmmVolatileSpecifier ()
   {
         return NULL;
   }

   inline virtual CmmTypeSpec * conv_CmmTypeSpec ()
   {
         return NULL;
   }

   inline virtual CmmTypeName * conv_CmmTypeName ()
   {
         return NULL;
   }

   inline virtual CmmSimpleDecl * conv_CmmSimpleDecl ()
   {
         return NULL;
   }

   inline virtual CmmDotsParam * conv_CmmDotsParam ()
   {
         return NULL;
   }

   inline virtual CmmNamespaceDecl * conv_CmmNamespaceDecl ()
   {
         return NULL;
   }

   inline virtual CmmUsingDecl * conv_CmmUsingDecl ()
   {
         return NULL;
   }

   inline virtual CmmExternDecl * conv_CmmExternDecl ()
   {
         return NULL;
   }

   inline virtual CmmTypedefDecl * conv_CmmTypedefDecl ()
   {
         return NULL;
   }

   inline virtual CmmFriendDecl * conv_CmmFriendDecl ()
   {
         return NULL;
   }

   inline virtual CmmEnumDecl * conv_CmmEnumDecl ()
   {
         return NULL;
   }

   inline virtual CmmClassDecl * conv_CmmClassDecl ()
   {
         return NULL;
   }

   inline virtual CmmMemberVisibility * conv_CmmMemberVisibility ()
   {
         return NULL;
   }

   inline virtual CmmSpecialFuction * conv_CmmSpecialFuction ()
   {
         return NULL;
   }

   inline virtual CmmTemplateDecl * conv_CmmTemplateDecl ()
   {
         return NULL;
   }

   inline virtual CmmStencilDecl * conv_CmmStencilDecl ()
   {
         return NULL;
   }

   inline virtual CmmTryStat * conv_CmmTryStat ()
   {
         return NULL;
   }

   inline virtual CmmThrowExpr * conv_CmmThrowExpr ()
   {
         return NULL;
   }

   inline virtual CmmCastExpr * conv_CmmCastExpr ()
   {
         return NULL;
   }

   inline virtual CmmPtrMemExpr * conv_CmmPtrMemExpr ()
   {
         return NULL;
   }

   inline virtual CmmMulExpr * conv_CmmMulExpr ()
   {
         return NULL;
   }

   inline virtual CmmAddExpr * conv_CmmAddExpr ()
   {
         return NULL;
   }

   inline virtual CmmShiftExpr * conv_CmmShiftExpr ()
   {
         return NULL;
   }

   inline virtual CmmRelExpr * conv_CmmRelExpr ()
   {
         return NULL;
   }

   inline virtual CmmEqExpr * conv_CmmEqExpr ()
   {
         return NULL;
   }

   inline virtual CmmAndExpr * conv_CmmAndExpr ()
   {
         return NULL;
   }

   inline virtual CmmXorExpr * conv_CmmXorExpr ()
   {
         return NULL;
   }

   inline virtual CmmOrExpr * conv_CmmOrExpr ()
   {
         return NULL;
   }

   inline virtual CmmAndAndExpr * conv_CmmAndAndExpr ()
   {
         return NULL;
   }

   inline virtual CmmOrOrExpr * conv_CmmOrOrExpr ()
   {
         return NULL;
   }

   inline virtual CmmAssignExpr * conv_CmmAssignExpr ()
   {
         return NULL;
   }

   inline virtual CmmCommaExpr * conv_CmmCommaExpr ()
   {
         return NULL;
   }

   inline virtual CmmBasic * conv_CmmBasic ()
   {
         return this;
   }
};

class CmmCommon : public CmmBasic
{
public:
   CmmKind kind;

   inline CmmCommon () :
      kind (CmmKind (0))
   {
   }

   inline virtual CmmCommon * conv_CmmCommon ()
   {

         return this;
   }
};

class CmmExpr : public CmmCommon
{
public:
   bool type_flag;
   bool constructor_flag;
   bool destructor_flag;
   CmmDecl * item_decl;
   CmmBasic * item_type;
   string alt_assign;
   string alt_assign_index;
   string alt_assign_param;
   string alt_read;
   string alt_connect;
   CmmExpr * alt_connect_expr;
   CmmDecl * alt_connect_decl;
   string alt_connect_signal;
   string alt_display;
   string alt_store;
   string alt_read_json;
   string alt_write_json;
   string alt_read_xml;
   string alt_write_xml;
   bool gpu_global;
   bool extra_assign;
   bool call_func;
   CmmClassDecl * class_member;
   bool var_field;
   bool str_field;
   bool stream_flag;
   bool leading_flag;
   vector < CmmDecl * > following_items;

   inline CmmExpr () :
      type_flag (false),
      constructor_flag (false),
      destructor_flag (false),
      item_decl (NULL),
      item_type (NULL),
      alt_assign (""),
      alt_assign_index (""),
      alt_assign_param (""),
      alt_read (""),
      alt_connect (""),
      alt_connect_expr (NULL),
      alt_connect_decl (NULL),
      alt_connect_signal (""),
      alt_display (""),
      alt_store (""),
      alt_read_json (""),
      alt_write_json (""),
      alt_read_xml (""),
      alt_write_xml (""),
      gpu_global (false),
      extra_assign (false),
      call_func (false),
      class_member (NULL),
      var_field (false),
      str_field (false),
      stream_flag (false),
      leading_flag (false),
      following_items ()
   {
   }

   inline virtual CmmExpr * conv_CmmExpr ()
   {

         return this;
   }
};

class CmmName : public CmmExpr
{
public:

   inline CmmName ()
   {
   }

   inline virtual CmmName * conv_CmmName ()
   {

         return this;
   }
};

class CmmUnaryExpr : public CmmExpr
{
public:

   inline CmmUnaryExpr ()
   {
   }

   inline virtual CmmUnaryExpr * conv_CmmUnaryExpr ()
   {

         return this;
   }
};

class CmmBinaryExpr : public CmmExpr
{
public:

   inline CmmBinaryExpr ()
   {
   }

   inline virtual CmmBinaryExpr * conv_CmmBinaryExpr ()
   {

         return this;
   }
};

class CmmStat : public CmmCommon
{
public:
   bool move_statement;

   inline CmmStat () :
      move_statement (false)
   {
   }

   inline virtual CmmStat * conv_CmmStat ()
   {

         return this;
   }
};

class CmmDecl : public CmmStat
{
public:

   inline CmmDecl ()
   {
   }

   inline virtual CmmDecl * conv_CmmDecl ()
   {

         return this;
   }
};

class CmmSimpleItem : public CmmDecl
{
public:
   bool no_init;
   bool extra_assign;
   bool cont_line;
   CmmDeclarator * declarator;
   CmmInitializer * init;
   CmmAttrSect * attr;

   inline CmmSimpleItem () :
      no_init (false),
      extra_assign (false),
      cont_line (false),
      declarator (NULL),
      init (NULL),
      attr (NULL)
   {

         kind = simpleItem;
   }

   inline virtual CmmSimpleItem * conv_CmmSimpleItem ()
   {
         return this;
   }
};

class CmmDeclarator : public CmmBasic
{
public:
   CmmDeclaratorKind kind;

   inline CmmDeclarator () :
      kind (CmmDeclaratorKind (0))
   {
   }

   inline virtual CmmPointerDeclarator * conv_CmmPointerDeclarator ()
   {

         return NULL;
   }

   inline virtual CmmReferenceDeclator * conv_CmmReferenceDeclator ()
   {
         return NULL;
   }

   inline virtual CmmBasicDeclarator * conv_CmmBasicDeclarator ()
   {
         return NULL;
   }

   inline virtual CmmEmptyDeclarator * conv_CmmEmptyDeclarator ()
   {
         return NULL;
   }

   inline virtual CmmNestedDeclarator * conv_CmmNestedDeclarator ()
   {
         return NULL;
   }

   inline virtual CmmArrayDeclarator * conv_CmmArrayDeclarator ()
   {
         return NULL;
   }

   inline virtual CmmFunctionDeclarator * conv_CmmFunctionDeclarator ()
   {
         return NULL;
   }

   inline virtual CmmDeclarator * conv_CmmDeclarator ()
   {
         return this;
   }
};

class CmmPtrSpecifier : public CmmBasic
{
public:
   CmmPtrKind kind;

   inline CmmPtrSpecifier () :
      kind (CmmPtrKind (0))
   {
   }

   inline virtual CmmPtrSpecifier * conv_CmmPtrSpecifier ()
   {

         return this;
   }
};

class CmmContSpecifier : public CmmBasic
{
public:
   CmmContKind kind;

   inline CmmContSpecifier () :
      kind (CmmContKind (0))
   {
   }

   inline virtual CmmContSpecifier * conv_CmmContSpecifier ()
   {

         return this;
   }
};

class CmmTemplateParam : public CmmBasic
{
public:
   CmmTemplateParamKind kind;

   inline CmmTemplateParam () :
      kind (CmmTemplateParamKind (0))
   {
   }

   inline virtual CmmTemplateTypeParam * conv_CmmTemplateTypeParam ()
   {

         return NULL;
   }

   inline virtual CmmTemplateNormalParam * conv_CmmTemplateNormalParam ()
   {
         return NULL;
   }

   inline virtual CmmTemplateParam * conv_CmmTemplateParam ()
   {
         return this;
   }
};

class CmmExtensionStat : public CmmStat
{
public:

   inline CmmExtensionStat ()
   {

         kind = extensionStat;
   }

   inline virtual CmmExtensionStat * conv_CmmExtensionStat ()
   {
         return this;
   }
};

class CmmSimpleName : public CmmName
{
public:
   string id;

   inline CmmSimpleName () :
      id ("")
   {

         kind = simpleName;
   }

   inline virtual CmmSimpleName * conv_CmmSimpleName ()
   {
         return this;
   }
};

class CmmGlobalName : public CmmName
{
public:
   CmmName * inner_name;

   inline CmmGlobalName () :
      inner_name (NULL)
   {

         kind = globalName;
   }

   inline virtual CmmGlobalName * conv_CmmGlobalName ()
   {
         return this;
   }
};

class CmmDestructorName : public CmmName
{
public:
   CmmSimpleName * inner_name;

   inline CmmDestructorName () :
      inner_name (NULL)
   {

         kind = destructorName;
   }

   inline virtual CmmDestructorName * conv_CmmDestructorName ()
   {
         return this;
   }
};

class CmmCompoundName : public CmmName
{
public:
   CmmName * left;
   CmmName * right;

   inline CmmCompoundName () :
      left (NULL),
      right (NULL)
   {

         kind = compoundName;
   }

   inline virtual CmmCompoundName * conv_CmmCompoundName ()
   {
         return this;
   }
};

class CmmTemplateName : public CmmName
{
public:
   CmmName * left;
   CmmTemplateArgSect * template_args;

   inline CmmTemplateName () :
      left (NULL),
      template_args (NULL)
   {

         kind = templateName;
   }

   inline virtual CmmTemplateName * conv_CmmTemplateName ()
   {
         return this;
   }
};

class CmmIntValue : public CmmExpr
{
public:
   string value;

   inline CmmIntValue () :
      value ("")
   {

         kind = intValue;
   }

   inline virtual CmmIntValue * conv_CmmIntValue ()
   {
         return this;
   }
};

class CmmRealValue : public CmmExpr
{
public:
   string value;

   inline CmmRealValue () :
      value ("")
   {

         kind = realValue;
   }

   inline virtual CmmRealValue * conv_CmmRealValue ()
   {
         return this;
   }
};

class CmmCharValue : public CmmExpr
{
public:
   string value;

   inline CmmCharValue () :
      value ("")
   {

         kind = charValue;
   }

   inline virtual CmmCharValue * conv_CmmCharValue ()
   {
         return this;
   }
};

class CmmStringValue : public CmmExpr
{
public:
   string value;
   vector < CmmStringCont * > items;

   inline CmmStringValue () :
      value (""),
      items ()
   {

         kind = stringValue;
   }

   inline virtual CmmStringValue * conv_CmmStringValue ()
   {
         return this;
   }
};

class CmmStringCont : public CmmBasic
{
public:
   string value;

   inline CmmStringCont () :
      value ("")
   {
   }

   inline virtual CmmStringCont * conv_CmmStringCont ()
   {

         return this;
   }
};

class CmmThisExpr : public CmmExpr
{
public:

   inline CmmThisExpr ()
   {

         kind = thisExpr;
   }

   inline virtual CmmThisExpr * conv_CmmThisExpr ()
   {
         return this;
   }
};

class CmmLambdaExpr : public CmmExpr
{
public:
   bool by_reference;
   CmmCompoundStat * body;

   inline CmmLambdaExpr () :
      by_reference (false),
      body (NULL)
   {

         kind = lambdaExpr;
   }

   inline virtual CmmLambdaExpr * conv_CmmLambdaExpr ()
   {
         return this;
   }
};

class CmmSubexprExpr : public CmmExpr
{
public:
   CmmExpr * param;

   inline CmmSubexprExpr () :
      param (NULL)
   {

         kind = subexprExpr;
   }

   inline virtual CmmSubexprExpr * conv_CmmSubexprExpr ()
   {
         return this;
   }
};

class CmmSignalSlotExpr : public CmmExpr
{
public:
   string macro_name;
   string func_name;
   CmmStatSect * parameters;

   inline CmmSignalSlotExpr () :
      macro_name (""),
      func_name (""),
      parameters (NULL)
   {

         kind = signalSlotExpr;
   }

   inline virtual CmmSignalSlotExpr * conv_CmmSignalSlotExpr ()
   {
         return this;
   }
};

class CmmModernCastExpr : public CmmExpr
{
public:
   CmmModernCastExprCast_kind cast_kind;
   CmmTypeId * type;
   CmmExpr * param;

   inline CmmModernCastExpr () :
      cast_kind (CmmModernCastExprCast_kind (0)),
      type (NULL),
      param (NULL)
   {

         kind = modernCastExpr;
   }

   inline virtual CmmModernCastExpr * conv_CmmModernCastExpr ()
   {
         return this;
   }
};

class CmmTypeIdExpr : public CmmExpr
{
public:
   CmmExpr * value;

   inline CmmTypeIdExpr () :
      value (NULL)
   {

         kind = typeIdExpr;
   }

   inline virtual CmmTypeIdExpr * conv_CmmTypeIdExpr ()
   {
         return this;
   }
};

class CmmIndexExpr : public CmmExpr
{
public:
   CmmExpr * left;
   CmmExpr * param;

   inline CmmIndexExpr () :
      left (NULL),
      param (NULL)
   {

         kind = indexExpr;
   }

   inline virtual CmmIndexExpr * conv_CmmIndexExpr ()
   {
         return this;
   }
};

class CmmCallExpr : public CmmExpr
{
public:
   CmmExpr * left;
   CmmExprList * param_list;

   inline CmmCallExpr () :
      left (NULL),
      param_list (NULL)
   {

         kind = callExpr;
   }

   inline virtual CmmCallExpr * conv_CmmCallExpr ()
   {
         return this;
   }
};

class CmmFieldExpr : public CmmExpr
{
public:
   CmmExpr * left;
   CmmName * field_name;

   inline CmmFieldExpr () :
      left (NULL),
      field_name (NULL)
   {

         kind = fieldExpr;
   }

   inline virtual CmmFieldExpr * conv_CmmFieldExpr ()
   {
         return this;
   }
};

class CmmPtrFieldExpr : public CmmExpr
{
public:
   CmmExpr * left;
   CmmName * field_name;

   inline CmmPtrFieldExpr () :
      left (NULL),
      field_name (NULL)
   {

         kind = ptrFieldExpr;
   }

   inline virtual CmmPtrFieldExpr * conv_CmmPtrFieldExpr ()
   {
         return this;
   }
};

class CmmPostIncExpr : public CmmExpr
{
public:
   CmmExpr * left;

   inline CmmPostIncExpr () :
      left (NULL)
   {

         kind = postIncExpr;
   }

   inline virtual CmmPostIncExpr * conv_CmmPostIncExpr ()
   {
         return this;
   }
};

class CmmPostDecExpr : public CmmExpr
{
public:
   CmmExpr * left;

   inline CmmPostDecExpr () :
      left (NULL)
   {

         kind = postDecExpr;
   }

   inline virtual CmmPostDecExpr * conv_CmmPostDecExpr ()
   {
         return this;
   }
};

class CmmExprList : public CmmBasic
{
public:
   vector < CmmExpr * > items;

   inline CmmExprList () :
      items ()
   {
   }

   inline virtual CmmExprList * conv_CmmExprList ()
   {

         return this;
   }
};

class CmmIncExpr : public CmmUnaryExpr
{
public:
   CmmExpr * param;

   inline CmmIncExpr () :
      param (NULL)
   {

         kind = incExpr;
   }

   inline virtual CmmIncExpr * conv_CmmIncExpr ()
   {
         return this;
   }
};

class CmmDecExpr : public CmmUnaryExpr
{
public:
   CmmExpr * param;

   inline CmmDecExpr () :
      param (NULL)
   {

         kind = decExpr;
   }

   inline virtual CmmDecExpr * conv_CmmDecExpr ()
   {
         return this;
   }
};

class CmmDerefExpr : public CmmUnaryExpr
{
public:
   CmmExpr * param;

   inline CmmDerefExpr () :
      param (NULL)
   {

         kind = derefExpr;
   }

   inline virtual CmmDerefExpr * conv_CmmDerefExpr ()
   {
         return this;
   }
};

class CmmAddrExpr : public CmmUnaryExpr
{
public:
   CmmExpr * param;

   inline CmmAddrExpr () :
      param (NULL)
   {

         kind = addrExpr;
   }

   inline virtual CmmAddrExpr * conv_CmmAddrExpr ()
   {
         return this;
   }
};

class CmmPlusExpr : public CmmUnaryExpr
{
public:
   CmmExpr * param;

   inline CmmPlusExpr () :
      param (NULL)
   {

         kind = plusExpr;
   }

   inline virtual CmmPlusExpr * conv_CmmPlusExpr ()
   {
         return this;
   }
};

class CmmMinusExpr : public CmmUnaryExpr
{
public:
   CmmExpr * param;

   inline CmmMinusExpr () :
      param (NULL)
   {

         kind = minusExpr;
   }

   inline virtual CmmMinusExpr * conv_CmmMinusExpr ()
   {
         return this;
   }
};

class CmmBitNotExpr : public CmmUnaryExpr
{
public:
   CmmExpr * param;

   inline CmmBitNotExpr () :
      param (NULL)
   {

         kind = bitNotExpr;
   }

   inline virtual CmmBitNotExpr * conv_CmmBitNotExpr ()
   {
         return this;
   }
};

class CmmLogNotExpr : public CmmUnaryExpr
{
public:
   CmmExpr * param;

   inline CmmLogNotExpr () :
      param (NULL)
   {

         kind = logNotExpr;
   }

   inline virtual CmmLogNotExpr * conv_CmmLogNotExpr ()
   {
         return this;
   }
};

class CmmSizeofExpr : public CmmUnaryExpr
{
public:
   CmmExpr * value;

   inline CmmSizeofExpr () :
      value (NULL)
   {

         kind = sizeofExpr;
   }

   inline virtual CmmSizeofExpr * conv_CmmSizeofExpr ()
   {
         return this;
   }
};

class CmmNewExpr : public CmmUnaryExpr
{
public:
   CmmNewTypeId * type1;
   CmmTypeId * type2;
   CmmExprList * init_list;

   inline CmmNewExpr () :
      type1 (NULL),
      type2 (NULL),
      init_list (NULL)
   {

         kind = newExpr;
   }

   inline virtual CmmNewExpr * conv_CmmNewExpr ()
   {
         return this;
   }
};

class CmmNewTypeId : public CmmBasic
{
public:
   CmmExpr * type_spec;
   CmmPtrSpecifierSect * ptr;
   vector < CmmNewArrayLimit * > items;

   inline CmmNewTypeId () :
      type_spec (NULL),
      ptr (NULL),
      items ()
   {
   }

   inline virtual CmmNewTypeId * conv_CmmNewTypeId ()
   {

         return this;
   }
};

class CmmNewArrayLimit : public CmmBasic
{
public:
   CmmExpr * value;

   inline CmmNewArrayLimit () :
      value (NULL)
   {
   }

   inline virtual CmmNewArrayLimit * conv_CmmNewArrayLimit ()
   {

         return this;
   }
};

class CmmDeleteExpr : public CmmUnaryExpr
{
public:
   bool a_array;
   CmmExpr * param;

   inline CmmDeleteExpr () :
      a_array (false),
      param (NULL)
   {

         kind = deleteExpr;
   }

   inline virtual CmmDeleteExpr * conv_CmmDeleteExpr ()
   {
         return this;
   }
};

class CmmEmptyStat : public CmmStat
{
public:

   inline CmmEmptyStat ()
   {

         kind = emptyStat;
   }

   inline virtual CmmEmptyStat * conv_CmmEmptyStat ()
   {
         return this;
   }
};

class CmmCompoundStat : public CmmStat
{
public:
   vector < CmmStat * > items;

   inline CmmCompoundStat () :
      items ()
   {

         kind = compoundStat;
   }

   inline virtual CmmCompoundStat * conv_CmmCompoundStat ()
   {
         return this;
   }
};

class CmmIfStat : public CmmStat
{
public:
   CmmStat * cond;
   CmmStat * then_stat;
   CmmStat * else_stat;

   inline CmmIfStat () :
      cond (NULL),
      then_stat (NULL),
      else_stat (NULL)
   {

         kind = ifStat;
   }

   inline virtual CmmIfStat * conv_CmmIfStat ()
   {
         return this;
   }
};

class CmmWhileStat : public CmmStat
{
public:
   CmmStat * cond;
   CmmStat * body;

   inline CmmWhileStat () :
      cond (NULL),
      body (NULL)
   {

         kind = whileStat;
   }

   inline virtual CmmWhileStat * conv_CmmWhileStat ()
   {
         return this;
   }
};

class CmmDoStat : public CmmStat
{
public:
   CmmStat * body;
   CmmExpr * cond_expr;

   inline CmmDoStat () :
      body (NULL),
      cond_expr (NULL)
   {

         kind = doStat;
   }

   inline virtual CmmDoStat * conv_CmmDoStat ()
   {
         return this;
   }
};

class CmmForStat : public CmmStat
{
public:
   CmmStat * from_expr;
   CmmExpr * iter_expr;
   CmmExpr * cond_expr;
   CmmExpr * step_expr;
   CmmStat * body;

   inline CmmForStat () :
      from_expr (NULL),
      iter_expr (NULL),
      cond_expr (NULL),
      step_expr (NULL),
      body (NULL)
   {

         kind = forStat;
   }

   inline virtual CmmForStat * conv_CmmForStat ()
   {
         return this;
   }
};

class CmmSwitchStat : public CmmStat
{
public:
   CmmStat * cond;
   CmmStat * body;

   inline CmmSwitchStat () :
      cond (NULL),
      body (NULL)
   {

         kind = switchStat;
   }

   inline virtual CmmSwitchStat * conv_CmmSwitchStat ()
   {
         return this;
   }
};

class CmmCaseStat : public CmmStat
{
public:
   CmmExpr * case_expr;
   CmmStat * body;

   inline CmmCaseStat () :
      case_expr (NULL),
      body (NULL)
   {

         kind = caseStat;
   }

   inline virtual CmmCaseStat * conv_CmmCaseStat ()
   {
         return this;
   }
};

class CmmDefaultStat : public CmmStat
{
public:
   CmmStat * body;

   inline CmmDefaultStat () :
      body (NULL)
   {

         kind = defaultStat;
   }

   inline virtual CmmDefaultStat * conv_CmmDefaultStat ()
   {
         return this;
   }
};

class CmmBreakStat : public CmmStat
{
public:

   inline CmmBreakStat ()
   {

         kind = breakStat;
   }

   inline virtual CmmBreakStat * conv_CmmBreakStat ()
   {
         return this;
   }
};

class CmmContinueStat : public CmmStat
{
public:

   inline CmmContinueStat ()
   {

         kind = continueStat;
   }

   inline virtual CmmContinueStat * conv_CmmContinueStat ()
   {
         return this;
   }
};

class CmmReturnStat : public CmmStat
{
public:
   CmmExpr * return_expr;

   inline CmmReturnStat () :
      return_expr (NULL)
   {

         kind = returnStat;
   }

   inline virtual CmmReturnStat * conv_CmmReturnStat ()
   {
         return this;
   }
};

class CmmGotoStat : public CmmStat
{
public:
   string goto_lab;

   inline CmmGotoStat () :
      goto_lab ("")
   {

         kind = gotoStat;
   }

   inline virtual CmmGotoStat * conv_CmmGotoStat ()
   {
         return this;
   }
};

class CmmSimpleStat : public CmmStat
{
public:
   CmmExpr * inner_expr;
   CmmCompoundStat * body;

   inline CmmSimpleStat () :
      inner_expr (NULL),
      body (NULL)
   {

         kind = simpleStat;
   }

   inline virtual CmmSimpleStat * conv_CmmSimpleStat ()
   {
         return this;
   }
};

class CmmDeclSpec : public CmmExpr
{
public:
   bool a_inline;
   bool a_virtual;
   bool a_explicit;
   bool a_mutable;
   bool a_static;
   bool a_register;
   bool a_destructor;
   CmmExpr * param;

   inline CmmDeclSpec () :
      a_inline (false),
      a_virtual (false),
      a_explicit (false),
      a_mutable (false),
      a_static (false),
      a_register (false),
      a_destructor (false),
      param (NULL)
   {

         kind = declSpec;
   }

   inline virtual CmmDeclSpec * conv_CmmDeclSpec ()
   {
         return this;
   }
};

class CmmConstSpecifier : public CmmExpr
{
public:
   CmmExpr * param;

   inline CmmConstSpecifier () :
      param (NULL)
   {

         kind = constSpec;
   }

   inline virtual CmmConstSpecifier * conv_CmmConstSpecifier ()
   {
         return this;
   }
};

class CmmVolatileSpecifier : public CmmExpr
{
public:
   CmmExpr * param;

   inline CmmVolatileSpecifier () :
      param (NULL)
   {

         kind = volatileSpec;
   }

   inline virtual CmmVolatileSpecifier * conv_CmmVolatileSpecifier ()
   {
         return this;
   }
};

class CmmTypeSpec : public CmmExpr
{
public:
   bool a_signed;
   bool a_unsigned;
   bool a_short;
   bool a_long;
   bool a_long_long;
   bool a_long_double;
   bool a_bool;
   bool a_char;
   bool a_wchar;
   bool a_int;
   bool a_float;
   bool a_double;
   bool a_void;

   inline CmmTypeSpec () :
      a_signed (false),
      a_unsigned (false),
      a_short (false),
      a_long (false),
      a_long_long (false),
      a_long_double (false),
      a_bool (false),
      a_char (false),
      a_wchar (false),
      a_int (false),
      a_float (false),
      a_double (false),
      a_void (false)
   {

         kind = typeSpec;
   }

   inline virtual CmmTypeSpec * conv_CmmTypeSpec ()
   {
         return this;
   }
};

class CmmTypeName : public CmmExpr
{
public:
   CmmName * qual_name;

   inline CmmTypeName () :
      qual_name (NULL)
   {

         kind = typeName;
   }

   inline virtual CmmTypeName * conv_CmmTypeName ()
   {
         return this;
   }
};

class CmmPointerDeclarator : public CmmDeclarator
{
public:
   CmmCvSpecifier * cv_spec;
   CmmDeclarator * inner_declarator;

   inline CmmPointerDeclarator () :
      cv_spec (NULL),
      inner_declarator (NULL)
   {

         kind = pointerDeclarator;
   }

   inline virtual CmmPointerDeclarator * conv_CmmPointerDeclarator ()
   {
         return this;
   }
};

class CmmReferenceDeclator : public CmmDeclarator
{
public:
   CmmCvSpecifier * cv_spec;
   CmmDeclarator * inner_declarator;

   inline CmmReferenceDeclator () :
      cv_spec (NULL),
      inner_declarator (NULL)
   {

         kind = referenceDeclarator;
   }

   inline virtual CmmReferenceDeclator * conv_CmmReferenceDeclator ()
   {
         return this;
   }
};

class CmmCvSpecifier : public CmmBasic
{
public:
   bool cv_const;
   bool cv_volatile;

   inline CmmCvSpecifier () :
      cv_const (false),
      cv_volatile (false)
   {
   }

   inline virtual CmmCvSpecifier * conv_CmmCvSpecifier ()
   {

         return this;
   }
};

class CmmBasicDeclarator : public CmmDeclarator
{
public:
   CmmName * qual_name;

   inline CmmBasicDeclarator () :
      qual_name (NULL)
   {

         kind = basicDeclarator;
   }

   inline virtual CmmBasicDeclarator * conv_CmmBasicDeclarator ()
   {
         return this;
   }
};

class CmmEmptyDeclarator : public CmmDeclarator
{
public:

   inline CmmEmptyDeclarator ()
   {

         kind = emptyDeclarator;
   }

   inline virtual CmmEmptyDeclarator * conv_CmmEmptyDeclarator ()
   {
         return this;
   }
};

class CmmNestedDeclarator : public CmmDeclarator
{
public:
   CmmDeclarator * inner_declarator;

   inline CmmNestedDeclarator () :
      inner_declarator (NULL)
   {

         kind = nestedDeclarator;
   }

   inline virtual CmmNestedDeclarator * conv_CmmNestedDeclarator ()
   {
         return this;
   }
};

class CmmArrayDeclarator : public CmmDeclarator
{
public:
   CmmDeclarator * inner_declarator;
   CmmExpr * lim;

   inline CmmArrayDeclarator () :
      inner_declarator (NULL),
      lim (NULL)
   {

         kind = arrayDeclarator;
   }

   inline virtual CmmArrayDeclarator * conv_CmmArrayDeclarator ()
   {
         return this;
   }
};

class CmmFunctionDeclarator : public CmmDeclarator
{
public:
   CmmDeclarator * inner_declarator;
   CmmStatSect * parameters;
   bool a_const;
   bool a_override;
   CmmExceptionSect * exception_spec;

   inline CmmFunctionDeclarator () :
      inner_declarator (NULL),
      parameters (NULL),
      a_const (false),
      a_override (false),
      exception_spec (NULL)
   {

         kind = functionDeclarator;
   }

   inline virtual CmmFunctionDeclarator * conv_CmmFunctionDeclarator ()
   {
         return this;
   }
};

class CmmPtrSpecifierSect : public CmmBasic
{
public:

   inline CmmPtrSpecifierSect ()
   {
   }

   inline virtual CmmPtrSpecifierSect * conv_CmmPtrSpecifierSect ()
   {

         return this;
   }
};

class CmmStatSect : public CmmBasic
{
public:
   vector < CmmStat * > items;

   inline CmmStatSect () :
      items ()
   {
   }

   inline virtual CmmStatSect * conv_CmmStatSect ()
   {

         return this;
   }
};

class CmmSimpleDecl : public CmmDecl
{
public:
   CmmExpr * type_spec;
   vector < CmmSimpleItem * > items;
   CmmCompoundStat * body;
   CmmCtorInitializer * ctor_init;

   inline CmmSimpleDecl () :
      type_spec (NULL),
      items (),
      body (NULL),
      ctor_init (NULL)
   {

         kind = simpleDecl;
   }

   inline virtual CmmSimpleDecl * conv_CmmSimpleDecl ()
   {
         return this;
   }
};

class CmmDotsParam : public CmmStat
{
public:

   inline CmmDotsParam ()
   {

         kind = dotsParam;
   }

   inline virtual CmmDotsParam * conv_CmmDotsParam ()
   {
         return this;
   }
};

class CmmTypeId : public CmmBasic
{
public:
   CmmExpr * type_spec;
   CmmDeclarator * declarator;

   inline CmmTypeId () :
      type_spec (NULL),
      declarator (NULL)
   {
   }

   inline virtual CmmTypeId * conv_CmmTypeId ()
   {

         return this;
   }
};

class CmmInitializer : public CmmBasic
{
public:
   CmmInitItem * value;

   inline CmmInitializer () :
      value (NULL)
   {
   }

   inline virtual CmmInitializer * conv_CmmInitializer ()
   {

         return this;
   }
};

class CmmInitItem : public CmmBasic
{
public:

   inline CmmInitItem ()
   {
   }

   inline virtual CmmInitSimple * conv_CmmInitSimple ()
   {

         return NULL;
   }

   inline virtual CmmInitList * conv_CmmInitList ()
   {
         return NULL;
   }

   inline virtual CmmInitItem * conv_CmmInitItem ()
   {
         return this;
   }
};

class CmmInitSimple : public CmmInitItem
{
public:
   CmmExpr * inner_expr;

   inline CmmInitSimple () :
      inner_expr (NULL)
   {
   }

   inline virtual CmmInitSimple * conv_CmmInitSimple ()
   {

         return this;
   }
};

class CmmInitList : public CmmInitItem
{
public:
   vector < CmmInitItem * > items;

   inline CmmInitList () :
      items ()
   {
   }

   inline virtual CmmInitList * conv_CmmInitList ()
   {

         return this;
   }
};

class CmmAttr : public CmmBasic
{
public:
   CmmExpr * attr_expr;

   inline CmmAttr () :
      attr_expr (NULL)
   {
   }

   inline virtual CmmAttr * conv_CmmAttr ()
   {

         return this;
   }
};

class CmmAttrGroup : public CmmBasic
{
public:
   vector < CmmAttr * > items;

   inline CmmAttrGroup () :
      items ()
   {
   }

   inline virtual CmmAttrGroup * conv_CmmAttrGroup ()
   {

         return this;
   }
};

class CmmAttrSect : public CmmBasic
{
public:
   vector < CmmAttrGroup * > items;

   inline CmmAttrSect () :
      items ()
   {
   }

   inline virtual CmmAttrSect * conv_CmmAttrSect ()
   {

         return this;
   }
};

class CmmNamespaceDecl : public CmmDecl
{
public:
   CmmSimpleName * simp_name;
   CmmAttrSect * attr;
   CmmStatSect * members;

   inline CmmNamespaceDecl () :
      simp_name (NULL),
      attr (NULL),
      members (NULL)
   {

         kind = namespaceDecl;
   }

   inline virtual CmmNamespaceDecl * conv_CmmNamespaceDecl ()
   {
         return this;
   }
};

class CmmUsingDecl : public CmmDecl
{
public:
   bool a_namespace;
   CmmName * qual_name;

   inline CmmUsingDecl () :
      a_namespace (false),
      qual_name (NULL)
   {

         kind = usingDecl;
   }

   inline virtual CmmUsingDecl * conv_CmmUsingDecl ()
   {
         return this;
   }
};

class CmmExternDecl : public CmmDecl
{
public:
   string language;
   CmmStatSect * members;
   CmmStat * inner_declaration;

   inline CmmExternDecl () :
      language (""),
      members (NULL),
      inner_declaration (NULL)
   {

         kind = externDecl;
   }

   inline virtual CmmExternDecl * conv_CmmExternDecl ()
   {
         return this;
   }
};

class CmmTypedefDecl : public CmmDecl
{
public:
   CmmExpr * type_spec;
   CmmDeclarator * declarator;

   inline CmmTypedefDecl () :
      type_spec (NULL),
      declarator (NULL)
   {

         kind = typedefDecl;
   }

   inline virtual CmmTypedefDecl * conv_CmmTypedefDecl ()
   {
         return this;
   }
};

class CmmFriendDecl : public CmmDecl
{
public:
   CmmStat * inner_declaration;

   inline CmmFriendDecl () :
      inner_declaration (NULL)
   {

         kind = friendDecl;
   }

   inline virtual CmmFriendDecl * conv_CmmFriendDecl ()
   {
         return this;
   }
};

class CmmEnumDecl : public CmmDecl
{
public:
   CmmSimpleName * simp_name;
   CmmEnumSect * enum_items;

   inline CmmEnumDecl () :
      simp_name (NULL),
      enum_items (NULL)
   {

         kind = enumDecl;
   }

   inline virtual CmmEnumDecl * conv_CmmEnumDecl ()
   {
         return this;
   }
};

class CmmEnumSect : public CmmBasic
{
public:
   vector < CmmEnumItem * > items;

   inline CmmEnumSect () :
      items ()
   {
   }

   inline virtual CmmEnumSect * conv_CmmEnumSect ()
   {

         return this;
   }
};

class CmmEnumItem : public CmmBasic
{
public:
   CmmSimpleName * simp_name;
   CmmExpr * init_value;

   inline CmmEnumItem () :
      simp_name (NULL),
      init_value (NULL)
   {
   }

   inline virtual CmmEnumItem * conv_CmmEnumItem ()
   {

         return this;
   }
};

class CmmClassDecl : public CmmDecl
{
public:
   CmmClassDeclStyle style;
   CmmSimpleName * simp_name;
   CmmAttrSect * attr;
   CmmBaseSect * base_list;
   CmmStatSect * members;

   inline CmmClassDecl () :
      style (CmmClassDeclStyle (0)),
      simp_name (NULL),
      attr (NULL),
      base_list (NULL),
      members (NULL)
   {

         kind = classDecl;
   }

   inline virtual CmmClassDecl * conv_CmmClassDecl ()
   {
         return this;
   }
};

class CmmMemberVisibility : public CmmDecl
{
public:
   CmmMemberVisibilityAccess access;

   inline CmmMemberVisibility () :
      access (CmmMemberVisibilityAccess (0))
   {

         kind = visibilityDecl;
   }

   inline virtual CmmMemberVisibility * conv_CmmMemberVisibility ()
   {
         return this;
   }
};

class CmmBaseSect : public CmmBasic
{
public:
   vector < CmmBaseItem * > items;

   inline CmmBaseSect () :
      items ()
   {
   }

   inline virtual CmmBaseSect * conv_CmmBaseSect ()
   {

         return this;
   }
};

class CmmBaseItem : public CmmBasic
{
public:
   bool a_virtual;
   CmmBaseItemAccess access;
   CmmName * from_cls;

   inline CmmBaseItem () :
      a_virtual (false),
      access (CmmBaseItemAccess (0)),
      from_cls (NULL)
   {
   }

   inline virtual CmmBaseItem * conv_CmmBaseItem ()
   {

         return this;
   }
};

class CmmCtorInitializer : public CmmBasic
{
public:
   vector < CmmMemberInitializer * > items;

   inline CmmCtorInitializer () :
      items ()
   {
   }

   inline virtual CmmCtorInitializer * conv_CmmCtorInitializer ()
   {

         return this;
   }
};

class CmmMemberInitializer : public CmmBasic
{
public:
   CmmSimpleName * simp_name;
   CmmExprList * params;

   inline CmmMemberInitializer () :
      simp_name (NULL),
      params (NULL)
   {
   }

   inline virtual CmmMemberInitializer * conv_CmmMemberInitializer ()
   {

         return this;
   }
};

class CmmConvSpec : public CmmBasic
{
public:
   CmmExpr * type_spec;
   CmmPtrSpecifierSect * ptr_spec;

   inline CmmConvSpec () :
      type_spec (NULL),
      ptr_spec (NULL)
   {
   }

   inline virtual CmmConvSpec * conv_CmmConvSpec ()
   {

         return this;
   }
};

class CmmSpecialFuction : public CmmName
{
public:
   CmmConvSpec * conv;
   bool spec_new;
   bool spec_new_array;
   bool spec_delete;
   bool spec_delete_array;
   bool spec_add;
   bool spec_sub;
   bool spec_mul;
   bool spec_div;
   bool spec_mod;
   bool spec_xor;
   bool spec_and;
   bool spec_or;
   bool spec_not;
   bool spec_log_not;
   bool spec_assign;
   bool spec_lt;
   bool spec_gt;
   bool spec_add_assign;
   bool spec_sub_assign;
   bool spec_mul_assign;
   bool spec_div_assign;
   bool spec_mod_assign;
   bool spec_xor_assign;
   bool spec_and_assign;
   bool spec_or_assign;
   bool spec_shl;
   bool spec_shr;
   bool spec_shl_assign;
   bool spec_shr_assign;
   bool spec_eq;
   bool spec_ne;
   bool spec_le;
   bool spec_ge;
   bool spec_log_and;
   bool spec_log_or;
   bool spec_inc;
   bool spec_dec;
   bool spec_comma;
   bool spec_member_deref;
   bool spec_deref;
   bool spec_call;
   bool spec_index;

   inline CmmSpecialFuction () :
      conv (NULL),
      spec_new (false),
      spec_new_array (false),
      spec_delete (false),
      spec_delete_array (false),
      spec_add (false),
      spec_sub (false),
      spec_mul (false),
      spec_div (false),
      spec_mod (false),
      spec_xor (false),
      spec_and (false),
      spec_or (false),
      spec_not (false),
      spec_log_not (false),
      spec_assign (false),
      spec_lt (false),
      spec_gt (false),
      spec_add_assign (false),
      spec_sub_assign (false),
      spec_mul_assign (false),
      spec_div_assign (false),
      spec_mod_assign (false),
      spec_xor_assign (false),
      spec_and_assign (false),
      spec_or_assign (false),
      spec_shl (false),
      spec_shr (false),
      spec_shl_assign (false),
      spec_shr_assign (false),
      spec_eq (false),
      spec_ne (false),
      spec_le (false),
      spec_ge (false),
      spec_log_and (false),
      spec_log_or (false),
      spec_inc (false),
      spec_dec (false),
      spec_comma (false),
      spec_member_deref (false),
      spec_deref (false),
      spec_call (false),
      spec_index (false)
   {

         kind = specialName;
   }

   inline virtual CmmSpecialFuction * conv_CmmSpecialFuction ()
   {
         return this;
   }
};

class CmmTemplateDecl : public CmmDecl
{
public:
   CmmTemplateParamSect * params;
   CmmStat * inner_declaration;

   inline CmmTemplateDecl () :
      params (NULL),
      inner_declaration (NULL)
   {

         kind = templateDecl;
   }

   inline virtual CmmTemplateDecl * conv_CmmTemplateDecl ()
   {
         return this;
   }
};

class CmmStencilDecl : public CmmDecl
{
public:
   CmmSimpleName * simp_name;
   CmmTemplateParamSect * params;
   CmmStatSect * members;

   inline CmmStencilDecl () :
      simp_name (NULL),
      params (NULL),
      members (NULL)
   {

         kind = stencilDecl;
   }

   inline virtual CmmStencilDecl * conv_CmmStencilDecl ()
   {
         return this;
   }
};

class CmmTemplateParamSect : public CmmBasic
{
public:
   vector < CmmTemplateParam * > items;

   inline CmmTemplateParamSect () :
      items ()
   {
   }

   inline virtual CmmTemplateParamSect * conv_CmmTemplateParamSect ()
   {

         return this;
   }
};

class CmmTemplateTypeParam : public CmmTemplateParam
{
public:
   CmmTemplateParamSect * params;
   bool a_class;
   bool a_typename;
   CmmSimpleName * simp_name;

   inline CmmTemplateTypeParam () :
      params (NULL),
      a_class (false),
      a_typename (false),
      simp_name (NULL)
   {

         kind = templateTypeParam;
   }

   inline virtual CmmTemplateTypeParam * conv_CmmTemplateTypeParam ()
   {
         return this;
   }
};

class CmmTemplateNormalParam : public CmmTemplateParam
{
public:
   CmmExpr * type_spec;
   CmmDeclarator * declarator;
   CmmExpr * init;

   inline CmmTemplateNormalParam () :
      type_spec (NULL),
      declarator (NULL),
      init (NULL)
   {

         kind = templateCommonParam;
   }

   inline virtual CmmTemplateNormalParam * conv_CmmTemplateNormalParam ()
   {
         return this;
   }
};

class CmmTemplateArgSect : public CmmBasic
{
public:
   vector < CmmTemplateArg * > items;

   inline CmmTemplateArgSect () :
      items ()
   {
   }

   inline virtual CmmTemplateArgSect * conv_CmmTemplateArgSect ()
   {

         return this;
   }
};

class CmmTemplateArg : public CmmBasic
{
public:
   CmmStat * value;

   inline CmmTemplateArg () :
      value (NULL)
   {
   }

   inline virtual CmmTemplateArg * conv_CmmTemplateArg ()
   {

         return this;
   }
};

class CmmTryStat : public CmmStat
{
public:
   CmmCompoundStat * body;
   CmmHandlerSect * handlers;

   inline CmmTryStat () :
      body (NULL),
      handlers (NULL)
   {

         kind = tryStat;
   }

   inline virtual CmmTryStat * conv_CmmTryStat ()
   {
         return this;
   }
};

class CmmHandlerSect : public CmmBasic
{
public:
   vector < CmmHandlerItem * > items;

   inline CmmHandlerSect () :
      items ()
   {
   }

   inline virtual CmmHandlerSect * conv_CmmHandlerSect ()
   {

         return this;
   }
};

class CmmHandlerItem : public CmmBasic
{
public:
   CmmExpr * type_spec;
   CmmDeclarator * declarator;
   bool dots;
   CmmCompoundStat * body;

   inline CmmHandlerItem () :
      type_spec (NULL),
      declarator (NULL),
      dots (false),
      body (NULL)
   {
   }

   inline virtual CmmHandlerItem * conv_CmmHandlerItem ()
   {

         return this;
   }
};

class CmmThrowExpr : public CmmUnaryExpr
{
public:
   CmmExpr * inner_expr;

   inline CmmThrowExpr () :
      inner_expr (NULL)
   {

         kind = throwExpr;
   }

   inline virtual CmmThrowExpr * conv_CmmThrowExpr ()
   {
         return this;
   }
};

class CmmExceptionSect : public CmmBasic
{
public:
   vector < CmmExceptionItem * > items;

   inline CmmExceptionSect () :
      items ()
   {
   }

   inline virtual CmmExceptionSect * conv_CmmExceptionSect ()
   {

         return this;
   }
};

class CmmExceptionItem : public CmmBasic
{
public:
   CmmTypeId * type;

   inline CmmExceptionItem () :
      type (NULL)
   {
   }

   inline virtual CmmExceptionItem * conv_CmmExceptionItem ()
   {

         return this;
   }
};

class CmmCastExpr : public CmmBinaryExpr
{
public:
   CmmExpr * left;
   CmmExpr * right;

   inline CmmCastExpr () :
      left (NULL),
      right (NULL)
   {

         kind = castExpr;
   }

   inline virtual CmmCastExpr * conv_CmmCastExpr ()
   {
         return this;
   }
};

class CmmPtrMemExpr : public CmmBinaryExpr
{
public:
   CmmExpr * left;
   CmmExpr * right;

   inline CmmPtrMemExpr () :
      left (NULL),
      right (NULL)
   {
   }

   inline virtual CmmPtrMemExpr * conv_CmmPtrMemExpr ()
   {

         return this;
   }
};

class CmmMulExpr : public CmmBinaryExpr
{
public:
   CmmExpr * left;
   string custom_mul;
   CmmExpr * right;

   inline CmmMulExpr () :
      left (NULL),
      custom_mul (""),
      right (NULL)
   {
   }

   inline virtual CmmMulExpr * conv_CmmMulExpr ()
   {

         return this;
   }
};

class CmmAddExpr : public CmmBinaryExpr
{
public:
   CmmExpr * left;
   string custom_add;
   CmmExpr * right;

   inline CmmAddExpr () :
      left (NULL),
      custom_add (""),
      right (NULL)
   {
   }

   inline virtual CmmAddExpr * conv_CmmAddExpr ()
   {

         return this;
   }
};

class CmmShiftExpr : public CmmBinaryExpr
{
public:
   CmmExpr * left;
   CmmExpr * right;

   inline CmmShiftExpr () :
      left (NULL),
      right (NULL)
   {
   }

   inline virtual CmmShiftExpr * conv_CmmShiftExpr ()
   {

         return this;
   }
};

class CmmRelExpr : public CmmBinaryExpr
{
public:
   CmmExpr * left;
   CmmExpr * right;

   inline CmmRelExpr () :
      left (NULL),
      right (NULL)
   {
   }

   inline virtual CmmRelExpr * conv_CmmRelExpr ()
   {

         return this;
   }
};

class CmmEqExpr : public CmmBinaryExpr
{
public:
   CmmExpr * left;
   CmmExpr * right;

   inline CmmEqExpr () :
      left (NULL),
      right (NULL)
   {
   }

   inline virtual CmmEqExpr * conv_CmmEqExpr ()
   {

         return this;
   }
};

class CmmAndExpr : public CmmBinaryExpr
{
public:
   CmmExpr * left;
   CmmExpr * right;

   inline CmmAndExpr () :
      left (NULL),
      right (NULL)
   {

         kind = bitAndExpr;
   }

   inline virtual CmmAndExpr * conv_CmmAndExpr ()
   {
         return this;
   }
};

class CmmXorExpr : public CmmBinaryExpr
{
public:
   CmmExpr * left;
   CmmExpr * right;

   inline CmmXorExpr () :
      left (NULL),
      right (NULL)
   {

         kind = bitXorExpr;
   }

   inline virtual CmmXorExpr * conv_CmmXorExpr ()
   {
         return this;
   }
};

class CmmOrExpr : public CmmBinaryExpr
{
public:
   CmmExpr * left;
   CmmExpr * right;

   inline CmmOrExpr () :
      left (NULL),
      right (NULL)
   {
   }

   inline virtual CmmOrExpr * conv_CmmOrExpr ()
   {

         return this;
   }
};

class CmmAndAndExpr : public CmmBinaryExpr
{
public:
   CmmExpr * left;
   CmmExpr * right;

   inline CmmAndAndExpr () :
      left (NULL),
      right (NULL)
   {

         kind = logAndExpr;
   }

   inline virtual CmmAndAndExpr * conv_CmmAndAndExpr ()
   {
         return this;
   }
};

class CmmOrOrExpr : public CmmBinaryExpr
{
public:
   CmmExpr * left;
   CmmExpr * right;

   inline CmmOrOrExpr () :
      left (NULL),
      right (NULL)
   {

         kind = logOrExpr;
   }

   inline virtual CmmOrOrExpr * conv_CmmOrOrExpr ()
   {
         return this;
   }
};

class CmmAssignExpr : public CmmBinaryExpr
{
public:
   CmmExpr * left;
   CmmExpr * middle;
   CmmExpr * right;

   inline CmmAssignExpr () :
      left (NULL),
      middle (NULL),
      right (NULL)
   {
   }

   inline virtual CmmAssignExpr * conv_CmmAssignExpr ()
   {

         return this;
   }
};

class CmmCommaExpr : public CmmBinaryExpr
{
public:
   CmmExpr * left;
   CmmExpr * right;

   inline CmmCommaExpr () :
      left (NULL),
      right (NULL)
   {

         kind = commaExpr;
   }

   inline virtual CmmCommaExpr * conv_CmmCommaExpr ()
   {
         return this;
   }
};


#endif //___CMM_CMM_PARSER_H
