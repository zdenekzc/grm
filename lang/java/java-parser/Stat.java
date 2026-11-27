
package cacao.src;

public class Stat extends Expr
{

  /* ------------------------------------------------------------------- */

  private VarGroupDef localVariableDeclaration (ExprDef typ)
  {
     /* ?? check if typ is valid type */
     VarGroupDef v = new VarGroupDef ();
     v.setType (typ);

     variableDeclarator (v);

     while (sy==COMMA)
     {
        nextSymbol ();
        variableDeclarator (v);
     }

     return v;
  }

  private void variableDeclarator (VarGroupDef v)
  {
     if (sy!=IDENT) error ("Identifier expected");
     String id = val; /* ?? ukladani */
     nextSymbol ();

     VarItemDef item = new VarItemDef (id);
     v.addItem (item);

     while (sy==LBRACK)
     {
        nextSymbol ();
        checkSymbol (RBRACK);
        item.addBracket ();
     }

     if (sy==ASSIGN)
     {
        nextSymbol ();
        item.setInit (variableInitializer ());
     }
  }

  public ExprDef variableInitializer ()
  {
     if (sy==LBRACE)
        return arrayInitializer ();
     else
        return expression ();
  }

  private ExprDef arrayInitializer ()
  {
     checkSymbol (LBRACE);
     ExprDef e = new ExprDef (LBRACE);

     if (sy != RBRACE)
     {
        e.addParam (variableInitializer ());

        while (sy==COMMA)
        {
           nextSymbol ();
           if (sy==RBRACE) break; /* <- */
           e.addParam (variableInitializer ());
        }
     }

     checkSymbol (RBRACE);
     return e;
  }

  /* ------------------------------------------------------------------- */

  private VarGroupDef formalParameter ()
  {
     VarGroupDef v = new VarGroupDef ();

     ExprDef typ = expression ();
     /* ?? check if typ is valid type */
     v.setType (typ);

     if (sy!=IDENT) error ("Identifier expected");
     String id = val; /* ?? ukladani */
     nextSymbol ();

     VarItemDef item = new VarItemDef (id);
     v.addItem (item);

     while (sy==LBRACK)
     {
        nextSymbol ();
        checkSymbol (RBRACK);
        item.addBracket ();
     }

     return v;
  }

  /* ------------------------------------------------------------------- */

  public StatDef block ()
  {
     checkSymbol (LBRACE);
     StatDef s = new StatDef (BLOCK_STAT);

     while (sy!=RBRACE)
        s.add (statement ());

     checkSymbol (RBRACE);
     return s;
  }

  /* ------------------------------------------------------------------- */

  private StatDef switchStatement ()
  {
     StatDef s;

     if (sy==CASE)
     {
        s = new StatDef (CASE);
        nextSymbol ();

        s.add (expression ());
        checkSymbol (COLON);
     }

     else if (sy==DEFAULT)
     {
        s = new StatDef (DEFAULT);
        nextSymbol ();
        checkSymbol (COLON);
     }

     else s = statement ();

     return s;
  }

  private StatDef switchBlock ()
  {
     checkSymbol (LBRACE);
     StatDef s = new StatDef (BLOCK_STAT);

     while (sy!=RBRACE)
     {
        s.add (switchStatement ());
     }

     checkSymbol (RBRACE);
     return s;
  }

  /* ------------------------------------------------------------------- */

  private StatDef forInit ()
  {
     StatDef s = new StatDef (FOR_INIT);

     if (sy!=SEMICOLON)
     {
        ExprDef e = expression ();

        if (sy!=COMMA && sy!=SEMICOLON)
        {
           // ?? check if expression is type
           VarGroupDef v = localVariableDeclaration (e);
           s.setDecl (v);
        }
        else
        {
           s.add (e);
           while (sy==COMMA)
           {
              nextSymbol ();
              s.add (expression ());
           }
        }
     }

     return s;
  }

  private StatDef forCondition ()
  {
     StatDef s = new StatDef (FOR_CONDITION);
     if (sy!=SEMICOLON)
        s.add (expression ());
     return s;
  }

  private StatDef forUpdate ()
  {
     StatDef s = new StatDef (FOR_UPDATE);
     if (sy!=RPAR)
     {
        s.add (expression ());

        while (sy==COMMA)
        {
           nextSymbol ();
           s.add (expression ());
        }
     }
     return s;
  }

  /* ------------------------------------------------------------------- */

  /*
  private void formalParameterList (DeclDef dcl)
  {
     checkSymbol (LPAR);
     while (sy != RPAR)
        // ??
        formalParameter ();
     checkSymbol (RPAR);
  }

  private void brackets (DeclDef dcl)
  {
     while (sy==LBRACK)
     {
        nextSymbol ();
        checkSymbol (RBRACK);
        // ??
     }
  }
  */

  /* ------------------------------------------------------------------- */

  public StatDef statement ()
  {
     StatDef s;

     if (sy==LBRACE)                             /* block */
     {
        s = block ();
     }

     else if (sy==WHILE)                         /* while */
     {
        s = new StatDef (WHILE);
        nextSymbol ();

        checkSymbol (LPAR);
        s.add (expression ());
        checkSymbol (RPAR);

        s.add (statement ());
     }

     else if (sy==DO)                            /* do */
     {
        s = new StatDef (DO);
        nextSymbol ();

        s.add (statement ());

        checkSymbol (WHILE);
        checkSymbol (LPAR);
        s.add (expression ());
        checkSymbol (RPAR);
        checkSemicolon ();
     }

     else if (sy==FOR)                           /* for */
     {
        s = new StatDef (FOR);
        nextSymbol ();

        checkSymbol (LPAR);
        s.add (forInit ());
        checkSemicolon ();

        s.add (forCondition ());
        checkSemicolon ();

        s.add (forUpdate ());
        checkSymbol (RPAR);

        s.add (statement ());
     }

     else if (sy==IF)                            /* if */
     {
        s = new StatDef (IF);
        nextSymbol ();

        checkSymbol (LPAR);
        s.add (expression ());
        checkSymbol (RPAR);

        s.add (statement ());

        if (sy==ELSE)
        {
           nextSymbol ();
           s.add (statement ());
        }
     }

     else if (sy==SWITCH)                        /* switch */
     {
        s = new StatDef (SWITCH);
        nextSymbol ();

        checkSymbol (LPAR);
        s.add (expression ());
        checkSymbol (RPAR);

        s.add (switchBlock ());
     }

     else if (sy==BREAK)                         /* break */
     {
        s = new StatDef (BREAK);
        nextSymbol ();
        if (sy!=SEMICOLON)
           s.add (identifier_expr ());
        checkSemicolon ();
     }

     else if (sy==CONTINUE)                      /* continue */
     {
        s = new StatDef (CONTINUE);
        nextSymbol ();
        if (sy!=SEMICOLON)
           s.add (identifier_expr ());
        checkSemicolon ();
     }

     else if (sy==RETURN)                        /* return */
     {
        s = new StatDef (RETURN);
        nextSymbol ();
        if (sy!=SEMICOLON)
           s.add (expression ());
        checkSemicolon ();
     }

     else if (sy==THROW)                         /* throw */
     {
        s = new StatDef (THROW);
        nextSymbol ();
        s.add (expression ());
        checkSemicolon ();
     }

     else if (sy==SYNCHRONIZED)                  /* synchronized */
     {
        s = new StatDef (SYNCHRONIZED);
        nextSymbol ();

        checkSymbol (LPAR);
        s.add (expression ());
        checkSymbol (RPAR);

        s.add (block ());
     }

     else if (sy==TRY)                           /* try */
     {
        s = new StatDef (THROW);
        nextSymbol ();
        s.add (block ());

        if (sy!=CATCH && sy!=FINALLY)
           error ("CATCH or FINALLY expected");

        while (sy==CATCH)
        {
           nextSymbol ();
           StatDef c = new StatDef (CATCH);

           checkSymbol (LPAR);
           c.setDecl (formalParameter ());
           checkSymbol (RPAR);
           c.add (block ());

           s.add (c);
        }

        if (sy==FINALLY)
        {
           nextSymbol ();
           StatDef f = new StatDef (FINALLY);
           f.add (block ());
           s.add (f);
        }
     }

     else if (sy==SEMICOLON)                     /* empty statement */
     {
        s = new StatDef (EMPTY_STAT);
        nextSymbol ();
     }

     else
     {
        ExprDef e = expression ();

        if (sy==COLON)                           /* labeled statement */
        {
           /* ?? check if expression is identifier */
           nextSymbol ();
           s = new StatDef (LABEL_STAT);
           s.add (e);
           s.add (statement ());
        }

        else if (sy==SEMICOLON)                  /* expression statement */
        {
           /* ?? StatementExpression = Expression */
           nextSymbol ();
           s = new StatDef (EXPRESSION_STAT);
           s.add (e);
        }

        else                                     /* local variable declaration */
        {
           /* ?? check if expression is type */
           /* ?? BlockStatement = Statement */

           VarGroupDef v = localVariableDeclaration (e);
           s = new StatDef (DECLARATION_STAT);
           s.setDecl (v);
           checkSemicolon ();
        }
     }

     return s;

  } // end of method

} // end of class

