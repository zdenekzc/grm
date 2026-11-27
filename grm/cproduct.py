
# cproduct.py

from __future__ import print_function

if __name__ == "__main__" :
   import os, sys
   work_dir = os.path.abspath (sys.path [0])
   module_dir = os.path.join (work_dir, "..", "code")
   sys.path.insert (1, module_dir)

from grammar import Grammar, Rule, Expression, Alternative, Ebnf, Nonterminal, Terminal, Directive, Assign, Style, New, Execute
from code_output import CodeOutput
from input import quoteString

# --------------------------------------------------------------------------

class CProduct (CodeOutput) :

   def enumItem (self, grammar, name) :
       if self.csharp or self.java :
          if name in grammar.enum_item_dict :
             return grammar.enum_item_dict [name] + "." + name
          else :
             return name
       else :
          return name

   # -----------------------------------------------------------------------

   def conditionFromAlternative (self, grammar, alt) :
       for item in alt.items :
           if isinstance (item, Nonterminal) :
              if item.variable != "" :
                 return self.actual_object + self.arrow + self.identifier (item.variable) + self.unequal + self.null
              elif item.add :
                 return "inx < cnt"
           elif isinstance (item, Terminal) :
              if item.multiterminal_name != "" :
                 return self.actual_object + self.arrow + self.identifier (item.variable) + self.unequal + '"' + '"'
           elif isinstance (item, Assign) :
              value = item.value
              if value == "True" :
                 return self.actual_object + self.arrow + self.identifier (item.variable)
              elif value == "False" :
                 return self.log_not + " " + "param" + self.arrow + self.identifier (item.variable)
              else :
                 return self.actual_object + self.arrow + self.identifier (item.variable) + self.equal + self.enumItem (grammar, value)
       # return "unknown"
       return "false"
       # grammar.error ("Cannot find condition")

   def conditionFromExpression (self, grammar, expr) :
       result = ""
       for alt in expr.alternatives :
           if result != "" :
              result = result + self.log_or
           result = result + self.conditionFromAlternative (grammar, alt)
       return result

   def conditionIsUnknown (self, cond) :
       # return (cond == "unknown")
       return False # !?

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
              self.productFromRule (grammar, rule)

   def headerFromRule (self, rule) :
       self.put_func ("send_" + rule.name, cls = self.class_name)
       self.put_param ("param", self.pointer (rule.rule_type))
       self.put_func_decl ()

   def productFromRule (self, grammar, rule) :
       grammar.updatePosition (rule)
       self.last_rule = rule

       if rule.rule_mode != "" :
          grammar.charLineNum = rule.src_line # !?
          grammar.charColNum = rule.src_column
          self.put_func ("send_" + rule.name, cls = self.class_name)
          self.put_param ("param", self.pointer (rule.rule_type))
          self.put_func_body ()
          if rule.store_name != "" :
             self.codeOneStore (grammar, rule)
          if rule.add_used :
             self.put_local ("int", "inx", "0")
             self.put_local ("int", "cnt", "param" + self.arrow + "items" + self.vector_size ())
          if rule.rule_mode == "select" :
             self.codeSelect (grammar, rule)
          else :
             self.productFromExpression (grammar, rule, rule.expr)
          self.put_func_end ()

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
                    self.send ("else")
              else :
                 if inx != 0 :
                    self.send ("else")
                 self.put_if ()
                 self.send (cond)
                 self.put_then ()
              self.put_begin ()
           self.productFromAlternative (grammar, rule, alt)
           if cnt > 1  or expr.continue_expr :
              self.put_end ()
           inx = inx + 1

   def productFromAlternative (self, grammar, rule, alt) :
       grammar.updatePosition (alt)
       for item in alt.items :
           self.productFromItem (grammar, rule, item)

   def productFromItem (self, grammar, rule, item) :
       if isinstance (item, Terminal) :
          self.productFromTerminal (grammar, item)
       elif isinstance (item, Nonterminal) :
          self.productFromNonterminal (grammar, item)
       elif isinstance (item, Ebnf) :
          self.productFromEbnf (grammar, rule, item)
       elif isinstance (item, Style) :
          self.productFromStyle (grammar, item)
       elif isinstance (item, Directive) :
          pass
       else :
          raise Exception ("Unknown alternative item")

   def productFromEbnf (self, grammar, rule, ebnf) :
       grammar.updatePosition (ebnf)
       block = False

       cond = self.conditionFromExpression (grammar, ebnf.expr)
       if ebnf.mark == '?' :
          self.put_if ()
          self.send (cond)
          self.put_then ()
          block = True
       if ebnf.mark == '*' or ebnf.mark == '+' :
          loop = self.conditionIsLoop (grammar, ebnf.expr)
          if loop :
             self.put_while ()
             self.send (cond)
             self.put_do ()
          else :
             self.put_if ()
             self.send (cond)
             self.put_then ()
          block = True

       if block :
          self.put_begin ()

       self.productFromExpression (grammar, rule, ebnf.expr)

       if block :
          self.put_end ()

   def productFromNonterminal (self, grammar, item) :
       grammar.updatePosition (item)
       proc = self.ruleOrGroupName (grammar, item.rule_name)

       self.send (self.access + "send_" + proc)
       self.send ("(")
       self.send (self.actual_object)

       if self.actual_field != "" :
          self.put (self.arrow + self.identifier (self.actual_field))
          dst = item.rule_ref.rule_type if item.rule_ref != None else ""
          src = self.fieldType (grammar, self.actual_owner_type, self.actual_field)
          if dst != "" and src != "" and dst != src and \
                self.isTypeDerived (grammar, dst, src) :
             self.put (self.arrow + "conv_" + dst + " ()")
       elif item.variable :
          self.put (self.arrow + self.identifier (item.variable))
          # a stored field usually has the base type (CmmDeclarator *),
          # but send_<rule> wants the concrete rule type
          dst = ""
          src = ""
          if item.rule_ref != None :
             dst = item.rule_ref.rule_type
          if self.last_rule != None :
             src = self.fieldType (grammar, self.last_rule.rule_type, item.variable)
          if dst != "" and src != "" and dst != src and \
                self.isTypeDerived (grammar, dst, src) :
             self.put (self.arrow + "conv_" + dst + " ()")
       elif item.add :
          self.put (self.arrow + "items" + self.vector_item ("inx"))
       else :
          # narrower type than the rule result => conversion (conv_CmmX)
          dst = ""
          src = ""
          if item.rule_ref != None :
             dst = item.rule_ref.rule_type
          if self.last_rule != None :
             src = self.last_rule.rule_type
          if dst != "" and src != "" and dst != src and \
                self.isTypeDerived (grammar, dst, src) :
             self.put (self.arrow + "conv_" + dst + " ()")

       self.send (")")
       self.putLn (";")

       if item.add :
          self.put_inc ("inx")

   def productFromTerminal (self, grammar, item) :
       if item.multiterminal_name != "" :
          if item.variable != "" :
             if item.multiterminal_name == "character_literal" :
                self.put (self.nested + "putChar (")
             elif item.multiterminal_name == "string_literal" :
                self.put (self.nested + "putString (")
             else :
                self.put (self.nested + "send (")
             self.put (self.actual_object + self.arrow + self.identifier (item.variable))
             if item.multiterminal_name == "character_literal" :
                if self.vala :
                   # value [0] is a char; putChar takes a string in Vala
                   self.put (" [0].to_string ()")
                else :
                   self.put (" [0]")
             self.putLn (");")
       else :
          self.putLn (self.nested + "send (" + self.quote (item.text) + ");")

   def productFromStyle (self, grammar, item) :
       self.putLn (self.nested + "style_" + item.name + " ();")

 # --------------------------------------------------------------------------

   def condOrType (self, grammar, cond, type_name) :
       if cond != "" :
          cond = cond + self.log_or
       rule_type = grammar.struct_dict [type_name]
       if rule_type.tag_name != "" :
           cond = cond + self.actual_object + self.arrow + self.identifier (rule_type.tag_name) + self.equal + self.enumItem (grammar, rule_type.tag_value)
       else :
           cond = cond + self.is_class (self.actual_object, type_name)
       return cond

   def condOrNonterm (self, grammar, cond, nonterm) :
       return self.condOrType (grammar, cond, nonterm.rule_ref.rule_type)

   def condOrAssign (self, grammar, cond, assign) :
       if cond != "" :
          cond = cond + self.log_or
       cond = cond + self.actual_object + self.arrow + self.identifier (assign.variable) + self.equal + self.enumItem (grammar, ssign.value)
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
           if next :
              reorder_next.append (sel_alt)
           else :
              reorder_start.append (sel_alt)
       reorder = reorder_start + reorder_next

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
                   self.send ("else")
                   self.put_begin ()
                for item in start_items :
                    self.productFromItem (grammar, rule, item)
                if self.if_cnt != 0 :
                   self.put_end ()

   def addElse (self) :
       if self.if_cnt > 0 :
          self.send ("else")
       self.if_cnt = self.if_cnt + 1

   def codeSimpleSelection (self, grammar, rule, sel_alt) :
       self.addElse ()
       self.put_if ()
       cond = self.condSelectionAlternative (grammar, sel_alt)
       self.send (cond)
       self.put_then ()
       self.put_begin ()
       self.codeChangeType (sel_alt.select_nonterm.rule_ref.rule_type)
       for item in sel_alt.items :
           self.productFromItem (grammar, rule, item)
       self.actual_object = "param"
       self.put_end ()

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
       self.addElse ()
       self.put_if ()
       cond = ""
       if cnt_alt.continue_nonterm != None :
          cond = self.condOrNonterm (grammar, cond, cnt_alt.continue_nonterm)
       elif cnt_alt.continue_new != None :
          cond = self.condOrType (grammar, cond, cnt_alt.continue_new.new_type)
       self.send (cond)
       self.put_then ()
       self.put_begin ()
       self.codeContinueStart (grammar, rule, cnt_alt, start_items)
       for item in cnt_alt.items :
           self.productFromItem (grammar, rule, item)
       self.actual_object = "param"
       self.put_end ()

   def codeSpecific (self, grammar, rule, cnt_alt, assign, start_items, stop_items, head_items, tail_items, spec_items) :
       if assign == None :
          grammar.error ("Missing tag value")
       self.addElse ()
       self.put_if ()
       self.send ("param" + self.arrow + self.identifier (assign.variable) + self.equal + self.enumItem (grammar, assign.value))
       self.put_then ()
       self.put_begin ()

       self.codeContinueStart (grammar, rule, cnt_alt, start_items)

       items = head_items + spec_items + tail_items + stop_items
       for item in items:
           if item == assign :
              pass
           elif isinstance (item, New) :
              pass
           else :
              self.productFromItem (grammar, rule, item)

       self.actual_object = "param"
       self.put_end ()

   def codeContinueStart (self, grammar, rule, cnt_alt, start_items) :
       if cnt_alt.continue_nonterm != None :
          self.actual_field = cnt_alt.continue_nonterm.rule_ref.store_name
          self.actual_owner_type = cnt_alt.continue_nonterm.rule_ref.rule_type
          self.codeChangeType (cnt_alt.continue_nonterm.rule_ref.rule_type)

       if cnt_alt.continue_new != None :
          self.actual_field = cnt_alt.continue_new.store_name
          self.actual_owner_type = cnt_alt.continue_new.new_type
          self.codeChangeType (cnt_alt.continue_new.new_type)

       skip = False
       if cnt_alt.continue_nonterm != None :
          # self.putLn ("# " + str ( len (cnt_alt.continue_nonterm.rule_ref.store_orig)))
          if len (cnt_alt.continue_nonterm.rule_ref.store_orig) == 1 :
             skip = True

       if not skip :
          for item in start_items :
              self.productFromItem (grammar, rule, item)

       self.actual_field = ""

   def codeChangeType (self, type) :
       if self.pascal :
          self.actual_object = "param.conv_" + type
       else :
          self.actual_object = "param0"
          ptr_type = self.pointer (type)
          self.put_local (ptr_type, "param0", self.type_cast (type, "param"))

  # -----------------------------------------------------------------------

   def isTypeDerived (self, grammar, type_name, base_name) :
       type = grammar.struct_dict.get (type_name, None)
       while type != None and type.type_name != base_name :
          type = type.super_type
       return type != None

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

   def groupType (self, group) :
       type = group.from_type
       if type == "" :
          type = group.ctrl_type
       return type

   def headerFromGroup (self, group) :
       self.putLn ("void " + "send_" + group.group_name + " (" + self.groupType (group) + " * param);")

   def productFromGroup (self, grammar, group) :
       proc = "send_" + group.group_name
       self.put_func (proc, cls = self.class_name)
       self.put_param ("param", self.pointer (self.groupType (group)))
       self.put_func_body ()

       self.if_cnt = 0

       for rule in grammar.rules :
           if rule.name in group.priority_list :
              self.ruleFromGroup (grammar, group, rule)

       for rule in grammar.rules :
           if rule.name not in group.priority_list :
              self.ruleFromGroup (grammar, group, rule)

       self.artificialItems (grammar, group)

       self.put_func_end ()

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

   def paramIsType (self, grammar, type) :
       if getattr (type, "tag_name", "") != "" :
          self.put ("param" + self.arrow + self.identifier (type.tag_name) + self.equal + self.enumItem (grammar, type.tag_value))
       else :
          self.put ("param" + self.arrow + "conv_" + getattr (type, "rule_type", "")  + "()" + self.unequal + self.null) # !?

   def ruleFromReuseGroup (self, grammar, group, rule) :
       proc = "send_" + group.group_name
       # proc = "send_expr" # !?
       if rule.rule_mode == "new" :
          self.addElse ()
          self.put_if ()
          self.paramIsType (grammar, rule)
          self.put_then ()
          self.put_begin ()
          self.codeChangeType (rule.rule_type)
          if rule.store_name != "" :
             self.codeMultiStore (grammar, rule)
          self.putLn (self.access + "send_" + rule.name + " (param0);")
          self.actual_object = "param"
          self.put_end ()

   def ruleFromRewriteGroup (self, grammar, group, rule) :
       proc = "send_" + group.group_name
       if rule.rule_mode == "new" :
          self.addElse ()
          self.put_if ()
          self.paramIsType (grammar, rule)
          self.put_then ()
          self.put_begin ()
          self.codeChangeType (rule.rule_type)
          if rule.add_used :
             self.put_local ("int", "inx", "0")
             self.put_local ("int", "cnt", "param0" + self.arrow + "items" + self.vector_size ())
          if rule.store_name != "" :
             self.codeStore (grammar, rule)
          self.productFromExpression (grammar, rule, rule.expr)
          self.actual_object = "param"
          self.put_end ()
       elif rule.rule_mode == "select" :
          self.codeSelectGroup (grammar, rule)

   def fieldType (self, grammar, type_name, field_name) :
       "type of a struct field, following the super types"
       type = grammar.struct_dict.get (type_name, None)
       while type != None :
          fields = getattr (type, "fields", None)
          if fields != None and field_name in fields :
             return fields [field_name].field_type
          type = type.super_type
       return ""

   def storeFieldType (self, grammar, rule) :
       return self.fieldType (grammar, rule.rule_type, rule.store_name)

   def putStore (self, grammar, rule, r) :
       proc = self.ruleOrGroupName (grammar, r.name)
       expr = "param0" + self.arrow + self.identifier (rule.store_name)
       # the field is usually stored with the base type (CmmDeclarator *);
       # send_<rule> wants the concrete rule type
       dst = getattr (r, "rule_type", "")
       src = self.storeFieldType (grammar, rule)
       if dst != "" and src != "" and dst != src and \
             self.isTypeDerived (grammar, dst, src) :
          expr = expr + self.arrow + "conv_" + dst + " ()"
       self.putLn ("send_" + proc + " (" + expr + ")")

   def codeStore (self, grammar, rule) :
       # self.putLn ("// store all ")
       if rule.store_from != None :
          self.putStore (grammar, rule, rule.store_from)
       else :
          # if len (rule.store_orig) > 1 :
          #    self.putLn ("// store all")
          for r in rule.store_orig :
              self.putStore (grammar, rule, r)

   def codeOneStore (self, grammar, rule) :
       if rule.store_from != None :
          self.putStore (grammar, rule, rule.store_from)
       else :
          if len (rule.store_orig) == 1 :
             # self.putLn ("// store one")
             r = rule.store_orig [0]
             self.putStore (grammar, rule, r)

   def codeMultiStore (self, grammar, rule) :
       if rule.store_from == None :
          if len (rule.store_orig) > 1 :
             # self.putLn ("// store multi")
             for r in rule.store_orig :
                 self.putStore (grammar, rule, r)

# --------------------------------------------------------------------------

   def artificialItems (self, grammar, group) :
       # start = True
       for artificial in group.artificial_list :
              type = grammar.struct_dict.get (artificial.struct_name, None)
              if type == None :
                 grammar.error ("Unknown stucture: " +  artificial.struct_name)

              self.put_if ()
              self.paramIsType (grammar, type)
              self.put_then ()

              self.incIndent ()
              self.putLn (self.access + "send_" + artificial.call_name + " (param);")
              self.decIndent ()

   def artificialFunctions (self, grammar, group) :
       for artificial in group.artificial_list :
           # cls is required, otherwise the function is registered on the
           # root and never printed (send_<artificial> stayed undefined in
           # C++/C# and Vala)
           self.put_func ("send_" + artificial.call_name, cls = self.class_name)
           self.put_param ("param", self.pointer (self.groupType (group)))
           self.put_func_body ()
           func = artificial.func_name
           if func != "" :
              self.send (self.nested + func)
              self.send ("(")
              if func in ["put", "send"] :
                 self.put ("param" + self.arrow + "text") # !?
              self.send (")")
              self.send (";")
              self.putEol ()
           self.put_func_end ()

   # -----------------------------------------------------------------------

   def __init__ (self) :
       super (CProduct, self).__init__ ()
       self.actual_field = ""
       self.actual_owner_type = ""
       self.actual_object = "param"
       self.if_cnt = 0 # local

       self.parser_header = "parser.h"
       self.product_header = "product.h"
       self.super_name = "Output"
       self.class_name = "Product"

   # -----------------------------------------------------------------------

   def productCSharp (self, grammar) :

       self.putLn ("using System.Collections.Generic;")
       self.empty_line ()

       self.send ("namespace")
       self.send (self.ns)
       self.putEol ()
       self.put_begin ()

       self.put_class (self.class_name, above = self.super_name)

       self.productFromRules (grammar)
       self.productFromGroups (grammar)

       self.put_method_declarations (self.class_name)
       self.put_class_end ()

       self.empty_line ()
       self.put_end () # end of namespace

   # -----------------------------------------------------------------------

   def productJava (self, grammar) :

       self.send ("package")
       self.send (self.ns)
       self.send (";")
       self.putEol ()

       self.empty_line ()

       self.put_class (self.class_name, above = self.super_name)

       self.productFromRules (grammar)
       self.productFromGroups (grammar)

       self.put_method_declarations (self.class_name)
       self.put_class_end ()

   # -----------------------------------------------------------------------

   def productPascal (self, grammar) :

       self.send ("unit")
       self.send (self.ns)
       self.send (";")
       self.putEol ()
       self.empty_line ()

       self.putLn ("interface")
       self.empty_line ()

       self.send ("use")
       self.send (self.parser_header)
       self.send (";")
       self.putEol ()
       self.empty_line ()

       self.put_class (self.class_name, above = self.super_name)
       self.put_public ()

       for rule in grammar.rules :
          self.headerFromRule (rule);

       for group in grammar.group_list :
           self.headerFromGroup (group)
           for artificial in group.artificial_list :
               # send_<artificial> is called from send_<group> in the
               # .cpp; the declaration has to be here (the implementations
               # come from artificialFunctions () in productFromGroups).
               self.putLn ("void send_" + artificial.call_name +
                           " (" + self.groupType (group) + " * param);")

       self.put_method_declarations (self.class_name)

       self.put_class_end ()

       self.empty_line ()
       self.putLn ("implementation")
       self.empty_line ()

       self.productFromRules (grammar)
       self.productFromGroups (grammar)

       self.put_method_implementations (self.class_name)

       self.empty_line ()
       self.putLn ("end.")

   # -----------------------------------------------------------------------

   def productJavaScript (self, grammar) :

       self.put_class (self.class_name, above = self.super_name)

       self.productFromRules (grammar)
       self.productFromGroups (grammar)

       self.put_method_declarations (self.class_name)
       self.put_class_end ()

   # -----------------------------------------------------------------------

   def productVala (self, grammar) :

       if self.ns != "" :
          self.send ("namespace")
          self.send (self.ns)
          self.putEol ()
          self.put_begin ()

       self.put_class (self.class_name, above = self.super_name)

       self.productFromRules (grammar)
       self.productFromGroups (grammar)

       self.put_method_declarations (self.class_name)
       self.put_class_end ()

       if self.ns != "" :
          self.empty_line ()
          self.put_end () # end of namespace

   # -----------------------------------------------------------------------

   def productRust (self, grammar) :

       self.put_class (self.class_name, above = self.super_name)

       self.productFromRules (grammar)
       self.productFromGroups (grammar)

       self.put_method_declarations (self.class_name)
       self.put_class_end ()

   # -----------------------------------------------------------------------

   def productHeader (self, grammar, header_name = "") :
       # header_name = the header file being written (the CLI passes its
       # --header value; library users pass their target name). It only
       # feeds the include-guard symbol.
       if header_name == "" :
          header_name = self.product_header
       header_symbol = self.get_header_symbol (header_name)
       self.put_header_ifdef (header_symbol)

       self.putLn ("#include " + quoteString (self.parser_header))
       self.putLn ()

       for rule in grammar.rules :
           self.setupGroup (grammar, rule)

       # if not self.c :
       self.put_class (self.class_name, above = self.super_name)
       self.put_public ()

       for rule in grammar.rules :
           if rule.hide_group == None :
              self.headerFromRule (rule);

       for group in grammar.group_list :
           self.headerFromGroup (group)
           for artificial in group.artificial_list :
               # send_<artificial> is called from send_<group> in the
               # .cpp; the declaration has to be here (the implementations
               # come from artificialFunctions () in productFromGroups).
               self.putLn ("void send_" + artificial.call_name +
                           " (" + self.groupType (group) + " * param);")

       self.put_method_declarations (self.class_name)

       # if not self.c :
       self.put_class_end ()

       self.put_header_endif (header_symbol)

   def productCode (self, grammar) :
       "call productCode after productHeader"

       self.putLn ("#include " + quoteString (self.product_header))
       self.putLn ()

       self.productFromRules (grammar)
       self.productFromGroups (grammar)

       self.put_method_implementations (self.class_name)

# --------------------------------------------------------------------------

if __name__ == "__main__" :

   import optparse

   options = optparse.OptionParser (usage = "usage: %prog [options] input_grammar_file")
   options.add_option ("--header", dest="header", default = "",    action="store",      help="Output header file name")
   options.add_option ("--code",   dest="code",   default = "",    action="store",      help="Output file name")
   options.add_option ("--cpp",    dest="cpp",    default = False, action="store_true", help="C++")
   options.add_option ("--c",      dest="c",      default = False, action="store_true", help="C")
   options.add_option ("--csharp", dest="csharp", default = False, action="store_true", help="C#")
   options.add_option ("--java",   dest="java",   default = False, action="store_true", help="Java")
   options.add_option ("--pascal", dest="pascal", default = False, action="store_true", help="Pascal")
   options.add_option ("--vala",   dest="vala",   default = False, action="store_true", help="Vala")
   options.add_option ("--js",     dest="js",     default = False, action="store_true", help="Java Script")
   options.add_option ("--rust",   dest="rust",   default = False, action="store_true", help="Rust")

   options.add_option ("--ns", "--namespace", "--package", "--unit", dest="ns", default = "", action="store", help="C# namespace, Java package")
   options.add_option ("--parser", "--parser-header", dest="parser", default = "", action="store", help="Parser header file name")
   options.add_option ("--class",  dest="class_name", default = "", action="store", help="Product class name")
   options.add_option ("--super",  dest="super_name", default = "", action="store", help="Base class of the product")

   (opts, args) = options.parse_args ()

   if len (args) == 0 :
      options.error ("Missing input file name")
   if len (args) > 1 :
      options.error ("Too many input file names")

   inputFileName = args [0]
   headerFileName = opts.header
   codeFileName = opts.code

   grammar = Grammar ()
   grammar.openFile (inputFileName)
   grammar.parseRules ()
   grammar.close ()

   product = CProduct ()

   if opts.class_name != "" :
      product.class_name = opts.class_name
   if opts.super_name != "" :
      product.super_name = opts.super_name

   if opts.csharp :
      product.csharp = True
   elif opts.java :
      product.java = True
   elif opts.pascal :
      product.pascal = True
   elif opts.vala :
      product.vala = True
   elif opts.js :
      product.js = True
   elif opts.rust :
      product.rust = True
   elif opts.c :
      product.c = True
   else :
     product.cpp = True
   product.set_consts ()

   if headerFileName != "" :
      product.product_header = os.path.basename (headerFileName)

   if opts.parser != "" :
      product.parser_header = os.path.basename (opts.parser)

   product.ns = ""
   if opts.ns != "" :
      product.ns = opts.ns

   if product.csharp :
      product.open (codeFileName)
      product.productCSharp (grammar)
      product.close ()
   elif product.java :
      product.open (codeFileName)
      product.productJava (grammar)
      product.close ()
   elif product.pascal :
      product.open (codeFileName)
      product.productPascal (grammar)
      product.close ()
   elif product.vala :
      product.open (codeFileName)
      product.productVala (grammar)
      product.close ()
   elif product.js :
      product.open (codeFileName)
      product.productJavaScript (grammar)
      product.close ()
   elif product.rust :
      product.open (codeFileName)
      product.productRust (grammar)
      product.close ()
   else :
      product.open (headerFileName)
      product.productHeader (grammar, headerFileName)
      product.close ()

      product.open (codeFileName)
      product.productCode (grammar)
      product.close ()

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
