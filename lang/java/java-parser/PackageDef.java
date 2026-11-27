
package cacao.src;

import java.util.Vector;

public class PackageDef
{

   private NameDef name;
   private ListDef imports;
   private Vector classes;

   public PackageDef ()
   {
   }

   public void setName (NameDef p)
   {
      name = p;
   }

   public void addImport (NameDef p)
   {
      if (imports==null) imports = new ListDef ();
      imports.add (p);
   }

   public void addClass (ClassDef c)
   {
      if (classes==null) classes = new Vector (2, 2);
      classes.add (c);
   }

}
