
#![allow(warnings, unused)]

mod lexer;
use lexer::Lexer;

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
   DOT,
   SLASH,
   DIV_ASSIGN,
   COLON,
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
   RBRACKET,
   BIT_XOR,
   BIT_XOR_ASSIGN,
   LBRACE,
   BIT_OR,
   BIT_OR_ASSIGN,
   LOG_OR,
   RBRACE,
   BIT_NOT,
   keyword_auto,
   keyword_bool,
   keyword_break,
   keyword_case,
   keyword_char,
   keyword_const,
   keyword_continue,
   keyword_dcl,
   keyword_default,
   keyword_delete,
   keyword_do,
   keyword_double,
   keyword_else,
   keyword_enum,
   keyword_extern,
   keyword_float,
   keyword_for,
   keyword_goto,
   keyword_if,
   keyword_int,
   keyword_long,
   keyword_new,
   keyword_register,
   keyword_return,
   keyword_short,
   keyword_signed,
   keyword_sizeof,
   keyword_static,
   keyword_struct,
   keyword_switch,
   keyword_type_cast,
   keyword_typedef,
   keyword_unsigned,
   keyword_void,
   keyword_volatile,
   keyword_wchar_t,
   keyword_while
}

enum CmmExprKind
{
   simpleName,
   incExp,
   decExp,
   derefExp,
   addrExp,
   plusExp,
   minusExp,
   bitNotExp,
   logNotExp,
   sizeofExp,
   newExp,
   deleteExp,
   mulExp,
   divExp,
   modExp,
   addExp,
   subExp,
   shlExp,
   shrExp,
   ltExp,
   gtExp,
   leExp,
   geExp,
   eqExp,
   neExp,
   bitAndExp,
   bitXorExp,
   bitOrExp,
   logAndExp,
   logOrExp,
   assignExp,
   addAssignExp,
   subAssignExp,
   mulAssignExp,
   divAssignExp,
   modAssignExp,
   shlAssignExp,
   shrAssignExp,
   andAssignExp,
   xorAssignExp,
   orAssignExp,
   condExp,
   commaExp,
   intValue,
   realValue,
   charValue,
   stringValue,
   subexprExp,
   indexExp,
   callExp,
   fieldExp,
   ptrFieldExp,
   postIncExp,
   postDecExp,
   typecastExp,
   declSpec,
   constSpec,
   volatileSpec,
   typeSpec
}

enum CmmStatMode
{
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
   localStat
}

struct CmmBasic
{
   src_file : i32,
   src_line : i32,
   src_column : i32,
}

impl CmmBasic
{
   fn new () -> CmmBasic
   {
      CmmBasic
      {
         src_file : 0,
         src_line : 0,
         src_column : 0,
      }
   }
}

struct CmmExpr
{
   inner : CmmBasic,
   kind : CmmExprKind,
   // item_decl : Option<Box<CmmDecl>>,
   // item_type : Option<Box<CmmBasic>>,
   id : String,
   // value : String,
   // items : Vec<Box<CmmStringCont>>,
   param : Option<Box<CmmExpr>>,
   left : Option<Box<CmmExpr>>,
   // param_list : Option<Box<CmmExprList>>,
   simp_name : Option<Box<CmmExpr>>,
   // value_from_sizeofExp : Option<Box<CmmExpr>>,
   // type_spec : Option<Box<CmmExpr>>,
   // ptr : Option<Box<CmmPtrSpecifierSect>>,
   // items_from_newExp : Vec<Box<CmmNewArrayLimit>>,
   // a_array : bool,
   // target_type : Option<Box<CmmTypeId>>,
   right : Option<Box<CmmExpr>>,
   // middle : Option<Box<CmmExpr>>,
}

impl CmmExpr
{
   fn new () -> CmmExpr
   {
      CmmExpr
      {
         inner : CmmBasic::new (),
         kind : CmmExprKind::simpleName,
         id : "".to_string (),
         simp_name : None,
         param : None,
         left : None,
         right : None,
      }
   }
}

struct CmmStat
{
   inner : CmmBasic,
   mode : CmmStatMode,
   items : Vec<Option<Box<CmmStat>> >,
   cond : Option<Box<CmmExpr>>,
   then_stat : Option<Box<CmmStat>>,
   else_stat : Option<Box<CmmStat>>,
   body : Option<Box<CmmStat>>,
   cond_expr : Option<Box<CmmExpr>>,
   from_expr : Option<Box<CmmExpr>>,
   iter_expr : Option<Box<CmmExpr>>,
   step_expr : Option<Box<CmmExpr>>,
   case_expr : Option<Box<CmmExpr>>,
   return_expr : Option<Box<CmmExpr>>,
   goto_lab : String,
   inner_expr : Option<Box<CmmExpr>>,
   // inner_decl : Option<Box<CmmSimpleDecl>>,
}

impl CmmStat
{
   fn new () -> CmmStat
   {
      CmmStat
      {
         inner : CmmBasic::new (),
         mode : CmmStatMode::emptyStat,
         items : Vec::<Option<Box<CmmStat>>>::new(),
         cond : None,
         then_stat : None,
         else_stat : None,
         body : None,
         cond_expr : None,
         from_expr : None,
         iter_expr : None,
         step_expr : None,
         case_expr : None,
         return_expr : None,
         goto_lab : "".to_string (),
         inner_expr : None,
         // inner_decl : None,
      }
   }
}

struct Parser
{
   inner : Lexer,
   token : CmmSymbol,
}

impl Parser
{
   fn parse_simple_name (& mut self) -> Option <Box<CmmExpr>>
   {
         let mut result = CmmExpr::new ();
         result.kind = CmmExprKind::simpleName;
         self.storeLocation (& mut result.inner);
         result.id = self.inner.readIdentifier ();
         return Some (Box::new (result));
   }

   fn parse_ident_expr (& mut self) -> Option <Box<CmmExpr>>
   {
         let result = self.parse_simple_name ();
         return result;
   }

   fn parse_primary_expr (& mut self) -> Option <Box<CmmExpr>>
   {

         let mut result = None;
         if (self.isSymbol (CmmSymbol::identifier))
         {
            result = self.parse_ident_expr ();
         }
         else
         {
            self.stop ("Unexpected token".to_string());
         }
         return result;
   }

   fn parse_call_expr (& mut self, store : Option<Box<CmmExpr>>) -> Option<Box<CmmExpr>>
   {
         let mut result = CmmExpr::new ();
         result.kind = CmmExprKind::callExp;
         self.storeLocation (& mut result.inner);
         result.left = store;
         self.checkSymbol (CmmSymbol::LPAREN);
         result.param = self.parse_expr ();
         self.checkSymbol (CmmSymbol::RPAREN);
         return Some (Box::new (result));
   }


   fn parse_postfix_expr (& mut self) -> Option<Box<CmmExpr>>
   {

         let mut result = None;
         result = self.parse_primary_expr ();
         while (self.isSymbol (CmmSymbol::LBRACKET) || self.isSymbol (CmmSymbol::LPAREN) || self.isSymbol (CmmSymbol::DOT) || self.isSymbol (CmmSymbol::ARROW) || self.isSymbol (CmmSymbol::INC) || self.isSymbol (CmmSymbol::DEC))
         {
            if (self.isSymbol (CmmSymbol::LPAREN))
            {
               result = self.parse_call_expr (result);
            }
            else {
               self.stop ("Unexpected token".to_string());
            }
         }
         return result;
   }



   fn parse_multiplicative_expr (& mut self) -> Option<Box<CmmExpr>>
   {
         let mut result = None;
         // result = self.parse_postfix_expr ();
         result = self.parse_expr ();
         while (self.isSymbol (CmmSymbol::STAR) || self.isSymbol (CmmSymbol::SLASH) || self.isSymbol (CmmSymbol::MOD))
         {
            let store = result;
            let mut result0 = CmmExpr::new ();
            self.storeLocation (& mut result0.inner);
            result0.left = store;
            if (self.isSymbol (CmmSymbol::STAR))
            {
               self.checkSymbol (CmmSymbol::STAR);
               result0.kind = CmmExprKind::mulExp;
            }
            else if (self.isSymbol (CmmSymbol::SLASH))
            {
               self.checkSymbol (CmmSymbol::SLASH);
               result0.kind = CmmExprKind::divExp;
            }
            else if (self.isSymbol (CmmSymbol::MOD))
            {
               self.checkSymbol (CmmSymbol::MOD);
               result0.kind = CmmExprKind::modExp;
            }
            else
            {
               self.stop ("Unexpected token".to_string());
            }
            // result0.right = self.parse_postfix_expr ();
            result0.right = self.parse_expr ();
            result = Some (Box::new (result0));
         }
         return result;
   }

   fn parse_expr (& mut self) -> Option<Box<CmmExpr>>
   {
      let result = self.parse_multiplicative_expr ();
      return result;
   }

   fn parse_stat (& mut self) -> Option <Box<CmmStat>>
   {
         let mut result = None;
         if (self.testSymbols (set_1))
         {
            result = self.parse_simple_stat ();
         }
         else if (self.isSymbol (CmmSymbol::keyword_if))
         {
            result = self.parse_if_stat ();
         }
         else {
            self.stop ("Unexpected token".to_string ());
         }
         return result;
   }


   fn parse_simple_stat (& mut self) -> Option<Box<CmmStat>>
   {
         let mut result = CmmStat::new ();
         result.mode = CmmStatMode::simpleStat;
         self.storeLocation (& mut result.inner);
         result.inner_expr = self.parse_expr ();
         self.checkSymbol (CmmSymbol::SEMICOLON);
         return Some (Box::new (result));
   }

   fn parse_if_stat (& mut self) -> Option<Box<CmmStat>>
   {
         let mut result = CmmStat::new ();
         result.mode = CmmStatMode::ifStat;
         self.storeLocation (& mut result.inner);
         self.checkSymbol (CmmSymbol::keyword_if);
         self.checkSymbol (CmmSymbol::LPAREN);
         result.cond = self.parse_expr ();
         self.checkSymbol (CmmSymbol::RPAREN);
         result.then_stat = self.parse_stat ();
         if (self.isSymbol (CmmSymbol::keyword_else))
         {
            self.checkSymbol (CmmSymbol::keyword_else);
            result.else_stat = self.parse_stat ();
         }
         return Some (Box::new (result));
   }

   fn storeLocation (& mut self, item : & mut CmmBasic)
   {
         item.src_file = self.inner.getTokenFileInx ();
         item.src_line = self.inner.getTokenLine ();
         item.src_column = self.inner.getTokenCol ();
   }

   fn isSymbol (& mut self, sym : CmmSymbol) -> bool
   {

         // return self.token as isize == sym as isize;
         return false;
   }

   fn testSymbols (& mut self, sym_set : [ u8 ; 12 ]) -> bool
   {
         return false;
   }

   fn checkSymbol (& mut self, sym : CmmSymbol)
   {
         /*
         if (self.token as i32 != sym as i32)
         {
            // self.stop (self.tokenToString (sym) + " expected".to_string());
         }
         */
         self.inner.nextToken ();
   }

   fn stop (& mut self, msg : String)
   {
         // self.error (msg);
   }

   fn stop_str (& mut self)
   {
        // self.stop ("Unexpected ".to_string () + self.tokenToString (self.token));
   }

   fn lookupKeyword (& mut self)
   {
         // let s : Vec <char> = self.inner.tokenText.chars().collect ();
         let s = self.inner.tokenText.clone(); // !?
         let n = s.len ();
         if (n == 2)
         {
            if (&s[0..0] == "d")
            {
                  if (&s[1..1] == "o")
                  {
                        self.token = CmmSymbol::keyword_do;
                  }
            }
         }
         else if (n == 3)
         {
            if (&s[0..0] == "f")
            {
                  if (&s[1..2] == "or")
                  {
                        self.token = CmmSymbol::keyword_for;
                  }
            }
         }
   }

   /*
   fn processSeparator (& mut self)
   {
         if (self.inner.tokenText == "!")
         {
            self.token = CmmSymbol::LOG_NOT;
            if (self.inner.ch == '=')
            {
               self.token = CmmSymbol::UNEQUAL;
               self.inner.tokenText = self.inner.tokenText + self.inner.ch;
               self.inner.nextCh ();
            }
         }
   }

   fn tokenToString (& mut self, value : CmmSymbol) -> String
   {
         if (value  ==  0)
         {
            return "<end of source text>";
         }
         if (value  ==  1)
         {
            return "<identifier>";
         }
         if (value  ==  2)
         {
            return "<number>";
         }
         if (value  ==  3)
         {
            return "<real_number>";
         }
         if (value  ==  4)
         {
            return "<character_literal>";
         }
         if (value  ==  5)
         {
            return "<string_literal>";
         }
         if (value  ==  6)
         {
            return "<unknown separator>";
         }
         if (value  ==  7)
         {
            return "<end of line>";
         }
         if (value  ==  8)
         {
            return "!";
         }
         if (value  ==  9)
         {
            return "!=";
         }
   }

   fn translate (& mut self)
   {
         if (self.tokenKind == self.inner.identifier)
         {
            self.token = CmmSymbol::identifier;
            self.lookupKeyword ();
         }
         else if (self.tokenKind == self.inner.number)
         {
            self.token = CmmSymbol::number;
         }
         else if (self.tokenKind == self.inner.character_literal)
         {
            self.token = CmmSymbol::character_literal;
         }
         else if (self.tokenKind == self.inner.string_literal)
         {
            self.token = CmmSymbol::string_literal;
         }
         else if (self.tokenKind == self.inner.eos)
         {
            self.token = CmmSymbol::eos;
         }
         else
         {
            self.token = CmmSymbol::separator;
            self.processSeparator ();
         }
   }
   */

   fn new () -> Parser
   {
      Parser
      {
         inner : Lexer::new (),
         token : CmmSymbol::eos,
      }
   }
}

const set_0 : [ u8 ; 12 ]  = [0, 128, 16, 13, 0, 8, 0, 0, 0, 0, 0, 0];
// set_0 :  ( ++ -- -> . [

const set_1 : [ u8 ; 12 ]  = [62, 145, 154, 1, 0, 0, 16, 64, 0, 132, 8, 0];
// set_1 :  identifier number real_number character_literal string_literal ! & ( * + ++ - -- ~ delete new sizeof type_cast

const set_2 : [ u8 ; 12 ]  = [62, 128, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
// set_2 :  identifier number real_number character_literal string_literal (

const set_3 : [ u8 ; 12 ]  = [62, 145, 154, 1, 0, 0, 16, 64, 0, 132, 0, 0];
// set_3 :  identifier number real_number character_literal string_literal ! & ( * + ++ - -- ~ delete new sizeof

const set_4 : [ u8 ; 12 ]  = [0, 0, 0, 0, 201, 0, 0, 0, 0, 0, 0, 0];
// set_4 :  < <= > >=

const set_5 : [ u8 ; 12 ]  = [0, 72, 36, 34, 20, 70, 2, 0, 0, 0, 0, 0];
// set_5 :  %= &= *= += -= /= <<= = >>= ? ^= |=

const set_6 : [ u8 ; 12 ]  = [62, 145, 154, 129, 0, 128, 144, 249, 224, 148, 12, 2];
// set_6 :  identifier number real_number character_literal string_literal ! & ( * + ++ - -- ; { ~ break case continue dcl default delete do for goto if new return sizeof switch type_cast while

const set_7 : [ u8 ; 12 ]  = [0, 0, 0, 0, 0, 0, 32, 0, 8, 8, 1, 0];
// set_7 :  auto extern register static

const set_8 : [ u8 ; 12 ]  = [0, 0, 0, 0, 0, 0, 64, 2, 17, 99, 96, 1];
// set_8 :  bool char double float int long short signed unsigned void wchar_t

const set_9 : [ u8 ; 12 ]  = [2, 0, 0, 0, 0, 0, 64, 6, 17, 99, 224, 1];
// set_9 :  identifier bool char const double float int long short signed unsigned void volatile wchar_t

const set_10 : [ u8 ; 12 ]  = [2, 0, 0, 128, 0, 0, 64, 6, 21, 99, 242, 1];
// set_10 :  identifier ; bool char const double enum float int long short signed struct typedef unsigned void volatile wchar_t

pub fn main ()
{
}
