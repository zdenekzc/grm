
package cacao.src;

import java.util.Vector;

public class VarGroupDef
{

  private ExprDef type;
  private Vector items;

  public VarGroupDef ()
  {
  }

  public void setType (ExprDef t)
  {
     type = t;
  }

  public void addItem (VarItemDef p)
  {
     if (items==null) items = new Vector (4, 4);
     items.add (p);
  }

}

