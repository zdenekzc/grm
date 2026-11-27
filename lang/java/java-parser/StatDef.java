
package cacao.src;

import java.util.Vector;

public class StatDef extends Const
{
  private int kind;
  private VarGroupDef decl;
  private Vector expr;
  private Vector stat;

  public StatDef (int p_kind)
  {
     kind = p_kind;
  }

  public void setDecl (VarGroupDef v)
  {
     // DECLARATION_STAT, FOR_INIT
     decl = v;
  }

  public void add (ExprDef e)
  {
     if (expr==null) expr = new Vector (2, 2);
     expr.add (e);
  }

  public void add (StatDef s)
  {
     if (stat==null) stat = new Vector (2, 2);
     stat.add (s);
  }

  /* ------------------------------------------------------------------- */

  public String getText ()
  {
     String s;

     switch (kind)
     {
        case BREAK:            s = "break"; break;
        case CONTINUE:         s = "continue"; break;
        case DO:               s = "do"; break;
        case FOR:              s = "for"; break;
        case IF:               s = "if"; break;
        case RETURN:           s = "return"; break;
        case SWITCH:           s = "switch"; break;
        case SYNCHRONIZED:     s = "synchronized"; break;
        case THROW:            s = "throw"; break;
        case TRY:              s = "try"; break;
        case WHILE:            s = "while"; break;

        case LABEL_STAT:       s = "label"; break;
        case EMPTY_STAT:       s = "empty statement"; break;
        case DECLARATION_STAT: s = "local declaration"; break;
        case EXPRESSION_STAT:  s = "expression"; break;
        case BLOCK_STAT:       s = "block"; break;

        case CASE:             s = "case"; break;
        case DEFAULT:          s = "default"; break;

        case CATCH:            s = "catch"; break;
        case FINALLY:          s = "finally"; break;

        case FOR_INIT:         s = "for init"; break;
        case FOR_CONDITION:    s = "for condition"; break;
        case FOR_UPDATE:       s = "for update"; break;

        default: s = "<" + kind + ">";
     }

     return s;
  }


}