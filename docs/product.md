# Printing a Program Stored in the Syntactic Tree

The source text stored in the syntactic tree is printed by the
**Product** class.

The generator creates this class similarly to the **Parser** class.
The source text is not read from the input; the data are obtained from
the nodes of the syntactic tree.
The decision-making when selecting alternatives is also based on the
stored data.

```python
class Product (Output) :

   def send_if_stat (self, param) :
       self.send ("if")
       self.send ("(")
       self.send_expr (param.cond)
       self.send (")")
       self.send_stat (param.then_code)
       if param.else_code != None :
         self.style_new_line ()
         self.send ("else")
         self.send_stat (param.else_code)
```

```cpp
void CmmProduct::send_if_stat (CmmIfStat * item)
{
   send ("if");
   send ("(");
   send_expr (item->cond);
   send (")");
   send_stat (item->then_code);
   if (item->else_code != NULL)
   {
      style_new_line ();
      send ("else");
      send_stat (item->else_code);
   }
}
```
