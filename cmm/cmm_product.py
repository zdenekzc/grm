
from cmm_parser import *
from output import Output

class Product (Output) :

   def send_string_value_cont (self, param) :
      self.sendStr (param.value)

   def send_modern_cast_expr (self, param) :
      if param.cast_kind == dynamicCast :
         self.send ("dynamic_cast")
      elif param.cast_kind == staticCast :
         self.send ("static_cast")
      elif param.cast_kind == constCast :
         self.send ("const_cast")
      elif param.cast_kind == reinterpreterCast :
         self.send ("reinterpret_cast")
      self.send ("<")
      self.style_no_space ()
      self.send_type_id (param.type)
      self.style_no_space ()
      self.send (">")
      self.send ("(")
      self.send_expr (param.param)
      self.send (")")

   def send_expr_list (self, param) :
      inx = 0
      cnt = len (param.items)
      if inx < cnt :
         self.send_expr (param.items [inx])
         inx = inx + 1
         while inx < cnt :
            self.send (",")
            self.send_expr (param.items [inx])
            inx = inx + 1

   def send_allocation_expr (self, param) :
      self.send ("new")
      if param.type1 != None :
         self.send_new_type_id (param.type1)
      elif param.type2 != None :
         self.send ("(")
         self.send_type_id (param.type2)
         self.send (")")
      if param.init_list != None :
         self.send ("(")
         self.send_expr_list (param.init_list)
         self.send (")")

   def send_new_type_id (self, param) :
      inx = 0
      cnt = len (param.items)
      self.send_expr (param.type_spec)
      self.send_ptr_specifier_list (param.ptr)
      while inx < cnt :
         self.send_allocation_array_limit (param.items [inx])
         inx = inx + 1

   def send_allocation_array_limit (self, param) :
      self.send ("[")
      self.send_expr (param.value)
      self.send ("]")

   def send_deallocation_expr (self, param) :
      self.send ("delete")
      if param.a_array :
         self.send ("[")
         self.send ("]")
      self.send_expr (param.param)

   def send_nested_stat (self, param) :
      self.style_indent ()
      self.send_stat (param)
      self.style_unindent ()

   def send_tail_stat (self, param) :
      self.style_indent ()
      self.send_stat (param)
      self.style_unindent ()

   def send_empty_stat (self, param) :
      self.send (";")

   def send_compound_stat (self, param) :
      inx = 0
      cnt = len (param.items)
      self.send ("{")
      self.style_indent ()
      while inx < cnt :
         self.style_new_line ()
         self.send_stat (param.items [inx])
         inx = inx + 1
      self.style_unindent ()
      self.send ("}")

   def send_if_stat (self, param) :
      self.send ("if")
      self.send ("(")
      self.send_condition (param.cond)
      self.send (")")
      self.send_nested_stat (param.then_stat)
      if param.else_stat != None :
         self.style_new_line ()
         self.send ("else")
         self.send_tail_stat (param.else_stat)

   def send_while_stat (self, param) :
      self.send ("while")
      self.send ("(")
      self.send_condition (param.cond)
      self.send (")")
      self.send_nested_stat (param.body)

   def send_do_stat (self, param) :
      self.send ("do")
      self.send_nested_stat (param.body)
      self.send ("while")
      self.send ("(")
      self.send_expr (param.cond_expr)
      self.send (")")
      self.send (";")

   def send_for_stat (self, param) :
      self.send ("for")
      self.send ("(")
      if param.from_expr != None :
         self.send_condition (param.from_expr)
      if param.iter_expr != None :
         self.send (":")
         self.send_expr (param.iter_expr)
      else :
         self.send (";")
         if param.cond_expr != None :
            self.send_expr (param.cond_expr)
         self.send (";")
         if param.step_expr != None :
            self.send_expr (param.step_expr)
      self.send (")")
      self.send_nested_stat (param.body)

   def send_switch_stat (self, param) :
      self.send ("switch")
      self.send ("(")
      self.send_condition (param.cond)
      self.send (")")
      self.send_nested_stat (param.body)

   def send_case_stat (self, param) :
      self.send ("case")
      self.send_expr (param.case_expr)
      self.send (":")
      self.style_new_line ()
      self.send_nested_stat (param.body)

   def send_default_stat (self, param) :
      self.send ("default")
      self.send (":")
      self.style_new_line ()
      self.send_nested_stat (param.body)

   def send_break_stat (self, param) :
      self.send ("break")
      self.send (";")

   def send_continue_stat (self, param) :
      self.send ("continue")
      self.send (";")

   def send_return_stat (self, param) :
      self.send ("return")
      if param.return_expr != None :
         self.send_expr (param.return_expr)
      self.send (";")

   def send_goto_stat (self, param) :
      self.send ("goto")
      self.send (param.goto_lab)
      self.send (";")

   def send_simple_stat (self, param) :
      self.send_expr (param.inner_expr)
      if param.body != None :
         self.style_new_line ()
         self.send_compound_stat (param.body)
      else :
         self.send (";")

   def send_decl_specifier (self, param) :
      if param.a_inline :
         self.send ("inline")
      elif param.a_virtual :
         self.send ("virtual")
      elif param.a_explicit :
         self.send ("explicit")
      elif param.a_mutable :
         self.send ("mutable")
      elif param.a_static :
         self.send ("static")
      elif param.a_register :
         self.send ("register")
      if param.a_destructor :
         self.send ("~")
      self.send_expr (param.param)

   def send_type_specifier (self, param) :
      if param.a_signed or param.a_unsigned :
         if param.a_signed :
            self.send ("signed")
         elif param.a_unsigned :
            self.send ("unsigned")
      if param.a_short :
         self.send ("short")
      elif param.a_long :
         self.send ("long")
         if param.a_long_long or param.a_long_double :
            if param.a_long_long :
               self.send ("long")
            elif param.a_long_double :
               self.send ("double")
      elif param.a_bool :
         self.send ("bool")
      elif param.a_char :
         self.send ("char")
      elif param.a_wchar :
         self.send ("wchar_t")
      elif param.a_int :
         self.send ("int")
      elif param.a_float :
         self.send ("float")
      elif param.a_double :
         self.send ("double")
      elif param.a_void :
         self.send ("void")

   def send_pointer_declarator (self, param) :
      self.send ("*")
      self.send_cv_specifier_list (param.cv_spec)
      self.send_declarator (param.inner_declarator)

   def send_reference_declarator (self, param) :
      self.send ("&")
      self.send_cv_specifier_list (param.cv_spec)
      self.send_declarator (param.inner_declarator)

   def send_cv_specifier_list (self, param) :
      if param.cv_const or param.cv_volatile :
         if param.cv_const :
            self.send ("const")
         elif param.cv_volatile :
            self.send ("volatile")

   def send_basic_declarator (self, param) :
      self.send_expr (param.qual_name)

   def send_empty_declarator (self, param) :
      pass

   def send_nested_declarator (self, param) :
      self.send ("(")
      self.send_declarator (param.inner_declarator)
      self.send (")")

   def send_array_declarator (self, param) :
      self.send_entry_declarator (param.inner_declarator)
      self.send ("[")
      if param.lim != None :
         self.send_expr (param.lim)
      self.send ("]")

   def send_function_declarator (self, param) :
      self.send ("(")
      self.send_parameter_declaration_list (param.parameters)
      self.send (")")
      if param.a_const :
         self.send ("const")
      if param.a_override :
         self.send ("override")
      if param.exception_spec != None :
         self.send_exception_specification (param.exception_spec)

   def send_entry_declarator (self, param) :
      if param.kind == basicDeclarator :
         self.send_basic_declarator (param)
      elif param.kind == emptyDeclarator :
         self.send_empty_declarator (param)
      elif param.kind == nestedDeclarator :
         self.send_nested_declarator (param)

   def send_continue_declarator (self, param) :
      if param.kind == arrayDeclarator :
         self.send_array_declarator (param)
      elif param.kind == functionDeclarator :
         self.send_entry_declarator (param.inner_declarator)
         self.send_function_declarator (param)
      else :
         self.send_entry_declarator (param)

   def send_declarator (self, param) :
      if param.kind == pointerDeclarator :
         self.send_pointer_declarator (param)
      elif param.kind == referenceDeclarator :
         self.send_reference_declarator (param)
      elif isinstance (param, CmmDeclarator) :
         self.send_continue_declarator (param)

   def send_simple_declarator (self, param) :
      self.send_declarator (param)

   def send_common_declarator (self, param) :
      self.send_declarator (param)

   def send_constructor_declarator (self, param) :
      if param.kind == functionDeclarator :
         self.send_empty_declarator (param.inner_declarator)
         self.send_function_declarator (param)

   def send_ptr_specifier_list (self, param) :
      pass

   def send_parameter_declaration_list (self, param) :
      inx = 0
      cnt = len (param.items)
      if inx < cnt :
         self.send_parameter_declaration (param.items [inx])
         inx = inx + 1
         while inx < cnt :
            self.send (",")
            self.send_parameter_declaration (param.items [inx])
            inx = inx + 1

   def send_parameter_declaration (self, param) :
      if param.kind == simpleStat :
         self.send_value_parameter (param)
      elif param.kind == simpleDecl :
         self.send_plain_parameter (param)
      elif param.kind == dotsParam :
         self.send_dots_parameter (param)

   def send_value_parameter (self, param) :
      self.send_expr (param.inner_expr)
      pass

   def send_plain_parameter (self, param) :
      self.send_expr (param.type_spec)
      inx = 0
      cnt = len (param.items)
      self.send_parameter_item (param.items [inx])
      inx = inx + 1

   def send_parameter_item (self, param) :
      self.send_common_declarator (param.declarator)
      if param.init != None :
         self.send_initializer (param.init)
      self.send_attr_list (param.attr)

   def send_dots_parameter (self, param) :
      self.send ("...")

   def send_type_id (self, param) :
      self.send_expr (param.type_spec)
      self.send_common_declarator (param.declarator)

   def send_initializer (self, param) :
      self.send ("=")
      self.send_initializer_item (param.value)

   def send_initializer_item (self, param) :
      if isinstance (param, CmmInitSimple) :
         self.send_simple_initializer (param)
      elif isinstance (param, CmmInitList) :
         self.send_initializer_list (param)

   def send_simple_initializer (self, param) :
      self.send_expr (param.inner_expr)

   def send_initializer_list (self, param) :
      inx = 0
      cnt = len (param.items)
      self.send ("{")
      self.style_indent ()
      if inx < cnt :
         self.send_initializer_item (param.items [inx])
         inx = inx + 1
         while inx < cnt :
            self.send (",")
            self.style_new_line ()
            self.send_initializer_item (param.items [inx])
            inx = inx + 1
      self.style_unindent ()
      self.send ("}")

   def send_attr_item (self, param) :
      self.send_expr (param.attr_expr)

   def send_attr_group (self, param) :
      inx = 0
      cnt = len (param.items)
      self.send ("[[")
      self.send_attr_item (param.items [inx])
      inx = inx + 1
      while inx < cnt :
         self.send (",")
         self.send_attr_item (param.items [inx])
         inx = inx + 1
      self.send ("]]")

   def send_attr_list (self, param) :
      inx = 0
      cnt = len (param.items)
      while inx < cnt :
         self.send_attr_group (param.items [inx])
         inx = inx + 1

   def send_simple_declaration (self, param) :
      self.send_expr (param.type_spec)
      inx = 0
      cnt = len (param.items)
      self.send_simple_item (param.items [inx])
      inx = inx + 1
      while inx < cnt :
         self.send (",")
         self.send_simple_item (param.items [inx])
         inx = inx + 1
      if param.body != None :
         self.style_new_line ()
         self.send_compound_stat (param.body)
      else :
         self.send (";")

   def send_simple_item (self, param) :
      self.send_simple_declarator (param.declarator)
      if param.init != None :
         self.send_initializer (param.init)
      self.send_attr_list (param.attr)

   def send_constructor_declaration (self, param) :
      self.send_expr (param.type_spec)
      inx = 0
      cnt = len (param.items)
      self.send_constructor_item (param.items [inx])
      inx = inx + 1
      if param.body != None :
         if param.ctor_init != None :
            self.send (":")
            self.style_new_line ()
            self.send_ctor_initializer (param.ctor_init)
         self.style_new_line ()
         self.send_compound_stat (param.body)
      else :
         self.send (";")

   def send_constructor_item (self, param) :
      self.send_constructor_declarator (param.declarator)
      self.send_attr_list (param.attr)

   def send_condition (self, param) :
      if param.kind == simpleStat :
         self.send_condition_value (param)
      elif param.kind == simpleDecl :
         self.send_condition_declaration (param)

   def send_condition_declaration (self, param) :
      self.send_expr (param.type_spec)
      inx = 0
      cnt = len (param.items)
      self.send_condition_item (param.items [inx])
      inx = inx + 1
      while inx < cnt :
         self.send (",")
         self.send_condition_item (param.items [inx])
         inx = inx + 1

   def send_condition_item (self, param) :
      self.send_simple_declarator (param.declarator)
      if param.init != None :
         self.send_initializer (param.init)
      self.send_attr_list (param.attr)

   def send_condition_value (self, param) :
      self.send_expr (param.inner_expr)
      pass

   def send_declaration_list (self, param) :
      inx = 0
      cnt = len (param.items)
      while inx < cnt :
         self.send_stat (param.items [inx])
         inx = inx + 1
         self.style_new_line ()

   def send_namespace_declaration (self, param) :
      self.send ("namespace")
      self.send_expr (param.simp_name)
      self.send_attr_list (param.attr)
      self.style_new_line ()
      self.send ("{")
      self.style_new_line ()
      self.style_indent ()
      self.send_declaration_list (param.members)
      self.style_unindent ()
      self.send ("}")

   def send_using_declaration (self, param) :
      self.send ("using")
      if param.a_namespace :
         self.send ("namespace")
      self.send_expr (param.qual_name)
      self.send (";")

   def send_extern_declaration (self, param) :
      self.send ("extern")
      if param.language != "" :
         self.sendStr (param.language)
      if param.members != None :
         self.send ("{")
         self.send_declaration_list (param.members)
         self.send ("}")
      elif param.inner_declaration != None :
         self.send_stat (param.inner_declaration)

   def send_typedef_declaration (self, param) :
      self.send ("typedef")
      self.send_expr (param.type_spec)
      self.send_simple_declarator (param.declarator)
      self.send (";")

   def send_friend_declaration (self, param) :
      self.send ("friend")
      self.send_stat (param.inner_declaration)

   def send_enum_declaration (self, param) :
      self.send ("enum")
      self.send_expr (param.simp_name)
      if param.enum_items != None :
         self.style_new_line ()
         self.send ("{")
         self.style_indent ()
         self.send_enum_list (param.enum_items)
         self.style_unindent ()
         self.send ("}")
      self.send (";")

   def send_enum_list (self, param) :
      inx = 0
      cnt = len (param.items)
      if inx < cnt :
         self.send_enumerator (param.items [inx])
         inx = inx + 1
         while inx < cnt :
            self.send (",")
            self.send_enumerator (param.items [inx])
            inx = inx + 1

   def send_enumerator (self, param) :
      self.style_new_line ()
      self.send_expr (param.simp_name)
      if param.init_value != None :
         self.send ("=")
         self.send_expr (param.init_value)

   def send_class_declaration (self, param) :
      if param.style == classStyle :
         self.send ("class")
      elif param.style == structStyle :
         self.send ("struct")
      elif param.style == unionStyle :
         self.send ("union")
      self.send_expr (param.simp_name)
      self.send_attr_list (param.attr)
      if param.members != None :
         if param.base_list != None :
            self.send (":")
            self.send_base_specifier_list (param.base_list)
         self.style_new_line ()
         self.send ("{")
         self.style_indent ()
         self.send_member_list (param.members)
         self.style_unindent ()
         self.send ("}")
      self.send (";")

   def send_member_visibility (self, param) :
      if param.access == privateAccess :
         self.send ("private")
      elif param.access == protectedAccess :
         self.send ("protected")
      elif param.access == publicAccess :
         self.send ("public")
      self.style_no_space ()
      self.send (":")

   def send_member_list (self, param) :
      inx = 0
      cnt = len (param.items)
      while inx < cnt :
         self.send_stat (param.items [inx])
         inx = inx + 1
         self.style_new_line ()

   def send_base_specifier_list (self, param) :
      inx = 0
      cnt = len (param.items)
      self.send_base_specifier (param.items [inx])
      inx = inx + 1
      while inx < cnt :
         self.send (",")
         self.send_base_specifier (param.items [inx])
         inx = inx + 1

   def send_base_specifier (self, param) :
      if param.a_virtual :
         self.send ("virtual")
      if param.access == privateBase :
         self.send ("private")
      elif param.access == protectedBase :
         self.send ("protected")
      elif param.access == publicBase :
         self.send ("public")
      elif param.access == unknownBase :
         pass
      self.send_expr (param.from_cls)

   def send_ctor_initializer (self, param) :
      inx = 0
      cnt = len (param.items)
      self.style_indent ()
      self.send_member_initializer (param.items [inx])
      inx = inx + 1
      while inx < cnt :
         self.send (",")
         self.style_new_line ()
         self.send_member_initializer (param.items [inx])
         inx = inx + 1
      self.style_unindent ()

   def send_member_initializer (self, param) :
      self.send_expr (param.simp_name)
      self.send ("(")
      self.send_expr_list (param.params)
      self.send (")")

   def send_conversion_specifiers (self, param) :
      self.send_expr (param.type_spec)
      self.send_ptr_specifier_list (param.ptr_spec)

   def send_special_function (self, param) :
      self.send ("operator")
      if param.conv != None :
         self.send_conversion_specifiers (param.conv)
      elif param.spec_new :
         self.send ("new")
         if param.spec_new_array :
            self.send ("[")
            self.send ("]")
      elif param.spec_delete :
         self.send ("delete")
         if param.spec_delete_array :
            self.send ("[")
            self.send ("]")
      elif param.spec_add :
         self.send ("+")
      elif param.spec_sub :
         self.send ("-")
      elif param.spec_mul :
         self.send ("*")
      elif param.spec_div :
         self.send ("/")
      elif param.spec_mod :
         self.send ("%")
      elif param.spec_xor :
         self.send ("^")
      elif param.spec_and :
         self.send ("&")
      elif param.spec_or :
         self.send ("|")
      elif param.spec_not :
         self.send ("~")
      elif param.spec_log_not :
         self.send ("!")
      elif param.spec_assign :
         self.send ("=")
      elif param.spec_lt :
         self.send ("<")
      elif param.spec_gt :
         self.send (">")
      elif param.spec_add_assign :
         self.send ("+=")
      elif param.spec_sub_assign :
         self.send ("-=")
      elif param.spec_mul_assign :
         self.send ("*=")
      elif param.spec_div_assign :
         self.send ("/=")
      elif param.spec_mod_assign :
         self.send ("%=")
      elif param.spec_xor_assign :
         self.send ("^=")
      elif param.spec_and_assign :
         self.send ("&=")
      elif param.spec_or_assign :
         self.send ("|=")
      elif param.spec_shl :
         self.send ("<<")
      elif param.spec_shr :
         self.send (">>")
      elif param.spec_shl_assign :
         self.send (">>=")
      elif param.spec_shr_assign :
         self.send ("<<=")
      elif param.spec_eq :
         self.send ("==")
      elif param.spec_ne :
         self.send ("!=")
      elif param.spec_le :
         self.send ("<=")
      elif param.spec_ge :
         self.send (">=")
      elif param.spec_log_and :
         self.send ("&&")
      elif param.spec_log_or :
         self.send ("||")
      elif param.spec_inc :
         self.send ("++")
      elif param.spec_dec :
         self.send ("--")
      elif param.spec_comma :
         self.send (",")
      elif param.spec_member_deref :
         self.send ("->*")
      elif param.spec_deref :
         self.send ("->")
      elif param.spec_call :
         self.send ("(")
         self.send (")")
      elif param.spec_index :
         self.send ("[")
         self.send ("]")

   def send_template_declaration (self, param) :
      self.send ("template")
      if param.params != None :
         self.send ("<")
         self.send_template_param_list (param.params)
         self.send (">")
      self.send_stat (param.inner_declaration)

   def send_stencil_declaration (self, param) :
      self.send ("stencil")
      self.send_expr (param.simp_name)
      self.send ("<")
      self.send_template_param_list (param.params)
      self.send (">")
      self.send ("{")
      self.send_stencil_member_list (param.members)
      self.send ("}")

   def send_stencil_member_list (self, param) :
      inx = 0
      cnt = len (param.items)
      while inx < cnt :
         self.send_stat (param.items [inx])
         inx = inx + 1
         self.style_new_line ()

   def send_template_param_list (self, param) :
      inx = 0
      cnt = len (param.items)
      if inx < cnt :
         self.send_template_param (param.items [inx])
         inx = inx + 1
         while inx < cnt :
            self.send (",")
            self.send_template_param (param.items [inx])
            inx = inx + 1

   def send_template_param (self, param) :
      if param.kind == templateTypeParam :
         self.send_template_type_param (param)
      elif param.kind == templateCommonParam :
         self.send_template_normal_param (param)

   def send_template_type_param (self, param) :
      if param.params != None :
         self.send ("template")
         self.send ("<")
         self.send_template_param_list (param.params)
         self.send (">")
      if param.a_class :
         self.send ("class")
      elif param.a_typename :
         self.send ("typename")
      if param.simp_name != None :
         self.send_expr (param.simp_name)

   def send_template_normal_param (self, param) :
      self.send_expr (param.type_spec)
      self.send_common_declarator (param.declarator)
      if param.init != None :
         self.send ("=")
         self.send_expr (param.init)

   def send_template_arg_list (self, param) :
      inx = 0
      cnt = len (param.items)
      self.send ("<")
      if inx < cnt :
         self.send_template_arg (param.items [inx])
         inx = inx + 1
         while inx < cnt :
            self.send (",")
            self.send_template_arg (param.items [inx])
            inx = inx + 1
      self.send (">")

   def send_template_arg (self, param) :
      self.send_parameter_declaration (param.value)

   def send_try_stat (self, param) :
      self.send ("try")
      self.style_new_line ()
      self.send_compound_stat (param.body)
      self.send_handler_list (param.handlers)

   def send_handler_list (self, param) :
      inx = 0
      cnt = len (param.items)
      self.send_handler (param.items [inx])
      inx = inx + 1
      while inx < cnt :
         self.send_handler (param.items [inx])
         inx = inx + 1

   def send_handler (self, param) :
      self.style_new_line ()
      self.send ("catch")
      self.send ("(")
      if param.type_spec != None :
         self.send_expr (param.type_spec)
         self.send_common_declarator (param.declarator)
      elif param.dots :
         self.send ("...")
      self.send (")")
      self.style_new_line ()
      self.send_compound_stat (param.body)

   def send_exception_specification (self, param) :
      inx = 0
      cnt = len (param.items)
      self.send ("throw")
      self.send ("(")
      if inx < cnt :
         self.send_exception_specification_item (param.items [inx])
         inx = inx + 1
         while inx < cnt :
            self.send (",")
            self.send_exception_specification_item (param.items [inx])
            inx = inx + 1
      self.send (")")

   def send_exception_specification_item (self, param) :
      self.send_type_id (param.type)

   def send_expr (self, param) :
      if param.kind == simpleName:
         self.send (param.id)
      elif param.kind == globalName:
         self.send ("::")
         self.send_expr (param.inner_name)
      elif param.kind == destructorName:
         self.send ("~")
         self.send_expr (param.inner_name)
      elif param.kind == compoundName:
         self.send_expr (param.left)
         self.style_no_space ()
         self.send ("::")
         self.style_no_space ()
         self.send_expr (param.right)
      elif param.kind == templateName:
         self.send_expr (param.left)
         self.send_template_arg_list (param.template_args)
      elif param.kind == intValue:
         self.send (param.value)
      elif param.kind == realValue:
         self.send (param.value)
      elif param.kind == charValue:
         self.sendChr (param.value)
      elif param.kind == stringValue:
         inx = 0
         cnt = len (param.items)
         self.sendStr (param.value)
         while inx < cnt :
            self.send_string_value_cont (param.items [inx])
            inx = inx + 1
      elif param.kind == thisExpr:
         self.send ("this")
      elif param.kind == lambdaExpr:
         self.send ("[")
         if param.by_reference :
            self.send ("&")
         self.send ("]")
         self.send_compound_stat (param.body)
      elif param.kind == subexprExpr:
         self.send ("(")
         self.send_expr (param.param)
         self.send (")")
      elif param.kind == signalSlotExpr:
         self.send (param.macro_name)
         self.send ("(")
         self.send (param.func_name)
         if param.parameters != None :
            self.send ("(")
            self.send_parameter_declaration_list (param.parameters)
            self.send (")")
         self.send (")")
      elif param.kind == modernCastExpr:
         self.send_modern_cast_expr (param)
      elif param.kind == typeIdExpr:
         self.send ("typeid")
         self.send ("(")
         self.send_expr (param.value)
         self.send (")")
      elif param.kind == indexExpr:
         self.send_expr (param.left)
         self.send ("[")
         self.send_expr (param.param)
         self.send ("]")
      elif param.kind == callExpr:
         self.send_expr (param.left)
         self.send ("(")
         self.send_expr_list (param.param_list)
         self.send (")")
      elif param.kind == fieldExpr:
         self.send_expr (param.left)
         self.style_no_space ()
         self.send (".")
         self.style_no_space ()
         self.send_expr (param.field_name)
      elif param.kind == ptrFieldExpr:
         self.send_expr (param.left)
         self.style_no_space ()
         self.send ("->")
         self.style_no_space ()
         self.send_expr (param.field_name)
      elif param.kind == postIncExpr:
         self.send_expr (param.left)
         self.send ("++")
      elif param.kind == postDecExpr:
         self.send_expr (param.left)
         self.send ("--")
      elif param.kind == incExpr:
         self.send ("++")
         self.send_expr (param.param)
      elif param.kind == decExpr:
         self.send ("--")
         self.send_expr (param.param)
      elif param.kind == derefExpr:
         self.send ("*")
         self.send_expr (param.param)
      elif param.kind == addrExpr:
         self.send ("&")
         self.send_expr (param.param)
      elif param.kind == plusExpr:
         self.send ("+")
         self.send_expr (param.param)
      elif param.kind == minusExpr:
         self.send ("-")
         self.send_expr (param.param)
      elif param.kind == bitNotExpr:
         self.send ("~")
         self.send_expr (param.param)
      elif param.kind == logNotExpr:
         self.send ("!")
         self.send_expr (param.param)
      elif param.kind == sizeofExpr:
         self.send ("sizeof")
         self.send_expr (param.value)
      elif param.kind == newExpr:
         self.send_allocation_expr (param)
      elif param.kind == deleteExpr:
         self.send_deallocation_expr (param)
      elif param.kind == castExpr :
         self.send_expr (param.left)
         self.send_expr (param.right)
      elif param.kind == dotMemberExpr :
         self.send_expr (param.left)
         self.send (".*")
         self.send_expr (param.right)
      elif param.kind == arrowMemberExpr :
         self.send_expr (param.left)
         self.send ("->*")
         self.send_expr (param.right)
      elif param.kind == mulExpr :
         self.send_expr (param.left)
         self.send ("*")
         self.send_expr (param.right)
      elif param.kind == divExpr :
         self.send_expr (param.left)
         self.send ("/")
         self.send_expr (param.right)
      elif param.kind == modExpr :
         self.send_expr (param.left)
         self.send ("%")
         self.send_expr (param.right)
      elif param.kind == customMulExpr :
         self.send_expr (param.left)
         self.send (param.custom_mul)
         self.send_expr (param.right)
      elif param.kind == addExpr :
         self.send_expr (param.left)
         self.send ("+")
         self.send_expr (param.right)
      elif param.kind == subExpr :
         self.send_expr (param.left)
         self.send ("-")
         self.send_expr (param.right)
      elif param.kind == customAddExpr :
         self.send_expr (param.left)
         self.send (param.custom_add)
         self.send_expr (param.right)
      elif param.kind == shlExpr :
         self.send_expr (param.left)
         self.send ("<<")
         self.send_expr (param.right)
      elif param.kind == shrExpr :
         self.send_expr (param.left)
         self.send (">>")
         self.send_expr (param.right)
      elif param.kind == ltExpr :
         self.send_expr (param.left)
         self.send ("<")
         self.send_expr (param.right)
      elif param.kind == gtExpr :
         self.send_expr (param.left)
         self.send (">")
         self.send_expr (param.right)
      elif param.kind == leExpr :
         self.send_expr (param.left)
         self.send ("<=")
         self.send_expr (param.right)
      elif param.kind == geExpr :
         self.send_expr (param.left)
         self.send (">=")
         self.send_expr (param.right)
      elif param.kind == eqExpr :
         self.send_expr (param.left)
         self.send ("==")
         self.send_expr (param.right)
      elif param.kind == neExpr :
         self.send_expr (param.left)
         self.send ("!=")
         self.send_expr (param.right)
      elif param.kind == bitAndExpr :
         self.send_expr (param.left)
         self.send ("&")
         self.send_expr (param.right)
      elif param.kind == bitXorExpr :
         self.send_expr (param.left)
         self.send ("^")
         self.send_expr (param.right)
      elif param.kind == bitOrExpr :
         self.send_expr (param.left)
         self.send ("|")
         self.send_expr (param.right)
      elif param.kind == logAndExpr :
         self.send_expr (param.left)
         self.send ("&&")
         self.send_expr (param.right)
      elif param.kind == logOrExpr :
         self.send_expr (param.left)
         self.send ("||")
         self.send_expr (param.right)
      elif param.kind == assignExpr :
         self.send_expr (param.left)
         self.send ("=")
         self.send_expr (param.right)
      elif param.kind == addAssignExpr :
         self.send_expr (param.left)
         self.send ("+=")
         self.send_expr (param.right)
      elif param.kind == subAssignExpr :
         self.send_expr (param.left)
         self.send ("-=")
         self.send_expr (param.right)
      elif param.kind == mulAssignExpr :
         self.send_expr (param.left)
         self.send ("*=")
         self.send_expr (param.right)
      elif param.kind == divAssignExpr :
         self.send_expr (param.left)
         self.send ("/=")
         self.send_expr (param.right)
      elif param.kind == modAssignExpr :
         self.send_expr (param.left)
         self.send ("%=")
         self.send_expr (param.right)
      elif param.kind == shlAssignExpr :
         self.send_expr (param.left)
         self.send ("<<=")
         self.send_expr (param.right)
      elif param.kind == shrAssignExpr :
         self.send_expr (param.left)
         self.send (">>=")
         self.send_expr (param.right)
      elif param.kind == andAssignExpr :
         self.send_expr (param.left)
         self.send ("&=")
         self.send_expr (param.right)
      elif param.kind == xorAssignExpr :
         self.send_expr (param.left)
         self.send ("^=")
         self.send_expr (param.right)
      elif param.kind == orAssignExpr :
         self.send_expr (param.left)
         self.send ("|=")
         self.send_expr (param.right)
      elif param.kind == condExpr :
         self.send_expr (param.left)
         self.send ("?")
         self.send_expr (param.middle)
         self.send (":")
         self.send_expr (param.right)
      elif param.kind == commaExpr :
         self.send_expr (param.left)
         self.send (",")
         self.send_expr (param.right)
      elif param.kind == declSpec:
         self.send_decl_specifier (param)
      elif param.kind == constSpec:
         self.send ("const")
         self.send_expr (param.param)
      elif param.kind == volatileSpec:
         self.send ("volatile")
         self.send_expr (param.param)
      elif param.kind == typeSpec:
         self.send_type_specifier (param)
      elif param.kind == typeName:
         self.send ("typename")
         self.send_expr (param.qual_name)
      elif param.kind == specialName:
         self.send_special_function (param)
      elif param.kind == throwExpr:
         self.send ("throw")
         if param.inner_expr != None :
            self.send_expr (param.inner_expr)

   def send_stat (self, param) :
      if param.kind == simpleStat:
         self.send_simple_stat (param)
      elif param.kind == emptyStat:
         self.send_empty_stat (param)
      elif param.kind == compoundStat:
         self.send_compound_stat (param)
      elif param.kind == ifStat:
         self.send_if_stat (param)
      elif param.kind == whileStat:
         self.send_while_stat (param)
      elif param.kind == doStat:
         self.send_do_stat (param)
      elif param.kind == forStat:
         self.send_for_stat (param)
      elif param.kind == switchStat:
         self.send_switch_stat (param)
      elif param.kind == caseStat:
         self.send_case_stat (param)
      elif param.kind == defaultStat:
         self.send_default_stat (param)
      elif param.kind == breakStat:
         self.send_break_stat (param)
      elif param.kind == continueStat:
         self.send_continue_stat (param)
      elif param.kind == returnStat:
         self.send_return_stat (param)
      elif param.kind == gotoStat:
         self.send_goto_stat (param)
      elif param.kind == simpleItem:
         self.send_parameter_item (param)
      elif param.kind == dotsParam:
         self.send_dots_parameter (param)
      elif param.kind == simpleDecl:
         self.send_simple_declaration (param)
      elif param.kind == simpleItem:
         self.send_simple_item (param)
      elif param.kind == namespaceDecl:
         self.send_namespace_declaration (param)
      elif param.kind == usingDecl:
         self.send_using_declaration (param)
      elif param.kind == externDecl:
         self.send_extern_declaration (param)
      elif param.kind == typedefDecl:
         self.send_typedef_declaration (param)
      elif param.kind == friendDecl:
         self.send_friend_declaration (param)
      elif param.kind == enumDecl:
         self.send_enum_declaration (param)
      elif param.kind == classDecl:
         self.send_class_declaration (param)
      elif param.kind == visibilityDecl:
         self.send_member_visibility (param)
      elif param.kind == templateDecl:
         self.send_template_declaration (param)
      elif param.kind == stencilDecl:
         self.send_stencil_declaration (param)
      elif param.kind == tryStat:
         self.send_try_stat (param)
      elif param.kind == extensionStat :
         self.send_extension_stat (param)

   def send_extension_stat (self, param) :
      pass

