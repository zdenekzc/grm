# A Grammar Describing the Statements of a Simplified C Language

```
while_stat :  "while" "(" expr ")" stat   ;

if_stat    :  "if" "(" expr ")" stat ( "elif" "(" expr")" stat  )* ( "else" stat  )?   ;

compound_stat : "{" ( stat )* "}" ;

simple_stat :  expr ";" ;

empty_stat :  ";" ;

stat : while_stat | if_stat | compound_stat | simple_stat | empty_stat ;


simple_expr : identifier | number  | "(" expr ")" ;

mult_expr :  simple_expr ( ("*"|"/") simple_expr )* ;
```
