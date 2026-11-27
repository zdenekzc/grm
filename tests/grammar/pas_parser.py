
from lexer import Lexer

class Parser (Lexer) :
   def parse_label_ident (self) :
      result = TLabelIdent ()
      self.storeLocation (result)
      result.id = self.readIdentifier ()
      return result

   def parse_qualified_name (self) :
      result = TQualName ()
      self.storeLocation (result)
      result.id = self.readIdentifier ()
      while self.token == self.DOT :
         result.items.append (self.parse_cont_name ())
      return result

   def parse_cont_name (self) :
      result = TContName ()
      self.storeLocation (result)
      self.checkToken (self.DOT)
      result.id = self.readIdentifier ()
      return result

   def parse_ifc_type (self) :
      result = self.parse_simple_alias_type ()
      return result

   def parse_param_type (self) :
      if self.token == self.identifier :
         result = self.parse_simple_alias_type ()
      elif self.token == self.keyword_string :
         result = self.parse_simple_string_type ()
      elif self.token == self.keyword_file :
         result = self.parse_simple_file_type ()
      else :
         self.error ("Unexpected token")
      return result

   def parse_result_type (self) :
      if self.token == self.identifier :
         result = self.parse_simple_alias_type ()
      elif self.token == self.keyword_string :
         result = self.parse_simple_string_type ()
      else :
         self.error ("Unexpected token")
      return result

   def parse_simple_alias_type (self) :
      result = TAliasType ()
      self.storeLocation (result)
      result.alias_name = self.parse_qualified_name ()
      return result

   def parse_simple_string_type (self) :
      result = TStringType ()
      self.storeLocation (result)
      self.checkToken (self.keyword_string)
      return result

   def parse_simple_file_type (self) :
      result = TFileType ()
      self.storeLocation (result)
      self.checkToken (self.keyword_file)
      return result

   def parse_index_expr_item (self) :
      result = TInxItem ()
      self.storeLocation (result)
      result.ref = self.parse_expr ()
      return result

   def parse_index_expr_list (self) :
      result = TInxList ()
      self.storeLocation (result)
      result.items.append (self.parse_index_expr_item ())
      while self.token == self.COMMA :
         self.checkToken (self.COMMA)
         result.items.append (self.parse_index_expr_item ())
      return result

   def parse_arg_item (self) :
      result = TArgItem ()
      self.storeLocation (result)
      result.value = self.parse_expr ()
      if self.token == self.COLON :
         self.checkToken (self.COLON)
         result.width = self.parse_expr ()
         if self.token == self.COLON :
            self.checkToken (self.COLON)
            result.digits = self.parse_expr ()
      return result

   def parse_arg_list (self) :
      result = TArgSect ()
      self.storeLocation (result)
      result.items.append (self.parse_arg_item ())
      while self.token == self.COMMA :
         self.checkToken (self.COMMA)
         result.items.append (self.parse_arg_item ())
      return result

   def parse_elem_sect (self) :
      result = TElemSect ()
      self.storeLocation (result)
      result.items.append (self.parse_elem_item ())
      while self.token == self.COMMA :
         self.checkToken (self.COMMA)
         result.items.append (self.parse_elem_item ())
      return result

   def parse_elem_item (self) :
      result = TElemItem ()
      self.storeLocation (result)
      result.low = self.parse_expr ()
      if self.token == self.RANGE :
         self.checkToken (self.RANGE)
         result.high = self.parse_expr ()
      return result

   def parse_struct_item (self) :
      result = TStructSect ()
      self.storeLocation (result)
      if self.token == self.identifier :
         result.name = self.readIdentifier ()
         self.checkToken (self.COLON)
      result.value = self.parse_expr ()
      return result

   def parse_struct_sect (self) :
      result = TStructSect ()
      self.storeLocation (result)
      result.items.append (self.parse_struct_item ())
      if self.token == self.COMMA or self.token == self.SEMICOLON :
         if self.token == self.COMMA :
            self.checkToken (self.COMMA)
            result.items.append (self.parse_struct_item ())
            while self.token == self.COMMA :
               self.checkToken (self.COMMA)
               result.items.append (self.parse_struct_item ())
         elif self.token == self.SEMICOLON :
            self.checkToken (self.SEMICOLON)
            result.items.append (self.parse_struct_item ())
            while self.token == self.SEMICOLON :
               self.checkToken (self.SEMICOLON)
               result.items.append (self.parse_struct_item ())
         else :
            self.error ("Unexpected token")
      return result

   def parse_ident_expr (self) :
      result = TIdentExpr ()
      self.storeLocation (result)
      result.name = self.readIdentifier ()
      self.on_ident_expr (result)
      return result

   def parse_int_value_expr (self) :
      result = TIntValueExpr ()
      self.storeLocation (result)
      result.value = self.readNumber ()
      return result

   def parse_float_value_expr (self) :
      result = TFltValueExpr ()
      self.storeLocation (result)
      result.value = self.readReal ()
      return result

   def parse_string_value_expr (self) :
      result = TStrValueExpr ()
      self.storeLocation (result)
      result.value = self.readString ()
      return result

   def parse_nil_expr (self) :
      result = TNilExpr ()
      self.storeLocation (result)
      self.checkToken (self.keyword_nil)
      return result

   def parse_sub_expr (self) :
      result = TStructExpr ()
      self.storeLocation (result)
      self.checkToken (self.LPAREN)
      result.value = self.parse_expr ()
      self.checkToken (self.RPAREN)
      return result

   def parse_not_expr (self) :
      result = TNotExpr ()
      self.storeLocation (result)
      self.checkToken (self.keyword_not)
      result.param = self.parse_factor ()
      return result

   def parse_plus_expr (self) :
      result = TPlusExpr ()
      self.storeLocation (result)
      self.checkToken (self.PLUS)
      result.param = self.parse_factor ()
      return result

   def parse_minus_expr (self) :
      result = TMinusExpr ()
      self.storeLocation (result)
      self.checkToken (self.MINUS)
      result.param = self.parse_factor ()
      return result

   def parse_adr_expr (self) :
      result = TAdrExpr ()
      self.storeLocation (result)
      self.checkToken (self.ADDRESS)
      result.param = self.parse_factor ()
      return result

   def parse_set_expr (self) :
      result = TSetExpr ()
      self.storeLocation (result)
      self.checkToken (self.LBRACKET)
      result.list = self.parse_elem_sect ()
      self.checkToken (self.RBRACKET)
      return result

   def parse_super_expr (self) :
      result = TSuperExpr ()
      self.storeLocation (result)
      self.checkToken (self.keyword_inherited)
      result.name = self.readIdentifier ()
      return result

   def parse_string_type_expr (self) :
      result = TStringExpr ()
      self.storeLocation (result)
      self.checkToken (self.keyword_string)
      self.checkToken (self.LPAREN)
      result.param = self.parse_expr ()
      self.checkToken (self.RPAREN)
      return result

   def parse_variable (self) :
      if self.token == self.identifier :
         result = self.parse_ident_expr ()
      elif self.token == self.LPAREN :
         result = self.parse_sub_expr ()
      elif self.token == self.keyword_inherited :
         result = self.parse_super_expr ()
      else :
         self.error ("Unexpected token")
      return result

   def parse_reference (self) :
      result = self.parse_variable ()
      while self.token == self.LBRACKET or self.token == self.LPAREN or self.token == self.ARROW or self.token == self.DOT :
         if self.token == self.LBRACKET :
            result = self.parse_index_expr (result)
         elif self.token == self.LPAREN :
            result = self.parse_call_expr (result)
         elif self.token == self.ARROW :
            result = self.parse_deref_expr (result)
         elif self.token == self.DOT :
            result = self.parse_field_expr (result)
         else :
            self.error ("Unexpected token")
      return result

   def parse_index_expr (self, store) :
      result = TIndexExpr ()
      self.storeLocation (result)
      result.left = store
      self.checkToken (self.LBRACKET)
      result.list = self.parse_index_expr_list ()
      self.checkToken (self.RBRACKET)
      return result

   def parse_call_expr (self, store) :
      result = TCallExpr ()
      self.storeLocation (result)
      result.func = store
      self.checkToken (self.LPAREN)
      result.list = self.parse_arg_list ()
      self.checkToken (self.RPAREN)
      return result

   def parse_deref_expr (self, store) :
      result = TDerefExpr ()
      self.storeLocation (result)
      result.param = store
      self.checkToken (self.ARROW)
      return result

   def parse_field_expr (self, store) :
      result = TFieldExpr ()
      self.storeLocation (result)
      result.param = store
      self.checkToken (self.DOT)
      result.name = self.readIdentifier ()
      self.on_field_expr (result)
      return result

   def parse_factor (self) :
      if self.token == self.number :
         result = self.parse_int_value_expr ()
      elif self.token == self.real_number :
         result = self.parse_float_value_expr ()
      elif self.token == self.string_literal :
         result = self.parse_string_value_expr ()
      elif self.token == self.keyword_not :
         result = self.parse_not_expr ()
      elif self.token == self.PLUS :
         result = self.parse_plus_expr ()
      elif self.token == self.MINUS :
         result = self.parse_minus_expr ()
      elif self.token == self.ADDRESS :
         result = self.parse_adr_expr ()
      elif self.token == self.keyword_nil :
         result = self.parse_nil_expr ()
      elif self.token == self.LBRACKET :
         result = self.parse_set_expr ()
      elif self.token == self.keyword_string and self.test_1 () :
         result = self.parse_string_type_expr ()
      elif self.token == self.identifier or self.token == self.LPAREN or self.token == self.keyword_inherited :
         result = self.parse_reference ()
      else :
         self.error ("Unexpected token")
      return result

   def parse_term (self) :
      result = self.parse_factor ()
      while self.token == self.STAR or self.token == self.SLASH or self.token == self.keyword_div or self.token == self.keyword_mod or self.token == self.keyword_shl or self.token == self.keyword_shr or self.token == self.keyword_and or self.token == self.keyword_as :
         store = result
         result = TTermExpr ()
         self.storeLocation (result)
         result.left = store
         if self.token == self.STAR :
            self.checkToken (self.STAR)
            result.fce = MulExp
         elif self.token == self.SLASH :
            self.checkToken (self.SLASH)
            result.fce = RDivExp
         elif self.token == self.keyword_div :
            self.checkToken (self.keyword_div)
            result.fce = DivExp
         elif self.token == self.keyword_mod :
            self.checkToken (self.keyword_mod)
            result.fce = ModExp
         elif self.token == self.keyword_shl :
            self.checkToken (self.keyword_shl)
            result.fce = ShlExp
         elif self.token == self.keyword_shr :
            self.checkToken (self.keyword_shr)
            result.fce = ShrExp
         elif self.token == self.keyword_and :
            self.checkToken (self.keyword_and)
            result.fce = AndExp
         elif self.token == self.keyword_as :
            self.checkToken (self.keyword_as)
            result.fce = AsExp
         else :
            self.error ("Unexpected token")
         result.right = self.parse_factor ()
      return result

   def parse_simple_expr (self) :
      result = self.parse_term ()
      while self.token == self.PLUS or self.token == self.MINUS or self.token == self.keyword_or or self.token == self.keyword_xor :
         store = result
         result = TSimpleExpr ()
         self.storeLocation (result)
         result.left = store
         if self.token == self.PLUS :
            self.checkToken (self.PLUS)
            result.fce = AddExp
         elif self.token == self.MINUS :
            self.checkToken (self.MINUS)
            result.fce = SubExp
         elif self.token == self.keyword_or :
            self.checkToken (self.keyword_or)
            result.fce = OrExp
         elif self.token == self.keyword_xor :
            self.checkToken (self.keyword_xor)
            result.fce = XorExp
         else :
            self.error ("Unexpected token")
         result.right = self.parse_term ()
      return result

   def parse_expr (self) :
      result = self.parse_simple_expr ()
      if self.token == self.EQUAL or self.token == self.UNEQUAL or self.token == self.LESS or self.token == self.GREATER or self.token == self.LESS_OR_EQUAL or self.token == self.GREATER_OR_EQUAL or self.token == self.keyword_in or self.token == self.keyword_is :
         store = result
         result = TCompleteExpr ()
         self.storeLocation (result)
         result.left = store
         if self.token == self.EQUAL :
            self.checkToken (self.EQUAL)
            result.fce = EqExp
         elif self.token == self.UNEQUAL :
            self.checkToken (self.UNEQUAL)
            result.fce = NeExp
         elif self.token == self.LESS :
            self.checkToken (self.LESS)
            result.fce = LtExp
         elif self.token == self.GREATER :
            self.checkToken (self.GREATER)
            result.fce = GtExp
         elif self.token == self.LESS_OR_EQUAL :
            self.checkToken (self.LESS_OR_EQUAL)
            result.fce = LeExp
         elif self.token == self.GREATER_OR_EQUAL :
            self.checkToken (self.GREATER_OR_EQUAL)
            result.fce = GeExp
         elif self.token == self.keyword_in :
            self.checkToken (self.keyword_in)
            result.fce = InExp
         elif self.token == self.keyword_is :
            self.checkToken (self.keyword_is)
            result.fce = IsExp
         else :
            self.error ("Unexpected token")
         result.right = self.parse_simple_expr ()
      return result

   def parse_goto_stat (self) :
      result = TGotoStat ()
      self.storeLocation (result)
      self.checkToken (self.keyword_goto)
      result.goto_lab = self.parse_label_ident ()
      return result

   def parse_begin_stat (self) :
      result = TBlockStat ()
      self.storeLocation (result)
      self.checkToken (self.keyword_begin)
      result.body_seq = self.parse_stat_list ()
      self.checkToken (self.keyword_end)
      return result

   def parse_stat_list (self) :
      result = TStatSeq ()
      self.storeLocation (result)
      result.items.append (self.parse_stat ())
      while self.token == self.SEMICOLON :
         self.checkToken (self.SEMICOLON)
         result.items.append (self.parse_stat ())
      return result

   def parse_inner_stat (self) :
      result = self.parse_stat ()
      return result

   def parse_if_stat (self) :
      result = TIfStat ()
      self.storeLocation (result)
      self.checkToken (self.keyword_if)
      result.cond_expr = self.parse_expr ()
      self.checkToken (self.keyword_then)
      result.then_stat = self.parse_inner_stat ()
      if self.token == self.keyword_else :
         self.checkToken (self.keyword_else)
         result.else_stat = self.parse_inner_stat ()
      return result

   def parse_case_stat (self) :
      result = TCaseStat ()
      self.storeLocation (result)
      self.checkToken (self.keyword_case)
      result.case_expr = self.parse_expr ()
      self.checkToken (self.keyword_of)
      result.case_list = self.parse_case_sect ()
      if self.token == self.keyword_else :
         self.checkToken (self.keyword_else)
         result.else_seq = self.parse_stat_list ()
      self.checkToken (self.keyword_end)
      return result

   def parse_case_sect (self) :
      result = TCaseSect ()
      self.storeLocation (result)
      result.items.append (self.parse_case_item ())
      while self.token == self.SEMICOLON :
         self.checkToken (self.SEMICOLON)
         result.items.append (self.parse_case_item ())
      return result

   def parse_case_item (self) :
      result = TCaseItem ()
      self.storeLocation (result)
      result.sel_list = self.parse_elem_sect ()
      self.checkToken (self.COLON)
      result.sel_stat = self.parse_inner_stat ()
      return result

   def parse_while_stat (self) :
      result = TWhileStat ()
      self.storeLocation (result)
      self.checkToken (self.keyword_while)
      result.cond_expr = self.parse_expr ()
      self.checkToken (self.keyword_do)
      result.body_stat = self.parse_inner_stat ()
      return result

   def parse_repeat_stat (self) :
      result = TRepeatStat ()
      self.storeLocation (result)
      self.checkToken (self.keyword_repeat)
      result.body_seq = self.parse_stat_list ()
      self.checkToken (self.keyword_until)
      result.until_expr = self.parse_expr ()
      return result

   def parse_for_stat (self) :
      result = TForStat ()
      self.storeLocation (result)
      self.checkToken (self.keyword_for)
      result.var_expr = self.parse_variable ()
      self.checkToken (self.ASSIGN)
      result.from_expr = self.parse_expr ()
      if self.token == self.keyword_to :
         self.checkToken (self.keyword_to)
         result.incr = True
      elif self.token == self.keyword_downto :
         self.checkToken (self.keyword_downto)
         result.incr = False
      else :
         self.error ("Unexpected token")
      result.to_expr = self.parse_expr ()
      self.checkToken (self.keyword_do)
      result.body_stat = self.parse_inner_stat ()
      return result

   def parse_with_stat (self) :
      result = TWithStat ()
      self.storeLocation (result)
      self.checkToken (self.keyword_with)
      result.with_list = self.parse_with_sect ()
      self.checkToken (self.keyword_do)
      result.body_stat = self.parse_inner_stat ()
      return result

   def parse_with_sect (self) :
      result = TWithSect ()
      self.storeLocation (result)
      result.items.append (self.parse_with_item ())
      while self.token == self.COMMA :
         self.checkToken (self.COMMA)
         result.items.append (self.parse_with_item ())
      return result

   def parse_with_item (self) :
      result = TWithItem ()
      self.storeLocation (result)
      result.expr = self.parse_variable ()
      return result

   def parse_raise_stat (self) :
      result = TRaiseStat ()
      self.storeLocation (result)
      self.checkToken (self.keyword_raise)
      if self.set_4 & 1 << self.token :
         result.raise_expr = self.parse_expr ()
      return result

   def parse_try_stat (self) :
      result = TTryStat ()
      self.storeLocation (result)
      self.checkToken (self.keyword_try)
      result.body_seq = self.parse_stat_list ()
      if self.token == self.keyword_finally :
         result.finally_branch = self.parse_finally_part ()
      elif self.token == self.keyword_except :
         result.except_branch = self.parse_except_part ()
      else :
         self.error ("Unexpected token")
      self.checkToken (self.keyword_end)
      return result

   def parse_finally_part (self) :
      result = TFinallyPart ()
      self.storeLocation (result)
      self.checkToken (self.keyword_finally)
      result.finally_seq = self.parse_stat_list ()
      return result

   def parse_except_part (self) :
      result = TExceptPart ()
      self.storeLocation (result)
      self.checkToken (self.keyword_except)
      if self.token == self.keyword_on :
         result.on_list = self.parse_on_sect ()
         if self.token == self.keyword_else :
            self.checkToken (self.keyword_else)
            result.else_seq = self.parse_stat_list ()
      else :
         result.else_seq = self.parse_stat_list ()
      return result

   def parse_on_sect (self) :
      result = TOnSect ()
      self.storeLocation (result)
      result.items.append (self.parse_on_item ())
      while self.token == self.SEMICOLON :
         self.checkToken (self.SEMICOLON)
         result.items.append (self.parse_on_item ())
      if self.token == self.SEMICOLON :
         self.checkToken (self.SEMICOLON)
         result.semicolon = True
      return result

   def parse_on_item (self) :
      result = TOnItem ()
      self.storeLocation (result)
      self.checkToken (self.keyword_on)
      if self.token == self.identifier :
         result.on_ident = self.readIdentifier ()
         self.checkToken (self.COLON)
      result.on_type = self.parse_type ()
      self.checkToken (self.keyword_do)
      result.body_stat = self.parse_inner_stat ()
      return result

   def parse_empty_stat (self) :
      result = TEmptyStat ()
      self.storeLocation (result)
      return result

   def parse_simple_stat (self) :
      result = self.parse_expr ()
      if self.token == self.ASSIGN :
         result = self.parse_assign_stat (result)
      else :
         result = self.parse_call_stat (result)
      return result

   def parse_assign_stat (self, store) :
      result = TAssignStat ()
      self.storeLocation (result)
      result.left_expr = store
      self.checkToken (self.ASSIGN)
      result.right_expr = self.parse_expr ()
      return result

   def parse_call_stat (self, store) :
      result = TCallStat ()
      self.storeLocation (result)
      result.call_expr = store
      return result

   def parse_labeled_stat (self) :
      result = TLabeledTStat ()
      self.storeLocation (result)
      result.lab = self.parse_label_ident ()
      self.checkToken (self.COLON)
      result.body = self.parse_stat ()
      return result

   def parse_stat (self) :
      if self.token == self.identifier and self.test_2 () :
         result = self.parse_labeled_stat ()
      elif self.set_4 & 1 << self.token :
         result = self.parse_simple_stat ()
      elif self.token == self.keyword_goto :
         result = self.parse_goto_stat ()
      elif self.token == self.keyword_begin :
         result = self.parse_begin_stat ()
      elif self.token == self.keyword_if :
         result = self.parse_if_stat ()
      elif self.token == self.keyword_case :
         result = self.parse_case_stat ()
      elif self.token == self.keyword_while :
         result = self.parse_while_stat ()
      elif self.token == self.keyword_repeat :
         result = self.parse_repeat_stat ()
      elif self.token == self.keyword_for :
         result = self.parse_for_stat ()
      elif self.token == self.keyword_with :
         result = self.parse_with_stat ()
      elif self.token == self.keyword_raise :
         result = self.parse_raise_stat ()
      elif self.token == self.keyword_try :
         result = self.parse_try_stat ()
      else :
         result = self.parse_empty_stat ()
      return result

   def parse_param_ident (self) :
      result = TParamIdent ()
      self.storeLocation (result)
      result.name = self.readIdentifier ()
      self.on_param (result)
      return result

   def parse_param_item (self) :
      result = TParamItem ()
      self.storeLocation (result)
      if self.token == self.keyword_var :
         self.checkToken (self.keyword_var)
         result.mode = VarParam
      elif self.token == self.keyword_const :
         self.checkToken (self.keyword_const)
         result.mode = ConstParam
      elif self.token == self.keyword_out :
         self.checkToken (self.keyword_out)
         result.mode = OutParam
      else :
         result.mode = ValueParam
      result.items.append (self.parse_param_ident ())
      while self.token == self.COMMA :
         self.checkToken (self.COMMA)
         result.items.append (self.parse_param_ident ())
      if self.token == self.COLON :
         self.checkToken (self.COLON)
         result.typ = self.parse_param_type ()
         if self.token == self.EQUAL :
            self.checkToken (self.EQUAL)
            result.ini = self.parse_expr ()
      self.add_param (result)
      return result

   def parse_formal_param_list (self) :
      result = TParamSect ()
      self.storeLocation (result)
      if self.token == self.LPAREN :
         self.checkToken (self.LPAREN)
         result.items.append (self.parse_param_item ())
         while self.token == self.SEMICOLON :
            self.checkToken (self.SEMICOLON)
            result.items.append (self.parse_param_item ())
         self.checkToken (self.RPAREN)
      return result

   def parse_property_param_list (self) :
      result = TParamSect ()
      self.storeLocation (result)
      self.checkToken (self.LBRACKET)
      result.items.append (self.parse_param_item ())
      while self.token == self.SEMICOLON :
         self.checkToken (self.SEMICOLON)
         result.items.append (self.parse_param_item ())
      self.checkToken (self.RBRACKET)
      return result

   def parse_class_type (self) :
      result = TClassType ()
      self.storeLocation (result)
      self.open_class (result)
      self.checkToken (self.keyword_class)
      if self.token == self.LPAREN :
         self.checkToken (self.LPAREN)
         result.parent = self.parse_ifc_type ()
         if self.token == self.COMMA :
            self.checkToken (self.COMMA)
            result.ifc_list = self.parse_interface_sect ()
         self.checkToken (self.RPAREN)
      result.components = self.parse_components_sect ()
      self.checkToken (self.keyword_end)
      self.close_class (result)
      return result

   def parse_interface_type (self) :
      result = TInterfaceType ()
      self.storeLocation (result)
      self.open_interface (result)
      self.checkToken (self.keyword_interface)
      if self.token == self.LPAREN :
         self.checkToken (self.LPAREN)
         result.ifc_list = self.parse_interface_sect ()
         self.checkToken (self.RPAREN)
      result.components = self.parse_components_sect ()
      self.checkToken (self.keyword_end)
      self.close_interface (result)
      return result

   def parse_interface_sect (self) :
      result = TInterfaceSect ()
      self.storeLocation (result)
      result.items.append (self.parse_interface_item ())
      while self.token == self.COMMA :
         self.checkToken (self.COMMA)
         result.items.append (self.parse_interface_item ())
      return result

   def parse_interface_item (self) :
      result = TIntefaceItem ()
      self.storeLocation (result)
      result.ifc = self.parse_ifc_type ()
      return result

   def parse_components_sect (self) :
      result = TComponetsSect ()
      self.storeLocation (result)
      result.items.append (self.parse_components_first_item ())
      while self.set_6 & 1 << self.token :
         result.items.append (self.parse_components_item ())
      return result

   def parse_components_item (self) :
      result = TComponentsItem ()
      self.storeLocation (result)
      if self.token == self.keyword_private :
         self.checkToken (self.keyword_private)
         result.acs = PrivateAccess
      elif self.token == self.keyword_protected :
         self.checkToken (self.keyword_protected)
         result.acs = ProtectedAccess
      elif self.token == self.keyword_public :
         self.checkToken (self.keyword_public)
         result.acs = PublicAccess
      elif self.token == self.keyword_published :
         self.checkToken (self.keyword_published)
         result.acs = PublishedAccess
      elif self.token == self.keyword_automated :
         self.checkToken (self.keyword_automated)
         result.acs = AutomatedAccess
      else :
         self.error ("Unexpected token")
      result.members = self.parse_member_sect ()
      return result

   def parse_components_first_item (self) :
      result = TComponentsItem ()
      self.storeLocation (result)
      result.acs = PublicAccess
      result.members = self.parse_member_sect ()
      return result

   def parse_member_sect (self) :
      result = TDeclGroup ()
      self.storeLocation (result)
      while self.set_7 & 1 << self.token :
         result.items.append (self.parse_member_decl ())
      return result

   def parse_member_decl (self) :
      if self.token == self.identifier :
         result = self.parse_field_decl ()
      elif self.set_8 & 1 << self.token :
         result = self.parse_method_decl ()
      elif self.token == self.keyword_property :
         result = self.parse_property_decl ()
      else :
         self.error ("Unexpected token")
      return result

   def parse_field_ident (self) :
      result = TFieldItem ()
      self.storeLocation (result)
      result.name = self.readIdentifier ()
      self.on_field (result)
      return result

   def parse_field_decl (self) :
      result = TFieldDecl ()
      self.storeLocation (result)
      result.items.append (self.parse_field_ident ())
      while self.token == self.COMMA :
         self.checkToken (self.COMMA)
         result.items.append (self.parse_field_ident ())
      self.checkToken (self.COLON)
      result.typ = self.parse_type ()
      self.checkToken (self.SEMICOLON)
      self.add_field (result)
      return result

   def parse_method_decl (self) :
      result = TProcDecl ()
      self.storeLocation (result)
      self.open_proc (result)
      self.parse_proc_head (result)
      while self.token == self.keyword_virtual or self.token == self.keyword_dynamic or self.token == self.keyword_override or self.token == self.keyword_abstract :
         if self.token == self.keyword_virtual :
            self.checkToken (self.keyword_virtual)
            result.a_virtual = True
            self.checkToken (self.SEMICOLON)
         elif self.token == self.keyword_dynamic :
            self.checkToken (self.keyword_dynamic)
            result.a_dynamic = True
            self.checkToken (self.SEMICOLON)
         elif self.token == self.keyword_override :
            self.checkToken (self.keyword_override)
            result.a_override = True
            self.checkToken (self.SEMICOLON)
         elif self.token == self.keyword_abstract :
            self.checkToken (self.keyword_abstract)
            result.a_abstract = True
            self.checkToken (self.SEMICOLON)
         else :
            self.error ("Unexpected token")
      self.close_proc (result)
      return result

   def parse_property_decl (self) :
      result = TPropertyDecl ()
      self.storeLocation (result)
      self.checkToken (self.keyword_property)
      result.name = self.readIdentifier ()
      if self.token == self.LBRACKET :
         result.param_list = self.parse_property_param_list ()
      if self.token == self.COLON :
         self.checkToken (self.COLON)
         result.typ = self.parse_result_type ()
      if self.token == self.keyword_read :
         self.checkToken (self.keyword_read)
         result.a_read = self.parse_expr ()
      if self.token == self.keyword_write :
         self.checkToken (self.keyword_write)
         result.a_write = self.parse_expr ()
      if self.token == self.keyword_stored :
         self.checkToken (self.keyword_stored)
         result.a_stored = True
      if self.token == self.keyword_default :
         self.checkToken (self.keyword_default)
         result.a_default = True
      if self.token == self.keyword_nodefault :
         self.checkToken (self.keyword_nodefault)
         result.a_nodefault = True
      if self.token == self.keyword_implements :
         self.checkToken (self.keyword_implements)
         result.a_implements = self.parse_interface_sect ()
      if self.token == self.SEMICOLON :
         self.checkToken (self.SEMICOLON)
         self.checkToken (self.keyword_default)
         result.a_def_array = True
      self.checkToken (self.SEMICOLON)
      return result

   def parse_enum_type (self) :
      result = TEnumType ()
      self.storeLocation (result)
      self.simple_type (result)
      self.checkToken (self.LPAREN)
      result.elements = self.parse_enum_sect ()
      self.checkToken (self.RPAREN)
      return result

   def parse_enum_sect (self) :
      result = TEnumSect ()
      self.storeLocation (result)
      result.items.append (self.parse_enum_item ())
      while self.token == self.COMMA :
         self.checkToken (self.COMMA)
         result.items.append (self.parse_enum_item ())
      return result

   def parse_enum_item (self) :
      result = TEnumItem ()
      self.storeLocation (result)
      result.name = self.readIdentifier ()
      return result

   def parse_string_type (self) :
      result = TStringType ()
      self.storeLocation (result)
      self.simple_type (result)
      self.checkToken (self.keyword_string)
      if self.token == self.LBRACKET :
         self.checkToken (self.LBRACKET)
         result.lim = self.parse_expr ()
         self.checkToken (self.RBRACKET)
      return result

   def parse_array_type (self) :
      result = TArrayType ()
      self.storeLocation (result)
      self.simple_type (result)
      self.checkToken (self.keyword_array)
      if self.token == self.LBRACKET :
         self.checkToken (self.LBRACKET)
         result.index_list = self.parse_index_type_sect ()
         self.checkToken (self.RBRACKET)
      self.checkToken (self.keyword_of)
      result.elem = self.parse_type ()
      return result

   def parse_index_type_sect (self) :
      result = TIndexTypeSect ()
      self.storeLocation (result)
      result.items.append (self.parse_index_type_item ())
      while self.token == self.COMMA :
         self.checkToken (self.COMMA)
         result.items.append (self.parse_index_type_item ())
      return result

   def parse_index_type_item (self) :
      result = TIndexTypeItem ()
      self.storeLocation (result)
      result.index = self.parse_type ()
      return result

   def parse_record_type (self) :
      result = TRecordType ()
      self.storeLocation (result)
      self.simple_type (result)
      if self.token == self.keyword_packed :
         self.checkToken (self.keyword_packed)
         result.a_packed = True
      self.checkToken (self.keyword_record)
      result.fields = self.parse_field_sect ()
      self.checkToken (self.keyword_end)
      return result

   def parse_field_sect (self) :
      result = TFieldDeclGroup ()
      self.storeLocation (result)
      while self.token == self.identifier :
         result.items.append (self.parse_field_decl ())
      return result

   def parse_pointer_type (self) :
      result = TPointerType ()
      self.storeLocation (result)
      self.simple_type (result)
      self.checkToken (self.ARROW)
      result.elem = self.parse_type ()
      return result

   def parse_set_type (self) :
      result = TSetType ()
      self.storeLocation (result)
      self.simple_type (result)
      self.checkToken (self.keyword_set)
      self.checkToken (self.keyword_of)
      result.elem = self.parse_type ()
      return result

   def parse_file_type (self) :
      result = TFileType ()
      self.storeLocation (result)
      self.simple_type (result)
      self.checkToken (self.keyword_file)
      if self.token == self.keyword_of :
         self.checkToken (self.keyword_of)
         result.elem = self.parse_type ()
      return result

   def parse_class_of_type (self) :
      result = TClassOfType ()
      self.storeLocation (result)
      self.simple_type (result)
      self.checkToken (self.keyword_class)
      self.checkToken (self.keyword_of)
      result.elem = self.parse_type ()
      return result

   def parse_proc_type (self) :
      result = TProcType ()
      self.storeLocation (result)
      self.simple_type (result)
      if self.token == self.keyword_procedure :
         self.checkToken (self.keyword_procedure)
         result.style = ProcedureStyle
      elif self.token == self.keyword_function :
         self.checkToken (self.keyword_function)
         result.style = FunctionStyle
      else :
         self.error ("Unexpected token")
      result.param_list = self.parse_formal_param_list ()
      if self.token == self.COLON :
         self.checkToken (self.COLON)
         result.answer = self.parse_result_type ()
      if self.token == self.keyword_of :
         self.checkToken (self.keyword_of)
         self.checkToken (self.keyword_object)
         result.of_object = True
      if self.token == self.keyword_register or self.token == self.keyword_pascal or self.token == self.keyword_cdecl or self.token == self.keyword_stdcall or self.token == self.keyword_safecall :
         if self.token == self.keyword_register :
            self.checkToken (self.keyword_register)
            result.call_conv = RegisterCall
         elif self.token == self.keyword_pascal :
            self.checkToken (self.keyword_pascal)
            result.call_conv = PascalCall
         elif self.token == self.keyword_cdecl :
            self.checkToken (self.keyword_cdecl)
            result.call_conv = CdeclCall
         elif self.token == self.keyword_stdcall :
            self.checkToken (self.keyword_stdcall)
            result.call_conv = StdcallCall
         elif self.token == self.keyword_safecall :
            self.checkToken (self.keyword_safecall)
            result.call_conv = SafecallCall
         else :
            self.error ("Unexpected token")
      return result

   def parse_range_type (self) :
      result = TSubrangeType ()
      self.storeLocation (result)
      self.simple_type (result)
      result.low = self.parse_simple_expr ()
      self.checkToken (self.RANGE)
      result.high = self.parse_simple_expr ()
      return result

   def parse_alias_type (self) :
      result = TAliasType ()
      self.storeLocation (result)
      self.simple_type (result)
      result.alias_name = self.parse_qualified_name ()
      return result

   def parse_type (self) :
      if self.token == self.keyword_string :
         result = self.parse_string_type ()
      elif self.token == self.keyword_array :
         result = self.parse_array_type ()
      elif self.token == self.keyword_set :
         result = self.parse_set_type ()
      elif self.token == self.keyword_file :
         result = self.parse_file_type ()
      elif self.token == self.keyword_packed or self.token == self.keyword_record :
         result = self.parse_record_type ()
      elif self.token == self.keyword_class :
         result = self.parse_class_type ()
      elif self.token == self.keyword_class :
         result = self.parse_class_of_type ()
      elif self.token == self.keyword_interface :
         result = self.parse_interface_type ()
      elif self.token == self.keyword_function or self.token == self.keyword_procedure :
         result = self.parse_proc_type ()
      elif self.token == self.ARROW :
         result = self.parse_pointer_type ()
      elif self.set_4 & 1 << self.token and self.test_3 () :
         result = self.parse_range_type ()
      elif self.token == self.LPAREN and self.test_4 () :
         result = self.parse_enum_type ()
      elif self.token == self.identifier :
         result = self.parse_alias_type ()
      else :
         self.error ("Unexpected token")
      return result

   def parse_label_decl (self) :
      result = TLabelDecl ()
      self.storeLocation (result)
      result.name = self.parse_label_ident ()
      return result

   def parse_label_sect (self) :
      result = TLabelSect ()
      self.storeLocation (result)
      self.checkToken (self.keyword_label)
      result.items.append (self.parse_label_decl ())
      while self.token == self.COMMA :
         self.checkToken (self.COMMA)
         result.items.append (self.parse_label_decl ())
      self.checkToken (self.SEMICOLON)
      return result

   def parse_const_decl (self) :
      result = TConstDecl ()
      self.storeLocation (result)
      result.name = self.readIdentifier ()
      self.on_const (result)
      if self.token == self.COLON :
         self.checkToken (self.COLON)
         result.typ = self.parse_type ()
      self.checkToken (self.EQUAL)
      result.val = self.parse_expr ()
      self.checkToken (self.SEMICOLON)
      self.add_const (result)
      return result

   def parse_const_sect (self) :
      result = TConstSect ()
      self.storeLocation (result)
      self.checkToken (self.keyword_const)
      result.items.append (self.parse_const_decl ())
      while self.token == self.identifier :
         result.items.append (self.parse_const_decl ())
      return result

   def parse_type_decl (self) :
      result = TTypeDecl ()
      self.storeLocation (result)
      result.name = self.readIdentifier ()
      self.on_type (result)
      self.checkToken (self.EQUAL)
      result.typ = self.parse_type ()
      self.checkToken (self.SEMICOLON)
      self.add_type (result)
      return result

   def parse_type_sect (self) :
      result = TTypeSect ()
      self.storeLocation (result)
      self.checkToken (self.keyword_type)
      result.items.append (self.parse_type_decl ())
      while self.token == self.identifier :
         result.items.append (self.parse_type_decl ())
      return result

   def parse_var_item (self) :
      result = TVarItem ()
      self.storeLocation (result)
      result.name = self.readIdentifier ()
      self.on_var (result)
      return result

   def parse_var_decl (self) :
      result = TVarDecl ()
      self.storeLocation (result)
      result.items.append (self.parse_var_item ())
      while self.token == self.COMMA :
         self.checkToken (self.COMMA)
         result.items.append (self.parse_var_item ())
      self.checkToken (self.COLON)
      result.typ = self.parse_type ()
      if self.token == self.EQUAL :
         self.checkToken (self.EQUAL)
         result.ini = self.parse_expr ()
      self.checkToken (self.SEMICOLON)
      self.add_var (result)
      return result

   def parse_var_sect (self) :
      result = TVarSect ()
      self.storeLocation (result)
      self.checkToken (self.keyword_var)
      result.items.append (self.parse_var_decl ())
      while self.token == self.identifier :
         result.items.append (self.parse_var_decl ())
      return result

   def parse_proc_head (self, result) :
      if self.token == self.keyword_class :
         self.checkToken (self.keyword_class)
         result.a_static = True
      if self.token == self.keyword_procedure :
         self.checkToken (self.keyword_procedure)
         result.style = ProcedureStyle
      elif self.token == self.keyword_function :
         self.checkToken (self.keyword_function)
         result.style = FunctionStyle
      elif self.token == self.keyword_constructor :
         self.checkToken (self.keyword_constructor)
         result.style = ConstructorStyle
      elif self.token == self.keyword_destructor :
         self.checkToken (self.keyword_destructor)
         result.style = DestructorStyle
      else :
         self.error ("Unexpected token")
      result.proc_name = self.parse_qualified_name ()
      self.on_proc (result)
      result.param_list = self.parse_formal_param_list ()
      if self.token == self.COLON :
         self.checkToken (self.COLON)
         result.answer = self.parse_result_type ()
      self.checkToken (self.SEMICOLON)
      return result

   def parse_proc_decl (self) :
      result = TProcDecl ()
      self.storeLocation (result)
      self.open_proc (result)
      self.parse_proc_head (result)
      if self.token == self.keyword_forward :
         self.checkToken (self.keyword_forward)
         result.a_forward = True
      elif self.token == self.keyword_external :
         self.parse_proc_external (result)
         result.external_spec = True
      elif self.set_11 & 1 << self.token :
         if self.token == self.keyword_inline :
            self.checkToken (self.keyword_inline)
            self.checkToken (self.SEMICOLON)
            result.a_inline = True
         result.local = self.parse_decl_part ()
         self.on_begin_proc (result)
         self.checkToken (self.keyword_begin)
         result.body = self.parse_stat_list ()
         self.on_end_proc (result)
         self.checkToken (self.keyword_end)
         self.on_tail_proc (result)
      else :
         self.error ("Unexpected token")
      self.checkToken (self.SEMICOLON)
      self.close_proc (result)
      return result

   def parse_proc_external (self, result) :
      self.checkToken (self.keyword_external)
      result.a_external = True
      if self.set_4 & 1 << self.token :
         result.a_lib = self.parse_expr ()
      self.checkToken (self.SEMICOLON)
      return result

   def parse_proc_intf_decl (self) :
      result = TProcDecl ()
      self.storeLocation (result)
      self.open_proc (result)
      self.parse_proc_head (result)
      if self.token == self.keyword_inline :
         self.checkToken (self.keyword_inline)
         self.checkToken (self.SEMICOLON)
         result.a_inline = True
      if self.token == self.keyword_external :
         self.parse_proc_external (result)
         result.external_spec = True
      self.close_proc (result)
      return result

   def parse_intf_decl (self) :
      if self.token == self.keyword_const :
         result = self.parse_const_sect ()
      elif self.token == self.keyword_type :
         result = self.parse_type_sect ()
      elif self.token == self.keyword_var :
         result = self.parse_var_sect ()
      elif self.set_8 & 1 << self.token :
         result = self.parse_proc_intf_decl ()
      else :
         self.error ("Unexpected token")
      return result

   def parse_intf_decl_part (self) :
      result = TDeclGroup ()
      self.storeLocation (result)
      while self.set_12 & 1 << self.token :
         result.items.append (self.parse_intf_decl ())
      return result

   def parse_decl (self) :
      if self.token == self.keyword_label :
         result = self.parse_label_sect ()
      elif self.token == self.keyword_const :
         result = self.parse_const_sect ()
      elif self.token == self.keyword_type :
         result = self.parse_type_sect ()
      elif self.token == self.keyword_var :
         result = self.parse_var_sect ()
      elif self.set_8 & 1 << self.token :
         result = self.parse_proc_decl ()
      else :
         self.error ("Unexpected token")
      return result

   def parse_decl_part (self) :
      result = TDeclGroup ()
      self.storeLocation (result)
      while self.set_13 & 1 << self.token :
         result.items.append (self.parse_decl ())
      return result

   def parse_import_item (self) :
      result = TImportItem ()
      self.storeLocation (result)
      result.name = self.readIdentifier ()
      self.on_import (result)
      if self.token == self.keyword_in :
         self.checkToken (self.keyword_in)
         result.path = self.readString ()
      return result

   def parse_import_sect (self) :
      result = TImportSect ()
      self.storeLocation (result)
      if self.token == self.keyword_uses :
         self.checkToken (self.keyword_uses)
         result.items.append (self.parse_import_item ())
         while self.token == self.COMMA :
            self.checkToken (self.COMMA)
            result.items.append (self.parse_import_item ())
         self.checkToken (self.SEMICOLON)
      return result

   def parse_unit_decl (self) :
      result = TUnitModule ()
      self.storeLocation (result)
      self.open_module (result)
      self.checkToken (self.keyword_unit)
      result.name = self.readIdentifier ()
      self.on_module (result)
      self.checkToken (self.SEMICOLON)
      self.checkToken (self.keyword_interface)
      result.intf_imports = self.parse_import_sect ()
      result.intf_decl = self.parse_intf_decl_part ()
      self.checkToken (self.keyword_implementation)
      result.impl_imports = self.parse_import_sect ()
      result.impl_decl = self.parse_decl_part ()
      if True or self.token == self.keyword_begin :
         if self.token == self.keyword_begin :
            self.checkToken (self.keyword_begin)
            result.init = self.parse_stat_list ()
         else :
            if self.token == self.keyword_initialization :
               self.checkToken (self.keyword_initialization)
               result.init = self.parse_stat_list ()
            if self.token == self.keyword_finalization :
               self.checkToken (self.keyword_finalization)
               result.finish = self.parse_stat_list ()
            result.no_begin = True
      self.checkToken (self.keyword_end)
      self.checkToken (self.DOT)
      self.close_module (result)
      return result

   def parse_program_decl (self) :
      result = TProgramModule ()
      self.storeLocation (result)
      self.open_module (result)
      self.checkToken (self.keyword_program)
      result.name = self.readIdentifier ()
      self.on_module (result)
      self.checkToken (self.SEMICOLON)
      result.impl_imports = self.parse_import_sect ()
      result.impl_decl = self.parse_decl_part ()
      self.checkToken (self.keyword_begin)
      result.init = self.parse_stat_list ()
      self.checkToken (self.keyword_end)
      self.checkToken (self.DOT)
      self.close_module (result)
      return result

   def parse_library_decl (self) :
      result = TLibraryModule ()
      self.storeLocation (result)
      self.open_module (result)
      self.checkToken (self.keyword_library)
      result.name = self.readIdentifier ()
      self.on_module (result)
      self.checkToken (self.SEMICOLON)
      result.impl_imports = self.parse_import_sect ()
      result.impl_decl = self.parse_decl_part ()
      self.checkToken (self.keyword_begin)
      result.init = self.parse_stat_list ()
      self.checkToken (self.keyword_end)
      self.checkToken (self.DOT)
      self.close_module (result)
      return result

   def parse_module_decl (self) :
      if self.token == self.keyword_unit :
         result = self.parse_unit_decl ()
      elif self.token == self.keyword_program :
         result = self.parse_program_decl ()
      elif self.token == self.keyword_library :
         result = self.parse_library_decl ()
      else :
         self.error ("Unexpected token")
      return result

   def test_1 (self) :
      result = True
      position = self.mark ()
      if result and self.token != self.keyword_string :
         result = False
      if result :
         self.nextToken ()
      if result and self.token != self.LPAREN :
         result = False
      if result :
         self.nextToken ()
      self.rewind (position)
      return result

   def test_2 (self) :
      result = True
      position = self.mark ()
      if result :
         if not self.test_label_ident () :
            result = False
      if result and self.token != self.COLON :
         result = False
      if result :
         self.nextToken ()
      self.rewind (position)
      return result

   def test_3 (self) :
      result = True
      position = self.mark ()
      if result :
         if not self.test_range_type () :
            result = False
      self.rewind (position)
      return result

   def test_4 (self) :
      result = True
      position = self.mark ()
      if result :
         if not self.test_enum_type () :
            result = False
      self.rewind (position)
      return result

   def test_label_ident (self) :
      if self.token != self.identifier :
         return False
      self.nextToken ()
      return True

   def test_range_type (self) :
      if not self.test_simple_expr () :
         return False
      if self.token != self.RANGE :
         return False
      self.nextToken ()
      if not self.test_simple_expr () :
         return False
      return True

   def test_simple_expr (self) :
      if not self.test_term () :
         return False
      while self.token == self.PLUS or self.token == self.MINUS or self.token == self.keyword_or or self.token == self.keyword_xor :
         if self.token == self.PLUS :
            self.nextToken ()
         elif self.token == self.MINUS :
            self.nextToken ()
         elif self.token == self.keyword_or :
            self.nextToken ()
         elif self.token == self.keyword_xor :
            self.nextToken ()
         else :
            return False
         if not self.test_term () :
            return False
      return True

   def test_term (self) :
      if not self.test_factor () :
         return False
      while self.token == self.STAR or self.token == self.SLASH or self.token == self.keyword_div or self.token == self.keyword_mod or self.token == self.keyword_shl or self.token == self.keyword_shr or self.token == self.keyword_and or self.token == self.keyword_as :
         if self.token == self.STAR :
            self.nextToken ()
         elif self.token == self.SLASH :
            self.nextToken ()
         elif self.token == self.keyword_div :
            self.nextToken ()
         elif self.token == self.keyword_mod :
            self.nextToken ()
         elif self.token == self.keyword_shl :
            self.nextToken ()
         elif self.token == self.keyword_shr :
            self.nextToken ()
         elif self.token == self.keyword_and :
            self.nextToken ()
         elif self.token == self.keyword_as :
            self.nextToken ()
         else :
            return False
         if not self.test_factor () :
            return False
      return True

   def test_factor (self) :
      if self.token == self.number :
         if not self.test_int_value_expr () :
            return False
      elif self.token == self.real_number :
         if not self.test_float_value_expr () :
            return False
      elif self.token == self.string_literal :
         if not self.test_string_value_expr () :
            return False
      elif self.token == self.keyword_not :
         if not self.test_not_expr () :
            return False
      elif self.token == self.PLUS :
         if not self.test_plus_expr () :
            return False
      elif self.token == self.MINUS :
         if not self.test_minus_expr () :
            return False
      elif self.token == self.ADDRESS :
         if not self.test_adr_expr () :
            return False
      elif self.token == self.keyword_nil :
         if not self.test_nil_expr () :
            return False
      elif self.token == self.LBRACKET :
         if not self.test_set_expr () :
            return False
      elif self.token == self.keyword_string and self.test_1 () :
         if not self.test_string_type_expr () :
            return False
      elif self.token == self.identifier or self.token == self.LPAREN or self.token == self.keyword_inherited :
         if not self.test_reference () :
            return False
      else :
         return False
      return True

   def test_int_value_expr (self) :
      if self.token != self.number :
         return False
      self.nextToken ()
      return True

   def test_float_value_expr (self) :
      if self.token != self.real_number :
         return False
      self.nextToken ()
      return True

   def test_string_value_expr (self) :
      if self.token != self.string_literal :
         return False
      self.nextToken ()
      return True

   def test_not_expr (self) :
      if self.token != self.keyword_not :
         return False
      self.nextToken ()
      if not self.test_factor () :
         return False
      return True

   def test_plus_expr (self) :
      if self.token != self.PLUS :
         return False
      self.nextToken ()
      if not self.test_factor () :
         return False
      return True

   def test_minus_expr (self) :
      if self.token != self.MINUS :
         return False
      self.nextToken ()
      if not self.test_factor () :
         return False
      return True

   def test_adr_expr (self) :
      if self.token != self.ADDRESS :
         return False
      self.nextToken ()
      if not self.test_factor () :
         return False
      return True

   def test_nil_expr (self) :
      if self.token != self.keyword_nil :
         return False
      self.nextToken ()
      return True

   def test_set_expr (self) :
      if self.token != self.LBRACKET :
         return False
      self.nextToken ()
      if not self.test_elem_sect () :
         return False
      if self.token != self.RBRACKET :
         return False
      self.nextToken ()
      return True

   def test_elem_sect (self) :
      if not self.test_elem_item () :
         return False
      while self.token == self.COMMA :
         self.nextToken ()
         if not self.test_elem_item () :
            return False
      return True

   def test_elem_item (self) :
      if not self.test_expr () :
         return False
      if self.token == self.RANGE :
         self.nextToken ()
         if not self.test_expr () :
            return False
      return True

   def test_expr (self) :
      if not self.test_simple_expr () :
         return False
      if self.token == self.EQUAL or self.token == self.UNEQUAL or self.token == self.LESS or self.token == self.GREATER or self.token == self.LESS_OR_EQUAL or self.token == self.GREATER_OR_EQUAL or self.token == self.keyword_in or self.token == self.keyword_is :
         if self.token == self.EQUAL :
            self.nextToken ()
         elif self.token == self.UNEQUAL :
            self.nextToken ()
         elif self.token == self.LESS :
            self.nextToken ()
         elif self.token == self.GREATER :
            self.nextToken ()
         elif self.token == self.LESS_OR_EQUAL :
            self.nextToken ()
         elif self.token == self.GREATER_OR_EQUAL :
            self.nextToken ()
         elif self.token == self.keyword_in :
            self.nextToken ()
         elif self.token == self.keyword_is :
            self.nextToken ()
         else :
            return False
         if not self.test_simple_expr () :
            return False
      return True

   def test_string_type_expr (self) :
      if self.token != self.keyword_string :
         return False
      self.nextToken ()
      if self.token != self.LPAREN :
         return False
      self.nextToken ()
      if not self.test_expr () :
         return False
      if self.token != self.RPAREN :
         return False
      self.nextToken ()
      return True

   def test_reference (self) :
      if not self.test_variable () :
         return False
      while self.token == self.LBRACKET or self.token == self.LPAREN or self.token == self.ARROW or self.token == self.DOT :
         if self.token == self.LBRACKET :
            if not self.test_index_expr () :
               return False
         elif self.token == self.LPAREN :
            if not self.test_call_expr () :
               return False
         elif self.token == self.ARROW :
            if not self.test_deref_expr () :
               return False
         elif self.token == self.DOT :
            if not self.test_field_expr () :
               return False
         else :
            return False
      return True

   def test_variable (self) :
      if self.token == self.identifier :
         if not self.test_ident_expr () :
            return False
      elif self.token == self.LPAREN :
         if not self.test_sub_expr () :
            return False
      elif self.token == self.keyword_inherited :
         if not self.test_super_expr () :
            return False
      else :
         return False
      return True

   def test_ident_expr (self) :
      if self.token != self.identifier :
         return False
      self.nextToken ()
      return True

   def test_sub_expr (self) :
      if self.token != self.LPAREN :
         return False
      self.nextToken ()
      if not self.test_expr () :
         return False
      if self.token != self.RPAREN :
         return False
      self.nextToken ()
      return True

   def test_super_expr (self) :
      if self.token != self.keyword_inherited :
         return False
      self.nextToken ()
      if self.token != self.identifier :
         return False
      self.nextToken ()
      return True

   def test_index_expr (self) :
      if self.token != self.LBRACKET :
         return False
      self.nextToken ()
      if not self.test_index_expr_list () :
         return False
      if self.token != self.RBRACKET :
         return False
      self.nextToken ()
      return True

   def test_index_expr_list (self) :
      if not self.test_index_expr_item () :
         return False
      while self.token == self.COMMA :
         self.nextToken ()
         if not self.test_index_expr_item () :
            return False
      return True

   def test_index_expr_item (self) :
      if not self.test_expr () :
         return False
      return True

   def test_call_expr (self) :
      if self.token != self.LPAREN :
         return False
      self.nextToken ()
      if not self.test_arg_list () :
         return False
      if self.token != self.RPAREN :
         return False
      self.nextToken ()
      return True

   def test_arg_list (self) :
      if not self.test_arg_item () :
         return False
      while self.token == self.COMMA :
         self.nextToken ()
         if not self.test_arg_item () :
            return False
      return True

   def test_arg_item (self) :
      if not self.test_expr () :
         return False
      if self.token == self.COLON :
         self.nextToken ()
         if not self.test_expr () :
            return False
         if self.token == self.COLON :
            self.nextToken ()
            if not self.test_expr () :
               return False
      return True

   def test_deref_expr (self) :
      if self.token != self.ARROW :
         return False
      self.nextToken ()
      return True

   def test_field_expr (self) :
      if self.token != self.DOT :
         return False
      self.nextToken ()
      if self.token != self.identifier :
         return False
      self.nextToken ()
      return True

   def test_enum_type (self) :
      if self.token != self.LPAREN :
         return False
      self.nextToken ()
      if not self.test_enum_sect () :
         return False
      if self.token != self.RPAREN :
         return False
      self.nextToken ()
      return True

   def test_enum_sect (self) :
      if not self.test_enum_item () :
         return False
      while self.token == self.COMMA :
         self.nextToken ()
         if not self.test_enum_item () :
            return False
      return True

   def test_enum_item (self) :
      if self.token != self.identifier :
         return False
      self.nextToken ()
      return True

   def lookupKeyword (self) :
      s = self.tokenText
      n = len (s)
      if n == 2 :
         if s[0] == 'a' :
            if s[1] == 's' :
               self.token = self.keyword_as
         elif s[0] == 'd' :
            if s[1] == 'o' :
               self.token = self.keyword_do
         elif s[0] == 'i' :
            if s[1] == 'f' :
               self.token = self.keyword_if
            elif s[1] == 'n' :
               self.token = self.keyword_in
            elif s[1] == 's' :
               self.token = self.keyword_is
         elif s[0] == 'o' :
            if s[1] == 'f' :
               self.token = self.keyword_of
            elif s[1] == 'n' :
               self.token = self.keyword_on
            elif s[1] == 'r' :
               self.token = self.keyword_or
         elif s[0] == 't' :
            if s[1] == 'o' :
               self.token = self.keyword_to
      elif n == 3 :
         if s[0] == 'a' :
            if s[1:3] == "nd" :
               self.token = self.keyword_and
         elif s[0] == 'd' :
            if s[1:3] == "iv" :
               self.token = self.keyword_div
         elif s[0] == 'e' :
            if s[1:3] == "nd" :
               self.token = self.keyword_end
         elif s[0] == 'f' :
            if s[1:3] == "or" :
               self.token = self.keyword_for
         elif s[0] == 'm' :
            if s[1:3] == "od" :
               self.token = self.keyword_mod
         elif s[0] == 'n' :
            if s[1] == 'i' :
               if s[2] == 'l' :
                  self.token = self.keyword_nil
            elif s[1] == 'o' :
               if s[2] == 't' :
                  self.token = self.keyword_not
         elif s[0] == 'o' :
            if s[1:3] == "ut" :
               self.token = self.keyword_out
         elif s[0] == 's' :
            if s[1] == 'e' :
               if s[2] == 't' :
                  self.token = self.keyword_set
            elif s[1] == 'h' :
               if s[2] == 'l' :
                  self.token = self.keyword_shl
               elif s[2] == 'r' :
                  self.token = self.keyword_shr
         elif s[0] == 't' :
            if s[1:3] == "ry" :
               self.token = self.keyword_try
         elif s[0] == 'v' :
            if s[1:3] == "ar" :
               self.token = self.keyword_var
         elif s[0] == 'x' :
            if s[1:3] == "or" :
               self.token = self.keyword_xor
      elif n == 4 :
         if s[0] == 'c' :
            if s[1:4] == "ase" :
               self.token = self.keyword_case
         elif s[0] == 'e' :
            if s[1:4] == "lse" :
               self.token = self.keyword_else
         elif s[0] == 'f' :
            if s[1:4] == "ile" :
               self.token = self.keyword_file
         elif s[0] == 'g' :
            if s[1:4] == "oto" :
               self.token = self.keyword_goto
         elif s[0] == 'r' :
            if s[1:4] == "ead" :
               self.token = self.keyword_read
         elif s[0] == 't' :
            if s[1] == 'h' :
               if s[2:4] == "en" :
                  self.token = self.keyword_then
            elif s[1] == 'y' :
               if s[2:4] == "pe" :
                  self.token = self.keyword_type
         elif s[0] == 'u' :
            if s[1] == 'n' :
               if s[2:4] == "it" :
                  self.token = self.keyword_unit
            elif s[1] == 's' :
               if s[2:4] == "es" :
                  self.token = self.keyword_uses
         elif s[0] == 'w' :
            if s[1:4] == "ith" :
               self.token = self.keyword_with
      elif n == 5 :
         if s[0] == 'a' :
            if s[1:5] == "rray" :
               self.token = self.keyword_array
         elif s[0] == 'b' :
            if s[1:5] == "egin" :
               self.token = self.keyword_begin
         elif s[0] == 'c' :
            if s[1] == 'd' :
               if s[2:5] == "ecl" :
                  self.token = self.keyword_cdecl
            elif s[1] == 'l' :
               if s[2:5] == "ass" :
                  self.token = self.keyword_class
            elif s[1] == 'o' :
               if s[2:5] == "nst" :
                  self.token = self.keyword_const
         elif s[0] == 'l' :
            if s[1:5] == "abel" :
               self.token = self.keyword_label
         elif s[0] == 'r' :
            if s[1:5] == "aise" :
               self.token = self.keyword_raise
         elif s[0] == 'u' :
            if s[1:5] == "ntil" :
               self.token = self.keyword_until
         elif s[0] == 'w' :
            if s[1] == 'h' :
               if s[2:5] == "ile" :
                  self.token = self.keyword_while
            elif s[1] == 'r' :
               if s[2:5] == "ite" :
                  self.token = self.keyword_write
      elif n == 6 :
         if s[0] == 'd' :
            if s[1:6] == "ownto" :
               self.token = self.keyword_downto
         elif s[0] == 'e' :
            if s[1:6] == "xcept" :
               self.token = self.keyword_except
         elif s[0] == 'i' :
            if s[1:6] == "nline" :
               self.token = self.keyword_inline
         elif s[0] == 'o' :
            if s[1:6] == "bject" :
               self.token = self.keyword_object
         elif s[0] == 'p' :
            if s[1] == 'a' :
               if s[2] == 'c' :
                  if s[3:6] == "ked" :
                     self.token = self.keyword_packed
               elif s[2] == 's' :
                  if s[3:6] == "cal" :
                     self.token = self.keyword_pascal
            elif s[1] == 'u' :
               if s[2:6] == "blic" :
                  self.token = self.keyword_public
         elif s[0] == 'r' :
            if s[1] == 'e' :
               if s[2] == 'c' :
                  if s[3:6] == "ord" :
                     self.token = self.keyword_record
               elif s[2] == 'p' :
                  if s[3:6] == "eat" :
                     self.token = self.keyword_repeat
         elif s[0] == 's' :
            if s[1] == 't' :
               if s[2] == 'o' :
                  if s[3:6] == "red" :
                     self.token = self.keyword_stored
               elif s[2] == 'r' :
                  if s[3:6] == "ing" :
                     self.token = self.keyword_string
      elif n == 7 :
         if s[0] == 'd' :
            if s[1] == 'e' :
               if s[2:7] == "fault" :
                  self.token = self.keyword_default
            elif s[1] == 'y' :
               if s[2:7] == "namic" :
                  self.token = self.keyword_dynamic
         elif s[0] == 'f' :
            if s[1] == 'i' :
               if s[2:7] == "nally" :
                  self.token = self.keyword_finally
            elif s[1] == 'o' :
               if s[2:7] == "rward" :
                  self.token = self.keyword_forward
         elif s[0] == 'l' :
            if s[1:7] == "ibrary" :
               self.token = self.keyword_library
         elif s[0] == 'p' :
            if s[1] == 'r' :
               if s[2] == 'i' :
                  if s[3:7] == "vate" :
                     self.token = self.keyword_private
               elif s[2] == 'o' :
                  if s[3:7] == "gram" :
                     self.token = self.keyword_program
         elif s[0] == 's' :
            if s[1:7] == "tdcall" :
               self.token = self.keyword_stdcall
         elif s[0] == 'v' :
            if s[1:7] == "irtual" :
               self.token = self.keyword_virtual
      elif n == 8 :
         if s[0] == 'a' :
            if s[1:8] == "bstract" :
               self.token = self.keyword_abstract
         elif s[0] == 'e' :
            if s[1:8] == "xternal" :
               self.token = self.keyword_external
         elif s[0] == 'f' :
            if s[1:8] == "unction" :
               self.token = self.keyword_function
         elif s[0] == 'o' :
            if s[1:8] == "verride" :
               self.token = self.keyword_override
         elif s[0] == 'p' :
            if s[1:8] == "roperty" :
               self.token = self.keyword_property
         elif s[0] == 'r' :
            if s[1:8] == "egister" :
               self.token = self.keyword_register
         elif s[0] == 's' :
            if s[1:8] == "afecall" :
               self.token = self.keyword_safecall
      elif n == 9 :
         if s[0] == 'a' :
            if s[1:9] == "utomated" :
               self.token = self.keyword_automated
         elif s[0] == 'i' :
            if s[1] == 'n' :
               if s[2] == 'h' :
                  if s[3:9] == "erited" :
                     self.token = self.keyword_inherited
               elif s[2] == 't' :
                  if s[3:9] == "erface" :
                     self.token = self.keyword_interface
         elif s[0] == 'n' :
            if s[1:9] == "odefault" :
               self.token = self.keyword_nodefault
         elif s[0] == 'p' :
            if s[1] == 'r' :
               if s[2] == 'o' :
                  if s[3] == 'c' :
                     if s[4:9] == "edure" :
                        self.token = self.keyword_procedure
                  elif s[3] == 't' :
                     if s[4:9] == "ected" :
                        self.token = self.keyword_protected
            elif s[1] == 'u' :
               if s[2:9] == "blished" :
                  self.token = self.keyword_published
      elif n == 10 :
         if s[0] == 'd' :
            if s[1:10] == "estructor" :
               self.token = self.keyword_destructor
         elif s[0] == 'i' :
            if s[1:10] == "mplements" :
               self.token = self.keyword_implements
      elif n == 11 :
         if s[0:11] == "constructor" :
            self.token = self.keyword_constructor
      elif n == 12 :
         if s[0:12] == "finalization" :
            self.token = self.keyword_finalization
      elif n == 14 :
         if s[0] == 'i' :
            if s[1] == 'm' :
               if s[2:14] == "plementation" :
                  self.token = self.keyword_implementation
            elif s[1] == 'n' :
               if s[2:14] == "itialization" :
                  self.token = self.keyword_initialization

   def processSeparator (self) :
      if self.tokenText == '(' :
         self.token = 8
      if self.tokenText == ')' :
         self.token = 9
      if self.tokenText == '*' :
         self.token = 10
      if self.tokenText == '+' :
         self.token = 11
      if self.tokenText == ',' :
         self.token = 12
      if self.tokenText == '-' :
         self.token = 13
      if self.tokenText == '.' :
         self.token = 14
         if self.ch == '.' :
            self.token = 15
            self.tokenText = self.tokenText + self.ch
            self.nextChar ()
      if self.tokenText == '/' :
         self.token = 16
      if self.tokenText == ':' :
         self.token = 17
         if self.ch == '=' :
            self.token = 18
            self.tokenText = self.tokenText + self.ch
            self.nextChar ()
      if self.tokenText == ';' :
         self.token = 19
      if self.tokenText == '<' :
         self.token = 20
         if self.ch == '=' :
            self.token = 21
            self.tokenText = self.tokenText + self.ch
            self.nextChar ()
         if self.ch == '>' :
            self.token = 22
            self.tokenText = self.tokenText + self.ch
            self.nextChar ()
      if self.tokenText == '=' :
         self.token = 23
      if self.tokenText == '>' :
         self.token = 24
         if self.ch == '=' :
            self.token = 25
            self.tokenText = self.tokenText + self.ch
            self.nextChar ()
      if self.tokenText == '@' :
         self.token = 26
      if self.tokenText == '[' :
         self.token = 27
      if self.tokenText == ']' :
         self.token = 28
      if self.tokenText == '^' :
         self.token = 29
      if self.token == self.separator :
         self.error ("Unknown separator")

   def tokenToString (self, value) :
      if value == 0: return "<end of source text>"
      if value == 1: return "<identifier>"
      if value == 2: return "<number>"
      if value == 3: return "<real_number>"
      if value == 4: return "<character_literal>"
      if value == 5: return "<string_literal>"
      if value == 6: return "<unknown separator>"
      if value == 7: return "<end of line>"
      if value == 8: return "("
      if value == 9: return ")"
      if value == 10: return "*"
      if value == 11: return "+"
      if value == 12: return ","
      if value == 13: return "-"
      if value == 14: return "."
      if value == 15: return ".."
      if value == 16: return "/"
      if value == 17: return ":"
      if value == 18: return ":="
      if value == 19: return ";"
      if value == 20: return "<"
      if value == 21: return "<="
      if value == 22: return "<>"
      if value == 23: return "="
      if value == 24: return ">"
      if value == 25: return ">="
      if value == 26: return "@"
      if value == 27: return "["
      if value == 28: return "]"
      if value == 29: return "^"
      if value == 30: return "abstract"
      if value == 31: return "and"
      if value == 32: return "array"
      if value == 33: return "as"
      if value == 34: return "automated"
      if value == 35: return "begin"
      if value == 36: return "case"
      if value == 37: return "cdecl"
      if value == 38: return "class"
      if value == 39: return "const"
      if value == 40: return "constructor"
      if value == 41: return "default"
      if value == 42: return "destructor"
      if value == 43: return "div"
      if value == 44: return "do"
      if value == 45: return "downto"
      if value == 46: return "dynamic"
      if value == 47: return "else"
      if value == 48: return "end"
      if value == 49: return "except"
      if value == 50: return "external"
      if value == 51: return "file"
      if value == 52: return "finalization"
      if value == 53: return "finally"
      if value == 54: return "for"
      if value == 55: return "forward"
      if value == 56: return "function"
      if value == 57: return "goto"
      if value == 58: return "if"
      if value == 59: return "implementation"
      if value == 60: return "implements"
      if value == 61: return "in"
      if value == 62: return "inherited"
      if value == 63: return "initialization"
      if value == 64: return "inline"
      if value == 65: return "interface"
      if value == 66: return "is"
      if value == 67: return "label"
      if value == 68: return "library"
      if value == 69: return "mod"
      if value == 70: return "nil"
      if value == 71: return "nodefault"
      if value == 72: return "not"
      if value == 73: return "object"
      if value == 74: return "of"
      if value == 75: return "on"
      if value == 76: return "or"
      if value == 77: return "out"
      if value == 78: return "override"
      if value == 79: return "packed"
      if value == 80: return "pascal"
      if value == 81: return "private"
      if value == 82: return "procedure"
      if value == 83: return "program"
      if value == 84: return "property"
      if value == 85: return "protected"
      if value == 86: return "public"
      if value == 87: return "published"
      if value == 88: return "raise"
      if value == 89: return "read"
      if value == 90: return "record"
      if value == 91: return "register"
      if value == 92: return "repeat"
      if value == 93: return "safecall"
      if value == 94: return "set"
      if value == 95: return "shl"
      if value == 96: return "shr"
      if value == 97: return "stdcall"
      if value == 98: return "stored"
      if value == 99: return "string"
      if value == 100: return "then"
      if value == 101: return "to"
      if value == 102: return "try"
      if value == 103: return "type"
      if value == 104: return "unit"
      if value == 105: return "until"
      if value == 106: return "uses"
      if value == 107: return "var"
      if value == 108: return "virtual"
      if value == 109: return "while"
      if value == 110: return "with"
      if value == 111: return "write"
      if value == 112: return "xor"
      return "<unknown symbol>"

   def storeLocation (self, item) :
      item.src_file = self.tokenFileInx
      item.src_line = self.tokenLineNum
      item.src_column = self.tokenColNum
      item.src_pos = self.tokenByteOfs
      item.src_end = self.charByteOfs

   def alloc (self, items) :
      result = 0
      for inx in items :
         result |= 1 << inx
      return result

   def __init__ (self) :
      super (Parser, self).__init__ ()

      # eos = 0
      # identifier = 1
      # number = 2
      # real_number = 3
      # character_literal = 4
      # string_literal = 5
      # separator = 6
      # end_of_line = 7
      self.LPAREN = 8 # (
      self.RPAREN = 9 # )
      self.STAR = 10 # *
      self.PLUS = 11 # +
      self.COMMA = 12 # ,
      self.MINUS = 13 # -
      self.DOT = 14 # .
      self.RANGE = 15 # ..
      self.SLASH = 16 # /
      self.COLON = 17 # :
      self.ASSIGN = 18 # :=
      self.SEMICOLON = 19 # ;
      self.LESS = 20 # <
      self.LESS_OR_EQUAL = 21 # <=
      self.UNEQUAL = 22 # <>
      self.EQUAL = 23 # =
      self.GREATER = 24 # >
      self.GREATER_OR_EQUAL = 25 # >=
      self.ADDRESS = 26 # @
      self.LBRACKET = 27 # [
      self.RBRACKET = 28 # ]
      self.ARROW = 29 # ^
      self.keyword_abstract = 30
      self.keyword_and = 31
      self.keyword_array = 32
      self.keyword_as = 33
      self.keyword_automated = 34
      self.keyword_begin = 35
      self.keyword_case = 36
      self.keyword_cdecl = 37
      self.keyword_class = 38
      self.keyword_const = 39
      self.keyword_constructor = 40
      self.keyword_default = 41
      self.keyword_destructor = 42
      self.keyword_div = 43
      self.keyword_do = 44
      self.keyword_downto = 45
      self.keyword_dynamic = 46
      self.keyword_else = 47
      self.keyword_end = 48
      self.keyword_except = 49
      self.keyword_external = 50
      self.keyword_file = 51
      self.keyword_finalization = 52
      self.keyword_finally = 53
      self.keyword_for = 54
      self.keyword_forward = 55
      self.keyword_function = 56
      self.keyword_goto = 57
      self.keyword_if = 58
      self.keyword_implementation = 59
      self.keyword_implements = 60
      self.keyword_in = 61
      self.keyword_inherited = 62
      self.keyword_initialization = 63
      self.keyword_inline = 64
      self.keyword_interface = 65
      self.keyword_is = 66
      self.keyword_label = 67
      self.keyword_library = 68
      self.keyword_mod = 69
      self.keyword_nil = 70
      self.keyword_nodefault = 71
      self.keyword_not = 72
      self.keyword_object = 73
      self.keyword_of = 74
      self.keyword_on = 75
      self.keyword_or = 76
      self.keyword_out = 77
      self.keyword_override = 78
      self.keyword_packed = 79
      self.keyword_pascal = 80
      self.keyword_private = 81
      self.keyword_procedure = 82
      self.keyword_program = 83
      self.keyword_property = 84
      self.keyword_protected = 85
      self.keyword_public = 86
      self.keyword_published = 87
      self.keyword_raise = 88
      self.keyword_read = 89
      self.keyword_record = 90
      self.keyword_register = 91
      self.keyword_repeat = 92
      self.keyword_safecall = 93
      self.keyword_set = 94
      self.keyword_shl = 95
      self.keyword_shr = 96
      self.keyword_stdcall = 97
      self.keyword_stored = 98
      self.keyword_string = 99
      self.keyword_then = 100
      self.keyword_to = 101
      self.keyword_try = 102
      self.keyword_type = 103
      self.keyword_unit = 104
      self.keyword_until = 105
      self.keyword_uses = 106
      self.keyword_var = 107
      self.keyword_virtual = 108
      self.keyword_while = 109
      self.keyword_with = 110
      self.keyword_write = 111
      self.keyword_xor = 112

      self.set_0 = self.alloc ([8, 14, 27, 29]) #  (  .  [  ^
      self.set_1 = self.alloc ([10, 16, 31, 33, 43, 69, 95, 96]) #  *  /  and  as  div  mod  shl  shr
      self.set_2 = self.alloc ([11, 13, 76, 112]) #  +  -  or  xor
      self.set_3 = self.alloc ([20, 21, 22, 23, 24, 25, 61, 66]) #  <  <=  <>  =  >  >=  in  is
      self.set_4 = self.alloc ([1, 2, 3, 5, 8, 11, 13, 26, 27, 62, 70, 72, 99]) #  identifier  number  real_number  string_literal  (  +  -  @  [  inherited  nil  not  string
      self.set_5 = self.alloc ([1, 2, 3, 5, 8, 11, 13, 19, 26, 27, 35, 36, 54, 57, 58, 62, 70, 72, 88, 92, 99, 102, 109, 110]) #  identifier  number  real_number  string_literal  (  +  -  ;  @  [  begin  case  for  goto  if  inherited  nil  not  raise  repeat  string  try  while  with
      self.set_6 = self.alloc ([34, 81, 85, 86, 87]) #  automated  private  protected  public  published
      self.set_7 = self.alloc ([1, 38, 40, 42, 56, 82, 84]) #  identifier  class  constructor  destructor  function  procedure  property
      self.set_8 = self.alloc ([38, 40, 42, 56, 82]) #  class  constructor  destructor  function  procedure
      self.set_9 = self.alloc ([30, 46, 78, 108]) #  abstract  dynamic  override  virtual
      self.set_10 = self.alloc ([37, 80, 91, 93, 97]) #  cdecl  pascal  register  safecall  stdcall
      self.set_11 = self.alloc ([35, 38, 39, 40, 42, 56, 64, 67, 82, 103, 107]) #  begin  class  const  constructor  destructor  function  inline  label  procedure  type  var
      self.set_12 = self.alloc ([38, 39, 40, 42, 56, 82, 103, 107]) #  class  const  constructor  destructor  function  procedure  type  var
      self.set_13 = self.alloc ([38, 39, 40, 42, 56, 67, 82, 103, 107]) #  class  const  constructor  destructor  function  label  procedure  type  var

   def on_ident_expr (self, item) :
      pass

   def on_field_expr (self, item) :
      pass

   def on_param (self, item) :
      pass

   def add_param (self, item) :
      pass

   def open_class (self, item) :
      pass

   def close_class (self, item) :
      pass

   def open_interface (self, item) :
      pass

   def close_interface (self, item) :
      pass

   def on_field (self, item) :
      pass

   def add_field (self, item) :
      pass

   def open_proc (self, item) :
      pass

   def close_proc (self, item) :
      pass

   def simple_type (self, item) :
      pass

   def on_const (self, item) :
      pass

   def add_const (self, item) :
      pass

   def on_type (self, item) :
      pass

   def add_type (self, item) :
      pass

   def on_var (self, item) :
      pass

   def add_var (self, item) :
      pass

   def on_proc (self, item) :
      pass

   def on_begin_proc (self, item) :
      pass

   def on_end_proc (self, item) :
      pass

   def on_tail_proc (self, item) :
      pass

   def on_import (self, item) :
      pass

   def open_module (self, item) :
      pass

   def on_module (self, item) :
      pass

   def close_module (self, item) :
      pass

# TFce
UnknownExp = 0
MulExp = 1
RDivExp = 2
DivExp = 3
ModExp = 4
ShlExp = 5
ShrExp = 6
AndExp = 7
AsExp = 8
AddExp = 9
SubExp = 10
OrExp = 11
XorExp = 12
EqExp = 13
NeExp = 14
LtExp = 15
GtExp = 16
LeExp = 17
GeExp = 18
InExp = 19
IsExp = 20

# TAccess
PrivateAccess = 0
ProtectedAccess = 1
PublicAccess = 2
PublishedAccess = 3
AutomatedAccess = 4

# TStyle
ProcedureStyle = 0
FunctionStyle = 1
ConstructorStyle = 2
DestructorStyle = 3

# TCall
RegisterCall = 0
PascalCall = 1
CdeclCall = 2
StdcallCall = 3
SafecallCall = 4

# TParamMode
VarParam = 0
ConstParam = 1
OutParam = 2
ValueParam = 3

# TDeclTag

# TModuleKind

class TBasic (object) :
   _fields_ = []
   def __init__ (self) :
      self.src_file = 0
      self.src_line = 0
      self.src_column = 0

class TExpr (object) :
   _fields_ = []
   def __init__ (self) :
      self.fce = 0

class TBinaryExpr (TExpr) :
   _fields_ = ["left", "right"]
   def __init__ (self) :
      super (TBinaryExpr, self).__init__ ()
      self.left = None
      self.right = None

class TComponentsItem (object) :
   _fields_ = ["members"]
   def __init__ (self) :
      self.acs = 0
      self.members = None

class TParamItem (object) :
   _fields_ = ["items", "typ", "ini"]
   def __init__ (self) :
      self.mode = 0
      self.items = [ ]
      self.typ = None
      self.ini = None

class TModule (object) :
   _fields_ = ["intf_imports", "impl_imports", "intf_decl", "impl_decl", "init", "finish"]
   def __init__ (self) :
      self.intf_imports = None
      self.impl_imports = None
      self.intf_decl = None
      self.impl_decl = None
      self.init = None
      self.finish = None

class TLabelIdent (object) :
   _fields_ = []
   def __init__ (self) :
      self.id = ""

class TQualName (object) :
   _fields_ = ["items"]
   def __init__ (self) :
      self.id = ""
      self.items = [ ]

class TContName (object) :
   _fields_ = []
   def __init__ (self) :
      self.id = ""

class TType (object) :
   _fields_ = []
   def __init__ (self) :
      pass

class TAliasType (TType) :
   _fields_ = ["alias_name"]
   def __init__ (self) :
      super (TAliasType, self).__init__ ()
      self.alias_name = None

class TStringType (TType) :
   _fields_ = ["lim"]
   def __init__ (self) :
      super (TStringType, self).__init__ ()
      self.lim = None

class TFileType (TType) :
   _fields_ = ["elem"]
   def __init__ (self) :
      super (TFileType, self).__init__ ()
      self.elem = None

class TInxItem (object) :
   _fields_ = ["ref"]
   def __init__ (self) :
      self.ref = None

class TInxList (object) :
   _fields_ = ["items"]
   def __init__ (self) :
      self.items = [ ]

class TArgItem (object) :
   _fields_ = ["value", "width", "digits"]
   def __init__ (self) :
      self.value = None
      self.width = None
      self.digits = None

class TArgSect (object) :
   _fields_ = ["items"]
   def __init__ (self) :
      self.items = [ ]

class TElemSect (object) :
   _fields_ = ["items"]
   def __init__ (self) :
      self.items = [ ]

class TElemItem (object) :
   _fields_ = ["low", "high"]
   def __init__ (self) :
      self.low = None
      self.high = None

class TStructSect (object) :
   _fields_ = ["value", "items"]
   def __init__ (self) :
      self.name = ""
      self.value = None
      self.items = [ ]

class TIdentExpr (TExpr) :
   _fields_ = []
   def __init__ (self) :
      super (TIdentExpr, self).__init__ ()
      self.name = ""

class TIntValueExpr (TExpr) :
   _fields_ = []
   def __init__ (self) :
      super (TIntValueExpr, self).__init__ ()
      self.value = ""

class TFltValueExpr (TExpr) :
   _fields_ = []
   def __init__ (self) :
      super (TFltValueExpr, self).__init__ ()
      self.value = ""

class TStrValueExpr (TExpr) :
   _fields_ = []
   def __init__ (self) :
      super (TStrValueExpr, self).__init__ ()
      self.value = ""

class TNilExpr (TExpr) :
   _fields_ = []
   def __init__ (self) :
      super (TNilExpr, self).__init__ ()

class TStructExpr (TExpr) :
   _fields_ = ["value"]
   def __init__ (self) :
      super (TStructExpr, self).__init__ ()
      self.value = None

class TNotExpr (TExpr) :
   _fields_ = ["param"]
   def __init__ (self) :
      super (TNotExpr, self).__init__ ()
      self.param = None

class TPlusExpr (TExpr) :
   _fields_ = ["param"]
   def __init__ (self) :
      super (TPlusExpr, self).__init__ ()
      self.param = None

class TMinusExpr (TExpr) :
   _fields_ = ["param"]
   def __init__ (self) :
      super (TMinusExpr, self).__init__ ()
      self.param = None

class TAdrExpr (TExpr) :
   _fields_ = ["param"]
   def __init__ (self) :
      super (TAdrExpr, self).__init__ ()
      self.param = None

class TSetExpr (TExpr) :
   _fields_ = ["list"]
   def __init__ (self) :
      super (TSetExpr, self).__init__ ()
      self.list = None

class TSuperExpr (TExpr) :
   _fields_ = []
   def __init__ (self) :
      super (TSuperExpr, self).__init__ ()
      self.name = ""

class TStringExpr (TExpr) :
   _fields_ = ["param"]
   def __init__ (self) :
      super (TStringExpr, self).__init__ ()
      self.param = None

class TIndexExpr (TExpr) :
   _fields_ = ["left", "list"]
   def __init__ (self) :
      super (TIndexExpr, self).__init__ ()
      self.left = None
      self.list = None

class TCallExpr (TExpr) :
   _fields_ = ["func", "list"]
   def __init__ (self) :
      super (TCallExpr, self).__init__ ()
      self.func = None
      self.list = None

class TDerefExpr (TExpr) :
   _fields_ = ["param"]
   def __init__ (self) :
      super (TDerefExpr, self).__init__ ()
      self.param = None

class TFieldExpr (TExpr) :
   _fields_ = ["param"]
   def __init__ (self) :
      super (TFieldExpr, self).__init__ ()
      self.param = None
      self.name = ""

class TStat (object) :
   _fields_ = []
   def __init__ (self) :
      pass

class TGotoStat (TStat) :
   _fields_ = ["goto_lab"]
   def __init__ (self) :
      super (TGotoStat, self).__init__ ()
      self.goto_lab = None

class TBlockStat (TStat) :
   _fields_ = ["body_seq"]
   def __init__ (self) :
      super (TBlockStat, self).__init__ ()
      self.body_seq = None

class TStatSeq (object) :
   _fields_ = ["items"]
   def __init__ (self) :
      self.items = [ ]

class TIfStat (TStat) :
   _fields_ = ["cond_expr", "then_stat", "else_stat"]
   def __init__ (self) :
      super (TIfStat, self).__init__ ()
      self.cond_expr = None
      self.then_stat = None
      self.else_stat = None

class TCaseStat (TStat) :
   _fields_ = ["case_expr", "case_list", "else_seq"]
   def __init__ (self) :
      super (TCaseStat, self).__init__ ()
      self.case_expr = None
      self.case_list = None
      self.else_seq = None

class TCaseSect (object) :
   _fields_ = ["items"]
   def __init__ (self) :
      self.items = [ ]

class TCaseItem (object) :
   _fields_ = ["sel_list", "sel_stat"]
   def __init__ (self) :
      self.sel_list = None
      self.sel_stat = None

class TWhileStat (TStat) :
   _fields_ = ["cond_expr", "body_stat"]
   def __init__ (self) :
      super (TWhileStat, self).__init__ ()
      self.cond_expr = None
      self.body_stat = None

class TRepeatStat (TStat) :
   _fields_ = ["body_seq", "until_expr"]
   def __init__ (self) :
      super (TRepeatStat, self).__init__ ()
      self.body_seq = None
      self.until_expr = None

class TForStat (TStat) :
   _fields_ = ["var_expr", "from_expr", "to_expr", "body_stat"]
   def __init__ (self) :
      super (TForStat, self).__init__ ()
      self.var_expr = None
      self.from_expr = None
      self.incr = False
      self.to_expr = None
      self.body_stat = None

class TWithStat (TStat) :
   _fields_ = ["with_list", "body_stat"]
   def __init__ (self) :
      super (TWithStat, self).__init__ ()
      self.with_list = None
      self.body_stat = None

class TWithSect (object) :
   _fields_ = ["items"]
   def __init__ (self) :
      self.items = [ ]

class TWithItem (object) :
   _fields_ = ["expr"]
   def __init__ (self) :
      self.expr = None

class TRaiseStat (TStat) :
   _fields_ = ["raise_expr"]
   def __init__ (self) :
      super (TRaiseStat, self).__init__ ()
      self.raise_expr = None

class TTryStat (TStat) :
   _fields_ = ["body_seq", "finally_branch", "except_branch"]
   def __init__ (self) :
      super (TTryStat, self).__init__ ()
      self.body_seq = None
      self.finally_branch = None
      self.except_branch = None

class TFinallyPart (object) :
   _fields_ = ["finally_seq"]
   def __init__ (self) :
      self.finally_seq = None

class TExceptPart (object) :
   _fields_ = ["on_list", "else_seq"]
   def __init__ (self) :
      self.on_list = None
      self.else_seq = None

class TOnSect (object) :
   _fields_ = ["items"]
   def __init__ (self) :
      self.items = [ ]
      self.semicolon = False

class TOnItem (object) :
   _fields_ = ["on_type", "body_stat"]
   def __init__ (self) :
      self.on_ident = ""
      self.on_type = None
      self.body_stat = None

class TEmptyStat (TStat) :
   _fields_ = []
   def __init__ (self) :
      super (TEmptyStat, self).__init__ ()

class TAssignStat (TStat) :
   _fields_ = ["left_expr", "right_expr"]
   def __init__ (self) :
      super (TAssignStat, self).__init__ ()
      self.left_expr = None
      self.right_expr = None

class TCallStat (TStat) :
   _fields_ = ["call_expr"]
   def __init__ (self) :
      super (TCallStat, self).__init__ ()
      self.call_expr = None

class TLabeledTStat (TStat) :
   _fields_ = ["lab", "body"]
   def __init__ (self) :
      super (TLabeledTStat, self).__init__ ()
      self.lab = None
      self.body = None

class TParamIdent (object) :
   _fields_ = []
   def __init__ (self) :
      self.name = ""

class TParamSect (object) :
   _fields_ = ["items"]
   def __init__ (self) :
      self.items = [ ]

class TClassType (TType) :
   _fields_ = ["parent", "ifc_list", "components"]
   def __init__ (self) :
      super (TClassType, self).__init__ ()
      self.parent = None
      self.ifc_list = None
      self.components = None

class TInterfaceType (TType) :
   _fields_ = ["ifc_list", "components"]
   def __init__ (self) :
      super (TInterfaceType, self).__init__ ()
      self.ifc_list = None
      self.components = None

class TInterfaceSect (object) :
   _fields_ = ["items"]
   def __init__ (self) :
      self.items = [ ]

class TIntefaceItem (object) :
   _fields_ = ["ifc"]
   def __init__ (self) :
      self.ifc = None

class TComponetsSect (object) :
   _fields_ = ["items"]
   def __init__ (self) :
      self.items = [ ]

class TDeclGroup (object) :
   _fields_ = ["items"]
   def __init__ (self) :
      self.items = [ ]

class TDeclSect (object) :
   _fields_ = []
   def __init__ (self) :
      pass

class TFieldItem (object) :
   _fields_ = []
   def __init__ (self) :
      self.name = ""

class TFieldDecl (TDeclSect) :
   _fields_ = ["items", "typ"]
   def __init__ (self) :
      super (TFieldDecl, self).__init__ ()
      self.items = [ ]
      self.typ = None

class TPropertyDecl (TDeclSect) :
   _fields_ = ["param_list", "typ", "a_read", "a_write", "a_implements"]
   def __init__ (self) :
      super (TPropertyDecl, self).__init__ ()
      self.name = ""
      self.param_list = None
      self.typ = None
      self.a_read = None
      self.a_write = None
      self.a_stored = False
      self.a_default = False
      self.a_nodefault = False
      self.a_implements = None
      self.a_def_array = False

class TEnumType (TType) :
   _fields_ = ["elements"]
   def __init__ (self) :
      super (TEnumType, self).__init__ ()
      self.elements = None

class TEnumSect (object) :
   _fields_ = ["items"]
   def __init__ (self) :
      self.items = [ ]

class TEnumItem (object) :
   _fields_ = []
   def __init__ (self) :
      self.name = ""

class TArrayType (TType) :
   _fields_ = ["index_list", "elem"]
   def __init__ (self) :
      super (TArrayType, self).__init__ ()
      self.index_list = None
      self.elem = None

class TIndexTypeSect (object) :
   _fields_ = ["items"]
   def __init__ (self) :
      self.items = [ ]

class TIndexTypeItem (object) :
   _fields_ = ["index"]
   def __init__ (self) :
      self.index = None

class TRecordType (TType) :
   _fields_ = ["fields"]
   def __init__ (self) :
      super (TRecordType, self).__init__ ()
      self.a_packed = False
      self.fields = None

class TFieldDeclGroup (object) :
   _fields_ = ["items"]
   def __init__ (self) :
      self.items = [ ]

class TPointerType (TType) :
   _fields_ = ["elem"]
   def __init__ (self) :
      super (TPointerType, self).__init__ ()
      self.elem = None

class TSetType (TType) :
   _fields_ = ["elem"]
   def __init__ (self) :
      super (TSetType, self).__init__ ()
      self.elem = None

class TClassOfType (TType) :
   _fields_ = ["elem"]
   def __init__ (self) :
      super (TClassOfType, self).__init__ ()
      self.elem = None

class TProcType (TType) :
   _fields_ = ["param_list", "answer"]
   def __init__ (self) :
      super (TProcType, self).__init__ ()
      self.style = 0
      self.call_conv = 0
      self.param_list = None
      self.answer = None
      self.of_object = False

class TSubrangeType (TType) :
   _fields_ = ["low", "high"]
   def __init__ (self) :
      super (TSubrangeType, self).__init__ ()
      self.low = None
      self.high = None

class TLabelDecl (object) :
   _fields_ = ["name"]
   def __init__ (self) :
      self.name = None

class TLabelSect (TDeclSect) :
   _fields_ = ["items"]
   def __init__ (self) :
      super (TLabelSect, self).__init__ ()
      self.items = [ ]

class TConstDecl (object) :
   _fields_ = ["typ", "val"]
   def __init__ (self) :
      self.name = ""
      self.typ = None
      self.val = None

class TConstSect (TDeclSect) :
   _fields_ = ["items"]
   def __init__ (self) :
      super (TConstSect, self).__init__ ()
      self.items = [ ]

class TTypeDecl (object) :
   _fields_ = ["typ"]
   def __init__ (self) :
      self.name = ""
      self.typ = None

class TTypeSect (TDeclSect) :
   _fields_ = ["items"]
   def __init__ (self) :
      super (TTypeSect, self).__init__ ()
      self.items = [ ]

class TVarItem (object) :
   _fields_ = []
   def __init__ (self) :
      self.name = ""

class TVarDecl (object) :
   _fields_ = ["items", "typ", "ini"]
   def __init__ (self) :
      self.items = [ ]
      self.typ = None
      self.ini = None

class TVarSect (TDeclSect) :
   _fields_ = ["items"]
   def __init__ (self) :
      super (TVarSect, self).__init__ ()
      self.items = [ ]

class TProcDecl (TDeclSect) :
   _fields_ = ["proc_name", "param_list", "answer", "local", "body", "a_lib"]
   def __init__ (self) :
      super (TProcDecl, self).__init__ ()
      self.style = 0
      self.call_conv = 0
      self.a_virtual = False
      self.a_dynamic = False
      self.a_override = False
      self.a_abstract = False
      self.a_static = False
      self.proc_name = None
      self.param_list = None
      self.answer = None
      self.a_forward = False
      self.external_spec = False
      self.a_inline = False
      self.local = None
      self.body = None
      self.a_external = False
      self.a_lib = None

class TImportItem (object) :
   _fields_ = []
   def __init__ (self) :
      self.name = ""
      self.path = ""

class TImportSect (object) :
   _fields_ = ["items"]
   def __init__ (self) :
      self.items = [ ]

class TUnitModule (TModule) :
   _fields_ = ["intf_imports", "impl_imports", "intf_decl", "impl_decl", "init", "finish"]
   def __init__ (self) :
      super (TUnitModule, self).__init__ ()
      self.name = ""
      self.no_begin = False

class TProgramModule (TModule) :
   _fields_ = ["intf_imports", "impl_imports", "intf_decl", "impl_decl", "init", "finish"]
   def __init__ (self) :
      super (TProgramModule, self).__init__ ()
      self.name = ""

class TLibraryModule (TModule) :
   _fields_ = ["intf_imports", "impl_imports", "intf_decl", "impl_decl", "init", "finish"]
   def __init__ (self) :
      super (TLibraryModule, self).__init__ ()
      self.name = ""

class TTermExpr (TBinaryExpr) :
   _fields_ = ["left", "right"]
   def __init__ (self) :
      super (TTermExpr, self).__init__ ()

class TSimpleExpr (TBinaryExpr) :
   _fields_ = ["left", "right"]
   def __init__ (self) :
      super (TSimpleExpr, self).__init__ ()

class TCompleteExpr (TBinaryExpr) :
   _fields_ = ["left", "right"]
   def __init__ (self) :
      super (TCompleteExpr, self).__init__ ()

