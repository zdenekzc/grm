# Choose — Delayed Decision

When processing arithmetic expressions it is not convenient to create a
new instance for every rule being processed:

```
simple_expr :          identifier | number  | "(" expr ")" ;
multiplicative_expr :  simple_expr ( ("*"|"/") simple_expr )* ;
additive_expr :        multiplicative_expr ( ("+"|"-") multiplicative_expr )* ;
expr :                 additive_expr ( "=" expr )? ;
```

If, for example, we process the expression A + B - C,
we are interested in the nodes corresponding to the additive expression
and in the leaves with the identifiers.

Nodes that do not store any arithmetic operation mostly make the tree
less clear.

## The Keyword choose before the Type of the Rule

```
additive_expr <choose CmmExpr> :
   multiplicative_expr
   (
      <new CmmAddExpr:CmmExpr>
      <store left:CmmExpr>
      ( '+' <set kind=addExp> |
        '-' <set kind=subExp> )
      right:multiplicative_expr
   )* ;
```

- Before the type of the rule we state the keyword **choose**.
- We begin the description of the rule with a nonterminal symbol, which
  will be the result if the variant in parentheses that follows does not
  occur
- The variant in parentheses is **( )?** or **( )***
- If the variant occurs, each repetition creates a new instance
  **\<new CmmAddExpr:CmmExpr\>**
- The original result or the previous variant is stored as an item of
  the new instance **\<store left:CmmExpr\>**
- Inside the variant there may be further branching, but everything is
  already stored into the created instance
- If some alternatives contain only terminals, for example
  **("+"|"-")**, we can set some item to a value of an enumeration type
  **\<set kind=addExp\>**

## Requirements for the Types Used

- The type of the initial nonterminal must be derived from the type of
  the rule
- The type used inside the variant must also be derived from the type of
  the rule

## The Generated Method of the Syntactic Analyzer

```python
   def parse_additive_expr (self) :
      result = self.parse_multiplicative_expr ()
      while self.tokenText == "+" or self.tokenText == "-" :
            store = result
            result = CmmAddExpr ()

            result.left = store

            if self.tokenText == "+" :
               self.check ("+")
               result.kind = result.addExp
            elif self.tokenText == "-" :
               self.check ("-")
               result.kind = result.subExp
            else :
               self.error ("Unexpected token")

            result.right = self.parse_multiplicative_expr ()
      return result
```

If the input is, for example, A + B - C, the following tree is created:

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

Into the variable **result** the value **A** is first stored by the call
of **parse_multiplicative_expr**.

Since a plus follows, we save the original value of **result** into the
variable **store**.
Into **result** we store a new node for the arithmetic operation of the
type **CmmAddExpr**.
We store the original value (**A**) into **result.left**.
We set **result.kind** to **addExp** or **subExp**.
We store the right operand (**B**) into **result.right**.

Now the **while** loop repeats.
Since a minus follows, we save the current result (**A+B**),
and we create a new instance, this time for the minus.

If no further plus or minus follows, the function ends and the result is
the sketched tree.
You can compare this with the introductory chapter [syntactic analysis
of expressions](expr.md).

## The Generated Method for Printing the Source Text

The printing method first tests whether the parameter is not of the type
of our variant **CmmAddExpr**.
For printing the left operand it recursively uses the same method.

At the end of the method there is the *else* branch for the case that
our variant did not occur:

```python
   def send_additive_expr (self, param) :
      if isinstance (param, CmmAddExpr) :
         self.send_additive_expr (param.left)
         if param.kind == param.addExp :
            self.send ("+")
         elif param.kind == param.subExp :
            self.send ("-")
         self.send_multiplicative_expr (param.right)
      else :
         self.send_multiplicative_expr (param)
```
