# A Grammar Describing the Grammar

The grammar notation used in the previous chapter can be regarded as a
programming language of its own kind.
We can write a grammar for this language:

## Grammar

The whole grammar is a sequence of rules:

```
   grammar : ( rule )* ;
```

## Rule

A rule is written as the rule name followed by a colon, the description
of the rule and a semicolon:

```
   rule : identifier ":" description ";" ;
```

*The colon and semicolon in quotes are the colon and semicolon mentioned
in the preceding sentence.*
*The colon and semicolon without quotes are part of the rule being
defined.*

## Expression Describing a Rule

The description of a rule is a sequence of one or more alternatives
separated by a vertical bar:

```
   description : alternative ( "|" alternative )* ;
```

:-) The vertical bar (or) can be regarded as a kind of additive operation.

## Alternative

An alternative is a sequence of simple items.
It may also be empty:

```
   alternative : ( simple )* ;
```

:-) Writing items one after another can be regarded as an analogue of a
multiplicative operation — we usually omit the multiplication sign there
as well.

## Simple Item

A simple item can be a string in double quotes (a terminal),
an identifier (a nonterminal), or an expression in parentheses:

```
   simple : string_literal | identifier | ebnf ;
```

## Expression in Parentheses

An expression in parentheses recursively uses the expression already
introduced for describing a rule (`description`).
A question mark, an asterisk or a plus may follow the parentheses:

```
   ebnf : "(" description ")" ( "?" | "*" | "+" | ) ;
```
