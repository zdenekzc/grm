#include "cmm_product.h"


void Product::send_string_value_cont (CmmStringCont * param)
{
   putString (param->value);
}

void Product::send_modern_cast_expr (CmmModernCastExpr * param)
{
   if (param->cast_kind == dynamicCast)
   {
      send ("dynamic_cast");
   }
   else if (param->cast_kind == staticCast)
   {
      send ("static_cast");
   }
   else if (param->cast_kind == constCast)
   {
      send ("const_cast");
   }
   else if (param->cast_kind == reinterpreterCast)
   {
      send ("reinterpret_cast");
   }
   send ("<");
   style_no_space ();
   send_type_id (param->type);
   style_no_space ();
   send (">");
   send ("(");
   send_expr (param->param);
   send (")");
}

void Product::send_expr_list (CmmExprList * param)
{
   int inx = 0;
   int cnt = param->items.size ();
   if (inx < cnt)
   {
      send_expr (param->items[inx]);
      inx++;
      while (inx < cnt)
      {
         send (",");
         send_expr (param->items[inx]);
         inx++;
      }
   }
}

void Product::send_allocation_expr (CmmNewExpr * param)
{
   send ("new");
   if (param->type1 != NULL)
   {
      send_new_type_id (param->type1);
   }
   else if (param->type2 != NULL)
   {
      send ("(");
      send_type_id (param->type2);
      send (")");
   }
   if (param->init_list != NULL)
   {
      send ("(");
      send_expr_list (param->init_list);
      send (")");
   }
}

void Product::send_new_type_id (CmmNewTypeId * param)
{
   int inx = 0;
   int cnt = param->items.size ();
   send_expr (param->type_spec);
   send_ptr_specifier_list (param->ptr);
   while (inx < cnt)
   {
      send_allocation_array_limit (param->items[inx]);
      inx++;
   }
}

void Product::send_allocation_array_limit (CmmNewArrayLimit * param)
{
   send ("[");
   send_expr (param->value);
   send ("]");
}

void Product::send_deallocation_expr (CmmDeleteExpr * param)
{
   send ("delete");
   if (param->a_array)
   {
      send ("[");
      send ("]");
   }
   send_expr (param->param);
}

void Product::send_nested_stat (CmmStat * param)
{
   style_indent ();
   send_stat (param);
   style_unindent ();
}

void Product::send_tail_stat (CmmStat * param)
{
   style_indent ();
   send_stat (param);
   style_unindent ();
}

void Product::send_empty_stat (CmmEmptyStat * param)
{
   send (";");
}

void Product::send_compound_stat (CmmCompoundStat * param)
{
   int inx = 0;
   int cnt = param->items.size ();
   send ("{");
   style_indent ();
   while (inx < cnt)
   {
      style_new_line ();
      send_stat (param->items[inx]);
      inx++;
   }
   style_unindent ();
   send ("}");
}

void Product::send_if_stat (CmmIfStat * param)
{
   send ("if");
   send ("(");
   send_condition (param->cond);
   send (")");
   send_nested_stat (param->then_stat);
   if (param->else_stat != NULL)
   {
      style_new_line ();
      send ("else");
      send_tail_stat (param->else_stat);
   }
}

void Product::send_while_stat (CmmWhileStat * param)
{
   send ("while");
   send ("(");
   send_condition (param->cond);
   send (")");
   send_nested_stat (param->body);
}

void Product::send_do_stat (CmmDoStat * param)
{
   send ("do");
   send_nested_stat (param->body);
   send ("while");
   send ("(");
   send_expr (param->cond_expr);
   send (")");
   send (";");
}

void Product::send_for_stat (CmmForStat * param)
{
   send ("for");
   send ("(");
   if (param->from_expr != NULL)
   {
      send_condition (param->from_expr);
   }
   if (param->iter_expr != NULL)
   {
      send (":");
      send_expr (param->iter_expr);
   }
   else if (false)
   {
      send (";");
      if (param->cond_expr != NULL)
      {
         send_expr (param->cond_expr);
      }
      send (";");
      if (param->step_expr != NULL)
      {
         send_expr (param->step_expr);
      }
   }
   send (")");
   send_nested_stat (param->body);
}

void Product::send_switch_stat (CmmSwitchStat * param)
{
   send ("switch");
   send ("(");
   send_condition (param->cond);
   send (")");
   send_nested_stat (param->body);
}

void Product::send_case_stat (CmmCaseStat * param)
{
   send ("case");
   send_expr (param->case_expr);
   send (":");
   style_new_line ();
   send_nested_stat (param->body);
}

void Product::send_default_stat (CmmDefaultStat * param)
{
   send ("default");
   send (":");
   style_new_line ();
   send_nested_stat (param->body);
}

void Product::send_break_stat (CmmBreakStat * param)
{
   send ("break");
   send (";");
}

void Product::send_continue_stat (CmmContinueStat * param)
{
   send ("continue");
   send (";");
}

void Product::send_return_stat (CmmReturnStat * param)
{
   send ("return");
   if (param->return_expr != NULL)
   {
      send_expr (param->return_expr);
   }
   send (";");
}

void Product::send_goto_stat (CmmGotoStat * param)
{
   send ("goto");
   send (param->goto_lab);
   send (";");
}

void Product::send_simple_stat (CmmSimpleStat * param)
{
   if (param->body != NULL)
   {
      style_new_line ();
      send_compound_stat (param->body);
   }
   else if (false)
   {
      send (";");
   }
}

void Product::send_decl_specifier (CmmDeclSpec * param)
{
   if (param->a_inline)
   {
      send ("inline");
   }
   else if (param->a_virtual)
   {
      send ("virtual");
   }
   else if (param->a_explicit)
   {
      send ("explicit");
   }
   else if (param->a_mutable)
   {
      send ("mutable");
   }
   else if (param->a_static)
   {
      send ("static");
   }
   else if (param->a_register)
   {
      send ("register");
   }
   if (param->a_destructor)
   {
      send ("~");
   }
   send_expr (param->param);
}

void Product::send_type_specifier (CmmTypeSpec * param)
{
   if (param->a_signed || param->a_unsigned)
   {
      if (param->a_signed)
      {
         send ("signed");
      }
      else if (param->a_unsigned)
      {
         send ("unsigned");
      }
   }
   if (param->a_short)
   {
      send ("short");
   }
   else if (param->a_long)
   {
      send ("long");
      if (param->a_long_long || param->a_long_double)
      {
         if (param->a_long_long)
         {
            send ("long");
         }
         else if (param->a_long_double)
         {
            send ("double");
         }
      }
   }
   else if (param->a_bool)
   {
      send ("bool");
   }
   else if (param->a_char)
   {
      send ("char");
   }
   else if (param->a_wchar)
   {
      send ("wchar_t");
   }
   else if (param->a_int)
   {
      send ("int");
   }
   else if (param->a_float)
   {
      send ("float");
   }
   else if (param->a_double)
   {
      send ("double");
   }
   else if (param->a_void)
   {
      send ("void");
   }
}

void Product::send_pointer_declarator (CmmPointerDeclarator * param)
{
   send ("*");
   send_cv_specifier_list (param->cv_spec);
   send_declarator (param->inner_declarator);
}

void Product::send_reference_declarator (CmmReferenceDeclator * param)
{
   send ("&");
   send_cv_specifier_list (param->cv_spec);
   send_declarator (param->inner_declarator);
}

void Product::send_cv_specifier_list (CmmCvSpecifier * param)
{
   if (param->cv_const || param->cv_volatile)
   {
      if (param->cv_const)
      {
         send ("const");
      }
      else if (param->cv_volatile)
      {
         send ("volatile");
      }
   }
}

void Product::send_basic_declarator (CmmBasicDeclarator * param)
{
   send_expr (param->qual_name);
}

void Product::send_empty_declarator (CmmEmptyDeclarator * param)
{
}

void Product::send_nested_declarator (CmmNestedDeclarator * param)
{
   send ("(");
   send_declarator (param->inner_declarator);
   send (")");
}

void Product::send_array_declarator (CmmArrayDeclarator * param)
{
   send ("[");
   if (param->lim != NULL)
   {
      send_expr (param->lim);
   }
   send ("]");
}

void Product::send_function_declarator (CmmFunctionDeclarator * param)
{
   send ("(");
   send_parameter_declaration_list (param->parameters);
   send (")");
   if (param->a_const)
   {
      send ("const");
   }
   if (param->a_override)
   {
      send ("override");
   }
   if (param->exception_spec != NULL)
   {
      send_exception_specification (param->exception_spec);
   }
}

void Product::send_entry_declarator (CmmDeclarator * param)
{
   if (param->kind == basicDeclarator)
   {
      CmmBasicDeclarator * param0 = param->conv_CmmBasicDeclarator ();
      send_basic_declarator (param0->conv_CmmBasicDeclarator ());
   }
   else if (param->kind == emptyDeclarator)
   {
      CmmEmptyDeclarator * param0 = param->conv_CmmEmptyDeclarator ();
      send_empty_declarator (param0->conv_CmmEmptyDeclarator ());
   }
   else if (param->kind == nestedDeclarator)
   {
      CmmNestedDeclarator * param0 = param->conv_CmmNestedDeclarator ();
      send_nested_declarator (param0->conv_CmmNestedDeclarator ());
   }
}

void Product::send_continue_declarator (CmmDeclarator * param)
{
   if (param->kind == arrayDeclarator)
   {
      CmmArrayDeclarator * param0 = param->conv_CmmArrayDeclarator ();
      send_entry_declarator (param0->inner_declarator);
      send_array_declarator (param0->conv_CmmArrayDeclarator ());
   }
   else if (param->kind == functionDeclarator)
   {
      CmmFunctionDeclarator * param0 = param->conv_CmmFunctionDeclarator ();
      send_entry_declarator (param0->inner_declarator);
      send_function_declarator (param0->conv_CmmFunctionDeclarator ());
   }
   else {
      send_entry_declarator (param);
   }
}

void Product::send_declarator (CmmDeclarator * param)
{
   if (param->kind == pointerDeclarator)
   {
      CmmPointerDeclarator * param0 = param->conv_CmmPointerDeclarator ();
      send_pointer_declarator (param0->conv_CmmPointerDeclarator ());
   }
   else if (param->kind == referenceDeclarator)
   {
      CmmReferenceDeclator * param0 = param->conv_CmmReferenceDeclator ();
      send_reference_declarator (param0->conv_CmmReferenceDeclator ());
   }
   else if (param->conv_CmmDeclarator () != NULL)
   {
      CmmDeclarator * param0 = param->conv_CmmDeclarator ();
      send_continue_declarator (param0);
   }
}

void Product::send_simple_declarator (CmmDeclarator * param)
{
   send_declarator (param);
}

void Product::send_common_declarator (CmmDeclarator * param)
{
   send_declarator (param);
}

void Product::send_constructor_declarator (CmmDeclarator * param)
{
   if (param->kind == functionDeclarator)
   {
      CmmFunctionDeclarator * param0 = param->conv_CmmFunctionDeclarator ();
      send_empty_declarator (param0->inner_declarator->conv_CmmEmptyDeclarator ());
      send_function_declarator (param0->conv_CmmFunctionDeclarator ());
   }
}

void Product::send_ptr_specifier_list (CmmPtrSpecifierSect * param)
{
}

void Product::send_parameter_declaration_list (CmmStatSect * param)
{
   int inx = 0;
   int cnt = param->items.size ();
   if (inx < cnt)
   {
      send_parameter_declaration (param->items[inx]);
      inx++;
      while (inx < cnt)
      {
         send (",");
         send_parameter_declaration (param->items[inx]);
         inx++;
      }
   }
}

void Product::send_parameter_declaration (CmmStat * param)
{
   if (param->kind == simpleStat)
   {
      CmmSimpleStat * param0 = param->conv_CmmSimpleStat ();
      send_expr (param0->inner_expr);
      send_value_parameter (param0->conv_CmmSimpleStat ());
   }
   else if (param->kind == simpleDecl)
   {
      CmmSimpleDecl * param0 = param->conv_CmmSimpleDecl ();
      send_expr (param0->type_spec);
      send_plain_parameter (param0->conv_CmmSimpleDecl ());
   }
   else if (param->kind == dotsParam)
   {
      CmmDotsParam * param0 = param->conv_CmmDotsParam ();
      send_dots_parameter (param0->conv_CmmDotsParam ());
   }
}

void Product::send_value_parameter (CmmSimpleStat * param)
{
}

void Product::send_plain_parameter (CmmSimpleDecl * param)
{
   int inx = 0;
   int cnt = param->items.size ();
   send_parameter_item (param->items[inx]);
   inx++;
}

void Product::send_parameter_item (CmmSimpleItem * param)
{
   send_common_declarator (param->declarator);
   if (param->init != NULL)
   {
      send_initializer (param->init);
   }
   send_attr_list (param->attr);
}

void Product::send_dots_parameter (CmmDotsParam * param)
{
   send ("...");
}

void Product::send_type_id (CmmTypeId * param)
{
   send_expr (param->type_spec);
   send_common_declarator (param->declarator);
}

void Product::send_initializer (CmmInitializer * param)
{
   send ("=");
   send_initializer_item (param->value);
}

void Product::send_initializer_item (CmmInitItem * param)
{
   if (param->conv_CmmInitSimple () != NULL)
   {
      CmmInitSimple * param0 = param->conv_CmmInitSimple ();
      send_simple_initializer (param0->conv_CmmInitSimple ());
   }
   else if (param->conv_CmmInitList () != NULL)
   {
      CmmInitList * param0 = param->conv_CmmInitList ();
      send_initializer_list (param0->conv_CmmInitList ());
   }
}

void Product::send_simple_initializer (CmmInitSimple * param)
{
   send_expr (param->inner_expr);
}

void Product::send_initializer_list (CmmInitList * param)
{
   int inx = 0;
   int cnt = param->items.size ();
   send ("{");
   style_indent ();
   if (inx < cnt)
   {
      send_initializer_item (param->items[inx]);
      inx++;
      while (inx < cnt)
      {
         send (",");
         style_new_line ();
         send_initializer_item (param->items[inx]);
         inx++;
      }
   }
   style_unindent ();
   send ("}");
}

void Product::send_attr_item (CmmAttr * param)
{
   send_expr (param->attr_expr);
}

void Product::send_attr_group (CmmAttrGroup * param)
{
   int inx = 0;
   int cnt = param->items.size ();
   send ("[[");
   send_attr_item (param->items[inx]);
   inx++;
   while (inx < cnt)
   {
      send (",");
      send_attr_item (param->items[inx]);
      inx++;
   }
   send ("]]");
}

void Product::send_attr_list (CmmAttrSect * param)
{
   int inx = 0;
   int cnt = param->items.size ();
   while (inx < cnt)
   {
      send_attr_group (param->items[inx]);
      inx++;
   }
}

void Product::send_simple_declaration (CmmSimpleDecl * param)
{
   int inx = 0;
   int cnt = param->items.size ();
   send_simple_item (param->items[inx]);
   inx++;
   while (inx < cnt)
   {
      send (",");
      send_simple_item (param->items[inx]);
      inx++;
   }
   if (param->body != NULL)
   {
      style_new_line ();
      send_compound_stat (param->body);
   }
   else if (false)
   {
      send (";");
   }
}

void Product::send_simple_item (CmmSimpleItem * param)
{
   send_simple_declarator (param->declarator);
   if (param->init != NULL)
   {
      send_initializer (param->init);
   }
   send_attr_list (param->attr);
}

void Product::send_constructor_declaration (CmmSimpleDecl * param)
{
   int inx = 0;
   int cnt = param->items.size ();
   send_constructor_item (param->items[inx]);
   inx++;
   if (param->body != NULL)
   {
      if (param->ctor_init != NULL)
      {
         send (":");
         style_new_line ();
         send_ctor_initializer (param->ctor_init);
      }
      style_new_line ();
      send_compound_stat (param->body);
   }
   else if (false)
   {
      send (";");
   }
}

void Product::send_constructor_item (CmmSimpleItem * param)
{
   send_constructor_declarator (param->declarator);
   send_attr_list (param->attr);
}

void Product::send_condition (CmmStat * param)
{
   if (param->kind == simpleStat)
   {
      CmmSimpleStat * param0 = param->conv_CmmSimpleStat ();
      send_expr (param0->inner_expr);
      send_condition_value (param0->conv_CmmSimpleStat ());
   }
   else if (param->kind == simpleDecl)
   {
      CmmSimpleDecl * param0 = param->conv_CmmSimpleDecl ();
      send_expr (param0->type_spec);
      send_condition_declaration (param0->conv_CmmSimpleDecl ());
   }
}

void Product::send_condition_declaration (CmmSimpleDecl * param)
{
   int inx = 0;
   int cnt = param->items.size ();
   send_condition_item (param->items[inx]);
   inx++;
   while (inx < cnt)
   {
      send (",");
      send_condition_item (param->items[inx]);
      inx++;
   }
}

void Product::send_condition_item (CmmSimpleItem * param)
{
   send_simple_declarator (param->declarator);
   if (param->init != NULL)
   {
      send_initializer (param->init);
   }
   send_attr_list (param->attr);
}

void Product::send_condition_value (CmmSimpleStat * param)
{
}

void Product::send_declaration_list (CmmStatSect * param)
{
   int inx = 0;
   int cnt = param->items.size ();
   while (inx < cnt)
   {
      send_stat (param->items[inx]);
      inx++;
      style_new_line ();
   }
}

void Product::send_namespace_declaration (CmmNamespaceDecl * param)
{
   send ("namespace");
   send_expr (param->simp_name);
   send_attr_list (param->attr);
   style_new_line ();
   send ("{");
   style_new_line ();
   style_indent ();
   send_declaration_list (param->members);
   style_unindent ();
   send ("}");
}

void Product::send_using_declaration (CmmUsingDecl * param)
{
   send ("using");
   if (param->a_namespace)
   {
      send ("namespace");
   }
   send_expr (param->qual_name);
   send (";");
}

void Product::send_extern_declaration (CmmExternDecl * param)
{
   send ("extern");
   if (param->language != "")
   {
      putString (param->language);
   }
   if (param->members != NULL)
   {
      send ("{");
      send_declaration_list (param->members);
      send ("}");
   }
   else if (param->inner_declaration != NULL)
   {
      send_stat (param->inner_declaration);
   }
}

void Product::send_typedef_declaration (CmmTypedefDecl * param)
{
   send ("typedef");
   send_expr (param->type_spec);
   send_simple_declarator (param->declarator);
   send (";");
}

void Product::send_friend_declaration (CmmFriendDecl * param)
{
   send ("friend");
   send_stat (param->inner_declaration);
}

void Product::send_enum_declaration (CmmEnumDecl * param)
{
   send ("enum");
   send_expr (param->simp_name);
   if (param->enum_items != NULL)
   {
      style_new_line ();
      send ("{");
      style_indent ();
      send_enum_list (param->enum_items);
      style_unindent ();
      send ("}");
   }
   send (";");
}

void Product::send_enum_list (CmmEnumSect * param)
{
   int inx = 0;
   int cnt = param->items.size ();
   if (inx < cnt)
   {
      send_enumerator (param->items[inx]);
      inx++;
      while (inx < cnt)
      {
         send (",");
         send_enumerator (param->items[inx]);
         inx++;
      }
   }
}

void Product::send_enumerator (CmmEnumItem * param)
{
   style_new_line ();
   send_expr (param->simp_name);
   if (param->init_value != NULL)
   {
      send ("=");
      send_expr (param->init_value);
   }
}

void Product::send_class_declaration (CmmClassDecl * param)
{
   if (param->style == classStyle)
   {
      send ("class");
   }
   else if (param->style == structStyle)
   {
      send ("struct");
   }
   else if (param->style == unionStyle)
   {
      send ("union");
   }
   send_expr (param->simp_name);
   send_attr_list (param->attr);
   if (param->members != NULL)
   {
      if (param->base_list != NULL)
      {
         send (":");
         send_base_specifier_list (param->base_list);
      }
      style_new_line ();
      send ("{");
      style_indent ();
      send_member_list (param->members);
      style_unindent ();
      send ("}");
   }
   send (";");
}

void Product::send_member_visibility (CmmMemberVisibility * param)
{
   if (param->access == privateAccess)
   {
      send ("private");
   }
   else if (param->access == protectedAccess)
   {
      send ("protected");
   }
   else if (param->access == publicAccess)
   {
      send ("public");
   }
   style_no_space ();
   send (":");
}

void Product::send_member_list (CmmStatSect * param)
{
   int inx = 0;
   int cnt = param->items.size ();
   while (inx < cnt)
   {
      send_stat (param->items[inx]);
      inx++;
      style_new_line ();
   }
}

void Product::send_base_specifier_list (CmmBaseSect * param)
{
   int inx = 0;
   int cnt = param->items.size ();
   send_base_specifier (param->items[inx]);
   inx++;
   while (inx < cnt)
   {
      send (",");
      send_base_specifier (param->items[inx]);
      inx++;
   }
}

void Product::send_base_specifier (CmmBaseItem * param)
{
   if (param->a_virtual)
   {
      send ("virtual");
   }
   if (param->access == privateBase)
   {
      send ("private");
   }
   else if (param->access == protectedBase)
   {
      send ("protected");
   }
   else if (param->access == publicBase)
   {
      send ("public");
   }
   else if (param->access == unknownBase)
   {
   }
   send_expr (param->from_cls);
}

void Product::send_ctor_initializer (CmmCtorInitializer * param)
{
   int inx = 0;
   int cnt = param->items.size ();
   style_indent ();
   send_member_initializer (param->items[inx]);
   inx++;
   while (inx < cnt)
   {
      send (",");
      style_new_line ();
      send_member_initializer (param->items[inx]);
      inx++;
   }
   style_unindent ();
}

void Product::send_member_initializer (CmmMemberInitializer * param)
{
   send_expr (param->simp_name);
   send ("(");
   send_expr_list (param->params);
   send (")");
}

void Product::send_conversion_specifiers (CmmConvSpec * param)
{
   send_expr (param->type_spec);
   send_ptr_specifier_list (param->ptr_spec);
}

void Product::send_special_function (CmmSpecialFuction * param)
{
   send ("operator");
   if (param->conv != NULL)
   {
      send_conversion_specifiers (param->conv);
   }
   else if (param->spec_new)
   {
      send ("new");
      if (param->spec_new_array)
      {
         send ("[");
         send ("]");
      }
   }
   else if (param->spec_delete)
   {
      send ("delete");
      if (param->spec_delete_array)
      {
         send ("[");
         send ("]");
      }
   }
   else if (param->spec_add)
   {
      send ("+");
   }
   else if (param->spec_sub)
   {
      send ("-");
   }
   else if (param->spec_mul)
   {
      send ("*");
   }
   else if (param->spec_div)
   {
      send ("/");
   }
   else if (param->spec_mod)
   {
      send ("%");
   }
   else if (param->spec_xor)
   {
      send ("^");
   }
   else if (param->spec_and)
   {
      send ("&");
   }
   else if (param->spec_or)
   {
      send ("|");
   }
   else if (param->spec_not)
   {
      send ("~");
   }
   else if (param->spec_log_not)
   {
      send ("!");
   }
   else if (param->spec_assign)
   {
      send ("=");
   }
   else if (param->spec_lt)
   {
      send ("<");
   }
   else if (param->spec_gt)
   {
      send (">");
   }
   else if (param->spec_add_assign)
   {
      send ("+=");
   }
   else if (param->spec_sub_assign)
   {
      send ("-=");
   }
   else if (param->spec_mul_assign)
   {
      send ("*=");
   }
   else if (param->spec_div_assign)
   {
      send ("/=");
   }
   else if (param->spec_mod_assign)
   {
      send ("%=");
   }
   else if (param->spec_xor_assign)
   {
      send ("^=");
   }
   else if (param->spec_and_assign)
   {
      send ("&=");
   }
   else if (param->spec_or_assign)
   {
      send ("|=");
   }
   else if (param->spec_shl)
   {
      send ("<<");
   }
   else if (param->spec_shr)
   {
      send (">>");
   }
   else if (param->spec_shl_assign)
   {
      send (">>=");
   }
   else if (param->spec_shr_assign)
   {
      send ("<<=");
   }
   else if (param->spec_eq)
   {
      send ("==");
   }
   else if (param->spec_ne)
   {
      send ("!=");
   }
   else if (param->spec_le)
   {
      send ("<=");
   }
   else if (param->spec_ge)
   {
      send (">=");
   }
   else if (param->spec_log_and)
   {
      send ("&&");
   }
   else if (param->spec_log_or)
   {
      send ("||");
   }
   else if (param->spec_inc)
   {
      send ("++");
   }
   else if (param->spec_dec)
   {
      send ("--");
   }
   else if (param->spec_comma)
   {
      send (",");
   }
   else if (param->spec_member_deref)
   {
      send ("->*");
   }
   else if (param->spec_deref)
   {
      send ("->");
   }
   else if (param->spec_call)
   {
      send ("(");
      send (")");
   }
   else if (param->spec_index)
   {
      send ("[");
      send ("]");
   }
}

void Product::send_template_declaration (CmmTemplateDecl * param)
{
   send ("template");
   if (param->params != NULL)
   {
      send ("<");
      send_template_param_list (param->params);
      send (">");
   }
   send_stat (param->inner_declaration);
}

void Product::send_stencil_declaration (CmmStencilDecl * param)
{
   send ("stencil");
   send_expr (param->simp_name);
   send ("<");
   send_template_param_list (param->params);
   send (">");
   send ("{");
   send_stencil_member_list (param->members);
   send ("}");
}

void Product::send_stencil_member_list (CmmStatSect * param)
{
   int inx = 0;
   int cnt = param->items.size ();
   while (inx < cnt)
   {
      send_stat (param->items[inx]);
      inx++;
      style_new_line ();
   }
}

void Product::send_template_param_list (CmmTemplateParamSect * param)
{
   int inx = 0;
   int cnt = param->items.size ();
   if (inx < cnt)
   {
      send_template_param (param->items[inx]);
      inx++;
      while (inx < cnt)
      {
         send (",");
         send_template_param (param->items[inx]);
         inx++;
      }
   }
}

void Product::send_template_param (CmmTemplateParam * param)
{
   if (param->kind == templateTypeParam)
   {
      CmmTemplateTypeParam * param0 = param->conv_CmmTemplateTypeParam ();
      send_template_type_param (param0->conv_CmmTemplateTypeParam ());
   }
   else if (param->kind == templateCommonParam)
   {
      CmmTemplateNormalParam * param0 = param->conv_CmmTemplateNormalParam ();
      send_template_normal_param (param0->conv_CmmTemplateNormalParam ());
   }
}

void Product::send_template_type_param (CmmTemplateTypeParam * param)
{
   if (param->params != NULL)
   {
      send ("template");
      send ("<");
      send_template_param_list (param->params);
      send (">");
   }
   if (param->a_class)
   {
      send ("class");
   }
   else if (param->a_typename)
   {
      send ("typename");
   }
   if (param->simp_name != NULL)
   {
      send_expr (param->simp_name);
   }
}

void Product::send_template_normal_param (CmmTemplateNormalParam * param)
{
   send_expr (param->type_spec);
   send_common_declarator (param->declarator);
   if (param->init != NULL)
   {
      send ("=");
      send_expr (param->init);
   }
}

void Product::send_template_arg_list (CmmTemplateArgSect * param)
{
   int inx = 0;
   int cnt = param->items.size ();
   send ("<");
   if (inx < cnt)
   {
      send_template_arg (param->items[inx]);
      inx++;
      while (inx < cnt)
      {
         send (",");
         send_template_arg (param->items[inx]);
         inx++;
      }
   }
   send (">");
}

void Product::send_template_arg (CmmTemplateArg * param)
{
   send_parameter_declaration (param->value);
}

void Product::send_try_stat (CmmTryStat * param)
{
   send ("try");
   style_new_line ();
   send_compound_stat (param->body);
   send_handler_list (param->handlers);
}

void Product::send_handler_list (CmmHandlerSect * param)
{
   int inx = 0;
   int cnt = param->items.size ();
   send_handler (param->items[inx]);
   inx++;
   while (inx < cnt)
   {
      send_handler (param->items[inx]);
      inx++;
   }
}

void Product::send_handler (CmmHandlerItem * param)
{
   style_new_line ();
   send ("catch");
   send ("(");
   if (param->type_spec != NULL)
   {
      send_expr (param->type_spec);
      send_common_declarator (param->declarator);
   }
   else if (param->dots)
   {
      send ("...");
   }
   send (")");
   style_new_line ();
   send_compound_stat (param->body);
}

void Product::send_exception_specification (CmmExceptionSect * param)
{
   int inx = 0;
   int cnt = param->items.size ();
   send ("throw");
   send ("(");
   if (inx < cnt)
   {
      send_exception_specification_item (param->items[inx]);
      inx++;
      while (inx < cnt)
      {
         send (",");
         send_exception_specification_item (param->items[inx]);
         inx++;
      }
   }
   send (")");
}

void Product::send_exception_specification_item (CmmExceptionItem * param)
{
   send_type_id (param->type);
}

void Product::send_expr (CmmExpr * param)
{
   if (param->kind == simpleName)
   {
      CmmSimpleName * param0 = param->conv_CmmSimpleName ();
      send (param0->id);
   }
   else if (param->kind == globalName)
   {
      CmmGlobalName * param0 = param->conv_CmmGlobalName ();
      send ("::");
      send_expr (param0->inner_name);
   }
   else if (param->kind == destructorName)
   {
      CmmDestructorName * param0 = param->conv_CmmDestructorName ();
      send ("~");
      send_expr (param0->inner_name);
   }
   else if (param->kind == compoundName)
   {
      CmmCompoundName * param0 = param->conv_CmmCompoundName ();
      style_no_space ();
      send ("::");
      style_no_space ();
      send_expr (param0->right);
   }
   else if (param->kind == templateName)
   {
      CmmTemplateName * param0 = param->conv_CmmTemplateName ();
      send_template_arg_list (param0->template_args);
   }
   else if (param->kind == intValue)
   {
      CmmIntValue * param0 = param->conv_CmmIntValue ();
      send (param0->value);
   }
   else if (param->kind == realValue)
   {
      CmmRealValue * param0 = param->conv_CmmRealValue ();
      send (param0->value);
   }
   else if (param->kind == charValue)
   {
      CmmCharValue * param0 = param->conv_CmmCharValue ();
      putChar (param0->value [0]);
   }
   else if (param->kind == stringValue)
   {
      CmmStringValue * param0 = param->conv_CmmStringValue ();
      int inx = 0;
      int cnt = param0->items.size ();
      putString (param0->value);
      while (inx < cnt)
      {
         send_string_value_cont (param0->items[inx]);
         inx++;
      }
   }
   else if (param->kind == thisExpr)
   {
      CmmThisExpr * param0 = param->conv_CmmThisExpr ();
      send ("this");
   }
   else if (param->kind == lambdaExpr)
   {
      CmmLambdaExpr * param0 = param->conv_CmmLambdaExpr ();
      send ("[");
      if (param0->by_reference)
      {
         send ("&");
      }
      send ("]");
      send_compound_stat (param0->body);
   }
   else if (param->kind == subexprExpr)
   {
      CmmSubexprExpr * param0 = param->conv_CmmSubexprExpr ();
      send ("(");
      send_expr (param0->param);
      send (")");
   }
   else if (param->kind == signalSlotExpr)
   {
      CmmSignalSlotExpr * param0 = param->conv_CmmSignalSlotExpr ();
      send (param0->macro_name);
      send ("(");
      send (param0->func_name);
      if (param0->parameters != NULL)
      {
         send ("(");
         send_parameter_declaration_list (param0->parameters);
         send (")");
      }
      send (")");
   }
   else if (param->kind == modernCastExpr)
   {
      CmmModernCastExpr * param0 = param->conv_CmmModernCastExpr ();
      send_modern_cast_expr (param0);
   }
   else if (param->kind == typeIdExpr)
   {
      CmmTypeIdExpr * param0 = param->conv_CmmTypeIdExpr ();
      send ("typeid");
      send ("(");
      send_expr (param0->value);
      send (")");
   }
   else if (param->kind == indexExpr)
   {
      CmmIndexExpr * param0 = param->conv_CmmIndexExpr ();
      send ("[");
      send_expr (param0->param);
      send ("]");
   }
   else if (param->kind == callExpr)
   {
      CmmCallExpr * param0 = param->conv_CmmCallExpr ();
      send ("(");
      send_expr_list (param0->param_list);
      send (")");
   }
   else if (param->kind == fieldExpr)
   {
      CmmFieldExpr * param0 = param->conv_CmmFieldExpr ();
      style_no_space ();
      send (".");
      style_no_space ();
      send_expr (param0->field_name);
   }
   else if (param->kind == ptrFieldExpr)
   {
      CmmPtrFieldExpr * param0 = param->conv_CmmPtrFieldExpr ();
      style_no_space ();
      send ("->");
      style_no_space ();
      send_expr (param0->field_name);
   }
   else if (param->kind == postIncExpr)
   {
      CmmPostIncExpr * param0 = param->conv_CmmPostIncExpr ();
      send ("++");
   }
   else if (param->kind == postDecExpr)
   {
      CmmPostDecExpr * param0 = param->conv_CmmPostDecExpr ();
      send ("--");
   }
   else if (param->kind == incExpr)
   {
      CmmIncExpr * param0 = param->conv_CmmIncExpr ();
      send ("++");
      send_expr (param0->param);
   }
   else if (param->kind == decExpr)
   {
      CmmDecExpr * param0 = param->conv_CmmDecExpr ();
      send ("--");
      send_expr (param0->param);
   }
   else if (param->kind == derefExpr)
   {
      CmmDerefExpr * param0 = param->conv_CmmDerefExpr ();
      send ("*");
      send_expr (param0->param);
   }
   else if (param->kind == addrExpr)
   {
      CmmAddrExpr * param0 = param->conv_CmmAddrExpr ();
      send ("&");
      send_expr (param0->param);
   }
   else if (param->kind == plusExpr)
   {
      CmmPlusExpr * param0 = param->conv_CmmPlusExpr ();
      send ("+");
      send_expr (param0->param);
   }
   else if (param->kind == minusExpr)
   {
      CmmMinusExpr * param0 = param->conv_CmmMinusExpr ();
      send ("-");
      send_expr (param0->param);
   }
   else if (param->kind == bitNotExpr)
   {
      CmmBitNotExpr * param0 = param->conv_CmmBitNotExpr ();
      send ("~");
      send_expr (param0->param);
   }
   else if (param->kind == logNotExpr)
   {
      CmmLogNotExpr * param0 = param->conv_CmmLogNotExpr ();
      send ("!");
      send_expr (param0->param);
   }
   else if (param->kind == sizeofExpr)
   {
      CmmSizeofExpr * param0 = param->conv_CmmSizeofExpr ();
      send ("sizeof");
      send_expr (param0->value);
   }
   else if (param->kind == newExpr)
   {
      CmmNewExpr * param0 = param->conv_CmmNewExpr ();
      send_allocation_expr (param0);
   }
   else if (param->kind == deleteExpr)
   {
      CmmDeleteExpr * param0 = param->conv_CmmDeleteExpr ();
      send_deallocation_expr (param0);
   }
   else if (param->kind == castExpr)
   {
      CmmCastExpr * param0 = param->conv_CmmCastExpr ();
      send_expr (param0->left);
      send_expr (param0->right);
   }
   else if (param->kind == dotMemberExpr)
   {
      CmmPtrMemExpr * param0 = param->conv_CmmPtrMemExpr ();
      send_expr (param0->left);
      send (".*");
      send_expr (param0->right);
   }
   else if (param->kind == arrowMemberExpr)
   {
      CmmPtrMemExpr * param0 = param->conv_CmmPtrMemExpr ();
      send_expr (param0->left);
      send ("->*");
      send_expr (param0->right);
   }
   else if (param->kind == mulExpr)
   {
      CmmMulExpr * param0 = param->conv_CmmMulExpr ();
      send_expr (param0->left);
      send ("*");
      send_expr (param0->right);
   }
   else if (param->kind == divExpr)
   {
      CmmMulExpr * param0 = param->conv_CmmMulExpr ();
      send_expr (param0->left);
      send ("/");
      send_expr (param0->right);
   }
   else if (param->kind == modExpr)
   {
      CmmMulExpr * param0 = param->conv_CmmMulExpr ();
      send_expr (param0->left);
      send ("%");
      send_expr (param0->right);
   }
   else if (param->kind == customMulExpr)
   {
      CmmMulExpr * param0 = param->conv_CmmMulExpr ();
      send_expr (param0->left);
      send (param0->custom_mul);
      send_expr (param0->right);
   }
   else if (param->kind == addExpr)
   {
      CmmAddExpr * param0 = param->conv_CmmAddExpr ();
      send_expr (param0->left);
      send ("+");
      send_expr (param0->right);
   }
   else if (param->kind == subExpr)
   {
      CmmAddExpr * param0 = param->conv_CmmAddExpr ();
      send_expr (param0->left);
      send ("-");
      send_expr (param0->right);
   }
   else if (param->kind == customAddExpr)
   {
      CmmAddExpr * param0 = param->conv_CmmAddExpr ();
      send_expr (param0->left);
      send (param0->custom_add);
      send_expr (param0->right);
   }
   else if (param->kind == shlExpr)
   {
      CmmShiftExpr * param0 = param->conv_CmmShiftExpr ();
      send_expr (param0->left);
      send ("<<");
      send_expr (param0->right);
   }
   else if (param->kind == shrExpr)
   {
      CmmShiftExpr * param0 = param->conv_CmmShiftExpr ();
      send_expr (param0->left);
      send (">>");
      send_expr (param0->right);
   }
   else if (param->kind == ltExpr)
   {
      CmmRelExpr * param0 = param->conv_CmmRelExpr ();
      send_expr (param0->left);
      send ("<");
      send_expr (param0->right);
   }
   else if (param->kind == gtExpr)
   {
      CmmRelExpr * param0 = param->conv_CmmRelExpr ();
      send_expr (param0->left);
      send (">");
      send_expr (param0->right);
   }
   else if (param->kind == leExpr)
   {
      CmmRelExpr * param0 = param->conv_CmmRelExpr ();
      send_expr (param0->left);
      send ("<=");
      send_expr (param0->right);
   }
   else if (param->kind == geExpr)
   {
      CmmRelExpr * param0 = param->conv_CmmRelExpr ();
      send_expr (param0->left);
      send (">=");
      send_expr (param0->right);
   }
   else if (param->kind == eqExpr)
   {
      CmmEqExpr * param0 = param->conv_CmmEqExpr ();
      send_expr (param0->left);
      send ("==");
      send_expr (param0->right);
   }
   else if (param->kind == neExpr)
   {
      CmmEqExpr * param0 = param->conv_CmmEqExpr ();
      send_expr (param0->left);
      send ("!=");
      send_expr (param0->right);
   }
   else if (param->kind == bitAndExpr)
   {
      CmmAndExpr * param0 = param->conv_CmmAndExpr ();
      send_expr (param0->left);
      send ("&");
      send_expr (param0->right);
   }
   else if (param->kind == bitXorExpr)
   {
      CmmXorExpr * param0 = param->conv_CmmXorExpr ();
      send_expr (param0->left);
      send ("^");
      send_expr (param0->right);
   }
   else if (param->kind == bitOrExpr)
   {
      CmmOrExpr * param0 = param->conv_CmmOrExpr ();
      send_expr (param0->left);
      send ("|");
      send_expr (param0->right);
   }
   else if (param->kind == logAndExpr)
   {
      CmmAndAndExpr * param0 = param->conv_CmmAndAndExpr ();
      send_expr (param0->left);
      send ("&&");
      send_expr (param0->right);
   }
   else if (param->kind == logOrExpr)
   {
      CmmOrOrExpr * param0 = param->conv_CmmOrOrExpr ();
      send_expr (param0->left);
      send ("||");
      send_expr (param0->right);
   }
   else if (param->kind == assignExpr)
   {
      CmmAssignExpr * param0 = param->conv_CmmAssignExpr ();
      send_expr (param0->left);
      send ("=");
      send_expr (param0->right);
   }
   else if (param->kind == addAssignExpr)
   {
      CmmAssignExpr * param0 = param->conv_CmmAssignExpr ();
      send_expr (param0->left);
      send ("+=");
      send_expr (param0->right);
   }
   else if (param->kind == subAssignExpr)
   {
      CmmAssignExpr * param0 = param->conv_CmmAssignExpr ();
      send_expr (param0->left);
      send ("-=");
      send_expr (param0->right);
   }
   else if (param->kind == mulAssignExpr)
   {
      CmmAssignExpr * param0 = param->conv_CmmAssignExpr ();
      send_expr (param0->left);
      send ("*=");
      send_expr (param0->right);
   }
   else if (param->kind == divAssignExpr)
   {
      CmmAssignExpr * param0 = param->conv_CmmAssignExpr ();
      send_expr (param0->left);
      send ("/=");
      send_expr (param0->right);
   }
   else if (param->kind == modAssignExpr)
   {
      CmmAssignExpr * param0 = param->conv_CmmAssignExpr ();
      send_expr (param0->left);
      send ("%=");
      send_expr (param0->right);
   }
   else if (param->kind == shlAssignExpr)
   {
      CmmAssignExpr * param0 = param->conv_CmmAssignExpr ();
      send_expr (param0->left);
      send ("<<=");
      send_expr (param0->right);
   }
   else if (param->kind == shrAssignExpr)
   {
      CmmAssignExpr * param0 = param->conv_CmmAssignExpr ();
      send_expr (param0->left);
      send (">>=");
      send_expr (param0->right);
   }
   else if (param->kind == andAssignExpr)
   {
      CmmAssignExpr * param0 = param->conv_CmmAssignExpr ();
      send_expr (param0->left);
      send ("&=");
      send_expr (param0->right);
   }
   else if (param->kind == xorAssignExpr)
   {
      CmmAssignExpr * param0 = param->conv_CmmAssignExpr ();
      send_expr (param0->left);
      send ("^=");
      send_expr (param0->right);
   }
   else if (param->kind == orAssignExpr)
   {
      CmmAssignExpr * param0 = param->conv_CmmAssignExpr ();
      send_expr (param0->left);
      send ("|=");
      send_expr (param0->right);
   }
   else if (param->kind == condExpr)
   {
      CmmAssignExpr * param0 = param->conv_CmmAssignExpr ();
      send_expr (param0->left);
      send ("?");
      send_expr (param0->middle);
      send (":");
      send_expr (param0->right);
   }
   else if (param->kind == commaExpr)
   {
      CmmCommaExpr * param0 = param->conv_CmmCommaExpr ();
      send_expr (param0->left);
      send (",");
      send_expr (param0->right);
   }
   else if (param->kind == declSpec)
   {
      CmmDeclSpec * param0 = param->conv_CmmDeclSpec ();
      send_decl_specifier (param0);
   }
   else if (param->kind == constSpec)
   {
      CmmConstSpecifier * param0 = param->conv_CmmConstSpecifier ();
      send ("const");
      send_expr (param0->param);
   }
   else if (param->kind == volatileSpec)
   {
      CmmVolatileSpecifier * param0 = param->conv_CmmVolatileSpecifier ();
      send ("volatile");
      send_expr (param0->param);
   }
   else if (param->kind == typeSpec)
   {
      CmmTypeSpec * param0 = param->conv_CmmTypeSpec ();
      send_type_specifier (param0);
   }
   else if (param->kind == typeName)
   {
      CmmTypeName * param0 = param->conv_CmmTypeName ();
      send ("typename");
      send_expr (param0->qual_name);
   }
   else if (param->kind == specialName)
   {
      CmmSpecialFuction * param0 = param->conv_CmmSpecialFuction ();
      send_special_function (param0);
   }
   else if (param->kind == throwExpr)
   {
      CmmThrowExpr * param0 = param->conv_CmmThrowExpr ();
      send ("throw");
      if (param0->inner_expr != NULL)
      {
         send_expr (param0->inner_expr);
      }
   }
}

void Product::send_stat (CmmStat * param)
{
   if (param->kind == simpleStat)
   {
      CmmSimpleStat * param0 = param->conv_CmmSimpleStat ();
      send_simple_stat (param0);
   }
   else if (param->kind == emptyStat)
   {
      CmmEmptyStat * param0 = param->conv_CmmEmptyStat ();
      send_empty_stat (param0);
   }
   else if (param->kind == compoundStat)
   {
      CmmCompoundStat * param0 = param->conv_CmmCompoundStat ();
      send_compound_stat (param0);
   }
   else if (param->kind == ifStat)
   {
      CmmIfStat * param0 = param->conv_CmmIfStat ();
      send_if_stat (param0);
   }
   else if (param->kind == whileStat)
   {
      CmmWhileStat * param0 = param->conv_CmmWhileStat ();
      send_while_stat (param0);
   }
   else if (param->kind == doStat)
   {
      CmmDoStat * param0 = param->conv_CmmDoStat ();
      send_do_stat (param0);
   }
   else if (param->kind == forStat)
   {
      CmmForStat * param0 = param->conv_CmmForStat ();
      send_for_stat (param0);
   }
   else if (param->kind == switchStat)
   {
      CmmSwitchStat * param0 = param->conv_CmmSwitchStat ();
      send_switch_stat (param0);
   }
   else if (param->kind == caseStat)
   {
      CmmCaseStat * param0 = param->conv_CmmCaseStat ();
      send_case_stat (param0);
   }
   else if (param->kind == defaultStat)
   {
      CmmDefaultStat * param0 = param->conv_CmmDefaultStat ();
      send_default_stat (param0);
   }
   else if (param->kind == breakStat)
   {
      CmmBreakStat * param0 = param->conv_CmmBreakStat ();
      send_break_stat (param0);
   }
   else if (param->kind == continueStat)
   {
      CmmContinueStat * param0 = param->conv_CmmContinueStat ();
      send_continue_stat (param0);
   }
   else if (param->kind == returnStat)
   {
      CmmReturnStat * param0 = param->conv_CmmReturnStat ();
      send_return_stat (param0);
   }
   else if (param->kind == gotoStat)
   {
      CmmGotoStat * param0 = param->conv_CmmGotoStat ();
      send_goto_stat (param0);
   }
   else if (param->kind == simpleItem)
   {
      CmmSimpleItem * param0 = param->conv_CmmSimpleItem ();
      send_parameter_item (param0);
   }
   else if (param->kind == dotsParam)
   {
      CmmDotsParam * param0 = param->conv_CmmDotsParam ();
      send_dots_parameter (param0);
   }
   else if (param->kind == simpleDecl)
   {
      CmmSimpleDecl * param0 = param->conv_CmmSimpleDecl ();
      send_simple_declaration (param0);
   }
   else if (param->kind == simpleItem)
   {
      CmmSimpleItem * param0 = param->conv_CmmSimpleItem ();
      send_simple_item (param0);
   }
   else if (param->kind == namespaceDecl)
   {
      CmmNamespaceDecl * param0 = param->conv_CmmNamespaceDecl ();
      send_namespace_declaration (param0);
   }
   else if (param->kind == usingDecl)
   {
      CmmUsingDecl * param0 = param->conv_CmmUsingDecl ();
      send_using_declaration (param0);
   }
   else if (param->kind == externDecl)
   {
      CmmExternDecl * param0 = param->conv_CmmExternDecl ();
      send_extern_declaration (param0);
   }
   else if (param->kind == typedefDecl)
   {
      CmmTypedefDecl * param0 = param->conv_CmmTypedefDecl ();
      send_typedef_declaration (param0);
   }
   else if (param->kind == friendDecl)
   {
      CmmFriendDecl * param0 = param->conv_CmmFriendDecl ();
      send_friend_declaration (param0);
   }
   else if (param->kind == enumDecl)
   {
      CmmEnumDecl * param0 = param->conv_CmmEnumDecl ();
      send_enum_declaration (param0);
   }
   else if (param->kind == classDecl)
   {
      CmmClassDecl * param0 = param->conv_CmmClassDecl ();
      send_class_declaration (param0);
   }
   else if (param->kind == visibilityDecl)
   {
      CmmMemberVisibility * param0 = param->conv_CmmMemberVisibility ();
      send_member_visibility (param0);
   }
   else if (param->kind == templateDecl)
   {
      CmmTemplateDecl * param0 = param->conv_CmmTemplateDecl ();
      send_template_declaration (param0);
   }
   else if (param->kind == stencilDecl)
   {
      CmmStencilDecl * param0 = param->conv_CmmStencilDecl ();
      send_stencil_declaration (param0);
   }
   else if (param->kind == tryStat)
   {
      CmmTryStat * param0 = param->conv_CmmTryStat ();
      send_try_stat (param0);
   }
   if (param->kind == extensionStat)
      send_extension_stat (param);
}

void Product::send_extension_stat (CmmStat * param)
{
}
