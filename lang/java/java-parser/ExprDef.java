
package cacao.src;

import java.util.Vector;

public class ExprDef extends Const
{

  private int kind;
  private ExprDef e1, e2, e3; /* subexpressions */
  private String val;         /* identifier, number, string */
  private Vector params;      /* list of expressions */

  public ExprDef (int p_kind)
  {
     kind = p_kind;
  }

  public ExprDef (int p_kind, ExprDef p1)
  {
     kind = p_kind;
     e1 = p1;
  }

  public ExprDef (int p_kind, ExprDef p1, ExprDef p2)
  {
     kind = p_kind;
     e1 = p1;
     e2 = p2;
  }

  public ExprDef (int p_kind, ExprDef p1, ExprDef p2, ExprDef p3)
  {
     kind = p_kind;
     e1 = p1;
     e2 = p2;
     e3 = p3;
  }

  public ExprDef (int p_kind, String p1)
  {
     kind = p_kind;
     val = p1;
  }

  public void addParam (ExprDef p)
  {
     if (params==null) params = new Vector (4, 4);
     params.add (p);
  }

  /* ------------------------------------------------------------------- */

  public String getText ()
  {
     String s;

     switch (kind)
     {
        case IDENT:  s = "IDENTIFIER " + val; break;
        case NUMBER: s = "NUMBER " + val; break;
        case FLT:    s = "FLOAT " + val; break;
        case STR:    s = "STRING " + val; break;
        case CHR:    s = "CHAR " + val; break;

        case FCE :   s = "function call"; break;
        case LBRACE: s = "{}"; break;

        case LPAR:    s = "()"; break;
        case LBRACK:  s = "[]"; break;
        case PERIOD:  s = "."; break;

        case ASSIGN:    s = "="; break;
        case LESS:      s = "<"; break;
        case GREATER:   s = ">"; break;
        case LOGNOT:    s = "!"; break;
        case BITNOT:    s = "~"; break;
        case QUESTION:  s = "?:"; break;

        case EQUAL:        s = "=="; break;
        case LESSEQUAL:    s = "<="; break;
        case GREATEREQUAL: s = ">="; break;
        case NOTEQUAL:     s = "!="; break;
        case LOGAND:       s = "&&"; break;
        case LOGOR:        s = "||"; break;
        case DPLUS:        s = "pre increment"; break;
        case DMINUS:       s = "pre decrement"; break;

        case PLUS:  s = "+"; break;
        case MINUS: s = "-"; break;
        case MUL:   s = "*"; break;
        case DIV:   s = "/"; break;
        case AND:   s = "&"; break;
        case OR:    s = "|"; break;
        case XOR:   s = "^"; break;
        case MOD:   s = "%"; break;
        case SHL:   s = "<<"; break;
        case SAR:   s = ">>"; break;
        case SHR:   s = ">>>"; break;

        case ADDASSIGN: s = "+="; break;
        case SUBASSIGN: s = "-="; break;
        case MULASSIGN: s = "*="; break;
        case DIVASSIGN: s = "/="; break;
        case ANDASSIGN: s = "&="; break;
        case ORASSIGN:  s = "|="; break;
        case XORASSIGN: s = "^="; break;
        case MODASSIGN: s = "%="; break;
        case SHLASSIGN: s = "<<="; break;
        case SARASSIGN: s = ">>="; break;
        case SHRASSIGN: s = ">>>="; break;

        case BOOLEAN: s = "boolean"; break;
        case CHAR:    s = "char"; break;
        case SHORT:   s = "short"; break;
        case BYTE:    s = "byte"; break;
        case INT:     s = "int"; break;
        case LONG:    s = "long"; break;
        case FLOAT:   s = "float"; break;
        case DOUBLE:  s = "double"; break;
        case VOID:    s = "void"; break;

        case TRUE:       s = "true"; break;
        case FALSE:      s = "false"; break;
        case NULL:       s = "null"; break;
        case THIS:       s = "this"; break;
        case SUPER:      s = "super"; break;
        case NEW:        s = "new"; break;
        case INSTANCEOF: s = "instanceof"; break;

        case DIM : s = "dim []"; break;
        case CAST: s = "type cast"; break;
        case INC : s = "post increment"; break;
        case DEC : s = "post decrement"; break;

        default: s = "<" + kind + ">";
     }

     return s;
  }

}
