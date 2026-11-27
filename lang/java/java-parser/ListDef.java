
package cacao.src;

import java.util.Vector;

public class ListDef
{

  private Vector vec = new Vector (4, 4);

  public ListDef ()
  {
  }

  public void add (NameDef item)
  {
     vec.add (item);
  }

  public int size ()
  {
     return vec.size ();
  }

  public NameDef get (int inx)
  {
     return (NameDef) vec.get (inx);
  }

}
