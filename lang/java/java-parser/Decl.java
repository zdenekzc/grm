
package cacao.src;

import java.lang.reflect.Modifier;

public class Decl extends Stat
{

  /* ------------------------------------------------------------------- */

  private String identifier ()
  {
     if (sy != IDENT) error ("Identifier expected");
     String s = val;
     nextSymbol ();
     return s;
  }

  private NameDef name ()
  {
     NameDef n = new NameDef ();

     n.add (identifier ());

     while (sy==PERIOD)
     {
        nextSymbol ();
        n.add (identifier ());
     }

     return n;
  }

  private NameDef importName ()
  {
     NameDef n = new NameDef ();

     n.add (identifier ());

     while (sy==PERIOD)
     {
        nextSymbol ();

        if (sy==MUL)
        {
           nextSymbol ();
           n.add ("*");
           break; /* <- */
        }
        else
        {
           n.add (identifier ());
        }
     }

     return n;
  }

  private ListDef nameList ()
  {
     ListDef list = new ListDef ();
     list.add (name ());

     while (sy==COMMA)
     {
        nextSymbol ();
        list.add (name ());
     }

     return list;
  }

  private int modifiers ()
  {
     int m = 0;
     while (true)
     {
             if (sy==PUBLIC)       m |= Modifier.PUBLIC;
        else if (sy==PROTECTED)    m |= Modifier.PROTECTED;
        else if (sy==PRIVATE)      m |= Modifier.PRIVATE;
        else if (sy==STATIC)       m |= Modifier.STATIC;
        else if (sy==ABSTRACT)     m |= Modifier.ABSTRACT;
        else if (sy==FINAL)        m |= Modifier.FINAL;
        else if (sy==NATIVE)       m |= Modifier.NATIVE;
        else if (sy==SYNCHRONIZED) m |= Modifier.SYNCHRONIZED;
        else if (sy==TRANSIENT)    m |= Modifier.TRANSIENT;
        else if (sy==VOLATILE)     m |= Modifier.VOLATILE;
        else break; /* <- */
        nextSymbol ();
     }
     return m;
  }

  /* ------------------------------------------------------------------- */

  private NameDef type ()
  {
     NameDef n;

     if (sy==BOOLEAN ||
         sy==BYTE ||
         sy==SHORT ||
         sy==INT ||
         sy==LONG ||
         sy==CHAR ||
         sy==FLOAT ||
         sy==DOUBLE)
     {
         n = new NameDef ();
         n.add (val);
         nextSymbol ();
     }
     else
     {
         n = name ();
     }

     brackets ();
     return n;
  }

  private NameDef typeOrVoid ()
  {
     NameDef n;

     if (sy==VOID)
     {
         n = new NameDef ();
         n.add (val);
         nextSymbol ();
     }
     else
     {
         n = type ();
     }

     return n;
  }

  /* ------------------------------------------------------------------- */

  public PackageDef packageDecl ()
  {
     PackageDef pkg = new PackageDef ();

     if (sy==PACKAGE)    /* package declaration */
     {
        nextSymbol ();
        pkg.setName (name ());
        checkSemicolon ();
     }

     while (sy == IMPORT)    /* import declarations */
     {
        nextSymbol ();
        pkg.addImport (importName ());
        checkSemicolon ();
     }

     while (sy!=EOS)
     {
        if (sy==SEMICOLON)
           nextSymbol ();
        else
        {
           int mod = modifiers ();
           if (sy==CLASS)
              classDecl (mod);
           else if (sy==INTERFACE)
              interfaceDecl (mod);
           else
              error ("Class or interface declaration expected");
        }
     }

     return pkg;
  }

  /* ------------------------------------------------------------------- */

  private ClassDef classDecl (int mod)
  {
     checkSymbol (CLASS);

     ClassDef cls = new ClassDef ();
     cls.setKind (CLASS);
     cls.setModifiers (mod);

     cls.setIdent (identifier ());

     if (sy==EXTENDS)
     {
        nextSymbol ();
        cls.setSuperClass (name ());
     }

     if (sy==IMPLEMENTS)
     {
        nextSymbol ();
        cls.setInterfaces (nameList ());
     }

     checkSymbol (LBRACE);

     while (sy != RBRACE)
        classBodyDecl (cls);

     checkSymbol (RBRACE);

     return cls;
  }

  private void classBodyDecl (ClassDef cls)
  {
     int     mod = modifiers ();
     NameDef typ = typeOrVoid ();

     if (sy==LBRACE)
     {
        initializer (cls, mod);
     }
     else if (sy==LPAR)
     {
        constructorDecl (cls, mod, typ);
     }
     else
     {
        String id = identifier ();

        if (sy == LPAR)
           methodDecl (cls, mod, typ, id);
        else
           fieldDecl (cls, mod, typ, id);
     }
  }

  /* ------------------------------------------------------------------- */

  private ClassDef interfaceDecl (int mod)
  {
     checkSymbol (INTERFACE);

     ClassDef cls = new ClassDef ();
     cls.setKind (INTERFACE);
     cls.setModifiers (mod);

     cls.setIdent (identifier ());

     if (sy==EXTENDS)
     {
        nextSymbol ();
        cls.setInterfaces (nameList ());
     }

     checkSymbol (LBRACE);

     while (sy != RBRACE)
        interfaceMemberDecl (cls);

     checkSymbol (RBRACE);

     return cls;
  }

  private void interfaceMemberDecl (ClassDef cls)
  {
     int     mod = modifiers ();
     NameDef typ = typeOrVoid ();
     String  id  = identifier ();

     if (sy == LPAR)
        methodDecl (cls, mod, typ, id);
     else
        fieldDecl (cls, mod, typ, id);
  }

  /* ------------------------------------------------------------------- */

  private void fieldDecl (ClassDef cls, int mod, NameDef typ, String id)
  {
     variableDecl (cls, mod, typ, id);

     while (sy==COMMA)
     {
        nextSymbol ();
        id = identifier ();
        variableDecl (cls, mod, typ, id);
     }
  }

  private void variableDecl (ClassDef cls, int mod, NameDef typ, String id)
  {
     DeclDef dcl = new DeclDef (FIELD_DECL);
     brackets ();

     if (sy==ASSIGN)
     {
        nextSymbol ();
        dcl.setInit (variableInitializer ());
     }

     cls.addDecl (dcl);
  }

  /* ------------------------------------------------------------------- */

  private void methodDecl (ClassDef cls, int mod, NameDef typ, String id)
  {
     DeclDef dcl = new DeclDef (METHOD_DECL);

     formalParameterList (dcl);
     brackets ();
     throwList (dcl);

     if (sy==SEMICOLON)
        nextSymbol ();
     else
        dcl.setBody (block ());

     cls.addDecl (dcl);
  }

  private void formalParameter ()
  {
     type ();
     identifier ();
     brackets ();
  }

  private void formalParameterList (DeclDef dcl)
  {
     checkSymbol (LPAR);
     while (sy != RPAR)
        /* ?? */
        formalParameter ();
     checkSymbol (RPAR);
  }

  private void brackets ()
  {
     while (sy==LBRACK)
     {
        nextSymbol ();
        checkSymbol (RBRACK);
        /* ?? */
     }
  }

  private void throwList (DeclDef dcl)
  {
     if (sy==THROWS)
     {
        nextSymbol ();
        dcl.addException (name ());

        while (sy==COMMA)
        {
           nextSymbol ();
           dcl.addException (name ());
        }
     }
  }

  /* ------------------------------------------------------------------- */

  private void constructorDecl (ClassDef cls, int mod, NameDef typ)
  {
     /* ?? check if typ is class identifier */

     DeclDef dcl = new DeclDef (CONSTRUCTOR_DECL);
     dcl.setModifiers (mod);
     dcl.setType (typ);

     formalParameterList (dcl);
     throwList (dcl);
     dcl.setBody (block ());

     cls.addDecl (dcl);
  }

  /* ------------------------------------------------------------------- */

  private void initializer (ClassDef cls, int mod)
  {
     if (mod!=0 && mod!=Modifier.STATIC)
        error ("Invalid modifiers");

     DeclDef dcl = new DeclDef (INITIALIZER_DECL);
     dcl.setModifiers (mod);
     dcl.setBody (block ());

     cls.addDecl (dcl);
  }

}

