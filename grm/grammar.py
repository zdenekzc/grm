
# grammar.py

from __future__ import print_function

from lexer import Lexer

# --------------------------------------------------------------------------

class Rule (object) :
   def __init__ (self) :
       self.name = ""
       self.expr = None
       self.rule_mode = ""
       self.rule_type = ""
       self.super_type = ""
       self.type_ref = None
       self.tag_name = ""
       self.tag_value = ""
       self.store_name = ""
       self.store_type = ""
       self.store_from_name = ""
       self.store_from = None
       self.store_orig = [ ]

       self.hide_group = None
       self.reuse_group = None
       self.rewrite_group = None
       self.subst_group = None

       self.start = False
       self.add_used = False
       self.product_types = [ ]
       self.actual_type = "" # local
       self.actual_result = "" # local
       self.predicate_level = 0 # local
       self.new_inx = 0 # local
       # self.line = 1
       # self.nullable = False
       # self.first = [ ]
       # self.follow = [ ]
       # self.rule_inx = [ ]
       # self.start_set = [ ]
       # self.start_rules = [ ]

class Expression (object) :
   def __init__ (self) :
       self.alternatives = [ ]
       # -- continue expr --
       self.continue_expr = False
       self.expr_link = None # selection alternative
       # self.line = 1
       # self.nullable = False
       # self.first = [ ]
       # self.follow = [ ]
       # self.start_set = [ ]

class Alternative (object) :
   def __init__ (self) :
       self.items = [ ]
       self.silent = False
       self.predicate = None
       self.semantic_predicate = None
       self.entry_result = ""
       # -- selection alternative --
       self.select_alt = False # top level alternative in <select> rule
       self.select_nonterm = None
       self.select_independent = False # True => compatibility between select item and rule type is not required
       self.select_ebnf = None
       self.select_branches = [ ] # list of continue alternatives
       # -- continue alternative --
       self.continue_alt = False # alternative in ( ... ) expression in <select> rule
       self.continue_nonterm = None
       self.continue_new = None
       self.continue_ebnf = None
       self.continue_assign = None
       self.continue_link = None # selection alternative
       self.continue_branches = [ ] # list of specific alternatives
       self.new_inx = 0 # index for local variable names
       # -- specific alternative --
       self.specific_alt = False # "set" alternative in continue alternative
       self.specific_assign = None
       self.specific_tags = [ ]
       self.specific_link = None # continue alternative
       # -- return alternative --
       self.return_alt = False # top level alternative in <return> rule
       # self.line = 1
       # self.nullable = False
       # self.first = [ ]
       # self.follow = [ ]
       # self.start_set = [ ]

class Item (object) :
   def __init__ (self) :
       self.current_type = None
       self.current_result = ""
       self.store_result = ""

class Ebnf (Item) :
   def __init__ (self) :
       super (Ebnf, self).__init__ ()
       self.mark = ""
       self.expr = None
       # self.line = 1
       # self.nullable = False
       # self.first = [ ]
       # self.follow = [ ]
       # self.start_set = [ ]

class Nonterminal (Item) :
   def __init__ (self) :
       super (Nonterminal, self).__init__ ()
       self.variable = ""
       self.rule_name = ""
       self.add = False
       self.modify = False
       # -- selection item --
       self.select_item = False # select item
       self.item_link = None # selection alternative (for select item or choose item)
       # -- continue item --
       self.continue_item = False # choose item
       # -- return item --
       self.return_item = False # return item
       # self.rule_ref = None
       # self.line = 1
       # self.nullable = False
       # self.first = [ ]
       # self.start_set = [ ]

class Terminal (Item) :
   def __init__ (self) :
       super (Terminal, self).__init__ ()

       self.text = ""

       self.variable = ""
       self.multiterminal_name = ""

       # self.symbol_ref = None
       # self.line = 1
       # self.nullable = False
       # self.first = [ ]
       # self.start_set = [ ]

# --------------------------------------------------------------------------

"""
additive_expr <choose CmmExpr>:
   multiplicative_expr                ... select_alt
   (                                                     ... select_ebnf
      <new CmmAddExpr:CmmBinaryExpr>  ... continue_alt   ... continue_new
      <store left:CmmExpr>
      (                                                  ... continue_ebnf
         '+' <set kind=addExp> |      ... specific_alt
         '-' <set kind=subExp>                           ... specific_assign
      )
      right:multiplicative_expr
   )* ;
"""

# --------------------------------------------------------------------------

class Directive (Item) :
   def __init__ (self) :
       super (Directive, self).__init__ ()

class Assign (Directive) :
   def __init__ (self) :
       super (Assign, self).__init__ ()
       self.variable = ""
       self.value = ""

class Execute (Directive) :
   def __init__ (self) :
       super (Execute, self).__init__ ()
       self.name = ""
       self.no_param = False

class New (Directive) :
   def __init__ (self) :
       super (New, self).__init__ ()
       self.new_type = ""
       self.new_super_type = ""
       self.store_name = ""
       self.store_type = ""
       # self.tag_name = ""
       # self.tag_value = ""

class Style (Directive) :
   def __init__ (self) :
       super (Style, self).__init__ ()
       self.name = ""

# --------------------------------------------------------------------------

class GroupDecl (object) :
   def __init__ (self) :
       self.group_name = ""
       self.from_type = ""
       self.rewrite_items = False
       self.include_list = [ ]
       self.exclude_list = [ ]
       self.artificial_list = [ ]
       self.priority_list = [ ]
       self.call_list = [ ]

class ArtificialDecl (object) :
   def __init__ (self) :
       self.group_name = ""
       self.call_name = ""
       self.struct_name = ""
       self.func_name = ""

# --------------------------------------------------------------------------

class Struct (object) :
    def __init__ (self) :
        self.type_name = ""
        self.super_type = None
        self.sub_types = [ ]
        self.fields = { }
        self.field_list = [ ]
        self.enums = { }
        self.enum_list = [ ]
        self.tag_name = ""
        self.tag_value = ""
        self.tag_defined = "" # tag_name for whole type hierarchy
        self.specific_tags = [ ] # tag_value(s) for specific alternatives
        self.conv_list = [ ]
        self.tag_low = ""
        self.tag_high = ""
        self.subst_name = "" # Rust
        self.skip_decl = "" # Rust

class Field (object) :
    def __init__ (self) :
        self.field_name = ""
        self.field_type = ""
        self.is_bool = False
        self.is_enum = False
        self.is_utiny = False
        self.is_tiny = False
        self.is_ushort = False
        self.is_short = False
        self.is_uint = False
        self.is_int = False
        self.is_ulong = False
        self.is_long = False
        self.is_str = False
        self.is_ptr = False
        self.is_list = False
        self.struct_type = None # above class type
        self.enum_type = None # type for enumerated field
        self.hidden = False # True ... add to list of fields
        self.composed_name = "" # Rust

class Enum (object) :
    def __init__ (self) :
        self.enum_name = ""
        self.values = [ ]

class Method (object) :
    def __init__ (self) :
        self.method_name = ""
        self.param_type = ""
        self.no_param = False
        self.is_bool = False
        self.rule_name = ""

class Typedef (object) :
    def __init__ (self) :
        self.new_name = ""
        self.old_name = ""

# --------------------------------------------------------------------------

class Options (object) :
   def __init__ (self) :
       self.add = False
       self.modify = False
       self.need_nonterminal = False
       self.leading_required = False

# --------------------------------------------------------------------------

class Grammar (Lexer) :

   def __init__ (self) :
       super (Grammar, self).__init__ ()
       self.rules = [ ]
       self.multiterminals = [ "identifier",
                               "number",
                               "real_number",
                               "character_literal",
                               "string_literal" ]

       self.struct_list = [ ]
       self.struct_dict = { }
       self.enum_item_dict = { }
       self.method_list = [ ]
       self.method_dict = { }
       self.typedef_list = [ ] # typedef / class forward declaration
       self.typedef_dict = { }
       self.header_list = [ ]
       self.literals = { }

       self.collections = [ ]
       self.predicates = [ ]
       self.test_list = [ ]
       self.test_dict = { }

       self.execute_on_begin = { }
       self.execute_on_end = { }
       self.execute_on_begin_no_param = { }
       self.execute_on_entry_no_param = { }
       self.execute_on_fork_no_param = { }
       self.predicate_on_choose = { }
       self.execute_on_choose = { }

       self.group_list = [ ]

       self.check_rules = [ ]

       self.show_tree = False

       self.combine = False

       # self.multiterminal_dict = { }
       # self.keyword_dict = { }
       # self.separator_dict = { }
       #
       # self.symbol_cnt = 0
       # self.symbols = [ ]
       #
       # self.rule_cnt = 0
       # self.rule_dict = { }
       # self.nullableChanged = True
       # self.firstChanged = True
       # self.followChanged = True


   # -- source code position --

   def setPosition (self, item) :
       item.src_file = self.tokenFileInx
       item.src_line = self.tokenLineNum
       item.src_column = self.tokenColNum
       item.src_pos = self.tokenByteOfs

   def rememberPosition (self) :
       return (self.tokenFileInx, self.tokenLineNum, self.tokenColNum, self.tokenByteOfs)

   def storePosition (self, item, value) :
       item.src_file = value [0]
       item.src_line = value [1]
       item.src_column = value [2]
       item.src_pos = value [3]

   def updatePosition (self, item) :
       "set position for error reporting"
       inp = self.file_input
       if inp != None :
          if inp.fileInx == item.src_file :
             inp.lineNum = item.src_line
             inp.colNum = item.src_column
             inp.byteOfs = item.src_pos

   # -- types --

   def declareStruct (self, name, super_type_name = "") :
       if name in self.struct_dict :
          type = self.struct_dict [name]
       else :
          if name in ["bool", "enum", "int", "str", "ptr", "list"] :
             self.error ("Invalid class name")
          type = Struct ()
          type.type_name = name
          type.subst_name = name # Rust
          self.struct_dict [name] = type
          self.struct_list.append (type)

       if super_type_name != "" :
          if type.super_type != None and type.super_type.type_name != super_type_name :
             self.error ("Super type for " + type.type_name + " already defined")
          if type.super_type == None :
             super_type = self.declareStruct (super_type_name)
             type.super_type = super_type
             super_type.sub_types.append (type)

       # if type (with super_type) was already in struct_list, correct struct_list
       if type.super_type != None :
          if self.struct_list.index (type.super_type) > self.struct_list.index (type) :
             self.struct_list.remove (type)
             self.struct_list.append (type)

       return type

   def findField (self, type, field_name) :
       while type != None and field_name not in type.fields :
          type = type.super_type
       field = None
       if type != None :
          field = type.fields [field_name]
       return field

   def declareField (self, type_name, field_name, field_type, is_list = False, hidden = False) :
       type = self.declareStruct (type_name)
       field = self.findField (type, field_name)
       if field != None :
          if field.field_type != field_type or field.is_list != is_list :
             self.error ("Field " + type_name + "." + field_name + " already defined with different type")
          if not hidden :
             field.hidden = False # not hidden => add to list of
       else :
          field = Field ()
          field.field_name = field_name
          field.field_type = field_type
          field.is_bool = (field_type == "bool")
          field.is_utiny = (field_type == "utiny")
          field.is_tiny = (field_type == "tiny")
          field.is_ushort = (field_type == "ushort")
          field.is_short = (field_type == "short")
          field.is_uint = (field_type == "uint")
          field.is_int = (field_type == "int")
          field.is_ulong = (field_type == "ulong")
          field.is_long = (field_type == "long")
          field.is_str = (field_type == "str")
          field.is_enum = field_type in type.enums
          field.is_list = is_list
          field.is_ptr = not is_list and (field_type in self.struct_dict)
          field.hidden = hidden
          field.composed_name = field_name # Rust

          field.struct_type = type
          if field.is_enum :
             field.enum_type = type.enums [field_type]

          type.fields [field_name] = field
          type.field_list.append (field)
       return field

   def declareEnumType (self, type, enum_name) :
       if enum_name in type.enums :
          enum = type.enums [enum_name]
       else :
          enum = Enum ()
          enum.enum_name = enum_name
          type.enums [enum_name] = enum
          type.enum_list.append (enum)
       return enum

   def declareEnumValue (self, enum_type, enum_value) :
       if enum_value not in enum_type.values :
          enum_type.values = enum_type.values + [enum_value]
          self.enum_item_dict [enum_value] = enum_type.enum_name

   def declareFieldValue (self, type_name, field_name, field_value) :
       if field_value == "True" or field_value == "False" :
          self.declareField (type_name, field_name, "bool")
       else :
          class_type = self.declareStruct (type_name)
          field = self.findField (class_type, field_name)
          if field == None :
             enum_name = type_name + field_name.capitalize ()
             enum_type = self.declareEnumType (class_type, enum_name)
             self.declareEnumValue (enum_type, field_value)
             field = self.declareField (type_name, field_name, enum_name)
             field.enum_type = enum_type
          else :
             if field.enum_type == None :
                self.error ("Field " + field.struct_type.type_name + "." + field_name + " is not enumerated")
             self.declareEnumValue (field.enum_type, field_value)

   def declareTagField (self, type_name, field_name, field_value) :
       self.declareFieldValue (type_name, field_name, field_value)

       type = self.struct_dict [type_name]
       if type.tag_name != "" and type.tag_name != field_name :
          self.error ("Struct " + type_name + " already has tag " + type.tag_name)
       type.tag_name = field_name
       type.tag_value = field_value

       self.defineTag (type, field_name)

   def declareSpecificTag (self, type_name, field_name, field_value) :
       type = self.struct_dict [type_name]
       self.defineTag (type, field_name)
       type.specific_tags.append (field_value)

   def defineTag (self, type, field_name) :
       t = type
       stop = False
       while t != None and not stop :
          if t.tag_defined != "" and t.tag_defined != field_name :
             self.error ("Struct " + t.type_name + " already has defined tag " + t.tag_defined)
          t.tag_defined = field_name
          if field_name in type.fields :
             stop = True
          t = t.super_type

       while t != None :
          if t.tag_defined != "" :
             self.error ("Struct " + t.type_name + " already has defined tag " + t.tag_defined)
          t = t.super_type


   def declareMethod (self, method_name, param_type, no_param = False, optional_param = False, is_bool = False) :
       if method_name in self.method_dict :
          m = self.method_dict [method_name]
          if m.param_type == "" :
             m.param_type = param_type
       else :
          m = Method ()
          m.method_name = method_name
          m.param_type = param_type
          m.is_bool = is_bool

          self.method_dict [method_name] = m
          self.method_list.append (m)

       if no_param:
          m.param_type = ""
          m.no_param = True

       if optional_param:
          if m.param_type == "" :
             m.no_param = True
          else :
             m.no_param = False

   # -- scan rule types --

   def scanRules (self) :
       self.rule_dict = { }
       for rule in self.rules :
           self.updatePosition (rule)
           if rule.name in self.rule_dict :
              self.error ("Rule " + rule.name + " already defined")
           self.rule_dict [rule.name] = rule

       for rule in self.rules :
           self.updatePosition (rule)
           if rule.rule_type != "" :
              rule.type_ref = self.declareStruct (rule.rule_type, rule.super_type) # type reference
           if rule.tag_name != "" :
              self.declareTagField (rule.rule_type, rule.tag_name, rule.tag_value)
           if rule.store_name != "" :
              self.declareField (rule.rule_type, rule.store_name, rule.store_type)

       for rule in self.rules :
           self.updatePosition (rule)
           name = rule.store_from_name
           if name != "" :
              if name not in self.rule_dict :
                 self.error ("Unknown rule: " + name)
              rule.store_from = self.rule_dict [name]

       for rule in self.rules :
           self.scanRule (rule)

       for rule in self.rules :
           if rule.rule_type != "" :
              "complete tag_name and tag_value"
              rule.tag_name = rule.type_ref.tag_name
              rule.tag_value = rule.type_ref.tag_value

   def scanRule (self, rule) :
       self.updatePosition (rule)
       rule.actual_type = rule.rule_type
       rule.actual_result = "result"
       self.scanExpression (rule, rule.expr)
       rule.actual_type = ""

   def scanExpression (self, rule, expr) :
       self.updatePosition (expr)
       if expr.continue_expr :
          save_type = rule.rule_type
          save_result = rule.actual_result
       for alt in expr.alternatives :
          if expr.continue_expr : # begin with same entry result
             rule.rule_type = save_type
             rule.actual_result = save_result
          self.scanAlternative (rule, alt)
       if expr.continue_expr : # follow with rule result
          rule.actual_type = rule.rule_type
          rule.actual_result = "result"

   # def add_product_type (self, rule, type_name) :
       # if type_name not in rule.product_types :
       #    rule.product_types.append (type_name)

   # def add_specific_tag (self, alt, value) :
       # if value not in alt.specific_tags :
       #    alt.specific_tags.append (value)

   def typeTag (self, type_name) :
       result = ""
       if type_name in self.struct_dict :
          type = self.struct_dict [type_name]
          while type != None and result == "" :
             result = type.tag_defined
             type = type.super_type
       # print ("typeTag", type_name, result)
       return result

   def scanAlternative (self, rule, alt) :
       self.updatePosition (alt)
       if alt.predicate != None :
          self.scanExpression (rule, alt.predicate) # set rule_ref for nonterminals
       alt.entry_result = rule.actual_result
       for item in alt.items :
           item.current_type = rule.actual_type
           item.current_result = rule.actual_result

           if isinstance (item, Ebnf) :
              self.scanExpression (rule, item.expr)
           elif isinstance (item, Nonterminal) :
              self.updatePosition (item)
              name = item.rule_name
              if name not in self.rule_dict:
                 self.error ("Unknown rule: " + name)
              item.rule_ref = self.rule_dict [name]

              if item.select_item :
                 if alt.select_independent :
                    rule.actual_type = item.rule_ref.rule_type
                    rule.actual_result = "result" + str (rule.new_inx)
                    rule.new_inx = rule.new_inx + 1
                    alt.new_inx = rule.new_inx
                    item.current_type = rule.actual_type
                    item.current_result = rule.actual_result
                 # self.add_product_type (rule, item.rule_ref.rule_type)

              if item.continue_item :
                 item.store_result = rule.actual_result # store parameter
                 rule.actual_type = rule.rule_type
                 rule.actual_result = "result"
                 item.current_type = rule.actual_type
                 item.current_result = rule.actual_result
                 # self.add_product_type (rule, item.rule_ref.rule_type)

              if item.variable != "" :
                 self.declareField (rule.actual_type, item.variable, item.rule_ref.rule_type)
              if item.add :
                 self.declareField (rule.actual_type, "items", item.rule_ref.rule_type, is_list = True)

           elif isinstance (item, Terminal) :
              if item.variable != "" :
                 self.declareField (rule.actual_type, item.variable, "str")

           elif isinstance (item, Assign) :
              self.declareFieldValue (rule.actual_type, item.variable, item.value)
              if alt.specific_alt :
                 if alt.specific_assign == None :
                    # print ("SPECIFIC", rule.actual_type, item.variable, item.value)
                    # print ("specific assign")
                    alt.specific_assign = item
                    if item.variable == self.typeTag (rule.actual_type) :
                       self.declareSpecificTag (rule.actual_type, item.variable, item.value)
                       # self.add_specific_tag (alt, item.value)
              if alt.continue_alt :
                 if alt.continue_assign == None :
                    if item.variable == self.typeTag (rule.actual_type) :
                       alt.continue_assign = item
                       self.declareTagField (rule.actual_type, item.variable, item.value)

           elif isinstance (item, Execute) :
              self.declareMethod (item.name, rule.actual_type, no_param = item.no_param)

           elif isinstance (item, New) :
              self.declareStruct (item.new_type, item.new_super_type)
              rule.actual_type = item.new_type
              rule.actual_result = "result" + str (rule.new_inx)
              rule.new_inx = rule.new_inx + 1
              alt.new_inx = rule.new_inx
              item.current_type = rule.actual_type
              item.current_result = rule.actual_result
              # self.add_product_type (rule, item.new_type)
              # if rule.tag_name != "" :
              #    self.declareTagField (rule.actual_type, rule.tag_name, rule.tag_value)
              if item.store_name != "" :
                 self.declareField (rule.actual_type, item.store_name, item.store_type)

       "end of loop"
       if alt.select_alt :
          rule.actual_type = rule.rule_type
          rule.actual_result = "result"

   # -- read directive --

   """
   def skipDirective (self) :
       while self.isSeparator ('<') :
          self.nextToken ()
          while not self.isEndOfSource () and not self.isSeparator ('>') :
             self.nextToken ()
          if self.isEndOfSource () :
             self.error ("Unfinished directive")
          self.nextToken () # skip '>'
   """

   # -- global directives - execute method --

   def addMethod (self, func_dict, rule_name, method_name) :
       if rule_name in func_dict :
          self.error ("Cannot register " + method_name + ", rule " + rule_name + "has already registered method " + func_dict [rule_name])
       func_dict [rule_name] = method_name
       self.check_rules.append (rule_name)

   def rememberMethod (self, func_dict, method_name) :
       cont = True
       while cont :
          rule_name = self.readIdentifier ("Rule identifier expected")
          self.addMethod (func_dict, rule_name, method_name)
          cont = False
          if self.isSeparator (',') :
             self.nextToken ()
             cont = True

   def modifyMethod (self, func_name, rule_name) :
       if func_name != "" :
          func = self.method_dict [func_name]
          func.rule_name = rule_name

   def completeMethods (self) :
       for func in self.method_list :
           if func.rule_name != "" :
              rule = self.rule_dict [func.rule_name]
              func.param_type = rule.rule_type

   def rememberMethods (self, begin_func, end_func) :
       cont = True
       cnt = 0
       while cont :
          rule_name = self.readIdentifier ("Rule identifier expected")
          if begin_func != "" :
             self.addMethod (self.execute_on_begin, rule_name, begin_func)
          if end_func != "" :
             self.addMethod (self.execute_on_end, rule_name, end_func)
          cont = False
          cnt = cnt + 1
          if self.isSeparator (',') :
             self.nextToken ()
             cont = True
       if cnt == 1 :
          self.modifyMethod (begin_func, rule_name)
          self.modifyMethod (end_func, rule_name)

   def readMethod (self, no_param = False, optional_param = False, is_bool = False) :
       func_name = self.readIdentifier ("Method identifier expected")
       param_type = ""
       if not no_param and self.isSeparator ("(") :
          self.nextToken ()
          if not self.isSeparator (")") :
             param_type = self.readIdentifier ("Type identifier expected")
          self.checkSeparator (")")
       self.declareMethod (func_name, param_type, no_param = no_param, optional_param = optional_param, is_bool = is_bool)
       return func_name

   def executeOnBeginEnd (self) :
       begin_func = ""
       if not self.isSeparator (',') :
          begin_func = self.readMethod ()
       self.checkSeparator (',')

       end_func = ""
       if not self.isSeparator (':') :
          end_func = self.readMethod ()
       self.checkSeparator (':')

       self.rememberMethods (begin_func, end_func)

   def executeOnBegin (self) :
       begin_func = self.readMethod ()
       self.checkSeparator (':')
       self.rememberMethods (begin_func, "")

   def executeOnEnd (self) :
       end_func = self.readMethod ()
       self.checkSeparator (':')
       self.rememberMethods ("", end_func)

   def executeOnChoose (self) :
       func_name = self.readMethod ()
       self.checkSeparator (':')
       self.rememberMethod (self.execute_on_choose, func_name)

   def executeOnBeginNoParam (self) :
       func_name = self.readMethod (no_param = True)
       self.checkSeparator (':')
       self.rememberMethod (self.execute_on_begin_no_param, func_name)

   def executeOnEntryNoParam (self) :
       func_name = self.readMethod (no_param = True)
       self.checkSeparator (':')
       self.rememberMethod (self.execute_on_entry_no_param, func_name)

   def executeOnForkNoParam (self) :
       func_name = self.readMethod (no_param = True)
       self.checkSeparator (':')
       self.rememberMethod (self.execute_on_fork_no_param, func_name)

   def predicateOnChoose (self) :
       func_name = self.readMethod (is_bool = True)
       self.checkSeparator (':')
       self.rememberMethod (self.predicate_on_choose, func_name)

   # -- header --

   def headerDirective (self) :
       name = self.readString ("String with header name expected")
       self.header_list.append (name)

   # -- typedef / class forward declaration --

   def typeDirective (self) :
       type = Typedef ()
       type.new_name = self.readIdentifier ("Type identifier expected")
       if self.isSeparator ('=') :
          self.checkSeparator ('=')
          type.old_name = self.readIdentifier ("Type identifier expected")
       self.typedef_list.append (type)
       self.typedef_dict [type.new_name] = type
       if self.isSeparator (';') :
          self.nextToken ()

   # -- structures --

   def enumDeclaration (self, class_type) :
       self.checkKeyword ("enum")
       type_name = self.readIdentifier ("Enum type identifier expected")
       enum_type = self.declareEnumType (class_type, type_name)
       if self.isSeparator ('{') :
          self.nextToken ()
          if not self.isSeparator ('}') :
             stop = False
             while not stop :
                item_name = self.readIdentifier ()
                self.declareEnumValue (enum_type, item_name, class_type)
                if self.isSeparator (',') :
                   self.nextToken ()
                else :
                   stop = True
          self.checkSeparator ('}')
       # if self.isSeparator (';') :
       #    self.nextToken ()


   def structDirective (self) :
       type_name = self.readIdentifier ("Type identifier expected")
       super_type = ""
       if self.isSeparator (':') :
          self.nextToken ()
          super_type = self.readIdentifier ("Super-type identifier expected")
       class_type = self.declareStruct (type_name, super_type)

       if self.isSeparator (',') :
          self.nextToken ()
          tag_name = self.readIdentifier ("Tag identifier expected")
          self.checkSeparator ('=')
          tag_value = self.readIdentifier ("Tag value expected")
          self.declareTagField (type_name, tag_name, tag_value)

       if self.isSeparator ('{') :
          self.nextToken ()
          while not self.isSeparator ('}') :
             if self.isKeyword ("enum") :
                self.enumDeclaration (class_type)
             else :
                is_list = False;
                if self.isKeyword ("list") :
                   self.nextToken ()
                   is_list = True
                field_type = self.readIdentifier ("Type identifier expected")
                compound = True
                if self.isSeparator (":") :
                   self.nextToken ()
                   self.checkSeparator (":")
                   field_type = field_type + "::" + self.readIdentifier ("Type from namespace expected")
                   compound = True
                if self.isSeparator ("*") :
                   self.nextToken ()
                   if not compound and field_type not in self.typedef_dict :
                      self.declareStruct (field_type)
                field_name = self.readIdentifier ("Field identifier expected")
                self.declareField (type_name, field_name, field_type, is_list = is_list, hidden = True)
             self.checkSeparator (';')
          self.checkSeparator ('}')
       # if self.isSeparator (';') :
       #    self.nextToken ()

   # -- groups --

   def readRuleList (self) :
       result = [ ]

       self.checkSeparator ('(')

       name = self.readIdentifier ("Rule identifier expected")
       result.append (name)
       self.check_rules.append (name)

       while self.isSeparator (',') :
          self.nextToken ()
          name = self.readIdentifier ("Rule identifier expected")
          result.append (name)
          self.check_rules.append (name)

       self.checkSeparator (')')

       return result

   def readStructureName (self, parenthesis = False) :
       if parenthesis :
          self.checkSeparator ('(')
       name = self.readIdentifier ("Structure identifier expected")
       if parenthesis :
          self.checkSeparator (')')

       if name not in self.struct_dict :
          self.error ("Unknown structure " + name)

       return name

   def readGroup (self) :
       name = self.readIdentifier ("Group identifier expected")

       group = None
       for item in self.group_list :
          if item.group_name == name :
             group = item

       if group == None :
          self.error ("Unknown group " + name)

       return group

   def groupDirective (self) :
       " < group expression reuse ( CmmExpr ) > "
       " < group statement  rewrite ( CmmStat ) include (stat, declaration) exclude ( nested_stat ) > "
       group = GroupDecl ()
       group.group_name = self.readIdentifier ("Group identifier expected")

       if self.isKeyword ("rewrite") :
          self.nextToken ()
          group.from_type = self.readStructureName (parenthesis = True)
          group.rewrite_items = True

       elif self.isKeyword ("reuse") :
          self.nextToken ()
          group.from_type = self.readStructureName (parenthesis = True)

       while not self.isSeparator ('>') :
          if self.isKeyword ("include") :
             self.nextToken ()
             group.include_list = self.readRuleList ()

          elif self.isKeyword ("exclude") :
             self.nextToken ()
             group.exclude_list = self.readRuleList ()

          elif self.isKeyword ("priority"):
             self.nextToken ()
             group.priority_list = self.readRuleList ()

          elif group.rewrite_items :
             if self.isKeyword ("call") :
                self.nextToken ()
                group.call_list = self.readRuleList ()

          else :
             self.error ("include, exclude, priority or call expected")

       if self.isSeparator (';') :
          self.nextToken ()

       self.group_list.append (group)

   def artificialDirective (self) :
       " < artificial statement, text_stat, CmmTextStat > "
       artificial = ArtificialDecl ()
       group = self.readGroup ()
       group.artificial_list.append (artificial)
       self.checkSeparator (',')
       artificial.call_name = self.readIdentifier ("Sub-rule identifier expected")
       self.checkSeparator (',')
       artificial.struct_name = self.readStructureName ()
       if self.isSeparator (',') :
          self.checkSeparator (',')
          artificial.func_name = self.readIdentifier ("Function name expected")
       if self.isSeparator (';') :
          self.nextToken ()


   # -- literals --

   def literalDirective (self) :
       " < literals LPAREN  : '(' ; RPAREN : ')' ; > "
       while not self.isSeparator ('>') :
          literal_name = self.readIdentifier ("Identifier expected")
          self.checkSeparator (':')
          if self.isCharacter () :
             literal_text = self.readCharacter ()
          else :
             literal_text = self.readString ()
          self.checkSeparator (';')
          self.literals [literal_text] = literal_name

   # -- global directives --

   def globalDirective (self) :
       while self.isSeparator ('<') :
          self.nextToken ()
          if self.isKeyword ("header") :
             self.nextToken ()
             self.headerDirective ()
          elif self.isKeyword ("type") :
             self.nextToken ()
             self.typeDirective ()
          elif self.isKeyword ("enum") :
             self.nextToken ()
             self.enumDirective ()
          elif self.isKeyword ("struct") :
             self.nextToken ()
             self.structDirective ()
          elif self.isKeyword ("execute_on_begin_end") :
             self.nextToken ()
             self.executeOnBeginEnd ()
          elif self.isKeyword ("execute_on_begin") :
             self.nextToken ()
             self.executeOnBegin ()
          elif self.isKeyword ("execute_on_end") :
             self.nextToken ()
             self.executeOnEnd ()
          elif self.isKeyword ("execute_on_begin_no_param") :
             self.nextToken ()
             self.executeOnBeginNoParam ()
          elif self.isKeyword ("execute_on_entry_no_param") :
             self.nextToken ()
             self.executeOnEntryNoParam ()
          elif self.isKeyword ("execute_on_fork_no_param") :
             self.nextToken ()
             self.executeOnForkNoParam ()
          elif self.isKeyword ("predicate_on_choose") :
             self.nextToken ()
             self.predicateOnChoose ()
          elif self.isKeyword ("execute_on_choose") :
             self.nextToken ()
             self.executeOnChoose ()
          elif self.isKeyword ("group") :
             self.nextToken ()
             self.groupDirective ()
          elif self.isKeyword ("artificial") :
             self.nextToken ()
             self.artificialDirective ()
          elif self.isKeyword ("literals") :
             self.nextToken ()
             self.literalDirective ()
          else :
             self.error ("Unknown global directive")
          self.checkSeparator ('>')

   # -- rule directive --

   def ruleDirective (self, rule) :
       if self.isSeparator ('<') :
          self.nextToken ()

          if not self.isSeparator ('>') :

             if self.isKeyword ("new") :
                rule.rule_mode = "new"
                self.nextToken ()
             elif self.isKeyword ("modify") :
                rule.rule_mode = "modify"
                self.nextToken ()
             elif  self.isKeyword ("return") :
                rule.rule_mode = "return"
                self.nextToken ()
             elif self.isKeyword ("select") or self.isKeyword ("choose"):
                rule.rule_mode = "select"
                self.nextToken ()
             else :
                rule.rule_mode = "new"

             rule.rule_type = self.readIdentifier ("Type name expected")

             if self.isSeparator (':') :
                self.nextToken ()
                rule.super_type = self.readIdentifier ("Super-type expected")

             if self.isSeparator (',') :
                self.nextToken ()
                rule.tag_name = self.readIdentifier ("Tag identifier expected")
                self.checkSeparator ('=')
                rule.tag_value = self.readIdentifier ("Tag value expected")
                if rule.rule_mode != "new" :
                   self.error ("Tag only allowed for \"new\" mode")

          self.checkSeparator ('>')

       "second < > directive"
       if self.isSeparator ('<') :
          self.nextToken ()
          if self.isKeyword ("start") :
             rule.start = True
             self.nextToken ()
          else :
             self.error ("Unknown directive")
          self.checkSeparator ('>')

   # -- item directive --

   def itemDirective (self, rule, alt, opt) :
       if self.isKeyword ("new") :
          self.nextToken ()
          # add New to this alternative
          item = New ()
          item.new_type = self.readIdentifier ("Type identifier expected")
          self.checkSeparator (':')
          item.new_super_type = self.readIdentifier ("Type identifier expected")
          alt.items.append (item)
          if not alt.continue_alt :
             self.error ("New allowed only in <continue> alternative")
          if alt.continue_new != None :
             self.error ("New for this alternative already defined")
          alt.continue_new = item
          opt.leading_required = False
          # if self.isSeparator (',') :
          #    self.nextToken ()
          #    rule.tag_name = self.readIdentifier ("Tag identifier expected")
          #    self.checkSeparator ('=')
          #    rule.tag_value = self.readIdentifier ("Tag value expected")

       elif self.isKeyword ("store") :
          self.nextToken ()
          name = self.readIdentifier ("Field identifier expected")
          self.checkSeparator (':')
          type = self.readIdentifier ("Type identifier expected")
          if alt.continue_new != None :
             alt.continue_new.store_name = name
             alt.continue_new.store_type = type
          else :
             rule.store_name = name
             rule.store_type = type
          if self.isSeparator (':') :
             self.checkSeparator (':')
             name = self.readIdentifier ("Rule identifier expected")
             rule.store_from_name = name

       elif self.isKeyword ("set") :
          self.nextToken ()
          variable = self.readIdentifier ("Variable identifier expected")
          self.checkSeparator ('=')
          value = self.readIdentifier ("Value expected")
          if value == "true" :
             value = "True"
          if value == "false" :
             value = "False"
          # add Assign to this alternative
          item = Assign ()
          item.variable = variable
          item.value = value
          alt.items.append (item)

       elif self.isKeyword ("add") :
          self.nextToken ()
          opt.add = True
          opt.need_nonterminal = True

       elif self.isKeyword ("modify") :
          self.nextToken ()
          opt.modify = True
          opt.need_nonterminal = True

       elif self.isKeyword ("execute") :
          self.nextToken ()
          name = self.readMethod ()
          # add Execute to this alternative
          item = Execute ()
          item.name = name
          alt.items.append (item)

       elif self.isKeyword ("execute_no_param") :
          self.nextToken ()
          name = self.readMethod (no_param = True)
          # add Execute to this alternative
          item = Execute ()
          item.name = name
          item.no_param = True
          alt.items.append (item)

       elif self.isKeyword ("silent") :
          self.nextToken ()
          # set silent field in this alternative
          alt.silent = True

       elif ( self.isKeyword ("indent") or
              self.isKeyword ("unindent") or
              self.isKeyword ("no_space") or
              self.isKeyword ("new_line") or
              self.isKeyword ("empty_line") or
              self.isKeyword ("no_empty_line") ) :
          name = self.tokenText
          self.nextToken ()
          # add Style to this alternative
          item = Style ()
          item.name = name
          alt.items.append (item)
       else :
          self.error ("Unknown directive " + self.tokenText)

   # -- rules --

   def parseRules (self) :
       while not self.isEndOfSource () :
          self.globalDirective ()
          if not self.isEndOfSource () :
             self.parseRule ()
       self.scanRules () # rule types

       for name in self.check_rules :
           if name not in self.rule_dict :
              self.error ("Unknown rule used in directive: " + name)

       self.completeMethods ()

   def parseRule (self) :
       rule = Rule ()

       rule.name = self.readIdentifier ("Rule identifier expected")
       self.setPosition (rule)

       self.ruleDirective (rule)
       self.checkSeparator (':')

       rule.expr = self.parseExpression (rule, top_alt = True, sel_alt = None, cnt_alt = None)

       self.checkSeparator (';')

       if self.combine :
          if rule.name in self.rule_dict :
             old = self.rule_dict [rule.name]
             inx = self.rules.index (old)
             self.rules [inx] = rule
             self.rule_dict [rule.name] = rule
          else :
             self.rules.append (rule)
       else :
          self.rules.append (rule)

   # -- expression --

   def parseExpression (self, rule, top_alt, sel_alt, cnt_alt) :
       expr = Expression ()
       self.setPosition (expr)

       if sel_alt != None :
          expr.continue_expr = True
          expr.expr_link = sel_alt

       alt = self.parseAlternative (rule, top_alt, sel_alt, cnt_alt)
       expr.alternatives.append (alt)

       while self.isSeparator ('|') :
          self.nextToken ()

          alt = self.parseAlternative (rule, top_alt, sel_alt, cnt_alt)
          expr.alternatives.append (alt)

       return expr

   def parseAlternative (self, rule, top_alt, sel_alt, cnt_alt) :
       alt = Alternative ()
       self.setPosition (alt)
       opt = Options ()

       if top_alt :
          if rule.rule_mode == "select" :
             alt.select_alt = True
             opt.leading_required = True
          if rule.rule_mode == "return":
             alt.return_alt = True
             opt.leading_required = True

       if sel_alt != None :
          alt.continue_alt = True
          alt.continue_link = sel_alt
          opt.leading_required = True
          sel_alt.select_branches.append (alt)

       if cnt_alt != None :
          alt.specific_alt = True
          alt.specific_link = cnt_alt
          cnt_alt.continue_branches.append (alt)

       nxt_sel = None
       if alt.select_alt :
          nxt_sel = alt # select alternative for inner alternatives

       nxt_cnt = None
       if alt.continue_alt :
          nxt_cnt = alt # # continue alternative for inner alternatives

       while not self.isSeparator ('|') and not self.isSeparator (')') and not self.isSeparator (']') and not self.isSeparator (';') :

          if self.token == self.identifier :
             item = self.parseNonterminal (rule, alt, opt)
             alt.items.append (item)

          elif self.token == self.character_literal or self.token == self.string_literal :
             if opt.need_nonterminal :
                self.error ("Nonterminal expected")
             item = self.parseTerminal ()
             alt.items.append (item)

          elif self.isSeparator ('(') :
             if rule.predicate_level == 0 :
                if opt.need_nonterminal :
                   self.error ("nonterminal expected")
                if opt.leading_required :
                   self.error ("missing nonterminal (in the beginning of sub-expression)")
             ebnf = self.parseEbnf (rule, nxt_sel, nxt_cnt)
             nxt_sel = None # only first ebnf is choose/continue
             nxt_cnt = None

             if alt.select_alt and alt.select_ebnf == None : # first ebnf after selecttion ite
                alt.select_ebnf = ebnf
                if ebnf.mark == "" or ebnf.mark == "+" :
                   alt.select_independent = True

             if alt.continue_alt and alt.continue_ebnf == None : # first ebnf after selecttion ite
                alt.continue_ebnf = ebnf

             alt.items.append (ebnf)

          elif self.isSeparator ('[') :
             if alt.predicate != None :
                self.error ("Syntactic predicate for this alternative already defined")
             self.checkSeparator ('[')
             rule.predicate_level = rule.predicate_level + 1
             alt.predicate = self.parseExpression (rule, top_alt = False, sel_alt = None, cnt_alt = None)
             rule.predicate_level = rule.predicate_level - 1
             self.checkSeparator (']')
             self.checkSeparator ('=')
             self.checkSeparator ('>')

          elif self.isSeparator ('{') :
             self.nextToken ()
             if alt.semantic_predicate != None :
                self.error ("Semantic predicate for this alternative already defined")
             alt.semantic_predicate = self.readMethod (is_bool = True)
             self.checkSeparator ('}')
             self.checkSeparator ('?')

          elif self.isSeparator ('<') :
             self.nextToken ()
             self.itemDirective (rule, alt, opt)
             self.checkSeparator ('>')

          else :
             self.error ("Unknown grammar item")

          # inside while loop

       # after while lopp
       if rule.predicate_level == 0 :
          if opt.need_nonterminal :
             self.error ("Nonterminal expected")

          if opt.leading_required :
             self.error ("Missing nonterminal (for rule with select attribute)")

       return alt

   def parseEbnf (self, rule, sel_alt, cnt_alt) :
       item = Ebnf ()

       self.setPosition (item)
       self.checkSeparator ('(')
       item.expr = self.parseExpression (rule, top_alt = False, sel_alt = sel_alt, cnt_alt = cnt_alt)
       self.checkSeparator (')')

       if self.isSeparator ('?') :
          item.mark = '?'
          self.nextToken ()
       elif self.isSeparator ('+') or self.isSeparator ('@') :
          item.mark = '+'
          self.nextToken ()
       elif self.isSeparator ('*') :
          item.mark = '*'
          self.nextToken ()

       return item

   def parseNonterminal (self, rule, alt, opt) :

       pos = self.rememberPosition ()
       variable = ""
       rule_name = self.readIdentifier ()

       if self.isSeparator (':') :
          self.nextToken ()
          variable = rule_name
          rule_name = self.readIdentifier ("Rule identifier expected")

       if rule_name in self.multiterminals :
          item = Terminal ()
          self.storePosition (item, pos)
          item.variable = variable
          item.multiterminal_name = rule_name
          if opt.add or opt.modify :
             self.error ("<add> or <modify> not allowed before multiterminal")
          if rule.predicate_level == 0 :
             if opt.leading_required :
                self.error ("Missing nonterminal (for rule with select or choose attribute) (and multiterminal found)")
       else :
          item = Nonterminal ()
          self.storePosition (item, pos)

          item.variable = variable
          item.rule_name = rule_name

          item.add = opt.add
          item.modify = opt.modify

          opt.need_nonterminal = False

          if opt.leading_required  :
             opt.leading_required = False
             if alt.select_alt :
                item.select_item = True
                item.item_link = alt
                alt.select_nonterm = item
             if alt.continue_alt :
                item.continue_item = True
                alt.continue_nonterm = item
                item.item_link = alt
             if alt.return_alt :
                item.return_item = True
             if item.variable != "" :
                if rule.predicate_level == 0 :
                   self.error ("Variable identifier not allowed for first nonterminal (in rule with select or choose attribute)")

          if item.add or item.modify :
             if item.variable != "" :
                self.error ("Variable identifier not allowed after <add> or <modify> directive")

          if item.add :
             rule.add_used = True

       opt.add = False
       opt.modify = False
       return item

   def parseTerminal (self) :
       item = Terminal ()
       self.setPosition (item)
       if self.token != self.character_literal and self.token != self.string_literal :
          self.error ("string expected")
       item.text = self.tokenText
       self.nextToken ()
       return item

   # -- combine with another grammar --

   def combineRules (self) :
       self.combine = True
       while not self.isEndOfSource () :
          self.parseRule ()
       self.scanRules () # rule types

# --------------------------------------------------------------------------

if __name__ == "__main__" :
    grammar = Grammar ()
    grammar.openFile ("pas.g")
    grammar.parseRules ()
    for rule in grammar.rules :
       print (rule.name)

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
