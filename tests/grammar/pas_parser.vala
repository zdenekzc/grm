public enum CmmSymbol
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
}

public enum TFce
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
}

public enum TAccess
{
   PrivateAccess,
   ProtectedAccess,
   PublicAccess,
   PublishedAccess,
   AutomatedAccess
}

public enum TStyle
{
   ProcedureStyle,
   FunctionStyle,
   ConstructorStyle,
   DestructorStyle
}

public enum TCall
{
   RegisterCall,
   PascalCall,
   CdeclCall,
   StdcallCall,
   SafecallCall
}

public enum TParamMode
{
   VarParam,
   ConstParam,
   OutParam,
   ValueParam
}

public enum TDeclTag
{
   none
}

public enum TModuleKind
{
   none
}

public class Parser : Lexer
{
   public CmmSymbol token;
   private uchar [] set_0 = {0, 65, 0, 40, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0};
   // set_0 :  ( . [ ^

   private uchar [] set_1 = {0, 4, 1, 128, 2, 8, 0, 0, 32, 0, 0, 128, 1, 0, 0};
   // set_1 :  * / and as div mod shl shr

   private uchar [] set_2 = {0, 40, 0, 0, 0, 0, 0, 0, 0, 16, 0, 0, 0, 0, 1};
   // set_2 :  + - or xor

   private uchar [] set_3 = {0, 0, 240, 3, 0, 0, 0, 32, 4, 0, 0, 0, 0, 0, 0};
   // set_3 :  < <= <> = > >= in is

   private uchar [] set_4 = {46, 41, 0, 12, 0, 0, 0, 64, 64, 1, 0, 0, 8, 0, 0};
   // set_4 :  identifier number real_number string_literal ( + - @ [ inherited nil not string

   private uchar [] set_5 = {46, 41, 8, 12, 24, 0, 64, 70, 64, 1, 0, 17, 72, 96, 0};
   // set_5 :  identifier number real_number string_literal ( + - ; @ [ begin case for goto if inherited nil not raise repeat string try while with

   private uchar [] set_6 = {0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 226, 0, 0, 0, 0};
   // set_6 :  automated private protected public published

   private uchar [] set_7 = {2, 0, 0, 0, 64, 5, 0, 1, 0, 0, 20, 0, 0, 0, 0};
   // set_7 :  identifier class constructor destructor function procedure property

   private uchar [] set_8 = {0, 0, 0, 0, 64, 5, 0, 1, 0, 0, 4, 0, 0, 0, 0};
   // set_8 :  class constructor destructor function procedure

   private uchar [] set_9 = {0, 0, 0, 64, 0, 64, 0, 0, 0, 64, 0, 0, 0, 16, 0};
   // set_9 :  abstract dynamic override virtual

   private uchar [] set_10 = {0, 0, 0, 0, 32, 0, 0, 0, 0, 0, 1, 40, 2, 0, 0};
   // set_10 :  cdecl pascal register safecall stdcall

   private uchar [] set_11 = {0, 0, 0, 0, 200, 5, 0, 1, 9, 0, 4, 0, 128, 8, 0};
   // set_11 :  begin class const constructor destructor function inline label procedure type var

   private uchar [] set_12 = {0, 0, 0, 0, 192, 5, 0, 1, 0, 0, 4, 0, 128, 8, 0};
   // set_12 :  class const constructor destructor function procedure type var

   private uchar [] set_13 = {0, 0, 0, 0, 192, 5, 0, 1, 8, 0, 4, 0, 128, 8, 0};
   // set_13 :  class const constructor destructor function label procedure type var


   public TLabelIdent parse_label_ident ()
   {

         TLabelIdent result = new TLabelIdent ();
         storeLocation (result);
         result.id = readIdent ();
         return result;
   }

   public TQualName parse_qualified_name ()
   {

         TQualName result = new TQualName ();
         storeLocation (result);
         result.id = readIdent ();
         while (isSymbol (DOT))
         {
            result.items.resize (result.items.length + 1);
            result.items [result.items.length - 1] = (parse_cont_name ());
         }
         return result;
   }

   public TContName parse_cont_name ()
   {

         TContName result = new TContName ();
         storeLocation (result);
         checkSymbol (DOT);
         result.id = readIdent ();
         return result;
   }

   public TType parse_ifc_type ()
   {

         TType result = null;
         result = parse_simple_alias_type ();
         return result;
   }

   public TType parse_param_type ()
   {

         TType result = null;
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

   public TType parse_result_type ()
   {

         TType result = null;
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

   public TAliasType parse_simple_alias_type ()
   {

         TAliasType result = new TAliasType ();
         storeLocation (result);
         result.alias_name = parse_qualified_name ();
         return result;
   }

   public TStringType parse_simple_string_type ()
   {

         TStringType result = new TStringType ();
         storeLocation (result);
         checkSymbol (keyword_string);
         return result;
   }

   public TFileType parse_simple_file_type ()
   {

         TFileType result = new TFileType ();
         storeLocation (result);
         checkSymbol (keyword_file);
         return result;
   }

   public TInxItem parse_index_expr_item ()
   {

         TInxItem result = new TInxItem ();
         storeLocation (result);
         result.ref = parse_expr ();
         return result;
   }

   public TInxList parse_index_expr_list ()
   {

         TInxList result = new TInxList ();
         storeLocation (result);
         result.items.resize (result.items.length + 1);
         result.items [result.items.length - 1] = (parse_index_expr_item ());
         while (isSymbol (COMMA))
         {
            checkSymbol (COMMA);
            result.items.resize (result.items.length + 1);
            result.items [result.items.length - 1] = (parse_index_expr_item ());
         }
         return result;
   }

   public TArgItem parse_arg_item ()
   {

         TArgItem result = new TArgItem ();
         storeLocation (result);
         result.value = parse_expr ();
         if (isSymbol (COLON))
         {
            checkSymbol (COLON);
            result.width = parse_expr ();
            if (isSymbol (COLON))
            {
               checkSymbol (COLON);
               result.digits = parse_expr ();
            }
         }
         return result;
   }

   public TArgSect parse_arg_list ()
   {

         TArgSect result = new TArgSect ();
         storeLocation (result);
         result.items.resize (result.items.length + 1);
         result.items [result.items.length - 1] = (parse_arg_item ());
         while (isSymbol (COMMA))
         {
            checkSymbol (COMMA);
            result.items.resize (result.items.length + 1);
            result.items [result.items.length - 1] = (parse_arg_item ());
         }
         return result;
   }

   public TElemSect parse_elem_sect ()
   {

         TElemSect result = new TElemSect ();
         storeLocation (result);
         result.items.resize (result.items.length + 1);
         result.items [result.items.length - 1] = (parse_elem_item ());
         while (isSymbol (COMMA))
         {
            checkSymbol (COMMA);
            result.items.resize (result.items.length + 1);
            result.items [result.items.length - 1] = (parse_elem_item ());
         }
         return result;
   }

   public TElemItem parse_elem_item ()
   {

         TElemItem result = new TElemItem ();
         storeLocation (result);
         result.low = parse_expr ();
         if (isSymbol (RANGE))
         {
            checkSymbol (RANGE);
            result.high = parse_expr ();
         }
         return result;
   }

   public TStructSect parse_struct_item ()
   {

         TStructSect result = new TStructSect ();
         storeLocation (result);
         if (isSymbol (identifier))
         {
            result.name = readIdent ();
            checkSymbol (COLON);
         }
         result.value = parse_expr ();
         return result;
   }

   public TStructSect parse_struct_sect ()
   {

         TStructSect result = new TStructSect ();
         storeLocation (result);
         result.items.resize (result.items.length + 1);
         result.items [result.items.length - 1] = (parse_struct_item ());
         if (isSymbol (COMMA) || isSymbol (SEMICOLON))
         {
            if (isSymbol (COMMA))
            {
               checkSymbol (COMMA);
               result.items.resize (result.items.length + 1);
               result.items [result.items.length - 1] = (parse_struct_item ());
               while (isSymbol (COMMA))
               {
                  checkSymbol (COMMA);
                  result.items.resize (result.items.length + 1);
                  result.items [result.items.length - 1] = (parse_struct_item ());
               }
            }
            else if (isSymbol (SEMICOLON))
            {
               checkSymbol (SEMICOLON);
               result.items.resize (result.items.length + 1);
               result.items [result.items.length - 1] = (parse_struct_item ());
               while (isSymbol (SEMICOLON))
               {
                  checkSymbol (SEMICOLON);
                  result.items.resize (result.items.length + 1);
                  result.items [result.items.length - 1] = (parse_struct_item ());
               }
            }
            else {
               stop ("Unexpected token");
            }
         }
         return result;
   }

   public TIdentExpr parse_ident_expr ()
   {

         TIdentExpr result = new TIdentExpr ();
         storeLocation (result);
         result.name = readIdent ();
         on_ident_expr (result);
         return result;
   }

   public TIntValueExpr parse_int_value_expr ()
   {

         TIntValueExpr result = new TIntValueExpr ();
         storeLocation (result);
         result.value = readNumber ();
         return result;
   }

   public TFltValueExpr parse_float_value_expr ()
   {

         TFltValueExpr result = new TFltValueExpr ();
         storeLocation (result);
         result.value = readReal ();
         return result;
   }

   public TStrValueExpr parse_string_value_expr ()
   {

         TStrValueExpr result = new TStrValueExpr ();
         storeLocation (result);
         result.value = readQuotedString ();
         return result;
   }

   public TNilExpr parse_nil_expr ()
   {

         TNilExpr result = new TNilExpr ();
         storeLocation (result);
         checkSymbol (keyword_nil);
         return result;
   }

   public TStructExpr parse_sub_expr ()
   {

         TStructExpr result = new TStructExpr ();
         storeLocation (result);
         checkSymbol (LPAREN);
         result.value = parse_expr ();
         checkSymbol (RPAREN);
         return result;
   }

   public TNotExpr parse_not_expr ()
   {

         TNotExpr result = new TNotExpr ();
         storeLocation (result);
         checkSymbol (keyword_not);
         result.param = parse_factor ();
         return result;
   }

   public TPlusExpr parse_plus_expr ()
   {

         TPlusExpr result = new TPlusExpr ();
         storeLocation (result);
         checkSymbol (PLUS);
         result.param = parse_factor ();
         return result;
   }

   public TMinusExpr parse_minus_expr ()
   {

         TMinusExpr result = new TMinusExpr ();
         storeLocation (result);
         checkSymbol (MINUS);
         result.param = parse_factor ();
         return result;
   }

   public TAdrExpr parse_adr_expr ()
   {

         TAdrExpr result = new TAdrExpr ();
         storeLocation (result);
         checkSymbol (ADDRESS);
         result.param = parse_factor ();
         return result;
   }

   public TSetExpr parse_set_expr ()
   {

         TSetExpr result = new TSetExpr ();
         storeLocation (result);
         checkSymbol (LBRACKET);
         result.list = parse_elem_sect ();
         checkSymbol (RBRACKET);
         return result;
   }

   public TSuperExpr parse_super_expr ()
   {

         TSuperExpr result = new TSuperExpr ();
         storeLocation (result);
         checkSymbol (keyword_inherited);
         result.name = readIdent ();
         return result;
   }

   public TStringExpr parse_string_type_expr ()
   {

         TStringExpr result = new TStringExpr ();
         storeLocation (result);
         checkSymbol (keyword_string);
         checkSymbol (LPAREN);
         result.param = parse_expr ();
         checkSymbol (RPAREN);
         return result;
   }

   public TExpr parse_variable ()
   {

         TExpr result = null;
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

   public TExpr parse_reference ()
   {

         TExpr result = null;
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

   public TIndexExpr parse_index_expr (TExpr store)
   {

         TIndexExpr result = new TIndexExpr ();
         storeLocation (result);
         result.left = store;
         checkSymbol (LBRACKET);
         result.list = parse_index_expr_list ();
         checkSymbol (RBRACKET);
         return result;
   }

   public TCallExpr parse_call_expr (TExpr store)
   {

         TCallExpr result = new TCallExpr ();
         storeLocation (result);
         result.func = store;
         checkSymbol (LPAREN);
         result.list = parse_arg_list ();
         checkSymbol (RPAREN);
         return result;
   }

   public TDerefExpr parse_deref_expr (TExpr store)
   {

         TDerefExpr result = new TDerefExpr ();
         storeLocation (result);
         result.param = store;
         checkSymbol (ARROW);
         return result;
   }

   public TFieldExpr parse_field_expr (TExpr store)
   {

         TFieldExpr result = new TFieldExpr ();
         storeLocation (result);
         result.param = store;
         checkSymbol (DOT);
         result.name = readIdent ();
         on_field_expr (result);
         return result;
   }

   public TExpr parse_factor ()
   {

         TExpr result = null;
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

   public TExpr parse_term ()
   {

         TExpr result = null;
         result = parse_factor ();
         while (isSymbol (STAR) || isSymbol (SLASH) || isSymbol (keyword_div) || isSymbol (keyword_mod) || isSymbol (keyword_shl) || isSymbol (keyword_shr) || isSymbol (keyword_and) || isSymbol (keyword_as))
         {
            TExpr store = result;
            TTermExpr result0 = new TTermExpr ();
            storeLocation (result0);
            result0.left = store;
            result = result0;
            if (isSymbol (STAR))
            {
               checkSymbol (STAR);
               result0.fce = MulExp;
            }
            else if (isSymbol (SLASH))
            {
               checkSymbol (SLASH);
               result0.fce = RDivExp;
            }
            else if (isSymbol (keyword_div))
            {
               checkSymbol (keyword_div);
               result0.fce = DivExp;
            }
            else if (isSymbol (keyword_mod))
            {
               checkSymbol (keyword_mod);
               result0.fce = ModExp;
            }
            else if (isSymbol (keyword_shl))
            {
               checkSymbol (keyword_shl);
               result0.fce = ShlExp;
            }
            else if (isSymbol (keyword_shr))
            {
               checkSymbol (keyword_shr);
               result0.fce = ShrExp;
            }
            else if (isSymbol (keyword_and))
            {
               checkSymbol (keyword_and);
               result0.fce = AndExp;
            }
            else if (isSymbol (keyword_as))
            {
               checkSymbol (keyword_as);
               result0.fce = AsExp;
            }
            else {
               stop ("Unexpected token");
            }
            result0.right = parse_factor ();
         }
         return result;
   }

   public TExpr parse_simple_expr ()
   {

         TExpr result = null;
         result = parse_term ();
         while (isSymbol (PLUS) || isSymbol (MINUS) || isSymbol (keyword_or) || isSymbol (keyword_xor))
         {
            TExpr store = result;
            TSimpleExpr result0 = new TSimpleExpr ();
            storeLocation (result0);
            result0.left = store;
            result = result0;
            if (isSymbol (PLUS))
            {
               checkSymbol (PLUS);
               result0.fce = AddExp;
            }
            else if (isSymbol (MINUS))
            {
               checkSymbol (MINUS);
               result0.fce = SubExp;
            }
            else if (isSymbol (keyword_or))
            {
               checkSymbol (keyword_or);
               result0.fce = OrExp;
            }
            else if (isSymbol (keyword_xor))
            {
               checkSymbol (keyword_xor);
               result0.fce = XorExp;
            }
            else {
               stop ("Unexpected token");
            }
            result0.right = parse_term ();
         }
         return result;
   }

   public TExpr parse_expr ()
   {

         TExpr result = null;
         result = parse_simple_expr ();
         if (isSymbol (EQUAL) || isSymbol (UNEQUAL) || isSymbol (LESS) || isSymbol (GREATER) || isSymbol (LESS_OR_EQUAL) || isSymbol (GREATER_OR_EQUAL) || isSymbol (keyword_in) || isSymbol (keyword_is))
         {
            TExpr store = result;
            TCompleteExpr result0 = new TCompleteExpr ();
            storeLocation (result0);
            result0.left = store;
            result = result0;
            if (isSymbol (EQUAL))
            {
               checkSymbol (EQUAL);
               result0.fce = EqExp;
            }
            else if (isSymbol (UNEQUAL))
            {
               checkSymbol (UNEQUAL);
               result0.fce = NeExp;
            }
            else if (isSymbol (LESS))
            {
               checkSymbol (LESS);
               result0.fce = LtExp;
            }
            else if (isSymbol (GREATER))
            {
               checkSymbol (GREATER);
               result0.fce = GtExp;
            }
            else if (isSymbol (LESS_OR_EQUAL))
            {
               checkSymbol (LESS_OR_EQUAL);
               result0.fce = LeExp;
            }
            else if (isSymbol (GREATER_OR_EQUAL))
            {
               checkSymbol (GREATER_OR_EQUAL);
               result0.fce = GeExp;
            }
            else if (isSymbol (keyword_in))
            {
               checkSymbol (keyword_in);
               result0.fce = InExp;
            }
            else if (isSymbol (keyword_is))
            {
               checkSymbol (keyword_is);
               result0.fce = IsExp;
            }
            else {
               stop ("Unexpected token");
            }
            result0.right = parse_simple_expr ();
         }
         return result;
   }

   public TGotoStat parse_goto_stat ()
   {

         TGotoStat result = new TGotoStat ();
         storeLocation (result);
         checkSymbol (keyword_goto);
         result.goto_lab = parse_label_ident ();
         return result;
   }

   public TBlockStat parse_begin_stat ()
   {

         TBlockStat result = new TBlockStat ();
         storeLocation (result);
         checkSymbol (keyword_begin);
         result.body_seq = parse_stat_list ();
         checkSymbol (keyword_end);
         return result;
   }

   public TStatSeq parse_stat_list ()
   {

         TStatSeq result = new TStatSeq ();
         storeLocation (result);
         result.items.resize (result.items.length + 1);
         result.items [result.items.length - 1] = (parse_stat ());
         while (isSymbol (SEMICOLON))
         {
            checkSymbol (SEMICOLON);
            result.items.resize (result.items.length + 1);
            result.items [result.items.length - 1] = (parse_stat ());
         }
         return result;
   }

   public TStat parse_inner_stat ()
   {

         TStat result = null;
         result = parse_stat ();
         return result;
   }

   public TIfStat parse_if_stat ()
   {

         TIfStat result = new TIfStat ();
         storeLocation (result);
         checkSymbol (keyword_if);
         result.cond_expr = parse_expr ();
         checkSymbol (keyword_then);
         result.then_stat = parse_inner_stat ();
         if (isSymbol (keyword_else))
         {
            checkSymbol (keyword_else);
            result.else_stat = parse_inner_stat ();
         }
         return result;
   }

   public TCaseStat parse_case_stat ()
   {

         TCaseStat result = new TCaseStat ();
         storeLocation (result);
         checkSymbol (keyword_case);
         result.case_expr = parse_expr ();
         checkSymbol (keyword_of);
         result.case_list = parse_case_sect ();
         if (isSymbol (keyword_else))
         {
            checkSymbol (keyword_else);
            result.else_seq = parse_stat_list ();
         }
         checkSymbol (keyword_end);
         return result;
   }

   public TCaseSect parse_case_sect ()
   {

         TCaseSect result = new TCaseSect ();
         storeLocation (result);
         result.items.resize (result.items.length + 1);
         result.items [result.items.length - 1] = (parse_case_item ());
         while (isSymbol (SEMICOLON))
         {
            checkSymbol (SEMICOLON);
            result.items.resize (result.items.length + 1);
            result.items [result.items.length - 1] = (parse_case_item ());
         }
         return result;
   }

   public TCaseItem parse_case_item ()
   {

         TCaseItem result = new TCaseItem ();
         storeLocation (result);
         result.sel_list = parse_elem_sect ();
         checkSymbol (COLON);
         result.sel_stat = parse_inner_stat ();
         return result;
   }

   public TWhileStat parse_while_stat ()
   {

         TWhileStat result = new TWhileStat ();
         storeLocation (result);
         checkSymbol (keyword_while);
         result.cond_expr = parse_expr ();
         checkSymbol (keyword_do);
         result.body_stat = parse_inner_stat ();
         return result;
   }

   public TRepeatStat parse_repeat_stat ()
   {

         TRepeatStat result = new TRepeatStat ();
         storeLocation (result);
         checkSymbol (keyword_repeat);
         result.body_seq = parse_stat_list ();
         checkSymbol (keyword_until);
         result.until_expr = parse_expr ();
         return result;
   }

   public TForStat parse_for_stat ()
   {

         TForStat result = new TForStat ();
         storeLocation (result);
         checkSymbol (keyword_for);
         result.var_expr = parse_variable ();
         checkSymbol (ASSIGN);
         result.from_expr = parse_expr ();
         if (isSymbol (keyword_to))
         {
            checkSymbol (keyword_to);
            result.incr = true;
         }
         else if (isSymbol (keyword_downto))
         {
            checkSymbol (keyword_downto);
            result.incr = false;
         }
         else {
            stop ("Unexpected token");
         }
         result.to_expr = parse_expr ();
         checkSymbol (keyword_do);
         result.body_stat = parse_inner_stat ();
         return result;
   }

   public TWithStat parse_with_stat ()
   {

         TWithStat result = new TWithStat ();
         storeLocation (result);
         checkSymbol (keyword_with);
         result.with_list = parse_with_sect ();
         checkSymbol (keyword_do);
         result.body_stat = parse_inner_stat ();
         return result;
   }

   public TWithSect parse_with_sect ()
   {

         TWithSect result = new TWithSect ();
         storeLocation (result);
         result.items.resize (result.items.length + 1);
         result.items [result.items.length - 1] = (parse_with_item ());
         while (isSymbol (COMMA))
         {
            checkSymbol (COMMA);
            result.items.resize (result.items.length + 1);
            result.items [result.items.length - 1] = (parse_with_item ());
         }
         return result;
   }

   public TWithItem parse_with_item ()
   {

         TWithItem result = new TWithItem ();
         storeLocation (result);
         result.expr = parse_variable ();
         return result;
   }

   public TRaiseStat parse_raise_stat ()
   {

         TRaiseStat result = new TRaiseStat ();
         storeLocation (result);
         checkSymbol (keyword_raise);
         if (testSymbols (set_4))
         {
            result.raise_expr = parse_expr ();
         }
         return result;
   }

   public TTryStat parse_try_stat ()
   {

         TTryStat result = new TTryStat ();
         storeLocation (result);
         checkSymbol (keyword_try);
         result.body_seq = parse_stat_list ();
         if (isSymbol (keyword_finally))
         {
            result.finally_branch = parse_finally_part ();
         }
         else if (isSymbol (keyword_except))
         {
            result.except_branch = parse_except_part ();
         }
         else {
            stop ("Unexpected token");
         }
         checkSymbol (keyword_end);
         return result;
   }

   public TFinallyPart parse_finally_part ()
   {

         TFinallyPart result = new TFinallyPart ();
         storeLocation (result);
         checkSymbol (keyword_finally);
         result.finally_seq = parse_stat_list ();
         return result;
   }

   public TExceptPart parse_except_part ()
   {

         TExceptPart result = new TExceptPart ();
         storeLocation (result);
         checkSymbol (keyword_except);
         if (isSymbol (keyword_on))
         {
            result.on_list = parse_on_sect ();
            if (isSymbol (keyword_else))
            {
               checkSymbol (keyword_else);
               result.else_seq = parse_stat_list ();
            }
         }
         else if (testSymbols (set_5))
         {
            result.else_seq = parse_stat_list ();
         }
         else {
            stop ("Unexpected token");
         }
         return result;
   }

   public TOnSect parse_on_sect ()
   {

         TOnSect result = new TOnSect ();
         storeLocation (result);
         result.items.resize (result.items.length + 1);
         result.items [result.items.length - 1] = (parse_on_item ());
         while (isSymbol (SEMICOLON))
         {
            checkSymbol (SEMICOLON);
            result.items.resize (result.items.length + 1);
            result.items [result.items.length - 1] = (parse_on_item ());
         }
         if (isSymbol (SEMICOLON))
         {
            checkSymbol (SEMICOLON);
            result.semicolon = true;
         }
         return result;
   }

   public TOnItem parse_on_item ()
   {

         TOnItem result = new TOnItem ();
         storeLocation (result);
         checkSymbol (keyword_on);
         if (isSymbol (identifier))
         {
            result.on_ident = readIdent ();
            checkSymbol (COLON);
         }
         result.on_type = parse_type ();
         checkSymbol (keyword_do);
         result.body_stat = parse_inner_stat ();
         return result;
   }

   public TEmptyStat parse_empty_stat ()
   {

         TEmptyStat result = new TEmptyStat ();
         storeLocation (result);
         return result;
   }

   public TStat parse_simple_stat ()
   {

         TStat result = null;
         TExpr result0 = parse_expr ();
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

   public TAssignStat parse_assign_stat (TExpr store)
   {

         TAssignStat result = new TAssignStat ();
         storeLocation (result);
         result.left_expr = store;
         checkSymbol (ASSIGN);
         result.right_expr = parse_expr ();
         return result;
   }

   public TCallStat parse_call_stat (TExpr store)
   {

         TCallStat result = new TCallStat ();
         storeLocation (result);
         result.call_expr = store;
         return result;
   }

   public TLabeledTStat parse_labeled_stat ()
   {

         TLabeledTStat result = new TLabeledTStat ();
         storeLocation (result);
         result.lab = parse_label_ident ();
         checkSymbol (COLON);
         result.body = parse_stat ();
         return result;
   }

   public TStat parse_stat ()
   {

         TStat result = null;
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

   public TParamIdent parse_param_ident ()
   {

         TParamIdent result = new TParamIdent ();
         storeLocation (result);
         result.name = readIdent ();
         on_param (result);
         return result;
   }

   public TParamItem parse_param_item ()
   {

         TParamItem result = new TParamItem ();
         storeLocation (result);
         if (isSymbol (keyword_var))
         {
            checkSymbol (keyword_var);
            result.mode = VarParam;
         }
         else if (isSymbol (keyword_const))
         {
            checkSymbol (keyword_const);
            result.mode = ConstParam;
         }
         else if (isSymbol (keyword_out))
         {
            checkSymbol (keyword_out);
            result.mode = OutParam;
         }
         else
         {
            result.mode = ValueParam;
         }
         result.items.resize (result.items.length + 1);
         result.items [result.items.length - 1] = (parse_param_ident ());
         while (isSymbol (COMMA))
         {
            checkSymbol (COMMA);
            result.items.resize (result.items.length + 1);
            result.items [result.items.length - 1] = (parse_param_ident ());
         }
         if (isSymbol (COLON))
         {
            checkSymbol (COLON);
            result.typ = parse_param_type ();
            if (isSymbol (EQUAL))
            {
               checkSymbol (EQUAL);
               result.ini = parse_expr ();
            }
         }
         add_param (result);
         return result;
   }

   public TParamSect parse_formal_param_list ()
   {

         TParamSect result = new TParamSect ();
         storeLocation (result);
         if (isSymbol (LPAREN))
         {
            checkSymbol (LPAREN);
            result.items.resize (result.items.length + 1);
            result.items [result.items.length - 1] = (parse_param_item ());
            while (isSymbol (SEMICOLON))
            {
               checkSymbol (SEMICOLON);
               result.items.resize (result.items.length + 1);
               result.items [result.items.length - 1] = (parse_param_item ());
            }
            checkSymbol (RPAREN);
         }
         return result;
   }

   public TParamSect parse_property_param_list ()
   {

         TParamSect result = new TParamSect ();
         storeLocation (result);
         checkSymbol (LBRACKET);
         result.items.resize (result.items.length + 1);
         result.items [result.items.length - 1] = (parse_param_item ());
         while (isSymbol (SEMICOLON))
         {
            checkSymbol (SEMICOLON);
            result.items.resize (result.items.length + 1);
            result.items [result.items.length - 1] = (parse_param_item ());
         }
         checkSymbol (RBRACKET);
         return result;
   }

   public TClassType parse_class_type ()
   {

         TClassType result = new TClassType ();
         storeLocation (result);
         open_class (result);
         checkSymbol (keyword_class);
         if (isSymbol (LPAREN))
         {
            checkSymbol (LPAREN);
            result.parent = parse_ifc_type ();
            if (isSymbol (COMMA))
            {
               checkSymbol (COMMA);
               result.ifc_list = parse_interface_sect ();
            }
            checkSymbol (RPAREN);
         }
         result.components = parse_components_sect ();
         checkSymbol (keyword_end);
         close_class (result);
         return result;
   }

   public TInterfaceType parse_interface_type ()
   {

         TInterfaceType result = new TInterfaceType ();
         storeLocation (result);
         open_interface (result);
         checkSymbol (keyword_interface);
         if (isSymbol (LPAREN))
         {
            checkSymbol (LPAREN);
            result.ifc_list = parse_interface_sect ();
            checkSymbol (RPAREN);
         }
         result.components = parse_components_sect ();
         checkSymbol (keyword_end);
         close_interface (result);
         return result;
   }

   public TInterfaceSect parse_interface_sect ()
   {

         TInterfaceSect result = new TInterfaceSect ();
         storeLocation (result);
         result.items.resize (result.items.length + 1);
         result.items [result.items.length - 1] = (parse_interface_item ());
         while (isSymbol (COMMA))
         {
            checkSymbol (COMMA);
            result.items.resize (result.items.length + 1);
            result.items [result.items.length - 1] = (parse_interface_item ());
         }
         return result;
   }

   public TIntefaceItem parse_interface_item ()
   {

         TIntefaceItem result = new TIntefaceItem ();
         storeLocation (result);
         result.ifc = parse_ifc_type ();
         return result;
   }

   public TComponetsSect parse_components_sect ()
   {

         TComponetsSect result = new TComponetsSect ();
         storeLocation (result);
         result.items.resize (result.items.length + 1);
         result.items [result.items.length - 1] = (parse_components_first_item ());
         while (testSymbols (set_6))
         {
            result.items.resize (result.items.length + 1);
            result.items [result.items.length - 1] = (parse_components_item ());
         }
         return result;
   }

   public TComponentsItem parse_components_item ()
   {

         TComponentsItem result = new TComponentsItem ();
         storeLocation (result);
         if (isSymbol (keyword_private))
         {
            checkSymbol (keyword_private);
            result.acs = PrivateAccess;
         }
         else if (isSymbol (keyword_protected))
         {
            checkSymbol (keyword_protected);
            result.acs = ProtectedAccess;
         }
         else if (isSymbol (keyword_public))
         {
            checkSymbol (keyword_public);
            result.acs = PublicAccess;
         }
         else if (isSymbol (keyword_published))
         {
            checkSymbol (keyword_published);
            result.acs = PublishedAccess;
         }
         else if (isSymbol (keyword_automated))
         {
            checkSymbol (keyword_automated);
            result.acs = AutomatedAccess;
         }
         else {
            stop ("Unexpected token");
         }
         result.members = parse_member_sect ();
         return result;
   }

   public TComponentsItem parse_components_first_item ()
   {

         TComponentsItem result = new TComponentsItem ();
         storeLocation (result);
         result.acs = PublicAccess;
         result.members = parse_member_sect ();
         return result;
   }

   public TDeclGroup parse_member_sect ()
   {

         TDeclGroup result = new TDeclGroup ();
         storeLocation (result);
         while (testSymbols (set_7))
         {
            result.items.resize (result.items.length + 1);
            result.items [result.items.length - 1] = (parse_member_decl ());
         }
         return result;
   }

   public TDeclSect parse_member_decl ()
   {

         TDeclSect result = null;
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

   public TFieldItem parse_field_ident ()
   {

         TFieldItem result = new TFieldItem ();
         storeLocation (result);
         result.name = readIdent ();
         on_field (result);
         return result;
   }

   public TFieldDecl parse_field_decl ()
   {

         TFieldDecl result = new TFieldDecl ();
         storeLocation (result);
         result.items.resize (result.items.length + 1);
         result.items [result.items.length - 1] = (parse_field_ident ());
         while (isSymbol (COMMA))
         {
            checkSymbol (COMMA);
            result.items.resize (result.items.length + 1);
            result.items [result.items.length - 1] = (parse_field_ident ());
         }
         checkSymbol (COLON);
         result.typ = parse_type ();
         checkSymbol (SEMICOLON);
         add_field (result);
         return result;
   }

   public TProcDecl parse_method_decl ()
   {

         TProcDecl result = new TProcDecl ();
         storeLocation (result);
         open_proc (result);
         parse_proc_head (result);
         while (isSymbol (keyword_virtual) || isSymbol (keyword_dynamic) || isSymbol (keyword_override) || isSymbol (keyword_abstract))
         {
            if (isSymbol (keyword_virtual))
            {
               checkSymbol (keyword_virtual);
               result.a_virtual = true;
               checkSymbol (SEMICOLON);
            }
            else if (isSymbol (keyword_dynamic))
            {
               checkSymbol (keyword_dynamic);
               result.a_dynamic = true;
               checkSymbol (SEMICOLON);
            }
            else if (isSymbol (keyword_override))
            {
               checkSymbol (keyword_override);
               result.a_override = true;
               checkSymbol (SEMICOLON);
            }
            else if (isSymbol (keyword_abstract))
            {
               checkSymbol (keyword_abstract);
               result.a_abstract = true;
               checkSymbol (SEMICOLON);
            }
            else {
               stop ("Unexpected token");
            }
         }
         close_proc (result);
         return result;
   }

   public TPropertyDecl parse_property_decl ()
   {

         TPropertyDecl result = new TPropertyDecl ();
         storeLocation (result);
         checkSymbol (keyword_property);
         result.name = readIdent ();
         if (isSymbol (LBRACKET))
         {
            result.param_list = parse_property_param_list ();
         }
         if (isSymbol (COLON))
         {
            checkSymbol (COLON);
            result.typ = parse_result_type ();
         }
         if (isSymbol (keyword_read))
         {
            checkSymbol (keyword_read);
            result.a_read = parse_expr ();
         }
         if (isSymbol (keyword_write))
         {
            checkSymbol (keyword_write);
            result.a_write = parse_expr ();
         }
         if (isSymbol (keyword_stored))
         {
            checkSymbol (keyword_stored);
            result.a_stored = true;
         }
         if (isSymbol (keyword_default))
         {
            checkSymbol (keyword_default);
            result.a_default = true;
         }
         if (isSymbol (keyword_nodefault))
         {
            checkSymbol (keyword_nodefault);
            result.a_nodefault = true;
         }
         if (isSymbol (keyword_implements))
         {
            checkSymbol (keyword_implements);
            result.a_implements = parse_interface_sect ();
         }
         if (isSymbol (SEMICOLON))
         {
            checkSymbol (SEMICOLON);
            checkSymbol (keyword_default);
            result.a_def_array = true;
         }
         checkSymbol (SEMICOLON);
         return result;
   }

   public TEnumType parse_enum_type ()
   {

         TEnumType result = new TEnumType ();
         storeLocation (result);
         simple_type (result);
         checkSymbol (LPAREN);
         result.elements = parse_enum_sect ();
         checkSymbol (RPAREN);
         return result;
   }

   public TEnumSect parse_enum_sect ()
   {

         TEnumSect result = new TEnumSect ();
         storeLocation (result);
         result.items.resize (result.items.length + 1);
         result.items [result.items.length - 1] = (parse_enum_item ());
         while (isSymbol (COMMA))
         {
            checkSymbol (COMMA);
            result.items.resize (result.items.length + 1);
            result.items [result.items.length - 1] = (parse_enum_item ());
         }
         return result;
   }

   public TEnumItem parse_enum_item ()
   {

         TEnumItem result = new TEnumItem ();
         storeLocation (result);
         result.name = readIdent ();
         return result;
   }

   public TStringType parse_string_type ()
   {

         TStringType result = new TStringType ();
         storeLocation (result);
         simple_type (result);
         checkSymbol (keyword_string);
         if (isSymbol (LBRACKET))
         {
            checkSymbol (LBRACKET);
            result.lim = parse_expr ();
            checkSymbol (RBRACKET);
         }
         return result;
   }

   public TArrayType parse_array_type ()
   {

         TArrayType result = new TArrayType ();
         storeLocation (result);
         simple_type (result);
         checkSymbol (keyword_array);
         if (isSymbol (LBRACKET))
         {
            checkSymbol (LBRACKET);
            result.index_list = parse_index_type_sect ();
            checkSymbol (RBRACKET);
         }
         checkSymbol (keyword_of);
         result.elem = parse_type ();
         return result;
   }

   public TIndexTypeSect parse_index_type_sect ()
   {

         TIndexTypeSect result = new TIndexTypeSect ();
         storeLocation (result);
         result.items.resize (result.items.length + 1);
         result.items [result.items.length - 1] = (parse_index_type_item ());
         while (isSymbol (COMMA))
         {
            checkSymbol (COMMA);
            result.items.resize (result.items.length + 1);
            result.items [result.items.length - 1] = (parse_index_type_item ());
         }
         return result;
   }

   public TIndexTypeItem parse_index_type_item ()
   {

         TIndexTypeItem result = new TIndexTypeItem ();
         storeLocation (result);
         result.index = parse_type ();
         return result;
   }

   public TRecordType parse_record_type ()
   {

         TRecordType result = new TRecordType ();
         storeLocation (result);
         simple_type (result);
         if (isSymbol (keyword_packed))
         {
            checkSymbol (keyword_packed);
            result.a_packed = true;
         }
         checkSymbol (keyword_record);
         result.fields = parse_field_sect ();
         checkSymbol (keyword_end);
         return result;
   }

   public TFieldDeclGroup parse_field_sect ()
   {

         TFieldDeclGroup result = new TFieldDeclGroup ();
         storeLocation (result);
         while (isSymbol (identifier))
         {
            result.items.resize (result.items.length + 1);
            result.items [result.items.length - 1] = (parse_field_decl ());
         }
         return result;
   }

   public TPointerType parse_pointer_type ()
   {

         TPointerType result = new TPointerType ();
         storeLocation (result);
         simple_type (result);
         checkSymbol (ARROW);
         result.elem = parse_type ();
         return result;
   }

   public TSetType parse_set_type ()
   {

         TSetType result = new TSetType ();
         storeLocation (result);
         simple_type (result);
         checkSymbol (keyword_set);
         checkSymbol (keyword_of);
         result.elem = parse_type ();
         return result;
   }

   public TFileType parse_file_type ()
   {

         TFileType result = new TFileType ();
         storeLocation (result);
         simple_type (result);
         checkSymbol (keyword_file);
         if (isSymbol (keyword_of))
         {
            checkSymbol (keyword_of);
            result.elem = parse_type ();
         }
         return result;
   }

   public TClassOfType parse_class_of_type ()
   {

         TClassOfType result = new TClassOfType ();
         storeLocation (result);
         simple_type (result);
         checkSymbol (keyword_class);
         checkSymbol (keyword_of);
         result.elem = parse_type ();
         return result;
   }

   public TProcType parse_proc_type ()
   {

         TProcType result = new TProcType ();
         storeLocation (result);
         simple_type (result);
         if (isSymbol (keyword_procedure))
         {
            checkSymbol (keyword_procedure);
            result.style = ProcedureStyle;
         }
         else if (isSymbol (keyword_function))
         {
            checkSymbol (keyword_function);
            result.style = FunctionStyle;
         }
         else {
            stop ("Unexpected token");
         }
         result.param_list = parse_formal_param_list ();
         if (isSymbol (COLON))
         {
            checkSymbol (COLON);
            result.answer = parse_result_type ();
         }
         if (isSymbol (keyword_of))
         {
            checkSymbol (keyword_of);
            checkSymbol (keyword_object);
            result.of_object = true;
         }
         if (isSymbol (keyword_register) || isSymbol (keyword_pascal) || isSymbol (keyword_cdecl) || isSymbol (keyword_stdcall) || isSymbol (keyword_safecall))
         {
            if (isSymbol (keyword_register))
            {
               checkSymbol (keyword_register);
               result.call_conv = RegisterCall;
            }
            else if (isSymbol (keyword_pascal))
            {
               checkSymbol (keyword_pascal);
               result.call_conv = PascalCall;
            }
            else if (isSymbol (keyword_cdecl))
            {
               checkSymbol (keyword_cdecl);
               result.call_conv = CdeclCall;
            }
            else if (isSymbol (keyword_stdcall))
            {
               checkSymbol (keyword_stdcall);
               result.call_conv = StdcallCall;
            }
            else if (isSymbol (keyword_safecall))
            {
               checkSymbol (keyword_safecall);
               result.call_conv = SafecallCall;
            }
            else {
               stop ("Unexpected token");
            }
         }
         return result;
   }

   public TSubrangeType parse_range_type ()
   {

         TSubrangeType result = new TSubrangeType ();
         storeLocation (result);
         simple_type (result);
         result.low = parse_simple_expr ();
         checkSymbol (RANGE);
         result.high = parse_simple_expr ();
         return result;
   }

   public TAliasType parse_alias_type ()
   {

         TAliasType result = new TAliasType ();
         storeLocation (result);
         simple_type (result);
         result.alias_name = parse_qualified_name ();
         return result;
   }

   public TType parse_type ()
   {

         TType result = null;
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

   public TLabelDecl parse_label_decl ()
   {

         TLabelDecl result = new TLabelDecl ();
         storeLocation (result);
         result.name = parse_label_ident ();
         return result;
   }

   public TLabelSect parse_label_sect ()
   {

         TLabelSect result = new TLabelSect ();
         storeLocation (result);
         checkSymbol (keyword_label);
         result.items.resize (result.items.length + 1);
         result.items [result.items.length - 1] = (parse_label_decl ());
         while (isSymbol (COMMA))
         {
            checkSymbol (COMMA);
            result.items.resize (result.items.length + 1);
            result.items [result.items.length - 1] = (parse_label_decl ());
         }
         checkSymbol (SEMICOLON);
         return result;
   }

   public TConstDecl parse_const_decl ()
   {

         TConstDecl result = new TConstDecl ();
         storeLocation (result);
         result.name = readIdent ();
         on_const (result);
         if (isSymbol (COLON))
         {
            checkSymbol (COLON);
            result.typ = parse_type ();
         }
         checkSymbol (EQUAL);
         result.val = parse_expr ();
         checkSymbol (SEMICOLON);
         add_const (result);
         return result;
   }

   public TConstSect parse_const_sect ()
   {

         TConstSect result = new TConstSect ();
         storeLocation (result);
         checkSymbol (keyword_const);
         result.items.resize (result.items.length + 1);
         result.items [result.items.length - 1] = (parse_const_decl ());
         while (isSymbol (identifier))
         {
            result.items.resize (result.items.length + 1);
            result.items [result.items.length - 1] = (parse_const_decl ());
         }
         return result;
   }

   public TTypeDecl parse_type_decl ()
   {

         TTypeDecl result = new TTypeDecl ();
         storeLocation (result);
         result.name = readIdent ();
         on_type (result);
         checkSymbol (EQUAL);
         result.typ = parse_type ();
         checkSymbol (SEMICOLON);
         add_type (result);
         return result;
   }

   public TTypeSect parse_type_sect ()
   {

         TTypeSect result = new TTypeSect ();
         storeLocation (result);
         checkSymbol (keyword_type);
         result.items.resize (result.items.length + 1);
         result.items [result.items.length - 1] = (parse_type_decl ());
         while (isSymbol (identifier))
         {
            result.items.resize (result.items.length + 1);
            result.items [result.items.length - 1] = (parse_type_decl ());
         }
         return result;
   }

   public TVarItem parse_var_item ()
   {

         TVarItem result = new TVarItem ();
         storeLocation (result);
         result.name = readIdent ();
         on_var (result);
         return result;
   }

   public TVarDecl parse_var_decl ()
   {

         TVarDecl result = new TVarDecl ();
         storeLocation (result);
         result.items.resize (result.items.length + 1);
         result.items [result.items.length - 1] = (parse_var_item ());
         while (isSymbol (COMMA))
         {
            checkSymbol (COMMA);
            result.items.resize (result.items.length + 1);
            result.items [result.items.length - 1] = (parse_var_item ());
         }
         checkSymbol (COLON);
         result.typ = parse_type ();
         if (isSymbol (EQUAL))
         {
            checkSymbol (EQUAL);
            result.ini = parse_expr ();
         }
         checkSymbol (SEMICOLON);
         add_var (result);
         return result;
   }

   public TVarSect parse_var_sect ()
   {

         TVarSect result = new TVarSect ();
         storeLocation (result);
         checkSymbol (keyword_var);
         result.items.resize (result.items.length + 1);
         result.items [result.items.length - 1] = (parse_var_decl ());
         while (isSymbol (identifier))
         {
            result.items.resize (result.items.length + 1);
            result.items [result.items.length - 1] = (parse_var_decl ());
         }
         return result;
   }

   public TProcDecl parse_proc_head (TProcDecl result)
   {

         if (isSymbol (keyword_class))
         {
            checkSymbol (keyword_class);
            result.a_static = true;
         }
         if (isSymbol (keyword_procedure))
         {
            checkSymbol (keyword_procedure);
            result.style = ProcedureStyle;
         }
         else if (isSymbol (keyword_function))
         {
            checkSymbol (keyword_function);
            result.style = FunctionStyle;
         }
         else if (isSymbol (keyword_constructor))
         {
            checkSymbol (keyword_constructor);
            result.style = ConstructorStyle;
         }
         else if (isSymbol (keyword_destructor))
         {
            checkSymbol (keyword_destructor);
            result.style = DestructorStyle;
         }
         else {
            stop ("Unexpected token");
         }
         result.proc_name = parse_qualified_name ();
         on_proc (result);
         result.param_list = parse_formal_param_list ();
         if (isSymbol (COLON))
         {
            checkSymbol (COLON);
            result.answer = parse_result_type ();
         }
         checkSymbol (SEMICOLON);
         return result;
   }

   public TProcDecl parse_proc_decl ()
   {

         TProcDecl result = new TProcDecl ();
         storeLocation (result);
         open_proc (result);
         parse_proc_head (result);
         if (isSymbol (keyword_forward))
         {
            checkSymbol (keyword_forward);
            result.a_forward = true;
         }
         else if (isSymbol (keyword_external))
         {
            parse_proc_external (result);
            result.external_spec = true;
         }
         else if (testSymbols (set_11))
         {
            if (isSymbol (keyword_inline))
            {
               checkSymbol (keyword_inline);
               checkSymbol (SEMICOLON);
               result.a_inline = true;
            }
            result.local = parse_decl_part ();
            on_begin_proc (result);
            checkSymbol (keyword_begin);
            result.body = parse_stat_list ();
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

   public TProcDecl parse_proc_external (TProcDecl result)
   {

         checkSymbol (keyword_external);
         result.a_external = true;
         if (testSymbols (set_4))
         {
            result.a_lib = parse_expr ();
         }
         checkSymbol (SEMICOLON);
         return result;
   }

   public TProcDecl parse_proc_intf_decl ()
   {

         TProcDecl result = new TProcDecl ();
         storeLocation (result);
         open_proc (result);
         parse_proc_head (result);
         if (isSymbol (keyword_inline))
         {
            checkSymbol (keyword_inline);
            checkSymbol (SEMICOLON);
            result.a_inline = true;
         }
         if (isSymbol (keyword_external))
         {
            parse_proc_external (result);
            result.external_spec = true;
         }
         close_proc (result);
         return result;
   }

   public TDeclSect parse_intf_decl ()
   {

         TDeclSect result = null;
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

   public TDeclGroup parse_intf_decl_part ()
   {

         TDeclGroup result = new TDeclGroup ();
         storeLocation (result);
         while (testSymbols (set_12))
         {
            result.items.resize (result.items.length + 1);
            result.items [result.items.length - 1] = (parse_intf_decl ());
         }
         return result;
   }

   public TDeclSect parse_decl ()
   {

         TDeclSect result = null;
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

   public TDeclGroup parse_decl_part ()
   {

         TDeclGroup result = new TDeclGroup ();
         storeLocation (result);
         while (testSymbols (set_13))
         {
            result.items.resize (result.items.length + 1);
            result.items [result.items.length - 1] = (parse_decl ());
         }
         return result;
   }

   public TImportItem parse_import_item ()
   {

         TImportItem result = new TImportItem ();
         storeLocation (result);
         result.name = readIdent ();
         on_import (result);
         if (isSymbol (keyword_in))
         {
            checkSymbol (keyword_in);
            result.path = readQuotedString ();
         }
         return result;
   }

   public TImportSect parse_import_sect ()
   {

         TImportSect result = new TImportSect ();
         storeLocation (result);
         if (isSymbol (keyword_uses))
         {
            checkSymbol (keyword_uses);
            result.items.resize (result.items.length + 1);
            result.items [result.items.length - 1] = (parse_import_item ());
            while (isSymbol (COMMA))
            {
               checkSymbol (COMMA);
               result.items.resize (result.items.length + 1);
               result.items [result.items.length - 1] = (parse_import_item ());
            }
            checkSymbol (SEMICOLON);
         }
         return result;
   }

   public TUnitModule parse_unit_decl ()
   {

         TUnitModule result = new TUnitModule ();
         storeLocation (result);
         open_module (result);
         checkSymbol (keyword_unit);
         result.name = readIdent ();
         on_module (result);
         checkSymbol (SEMICOLON);
         checkSymbol (keyword_interface);
         result.intf_imports = parse_import_sect ();
         result.intf_decl = parse_intf_decl_part ();
         checkSymbol (keyword_implementation);
         result.impl_imports = parse_import_sect ();
         result.impl_decl = parse_decl_part ();
         if (isSymbol (keyword_finalization) || isSymbol (keyword_initialization) || isSymbol (keyword_begin))
         {
            if (isSymbol (keyword_begin))
            {
               checkSymbol (keyword_begin);
               result.init = parse_stat_list ();
            }
            else if (isSymbol (keyword_finalization) || isSymbol (keyword_initialization))
            {
               if (isSymbol (keyword_initialization))
               {
                  checkSymbol (keyword_initialization);
                  result.init = parse_stat_list ();
               }
               if (isSymbol (keyword_finalization))
               {
                  checkSymbol (keyword_finalization);
                  result.finish = parse_stat_list ();
               }
               result.no_begin = true;
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

   public TProgramModule parse_program_decl ()
   {

         TProgramModule result = new TProgramModule ();
         storeLocation (result);
         open_module (result);
         checkSymbol (keyword_program);
         result.name = readIdent ();
         on_module (result);
         checkSymbol (SEMICOLON);
         result.impl_imports = parse_import_sect ();
         result.impl_decl = parse_decl_part ();
         checkSymbol (keyword_begin);
         result.init = parse_stat_list ();
         checkSymbol (keyword_end);
         checkSymbol (DOT);
         close_module (result);
         return result;
   }

   public TLibraryModule parse_library_decl ()
   {

         TLibraryModule result = new TLibraryModule ();
         storeLocation (result);
         open_module (result);
         checkSymbol (keyword_library);
         result.name = readIdent ();
         on_module (result);
         checkSymbol (SEMICOLON);
         result.impl_imports = parse_import_sect ();
         result.impl_decl = parse_decl_part ();
         checkSymbol (keyword_begin);
         result.init = parse_stat_list ();
         checkSymbol (keyword_end);
         checkSymbol (DOT);
         close_module (result);
         return result;
   }

   public TModule parse_module_decl ()
   {

         TModule result = null;
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

   public bool test_1 ()
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

   public bool test_2 ()
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

   public bool test_3 ()
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

   public bool test_4 ()
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

   public bool test_label_ident ()
   {
         if (token != identifier)
         {
            return false;
         }
         nextToken ();
         return true;
   }

   public bool test_range_type ()
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

   public bool test_simple_expr ()
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

   public bool test_term ()
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

   public bool test_factor ()
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

   public bool test_int_value_expr ()
   {
         if (token != number)
         {
            return false;
         }
         nextToken ();
         return true;
   }

   public bool test_float_value_expr ()
   {
         if (token != real_number)
         {
            return false;
         }
         nextToken ();
         return true;
   }

   public bool test_string_value_expr ()
   {
         if (token != string_literal)
         {
            return false;
         }
         nextToken ();
         return true;
   }

   public bool test_not_expr ()
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

   public bool test_plus_expr ()
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

   public bool test_minus_expr ()
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

   public bool test_adr_expr ()
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

   public bool test_nil_expr ()
   {
         if (token != keyword_nil)
         {
            return false;
         }
         nextToken ();
         return true;
   }

   public bool test_set_expr ()
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

   public bool test_elem_sect ()
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

   public bool test_elem_item ()
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

   public bool test_expr ()
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

   public bool test_string_type_expr ()
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

   public bool test_reference ()
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

   public bool test_variable ()
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

   public bool test_ident_expr ()
   {
         if (token != identifier)
         {
            return false;
         }
         nextToken ();
         return true;
   }

   public bool test_sub_expr ()
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

   public bool test_super_expr ()
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

   public bool test_index_expr ()
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

   public bool test_index_expr_list ()
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

   public bool test_index_expr_item ()
   {
         if (!test_expr ())
         {
            return false;
         }
         return true;
   }

   public bool test_call_expr ()
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

   public bool test_arg_list ()
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

   public bool test_arg_item ()
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

   public bool test_deref_expr ()
   {
         if (token != ARROW)
         {
            return false;
         }
         nextToken ();
         return true;
   }

   public bool test_field_expr ()
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

   public bool test_enum_type ()
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

   public bool test_enum_sect ()
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

   public bool test_enum_item ()
   {
         if (token != identifier)
         {
            return false;
         }
         nextToken ();
         return true;
   }

   public bool isSymbol (CmmSymbol sym)
   {
         return token == sym;
   }

   public void checkSymbol (CmmSymbol sym)
   {
         if (token != sym)
         {
            stop (tokenToString (sym) + " expected");
         }
         nextToken ();
   }

   public bool testSymbols (uchar [ ] table)
   {
         int pos = (int) token / 8;
         int bit = (int) token % 8;
         return (table [pos]  &  (1 << bit)) != 0;
   }

   public void stop (string msg)
   {
         error (msg);
   }

   public void stop_str ()
   {
         stop ("Unexpected " + tokenToString (token));
   }

   public void lookupKeyword ()
   {
         string s = tokenTxt;
         int n = s.length;
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
                  if (s.substring (1,2) == "nd")
                  {
                        token = keyword_and;
                  }
            }
            else if (s[0] == 'd')
            {
                  if (s.substring (1,2) == "iv")
                  {
                        token = keyword_div;
                  }
            }
            else if (s[0] == 'e')
            {
                  if (s.substring (1,2) == "nd")
                  {
                        token = keyword_end;
                  }
            }
            else if (s[0] == 'f')
            {
                  if (s.substring (1,2) == "or")
                  {
                        token = keyword_for;
                  }
            }
            else if (s[0] == 'm')
            {
                  if (s.substring (1,2) == "od")
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
                  if (s.substring (1,2) == "ut")
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
                  if (s.substring (1,2) == "ry")
                  {
                        token = keyword_try;
                  }
            }
            else if (s[0] == 'v')
            {
                  if (s.substring (1,2) == "ar")
                  {
                        token = keyword_var;
                  }
            }
            else if (s[0] == 'x')
            {
                  if (s.substring (1,2) == "or")
                  {
                        token = keyword_xor;
                  }
            }
         }
         else if (n == 4)
         {
            if (s[0] == 'c')
            {
                  if (s.substring (1,3) == "ase")
                  {
                        token = keyword_case;
                  }
            }
            else if (s[0] == 'e')
            {
                  if (s.substring (1,3) == "lse")
                  {
                        token = keyword_else;
                  }
            }
            else if (s[0] == 'f')
            {
                  if (s.substring (1,3) == "ile")
                  {
                        token = keyword_file;
                  }
            }
            else if (s[0] == 'g')
            {
                  if (s.substring (1,3) == "oto")
                  {
                        token = keyword_goto;
                  }
            }
            else if (s[0] == 'r')
            {
                  if (s.substring (1,3) == "ead")
                  {
                        token = keyword_read;
                  }
            }
            else if (s[0] == 't')
            {
                  if (s[1] == 'h')
                  {
                        if (s.substring (2,2) == "en")
                        {
                              token = keyword_then;
                        }
                  }
                  else if (s[1] == 'y')
                  {
                        if (s.substring (2,2) == "pe")
                        {
                              token = keyword_type;
                        }
                  }
            }
            else if (s[0] == 'u')
            {
                  if (s[1] == 'n')
                  {
                        if (s.substring (2,2) == "it")
                        {
                              token = keyword_unit;
                        }
                  }
                  else if (s[1] == 's')
                  {
                        if (s.substring (2,2) == "es")
                        {
                              token = keyword_uses;
                        }
                  }
            }
            else if (s[0] == 'w')
            {
                  if (s.substring (1,3) == "ith")
                  {
                        token = keyword_with;
                  }
            }
         }
         else if (n == 5)
         {
            if (s[0] == 'a')
            {
                  if (s.substring (1,4) == "rray")
                  {
                        token = keyword_array;
                  }
            }
            else if (s[0] == 'b')
            {
                  if (s.substring (1,4) == "egin")
                  {
                        token = keyword_begin;
                  }
            }
            else if (s[0] == 'c')
            {
                  if (s[1] == 'd')
                  {
                        if (s.substring (2,3) == "ecl")
                        {
                              token = keyword_cdecl;
                        }
                  }
                  else if (s[1] == 'l')
                  {
                        if (s.substring (2,3) == "ass")
                        {
                              token = keyword_class;
                        }
                  }
                  else if (s[1] == 'o')
                  {
                        if (s.substring (2,3) == "nst")
                        {
                              token = keyword_const;
                        }
                  }
            }
            else if (s[0] == 'l')
            {
                  if (s.substring (1,4) == "abel")
                  {
                        token = keyword_label;
                  }
            }
            else if (s[0] == 'r')
            {
                  if (s.substring (1,4) == "aise")
                  {
                        token = keyword_raise;
                  }
            }
            else if (s[0] == 'u')
            {
                  if (s.substring (1,4) == "ntil")
                  {
                        token = keyword_until;
                  }
            }
            else if (s[0] == 'w')
            {
                  if (s[1] == 'h')
                  {
                        if (s.substring (2,3) == "ile")
                        {
                              token = keyword_while;
                        }
                  }
                  else if (s[1] == 'r')
                  {
                        if (s.substring (2,3) == "ite")
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
                  if (s.substring (1,5) == "ownto")
                  {
                        token = keyword_downto;
                  }
            }
            else if (s[0] == 'e')
            {
                  if (s.substring (1,5) == "xcept")
                  {
                        token = keyword_except;
                  }
            }
            else if (s[0] == 'i')
            {
                  if (s.substring (1,5) == "nline")
                  {
                        token = keyword_inline;
                  }
            }
            else if (s[0] == 'o')
            {
                  if (s.substring (1,5) == "bject")
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
                              if (s.substring (3,3) == "ked")
                              {
                                    token = keyword_packed;
                              }
                        }
                        else if (s[2] == 's')
                        {
                              if (s.substring (3,3) == "cal")
                              {
                                    token = keyword_pascal;
                              }
                        }
                  }
                  else if (s[1] == 'u')
                  {
                        if (s.substring (2,4) == "blic")
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
                              if (s.substring (3,3) == "ord")
                              {
                                    token = keyword_record;
                              }
                        }
                        else if (s[2] == 'p')
                        {
                              if (s.substring (3,3) == "eat")
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
                              if (s.substring (3,3) == "red")
                              {
                                    token = keyword_stored;
                              }
                        }
                        else if (s[2] == 'r')
                        {
                              if (s.substring (3,3) == "ing")
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
                        if (s.substring (2,5) == "fault")
                        {
                              token = keyword_default;
                        }
                  }
                  else if (s[1] == 'y')
                  {
                        if (s.substring (2,5) == "namic")
                        {
                              token = keyword_dynamic;
                        }
                  }
            }
            else if (s[0] == 'f')
            {
                  if (s[1] == 'i')
                  {
                        if (s.substring (2,5) == "nally")
                        {
                              token = keyword_finally;
                        }
                  }
                  else if (s[1] == 'o')
                  {
                        if (s.substring (2,5) == "rward")
                        {
                              token = keyword_forward;
                        }
                  }
            }
            else if (s[0] == 'l')
            {
                  if (s.substring (1,6) == "ibrary")
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
                              if (s.substring (3,4) == "vate")
                              {
                                    token = keyword_private;
                              }
                        }
                        else if (s[2] == 'o')
                        {
                              if (s.substring (3,4) == "gram")
                              {
                                    token = keyword_program;
                              }
                        }
                  }
            }
            else if (s[0] == 's')
            {
                  if (s.substring (1,6) == "tdcall")
                  {
                        token = keyword_stdcall;
                  }
            }
            else if (s[0] == 'v')
            {
                  if (s.substring (1,6) == "irtual")
                  {
                        token = keyword_virtual;
                  }
            }
         }
         else if (n == 8)
         {
            if (s[0] == 'a')
            {
                  if (s.substring (1,7) == "bstract")
                  {
                        token = keyword_abstract;
                  }
            }
            else if (s[0] == 'e')
            {
                  if (s.substring (1,7) == "xternal")
                  {
                        token = keyword_external;
                  }
            }
            else if (s[0] == 'f')
            {
                  if (s.substring (1,7) == "unction")
                  {
                        token = keyword_function;
                  }
            }
            else if (s[0] == 'o')
            {
                  if (s.substring (1,7) == "verride")
                  {
                        token = keyword_override;
                  }
            }
            else if (s[0] == 'p')
            {
                  if (s.substring (1,7) == "roperty")
                  {
                        token = keyword_property;
                  }
            }
            else if (s[0] == 'r')
            {
                  if (s.substring (1,7) == "egister")
                  {
                        token = keyword_register;
                  }
            }
            else if (s[0] == 's')
            {
                  if (s.substring (1,7) == "afecall")
                  {
                        token = keyword_safecall;
                  }
            }
         }
         else if (n == 9)
         {
            if (s[0] == 'a')
            {
                  if (s.substring (1,8) == "utomated")
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
                              if (s.substring (3,6) == "erited")
                              {
                                    token = keyword_inherited;
                              }
                        }
                        else if (s[2] == 't')
                        {
                              if (s.substring (3,6) == "erface")
                              {
                                    token = keyword_interface;
                              }
                        }
                  }
            }
            else if (s[0] == 'n')
            {
                  if (s.substring (1,8) == "odefault")
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
                                    if (s.substring (4,5) == "edure")
                                    {
                                          token = keyword_procedure;
                                    }
                              }
                              else if (s[3] == 't')
                              {
                                    if (s.substring (4,5) == "ected")
                                    {
                                          token = keyword_protected;
                                    }
                              }
                        }
                  }
                  else if (s[1] == 'u')
                  {
                        if (s.substring (2,7) == "blished")
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
                  if (s.substring (1,9) == "estructor")
                  {
                        token = keyword_destructor;
                  }
            }
            else if (s[0] == 'i')
            {
                  if (s.substring (1,9) == "mplements")
                  {
                        token = keyword_implements;
                  }
            }
         }
         else if (n == 11)
         {
            if (s.substring (0,11) == "constructor")
            {
                  token = keyword_constructor;
            }
         }
         else if (n == 12)
         {
            if (s.substring (0,12) == "finalization")
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
                        if (s.substring (2,12) == "plementation")
                        {
                              token = keyword_implementation;
                        }
                  }
                  else if (s[1] == 'n')
                  {
                        if (s.substring (2,12) == "itialization")
                        {
                              token = keyword_initialization;
                        }
                  }
            }
         }
   }

   public void processSeparator ()
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
               tokenTxt = tokenTxt + inpCh.to_string ();
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
               tokenTxt = tokenTxt + inpCh.to_string ();
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
               tokenTxt = tokenTxt + inpCh.to_string ();
               nextCh ();
            }
            if (inpCh == '>')
            {
               token = UNEQUAL;
               tokenTxt = tokenTxt + inpCh.to_string ();
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
               tokenTxt = tokenTxt + inpCh.to_string ();
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

   public string tokenToString (CmmSymbol value)
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

   public override void translate ()
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

   public void storeLocation (CmmBasic item)
   {
         item.src_file = getTokenFileInx ();
         item.src_line = getTokenLine ();
         item.src_column = getTokenCol ();
   }

   public virtual void on_ident_expr (TIdentExpr item)
   {
   }

   public virtual void on_field_expr (TFieldExpr item)
   {
   }

   public virtual void on_param (TParamIdent item)
   {
   }

   public virtual void add_param (TParamItem item)
   {
   }

   public virtual void open_class (TClassType item)
   {
   }

   public virtual void close_class (TClassType item)
   {
   }

   public virtual void open_interface (TInterfaceType item)
   {
   }

   public virtual void close_interface (TInterfaceType item)
   {
   }

   public virtual void on_field (TFieldItem item)
   {
   }

   public virtual void add_field (TFieldDecl item)
   {
   }

   public virtual void open_proc (TProcDecl item)
   {
   }

   public virtual void close_proc (TProcDecl item)
   {
   }

   public virtual void simple_type (CmmBasic item)
   {
   }

   public virtual void on_const (TConstDecl item)
   {
   }

   public virtual void add_const (TConstDecl item)
   {
   }

   public virtual void on_type (TTypeDecl item)
   {
   }

   public virtual void add_type (TTypeDecl item)
   {
   }

   public virtual void on_var (TVarItem item)
   {
   }

   public virtual void add_var (TVarDecl item)
   {
   }

   public virtual void on_proc (TProcDecl item)
   {
   }

   public virtual void on_begin_proc (TProcDecl item)
   {
   }

   public virtual void on_end_proc (TProcDecl item)
   {
   }

   public virtual void on_tail_proc (TProcDecl item)
   {
   }

   public virtual void on_import (TImportItem item)
   {
   }

   public virtual void open_module (CmmBasic item)
   {
   }

   public virtual void on_module (CmmBasic item)
   {
   }

   public virtual void close_module (CmmBasic item)
   {
   }

   public Parser ()
   {
   }
}

public class TBasic : CmmBasic
{
   public int src_file;
   public int src_line;
   public int src_column;

   public TBasic ()
   {
      src_file = 0;
      src_line = 0;
      src_column = 0;
   }

   public virtual TBasic conv_TBasic ()
   {

         return this;
   }
}

public class TExpr : CmmBasic
{
   public TFce fce;

   public TExpr ()
   {
      fce = TFce.UnknownExp;
   }

   public virtual TBinaryExpr conv_TBinaryExpr ()
   {

         return null;
   }

   public virtual TIdentExpr conv_TIdentExpr ()
   {
         return null;
   }

   public virtual TIntValueExpr conv_TIntValueExpr ()
   {
         return null;
   }

   public virtual TFltValueExpr conv_TFltValueExpr ()
   {
         return null;
   }

   public virtual TStrValueExpr conv_TStrValueExpr ()
   {
         return null;
   }

   public virtual TNilExpr conv_TNilExpr ()
   {
         return null;
   }

   public virtual TStructExpr conv_TStructExpr ()
   {
         return null;
   }

   public virtual TNotExpr conv_TNotExpr ()
   {
         return null;
   }

   public virtual TPlusExpr conv_TPlusExpr ()
   {
         return null;
   }

   public virtual TMinusExpr conv_TMinusExpr ()
   {
         return null;
   }

   public virtual TAdrExpr conv_TAdrExpr ()
   {
         return null;
   }

   public virtual TSetExpr conv_TSetExpr ()
   {
         return null;
   }

   public virtual TSuperExpr conv_TSuperExpr ()
   {
         return null;
   }

   public virtual TStringExpr conv_TStringExpr ()
   {
         return null;
   }

   public virtual TIndexExpr conv_TIndexExpr ()
   {
         return null;
   }

   public virtual TCallExpr conv_TCallExpr ()
   {
         return null;
   }

   public virtual TDerefExpr conv_TDerefExpr ()
   {
         return null;
   }

   public virtual TFieldExpr conv_TFieldExpr ()
   {
         return null;
   }

   public virtual TTermExpr conv_TTermExpr ()
   {
         return null;
   }

   public virtual TSimpleExpr conv_TSimpleExpr ()
   {
         return null;
   }

   public virtual TCompleteExpr conv_TCompleteExpr ()
   {
         return null;
   }

   public virtual TExpr conv_TExpr ()
   {
         return this;
   }
}

public class TBinaryExpr : TExpr
{
   public TExpr left;
   public TExpr right;

   public TBinaryExpr ()
   {
      left = null;
      right = null;
   }

   public override TBinaryExpr conv_TBinaryExpr ()
   {

         return this;
   }
}

public class TComponentsItem : CmmBasic
{
   public TAccess acs;
   public TDeclGroup members;

   public TComponentsItem ()
   {
      acs = TAccess.PrivateAccess;
      members = null;
   }

   public virtual TComponentsItem conv_TComponentsItem ()
   {

         return this;
   }
}

public class TParamItem : CmmBasic
{
   public TParamMode mode;
   public TParamIdent [] items;
   public TType typ;
   public TExpr ini;

   public TParamItem ()
   {
      mode = TParamMode.VarParam;
      items = new TParamIdent [] { };
      typ = null;
      ini = null;
   }

   public virtual TParamItem conv_TParamItem ()
   {

         return this;
   }
}

public class TModule : CmmBasic
{
   public TImportSect intf_imports;
   public TImportSect impl_imports;
   public TDeclGroup intf_decl;
   public TDeclGroup impl_decl;
   public TStatSeq init;
   public TStatSeq finish;

   public TModule ()
   {
      intf_imports = null;
      impl_imports = null;
      intf_decl = null;
      impl_decl = null;
      init = null;
      finish = null;
   }

   public virtual TUnitModule conv_TUnitModule ()
   {

         return null;
   }

   public virtual TProgramModule conv_TProgramModule ()
   {
         return null;
   }

   public virtual TLibraryModule conv_TLibraryModule ()
   {
         return null;
   }

   public virtual TModule conv_TModule ()
   {
         return this;
   }
}

public class TLabelIdent : CmmBasic
{
   public string id;

   public TLabelIdent ()
   {
      id = "";
   }

   public virtual TLabelIdent conv_TLabelIdent ()
   {

         return this;
   }
}

public class TQualName : CmmBasic
{
   public string id;
   public TContName [] items;

   public TQualName ()
   {
      id = "";
      items = new TContName [] { };
   }

   public virtual TQualName conv_TQualName ()
   {

         return this;
   }
}

public class TContName : CmmBasic
{
   public string id;

   public TContName ()
   {
      id = "";
   }

   public virtual TContName conv_TContName ()
   {

         return this;
   }
}

public class TType : CmmBasic
{

   public TType ()
   {
   }

   public virtual TAliasType conv_TAliasType ()
   {
         return null;
   }

   public virtual TStringType conv_TStringType ()
   {
         return null;
   }

   public virtual TFileType conv_TFileType ()
   {
         return null;
   }

   public virtual TClassType conv_TClassType ()
   {
         return null;
   }

   public virtual TInterfaceType conv_TInterfaceType ()
   {
         return null;
   }

   public virtual TEnumType conv_TEnumType ()
   {
         return null;
   }

   public virtual TArrayType conv_TArrayType ()
   {
         return null;
   }

   public virtual TRecordType conv_TRecordType ()
   {
         return null;
   }

   public virtual TPointerType conv_TPointerType ()
   {
         return null;
   }

   public virtual TSetType conv_TSetType ()
   {
         return null;
   }

   public virtual TClassOfType conv_TClassOfType ()
   {
         return null;
   }

   public virtual TProcType conv_TProcType ()
   {
         return null;
   }

   public virtual TSubrangeType conv_TSubrangeType ()
   {
         return null;
   }

   public virtual TType conv_TType ()
   {
         return this;
   }
}

public class TAliasType : TType
{
   public TQualName alias_name;

   public TAliasType ()
   {
      alias_name = null;
   }

   public override TAliasType conv_TAliasType ()
   {

         return this;
   }
}

public class TStringType : TType
{
   public TExpr lim;

   public TStringType ()
   {
      lim = null;
   }

   public override TStringType conv_TStringType ()
   {

         return this;
   }
}

public class TFileType : TType
{
   public TType elem;

   public TFileType ()
   {
      elem = null;
   }

   public override TFileType conv_TFileType ()
   {

         return this;
   }
}

public class TInxItem : CmmBasic
{
   public TExpr ref;

   public TInxItem ()
   {
      ref = null;
   }

   public virtual TInxItem conv_TInxItem ()
   {

         return this;
   }
}

public class TInxList : CmmBasic
{
   public TInxItem [] items;

   public TInxList ()
   {
      items = new TInxItem [] { };
   }

   public virtual TInxList conv_TInxList ()
   {

         return this;
   }
}

public class TArgItem : CmmBasic
{
   public TExpr value;
   public TExpr width;
   public TExpr digits;

   public TArgItem ()
   {
      value = null;
      width = null;
      digits = null;
   }

   public virtual TArgItem conv_TArgItem ()
   {

         return this;
   }
}

public class TArgSect : CmmBasic
{
   public TArgItem [] items;

   public TArgSect ()
   {
      items = new TArgItem [] { };
   }

   public virtual TArgSect conv_TArgSect ()
   {

         return this;
   }
}

public class TElemSect : CmmBasic
{
   public TElemItem [] items;

   public TElemSect ()
   {
      items = new TElemItem [] { };
   }

   public virtual TElemSect conv_TElemSect ()
   {

         return this;
   }
}

public class TElemItem : CmmBasic
{
   public TExpr low;
   public TExpr high;

   public TElemItem ()
   {
      low = null;
      high = null;
   }

   public virtual TElemItem conv_TElemItem ()
   {

         return this;
   }
}

public class TStructSect : CmmBasic
{
   public string name;
   public TExpr value;
   public TStructSect [] items;

   public TStructSect ()
   {
      name = "";
      value = null;
      items = new TStructSect [] { };
   }

   public virtual TStructSect conv_TStructSect ()
   {

         return this;
   }
}

public class TIdentExpr : TExpr
{
   public string name;

   public TIdentExpr ()
   {
      name = "";
   }

   public override TIdentExpr conv_TIdentExpr ()
   {

         return this;
   }
}

public class TIntValueExpr : TExpr
{
   public string value;

   public TIntValueExpr ()
   {
      value = "";
   }

   public override TIntValueExpr conv_TIntValueExpr ()
   {

         return this;
   }
}

public class TFltValueExpr : TExpr
{
   public string value;

   public TFltValueExpr ()
   {
      value = "";
   }

   public override TFltValueExpr conv_TFltValueExpr ()
   {

         return this;
   }
}

public class TStrValueExpr : TExpr
{
   public string value;

   public TStrValueExpr ()
   {
      value = "";
   }

   public override TStrValueExpr conv_TStrValueExpr ()
   {

         return this;
   }
}

public class TNilExpr : TExpr
{

   public TNilExpr ()
   {
   }

   public override TNilExpr conv_TNilExpr ()
   {
         return this;
   }
}

public class TStructExpr : TExpr
{
   public TExpr value;

   public TStructExpr ()
   {
      value = null;
   }

   public override TStructExpr conv_TStructExpr ()
   {

         return this;
   }
}

public class TNotExpr : TExpr
{
   public TExpr param;

   public TNotExpr ()
   {
      param = null;
   }

   public override TNotExpr conv_TNotExpr ()
   {

         return this;
   }
}

public class TPlusExpr : TExpr
{
   public TExpr param;

   public TPlusExpr ()
   {
      param = null;
   }

   public override TPlusExpr conv_TPlusExpr ()
   {

         return this;
   }
}

public class TMinusExpr : TExpr
{
   public TExpr param;

   public TMinusExpr ()
   {
      param = null;
   }

   public override TMinusExpr conv_TMinusExpr ()
   {

         return this;
   }
}

public class TAdrExpr : TExpr
{
   public TExpr param;

   public TAdrExpr ()
   {
      param = null;
   }

   public override TAdrExpr conv_TAdrExpr ()
   {

         return this;
   }
}

public class TSetExpr : TExpr
{
   public TElemSect list;

   public TSetExpr ()
   {
      list = null;
   }

   public override TSetExpr conv_TSetExpr ()
   {

         return this;
   }
}

public class TSuperExpr : TExpr
{
   public string name;

   public TSuperExpr ()
   {
      name = "";
   }

   public override TSuperExpr conv_TSuperExpr ()
   {

         return this;
   }
}

public class TStringExpr : TExpr
{
   public TExpr param;

   public TStringExpr ()
   {
      param = null;
   }

   public override TStringExpr conv_TStringExpr ()
   {

         return this;
   }
}

public class TIndexExpr : TExpr
{
   public TExpr left;
   public TInxList list;

   public TIndexExpr ()
   {
      left = null;
      list = null;
   }

   public override TIndexExpr conv_TIndexExpr ()
   {

         return this;
   }
}

public class TCallExpr : TExpr
{
   public TExpr func;
   public TArgSect list;

   public TCallExpr ()
   {
      func = null;
      list = null;
   }

   public override TCallExpr conv_TCallExpr ()
   {

         return this;
   }
}

public class TDerefExpr : TExpr
{
   public TExpr param;

   public TDerefExpr ()
   {
      param = null;
   }

   public override TDerefExpr conv_TDerefExpr ()
   {

         return this;
   }
}

public class TFieldExpr : TExpr
{
   public TExpr param;
   public string name;

   public TFieldExpr ()
   {
      param = null;
      name = "";
   }

   public override TFieldExpr conv_TFieldExpr ()
   {

         return this;
   }
}

public class TStat : CmmBasic
{

   public TStat ()
   {
   }

   public virtual TGotoStat conv_TGotoStat ()
   {
         return null;
   }

   public virtual TBlockStat conv_TBlockStat ()
   {
         return null;
   }

   public virtual TIfStat conv_TIfStat ()
   {
         return null;
   }

   public virtual TCaseStat conv_TCaseStat ()
   {
         return null;
   }

   public virtual TWhileStat conv_TWhileStat ()
   {
         return null;
   }

   public virtual TRepeatStat conv_TRepeatStat ()
   {
         return null;
   }

   public virtual TForStat conv_TForStat ()
   {
         return null;
   }

   public virtual TWithStat conv_TWithStat ()
   {
         return null;
   }

   public virtual TRaiseStat conv_TRaiseStat ()
   {
         return null;
   }

   public virtual TTryStat conv_TTryStat ()
   {
         return null;
   }

   public virtual TEmptyStat conv_TEmptyStat ()
   {
         return null;
   }

   public virtual TAssignStat conv_TAssignStat ()
   {
         return null;
   }

   public virtual TCallStat conv_TCallStat ()
   {
         return null;
   }

   public virtual TLabeledTStat conv_TLabeledTStat ()
   {
         return null;
   }

   public virtual TStat conv_TStat ()
   {
         return this;
   }
}

public class TGotoStat : TStat
{
   public TLabelIdent goto_lab;

   public TGotoStat ()
   {
      goto_lab = null;
   }

   public override TGotoStat conv_TGotoStat ()
   {

         return this;
   }
}

public class TBlockStat : TStat
{
   public TStatSeq body_seq;

   public TBlockStat ()
   {
      body_seq = null;
   }

   public override TBlockStat conv_TBlockStat ()
   {

         return this;
   }
}

public class TStatSeq : CmmBasic
{
   public TStat [] items;

   public TStatSeq ()
   {
      items = new TStat [] { };
   }

   public virtual TStatSeq conv_TStatSeq ()
   {

         return this;
   }
}

public class TIfStat : TStat
{
   public TExpr cond_expr;
   public TStat then_stat;
   public TStat else_stat;

   public TIfStat ()
   {
      cond_expr = null;
      then_stat = null;
      else_stat = null;
   }

   public override TIfStat conv_TIfStat ()
   {

         return this;
   }
}

public class TCaseStat : TStat
{
   public TExpr case_expr;
   public TCaseSect case_list;
   public TStatSeq else_seq;

   public TCaseStat ()
   {
      case_expr = null;
      case_list = null;
      else_seq = null;
   }

   public override TCaseStat conv_TCaseStat ()
   {

         return this;
   }
}

public class TCaseSect : CmmBasic
{
   public TCaseItem [] items;

   public TCaseSect ()
   {
      items = new TCaseItem [] { };
   }

   public virtual TCaseSect conv_TCaseSect ()
   {

         return this;
   }
}

public class TCaseItem : CmmBasic
{
   public TElemSect sel_list;
   public TStat sel_stat;

   public TCaseItem ()
   {
      sel_list = null;
      sel_stat = null;
   }

   public virtual TCaseItem conv_TCaseItem ()
   {

         return this;
   }
}

public class TWhileStat : TStat
{
   public TExpr cond_expr;
   public TStat body_stat;

   public TWhileStat ()
   {
      cond_expr = null;
      body_stat = null;
   }

   public override TWhileStat conv_TWhileStat ()
   {

         return this;
   }
}

public class TRepeatStat : TStat
{
   public TStatSeq body_seq;
   public TExpr until_expr;

   public TRepeatStat ()
   {
      body_seq = null;
      until_expr = null;
   }

   public override TRepeatStat conv_TRepeatStat ()
   {

         return this;
   }
}

public class TForStat : TStat
{
   public TExpr var_expr;
   public TExpr from_expr;
   public bool incr;
   public TExpr to_expr;
   public TStat body_stat;

   public TForStat ()
   {
      var_expr = null;
      from_expr = null;
      incr = false;
      to_expr = null;
      body_stat = null;
   }

   public override TForStat conv_TForStat ()
   {

         return this;
   }
}

public class TWithStat : TStat
{
   public TWithSect with_list;
   public TStat body_stat;

   public TWithStat ()
   {
      with_list = null;
      body_stat = null;
   }

   public override TWithStat conv_TWithStat ()
   {

         return this;
   }
}

public class TWithSect : CmmBasic
{
   public TWithItem [] items;

   public TWithSect ()
   {
      items = new TWithItem [] { };
   }

   public virtual TWithSect conv_TWithSect ()
   {

         return this;
   }
}

public class TWithItem : CmmBasic
{
   public TExpr expr;

   public TWithItem ()
   {
      expr = null;
   }

   public virtual TWithItem conv_TWithItem ()
   {

         return this;
   }
}

public class TRaiseStat : TStat
{
   public TExpr raise_expr;

   public TRaiseStat ()
   {
      raise_expr = null;
   }

   public override TRaiseStat conv_TRaiseStat ()
   {

         return this;
   }
}

public class TTryStat : TStat
{
   public TStatSeq body_seq;
   public TFinallyPart finally_branch;
   public TExceptPart except_branch;

   public TTryStat ()
   {
      body_seq = null;
      finally_branch = null;
      except_branch = null;
   }

   public override TTryStat conv_TTryStat ()
   {

         return this;
   }
}

public class TFinallyPart : CmmBasic
{
   public TStatSeq finally_seq;

   public TFinallyPart ()
   {
      finally_seq = null;
   }

   public virtual TFinallyPart conv_TFinallyPart ()
   {

         return this;
   }
}

public class TExceptPart : CmmBasic
{
   public TOnSect on_list;
   public TStatSeq else_seq;

   public TExceptPart ()
   {
      on_list = null;
      else_seq = null;
   }

   public virtual TExceptPart conv_TExceptPart ()
   {

         return this;
   }
}

public class TOnSect : CmmBasic
{
   public TOnItem [] items;
   public bool semicolon;

   public TOnSect ()
   {
      items = new TOnItem [] { };
      semicolon = false;
   }

   public virtual TOnSect conv_TOnSect ()
   {

         return this;
   }
}

public class TOnItem : CmmBasic
{
   public string on_ident;
   public TType on_type;
   public TStat body_stat;

   public TOnItem ()
   {
      on_ident = "";
      on_type = null;
      body_stat = null;
   }

   public virtual TOnItem conv_TOnItem ()
   {

         return this;
   }
}

public class TEmptyStat : TStat
{

   public TEmptyStat ()
   {
   }

   public override TEmptyStat conv_TEmptyStat ()
   {
         return this;
   }
}

public class TAssignStat : TStat
{
   public TExpr left_expr;
   public TExpr right_expr;

   public TAssignStat ()
   {
      left_expr = null;
      right_expr = null;
   }

   public override TAssignStat conv_TAssignStat ()
   {

         return this;
   }
}

public class TCallStat : TStat
{
   public TExpr call_expr;

   public TCallStat ()
   {
      call_expr = null;
   }

   public override TCallStat conv_TCallStat ()
   {

         return this;
   }
}

public class TLabeledTStat : TStat
{
   public TLabelIdent lab;
   public TStat body;

   public TLabeledTStat ()
   {
      lab = null;
      body = null;
   }

   public override TLabeledTStat conv_TLabeledTStat ()
   {

         return this;
   }
}

public class TParamIdent : CmmBasic
{
   public string name;

   public TParamIdent ()
   {
      name = "";
   }

   public virtual TParamIdent conv_TParamIdent ()
   {

         return this;
   }
}

public class TParamSect : CmmBasic
{
   public TParamItem [] items;

   public TParamSect ()
   {
      items = new TParamItem [] { };
   }

   public virtual TParamSect conv_TParamSect ()
   {

         return this;
   }
}

public class TClassType : TType
{
   public TType parent;
   public TInterfaceSect ifc_list;
   public TComponetsSect components;

   public TClassType ()
   {
      parent = null;
      ifc_list = null;
      components = null;
   }

   public override TClassType conv_TClassType ()
   {

         return this;
   }
}

public class TInterfaceType : TType
{
   public TInterfaceSect ifc_list;
   public TComponetsSect components;

   public TInterfaceType ()
   {
      ifc_list = null;
      components = null;
   }

   public override TInterfaceType conv_TInterfaceType ()
   {

         return this;
   }
}

public class TInterfaceSect : CmmBasic
{
   public TIntefaceItem [] items;

   public TInterfaceSect ()
   {
      items = new TIntefaceItem [] { };
   }

   public virtual TInterfaceSect conv_TInterfaceSect ()
   {

         return this;
   }
}

public class TIntefaceItem : CmmBasic
{
   public TType ifc;

   public TIntefaceItem ()
   {
      ifc = null;
   }

   public virtual TIntefaceItem conv_TIntefaceItem ()
   {

         return this;
   }
}

public class TComponetsSect : CmmBasic
{
   public TComponentsItem [] items;

   public TComponetsSect ()
   {
      items = new TComponentsItem [] { };
   }

   public virtual TComponetsSect conv_TComponetsSect ()
   {

         return this;
   }
}

public class TDeclGroup : CmmBasic
{
   public TDeclSect [] items;

   public TDeclGroup ()
   {
      items = new TDeclSect [] { };
   }

   public virtual TDeclGroup conv_TDeclGroup ()
   {

         return this;
   }
}

public class TDeclSect : CmmBasic
{

   public TDeclSect ()
   {
   }

   public virtual TFieldDecl conv_TFieldDecl ()
   {
         return null;
   }

   public virtual TPropertyDecl conv_TPropertyDecl ()
   {
         return null;
   }

   public virtual TLabelSect conv_TLabelSect ()
   {
         return null;
   }

   public virtual TConstSect conv_TConstSect ()
   {
         return null;
   }

   public virtual TTypeSect conv_TTypeSect ()
   {
         return null;
   }

   public virtual TVarSect conv_TVarSect ()
   {
         return null;
   }

   public virtual TProcDecl conv_TProcDecl ()
   {
         return null;
   }

   public virtual TDeclSect conv_TDeclSect ()
   {
         return this;
   }
}

public class TFieldItem : CmmBasic
{
   public string name;

   public TFieldItem ()
   {
      name = "";
   }

   public virtual TFieldItem conv_TFieldItem ()
   {

         return this;
   }
}

public class TFieldDecl : TDeclSect
{
   public TFieldItem [] items;
   public TType typ;

   public TFieldDecl ()
   {
      items = new TFieldItem [] { };
      typ = null;
   }

   public override TFieldDecl conv_TFieldDecl ()
   {

         return this;
   }
}

public class TPropertyDecl : TDeclSect
{
   public string name;
   public TParamSect param_list;
   public TType typ;
   public TExpr a_read;
   public TExpr a_write;
   public bool a_stored;
   public bool a_default;
   public bool a_nodefault;
   public TInterfaceSect a_implements;
   public bool a_def_array;

   public TPropertyDecl ()
   {
      name = "";
      param_list = null;
      typ = null;
      a_read = null;
      a_write = null;
      a_stored = false;
      a_default = false;
      a_nodefault = false;
      a_implements = null;
      a_def_array = false;
   }

   public override TPropertyDecl conv_TPropertyDecl ()
   {

         return this;
   }
}

public class TEnumType : TType
{
   public TEnumSect elements;

   public TEnumType ()
   {
      elements = null;
   }

   public override TEnumType conv_TEnumType ()
   {

         return this;
   }
}

public class TEnumSect : CmmBasic
{
   public TEnumItem [] items;

   public TEnumSect ()
   {
      items = new TEnumItem [] { };
   }

   public virtual TEnumSect conv_TEnumSect ()
   {

         return this;
   }
}

public class TEnumItem : CmmBasic
{
   public string name;

   public TEnumItem ()
   {
      name = "";
   }

   public virtual TEnumItem conv_TEnumItem ()
   {

         return this;
   }
}

public class TArrayType : TType
{
   public TIndexTypeSect index_list;
   public TType elem;

   public TArrayType ()
   {
      index_list = null;
      elem = null;
   }

   public override TArrayType conv_TArrayType ()
   {

         return this;
   }
}

public class TIndexTypeSect : CmmBasic
{
   public TIndexTypeItem [] items;

   public TIndexTypeSect ()
   {
      items = new TIndexTypeItem [] { };
   }

   public virtual TIndexTypeSect conv_TIndexTypeSect ()
   {

         return this;
   }
}

public class TIndexTypeItem : CmmBasic
{
   public TType index;

   public TIndexTypeItem ()
   {
      index = null;
   }

   public virtual TIndexTypeItem conv_TIndexTypeItem ()
   {

         return this;
   }
}

public class TRecordType : TType
{
   public bool a_packed;
   public TFieldDeclGroup fields;

   public TRecordType ()
   {
      a_packed = false;
      fields = null;
   }

   public override TRecordType conv_TRecordType ()
   {

         return this;
   }
}

public class TFieldDeclGroup : CmmBasic
{
   public TFieldDecl [] items;

   public TFieldDeclGroup ()
   {
      items = new TFieldDecl [] { };
   }

   public virtual TFieldDeclGroup conv_TFieldDeclGroup ()
   {

         return this;
   }
}

public class TPointerType : TType
{
   public TType elem;

   public TPointerType ()
   {
      elem = null;
   }

   public override TPointerType conv_TPointerType ()
   {

         return this;
   }
}

public class TSetType : TType
{
   public TType elem;

   public TSetType ()
   {
      elem = null;
   }

   public override TSetType conv_TSetType ()
   {

         return this;
   }
}

public class TClassOfType : TType
{
   public TType elem;

   public TClassOfType ()
   {
      elem = null;
   }

   public override TClassOfType conv_TClassOfType ()
   {

         return this;
   }
}

public class TProcType : TType
{
   public TStyle style;
   public TCall call_conv;
   public TParamSect param_list;
   public TType answer;
   public bool of_object;

   public TProcType ()
   {
      style = TStyle.ProcedureStyle;
      call_conv = TCall.RegisterCall;
      param_list = null;
      answer = null;
      of_object = false;
   }

   public override TProcType conv_TProcType ()
   {

         return this;
   }
}

public class TSubrangeType : TType
{
   public TExpr low;
   public TExpr high;

   public TSubrangeType ()
   {
      low = null;
      high = null;
   }

   public override TSubrangeType conv_TSubrangeType ()
   {

         return this;
   }
}

public class TLabelDecl : CmmBasic
{
   public TLabelIdent name;

   public TLabelDecl ()
   {
      name = null;
   }

   public virtual TLabelDecl conv_TLabelDecl ()
   {

         return this;
   }
}

public class TLabelSect : TDeclSect
{
   public TLabelDecl [] items;

   public TLabelSect ()
   {
      items = new TLabelDecl [] { };
   }

   public override TLabelSect conv_TLabelSect ()
   {

         return this;
   }
}

public class TConstDecl : CmmBasic
{
   public string name;
   public TType typ;
   public TExpr val;

   public TConstDecl ()
   {
      name = "";
      typ = null;
      val = null;
   }

   public virtual TConstDecl conv_TConstDecl ()
   {

         return this;
   }
}

public class TConstSect : TDeclSect
{
   public TConstDecl [] items;

   public TConstSect ()
   {
      items = new TConstDecl [] { };
   }

   public override TConstSect conv_TConstSect ()
   {

         return this;
   }
}

public class TTypeDecl : CmmBasic
{
   public string name;
   public TType typ;

   public TTypeDecl ()
   {
      name = "";
      typ = null;
   }

   public virtual TTypeDecl conv_TTypeDecl ()
   {

         return this;
   }
}

public class TTypeSect : TDeclSect
{
   public TTypeDecl [] items;

   public TTypeSect ()
   {
      items = new TTypeDecl [] { };
   }

   public override TTypeSect conv_TTypeSect ()
   {

         return this;
   }
}

public class TVarItem : CmmBasic
{
   public string name;

   public TVarItem ()
   {
      name = "";
   }

   public virtual TVarItem conv_TVarItem ()
   {

         return this;
   }
}

public class TVarDecl : CmmBasic
{
   public TVarItem [] items;
   public TType typ;
   public TExpr ini;

   public TVarDecl ()
   {
      items = new TVarItem [] { };
      typ = null;
      ini = null;
   }

   public virtual TVarDecl conv_TVarDecl ()
   {

         return this;
   }
}

public class TVarSect : TDeclSect
{
   public TVarDecl [] items;

   public TVarSect ()
   {
      items = new TVarDecl [] { };
   }

   public override TVarSect conv_TVarSect ()
   {

         return this;
   }
}

public class TProcDecl : TDeclSect
{
   public TStyle style;
   public TCall call_conv;
   public bool a_virtual;
   public bool a_dynamic;
   public bool a_override;
   public bool a_abstract;
   public bool a_static;
   public TQualName proc_name;
   public TParamSect param_list;
   public TType answer;
   public bool a_forward;
   public bool external_spec;
   public bool a_inline;
   public TDeclGroup local;
   public TStatSeq body;
   public bool a_external;
   public TExpr a_lib;

   public TProcDecl ()
   {
      style = TStyle.ProcedureStyle;
      call_conv = TCall.RegisterCall;
      a_virtual = false;
      a_dynamic = false;
      a_override = false;
      a_abstract = false;
      a_static = false;
      proc_name = null;
      param_list = null;
      answer = null;
      a_forward = false;
      external_spec = false;
      a_inline = false;
      local = null;
      body = null;
      a_external = false;
      a_lib = null;
   }

   public override TProcDecl conv_TProcDecl ()
   {

         return this;
   }
}

public class TImportItem : CmmBasic
{
   public string name;
   public string path;

   public TImportItem ()
   {
      name = "";
      path = "";
   }

   public virtual TImportItem conv_TImportItem ()
   {

         return this;
   }
}

public class TImportSect : CmmBasic
{
   public TImportItem [] items;

   public TImportSect ()
   {
      items = new TImportItem [] { };
   }

   public virtual TImportSect conv_TImportSect ()
   {

         return this;
   }
}

public class TUnitModule : TModule
{
   public string name;
   public bool no_begin;

   public TUnitModule ()
   {
      name = "";
      no_begin = false;
   }

   public override TUnitModule conv_TUnitModule ()
   {

         return this;
   }
}

public class TProgramModule : TModule
{
   public string name;

   public TProgramModule ()
   {
      name = "";
   }

   public override TProgramModule conv_TProgramModule ()
   {

         return this;
   }
}

public class TLibraryModule : TModule
{
   public string name;

   public TLibraryModule ()
   {
      name = "";
   }

   public override TLibraryModule conv_TLibraryModule ()
   {

         return this;
   }
}

public class TTermExpr : TBinaryExpr
{

   public TTermExpr ()
   {
   }

   public override TTermExpr conv_TTermExpr ()
   {
         return this;
   }
}

public class TSimpleExpr : TBinaryExpr
{

   public TSimpleExpr ()
   {
   }

   public override TSimpleExpr conv_TSimpleExpr ()
   {
         return this;
   }
}

public class TCompleteExpr : TBinaryExpr
{

   public TCompleteExpr ()
   {
   }

   public override TCompleteExpr conv_TCompleteExpr ()
   {
         return this;
   }
}
