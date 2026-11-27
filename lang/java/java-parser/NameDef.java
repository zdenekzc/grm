
package cacao.src;

import java.util.Vector;

public class NameDef
{
  private Vector vec = new Vector (4, 4);

  public NameDef ()
  {
  }

  public void add (String item)
  {
     vec.add (item);
  }

  public int size ()
  {
     return vec.size ();
  }

  public String get (int inx)
  {
     return (String) vec.get (inx);
  }

}
