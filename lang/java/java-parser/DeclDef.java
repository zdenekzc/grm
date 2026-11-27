
package cacao.src;

import java.util.Vector;

public class DeclDef
{

  private int kind;
  private int modifiers;
  private NameDef type;
  private Vector exceptions;
  private ExprDef init;
  private StatDef body;

  public DeclDef (int p_kind)
  {
     kind = p_kind;
  }

  public void setModifiers (int m)
  {
     modifiers = m;
  }

  public void setType (NameDef t)
  {
     type = t;
  }

  public void addException (NameDef t)
  {
     if (exceptions==null) exceptions = new Vector (2, 2);
     exceptions.add (t);
  }

  public void setInit (ExprDef e)
  {
     init = e;
  }

  public void setBody (StatDef s)
  {
     body = s;
  }

}
