
package cacao.src;

import java.util.Vector;

public class ClassDef
{
  private int     modifiers;
  private int     kind;        /* CLASS / INTERFACE */
  private String  ident;
  private NameDef superClass;
  private ListDef interfaces;
  private Vector  declarations;

  public ClassDef ()
  {
  }

  public void setModifiers (int m)
  {
     modifiers = m;
  }

  public void setKind (int k)
  {
     kind = k;
  }

  public void setIdent (String s)
  {
     ident = s;
  }

  public void setSuperClass (NameDef n)
  {
     superClass = n;
  }

  public void setInterfaces (ListDef list)
  {
     interfaces = list;
  }

  public void addDecl (DeclDef d)
  {
     if (declarations==null) declarations = new Vector (10, 10);
     declarations.add (d);
  }

}
