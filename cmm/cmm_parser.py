
from lexer import Lexer

class Parser (Lexer) :
   def parse_simple_name (self) :
      result = CmmSimpleName ()
      self.storeLocation (result)
      result.id = self.readIdentifier ()
      return result

   def parse_global_variant (self) :
      if self.token == self.identifier :
         result = self.parse_simple_name ()
      elif self.token == self.keyword_operator :
         result = self.parse_special_function ()
      else :
         self.error ("Unexpected token")
      return result

   def parse_global_name (self) :
      result = CmmGlobalName ()
      self.storeLocation (result)
      self.checkToken (self.SCOPE)
      result.inner_name = self.parse_global_variant ()
      return result

   def parse_base_variant (self) :
      if self.token == self.SCOPE :
         result = self.parse_global_name ()
      elif self.token == self.identifier :
         result = self.parse_simple_name ()
      elif self.token == self.keyword_operator :
         result = self.parse_special_function ()
      else :
         self.error ("Unexpected token")
      return result

   def parse_base_name (self) :
      result = self.parse_base_variant ()
      self.on_base_name (result)
      return result

   def parse_destructor_name (self) :
      result = CmmDestructorName ()
      self.storeLocation (result)
      self.checkToken (self.BIT_NOT)
      result.inner_name = self.parse_simple_name ()
      return result

   def parse_cont_variant (self) :
      if self.token == self.identifier :
         result = self.parse_simple_name ()
      elif self.token == self.keyword_operator :
         result = self.parse_special_function ()
      elif self.token == self.BIT_NOT :
         result = self.parse_destructor_name ()
      else :
         self.error ("Unexpected token")
      return result

   def parse_cont_name (self, store) :
      result = CmmCompoundName ()
      self.storeLocation (result)
      result.left = store
      self.checkToken (self.SCOPE)
      result.right = self.parse_cont_variant ()
      self.on_cont_name (result)
      return result

   def parse_template_name (self, store) :
      result = CmmTemplateName ()
      self.storeLocation (result)
      result.left = store
      result.template_args = self.parse_template_arg_list ()
      self.on_template_name (result)
      return result

   def parse_field_name (self) :
      result = self.parse_simple_name ()
      while self.token == self.LESS and self.is_template_name (result) :
         result = self.parse_template_name (result)
         self.on_base_name (result)
      return result

   def parse_qualified_name (self) :
      result = self.parse_base_name ()
      while self.token == self.SCOPE or self.token == self.LESS and self.is_template_name (result) :
         if self.token == self.SCOPE :
            result = self.parse_cont_name (result)
            self.on_base_name (result)
         elif self.token == self.LESS and self.is_template_name (result) :
            result = self.parse_template_name (result)
            self.on_base_name (result)
         else :
            self.error ("Unexpected token")
      return result

   def parse_new_qualified_name (self) :
      result = self.parse_base_variant ()
      while self.token == self.SCOPE or self.token == self.LESS and self.is_template_name (result) :
         if self.token == self.SCOPE :
            self.on_base_name (result)
            result = self.parse_cont_name (result)
         elif self.token == self.LESS and self.is_template_name (result) :
            self.on_base_name (result)
            result = self.parse_template_name (result)
         else :
            self.error ("Unexpected token")
      return result

   def parse_primary_expr (self) :
      if self.token == self.identifier or self.token == self.SCOPE or self.token == self.keyword_operator :
         result = self.parse_ident_expr ()
      elif self.token == self.number :
         result = self.parse_int_value ()
      elif self.token == self.real_number :
         result = self.parse_real_value ()
      elif self.token == self.character_literal :
         result = self.parse_char_value ()
      elif self.token == self.string_literal :
         result = self.parse_string_value ()
      elif self.token == self.keyword_this :
         result = self.parse_this_expr ()
      elif self.token == self.LBRACKET :
         result = self.parse_lambda_expr ()
      elif self.token == self.LPAREN :
         result = self.parse_subexpr_expr ()
      else :
         self.error ("Unexpected token")
      return result

   def parse_ident_expr (self) :
      result = self.parse_qualified_name ()
      self.on_ident_expr (result)
      return result

   def parse_int_value (self) :
      result = CmmIntValue ()
      self.storeLocation (result)
      result.value = self.readNumber ()
      self.on_int_value (result)
      return result

   def parse_real_value (self) :
      result = CmmRealValue ()
      self.storeLocation (result)
      result.value = self.readReal ()
      self.on_real_value (result)
      return result

   def parse_char_value (self) :
      result = CmmCharValue ()
      self.storeLocation (result)
      result.value = self.readCharacter ()
      self.on_char_value (result)
      return result

   def parse_string_value (self) :
      result = CmmStringValue ()
      self.storeLocation (result)
      result.value = self.readString ()
      while self.token == self.string_literal :
         result.items.append (self.parse_string_value_cont ())
      self.on_string_value (result)
      return result

   def parse_string_value_cont (self) :
      result = CmmStringCont ()
      self.storeLocation (result)
      result.value = self.readString ()
      return result

   def parse_this_expr (self) :
      result = CmmThisExpr ()
      self.storeLocation (result)
      self.checkToken (self.keyword_this)
      self.on_this_expr (result)
      return result

   def parse_lambda_expr (self) :
      result = CmmLambdaExpr ()
      self.storeLocation (result)
      self.checkToken (self.LBRACKET)
      if self.token == self.BIT_AND :
         self.checkToken (self.BIT_AND)
         result.by_reference = True
      self.checkToken (self.RBRACKET)
      result.body = self.parse_compound_stat ()
      return result

   def parse_subexpr_expr (self) :
      result = CmmSubexprExpr ()
      self.storeLocation (result)
      self.checkToken (self.LPAREN)
      result.param = self.parse_expr ()
      self.checkToken (self.RPAREN)
      self.on_subexpr_expr (result)
      return result

   def parse_postfix_start (self) :
      if self.token == self.identifier and self.is_signal_slot () :
         result = self.parse_signal_slot_expr ()
      elif self.set_0 & 1 << self.token :
         result = self.parse_primary_expr ()
      elif self.set_1 & 1 << self.token :
         result = self.parse_modern_cast_expr ()
      elif self.token == self.keyword_typeid :
         result = self.parse_typeid_expr ()
      elif self.token == self.keyword_typename :
         result = self.parse_type_name ()
      elif self.set_2 & 1 << self.token :
         result = self.parse_type_specifier ()
      elif self.token == self.keyword_const :
         result = self.parse_const_specifier ()
      elif self.token == self.keyword_volatile :
         result = self.parse_volatile_specifier ()
      elif self.set_3 & 1 << self.token :
         result = self.parse_decl_specifier ()
      else :
         self.error ("Unexpected token")
      return result

   def parse_signal_slot_expr (self) :
      result = CmmSignalSlotExpr ()
      self.storeLocation (result)
      result.macro_name = self.readIdentifier ()
      self.checkToken (self.LPAREN)
      result.func_name = self.readIdentifier ()
      if self.token == self.LPAREN :
         self.checkToken (self.LPAREN)
         result.parameters = self.parse_parameter_declaration_list ()
         self.checkToken (self.RPAREN)
      self.checkToken (self.RPAREN)
      return result

   def parse_modern_cast_expr (self) :
      result = CmmModernCastExpr ()
      self.storeLocation (result)
      if self.token == self.keyword_dynamic_cast :
         self.checkToken (self.keyword_dynamic_cast)
         result.cast_kind = dynamicCast
      elif self.token == self.keyword_static_cast :
         self.checkToken (self.keyword_static_cast)
         result.cast_kind = staticCast
      elif self.token == self.keyword_const_cast :
         self.checkToken (self.keyword_const_cast)
         result.cast_kind = constCast
      elif self.token == self.keyword_reinterpret_cast :
         self.checkToken (self.keyword_reinterpret_cast)
         result.cast_kind = reinterpreterCast
      else :
         self.error ("Unexpected token")
      self.checkToken (self.LESS)
      result.type = self.parse_type_id ()
      self.checkToken (self.GREATER)
      self.checkToken (self.LPAREN)
      result.param = self.parse_expr ()
      self.checkToken (self.RPAREN)
      self.on_modern_cast_expr (result)
      return result

   def parse_typeid_expr (self) :
      result = CmmTypeIdExpr ()
      self.storeLocation (result)
      self.checkToken (self.keyword_typeid)
      self.checkToken (self.LPAREN)
      result.value = self.parse_expr ()
      self.checkToken (self.RPAREN)
      self.on_typeid_expr (result)
      return result

   def parse_postfix_expr (self) :
      result = self.parse_postfix_start ()
      if self.is_postfix_expression (result) :
         while self.token == self.LBRACKET or self.token == self.LPAREN or self.token == self.DOT or self.token == self.ARROW or self.token == self.INC or self.token == self.DEC :
            if self.token == self.LBRACKET :
               result = self.parse_index_expr (result)
            elif self.token == self.LPAREN :
               result = self.parse_call_expr (result)
            elif self.token == self.DOT :
               result = self.parse_field_expr (result)
            elif self.token == self.ARROW :
               result = self.parse_ptr_field_expr (result)
            elif self.token == self.INC :
               result = self.parse_post_inc_expr (result)
            elif self.token == self.DEC :
               result = self.parse_post_dec_expr (result)
            else :
               self.error ("Unexpected token")
      return result

   def parse_index_expr (self, store) :
      result = CmmIndexExpr ()
      self.storeLocation (result)
      result.left = store
      self.checkToken (self.LBRACKET)
      result.param = self.parse_expr ()
      self.checkToken (self.RBRACKET)
      self.on_index_expr (result)
      return result

   def parse_call_expr (self, store) :
      result = CmmCallExpr ()
      self.storeLocation (result)
      result.left = store
      self.checkToken (self.LPAREN)
      result.param_list = self.parse_expr_list ()
      self.checkToken (self.RPAREN)
      self.on_call_expr (result)
      return result

   def parse_field_expr (self, store) :
      result = CmmFieldExpr ()
      self.storeLocation (result)
      result.left = store
      self.checkToken (self.DOT)
      result.field_name = self.parse_field_name ()
      self.on_field_expr (result)
      return result

   def parse_ptr_field_expr (self, store) :
      result = CmmPtrFieldExpr ()
      self.storeLocation (result)
      result.left = store
      self.checkToken (self.ARROW)
      result.field_name = self.parse_field_name ()
      self.on_ptr_field_expr (result)
      return result

   def parse_post_inc_expr (self, store) :
      result = CmmPostIncExpr ()
      self.storeLocation (result)
      result.left = store
      self.checkToken (self.INC)
      self.on_post_inc_expr (result)
      return result

   def parse_post_dec_expr (self, store) :
      result = CmmPostDecExpr ()
      self.storeLocation (result)
      result.left = store
      self.checkToken (self.DEC)
      self.on_post_dec_expr (result)
      return result

   def parse_expr_list (self) :
      result = CmmExprList ()
      self.storeLocation (result)
      if self.set_5 & 1 << self.token :
         result.items.append (self.parse_assignment_expr ())
         while self.token == self.COMMA :
            self.checkToken (self.COMMA)
            result.items.append (self.parse_assignment_expr ())
      return result

   def parse_unary_expr (self) :
      if self.set_6 & 1 << self.token :
         result = self.parse_postfix_expr ()
      elif self.token == self.INC :
         result = self.parse_inc_expr ()
      elif self.token == self.DEC :
         result = self.parse_dec_expr ()
      elif self.token == self.STAR :
         result = self.parse_deref_expr ()
      elif self.token == self.BIT_AND :
         result = self.parse_addr_expr ()
      elif self.token == self.PLUS :
         result = self.parse_plus_expr ()
      elif self.token == self.MINUS :
         result = self.parse_minus_expr ()
      elif self.token == self.BIT_NOT :
         result = self.parse_bit_not_expr ()
      elif self.token == self.LOG_NOT :
         result = self.parse_log_not_expr ()
      elif self.token == self.keyword_sizeof :
         result = self.parse_sizeof_expr ()
      elif self.token == self.keyword_new :
         result = self.parse_allocation_expr ()
      elif self.token == self.keyword_delete :
         result = self.parse_deallocation_expr ()
      elif self.token == self.keyword_throw :
         result = self.parse_throw_expr ()
      else :
         self.error ("Unexpected token")
      return result

   def parse_inc_expr (self) :
      result = CmmIncExpr ()
      self.storeLocation (result)
      self.checkToken (self.INC)
      result.param = self.parse_cast_expr ()
      self.on_inc_expr (result)
      return result

   def parse_dec_expr (self) :
      result = CmmDecExpr ()
      self.storeLocation (result)
      self.checkToken (self.DEC)
      result.param = self.parse_cast_expr ()
      self.on_dec_expr (result)
      return result

   def parse_deref_expr (self) :
      result = CmmDerefExpr ()
      self.storeLocation (result)
      self.checkToken (self.STAR)
      result.param = self.parse_cast_expr ()
      self.on_deref_expr (result)
      return result

   def parse_addr_expr (self) :
      result = CmmAddrExpr ()
      self.storeLocation (result)
      self.checkToken (self.BIT_AND)
      result.param = self.parse_cast_expr ()
      self.on_addr_expr (result)
      return result

   def parse_plus_expr (self) :
      result = CmmPlusExpr ()
      self.storeLocation (result)
      self.checkToken (self.PLUS)
      result.param = self.parse_cast_expr ()
      self.on_plus_expr (result)
      return result

   def parse_minus_expr (self) :
      result = CmmMinusExpr ()
      self.storeLocation (result)
      self.checkToken (self.MINUS)
      result.param = self.parse_cast_expr ()
      self.on_minus_expr (result)
      return result

   def parse_bit_not_expr (self) :
      result = CmmBitNotExpr ()
      self.storeLocation (result)
      self.checkToken (self.BIT_NOT)
      self.on_middle_bit_not_expr (result)
      result.param = self.parse_cast_expr ()
      self.on_bit_not_expr (result)
      return result

   def parse_log_not_expr (self) :
      result = CmmLogNotExpr ()
      self.storeLocation (result)
      self.checkToken (self.LOG_NOT)
      result.param = self.parse_cast_expr ()
      self.on_log_not_expr (result)
      return result

   def parse_sizeof_expr (self) :
      result = CmmSizeofExpr ()
      self.storeLocation (result)
      self.checkToken (self.keyword_sizeof)
      result.value = self.parse_unary_expr ()
      self.on_sizeof_expr (result)
      return result

   def parse_allocation_expr (self) :
      result = CmmNewExpr ()
      self.storeLocation (result)
      self.checkToken (self.keyword_new)
      if self.set_7 & 1 << self.token :
         result.type1 = self.parse_new_type_id ()
      elif self.token == self.LPAREN :
         self.checkToken (self.LPAREN)
         result.type2 = self.parse_type_id ()
         self.checkToken (self.RPAREN)
      else :
         self.error ("Unexpected token")
      if self.token == self.LPAREN :
         self.checkToken (self.LPAREN)
         result.init_list = self.parse_expr_list ()
         self.checkToken (self.RPAREN)
      self.on_allocation_expr (result)
      return result

   def parse_new_type_id (self) :
      result = CmmNewTypeId ()
      self.storeLocation (result)
      result.type_spec = self.parse_type_specifiers ()
      result.ptr = self.parse_ptr_specifier_list ()
      while self.token == self.LBRACKET :
         result.items.append (self.parse_allocation_array_limit ())
      return result

   def parse_allocation_array_limit (self) :
      result = CmmNewArrayLimit ()
      self.storeLocation (result)
      self.checkToken (self.LBRACKET)
      result.value = self.parse_expr ()
      self.checkToken (self.RBRACKET)
      return result

   def parse_deallocation_expr (self) :
      result = CmmDeleteExpr ()
      self.storeLocation (result)
      self.checkToken (self.keyword_delete)
      if self.token == self.LBRACKET :
         self.checkToken (self.LBRACKET)
         self.checkToken (self.RBRACKET)
         result.a_array = True
      result.param = self.parse_cast_expr ()
      self.on_deallocation_expr (result)
      return result

   def parse_cast_expr (self) :
      result = self.parse_unary_expr ()
      if self.is_cast_expression (result) :
         if self.set_5 & 1 << self.token :
            store = result
            result = CmmCastExpr ()
            self.storeLocation (result)
            result.left = store
            result.kind = castExpr
            result.right = self.parse_cast_expr ()
      return result

   def parse_pm_expr (self) :
      result = self.parse_cast_expr ()
      if self.is_binary_expression (result) :
         while self.token == self.DOT_STAR or self.token == self.ARROW_STAR :
            store = result
            result = CmmPtrMemExpr ()
            self.storeLocation (result)
            result.left = store
            if self.token == self.DOT_STAR :
               self.checkToken (self.DOT_STAR)
               result.kind = dotMemberExpr
            elif self.token == self.ARROW_STAR :
               self.checkToken (self.ARROW_STAR)
               result.kind = arrowMemberExpr
            else :
               self.error ("Unexpected token")
            result.right = self.parse_cast_expr ()
            self.on_binary_expr (result)
      return result

   def parse_multiplicative_expr (self) :
      result = self.parse_pm_expr ()
      if self.is_binary_expression (result) :
         while self.token == self.STAR or self.token == self.SLASH or self.token == self.MOD or self.token == self.identifier and self.is_mul () :
            store = result
            result = CmmMulExpr ()
            self.storeLocation (result)
            result.left = store
            if self.token == self.STAR :
               self.checkToken (self.STAR)
               result.kind = mulExpr
            elif self.token == self.SLASH :
               self.checkToken (self.SLASH)
               result.kind = divExpr
            elif self.token == self.MOD :
               self.checkToken (self.MOD)
               result.kind = modExpr
            elif self.token == self.identifier and self.is_mul () :
               result.kind = customMulExpr
               result.custom_mul = self.readIdentifier ()
            else :
               self.error ("Unexpected token")
            result.right = self.parse_pm_expr ()
            self.on_binary_expr (result)
      return result

   def parse_additive_expr (self) :
      result = self.parse_multiplicative_expr ()
      if self.is_binary_expression (result) :
         while self.token == self.PLUS or self.token == self.MINUS or self.token == self.identifier and self.is_add () :
            store = result
            result = CmmAddExpr ()
            self.storeLocation (result)
            result.left = store
            if self.token == self.PLUS :
               self.checkToken (self.PLUS)
               result.kind = addExpr
            elif self.token == self.MINUS :
               self.checkToken (self.MINUS)
               result.kind = subExpr
            elif self.token == self.identifier and self.is_add () :
               result.kind = customAddExpr
               result.custom_add = self.readIdentifier ()
            else :
               self.error ("Unexpected token")
            result.right = self.parse_multiplicative_expr ()
            self.on_binary_expr (result)
      return result

   def parse_shift_expr (self) :
      result = self.parse_additive_expr ()
      if self.is_binary_expression (result) :
         while self.token == self.SHL or self.token == self.SHR :
            store = result
            result = CmmShiftExpr ()
            self.storeLocation (result)
            result.left = store
            if self.token == self.SHL :
               self.checkToken (self.SHL)
               result.kind = shlExpr
            elif self.token == self.SHR :
               self.checkToken (self.SHR)
               result.kind = shrExpr
            else :
               self.error ("Unexpected token")
            result.right = self.parse_additive_expr ()
            self.on_binary_expr (result)
      return result

   def parse_relational_expr (self) :
      result = self.parse_shift_expr ()
      if self.is_binary_expression (result) :
         while self.token == self.LESS or self.token == self.GREATER or self.token == self.LESS_OR_EQUAL or self.token == self.GREATER_OR_EQUAL :
            store = result
            result = CmmRelExpr ()
            self.storeLocation (result)
            result.left = store
            if self.token == self.LESS :
               self.checkToken (self.LESS)
               result.kind = ltExpr
            elif self.token == self.GREATER :
               self.checkToken (self.GREATER)
               result.kind = gtExpr
            elif self.token == self.LESS_OR_EQUAL :
               self.checkToken (self.LESS_OR_EQUAL)
               result.kind = leExpr
            elif self.token == self.GREATER_OR_EQUAL :
               self.checkToken (self.GREATER_OR_EQUAL)
               result.kind = geExpr
            else :
               self.error ("Unexpected token")
            result.right = self.parse_shift_expr ()
            self.on_binary_expr (result)
      return result

   def parse_equality_expr (self) :
      result = self.parse_relational_expr ()
      if self.is_binary_expression (result) :
         while self.token == self.EQUAL or self.token == self.UNEQUAL :
            store = result
            result = CmmEqExpr ()
            self.storeLocation (result)
            result.left = store
            if self.token == self.EQUAL :
               self.checkToken (self.EQUAL)
               result.kind = eqExpr
            elif self.token == self.UNEQUAL :
               self.checkToken (self.UNEQUAL)
               result.kind = neExpr
            else :
               self.error ("Unexpected token")
            result.right = self.parse_relational_expr ()
            self.on_binary_expr (result)
      return result

   def parse_and_expr (self) :
      result = self.parse_equality_expr ()
      if self.is_binary_expression (result) :
         while self.token == self.BIT_AND :
            store = result
            result = CmmAndExpr ()
            self.storeLocation (result)
            result.left = store
            self.checkToken (self.BIT_AND)
            result.kind = bitAndExpr
            result.right = self.parse_equality_expr ()
            self.on_binary_expr (result)
      return result

   def parse_exclusive_or_expr (self) :
      result = self.parse_and_expr ()
      if self.is_binary_expression (result) :
         while self.token == self.BIT_XOR :
            store = result
            result = CmmXorExpr ()
            self.storeLocation (result)
            result.left = store
            self.checkToken (self.BIT_XOR)
            result.kind = bitXorExpr
            result.right = self.parse_and_expr ()
            self.on_binary_expr (result)
      return result

   def parse_inclusive_or_expr (self) :
      result = self.parse_exclusive_or_expr ()
      if self.is_binary_expression (result) :
         while self.token == self.BIT_OR :
            store = result
            result = CmmOrExpr ()
            self.storeLocation (result)
            result.left = store
            self.checkToken (self.BIT_OR)
            result.kind = bitOrExpr
            result.right = self.parse_exclusive_or_expr ()
            self.on_binary_expr (result)
      return result

   def parse_logical_and_expr (self) :
      result = self.parse_inclusive_or_expr ()
      if self.is_binary_expression (result) :
         while self.token == self.LOG_AND :
            store = result
            result = CmmAndAndExpr ()
            self.storeLocation (result)
            result.left = store
            self.checkToken (self.LOG_AND)
            result.kind = logAndExpr
            result.right = self.parse_inclusive_or_expr ()
            self.on_binary_expr (result)
      return result

   def parse_logical_or_expr (self) :
      result = self.parse_logical_and_expr ()
      if self.is_binary_expression (result) :
         while self.token == self.LOG_OR :
            store = result
            result = CmmOrOrExpr ()
            self.storeLocation (result)
            result.left = store
            self.checkToken (self.LOG_OR)
            result.kind = logOrExpr
            result.right = self.parse_logical_and_expr ()
            self.on_binary_expr (result)
      return result

   def parse_assignment_expr (self) :
      result = self.parse_logical_or_expr ()
      if self.is_binary_expression (result) :
         if self.token == self.ASSIGN or self.token == self.PLUS_ASSIGN or self.token == self.MINUS_ASSIGN or self.token == self.MUL_ASSIGN or self.token == self.DIV_ASSIGN or self.token == self.MOD_ASSIGN or self.token == self.SHL_ASSIGN or self.token == self.SHR_ASSIGN or self.token == self.BIT_AND_ASSIGN or self.token == self.BIT_XOR_ASSIGN or self.token == self.BIT_OR_ASSIGN or self.token == self.QUESTION :
            store = result
            result = CmmAssignExpr ()
            self.storeLocation (result)
            result.left = store
            if self.token == self.ASSIGN :
               self.checkToken (self.ASSIGN)
               result.kind = assignExpr
            elif self.token == self.PLUS_ASSIGN :
               self.checkToken (self.PLUS_ASSIGN)
               result.kind = addAssignExpr
            elif self.token == self.MINUS_ASSIGN :
               self.checkToken (self.MINUS_ASSIGN)
               result.kind = subAssignExpr
            elif self.token == self.MUL_ASSIGN :
               self.checkToken (self.MUL_ASSIGN)
               result.kind = mulAssignExpr
            elif self.token == self.DIV_ASSIGN :
               self.checkToken (self.DIV_ASSIGN)
               result.kind = divAssignExpr
            elif self.token == self.MOD_ASSIGN :
               self.checkToken (self.MOD_ASSIGN)
               result.kind = modAssignExpr
            elif self.token == self.SHL_ASSIGN :
               self.checkToken (self.SHL_ASSIGN)
               result.kind = shlAssignExpr
            elif self.token == self.SHR_ASSIGN :
               self.checkToken (self.SHR_ASSIGN)
               result.kind = shrAssignExpr
            elif self.token == self.BIT_AND_ASSIGN :
               self.checkToken (self.BIT_AND_ASSIGN)
               result.kind = andAssignExpr
            elif self.token == self.BIT_XOR_ASSIGN :
               self.checkToken (self.BIT_XOR_ASSIGN)
               result.kind = xorAssignExpr
            elif self.token == self.BIT_OR_ASSIGN :
               self.checkToken (self.BIT_OR_ASSIGN)
               result.kind = orAssignExpr
            elif self.token == self.QUESTION :
               self.checkToken (self.QUESTION)
               result.kind = condExpr
               result.middle = self.parse_assignment_expr ()
               self.checkToken (self.COLON)
            else :
               self.error ("Unexpected token")
            result.right = self.parse_logical_or_expr ()
            self.on_binary_expr (result)
      return result

   def parse_colon_expr (self) :
      result = self.parse_assignment_expr ()
      return result

   def parse_comma_expr (self) :
      result = self.parse_colon_expr ()
      if self.is_binary_expression (result) :
         while self.token == self.COMMA :
            store = result
            result = CmmCommaExpr ()
            self.storeLocation (result)
            result.left = store
            self.checkToken (self.COMMA)
            result.kind = commaExpr
            result.right = self.parse_colon_expr ()
            self.on_binary_expr (result)
      return result

   def parse_expr (self) :
      result = self.parse_comma_expr ()
      self.on_expr (result)
      return result

   def parse_const_expr (self) :
      result = self.parse_assignment_expr ()
      return result

   def parse_stat (self) :
      if self.set_5 & 1 << self.token :
         result = self.parse_flexible_stat ()
      elif self.token == self.SEMICOLON :
         result = self.parse_empty_stat ()
      elif self.token == self.LBRACE :
         result = self.parse_compound_stat ()
      elif self.token == self.keyword_if :
         result = self.parse_if_stat ()
      elif self.token == self.keyword_while :
         result = self.parse_while_stat ()
      elif self.token == self.keyword_do :
         result = self.parse_do_stat ()
      elif self.token == self.keyword_for :
         result = self.parse_for_stat ()
      elif self.token == self.keyword_switch :
         result = self.parse_switch_stat ()
      elif self.token == self.keyword_case :
         result = self.parse_case_stat ()
      elif self.token == self.keyword_default :
         result = self.parse_default_stat ()
      elif self.token == self.keyword_break :
         result = self.parse_break_stat ()
      elif self.token == self.keyword_continue :
         result = self.parse_continue_stat ()
      elif self.token == self.keyword_return :
         result = self.parse_return_stat ()
      elif self.token == self.keyword_goto :
         result = self.parse_goto_stat ()
      elif self.token == self.keyword_try :
         result = self.parse_try_stat ()
      else :
         self.error ("Unexpected token")
      return result

   def parse_nested_stat (self) :
      result = self.parse_stat ()
      return result

   def parse_tail_stat (self) :
      result = self.parse_stat ()
      return result

   def parse_empty_stat (self) :
      result = CmmEmptyStat ()
      self.storeLocation (result)
      self.checkToken (self.SEMICOLON)
      return result

   def parse_compound_stat (self) :
      result = CmmCompoundStat ()
      self.storeLocation (result)
      self.checkToken (self.LBRACE)
      self.on_open_compound_statement (result)
      while self.set_11 & 1 << self.token :
         self.on_declaration (result)
         result.items.append (self.parse_stat ())
      self.on_close_compound_statement (result)
      self.checkToken (self.RBRACE)
      return result

   def parse_if_stat (self) :
      result = CmmIfStat ()
      self.storeLocation (result)
      self.checkToken (self.keyword_if)
      self.checkToken (self.LPAREN)
      result.cond = self.parse_condition ()
      self.checkToken (self.RPAREN)
      self.on_open_if_statement (result)
      result.then_stat = self.parse_nested_stat ()
      if self.token == self.keyword_else :
         self.checkToken (self.keyword_else)
         result.else_stat = self.parse_tail_stat ()
      self.on_close_if_statement (result)
      return result

   def parse_while_stat (self) :
      result = CmmWhileStat ()
      self.storeLocation (result)
      self.checkToken (self.keyword_while)
      self.checkToken (self.LPAREN)
      result.cond = self.parse_condition ()
      self.checkToken (self.RPAREN)
      self.on_open_while_statement (result)
      result.body = self.parse_nested_stat ()
      self.on_close_while_statement (result)
      return result

   def parse_do_stat (self) :
      result = CmmDoStat ()
      self.storeLocation (result)
      self.checkToken (self.keyword_do)
      result.body = self.parse_nested_stat ()
      self.checkToken (self.keyword_while)
      self.checkToken (self.LPAREN)
      result.cond_expr = self.parse_expr ()
      self.checkToken (self.RPAREN)
      self.checkToken (self.SEMICOLON)
      return result

   def parse_for_stat (self) :
      result = CmmForStat ()
      self.storeLocation (result)
      self.checkToken (self.keyword_for)
      self.checkToken (self.LPAREN)
      if self.set_5 & 1 << self.token :
         result.from_expr = self.parse_condition ()
      if self.token == self.COLON :
         self.checkToken (self.COLON)
         result.iter_expr = self.parse_expr ()
      elif self.token == self.SEMICOLON :
         self.checkToken (self.SEMICOLON)
         if self.set_5 & 1 << self.token :
            result.cond_expr = self.parse_expr ()
         self.checkToken (self.SEMICOLON)
         if self.set_5 & 1 << self.token :
            result.step_expr = self.parse_expr ()
      else :
         self.error ("Unexpected token")
      self.checkToken (self.RPAREN)
      self.on_open_for_statement (result)
      result.body = self.parse_nested_stat ()
      self.on_close_for_statement (result)
      return result

   def parse_switch_stat (self) :
      result = CmmSwitchStat ()
      self.storeLocation (result)
      self.checkToken (self.keyword_switch)
      self.checkToken (self.LPAREN)
      result.cond = self.parse_condition ()
      self.checkToken (self.RPAREN)
      self.on_open_switch_statement (result)
      result.body = self.parse_nested_stat ()
      self.on_close_switch_statement (result)
      return result

   def parse_case_stat (self) :
      result = CmmCaseStat ()
      self.storeLocation (result)
      self.checkToken (self.keyword_case)
      result.case_expr = self.parse_expr ()
      self.checkToken (self.COLON)
      result.body = self.parse_nested_stat ()
      return result

   def parse_default_stat (self) :
      result = CmmDefaultStat ()
      self.storeLocation (result)
      self.checkToken (self.keyword_default)
      self.checkToken (self.COLON)
      result.body = self.parse_nested_stat ()
      return result

   def parse_break_stat (self) :
      result = CmmBreakStat ()
      self.storeLocation (result)
      self.checkToken (self.keyword_break)
      self.checkToken (self.SEMICOLON)
      return result

   def parse_continue_stat (self) :
      result = CmmContinueStat ()
      self.storeLocation (result)
      self.checkToken (self.keyword_continue)
      self.checkToken (self.SEMICOLON)
      return result

   def parse_return_stat (self) :
      result = CmmReturnStat ()
      self.storeLocation (result)
      self.checkToken (self.keyword_return)
      if self.set_5 & 1 << self.token :
         result.return_expr = self.parse_expr ()
      self.checkToken (self.SEMICOLON)
      return result

   def parse_goto_stat (self) :
      result = CmmGotoStat ()
      self.storeLocation (result)
      self.checkToken (self.keyword_goto)
      result.goto_lab = self.readIdentifier ()
      self.checkToken (self.SEMICOLON)
      return result

   def parse_flexible_stat (self) :
      self.on_open_flexible_stat ()
      result = self.parse_expr ()
      if (self.token == self.SEMICOLON or self.token == self.LBRACE) and self.is_expression (result) :
         result = self.parse_simple_stat (result)
      elif self.token == self.LPAREN and self.is_constructor (result) :
         result = self.parse_constructor_declaration (result)
      elif self.set_12 & 1 << self.token :
         result = self.parse_simple_declaration (result)
      else :
         self.error ("Unexpected token")
      return result

   def parse_simple_stat (self, store) :
      result = CmmSimpleStat ()
      self.storeLocation (result)
      result.inner_expr = store
      self.on_open_simple_stat (result)
      if self.token == self.LBRACE :
         self.on_open_expr_block (result)
         result.body = self.parse_compound_stat ()
         self.on_close_expr_block (result)
      elif self.token == self.SEMICOLON :
         self.checkToken (self.SEMICOLON)
         self.on_simple_statement (result)
      else :
         self.error ("Unexpected token")
      return result

   def parse_decl_specifier (self) :
      result = CmmDeclSpec ()
      self.storeLocation (result)
      if self.token == self.keyword_inline :
         self.checkToken (self.keyword_inline)
         result.a_inline = True
      elif self.token == self.keyword_virtual :
         self.checkToken (self.keyword_virtual)
         result.a_virtual = True
      elif self.token == self.keyword_explicit :
         self.checkToken (self.keyword_explicit)
         result.a_explicit = True
      elif self.token == self.keyword_mutable :
         self.checkToken (self.keyword_mutable)
         result.a_mutable = True
      elif self.token == self.keyword_static :
         self.checkToken (self.keyword_static)
         result.a_static = True
      elif self.token == self.keyword_register :
         self.checkToken (self.keyword_register)
         result.a_register = True
      else :
         self.error ("Unexpected token")
      if self.token == self.BIT_NOT :
         self.checkToken (self.BIT_NOT)
         result.a_destructor = True
         self.on_middle_decl_specifier (result)
      result.param = self.parse_type_specifiers ()
      self.on_decl_specifier (result)
      return result

   def parse_const_specifier (self) :
      result = CmmConstSpecifier ()
      self.storeLocation (result)
      self.checkToken (self.keyword_const)
      result.param = self.parse_type_specifiers ()
      self.on_const_specifier (result)
      return result

   def parse_volatile_specifier (self) :
      result = CmmVolatileSpecifier ()
      self.storeLocation (result)
      self.checkToken (self.keyword_volatile)
      result.param = self.parse_type_specifiers ()
      self.on_volatile_specifier (result)
      return result

   def parse_type_specifier (self) :
      result = CmmTypeSpec ()
      self.storeLocation (result)
      if self.token == self.keyword_signed or self.token == self.keyword_unsigned :
         if self.token == self.keyword_signed :
            self.checkToken (self.keyword_signed)
            result.a_signed = True
         elif self.token == self.keyword_unsigned :
            self.checkToken (self.keyword_unsigned)
            result.a_unsigned = True
         else :
            self.error ("Unexpected token")
      if self.token == self.keyword_short :
         self.checkToken (self.keyword_short)
         result.a_short = True
      elif self.token == self.keyword_long :
         self.checkToken (self.keyword_long)
         result.a_long = True
         if self.token == self.keyword_long or self.token == self.keyword_double :
            if self.token == self.keyword_long :
               self.checkToken (self.keyword_long)
               result.a_long_long = True
            elif self.token == self.keyword_double :
               self.checkToken (self.keyword_double)
               result.a_long_double = True
            else :
               self.error ("Unexpected token")
      elif self.token == self.keyword_bool :
         self.checkToken (self.keyword_bool)
         result.a_bool = True
      elif self.token == self.keyword_char :
         self.checkToken (self.keyword_char)
         result.a_char = True
      elif self.token == self.keyword_wchar_t :
         self.checkToken (self.keyword_wchar_t)
         result.a_wchar = True
      elif self.token == self.keyword_int :
         self.checkToken (self.keyword_int)
         result.a_int = True
      elif self.token == self.keyword_float :
         self.checkToken (self.keyword_float)
         result.a_float = True
      elif self.token == self.keyword_double :
         self.checkToken (self.keyword_double)
         result.a_double = True
      elif self.token == self.keyword_void :
         self.checkToken (self.keyword_void)
         result.a_void = True
      else :
         self.error ("Unexpected token")
      self.on_type_specifier (result)
      return result

   def parse_type_name (self) :
      result = CmmTypeName ()
      self.storeLocation (result)
      self.checkToken (self.keyword_typename)
      result.qual_name = self.parse_qualified_name ()
      self.on_type_name (result)
      return result

   def parse_type_specifiers (self) :
      if self.token == self.identifier or self.token == self.SCOPE or self.token == self.keyword_operator :
         result = self.parse_ident_expr ()
      elif self.token == self.keyword_typename :
         result = self.parse_type_name ()
      elif self.set_2 & 1 << self.token :
         result = self.parse_type_specifier ()
      elif self.token == self.keyword_const :
         result = self.parse_const_specifier ()
      elif self.token == self.keyword_volatile :
         result = self.parse_volatile_specifier ()
      elif self.set_3 & 1 << self.token :
         result = self.parse_decl_specifier ()
      else :
         self.error ("Unexpected token")
      return result

   def parse_pointer_declarator (self) :
      result = CmmPointerDeclarator ()
      self.storeLocation (result)
      self.checkToken (self.STAR)
      result.cv_spec = self.parse_cv_specifier_list ()
      result.inner_declarator = self.parse_declarator ()
      return result

   def parse_reference_declarator (self) :
      result = CmmReferenceDeclator ()
      self.storeLocation (result)
      self.checkToken (self.BIT_AND)
      result.cv_spec = self.parse_cv_specifier_list ()
      result.inner_declarator = self.parse_declarator ()
      return result

   def parse_cv_specifier_list (self) :
      result = CmmCvSpecifier ()
      self.storeLocation (result)
      while self.token == self.keyword_const or self.token == self.keyword_volatile :
         if self.token == self.keyword_const :
            self.checkToken (self.keyword_const)
            result.cv_const = True
         elif self.token == self.keyword_volatile :
            self.checkToken (self.keyword_volatile)
            result.cv_volatile = True
         else :
            self.error ("Unexpected token")
      return result

   def parse_basic_declarator (self) :
      result = CmmBasicDeclarator ()
      self.storeLocation (result)
      result.qual_name = self.parse_new_qualified_name ()
      return result

   def parse_empty_declarator (self) :
      result = CmmEmptyDeclarator ()
      self.storeLocation (result)
      return result

   def parse_nested_declarator (self) :
      result = CmmNestedDeclarator ()
      self.storeLocation (result)
      self.checkToken (self.LPAREN)
      result.inner_declarator = self.parse_declarator ()
      self.checkToken (self.RPAREN)
      return result

   def parse_array_declarator (self, store) :
      result = CmmArrayDeclarator ()
      self.storeLocation (result)
      result.inner_declarator = store
      self.checkToken (self.LBRACKET)
      if self.set_5 & 1 << self.token :
         result.lim = self.parse_expr ()
      self.checkToken (self.RBRACKET)
      return result

   def parse_function_declarator (self, store) :
      result = CmmFunctionDeclarator ()
      self.storeLocation (result)
      result.inner_declarator = store
      self.checkToken (self.LPAREN)
      result.parameters = self.parse_parameter_declaration_list ()
      self.checkToken (self.RPAREN)
      if self.token == self.keyword_const :
         self.checkToken (self.keyword_const)
         result.a_const = True
      if self.token == self.keyword_override :
         self.checkToken (self.keyword_override)
         result.a_override = True
      if self.token == self.keyword_throw :
         result.exception_spec = self.parse_exception_specification ()
      return result

   def parse_entry_declarator (self) :
      if self.token == self.identifier or self.token == self.SCOPE or self.token == self.keyword_operator :
         result = self.parse_basic_declarator ()
      elif self.token == self.LPAREN :
         result = self.parse_nested_declarator ()
      else :
         result = self.parse_empty_declarator ()
      return result

   def parse_continue_declarator (self) :
      result = self.parse_entry_declarator ()
      while self.token == self.LBRACKET or self.token == self.LPAREN :
         if self.token == self.LBRACKET :
            result = self.parse_array_declarator (result)
         elif self.token == self.LPAREN :
            result = self.parse_function_declarator (result)
         else :
            self.error ("Unexpected token")
      return result

   def parse_declarator (self) :
      if self.token == self.STAR :
         result = self.parse_pointer_declarator ()
      elif self.token == self.BIT_AND :
         result = self.parse_reference_declarator ()
      else :
         result = self.parse_continue_declarator ()
      return result

   def parse_simple_declarator (self) :
      result = self.parse_declarator ()
      self.on_simple_declarator (result)
      return result

   def parse_common_declarator (self) :
      result = self.parse_declarator ()
      return result

   def parse_constructor_declarator (self) :
      result = self.parse_empty_declarator ()
      result = self.parse_function_declarator (result)
      return result

   def parse_ptr_specifier_list (self) :
      result = CmmPtrSpecifierSect ()
      self.storeLocation (result)
      return result

   def parse_parameter_declaration_list (self) :
      result = CmmStatSect ()
      self.storeLocation (result)
      if self.set_14 & 1 << self.token :
         result.items.append (self.parse_parameter_declaration ())
         while self.token == self.COMMA :
            self.checkToken (self.COMMA)
            result.items.append (self.parse_parameter_declaration ())
      return result

   def parse_parameter_declaration (self) :
      if self.set_5 & 1 << self.token :
         result = self.parse_assignment_expr ()
         if self.is_value_parameter (result) :
            result = self.parse_value_parameter (result)
         else :
            result = self.parse_plain_parameter (result)
      elif self.token == self.DOTS :
         result = self.parse_dots_parameter ()
      else :
         self.error ("Unexpected token")
      return result

   def parse_value_parameter (self, store) :
      result = CmmSimpleStat ()
      self.storeLocation (result)
      result.inner_expr = store
      return result

   def parse_plain_parameter (self, store) :
      result = CmmSimpleDecl ()
      self.storeLocation (result)
      result.type_spec = store
      result.items.append (self.parse_parameter_item ())
      return result

   def parse_parameter_item (self) :
      result = CmmSimpleItem ()
      self.storeLocation (result)
      result.declarator = self.parse_common_declarator ()
      if self.token == self.ASSIGN :
         result.init = self.parse_initializer ()
      result.attr = self.parse_attr_list ()
      return result

   def parse_dots_parameter (self) :
      result = CmmDotsParam ()
      self.storeLocation (result)
      self.checkToken (self.DOTS)
      return result

   def parse_type_id (self) :
      result = CmmTypeId ()
      self.storeLocation (result)
      result.type_spec = self.parse_type_specifiers ()
      result.declarator = self.parse_common_declarator ()
      return result

   def parse_initializer (self) :
      result = CmmInitializer ()
      self.storeLocation (result)
      self.checkToken (self.ASSIGN)
      result.value = self.parse_initializer_item ()
      return result

   def parse_initializer_item (self) :
      if self.set_5 & 1 << self.token :
         result = self.parse_simple_initializer ()
      elif self.token == self.LBRACE :
         result = self.parse_initializer_list ()
      else :
         self.error ("Unexpected token")
      return result

   def parse_simple_initializer (self) :
      result = CmmInitSimple ()
      self.storeLocation (result)
      result.inner_expr = self.parse_assignment_expr ()
      return result

   def parse_initializer_list (self) :
      result = CmmInitList ()
      self.storeLocation (result)
      self.checkToken (self.LBRACE)
      if self.set_16 & 1 << self.token :
         result.items.append (self.parse_initializer_item ())
         while self.token == self.COMMA :
            self.checkToken (self.COMMA)
            result.items.append (self.parse_initializer_item ())
      self.checkToken (self.RBRACE)
      return result

   def parse_attr_item (self) :
      result = CmmAttr ()
      self.storeLocation (result)
      result.attr_expr = self.parse_assignment_expr ()
      return result

   def parse_attr_group (self) :
      result = CmmAttrGroup ()
      self.storeLocation (result)
      self.checkToken (self.literal_1)
      result.items.append (self.parse_attr_item ())
      while self.token == self.COMMA :
         self.checkToken (self.COMMA)
         result.items.append (self.parse_attr_item ())
      self.checkToken (self.literal_2)
      return result

   def parse_attr_list (self) :
      result = CmmAttrSect ()
      self.storeLocation (result)
      while self.token == self.literal_1 :
         result.items.append (self.parse_attr_group ())
      return result

   def parse_simple_declaration (self, store) :
      result = CmmSimpleDecl ()
      self.storeLocation (result)
      result.type_spec = store
      self.on_open_simple_declaration (result)
      result.items.append (self.parse_simple_item ())
      self.on_simple_item (result)
      while self.token == self.COMMA :
         self.checkToken (self.COMMA)
         result.items.append (self.parse_simple_item ())
         self.on_simple_item (result)
      if self.token == self.LBRACE :
         self.on_open_function (result)
         result.body = self.parse_compound_stat ()
         self.on_close_function (result)
      elif self.token == self.SEMICOLON :
         self.checkToken (self.SEMICOLON)
      else :
         self.error ("Unexpected token")
      self.on_simple_declaration (result)
      return result

   def parse_simple_item (self) :
      result = CmmSimpleItem ()
      self.storeLocation (result)
      result.declarator = self.parse_simple_declarator ()
      if self.token == self.ASSIGN :
         result.init = self.parse_initializer ()
      result.attr = self.parse_attr_list ()
      return result

   def parse_constructor_declaration (self, store) :
      result = CmmSimpleDecl ()
      self.storeLocation (result)
      result.type_spec = store
      self.on_open_constructor_declaration (result)
      result.items.append (self.parse_constructor_item ())
      self.on_simple_item (result)
      if self.token == self.COLON or self.token == self.LBRACE :
         self.on_open_function (result)
         if self.token == self.COLON :
            self.checkToken (self.COLON)
            result.ctor_init = self.parse_ctor_initializer ()
         result.body = self.parse_compound_stat ()
         self.on_close_function (result)
      elif self.token == self.SEMICOLON :
         self.checkToken (self.SEMICOLON)
      else :
         self.error ("Unexpected token")
      self.on_simple_declaration (result)
      return result

   def parse_constructor_item (self) :
      result = CmmSimpleItem ()
      self.storeLocation (result)
      result.declarator = self.parse_constructor_declarator ()
      result.attr = self.parse_attr_list ()
      return result

   def parse_condition (self) :
      result = self.parse_expr ()
      if self.is_expression (result) :
         result = self.parse_condition_value (result)
      else :
         result = self.parse_condition_declaration (result)
      return result

   def parse_condition_declaration (self, store) :
      result = CmmSimpleDecl ()
      self.storeLocation (result)
      result.type_spec = store
      result.items.append (self.parse_condition_item ())
      self.on_simple_item (result)
      while self.token == self.COMMA :
         self.checkToken (self.COMMA)
         result.items.append (self.parse_condition_item ())
         self.on_simple_item (result)
      return result

   def parse_condition_item (self) :
      result = CmmSimpleItem ()
      self.storeLocation (result)
      result.declarator = self.parse_simple_declarator ()
      if self.token == self.ASSIGN :
         result.init = self.parse_initializer ()
      result.attr = self.parse_attr_list ()
      return result

   def parse_condition_value (self, store) :
      result = CmmSimpleStat ()
      self.storeLocation (result)
      result.inner_expr = store
      return result

   def parse_declaration_list (self) :
      result = CmmStatSect ()
      self.storeLocation (result)
      while self.set_18 & 1 << self.token :
         self.on_declaration (result)
         result.items.append (self.parse_declaration ())
      return result

   def parse_declaration (self) :
      if self.set_5 & 1 << self.token :
         result = self.parse_flexible_stat ()
      elif self.token == self.SEMICOLON :
         result = self.parse_empty_stat ()
      elif self.token == self.LBRACE :
         result = self.parse_compound_stat ()
      elif self.token == self.keyword_if :
         result = self.parse_if_stat ()
      elif self.token == self.keyword_while :
         result = self.parse_while_stat ()
      elif self.token == self.keyword_do :
         result = self.parse_do_stat ()
      elif self.token == self.keyword_for :
         result = self.parse_for_stat ()
      elif self.token == self.keyword_switch :
         result = self.parse_switch_stat ()
      elif self.token == self.keyword_class or self.token == self.keyword_struct or self.token == self.keyword_union :
         result = self.parse_class_declaration ()
      elif self.token == self.keyword_enum :
         result = self.parse_enum_declaration ()
      elif self.token == self.keyword_typedef :
         result = self.parse_typedef_declaration ()
      elif self.token == self.keyword_friend :
         result = self.parse_friend_declaration ()
      elif self.token == self.keyword_namespace :
         result = self.parse_namespace_declaration ()
      elif self.token == self.keyword_using :
         result = self.parse_using_declaration ()
      elif self.token == self.keyword_extern :
         result = self.parse_extern_declaration ()
      elif self.token == self.keyword_template :
         result = self.parse_template_declaration ()
      elif self.token == self.keyword_stencil :
         result = self.parse_stencil_declaration ()
      else :
         self.error ("Unexpected token")
      return result

   def parse_namespace_declaration (self) :
      result = CmmNamespaceDecl ()
      self.storeLocation (result)
      self.on_start_namespace (result)
      self.checkToken (self.keyword_namespace)
      result.simp_name = self.parse_simple_name ()
      result.attr = self.parse_attr_list ()
      self.on_namespace (result)
      self.checkToken (self.LBRACE)
      self.on_open_namespace (result)
      result.members = self.parse_declaration_list ()
      self.on_close_namespace (result)
      self.checkToken (self.RBRACE)
      self.on_stop_namespace (result)
      return result

   def parse_using_declaration (self) :
      result = CmmUsingDecl ()
      self.storeLocation (result)
      self.checkToken (self.keyword_using)
      if self.token == self.keyword_namespace :
         self.checkToken (self.keyword_namespace)
         result.a_namespace = True
      result.qual_name = self.parse_qualified_name ()
      self.on_using (result)
      self.checkToken (self.SEMICOLON)
      return result

   def parse_extern_declaration (self) :
      result = CmmExternDecl ()
      self.storeLocation (result)
      self.checkToken (self.keyword_extern)
      if self.token == self.string_literal :
         result.language = self.readString ()
      if self.token == self.LBRACE :
         self.checkToken (self.LBRACE)
         result.members = self.parse_declaration_list ()
         self.checkToken (self.RBRACE)
      elif self.set_18 & 1 << self.token :
         result.inner_declaration = self.parse_declaration ()
      else :
         self.error ("Unexpected token")
      return result

   def parse_typedef_declaration (self) :
      result = CmmTypedefDecl ()
      self.storeLocation (result)
      self.checkToken (self.keyword_typedef)
      result.type_spec = self.parse_type_specifiers ()
      result.declarator = self.parse_simple_declarator ()
      self.on_typedef (result)
      self.checkToken (self.SEMICOLON)
      return result

   def parse_friend_declaration (self) :
      result = CmmFriendDecl ()
      self.storeLocation (result)
      self.checkToken (self.keyword_friend)
      result.inner_declaration = self.parse_declaration ()
      return result

   def parse_enum_declaration (self) :
      result = CmmEnumDecl ()
      self.storeLocation (result)
      self.on_start_enum (result)
      self.checkToken (self.keyword_enum)
      result.simp_name = self.parse_simple_name ()
      self.on_enum (result)
      if self.token == self.LBRACE :
         self.checkToken (self.LBRACE)
         self.on_open_enum (result)
         result.enum_items = self.parse_enum_list ()
         self.on_close_enum (result)
         self.checkToken (self.RBRACE)
      self.checkToken (self.SEMICOLON)
      self.on_stop_enum (result)
      return result

   def parse_enum_list (self) :
      result = CmmEnumSect ()
      self.storeLocation (result)
      if self.token == self.identifier :
         result.items.append (self.parse_enumerator ())
         while self.token == self.COMMA :
            self.checkToken (self.COMMA)
            result.items.append (self.parse_enumerator ())
      return result

   def parse_enumerator (self) :
      result = CmmEnumItem ()
      self.storeLocation (result)
      result.simp_name = self.parse_simple_name ()
      self.on_enum_item (result)
      if self.token == self.ASSIGN :
         self.checkToken (self.ASSIGN)
         result.init_value = self.parse_const_expr ()
      return result

   def parse_class_declaration (self) :
      result = CmmClassDecl ()
      self.storeLocation (result)
      self.on_start_class (result)
      if self.token == self.keyword_class :
         self.checkToken (self.keyword_class)
         result.style = classStyle
      elif self.token == self.keyword_struct :
         self.checkToken (self.keyword_struct)
         result.style = structStyle
      elif self.token == self.keyword_union :
         self.checkToken (self.keyword_union)
         result.style = unionStyle
      else :
         self.error ("Unexpected token")
      result.simp_name = self.parse_simple_name ()
      result.attr = self.parse_attr_list ()
      self.on_class (result)
      if self.token == self.COLON or self.token == self.LBRACE :
         if self.token == self.COLON :
            self.checkToken (self.COLON)
            result.base_list = self.parse_base_specifier_list ()
         self.checkToken (self.LBRACE)
         self.on_open_class (result)
         result.members = self.parse_member_list ()
         self.on_close_class (result)
         self.checkToken (self.RBRACE)
      self.checkToken (self.SEMICOLON)
      self.on_stop_class (result)
      return result

   def parse_member_visibility (self) :
      result = CmmMemberVisibility ()
      self.storeLocation (result)
      if self.token == self.keyword_private :
         self.checkToken (self.keyword_private)
         result.access = privateAccess
      elif self.token == self.keyword_protected :
         self.checkToken (self.keyword_protected)
         result.access = protectedAccess
      elif self.token == self.keyword_public :
         self.checkToken (self.keyword_public)
         result.access = publicAccess
      else :
         self.error ("Unexpected token")
      self.on_member_visibility (result)
      self.checkToken (self.COLON)
      return result

   def parse_member_item (self) :
      if self.token == self.keyword_private or self.token == self.keyword_protected or self.token == self.keyword_public :
         result = self.parse_member_visibility ()
      elif self.set_5 & 1 << self.token :
         result = self.parse_flexible_stat ()
      elif self.token == self.SEMICOLON :
         result = self.parse_empty_stat ()
      elif self.token == self.LBRACE :
         result = self.parse_compound_stat ()
      elif self.token == self.keyword_if :
         result = self.parse_if_stat ()
      elif self.token == self.keyword_while :
         result = self.parse_while_stat ()
      elif self.token == self.keyword_for :
         result = self.parse_for_stat ()
      elif self.token == self.keyword_class or self.token == self.keyword_struct or self.token == self.keyword_union :
         result = self.parse_class_declaration ()
      elif self.token == self.keyword_enum :
         result = self.parse_enum_declaration ()
      elif self.token == self.keyword_typedef :
         result = self.parse_typedef_declaration ()
      elif self.token == self.keyword_friend :
         result = self.parse_friend_declaration ()
      elif self.token == self.keyword_using :
         result = self.parse_using_declaration ()
      elif self.token == self.keyword_template :
         result = self.parse_template_declaration ()
      elif self.token == self.keyword_stencil :
         result = self.parse_stencil_declaration ()
      else :
         self.error ("Unexpected token")
      return result

   def parse_member_list (self) :
      result = CmmStatSect ()
      self.storeLocation (result)
      while self.set_19 & 1 << self.token :
         self.on_declaration (result)
         self.on_start_member_item (result)
         result.items.append (self.parse_member_item ())
      return result

   def parse_base_specifier_list (self) :
      result = CmmBaseSect ()
      self.storeLocation (result)
      result.items.append (self.parse_base_specifier ())
      while self.token == self.COMMA :
         self.checkToken (self.COMMA)
         result.items.append (self.parse_base_specifier ())
      return result

   def parse_base_specifier (self) :
      result = CmmBaseItem ()
      self.storeLocation (result)
      if self.token == self.keyword_virtual :
         self.checkToken (self.keyword_virtual)
         result.a_virtual = True
      if self.token == self.keyword_private :
         self.checkToken (self.keyword_private)
         result.access = privateBase
      elif self.token == self.keyword_protected :
         self.checkToken (self.keyword_protected)
         result.access = protectedBase
      elif self.token == self.keyword_public :
         self.checkToken (self.keyword_public)
         result.access = publicBase
      else :
         result.access = unknownBase
      result.from_cls = self.parse_qualified_name ()
      return result

   def parse_ctor_initializer (self) :
      result = CmmCtorInitializer ()
      self.storeLocation (result)
      result.items.append (self.parse_member_initializer ())
      while self.token == self.COMMA :
         self.checkToken (self.COMMA)
         result.items.append (self.parse_member_initializer ())
      return result

   def parse_member_initializer (self) :
      result = CmmMemberInitializer ()
      self.storeLocation (result)
      result.simp_name = self.parse_simple_name ()
      self.on_member_initializer (result)
      self.checkToken (self.LPAREN)
      result.params = self.parse_expr_list ()
      self.checkToken (self.RPAREN)
      return result

   def parse_conversion_specifiers (self) :
      result = CmmConvSpec ()
      self.storeLocation (result)
      result.type_spec = self.parse_type_specifiers ()
      result.ptr_spec = self.parse_ptr_specifier_list ()
      return result

   def parse_special_function (self) :
      result = CmmSpecialFuction ()
      self.storeLocation (result)
      self.checkToken (self.keyword_operator)
      if self.set_7 & 1 << self.token :
         result.conv = self.parse_conversion_specifiers ()
      elif self.token == self.keyword_new :
         self.checkToken (self.keyword_new)
         result.spec_new = True
         if self.token == self.LBRACKET :
            self.checkToken (self.LBRACKET)
            self.checkToken (self.RBRACKET)
            result.spec_new_array = True
      elif self.token == self.keyword_delete :
         self.checkToken (self.keyword_delete)
         result.spec_delete = True
         if self.token == self.LBRACKET :
            self.checkToken (self.LBRACKET)
            self.checkToken (self.RBRACKET)
            result.spec_delete_array = True
      elif self.token == self.PLUS :
         self.checkToken (self.PLUS)
         result.spec_add = True
      elif self.token == self.MINUS :
         self.checkToken (self.MINUS)
         result.spec_sub = True
      elif self.token == self.STAR :
         self.checkToken (self.STAR)
         result.spec_mul = True
      elif self.token == self.SLASH :
         self.checkToken (self.SLASH)
         result.spec_div = True
      elif self.token == self.MOD :
         self.checkToken (self.MOD)
         result.spec_mod = True
      elif self.token == self.BIT_XOR :
         self.checkToken (self.BIT_XOR)
         result.spec_xor = True
      elif self.token == self.BIT_AND :
         self.checkToken (self.BIT_AND)
         result.spec_and = True
      elif self.token == self.BIT_OR :
         self.checkToken (self.BIT_OR)
         result.spec_or = True
      elif self.token == self.BIT_NOT :
         self.checkToken (self.BIT_NOT)
         result.spec_not = True
      elif self.token == self.LOG_NOT :
         self.checkToken (self.LOG_NOT)
         result.spec_log_not = True
      elif self.token == self.ASSIGN :
         self.checkToken (self.ASSIGN)
         result.spec_assign = True
      elif self.token == self.LESS :
         self.checkToken (self.LESS)
         result.spec_lt = True
      elif self.token == self.GREATER :
         self.checkToken (self.GREATER)
         result.spec_gt = True
      elif self.token == self.PLUS_ASSIGN :
         self.checkToken (self.PLUS_ASSIGN)
         result.spec_add_assign = True
      elif self.token == self.MINUS_ASSIGN :
         self.checkToken (self.MINUS_ASSIGN)
         result.spec_sub_assign = True
      elif self.token == self.MUL_ASSIGN :
         self.checkToken (self.MUL_ASSIGN)
         result.spec_mul_assign = True
      elif self.token == self.DIV_ASSIGN :
         self.checkToken (self.DIV_ASSIGN)
         result.spec_div_assign = True
      elif self.token == self.MOD_ASSIGN :
         self.checkToken (self.MOD_ASSIGN)
         result.spec_mod_assign = True
      elif self.token == self.BIT_XOR_ASSIGN :
         self.checkToken (self.BIT_XOR_ASSIGN)
         result.spec_xor_assign = True
      elif self.token == self.BIT_AND_ASSIGN :
         self.checkToken (self.BIT_AND_ASSIGN)
         result.spec_and_assign = True
      elif self.token == self.BIT_OR_ASSIGN :
         self.checkToken (self.BIT_OR_ASSIGN)
         result.spec_or_assign = True
      elif self.token == self.SHL :
         self.checkToken (self.SHL)
         result.spec_shl = True
      elif self.token == self.SHR :
         self.checkToken (self.SHR)
         result.spec_shr = True
      elif self.token == self.SHR_ASSIGN :
         self.checkToken (self.SHR_ASSIGN)
         result.spec_shl_assign = True
      elif self.token == self.SHL_ASSIGN :
         self.checkToken (self.SHL_ASSIGN)
         result.spec_shr_assign = True
      elif self.token == self.EQUAL :
         self.checkToken (self.EQUAL)
         result.spec_eq = True
      elif self.token == self.UNEQUAL :
         self.checkToken (self.UNEQUAL)
         result.spec_ne = True
      elif self.token == self.LESS_OR_EQUAL :
         self.checkToken (self.LESS_OR_EQUAL)
         result.spec_le = True
      elif self.token == self.GREATER_OR_EQUAL :
         self.checkToken (self.GREATER_OR_EQUAL)
         result.spec_ge = True
      elif self.token == self.LOG_AND :
         self.checkToken (self.LOG_AND)
         result.spec_log_and = True
      elif self.token == self.LOG_OR :
         self.checkToken (self.LOG_OR)
         result.spec_log_or = True
      elif self.token == self.INC :
         self.checkToken (self.INC)
         result.spec_inc = True
      elif self.token == self.DEC :
         self.checkToken (self.DEC)
         result.spec_dec = True
      elif self.token == self.COMMA :
         self.checkToken (self.COMMA)
         result.spec_comma = True
      elif self.token == self.ARROW_STAR :
         self.checkToken (self.ARROW_STAR)
         result.spec_member_deref = True
      elif self.token == self.ARROW :
         self.checkToken (self.ARROW)
         result.spec_deref = True
      elif self.token == self.LPAREN :
         self.checkToken (self.LPAREN)
         self.checkToken (self.RPAREN)
         result.spec_call = True
      elif self.token == self.LBRACKET :
         self.checkToken (self.LBRACKET)
         self.checkToken (self.RBRACKET)
         result.spec_index = True
      else :
         self.error ("Unexpected token")
      return result

   def parse_template_declaration (self) :
      result = CmmTemplateDecl ()
      self.storeLocation (result)
      self.checkToken (self.keyword_template)
      if self.token == self.LESS :
         self.checkToken (self.LESS)
         result.params = self.parse_template_param_list ()
         self.checkToken (self.GREATER)
      result.inner_declaration = self.parse_declaration ()
      self.on_template_declaration (result)
      return result

   def parse_stencil_declaration (self) :
      result = CmmStencilDecl ()
      self.storeLocation (result)
      self.checkToken (self.keyword_stencil)
      result.simp_name = self.parse_simple_name ()
      self.checkToken (self.LESS)
      result.params = self.parse_template_param_list ()
      self.checkToken (self.GREATER)
      self.on_stencil_params (result)
      self.checkToken (self.LBRACE)
      self.on_open_stencil (result)
      result.members = self.parse_stencil_member_list ()
      self.on_close_stencil (result)
      self.checkToken (self.RBRACE)
      self.on_stencil_declaration (result)
      return result

   def parse_stencil_member_list (self) :
      result = CmmStatSect ()
      self.storeLocation (result)
      while self.set_18 & 1 << self.token :
         self.on_declaration (result)
         result.items.append (self.parse_declaration ())
      return result

   def parse_template_param_list (self) :
      result = CmmTemplateParamSect ()
      self.storeLocation (result)
      if self.set_20 & 1 << self.token :
         result.items.append (self.parse_template_param ())
         while self.token == self.COMMA :
            self.checkToken (self.COMMA)
            result.items.append (self.parse_template_param ())
      return result

   def parse_template_param (self) :
      if self.token == self.keyword_class or self.token == self.keyword_template or self.token == self.keyword_typename :
         result = self.parse_template_type_param ()
      elif self.set_7 & 1 << self.token :
         result = self.parse_template_normal_param ()
      else :
         self.error ("Unexpected token")
      return result

   def parse_template_type_param (self) :
      result = CmmTemplateTypeParam ()
      self.storeLocation (result)
      if self.token == self.keyword_template :
         self.checkToken (self.keyword_template)
         self.checkToken (self.LESS)
         result.params = self.parse_template_param_list ()
         self.checkToken (self.GREATER)
      if self.token == self.keyword_class :
         self.checkToken (self.keyword_class)
         result.a_class = True
      elif self.token == self.keyword_typename :
         self.checkToken (self.keyword_typename)
         result.a_typename = True
      else :
         self.error ("Unexpected token")
      if self.token == self.identifier :
         result.simp_name = self.parse_simple_name ()
      return result

   def parse_template_normal_param (self) :
      result = CmmTemplateNormalParam ()
      self.storeLocation (result)
      result.type_spec = self.parse_type_specifiers ()
      result.declarator = self.parse_common_declarator ()
      if self.token == self.ASSIGN :
         self.checkToken (self.ASSIGN)
         result.init = self.parse_shift_expr ()
      return result

   def parse_template_arg_list (self) :
      result = CmmTemplateArgSect ()
      self.storeLocation (result)
      self.checkToken (self.LESS)
      if self.set_14 & 1 << self.token :
         result.items.append (self.parse_template_arg ())
         while self.token == self.COMMA :
            self.checkToken (self.COMMA)
            result.items.append (self.parse_template_arg ())
      self.checkToken (self.GREATER)
      return result

   def parse_template_arg (self) :
      result = CmmTemplateArg ()
      self.storeLocation (result)
      result.value = self.parse_parameter_declaration ()
      return result

   def parse_try_stat (self) :
      result = CmmTryStat ()
      self.storeLocation (result)
      self.checkToken (self.keyword_try)
      result.body = self.parse_compound_stat ()
      result.handlers = self.parse_handler_list ()
      return result

   def parse_handler_list (self) :
      result = CmmHandlerSect ()
      self.storeLocation (result)
      result.items.append (self.parse_handler ())
      while self.token == self.keyword_catch :
         result.items.append (self.parse_handler ())
      return result

   def parse_handler (self) :
      result = CmmHandlerItem ()
      self.storeLocation (result)
      self.checkToken (self.keyword_catch)
      self.checkToken (self.LPAREN)
      if self.set_7 & 1 << self.token :
         result.type_spec = self.parse_type_specifiers ()
         result.declarator = self.parse_common_declarator ()
      elif self.token == self.DOTS :
         self.checkToken (self.DOTS)
         result.dots = True
      else :
         self.error ("Unexpected token")
      self.checkToken (self.RPAREN)
      result.body = self.parse_compound_stat ()
      return result

   def parse_throw_expr (self) :
      result = CmmThrowExpr ()
      self.storeLocation (result)
      self.checkToken (self.keyword_throw)
      if self.set_5 & 1 << self.token :
         result.inner_expr = self.parse_assignment_expr ()
      self.on_throw_expr (result)
      return result

   def parse_exception_specification (self) :
      result = CmmExceptionSect ()
      self.storeLocation (result)
      self.checkToken (self.keyword_throw)
      self.checkToken (self.LPAREN)
      if self.set_7 & 1 << self.token :
         result.items.append (self.parse_exception_specification_item ())
         while self.token == self.COMMA :
            self.checkToken (self.COMMA)
            result.items.append (self.parse_exception_specification_item ())
      self.checkToken (self.RPAREN)
      return result

   def parse_exception_specification_item (self) :
      result = CmmExceptionItem ()
      self.storeLocation (result)
      result.type = self.parse_type_id ()
      return result

   def lookupKeyword (self) :
      s = self.tokenText
      n = len (s)
      if n == 2 :
         if s[0] == 'd' :
            if s[1] == 'o' :
               self.token = self.keyword_do
         elif s[0] == 'i' :
            if s[1] == 'f' :
               self.token = self.keyword_if
      elif n == 3 :
         if s[0] == 'f' :
            if s[1:3] == "or" :
               self.token = self.keyword_for
         elif s[0] == 'i' :
            if s[1:3] == "nt" :
               self.token = self.keyword_int
         elif s[0] == 'n' :
            if s[1:3] == "ew" :
               self.token = self.keyword_new
         elif s[0] == 't' :
            if s[1:3] == "ry" :
               self.token = self.keyword_try
      elif n == 4 :
         if s[0] == 'b' :
            if s[1:4] == "ool" :
               self.token = self.keyword_bool
         elif s[0] == 'c' :
            if s[1] == 'a' :
               if s[2:4] == "se" :
                  self.token = self.keyword_case
            elif s[1] == 'h' :
               if s[2:4] == "ar" :
                  self.token = self.keyword_char
         elif s[0] == 'e' :
            if s[1] == 'l' :
               if s[2:4] == "se" :
                  self.token = self.keyword_else
            elif s[1] == 'n' :
               if s[2:4] == "um" :
                  self.token = self.keyword_enum
         elif s[0] == 'g' :
            if s[1:4] == "oto" :
               self.token = self.keyword_goto
         elif s[0] == 'l' :
            if s[1:4] == "ong" :
               self.token = self.keyword_long
         elif s[0] == 't' :
            if s[1:4] == "his" :
               self.token = self.keyword_this
         elif s[0] == 'v' :
            if s[1:4] == "oid" :
               self.token = self.keyword_void
      elif n == 5 :
         if s[0] == 'b' :
            if s[1:5] == "reak" :
               self.token = self.keyword_break
         elif s[0] == 'c' :
            if s[1] == 'a' :
               if s[2:5] == "tch" :
                  self.token = self.keyword_catch
            elif s[1] == 'l' :
               if s[2:5] == "ass" :
                  self.token = self.keyword_class
            elif s[1] == 'o' :
               if s[2:5] == "nst" :
                  self.token = self.keyword_const
         elif s[0] == 'f' :
            if s[1:5] == "loat" :
               self.token = self.keyword_float
         elif s[0] == 's' :
            if s[1:5] == "hort" :
               self.token = self.keyword_short
         elif s[0] == 't' :
            if s[1:5] == "hrow" :
               self.token = self.keyword_throw
         elif s[0] == 'u' :
            if s[1] == 'n' :
               if s[2:5] == "ion" :
                  self.token = self.keyword_union
            elif s[1] == 's' :
               if s[2:5] == "ing" :
                  self.token = self.keyword_using
         elif s[0] == 'w' :
            if s[1:5] == "hile" :
               self.token = self.keyword_while
      elif n == 6 :
         if s[0] == 'd' :
            if s[1] == 'e' :
               if s[2:6] == "lete" :
                  self.token = self.keyword_delete
            elif s[1] == 'o' :
               if s[2:6] == "uble" :
                  self.token = self.keyword_double
         elif s[0] == 'e' :
            if s[1:6] == "xtern" :
               self.token = self.keyword_extern
         elif s[0] == 'f' :
            if s[1:6] == "riend" :
               self.token = self.keyword_friend
         elif s[0] == 'i' :
            if s[1:6] == "nline" :
               self.token = self.keyword_inline
         elif s[0] == 'p' :
            if s[1:6] == "ublic" :
               self.token = self.keyword_public
         elif s[0] == 'r' :
            if s[1:6] == "eturn" :
               self.token = self.keyword_return
         elif s[0] == 's' :
            if s[1] == 'i' :
               if s[2] == 'g' :
                  if s[3:6] == "ned" :
                     self.token = self.keyword_signed
               elif s[2] == 'z' :
                  if s[3:6] == "eof" :
                     self.token = self.keyword_sizeof
            elif s[1] == 't' :
               if s[2] == 'a' :
                  if s[3:6] == "tic" :
                     self.token = self.keyword_static
               elif s[2] == 'r' :
                  if s[3:6] == "uct" :
                     self.token = self.keyword_struct
            elif s[1] == 'w' :
               if s[2:6] == "itch" :
                  self.token = self.keyword_switch
         elif s[0] == 't' :
            if s[1:6] == "ypeid" :
               self.token = self.keyword_typeid
      elif n == 7 :
         if s[0] == 'd' :
            if s[1:7] == "efault" :
               self.token = self.keyword_default
         elif s[0] == 'm' :
            if s[1:7] == "utable" :
               self.token = self.keyword_mutable
         elif s[0] == 'p' :
            if s[1:7] == "rivate" :
               self.token = self.keyword_private
         elif s[0] == 's' :
            if s[1:7] == "tencil" :
               self.token = self.keyword_stencil
         elif s[0] == 't' :
            if s[1:7] == "ypedef" :
               self.token = self.keyword_typedef
         elif s[0] == 'v' :
            if s[1:7] == "irtual" :
               self.token = self.keyword_virtual
         elif s[0] == 'w' :
            if s[1:7] == "char_t" :
               self.token = self.keyword_wchar_t
      elif n == 8 :
         if s[0] == 'c' :
            if s[1:8] == "ontinue" :
               self.token = self.keyword_continue
         elif s[0] == 'e' :
            if s[1:8] == "xplicit" :
               self.token = self.keyword_explicit
         elif s[0] == 'o' :
            if s[1] == 'p' :
               if s[2:8] == "erator" :
                  self.token = self.keyword_operator
            elif s[1] == 'v' :
               if s[2:8] == "erride" :
                  self.token = self.keyword_override
         elif s[0] == 'r' :
            if s[1:8] == "egister" :
               self.token = self.keyword_register
         elif s[0] == 't' :
            if s[1] == 'e' :
               if s[2:8] == "mplate" :
                  self.token = self.keyword_template
            elif s[1] == 'y' :
               if s[2:8] == "pename" :
                  self.token = self.keyword_typename
         elif s[0] == 'u' :
            if s[1:8] == "nsigned" :
               self.token = self.keyword_unsigned
         elif s[0] == 'v' :
            if s[1:8] == "olatile" :
               self.token = self.keyword_volatile
      elif n == 9 :
         if s[0] == 'n' :
            if s[1:9] == "amespace" :
               self.token = self.keyword_namespace
         elif s[0] == 'p' :
            if s[1:9] == "rotected" :
               self.token = self.keyword_protected
      elif n == 10 :
         if s[0:10] == "const_cast" :
            self.token = self.keyword_const_cast
      elif n == 11 :
         if s[0:11] == "static_cast" :
            self.token = self.keyword_static_cast
      elif n == 12 :
         if s[0:12] == "dynamic_cast" :
            self.token = self.keyword_dynamic_cast
      elif n == 16 :
         if s[0:16] == "reinterpret_cast" :
            self.token = self.keyword_reinterpret_cast

   def processSeparator (self) :
      if self.tokenText == '!' :
         self.token = 8
         if self.ch == '=' :
            self.token = 9
            self.tokenText = self.tokenText + self.ch
            self.nextChar ()
      if self.tokenText == '%' :
         self.token = 10
         if self.ch == '=' :
            self.token = 11
            self.tokenText = self.tokenText + self.ch
            self.nextChar ()
      if self.tokenText == '&' :
         self.token = 12
         if self.ch == '&' :
            self.token = 13
            self.tokenText = self.tokenText + self.ch
            self.nextChar ()
         if self.ch == '=' :
            self.token = 14
            self.tokenText = self.tokenText + self.ch
            self.nextChar ()
      if self.tokenText == '(' :
         self.token = 15
      if self.tokenText == ')' :
         self.token = 16
      if self.tokenText == '*' :
         self.token = 17
         if self.ch == '=' :
            self.token = 18
            self.tokenText = self.tokenText + self.ch
            self.nextChar ()
      if self.tokenText == '+' :
         self.token = 19
         if self.ch == '+' :
            self.token = 20
            self.tokenText = self.tokenText + self.ch
            self.nextChar ()
         if self.ch == '=' :
            self.token = 21
            self.tokenText = self.tokenText + self.ch
            self.nextChar ()
      if self.tokenText == ',' :
         self.token = 22
      if self.tokenText == '-' :
         self.token = 23
         if self.ch == '-' :
            self.token = 24
            self.tokenText = self.tokenText + self.ch
            self.nextChar ()
         if self.ch == '=' :
            self.token = 25
            self.tokenText = self.tokenText + self.ch
            self.nextChar ()
         if self.ch == '>' :
            self.token = 26
            self.tokenText = self.tokenText + self.ch
            self.nextChar ()
            if self.ch == '*' :
               self.token = 27
               self.tokenText = self.tokenText + self.ch
               self.nextChar ()
      if self.tokenText == '.' :
         self.token = 28
         if self.ch == '*' :
            self.token = 29
            self.tokenText = self.tokenText + self.ch
            self.nextChar ()
         if self.ch == '.' :
            self.tokenText = self.tokenText + self.ch
            self.nextChar ()
            if self.ch == '.' :
               self.token = 30
               self.tokenText = self.tokenText + self.ch
               self.nextChar ()
      if self.tokenText == '/' :
         self.token = 31
         if self.ch == '=' :
            self.token = 32
            self.tokenText = self.tokenText + self.ch
            self.nextChar ()
      if self.tokenText == ':' :
         self.token = 33
         if self.ch == ':' :
            self.token = 34
            self.tokenText = self.tokenText + self.ch
            self.nextChar ()
      if self.tokenText == ';' :
         self.token = 35
      if self.tokenText == '<' :
         self.token = 36
         if self.ch == '<' :
            self.token = 37
            self.tokenText = self.tokenText + self.ch
            self.nextChar ()
            if self.ch == '=' :
               self.token = 38
               self.tokenText = self.tokenText + self.ch
               self.nextChar ()
         if self.ch == '=' :
            self.token = 39
            self.tokenText = self.tokenText + self.ch
            self.nextChar ()
      if self.tokenText == '=' :
         self.token = 40
         if self.ch == '=' :
            self.token = 41
            self.tokenText = self.tokenText + self.ch
            self.nextChar ()
      if self.tokenText == '>' :
         self.token = 42
         if self.ch == '=' :
            self.token = 43
            self.tokenText = self.tokenText + self.ch
            self.nextChar ()
         if self.ch == '>' :
            self.token = 44
            self.tokenText = self.tokenText + self.ch
            self.nextChar ()
            if self.ch == '=' :
               self.token = 45
               self.tokenText = self.tokenText + self.ch
               self.nextChar ()
      if self.tokenText == '?' :
         self.token = 46
      if self.tokenText == '[' :
         self.token = 47
         if self.ch == '[' :
            self.token = 48
            self.tokenText = self.tokenText + self.ch
            self.nextChar ()
      if self.tokenText == ']' :
         self.token = 49
         if self.ch == ']' :
            self.token = 50
            self.tokenText = self.tokenText + self.ch
            self.nextChar ()
      if self.tokenText == '^' :
         self.token = 51
         if self.ch == '=' :
            self.token = 52
            self.tokenText = self.tokenText + self.ch
            self.nextChar ()
      if self.tokenText == '{' :
         self.token = 53
      if self.tokenText == '|' :
         self.token = 54
         if self.ch == '=' :
            self.token = 55
            self.tokenText = self.tokenText + self.ch
            self.nextChar ()
         if self.ch == '|' :
            self.token = 56
            self.tokenText = self.tokenText + self.ch
            self.nextChar ()
      if self.tokenText == '}' :
         self.token = 57
      if self.tokenText == '~' :
         self.token = 58
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
      if value == 8: return "!"
      if value == 9: return "!="
      if value == 10: return "%"
      if value == 11: return "%="
      if value == 12: return "&"
      if value == 13: return "&&"
      if value == 14: return "&="
      if value == 15: return "("
      if value == 16: return ")"
      if value == 17: return "*"
      if value == 18: return "*="
      if value == 19: return "+"
      if value == 20: return "++"
      if value == 21: return "+="
      if value == 22: return ","
      if value == 23: return "-"
      if value == 24: return "--"
      if value == 25: return "-="
      if value == 26: return "->"
      if value == 27: return "->*"
      if value == 28: return "."
      if value == 29: return ".*"
      if value == 30: return "..."
      if value == 31: return "/"
      if value == 32: return "/="
      if value == 33: return ":"
      if value == 34: return "::"
      if value == 35: return ";"
      if value == 36: return "<"
      if value == 37: return "<<"
      if value == 38: return "<<="
      if value == 39: return "<="
      if value == 40: return "="
      if value == 41: return "=="
      if value == 42: return ">"
      if value == 43: return ">="
      if value == 44: return ">>"
      if value == 45: return ">>="
      if value == 46: return "?"
      if value == 47: return "["
      if value == 48: return "[["
      if value == 49: return "]"
      if value == 50: return "]]"
      if value == 51: return "^"
      if value == 52: return "^="
      if value == 53: return "{"
      if value == 54: return "|"
      if value == 55: return "|="
      if value == 56: return "||"
      if value == 57: return "}"
      if value == 58: return "~"
      if value == 59: return "bool"
      if value == 60: return "break"
      if value == 61: return "case"
      if value == 62: return "catch"
      if value == 63: return "char"
      if value == 64: return "class"
      if value == 65: return "const"
      if value == 66: return "const_cast"
      if value == 67: return "continue"
      if value == 68: return "default"
      if value == 69: return "delete"
      if value == 70: return "do"
      if value == 71: return "double"
      if value == 72: return "dynamic_cast"
      if value == 73: return "else"
      if value == 74: return "enum"
      if value == 75: return "explicit"
      if value == 76: return "extern"
      if value == 77: return "float"
      if value == 78: return "for"
      if value == 79: return "friend"
      if value == 80: return "goto"
      if value == 81: return "if"
      if value == 82: return "inline"
      if value == 83: return "int"
      if value == 84: return "long"
      if value == 85: return "mutable"
      if value == 86: return "namespace"
      if value == 87: return "new"
      if value == 88: return "operator"
      if value == 89: return "override"
      if value == 90: return "private"
      if value == 91: return "protected"
      if value == 92: return "public"
      if value == 93: return "register"
      if value == 94: return "reinterpret_cast"
      if value == 95: return "return"
      if value == 96: return "short"
      if value == 97: return "signed"
      if value == 98: return "sizeof"
      if value == 99: return "static"
      if value == 100: return "static_cast"
      if value == 101: return "stencil"
      if value == 102: return "struct"
      if value == 103: return "switch"
      if value == 104: return "template"
      if value == 105: return "this"
      if value == 106: return "throw"
      if value == 107: return "try"
      if value == 108: return "typedef"
      if value == 109: return "typeid"
      if value == 110: return "typename"
      if value == 111: return "union"
      if value == 112: return "unsigned"
      if value == 113: return "using"
      if value == 114: return "virtual"
      if value == 115: return "void"
      if value == 116: return "volatile"
      if value == 117: return "wchar_t"
      if value == 118: return "while"
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
      self.LOG_NOT = 8 # !
      self.UNEQUAL = 9 # !=
      self.MOD = 10 # %
      self.MOD_ASSIGN = 11 # %=
      self.BIT_AND = 12 # &
      self.LOG_AND = 13 # &&
      self.BIT_AND_ASSIGN = 14 # &=
      self.LPAREN = 15 # (
      self.RPAREN = 16 # )
      self.STAR = 17 # *
      self.MUL_ASSIGN = 18 # *=
      self.PLUS = 19 # +
      self.INC = 20 # ++
      self.PLUS_ASSIGN = 21 # +=
      self.COMMA = 22 # ,
      self.MINUS = 23 # -
      self.DEC = 24 # --
      self.MINUS_ASSIGN = 25 # -=
      self.ARROW = 26 # ->
      self.ARROW_STAR = 27 # ->*
      self.DOT = 28 # .
      self.DOT_STAR = 29 # .*
      self.DOTS = 30 # ...
      self.SLASH = 31 # /
      self.DIV_ASSIGN = 32 # /=
      self.COLON = 33 # :
      self.SCOPE = 34 # ::
      self.SEMICOLON = 35 # ;
      self.LESS = 36 # <
      self.SHL = 37 # <<
      self.SHL_ASSIGN = 38 # <<=
      self.LESS_OR_EQUAL = 39 # <=
      self.ASSIGN = 40 # =
      self.EQUAL = 41 # ==
      self.GREATER = 42 # >
      self.GREATER_OR_EQUAL = 43 # >=
      self.SHR = 44 # >>
      self.SHR_ASSIGN = 45 # >>=
      self.QUESTION = 46 # ?
      self.LBRACKET = 47 # [
      self.literal_1 = 48 # [[
      self.RBRACKET = 49 # ]
      self.literal_2 = 50 # ]]
      self.BIT_XOR = 51 # ^
      self.BIT_XOR_ASSIGN = 52 # ^=
      self.LBRACE = 53 # {
      self.BIT_OR = 54 # |
      self.BIT_OR_ASSIGN = 55 # |=
      self.LOG_OR = 56 # ||
      self.RBRACE = 57 # }
      self.BIT_NOT = 58 # ~
      self.keyword_bool = 59
      self.keyword_break = 60
      self.keyword_case = 61
      self.keyword_catch = 62
      self.keyword_char = 63
      self.keyword_class = 64
      self.keyword_const = 65
      self.keyword_const_cast = 66
      self.keyword_continue = 67
      self.keyword_default = 68
      self.keyword_delete = 69
      self.keyword_do = 70
      self.keyword_double = 71
      self.keyword_dynamic_cast = 72
      self.keyword_else = 73
      self.keyword_enum = 74
      self.keyword_explicit = 75
      self.keyword_extern = 76
      self.keyword_float = 77
      self.keyword_for = 78
      self.keyword_friend = 79
      self.keyword_goto = 80
      self.keyword_if = 81
      self.keyword_inline = 82
      self.keyword_int = 83
      self.keyword_long = 84
      self.keyword_mutable = 85
      self.keyword_namespace = 86
      self.keyword_new = 87
      self.keyword_operator = 88
      self.keyword_override = 89
      self.keyword_private = 90
      self.keyword_protected = 91
      self.keyword_public = 92
      self.keyword_register = 93
      self.keyword_reinterpret_cast = 94
      self.keyword_return = 95
      self.keyword_short = 96
      self.keyword_signed = 97
      self.keyword_sizeof = 98
      self.keyword_static = 99
      self.keyword_static_cast = 100
      self.keyword_stencil = 101
      self.keyword_struct = 102
      self.keyword_switch = 103
      self.keyword_template = 104
      self.keyword_this = 105
      self.keyword_throw = 106
      self.keyword_try = 107
      self.keyword_typedef = 108
      self.keyword_typeid = 109
      self.keyword_typename = 110
      self.keyword_union = 111
      self.keyword_unsigned = 112
      self.keyword_using = 113
      self.keyword_virtual = 114
      self.keyword_void = 115
      self.keyword_volatile = 116
      self.keyword_wchar_t = 117
      self.keyword_while = 118

      self.set_0 = self.alloc ([1, 2, 3, 4, 5, 15, 34, 47, 88, 105]) #  identifier  number  real_number  character_literal  string_literal  (  ::  [  operator  this
      self.set_1 = self.alloc ([66, 72, 94, 100]) #  const_cast  dynamic_cast  reinterpret_cast  static_cast
      self.set_2 = self.alloc ([59, 63, 71, 77, 83, 84, 96, 97, 112, 115, 117]) #  bool  char  double  float  int  long  short  signed  unsigned  void  wchar_t
      self.set_3 = self.alloc ([75, 82, 85, 93, 99, 114]) #  explicit  inline  mutable  register  static  virtual
      self.set_4 = self.alloc ([15, 20, 24, 26, 28, 47]) #  (  ++  --  ->  .  [
      self.set_5 = self.alloc ([1, 2, 3, 4, 5, 8, 12, 15, 17, 19, 20, 23, 24, 34, 47, 58, 59, 63, 65, 66, 69, 71, 72, 75, 77, 82, 83, 84, 85, 87, 88, 93, 94, 96, 97, 98, 99, 100, 105, 106, 109, 110, 112, 114, 115, 116, 117]) #  identifier  number  real_number  character_literal  string_literal  !  &  (  *  +  ++  -  --  ::  [  ~  bool  char  const  const_cast  delete  double  dynamic_cast  explicit  float  inline  int  long  mutable  new  operator  register  reinterpret_cast  short  signed  sizeof  static  static_cast  this  throw  typeid  typename  unsigned  virtual  void  volatile  wchar_t
      self.set_6 = self.alloc ([1, 2, 3, 4, 5, 15, 34, 47, 59, 63, 65, 66, 71, 72, 75, 77, 82, 83, 84, 85, 88, 93, 94, 96, 97, 99, 100, 105, 109, 110, 112, 114, 115, 116, 117]) #  identifier  number  real_number  character_literal  string_literal  (  ::  [  bool  char  const  const_cast  double  dynamic_cast  explicit  float  inline  int  long  mutable  operator  register  reinterpret_cast  short  signed  static  static_cast  this  typeid  typename  unsigned  virtual  void  volatile  wchar_t
      self.set_7 = self.alloc ([1, 34, 59, 63, 65, 71, 75, 77, 82, 83, 84, 85, 88, 93, 96, 97, 99, 110, 112, 114, 115, 116, 117]) #  identifier  ::  bool  char  const  double  explicit  float  inline  int  long  mutable  operator  register  short  signed  static  typename  unsigned  virtual  void  volatile  wchar_t
      self.set_8 = self.alloc ([1, 10, 17, 31]) #  identifier  %  *  /
      self.set_9 = self.alloc ([36, 39, 42, 43]) #  <  <=  >  >=
      self.set_10 = self.alloc ([11, 14, 18, 21, 25, 32, 38, 40, 45, 46, 52, 55]) #  %=  &=  *=  +=  -=  /=  <<=  =  >>=  ?  ^=  |=
      self.set_11 = self.alloc ([1, 2, 3, 4, 5, 8, 12, 15, 17, 19, 20, 23, 24, 34, 35, 47, 53, 58, 59, 60, 61, 63, 65, 66, 67, 68, 69, 70, 71, 72, 75, 77, 78, 80, 81, 82, 83, 84, 85, 87, 88, 93, 94, 95, 96, 97, 98, 99, 100, 103, 105, 106, 107, 109, 110, 112, 114, 115, 116, 117, 118]) #  identifier  number  real_number  character_literal  string_literal  !  &  (  *  +  ++  -  --  ::  ;  [  {  ~  bool  break  case  char  const  const_cast  continue  default  delete  do  double  dynamic_cast  explicit  float  for  goto  if  inline  int  long  mutable  new  operator  register  reinterpret_cast  return  short  signed  sizeof  static  static_cast  switch  this  throw  try  typeid  typename  unsigned  virtual  void  volatile  wchar_t  while
      self.set_12 = self.alloc ([1, 12, 15, 17, 22, 34, 35, 40, 47, 48, 53, 88]) #  identifier  &  (  *  ,  ::  ;  =  [  [[  {  operator
      self.set_13 = self.alloc ([1, 15, 34, 47, 88]) #  identifier  (  ::  [  operator
      self.set_14 = self.alloc ([1, 2, 3, 4, 5, 8, 12, 15, 17, 19, 20, 23, 24, 30, 34, 47, 58, 59, 63, 65, 66, 69, 71, 72, 75, 77, 82, 83, 84, 85, 87, 88, 93, 94, 96, 97, 98, 99, 100, 105, 106, 109, 110, 112, 114, 115, 116, 117]) #  identifier  number  real_number  character_literal  string_literal  !  &  (  *  +  ++  -  --  ...  ::  [  ~  bool  char  const  const_cast  delete  double  dynamic_cast  explicit  float  inline  int  long  mutable  new  operator  register  reinterpret_cast  short  signed  sizeof  static  static_cast  this  throw  typeid  typename  unsigned  virtual  void  volatile  wchar_t
      self.set_15 = self.alloc ([1, 12, 15, 17, 34, 40, 47, 48, 88]) #  identifier  &  (  *  ::  =  [  [[  operator
      self.set_16 = self.alloc ([1, 2, 3, 4, 5, 8, 12, 15, 17, 19, 20, 23, 24, 34, 47, 53, 58, 59, 63, 65, 66, 69, 71, 72, 75, 77, 82, 83, 84, 85, 87, 88, 93, 94, 96, 97, 98, 99, 100, 105, 106, 109, 110, 112, 114, 115, 116, 117]) #  identifier  number  real_number  character_literal  string_literal  !  &  (  *  +  ++  -  --  ::  [  {  ~  bool  char  const  const_cast  delete  double  dynamic_cast  explicit  float  inline  int  long  mutable  new  operator  register  reinterpret_cast  short  signed  sizeof  static  static_cast  this  throw  typeid  typename  unsigned  virtual  void  volatile  wchar_t
      self.set_17 = self.alloc ([1, 12, 15, 17, 22, 34, 40, 47, 48, 88]) #  identifier  &  (  *  ,  ::  =  [  [[  operator
      self.set_18 = self.alloc ([1, 2, 3, 4, 5, 8, 12, 15, 17, 19, 20, 23, 24, 34, 35, 47, 53, 58, 59, 63, 64, 65, 66, 69, 70, 71, 72, 74, 75, 76, 77, 78, 79, 81, 82, 83, 84, 85, 86, 87, 88, 93, 94, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118]) #  identifier  number  real_number  character_literal  string_literal  !  &  (  *  +  ++  -  --  ::  ;  [  {  ~  bool  char  class  const  const_cast  delete  do  double  dynamic_cast  enum  explicit  extern  float  for  friend  if  inline  int  long  mutable  namespace  new  operator  register  reinterpret_cast  short  signed  sizeof  static  static_cast  stencil  struct  switch  template  this  throw  typedef  typeid  typename  union  unsigned  using  virtual  void  volatile  wchar_t  while
      self.set_19 = self.alloc ([1, 2, 3, 4, 5, 8, 12, 15, 17, 19, 20, 23, 24, 34, 35, 47, 53, 58, 59, 63, 64, 65, 66, 69, 71, 72, 74, 75, 77, 78, 79, 81, 82, 83, 84, 85, 87, 88, 90, 91, 92, 93, 94, 96, 97, 98, 99, 100, 101, 102, 104, 105, 106, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118]) #  identifier  number  real_number  character_literal  string_literal  !  &  (  *  +  ++  -  --  ::  ;  [  {  ~  bool  char  class  const  const_cast  delete  double  dynamic_cast  enum  explicit  float  for  friend  if  inline  int  long  mutable  new  operator  private  protected  public  register  reinterpret_cast  short  signed  sizeof  static  static_cast  stencil  struct  template  this  throw  typedef  typeid  typename  union  unsigned  using  virtual  void  volatile  wchar_t  while
      self.set_20 = self.alloc ([1, 34, 59, 63, 64, 65, 71, 75, 77, 82, 83, 84, 85, 88, 93, 96, 97, 99, 104, 110, 112, 114, 115, 116, 117]) #  identifier  ::  bool  char  class  const  double  explicit  float  inline  int  long  mutable  operator  register  short  signed  static  template  typename  unsigned  virtual  void  volatile  wchar_t

   def on_binary_expr (self) :
      pass

   def is_binary_expression (self) :
      return False

   def is_postfix_expression (self) :
      return False

   def is_cast_expression (self) :
      return False

   def on_ident_expr (self, item) :
      pass

   def on_int_value (self, item) :
      pass

   def on_real_value (self, item) :
      pass

   def on_char_value (self, item) :
      pass

   def on_string_value (self, item) :
      pass

   def on_this_expr (self, item) :
      pass

   def on_subexpr_expr (self, item) :
      pass

   def on_modern_cast_expr (self, item) :
      pass

   def on_typeid_expr (self, item) :
      pass

   def on_type_name (self, item) :
      pass

   def on_type_specifier (self, item) :
      pass

   def on_const_specifier (self, item) :
      pass

   def on_volatile_specifier (self, item) :
      pass

   def on_decl_specifier (self, item) :
      pass

   def on_index_expr (self, item) :
      pass

   def on_call_expr (self, item) :
      pass

   def on_field_expr (self, item) :
      pass

   def on_ptr_field_expr (self, item) :
      pass

   def on_post_inc_expr (self, item) :
      pass

   def on_post_dec_expr (self, item) :
      pass

   def on_bit_not_expr (self, item) :
      pass

   def on_inc_expr (self, item) :
      pass

   def on_dec_expr (self, item) :
      pass

   def on_deref_expr (self, item) :
      pass

   def on_addr_expr (self, item) :
      pass

   def on_plus_expr (self, item) :
      pass

   def on_minus_expr (self, item) :
      pass

   def on_log_not_expr (self, item) :
      pass

   def on_sizeof_expr (self, item) :
      pass

   def on_allocation_expr (self, item) :
      pass

   def on_deallocation_expr (self, item) :
      pass

   def on_throw_expr (self, item) :
      pass

   def on_base_name (self, item) :
      pass

   def on_cont_name (self, item) :
      pass

   def on_template_name (self, item) :
      pass

   def is_template_name (self, item) :
      return False

   def is_signal_slot (self) :
      return False

   def on_middle_bit_not_expr (self, item) :
      pass

   def is_mul (self) :
      return False

   def is_add (self) :
      return False

   def on_expr (self, item) :
      pass

   def on_open_compound_statement (self, item) :
      pass

   def on_declaration (self, item) :
      pass

   def on_close_compound_statement (self, item) :
      pass

   def on_open_if_statement (self, item) :
      pass

   def on_close_if_statement (self, item) :
      pass

   def on_open_while_statement (self, item) :
      pass

   def on_close_while_statement (self, item) :
      pass

   def on_open_for_statement (self, item) :
      pass

   def on_close_for_statement (self, item) :
      pass

   def on_open_switch_statement (self, item) :
      pass

   def on_close_switch_statement (self, item) :
      pass

   def on_open_flexible_stat (self) :
      pass

   def is_expression (self, item) :
      return False

   def is_constructor (self, item) :
      return False

   def on_open_simple_stat (self, item) :
      pass

   def on_open_expr_block (self, item) :
      pass

   def on_close_expr_block (self, item) :
      pass

   def on_simple_statement (self, item) :
      pass

   def on_middle_decl_specifier (self, item) :
      pass

   def on_simple_declarator (self, item) :
      pass

   def is_value_parameter (self, item) :
      return False

   def on_open_simple_declaration (self, item) :
      pass

   def on_simple_item (self, item) :
      pass

   def on_open_function (self, item) :
      pass

   def on_close_function (self, item) :
      pass

   def on_simple_declaration (self, item) :
      pass

   def on_open_constructor_declaration (self, item) :
      pass

   def on_start_namespace (self, item) :
      pass

   def on_namespace (self, item) :
      pass

   def on_open_namespace (self, item) :
      pass

   def on_close_namespace (self, item) :
      pass

   def on_stop_namespace (self, item) :
      pass

   def on_using (self, item) :
      pass

   def on_typedef (self, item) :
      pass

   def on_start_enum (self, item) :
      pass

   def on_enum (self, item) :
      pass

   def on_open_enum (self, item) :
      pass

   def on_close_enum (self, item) :
      pass

   def on_stop_enum (self, item) :
      pass

   def on_enum_item (self, item) :
      pass

   def on_start_class (self, item) :
      pass

   def on_class (self, item) :
      pass

   def on_open_class (self, item) :
      pass

   def on_close_class (self, item) :
      pass

   def on_stop_class (self, item) :
      pass

   def on_member_visibility (self, item) :
      pass

   def on_start_member_item (self, item) :
      pass

   def on_member_initializer (self, item) :
      pass

   def on_template_declaration (self, item) :
      pass

   def on_stencil_params (self, item) :
      pass

   def on_open_stencil (self, item) :
      pass

   def on_close_stencil (self, item) :
      pass

   def on_stencil_declaration (self, item) :
      pass

# CmmKind in CmmCommon
simpleName = 0
globalName = 1
destructorName = 2
compoundName = 3
templateName = 4
specialName = 5
incExpr = 6
decExpr = 7
derefExpr = 8
addrExpr = 9
plusExpr = 10
minusExpr = 11
bitNotExpr = 12
logNotExpr = 13
sizeofExpr = 14
newExpr = 15
deleteExpr = 16
throwExpr = 17
castExpr = 18
dotMemberExpr = 19
arrowMemberExpr = 20
mulExpr = 21
divExpr = 22
modExpr = 23
customMulExpr = 24
addExpr = 25
subExpr = 26
customAddExpr = 27
shlExpr = 28
shrExpr = 29
ltExpr = 30
gtExpr = 31
leExpr = 32
geExpr = 33
eqExpr = 34
neExpr = 35
bitAndExpr = 36
bitXorExpr = 37
bitOrExpr = 38
logAndExpr = 39
logOrExpr = 40
assignExpr = 41
addAssignExpr = 42
subAssignExpr = 43
mulAssignExpr = 44
divAssignExpr = 45
modAssignExpr = 46
shlAssignExpr = 47
shrAssignExpr = 48
andAssignExpr = 49
xorAssignExpr = 50
orAssignExpr = 51
condExpr = 52
commaExpr = 53
intValue = 54
realValue = 55
charValue = 56
stringValue = 57
thisExpr = 58
lambdaExpr = 59
subexprExpr = 60
signalSlotExpr = 61
modernCastExpr = 62
typeIdExpr = 63
indexExpr = 64
callExpr = 65
fieldExpr = 66
ptrFieldExpr = 67
postIncExpr = 68
postDecExpr = 69
declSpec = 70
constSpec = 71
volatileSpec = 72
typeSpec = 73
typeName = 74
simpleItem = 75
simpleDecl = 76
namespaceDecl = 77
usingDecl = 78
externDecl = 79
typedefDecl = 80
friendDecl = 81
enumDecl = 82
classDecl = 83
visibilityDecl = 84
templateDecl = 85
stencilDecl = 86
extensionStat = 87
emptyStat = 88
compoundStat = 89
ifStat = 90
whileStat = 91
doStat = 92
forStat = 93
switchStat = 94
caseStat = 95
defaultStat = 96
breakStat = 97
continueStat = 98
returnStat = 99
gotoStat = 100
simpleStat = 101
dotsParam = 102
tryStat = 103

# CmmDeclaratorKind in CmmDeclarator
pointerDeclarator = 0
referenceDeclarator = 1
basicDeclarator = 2
emptyDeclarator = 3
nestedDeclarator = 4
arrayDeclarator = 5
functionDeclarator = 6

# CmmPtrKind in CmmPtrSpecifier

# CmmContKind in CmmContSpecifier

# CmmTemplateParamKind in CmmTemplateParam
templateTypeParam = 0
templateCommonParam = 1

# CmmModernCastExprCast_kind in CmmModernCastExpr
dynamicCast = 0
staticCast = 1
constCast = 2
reinterpreterCast = 3

# CmmClassDeclStyle in CmmClassDecl
classStyle = 0
structStyle = 1
unionStyle = 2

# CmmMemberVisibilityAccess in CmmMemberVisibility
privateAccess = 0
protectedAccess = 1
publicAccess = 2

# CmmBaseItemAccess in CmmBaseItem
privateBase = 0
protectedBase = 1
publicBase = 2
unknownBase = 3

class CmmBasic (object) :
   _fields_ = []
   def __init__ (self) :
      self.src_file = 0
      self.src_line = 0
      self.src_column = 0

class CmmCommon (CmmBasic) :
   _fields_ = []
   _tag_low_ = simpleName
   _tag_high_ = tryStat
   def __init__ (self) :
      super (CmmCommon, self).__init__ ()
      self.kind = 0

class CmmExpr (CmmCommon) :
   _fields_ = []
   _tag_low_ = simpleName
   _tag_high_ = typeName
   def __init__ (self) :
      super (CmmExpr, self).__init__ ()
      self.type_flag = False
      self.constructor_flag = False
      self.destructor_flag = False
      self.item_decl = None
      self.item_type = None
      self.alt_assign = ""
      self.alt_assign_index = ""
      self.alt_assign_param = ""
      self.alt_read = ""
      self.alt_connect = ""
      self.alt_connect_expr = None
      self.alt_connect_decl = None
      self.alt_connect_signal = ""
      self.alt_display = ""
      self.alt_store = ""
      self.alt_read_json = ""
      self.alt_write_json = ""
      self.alt_read_xml = ""
      self.alt_write_xml = ""
      self.gpu_global = False
      self.extra_assign = False
      self.call_func = False
      self.class_member = None
      self.var_field = False
      self.str_field = False
      self.stream_flag = False
      self.leading_flag = False
      self.following_items = [ ]

class CmmName (CmmExpr) :
   _fields_ = []
   _tag_low_ = simpleName
   _tag_high_ = specialName
   def __init__ (self) :
      super (CmmName, self).__init__ ()

class CmmUnaryExpr (CmmExpr) :
   _fields_ = []
   _tag_low_ = incExpr
   _tag_high_ = throwExpr
   def __init__ (self) :
      super (CmmUnaryExpr, self).__init__ ()

class CmmBinaryExpr (CmmExpr) :
   _fields_ = []
   _tag_low_ = castExpr
   _tag_high_ = commaExpr
   def __init__ (self) :
      super (CmmBinaryExpr, self).__init__ ()

class CmmStat (CmmCommon) :
   _fields_ = []
   _tag_low_ = simpleItem
   _tag_high_ = tryStat
   def __init__ (self) :
      super (CmmStat, self).__init__ ()
      self.move_statement = False

class CmmDecl (CmmStat) :
   _fields_ = []
   _tag_low_ = simpleItem
   _tag_high_ = stencilDecl
   def __init__ (self) :
      super (CmmDecl, self).__init__ ()

class CmmSimpleItem (CmmDecl) :
   _fields_ = ["declarator", "init", "attr"]
   def __init__ (self) :
      super (CmmSimpleItem, self).__init__ ()
      self.no_init = False
      self.extra_assign = False
      self.cont_line = False
      self.declarator = None
      self.init = None
      self.attr = None
      self.kind = simpleItem

class CmmDeclarator (object) :
   _fields_ = []
   _tag_low_ = pointerDeclarator
   _tag_high_ = functionDeclarator
   def __init__ (self) :
      self.kind = 0

class CmmPtrSpecifier (object) :
   _fields_ = []
   def __init__ (self) :
      self.kind = 0

class CmmContSpecifier (object) :
   _fields_ = []
   def __init__ (self) :
      self.kind = 0

class CmmTemplateParam (object) :
   _fields_ = []
   _tag_low_ = templateTypeParam
   _tag_high_ = templateCommonParam
   def __init__ (self) :
      self.kind = 0

class CmmExtensionStat (CmmStat) :
   _fields_ = []
   def __init__ (self) :
      super (CmmExtensionStat, self).__init__ ()
      self.kind = extensionStat

class CmmSimpleName (CmmName) :
   _fields_ = []
   def __init__ (self) :
      super (CmmSimpleName, self).__init__ ()
      self.id = ""
      self.kind = simpleName

class CmmGlobalName (CmmName) :
   _fields_ = ["inner_name"]
   def __init__ (self) :
      super (CmmGlobalName, self).__init__ ()
      self.inner_name = None
      self.kind = globalName

class CmmDestructorName (CmmName) :
   _fields_ = ["inner_name"]
   def __init__ (self) :
      super (CmmDestructorName, self).__init__ ()
      self.inner_name = None
      self.kind = destructorName

class CmmCompoundName (CmmName) :
   _fields_ = ["left", "right"]
   def __init__ (self) :
      super (CmmCompoundName, self).__init__ ()
      self.left = None
      self.right = None
      self.kind = compoundName

class CmmTemplateName (CmmName) :
   _fields_ = ["left", "template_args"]
   def __init__ (self) :
      super (CmmTemplateName, self).__init__ ()
      self.left = None
      self.template_args = None
      self.kind = templateName

class CmmIntValue (CmmExpr) :
   _fields_ = []
   def __init__ (self) :
      super (CmmIntValue, self).__init__ ()
      self.value = ""
      self.kind = intValue

class CmmRealValue (CmmExpr) :
   _fields_ = []
   def __init__ (self) :
      super (CmmRealValue, self).__init__ ()
      self.value = ""
      self.kind = realValue

class CmmCharValue (CmmExpr) :
   _fields_ = []
   def __init__ (self) :
      super (CmmCharValue, self).__init__ ()
      self.value = ""
      self.kind = charValue

class CmmStringValue (CmmExpr) :
   _fields_ = ["items"]
   def __init__ (self) :
      super (CmmStringValue, self).__init__ ()
      self.value = ""
      self.items = [ ]
      self.kind = stringValue

class CmmStringCont (object) :
   _fields_ = []
   def __init__ (self) :
      self.value = ""

class CmmThisExpr (CmmExpr) :
   _fields_ = []
   def __init__ (self) :
      super (CmmThisExpr, self).__init__ ()
      self.kind = thisExpr

class CmmLambdaExpr (CmmExpr) :
   _fields_ = ["body"]
   def __init__ (self) :
      super (CmmLambdaExpr, self).__init__ ()
      self.by_reference = False
      self.body = None
      self.kind = lambdaExpr

class CmmSubexprExpr (CmmExpr) :
   _fields_ = ["param"]
   def __init__ (self) :
      super (CmmSubexprExpr, self).__init__ ()
      self.param = None
      self.kind = subexprExpr

class CmmSignalSlotExpr (CmmExpr) :
   _fields_ = ["parameters"]
   def __init__ (self) :
      super (CmmSignalSlotExpr, self).__init__ ()
      self.macro_name = ""
      self.func_name = ""
      self.parameters = None
      self.kind = signalSlotExpr

class CmmModernCastExpr (CmmExpr) :
   _fields_ = ["type", "param"]
   def __init__ (self) :
      super (CmmModernCastExpr, self).__init__ ()
      self.cast_kind = 0
      self.type = None
      self.param = None
      self.kind = modernCastExpr

class CmmTypeIdExpr (CmmExpr) :
   _fields_ = ["value"]
   def __init__ (self) :
      super (CmmTypeIdExpr, self).__init__ ()
      self.value = None
      self.kind = typeIdExpr

class CmmIndexExpr (CmmExpr) :
   _fields_ = ["left", "param"]
   def __init__ (self) :
      super (CmmIndexExpr, self).__init__ ()
      self.left = None
      self.param = None
      self.kind = indexExpr

class CmmCallExpr (CmmExpr) :
   _fields_ = ["left", "param_list"]
   def __init__ (self) :
      super (CmmCallExpr, self).__init__ ()
      self.left = None
      self.param_list = None
      self.kind = callExpr

class CmmFieldExpr (CmmExpr) :
   _fields_ = ["left", "field_name"]
   def __init__ (self) :
      super (CmmFieldExpr, self).__init__ ()
      self.left = None
      self.field_name = None
      self.kind = fieldExpr

class CmmPtrFieldExpr (CmmExpr) :
   _fields_ = ["left", "field_name"]
   def __init__ (self) :
      super (CmmPtrFieldExpr, self).__init__ ()
      self.left = None
      self.field_name = None
      self.kind = ptrFieldExpr

class CmmPostIncExpr (CmmExpr) :
   _fields_ = ["left"]
   def __init__ (self) :
      super (CmmPostIncExpr, self).__init__ ()
      self.left = None
      self.kind = postIncExpr

class CmmPostDecExpr (CmmExpr) :
   _fields_ = ["left"]
   def __init__ (self) :
      super (CmmPostDecExpr, self).__init__ ()
      self.left = None
      self.kind = postDecExpr

class CmmExprList (object) :
   _fields_ = ["items"]
   def __init__ (self) :
      self.items = [ ]

class CmmIncExpr (CmmUnaryExpr) :
   _fields_ = ["param"]
   def __init__ (self) :
      super (CmmIncExpr, self).__init__ ()
      self.param = None
      self.kind = incExpr

class CmmDecExpr (CmmUnaryExpr) :
   _fields_ = ["param"]
   def __init__ (self) :
      super (CmmDecExpr, self).__init__ ()
      self.param = None
      self.kind = decExpr

class CmmDerefExpr (CmmUnaryExpr) :
   _fields_ = ["param"]
   def __init__ (self) :
      super (CmmDerefExpr, self).__init__ ()
      self.param = None
      self.kind = derefExpr

class CmmAddrExpr (CmmUnaryExpr) :
   _fields_ = ["param"]
   def __init__ (self) :
      super (CmmAddrExpr, self).__init__ ()
      self.param = None
      self.kind = addrExpr

class CmmPlusExpr (CmmUnaryExpr) :
   _fields_ = ["param"]
   def __init__ (self) :
      super (CmmPlusExpr, self).__init__ ()
      self.param = None
      self.kind = plusExpr

class CmmMinusExpr (CmmUnaryExpr) :
   _fields_ = ["param"]
   def __init__ (self) :
      super (CmmMinusExpr, self).__init__ ()
      self.param = None
      self.kind = minusExpr

class CmmBitNotExpr (CmmUnaryExpr) :
   _fields_ = ["param"]
   def __init__ (self) :
      super (CmmBitNotExpr, self).__init__ ()
      self.param = None
      self.kind = bitNotExpr

class CmmLogNotExpr (CmmUnaryExpr) :
   _fields_ = ["param"]
   def __init__ (self) :
      super (CmmLogNotExpr, self).__init__ ()
      self.param = None
      self.kind = logNotExpr

class CmmSizeofExpr (CmmUnaryExpr) :
   _fields_ = ["value"]
   def __init__ (self) :
      super (CmmSizeofExpr, self).__init__ ()
      self.value = None
      self.kind = sizeofExpr

class CmmNewExpr (CmmUnaryExpr) :
   _fields_ = ["type1", "type2", "init_list"]
   def __init__ (self) :
      super (CmmNewExpr, self).__init__ ()
      self.type1 = None
      self.type2 = None
      self.init_list = None
      self.kind = newExpr

class CmmNewTypeId (object) :
   _fields_ = ["type_spec", "ptr", "items"]
   def __init__ (self) :
      self.type_spec = None
      self.ptr = None
      self.items = [ ]

class CmmNewArrayLimit (object) :
   _fields_ = ["value"]
   def __init__ (self) :
      self.value = None

class CmmDeleteExpr (CmmUnaryExpr) :
   _fields_ = ["param"]
   def __init__ (self) :
      super (CmmDeleteExpr, self).__init__ ()
      self.a_array = False
      self.param = None
      self.kind = deleteExpr

class CmmEmptyStat (CmmStat) :
   _fields_ = []
   def __init__ (self) :
      super (CmmEmptyStat, self).__init__ ()
      self.kind = emptyStat

class CmmCompoundStat (CmmStat) :
   _fields_ = ["items"]
   def __init__ (self) :
      super (CmmCompoundStat, self).__init__ ()
      self.items = [ ]
      self.kind = compoundStat

class CmmIfStat (CmmStat) :
   _fields_ = ["cond", "then_stat", "else_stat"]
   def __init__ (self) :
      super (CmmIfStat, self).__init__ ()
      self.cond = None
      self.then_stat = None
      self.else_stat = None
      self.kind = ifStat

class CmmWhileStat (CmmStat) :
   _fields_ = ["cond", "body"]
   def __init__ (self) :
      super (CmmWhileStat, self).__init__ ()
      self.cond = None
      self.body = None
      self.kind = whileStat

class CmmDoStat (CmmStat) :
   _fields_ = ["body", "cond_expr"]
   def __init__ (self) :
      super (CmmDoStat, self).__init__ ()
      self.body = None
      self.cond_expr = None
      self.kind = doStat

class CmmForStat (CmmStat) :
   _fields_ = ["from_expr", "iter_expr", "cond_expr", "step_expr", "body"]
   def __init__ (self) :
      super (CmmForStat, self).__init__ ()
      self.from_expr = None
      self.iter_expr = None
      self.cond_expr = None
      self.step_expr = None
      self.body = None
      self.kind = forStat

class CmmSwitchStat (CmmStat) :
   _fields_ = ["cond", "body"]
   def __init__ (self) :
      super (CmmSwitchStat, self).__init__ ()
      self.cond = None
      self.body = None
      self.kind = switchStat

class CmmCaseStat (CmmStat) :
   _fields_ = ["case_expr", "body"]
   def __init__ (self) :
      super (CmmCaseStat, self).__init__ ()
      self.case_expr = None
      self.body = None
      self.kind = caseStat

class CmmDefaultStat (CmmStat) :
   _fields_ = ["body"]
   def __init__ (self) :
      super (CmmDefaultStat, self).__init__ ()
      self.body = None
      self.kind = defaultStat

class CmmBreakStat (CmmStat) :
   _fields_ = []
   def __init__ (self) :
      super (CmmBreakStat, self).__init__ ()
      self.kind = breakStat

class CmmContinueStat (CmmStat) :
   _fields_ = []
   def __init__ (self) :
      super (CmmContinueStat, self).__init__ ()
      self.kind = continueStat

class CmmReturnStat (CmmStat) :
   _fields_ = ["return_expr"]
   def __init__ (self) :
      super (CmmReturnStat, self).__init__ ()
      self.return_expr = None
      self.kind = returnStat

class CmmGotoStat (CmmStat) :
   _fields_ = []
   def __init__ (self) :
      super (CmmGotoStat, self).__init__ ()
      self.goto_lab = ""
      self.kind = gotoStat

class CmmSimpleStat (CmmStat) :
   _fields_ = ["inner_expr", "body"]
   def __init__ (self) :
      super (CmmSimpleStat, self).__init__ ()
      self.inner_expr = None
      self.body = None
      self.kind = simpleStat

class CmmDeclSpec (CmmExpr) :
   _fields_ = ["param"]
   def __init__ (self) :
      super (CmmDeclSpec, self).__init__ ()
      self.a_inline = False
      self.a_virtual = False
      self.a_explicit = False
      self.a_mutable = False
      self.a_static = False
      self.a_register = False
      self.a_destructor = False
      self.param = None
      self.kind = declSpec

class CmmConstSpecifier (CmmExpr) :
   _fields_ = ["param"]
   def __init__ (self) :
      super (CmmConstSpecifier, self).__init__ ()
      self.param = None
      self.kind = constSpec

class CmmVolatileSpecifier (CmmExpr) :
   _fields_ = ["param"]
   def __init__ (self) :
      super (CmmVolatileSpecifier, self).__init__ ()
      self.param = None
      self.kind = volatileSpec

class CmmTypeSpec (CmmExpr) :
   _fields_ = []
   def __init__ (self) :
      super (CmmTypeSpec, self).__init__ ()
      self.a_signed = False
      self.a_unsigned = False
      self.a_short = False
      self.a_long = False
      self.a_long_long = False
      self.a_long_double = False
      self.a_bool = False
      self.a_char = False
      self.a_wchar = False
      self.a_int = False
      self.a_float = False
      self.a_double = False
      self.a_void = False
      self.kind = typeSpec

class CmmTypeName (CmmExpr) :
   _fields_ = ["qual_name"]
   def __init__ (self) :
      super (CmmTypeName, self).__init__ ()
      self.qual_name = None
      self.kind = typeName

class CmmPointerDeclarator (CmmDeclarator) :
   _fields_ = ["cv_spec", "inner_declarator"]
   def __init__ (self) :
      super (CmmPointerDeclarator, self).__init__ ()
      self.cv_spec = None
      self.inner_declarator = None
      self.kind = pointerDeclarator

class CmmReferenceDeclator (CmmDeclarator) :
   _fields_ = ["cv_spec", "inner_declarator"]
   def __init__ (self) :
      super (CmmReferenceDeclator, self).__init__ ()
      self.cv_spec = None
      self.inner_declarator = None
      self.kind = referenceDeclarator

class CmmCvSpecifier (object) :
   _fields_ = []
   def __init__ (self) :
      self.cv_const = False
      self.cv_volatile = False

class CmmBasicDeclarator (CmmDeclarator) :
   _fields_ = ["qual_name"]
   def __init__ (self) :
      super (CmmBasicDeclarator, self).__init__ ()
      self.qual_name = None
      self.kind = basicDeclarator

class CmmEmptyDeclarator (CmmDeclarator) :
   _fields_ = []
   def __init__ (self) :
      super (CmmEmptyDeclarator, self).__init__ ()
      self.kind = emptyDeclarator

class CmmNestedDeclarator (CmmDeclarator) :
   _fields_ = ["inner_declarator"]
   def __init__ (self) :
      super (CmmNestedDeclarator, self).__init__ ()
      self.inner_declarator = None
      self.kind = nestedDeclarator

class CmmArrayDeclarator (CmmDeclarator) :
   _fields_ = ["inner_declarator", "lim"]
   def __init__ (self) :
      super (CmmArrayDeclarator, self).__init__ ()
      self.inner_declarator = None
      self.lim = None
      self.kind = arrayDeclarator

class CmmFunctionDeclarator (CmmDeclarator) :
   _fields_ = ["inner_declarator", "parameters", "exception_spec"]
   def __init__ (self) :
      super (CmmFunctionDeclarator, self).__init__ ()
      self.inner_declarator = None
      self.parameters = None
      self.a_const = False
      self.a_override = False
      self.exception_spec = None
      self.kind = functionDeclarator

class CmmPtrSpecifierSect (object) :
   _fields_ = []
   def __init__ (self) :
      pass

class CmmStatSect (object) :
   _fields_ = ["items"]
   def __init__ (self) :
      self.items = [ ]

class CmmSimpleDecl (CmmDecl) :
   _fields_ = ["type_spec", "items", "body", "ctor_init"]
   def __init__ (self) :
      super (CmmSimpleDecl, self).__init__ ()
      self.type_spec = None
      self.items = [ ]
      self.body = None
      self.ctor_init = None
      self.kind = simpleDecl

class CmmDotsParam (CmmStat) :
   _fields_ = []
   def __init__ (self) :
      super (CmmDotsParam, self).__init__ ()
      self.kind = dotsParam

class CmmTypeId (object) :
   _fields_ = ["type_spec", "declarator"]
   def __init__ (self) :
      self.type_spec = None
      self.declarator = None

class CmmInitializer (object) :
   _fields_ = ["value"]
   def __init__ (self) :
      self.value = None

class CmmInitItem (object) :
   _fields_ = []
   def __init__ (self) :
      pass

class CmmInitSimple (CmmInitItem) :
   _fields_ = ["inner_expr"]
   def __init__ (self) :
      super (CmmInitSimple, self).__init__ ()
      self.inner_expr = None

class CmmInitList (CmmInitItem) :
   _fields_ = ["items"]
   def __init__ (self) :
      super (CmmInitList, self).__init__ ()
      self.items = [ ]

class CmmAttr (object) :
   _fields_ = ["attr_expr"]
   def __init__ (self) :
      self.attr_expr = None

class CmmAttrGroup (object) :
   _fields_ = ["items"]
   def __init__ (self) :
      self.items = [ ]

class CmmAttrSect (object) :
   _fields_ = ["items"]
   def __init__ (self) :
      self.items = [ ]

class CmmNamespaceDecl (CmmDecl) :
   _fields_ = ["simp_name", "attr", "members"]
   def __init__ (self) :
      super (CmmNamespaceDecl, self).__init__ ()
      self.simp_name = None
      self.attr = None
      self.members = None
      self.kind = namespaceDecl

class CmmUsingDecl (CmmDecl) :
   _fields_ = ["qual_name"]
   def __init__ (self) :
      super (CmmUsingDecl, self).__init__ ()
      self.a_namespace = False
      self.qual_name = None
      self.kind = usingDecl

class CmmExternDecl (CmmDecl) :
   _fields_ = ["members", "inner_declaration"]
   def __init__ (self) :
      super (CmmExternDecl, self).__init__ ()
      self.language = ""
      self.members = None
      self.inner_declaration = None
      self.kind = externDecl

class CmmTypedefDecl (CmmDecl) :
   _fields_ = ["type_spec", "declarator"]
   def __init__ (self) :
      super (CmmTypedefDecl, self).__init__ ()
      self.type_spec = None
      self.declarator = None
      self.kind = typedefDecl

class CmmFriendDecl (CmmDecl) :
   _fields_ = ["inner_declaration"]
   def __init__ (self) :
      super (CmmFriendDecl, self).__init__ ()
      self.inner_declaration = None
      self.kind = friendDecl

class CmmEnumDecl (CmmDecl) :
   _fields_ = ["simp_name", "enum_items"]
   def __init__ (self) :
      super (CmmEnumDecl, self).__init__ ()
      self.simp_name = None
      self.enum_items = None
      self.kind = enumDecl

class CmmEnumSect (object) :
   _fields_ = ["items"]
   def __init__ (self) :
      self.items = [ ]

class CmmEnumItem (object) :
   _fields_ = ["simp_name", "init_value"]
   def __init__ (self) :
      self.simp_name = None
      self.init_value = None

class CmmClassDecl (CmmDecl) :
   _fields_ = ["simp_name", "attr", "base_list", "members"]
   def __init__ (self) :
      super (CmmClassDecl, self).__init__ ()
      self.style = 0
      self.simp_name = None
      self.attr = None
      self.base_list = None
      self.members = None
      self.kind = classDecl

class CmmMemberVisibility (CmmDecl) :
   _fields_ = []
   def __init__ (self) :
      super (CmmMemberVisibility, self).__init__ ()
      self.access = 0
      self.kind = visibilityDecl

class CmmBaseSect (object) :
   _fields_ = ["items"]
   def __init__ (self) :
      self.items = [ ]

class CmmBaseItem (object) :
   _fields_ = ["from_cls"]
   def __init__ (self) :
      self.a_virtual = False
      self.access = 0
      self.from_cls = None

class CmmCtorInitializer (object) :
   _fields_ = ["items"]
   def __init__ (self) :
      self.items = [ ]

class CmmMemberInitializer (object) :
   _fields_ = ["simp_name", "params"]
   def __init__ (self) :
      self.simp_name = None
      self.params = None

class CmmConvSpec (object) :
   _fields_ = ["type_spec", "ptr_spec"]
   def __init__ (self) :
      self.type_spec = None
      self.ptr_spec = None

class CmmSpecialFuction (CmmName) :
   _fields_ = ["conv"]
   def __init__ (self) :
      super (CmmSpecialFuction, self).__init__ ()
      self.conv = None
      self.spec_new = False
      self.spec_new_array = False
      self.spec_delete = False
      self.spec_delete_array = False
      self.spec_add = False
      self.spec_sub = False
      self.spec_mul = False
      self.spec_div = False
      self.spec_mod = False
      self.spec_xor = False
      self.spec_and = False
      self.spec_or = False
      self.spec_not = False
      self.spec_log_not = False
      self.spec_assign = False
      self.spec_lt = False
      self.spec_gt = False
      self.spec_add_assign = False
      self.spec_sub_assign = False
      self.spec_mul_assign = False
      self.spec_div_assign = False
      self.spec_mod_assign = False
      self.spec_xor_assign = False
      self.spec_and_assign = False
      self.spec_or_assign = False
      self.spec_shl = False
      self.spec_shr = False
      self.spec_shl_assign = False
      self.spec_shr_assign = False
      self.spec_eq = False
      self.spec_ne = False
      self.spec_le = False
      self.spec_ge = False
      self.spec_log_and = False
      self.spec_log_or = False
      self.spec_inc = False
      self.spec_dec = False
      self.spec_comma = False
      self.spec_member_deref = False
      self.spec_deref = False
      self.spec_call = False
      self.spec_index = False
      self.kind = specialName

class CmmTemplateDecl (CmmDecl) :
   _fields_ = ["params", "inner_declaration"]
   def __init__ (self) :
      super (CmmTemplateDecl, self).__init__ ()
      self.params = None
      self.inner_declaration = None
      self.kind = templateDecl

class CmmStencilDecl (CmmDecl) :
   _fields_ = ["simp_name", "params", "members"]
   def __init__ (self) :
      super (CmmStencilDecl, self).__init__ ()
      self.simp_name = None
      self.params = None
      self.members = None
      self.kind = stencilDecl

class CmmTemplateParamSect (object) :
   _fields_ = ["items"]
   def __init__ (self) :
      self.items = [ ]

class CmmTemplateTypeParam (CmmTemplateParam) :
   _fields_ = ["params", "simp_name"]
   def __init__ (self) :
      super (CmmTemplateTypeParam, self).__init__ ()
      self.params = None
      self.a_class = False
      self.a_typename = False
      self.simp_name = None
      self.kind = templateTypeParam

class CmmTemplateNormalParam (CmmTemplateParam) :
   _fields_ = ["type_spec", "declarator", "init"]
   def __init__ (self) :
      super (CmmTemplateNormalParam, self).__init__ ()
      self.type_spec = None
      self.declarator = None
      self.init = None
      self.kind = templateCommonParam

class CmmTemplateArgSect (object) :
   _fields_ = ["items"]
   def __init__ (self) :
      self.items = [ ]

class CmmTemplateArg (object) :
   _fields_ = ["value"]
   def __init__ (self) :
      self.value = None

class CmmTryStat (CmmStat) :
   _fields_ = ["body", "handlers"]
   def __init__ (self) :
      super (CmmTryStat, self).__init__ ()
      self.body = None
      self.handlers = None
      self.kind = tryStat

class CmmHandlerSect (object) :
   _fields_ = ["items"]
   def __init__ (self) :
      self.items = [ ]

class CmmHandlerItem (object) :
   _fields_ = ["type_spec", "declarator", "body"]
   def __init__ (self) :
      self.type_spec = None
      self.declarator = None
      self.dots = False
      self.body = None

class CmmThrowExpr (CmmUnaryExpr) :
   _fields_ = ["inner_expr"]
   def __init__ (self) :
      super (CmmThrowExpr, self).__init__ ()
      self.inner_expr = None
      self.kind = throwExpr

class CmmExceptionSect (object) :
   _fields_ = ["items"]
   def __init__ (self) :
      self.items = [ ]

class CmmExceptionItem (object) :
   _fields_ = ["type"]
   def __init__ (self) :
      self.type = None

class CmmCastExpr (CmmBinaryExpr) :
   _fields_ = ["left", "right"]
   def __init__ (self) :
      super (CmmCastExpr, self).__init__ ()
      self.left = None
      self.right = None
      self.kind = castExpr

class CmmPtrMemExpr (CmmBinaryExpr) :
   _fields_ = ["left", "right"]
   _tag_low_ = dotMemberExpr
   _tag_high_ = arrowMemberExpr
   def __init__ (self) :
      super (CmmPtrMemExpr, self).__init__ ()
      self.left = None
      self.right = None

class CmmMulExpr (CmmBinaryExpr) :
   _fields_ = ["left", "right"]
   _tag_low_ = mulExpr
   _tag_high_ = customMulExpr
   def __init__ (self) :
      super (CmmMulExpr, self).__init__ ()
      self.left = None
      self.custom_mul = ""
      self.right = None

class CmmAddExpr (CmmBinaryExpr) :
   _fields_ = ["left", "right"]
   _tag_low_ = addExpr
   _tag_high_ = customAddExpr
   def __init__ (self) :
      super (CmmAddExpr, self).__init__ ()
      self.left = None
      self.custom_add = ""
      self.right = None

class CmmShiftExpr (CmmBinaryExpr) :
   _fields_ = ["left", "right"]
   _tag_low_ = shlExpr
   _tag_high_ = shrExpr
   def __init__ (self) :
      super (CmmShiftExpr, self).__init__ ()
      self.left = None
      self.right = None

class CmmRelExpr (CmmBinaryExpr) :
   _fields_ = ["left", "right"]
   _tag_low_ = ltExpr
   _tag_high_ = geExpr
   def __init__ (self) :
      super (CmmRelExpr, self).__init__ ()
      self.left = None
      self.right = None

class CmmEqExpr (CmmBinaryExpr) :
   _fields_ = ["left", "right"]
   _tag_low_ = eqExpr
   _tag_high_ = neExpr
   def __init__ (self) :
      super (CmmEqExpr, self).__init__ ()
      self.left = None
      self.right = None

class CmmAndExpr (CmmBinaryExpr) :
   _fields_ = ["left", "right"]
   def __init__ (self) :
      super (CmmAndExpr, self).__init__ ()
      self.left = None
      self.right = None
      self.kind = bitAndExpr

class CmmXorExpr (CmmBinaryExpr) :
   _fields_ = ["left", "right"]
   def __init__ (self) :
      super (CmmXorExpr, self).__init__ ()
      self.left = None
      self.right = None
      self.kind = bitXorExpr

class CmmOrExpr (CmmBinaryExpr) :
   _fields_ = ["left", "right"]
   _tag_low_ = bitOrExpr
   _tag_high_ = bitOrExpr
   def __init__ (self) :
      super (CmmOrExpr, self).__init__ ()
      self.left = None
      self.right = None

class CmmAndAndExpr (CmmBinaryExpr) :
   _fields_ = ["left", "right"]
   def __init__ (self) :
      super (CmmAndAndExpr, self).__init__ ()
      self.left = None
      self.right = None
      self.kind = logAndExpr

class CmmOrOrExpr (CmmBinaryExpr) :
   _fields_ = ["left", "right"]
   def __init__ (self) :
      super (CmmOrOrExpr, self).__init__ ()
      self.left = None
      self.right = None
      self.kind = logOrExpr

class CmmAssignExpr (CmmBinaryExpr) :
   _fields_ = ["left", "middle", "right"]
   _tag_low_ = assignExpr
   _tag_high_ = condExpr
   def __init__ (self) :
      super (CmmAssignExpr, self).__init__ ()
      self.left = None
      self.middle = None
      self.right = None

class CmmCommaExpr (CmmBinaryExpr) :
   _fields_ = ["left", "right"]
   def __init__ (self) :
      super (CmmCommaExpr, self).__init__ ()
      self.left = None
      self.right = None
      self.kind = commaExpr

Namespace = CmmNamespaceDecl
Class = CmmClassDecl
Enum = CmmEnumDecl
Typedef = CmmTypedefDecl
Variable = CmmSimpleItem
