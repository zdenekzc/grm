
# toparser.py

from __future__ import print_function

if __name__ == "__main__" :
   import os, sys
   work_dir = os.path.abspath (sys.path [0])
   module_dir = os.path.join (work_dir, "..", "code")
   sys.path.insert (1, module_dir)

from grammar import Grammar, Rule, Expression, Alternative, Ebnf, Nonterminal, Terminal, Assign, Execute, New, Style
from code_output import CodeOutput
from symbols import Symbol, initSymbols
from input import quoteString
# from util import get_time

# --------------------------------------------------------------------------

class ToParser (CodeOutput) :

   use_strings = False # use symbol text (in parsing)
   use_numbers = True # use integers (during set allocation)

   def addToDictionary (self, tree, name) :
       ref = tree
       for c in name :
           if c not in ref :
               ref[c] = { }
           ref = ref[c]

   def printKeywordItem (self, dictionary, inx, name) :
       self.incIndent ()
       if len (dictionary) == 0 :
          self.putLn ("self.token = " + "self.keyword_" + name )
       else :
          self.printKeywordDictionary (dictionary, inx+1, name)
       self.decIndent ()

   def printKeywordDictionary (self, dictionary, inx, name) :
       if len (dictionary) == 1 :
          start_inx = inx
          substr = ""
          while len (dictionary) == 1:
             for c in sorted (dictionary.keys ()) : # only one
                 substr = substr + c
                 dictionary = dictionary [c]
                 inx = inx + 1
                 name = name + c
          inx = inx - 1
          if start_inx == inx :
             self.putLn ("if s[" + str (inx) + "] == " + "'" + substr + "'" + " :")
          else :
             self.putLn ("if s[" + str (start_inx) + ":" + str (inx+1) + "] == " + '"' + substr + '"' + " :")
          self.printKeywordItem (dictionary, inx, name)
       else :
           first_item = True
           for c in sorted (dictionary.keys ()) :
               if first_item :
                  cmd = "if"
                  first_item = False
               else :
                  cmd = "elif"
               self.putLn (cmd + " s[" + str (inx) + "] == "  "'" + c + "'" + " :")
               self.printKeywordItem (dictionary[c], inx, name+c)

   def selectKeywords (self, grammar) :
       self.putLn ("def lookupKeyword (self) :")
       self.incIndent ()
       self.putLn ("s = self.tokenText")
       self.putLn ("n = len (s)")

       lim = 0
       for name in grammar.keyword_dict :
           n = len (name)
           if n > lim :
              lim = n

       size = 1
       first_item = True
       while size <= lim :
          tree = { }
          for name in grammar.keyword_dict :
              if len (name) == size :
                 self.addToDictionary (tree, name)
          if len (tree) != 0 :
             if first_item :
                cmd = "if"
                first_item = False
             else :
                cmd = "elif"
             self.putLn (cmd + " n == " + str (size) + " :")
             self.incIndent ()
             self.printKeywordDictionary (tree, 0, "")
             self.decIndent ()
          size = size + 1

       self.decIndent ()
       self.putLn ()

# --------------------------------------------------------------------------

   def printDictionary (self, dictionary) :
       for c in sorted (dictionary.keys ()) :
           self.putLn ("'" + c + "'" + " :")
           self.incIndent ()
           if len (dictionary[c]) == 0 :
              self.putLn ("#")
           else :
              printDictionary (dictionary[c])
           self.decIndent ()

# --------------------------------------------------------------------------

   def printStart (self, grammar) :
       for rule in grammar.rules :
           if rule.start_set != None :
              self.put ("# " + rule.name + " starts with:")
              for inx in range (grammar.rule_cnt) :
                 if rule.start_set & 1 << inx :
                    r = grammar.rules [inx]
                    self.put (" " + r.name)
              self.putEol ()
       self.style_empty_line ()

   def printSelect (self, grammar) :
       for rule in grammar.rules :
           if rule.rule_mode == "select" :
              self.putLn ("# " + rule.name + " :")
              for sel_alt in rule.expr.alternatives :
                  self.putLn ("#    " + sel_alt.select_nonterm.rule_name)
                  for cnt_alt in sel_alt.select_branches :
                      if cnt_alt.continue_nonterm != None :
                         self.putLn ("#       " + cnt_alt.continue_nonterm.rule_name)
                      if cnt_alt.continue_new != None :
                         self.putLn ("#       " + cnt_alt.continue_new.new_type)
                      if cnt_alt.continue_assign != None :
                         self.putLn ("#       " + cnt_alt.continue_assign.value)
                      for spec_alt in cnt_alt.continue_branches :
                          if spec_alt.specific_assign != None :
                             self.putLn ("#          " + spec_alt.specific_assign.value)
       self.style_empty_line ()

   def displayTags (self, subtypes, type, level) :
       self.put ("# ")
       self.put ((level-1)*3*" ")
       self.put (type.type_name + " : " + type.tag_defined)
       if type.tag_value != "" :
          self.put (" " + type.tag_name + "=" + type.tag_value)
       self.putLn ()
       for s in type.specific_tags :
          self.putLn ("# " + 3*level*" " + "specific : " + s)
       for t in subtypes [type] :
           self.displayTags (subtypes, t, level+1)

   def printTags (self, grammar) :
       subtypes = { }
       for type in grammar.struct_list :
           subtypes [type] = [ ]
       for type in grammar.struct_list :
           if type.super_type != None :
              subtypes [type.super_type].append (type)
       for type in grammar.struct_list :
           if type.super_type == None :
              self.displayTags (subtypes, type, 1)
       self.style_empty_line ()

# --------------------------------------------------------------------------

   def selectBranch (self, grammar, dictionary, level, prefix) :
       for c in sorted (dictionary.keys ()) :
           if level == 1 :
              self.putLn ("if self.tokenText == " + "'" + c + "'" + " :")
           else :
              self.putLn ("if self.ch == " + "'" + c + "'" + " :")
           self.incIndent ()
           name = prefix + c
           if name in grammar.separator_dict :
              self.putLn ("self.token = " + str ( grammar.separator_dict[name].inx)) # !?
           if level > 1 :
              self.putLn ("self.tokenText = self.tokenText + self.ch")
              self.putLn ("self.nextChar ()")
           if len (dictionary[c]) != 0 :
              self.selectBranch (grammar, dictionary[c], level+1, prefix+c)
           self.decIndent ()

   def selectSeparators (self, grammar) :
       self.putLn ("def processSeparator (self) :")
       self.incIndent ()

       tree = { }
       for name in grammar.separator_dict :
           self.addToDictionary (tree, name)

       self.selectBranch (grammar, tree, 1, "")

       self.putLn ("if self.token == self.separator :")
       self.incIndent ()
       self.putLn ("self.error (" + '"' + "Unknown separator" + '"' + ")")
       self.decIndent ()

       self.decIndent ()
       self.putLn ()

   # -----------------------------------------------------------------------

   def executeMethod (self, grammar, func_dict, rule_name, no_param = False) :
       if rule_name in func_dict :
          method_name = func_dict [rule_name]
          if no_param :
             self.putLn ("self." + method_name + " ()")
          else :
             self.putLn ("self." + method_name + " (result)")

   def declareEnums (self, grammar) :
       for type in grammar.struct_list :
          for enum_name in type.enums :
              enum = type.enums [enum_name]
              self.putLn ("# " + enum.enum_name + " in " + type.type_name)
              inx = 0
              for value in enum.values :
                  self.putLn (value + " = " + str (inx))
                  inx = inx + 1
              self.putLn ()

   def declareTypes (self, grammar) :
       for type in grammar.struct_list :
          self.put ("class " + type.type_name + " (")
          if type.super_type != None :
             self.put (type.super_type.type_name)
          else :
             self.put ("object")
          self.putLn (") :")
          self.incIndent ()

          all_fields = [ ]
          t = type
          while t != None :
             all_fields = t.field_list + all_fields
             t = t.super_type

          self.put ("_fields_ = [")
          first = True
          for field in all_fields :
              if not field.hidden :
                 if not field.is_bool and not field.is_enum and not field.is_int and not field.is_str :
                    "only fields visible in tree"
                    if not first :
                       self.put (", ")
                    self.put ('"' + field.field_name + '"')
                    first = False
          self.putLn ("]")

          # if type.tag_low != "" :
          #    self.putLn ("_tag_low_ = " + type.tag_low)
          # if type.tag_high != "" :
          #    self.putLn ("_tag_high_ = " + type.tag_high)

          if type.tag_low != "" and type.tag_high != "" :
             if type.tag_high != type.tag_value :
                self.putLn ("_tag_low_ = " + type.tag_low)
                self.putLn ("_tag_high_ = " + type.tag_high)

          self.putLn ("def __init__ (self) :")
          self.incIndent ()
          any = False

          if type.super_type != None :
             self.putLn ("super (" + type.type_name + ", self).__init__ ()")
             # self.putLn (type.super_type.type_name + ".__init__ (self)")
             any = True

          for field in type.field_list :
             any = True
             if field.field_name != type.tag_name :
                self.put ("self." + field.field_name + " = ")
                if field.is_bool :
                   self.put ("False")
                elif field.is_enum :
                   self.put ("0")
                elif field.is_int :
                   self.put ("0")
                elif field.is_str :
                   self.put ('"' + '"')
                elif field.is_list :
                   self.put ("[ ]")
                else :
                   self.put ("None")
                self.putEol ()

          if type.tag_name != "" :
             # self.putLn ("self." + type.tag_name + " = self." + type.tag_value)
             self.putLn ("self." + type.tag_name + " = " + type.tag_value)
             any = True

          if not any :
             self.putLn ("pass")
          self.decIndent ()

          self.decIndent ()
          self.putLn ()
          # self.putLn ("# end of " + type.type_name)

       for t in grammar.typedef_list :
          self.putLn (t.new_name + " = " + t.old_name)
       self.style_empty_line ()

   # -----------------------------------------------------------------------

   def declareTerminals (self, grammar) :
       for symbol in grammar.symbols :
           if symbol.keyword :
              self.putLn ("self." + symbol.ident + " = " + str (symbol.inx))
           elif symbol.separator :
              if symbol.ident != "" :
                 self.putLn ("self." + symbol.ident + " = " + str (symbol.inx) + " # " + symbol.text)
              else :
                 self.putLn ("# " + symbol.text + " " + str (symbol.inx))
           else :
              self.putLn ("# " + symbol.ident + " = " + str (symbol.inx))

   def convertTerminals (self, grammar) :
       self.putLn ("def tokenToString (self, value) :")
       self.incIndent ()

       for symbol in grammar.symbols :
           self.putLn ("if value == " + str (symbol.inx) + ": " + "return " + '"' + symbol.alias + '"')

       self.putLn ("return " + '"' + "<unknown symbol>" + '"')
       self.decIndent ()
       self.putLn ()

   # --------------------------------------------------------------------------

   def declareStoreLocation (self, grammar) :
       self.putLn ("def storeLocation (self, item) :")
       self.incIndent ()
       self.putLn ("item.src_file = self.tokenFileInx") # !?
       self.putLn ("item.src_line = self.tokenLineNum")
       self.putLn ("item.src_column = self.tokenColNum")
       self.putLn ("item.src_pos = self.tokenByteOfs")
       self.putLn ("item.src_end = self.charByteOfs")
       # self.putLn ("item.src_step = self.tokenStepNum")
       self.decIndent ()
       self.putLn ()

   def declareAlloc (self, grammar) :
       self.putLn ("def alloc (self, items) :")
       self.incIndent ()
       self.putLn ("result = 0")
       self.putLn ("for inx in items :")
       self.incIndent ()
       self.putLn ("result |= 1 << inx")
       self.decIndent ()
       self.putLn ("return result")
       self.decIndent ()
       self.putLn ()

   def declareCollections (self, grammar) :
       num = 0
       for data in grammar.collections :

           self.put ("self.set_" + str (num) + " = self.alloc (" )

           self.put ("[")
           any = False
           for inx in range (grammar.symbol_cnt) :
               if data & 1 << inx :
                  if any :
                     self.put (", ")
                  any = True
                  symbol = grammar.symbols [inx]
                  if symbol.ident != "" and not self.use_numbers :
                     self.put ("self." + symbol.ident)
                  else :
                     self.put (str (inx))
           self.put ("]")

           self.put ( ") #" )

           for inx in range (grammar.symbol_cnt) :
               if data & 1 << inx :
                  self.put (" ")
                  symbol = grammar.symbols [inx]
                  if symbol.text != "" :
                     self.put (" " +symbol.text)
                  else :
                     self.put (" " +symbol.ident)

           self.putEol ()
           num = num + 1

   def findCollection (self, grammar, collection) :
       "collection is set of (at least four) symbols"
       if collection not in grammar.collections :
          error ("Unknown (not registered) collections")
       return grammar.collections.index (collection)

   def condition (self, grammar, collection, predicate = None, semantic_predicate = None, test = False) :
       cnt = 0
       for inx in range (grammar.symbol_cnt) :
           if collection & 1 << inx :
              cnt = cnt + 1

       complex = False
       if cnt == 0 :
          # grammar.error ("Empty set")
          # return "nothing"
          code = "" # !?
       elif cnt <= 3 :
          if cnt > 1 :
             complex = True
          code = ""
          start = True
          for inx in range (grammar.symbol_cnt) :
              if collection & 1 << inx :
                 if not start :
                    code = code + " or "
                 start = False
                 symbol = grammar.symbols[inx]
                 if symbol.ident != "" and not (self.use_strings and symbol.text != "") :
                    code = code + "self.token == self." + symbol.ident
                 elif symbol.text != "" :
                    code = code + "self.tokenText == " + '"' + symbol.text + '"'
                 else :
                    code = code + "self.token == " + str (symbol.inx)
       else :
          num = self.findCollection (grammar, collection)
          code = "self.set_" + str (num) + " & 1 << self.token";

       if predicate != None :
          if not self.simpleExpression (predicate) :
             if cnt == 0 :
                code =  ""
             elif complex :
                code = "(" + code + ")" + " and "
                complex = False
             else :
                code = code + " and "
             inx = self.findPredicateExpression (grammar, predicate)
             code = code + "self.test_" + str (inx) + " ()"

       if semantic_predicate != None and not test:
          if code == "True" :
             code = ""
          if code != "" :
             if complex :
                code = "(" + code + ")"
             code = code + " and "
          code = code + "self." + semantic_predicate
          method = grammar.method_dict [semantic_predicate]
          if method.param_type == "" :
             code = code + " ()"
          else :
             code = code + " (result)"

       return code

   def conditionFromAlternative (self, grammar, alt, test = False) :
       code = ""
       if not (alt.nullable and alt.semantic_predicate == None) :
          done = False
          if alt.continue_alt :
             # semantic predicates inside choose
             for item in alt.items :
                 if not done and isinstance (item, Ebnf) :
                    ebnf = item
                    code = self.conditionFromExpression (grammar, ebnf.expr, test)
                    done = True
          if not done :
             code = self.condition (grammar, alt.first, alt.predicate, alt.semantic_predicate, test)
       if code == "" : # !?
          code = "True"
       return code

   def conditionFromExpression (self, grammar, expr, test = False) :
       code = ""
       for alt in expr.alternatives :
           if code != "" :
              code = code + " or "
           code = code + self.conditionFromAlternative (grammar, alt, test)
       return code

   """
   def conditionFromRule (self, grammar, name) :
       if name not in grammar.rule_dict :
          grammar.error ("Unknown rule: " + name)
       rule = grammar.rule_dict [name]
       return self.condition (grammar, rule.first)
   """

   # -----------------------------------------------------------------------

   def findPredicateExpression (self, grammar, expr) :
       if expr not in grammar.predicates :
          grammar.error ("Unknown (not registered) predicate")
       return grammar.predicates.index (expr) + 1

   """
   def registerPredicateNonterminal (self, grammar, item) :
       rule = item.rule_ref
       if rule not in grammar.test_dict :
          grammar.test_dict [rule] = True
          grammar.test_list.append (rule)
   """

   def declarePredicates (self, grammar) :
       inx = 1
       for expr in grammar.predicates :
          self.putLn ("def test_" + str (inx) + " (self) :")
          self.incIndent ()
          self.putLn ("result = True")
          self.putLn ("position = self.mark ()")
          self.checkFromExpression (grammar, expr)
          self.putLn ("self.rewind (position)")
          self.putLn ("return result")
          self.decIndent()
          self.putLn ()
          inx = inx + 1

       inx = 0
       while inx < len (grammar.test_list) :
          rule = grammar.test_list [inx]
          self.testFromRule (grammar, rule)
          inx = inx + 1

   # -----------------------------------------------------------------------

   def checkFromExpression (self, grammar, expr, reduced = False) :
       cnt = len (expr.alternatives)
       start = True
       stop = False
       for alt in expr.alternatives :
           if cnt > 1 :
              if stop :
                 gram.warning ("Cannot construct alternative condition")
              cond = self.conditionFromAlternative (grammar, alt, test = True)
              if cond == "True" or cond == "":
                 stop = True
              if start :
                 self.putLn ("if " + cond + " :")
              elif stop:
                 self.putLn ("else :")
              else :
                 self.putLn ("elif " + cond + " :")
              start = False
              self.incIndent ()
           self.checkFromAlternative (grammar, alt, cnt > 1 or reduced)
           if cnt > 1 :
              self.decIndent ()
       if cnt > 1 and not stop :
          self.putLn ("else :")
          self.incIndent ()
          self.putLn ("result = False")
          self.decIndent ()

   def checkFromAlternative (self, grammar, alt, reduced) :
       any = False
       inx = 1
       for item in alt.items :
           if isinstance (item, Terminal) :
              self.checkFromTerminal (grammar, item, inx == 1 and reduced)
              any = True
           elif isinstance (item, Nonterminal) :
              self.checkFromNonterminal (grammar, item)
              any = True
           elif isinstance (item, Ebnf) :
              self.checkFromEbnf (grammar, item)
              any = True
           inx = inx + 1
       if not any :
          self.putLn ("pass")

   def checkFromEbnf (self, grammar, ebnf) :
       if ebnf.mark == '?' :
          self.put ("if ")
       elif ebnf.mark == '*' :
          self.put ("while ")
       elif ebnf.mark == '+' :
          self.put ("while ")

       if ebnf.mark != "" :
          self.put ("result and (")
          cond = self.conditionFromExpression (grammar, ebnf.expr, test = True)
          self.put (cond)
          self.putLn (") :")
          self.incIndent ()

       self.checkFromExpression (grammar, ebnf.expr, ebnf.mark != "")

       if ebnf.mark != "" :
          self.decIndent ()

   def checkFromNonterminal (self, grammar, item) :
       # self.registerPredicateNonterminal (grammar, item)
       self.putLn ("if result :")
       self.incIndent ()
       self.putLn ("if not self.test_" + item.rule_name + " () :")
       self.incIndent ()
       self.putLn ("result = False")
       self.decIndent ()
       self.decIndent ()

   def checkFromTerminal (self, grammar, item, reduced) :
       if not reduced :
          symbol = item.symbol_ref
          self.put ("if result and ")
          if symbol.ident != "" and (symbol.multiterminal or not self.use_strings or symbol.text == "") :
             self.put ("self.token != self." + symbol.ident)
          elif symbol.text != "":
             self.put ("self.tokenText != " + '"' + symbol.text + '"')
          else :
             self.put ("self.check (" + str (symbol.inx) + ")")
          self.putLn (" :")
          self.incIndent ()
          self.putLn ("result = False")
          self.decIndent ()

       self.putLn ("if result :")
       self.incIndent ()
       self.putLn ("self.nextToken ()")
       self.decIndent ()

   # -----------------------------------------------------------------------

   def testFromRule (self, grammar, rule) :
       self.putLn ("def test_" + rule.name + " (self) :")
       self.incIndent ()
       self.testFromExpression (grammar, rule.expr)
       self.putLn ("return True")
       self.decIndent ()
       self.putEol ()

   def testFromExpression (self, grammar, expr, reduced = False) :
       cnt = len (expr.alternatives)
       start = True
       for alt in expr.alternatives :
           if cnt > 1 :
              cond = self.conditionFromAlternative (grammar, alt, test = True)
              if start :
                 self.put ("if")
              else :
                 self.put ("elif")
              start = False
              self.putLn (" " + cond + " :")
              self.incIndent ()
           self.testFromAlternative (grammar, alt, cnt > 1 or reduced)
           if cnt > 1 :
              self.decIndent ()
       if cnt > 1 :
          self.putLn ("else :")
          self.incIndent ()
          self.putLn ("return False")
          self.decIndent ()

   def testFromAlternative (self, grammar, alt, reduced) :
       any = False
       inx = 1
       for item in alt.items :
           if isinstance (item, Terminal) :
              self.testFromTerminal (grammar, item, inx == 1 and reduced)
              any = True
           elif isinstance (item, Nonterminal) :
              self.testFromNonterminal (grammar, item)
              any = True
           elif isinstance (item, Ebnf) :
              self.testFromEbnf (grammar, item)
              any = True
           inx = inx + 1
       if not any :
          self.putLn ("pass")

   def testFromEbnf (self, grammar, ebnf) :
       if ebnf.mark == '?' :
          self.put ("if ")
       elif ebnf.mark == '*' :
          self.put ("while ")
       elif ebnf.mark == '+' :
          self.put ("while ")

       if ebnf.mark != "" :
          cond = self.conditionFromExpression (grammar, ebnf.expr, test = True)
          self.put (cond)
          self.putLn (" :")
          self.incIndent ()

       self.testFromExpression (grammar, ebnf.expr, ebnf.mark != "")

       if ebnf.mark != "" :
          self.decIndent ()

   def testFromNonterminal (self, grammar, item) :
       # self.registerPredicateNonterminal (grammar, item)
       self.putLn ("if not self.test_" + item.rule_name + " () :")
       self.incIndent ()
       self.putLn ("return False")
       self.decIndent ()

   def testFromTerminal (self, grammar, item, reduced) :
       if not reduced :
          symbol = item.symbol_ref
          self.put ("if ")
          if symbol.ident != "" and (symbol.multiterminal or not self.use_strings or symbol.text == "") :
             self.put ("self.token != self." + symbol.ident)
          elif symbol.text != "":
             self.put ("self.tokenText != " + '"' + symbol.text + '"')
          else :
             self.put ("self.check (" + str (symbol.inx) + ")")
          self.putLn (" :")
          self.incIndent ()
          self.putLn ("return False")
          self.decIndent ()

       self.putLn ("self.nextToken ()")

   # -----------------------------------------------------------------------

   def simpleExpression (self, expr) :
       simple = len (expr.alternatives) != 0
       for alt in expr.alternatives :
           if not self.simpleAlternative (alt) :
              simple = False
       return simple

   def simpleAlternative (self, alt) :
       simple = False
       if len (alt.items) == 1 :
          item = alt.items [0]
          if isinstance (item, Terminal) :
             simple = True
       return simple

   # def simpleEbnf (self, ebnf) :
   #     return self.simpleExpression (ebnf.expr)

   # -----------------------------------------------------------------------

   def parserFromRules (self, grammar) :
       for rule in grammar.rules :
           self.openSection (rule)
           self.parserFromRule (grammar, rule)
           self.closeSection ()

   def parserFromRule (self, grammar, rule) :
       grammar.updatePosition (rule)

       params = ""
       if rule.rule_mode == "modify" :
          params = "result"
       if rule.store_name != "" :
          if params != "" :
             params = params + ", "
          params = params + "store"
       if params != "" :
          params = ", " + params # comma after self

       self.putLn ("def parse_" + rule.name + " (self" + params + ") :")

       self.incIndent ()

       if rule.rule_mode == "modify" :
          if grammar.show_tree :
             self.putLn ("if self.monitor : self.monitor.reopenObject (result)")

       if rule.rule_mode == "new" :
          self.putLn ("result = " + rule.rule_type + " ()")
          if rule.tag_name != "" :
             # self.putLn ("result." + rule.tag_name + " = result." + rule.tag_value)
             type = grammar.struct_dict [rule.rule_type]
             if rule.tag_name != type.tag_name or rule.tag_value != type.tag_value :
                grammar.error ("Internal tag mismatch")

          self.putLn ("self.storeLocation (result)")
          if grammar.show_tree :
             self.putLn ("if self.monitor : self.monitor.openObject (result)")

       if rule.store_name != "" :
          self.putLn ("result." + rule.store_name + " = store")

       self.executeMethod (grammar, grammar.execute_on_begin, rule.name)
       self.executeMethod (grammar, grammar.execute_on_begin_no_param, rule.name, no_param = True)

       self.parserFromExpression (grammar, rule, rule.expr)

       self.executeMethod (grammar, grammar.execute_on_end, rule.name)

       if rule.rule_mode == "new" or rule.rule_mode == "modify" :
          if grammar.show_tree :
             self.putLn ("if self.monitor : self.monitor.closeObject ()")

       self.putLn ("return result")
       self.decIndent ()
       self.putEol ()

   def parserFromExpression (self, grammar, rule, expr) :
       reordered = [ ]
       reordered_end = [ ]
       for alt in expr.alternatives :
           if alt.nullable :
              reordered_end.append (alt)
           else :
              reordered.append (alt)
       reordered += reordered_end

       cnt = len (reordered)
       start = True
       stop = False
       for alt in reordered :
           if cnt > 1 :
              if stop :
                 grammar.warning ("Cannot construct alternative condition")
              cond = self.conditionFromAlternative (grammar, alt)
              if cond == "True" or cond == "":
                 stop = True
              if start :
                 self.putLn ("if " + cond + " :")
              elif stop:
                 self.putLn ("else :")
              else :
                 self.putLn ("elif " + cond + " :")
              start = False
              self.incIndent ()
           self.parserFromAlternative (grammar, rule, alt)
           if cnt > 1 :
              self.decIndent ()
       if cnt > 1 and not stop :
          self.putLn ("else :")
          self.incIndent ()
          self.putLn ("self.error (" +  '"' + "Unexpected token" + '"' + ")")
          self.decIndent ()
       if expr.continue_expr :
          self.executeMethod (grammar, grammar.execute_on_choose, rule.name)

   def parserFromAlternative (self, grammar, rule, alt) :
       opened_branch = False
       opened_if = False
       for item in alt.items :
           if isinstance (item, Terminal) :
              self.parserFromTerminal (grammar, rule, item)
           elif isinstance (item, Nonterminal) :
              self.parserFromNonterminal (grammar, rule, item)
           elif isinstance (item, Ebnf) :
              if alt.select_alt :
                 if rule.name in grammar.predicate_on_choose :
                    func_name = grammar.predicate_on_choose [rule.name]
                    self.putLn ("if self." + func_name + " (result) :")
                    self.incIndent ()
                    opened_if = True
              self.parserFromEbnf (grammar, rule, item)
           elif isinstance (item, Assign) :
              prefix = ""
              # if item.value != "True" and item.value != "False" :
              #    prefix = "result."
              self.putLn ("result." + item.variable + " = " + prefix + item.value)
           elif isinstance (item, Execute) :
              if item.no_param :
                 self.putLn ("self." + item.name + " ()")
              else :
                 self.putLn ("self." + item.name + " (result)")
           elif isinstance (item, New) :
              self.putLn ("store = result")
              self.putLn ("result = " + item.new_type + " ()")
              self.putLn ("self.storeLocation (result)")
              self.putLn ("result."  + item.store_name + " = store")
              if grammar.show_tree :
                 self.putLn ("if self.monitor : self.monitor.openObject (result)")
                 opened_branch = True
           elif isinstance (item, Style) :
              pass
           else :
              grammar.error ("Unknown alternative item: " + item.__class__.__name__)
       if opened_branch :
          self.putLn ("if self.monitor : self.monitor.closeObject ()")
       if opened_if :
           self.decIndent ()

   def parserFromEbnf (self, grammar, rule, ebnf) :
       if ebnf.mark == '?' :
          self.put ("if ")
       elif ebnf.mark == '*' :
          self.put ("while ")
       elif ebnf.mark == '+' :
          self.put ("while ")

       if ebnf.mark != "" :
          cond = self.conditionFromExpression (grammar, ebnf.expr)
          self.put (cond)
          self.putLn (" :")
          self.incIndent ()

       self.parserFromExpression (grammar, rule, ebnf.expr)

       if ebnf.mark != "" :
          self.decIndent ()

   def parserFromNonterminal (self, grammar, rule, item) :
       if item.variable == "" :
          if item.rule_ref.rule_mode == "modify" :
             item.modify = True;

       if item.select_item :
          self.executeMethod (grammar, grammar.execute_on_entry_no_param, rule.name, no_param = True)

       if item.add :
          self.put ("result.items.append (")
       if item.select_item or item.continue_item or item.return_item:
          self.put ("result = ")
       if item.variable != "" :
          self.put ("result." + item.variable + " = ")

       self.put ("self.parse_" + item.rule_name)

       params = ""
       if item.modify or item.rule_ref.rule_mode == "modify" :
          params = "result"
       if item.rule_ref.store_name != "" :
          params = "result"

       self.put (" (")
       if params != "" :
          self.put (params)
       self.put (")")

       if item.add :
          self.put (")") # close append parameters
       self.putEol ()

       if item.select_item :
          self.executeMethod (grammar, grammar.execute_on_fork_no_param, rule.name, no_param = True)

   def parserFromTerminal (self, grammar, rule, item) :
       symbol = item.symbol_ref
       if symbol.multiterminal :
          if item.variable != "" :
             self.put ("result." + item.variable + " = ")

          func = symbol.ident
          if func.endswith ("_number") :
             func = func [ : -7 ]
          if func.endswith ("_literal") :
             func = func [ : -8 ]
          func = "read" + func.capitalize()

          self.putLn ("self." + func + " ()")
       else :
          if symbol.ident != "" and not (self.use_strings and symbol.text != "") :
             self.putLn ("self.checkToken (self." + symbol.ident + ")")
          elif symbol.text != "":
             self.putLn ("self.check (" + '"' + symbol.text + '"' + ")")
          else :
             self.putLn ("self.check (" + str (symbol.inx) + ")")

   # -----------------------------------------------------------------------

   def note (self, txt) :
       # txt == "" ... init timer
       if 0 :
          start_time = getattr (self, "start_time", 0)
          stop_time = get_time ()
          if start_time == 0 :
             start_time = stop_time # first time measurement
          if txt != "" :
             print (txt + ", time %0.4f s" % (stop_time - start_time))
          self.start_time = stop_time

   # -----------------------------------------------------------------------

   def parserFromGrammar (self, grammar, class_name = "Parser") :
       self.note ("")
       grammar.parseRules ()
       self.note ("grammar parsed")

       initSymbols (grammar)

       self.putLn ()
       self.putLn ("from lexer import Lexer")
       self.putLn ()

       self.putLn ("class " + class_name + " (Lexer) :")
       self.incIndent ()

       self.parserFromRules (grammar)
       # self.note ("parser methods generated")

       self.declarePredicates (grammar)
       # self.note ("test methods generated")

       self.selectKeywords (grammar)
       self.selectSeparators (grammar)
       self.convertTerminals (grammar)
       self.declareStoreLocation (grammar)
       self.declareAlloc (grammar)

       self.putLn ("def __init__ (self) :")
       self.incIndent ()
       self.putLn ("super (" + class_name + ", self).__init__ ()") # problem with reloaded lexer module
       # self.putLn ("Lexer.__init__ (self)")
       if grammar.show_tree :
          self.putLn ("self.monitor = None")
       self.putLn ()
       self.declareTerminals (grammar)
       self.putLn ()
       self.declareCollections (grammar)
       self.decIndent ()
       self.putLn ()

       for m in grammar.method_list :
          if m.param_type == "" :
             self.putLn ("def " +  m.method_name + " (self) :")
          else :
             self.putLn ("def " +  m.method_name + " (self, item) :")
          self.incIndent ()
          if m.is_bool :
             self.putLn ("return False")
          else :
             self.putLn ("pass")
          self.decIndent ()
          self.putLn ()

       self.decIndent () # end of class

       self.declareEnums (grammar)
       self.declareTypes (grammar)

       # self.printStart (grammar)
       # self.printSelect (grammar)
       # self.printTags (grammar)

       # self.note ("finished")

# --------------------------------------------------------------------------

if __name__ == "__main__" :

   import optparse

   options = optparse.OptionParser (usage = "usage: %prog [options] input_grammar_file")
   options.add_option ("-o", "--output", "--code", dest="output", default = "", action="store", help="Output file name")

   (opts, args) = options.parse_args ()

   if len (args) == 0 :
      options.error ("Missing input file name")
   if len (args) > 1 :
      options.error ("Too many input file names")

   inputFileName = args [0]
   outputFileName = opts.output

   grammar = Grammar ()
   grammar.openFile (inputFileName)
   grammar.parseRules ()
   grammar.close ()

   product = ToParser ()
   product.open (outputFileName)
   product.parserFromGrammar (grammar)
   product.close ()

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
