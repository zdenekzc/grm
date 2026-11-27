#include "pas_parser.h"

const unsigned char set_0 [15] = {0, 65, 0, 40, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
// set_0 :  ( . [ ^

const unsigned char set_1 [15] = {0, 4, 1, 128, 2, 8, 0, 0, 32, 0, 0, 128, 1, 0, 0};
// set_1 :  * / and as div mod shl shr

const unsigned char set_2 [15] = {0, 40, 0, 0, 0, 0, 0, 0, 0, 16, 0, 0, 0, 0, 1};
// set_2 :  + - or xor

const unsigned char set_3 [15] = {0, 0, 240, 3, 0, 0, 0, 32, 4, 0, 0, 0, 0, 0, 0};
// set_3 :  < <= <> = > >= in is

const unsigned char set_4 [15] = {46, 41, 0, 12, 0, 0, 0, 64, 64, 1, 0, 0, 8, 0, 0};
// set_4 :  identifier number real_number string_literal ( + - @ [ inherited nil not string

const unsigned char set_5 [15] = {46, 41, 8, 12, 24, 0, 64, 70, 64, 1, 0, 17, 72, 96, 0};
// set_5 :  identifier number real_number string_literal ( + - ; @ [ begin case for goto if inherited nil not raise repeat string try while with

const unsigned char set_6 [15] = {0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 226, 0, 0, 0, 0};
// set_6 :  automated private protected public published

const unsigned char set_7 [15] = {2, 0, 0, 0, 64, 5, 0, 1, 0, 0, 20, 0, 0, 0, 0};
// set_7 :  identifier class constructor destructor function procedure property

const unsigned char set_8 [15] = {0, 0, 0, 0, 64, 5, 0, 1, 0, 0, 4, 0, 0, 0, 0};
// set_8 :  class constructor destructor function procedure

const unsigned char set_9 [15] = {0, 0, 0, 64, 0, 64, 0, 0, 0, 64, 0, 0, 0, 16, 0};
// set_9 :  abstract dynamic override virtual

const unsigned char set_10 [15] = {0, 0, 0, 0, 32, 0, 0, 0, 0, 0, 1, 40, 2, 0, 0};
// set_10 :  cdecl pascal register safecall stdcall

const unsigned char set_11 [15] = {0, 0, 0, 0, 200, 5, 0, 1, 9, 0, 4, 0, 128, 8, 0};
// set_11 :  begin class const constructor destructor function inline label procedure type var

const unsigned char set_12 [15] = {0, 0, 0, 0, 192, 5, 0, 1, 0, 0, 4, 0, 128, 8, 0};
// set_12 :  class const constructor destructor function procedure type var

const unsigned char set_13 [15] = {0, 0, 0, 0, 192, 5, 0, 1, 8, 0, 4, 0, 128, 8, 0};
// set_13 :  class const constructor destructor function label procedure type var


TLabelIdent * Parser::parse_label_ident ()
{

      TLabelIdent * result = new TLabelIdent;
      storeLocation (result);
      result->id = readIdent ();
      return result;
}

TQualName * Parser::parse_qualified_name ()
{

      TQualName * result = new TQualName;
      storeLocation (result);
      result->id = readIdent ();
      while (isSymbol (DOT))
      {
         result->items.push_back (parse_cont_name ());
      }
      return result;
}

TContName * Parser::parse_cont_name ()
{

      TContName * result = new TContName;
      storeLocation (result);
      checkSymbol (DOT);
      result->id = readIdent ();
      return result;
}

TType * Parser::parse_ifc_type ()
{

      TType * result = NULL;
      result = parse_simple_alias_type ();
      return result;
}

TType * Parser::parse_param_type ()
{

      TType * result = NULL;
      if (isSymbol (identifier))
      {
         result = parse_simple_alias_type ();
      }
      else if (isSymbol (keyword_string))
      {
         result = parse_simple_string_type ();
      }
      else if (isSymbol (keyword_file))
      {
         result = parse_simple_file_type ();
      }
      else {
         stop ("Unexpected token");
      }
      return result;
}

TType * Parser::parse_result_type ()
{

      TType * result = NULL;
      if (isSymbol (identifier))
      {
         result = parse_simple_alias_type ();
      }
      else if (isSymbol (keyword_string))
      {
         result = parse_simple_string_type ();
      }
      else {
         stop ("Unexpected token");
      }
      return result;
}

TAliasType * Parser::parse_simple_alias_type ()
{

      TAliasType * result = new TAliasType;
      storeLocation (result);
      result->alias_name = parse_qualified_name ();
      return result;
}

TStringType * Parser::parse_simple_string_type ()
{

      TStringType * result = new TStringType;
      storeLocation (result);
      checkSymbol (keyword_string);
      return result;
}

TFileType * Parser::parse_simple_file_type ()
{

      TFileType * result = new TFileType;
      storeLocation (result);
      checkSymbol (keyword_file);
      return result;
}

TInxItem * Parser::parse_index_expr_item ()
{

      TInxItem * result = new TInxItem;
      storeLocation (result);
      result->ref = parse_expr ();
      return result;
}

TInxList * Parser::parse_index_expr_list ()
{

      TInxList * result = new TInxList;
      storeLocation (result);
      result->items.push_back (parse_index_expr_item ());
      while (isSymbol (COMMA))
      {
         checkSymbol (COMMA);
         result->items.push_back (parse_index_expr_item ());
      }
      return result;
}

TArgItem * Parser::parse_arg_item ()
{

      TArgItem * result = new TArgItem;
      storeLocation (result);
      result->value = parse_expr ();
      if (isSymbol (COLON))
      {
         checkSymbol (COLON);
         result->width = parse_expr ();
         if (isSymbol (COLON))
         {
            checkSymbol (COLON);
            result->digits = parse_expr ();
         }
      }
      return result;
}

TArgSect * Parser::parse_arg_list ()
{

      TArgSect * result = new TArgSect;
      storeLocation (result);
      result->items.push_back (parse_arg_item ());
      while (isSymbol (COMMA))
      {
         checkSymbol (COMMA);
         result->items.push_back (parse_arg_item ());
      }
      return result;
}

TElemSect * Parser::parse_elem_sect ()
{

      TElemSect * result = new TElemSect;
      storeLocation (result);
      result->items.push_back (parse_elem_item ());
      while (isSymbol (COMMA))
      {
         checkSymbol (COMMA);
         result->items.push_back (parse_elem_item ());
      }
      return result;
}

TElemItem * Parser::parse_elem_item ()
{

      TElemItem * result = new TElemItem;
      storeLocation (result);
      result->low = parse_expr ();
      if (isSymbol (RANGE))
      {
         checkSymbol (RANGE);
         result->high = parse_expr ();
      }
      return result;
}

TStructSect * Parser::parse_struct_item ()
{

      TStructSect * result = new TStructSect;
      storeLocation (result);
      if (isSymbol (identifier))
      {
         result->name = readIdent ();
         checkSymbol (COLON);
      }
      result->value = parse_expr ();
      return result;
}

TStructSect * Parser::parse_struct_sect ()
{

      TStructSect * result = new TStructSect;
      storeLocation (result);
      result->items.push_back (parse_struct_item ());
      if (isSymbol (COMMA) || isSymbol (SEMICOLON))
      {
         if (isSymbol (COMMA))
         {
            checkSymbol (COMMA);
            result->items.push_back (parse_struct_item ());
            while (isSymbol (COMMA))
            {
               checkSymbol (COMMA);
               result->items.push_back (parse_struct_item ());
            }
         }
         else if (isSymbol (SEMICOLON))
         {
            checkSymbol (SEMICOLON);
            result->items.push_back (parse_struct_item ());
            while (isSymbol (SEMICOLON))
            {
               checkSymbol (SEMICOLON);
               result->items.push_back (parse_struct_item ());
            }
         }
         else {
            stop ("Unexpected token");
         }
      }
      return result;
}

TIdentExpr * Parser::parse_ident_expr ()
{

      TIdentExpr * result = new TIdentExpr;
      storeLocation (result);
      result->name = readIdent ();
      on_ident_expr (result);
      return result;
}

TIntValueExpr * Parser::parse_int_value_expr ()
{

      TIntValueExpr * result = new TIntValueExpr;
      storeLocation (result);
      result->value = readNumber ();
      return result;
}

TFltValueExpr * Parser::parse_float_value_expr ()
{

      TFltValueExpr * result = new TFltValueExpr;
      storeLocation (result);
      result->value = readReal ();
      return result;
}

TStrValueExpr * Parser::parse_string_value_expr ()
{

      TStrValueExpr * result = new TStrValueExpr;
      storeLocation (result);
      result->value = readQuotedString ();
      return result;
}

TNilExpr * Parser::parse_nil_expr ()
{

      TNilExpr * result = new TNilExpr;
      storeLocation (result);
      checkSymbol (keyword_nil);
      return result;
}

TStructExpr * Parser::parse_sub_expr ()
{

      TStructExpr * result = new TStructExpr;
      storeLocation (result);
      checkSymbol (LPAREN);
      result->value = parse_expr ();
      checkSymbol (RPAREN);
      return result;
}

TNotExpr * Parser::parse_not_expr ()
{

      TNotExpr * result = new TNotExpr;
      storeLocation (result);
      checkSymbol (keyword_not);
      result->param = parse_factor ();
      return result;
}

TPlusExpr * Parser::parse_plus_expr ()
{

      TPlusExpr * result = new TPlusExpr;
      storeLocation (result);
      checkSymbol (PLUS);
      result->param = parse_factor ();
      return result;
}

TMinusExpr * Parser::parse_minus_expr ()
{

      TMinusExpr * result = new TMinusExpr;
      storeLocation (result);
      checkSymbol (MINUS);
      result->param = parse_factor ();
      return result;
}

TAdrExpr * Parser::parse_adr_expr ()
{

      TAdrExpr * result = new TAdrExpr;
      storeLocation (result);
      checkSymbol (ADDRESS);
      result->param = parse_factor ();
      return result;
}

TSetExpr * Parser::parse_set_expr ()
{

      TSetExpr * result = new TSetExpr;
      storeLocation (result);
      checkSymbol (LBRACKET);
      result->list = parse_elem_sect ();
      checkSymbol (RBRACKET);
      return result;
}

TSuperExpr * Parser::parse_super_expr ()
{

      TSuperExpr * result = new TSuperExpr;
      storeLocation (result);
      checkSymbol (keyword_inherited);
      result->name = readIdent ();
      return result;
}

TStringExpr * Parser::parse_string_type_expr ()
{

      TStringExpr * result = new TStringExpr;
      storeLocation (result);
      checkSymbol (keyword_string);
      checkSymbol (LPAREN);
      result->param = parse_expr ();
      checkSymbol (RPAREN);
      return result;
}

TExpr * Parser::parse_variable ()
{

      TExpr * result = NULL;
      if (isSymbol (identifier))
      {
         result = parse_ident_expr ();
      }
      else if (isSymbol (LPAREN))
      {
         result = parse_sub_expr ();
      }
      else if (isSymbol (keyword_inherited))
      {
         result = parse_super_expr ();
      }
      else {
         stop ("Unexpected token");
      }
      return result;
}

TExpr * Parser::parse_reference ()
{

      TExpr * result = NULL;
      result = parse_variable ();
      while (isSymbol (LBRACKET) || isSymbol (LPAREN) || isSymbol (ARROW) || isSymbol (DOT))
      {
         if (isSymbol (LBRACKET))
         {
            result = parse_index_expr (result);
         }
         else if (isSymbol (LPAREN))
         {
            result = parse_call_expr (result);
         }
         else if (isSymbol (ARROW))
         {
            result = parse_deref_expr (result);
         }
         else if (isSymbol (DOT))
         {
            result = parse_field_expr (result);
         }
         else {
            stop ("Unexpected token");
         }
      }
      return result;
}

TIndexExpr * Parser::parse_index_expr (TExpr * store)
{

      TIndexExpr * result = new TIndexExpr;
      storeLocation (result);
      result->left = store;
      checkSymbol (LBRACKET);
      result->list = parse_index_expr_list ();
      checkSymbol (RBRACKET);
      return result;
}

TCallExpr * Parser::parse_call_expr (TExpr * store)
{

      TCallExpr * result = new TCallExpr;
      storeLocation (result);
      result->func = store;
      checkSymbol (LPAREN);
      result->list = parse_arg_list ();
      checkSymbol (RPAREN);
      return result;
}

TDerefExpr * Parser::parse_deref_expr (TExpr * store)
{

      TDerefExpr * result = new TDerefExpr;
      storeLocation (result);
      result->param = store;
      checkSymbol (ARROW);
      return result;
}

TFieldExpr * Parser::parse_field_expr (TExpr * store)
{

      TFieldExpr * result = new TFieldExpr;
      storeLocation (result);
      result->param = store;
      checkSymbol (DOT);
      result->name = readIdent ();
      on_field_expr (result);
      return result;
}

TExpr * Parser::parse_factor ()
{

      TExpr * result = NULL;
      if (isSymbol (number))
      {
         result = parse_int_value_expr ();
      }
      else if (isSymbol (real_number))
      {
         result = parse_float_value_expr ();
      }
      else if (isSymbol (string_literal))
      {
         result = parse_string_value_expr ();
      }
      else if (isSymbol (keyword_not))
      {
         result = parse_not_expr ();
      }
      else if (isSymbol (PLUS))
      {
         result = parse_plus_expr ();
      }
      else if (isSymbol (MINUS))
      {
         result = parse_minus_expr ();
      }
      else if (isSymbol (ADDRESS))
      {
         result = parse_adr_expr ();
      }
      else if (isSymbol (keyword_nil))
      {
         result = parse_nil_expr ();
      }
      else if (isSymbol (LBRACKET))
      {
         result = parse_set_expr ();
      }
      else if (isSymbol (keyword_string) && test_1 ())
      {
         result = parse_string_type_expr ();
      }
      else if (isSymbol (identifier) || isSymbol (LPAREN) || isSymbol (keyword_inherited))
      {
         result = parse_reference ();
      }
      else {
         stop ("Unexpected token");
      }
      return result;
}

TExpr * Parser::parse_term ()
{

      TExpr * result = NULL;
      result = parse_factor ();
      while (isSymbol (STAR) || isSymbol (SLASH) || isSymbol (keyword_div) || isSymbol (keyword_mod) || isSymbol (keyword_shl) || isSymbol (keyword_shr) || isSymbol (keyword_and) || isSymbol (keyword_as))
      {
         TExpr * store = result;
         TTermExpr * result0 = new TTermExpr;
         storeLocation (result0);
         result0->left = store;
         result = result0;
         if (isSymbol (STAR))
         {
            checkSymbol (STAR);
            result0->fce = MulExp;
         }
         else if (isSymbol (SLASH))
         {
            checkSymbol (SLASH);
            result0->fce = RDivExp;
         }
         else if (isSymbol (keyword_div))
         {
            checkSymbol (keyword_div);
            result0->fce = DivExp;
         }
         else if (isSymbol (keyword_mod))
         {
            checkSymbol (keyword_mod);
            result0->fce = ModExp;
         }
         else if (isSymbol (keyword_shl))
         {
            checkSymbol (keyword_shl);
            result0->fce = ShlExp;
         }
         else if (isSymbol (keyword_shr))
         {
            checkSymbol (keyword_shr);
            result0->fce = ShrExp;
         }
         else if (isSymbol (keyword_and))
         {
            checkSymbol (keyword_and);
            result0->fce = AndExp;
         }
         else if (isSymbol (keyword_as))
         {
            checkSymbol (keyword_as);
            result0->fce = AsExp;
         }
         else {
            stop ("Unexpected token");
         }
         result0->right = parse_factor ();
      }
      return result;
}

TExpr * Parser::parse_simple_expr ()
{

      TExpr * result = NULL;
      result = parse_term ();
      while (isSymbol (PLUS) || isSymbol (MINUS) || isSymbol (keyword_or) || isSymbol (keyword_xor))
      {
         TExpr * store = result;
         TSimpleExpr * result0 = new TSimpleExpr;
         storeLocation (result0);
         result0->left = store;
         result = result0;
         if (isSymbol (PLUS))
         {
            checkSymbol (PLUS);
            result0->fce = AddExp;
         }
         else if (isSymbol (MINUS))
         {
            checkSymbol (MINUS);
            result0->fce = SubExp;
         }
         else if (isSymbol (keyword_or))
         {
            checkSymbol (keyword_or);
            result0->fce = OrExp;
         }
         else if (isSymbol (keyword_xor))
         {
            checkSymbol (keyword_xor);
            result0->fce = XorExp;
         }
         else {
            stop ("Unexpected token");
         }
         result0->right = parse_term ();
      }
      return result;
}

TExpr * Parser::parse_expr ()
{

      TExpr * result = NULL;
      result = parse_simple_expr ();
      if (isSymbol (EQUAL) || isSymbol (UNEQUAL) || isSymbol (LESS) || isSymbol (GREATER) || isSymbol (LESS_OR_EQUAL) || isSymbol (GREATER_OR_EQUAL) || isSymbol (keyword_in) || isSymbol (keyword_is))
      {
         TExpr * store = result;
         TCompleteExpr * result0 = new TCompleteExpr;
         storeLocation (result0);
         result0->left = store;
         result = result0;
         if (isSymbol (EQUAL))
         {
            checkSymbol (EQUAL);
            result0->fce = EqExp;
         }
         else if (isSymbol (UNEQUAL))
         {
            checkSymbol (UNEQUAL);
            result0->fce = NeExp;
         }
         else if (isSymbol (LESS))
         {
            checkSymbol (LESS);
            result0->fce = LtExp;
         }
         else if (isSymbol (GREATER))
         {
            checkSymbol (GREATER);
            result0->fce = GtExp;
         }
         else if (isSymbol (LESS_OR_EQUAL))
         {
            checkSymbol (LESS_OR_EQUAL);
            result0->fce = LeExp;
         }
         else if (isSymbol (GREATER_OR_EQUAL))
         {
            checkSymbol (GREATER_OR_EQUAL);
            result0->fce = GeExp;
         }
         else if (isSymbol (keyword_in))
         {
            checkSymbol (keyword_in);
            result0->fce = InExp;
         }
         else if (isSymbol (keyword_is))
         {
            checkSymbol (keyword_is);
            result0->fce = IsExp;
         }
         else {
            stop ("Unexpected token");
         }
         result0->right = parse_simple_expr ();
      }
      return result;
}

TGotoStat * Parser::parse_goto_stat ()
{

      TGotoStat * result = new TGotoStat;
      storeLocation (result);
      checkSymbol (keyword_goto);
      result->goto_lab = parse_label_ident ();
      return result;
}

TBlockStat * Parser::parse_begin_stat ()
{

      TBlockStat * result = new TBlockStat;
      storeLocation (result);
      checkSymbol (keyword_begin);
      result->body_seq = parse_stat_list ();
      checkSymbol (keyword_end);
      return result;
}

TStatSeq * Parser::parse_stat_list ()
{

      TStatSeq * result = new TStatSeq;
      storeLocation (result);
      result->items.push_back (parse_stat ());
      while (isSymbol (SEMICOLON))
      {
         checkSymbol (SEMICOLON);
         result->items.push_back (parse_stat ());
      }
      return result;
}

TStat * Parser::parse_inner_stat ()
{

      TStat * result = NULL;
      result = parse_stat ();
      return result;
}

TIfStat * Parser::parse_if_stat ()
{

      TIfStat * result = new TIfStat;
      storeLocation (result);
      checkSymbol (keyword_if);
      result->cond_expr = parse_expr ();
      checkSymbol (keyword_then);
      result->then_stat = parse_inner_stat ();
      if (isSymbol (keyword_else))
      {
         checkSymbol (keyword_else);
         result->else_stat = parse_inner_stat ();
      }
      return result;
}

TCaseStat * Parser::parse_case_stat ()
{

      TCaseStat * result = new TCaseStat;
      storeLocation (result);
      checkSymbol (keyword_case);
      result->case_expr = parse_expr ();
      checkSymbol (keyword_of);
      result->case_list = parse_case_sect ();
      if (isSymbol (keyword_else))
      {
         checkSymbol (keyword_else);
         result->else_seq = parse_stat_list ();
      }
      checkSymbol (keyword_end);
      return result;
}

TCaseSect * Parser::parse_case_sect ()
{

      TCaseSect * result = new TCaseSect;
      storeLocation (result);
      result->items.push_back (parse_case_item ());
      while (isSymbol (SEMICOLON))
      {
         checkSymbol (SEMICOLON);
         result->items.push_back (parse_case_item ());
      }
      return result;
}

TCaseItem * Parser::parse_case_item ()
{

      TCaseItem * result = new TCaseItem;
      storeLocation (result);
      result->sel_list = parse_elem_sect ();
      checkSymbol (COLON);
      result->sel_stat = parse_inner_stat ();
      return result;
}

TWhileStat * Parser::parse_while_stat ()
{

      TWhileStat * result = new TWhileStat;
      storeLocation (result);
      checkSymbol (keyword_while);
      result->cond_expr = parse_expr ();
      checkSymbol (keyword_do);
      result->body_stat = parse_inner_stat ();
      return result;
}

TRepeatStat * Parser::parse_repeat_stat ()
{

      TRepeatStat * result = new TRepeatStat;
      storeLocation (result);
      checkSymbol (keyword_repeat);
      result->body_seq = parse_stat_list ();
      checkSymbol (keyword_until);
      result->until_expr = parse_expr ();
      return result;
}

TForStat * Parser::parse_for_stat ()
{

      TForStat * result = new TForStat;
      storeLocation (result);
      checkSymbol (keyword_for);
      result->var_expr = parse_variable ();
      checkSymbol (ASSIGN);
      result->from_expr = parse_expr ();
      if (isSymbol (keyword_to))
      {
         checkSymbol (keyword_to);
         result->incr = true;
      }
      else if (isSymbol (keyword_downto))
      {
         checkSymbol (keyword_downto);
         result->incr = false;
      }
      else {
         stop ("Unexpected token");
      }
      result->to_expr = parse_expr ();
      checkSymbol (keyword_do);
      result->body_stat = parse_inner_stat ();
      return result;
}

TWithStat * Parser::parse_with_stat ()
{

      TWithStat * result = new TWithStat;
      storeLocation (result);
      checkSymbol (keyword_with);
      result->with_list = parse_with_sect ();
      checkSymbol (keyword_do);
      result->body_stat = parse_inner_stat ();
      return result;
}

TWithSect * Parser::parse_with_sect ()
{

      TWithSect * result = new TWithSect;
      storeLocation (result);
      result->items.push_back (parse_with_item ());
      while (isSymbol (COMMA))
      {
         checkSymbol (COMMA);
         result->items.push_back (parse_with_item ());
      }
      return result;
}

TWithItem * Parser::parse_with_item ()
{

      TWithItem * result = new TWithItem;
      storeLocation (result);
      result->expr = parse_variable ();
      return result;
}

TRaiseStat * Parser::parse_raise_stat ()
{

      TRaiseStat * result = new TRaiseStat;
      storeLocation (result);
      checkSymbol (keyword_raise);
      if (testSymbols (set_4))
      {
         result->raise_expr = parse_expr ();
      }
      return result;
}

TTryStat * Parser::parse_try_stat ()
{

      TTryStat * result = new TTryStat;
      storeLocation (result);
      checkSymbol (keyword_try);
      result->body_seq = parse_stat_list ();
      if (isSymbol (keyword_finally))
      {
         result->finally_branch = parse_finally_part ();
      }
      else if (isSymbol (keyword_except))
      {
         result->except_branch = parse_except_part ();
      }
      else {
         stop ("Unexpected token");
      }
      checkSymbol (keyword_end);
      return result;
}

TFinallyPart * Parser::parse_finally_part ()
{

      TFinallyPart * result = new TFinallyPart;
      storeLocation (result);
      checkSymbol (keyword_finally);
      result->finally_seq = parse_stat_list ();
      return result;
}

TExceptPart * Parser::parse_except_part ()
{

      TExceptPart * result = new TExceptPart;
      storeLocation (result);
      checkSymbol (keyword_except);
      if (isSymbol (keyword_on))
      {
         result->on_list = parse_on_sect ();
         if (isSymbol (keyword_else))
         {
            checkSymbol (keyword_else);
            result->else_seq = parse_stat_list ();
         }
      }
      else if (testSymbols (set_5))
      {
         result->else_seq = parse_stat_list ();
      }
      else {
         stop ("Unexpected token");
      }
      return result;
}

TOnSect * Parser::parse_on_sect ()
{

      TOnSect * result = new TOnSect;
      storeLocation (result);
      result->items.push_back (parse_on_item ());
      while (isSymbol (SEMICOLON))
      {
         checkSymbol (SEMICOLON);
         result->items.push_back (parse_on_item ());
      }
      if (isSymbol (SEMICOLON))
      {
         checkSymbol (SEMICOLON);
         result->semicolon = true;
      }
      return result;
}

TOnItem * Parser::parse_on_item ()
{

      TOnItem * result = new TOnItem;
      storeLocation (result);
      checkSymbol (keyword_on);
      if (isSymbol (identifier))
      {
         result->on_ident = readIdent ();
         checkSymbol (COLON);
      }
      result->on_type = parse_type ();
      checkSymbol (keyword_do);
      result->body_stat = parse_inner_stat ();
      return result;
}

TEmptyStat * Parser::parse_empty_stat ()
{

      TEmptyStat * result = new TEmptyStat;
      storeLocation (result);
      return result;
}

TStat * Parser::parse_simple_stat ()
{

      TStat * result = NULL;
      TExpr * result0 = parse_expr ();
      if (isSymbol (ASSIGN))
      {
         result = parse_assign_stat (result0);
      }
      else
      {
         result = parse_call_stat (result0);
      }
      return result;
}

TAssignStat * Parser::parse_assign_stat (TExpr * store)
{

      TAssignStat * result = new TAssignStat;
      storeLocation (result);
      result->left_expr = store;
      checkSymbol (ASSIGN);
      result->right_expr = parse_expr ();
      return result;
}

TCallStat * Parser::parse_call_stat (TExpr * store)
{

      TCallStat * result = new TCallStat;
      storeLocation (result);
      result->call_expr = store;
      return result;
}

TLabeledTStat * Parser::parse_labeled_stat ()
{

      TLabeledTStat * result = new TLabeledTStat;
      storeLocation (result);
      result->lab = parse_label_ident ();
      checkSymbol (COLON);
      result->body = parse_stat ();
      return result;
}

TStat * Parser::parse_stat ()
{

      TStat * result = NULL;
      if (isSymbol (identifier) && test_2 ())
      {
         result = parse_labeled_stat ();
      }
      else if (testSymbols (set_4))
      {
         result = parse_simple_stat ();
      }
      else if (isSymbol (keyword_goto))
      {
         result = parse_goto_stat ();
      }
      else if (isSymbol (keyword_begin))
      {
         result = parse_begin_stat ();
      }
      else if (isSymbol (keyword_if))
      {
         result = parse_if_stat ();
      }
      else if (isSymbol (keyword_case))
      {
         result = parse_case_stat ();
      }
      else if (isSymbol (keyword_while))
      {
         result = parse_while_stat ();
      }
      else if (isSymbol (keyword_repeat))
      {
         result = parse_repeat_stat ();
      }
      else if (isSymbol (keyword_for))
      {
         result = parse_for_stat ();
      }
      else if (isSymbol (keyword_with))
      {
         result = parse_with_stat ();
      }
      else if (isSymbol (keyword_raise))
      {
         result = parse_raise_stat ();
      }
      else if (isSymbol (keyword_try))
      {
         result = parse_try_stat ();
      }
      else
      {
         result = parse_empty_stat ();
      }
      return result;
}

TParamIdent * Parser::parse_param_ident ()
{

      TParamIdent * result = new TParamIdent;
      storeLocation (result);
      result->name = readIdent ();
      on_param (result);
      return result;
}

TParamItem * Parser::parse_param_item ()
{

      TParamItem * result = new TParamItem;
      storeLocation (result);
      if (isSymbol (keyword_var))
      {
         checkSymbol (keyword_var);
         result->mode = VarParam;
      }
      else if (isSymbol (keyword_const))
      {
         checkSymbol (keyword_const);
         result->mode = ConstParam;
      }
      else if (isSymbol (keyword_out))
      {
         checkSymbol (keyword_out);
         result->mode = OutParam;
      }
      else
      {
         result->mode = ValueParam;
      }
      result->items.push_back (parse_param_ident ());
      while (isSymbol (COMMA))
      {
         checkSymbol (COMMA);
         result->items.push_back (parse_param_ident ());
      }
      if (isSymbol (COLON))
      {
         checkSymbol (COLON);
         result->typ = parse_param_type ();
         if (isSymbol (EQUAL))
         {
            checkSymbol (EQUAL);
            result->ini = parse_expr ();
         }
      }
      add_param (result);
      return result;
}

TParamSect * Parser::parse_formal_param_list ()
{

      TParamSect * result = new TParamSect;
      storeLocation (result);
      if (isSymbol (LPAREN))
      {
         checkSymbol (LPAREN);
         result->items.push_back (parse_param_item ());
         while (isSymbol (SEMICOLON))
         {
            checkSymbol (SEMICOLON);
            result->items.push_back (parse_param_item ());
         }
         checkSymbol (RPAREN);
      }
      return result;
}

TParamSect * Parser::parse_property_param_list ()
{

      TParamSect * result = new TParamSect;
      storeLocation (result);
      checkSymbol (LBRACKET);
      result->items.push_back (parse_param_item ());
      while (isSymbol (SEMICOLON))
      {
         checkSymbol (SEMICOLON);
         result->items.push_back (parse_param_item ());
      }
      checkSymbol (RBRACKET);
      return result;
}

TClassType * Parser::parse_class_type ()
{

      TClassType * result = new TClassType;
      storeLocation (result);
      open_class (result);
      checkSymbol (keyword_class);
      if (isSymbol (LPAREN))
      {
         checkSymbol (LPAREN);
         result->parent = parse_ifc_type ();
         if (isSymbol (COMMA))
         {
            checkSymbol (COMMA);
            result->ifc_list = parse_interface_sect ();
         }
         checkSymbol (RPAREN);
      }
      result->components = parse_components_sect ();
      checkSymbol (keyword_end);
      close_class (result);
      return result;
}

TInterfaceType * Parser::parse_interface_type ()
{

      TInterfaceType * result = new TInterfaceType;
      storeLocation (result);
      open_interface (result);
      checkSymbol (keyword_interface);
      if (isSymbol (LPAREN))
      {
         checkSymbol (LPAREN);
         result->ifc_list = parse_interface_sect ();
         checkSymbol (RPAREN);
      }
      result->components = parse_components_sect ();
      checkSymbol (keyword_end);
      close_interface (result);
      return result;
}

TInterfaceSect * Parser::parse_interface_sect ()
{

      TInterfaceSect * result = new TInterfaceSect;
      storeLocation (result);
      result->items.push_back (parse_interface_item ());
      while (isSymbol (COMMA))
      {
         checkSymbol (COMMA);
         result->items.push_back (parse_interface_item ());
      }
      return result;
}

TIntefaceItem * Parser::parse_interface_item ()
{

      TIntefaceItem * result = new TIntefaceItem;
      storeLocation (result);
      result->ifc = parse_ifc_type ();
      return result;
}

TComponetsSect * Parser::parse_components_sect ()
{

      TComponetsSect * result = new TComponetsSect;
      storeLocation (result);
      result->items.push_back (parse_components_first_item ());
      while (testSymbols (set_6))
      {
         result->items.push_back (parse_components_item ());
      }
      return result;
}

TComponentsItem * Parser::parse_components_item ()
{

      TComponentsItem * result = new TComponentsItem;
      storeLocation (result);
      if (isSymbol (keyword_private))
      {
         checkSymbol (keyword_private);
         result->acs = PrivateAccess;
      }
      else if (isSymbol (keyword_protected))
      {
         checkSymbol (keyword_protected);
         result->acs = ProtectedAccess;
      }
      else if (isSymbol (keyword_public))
      {
         checkSymbol (keyword_public);
         result->acs = PublicAccess;
      }
      else if (isSymbol (keyword_published))
      {
         checkSymbol (keyword_published);
         result->acs = PublishedAccess;
      }
      else if (isSymbol (keyword_automated))
      {
         checkSymbol (keyword_automated);
         result->acs = AutomatedAccess;
      }
      else {
         stop ("Unexpected token");
      }
      result->members = parse_member_sect ();
      return result;
}

TComponentsItem * Parser::parse_components_first_item ()
{

      TComponentsItem * result = new TComponentsItem;
      storeLocation (result);
      result->acs = PublicAccess;
      result->members = parse_member_sect ();
      return result;
}

TDeclGroup * Parser::parse_member_sect ()
{

      TDeclGroup * result = new TDeclGroup;
      storeLocation (result);
      while (testSymbols (set_7))
      {
         result->items.push_back (parse_member_decl ());
      }
      return result;
}

TDeclSect * Parser::parse_member_decl ()
{

      TDeclSect * result = NULL;
      if (isSymbol (identifier))
      {
         result = parse_field_decl ();
      }
      else if (testSymbols (set_8))
      {
         result = parse_method_decl ();
      }
      else if (isSymbol (keyword_property))
      {
         result = parse_property_decl ();
      }
      else {
         stop ("Unexpected token");
      }
      return result;
}

TFieldItem * Parser::parse_field_ident ()
{

      TFieldItem * result = new TFieldItem;
      storeLocation (result);
      result->name = readIdent ();
      on_field (result);
      return result;
}

TFieldDecl * Parser::parse_field_decl ()
{

      TFieldDecl * result = new TFieldDecl;
      storeLocation (result);
      result->items.push_back (parse_field_ident ());
      while (isSymbol (COMMA))
      {
         checkSymbol (COMMA);
         result->items.push_back (parse_field_ident ());
      }
      checkSymbol (COLON);
      result->typ = parse_type ();
      checkSymbol (SEMICOLON);
      add_field (result);
      return result;
}

TProcDecl * Parser::parse_method_decl ()
{

      TProcDecl * result = new TProcDecl;
      storeLocation (result);
      open_proc (result);
      parse_proc_head (result);
      while (isSymbol (keyword_virtual) || isSymbol (keyword_dynamic) || isSymbol (keyword_override) || isSymbol (keyword_abstract))
      {
         if (isSymbol (keyword_virtual))
         {
            checkSymbol (keyword_virtual);
            result->a_virtual = true;
            checkSymbol (SEMICOLON);
         }
         else if (isSymbol (keyword_dynamic))
         {
            checkSymbol (keyword_dynamic);
            result->a_dynamic = true;
            checkSymbol (SEMICOLON);
         }
         else if (isSymbol (keyword_override))
         {
            checkSymbol (keyword_override);
            result->a_override = true;
            checkSymbol (SEMICOLON);
         }
         else if (isSymbol (keyword_abstract))
         {
            checkSymbol (keyword_abstract);
            result->a_abstract = true;
            checkSymbol (SEMICOLON);
         }
         else {
            stop ("Unexpected token");
         }
      }
      close_proc (result);
      return result;
}

TPropertyDecl * Parser::parse_property_decl ()
{

      TPropertyDecl * result = new TPropertyDecl;
      storeLocation (result);
      checkSymbol (keyword_property);
      result->name = readIdent ();
      if (isSymbol (LBRACKET))
      {
         result->param_list = parse_property_param_list ();
      }
      if (isSymbol (COLON))
      {
         checkSymbol (COLON);
         result->typ = parse_result_type ();
      }
      if (isSymbol (keyword_read))
      {
         checkSymbol (keyword_read);
         result->a_read = parse_expr ();
      }
      if (isSymbol (keyword_write))
      {
         checkSymbol (keyword_write);
         result->a_write = parse_expr ();
      }
      if (isSymbol (keyword_stored))
      {
         checkSymbol (keyword_stored);
         result->a_stored = true;
      }
      if (isSymbol (keyword_default))
      {
         checkSymbol (keyword_default);
         result->a_default = true;
      }
      if (isSymbol (keyword_nodefault))
      {
         checkSymbol (keyword_nodefault);
         result->a_nodefault = true;
      }
      if (isSymbol (keyword_implements))
      {
         checkSymbol (keyword_implements);
         result->a_implements = parse_interface_sect ();
      }
      if (isSymbol (SEMICOLON))
      {
         checkSymbol (SEMICOLON);
         checkSymbol (keyword_default);
         result->a_def_array = true;
      }
      checkSymbol (SEMICOLON);
      return result;
}

TEnumType * Parser::parse_enum_type ()
{

      TEnumType * result = new TEnumType;
      storeLocation (result);
      simple_type (result);
      checkSymbol (LPAREN);
      result->elements = parse_enum_sect ();
      checkSymbol (RPAREN);
      return result;
}

TEnumSect * Parser::parse_enum_sect ()
{

      TEnumSect * result = new TEnumSect;
      storeLocation (result);
      result->items.push_back (parse_enum_item ());
      while (isSymbol (COMMA))
      {
         checkSymbol (COMMA);
         result->items.push_back (parse_enum_item ());
      }
      return result;
}

TEnumItem * Parser::parse_enum_item ()
{

      TEnumItem * result = new TEnumItem;
      storeLocation (result);
      result->name = readIdent ();
      return result;
}

TStringType * Parser::parse_string_type ()
{

      TStringType * result = new TStringType;
      storeLocation (result);
      simple_type (result);
      checkSymbol (keyword_string);
      if (isSymbol (LBRACKET))
      {
         checkSymbol (LBRACKET);
         result->lim = parse_expr ();
         checkSymbol (RBRACKET);
      }
      return result;
}

TArrayType * Parser::parse_array_type ()
{

      TArrayType * result = new TArrayType;
      storeLocation (result);
      simple_type (result);
      checkSymbol (keyword_array);
      if (isSymbol (LBRACKET))
      {
         checkSymbol (LBRACKET);
         result->index_list = parse_index_type_sect ();
         checkSymbol (RBRACKET);
      }
      checkSymbol (keyword_of);
      result->elem = parse_type ();
      return result;
}

TIndexTypeSect * Parser::parse_index_type_sect ()
{

      TIndexTypeSect * result = new TIndexTypeSect;
      storeLocation (result);
      result->items.push_back (parse_index_type_item ());
      while (isSymbol (COMMA))
      {
         checkSymbol (COMMA);
         result->items.push_back (parse_index_type_item ());
      }
      return result;
}

TIndexTypeItem * Parser::parse_index_type_item ()
{

      TIndexTypeItem * result = new TIndexTypeItem;
      storeLocation (result);
      result->index = parse_type ();
      return result;
}

TRecordType * Parser::parse_record_type ()
{

      TRecordType * result = new TRecordType;
      storeLocation (result);
      simple_type (result);
      if (isSymbol (keyword_packed))
      {
         checkSymbol (keyword_packed);
         result->a_packed = true;
      }
      checkSymbol (keyword_record);
      result->fields = parse_field_sect ();
      checkSymbol (keyword_end);
      return result;
}

TFieldDeclGroup * Parser::parse_field_sect ()
{

      TFieldDeclGroup * result = new TFieldDeclGroup;
      storeLocation (result);
      while (isSymbol (identifier))
      {
         result->items.push_back (parse_field_decl ());
      }
      return result;
}

TPointerType * Parser::parse_pointer_type ()
{

      TPointerType * result = new TPointerType;
      storeLocation (result);
      simple_type (result);
      checkSymbol (ARROW);
      result->elem = parse_type ();
      return result;
}

TSetType * Parser::parse_set_type ()
{

      TSetType * result = new TSetType;
      storeLocation (result);
      simple_type (result);
      checkSymbol (keyword_set);
      checkSymbol (keyword_of);
      result->elem = parse_type ();
      return result;
}

TFileType * Parser::parse_file_type ()
{

      TFileType * result = new TFileType;
      storeLocation (result);
      simple_type (result);
      checkSymbol (keyword_file);
      if (isSymbol (keyword_of))
      {
         checkSymbol (keyword_of);
         result->elem = parse_type ();
      }
      return result;
}

TClassOfType * Parser::parse_class_of_type ()
{

      TClassOfType * result = new TClassOfType;
      storeLocation (result);
      simple_type (result);
      checkSymbol (keyword_class);
      checkSymbol (keyword_of);
      result->elem = parse_type ();
      return result;
}

TProcType * Parser::parse_proc_type ()
{

      TProcType * result = new TProcType;
      storeLocation (result);
      simple_type (result);
      if (isSymbol (keyword_procedure))
      {
         checkSymbol (keyword_procedure);
         result->style = ProcedureStyle;
      }
      else if (isSymbol (keyword_function))
      {
         checkSymbol (keyword_function);
         result->style = FunctionStyle;
      }
      else {
         stop ("Unexpected token");
      }
      result->param_list = parse_formal_param_list ();
      if (isSymbol (COLON))
      {
         checkSymbol (COLON);
         result->answer = parse_result_type ();
      }
      if (isSymbol (keyword_of))
      {
         checkSymbol (keyword_of);
         checkSymbol (keyword_object);
         result->of_object = true;
      }
      if (isSymbol (keyword_register) || isSymbol (keyword_pascal) || isSymbol (keyword_cdecl) || isSymbol (keyword_stdcall) || isSymbol (keyword_safecall))
      {
         if (isSymbol (keyword_register))
         {
            checkSymbol (keyword_register);
            result->call_conv = RegisterCall;
         }
         else if (isSymbol (keyword_pascal))
         {
            checkSymbol (keyword_pascal);
            result->call_conv = PascalCall;
         }
         else if (isSymbol (keyword_cdecl))
         {
            checkSymbol (keyword_cdecl);
            result->call_conv = CdeclCall;
         }
         else if (isSymbol (keyword_stdcall))
         {
            checkSymbol (keyword_stdcall);
            result->call_conv = StdcallCall;
         }
         else if (isSymbol (keyword_safecall))
         {
            checkSymbol (keyword_safecall);
            result->call_conv = SafecallCall;
         }
         else {
            stop ("Unexpected token");
         }
      }
      return result;
}

TSubrangeType * Parser::parse_range_type ()
{

      TSubrangeType * result = new TSubrangeType;
      storeLocation (result);
      simple_type (result);
      result->low = parse_simple_expr ();
      checkSymbol (RANGE);
      result->high = parse_simple_expr ();
      return result;
}

TAliasType * Parser::parse_alias_type ()
{

      TAliasType * result = new TAliasType;
      storeLocation (result);
      simple_type (result);
      result->alias_name = parse_qualified_name ();
      return result;
}

TType * Parser::parse_type ()
{

      TType * result = NULL;
      if (isSymbol (keyword_string))
      {
         result = parse_string_type ();
      }
      else if (isSymbol (keyword_array))
      {
         result = parse_array_type ();
      }
      else if (isSymbol (keyword_set))
      {
         result = parse_set_type ();
      }
      else if (isSymbol (keyword_file))
      {
         result = parse_file_type ();
      }
      else if (isSymbol (keyword_packed) || isSymbol (keyword_record))
      {
         result = parse_record_type ();
      }
      else if (isSymbol (keyword_class))
      {
         result = parse_class_type ();
      }
      else if (isSymbol (keyword_class))
      {
         result = parse_class_of_type ();
      }
      else if (isSymbol (keyword_interface))
      {
         result = parse_interface_type ();
      }
      else if (isSymbol (keyword_function) || isSymbol (keyword_procedure))
      {
         result = parse_proc_type ();
      }
      else if (isSymbol (ARROW))
      {
         result = parse_pointer_type ();
      }
      else if (testSymbols (set_4) && test_3 ())
      {
         result = parse_range_type ();
      }
      else if (isSymbol (LPAREN) && test_4 ())
      {
         result = parse_enum_type ();
      }
      else if (isSymbol (identifier))
      {
         result = parse_alias_type ();
      }
      else {
         stop ("Unexpected token");
      }
      return result;
}

TLabelDecl * Parser::parse_label_decl ()
{

      TLabelDecl * result = new TLabelDecl;
      storeLocation (result);
      result->name = parse_label_ident ();
      return result;
}

TLabelSect * Parser::parse_label_sect ()
{

      TLabelSect * result = new TLabelSect;
      storeLocation (result);
      checkSymbol (keyword_label);
      result->items.push_back (parse_label_decl ());
      while (isSymbol (COMMA))
      {
         checkSymbol (COMMA);
         result->items.push_back (parse_label_decl ());
      }
      checkSymbol (SEMICOLON);
      return result;
}

TConstDecl * Parser::parse_const_decl ()
{

      TConstDecl * result = new TConstDecl;
      storeLocation (result);
      result->name = readIdent ();
      on_const (result);
      if (isSymbol (COLON))
      {
         checkSymbol (COLON);
         result->typ = parse_type ();
      }
      checkSymbol (EQUAL);
      result->val = parse_expr ();
      checkSymbol (SEMICOLON);
      add_const (result);
      return result;
}

TConstSect * Parser::parse_const_sect ()
{

      TConstSect * result = new TConstSect;
      storeLocation (result);
      checkSymbol (keyword_const);
      result->items.push_back (parse_const_decl ());
      while (isSymbol (identifier))
      {
         result->items.push_back (parse_const_decl ());
      }
      return result;
}

TTypeDecl * Parser::parse_type_decl ()
{

      TTypeDecl * result = new TTypeDecl;
      storeLocation (result);
      result->name = readIdent ();
      on_type (result);
      checkSymbol (EQUAL);
      result->typ = parse_type ();
      checkSymbol (SEMICOLON);
      add_type (result);
      return result;
}

TTypeSect * Parser::parse_type_sect ()
{

      TTypeSect * result = new TTypeSect;
      storeLocation (result);
      checkSymbol (keyword_type);
      result->items.push_back (parse_type_decl ());
      while (isSymbol (identifier))
      {
         result->items.push_back (parse_type_decl ());
      }
      return result;
}

TVarItem * Parser::parse_var_item ()
{

      TVarItem * result = new TVarItem;
      storeLocation (result);
      result->name = readIdent ();
      on_var (result);
      return result;
}

TVarDecl * Parser::parse_var_decl ()
{

      TVarDecl * result = new TVarDecl;
      storeLocation (result);
      result->items.push_back (parse_var_item ());
      while (isSymbol (COMMA))
      {
         checkSymbol (COMMA);
         result->items.push_back (parse_var_item ());
      }
      checkSymbol (COLON);
      result->typ = parse_type ();
      if (isSymbol (EQUAL))
      {
         checkSymbol (EQUAL);
         result->ini = parse_expr ();
      }
      checkSymbol (SEMICOLON);
      add_var (result);
      return result;
}

TVarSect * Parser::parse_var_sect ()
{

      TVarSect * result = new TVarSect;
      storeLocation (result);
      checkSymbol (keyword_var);
      result->items.push_back (parse_var_decl ());
      while (isSymbol (identifier))
      {
         result->items.push_back (parse_var_decl ());
      }
      return result;
}

TProcDecl * Parser::parse_proc_head (TProcDecl * result)
{

      if (isSymbol (keyword_class))
      {
         checkSymbol (keyword_class);
         result->a_static = true;
      }
      if (isSymbol (keyword_procedure))
      {
         checkSymbol (keyword_procedure);
         result->style = ProcedureStyle;
      }
      else if (isSymbol (keyword_function))
      {
         checkSymbol (keyword_function);
         result->style = FunctionStyle;
      }
      else if (isSymbol (keyword_constructor))
      {
         checkSymbol (keyword_constructor);
         result->style = ConstructorStyle;
      }
      else if (isSymbol (keyword_destructor))
      {
         checkSymbol (keyword_destructor);
         result->style = DestructorStyle;
      }
      else {
         stop ("Unexpected token");
      }
      result->proc_name = parse_qualified_name ();
      on_proc (result);
      result->param_list = parse_formal_param_list ();
      if (isSymbol (COLON))
      {
         checkSymbol (COLON);
         result->answer = parse_result_type ();
      }
      checkSymbol (SEMICOLON);
      return result;
}

TProcDecl * Parser::parse_proc_decl ()
{

      TProcDecl * result = new TProcDecl;
      storeLocation (result);
      open_proc (result);
      parse_proc_head (result);
      if (isSymbol (keyword_forward))
      {
         checkSymbol (keyword_forward);
         result->a_forward = true;
      }
      else if (isSymbol (keyword_external))
      {
         parse_proc_external (result);
         result->external_spec = true;
      }
      else if (testSymbols (set_11))
      {
         if (isSymbol (keyword_inline))
         {
            checkSymbol (keyword_inline);
            checkSymbol (SEMICOLON);
            result->a_inline = true;
         }
         result->local = parse_decl_part ();
         on_begin_proc (result);
         checkSymbol (keyword_begin);
         result->body = parse_stat_list ();
         on_end_proc (result);
         checkSymbol (keyword_end);
         on_tail_proc (result);
      }
      else {
         stop ("Unexpected token");
      }
      checkSymbol (SEMICOLON);
      close_proc (result);
      return result;
}

TProcDecl * Parser::parse_proc_external (TProcDecl * result)
{

      checkSymbol (keyword_external);
      result->a_external = true;
      if (testSymbols (set_4))
      {
         result->a_lib = parse_expr ();
      }
      checkSymbol (SEMICOLON);
      return result;
}

TProcDecl * Parser::parse_proc_intf_decl ()
{

      TProcDecl * result = new TProcDecl;
      storeLocation (result);
      open_proc (result);
      parse_proc_head (result);
      if (isSymbol (keyword_inline))
      {
         checkSymbol (keyword_inline);
         checkSymbol (SEMICOLON);
         result->a_inline = true;
      }
      if (isSymbol (keyword_external))
      {
         parse_proc_external (result);
         result->external_spec = true;
      }
      close_proc (result);
      return result;
}

TDeclSect * Parser::parse_intf_decl ()
{

      TDeclSect * result = NULL;
      if (isSymbol (keyword_const))
      {
         result = parse_const_sect ();
      }
      else if (isSymbol (keyword_type))
      {
         result = parse_type_sect ();
      }
      else if (isSymbol (keyword_var))
      {
         result = parse_var_sect ();
      }
      else if (testSymbols (set_8))
      {
         result = parse_proc_intf_decl ();
      }
      else {
         stop ("Unexpected token");
      }
      return result;
}

TDeclGroup * Parser::parse_intf_decl_part ()
{

      TDeclGroup * result = new TDeclGroup;
      storeLocation (result);
      while (testSymbols (set_12))
      {
         result->items.push_back (parse_intf_decl ());
      }
      return result;
}

TDeclSect * Parser::parse_decl ()
{

      TDeclSect * result = NULL;
      if (isSymbol (keyword_label))
      {
         result = parse_label_sect ();
      }
      else if (isSymbol (keyword_const))
      {
         result = parse_const_sect ();
      }
      else if (isSymbol (keyword_type))
      {
         result = parse_type_sect ();
      }
      else if (isSymbol (keyword_var))
      {
         result = parse_var_sect ();
      }
      else if (testSymbols (set_8))
      {
         result = parse_proc_decl ();
      }
      else {
         stop ("Unexpected token");
      }
      return result;
}

TDeclGroup * Parser::parse_decl_part ()
{

      TDeclGroup * result = new TDeclGroup;
      storeLocation (result);
      while (testSymbols (set_13))
      {
         result->items.push_back (parse_decl ());
      }
      return result;
}

TImportItem * Parser::parse_import_item ()
{

      TImportItem * result = new TImportItem;
      storeLocation (result);
      result->name = readIdent ();
      on_import (result);
      if (isSymbol (keyword_in))
      {
         checkSymbol (keyword_in);
         result->path = readQuotedString ();
      }
      return result;
}

TImportSect * Parser::parse_import_sect ()
{

      TImportSect * result = new TImportSect;
      storeLocation (result);
      if (isSymbol (keyword_uses))
      {
         checkSymbol (keyword_uses);
         result->items.push_back (parse_import_item ());
         while (isSymbol (COMMA))
         {
            checkSymbol (COMMA);
            result->items.push_back (parse_import_item ());
         }
         checkSymbol (SEMICOLON);
      }
      return result;
}

TUnitModule * Parser::parse_unit_decl ()
{

      TUnitModule * result = new TUnitModule;
      storeLocation (result);
      open_module (result);
      checkSymbol (keyword_unit);
      result->name = readIdent ();
      on_module (result);
      checkSymbol (SEMICOLON);
      checkSymbol (keyword_interface);
      result->intf_imports = parse_import_sect ();
      result->intf_decl = parse_intf_decl_part ();
      checkSymbol (keyword_implementation);
      result->impl_imports = parse_import_sect ();
      result->impl_decl = parse_decl_part ();
      if (isSymbol (keyword_finalization) || isSymbol (keyword_initialization) || isSymbol (keyword_begin))
      {
         if (isSymbol (keyword_begin))
         {
            checkSymbol (keyword_begin);
            result->init = parse_stat_list ();
         }
         else if (isSymbol (keyword_finalization) || isSymbol (keyword_initialization))
         {
            if (isSymbol (keyword_initialization))
            {
               checkSymbol (keyword_initialization);
               result->init = parse_stat_list ();
            }
            if (isSymbol (keyword_finalization))
            {
               checkSymbol (keyword_finalization);
               result->finish = parse_stat_list ();
            }
            result->no_begin = true;
         }
         else {
            stop ("Unexpected token");
         }
      }
      checkSymbol (keyword_end);
      checkSymbol (DOT);
      close_module (result);
      return result;
}

TProgramModule * Parser::parse_program_decl ()
{

      TProgramModule * result = new TProgramModule;
      storeLocation (result);
      open_module (result);
      checkSymbol (keyword_program);
      result->name = readIdent ();
      on_module (result);
      checkSymbol (SEMICOLON);
      result->impl_imports = parse_import_sect ();
      result->impl_decl = parse_decl_part ();
      checkSymbol (keyword_begin);
      result->init = parse_stat_list ();
      checkSymbol (keyword_end);
      checkSymbol (DOT);
      close_module (result);
      return result;
}

TLibraryModule * Parser::parse_library_decl ()
{

      TLibraryModule * result = new TLibraryModule;
      storeLocation (result);
      open_module (result);
      checkSymbol (keyword_library);
      result->name = readIdent ();
      on_module (result);
      checkSymbol (SEMICOLON);
      result->impl_imports = parse_import_sect ();
      result->impl_decl = parse_decl_part ();
      checkSymbol (keyword_begin);
      result->init = parse_stat_list ();
      checkSymbol (keyword_end);
      checkSymbol (DOT);
      close_module (result);
      return result;
}

TModule * Parser::parse_module_decl ()
{

      TModule * result = NULL;
      if (isSymbol (keyword_unit))
      {
         result = parse_unit_decl ();
      }
      else if (isSymbol (keyword_program))
      {
         result = parse_program_decl ();
      }
      else if (isSymbol (keyword_library))
      {
         result = parse_library_decl ();
      }
      else {
         stop ("Unexpected token");
      }
      return result;
}

bool Parser::test_1 ()
{

      bool result = true;
      int position = mark ();
      if (result && token != keyword_string)
      {
         result = false;
      }
      if (result)
      {
         nextToken ();
      }
      if (result && token != LPAREN)
      {
         result = false;
      }
      if (result)
      {
         nextToken ();
      }
      rewind (position);
      return result;
}

bool Parser::test_2 ()
{
      bool result = true;
      int position = mark ();
      if (result)
      {
         if (!test_label_ident ())
         {
            result = false;
         }
      }
      if (result && token != COLON)
      {
         result = false;
      }
      if (result)
      {
         nextToken ();
      }
      rewind (position);
      return result;
}

bool Parser::test_3 ()
{
      bool result = true;
      int position = mark ();
      if (result)
      {
         if (!test_range_type ())
         {
            result = false;
         }
      }
      rewind (position);
      return result;
}

bool Parser::test_4 ()
{
      bool result = true;
      int position = mark ();
      if (result)
      {
         if (!test_enum_type ())
         {
            result = false;
         }
      }
      rewind (position);
      return result;
}

bool Parser::test_label_ident ()
{
      if (token != identifier)
      {
         return false;
      }
      nextToken ();
      return true;
}

bool Parser::test_range_type ()
{
      if (!test_simple_expr ())
      {
         return false;
      }
      if (token != RANGE)
      {
         return false;
      }
      nextToken ();
      if (!test_simple_expr ())
      {
         return false;
      }
      return true;
}

bool Parser::test_simple_expr ()
{
      if (!test_term ())
      {
         return false;
      }
      while (isSymbol (PLUS) || isSymbol (MINUS) || isSymbol (keyword_or) || isSymbol (keyword_xor))
      {
         if (isSymbol (PLUS))
         {
            nextToken ();
         }
         else if (isSymbol (MINUS))
         {
            nextToken ();
         }
         else if (isSymbol (keyword_or))
         {
            nextToken ();
         }
         else if (isSymbol (keyword_xor))
         {
            nextToken ();
         }
         else {
            return false;
         }
         if (!test_term ())
         {
            return false;
         }
      }
      return true;
}

bool Parser::test_term ()
{
      if (!test_factor ())
      {
         return false;
      }
      while (isSymbol (STAR) || isSymbol (SLASH) || isSymbol (keyword_div) || isSymbol (keyword_mod) || isSymbol (keyword_shl) || isSymbol (keyword_shr) || isSymbol (keyword_and) || isSymbol (keyword_as))
      {
         if (isSymbol (STAR))
         {
            nextToken ();
         }
         else if (isSymbol (SLASH))
         {
            nextToken ();
         }
         else if (isSymbol (keyword_div))
         {
            nextToken ();
         }
         else if (isSymbol (keyword_mod))
         {
            nextToken ();
         }
         else if (isSymbol (keyword_shl))
         {
            nextToken ();
         }
         else if (isSymbol (keyword_shr))
         {
            nextToken ();
         }
         else if (isSymbol (keyword_and))
         {
            nextToken ();
         }
         else if (isSymbol (keyword_as))
         {
            nextToken ();
         }
         else {
            return false;
         }
         if (!test_factor ())
         {
            return false;
         }
      }
      return true;
}

bool Parser::test_factor ()
{
      if (isSymbol (number))
      {
         if (!test_int_value_expr ())
         {
            return false;
         }
      }
      else if (isSymbol (real_number))
      {
         if (!test_float_value_expr ())
         {
            return false;
         }
      }
      else if (isSymbol (string_literal))
      {
         if (!test_string_value_expr ())
         {
            return false;
         }
      }
      else if (isSymbol (keyword_not))
      {
         if (!test_not_expr ())
         {
            return false;
         }
      }
      else if (isSymbol (PLUS))
      {
         if (!test_plus_expr ())
         {
            return false;
         }
      }
      else if (isSymbol (MINUS))
      {
         if (!test_minus_expr ())
         {
            return false;
         }
      }
      else if (isSymbol (ADDRESS))
      {
         if (!test_adr_expr ())
         {
            return false;
         }
      }
      else if (isSymbol (keyword_nil))
      {
         if (!test_nil_expr ())
         {
            return false;
         }
      }
      else if (isSymbol (LBRACKET))
      {
         if (!test_set_expr ())
         {
            return false;
         }
      }
      else if (isSymbol (keyword_string) && test_1 ())
      {
         if (!test_string_type_expr ())
         {
            return false;
         }
      }
      else if (isSymbol (identifier) || isSymbol (LPAREN) || isSymbol (keyword_inherited))
      {
         if (!test_reference ())
         {
            return false;
         }
      }
      else {
         return false;
      }
      return true;
}

bool Parser::test_int_value_expr ()
{
      if (token != number)
      {
         return false;
      }
      nextToken ();
      return true;
}

bool Parser::test_float_value_expr ()
{
      if (token != real_number)
      {
         return false;
      }
      nextToken ();
      return true;
}

bool Parser::test_string_value_expr ()
{
      if (token != string_literal)
      {
         return false;
      }
      nextToken ();
      return true;
}

bool Parser::test_not_expr ()
{
      if (token != keyword_not)
      {
         return false;
      }
      nextToken ();
      if (!test_factor ())
      {
         return false;
      }
      return true;
}

bool Parser::test_plus_expr ()
{
      if (token != PLUS)
      {
         return false;
      }
      nextToken ();
      if (!test_factor ())
      {
         return false;
      }
      return true;
}

bool Parser::test_minus_expr ()
{
      if (token != MINUS)
      {
         return false;
      }
      nextToken ();
      if (!test_factor ())
      {
         return false;
      }
      return true;
}

bool Parser::test_adr_expr ()
{
      if (token != ADDRESS)
      {
         return false;
      }
      nextToken ();
      if (!test_factor ())
      {
         return false;
      }
      return true;
}

bool Parser::test_nil_expr ()
{
      if (token != keyword_nil)
      {
         return false;
      }
      nextToken ();
      return true;
}

bool Parser::test_set_expr ()
{
      if (token != LBRACKET)
      {
         return false;
      }
      nextToken ();
      if (!test_elem_sect ())
      {
         return false;
      }
      if (token != RBRACKET)
      {
         return false;
      }
      nextToken ();
      return true;
}

bool Parser::test_elem_sect ()
{
      if (!test_elem_item ())
      {
         return false;
      }
      while (isSymbol (COMMA))
      {
         nextToken ();
         if (!test_elem_item ())
         {
            return false;
         }
      }
      return true;
}

bool Parser::test_elem_item ()
{
      if (!test_expr ())
      {
         return false;
      }
      if (isSymbol (RANGE))
      {
         nextToken ();
         if (!test_expr ())
         {
            return false;
         }
      }
      return true;
}

bool Parser::test_expr ()
{
      if (!test_simple_expr ())
      {
         return false;
      }
      if (isSymbol (EQUAL) || isSymbol (UNEQUAL) || isSymbol (LESS) || isSymbol (GREATER) || isSymbol (LESS_OR_EQUAL) || isSymbol (GREATER_OR_EQUAL) || isSymbol (keyword_in) || isSymbol (keyword_is))
      {
         if (isSymbol (EQUAL))
         {
            nextToken ();
         }
         else if (isSymbol (UNEQUAL))
         {
            nextToken ();
         }
         else if (isSymbol (LESS))
         {
            nextToken ();
         }
         else if (isSymbol (GREATER))
         {
            nextToken ();
         }
         else if (isSymbol (LESS_OR_EQUAL))
         {
            nextToken ();
         }
         else if (isSymbol (GREATER_OR_EQUAL))
         {
            nextToken ();
         }
         else if (isSymbol (keyword_in))
         {
            nextToken ();
         }
         else if (isSymbol (keyword_is))
         {
            nextToken ();
         }
         else {
            return false;
         }
         if (!test_simple_expr ())
         {
            return false;
         }
      }
      return true;
}

bool Parser::test_string_type_expr ()
{
      if (token != keyword_string)
      {
         return false;
      }
      nextToken ();
      if (token != LPAREN)
      {
         return false;
      }
      nextToken ();
      if (!test_expr ())
      {
         return false;
      }
      if (token != RPAREN)
      {
         return false;
      }
      nextToken ();
      return true;
}

bool Parser::test_reference ()
{
      if (!test_variable ())
      {
         return false;
      }
      while (isSymbol (LBRACKET) || isSymbol (LPAREN) || isSymbol (ARROW) || isSymbol (DOT))
      {
         if (isSymbol (LBRACKET))
         {
            if (!test_index_expr ())
            {
               return false;
            }
         }
         else if (isSymbol (LPAREN))
         {
            if (!test_call_expr ())
            {
               return false;
            }
         }
         else if (isSymbol (ARROW))
         {
            if (!test_deref_expr ())
            {
               return false;
            }
         }
         else if (isSymbol (DOT))
         {
            if (!test_field_expr ())
            {
               return false;
            }
         }
         else {
            return false;
         }
      }
      return true;
}

bool Parser::test_variable ()
{
      if (isSymbol (identifier))
      {
         if (!test_ident_expr ())
         {
            return false;
         }
      }
      else if (isSymbol (LPAREN))
      {
         if (!test_sub_expr ())
         {
            return false;
         }
      }
      else if (isSymbol (keyword_inherited))
      {
         if (!test_super_expr ())
         {
            return false;
         }
      }
      else {
         return false;
      }
      return true;
}

bool Parser::test_ident_expr ()
{
      if (token != identifier)
      {
         return false;
      }
      nextToken ();
      return true;
}

bool Parser::test_sub_expr ()
{
      if (token != LPAREN)
      {
         return false;
      }
      nextToken ();
      if (!test_expr ())
      {
         return false;
      }
      if (token != RPAREN)
      {
         return false;
      }
      nextToken ();
      return true;
}

bool Parser::test_super_expr ()
{
      if (token != keyword_inherited)
      {
         return false;
      }
      nextToken ();
      if (token != identifier)
      {
         return false;
      }
      nextToken ();
      return true;
}

bool Parser::test_index_expr ()
{
      if (token != LBRACKET)
      {
         return false;
      }
      nextToken ();
      if (!test_index_expr_list ())
      {
         return false;
      }
      if (token != RBRACKET)
      {
         return false;
      }
      nextToken ();
      return true;
}

bool Parser::test_index_expr_list ()
{
      if (!test_index_expr_item ())
      {
         return false;
      }
      while (isSymbol (COMMA))
      {
         nextToken ();
         if (!test_index_expr_item ())
         {
            return false;
         }
      }
      return true;
}

bool Parser::test_index_expr_item ()
{
      if (!test_expr ())
      {
         return false;
      }
      return true;
}

bool Parser::test_call_expr ()
{
      if (token != LPAREN)
      {
         return false;
      }
      nextToken ();
      if (!test_arg_list ())
      {
         return false;
      }
      if (token != RPAREN)
      {
         return false;
      }
      nextToken ();
      return true;
}

bool Parser::test_arg_list ()
{
      if (!test_arg_item ())
      {
         return false;
      }
      while (isSymbol (COMMA))
      {
         nextToken ();
         if (!test_arg_item ())
         {
            return false;
         }
      }
      return true;
}

bool Parser::test_arg_item ()
{
      if (!test_expr ())
      {
         return false;
      }
      if (isSymbol (COLON))
      {
         nextToken ();
         if (!test_expr ())
         {
            return false;
         }
         if (isSymbol (COLON))
         {
            nextToken ();
            if (!test_expr ())
            {
               return false;
            }
         }
      }
      return true;
}

bool Parser::test_deref_expr ()
{
      if (token != ARROW)
      {
         return false;
      }
      nextToken ();
      return true;
}

bool Parser::test_field_expr ()
{
      if (token != DOT)
      {
         return false;
      }
      nextToken ();
      if (token != identifier)
      {
         return false;
      }
      nextToken ();
      return true;
}

bool Parser::test_enum_type ()
{
      if (token != LPAREN)
      {
         return false;
      }
      nextToken ();
      if (!test_enum_sect ())
      {
         return false;
      }
      if (token != RPAREN)
      {
         return false;
      }
      nextToken ();
      return true;
}

bool Parser::test_enum_sect ()
{
      if (!test_enum_item ())
      {
         return false;
      }
      while (isSymbol (COMMA))
      {
         nextToken ();
         if (!test_enum_item ())
         {
            return false;
         }
      }
      return true;
}

bool Parser::test_enum_item ()
{
      if (token != identifier)
      {
         return false;
      }
      nextToken ();
      return true;
}

void Parser::lookupKeyword ()
{
      string s = tokenTxt;
      int n = s.length ();
      if (n == 2)
      {
         if (s[0] == 'a')
         {
               if (s[1] == 's')
               {
                     token = keyword_as;
               }
         }
         else if (s[0] == 'd')
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
               else if (s[1] == 'n')
               {
                     token = keyword_in;
               }
               else if (s[1] == 's')
               {
                     token = keyword_is;
               }
         }
         else if (s[0] == 'o')
         {
               if (s[1] == 'f')
               {
                     token = keyword_of;
               }
               else if (s[1] == 'n')
               {
                     token = keyword_on;
               }
               else if (s[1] == 'r')
               {
                     token = keyword_or;
               }
         }
         else if (s[0] == 't')
         {
               if (s[1] == 'o')
               {
                     token = keyword_to;
               }
         }
      }
      else if (n == 3)
      {
         if (s[0] == 'a')
         {
               if (s.substr (1,2) == "nd")
               {
                     token = keyword_and;
               }
         }
         else if (s[0] == 'd')
         {
               if (s.substr (1,2) == "iv")
               {
                     token = keyword_div;
               }
         }
         else if (s[0] == 'e')
         {
               if (s.substr (1,2) == "nd")
               {
                     token = keyword_end;
               }
         }
         else if (s[0] == 'f')
         {
               if (s.substr (1,2) == "or")
               {
                     token = keyword_for;
               }
         }
         else if (s[0] == 'm')
         {
               if (s.substr (1,2) == "od")
               {
                     token = keyword_mod;
               }
         }
         else if (s[0] == 'n')
         {
               if (s[1] == 'i')
               {
                     if (s[2] == 'l')
                     {
                           token = keyword_nil;
                     }
               }
               else if (s[1] == 'o')
               {
                     if (s[2] == 't')
                     {
                           token = keyword_not;
                     }
               }
         }
         else if (s[0] == 'o')
         {
               if (s.substr (1,2) == "ut")
               {
                     token = keyword_out;
               }
         }
         else if (s[0] == 's')
         {
               if (s[1] == 'e')
               {
                     if (s[2] == 't')
                     {
                           token = keyword_set;
                     }
               }
               else if (s[1] == 'h')
               {
                     if (s[2] == 'l')
                     {
                           token = keyword_shl;
                     }
                     else if (s[2] == 'r')
                     {
                           token = keyword_shr;
                     }
               }
         }
         else if (s[0] == 't')
         {
               if (s.substr (1,2) == "ry")
               {
                     token = keyword_try;
               }
         }
         else if (s[0] == 'v')
         {
               if (s.substr (1,2) == "ar")
               {
                     token = keyword_var;
               }
         }
         else if (s[0] == 'x')
         {
               if (s.substr (1,2) == "or")
               {
                     token = keyword_xor;
               }
         }
      }
      else if (n == 4)
      {
         if (s[0] == 'c')
         {
               if (s.substr (1,3) == "ase")
               {
                     token = keyword_case;
               }
         }
         else if (s[0] == 'e')
         {
               if (s.substr (1,3) == "lse")
               {
                     token = keyword_else;
               }
         }
         else if (s[0] == 'f')
         {
               if (s.substr (1,3) == "ile")
               {
                     token = keyword_file;
               }
         }
         else if (s[0] == 'g')
         {
               if (s.substr (1,3) == "oto")
               {
                     token = keyword_goto;
               }
         }
         else if (s[0] == 'r')
         {
               if (s.substr (1,3) == "ead")
               {
                     token = keyword_read;
               }
         }
         else if (s[0] == 't')
         {
               if (s[1] == 'h')
               {
                     if (s.substr (2,2) == "en")
                     {
                           token = keyword_then;
                     }
               }
               else if (s[1] == 'y')
               {
                     if (s.substr (2,2) == "pe")
                     {
                           token = keyword_type;
                     }
               }
         }
         else if (s[0] == 'u')
         {
               if (s[1] == 'n')
               {
                     if (s.substr (2,2) == "it")
                     {
                           token = keyword_unit;
                     }
               }
               else if (s[1] == 's')
               {
                     if (s.substr (2,2) == "es")
                     {
                           token = keyword_uses;
                     }
               }
         }
         else if (s[0] == 'w')
         {
               if (s.substr (1,3) == "ith")
               {
                     token = keyword_with;
               }
         }
      }
      else if (n == 5)
      {
         if (s[0] == 'a')
         {
               if (s.substr (1,4) == "rray")
               {
                     token = keyword_array;
               }
         }
         else if (s[0] == 'b')
         {
               if (s.substr (1,4) == "egin")
               {
                     token = keyword_begin;
               }
         }
         else if (s[0] == 'c')
         {
               if (s[1] == 'd')
               {
                     if (s.substr (2,3) == "ecl")
                     {
                           token = keyword_cdecl;
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
         else if (s[0] == 'l')
         {
               if (s.substr (1,4) == "abel")
               {
                     token = keyword_label;
               }
         }
         else if (s[0] == 'r')
         {
               if (s.substr (1,4) == "aise")
               {
                     token = keyword_raise;
               }
         }
         else if (s[0] == 'u')
         {
               if (s.substr (1,4) == "ntil")
               {
                     token = keyword_until;
               }
         }
         else if (s[0] == 'w')
         {
               if (s[1] == 'h')
               {
                     if (s.substr (2,3) == "ile")
                     {
                           token = keyword_while;
                     }
               }
               else if (s[1] == 'r')
               {
                     if (s.substr (2,3) == "ite")
                     {
                           token = keyword_write;
                     }
               }
         }
      }
      else if (n == 6)
      {
         if (s[0] == 'd')
         {
               if (s.substr (1,5) == "ownto")
               {
                     token = keyword_downto;
               }
         }
         else if (s[0] == 'e')
         {
               if (s.substr (1,5) == "xcept")
               {
                     token = keyword_except;
               }
         }
         else if (s[0] == 'i')
         {
               if (s.substr (1,5) == "nline")
               {
                     token = keyword_inline;
               }
         }
         else if (s[0] == 'o')
         {
               if (s.substr (1,5) == "bject")
               {
                     token = keyword_object;
               }
         }
         else if (s[0] == 'p')
         {
               if (s[1] == 'a')
               {
                     if (s[2] == 'c')
                     {
                           if (s.substr (3,3) == "ked")
                           {
                                 token = keyword_packed;
                           }
                     }
                     else if (s[2] == 's')
                     {
                           if (s.substr (3,3) == "cal")
                           {
                                 token = keyword_pascal;
                           }
                     }
               }
               else if (s[1] == 'u')
               {
                     if (s.substr (2,4) == "blic")
                     {
                           token = keyword_public;
                     }
               }
         }
         else if (s[0] == 'r')
         {
               if (s[1] == 'e')
               {
                     if (s[2] == 'c')
                     {
                           if (s.substr (3,3) == "ord")
                           {
                                 token = keyword_record;
                           }
                     }
                     else if (s[2] == 'p')
                     {
                           if (s.substr (3,3) == "eat")
                           {
                                 token = keyword_repeat;
                           }
                     }
               }
         }
         else if (s[0] == 's')
         {
               if (s[1] == 't')
               {
                     if (s[2] == 'o')
                     {
                           if (s.substr (3,3) == "red")
                           {
                                 token = keyword_stored;
                           }
                     }
                     else if (s[2] == 'r')
                     {
                           if (s.substr (3,3) == "ing")
                           {
                                 token = keyword_string;
                           }
                     }
               }
         }
      }
      else if (n == 7)
      {
         if (s[0] == 'd')
         {
               if (s[1] == 'e')
               {
                     if (s.substr (2,5) == "fault")
                     {
                           token = keyword_default;
                     }
               }
               else if (s[1] == 'y')
               {
                     if (s.substr (2,5) == "namic")
                     {
                           token = keyword_dynamic;
                     }
               }
         }
         else if (s[0] == 'f')
         {
               if (s[1] == 'i')
               {
                     if (s.substr (2,5) == "nally")
                     {
                           token = keyword_finally;
                     }
               }
               else if (s[1] == 'o')
               {
                     if (s.substr (2,5) == "rward")
                     {
                           token = keyword_forward;
                     }
               }
         }
         else if (s[0] == 'l')
         {
               if (s.substr (1,6) == "ibrary")
               {
                     token = keyword_library;
               }
         }
         else if (s[0] == 'p')
         {
               if (s[1] == 'r')
               {
                     if (s[2] == 'i')
                     {
                           if (s.substr (3,4) == "vate")
                           {
                                 token = keyword_private;
                           }
                     }
                     else if (s[2] == 'o')
                     {
                           if (s.substr (3,4) == "gram")
                           {
                                 token = keyword_program;
                           }
                     }
               }
         }
         else if (s[0] == 's')
         {
               if (s.substr (1,6) == "tdcall")
               {
                     token = keyword_stdcall;
               }
         }
         else if (s[0] == 'v')
         {
               if (s.substr (1,6) == "irtual")
               {
                     token = keyword_virtual;
               }
         }
      }
      else if (n == 8)
      {
         if (s[0] == 'a')
         {
               if (s.substr (1,7) == "bstract")
               {
                     token = keyword_abstract;
               }
         }
         else if (s[0] == 'e')
         {
               if (s.substr (1,7) == "xternal")
               {
                     token = keyword_external;
               }
         }
         else if (s[0] == 'f')
         {
               if (s.substr (1,7) == "unction")
               {
                     token = keyword_function;
               }
         }
         else if (s[0] == 'o')
         {
               if (s.substr (1,7) == "verride")
               {
                     token = keyword_override;
               }
         }
         else if (s[0] == 'p')
         {
               if (s.substr (1,7) == "roperty")
               {
                     token = keyword_property;
               }
         }
         else if (s[0] == 'r')
         {
               if (s.substr (1,7) == "egister")
               {
                     token = keyword_register;
               }
         }
         else if (s[0] == 's')
         {
               if (s.substr (1,7) == "afecall")
               {
                     token = keyword_safecall;
               }
         }
      }
      else if (n == 9)
      {
         if (s[0] == 'a')
         {
               if (s.substr (1,8) == "utomated")
               {
                     token = keyword_automated;
               }
         }
         else if (s[0] == 'i')
         {
               if (s[1] == 'n')
               {
                     if (s[2] == 'h')
                     {
                           if (s.substr (3,6) == "erited")
                           {
                                 token = keyword_inherited;
                           }
                     }
                     else if (s[2] == 't')
                     {
                           if (s.substr (3,6) == "erface")
                           {
                                 token = keyword_interface;
                           }
                     }
               }
         }
         else if (s[0] == 'n')
         {
               if (s.substr (1,8) == "odefault")
               {
                     token = keyword_nodefault;
               }
         }
         else if (s[0] == 'p')
         {
               if (s[1] == 'r')
               {
                     if (s[2] == 'o')
                     {
                           if (s[3] == 'c')
                           {
                                 if (s.substr (4,5) == "edure")
                                 {
                                       token = keyword_procedure;
                                 }
                           }
                           else if (s[3] == 't')
                           {
                                 if (s.substr (4,5) == "ected")
                                 {
                                       token = keyword_protected;
                                 }
                           }
                     }
               }
               else if (s[1] == 'u')
               {
                     if (s.substr (2,7) == "blished")
                     {
                           token = keyword_published;
                     }
               }
         }
      }
      else if (n == 10)
      {
         if (s[0] == 'd')
         {
               if (s.substr (1,9) == "estructor")
               {
                     token = keyword_destructor;
               }
         }
         else if (s[0] == 'i')
         {
               if (s.substr (1,9) == "mplements")
               {
                     token = keyword_implements;
               }
         }
      }
      else if (n == 11)
      {
         if (s.substr (0,11) == "constructor")
         {
               token = keyword_constructor;
         }
      }
      else if (n == 12)
      {
         if (s.substr (0,12) == "finalization")
         {
               token = keyword_finalization;
         }
      }
      else if (n == 14)
      {
         if (s[0] == 'i')
         {
               if (s[1] == 'm')
               {
                     if (s.substr (2,12) == "plementation")
                     {
                           token = keyword_implementation;
                     }
               }
               else if (s[1] == 'n')
               {
                     if (s.substr (2,12) == "itialization")
                     {
                           token = keyword_initialization;
                     }
               }
         }
      }
}

void Parser::processSeparator ()
{
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
      }
      if (tokenTxt == "+")
      {
         token = PLUS;
      }
      if (tokenTxt == ",")
      {
         token = COMMA;
      }
      if (tokenTxt == "-")
      {
         token = MINUS;
      }
      if (tokenTxt == ".")
      {
         token = DOT;
         if (inpCh == '.')
         {
            token = RANGE;
            tokenTxt = tokenTxt + inpCh;
            nextCh ();
         }
      }
      if (tokenTxt == "/")
      {
         token = SLASH;
      }
      if (tokenTxt == ":")
      {
         token = COLON;
         if (inpCh == '=')
         {
            token = ASSIGN;
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
         if (inpCh == '=')
         {
            token = LESS_OR_EQUAL;
            tokenTxt = tokenTxt + inpCh;
            nextCh ();
         }
         if (inpCh == '>')
         {
            token = UNEQUAL;
            tokenTxt = tokenTxt + inpCh;
            nextCh ();
         }
      }
      if (tokenTxt == "=")
      {
         token = EQUAL;
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
      }
      if (tokenTxt == "@")
      {
         token = ADDRESS;
      }
      if (tokenTxt == "[")
      {
         token = LBRACKET;
      }
      if (tokenTxt == "]")
      {
         token = RBRACKET;
      }
      if (tokenTxt == "^")
      {
         token = ARROW;
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
         return "(";
      if (value  ==  9)
         return ")";
      if (value  ==  10)
         return "*";
      if (value  ==  11)
         return "+";
      if (value  ==  12)
         return ",";
      if (value  ==  13)
         return "-";
      if (value  ==  14)
         return ".";
      if (value  ==  15)
         return "..";
      if (value  ==  16)
         return "/";
      if (value  ==  17)
         return ":";
      if (value  ==  18)
         return ":=";
      if (value  ==  19)
         return ";";
      if (value  ==  20)
         return "<";
      if (value  ==  21)
         return "<=";
      if (value  ==  22)
         return "<>";
      if (value  ==  23)
         return "=";
      if (value  ==  24)
         return ">";
      if (value  ==  25)
         return ">=";
      if (value  ==  26)
         return "@";
      if (value  ==  27)
         return "[";
      if (value  ==  28)
         return "]";
      if (value  ==  29)
         return "^";
      if (value  ==  30)
         return "abstract";
      if (value  ==  31)
         return "and";
      if (value  ==  32)
         return "array";
      if (value  ==  33)
         return "as";
      if (value  ==  34)
         return "automated";
      if (value  ==  35)
         return "begin";
      if (value  ==  36)
         return "case";
      if (value  ==  37)
         return "cdecl";
      if (value  ==  38)
         return "class";
      if (value  ==  39)
         return "const";
      if (value  ==  40)
         return "constructor";
      if (value  ==  41)
         return "default";
      if (value  ==  42)
         return "destructor";
      if (value  ==  43)
         return "div";
      if (value  ==  44)
         return "do";
      if (value  ==  45)
         return "downto";
      if (value  ==  46)
         return "dynamic";
      if (value  ==  47)
         return "else";
      if (value  ==  48)
         return "end";
      if (value  ==  49)
         return "except";
      if (value  ==  50)
         return "external";
      if (value  ==  51)
         return "file";
      if (value  ==  52)
         return "finalization";
      if (value  ==  53)
         return "finally";
      if (value  ==  54)
         return "for";
      if (value  ==  55)
         return "forward";
      if (value  ==  56)
         return "function";
      if (value  ==  57)
         return "goto";
      if (value  ==  58)
         return "if";
      if (value  ==  59)
         return "implementation";
      if (value  ==  60)
         return "implements";
      if (value  ==  61)
         return "in";
      if (value  ==  62)
         return "inherited";
      if (value  ==  63)
         return "initialization";
      if (value  ==  64)
         return "inline";
      if (value  ==  65)
         return "interface";
      if (value  ==  66)
         return "is";
      if (value  ==  67)
         return "label";
      if (value  ==  68)
         return "library";
      if (value  ==  69)
         return "mod";
      if (value  ==  70)
         return "nil";
      if (value  ==  71)
         return "nodefault";
      if (value  ==  72)
         return "not";
      if (value  ==  73)
         return "object";
      if (value  ==  74)
         return "of";
      if (value  ==  75)
         return "on";
      if (value  ==  76)
         return "or";
      if (value  ==  77)
         return "out";
      if (value  ==  78)
         return "override";
      if (value  ==  79)
         return "packed";
      if (value  ==  80)
         return "pascal";
      if (value  ==  81)
         return "private";
      if (value  ==  82)
         return "procedure";
      if (value  ==  83)
         return "program";
      if (value  ==  84)
         return "property";
      if (value  ==  85)
         return "protected";
      if (value  ==  86)
         return "public";
      if (value  ==  87)
         return "published";
      if (value  ==  88)
         return "raise";
      if (value  ==  89)
         return "read";
      if (value  ==  90)
         return "record";
      if (value  ==  91)
         return "register";
      if (value  ==  92)
         return "repeat";
      if (value  ==  93)
         return "safecall";
      if (value  ==  94)
         return "set";
      if (value  ==  95)
         return "shl";
      if (value  ==  96)
         return "shr";
      if (value  ==  97)
         return "stdcall";
      if (value  ==  98)
         return "stored";
      if (value  ==  99)
         return "string";
      if (value  ==  100)
         return "then";
      if (value  ==  101)
         return "to";
      if (value  ==  102)
         return "try";
      if (value  ==  103)
         return "type";
      if (value  ==  104)
         return "unit";
      if (value  ==  105)
         return "until";
      if (value  ==  106)
         return "uses";
      if (value  ==  107)
         return "var";
      if (value  ==  108)
         return "virtual";
      if (value  ==  109)
         return "while";
      if (value  ==  110)
         return "with";
      if (value  ==  111)
         return "write";
      if (value  ==  112)
         return "xor";
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

void Parser::on_ident_expr (TIdentExpr * item)
{
}

void Parser::on_field_expr (TFieldExpr * item)
{
}

void Parser::on_param (TParamIdent * item)
{
}

void Parser::add_param (TParamItem * item)
{
}

void Parser::open_class (TClassType * item)
{
}

void Parser::close_class (TClassType * item)
{
}

void Parser::open_interface (TInterfaceType * item)
{
}

void Parser::close_interface (TInterfaceType * item)
{
}

void Parser::on_field (TFieldItem * item)
{
}

void Parser::add_field (TFieldDecl * item)
{
}

void Parser::open_proc (TProcDecl * item)
{
}

void Parser::close_proc (TProcDecl * item)
{
}

void Parser::simple_type (CmmBasic * item)
{
}

void Parser::on_const (TConstDecl * item)
{
}

void Parser::add_const (TConstDecl * item)
{
}

void Parser::on_type (TTypeDecl * item)
{
}

void Parser::add_type (TTypeDecl * item)
{
}

void Parser::on_var (TVarItem * item)
{
}

void Parser::add_var (TVarDecl * item)
{
}

void Parser::on_proc (TProcDecl * item)
{
}

void Parser::on_begin_proc (TProcDecl * item)
{
}

void Parser::on_end_proc (TProcDecl * item)
{
}

void Parser::on_tail_proc (TProcDecl * item)
{
}

void Parser::on_import (TImportItem * item)
{
}

void Parser::open_module (CmmBasic * item)
{
}

void Parser::on_module (CmmBasic * item)
{
}

void Parser::close_module (CmmBasic * item)
{
}

Parser::Parser ()
{
}
