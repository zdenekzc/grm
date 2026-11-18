# Select — Class Inheritance

The keyword **select** before the type of the rule.

The rule is formed by a choice from several simple alternatives,
which have a resulting type derived from the type of the mentioned rule:

```
   stat < select TStat > :
      while_stat | if_stat | compound_stat | simple_stat | empty_stat ;
```

The created method **parse_stat** does not itself create a new instance;
it uses the instance supplied by the method **parse_while_stat**,
**parse_if_stat**, ...:

```python
   def parse_stat (self) :
      if self.tokenText == "while" :
         result = self.parse_while_stat ()
      elif self.tokenText == "if" :
         result = self.parse_if_stat ()
      elif self.tokenText == "{" :
         result = self.parse_compound_stat ()
      elif self.token == self.identifier or self.token == self.number or self.tokenText == "(" :
         result = self.parse_simple_stat ()
      elif self.tokenText == ";" :
         result = self.parse_empty_stat ()
      else :
         self.error ("Unexpected token")
      return result
```

The method for printing the source text stored in the syntactic tree,
**send_stat**,
tests the actual type of the parameter and calls **send_while_stat**,
...:

```python
   def send_stat (self, param) :
      if isinstance (param, TWhileStat) :
         self.send_while_stat (param)
      elif isinstance (param, TIfStat) :
         self.send_if_stat (param)
      elif isinstance (param, TCompoundStat) :
         self.send_compound_stat (param)
      elif isinstance (param, TSimpleStat) :
         self.send_simple_stat (param)
      elif isinstance (param, TEmptyStat) :
         self.send_empty_stat (param)
```

Here are the generated classes for storing the data:

```python
class TStat :
   pass

class TWhileStat (TStat) :
   def __init__ (self) :
      super (TWhileStat, self).__init__ ()
      self.cond = None
      self.code = None
```

# The Same in C++

```cpp
CmmStat *  CmmParser::parse_stat ()
{
   CmmStat * result = NULL;
   if (isSymbol (KEYWORD_while))
      result = parse_while_stat ();
   else if (isSymbol (KEYWORD_if))
      result = parse_if_stat ();
   else if (isSymbol (LBRACE))
      result = parse_compound_stat ();
   else if (TestSymbols (set_11))
      result = parse_simple_stat ();
   else if (isSymbol (SEMICOLON))
      result = parse_empty_stat ();
   else
      error ("Unexpected symbol");
   return result;
}

const unsigned char set_11 [] = { ... };
```

The set set_11 contains the symbols with which a simple statement can
begin.

```cpp
void CmmProduct::send_stat (CmmStat *  item)
{
    if (item->conv_CmmWhileStat () != NULL)
        send_while_stat (item->conv_CmmWhileStat ());
    else if (item->conv_CmmIfStat () != NULL)
        send_if_stat (item->conv_CmmIfStat ());
    else if (item->conv_CmmCompoundStat () != NULL)
        send_compound_stat (item->conv_CmmCompoundStat ());
    else if (item->conv_CmmSimpleStat () != NULL)
      send_simple_stat (item->conv_CmmSimpleStat ());
    else if (item->conv_CmmEmptyStat () != NULL)
       send_empty_stat (item->conv_CmmEmptyStat ());
    else
      assert (false);
}
```

For type testing one can use **dynamic_cast**.
Or simple virtual functions such as **conv_CmmIfStat**,
**conv_CmmWhileStat**:

```cpp
class CmmStat
{
   // conversion functions
   public:
      virtual CmmIfStat *  conv_CmmIfStat () { return NULL; }
      virtual CmmWhileStat *  conv_CmmWhileStat () { return NULL; }
};

class CmmWhileStat : public CmmStat
{
   public:
      CmmExpr *  cond;
      CmmStat *  body;

   // conversion functions
   public:
      virtual CmmWhileStat *  conv_CmmWhileStat () { return this; }
};
```
