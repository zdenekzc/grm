
package cacao.src;

public class Expr extends Lex
{

  /* ------------------------------------------------------------------- */

  private static ExprDef calc (int tag)
  {
     return new ExprDef (tag);
  }

  private static ExprDef calc (int tag, ExprDef p1)
  {
     return new ExprDef (tag, p1);
  }

  private static ExprDef calc (int tag, ExprDef p1, ExprDef p2)
  {
     return new ExprDef (tag, p1, p2);
  }

  private static ExprDef calc (int tag, ExprDef p1, ExprDef p2, ExprDef p3)
  {
     return new ExprDef (tag, p1, p2, p3);
  }

  private static ExprDef calc (int tag, String val)
  {
     return new ExprDef (tag, val);
  }

  /* ------------------------------------------------------------------- */

  ExprDef identifier_expr ()
  {
     if (sy!=IDENT) error ("Identifier expected");
     ExprDef e = calc (IDENT, val);
     nextSymbol ();
     return e;
  }

  private void argument_list (ExprDef e)
  {
     checkSymbol (LPAR);

     if (sy!=RPAR)
     {
        e.addParam (expression ());
        while (sy==COMMA)
        {
           nextSymbol ();
           e.addParam (expression ());
        }
     }

     checkSymbol (RPAR);
  }

  private boolean is_cast ()
  {
     final int [] table = { BITNOT, LOGNOT, LPAR,
                            IDENT, NUMBER, FLT, CHR, STR,
                            NEW, THIS, SUPER };

     int i = 0;
     int len = table.length;

     while (i<len && sy!=table[i])
        i++;

     return (i<len);
  }

  /* ------------------------------------------------------------------- */

  private ExprDef primary_expr ()
  {
     ExprDef t1 = null; // compiler

     if (sy==IDENT ||
         sy==NUMBER ||
         sy==FLT ||
         sy==CHR ||
         sy==STR)
     {
        t1 = calc (sy, val);
        nextSymbol ();
     }

     else if (sy==THIS ||
              sy==SUPER ||   /* ?? pridano */
              sy==TRUE ||
              sy==FALSE ||
              sy==NULL||
              sy==BOOLEAN ||  /* ?? pridano */
              sy==CHAR ||
              sy==BYTE ||
              sy==SHORT ||
              sy==INT ||
              sy==LONG ||
              sy==FLOAT ||
              sy==DOUBLE ||
              sy==VOID)
     {
        t1 = calc (sy);
        nextSymbol ();
     }

     else if (sy==NEW)
     {
        nextSymbol ();
        t1 = primary_expr ();
        t1 = calc (NEW, t1);
     }

     else if (sy==LPAR)
     {
        nextSymbol ();
        t1 = expression ();
        checkSymbol (RPAR);

        if (is_cast ())
        {
           ExprDef t2 = unary_expr ();
           t1 = calc (CAST, t1, t2);
        }
        else
        {
           t1 = calc (LPAR, t1);
        }
     }
     else error ("Syntax error in expression");

     while (sy==PERIOD || sy==LPAR || sy == LBRACK)
     {
        if (sy==PERIOD)
        {
           nextSymbol ();
           ExprDef t2 = identifier_expr ();
           t1 = calc (PERIOD, t1, t2);
        }

        else if (sy==LBRACK)
        {
           nextSymbol ();
           if (sy==LBRACK)
           {
              t1 = calc (DIM, t1); /* ?? pridano */
           }
           else
           {
              ExprDef t2 = expression ();
              t1 = calc (LBRACK, t1, t2);
              checkSymbol (RBRACK);
           }
        }

        else if (sy==LPAR)
        {
           t1 = calc (FCE, t1);
           argument_list (t1);
        }

        else bug ();
     }

     return t1;
  }

  private ExprDef postfix_expr ()
  {
     ExprDef t1;
     int tag;

     t1 = primary_expr ();

     while (sy==DPLUS || sy==DMINUS)
     {
        tag = (sy==DPLUS) ? INC : DEC;
        nextSymbol ();
        t1 = calc (tag, t1);
     }

     return t1;
  }

  private ExprDef unary_expr ()
  {
     ExprDef t1, t2;
     int tag;

     if (sy==BITNOT ||
         sy==LOGNOT ||
         sy==PLUS ||
         sy==MINUS ||
         sy==DPLUS ||
         sy==DMINUS)
     {
        tag = sy;
        nextSymbol ();
        t1 = unary_expr ();
        t1 = calc (tag, t1);
     }

     else if (sy==LPAR)
     {
        t1 = postfix_expr ();
        if (is_cast ())
        {
           t2 = unary_expr ();
           t1 = calc (CAST, t1, t2);
        }
     }

     else t1 = postfix_expr ();

     return t1;
  }

  private ExprDef mul_expr ()
  {
     ExprDef t1, t2;
     int tag;

     t1 = unary_expr ();

     while (sy==MUL ||
            sy==DIV ||
            sy==MOD)
     {
        tag = sy;
        nextSymbol ();
        t2 = unary_expr ();
        t1 = calc (tag, t1, t2);
     }

     return t1;
  }

  private ExprDef add_expr ()
  {
     ExprDef t1, t2;
     int tag;

     t1 = mul_expr ();

     while (sy==PLUS ||
            sy==MINUS)
     {
        tag = sy;
        nextSymbol ();
        t2 = mul_expr ();
        t1 = calc (tag, t1, t2);
     }

     return t1;
  }

  private ExprDef shift_expr ()
  {
     ExprDef t1, t2;
     int tag;

     t1 = add_expr ();

     while (sy==SHL ||
            sy==SHR ||
            sy==SAR)
     {
        tag = sy;
        nextSymbol ();
        t2 = add_expr ();
        t1 = calc (tag, t1, t2);
     }

     return (t1);
  }

  private ExprDef rel_expr ()
  {
     ExprDef t1, t2;
     int tag;

     t1 = shift_expr ();

     while (sy==LESS ||
            sy==GREATER ||
            sy==LESSEQUAL ||
            sy==GREATEREQUAL ||
            sy==INSTANCEOF)       /* ?? ReferenceType = Expression */
     {
        tag = sy;
        nextSymbol ();
        t2 = shift_expr ();
        t1 = calc (tag, t1, t2);
     }

     return t1;
  }

  private ExprDef equ_expr ()
  {
     ExprDef t1, t2;
     int tag;

     t1 = rel_expr ();
     while (sy==EQUAL ||
            sy==NOTEQUAL)
     {
        tag = sy;
        nextSymbol ();
        t2 = rel_expr ();
        t1 = calc (tag, t1, t2);
     }

     return t1;
  }

  private ExprDef and_expr ()
  {
     ExprDef t1, t2;

     t1 = equ_expr ();

     while (sy==AND)
     {
        nextSymbol ();
        t2 = equ_expr ();
        t1 = calc (AND, t1, t2);
     }

     return t1;
  }

  private ExprDef xor_expr ()
  {
     ExprDef t1, t2;

     t1 = and_expr ();

     while (sy==XOR)
     {
        nextSymbol ();
        t2 = and_expr ();
        t1 = calc (XOR, t1, t2);
     }

     return (t1);
  }

  private ExprDef or_expr ()
  {
     ExprDef t1, t2;

     t1 = xor_expr ();

     while (sy==OR)
     {
        nextSymbol ();
        t2 = xor_expr ();
        t1 = calc (OR, t1, t2);
     }

     return t1;
  }

  private ExprDef land_expr ()
  {
     ExprDef t1, t2;

     t1 = or_expr ();

     while (sy==LOGAND)
     {
        nextSymbol ();
        t2 = or_expr ();
        t1 = calc (LOGAND, t1, t2);
     }

     return t1;
  }

  private ExprDef lor_expr ()
  {
     ExprDef t1, t2;

     t1 = land_expr ();

     while (sy==LOGOR)
     {
        nextSymbol ();
        t2 = land_expr ();
        t1 = calc (LOGOR, t1, t2);
     }

     return t1;
  }

  private ExprDef cond_expr ()
  {
     ExprDef t1, t2, t3;

     t1 = lor_expr ();

     if (sy==QUESTION)
     {
        t2 = expression ();
        checkSymbol (COLON);
        t3 = cond_expr ();
        t1 = calc (QUESTION, t1, t2, t3);
     }

     return t1;
  }

  private ExprDef assignment_expr ()
  {
     ExprDef t1, t2;
     int tag;

     t1 = cond_expr ();

     if (sy==ASSIGN ||
         sy==MULASSIGN ||
         sy==DIVASSIGN ||
         sy==MODASSIGN ||
         sy==ADDASSIGN ||
         sy==SUBASSIGN ||
         sy==SHLASSIGN ||
         sy==SHRASSIGN ||
         sy==SARASSIGN ||
         sy==ANDASSIGN ||
         sy==XORASSIGN ||
         sy==ORASSIGN)
     {
        tag = sy;
        nextSymbol ();
        t2 = assignment_expr ();
        t1 = calc (tag, t1, t2);
     }

     return t1;
  }

  ExprDef expression ()
  {
     return assignment_expr ();
  }

}
