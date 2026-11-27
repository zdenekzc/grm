
# toproduct.py

from __future__ import print_function

if __name__ == "__main__" :
   import os, sys
   work_dir = os.path.abspath (sys.path [0])
   module_dir = os.path.join (work_dir, "..", "code")
   sys.path.insert (1, module_dir)

from grammar import Grammar, Rule, Expression, Alternative, Ebnf, Nonterminal, Terminal, Directive, Assign, Style, New, Execute
from code_output import CodeOutput
# from output import incIndent, decIndent, put, putEol, putCondEol, putLn

# --------------------------------------------------------------------------

class ToProduct (CodeOutput) :

   def __init__ (self) :
       super (ToProduct, self).__init__ ()
       self.actual_param = ""
       self.if_cnt = 0 # local

   # -- scan store directives --

   def scanRules (self, grammar) :
       for rule in grammar.rules :
           grammar.updatePosition (rule)
           self.scanExpression (grammar, rule.expr)

   def scanExpression (self, grammar, expr) :
       for alt in expr.alternatives :
          self.scanAlternative (grammar, alt)

   def scanAlternative (self, grammar, alt) :
       for item in alt.items :
           if isinstance (item, Ebnf) :
              self.scanExpression (grammar, item.expr)
           elif isinstance (item, Nonterminal) :
              if item.rule_ref.store_name != "" :
                 if alt.continue_link == None :
                    grammar.error ("Missing continue alternative")
                 store_nonterm = alt.continue_link.select_nonterm
                 store_orig_rule = store_nonterm.rule_ref
                 store_to_rule = item.rule_ref
                 if store_orig_rule not in store_to_rule.store_orig :
                    store_to_rule.store_orig.append (store_orig_rule)
                    # print ("STORE", store_orig_rule.name, "->", store_to_rule.name, "(", len (store_to_rule.store_orig), ")")

   # -----------------------------------------------------------------------

   def conditionFromAlternative (self, grammar, alt) :
       for item in alt.items :
           if isinstance (item, Nonterminal) :
              if item.variable != "" :
                 return "param." + item.variable + " != None"
              elif item.add :
                 return "inx < cnt"
           elif isinstance (item, Terminal) :
              if item.multiterminal_name != "" :
                 return "param." + item.variable + " != " + '"' + '"'
           elif isinstance (item, Assign) :
              if item.value == "True" :
                 return "param." + item.variable
              elif item.value == "False" :
                 return "not param." + item.variable
              else :
                 return "param." + item.variable + " == " + item.value
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

   # -----------------------------------------------------------------------

   def productFromRules (self, grammar) :
       self.last_rule = None
       for rule in grammar.rules :
           self.setupGroup (grammar, rule)
       for rule in grammar.rules :
           if rule.hide_group == None :
              self.openSection (rule)
              self.productFromRule (grammar, rule)
              self.closeSection ()

   def productFromRule (self, grammar, rule) :
       grammar.updatePosition (rule)
       self.last_rule = rule
       if rule.rule_mode != "" :
          grammar.charLineNum = rule.src_line # !?
          grammar.charColNum = rule.src_column
          self.putLn ("def send_" + rule.name + " (self, param) :")
          self.incIndent ()
          if rule.store_name != "" :
             self.codeOneStore (grammar, rule)
          if rule.add_used :
             self.putLn ("inx = 0")
             self.putLn ("cnt = len (param.items)")
          if rule.rule_mode == "select" :
             self.codeSelect (grammar, rule)
          else :
             self.productFromExpression (grammar, rule, rule.expr)
          self.decIndent ()
          self.putEol ()

   def productFromExpression (self, grammar, rule, expr) :
       cnt = len (expr.alternatives)
       inx = 0
       for alt in expr.alternatives :
           if cnt > 1 :
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
           self.productFromAlternative (grammar, rule, alt)
           if cnt > 1 : #  or expr.continue_expr :
              self.decIndent ()
           inx = inx + 1

   def productFromAlternative (self, grammar, rule, alt) :
       grammar.updatePosition (alt)
       any = False
       for item in alt.items :
           tmp = self.productFromItem (grammar, rule, item)
           any = any or tmp
       if not any :
          self.putLn ("pass")

   def productFromItem (self, grammar, rule, item) :
       any = False
       if isinstance (item, Terminal) :
          self.productFromTerminal (grammar, item)
          any = True
       elif isinstance (item, Nonterminal) :
          self.productFromNonterminal (grammar, item)
          any = True
       elif isinstance (item, Ebnf) :
          self.productFromEbnf (grammar, rule, item)
          any = True
       elif isinstance (item, Style) :
          self.productFromStyle (grammar, item)
          any = True
       # elif isinstance (item, New) :
       #    self.productChooseItem (grammar, rule, alt.continue_link, "param." + item.store_name, True)
       #    any = True
       elif isinstance (item, Directive) :
          pass
       else :
          raise Exception ("Unknown alternative item")
       return any

   def productFromEbnf (self, grammar, rule, ebnf) :
       grammar.updatePosition (ebnf)
       block = False

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

       self.productFromExpression (grammar, rule, ebnf.expr)

       if block :
          self.decIndent ()

   def productFromNonterminal (self, grammar, item) :
       grammar.updatePosition (item)
       proc = self.ruleOrGroupName (grammar, item.rule_name)

       self.put ("self.send_" + proc)
       self.put (" (")
       self.put ("param")
       if self.actual_param != "" :
          self.put ("." + self.actual_param)
       if item.variable :
          self.put ("." + item.variable)
       elif item.add :
          self.put (".items [inx]")
       self.putLn (")")

       if item.add :
          self.putLn ("inx = inx + 1")

   def productFromTerminal (self, grammar, item) :
       if item.multiterminal_name != "" :
          if item.variable != "" :
             quote1 = item.multiterminal_name == "character_literal";
             quote2 = item.multiterminal_name == "string_literal";

             if quote1 :
                self.put ("self.sendChr (")
             elif quote2 :
                self.put ("self.sendStr (")
             else :
                self.put ("self.send (")
             self.put ("param." + item.variable)
             self.putLn (")")
       else :
          self.putLn ("self.send (" + '"' + item.text + '"' + ")")

   def productFromStyle (self, grammar, item) :
       self.putLn ("self.style_" + item.name + " ()")

# --------------------------------------------------------------------------

   def condOrType (self, grammar, cond, type_name) :
       if cond != "" :
          cond = cond + " or "
       rule_type = grammar.struct_dict [type_name]
       if rule_type.tag_name != "" :
           # cond = cond + "param." + rule_type.tag_name + " == " + "param." + rule_type.tag_value
           cond = cond + "param." + rule_type.tag_name + " == " + rule_type.tag_value
       else :
           cond = cond + "isinstance (param, " + type_name + ")"
       return cond

   def condOrNonterm (self, grammar, cond, nonterm) :
       return self.condOrType (grammar, cond, nonterm.rule_ref.rule_type)

   def condOrAssign (self, grammar, cond, assign) :
       if cond != "" :
          cond = cond + " or "
       # cond = cond + "param." + assign.variable + " == " + "param." + assign.value
       cond = cond + "param." + assign.variable + " == " + assign.value
       return cond

   def condSelectionAlternative (self, grammar, sel_alt) :
       cond = ""
       if not sel_alt.select_independent or sel_alt.select_ebnf == None:
          cond = self.condOrNonterm (grammar, cond, sel_alt.select_nonterm)

       for cnt_alt in sel_alt.select_branches :
          if cnt_alt.continue_nonterm != None :
             cond = self.condOrNonterm (grammar, cond, cnt_alt.continue_nonterm)
          else :
             if cnt_alt.continue_assign != None :
                cond = self.condOrAssign (self, grammar, cnt_alt.continue_assign)
             for spec_alt in cnt_alt.continue_branches :
                 if spec_alt.specific_assign != None :
                    cond = self.condOrAssign (self, grammar, spec_alt.specific_assign)

       return cond

   def codeSelect (self, grammar, rule) :
       reorder_start = [ ]
       reorder_next = [ ]
       for sel_alt in rule.expr.alternatives :
           next = False
           if sel_alt.select_ebnf == None :
              rule_ref = sel_alt.select_nonterm.rule_ref
              rule_type = grammar.struct_dict [rule_ref.rule_type]
              # if rule_ref.rule_mode == "select" :
              if rule_type.tag_value == "" :
                 next = True
              # alternativa stejneho typu jako select (stat <select CmmItem>: flexible_stat
              # s typem CmmItem) pokryva vsechny potomky: jeji tag (itemKind) neni tag
              # potomku, takze ma byt az posledni (else)
              if rule_ref.rule_type == rule.rule_type :
                 next = True
           if next :
              reorder_next.append (sel_alt)
           else :
              reorder_start.append (sel_alt)
       reorder = reorder_start + reorder_next

       # posledni alternativa stejneho typu / nulovatelna je else
       self.catch_all_alt = None
       if reorder and getattr (reorder [-1], "nullable", False) :
          self.catch_all_alt = reorder [-1]
       if reorder and reorder [-1].select_ebnf == None and \
          reorder [-1].select_nonterm.rule_ref.rule_type == rule.rule_type :
          self.catch_all_alt = reorder [-1]

       self.if_cnt = 0
       for sel_alt in reorder :
           self.codeSelectionAlternative (grammar, rule, sel_alt)

   def codeSelectGroup (self, grammar, rule) :
       for sel_alt in rule.expr.alternatives :
           self.codeSelectionAlternative (grammar, rule, sel_alt, code_group = True)

   def codeSelectionAlternative (self, grammar, rule, sel_alt, code_group = False) :
       if sel_alt.select_ebnf == None :
          if not code_group :
             self.codeSimpleSelection (grammar, rule, sel_alt)
       else :
          start_items = [ ]
          stop_items = [ ]
          stop = False
          for item in sel_alt.items :
              if item == sel_alt.select_ebnf :
                 stop = True
              elif not stop :
                 start_items.append (item)
              else :
                 stop_items.append (item)

          for cnt_alt in sel_alt.select_branches :
              self.codeContinue (grammar, rule, cnt_alt, start_items, stop_items, code_group)

          if not code_group :
             if not sel_alt.select_independent :
                if self.if_cnt != 0 :
                   self.putLn ("else :")
                   self.incIndent ()
                for item in start_items :
                    self.productFromItem (grammar, rule, item)
                if self.if_cnt != 0 :
                   self.decIndent ()

   def codeIf (self) :
       if self.if_cnt == 0 :
          self.put ("if ")
       else :
          self.put ("elif ")
       self.if_cnt = self.if_cnt + 1

   def codeSimpleSelection (self, grammar, rule, sel_alt) :
       if sel_alt is getattr (self, "catch_all_alt", None) and self.if_cnt > 0 :
          self.putLn ("else :")
       else :
          self.codeIf ()
          cond = self.condSelectionAlternative (grammar, sel_alt)
          self.putLn (cond + " :")
       self.incIndent ()
       for item in sel_alt.items :
           self.productFromItem (grammar, rule, item)
       self.decIndent ()

   def codeContinue (self, grammar, rule, cnt_alt, start_items, stop_items, code_group) :
       grammar.updatePosition (cnt_alt)
       head_items = [ ]
       tail_items = [ ]
       stop = False
       for item in cnt_alt.items :
           if item == cnt_alt.continue_ebnf :
              stop = True
           elif not stop :
              head_items.append (item)
           else :
              tail_items.append (item)

       if cnt_alt.continue_ebnf == None :
          if cnt_alt.continue_assign == None :
             if not code_group or cnt_alt.continue_nonterm == None :
                self.codeSimpleContinue (grammar, rule, cnt_alt, start_items)
          else :
             self.codeSpecific (grammar, rule, cnt_alt, cnt_alt.continue_assign,
                                start_items, stop_items, head_items, tail_items, [])
       else :
          for spec_alt in cnt_alt.continue_branches :
              self.codeSpecific (grammar, rule, cnt_alt, spec_alt.specific_assign,
                                 start_items, stop_items, head_items, tail_items, spec_alt.items)

   def codeSimpleContinue (self, grammar, rule, cnt_alt, start_items) :
       self.codeIf ()
       cond = ""
       if cnt_alt.continue_nonterm != None :
          cond = self.condOrNonterm (grammar, cond, cnt_alt.continue_nonterm)
       elif cnt_alt.continue_new != None :
          cond = self.condOrType (grammar, cond, cnt_alt.continue_new.new_type)
       self.putLn (cond + " :")
       self.incIndent ()
       self.codeContinueStart (grammar, rule, cnt_alt, start_items)
       for item in cnt_alt.items :
           self.productFromItem (grammar, rule, item)
       self.decIndent ()

   def codeSpecific (self, grammar, rule, cnt_alt, assign, start_items, stop_items, head_items, tail_items, spec_items) :
       if assign == None :
          grammar.error ("Missing tag value")
       self.codeIf ()
       # self.putLn ("param." + assign.variable + " == param." + assign.value + " :")
       self.putLn ("param." + assign.variable + " == " + assign.value + " :")
       self.incIndent ()

       self.codeContinueStart (grammar, rule, cnt_alt, start_items)

       items = head_items + spec_items + tail_items + stop_items
       for item in items:
           if item == assign :
              pass
           elif isinstance (item, New) :
              pass
           else :
              self.productFromItem (grammar, rule, item)
       self.decIndent( )

   def codeContinueStart (self, grammar, rule, cnt_alt, start_items) :
       if cnt_alt.continue_nonterm != None :
          self.actual_param = cnt_alt.continue_nonterm.rule_ref.store_name
       if cnt_alt.continue_new != None :
          self.actual_param = cnt_alt.continue_new.store_name

       skip = False
       if cnt_alt.continue_nonterm != None :
          # self.putLn ("# " + str ( len (cnt_alt.continue_nonterm.rule_ref.store_orig)))
          if len (cnt_alt.continue_nonterm.rule_ref.store_orig) == 1 :
             skip = True

       if not skip :
          for item in start_items :
              # self.putLn ("# store start")
              self.productFromItem (grammar, rule, item)

       self.actual_param = ""

  # -----------------------------------------------------------------------

   def isDerivedType (self, grammar, rule, target_name) :
       result = False
       if rule.rule_type != "" :
          type = grammar.struct_dict.get (rule.rule_type, None)
          while type != None and type.type_name != target_name :
             type = type.super_type
          if type != None :
             result = True
       return result

   def setupGroup (self, grammar, rule) :
       grammar.updatePosition (rule)
       cnt = 0
       for group in grammar.group_list :
           result = False
           # grammar.info ("Testing " + rule_name + " : " + group.group_name + " : " + str (group.rule_list))

           if group.rewrite_items :
              result = self.isDerivedType (grammar, rule, group.from_type)
              if rule.name in group.include_list :
                 result = True
              if rule.name in group.exclude_list :
                 result = False
              if result  :
                 cnt = cnt + 1
                 if rule.name in group.call_list :
                    rule.reuse_group = group # reuse complicated rule
                 else :
                    rule.hide_group = group
                    rule.rewrite_group = group
                    rule.subst_group = group

           if not group.rewrite_items :
              if rule.name in group.include_list :
                 cnt = cnt + 1
                 rule.hide_group = group
                 rule.subst_group = group
              else :
                 result = self.isDerivedType (grammar, rule, group.from_type)
                 if rule.name in group.exclude_list :
                    result = False
                 if result :
                    cnt = cnt + 1
                    rule.reuse_group = group

       if cnt > 1 :
          grammar.error ("Rule " + rule.name + " is in two groups")

   def ruleOrGroupName (self, grammar, rule_name) :
       rule = grammar.rule_dict [rule_name]
       group = rule.subst_group
       if group != None :
          proc = group.group_name
       else :
          proc = rule_name
       return proc

   def productFromGroups (self, grammar) :
       for group in grammar.group_list :
           self.productFromGroup (grammar, group)

   def productFromGroup (self, grammar, group) :
       proc = "send_" + group.group_name
       self.putLn ("def " + proc + " (self, param) :")
       self.incIndent ()
       self.if_cnt = 0

       for rule in grammar.rules :
           if rule.name in group.priority_list :
              self.ruleFromGroup (grammar, group, rule)

       for rule in grammar.rules :
           if rule.name not in group.priority_list :
              self.ruleFromGroup (grammar, group, rule)

       self.artificialItems (grammar, group)

       self.decIndent ()
       self.putLn ("")

       self.artificialFunctions (grammar, group)

   def ruleFromGroup (self, grammar, group, rule) :
       grammar.updatePosition (rule)
       grammar.charLineNum = rule.src_line # !?
       grammar.charColNum = rule.src_column
       if rule.rule_mode != "" :
          if rule.reuse_group == group :
             self.ruleFromReuseGroup (grammar, group, rule)
          if rule.rewrite_group == group :
             self.ruleFromRewriteGroup (grammar, group, rule)

   def ruleFromReuseGroup (self, grammar, group, rule) :
       # self.putLn ("# " + rule.name)
       if rule.rule_mode == "new" :
          self.codeIf ()
          if rule.tag_name != "" :
             # self.putLn ("param." + rule.tag_name + " == param." + rule.tag_value + ":")
             self.putLn ("param." + rule.tag_name + " == " + rule.tag_value + ":")
          else :
             self.putLn ("isinstance (param, " + rule.rule_type + ") :")
          self.incIndent ()
          if rule.store_name != "" :
             self.codeMultiStore (grammar, rule)
          self.putLn ("self.send_" + rule.name + " (param)")
          self.decIndent ()

   def ruleFromRewriteGroup (self, grammar, group, rule) :
       # self.putLn ("# " + rule.name)
       if rule.rule_mode == "new" :
          self.codeIf ()
          if rule.tag_name != "" :
             # self.putLn ("param." + rule.tag_name + " == param." + rule.tag_value + ":")
             self.putLn ("param." + rule.tag_name + " == " + rule.tag_value + ":")
          else :
             self.putLn ("isinstance (param, " + rule.rule_type + ") :")
          self.incIndent ()
          if rule.add_used :
             self.putLn ("inx = 0")
             self.putLn ("cnt = len (param.items)")
          if rule.store_name != "" :
             self.codeStore (grammar, rule)
          self.productFromExpression (grammar, rule, rule.expr)
          self.decIndent ()
       elif rule.rule_mode == "select" :
          self.codeSelectGroup (grammar, rule)

   def putStore (self, grammar, rule, r) :
       proc = self.ruleOrGroupName (grammar, r.name)
       self.putLn ("self.send_" + proc + " (param." + rule.store_name + ")")

   def codeStore (self, grammar, rule) :
       # self.putLn ("# store all ")
       if rule.store_from != None :
          self.putStore (grammar, rule, rule.store_from)
       else :
          # rewrite group nemusi mit store_orig (stejne jako cproduct.py)
          for r in rule.store_orig :
              self.putStore (grammar, rule, r)

   def codeOneStore (self, grammar, rule) :
       if rule.store_from != None :
          self.putStore (grammar, rule, rule.store_from)
       else :
          if len (rule.store_orig) == 1 :
             # self.putLn ("# store one")
             r = rule.store_orig [0]
             self.putStore (grammar, rule, r)

   def codeMultiStore (self, grammar, rule) :
       if rule.store_from == None :
          if len (rule.store_orig) > 1 :
             self.putLn ("# store multi")
             for r in rule.store_orig :
                 self.putStore (grammar, rule, r)

# --------------------------------------------------------------------------

   def artificialItems (self, grammar, group) :
       # start = True
       for artificial in group.artificial_list :
              type = grammar.struct_dict.get (artificial.struct_name, None)
              if type == None :
                 grammar.error ("Unknown stucture: " +  artificial.struct_name)

              if type.tag_name != "" :
                 # cond =  "param." + type.tag_name + " == " + "param." + type.tag_value
                 cond =  "param." + type.tag_name + " == " + type.tag_value
              else :
                 cond = "isinstance (param, " + type.type_name + ")"

              self.codeIf ()
              self.putLn (cond + " :")

              self.incIndent ()
              self.putLn ("self.send_" + artificial.call_name + " (param)")
              self.decIndent ()

   def artificialFunctions (self, grammar, group) :
       for artificial in group.artificial_list :
           self.putLn ("def send_" + artificial.call_name + " (self, param) :")
           self.incIndent ()
           func = artificial.func_name
           if func == "" :
              self.putLn ("pass")
           else :
              self.put ("self." + func + " (")
              if func in ["put", "send"] :
                 self.put ("param.text") # !?
              self.putLn (")")
           self.decIndent ()
           self.putLn ()

# --------------------------------------------------------------------------

   def productFromGrammar (self, grammar, parser_module = "") :

       self.putLn ()
       if parser_module != "" :
          self.putLn ("from " + parser_module + " import *")
       self.putLn ("from output import Output")
       self.putLn ()

       self.putLn ("class Product (Output) :")
       self.putLn ("")
       self.incIndent ()

       self.scanRules (grammar)
       self.productFromRules (grammar)
       self.productFromGroups (grammar)

       self.decIndent ()

# --------------------------------------------------------------------------

if __name__ == "__main__" :

   import optparse

   options = optparse.OptionParser (usage = "usage: %prog [options] input_grammar_file")
   options.add_option ("-o", "--output", "--code", dest="output", default = "", action="store", help="Output file name")
   options.add_option ("--parser", "--parser-module", dest="parser", default = "", action="store",
                       help="Parser module to import (e.g. cmm_parser); needed for enum constants and node classes")

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

   parser_module = ""
   if opts.parser != "" :
      parser_module = os.path.splitext (os.path.basename (opts.parser)) [0]

   product = ToProduct ()
   product.openFile (outputFileName)
   product.productFromGrammar (grammar, parser_module)
   product.close ()

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
