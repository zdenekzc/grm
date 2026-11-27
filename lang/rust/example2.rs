
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
   item_decl : Option<Box<CmmDecl>>,
   item_type : Option<Box<CmmBasic>>,
   id : String,
   value : String,
   items : Vec<Box<CmmStringCont>>,
   param : Option<Box<CmmExpr>>,
   left : Option<Box<CmmExpr>>,
   param_list : Option<Box<CmmExprList>>,
   simp_name : Option<Box<CmmExpr>>,
   value_from_sizeofExp : Option<Box<CmmExpr>>,
   type_spec : Option<Box<CmmExpr>>,
   ptr : Option<Box<CmmPtrSpecifierSect>>,
   items_from_newExp : Vec<Box<CmmNewArrayLimit>>,
   a_array : bool,
   target_type : Option<Box<CmmTypeId>>,
   a_extern : bool,
   a_static : bool,
   a_auto : bool,
   a_register : bool,
   a_signed : bool,
   a_unsigned : bool,
   a_bool : bool,
   a_char : bool,
   a_wchar : bool,
   a_short : bool,
   a_int : bool,
   a_long : bool,
   a_float : bool,
   a_double : bool,
   a_void : bool,
   right : Option<Box<CmmExpr>>,
   middle : Option<Box<CmmExpr>>,
}

impl CmmExpr
{
   fn new () -> CmmExpr
   {
      CmmExpr
      {
         inner : CmmBasic::new (),
         kind : CmmExprKind::simpleName,
         item_decl : None,
         item_type : None,
         id : "".to_string (),
         value : "".to_string (),
         items : Vec::<Box<CmmStringCont>>::new(),
         param : None,
         left : None,
         param_list : None,
         simp_name : None,
         value_from_sizeofExp : None,
         type_spec : None,
         ptr : None,
         items_from_newExp : Vec::<Box<CmmNewArrayLimit>>::new(),
         a_array : false,
         target_type : None,
         a_extern : false,
         a_static : false,
         a_auto : false,
         a_register : false,
         a_signed : false,
         a_unsigned : false,
         a_bool : false,
         a_char : false,
         a_wchar : false,
         a_short : false,
         a_int : false,
         a_long : false,
         a_float : false,
         a_double : false,
         a_void : false,
         right : None,
         middle : None,
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
   fn parse_simple_name (& mut self) -> CmmExpr
   {

         let mut result = CmmExpr::new ();
         result.kind = CmmExprKind::simpleName;
         self.storeLocation (result.inner);
         result.id = self.inner.readIdentifier ();
         return result;
   }

   fn parse_primary_expr (& mut self) -> CmmExpr
   {

         let mut result : CmmExpr;
         if (self.isSymbol (CmmSymbol::identifier))
         {
            result = self.parse_ident_expr ();
         }
         else {
            self.stop ("Unexpected token".to_string ());
         }
         return result;
   }

   fn parse_ident_expr (& mut self) -> CmmExpr
   {

         let mut result  : CmmExpr ;
         result = self.parse_simple_name ();
         return result;
   }

   fn parse_int_value (& mut self) -> CmmExpr
   {

         let mut result = CmmExpr::new ();
         result.kind = CmmExprKind::intValue;
         self.storeLocation (result.inner);
         result.value = self.inner.readNumber ();
         return result;
   }

   fn parse_real_value (& mut self) -> CmmExpr
   {

         let mut result = CmmExpr::new ();
         result.kind = CmmExprKind::realValue;
         self.storeLocation (result.inner);
         result.value = self.inner.readNumber ();
         return result;
   }

   fn parse_char_value (& mut self) -> CmmExpr
   {

         let mut result = CmmExpr::new ();
         result.kind = CmmExprKind::charValue;
         self.storeLocation (result.inner);
         result.value = self.inner.readChar ();
         return result;
   }

   fn parse_string_value (& mut self) -> CmmExpr
   {

         let mut result = CmmExpr::new ();
         result.kind = CmmExprKind::stringValue;
         self.storeLocation (result.inner);
         result.value = self.inner.readString ();
         while (self.isSymbol (CmmSymbol::string_literal))
         {
            result.items.push (Box::new (self.parse_string_value_cont ()));
         }
         return result;
   }

   fn parse_string_value_cont (& mut self) -> CmmStringCont
   {

         let mut result = CmmStringCont::new ();
         self.storeLocation (result.inner);
         result.value = self.inner.readString ();
         return result;
   }

   fn parse_subexpr_expr (& mut self) -> CmmExpr
   {

         let mut result = CmmExpr::new ();
         result.kind = CmmExprKind::subexprExp;
         self.storeLocation (result.inner);
         self.checkSymbol (CmmSymbol::LPAREN);
         result.param = Some (Box::new (self.parse_expr ()));
         self.checkSymbol (CmmSymbol::RPAREN);
         return result;
   }

   fn parse_multiplicative_expr (& mut self) -> CmmExpr
   {

         let mut result : CmmExpr;
         result = self.parse_pm_expr ();
         while (self.isSymbol (CmmSymbol::STAR) || self.isSymbol (CmmSymbol::SLASH) || self.isSymbol (CmmSymbol::MOD))
         {
            let mut store = result;
            let mut result0 = CmmExpr::new ();
            self.storeLocation (result0.inner);
            result0.left = Some (Box::new (store));
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
            else {
               self.stop ("Unexpected token".to_string ());
            }
            result0.right = Some (Box::new (self.parse_pm_expr ()));
            result = result0;
         }
         return result;
   }

   fn testSymbols (& mut self, table : [u8 ; 12] ) -> bool
   {
      let mut pos = inner.token / 8;
      let mut bit = inner.token % 8;;
      return table [pos]  &  (1 << bit);
   }

   fn testSymbols (& mut self, mut table : [u8;12]) -> bool
   {
         let mut pos : usize = (self.inner.token / 8).try_into().unwrap();
         let mut bit : usize = (self.inner.token % 8).try_into().unwrap();
         return table [pos]  &  (1 << bit) != 0;
   }

   fn lookupKeyword (& mut self)
   {
         let orig = self.inner.tokenText;
         let s : Vec <char> = orig.chars ().collect();
         let n = s.len ();
         if (n == 2)
         {
            if (s[0] == 'd')
            {
                  if (s[1] == 'o')
                  {
                        self.token = CmmSymbol::keyword_do;
                  }
            }
            else if (s[0] == 'i')
            {
                  if (s[1] == 'f')
                  {
                        self.token = CmmSymbol::keyword_if;
                  }
            }
         }
         else if (n == 3)
         {
            if (s[0] == 'd')
            {
                  if (&orig [1..2] == "cl")
                  {
                        self.token = CmmSymbol::keyword_dcl;
                  }
            }
         }
   }



}
