
# tocopy.py

from __future__ import print_function

from grammar import Grammar, Rule, Expression, Alternative, Ebnf, Nonterminal, Terminal, Directive, Assign, Style, New, Execute
from output import Output

# --------------------------------------------------------------------------

class ToCopy (Output) :

   enable_arit = False

   def conditionFromAlternative (self, grammar, alt) :
       for item in alt.items :
           if isinstance (item, Nonterminal) :
              if item.variable != "" :
                 return "param." + item.variable + " != None"
              elif item.add :
                 return "inx < cnt"
              elif item.select_item or item.continue_item :
                 rule_ref = item.rule_ref
                 if rule_ref.tag_name != "" :
                    return "param." + rule_ref.tag_name + " == " + "param." + rule_ref.tag_value
                 else :
                    return "isinstance (param, " + rule_ref.rule_type + ")"
           elif isinstance (item, Terminal) :
              if item.multiterminal_name != "" :
                 return "param." + item.variable + " != " + '"' + '"'
           elif isinstance (item, New) :
              # type = grammar.struct_dict [item.new_type]
              # if type.tag_name != "" : # !?
              #    return "param." + type.tag_name + " == " + "param." + type.tag_value
              # else :
                 return "isinstance (param, " + item.new_type + ")"
           elif isinstance (item, Assign) :
              prefix = ""
              if item.value != "True" and item.value != "False" :
                 prefix = "param."
              return "param." + item.variable + " == " + prefix + item.value
       return "unknown"
       # grammar.error ("Cannot find condition")

   def conditionFromExpression (self, grammar, expr) :
       result = ""
       for alt in expr.alternatives :
           if result != "" :
              result = result + " or "
           result = result + self.conditionFromAlternative (grammar, alt)
       return result

   def conditionIsUnknown (self, cond) :
       return (cond == "unknown")

   def conditionIsLoop (self, grammar, expr) :
       result = False
       for alt in expr.alternatives :
           cond = self.conditionFromAlternative (grammar, alt)
           if cond == "inx < cnt" :
              result = True
       return result

# --------------------------------------------------------------------------

   def executeMethod (self, grammar, func_dict, rule_name, no_param = False) :
       # if rule_name in func_dict :
       #    method_name = func_dict [rule_name]
       #    if no_param :
       #       self.putLn ("self." + method_name + " ()")
       #    else :
       #       self.putLn ("self." + method_name + " (result)")
       pass

# --------------------------------------------------------------------------

   def copyFromRules (self, grammar) :
       self.last_rule = None
       for rule in grammar.rules :
           if not self.isArit (grammar, rule.name) :
              self.copyFromRule (grammar, rule)

   def copyFromRule (self, grammar, rule) :
       grammar.updatePosition (rule)
       self.last_rule = rule
       if rule.rule_mode != "" :

          params = "param"
          # if rule.rule_mode == "modify" :
          #    params = "result"
          if rule.store_name != "" :
             params = params + ", store"

          self.putLn ("def copy_" + rule.name + " (self, " + params + ") :")
          self.incIndent ()

          if rule.rule_mode == "modify" :
             if grammar.show_tree :
                self.putLn ("if self.monitor : self.monitor.reopenObject (result)")

          if rule.rule_mode == "new" :
             self.putLn ("result = " + rule.rule_type + " ()")
             if rule.tag_name != "" :
                self.putLn ("result." + rule.tag_name + " = result." + rule.tag_value)
             self.putLn ("self.copyLocation (result)")
             if grammar.show_tree :
                self.putLn ("if self.monitor : self.monitor.openObject (result)")

          if rule.store_name != "" :
             self.putLn ("result." + rule.store_name + " = store")

          self.executeMethod (grammar, grammar.execute_on_begin, rule.name)
          self.executeMethod (grammar, grammar.execute_on_begin_no_param, rule.name, no_param = True)

          if rule.add_used :
             self.putLn ("inx = 0")
             self.putLn ("cnt = len (param.items)")

          self.copyFromExpression (grammar, rule, rule.expr)

          self.executeMethod (grammar, grammar.execute_on_end, rule.name)

          if rule.rule_mode == "new" or rule.rule_mode == "modify" :
             if grammar.show_tree :
                self.putLn ("if self.monitor : self.monitor.closeObject ()")

          self.putLn ("return result")
          self.decIndent ()
          self.putEol ()

   def copyChooseItem (self, grammar, rule, alt, target, field, enable_recursion) :
       if self.isArit (grammar, alt.select_nonterm.rule_name) :
          proc = "expression"
       else :
          proc = alt.select_nonterm.rule_name
       if enable_recursion :
          mark = alt.select_ebnf.mark
          if mark == "+" or mark == "*" :
             proc = rule.name
       self.putLn (target + " = self.copy_" + proc + " (" + field + ")")

   def copyFromExpression (self, grammar, rule, expr) :
       cnt = len (expr.alternatives)
       inx = 0
       for alt in expr.alternatives :
           if cnt > 1 or expr.continue_expr :
              cond = self.conditionFromAlternative (grammar, alt)
              if self.conditionIsUnknown (cond) :
                 if inx < len (expr.alternatives) - 1 :
                    grammar.error ("Cannot find condition (rule: " + self.last_rule.name+ ")")
                 else :
                    self.putLn ("else :")
              else :
                 if inx == 0 :
                    self.putLn ("if " + cond + " :")
                 else :
                    self.putLn ("elif " + cond + " :")
              self.incIndent ()
           self.copyFromAlternative (grammar, rule, alt)
           if cnt > 1  or expr.continue_expr :
              self.decIndent ()
           inx = inx + 1
       if expr.continue_expr :
          self.putLn ("else :")
          self.incIndent ()
          self.copyChooseItem (grammar, rule, expr.expr_link, "result", "param", False)
          self.decIndent ()
       if expr.continue_expr :
          self.executeMethod (grammar, grammar.execute_on_choose, rule.name)

   def copyFromAlternative (self, grammar, rule, alt) :
       grammar.updatePosition (alt)
       any = False
       for item in alt.items :
           if isinstance (item, Terminal) :
              if self.copyFromTerminal (grammar, item) :
                 any = True
           elif isinstance (item, Nonterminal) :
              if item.continue_item :
                 if item.rule_ref.store_name != "" :
                    self.copyChooseItem (grammar, rule, alt.continue_link, "store", "param." + item.rule_ref.store_name, True)
              choose = item.select_item and item.item_link.select_ebnf != None
              if not choose :
                 self.copyFromNonterminal (grammar, item)
                 any = True
           elif isinstance (item, Ebnf) :
              self.copyFromEbnf (grammar, rule, item)
              any = True
           elif isinstance (item, New) :
              self.putLn ("result = " + item.new_type + " ()")
              self.putLn ("self.copyLocation (result)")
              if grammar.show_tree :
                 self.putLn ("if self.monitor : self.monitor.openObject (result)")
              self.copyChooseItem (grammar, rule,  alt.continue_link, "result." + item.store_name , "param." + item.store_name, True)
              any = True
           elif isinstance (item, Assign) :
              prefix = ""
              if item.value != "True" and item.value != "False" :
                 prefix = "result."
              self.putLn ("result." + item.variable + " = " + prefix + item.value)
              any = True
           # elif isinstance (item, Execute) :
           #    self.putLn ("self." + item.name + " (result)")
           #    any = True
       if not any :
          self.putLn ("pass")

   def copyFromEbnf (self, grammar, rule, ebnf) :
       grammar.updatePosition (ebnf)
       block = False
       if not ebnf.expr.continue_expr :
          cond = self.conditionFromExpression (grammar, ebnf.expr)
          if ebnf.mark == '?' :
             self.putLn ("if " + cond + " :")
             block = True
          if ebnf.mark == '*' or ebnf.mark == '+' :
             loop = self.conditionIsLoop (grammar, ebnf.expr)
             if loop :
                self.putLn ("while " + cond + " :")
             else :
                self.putLn ("if " + cond + " :")
             block = True

       if block :
          self.incIndent ()

       self.copyFromExpression (grammar, rule, ebnf.expr)

       if block :
          self.decIndent ()

   def copyFromNonterminal (self, grammar, item, field = "") :
       grammar.updatePosition (item)

       if item.add :
          self.put ("result.items.append (")
       if item.select_item or item.continue_item or item.return_item :
          self.put ("result = ")
       if item.variable != ""  :
          self.put ("result." + item.variable + " = ")

       if self.isArit (grammar, item.rule_name) :
          proc = "expression"
       else :
          proc = item.rule_name

       self.put ("self.copy_" + proc)
       self.put (" (")
       if field != "" :
          self.put ("param." + field)
       elif item.variable :
          self.put ("param." + item.variable)
       elif item.add :
          self.put ("param.items [inx]")
          self.put (")")
       elif item.modify or item.select_item or item.continue_item or item.return_item :
          self.put ("param")
       if item.continue_item :
          self.put (", store")
       self.putLn (")")

       if item.add :
          self.putLn ("inx = inx + 1")

   def copyFromTerminal (self, grammar, item) :
       any = False
       symbol = item.symbol_ref
       if symbol.multiterminal :
          if item.variable != "" :
             self.putLn ("result." + item.variable + " = " + "param." + item.variable)
             any = True
       return any

# --------------------------------------------------------------------------

   def isArit (self, grammar, rule_name) :
       if not self.enable_arit:
          return False
       rule = grammar.rule_dict [rule_name]
       if rule.rule_type == "" :
          return False
       else :
          type = grammar.struct_dict [rule.rule_type]
          while type != None and type.name != grammar.expression_type_name :
             type = type.super_type
          return type != None # derived from expression type

   def copyFromArit (self, grammar) :
       any = False
       for rule in grammar.rules :
          grammar.charLineNum = rule.src_line # !?
          grammar.charColNum = rule.src_column
          if rule.rule_mode != "" :
             if self.isArit (grammar, rule.name) : # derived from CmmExpr
                if not any :
                   self.putLn ("def copy_expression (self, param) :")
                   self.incIndent ()
                any = True
                if rule.rule_mode == "new" :
                    if rule.tag_name != "" :
                       self.putLn ("if param." + rule.tag_name + " == param." + rule.tag_value + ":")
                    else :
                       self.putLn ("if isinstance (param, " + rule.rule_type + ") :")
                    self.incIndent ()
                    if rule.add_used :
                       self.putLn ("inx = 0")
                       self.putLn ("cnt = len (param.items)")
                    if rule.store_name != "" :
                         self.putLn ("self.copy_expression (param." + rule.store_name + ")")
                    self.copyFromExpression (grammar, rule, rule.expr)
                    self.decIndent ()
                elif rule.rule_mode == "select" :
                   for alt1 in rule.expr.alternatives :
                      for item1 in alt1.items :
                          if isinstance (item1, Ebnf) :
                             expr1 = item1.expr
                             if expr1.continue_expr :
                                for alt2 in expr1.alternatives :
                                    cnt2 = len (alt2.items)
                                    if cnt2 == 4 or cnt2 == 5 :
                                       if isinstance (alt2.items [cnt2-2], Execute) :
                                          cnt2 = cnt2 - 1
                                    if cnt2 == 1 :
                                       pass
                                    elif cnt2 == 3 :
                                       a = alt2.items [0]
                                       b = alt2.items [1]
                                       c = alt2.items [2]
                                       if isinstance (a, New) and isinstance (b, Ebnf) and isinstance (c, Nonterminal) and c.variable != "" :
                                          for alt3 in b.expr.alternatives :
                                              cond = self.conditionFromAlternative (grammar, alt3)
                                              self.putLn ("if " + cond + " :")
                                              self.incIndent ()
                                              self.putLn ("self.copy_expression (param." + a.store_name + ")")
                                              self.copyFromAlternative (grammar, rule, alt3)
                                              self.putLn ("self.copy_expression (param." + c.variable + ")")
                                              self.decIndent ()
                                       else :
                                          self.putLn ("# unknown rule " + rule.name)
                                    elif cnt2 == 4 :
                                       a = alt2.items [0]
                                       b = alt2.items [1]
                                       c = alt2.items [2]
                                       d = alt2.items [3]
                                       if isinstance (a, New) and isinstance (b, Terminal) and isinstance (c, Assign) and isinstance (d, Nonterminal) and d.variable != "":
                                          cond = self.conditionFromAlternative (grammar, alt2)
                                          self.putLn ("if param." + c.variable + " == param." + c.value + " :")
                                          self.incIndent ()
                                          self.putLn ("self.copy_expression (param." + a.store_name + ")")
                                          # self.copyFromTerminal (grammar, b)
                                          self.putLn ("self.copy_expression (param." + d.variable + ")")
                                          self.decIndent ()
                                       else :
                                          self.putLn ("# unknown rule" + rule.name)
                                    else :
                                       self.putLn ("# unknown rule " + rule.name)
       if any :
          self.decIndent ()
       self.putLn ("")

# --------------------------------------------------------------------------

   def copyFromGrammar (self, grammar, parser_module = "") :

       self.putLn ()
       if parser_module != "" :
          self.putLn ("from " + parser_module + " import *")
       self.putLn ("from output import Output")
       self.putLn ()

       self.putLn ("class Copy (Output) :")
       self.putLn ("")
       self.incIndent ()

       self.copyFromRules (grammar)
       self.copyFromArit (grammar)

       self.decIndent ()

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
