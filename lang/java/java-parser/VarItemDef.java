
package cacao.src;

public class VarItemDef
{

  private String ident;
  private int brackets;
  private ExprDef init;

  public VarItemDef (String p_ident)
  {
     ident = p_ident;
  }

  public void addBracket ()
  {
     brackets ++;
  }

  public void setInit (ExprDef e)
  {
     init = e;
  }

}
