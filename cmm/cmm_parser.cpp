#include "cmm_parser.h"

const unsigned char set_0 [15] = {62, 128, 0, 0, 4, 128, 0, 0, 0, 0, 0, 1, 0, 2, 0};
// set_0 :  identifier number real_number character_literal string_literal ( :: [ operator this

const unsigned char set_1 [15] = {0, 0, 0, 0, 0, 0, 0, 0, 4, 1, 0, 64, 16, 0, 0};
// set_1 :  const_cast dynamic_cast reinterpret_cast static_cast

const unsigned char set_2 [15] = {0, 0, 0, 0, 0, 0, 0, 136, 128, 32, 24, 0, 3, 0, 41};
// set_2 :  bool char double float int long short signed unsigned void wchar_t

const unsigned char set_3 [15] = {0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 36, 32, 8, 0, 4};
// set_3 :  explicit inline mutable register static virtual

const unsigned char set_4 [15] = {0, 128, 16, 21, 0, 128, 0, 0, 0, 0, 0, 0, 0, 0, 0};
// set_4 :  ( ++ -- -> . [

const unsigned char set_5 [15] = {62, 145, 154, 1, 4, 128, 0, 140, 166, 41, 188, 97, 31, 102, 61};
// set_5 :  identifier number real_number character_literal string_literal ! & ( * + ++ - -- :: [ ~ bool char const const_cast delete double dynamic_cast explicit float inline int long mutable new operator register reinterpret_cast short signed sizeof static static_cast this throw typeid typename unsigned virtual void volatile wchar_t

const unsigned char set_6 [15] = {62, 128, 0, 0, 4, 128, 0, 136, 134, 41, 60, 97, 27, 98, 61};
// set_6 :  identifier number real_number character_literal string_literal ( :: [ bool char const const_cast double dynamic_cast explicit float inline int long mutable operator register reinterpret_cast short signed static static_cast this typeid typename unsigned virtual void volatile wchar_t

const unsigned char set_7 [15] = {2, 0, 0, 0, 4, 0, 0, 136, 130, 40, 60, 33, 11, 64, 61};
// set_7 :  identifier :: bool char const double explicit float inline int long mutable operator register short signed static typename unsigned virtual void volatile wchar_t

const unsigned char set_8 [15] = {2, 4, 2, 128, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
// set_8 :  identifier % * /

const unsigned char set_9 [15] = {0, 0, 0, 0, 144, 12, 0, 0, 0, 0, 0, 0, 0, 0, 0};
// set_9 :  < <= > >=

const unsigned char set_10 [15] = {0, 72, 36, 2, 65, 97, 144, 0, 0, 0, 0, 0, 0, 0, 0};
// set_10 :  %= &= *= += -= /= <<= = >>= ? ^= |=

const unsigned char set_11 [15] = {62, 145, 154, 1, 12, 128, 32, 188, 254, 105, 191, 225, 159, 110, 125};
// set_11 :  identifier number real_number character_literal string_literal ! & ( * + ++ - -- :: ; [ { ~ bool break case char const const_cast continue default delete do double dynamic_cast explicit float for goto if inline int long mutable new operator register reinterpret_cast return short signed sizeof static static_cast switch this throw try typeid typename unsigned virtual void volatile wchar_t while

const unsigned char set_12 [15] = {2, 144, 66, 0, 12, 129, 33, 0, 0, 0, 0, 1, 0, 0, 0};
// set_12 :  identifier & ( * , :: ; = [ [[ { operator

const unsigned char set_13 [15] = {2, 128, 0, 0, 4, 128, 0, 0, 0, 0, 0, 1, 0, 0, 0};
// set_13 :  identifier ( :: [ operator

const unsigned char set_14 [15] = {62, 145, 154, 65, 4, 128, 0, 140, 166, 41, 188, 97, 31, 102, 61};
// set_14 :  identifier number real_number character_literal string_literal ! & ( * + ++ - -- ... :: [ ~ bool char const const_cast delete double dynamic_cast explicit float inline int long mutable new operator register reinterpret_cast short signed sizeof static static_cast this throw typeid typename unsigned virtual void volatile wchar_t

const unsigned char set_15 [15] = {2, 144, 2, 0, 4, 129, 1, 0, 0, 0, 0, 1, 0, 0, 0};
// set_15 :  identifier & ( * :: = [ [[ operator

const unsigned char set_16 [15] = {62, 145, 154, 1, 4, 128, 32, 140, 166, 41, 188, 97, 31, 102, 61};
// set_16 :  identifier number real_number character_literal string_literal ! & ( * + ++ - -- :: [ { ~ bool char const const_cast delete double dynamic_cast explicit float inline int long mutable new operator register reinterpret_cast short signed sizeof static static_cast this throw typeid typename unsigned virtual void volatile wchar_t

const unsigned char set_17 [15] = {2, 144, 66, 0, 4, 129, 1, 0, 0, 0, 0, 1, 0, 0, 0};
// set_17 :  identifier & ( * , :: = [ [[ operator

const unsigned char set_18 [15] = {62, 145, 154, 1, 12, 128, 32, 140, 231, 253, 254, 97, 255, 247, 127};
// set_18 :  identifier number real_number character_literal string_literal ! & ( * + ++ - -- :: ; [ { ~ bool char class const const_cast delete do double dynamic_cast enum explicit extern float for friend if inline int long mutable namespace new operator register reinterpret_cast short signed sizeof static static_cast stencil struct switch template this throw typedef typeid typename union unsigned using virtual void volatile wchar_t while

const unsigned char set_19 [15] = {62, 145, 154, 1, 12, 128, 32, 140, 167, 237, 190, 125, 127, 247, 127};
// set_19 :  identifier number real_number character_literal string_literal ! & ( * + ++ - -- :: ; [ { ~ bool char class const const_cast delete double dynamic_cast enum explicit float for friend if inline int long mutable new operator private protected public register reinterpret_cast short signed sizeof static static_cast stencil struct template this throw typedef typeid typename union unsigned using virtual void volatile wchar_t while

const unsigned char set_20 [15] = {2, 0, 0, 0, 4, 0, 0, 136, 131, 40, 60, 33, 11, 65, 61};
// set_20 :  identifier :: bool char class const double explicit float inline int long mutable operator register short signed static template typename unsigned virtual void volatile wchar_t


CmmSimpleName * Parser::parse_simple_name ()
{

      CmmSimpleName * result = new CmmSimpleName;
      result->kind = simpleName;
      storeLocation (result);
      result->id = readIdent ();
      return result;
}

CmmName * Parser::parse_global_variant ()
{

      CmmName * result = NULL;
      if (isSymbol (identifier))
      {
         result = parse_simple_name ();
      }
      else if (isSymbol (keyword_operator))
      {
         result = parse_special_function ();
      }
      else {
         stop ("Unexpected token");
      }
      return result;
}

CmmGlobalName * Parser::parse_global_name ()
{

      CmmGlobalName * result = new CmmGlobalName;
      result->kind = globalName;
      storeLocation (result);
      checkSymbol (SCOPE);
      result->inner_name = parse_global_variant ();
      return result;
}

CmmName * Parser::parse_base_variant ()
{

      CmmName * result = NULL;
      if (isSymbol (SCOPE))
      {
         result = parse_global_name ();
      }
      else if (isSymbol (identifier))
      {
         result = parse_simple_name ();
      }
      else if (isSymbol (keyword_operator))
      {
         result = parse_special_function ();
      }
      else {
         stop ("Unexpected token");
      }
      return result;
}

CmmName * Parser::parse_base_name ()
{

      CmmName * result = NULL;
      result = parse_base_variant ();
      on_base_name (result);
      return result;
}

CmmDestructorName * Parser::parse_destructor_name ()
{

      CmmDestructorName * result = new CmmDestructorName;
      result->kind = destructorName;
      storeLocation (result);
      checkSymbol (BIT_NOT);
      result->inner_name = parse_simple_name ();
      return result;
}

CmmName * Parser::parse_cont_variant ()
{

      CmmName * result = NULL;
      if (isSymbol (identifier))
      {
         result = parse_simple_name ();
      }
      else if (isSymbol (keyword_operator))
      {
         result = parse_special_function ();
      }
      else if (isSymbol (BIT_NOT))
      {
         result = parse_destructor_name ();
      }
      else {
         stop ("Unexpected token");
      }
      return result;
}

CmmCompoundName * Parser::parse_cont_name (CmmName * store)
{

      CmmCompoundName * result = new CmmCompoundName;
      result->kind = compoundName;
      storeLocation (result);
      result->left = store;
      checkSymbol (SCOPE);
      result->right = parse_cont_variant ();
      on_cont_name (result);
      return result;
}

CmmTemplateName * Parser::parse_template_name (CmmName * store)
{

      CmmTemplateName * result = new CmmTemplateName;
      result->kind = templateName;
      storeLocation (result);
      result->left = store;
      result->template_args = parse_template_arg_list ();
      on_template_name (result);
      return result;
}

CmmName * Parser::parse_field_name ()
{

      CmmName * result = NULL;
      result = parse_simple_name ();
      while (isSymbol (LESS) && is_template_name (result))
      {
         result = parse_template_name (result);
         on_base_name (result);
      }
      return result;
}

CmmName * Parser::parse_qualified_name ()
{

      CmmName * result = NULL;
      result = parse_base_name ();
      while (isSymbol (SCOPE) || isSymbol (LESS) && is_template_name (result))
      {
         if (isSymbol (SCOPE))
         {
            result = parse_cont_name (result);
            on_base_name (result);
         }
         else if (isSymbol (LESS) && is_template_name (result))
         {
            result = parse_template_name (result);
            on_base_name (result);
         }
         else {
            stop ("Unexpected token");
         }
      }
      return result;
}

CmmName * Parser::parse_new_qualified_name ()
{

      CmmName * result = NULL;
      result = parse_base_variant ();
      while (isSymbol (SCOPE) || isSymbol (LESS) && is_template_name (result))
      {
         if (isSymbol (SCOPE))
         {
            on_base_name (result);
            result = parse_cont_name (result);
         }
         else if (isSymbol (LESS) && is_template_name (result))
         {
            on_base_name (result);
            result = parse_template_name (result);
         }
         else {
            stop ("Unexpected token");
         }
      }
      return result;
}

CmmExpr * Parser::parse_primary_expr ()
{

      CmmExpr * result = NULL;
      if (isSymbol (identifier) || isSymbol (SCOPE) || isSymbol (keyword_operator))
      {
         result = parse_ident_expr ();
      }
      else if (isSymbol (number))
      {
         result = parse_int_value ();
      }
      else if (isSymbol (real_number))
      {
         result = parse_real_value ();
      }
      else if (isSymbol (character_literal))
      {
         result = parse_char_value ();
      }
      else if (isSymbol (string_literal))
      {
         result = parse_string_value ();
      }
      else if (isSymbol (keyword_this))
      {
         result = parse_this_expr ();
      }
      else if (isSymbol (LBRACKET))
      {
         result = parse_lambda_expr ();
      }
      else if (isSymbol (LPAREN))
      {
         result = parse_subexpr_expr ();
      }
      else {
         stop ("Unexpected token");
      }
      return result;
}

CmmName * Parser::parse_ident_expr ()
{

      CmmName * result = NULL;
      result = parse_qualified_name ();
      on_ident_expr (result);
      return result;
}

CmmIntValue * Parser::parse_int_value ()
{

      CmmIntValue * result = new CmmIntValue;
      result->kind = intValue;
      storeLocation (result);
      result->value = readNumber ();
      on_int_value (result);
      return result;
}

CmmRealValue * Parser::parse_real_value ()
{

      CmmRealValue * result = new CmmRealValue;
      result->kind = realValue;
      storeLocation (result);
      result->value = readReal ();
      on_real_value (result);
      return result;
}

CmmCharValue * Parser::parse_char_value ()
{

      CmmCharValue * result = new CmmCharValue;
      result->kind = charValue;
      storeLocation (result);
      result->value = readQuotedCharAsString ();
      on_char_value (result);
      return result;
}

CmmStringValue * Parser::parse_string_value ()
{

      CmmStringValue * result = new CmmStringValue;
      result->kind = stringValue;
      storeLocation (result);
      result->value = readQuotedString ();
      while (isSymbol (string_literal))
      {
         result->items.push_back (parse_string_value_cont ());
      }
      on_string_value (result);
      return result;
}

CmmStringCont * Parser::parse_string_value_cont ()
{

      CmmStringCont * result = new CmmStringCont;
      storeLocation (result);
      result->value = readQuotedString ();
      return result;
}

CmmThisExpr * Parser::parse_this_expr ()
{

      CmmThisExpr * result = new CmmThisExpr;
      result->kind = thisExpr;
      storeLocation (result);
      checkSymbol (keyword_this);
      on_this_expr (result);
      return result;
}

CmmLambdaExpr * Parser::parse_lambda_expr ()
{

      CmmLambdaExpr * result = new CmmLambdaExpr;
      result->kind = lambdaExpr;
      storeLocation (result);
      checkSymbol (LBRACKET);
      if (isSymbol (BIT_AND))
      {
         checkSymbol (BIT_AND);
         result->by_reference = true;
      }
      checkSymbol (RBRACKET);
      result->body = parse_compound_stat ();
      return result;
}

CmmSubexprExpr * Parser::parse_subexpr_expr ()
{

      CmmSubexprExpr * result = new CmmSubexprExpr;
      result->kind = subexprExpr;
      storeLocation (result);
      checkSymbol (LPAREN);
      result->param = parse_expr ();
      checkSymbol (RPAREN);
      on_subexpr_expr (result);
      return result;
}

CmmExpr * Parser::parse_postfix_start ()
{

      CmmExpr * result = NULL;
      if (isSymbol (identifier) && is_signal_slot (result))
      {
         result = parse_signal_slot_expr ();
      }
      else if (testSymbols (set_0))
      {
         result = parse_primary_expr ();
      }
      else if (testSymbols (set_1))
      {
         result = parse_modern_cast_expr ();
      }
      else if (isSymbol (keyword_typeid))
      {
         result = parse_typeid_expr ();
      }
      else if (isSymbol (keyword_typename))
      {
         result = parse_type_name ();
      }
      else if (testSymbols (set_2))
      {
         result = parse_type_specifier ();
      }
      else if (isSymbol (keyword_const))
      {
         result = parse_const_specifier ();
      }
      else if (isSymbol (keyword_volatile))
      {
         result = parse_volatile_specifier ();
      }
      else if (testSymbols (set_3))
      {
         result = parse_decl_specifier ();
      }
      else {
         stop ("Unexpected token");
      }
      return result;
}

CmmSignalSlotExpr * Parser::parse_signal_slot_expr ()
{

      CmmSignalSlotExpr * result = new CmmSignalSlotExpr;
      result->kind = signalSlotExpr;
      storeLocation (result);
      result->macro_name = readIdent ();
      checkSymbol (LPAREN);
      result->func_name = readIdent ();
      if (isSymbol (LPAREN))
      {
         checkSymbol (LPAREN);
         result->parameters = parse_parameter_declaration_list ();
         checkSymbol (RPAREN);
      }
      checkSymbol (RPAREN);
      return result;
}

CmmModernCastExpr * Parser::parse_modern_cast_expr ()
{

      CmmModernCastExpr * result = new CmmModernCastExpr;
      result->kind = modernCastExpr;
      storeLocation (result);
      if (isSymbol (keyword_dynamic_cast))
      {
         checkSymbol (keyword_dynamic_cast);
         result->cast_kind = dynamicCast;
      }
      else if (isSymbol (keyword_static_cast))
      {
         checkSymbol (keyword_static_cast);
         result->cast_kind = staticCast;
      }
      else if (isSymbol (keyword_const_cast))
      {
         checkSymbol (keyword_const_cast);
         result->cast_kind = constCast;
      }
      else if (isSymbol (keyword_reinterpret_cast))
      {
         checkSymbol (keyword_reinterpret_cast);
         result->cast_kind = reinterpreterCast;
      }
      else {
         stop ("Unexpected token");
      }
      checkSymbol (LESS);
      result->type = parse_type_id ();
      checkSymbol (GREATER);
      checkSymbol (LPAREN);
      result->param = parse_expr ();
      checkSymbol (RPAREN);
      on_modern_cast_expr (result);
      return result;
}

CmmTypeIdExpr * Parser::parse_typeid_expr ()
{

      CmmTypeIdExpr * result = new CmmTypeIdExpr;
      result->kind = typeIdExpr;
      storeLocation (result);
      checkSymbol (keyword_typeid);
      checkSymbol (LPAREN);
      result->value = parse_expr ();
      checkSymbol (RPAREN);
      on_typeid_expr (result);
      return result;
}

CmmExpr * Parser::parse_postfix_expr ()
{

      CmmExpr * result = NULL;
      result = parse_postfix_start ();
      if (is_postfix_expression (result))
      {
         while (isSymbol (LBRACKET) || isSymbol (LPAREN) || isSymbol (DOT) || isSymbol (ARROW) || isSymbol (INC) || isSymbol (DEC))
         {
            if (isSymbol (LBRACKET))
            {
               result = parse_index_expr (result);
            }
            else if (isSymbol (LPAREN))
            {
               result = parse_call_expr (result);
            }
            else if (isSymbol (DOT))
            {
               result = parse_field_expr (result);
            }
            else if (isSymbol (ARROW))
            {
               result = parse_ptr_field_expr (result);
            }
            else if (isSymbol (INC))
            {
               result = parse_post_inc_expr (result);
            }
            else if (isSymbol (DEC))
            {
               result = parse_post_dec_expr (result);
            }
            else {
               stop ("Unexpected token");
            }
         }
      }
      return result;
}

CmmIndexExpr * Parser::parse_index_expr (CmmExpr * store)
{

      CmmIndexExpr * result = new CmmIndexExpr;
      result->kind = indexExpr;
      storeLocation (result);
      result->left = store;
      checkSymbol (LBRACKET);
      result->param = parse_expr ();
      checkSymbol (RBRACKET);
      on_index_expr (result);
      return result;
}

CmmCallExpr * Parser::parse_call_expr (CmmExpr * store)
{

      CmmCallExpr * result = new CmmCallExpr;
      result->kind = callExpr;
      storeLocation (result);
      result->left = store;
      checkSymbol (LPAREN);
      result->param_list = parse_expr_list ();
      checkSymbol (RPAREN);
      on_call_expr (result);
      return result;
}

CmmFieldExpr * Parser::parse_field_expr (CmmExpr * store)
{

      CmmFieldExpr * result = new CmmFieldExpr;
      result->kind = fieldExpr;
      storeLocation (result);
      result->left = store;
      checkSymbol (DOT);
      result->field_name = parse_field_name ();
      on_field_expr (result);
      return result;
}

CmmPtrFieldExpr * Parser::parse_ptr_field_expr (CmmExpr * store)
{

      CmmPtrFieldExpr * result = new CmmPtrFieldExpr;
      result->kind = ptrFieldExpr;
      storeLocation (result);
      result->left = store;
      checkSymbol (ARROW);
      result->field_name = parse_field_name ();
      on_ptr_field_expr (result);
      return result;
}

CmmPostIncExpr * Parser::parse_post_inc_expr (CmmExpr * store)
{

      CmmPostIncExpr * result = new CmmPostIncExpr;
      result->kind = postIncExpr;
      storeLocation (result);
      result->left = store;
      checkSymbol (INC);
      on_post_inc_expr (result);
      return result;
}

CmmPostDecExpr * Parser::parse_post_dec_expr (CmmExpr * store)
{

      CmmPostDecExpr * result = new CmmPostDecExpr;
      result->kind = postDecExpr;
      storeLocation (result);
      result->left = store;
      checkSymbol (DEC);
      on_post_dec_expr (result);
      return result;
}

CmmExprList * Parser::parse_expr_list ()
{

      CmmExprList * result = new CmmExprList;
      storeLocation (result);
      if (testSymbols (set_5))
      {
         result->items.push_back (parse_assignment_expr ());
         while (isSymbol (COMMA))
         {
            checkSymbol (COMMA);
            result->items.push_back (parse_assignment_expr ());
         }
      }
      return result;
}

CmmExpr * Parser::parse_unary_expr ()
{

      CmmExpr * result = NULL;
      if (testSymbols (set_6))
      {
         result = parse_postfix_expr ();
      }
      else if (isSymbol (INC))
      {
         result = parse_inc_expr ();
      }
      else if (isSymbol (DEC))
      {
         result = parse_dec_expr ();
      }
      else if (isSymbol (STAR))
      {
         result = parse_deref_expr ();
      }
      else if (isSymbol (BIT_AND))
      {
         result = parse_addr_expr ();
      }
      else if (isSymbol (PLUS))
      {
         result = parse_plus_expr ();
      }
      else if (isSymbol (MINUS))
      {
         result = parse_minus_expr ();
      }
      else if (isSymbol (BIT_NOT))
      {
         result = parse_bit_not_expr ();
      }
      else if (isSymbol (LOG_NOT))
      {
         result = parse_log_not_expr ();
      }
      else if (isSymbol (keyword_sizeof))
      {
         result = parse_sizeof_expr ();
      }
      else if (isSymbol (keyword_new))
      {
         result = parse_allocation_expr ();
      }
      else if (isSymbol (keyword_delete))
      {
         result = parse_deallocation_expr ();
      }
      else if (isSymbol (keyword_throw))
      {
         result = parse_throw_expr ();
      }
      else {
         stop ("Unexpected token");
      }
      return result;
}

CmmIncExpr * Parser::parse_inc_expr ()
{

      CmmIncExpr * result = new CmmIncExpr;
      result->kind = incExpr;
      storeLocation (result);
      checkSymbol (INC);
      result->param = parse_cast_expr ();
      on_inc_expr (result);
      return result;
}

CmmDecExpr * Parser::parse_dec_expr ()
{

      CmmDecExpr * result = new CmmDecExpr;
      result->kind = decExpr;
      storeLocation (result);
      checkSymbol (DEC);
      result->param = parse_cast_expr ();
      on_dec_expr (result);
      return result;
}

CmmDerefExpr * Parser::parse_deref_expr ()
{

      CmmDerefExpr * result = new CmmDerefExpr;
      result->kind = derefExpr;
      storeLocation (result);
      checkSymbol (STAR);
      result->param = parse_cast_expr ();
      on_deref_expr (result);
      return result;
}

CmmAddrExpr * Parser::parse_addr_expr ()
{

      CmmAddrExpr * result = new CmmAddrExpr;
      result->kind = addrExpr;
      storeLocation (result);
      checkSymbol (BIT_AND);
      result->param = parse_cast_expr ();
      on_addr_expr (result);
      return result;
}

CmmPlusExpr * Parser::parse_plus_expr ()
{

      CmmPlusExpr * result = new CmmPlusExpr;
      result->kind = plusExpr;
      storeLocation (result);
      checkSymbol (PLUS);
      result->param = parse_cast_expr ();
      on_plus_expr (result);
      return result;
}

CmmMinusExpr * Parser::parse_minus_expr ()
{

      CmmMinusExpr * result = new CmmMinusExpr;
      result->kind = minusExpr;
      storeLocation (result);
      checkSymbol (MINUS);
      result->param = parse_cast_expr ();
      on_minus_expr (result);
      return result;
}

CmmBitNotExpr * Parser::parse_bit_not_expr ()
{

      CmmBitNotExpr * result = new CmmBitNotExpr;
      result->kind = bitNotExpr;
      storeLocation (result);
      checkSymbol (BIT_NOT);
      on_middle_bit_not_expr (result);
      result->param = parse_cast_expr ();
      on_bit_not_expr (result);
      return result;
}

CmmLogNotExpr * Parser::parse_log_not_expr ()
{

      CmmLogNotExpr * result = new CmmLogNotExpr;
      result->kind = logNotExpr;
      storeLocation (result);
      checkSymbol (LOG_NOT);
      result->param = parse_cast_expr ();
      on_log_not_expr (result);
      return result;
}

CmmSizeofExpr * Parser::parse_sizeof_expr ()
{

      CmmSizeofExpr * result = new CmmSizeofExpr;
      result->kind = sizeofExpr;
      storeLocation (result);
      checkSymbol (keyword_sizeof);
      result->value = parse_unary_expr ();
      on_sizeof_expr (result);
      return result;
}

CmmNewExpr * Parser::parse_allocation_expr ()
{

      CmmNewExpr * result = new CmmNewExpr;
      result->kind = newExpr;
      storeLocation (result);
      checkSymbol (keyword_new);
      if (testSymbols (set_7))
      {
         result->type1 = parse_new_type_id ();
      }
      else if (isSymbol (LPAREN))
      {
         checkSymbol (LPAREN);
         result->type2 = parse_type_id ();
         checkSymbol (RPAREN);
      }
      else {
         stop ("Unexpected token");
      }
      if (isSymbol (LPAREN))
      {
         checkSymbol (LPAREN);
         result->init_list = parse_expr_list ();
         checkSymbol (RPAREN);
      }
      on_allocation_expr (result);
      return result;
}

CmmNewTypeId * Parser::parse_new_type_id ()
{

      CmmNewTypeId * result = new CmmNewTypeId;
      storeLocation (result);
      result->type_spec = parse_type_specifiers ();
      result->ptr = parse_ptr_specifier_list ();
      while (isSymbol (LBRACKET))
      {
         result->items.push_back (parse_allocation_array_limit ());
      }
      return result;
}

CmmNewArrayLimit * Parser::parse_allocation_array_limit ()
{

      CmmNewArrayLimit * result = new CmmNewArrayLimit;
      storeLocation (result);
      checkSymbol (LBRACKET);
      result->value = parse_expr ();
      checkSymbol (RBRACKET);
      return result;
}

CmmDeleteExpr * Parser::parse_deallocation_expr ()
{

      CmmDeleteExpr * result = new CmmDeleteExpr;
      result->kind = deleteExpr;
      storeLocation (result);
      checkSymbol (keyword_delete);
      if (isSymbol (LBRACKET))
      {
         checkSymbol (LBRACKET);
         checkSymbol (RBRACKET);
         result->a_array = true;
      }
      result->param = parse_cast_expr ();
      on_deallocation_expr (result);
      return result;
}

CmmExpr * Parser::parse_cast_expr ()
{

      CmmExpr * result = NULL;
      result = parse_unary_expr ();
      if (is_cast_expression (result))
      {
         if (testSymbols (set_5))
         {
            CmmExpr * store = result;
            CmmCastExpr * result0 = new CmmCastExpr;
            storeLocation (result0);
            result0->left = store;
            result = result0;
            result0->kind = castExpr;
            result0->right = parse_cast_expr ();
         }
      }
      return result;
}

CmmExpr * Parser::parse_pm_expr ()
{

      CmmExpr * result = NULL;
      result = parse_cast_expr ();
      if (is_binary_expression (result))
      {
         while (isSymbol (DOT_STAR) || isSymbol (ARROW_STAR))
         {
            CmmExpr * store = result;
            CmmPtrMemExpr * result0 = new CmmPtrMemExpr;
            storeLocation (result0);
            result0->left = store;
            result = result0;
            if (isSymbol (DOT_STAR))
            {
               checkSymbol (DOT_STAR);
               result0->kind = dotMemberExpr;
            }
            else if (isSymbol (ARROW_STAR))
            {
               checkSymbol (ARROW_STAR);
               result0->kind = arrowMemberExpr;
            }
            else {
               stop ("Unexpected token");
            }
            result0->right = parse_cast_expr ();
            on_binary_expr (result);
         }
      }
      return result;
}

CmmExpr * Parser::parse_multiplicative_expr ()
{

      CmmExpr * result = NULL;
      result = parse_pm_expr ();
      if (is_binary_expression (result))
      {
         while (isSymbol (STAR) || isSymbol (SLASH) || isSymbol (MOD) || isSymbol (identifier) && is_mul (result))
         {
            CmmExpr * store = result;
            CmmMulExpr * result0 = new CmmMulExpr;
            storeLocation (result0);
            result0->left = store;
            result = result0;
            if (isSymbol (STAR))
            {
               checkSymbol (STAR);
               result0->kind = mulExpr;
            }
            else if (isSymbol (SLASH))
            {
               checkSymbol (SLASH);
               result0->kind = divExpr;
            }
            else if (isSymbol (MOD))
            {
               checkSymbol (MOD);
               result0->kind = modExpr;
            }
            else if (isSymbol (identifier) && is_mul (result0))
            {
               result0->kind = customMulExpr;
               result0->custom_mul = readIdent ();
            }
            else {
               stop ("Unexpected token");
            }
            result0->right = parse_pm_expr ();
            on_binary_expr (result);
         }
      }
      return result;
}

CmmExpr * Parser::parse_additive_expr ()
{

      CmmExpr * result = NULL;
      result = parse_multiplicative_expr ();
      if (is_binary_expression (result))
      {
         while (isSymbol (PLUS) || isSymbol (MINUS) || isSymbol (identifier) && is_add (result))
         {
            CmmExpr * store = result;
            CmmAddExpr * result0 = new CmmAddExpr;
            storeLocation (result0);
            result0->left = store;
            result = result0;
            if (isSymbol (PLUS))
            {
               checkSymbol (PLUS);
               result0->kind = addExpr;
            }
            else if (isSymbol (MINUS))
            {
               checkSymbol (MINUS);
               result0->kind = subExpr;
            }
            else if (isSymbol (identifier) && is_add (result0))
            {
               result0->kind = customAddExpr;
               result0->custom_add = readIdent ();
            }
            else {
               stop ("Unexpected token");
            }
            result0->right = parse_multiplicative_expr ();
            on_binary_expr (result);
         }
      }
      return result;
}

CmmExpr * Parser::parse_shift_expr ()
{

      CmmExpr * result = NULL;
      result = parse_additive_expr ();
      if (is_binary_expression (result))
      {
         while (isSymbol (SHL) || isSymbol (SHR))
         {
            CmmExpr * store = result;
            CmmShiftExpr * result0 = new CmmShiftExpr;
            storeLocation (result0);
            result0->left = store;
            result = result0;
            if (isSymbol (SHL))
            {
               checkSymbol (SHL);
               result0->kind = shlExpr;
            }
            else if (isSymbol (SHR))
            {
               checkSymbol (SHR);
               result0->kind = shrExpr;
            }
            else {
               stop ("Unexpected token");
            }
            result0->right = parse_additive_expr ();
            on_binary_expr (result);
         }
      }
      return result;
}

CmmExpr * Parser::parse_relational_expr ()
{

      CmmExpr * result = NULL;
      result = parse_shift_expr ();
      if (is_binary_expression (result))
      {
         while (isSymbol (LESS) || isSymbol (GREATER) || isSymbol (LESS_OR_EQUAL) || isSymbol (GREATER_OR_EQUAL))
         {
            CmmExpr * store = result;
            CmmRelExpr * result0 = new CmmRelExpr;
            storeLocation (result0);
            result0->left = store;
            result = result0;
            if (isSymbol (LESS))
            {
               checkSymbol (LESS);
               result0->kind = ltExpr;
            }
            else if (isSymbol (GREATER))
            {
               checkSymbol (GREATER);
               result0->kind = gtExpr;
            }
            else if (isSymbol (LESS_OR_EQUAL))
            {
               checkSymbol (LESS_OR_EQUAL);
               result0->kind = leExpr;
            }
            else if (isSymbol (GREATER_OR_EQUAL))
            {
               checkSymbol (GREATER_OR_EQUAL);
               result0->kind = geExpr;
            }
            else {
               stop ("Unexpected token");
            }
            result0->right = parse_shift_expr ();
            on_binary_expr (result);
         }
      }
      return result;
}

CmmExpr * Parser::parse_equality_expr ()
{

      CmmExpr * result = NULL;
      result = parse_relational_expr ();
      if (is_binary_expression (result))
      {
         while (isSymbol (EQUAL) || isSymbol (UNEQUAL))
         {
            CmmExpr * store = result;
            CmmEqExpr * result0 = new CmmEqExpr;
            storeLocation (result0);
            result0->left = store;
            result = result0;
            if (isSymbol (EQUAL))
            {
               checkSymbol (EQUAL);
               result0->kind = eqExpr;
            }
            else if (isSymbol (UNEQUAL))
            {
               checkSymbol (UNEQUAL);
               result0->kind = neExpr;
            }
            else {
               stop ("Unexpected token");
            }
            result0->right = parse_relational_expr ();
            on_binary_expr (result);
         }
      }
      return result;
}

CmmExpr * Parser::parse_and_expr ()
{

      CmmExpr * result = NULL;
      result = parse_equality_expr ();
      if (is_binary_expression (result))
      {
         while (isSymbol (BIT_AND))
         {
            CmmExpr * store = result;
            CmmAndExpr * result0 = new CmmAndExpr;
            storeLocation (result0);
            result0->left = store;
            result = result0;
            checkSymbol (BIT_AND);
            result0->kind = bitAndExpr;
            result0->right = parse_equality_expr ();
            on_binary_expr (result);
         }
      }
      return result;
}

CmmExpr * Parser::parse_exclusive_or_expr ()
{

      CmmExpr * result = NULL;
      result = parse_and_expr ();
      if (is_binary_expression (result))
      {
         while (isSymbol (BIT_XOR))
         {
            CmmExpr * store = result;
            CmmXorExpr * result0 = new CmmXorExpr;
            storeLocation (result0);
            result0->left = store;
            result = result0;
            checkSymbol (BIT_XOR);
            result0->kind = bitXorExpr;
            result0->right = parse_and_expr ();
            on_binary_expr (result);
         }
      }
      return result;
}

CmmExpr * Parser::parse_inclusive_or_expr ()
{

      CmmExpr * result = NULL;
      result = parse_exclusive_or_expr ();
      if (is_binary_expression (result))
      {
         while (isSymbol (BIT_OR))
         {
            CmmExpr * store = result;
            CmmOrExpr * result0 = new CmmOrExpr;
            storeLocation (result0);
            result0->left = store;
            result = result0;
            checkSymbol (BIT_OR);
            result0->kind = bitOrExpr;
            result0->right = parse_exclusive_or_expr ();
            on_binary_expr (result);
         }
      }
      return result;
}

CmmExpr * Parser::parse_logical_and_expr ()
{

      CmmExpr * result = NULL;
      result = parse_inclusive_or_expr ();
      if (is_binary_expression (result))
      {
         while (isSymbol (LOG_AND))
         {
            CmmExpr * store = result;
            CmmAndAndExpr * result0 = new CmmAndAndExpr;
            storeLocation (result0);
            result0->left = store;
            result = result0;
            checkSymbol (LOG_AND);
            result0->kind = logAndExpr;
            result0->right = parse_inclusive_or_expr ();
            on_binary_expr (result);
         }
      }
      return result;
}

CmmExpr * Parser::parse_logical_or_expr ()
{

      CmmExpr * result = NULL;
      result = parse_logical_and_expr ();
      if (is_binary_expression (result))
      {
         while (isSymbol (LOG_OR))
         {
            CmmExpr * store = result;
            CmmOrOrExpr * result0 = new CmmOrOrExpr;
            storeLocation (result0);
            result0->left = store;
            result = result0;
            checkSymbol (LOG_OR);
            result0->kind = logOrExpr;
            result0->right = parse_logical_and_expr ();
            on_binary_expr (result);
         }
      }
      return result;
}

CmmExpr * Parser::parse_assignment_expr ()
{

      CmmExpr * result = NULL;
      result = parse_logical_or_expr ();
      if (is_binary_expression (result))
      {
         if (isSymbol (ASSIGN) || isSymbol (PLUS_ASSIGN) || isSymbol (MINUS_ASSIGN) || isSymbol (MUL_ASSIGN) || isSymbol (DIV_ASSIGN) || isSymbol (MOD_ASSIGN) || isSymbol (SHL_ASSIGN) || isSymbol (SHR_ASSIGN) || isSymbol (BIT_AND_ASSIGN) || isSymbol (BIT_XOR_ASSIGN) || isSymbol (BIT_OR_ASSIGN) || isSymbol (QUESTION))
         {
            CmmExpr * store = result;
            CmmAssignExpr * result0 = new CmmAssignExpr;
            storeLocation (result0);
            result0->left = store;
            result = result0;
            if (isSymbol (ASSIGN))
            {
               checkSymbol (ASSIGN);
               result0->kind = assignExpr;
            }
            else if (isSymbol (PLUS_ASSIGN))
            {
               checkSymbol (PLUS_ASSIGN);
               result0->kind = addAssignExpr;
            }
            else if (isSymbol (MINUS_ASSIGN))
            {
               checkSymbol (MINUS_ASSIGN);
               result0->kind = subAssignExpr;
            }
            else if (isSymbol (MUL_ASSIGN))
            {
               checkSymbol (MUL_ASSIGN);
               result0->kind = mulAssignExpr;
            }
            else if (isSymbol (DIV_ASSIGN))
            {
               checkSymbol (DIV_ASSIGN);
               result0->kind = divAssignExpr;
            }
            else if (isSymbol (MOD_ASSIGN))
            {
               checkSymbol (MOD_ASSIGN);
               result0->kind = modAssignExpr;
            }
            else if (isSymbol (SHL_ASSIGN))
            {
               checkSymbol (SHL_ASSIGN);
               result0->kind = shlAssignExpr;
            }
            else if (isSymbol (SHR_ASSIGN))
            {
               checkSymbol (SHR_ASSIGN);
               result0->kind = shrAssignExpr;
            }
            else if (isSymbol (BIT_AND_ASSIGN))
            {
               checkSymbol (BIT_AND_ASSIGN);
               result0->kind = andAssignExpr;
            }
            else if (isSymbol (BIT_XOR_ASSIGN))
            {
               checkSymbol (BIT_XOR_ASSIGN);
               result0->kind = xorAssignExpr;
            }
            else if (isSymbol (BIT_OR_ASSIGN))
            {
               checkSymbol (BIT_OR_ASSIGN);
               result0->kind = orAssignExpr;
            }
            else if (isSymbol (QUESTION))
            {
               checkSymbol (QUESTION);
               result0->kind = condExpr;
               result0->middle = parse_assignment_expr ();
               checkSymbol (COLON);
            }
            else {
               stop ("Unexpected token");
            }
            result0->right = parse_logical_or_expr ();
            on_binary_expr (result);
         }
      }
      return result;
}

CmmExpr * Parser::parse_colon_expr ()
{

      CmmExpr * result = NULL;
      result = parse_assignment_expr ();
      return result;
}

CmmExpr * Parser::parse_comma_expr ()
{

      CmmExpr * result = NULL;
      result = parse_colon_expr ();
      if (is_binary_expression (result))
      {
         while (isSymbol (COMMA))
         {
            CmmExpr * store = result;
            CmmCommaExpr * result0 = new CmmCommaExpr;
            storeLocation (result0);
            result0->left = store;
            result = result0;
            checkSymbol (COMMA);
            result0->kind = commaExpr;
            result0->right = parse_colon_expr ();
            on_binary_expr (result);
         }
      }
      return result;
}

CmmExpr * Parser::parse_expr ()
{

      CmmExpr * result = NULL;
      result = parse_comma_expr ();
      on_expr (result);
      return result;
}

CmmExpr * Parser::parse_const_expr ()
{

      CmmExpr * result = NULL;
      result = parse_assignment_expr ();
      return result;
}

CmmStat * Parser::parse_stat ()
{

      CmmStat * result = NULL;
      if (testSymbols (set_5))
      {
         result = parse_flexible_stat ();
      }
      else if (isSymbol (SEMICOLON))
      {
         result = parse_empty_stat ();
      }
      else if (isSymbol (LBRACE))
      {
         result = parse_compound_stat ();
      }
      else if (isSymbol (keyword_if))
      {
         result = parse_if_stat ();
      }
      else if (isSymbol (keyword_while))
      {
         result = parse_while_stat ();
      }
      else if (isSymbol (keyword_do))
      {
         result = parse_do_stat ();
      }
      else if (isSymbol (keyword_for))
      {
         result = parse_for_stat ();
      }
      else if (isSymbol (keyword_switch))
      {
         result = parse_switch_stat ();
      }
      else if (isSymbol (keyword_case))
      {
         result = parse_case_stat ();
      }
      else if (isSymbol (keyword_default))
      {
         result = parse_default_stat ();
      }
      else if (isSymbol (keyword_break))
      {
         result = parse_break_stat ();
      }
      else if (isSymbol (keyword_continue))
      {
         result = parse_continue_stat ();
      }
      else if (isSymbol (keyword_return))
      {
         result = parse_return_stat ();
      }
      else if (isSymbol (keyword_goto))
      {
         result = parse_goto_stat ();
      }
      else if (isSymbol (keyword_try))
      {
         result = parse_try_stat ();
      }
      else {
         stop ("Unexpected token");
      }
      return result;
}

CmmStat * Parser::parse_nested_stat ()
{

      CmmStat * result = NULL;
      result = parse_stat ();
      return result;
}

CmmStat * Parser::parse_tail_stat ()
{

      CmmStat * result = NULL;
      result = parse_stat ();
      return result;
}

CmmEmptyStat * Parser::parse_empty_stat ()
{

      CmmEmptyStat * result = new CmmEmptyStat;
      result->kind = emptyStat;
      storeLocation (result);
      checkSymbol (SEMICOLON);
      return result;
}

CmmCompoundStat * Parser::parse_compound_stat ()
{

      CmmCompoundStat * result = new CmmCompoundStat;
      result->kind = compoundStat;
      storeLocation (result);
      checkSymbol (LBRACE);
      on_open_compound_statement (result);
      while (testSymbols (set_11))
      {
         on_declaration (result);
         result->items.push_back (parse_stat ());
      }
      on_close_compound_statement (result);
      checkSymbol (RBRACE);
      return result;
}

CmmIfStat * Parser::parse_if_stat ()
{

      CmmIfStat * result = new CmmIfStat;
      result->kind = ifStat;
      storeLocation (result);
      checkSymbol (keyword_if);
      checkSymbol (LPAREN);
      result->cond = parse_condition ();
      checkSymbol (RPAREN);
      on_open_if_statement (result);
      result->then_stat = parse_nested_stat ();
      if (isSymbol (keyword_else))
      {
         checkSymbol (keyword_else);
         result->else_stat = parse_tail_stat ();
      }
      on_close_if_statement (result);
      return result;
}

CmmWhileStat * Parser::parse_while_stat ()
{

      CmmWhileStat * result = new CmmWhileStat;
      result->kind = whileStat;
      storeLocation (result);
      checkSymbol (keyword_while);
      checkSymbol (LPAREN);
      result->cond = parse_condition ();
      checkSymbol (RPAREN);
      on_open_while_statement (result);
      result->body = parse_nested_stat ();
      on_close_while_statement (result);
      return result;
}

CmmDoStat * Parser::parse_do_stat ()
{

      CmmDoStat * result = new CmmDoStat;
      result->kind = doStat;
      storeLocation (result);
      checkSymbol (keyword_do);
      result->body = parse_nested_stat ();
      checkSymbol (keyword_while);
      checkSymbol (LPAREN);
      result->cond_expr = parse_expr ();
      checkSymbol (RPAREN);
      checkSymbol (SEMICOLON);
      return result;
}

CmmForStat * Parser::parse_for_stat ()
{

      CmmForStat * result = new CmmForStat;
      result->kind = forStat;
      storeLocation (result);
      checkSymbol (keyword_for);
      checkSymbol (LPAREN);
      if (testSymbols (set_5))
      {
         result->from_expr = parse_condition ();
      }
      if (isSymbol (COLON))
      {
         checkSymbol (COLON);
         result->iter_expr = parse_expr ();
      }
      else if (isSymbol (SEMICOLON))
      {
         checkSymbol (SEMICOLON);
         if (testSymbols (set_5))
         {
            result->cond_expr = parse_expr ();
         }
         checkSymbol (SEMICOLON);
         if (testSymbols (set_5))
         {
            result->step_expr = parse_expr ();
         }
      }
      else {
         stop ("Unexpected token");
      }
      checkSymbol (RPAREN);
      on_open_for_statement (result);
      result->body = parse_nested_stat ();
      on_close_for_statement (result);
      return result;
}

CmmSwitchStat * Parser::parse_switch_stat ()
{

      CmmSwitchStat * result = new CmmSwitchStat;
      result->kind = switchStat;
      storeLocation (result);
      checkSymbol (keyword_switch);
      checkSymbol (LPAREN);
      result->cond = parse_condition ();
      checkSymbol (RPAREN);
      on_open_switch_statement (result);
      result->body = parse_nested_stat ();
      on_close_switch_statement (result);
      return result;
}

CmmCaseStat * Parser::parse_case_stat ()
{

      CmmCaseStat * result = new CmmCaseStat;
      result->kind = caseStat;
      storeLocation (result);
      checkSymbol (keyword_case);
      result->case_expr = parse_expr ();
      checkSymbol (COLON);
      result->body = parse_nested_stat ();
      return result;
}

CmmDefaultStat * Parser::parse_default_stat ()
{

      CmmDefaultStat * result = new CmmDefaultStat;
      result->kind = defaultStat;
      storeLocation (result);
      checkSymbol (keyword_default);
      checkSymbol (COLON);
      result->body = parse_nested_stat ();
      return result;
}

CmmBreakStat * Parser::parse_break_stat ()
{

      CmmBreakStat * result = new CmmBreakStat;
      result->kind = breakStat;
      storeLocation (result);
      checkSymbol (keyword_break);
      checkSymbol (SEMICOLON);
      return result;
}

CmmContinueStat * Parser::parse_continue_stat ()
{

      CmmContinueStat * result = new CmmContinueStat;
      result->kind = continueStat;
      storeLocation (result);
      checkSymbol (keyword_continue);
      checkSymbol (SEMICOLON);
      return result;
}

CmmReturnStat * Parser::parse_return_stat ()
{

      CmmReturnStat * result = new CmmReturnStat;
      result->kind = returnStat;
      storeLocation (result);
      checkSymbol (keyword_return);
      if (testSymbols (set_5))
      {
         result->return_expr = parse_expr ();
      }
      checkSymbol (SEMICOLON);
      return result;
}

CmmGotoStat * Parser::parse_goto_stat ()
{

      CmmGotoStat * result = new CmmGotoStat;
      result->kind = gotoStat;
      storeLocation (result);
      checkSymbol (keyword_goto);
      result->goto_lab = readIdent ();
      checkSymbol (SEMICOLON);
      return result;
}

CmmStat * Parser::parse_flexible_stat ()
{

      CmmStat * result = NULL;
      on_open_flexible_stat ();
      CmmExpr * result0 = parse_expr ();
      if ((isSymbol (SEMICOLON) || isSymbol (LBRACE)) && is_expression (result0))
      {
         result = parse_simple_stat (result0);
      }
      else if (isSymbol (LPAREN) && is_constructor (result0))
      {
         result = parse_constructor_declaration (result0);
      }
      else if (testSymbols (set_12))
      {
         result = parse_simple_declaration (result0);
      }
      else {
         stop ("Unexpected token");
      }
      return result;
}

CmmSimpleStat * Parser::parse_simple_stat (CmmExpr * store)
{

      CmmSimpleStat * result = new CmmSimpleStat;
      result->kind = simpleStat;
      storeLocation (result);
      result->inner_expr = store;
      on_open_simple_stat (result);
      if (isSymbol (LBRACE))
      {
         on_open_expr_block (result);
         result->body = parse_compound_stat ();
         on_close_expr_block (result);
      }
      else if (isSymbol (SEMICOLON))
      {
         checkSymbol (SEMICOLON);
         on_simple_statement (result);
      }
      else {
         stop ("Unexpected token");
      }
      return result;
}

CmmDeclSpec * Parser::parse_decl_specifier ()
{

      CmmDeclSpec * result = new CmmDeclSpec;
      result->kind = declSpec;
      storeLocation (result);
      if (isSymbol (keyword_inline))
      {
         checkSymbol (keyword_inline);
         result->a_inline = true;
      }
      else if (isSymbol (keyword_virtual))
      {
         checkSymbol (keyword_virtual);
         result->a_virtual = true;
      }
      else if (isSymbol (keyword_explicit))
      {
         checkSymbol (keyword_explicit);
         result->a_explicit = true;
      }
      else if (isSymbol (keyword_mutable))
      {
         checkSymbol (keyword_mutable);
         result->a_mutable = true;
      }
      else if (isSymbol (keyword_static))
      {
         checkSymbol (keyword_static);
         result->a_static = true;
      }
      else if (isSymbol (keyword_register))
      {
         checkSymbol (keyword_register);
         result->a_register = true;
      }
      else {
         stop ("Unexpected token");
      }
      if (isSymbol (BIT_NOT))
      {
         checkSymbol (BIT_NOT);
         result->a_destructor = true;
         on_middle_decl_specifier (result);
      }
      result->param = parse_type_specifiers ();
      on_decl_specifier (result);
      return result;
}

CmmConstSpecifier * Parser::parse_const_specifier ()
{

      CmmConstSpecifier * result = new CmmConstSpecifier;
      result->kind = constSpec;
      storeLocation (result);
      checkSymbol (keyword_const);
      result->param = parse_type_specifiers ();
      on_const_specifier (result);
      return result;
}

CmmVolatileSpecifier * Parser::parse_volatile_specifier ()
{

      CmmVolatileSpecifier * result = new CmmVolatileSpecifier;
      result->kind = volatileSpec;
      storeLocation (result);
      checkSymbol (keyword_volatile);
      result->param = parse_type_specifiers ();
      on_volatile_specifier (result);
      return result;
}

CmmTypeSpec * Parser::parse_type_specifier ()
{

      CmmTypeSpec * result = new CmmTypeSpec;
      result->kind = typeSpec;
      storeLocation (result);
      if (isSymbol (keyword_signed) || isSymbol (keyword_unsigned))
      {
         if (isSymbol (keyword_signed))
         {
            checkSymbol (keyword_signed);
            result->a_signed = true;
         }
         else if (isSymbol (keyword_unsigned))
         {
            checkSymbol (keyword_unsigned);
            result->a_unsigned = true;
         }
         else {
            stop ("Unexpected token");
         }
      }
      if (isSymbol (keyword_short))
      {
         checkSymbol (keyword_short);
         result->a_short = true;
      }
      else if (isSymbol (keyword_long))
      {
         checkSymbol (keyword_long);
         result->a_long = true;
         if (isSymbol (keyword_long) || isSymbol (keyword_double))
         {
            if (isSymbol (keyword_long))
            {
               checkSymbol (keyword_long);
               result->a_long_long = true;
            }
            else if (isSymbol (keyword_double))
            {
               checkSymbol (keyword_double);
               result->a_long_double = true;
            }
            else {
               stop ("Unexpected token");
            }
         }
      }
      else if (isSymbol (keyword_bool))
      {
         checkSymbol (keyword_bool);
         result->a_bool = true;
      }
      else if (isSymbol (keyword_char))
      {
         checkSymbol (keyword_char);
         result->a_char = true;
      }
      else if (isSymbol (keyword_wchar_t))
      {
         checkSymbol (keyword_wchar_t);
         result->a_wchar = true;
      }
      else if (isSymbol (keyword_int))
      {
         checkSymbol (keyword_int);
         result->a_int = true;
      }
      else if (isSymbol (keyword_float))
      {
         checkSymbol (keyword_float);
         result->a_float = true;
      }
      else if (isSymbol (keyword_double))
      {
         checkSymbol (keyword_double);
         result->a_double = true;
      }
      else if (isSymbol (keyword_void))
      {
         checkSymbol (keyword_void);
         result->a_void = true;
      }
      else {
         stop ("Unexpected token");
      }
      on_type_specifier (result);
      return result;
}

CmmTypeName * Parser::parse_type_name ()
{

      CmmTypeName * result = new CmmTypeName;
      result->kind = typeName;
      storeLocation (result);
      checkSymbol (keyword_typename);
      result->qual_name = parse_qualified_name ();
      on_type_name (result);
      return result;
}

CmmExpr * Parser::parse_type_specifiers ()
{

      CmmExpr * result = NULL;
      if (isSymbol (identifier) || isSymbol (SCOPE) || isSymbol (keyword_operator))
      {
         result = parse_ident_expr ();
      }
      else if (isSymbol (keyword_typename))
      {
         result = parse_type_name ();
      }
      else if (testSymbols (set_2))
      {
         result = parse_type_specifier ();
      }
      else if (isSymbol (keyword_const))
      {
         result = parse_const_specifier ();
      }
      else if (isSymbol (keyword_volatile))
      {
         result = parse_volatile_specifier ();
      }
      else if (testSymbols (set_3))
      {
         result = parse_decl_specifier ();
      }
      else {
         stop ("Unexpected token");
      }
      return result;
}

CmmPointerDeclarator * Parser::parse_pointer_declarator ()
{

      CmmPointerDeclarator * result = new CmmPointerDeclarator;
      result->kind = pointerDeclarator;
      storeLocation (result);
      checkSymbol (STAR);
      result->cv_spec = parse_cv_specifier_list ();
      result->inner_declarator = parse_declarator ();
      return result;
}

CmmReferenceDeclator * Parser::parse_reference_declarator ()
{

      CmmReferenceDeclator * result = new CmmReferenceDeclator;
      result->kind = referenceDeclarator;
      storeLocation (result);
      checkSymbol (BIT_AND);
      result->cv_spec = parse_cv_specifier_list ();
      result->inner_declarator = parse_declarator ();
      return result;
}

CmmCvSpecifier * Parser::parse_cv_specifier_list ()
{

      CmmCvSpecifier * result = new CmmCvSpecifier;
      storeLocation (result);
      while (isSymbol (keyword_const) || isSymbol (keyword_volatile))
      {
         if (isSymbol (keyword_const))
         {
            checkSymbol (keyword_const);
            result->cv_const = true;
         }
         else if (isSymbol (keyword_volatile))
         {
            checkSymbol (keyword_volatile);
            result->cv_volatile = true;
         }
         else {
            stop ("Unexpected token");
         }
      }
      return result;
}

CmmBasicDeclarator * Parser::parse_basic_declarator ()
{

      CmmBasicDeclarator * result = new CmmBasicDeclarator;
      result->kind = basicDeclarator;
      storeLocation (result);
      result->qual_name = parse_new_qualified_name ();
      return result;
}

CmmEmptyDeclarator * Parser::parse_empty_declarator ()
{

      CmmEmptyDeclarator * result = new CmmEmptyDeclarator;
      result->kind = emptyDeclarator;
      storeLocation (result);
      return result;
}

CmmNestedDeclarator * Parser::parse_nested_declarator ()
{

      CmmNestedDeclarator * result = new CmmNestedDeclarator;
      result->kind = nestedDeclarator;
      storeLocation (result);
      checkSymbol (LPAREN);
      result->inner_declarator = parse_declarator ();
      checkSymbol (RPAREN);
      return result;
}

CmmArrayDeclarator * Parser::parse_array_declarator (CmmDeclarator * store)
{

      CmmArrayDeclarator * result = new CmmArrayDeclarator;
      result->kind = arrayDeclarator;
      storeLocation (result);
      result->inner_declarator = store;
      checkSymbol (LBRACKET);
      if (testSymbols (set_5))
      {
         result->lim = parse_expr ();
      }
      checkSymbol (RBRACKET);
      return result;
}

CmmFunctionDeclarator * Parser::parse_function_declarator (CmmDeclarator * store)
{

      CmmFunctionDeclarator * result = new CmmFunctionDeclarator;
      result->kind = functionDeclarator;
      storeLocation (result);
      result->inner_declarator = store;
      checkSymbol (LPAREN);
      result->parameters = parse_parameter_declaration_list ();
      checkSymbol (RPAREN);
      if (isSymbol (keyword_const))
      {
         checkSymbol (keyword_const);
         result->a_const = true;
      }
      if (isSymbol (keyword_override))
      {
         checkSymbol (keyword_override);
         result->a_override = true;
      }
      if (isSymbol (keyword_throw))
      {
         result->exception_spec = parse_exception_specification ();
      }
      return result;
}

CmmDeclarator * Parser::parse_entry_declarator ()
{

      CmmDeclarator * result = NULL;
      if (isSymbol (identifier) || isSymbol (SCOPE) || isSymbol (keyword_operator))
      {
         result = parse_basic_declarator ();
      }
      else if (isSymbol (LPAREN))
      {
         result = parse_nested_declarator ();
      }
      else
      {
         result = parse_empty_declarator ();
      }
      return result;
}

CmmDeclarator * Parser::parse_continue_declarator ()
{

      CmmDeclarator * result = NULL;
      result = parse_entry_declarator ();
      while (isSymbol (LBRACKET) || isSymbol (LPAREN))
      {
         if (isSymbol (LBRACKET))
         {
            result = parse_array_declarator (result);
         }
         else if (isSymbol (LPAREN))
         {
            result = parse_function_declarator (result);
         }
         else {
            stop ("Unexpected token");
         }
      }
      return result;
}

CmmDeclarator * Parser::parse_declarator ()
{

      CmmDeclarator * result = NULL;
      if (isSymbol (STAR))
      {
         result = parse_pointer_declarator ();
      }
      else if (isSymbol (BIT_AND))
      {
         result = parse_reference_declarator ();
      }
      else if (testSymbols (set_13))
      {
         result = parse_continue_declarator ();
      }
      else {
         stop ("Unexpected token");
      }
      return result;
}

CmmDeclarator * Parser::parse_simple_declarator ()
{

      CmmDeclarator * result = NULL;
      result = parse_declarator ();
      on_simple_declarator (result);
      return result;
}

CmmDeclarator * Parser::parse_common_declarator ()
{

      CmmDeclarator * result = NULL;
      result = parse_declarator ();
      return result;
}

CmmDeclarator * Parser::parse_constructor_declarator ()
{

      CmmDeclarator * result = NULL;
      CmmEmptyDeclarator * result0 = parse_empty_declarator ();
      result = parse_function_declarator (result0);
      return result;
}

CmmPtrSpecifierSect * Parser::parse_ptr_specifier_list ()
{

      CmmPtrSpecifierSect * result = new CmmPtrSpecifierSect;
      storeLocation (result);
      return result;
}

CmmStatSect * Parser::parse_parameter_declaration_list ()
{

      CmmStatSect * result = new CmmStatSect;
      storeLocation (result);
      if (testSymbols (set_14))
      {
         result->items.push_back (parse_parameter_declaration ());
         while (isSymbol (COMMA))
         {
            checkSymbol (COMMA);
            result->items.push_back (parse_parameter_declaration ());
         }
      }
      return result;
}

CmmStat * Parser::parse_parameter_declaration ()
{

      CmmStat * result = NULL;
      if (testSymbols (set_5))
      {
         CmmExpr * result0 = parse_assignment_expr ();
         if (is_value_parameter (result0))
         {
            result = parse_value_parameter (result0);
         }
         else if (testSymbols (set_15))
         {
            result = parse_plain_parameter (result0);
         }
         else {
            stop ("Unexpected token");
         }
      }
      else if (isSymbol (DOTS))
      {
         result = parse_dots_parameter ();
      }
      else {
         stop ("Unexpected token");
      }
      return result;
}

CmmSimpleStat * Parser::parse_value_parameter (CmmExpr * store)
{

      CmmSimpleStat * result = new CmmSimpleStat;
      result->kind = simpleStat;
      storeLocation (result);
      result->inner_expr = store;
      return result;
}

CmmSimpleDecl * Parser::parse_plain_parameter (CmmExpr * store)
{

      CmmSimpleDecl * result = new CmmSimpleDecl;
      result->kind = simpleDecl;
      storeLocation (result);
      result->type_spec = store;
      result->items.push_back (parse_parameter_item ());
      return result;
}

CmmSimpleItem * Parser::parse_parameter_item ()
{

      CmmSimpleItem * result = new CmmSimpleItem;
      result->kind = simpleItem;
      storeLocation (result);
      result->declarator = parse_common_declarator ();
      if (isSymbol (ASSIGN))
      {
         result->init = parse_initializer ();
      }
      result->attr = parse_attr_list ();
      return result;
}

CmmDotsParam * Parser::parse_dots_parameter ()
{

      CmmDotsParam * result = new CmmDotsParam;
      result->kind = dotsParam;
      storeLocation (result);
      checkSymbol (DOTS);
      return result;
}

CmmTypeId * Parser::parse_type_id ()
{

      CmmTypeId * result = new CmmTypeId;
      storeLocation (result);
      result->type_spec = parse_type_specifiers ();
      result->declarator = parse_common_declarator ();
      return result;
}

CmmInitializer * Parser::parse_initializer ()
{

      CmmInitializer * result = new CmmInitializer;
      storeLocation (result);
      checkSymbol (ASSIGN);
      result->value = parse_initializer_item ();
      return result;
}

CmmInitItem * Parser::parse_initializer_item ()
{

      CmmInitItem * result = NULL;
      if (testSymbols (set_5))
      {
         result = parse_simple_initializer ();
      }
      else if (isSymbol (LBRACE))
      {
         result = parse_initializer_list ();
      }
      else {
         stop ("Unexpected token");
      }
      return result;
}

CmmInitSimple * Parser::parse_simple_initializer ()
{

      CmmInitSimple * result = new CmmInitSimple;
      storeLocation (result);
      result->inner_expr = parse_assignment_expr ();
      return result;
}

CmmInitList * Parser::parse_initializer_list ()
{

      CmmInitList * result = new CmmInitList;
      storeLocation (result);
      checkSymbol (LBRACE);
      if (testSymbols (set_16))
      {
         result->items.push_back (parse_initializer_item ());
         while (isSymbol (COMMA))
         {
            checkSymbol (COMMA);
            result->items.push_back (parse_initializer_item ());
         }
      }
      checkSymbol (RBRACE);
      return result;
}

CmmAttr * Parser::parse_attr_item ()
{

      CmmAttr * result = new CmmAttr;
      storeLocation (result);
      result->attr_expr = parse_assignment_expr ();
      return result;
}

CmmAttrGroup * Parser::parse_attr_group ()
{

      CmmAttrGroup * result = new CmmAttrGroup;
      storeLocation (result);
      checkSymbol (literal_1);
      result->items.push_back (parse_attr_item ());
      while (isSymbol (COMMA))
      {
         checkSymbol (COMMA);
         result->items.push_back (parse_attr_item ());
      }
      checkSymbol (literal_2);
      return result;
}

CmmAttrSect * Parser::parse_attr_list ()
{

      CmmAttrSect * result = new CmmAttrSect;
      storeLocation (result);
      while (isSymbol (literal_1))
      {
         result->items.push_back (parse_attr_group ());
      }
      return result;
}

CmmSimpleDecl * Parser::parse_simple_declaration (CmmExpr * store)
{

      CmmSimpleDecl * result = new CmmSimpleDecl;
      result->kind = simpleDecl;
      storeLocation (result);
      result->type_spec = store;
      on_open_simple_declaration (result);
      result->items.push_back (parse_simple_item ());
      on_simple_item (result);
      while (isSymbol (COMMA))
      {
         checkSymbol (COMMA);
         result->items.push_back (parse_simple_item ());
         on_simple_item (result);
      }
      if (isSymbol (LBRACE))
      {
         on_open_function (result);
         result->body = parse_compound_stat ();
         on_close_function (result);
      }
      else if (isSymbol (SEMICOLON))
      {
         checkSymbol (SEMICOLON);
      }
      else {
         stop ("Unexpected token");
      }
      on_simple_declaration (result);
      return result;
}

CmmSimpleItem * Parser::parse_simple_item ()
{

      CmmSimpleItem * result = new CmmSimpleItem;
      result->kind = simpleItem;
      storeLocation (result);
      result->declarator = parse_simple_declarator ();
      if (isSymbol (ASSIGN))
      {
         result->init = parse_initializer ();
      }
      result->attr = parse_attr_list ();
      return result;
}

CmmSimpleDecl * Parser::parse_constructor_declaration (CmmExpr * store)
{

      CmmSimpleDecl * result = new CmmSimpleDecl;
      result->kind = simpleDecl;
      storeLocation (result);
      result->type_spec = store;
      on_open_constructor_declaration (result);
      result->items.push_back (parse_constructor_item ());
      on_simple_item (result);
      if (isSymbol (COLON) || isSymbol (LBRACE))
      {
         on_open_function (result);
         if (isSymbol (COLON))
         {
            checkSymbol (COLON);
            result->ctor_init = parse_ctor_initializer ();
         }
         result->body = parse_compound_stat ();
         on_close_function (result);
      }
      else if (isSymbol (SEMICOLON))
      {
         checkSymbol (SEMICOLON);
      }
      else {
         stop ("Unexpected token");
      }
      on_simple_declaration (result);
      return result;
}

CmmSimpleItem * Parser::parse_constructor_item ()
{

      CmmSimpleItem * result = new CmmSimpleItem;
      result->kind = simpleItem;
      storeLocation (result);
      result->declarator = parse_constructor_declarator ();
      result->attr = parse_attr_list ();
      return result;
}

CmmStat * Parser::parse_condition ()
{

      CmmStat * result = NULL;
      CmmExpr * result0 = parse_expr ();
      if (is_expression (result0))
      {
         result = parse_condition_value (result0);
      }
      else if (testSymbols (set_17))
      {
         result = parse_condition_declaration (result0);
      }
      else {
         stop ("Unexpected token");
      }
      return result;
}

CmmSimpleDecl * Parser::parse_condition_declaration (CmmExpr * store)
{

      CmmSimpleDecl * result = new CmmSimpleDecl;
      result->kind = simpleDecl;
      storeLocation (result);
      result->type_spec = store;
      result->items.push_back (parse_condition_item ());
      on_simple_item (result);
      while (isSymbol (COMMA))
      {
         checkSymbol (COMMA);
         result->items.push_back (parse_condition_item ());
         on_simple_item (result);
      }
      return result;
}

CmmSimpleItem * Parser::parse_condition_item ()
{

      CmmSimpleItem * result = new CmmSimpleItem;
      result->kind = simpleItem;
      storeLocation (result);
      result->declarator = parse_simple_declarator ();
      if (isSymbol (ASSIGN))
      {
         result->init = parse_initializer ();
      }
      result->attr = parse_attr_list ();
      return result;
}

CmmSimpleStat * Parser::parse_condition_value (CmmExpr * store)
{

      CmmSimpleStat * result = new CmmSimpleStat;
      result->kind = simpleStat;
      storeLocation (result);
      result->inner_expr = store;
      return result;
}

CmmStatSect * Parser::parse_declaration_list ()
{

      CmmStatSect * result = new CmmStatSect;
      storeLocation (result);
      while (testSymbols (set_18))
      {
         on_declaration (result);
         result->items.push_back (parse_declaration ());
      }
      return result;
}

CmmStat * Parser::parse_declaration ()
{

      CmmStat * result = NULL;
      if (testSymbols (set_5))
      {
         result = parse_flexible_stat ();
      }
      else if (isSymbol (SEMICOLON))
      {
         result = parse_empty_stat ();
      }
      else if (isSymbol (LBRACE))
      {
         result = parse_compound_stat ();
      }
      else if (isSymbol (keyword_if))
      {
         result = parse_if_stat ();
      }
      else if (isSymbol (keyword_while))
      {
         result = parse_while_stat ();
      }
      else if (isSymbol (keyword_do))
      {
         result = parse_do_stat ();
      }
      else if (isSymbol (keyword_for))
      {
         result = parse_for_stat ();
      }
      else if (isSymbol (keyword_switch))
      {
         result = parse_switch_stat ();
      }
      else if (isSymbol (keyword_class) || isSymbol (keyword_struct) || isSymbol (keyword_union))
      {
         result = parse_class_declaration ();
      }
      else if (isSymbol (keyword_enum))
      {
         result = parse_enum_declaration ();
      }
      else if (isSymbol (keyword_typedef))
      {
         result = parse_typedef_declaration ();
      }
      else if (isSymbol (keyword_friend))
      {
         result = parse_friend_declaration ();
      }
      else if (isSymbol (keyword_namespace))
      {
         result = parse_namespace_declaration ();
      }
      else if (isSymbol (keyword_using))
      {
         result = parse_using_declaration ();
      }
      else if (isSymbol (keyword_extern))
      {
         result = parse_extern_declaration ();
      }
      else if (isSymbol (keyword_template))
      {
         result = parse_template_declaration ();
      }
      else if (isSymbol (keyword_stencil))
      {
         result = parse_stencil_declaration ();
      }
      else {
         stop ("Unexpected token");
      }
      return result;
}

CmmNamespaceDecl * Parser::parse_namespace_declaration ()
{

      CmmNamespaceDecl * result = new CmmNamespaceDecl;
      result->kind = namespaceDecl;
      storeLocation (result);
      on_start_namespace (result);
      checkSymbol (keyword_namespace);
      result->simp_name = parse_simple_name ();
      result->attr = parse_attr_list ();
      on_namespace (result);
      checkSymbol (LBRACE);
      on_open_namespace (result);
      result->members = parse_declaration_list ();
      on_close_namespace (result);
      checkSymbol (RBRACE);
      on_stop_namespace (result);
      return result;
}

CmmUsingDecl * Parser::parse_using_declaration ()
{

      CmmUsingDecl * result = new CmmUsingDecl;
      result->kind = usingDecl;
      storeLocation (result);
      checkSymbol (keyword_using);
      if (isSymbol (keyword_namespace))
      {
         checkSymbol (keyword_namespace);
         result->a_namespace = true;
      }
      result->qual_name = parse_qualified_name ();
      on_using (result);
      checkSymbol (SEMICOLON);
      return result;
}

CmmExternDecl * Parser::parse_extern_declaration ()
{

      CmmExternDecl * result = new CmmExternDecl;
      result->kind = externDecl;
      storeLocation (result);
      checkSymbol (keyword_extern);
      if (isSymbol (string_literal))
      {
         result->language = readQuotedString ();
      }
      if (isSymbol (LBRACE))
      {
         checkSymbol (LBRACE);
         result->members = parse_declaration_list ();
         checkSymbol (RBRACE);
      }
      else if (testSymbols (set_18))
      {
         result->inner_declaration = parse_declaration ();
      }
      else {
         stop ("Unexpected token");
      }
      return result;
}

CmmTypedefDecl * Parser::parse_typedef_declaration ()
{

      CmmTypedefDecl * result = new CmmTypedefDecl;
      result->kind = typedefDecl;
      storeLocation (result);
      checkSymbol (keyword_typedef);
      result->type_spec = parse_type_specifiers ();
      result->declarator = parse_simple_declarator ();
      on_typedef (result);
      checkSymbol (SEMICOLON);
      return result;
}

CmmFriendDecl * Parser::parse_friend_declaration ()
{

      CmmFriendDecl * result = new CmmFriendDecl;
      result->kind = friendDecl;
      storeLocation (result);
      checkSymbol (keyword_friend);
      result->inner_declaration = parse_declaration ();
      return result;
}

CmmEnumDecl * Parser::parse_enum_declaration ()
{

      CmmEnumDecl * result = new CmmEnumDecl;
      result->kind = enumDecl;
      storeLocation (result);
      on_start_enum (result);
      checkSymbol (keyword_enum);
      result->simp_name = parse_simple_name ();
      on_enum (result);
      if (isSymbol (LBRACE))
      {
         checkSymbol (LBRACE);
         on_open_enum (result);
         result->enum_items = parse_enum_list ();
         on_close_enum (result);
         checkSymbol (RBRACE);
      }
      checkSymbol (SEMICOLON);
      on_stop_enum (result);
      return result;
}

CmmEnumSect * Parser::parse_enum_list ()
{

      CmmEnumSect * result = new CmmEnumSect;
      storeLocation (result);
      if (isSymbol (identifier))
      {
         result->items.push_back (parse_enumerator ());
         while (isSymbol (COMMA))
         {
            checkSymbol (COMMA);
            result->items.push_back (parse_enumerator ());
         }
      }
      return result;
}

CmmEnumItem * Parser::parse_enumerator ()
{

      CmmEnumItem * result = new CmmEnumItem;
      storeLocation (result);
      result->simp_name = parse_simple_name ();
      on_enum_item (result);
      if (isSymbol (ASSIGN))
      {
         checkSymbol (ASSIGN);
         result->init_value = parse_const_expr ();
      }
      return result;
}

CmmClassDecl * Parser::parse_class_declaration ()
{

      CmmClassDecl * result = new CmmClassDecl;
      result->kind = classDecl;
      storeLocation (result);
      on_start_class (result);
      if (isSymbol (keyword_class))
      {
         checkSymbol (keyword_class);
         result->style = classStyle;
      }
      else if (isSymbol (keyword_struct))
      {
         checkSymbol (keyword_struct);
         result->style = structStyle;
      }
      else if (isSymbol (keyword_union))
      {
         checkSymbol (keyword_union);
         result->style = unionStyle;
      }
      else {
         stop ("Unexpected token");
      }
      result->simp_name = parse_simple_name ();
      result->attr = parse_attr_list ();
      on_class (result);
      if (isSymbol (COLON) || isSymbol (LBRACE))
      {
         if (isSymbol (COLON))
         {
            checkSymbol (COLON);
            result->base_list = parse_base_specifier_list ();
         }
         checkSymbol (LBRACE);
         on_open_class (result);
         result->members = parse_member_list ();
         on_close_class (result);
         checkSymbol (RBRACE);
      }
      checkSymbol (SEMICOLON);
      on_stop_class (result);
      return result;
}

CmmMemberVisibility * Parser::parse_member_visibility ()
{

      CmmMemberVisibility * result = new CmmMemberVisibility;
      result->kind = visibilityDecl;
      storeLocation (result);
      if (isSymbol (keyword_private))
      {
         checkSymbol (keyword_private);
         result->access = privateAccess;
      }
      else if (isSymbol (keyword_protected))
      {
         checkSymbol (keyword_protected);
         result->access = protectedAccess;
      }
      else if (isSymbol (keyword_public))
      {
         checkSymbol (keyword_public);
         result->access = publicAccess;
      }
      else {
         stop ("Unexpected token");
      }
      on_member_visibility (result);
      checkSymbol (COLON);
      return result;
}

CmmStat * Parser::parse_member_item ()
{

      CmmStat * result = NULL;
      if (isSymbol (keyword_private) || isSymbol (keyword_protected) || isSymbol (keyword_public))
      {
         result = parse_member_visibility ();
      }
      else if (testSymbols (set_5))
      {
         result = parse_flexible_stat ();
      }
      else if (isSymbol (SEMICOLON))
      {
         result = parse_empty_stat ();
      }
      else if (isSymbol (LBRACE))
      {
         result = parse_compound_stat ();
      }
      else if (isSymbol (keyword_if))
      {
         result = parse_if_stat ();
      }
      else if (isSymbol (keyword_while))
      {
         result = parse_while_stat ();
      }
      else if (isSymbol (keyword_for))
      {
         result = parse_for_stat ();
      }
      else if (isSymbol (keyword_class) || isSymbol (keyword_struct) || isSymbol (keyword_union))
      {
         result = parse_class_declaration ();
      }
      else if (isSymbol (keyword_enum))
      {
         result = parse_enum_declaration ();
      }
      else if (isSymbol (keyword_typedef))
      {
         result = parse_typedef_declaration ();
      }
      else if (isSymbol (keyword_friend))
      {
         result = parse_friend_declaration ();
      }
      else if (isSymbol (keyword_using))
      {
         result = parse_using_declaration ();
      }
      else if (isSymbol (keyword_template))
      {
         result = parse_template_declaration ();
      }
      else if (isSymbol (keyword_stencil))
      {
         result = parse_stencil_declaration ();
      }
      else {
         stop ("Unexpected token");
      }
      return result;
}

CmmStatSect * Parser::parse_member_list ()
{

      CmmStatSect * result = new CmmStatSect;
      storeLocation (result);
      while (testSymbols (set_19))
      {
         on_declaration (result);
         on_start_member_item (result);
         result->items.push_back (parse_member_item ());
      }
      return result;
}

CmmBaseSect * Parser::parse_base_specifier_list ()
{

      CmmBaseSect * result = new CmmBaseSect;
      storeLocation (result);
      result->items.push_back (parse_base_specifier ());
      while (isSymbol (COMMA))
      {
         checkSymbol (COMMA);
         result->items.push_back (parse_base_specifier ());
      }
      return result;
}

CmmBaseItem * Parser::parse_base_specifier ()
{

      CmmBaseItem * result = new CmmBaseItem;
      storeLocation (result);
      if (isSymbol (keyword_virtual))
      {
         checkSymbol (keyword_virtual);
         result->a_virtual = true;
      }
      if (isSymbol (keyword_private))
      {
         checkSymbol (keyword_private);
         result->access = privateBase;
      }
      else if (isSymbol (keyword_protected))
      {
         checkSymbol (keyword_protected);
         result->access = protectedBase;
      }
      else if (isSymbol (keyword_public))
      {
         checkSymbol (keyword_public);
         result->access = publicBase;
      }
      else
      {
         result->access = unknownBase;
      }
      result->from_cls = parse_qualified_name ();
      return result;
}

CmmCtorInitializer * Parser::parse_ctor_initializer ()
{

      CmmCtorInitializer * result = new CmmCtorInitializer;
      storeLocation (result);
      result->items.push_back (parse_member_initializer ());
      while (isSymbol (COMMA))
      {
         checkSymbol (COMMA);
         result->items.push_back (parse_member_initializer ());
      }
      return result;
}

CmmMemberInitializer * Parser::parse_member_initializer ()
{

      CmmMemberInitializer * result = new CmmMemberInitializer;
      storeLocation (result);
      result->simp_name = parse_simple_name ();
      on_member_initializer (result);
      checkSymbol (LPAREN);
      result->params = parse_expr_list ();
      checkSymbol (RPAREN);
      return result;
}

CmmConvSpec * Parser::parse_conversion_specifiers ()
{

      CmmConvSpec * result = new CmmConvSpec;
      storeLocation (result);
      result->type_spec = parse_type_specifiers ();
      result->ptr_spec = parse_ptr_specifier_list ();
      return result;
}

CmmSpecialFuction * Parser::parse_special_function ()
{

      CmmSpecialFuction * result = new CmmSpecialFuction;
      result->kind = specialName;
      storeLocation (result);
      checkSymbol (keyword_operator);
      if (testSymbols (set_7))
      {
         result->conv = parse_conversion_specifiers ();
      }
      else if (isSymbol (keyword_new))
      {
         checkSymbol (keyword_new);
         result->spec_new = true;
         if (isSymbol (LBRACKET))
         {
            checkSymbol (LBRACKET);
            checkSymbol (RBRACKET);
            result->spec_new_array = true;
         }
      }
      else if (isSymbol (keyword_delete))
      {
         checkSymbol (keyword_delete);
         result->spec_delete = true;
         if (isSymbol (LBRACKET))
         {
            checkSymbol (LBRACKET);
            checkSymbol (RBRACKET);
            result->spec_delete_array = true;
         }
      }
      else if (isSymbol (PLUS))
      {
         checkSymbol (PLUS);
         result->spec_add = true;
      }
      else if (isSymbol (MINUS))
      {
         checkSymbol (MINUS);
         result->spec_sub = true;
      }
      else if (isSymbol (STAR))
      {
         checkSymbol (STAR);
         result->spec_mul = true;
      }
      else if (isSymbol (SLASH))
      {
         checkSymbol (SLASH);
         result->spec_div = true;
      }
      else if (isSymbol (MOD))
      {
         checkSymbol (MOD);
         result->spec_mod = true;
      }
      else if (isSymbol (BIT_XOR))
      {
         checkSymbol (BIT_XOR);
         result->spec_xor = true;
      }
      else if (isSymbol (BIT_AND))
      {
         checkSymbol (BIT_AND);
         result->spec_and = true;
      }
      else if (isSymbol (BIT_OR))
      {
         checkSymbol (BIT_OR);
         result->spec_or = true;
      }
      else if (isSymbol (BIT_NOT))
      {
         checkSymbol (BIT_NOT);
         result->spec_not = true;
      }
      else if (isSymbol (LOG_NOT))
      {
         checkSymbol (LOG_NOT);
         result->spec_log_not = true;
      }
      else if (isSymbol (ASSIGN))
      {
         checkSymbol (ASSIGN);
         result->spec_assign = true;
      }
      else if (isSymbol (LESS))
      {
         checkSymbol (LESS);
         result->spec_lt = true;
      }
      else if (isSymbol (GREATER))
      {
         checkSymbol (GREATER);
         result->spec_gt = true;
      }
      else if (isSymbol (PLUS_ASSIGN))
      {
         checkSymbol (PLUS_ASSIGN);
         result->spec_add_assign = true;
      }
      else if (isSymbol (MINUS_ASSIGN))
      {
         checkSymbol (MINUS_ASSIGN);
         result->spec_sub_assign = true;
      }
      else if (isSymbol (MUL_ASSIGN))
      {
         checkSymbol (MUL_ASSIGN);
         result->spec_mul_assign = true;
      }
      else if (isSymbol (DIV_ASSIGN))
      {
         checkSymbol (DIV_ASSIGN);
         result->spec_div_assign = true;
      }
      else if (isSymbol (MOD_ASSIGN))
      {
         checkSymbol (MOD_ASSIGN);
         result->spec_mod_assign = true;
      }
      else if (isSymbol (BIT_XOR_ASSIGN))
      {
         checkSymbol (BIT_XOR_ASSIGN);
         result->spec_xor_assign = true;
      }
      else if (isSymbol (BIT_AND_ASSIGN))
      {
         checkSymbol (BIT_AND_ASSIGN);
         result->spec_and_assign = true;
      }
      else if (isSymbol (BIT_OR_ASSIGN))
      {
         checkSymbol (BIT_OR_ASSIGN);
         result->spec_or_assign = true;
      }
      else if (isSymbol (SHL))
      {
         checkSymbol (SHL);
         result->spec_shl = true;
      }
      else if (isSymbol (SHR))
      {
         checkSymbol (SHR);
         result->spec_shr = true;
      }
      else if (isSymbol (SHR_ASSIGN))
      {
         checkSymbol (SHR_ASSIGN);
         result->spec_shl_assign = true;
      }
      else if (isSymbol (SHL_ASSIGN))
      {
         checkSymbol (SHL_ASSIGN);
         result->spec_shr_assign = true;
      }
      else if (isSymbol (EQUAL))
      {
         checkSymbol (EQUAL);
         result->spec_eq = true;
      }
      else if (isSymbol (UNEQUAL))
      {
         checkSymbol (UNEQUAL);
         result->spec_ne = true;
      }
      else if (isSymbol (LESS_OR_EQUAL))
      {
         checkSymbol (LESS_OR_EQUAL);
         result->spec_le = true;
      }
      else if (isSymbol (GREATER_OR_EQUAL))
      {
         checkSymbol (GREATER_OR_EQUAL);
         result->spec_ge = true;
      }
      else if (isSymbol (LOG_AND))
      {
         checkSymbol (LOG_AND);
         result->spec_log_and = true;
      }
      else if (isSymbol (LOG_OR))
      {
         checkSymbol (LOG_OR);
         result->spec_log_or = true;
      }
      else if (isSymbol (INC))
      {
         checkSymbol (INC);
         result->spec_inc = true;
      }
      else if (isSymbol (DEC))
      {
         checkSymbol (DEC);
         result->spec_dec = true;
      }
      else if (isSymbol (COMMA))
      {
         checkSymbol (COMMA);
         result->spec_comma = true;
      }
      else if (isSymbol (ARROW_STAR))
      {
         checkSymbol (ARROW_STAR);
         result->spec_member_deref = true;
      }
      else if (isSymbol (ARROW))
      {
         checkSymbol (ARROW);
         result->spec_deref = true;
      }
      else if (isSymbol (LPAREN))
      {
         checkSymbol (LPAREN);
         checkSymbol (RPAREN);
         result->spec_call = true;
      }
      else if (isSymbol (LBRACKET))
      {
         checkSymbol (LBRACKET);
         checkSymbol (RBRACKET);
         result->spec_index = true;
      }
      else {
         stop ("Unexpected token");
      }
      return result;
}

CmmTemplateDecl * Parser::parse_template_declaration ()
{

      CmmTemplateDecl * result = new CmmTemplateDecl;
      result->kind = templateDecl;
      storeLocation (result);
      checkSymbol (keyword_template);
      if (isSymbol (LESS))
      {
         checkSymbol (LESS);
         result->params = parse_template_param_list ();
         checkSymbol (GREATER);
      }
      result->inner_declaration = parse_declaration ();
      on_template_declaration (result);
      return result;
}

CmmStencilDecl * Parser::parse_stencil_declaration ()
{

      CmmStencilDecl * result = new CmmStencilDecl;
      result->kind = stencilDecl;
      storeLocation (result);
      checkSymbol (keyword_stencil);
      result->simp_name = parse_simple_name ();
      checkSymbol (LESS);
      result->params = parse_template_param_list ();
      checkSymbol (GREATER);
      on_stencil_params (result);
      checkSymbol (LBRACE);
      on_open_stencil (result);
      result->members = parse_stencil_member_list ();
      on_close_stencil (result);
      checkSymbol (RBRACE);
      on_stencil_declaration (result);
      return result;
}

CmmStatSect * Parser::parse_stencil_member_list ()
{

      CmmStatSect * result = new CmmStatSect;
      storeLocation (result);
      while (testSymbols (set_18))
      {
         on_declaration (result);
         result->items.push_back (parse_declaration ());
      }
      return result;
}

CmmTemplateParamSect * Parser::parse_template_param_list ()
{

      CmmTemplateParamSect * result = new CmmTemplateParamSect;
      storeLocation (result);
      if (testSymbols (set_20))
      {
         result->items.push_back (parse_template_param ());
         while (isSymbol (COMMA))
         {
            checkSymbol (COMMA);
            result->items.push_back (parse_template_param ());
         }
      }
      return result;
}

CmmTemplateParam * Parser::parse_template_param ()
{

      CmmTemplateParam * result = NULL;
      if (isSymbol (keyword_class) || isSymbol (keyword_template) || isSymbol (keyword_typename))
      {
         result = parse_template_type_param ();
      }
      else if (testSymbols (set_7))
      {
         result = parse_template_normal_param ();
      }
      else {
         stop ("Unexpected token");
      }
      return result;
}

CmmTemplateTypeParam * Parser::parse_template_type_param ()
{

      CmmTemplateTypeParam * result = new CmmTemplateTypeParam;
      result->kind = templateTypeParam;
      storeLocation (result);
      if (isSymbol (keyword_template))
      {
         checkSymbol (keyword_template);
         checkSymbol (LESS);
         result->params = parse_template_param_list ();
         checkSymbol (GREATER);
      }
      if (isSymbol (keyword_class))
      {
         checkSymbol (keyword_class);
         result->a_class = true;
      }
      else if (isSymbol (keyword_typename))
      {
         checkSymbol (keyword_typename);
         result->a_typename = true;
      }
      else {
         stop ("Unexpected token");
      }
      if (isSymbol (identifier))
      {
         result->simp_name = parse_simple_name ();
      }
      return result;
}

CmmTemplateNormalParam * Parser::parse_template_normal_param ()
{

      CmmTemplateNormalParam * result = new CmmTemplateNormalParam;
      result->kind = templateCommonParam;
      storeLocation (result);
      result->type_spec = parse_type_specifiers ();
      result->declarator = parse_common_declarator ();
      if (isSymbol (ASSIGN))
      {
         checkSymbol (ASSIGN);
         result->init = parse_shift_expr ();
      }
      return result;
}

CmmTemplateArgSect * Parser::parse_template_arg_list ()
{

      CmmTemplateArgSect * result = new CmmTemplateArgSect;
      storeLocation (result);
      checkSymbol (LESS);
      if (testSymbols (set_14))
      {
         result->items.push_back (parse_template_arg ());
         while (isSymbol (COMMA))
         {
            checkSymbol (COMMA);
            result->items.push_back (parse_template_arg ());
         }
      }
      checkSymbol (GREATER);
      return result;
}

CmmTemplateArg * Parser::parse_template_arg ()
{

      CmmTemplateArg * result = new CmmTemplateArg;
      storeLocation (result);
      result->value = parse_parameter_declaration ();
      return result;
}

CmmTryStat * Parser::parse_try_stat ()
{

      CmmTryStat * result = new CmmTryStat;
      result->kind = tryStat;
      storeLocation (result);
      checkSymbol (keyword_try);
      result->body = parse_compound_stat ();
      result->handlers = parse_handler_list ();
      return result;
}

CmmHandlerSect * Parser::parse_handler_list ()
{

      CmmHandlerSect * result = new CmmHandlerSect;
      storeLocation (result);
      result->items.push_back (parse_handler ());
      while (isSymbol (keyword_catch))
      {
         result->items.push_back (parse_handler ());
      }
      return result;
}

CmmHandlerItem * Parser::parse_handler ()
{

      CmmHandlerItem * result = new CmmHandlerItem;
      storeLocation (result);
      checkSymbol (keyword_catch);
      checkSymbol (LPAREN);
      if (testSymbols (set_7))
      {
         result->type_spec = parse_type_specifiers ();
         result->declarator = parse_common_declarator ();
      }
      else if (isSymbol (DOTS))
      {
         checkSymbol (DOTS);
         result->dots = true;
      }
      else {
         stop ("Unexpected token");
      }
      checkSymbol (RPAREN);
      result->body = parse_compound_stat ();
      return result;
}

CmmThrowExpr * Parser::parse_throw_expr ()
{

      CmmThrowExpr * result = new CmmThrowExpr;
      result->kind = throwExpr;
      storeLocation (result);
      checkSymbol (keyword_throw);
      if (testSymbols (set_5))
      {
         result->inner_expr = parse_assignment_expr ();
      }
      on_throw_expr (result);
      return result;
}

CmmExceptionSect * Parser::parse_exception_specification ()
{

      CmmExceptionSect * result = new CmmExceptionSect;
      storeLocation (result);
      checkSymbol (keyword_throw);
      checkSymbol (LPAREN);
      if (testSymbols (set_7))
      {
         result->items.push_back (parse_exception_specification_item ());
         while (isSymbol (COMMA))
         {
            checkSymbol (COMMA);
            result->items.push_back (parse_exception_specification_item ());
         }
      }
      checkSymbol (RPAREN);
      return result;
}

CmmExceptionItem * Parser::parse_exception_specification_item ()
{

      CmmExceptionItem * result = new CmmExceptionItem;
      storeLocation (result);
      result->type = parse_type_id ();
      return result;
}

void Parser::lookupKeyword ()
{
      string s = tokenTxt;
      int n = s.length ();
      if (n == 2)
      {
         if (s[0] == 'd')
         {
               if (s[1] == 'o')
               {
                     token = keyword_do;
               }
         }
         else if (s[0] == 'i')
         {
               if (s[1] == 'f')
               {
                     token = keyword_if;
               }
         }
      }
      else if (n == 3)
      {
         if (s[0] == 'f')
         {
               if (s.substr (1,2) == "or")
               {
                     token = keyword_for;
               }
         }
         else if (s[0] == 'i')
         {
               if (s.substr (1,2) == "nt")
               {
                     token = keyword_int;
               }
         }
         else if (s[0] == 'n')
         {
               if (s.substr (1,2) == "ew")
               {
                     token = keyword_new;
               }
         }
         else if (s[0] == 't')
         {
               if (s.substr (1,2) == "ry")
               {
                     token = keyword_try;
               }
         }
      }
      else if (n == 4)
      {
         if (s[0] == 'b')
         {
               if (s.substr (1,3) == "ool")
               {
                     token = keyword_bool;
               }
         }
         else if (s[0] == 'c')
         {
               if (s[1] == 'a')
               {
                     if (s.substr (2,2) == "se")
                     {
                           token = keyword_case;
                     }
               }
               else if (s[1] == 'h')
               {
                     if (s.substr (2,2) == "ar")
                     {
                           token = keyword_char;
                     }
               }
         }
         else if (s[0] == 'e')
         {
               if (s[1] == 'l')
               {
                     if (s.substr (2,2) == "se")
                     {
                           token = keyword_else;
                     }
               }
               else if (s[1] == 'n')
               {
                     if (s.substr (2,2) == "um")
                     {
                           token = keyword_enum;
                     }
               }
         }
         else if (s[0] == 'g')
         {
               if (s.substr (1,3) == "oto")
               {
                     token = keyword_goto;
               }
         }
         else if (s[0] == 'l')
         {
               if (s.substr (1,3) == "ong")
               {
                     token = keyword_long;
               }
         }
         else if (s[0] == 't')
         {
               if (s.substr (1,3) == "his")
               {
                     token = keyword_this;
               }
         }
         else if (s[0] == 'v')
         {
               if (s.substr (1,3) == "oid")
               {
                     token = keyword_void;
               }
         }
      }
      else if (n == 5)
      {
         if (s[0] == 'b')
         {
               if (s.substr (1,4) == "reak")
               {
                     token = keyword_break;
               }
         }
         else if (s[0] == 'c')
         {
               if (s[1] == 'a')
               {
                     if (s.substr (2,3) == "tch")
                     {
                           token = keyword_catch;
                     }
               }
               else if (s[1] == 'l')
               {
                     if (s.substr (2,3) == "ass")
                     {
                           token = keyword_class;
                     }
               }
               else if (s[1] == 'o')
               {
                     if (s.substr (2,3) == "nst")
                     {
                           token = keyword_const;
                     }
               }
         }
         else if (s[0] == 'f')
         {
               if (s.substr (1,4) == "loat")
               {
                     token = keyword_float;
               }
         }
         else if (s[0] == 's')
         {
               if (s.substr (1,4) == "hort")
               {
                     token = keyword_short;
               }
         }
         else if (s[0] == 't')
         {
               if (s.substr (1,4) == "hrow")
               {
                     token = keyword_throw;
               }
         }
         else if (s[0] == 'u')
         {
               if (s[1] == 'n')
               {
                     if (s.substr (2,3) == "ion")
                     {
                           token = keyword_union;
                     }
               }
               else if (s[1] == 's')
               {
                     if (s.substr (2,3) == "ing")
                     {
                           token = keyword_using;
                     }
               }
         }
         else if (s[0] == 'w')
         {
               if (s.substr (1,4) == "hile")
               {
                     token = keyword_while;
               }
         }
      }
      else if (n == 6)
      {
         if (s[0] == 'd')
         {
               if (s[1] == 'e')
               {
                     if (s.substr (2,4) == "lete")
                     {
                           token = keyword_delete;
                     }
               }
               else if (s[1] == 'o')
               {
                     if (s.substr (2,4) == "uble")
                     {
                           token = keyword_double;
                     }
               }
         }
         else if (s[0] == 'e')
         {
               if (s.substr (1,5) == "xtern")
               {
                     token = keyword_extern;
               }
         }
         else if (s[0] == 'f')
         {
               if (s.substr (1,5) == "riend")
               {
                     token = keyword_friend;
               }
         }
         else if (s[0] == 'i')
         {
               if (s.substr (1,5) == "nline")
               {
                     token = keyword_inline;
               }
         }
         else if (s[0] == 'p')
         {
               if (s.substr (1,5) == "ublic")
               {
                     token = keyword_public;
               }
         }
         else if (s[0] == 'r')
         {
               if (s.substr (1,5) == "eturn")
               {
                     token = keyword_return;
               }
         }
         else if (s[0] == 's')
         {
               if (s[1] == 'i')
               {
                     if (s[2] == 'g')
                     {
                           if (s.substr (3,3) == "ned")
                           {
                                 token = keyword_signed;
                           }
                     }
                     else if (s[2] == 'z')
                     {
                           if (s.substr (3,3) == "eof")
                           {
                                 token = keyword_sizeof;
                           }
                     }
               }
               else if (s[1] == 't')
               {
                     if (s[2] == 'a')
                     {
                           if (s.substr (3,3) == "tic")
                           {
                                 token = keyword_static;
                           }
                     }
                     else if (s[2] == 'r')
                     {
                           if (s.substr (3,3) == "uct")
                           {
                                 token = keyword_struct;
                           }
                     }
               }
               else if (s[1] == 'w')
               {
                     if (s.substr (2,4) == "itch")
                     {
                           token = keyword_switch;
                     }
               }
         }
         else if (s[0] == 't')
         {
               if (s.substr (1,5) == "ypeid")
               {
                     token = keyword_typeid;
               }
         }
      }
      else if (n == 7)
      {
         if (s[0] == 'd')
         {
               if (s.substr (1,6) == "efault")
               {
                     token = keyword_default;
               }
         }
         else if (s[0] == 'm')
         {
               if (s.substr (1,6) == "utable")
               {
                     token = keyword_mutable;
               }
         }
         else if (s[0] == 'p')
         {
               if (s.substr (1,6) == "rivate")
               {
                     token = keyword_private;
               }
         }
         else if (s[0] == 's')
         {
               if (s.substr (1,6) == "tencil")
               {
                     token = keyword_stencil;
               }
         }
         else if (s[0] == 't')
         {
               if (s.substr (1,6) == "ypedef")
               {
                     token = keyword_typedef;
               }
         }
         else if (s[0] == 'v')
         {
               if (s.substr (1,6) == "irtual")
               {
                     token = keyword_virtual;
               }
         }
         else if (s[0] == 'w')
         {
               if (s.substr (1,6) == "char_t")
               {
                     token = keyword_wchar_t;
               }
         }
      }
      else if (n == 8)
      {
         if (s[0] == 'c')
         {
               if (s.substr (1,7) == "ontinue")
               {
                     token = keyword_continue;
               }
         }
         else if (s[0] == 'e')
         {
               if (s.substr (1,7) == "xplicit")
               {
                     token = keyword_explicit;
               }
         }
         else if (s[0] == 'o')
         {
               if (s[1] == 'p')
               {
                     if (s.substr (2,6) == "erator")
                     {
                           token = keyword_operator;
                     }
               }
               else if (s[1] == 'v')
               {
                     if (s.substr (2,6) == "erride")
                     {
                           token = keyword_override;
                     }
               }
         }
         else if (s[0] == 'r')
         {
               if (s.substr (1,7) == "egister")
               {
                     token = keyword_register;
               }
         }
         else if (s[0] == 't')
         {
               if (s[1] == 'e')
               {
                     if (s.substr (2,6) == "mplate")
                     {
                           token = keyword_template;
                     }
               }
               else if (s[1] == 'y')
               {
                     if (s.substr (2,6) == "pename")
                     {
                           token = keyword_typename;
                     }
               }
         }
         else if (s[0] == 'u')
         {
               if (s.substr (1,7) == "nsigned")
               {
                     token = keyword_unsigned;
               }
         }
         else if (s[0] == 'v')
         {
               if (s.substr (1,7) == "olatile")
               {
                     token = keyword_volatile;
               }
         }
      }
      else if (n == 9)
      {
         if (s[0] == 'n')
         {
               if (s.substr (1,8) == "amespace")
               {
                     token = keyword_namespace;
               }
         }
         else if (s[0] == 'p')
         {
               if (s.substr (1,8) == "rotected")
               {
                     token = keyword_protected;
               }
         }
      }
      else if (n == 10)
      {
         if (s.substr (0,10) == "const_cast")
         {
               token = keyword_const_cast;
         }
      }
      else if (n == 11)
      {
         if (s.substr (0,11) == "static_cast")
         {
               token = keyword_static_cast;
         }
      }
      else if (n == 12)
      {
         if (s.substr (0,12) == "dynamic_cast")
         {
               token = keyword_dynamic_cast;
         }
      }
      else if (n == 16)
      {
         if (s.substr (0,16) == "reinterpret_cast")
         {
               token = keyword_reinterpret_cast;
         }
      }
}

void Parser::processSeparator ()
{
      if (tokenTxt == "!")
      {
         token = LOG_NOT;
         if (inpCh == '=')
         {
            token = UNEQUAL;
            tokenTxt = tokenTxt + inpCh;
            nextCh ();
         }
      }
      if (tokenTxt == "%")
      {
         token = MOD;
         if (inpCh == '=')
         {
            token = MOD_ASSIGN;
            tokenTxt = tokenTxt + inpCh;
            nextCh ();
         }
      }
      if (tokenTxt == "&")
      {
         token = BIT_AND;
         if (inpCh == '&')
         {
            token = LOG_AND;
            tokenTxt = tokenTxt + inpCh;
            nextCh ();
         }
         if (inpCh == '=')
         {
            token = BIT_AND_ASSIGN;
            tokenTxt = tokenTxt + inpCh;
            nextCh ();
         }
      }
      if (tokenTxt == "(")
      {
         token = LPAREN;
      }
      if (tokenTxt == ")")
      {
         token = RPAREN;
      }
      if (tokenTxt == "*")
      {
         token = STAR;
         if (inpCh == '=')
         {
            token = MUL_ASSIGN;
            tokenTxt = tokenTxt + inpCh;
            nextCh ();
         }
      }
      if (tokenTxt == "+")
      {
         token = PLUS;
         if (inpCh == '+')
         {
            token = INC;
            tokenTxt = tokenTxt + inpCh;
            nextCh ();
         }
         if (inpCh == '=')
         {
            token = PLUS_ASSIGN;
            tokenTxt = tokenTxt + inpCh;
            nextCh ();
         }
      }
      if (tokenTxt == ",")
      {
         token = COMMA;
      }
      if (tokenTxt == "-")
      {
         token = MINUS;
         if (inpCh == '-')
         {
            token = DEC;
            tokenTxt = tokenTxt + inpCh;
            nextCh ();
         }
         if (inpCh == '=')
         {
            token = MINUS_ASSIGN;
            tokenTxt = tokenTxt + inpCh;
            nextCh ();
         }
         if (inpCh == '>')
         {
            token = ARROW;
            tokenTxt = tokenTxt + inpCh;
            nextCh ();
            if (inpCh == '*')
            {
               token = ARROW_STAR;
               tokenTxt = tokenTxt + inpCh;
               nextCh ();
            }
         }
      }
      if (tokenTxt == ".")
      {
         token = DOT;
         if (inpCh == '*')
         {
            token = DOT_STAR;
            tokenTxt = tokenTxt + inpCh;
            nextCh ();
         }
         if (inpCh == '.')
         {
            tokenTxt = tokenTxt + inpCh;
            nextCh ();
            if (inpCh == '.')
            {
               token = DOTS;
               tokenTxt = tokenTxt + inpCh;
               nextCh ();
            }
         }
      }
      if (tokenTxt == "/")
      {
         token = SLASH;
         if (inpCh == '=')
         {
            token = DIV_ASSIGN;
            tokenTxt = tokenTxt + inpCh;
            nextCh ();
         }
      }
      if (tokenTxt == ":")
      {
         token = COLON;
         if (inpCh == ':')
         {
            token = SCOPE;
            tokenTxt = tokenTxt + inpCh;
            nextCh ();
         }
      }
      if (tokenTxt == ";")
      {
         token = SEMICOLON;
      }
      if (tokenTxt == "<")
      {
         token = LESS;
         if (inpCh == '<')
         {
            token = SHL;
            tokenTxt = tokenTxt + inpCh;
            nextCh ();
            if (inpCh == '=')
            {
               token = SHL_ASSIGN;
               tokenTxt = tokenTxt + inpCh;
               nextCh ();
            }
         }
         if (inpCh == '=')
         {
            token = LESS_OR_EQUAL;
            tokenTxt = tokenTxt + inpCh;
            nextCh ();
         }
      }
      if (tokenTxt == "=")
      {
         token = ASSIGN;
         if (inpCh == '=')
         {
            token = EQUAL;
            tokenTxt = tokenTxt + inpCh;
            nextCh ();
         }
      }
      if (tokenTxt == ">")
      {
         token = GREATER;
         if (inpCh == '=')
         {
            token = GREATER_OR_EQUAL;
            tokenTxt = tokenTxt + inpCh;
            nextCh ();
         }
         if (inpCh == '>')
         {
            token = SHR;
            tokenTxt = tokenTxt + inpCh;
            nextCh ();
            if (inpCh == '=')
            {
               token = SHR_ASSIGN;
               tokenTxt = tokenTxt + inpCh;
               nextCh ();
            }
         }
      }
      if (tokenTxt == "?")
      {
         token = QUESTION;
      }
      if (tokenTxt == "[")
      {
         token = LBRACKET;
         if (inpCh == '[')
         {
            token = literal_1;
            tokenTxt = tokenTxt + inpCh;
            nextCh ();
         }
      }
      if (tokenTxt == "]")
      {
         token = RBRACKET;
         if (inpCh == ']')
         {
            token = literal_2;
            tokenTxt = tokenTxt + inpCh;
            nextCh ();
         }
      }
      if (tokenTxt == "^")
      {
         token = BIT_XOR;
         if (inpCh == '=')
         {
            token = BIT_XOR_ASSIGN;
            tokenTxt = tokenTxt + inpCh;
            nextCh ();
         }
      }
      if (tokenTxt == "{")
      {
         token = LBRACE;
      }
      if (tokenTxt == "|")
      {
         token = BIT_OR;
         if (inpCh == '=')
         {
            token = BIT_OR_ASSIGN;
            tokenTxt = tokenTxt + inpCh;
            nextCh ();
         }
         if (inpCh == '|')
         {
            token = LOG_OR;
            tokenTxt = tokenTxt + inpCh;
            nextCh ();
         }
      }
      if (tokenTxt == "}")
      {
         token = RBRACE;
      }
      if (tokenTxt == "~")
      {
         token = BIT_NOT;
      }
      if (token == separator)
      {
         stop ("Unknown separator");
      }
}

string Parser::tokenToString (CmmSymbol value)
{
      if (value  ==  0)
         return "<end of source text>";
      if (value  ==  1)
         return "<identifier>";
      if (value  ==  2)
         return "<number>";
      if (value  ==  3)
         return "<real_number>";
      if (value  ==  4)
         return "<character_literal>";
      if (value  ==  5)
         return "<string_literal>";
      if (value  ==  6)
         return "<unknown separator>";
      if (value  ==  7)
         return "<end of line>";
      if (value  ==  8)
         return "!";
      if (value  ==  9)
         return "!=";
      if (value  ==  10)
         return "%";
      if (value  ==  11)
         return "%=";
      if (value  ==  12)
         return "&";
      if (value  ==  13)
         return "&&";
      if (value  ==  14)
         return "&=";
      if (value  ==  15)
         return "(";
      if (value  ==  16)
         return ")";
      if (value  ==  17)
         return "*";
      if (value  ==  18)
         return "*=";
      if (value  ==  19)
         return "+";
      if (value  ==  20)
         return "++";
      if (value  ==  21)
         return "+=";
      if (value  ==  22)
         return ",";
      if (value  ==  23)
         return "-";
      if (value  ==  24)
         return "--";
      if (value  ==  25)
         return "-=";
      if (value  ==  26)
         return "->";
      if (value  ==  27)
         return "->*";
      if (value  ==  28)
         return ".";
      if (value  ==  29)
         return ".*";
      if (value  ==  30)
         return "...";
      if (value  ==  31)
         return "/";
      if (value  ==  32)
         return "/=";
      if (value  ==  33)
         return ":";
      if (value  ==  34)
         return "::";
      if (value  ==  35)
         return ";";
      if (value  ==  36)
         return "<";
      if (value  ==  37)
         return "<<";
      if (value  ==  38)
         return "<<=";
      if (value  ==  39)
         return "<=";
      if (value  ==  40)
         return "=";
      if (value  ==  41)
         return "==";
      if (value  ==  42)
         return ">";
      if (value  ==  43)
         return ">=";
      if (value  ==  44)
         return ">>";
      if (value  ==  45)
         return ">>=";
      if (value  ==  46)
         return "?";
      if (value  ==  47)
         return "[";
      if (value  ==  48)
         return "[[";
      if (value  ==  49)
         return "]";
      if (value  ==  50)
         return "]]";
      if (value  ==  51)
         return "^";
      if (value  ==  52)
         return "^=";
      if (value  ==  53)
         return "{";
      if (value  ==  54)
         return "|";
      if (value  ==  55)
         return "|=";
      if (value  ==  56)
         return "||";
      if (value  ==  57)
         return "}";
      if (value  ==  58)
         return "~";
      if (value  ==  59)
         return "bool";
      if (value  ==  60)
         return "break";
      if (value  ==  61)
         return "case";
      if (value  ==  62)
         return "catch";
      if (value  ==  63)
         return "char";
      if (value  ==  64)
         return "class";
      if (value  ==  65)
         return "const";
      if (value  ==  66)
         return "const_cast";
      if (value  ==  67)
         return "continue";
      if (value  ==  68)
         return "default";
      if (value  ==  69)
         return "delete";
      if (value  ==  70)
         return "do";
      if (value  ==  71)
         return "double";
      if (value  ==  72)
         return "dynamic_cast";
      if (value  ==  73)
         return "else";
      if (value  ==  74)
         return "enum";
      if (value  ==  75)
         return "explicit";
      if (value  ==  76)
         return "extern";
      if (value  ==  77)
         return "float";
      if (value  ==  78)
         return "for";
      if (value  ==  79)
         return "friend";
      if (value  ==  80)
         return "goto";
      if (value  ==  81)
         return "if";
      if (value  ==  82)
         return "inline";
      if (value  ==  83)
         return "int";
      if (value  ==  84)
         return "long";
      if (value  ==  85)
         return "mutable";
      if (value  ==  86)
         return "namespace";
      if (value  ==  87)
         return "new";
      if (value  ==  88)
         return "operator";
      if (value  ==  89)
         return "override";
      if (value  ==  90)
         return "private";
      if (value  ==  91)
         return "protected";
      if (value  ==  92)
         return "public";
      if (value  ==  93)
         return "register";
      if (value  ==  94)
         return "reinterpret_cast";
      if (value  ==  95)
         return "return";
      if (value  ==  96)
         return "short";
      if (value  ==  97)
         return "signed";
      if (value  ==  98)
         return "sizeof";
      if (value  ==  99)
         return "static";
      if (value  ==  100)
         return "static_cast";
      if (value  ==  101)
         return "stencil";
      if (value  ==  102)
         return "struct";
      if (value  ==  103)
         return "switch";
      if (value  ==  104)
         return "template";
      if (value  ==  105)
         return "this";
      if (value  ==  106)
         return "throw";
      if (value  ==  107)
         return "try";
      if (value  ==  108)
         return "typedef";
      if (value  ==  109)
         return "typeid";
      if (value  ==  110)
         return "typename";
      if (value  ==  111)
         return "union";
      if (value  ==  112)
         return "unsigned";
      if (value  ==  113)
         return "using";
      if (value  ==  114)
         return "virtual";
      if (value  ==  115)
         return "void";
      if (value  ==  116)
         return "volatile";
      if (value  ==  117)
         return "wchar_t";
      if (value  ==  118)
         return "while";
      return "<unknown symbol>";
}

void Parser::translate ()
{
      if (tokenKind == nameToken)
      {
         token = identifier;
         lookupKeyword ();
      }
      else if (tokenKind == numberToken)
      {
         token = number;
      }
      else if (tokenKind == realToken)
      {
         token = real_number;
      }
      else if (tokenKind == charToken)
      {
         token = character_literal;
      }
      else if (tokenKind == stringToken)
      {
         token = string_literal;
      }
      else if (tokenKind == eofToken)
      {
         token = eos;
      }
      else
      {
         token = separator;
         processSeparator ();
      }
}

void Parser::storeLocation (CmmBasic * item)
{
      item->src_file = getTokenFileInx ();
      item->src_line = getTokenLine ();
      item->src_column = getTokenCol ();
}

void Parser::on_binary_expr (CmmBasic * item)
{
}

bool Parser::is_binary_expression (CmmBasic * item)
{
      return false;
}

bool Parser::is_postfix_expression (CmmBasic * item)
{
      return false;
}

bool Parser::is_cast_expression (CmmBasic * item)
{
      return false;
}

void Parser::on_ident_expr (CmmName * item)
{
}

void Parser::on_int_value (CmmIntValue * item)
{
}

void Parser::on_real_value (CmmRealValue * item)
{
}

void Parser::on_char_value (CmmCharValue * item)
{
}

void Parser::on_string_value (CmmStringValue * item)
{
}

void Parser::on_this_expr (CmmThisExpr * item)
{
}

void Parser::on_subexpr_expr (CmmSubexprExpr * item)
{
}

void Parser::on_modern_cast_expr (CmmModernCastExpr * item)
{
}

void Parser::on_typeid_expr (CmmTypeIdExpr * item)
{
}

void Parser::on_type_name (CmmTypeName * item)
{
}

void Parser::on_type_specifier (CmmTypeSpec * item)
{
}

void Parser::on_const_specifier (CmmConstSpecifier * item)
{
}

void Parser::on_volatile_specifier (CmmVolatileSpecifier * item)
{
}

void Parser::on_decl_specifier (CmmDeclSpec * item)
{
}

void Parser::on_index_expr (CmmIndexExpr * item)
{
}

void Parser::on_call_expr (CmmCallExpr * item)
{
}

void Parser::on_field_expr (CmmFieldExpr * item)
{
}

void Parser::on_ptr_field_expr (CmmPtrFieldExpr * item)
{
}

void Parser::on_post_inc_expr (CmmPostIncExpr * item)
{
}

void Parser::on_post_dec_expr (CmmPostDecExpr * item)
{
}

void Parser::on_bit_not_expr (CmmBitNotExpr * item)
{
}

void Parser::on_inc_expr (CmmIncExpr * item)
{
}

void Parser::on_dec_expr (CmmDecExpr * item)
{
}

void Parser::on_deref_expr (CmmDerefExpr * item)
{
}

void Parser::on_addr_expr (CmmAddrExpr * item)
{
}

void Parser::on_plus_expr (CmmPlusExpr * item)
{
}

void Parser::on_minus_expr (CmmMinusExpr * item)
{
}

void Parser::on_log_not_expr (CmmLogNotExpr * item)
{
}

void Parser::on_sizeof_expr (CmmSizeofExpr * item)
{
}

void Parser::on_allocation_expr (CmmNewExpr * item)
{
}

void Parser::on_deallocation_expr (CmmDeleteExpr * item)
{
}

void Parser::on_throw_expr (CmmThrowExpr * item)
{
}

void Parser::on_base_name (CmmName * item)
{
}

void Parser::on_cont_name (CmmCompoundName * item)
{
}

void Parser::on_template_name (CmmTemplateName * item)
{
}

bool Parser::is_template_name (CmmName * item)
{
      return false;
}

bool Parser::is_signal_slot (CmmBasic * item)
{
      return false;
}

void Parser::on_middle_bit_not_expr (CmmBitNotExpr * item)
{
}

bool Parser::is_mul (CmmBasic * item)
{
      return false;
}

bool Parser::is_add (CmmBasic * item)
{
      return false;
}

void Parser::on_expr (CmmExpr * item)
{
}

void Parser::on_open_compound_statement (CmmCompoundStat * item)
{
}

void Parser::on_declaration (CmmBasic * item)
{
}

void Parser::on_close_compound_statement (CmmCompoundStat * item)
{
}

void Parser::on_open_if_statement (CmmIfStat * item)
{
}

void Parser::on_close_if_statement (CmmIfStat * item)
{
}

void Parser::on_open_while_statement (CmmWhileStat * item)
{
}

void Parser::on_close_while_statement (CmmWhileStat * item)
{
}

void Parser::on_open_for_statement (CmmForStat * item)
{
}

void Parser::on_close_for_statement (CmmForStat * item)
{
}

void Parser::on_open_switch_statement (CmmSwitchStat * item)
{
}

void Parser::on_close_switch_statement (CmmSwitchStat * item)
{
}

void Parser::on_open_flexible_stat ()
{
}

bool Parser::is_expression (CmmExpr * item)
{
      return false;
}

bool Parser::is_constructor (CmmExpr * item)
{
      return false;
}

void Parser::on_open_simple_stat (CmmSimpleStat * item)
{
}

void Parser::on_open_expr_block (CmmSimpleStat * item)
{
}

void Parser::on_close_expr_block (CmmSimpleStat * item)
{
}

void Parser::on_simple_statement (CmmSimpleStat * item)
{
}

void Parser::on_middle_decl_specifier (CmmDeclSpec * item)
{
}

void Parser::on_simple_declarator (CmmDeclarator * item)
{
}

bool Parser::is_value_parameter (CmmExpr * item)
{
      return false;
}

void Parser::on_open_simple_declaration (CmmSimpleDecl * item)
{
}

void Parser::on_simple_item (CmmSimpleDecl * item)
{
}

void Parser::on_open_function (CmmSimpleDecl * item)
{
}

void Parser::on_close_function (CmmSimpleDecl * item)
{
}

void Parser::on_simple_declaration (CmmSimpleDecl * item)
{
}

void Parser::on_open_constructor_declaration (CmmSimpleDecl * item)
{
}

void Parser::on_start_namespace (CmmNamespaceDecl * item)
{
}

void Parser::on_namespace (CmmNamespaceDecl * item)
{
}

void Parser::on_open_namespace (CmmNamespaceDecl * item)
{
}

void Parser::on_close_namespace (CmmNamespaceDecl * item)
{
}

void Parser::on_stop_namespace (CmmNamespaceDecl * item)
{
}

void Parser::on_using (CmmUsingDecl * item)
{
}

void Parser::on_typedef (CmmTypedefDecl * item)
{
}

void Parser::on_start_enum (CmmEnumDecl * item)
{
}

void Parser::on_enum (CmmEnumDecl * item)
{
}

void Parser::on_open_enum (CmmEnumDecl * item)
{
}

void Parser::on_close_enum (CmmEnumDecl * item)
{
}

void Parser::on_stop_enum (CmmEnumDecl * item)
{
}

void Parser::on_enum_item (CmmEnumItem * item)
{
}

void Parser::on_start_class (CmmClassDecl * item)
{
}

void Parser::on_class (CmmClassDecl * item)
{
}

void Parser::on_open_class (CmmClassDecl * item)
{
}

void Parser::on_close_class (CmmClassDecl * item)
{
}

void Parser::on_stop_class (CmmClassDecl * item)
{
}

void Parser::on_member_visibility (CmmMemberVisibility * item)
{
}

void Parser::on_start_member_item (CmmStatSect * item)
{
}

void Parser::on_member_initializer (CmmMemberInitializer * item)
{
}

void Parser::on_template_declaration (CmmTemplateDecl * item)
{
}

void Parser::on_stencil_params (CmmStencilDecl * item)
{
}

void Parser::on_open_stencil (CmmStencilDecl * item)
{
}

void Parser::on_close_stencil (CmmStencilDecl * item)
{
}

void Parser::on_stencil_declaration (CmmStencilDecl * item)
{
}

Parser::Parser ()
{
}
