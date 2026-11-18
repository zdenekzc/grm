# Syntactic Analysis of Expressions

The files lex.h, lex.cc, decl.h and expr.cc contain a parser of a
simplified C language.
http://kmlinux.fjfi.cvut.cz/~culikzde/prekl/Comp11.tgz
or http://gitlab.fjfi.cvut.cz/culikzde/c-parser

We will process expressions that can contain identifiers, integers,
expressions in parentheses, plus and times:

```
  simple : identifier | number | '(' expr ')' ;
  mul    : simple ( '*' simple )* ;
  expr   : mul    ( ( '+' | '-' ) mul )* ;
```

A grammar rule starts with the name of the defined nonterminal and a
colon **:**.
Strings in quotes are terminal symbols.
Ordinary identifiers represent nonterminal symbols.
The vertical bar **|** represents *or*.
Parentheses with an asterisk **( )\*** allow repetition 0, 1, 2, ...
arbitrary many times.
Parentheses with a plus **( )+** allow repetition 1, 2, ... arbitrary
many times.
Parentheses with a question mark **( )?** allow repetition 0 or 1
times.
Parentheses without a following mark **( )** are mostly used when
writing several alternatives separated by a vertical bar.
A grammar rule ends with a semicolon **;**

## Functions Recognizing Simple Expressions

```cpp
void simple_expr (void)
{
  if (sy==IDENT)
  {
     NextSymbol ();
  }
  else if (sy==NUM)
  {
     NextSymbol ();
  }
  else if (sy==LPAR)
  {
     NextSymbol ();
     add_expr ();
     CheckSymbol (RPAR);
  }
  else Error ("Syntax error in expression");
}

void mul_expr (void)
{
  simple_expr ();
  while (sy==ASTERISK ||
         sy==SLASH ||
         sy==MOD)
  {
     NextSymbol ();
     simple_expr ();
  }
}

void add_expr (void)
{
  mul_expr ();
  while (sy==PLUS ||
         sy==MINUS)
  {
     NextSymbol ();
     mul_expr ();
  }
}
```

## Functions Creating Syntactic Trees

In the file expr.cc we find similar functions which additionally create
trees representing the recognized expressions:
http://gitlab.fjfi.cvut.cz/culikzde/c-parser/-/blob/master/expr.cc#L909

```cpp
ExprPtr simple_expr (void)
{
  ExprPtr t1;

  if (sy==IDENT ||
  {
     t1 = NewStr (IdentVal);
     NextSymbol ();
  }
  else if (sy==NUM)
  {
     t1 = NewStr (NumVal);
     NextSymbol ();
  }
  else if (sy==LPAR)
  {
     NextSymbol ();
     t1 = expression ();
     t1 = calc (t1, NULL, LPAR);
     CheckSymbol (RPAR);
  }
  else Error ("Syntax error in expression");

  return t1;
}

ExprPtr mul_expr (void)
{
  ExprPtr t1, t2;
  SYMBOL op;

  t1 = simple_expr ();
  while (sy==ASTERISK ||
         sy==SLASH ||
         sy==MOD)
  {
     op = sy;
     NextSymbol ();
     t2 = simple_expr ();
     t1 = calc (t1, t2, op);
  }
  return t1;
}

ExprPtr add_expr (void)
{
  ExprPtr t1, t2;
  SYMBOL op;

  t1 = mul_expr ();
  while (sy==PLUS ||
         sy==MINUS)
  {
     op = sy;
     NextSymbol ();
     t2 = mul_expr ();
     t1 = calc (t1, t2, op);
  }

  return t1;
}
```

The helper function **calc** creates a new tree node. For example

```
 t3 = calc (t1, t2, op);
```

stores into t3 a pointer to a new node which has the subtrees t1 and t2:

```
       op
       |
   .------.
   |      |
   t1     t2
```

The function **add_expr** gradually builds a tree out of the
multiplicative expressions.
If we have on the input

```
 A + B - C
```

the function add_expr creates the tree

```
          "-"
           |
       .------.
       |      |
      "+"      C
       |
   .------.
   |      |
   A      B
```

Pictures: Chapter 2, pages 9 and 10
http://inf.ethz.ch/personal/wirth/CompilerConstruction/CompilerConstruction1.pdf
Further information: chapters 4.1 and 4.2
