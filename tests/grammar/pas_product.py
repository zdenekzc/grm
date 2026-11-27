
from pas_parser import *
from output import Output

class Product (Output) :

   def send_label_ident (self, param) :
      self.send (param.id)

   def send_qualified_name (self, param) :
      inx = 0
      cnt = len (param.items)
      self.send (param.id)
      while inx < cnt :
         self.send_cont_name (param.items [inx])
         inx = inx + 1

   def send_cont_name (self, param) :
      self.style_no_space ()
      self.send (".")
      self.style_no_space ()
      self.send (param.id)

   def send_ifc_type (self, param) :
      self.send_simple_alias_type (param)

   def send_param_type (self, param) :
      if isinstance (param, TAliasType) :
         self.send_simple_alias_type (param)
      elif isinstance (param, TStringType) :
         self.send_simple_string_type (param)
      elif isinstance (param, TFileType) :
         self.send_simple_file_type (param)

   def send_result_type (self, param) :
      if isinstance (param, TAliasType) :
         self.send_simple_alias_type (param)
      elif isinstance (param, TStringType) :
         self.send_simple_string_type (param)

   def send_simple_alias_type (self, param) :
      self.send_qualified_name (param.alias_name)

   def send_simple_string_type (self, param) :
      self.send ("string")

   def send_simple_file_type (self, param) :
      self.send ("file")

   def send_index_expr_item (self, param) :
      self.send_expr (param.ref)

   def send_index_expr_list (self, param) :
      inx = 0
      cnt = len (param.items)
      self.send_index_expr_item (param.items [inx])
      inx = inx + 1
      while inx < cnt :
         self.send (",")
         self.send_index_expr_item (param.items [inx])
         inx = inx + 1

   def send_arg_item (self, param) :
      self.send_expr (param.value)
      if param.width != None :
         self.send (":")
         self.send_expr (param.width)
         if param.digits != None :
            self.send (":")
            self.send_expr (param.digits)

   def send_arg_list (self, param) :
      inx = 0
      cnt = len (param.items)
      self.send_arg_item (param.items [inx])
      inx = inx + 1
      while inx < cnt :
         self.send (",")
         self.send_arg_item (param.items [inx])
         inx = inx + 1

   def send_elem_sect (self, param) :
      inx = 0
      cnt = len (param.items)
      self.send_elem_item (param.items [inx])
      inx = inx + 1
      while inx < cnt :
         self.send (",")
         self.send_elem_item (param.items [inx])
         inx = inx + 1

   def send_elem_item (self, param) :
      self.send_expr (param.low)
      if param.high != None :
         self.send ("..")
         self.send_expr (param.high)

   def send_struct_item (self, param) :
      if param.name != "" :
         self.send (param.name)
         self.send (":")
      self.send_expr (param.value)

   def send_struct_sect (self, param) :
      inx = 0
      cnt = len (param.items)
      self.send_struct_item (param.items [inx])
      inx = inx + 1
      if inx < cnt or inx < cnt :
         if inx < cnt :
            self.send (",")
            self.send_struct_item (param.items [inx])
            inx = inx + 1
            while inx < cnt :
               self.send (",")
               self.send_struct_item (param.items [inx])
               inx = inx + 1
         elif inx < cnt :
            self.send (";")
            self.send_struct_item (param.items [inx])
            inx = inx + 1
            while inx < cnt :
               self.send (";")
               self.send_struct_item (param.items [inx])
               inx = inx + 1

   def send_ident_expr (self, param) :
      self.send (param.name)

   def send_int_value_expr (self, param) :
      self.send (param.value)

   def send_float_value_expr (self, param) :
      self.send (param.value)

   def send_string_value_expr (self, param) :
      self.sendStr (param.value)

   def send_nil_expr (self, param) :
      self.send ("nil")

   def send_sub_expr (self, param) :
      self.send ("(")
      self.send_expr (param.value)
      self.send (")")

   def send_not_expr (self, param) :
      self.send ("not")
      self.send_factor (param.param)

   def send_plus_expr (self, param) :
      self.send ("+")
      self.send_factor (param.param)

   def send_minus_expr (self, param) :
      self.send ("-")
      self.send_factor (param.param)

   def send_adr_expr (self, param) :
      self.send ("@")
      self.send_factor (param.param)

   def send_set_expr (self, param) :
      self.send ("[")
      self.send_elem_sect (param.list)
      self.send ("]")

   def send_super_expr (self, param) :
      self.send ("inherited")
      self.send (param.name)

   def send_string_type_expr (self, param) :
      self.send ("string")
      self.send ("(")
      self.send_expr (param.param)
      self.send (")")

   def send_variable (self, param) :
      if isinstance (param, TIdentExpr) :
         self.send_ident_expr (param)
      elif isinstance (param, TStructExpr) :
         self.send_sub_expr (param)
      elif isinstance (param, TSuperExpr) :
         self.send_super_expr (param)

   def send_reference (self, param) :
      if isinstance (param, TIndexExpr) :
         self.send_index_expr (param)
      elif isinstance (param, TCallExpr) :
         self.send_call_expr (param)
      elif isinstance (param, TDerefExpr) :
         self.send_deref_expr (param)
      elif isinstance (param, TFieldExpr) :
         self.send_field_expr (param)
      else :
         self.send_variable (param)

   def send_index_expr (self, param) :
      self.send_variable (param.left)
      self.send ("[")
      self.send_index_expr_list (param.list)
      self.send ("]")

   def send_call_expr (self, param) :
      self.send_variable (param.func)
      self.send ("(")
      self.send_arg_list (param.list)
      self.send (")")

   def send_deref_expr (self, param) :
      self.send_variable (param.param)
      self.send ("^")

   def send_field_expr (self, param) :
      self.send_variable (param.param)
      self.style_no_space ()
      self.send (".")
      self.style_no_space ()
      self.send (param.name)

   def send_factor (self, param) :
      if isinstance (param, TIntValueExpr) :
         self.send_int_value_expr (param)
      elif isinstance (param, TFltValueExpr) :
         self.send_float_value_expr (param)
      elif isinstance (param, TStrValueExpr) :
         self.send_string_value_expr (param)
      elif isinstance (param, TNotExpr) :
         self.send_not_expr (param)
      elif isinstance (param, TPlusExpr) :
         self.send_plus_expr (param)
      elif isinstance (param, TMinusExpr) :
         self.send_minus_expr (param)
      elif isinstance (param, TAdrExpr) :
         self.send_adr_expr (param)
      elif isinstance (param, TNilExpr) :
         self.send_nil_expr (param)
      elif isinstance (param, TSetExpr) :
         self.send_set_expr (param)
      elif isinstance (param, TStringExpr) :
         self.send_string_type_expr (param)
      elif isinstance (param, TExpr) :
         self.send_reference (param)

   def send_term (self, param) :
      if param.fce == MulExp :
         self.send_factor (param.left)
         self.send ("*")
         self.send_factor (param.right)
      elif param.fce == RDivExp :
         self.send_factor (param.left)
         self.send ("/")
         self.send_factor (param.right)
      elif param.fce == DivExp :
         self.send_factor (param.left)
         self.send ("div")
         self.send_factor (param.right)
      elif param.fce == ModExp :
         self.send_factor (param.left)
         self.send ("mod")
         self.send_factor (param.right)
      elif param.fce == ShlExp :
         self.send_factor (param.left)
         self.send ("shl")
         self.send_factor (param.right)
      elif param.fce == ShrExp :
         self.send_factor (param.left)
         self.send ("shr")
         self.send_factor (param.right)
      elif param.fce == AndExp :
         self.send_factor (param.left)
         self.send ("and")
         self.send_factor (param.right)
      elif param.fce == AsExp :
         self.send_factor (param.left)
         self.send ("as")
         self.send_factor (param.right)
      else :
         self.send_factor (param)

   def send_simple_expr (self, param) :
      if param.fce == AddExp :
         self.send_term (param.left)
         self.send ("+")
         self.send_term (param.right)
      elif param.fce == SubExp :
         self.send_term (param.left)
         self.send ("-")
         self.send_term (param.right)
      elif param.fce == OrExp :
         self.send_term (param.left)
         self.send ("or")
         self.send_term (param.right)
      elif param.fce == XorExp :
         self.send_term (param.left)
         self.send ("xor")
         self.send_term (param.right)
      else :
         self.send_term (param)

   def send_expr (self, param) :
      if param.fce == EqExp :
         self.send_simple_expr (param.left)
         self.send ("=")
         self.send_simple_expr (param.right)
      elif param.fce == NeExp :
         self.send_simple_expr (param.left)
         self.send ("<>")
         self.send_simple_expr (param.right)
      elif param.fce == LtExp :
         self.send_simple_expr (param.left)
         self.send ("<")
         self.send_simple_expr (param.right)
      elif param.fce == GtExp :
         self.send_simple_expr (param.left)
         self.send (">")
         self.send_simple_expr (param.right)
      elif param.fce == LeExp :
         self.send_simple_expr (param.left)
         self.send ("<=")
         self.send_simple_expr (param.right)
      elif param.fce == GeExp :
         self.send_simple_expr (param.left)
         self.send (">=")
         self.send_simple_expr (param.right)
      elif param.fce == InExp :
         self.send_simple_expr (param.left)
         self.send ("in")
         self.send_simple_expr (param.right)
      elif param.fce == IsExp :
         self.send_simple_expr (param.left)
         self.send ("is")
         self.send_simple_expr (param.right)
      else :
         self.send_simple_expr (param)

   def send_goto_stat (self, param) :
      self.send ("goto")
      self.send_label_ident (param.goto_lab)

   def send_begin_stat (self, param) :
      self.send ("begin")
      self.send_stat_list (param.body_seq)
      self.send ("end")

   def send_stat_list (self, param) :
      inx = 0
      cnt = len (param.items)
      self.style_new_line ()
      self.style_indent ()
      self.send_stat (param.items [inx])
      inx = inx + 1
      while inx < cnt :
         self.send (";")
         self.style_new_line ()
         self.send_stat (param.items [inx])
         inx = inx + 1
      self.style_unindent ()
      self.style_new_line ()

   def send_inner_stat (self, param) :
      self.style_new_line ()
      self.style_indent ()
      self.send_stat (param)
      self.style_unindent ()

   def send_if_stat (self, param) :
      self.send ("if")
      self.send_expr (param.cond_expr)
      self.send ("then")
      self.send_inner_stat (param.then_stat)
      if param.else_stat != None :
         self.send ("else")
         self.send_inner_stat (param.else_stat)

   def send_case_stat (self, param) :
      self.send ("case")
      self.send_expr (param.case_expr)
      self.send ("of")
      self.send_case_sect (param.case_list)
      if param.else_seq != None :
         self.send ("else")
         self.send_stat_list (param.else_seq)
      self.send ("end")

   def send_case_sect (self, param) :
      inx = 0
      cnt = len (param.items)
      self.send_case_item (param.items [inx])
      inx = inx + 1
      while inx < cnt :
         self.send (";")
         self.style_new_line ()
         self.send_case_item (param.items [inx])
         inx = inx + 1

   def send_case_item (self, param) :
      self.send_elem_sect (param.sel_list)
      self.send (":")
      self.send_inner_stat (param.sel_stat)

   def send_while_stat (self, param) :
      self.send ("while")
      self.send_expr (param.cond_expr)
      self.send ("do")
      self.send_inner_stat (param.body_stat)

   def send_repeat_stat (self, param) :
      self.send ("repeat")
      self.send_stat_list (param.body_seq)
      self.send ("until")
      self.send_expr (param.until_expr)

   def send_for_stat (self, param) :
      self.send ("for")
      self.send_variable (param.var_expr)
      self.send (":=")
      self.send_expr (param.from_expr)
      if param.incr :
         self.send ("to")
      elif not param.incr :
         self.send ("downto")
      self.send_expr (param.to_expr)
      self.send ("do")
      self.send_inner_stat (param.body_stat)

   def send_with_stat (self, param) :
      self.send ("with")
      self.send_with_sect (param.with_list)
      self.send ("do")
      self.send_inner_stat (param.body_stat)

   def send_with_sect (self, param) :
      inx = 0
      cnt = len (param.items)
      self.send_with_item (param.items [inx])
      inx = inx + 1
      while inx < cnt :
         self.send (",")
         self.send_with_item (param.items [inx])
         inx = inx + 1

   def send_with_item (self, param) :
      self.send_variable (param.expr)

   def send_raise_stat (self, param) :
      self.send ("raise")
      if param.raise_expr != None :
         self.send_expr (param.raise_expr)

   def send_try_stat (self, param) :
      self.send ("try")
      self.send_stat_list (param.body_seq)
      if param.finally_branch != None :
         self.send_finally_part (param.finally_branch)
      elif param.except_branch != None :
         self.send_except_part (param.except_branch)
      self.send ("end")

   def send_finally_part (self, param) :
      self.send ("finally")
      self.send_stat_list (param.finally_seq)

   def send_except_part (self, param) :
      self.send ("except")
      if param.on_list != None :
         self.send_on_sect (param.on_list)
         if param.else_seq != None :
            self.send ("else")
            self.send_stat_list (param.else_seq)
      elif param.else_seq != None :
         self.send_stat_list (param.else_seq)

   def send_on_sect (self, param) :
      inx = 0
      cnt = len (param.items)
      self.send_on_item (param.items [inx])
      inx = inx + 1
      while inx < cnt :
         self.send (";")
         self.send_on_item (param.items [inx])
         inx = inx + 1
      if param.semicolon :
         self.send (";")

   def send_on_item (self, param) :
      self.send ("on")
      if param.on_ident != "" :
         self.send (param.on_ident)
         self.send (":")
      self.send_type (param.on_type)
      self.send ("do")
      self.send_inner_stat (param.body_stat)

   def send_empty_stat (self, param) :
      pass

   def send_simple_stat (self, param) :
      if isinstance (param, TAssignStat) :
         self.send_assign_stat (param)
      elif isinstance (param, TCallStat) :
         self.send_call_stat (param)

   def send_assign_stat (self, param) :
      self.send_expr (param.left_expr)
      self.send (":=")
      self.send_expr (param.right_expr)

   def send_call_stat (self, param) :
      self.send_expr (param.call_expr)
      pass

   def send_labeled_stat (self, param) :
      self.send_label_ident (param.lab)
      self.send (":")
      self.send_stat (param.body)

   def send_stat (self, param) :
      if isinstance (param, TLabeledTStat) :
         self.send_labeled_stat (param)
      elif isinstance (param, TStat) :
         self.send_simple_stat (param)
      elif isinstance (param, TEmptyStat) :
         self.send_empty_stat (param)
      elif isinstance (param, TGotoStat) :
         self.send_goto_stat (param)
      elif isinstance (param, TBlockStat) :
         self.send_begin_stat (param)
      elif isinstance (param, TIfStat) :
         self.send_if_stat (param)
      elif isinstance (param, TCaseStat) :
         self.send_case_stat (param)
      elif isinstance (param, TWhileStat) :
         self.send_while_stat (param)
      elif isinstance (param, TRepeatStat) :
         self.send_repeat_stat (param)
      elif isinstance (param, TForStat) :
         self.send_for_stat (param)
      elif isinstance (param, TWithStat) :
         self.send_with_stat (param)
      elif isinstance (param, TRaiseStat) :
         self.send_raise_stat (param)
      elif isinstance (param, TTryStat) :
         self.send_try_stat (param)

   def send_param_ident (self, param) :
      self.send (param.name)

   def send_param_item (self, param) :
      inx = 0
      cnt = len (param.items)
      if param.mode == VarParam :
         self.send ("var")
      elif param.mode == ConstParam :
         self.send ("const")
      elif param.mode == OutParam :
         self.send ("out")
      elif param.mode == ValueParam :
         pass
      self.send_param_ident (param.items [inx])
      inx = inx + 1
      while inx < cnt :
         self.send (",")
         self.send_param_ident (param.items [inx])
         inx = inx + 1
      if param.typ != None :
         self.send (":")
         self.send_param_type (param.typ)
         if param.ini != None :
            self.send ("=")
            self.send_expr (param.ini)

   def send_formal_param_list (self, param) :
      inx = 0
      cnt = len (param.items)
      if inx < cnt :
         self.send ("(")
         self.send_param_item (param.items [inx])
         inx = inx + 1
         while inx < cnt :
            self.send (";")
            self.send_param_item (param.items [inx])
            inx = inx + 1
         self.send (")")

   def send_property_param_list (self, param) :
      inx = 0
      cnt = len (param.items)
      self.send ("[")
      self.send_param_item (param.items [inx])
      inx = inx + 1
      while inx < cnt :
         self.send (";")
         self.send_param_item (param.items [inx])
         inx = inx + 1
      self.send ("]")

   def send_class_type (self, param) :
      self.send ("class")
      if param.parent != None :
         self.send ("(")
         self.send_ifc_type (param.parent)
         if param.ifc_list != None :
            self.send (",")
            self.send_interface_sect (param.ifc_list)
         self.send (")")
      self.style_indent ()
      self.send_components_sect (param.components)
      self.style_unindent ()
      self.send ("end")

   def send_interface_type (self, param) :
      self.send ("interface")
      if param.ifc_list != None :
         self.send ("(")
         self.send_interface_sect (param.ifc_list)
         self.send (")")
      self.style_indent ()
      self.send_components_sect (param.components)
      self.style_unindent ()
      self.send ("end")

   def send_interface_sect (self, param) :
      inx = 0
      cnt = len (param.items)
      self.send_interface_item (param.items [inx])
      inx = inx + 1
      while inx < cnt :
         self.send (",")
         self.send_interface_item (param.items [inx])
         inx = inx + 1

   def send_interface_item (self, param) :
      self.send_ifc_type (param.ifc)

   def send_components_sect (self, param) :
      inx = 0
      cnt = len (param.items)
      self.send_components_first_item (param.items [inx])
      inx = inx + 1
      while inx < cnt :
         self.send_components_item (param.items [inx])
         inx = inx + 1

   def send_components_item (self, param) :
      if param.acs == PrivateAccess :
         self.send ("private")
      elif param.acs == ProtectedAccess :
         self.send ("protected")
      elif param.acs == PublicAccess :
         self.send ("public")
      elif param.acs == PublishedAccess :
         self.send ("published")
      elif param.acs == AutomatedAccess :
         self.send ("automated")
      self.send_member_sect (param.members)

   def send_components_first_item (self, param) :
      self.send_member_sect (param.members)

   def send_member_sect (self, param) :
      inx = 0
      cnt = len (param.items)
      while inx < cnt :
         self.style_new_line ()
         self.send_member_decl (param.items [inx])
         inx = inx + 1

   def send_member_decl (self, param) :
      if isinstance (param, TFieldDecl) :
         self.send_field_decl (param)
      elif isinstance (param, TProcDecl) :
         self.send_method_decl (param)
      elif isinstance (param, TPropertyDecl) :
         self.send_property_decl (param)

   def send_field_ident (self, param) :
      self.send (param.name)

   def send_field_decl (self, param) :
      inx = 0
      cnt = len (param.items)
      self.send_field_ident (param.items [inx])
      inx = inx + 1
      while inx < cnt :
         self.send (",")
         self.send_field_ident (param.items [inx])
         inx = inx + 1
      self.send (":")
      self.send_type (param.typ)
      self.send (";")

   def send_method_decl (self, param) :
      self.send_proc_head (param)
      if param.a_virtual or param.a_dynamic or param.a_override or param.a_abstract :
         if param.a_virtual :
            self.send ("virtual")
            self.send (";")
         elif param.a_dynamic :
            self.send ("dynamic")
            self.send (";")
         elif param.a_override :
            self.send ("override")
            self.send (";")
         elif param.a_abstract :
            self.send ("abstract")
            self.send (";")

   def send_property_decl (self, param) :
      self.send ("property")
      self.send (param.name)
      if param.param_list != None :
         self.send_property_param_list (param.param_list)
      if param.typ != None :
         self.send (":")
         self.send_result_type (param.typ)
      if param.a_read != None :
         self.send ("read")
         self.send_expr (param.a_read)
      if param.a_write != None :
         self.send ("write")
         self.send_expr (param.a_write)
      if param.a_stored :
         self.send ("stored")
      if param.a_default :
         self.send ("default")
      if param.a_nodefault :
         self.send ("nodefault")
      if param.a_implements != None :
         self.send ("implements")
         self.send_interface_sect (param.a_implements)
      if param.a_def_array :
         self.send (";")
         self.send ("default")
      self.send (";")

   def send_enum_type (self, param) :
      self.send ("(")
      self.send_enum_sect (param.elements)
      self.send (")")

   def send_enum_sect (self, param) :
      inx = 0
      cnt = len (param.items)
      self.send_enum_item (param.items [inx])
      inx = inx + 1
      while inx < cnt :
         self.send (",")
         self.send_enum_item (param.items [inx])
         inx = inx + 1

   def send_enum_item (self, param) :
      self.send (param.name)

   def send_string_type (self, param) :
      self.send ("string")
      if param.lim != None :
         self.send ("[")
         self.send_expr (param.lim)
         self.send ("]")

   def send_array_type (self, param) :
      self.send ("array")
      if param.index_list != None :
         self.send ("[")
         self.send_index_type_sect (param.index_list)
         self.send ("]")
      self.send ("of")
      self.send_type (param.elem)

   def send_index_type_sect (self, param) :
      inx = 0
      cnt = len (param.items)
      self.send_index_type_item (param.items [inx])
      inx = inx + 1
      while inx < cnt :
         self.send (",")
         self.send_index_type_item (param.items [inx])
         inx = inx + 1

   def send_index_type_item (self, param) :
      self.send_type (param.index)

   def send_record_type (self, param) :
      if param.a_packed :
         self.send ("packed")
      self.send ("record")
      self.send_field_sect (param.fields)
      self.send ("end")

   def send_field_sect (self, param) :
      inx = 0
      cnt = len (param.items)
      while inx < cnt :
         self.send_field_decl (param.items [inx])
         inx = inx + 1

   def send_pointer_type (self, param) :
      self.send ("^")
      self.send_type (param.elem)

   def send_set_type (self, param) :
      self.send ("set")
      self.send ("of")
      self.send_type (param.elem)

   def send_file_type (self, param) :
      self.send ("file")
      if param.elem != None :
         self.send ("of")
         self.send_type (param.elem)

   def send_class_of_type (self, param) :
      self.send ("class")
      self.send ("of")
      self.send_type (param.elem)

   def send_proc_type (self, param) :
      if param.style == ProcedureStyle :
         self.send ("procedure")
      elif param.style == FunctionStyle :
         self.send ("function")
      self.send_formal_param_list (param.param_list)
      if param.answer != None :
         self.send (":")
         self.send_result_type (param.answer)
      if param.of_object :
         self.send ("of")
         self.send ("object")
      if param.call_conv == RegisterCall or param.call_conv == PascalCall or param.call_conv == CdeclCall or param.call_conv == StdcallCall or param.call_conv == SafecallCall :
         if param.call_conv == RegisterCall :
            self.send ("register")
         elif param.call_conv == PascalCall :
            self.send ("pascal")
         elif param.call_conv == CdeclCall :
            self.send ("cdecl")
         elif param.call_conv == StdcallCall :
            self.send ("stdcall")
         elif param.call_conv == SafecallCall :
            self.send ("safecall")

   def send_range_type (self, param) :
      self.send_simple_expr (param.low)
      self.send ("..")
      self.send_simple_expr (param.high)

   def send_alias_type (self, param) :
      self.send_qualified_name (param.alias_name)

   def send_type (self, param) :
      if isinstance (param, TStringType) :
         self.send_string_type (param)
      elif isinstance (param, TArrayType) :
         self.send_array_type (param)
      elif isinstance (param, TSetType) :
         self.send_set_type (param)
      elif isinstance (param, TFileType) :
         self.send_file_type (param)
      elif isinstance (param, TRecordType) :
         self.send_record_type (param)
      elif isinstance (param, TClassType) :
         self.send_class_type (param)
      elif isinstance (param, TClassOfType) :
         self.send_class_of_type (param)
      elif isinstance (param, TInterfaceType) :
         self.send_interface_type (param)
      elif isinstance (param, TProcType) :
         self.send_proc_type (param)
      elif isinstance (param, TPointerType) :
         self.send_pointer_type (param)
      elif isinstance (param, TSubrangeType) :
         self.send_range_type (param)
      elif isinstance (param, TEnumType) :
         self.send_enum_type (param)
      elif isinstance (param, TAliasType) :
         self.send_alias_type (param)

   def send_label_decl (self, param) :
      self.send_label_ident (param.name)

   def send_label_sect (self, param) :
      inx = 0
      cnt = len (param.items)
      self.send ("label")
      self.send_label_decl (param.items [inx])
      inx = inx + 1
      while inx < cnt :
         self.send (",")
         self.send_label_decl (param.items [inx])
         inx = inx + 1
      self.send (";")

   def send_const_decl (self, param) :
      self.send (param.name)
      if param.typ != None :
         self.send (":")
         self.send_type (param.typ)
      self.send ("=")
      self.send_expr (param.val)
      self.send (";")

   def send_const_sect (self, param) :
      inx = 0
      cnt = len (param.items)
      self.send ("const")
      self.send_const_decl (param.items [inx])
      inx = inx + 1
      while inx < cnt :
         self.send_const_decl (param.items [inx])
         inx = inx + 1

   def send_type_decl (self, param) :
      self.send (param.name)
      self.send ("=")
      self.send_type (param.typ)
      self.send (";")

   def send_type_sect (self, param) :
      inx = 0
      cnt = len (param.items)
      self.send ("type")
      self.send_type_decl (param.items [inx])
      inx = inx + 1
      while inx < cnt :
         self.send_type_decl (param.items [inx])
         inx = inx + 1

   def send_var_item (self, param) :
      self.send (param.name)

   def send_var_decl (self, param) :
      inx = 0
      cnt = len (param.items)
      self.send_var_item (param.items [inx])
      inx = inx + 1
      while inx < cnt :
         self.send (",")
         self.send_var_item (param.items [inx])
         inx = inx + 1
      self.send (":")
      self.send_type (param.typ)
      if param.ini != None :
         self.send ("=")
         self.send_expr (param.ini)
      self.send (";")

   def send_var_sect (self, param) :
      inx = 0
      cnt = len (param.items)
      self.send ("var")
      self.style_indent ()
      self.style_new_line ()
      self.send_var_decl (param.items [inx])
      inx = inx + 1
      while inx < cnt :
         self.style_new_line ()
         self.send_var_decl (param.items [inx])
         inx = inx + 1
      self.style_unindent ()

   def send_proc_head (self, param) :
      if param.a_static :
         self.send ("class")
      if param.style == ProcedureStyle :
         self.send ("procedure")
      elif param.style == FunctionStyle :
         self.send ("function")
      elif param.style == ConstructorStyle :
         self.send ("constructor")
      elif param.style == DestructorStyle :
         self.send ("destructor")
      self.send_qualified_name (param.proc_name)
      self.send_formal_param_list (param.param_list)
      if param.answer != None :
         self.send (":")
         self.send_result_type (param.answer)
      self.send (";")

   def send_proc_decl (self, param) :
      self.send_proc_head (param)
      if param.a_forward :
         self.send ("forward")
      elif param.external_spec :
         self.send_proc_external (param)
      elif param.local != None :
         if param.a_inline :
            self.send ("inline")
            self.send (";")
         self.send_decl_part (param.local)
         self.style_new_line ()
         self.send ("begin")
         self.send_stat_list (param.body)
         self.send ("end")
      self.send (";")
      self.style_empty_line ()

   def send_proc_external (self, param) :
      self.send ("external")
      if param.a_lib != None :
         self.send_expr (param.a_lib)
      self.send (";")
      self.style_empty_line ()

   def send_proc_intf_decl (self, param) :
      self.send_proc_head (param)
      if param.a_inline :
         self.send ("inline")
         self.send (";")
      if param.external_spec :
         self.send_proc_external (param)

   def send_intf_decl (self, param) :
      if isinstance (param, TConstSect) :
         self.send_const_sect (param)
      elif isinstance (param, TTypeSect) :
         self.send_type_sect (param)
      elif isinstance (param, TVarSect) :
         self.send_var_sect (param)
      elif isinstance (param, TProcDecl) :
         self.send_proc_intf_decl (param)

   def send_intf_decl_part (self, param) :
      inx = 0
      cnt = len (param.items)
      while inx < cnt :
         self.style_new_line ()
         self.send_intf_decl (param.items [inx])
         inx = inx + 1

   def send_decl (self, param) :
      if isinstance (param, TLabelSect) :
         self.send_label_sect (param)
      elif isinstance (param, TConstSect) :
         self.send_const_sect (param)
      elif isinstance (param, TTypeSect) :
         self.send_type_sect (param)
      elif isinstance (param, TVarSect) :
         self.send_var_sect (param)
      elif isinstance (param, TProcDecl) :
         self.send_proc_decl (param)

   def send_decl_part (self, param) :
      inx = 0
      cnt = len (param.items)
      while inx < cnt :
         self.style_new_line ()
         self.send_decl (param.items [inx])
         inx = inx + 1

   def send_import_item (self, param) :
      self.send (param.name)
      if param.path != "" :
         self.send ("in")
         self.sendStr (param.path)

   def send_import_sect (self, param) :
      inx = 0
      cnt = len (param.items)
      if inx < cnt :
         self.style_empty_line ()
         self.send ("uses")
         self.send_import_item (param.items [inx])
         inx = inx + 1
         while inx < cnt :
            self.send (",")
            self.send_import_item (param.items [inx])
            inx = inx + 1
         self.send (";")
         self.style_empty_line ()

   def send_unit_decl (self, param) :
      self.send ("unit")
      self.send (param.name)
      self.send (";")
      self.style_empty_line ()
      self.send ("interface")
      self.style_empty_line ()
      self.send_import_sect (param.intf_imports)
      self.send_intf_decl_part (param.intf_decl)
      self.style_empty_line ()
      self.send ("implementation")
      self.style_empty_line ()
      self.send_import_sect (param.impl_imports)
      self.send_decl_part (param.impl_decl)
      if param.no_begin or param.init != None :
         if param.no_begin :
            if param.init != None :
               self.send ("initialization")
               self.send_stat_list (param.init)
            if param.finish != None :
               self.send ("finalization")
               self.send_stat_list (param.finish)
         elif param.init != None :
            self.send ("begin")
            self.send_stat_list (param.init)
      self.send ("end")
      self.style_no_space ()
      self.send (".")

   def send_program_decl (self, param) :
      self.send ("program")
      self.send (param.name)
      self.send (";")
      self.style_empty_line ()
      self.send_import_sect (param.impl_imports)
      self.send_decl_part (param.impl_decl)
      self.style_new_line ()
      self.send ("begin")
      self.send_stat_list (param.init)
      self.send ("end")
      self.style_no_space ()
      self.send (".")

   def send_library_decl (self, param) :
      self.send ("library")
      self.send (param.name)
      self.send (";")
      self.style_empty_line ()
      self.send_import_sect (param.impl_imports)
      self.send_decl_part (param.impl_decl)
      self.style_new_line ()
      self.send ("begin")
      self.send_stat_list (param.init)
      self.send ("end")
      self.style_no_space ()
      self.send (".")

   def send_module_decl (self, param) :
      if isinstance (param, TUnitModule) :
         self.send_unit_decl (param)
      elif isinstance (param, TProgramModule) :
         self.send_program_decl (param)
      elif isinstance (param, TLibraryModule) :
         self.send_library_decl (param)

