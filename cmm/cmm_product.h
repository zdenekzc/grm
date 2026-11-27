#ifndef ___CMM_CMM_PRODUCT_H
#define ___CMM_CMM_PRODUCT_H

#include "cmm_parser.h"

class Product : public Output
{
public:
   void send_expr (CmmExpr * param);
   void send_stat (CmmStat * param);
   void send_extension_stat (CmmStat * param);
   void send_string_value_cont (CmmStringCont * param);
   void send_modern_cast_expr (CmmModernCastExpr * param);
   void send_expr_list (CmmExprList * param);
   void send_allocation_expr (CmmNewExpr * param);
   void send_new_type_id (CmmNewTypeId * param);
   void send_allocation_array_limit (CmmNewArrayLimit * param);
   void send_deallocation_expr (CmmDeleteExpr * param);
   void send_nested_stat (CmmStat * param);
   void send_tail_stat (CmmStat * param);
   void send_empty_stat (CmmEmptyStat * param);
   void send_compound_stat (CmmCompoundStat * param);
   void send_if_stat (CmmIfStat * param);
   void send_while_stat (CmmWhileStat * param);
   void send_do_stat (CmmDoStat * param);
   void send_for_stat (CmmForStat * param);
   void send_switch_stat (CmmSwitchStat * param);
   void send_case_stat (CmmCaseStat * param);
   void send_default_stat (CmmDefaultStat * param);
   void send_break_stat (CmmBreakStat * param);
   void send_continue_stat (CmmContinueStat * param);
   void send_return_stat (CmmReturnStat * param);
   void send_goto_stat (CmmGotoStat * param);
   void send_simple_stat (CmmSimpleStat * param);
   void send_decl_specifier (CmmDeclSpec * param);
   void send_type_specifier (CmmTypeSpec * param);
   void send_pointer_declarator (CmmPointerDeclarator * param);
   void send_reference_declarator (CmmReferenceDeclator * param);
   void send_cv_specifier_list (CmmCvSpecifier * param);
   void send_basic_declarator (CmmBasicDeclarator * param);
   void send_empty_declarator (CmmEmptyDeclarator * param);
   void send_nested_declarator (CmmNestedDeclarator * param);
   void send_array_declarator (CmmArrayDeclarator * param);
   void send_function_declarator (CmmFunctionDeclarator * param);
   void send_entry_declarator (CmmDeclarator * param);
   void send_continue_declarator (CmmDeclarator * param);
   void send_declarator (CmmDeclarator * param);
   void send_simple_declarator (CmmDeclarator * param);
   void send_common_declarator (CmmDeclarator * param);
   void send_constructor_declarator (CmmDeclarator * param);
   void send_ptr_specifier_list (CmmPtrSpecifierSect * param);
   void send_parameter_declaration_list (CmmStatSect * param);
   void send_parameter_declaration (CmmStat * param);
   void send_value_parameter (CmmSimpleStat * param);
   void send_plain_parameter (CmmSimpleDecl * param);
   void send_parameter_item (CmmSimpleItem * param);
   void send_dots_parameter (CmmDotsParam * param);
   void send_type_id (CmmTypeId * param);
   void send_initializer (CmmInitializer * param);
   void send_initializer_item (CmmInitItem * param);
   void send_simple_initializer (CmmInitSimple * param);
   void send_initializer_list (CmmInitList * param);
   void send_attr_item (CmmAttr * param);
   void send_attr_group (CmmAttrGroup * param);
   void send_attr_list (CmmAttrSect * param);
   void send_simple_declaration (CmmSimpleDecl * param);
   void send_simple_item (CmmSimpleItem * param);
   void send_constructor_declaration (CmmSimpleDecl * param);
   void send_constructor_item (CmmSimpleItem * param);
   void send_condition (CmmStat * param);
   void send_condition_declaration (CmmSimpleDecl * param);
   void send_condition_item (CmmSimpleItem * param);
   void send_condition_value (CmmSimpleStat * param);
   void send_declaration_list (CmmStatSect * param);
   void send_namespace_declaration (CmmNamespaceDecl * param);
   void send_using_declaration (CmmUsingDecl * param);
   void send_extern_declaration (CmmExternDecl * param);
   void send_typedef_declaration (CmmTypedefDecl * param);
   void send_friend_declaration (CmmFriendDecl * param);
   void send_enum_declaration (CmmEnumDecl * param);
   void send_enum_list (CmmEnumSect * param);
   void send_enumerator (CmmEnumItem * param);
   void send_class_declaration (CmmClassDecl * param);
   void send_member_visibility (CmmMemberVisibility * param);
   void send_member_list (CmmStatSect * param);
   void send_base_specifier_list (CmmBaseSect * param);
   void send_base_specifier (CmmBaseItem * param);
   void send_ctor_initializer (CmmCtorInitializer * param);
   void send_member_initializer (CmmMemberInitializer * param);
   void send_conversion_specifiers (CmmConvSpec * param);
   void send_special_function (CmmSpecialFuction * param);
   void send_template_declaration (CmmTemplateDecl * param);
   void send_stencil_declaration (CmmStencilDecl * param);
   void send_stencil_member_list (CmmStatSect * param);
   void send_template_param_list (CmmTemplateParamSect * param);
   void send_template_param (CmmTemplateParam * param);
   void send_template_type_param (CmmTemplateTypeParam * param);
   void send_template_normal_param (CmmTemplateNormalParam * param);
   void send_template_arg_list (CmmTemplateArgSect * param);
   void send_template_arg (CmmTemplateArg * param);
   void send_try_stat (CmmTryStat * param);
   void send_handler_list (CmmHandlerSect * param);
   void send_handler (CmmHandlerItem * param);
   void send_exception_specification (CmmExceptionSect * param);
   void send_exception_specification_item (CmmExceptionItem * param);
};


#endif //___CMM_CMM_PRODUCT_H
