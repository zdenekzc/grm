
# c2cpp.py

from __future__ import print_function

import os
from output import Output

from util import use_qt4, use_qt5, use_qt6
from input import quoteString
from code_base import *
from cmm_parser import *
from cmm_product import Product

# --------------------------------------------------------------------------

class ToCpp (Product) :

   python = False # C++ output — mirrors ToPy.python = True in c2py.py,
                  # cmm_set.py checks output.python for . vs ->

   normal_style = 0
   class_style = 1 # class member declarations
   init_style = 2 # code for construcor / intialize function
   global_style = 3 # global declaration

   def __init__ (self) :
       super (ToCpp, self).__init__ ()

       self.compiler = None
       self.builder = None
       self.win = None

       self.class_stack = [ ]
       self.only_name_stack = [ False ]
       self.style_stack = [ self.normal_style ]

   def send_program (self, decl_list) :
       self.send_declaration_list (decl_list)

   def comment (self, txt) :
       self.style_empty_line ()
       # self.style_new_line ()
       self.send ("//")
       self.send (txt)
       self.style_new_line ()

   def put_dot (self) :
       self.style_no_space ()
       self.send (".")
       self.style_no_space ()

   def put_arrow (self) :
       self.style_no_space ()
       self.send ("->")
       self.style_no_space ()

   def put_colons (self) :
       self.style_no_space ()
       self.send ("::")
       self.style_no_space ()

   # -----------------------------------------------------------------------

   def put_obj (self, text, obj) :
       self.addUsage (text, obj)

   def put_name (self, obj) :
       ref = getattr (obj, "item_decl", None)
       ref = getattr (obj, "item_ref", ref)
       if ref == None :
          ref = obj
       if getattr (ref, "mod_rename", None) != None :
          self.put_obj (ref.mod_rename, ref)
       else :
          self.put_obj (obj.item_name, ref)

   # -----------------------------------------------------------------------

   def send_nested_stat (self, stat) :
       if stat.kind == compoundStat :
          self.style_new_line ()
          self.send_stat (stat)
       else :
          self.style_indent ()
          self.send_stat (stat)
          self.style_unindent ()

   def send_tail_stat (self, stat) :
       if stat.kind == ifStat :
          self.send_stat (stat) # if statement without indentation
       else :
          self.send_nested_stat (stat)

   # def send_cpp_only_stat (self, stat) :
   #     self.send_stat (stat.inner_stat)

   # def send_python_only_stat (self, stat) :
   #     pass

   # -----------------------------------------------------------------------

   def get_expr_value (self, expr) :
       return getattr (expr, "item_value", None)

   def send_expr (self, expr) :
       done = False

       decl = getattr (expr, "item_decl", None)

       "true or false constants"
       value = self.get_expr_value (expr)
       if value != None :
          if isinstance (value, bool) :
             if value == True :
                self.send ("true")
             else :
                self.send ("false")
             done = True

       " && "
       if expr.kind == logAndExpr :
          left = self.get_expr_value (expr.left)
          if left == True :
             self.send_expr (expr.right)
             done = True
          elif left == False :
             self.send ("false")
             done = True

       " || "
       if expr.kind == logOrExpr :
          left = self.get_expr_value (expr.left)
          if left == False :
             self.send_expr (expr.right)
             done = True
          elif left == True :
             self.send ("true")
             done = True

       "simple identifier"
       if expr.kind == simpleName and not done :
          if decl != None :
             "copy loop parameter"
             expr.item_value = self.get_expr_value (expr.item_decl)

          if getattr (expr, "name_owner", None) != None :
             scope = expr.name_owner
             if scope != None and (scope.owner_obj != None or scope.owner_expr != None):
                if scope.owner_parenthesis :
                   self.send ('(')
                if scope.owner_obj != None :
                   self.put_name (scope.owner_obj)
                else :
                   self.send_expr (scope.owner_expr)
                if scope.owner_parenthesis :
                   self.send (')')
                if scope.owner_arrow :
                   self.put_arrow ()
                else :
                   self.put_dot ()

          ref = getattr (expr, "item_ref", decl)
          if getattr (ref, "mod_rename", None) != None :
             self.put_obj (ref.mod_rename, ref)
             done = True
          else :
             self.put_obj (expr.id, ref)
             done = True

       "function call"
       if expr.kind == callExpr:
          if getattr (expr, "skip_code", False) :
             done = True
          else :
             decl = getattr (expr.left, "item_decl", None)
             if decl != None :
                if getattr (decl, "mod_call", None) != None :
                   # print ("MOD_CALL", decl.item_qual)
                   # self.send ("// MOD_CALL (" + decl.item_qual + ");")
                   call = decl.mod_call
                   call (self, expr)
                   done = True
                   expr.skip_semicolon = True

       if not done :
          super (ToCpp, self). send_expr (expr)

   # -----------------------------------------------------------------------

   def send_if_stat (self, stat) :
       done = False

       value = self.get_expr_value (stat.cond)
       if value == True :
          self.send_stat (stat.then_stat)
          # self.style_new_line ()
          done = True
       elif value == False :
          if stat.else_stat != None :
             self.send_stat (stat.else_stat)
             # self.style_new_line ()
          done = True

       if not done :
          super (ToCpp, self). send_if_stat (stat)

   def send_for_stat (self, stat) :
       done = False

       target = None
       if stat.from_expr != None :
          if stat.from_expr.kind == simpleStat :
             expr = stat.from_expr.inner_expr
             # print ("EXPR", expr)
             if getattr (expr, "item_decl", None) != None :
                target = expr.item_decl
                # print ("TARGET", target.item_name, target)
          elif stat.from_expr.kind == simpleDecl :
             target = stat.from_expr.items [0]
             # print ("TARGET", target.item_name, target)

       if stat.iter_expr != None :
          if stat.iter_expr.kind == commaExpr :
             self.custom_for_stat (stat, target)
             done = True
          else :
             value = self.get_expr_value (stat.iter_expr)
             if value != None:
                for item in value :
                   if target != None :
                      target.item_value = item
                   self.style_new_line ()
                   self.send_stat (stat.body)
                done = True

       if not done :
          super (ToCpp, self). send_for_stat (stat)

   def custom_for_stat (self, stat, target) :
       pass

   # -----------------------------------------------------------------------

   def custom_with_stat (self, stat) :
       pass

   # -----------------------------------------------------------------------

   def send_simple_stat (self, stat) :

       if stat.body != None :
          self.custom_with_stat (stat)
       else :
          expr = stat.inner_expr
          self.send_expr (expr)
          if not getattr (expr, "skip_semicolon", False) :
             self.send (";")

   def send_declaration_list (self, stat) :
       for item in stat.items :
           self.custom_statement (item)

   def send_declaration (self, decl) :
       self.custom_statement (decl)

   def custom_statements (self, block) :
       for item in block :
           self.custom_statement (item)

   def custom_statement (self, stat) :
       self.send_stat (stat)
       self.style_new_line ()

   def send_compound_stat (self, stat) :
       self.send ("{")
       self.style_indent ()
       self.custom_statements (stat.items)
       self.style_unindent ()
       self.send ("}")

   # -----------------------------------------------------------------------

   def send_simple_declaration (self, simple_decl) :
       for simple_item in simple_decl.items :
           if not simple_item.skip_code :
              if simple_item.is_function :
                 self.custom_function (simple_item)
              else :
                 self.custom_variable (simple_item)

   def custom_variable (self, var) :

       self.send_expr (var.item_simple_decl.type_spec)
       self.simple_item_declarator (var)

       if var.init != None :
          self.send_initializer (var.init)

       self.send (";")

   def simple_item_declarator (self, simple_item) :
       self.only_name_stack.append (True) # print only short, unqualified names
       declarator = simple_item.declarator
       if declarator.kind == functionDeclarator and declarator.inner_declarator.kind == emptyDeclarator :
       # if declarator.kind == constructorDeclarator :
          self.send_constructor_declarator (declarator)
       else :
          self.send_common_declarator (declarator)
       self.only_name_stack.pop ()

   def custom_function (self, func) :
       self.function (func)

   def function (self, func) :
       if func.item_body != None :
          self.style_empty_line ()

       self.openSection (func)

       self.send_expr (func.item_simple_decl.type_spec)
       self.simple_item_declarator (func)

       if func.init != None :
          self.send_initializer (func.init)

       if func.item_body != None :
           self.function_body (func)
       else :
           self.send (";")

       self.closeSection ()

       if func.item_body != None :
          self.style_empty_line ()

   def function_body (self, func) :
       self.style_stack.append (self.normal_style)

       if func.is_constructor :
          ctor_init = func.item_simple_decl.ctor_init
          if ctor_init != None :
             self.send (":")
             self.style_new_line ()
             self.send_ctor_initializer (ctor_init)
       self.style_new_line ()

       self.send ("{")
       self.style_indent ()
       self.style_no_empty_line ()

       self.custom_function_start (func)

       if func.is_constructor :
          self.custom_constructor_statements (func.item_context)

       self.custom_statements (func.item_body.items)

       if getattr (func, "mod_decl", None) != None :
          func.mod_decl (self, func)

       self.style_no_empty_line ()
       self.style_unindent ()
       self.send ("}")

       self.style_stack.pop ()

   def custom_function_start (self, func) :
       pass

   def custom_constructor_statements (self, cls) :
       pass

   # -----------------------------------------------------------------------

   def send_class_declaration (self, cls) :
       if not cls.skip_code :
          self.class_stack.append (cls)
          self.style_stack.append (self.normal_style)
          self.openSection (cls)

          if cls.style == classStyle :
             self.send ("class")
          elif cls.style == structStyle :
             self.send ("struct")
          elif cls.style == unionStyle :
             self.send ("union")
          self.send_expr (cls.simp_name)
          # self.send_attr_list (cls.attr)

          if cls.style == classStyle :
             cls.member_visibility = privateAccess
          else :
             cls.member_visibility = publicAccess

          if cls.members != None :
             if cls.base_list != None :
                self.send (":")
                self.send_base_specifier_list (cls.base_list)
             self.style_new_line ()
             self.send ("{")
             self.style_indent ()
             self.style_no_empty_line ()

             self.lookup_constructors (cls)

             if getattr (cls, "mod_decl", None) != None :
                self.switch_visibility (publicAccess)
                cls.mod_decl (self, cls)

             self.custom_members (cls)

             "additional (generated) methods"
             for method in cls.methods :
                 self.switch_visibility (publicAccess)
                 self.style_new_line ()
                 self.send ("void")
                 self.send (method.name)
                 self.send ("(")
                 self.send (")")
                 self.style_new_line ()
                 if method.body == None : # !?
                    self.send ("{}")
                 else :
                    self.send_compound_stat (method.body)
                 self.style_empty_line ()

             self.custom_default_constructor (cls)

             "end of class declaration"
             self.style_no_empty_line ()
             self.style_unindent ()
             self.send ("}")

          self.send (";")
          self.style_empty_line ()
          self.closeSection ()
          self.class_stack.pop ()
          self.style_stack.pop ()

   def lookup_constructors (self, cls) :
       cnt = 0
       for item in cls.item_list :
           if getattr (item, "is_constructor", False) :
              cnt = cnt + 1
       cls.constructor_count = cnt

   def switch_visibility (self, visibity) :
       cls = self.class_stack [-1]
       if cls.member_visibility != visibity :
          cls.member_visibility = visibity
          self.style_unindent ()
          if visibity == privateAccess :
             self.send ("private")
          elif visibity == protectedAccess :
             self.send ("protected")
          else :
             self.send ("public")
          self.send (":")
          self.style_indent ()
          self.style_no_empty_line ()

   def send_member_visibility (self, param) :
       self.switch_visibility (param.access)

   def custom_members (self, cls) :
       self.custom_statements (cls.members.items)

   def custom_default_constructor (self, cls) :
       pass

   # -----------------------------------------------------------------------

   def send_namespace_declaration (self, ns) :
       if not ns.skip_code :
          if ns.transparent_namespace or ns.hidden_scope:
             self.send_declaration_list (ns.members)
          else :
             super (ToCpp, self). send_namespace_declaration (ns)

   def send_using_declaration (self, using_decl) :
       cont = True
       if using_decl.a_namespace :
          ns = using_decl.qual_name.item_decl
          if ns != None :
             if ns.skip_code or ns.transparent_namespace :
                cont = False
       if cont :
             super (ToCpp, self). send_using_declaration (using_decl)

# --------------------------------------------------------------------------

class ToInitCpp (ToCpp) :

   def __init__ (self) :
       super (ToInitCpp, self).__init__ ()
       self.special_name = ""
       self.special_value = ""

   # -----------------------------------------------------------------------

   def custom_statement (self, stat) :
       style = self.style_stack [-1]
       only_class = (style == self.class_style)
       only_init = (style == self.init_style)

       skip = False

       if only_class :
          if not stat.move_statement :
             if stat.kind not in [simpleDecl, visibilityDecl] :
                skip = True
             if stat.kind == simpleStat and stat.inner_expr.alt_connect != "" :
                skip = True

       if only_init :
          if stat.kind in [namespaceDecl, classDecl, enumDecl, visibilityDecl] :
             skip = True

       if stat.kind == emptyStat :
          skip = True

       if not skip :
          if stat.move_statement :
             self.place_variable (stat.inner_expr.item_decl)
          else :
             self.send_stat (stat)
          self.style_new_line ()

   def custom_members (self, cls) :
       "send member list without initializers"
       self.style_stack.append (self.class_style)
       self.custom_statements (cls.members.items)
       self.style_stack.pop ()

   def custom_with_stat (self, stat) :
       only_global = (self.style_stack [-1] == self.global_style)
       if not only_global :
          self.custom_statements (stat.body.items)

   def custom_function (self, func) :
       only_init = (self.style_stack [-1] == self.init_style)
       if not only_init :
          self.function (func)

   # -----------------------------------------------------------------------

   def custom_variable (self, var) :
       if not var.move_variable :
          self.place_variable (var)

   def place_variable (self, var) :
       style = self.style_stack [-1]
       normal = (style == self.normal_style)
       only_class = (style == self.class_style) # class member
       only_init = (style == self.init_style) # default constructor / initialization function
       only_global = (style == self.global_style) # global declarations

       if only_class :
          self.send_expr (var.item_simple_decl.type_spec)
          self.simple_item_declarator (var)

          if self.std_cpp11 :
             if var.init != None :
                self.send_initializer (var.init)

          self.send (";")

          # nested declarations
          if var.item_body != None :
             self.style_new_line ()
             self.custom_statements (var.item_body.items)

       else :

          if normal or only_init :
             if var.item_body != None :
                self.style_empty_line ()
                self.comment (var.item_name)

          any = False

          if normal or only_global :
             self.send_expr (var.item_simple_decl.type_spec)
             self.simple_item_declarator (var)
             any = True

             if var.init != None :
                self.send_initializer (var.init)
                any = True
             "constructor_parameters already printed by simple_item_declarator"
             # elif len (var.construction_list) != 0 :
             #    if only_global :
             #       self.constructor_parameters (var)
             #       any = True

          if normal or only_init :
             if var.init == None and len (var.construction_list) == 0 :
                if var.alt_create == "" :
                   if var.item_body != None :
                      cls = self.get_pointer_class (var)
                      if cls != None :
                         if only_init :
                            self.send (var.item_name)
                         self.send ("=")
                         self.send ("new")
                         self.send (cls.item_name) # !?
                         any = True

          if any :
             self.send (";")
             self.style_new_line ()

          if normal or only_init :
             if only_init :
                self.custom_variable_create (var)
                self.style_new_line ()
             self.custom_variable_setup (var)

             if var.item_body != None :
                self.custom_statements (var.item_body.items)
                self.style_empty_line ()

   def constructor_parameters  (self, var) :
       self.send ("(")
       first = True
       for item in var.construction_list :
           if not first :
              self.send (",")
           self.send_expr (item)
           first = False
       self.send (")")

   def get_pointer_class (self, var) :
       cls = None
       type = var.item_type
       if isinstance (type, PointerType) :
          type = type.type_from
          if isinstance (type, NamedType) :
            if isinstance (type.type_decl, Class) :
               cls = type.type_decl
       return cls

   def custom_variable_create (self, var) :
       pass

   def custom_variable_setup (self, var) :
       pass

   def send_function_specifier (self, func_spec) :
       "skip constructor parameters in class member declarations"
       only_class = (self.style_stack [-1] == self.class_style)
       all_values = getattr (func_spec, "all_values", False)
       if not all_values or not only_class :
          super (ToInitCpp, self).send_function_specifier (func_spec)

  # -----------------------------------------------------------------------

   initialize_name = "initialize"

   def custom_default_constructor (self, cls) :
       if cls.constructor_count > 1 :
          self.initialize_function (cls)

       if cls.constructor_count == 0 :
          self.default_constructor (cls)

   def default_constructor (self, cls) :
       self.switch_visibility (publicAccess)
       self.style_empty_line ()
       self.put_name (cls)
       self.send ("(")
       self.send (")")
       self.constructor_initialization (cls, None)
       self.send ("{")
       self.style_indent ()
       self.style_no_empty_line ()

       self.custom_constructor_statements (cls)

       self.style_no_empty_line ()
       self.style_unindent ()
       self.send ("}")
       self.style_empty_line ()

   def custom_constructor_statements (self, cls) :
       if cls.constructor_count > 1 :
          self.style_new_line ()
          self.send (self.initialize_name)
          self.send ("(")
          self.send (")")
          self.send (";")
          self.style_new_line ()
       else :
          self.additional_statements (cls.members.items)

   def initialize_function (self, cls) :
       self.switch_visibility (publicAccess)
       self.style_empty_line ()
       self.send ("void")
       self.send (self.initialize_name)
       self.send ("(")
       self.send (")")
       self.style_new_line ()
       self.send ("{")
       self.style_indent ()
       self.style_no_empty_line ()

       self.additional_statements (cls.members.items)

       self.style_no_empty_line ()
       self.style_unindent ()
       self.send ("}")
       self.style_empty_line ()

   def additional_statements (self, block) :
       self.style_stack.append (self.init_style)
       self.custom_statements (block)
       self.style_stack.pop ()

   # -----------------------------------------------------------------------

   std_cpp11 = False
   # std_cpp11 = False => no class member initialization in variable declaration

   def start_member_initializer (self, any) :
       if not any :
          self.send (":")
          self.style_indent ()
       else :
          self.send (",")
          self.style_new_line ()

   def variable_init_value (self, var) :
       special = var.alt_init
       if special == "<false>" :
          self.send ("false")
       elif special == "<char_zero>" :
          self.send ("0")
       elif special == "<zero>" :
          self.send ("0")
       elif special == "<float_zero>" :
          self.send ("0.0f")
       elif special == "<double_zero>" :
          self.send ("0.0")
       elif special == "<empty_string>" or special == "<empty_qstring>" :
          self.send ("\"\"")
       elif special == "<null>" :
          self.send ("nullptr") # !?

   def constructor_initialization (self, cls, func) :
       start = [ ] # base class initializers
       variable_dict = { } # variable initializers

       if func != None :
          ctor_init = func.item_simple_decl.ctor_init
          if ctor_init != None :
             for item in ctor_init.items :
                 var_name = None
                 if item.simp_name.kind == simpleName :
                    name = item.simp_name.id
                    if name in cls.item_dict :
                       var = cls.item_dict [name]
                       if not var.is_function :
                          var_name = name
                 if var_name != None :
                    variable_dict [var_name] = item
                 else :
                    start.append (item)

       "base class initializers"
       any = False
       for item in start :
           self.start_member_initializer (any)
           any = True
           self.send_member_initializer (item)

       "variable initializers"
       for var in cls.item_list :
           if isinstance (var, CmmSimpleDecl) and not var.is_function :
              name = var.item_name
              if name in variable_dict :
                 "initializer from constructor"
                 self.start_member_initializer (any)
                 any = True
                 item = variable_dict [var.item_name]
                 self.send_member_initializer (item)
              elif var.init != None :
                 "initializer from variable declaration"
                 if not self.std_cpp11 :
                    self.start_member_initializer (any)
                    any = True
                    self.send (name)
                    self.send ("(")
                    self.send_initializer_item (var.init.value)
                    self.send (")")
              elif len (var.construction_list) != 0 :
                 "constructor_parameters from variable declaration"
                 self.start_member_initializer (any)
                 any = True
                 self.send (name)
                 self.constructor_parameters (var)
              else :
                 "default value"
                 self.start_member_initializer (any)
                 any = True
                 self.send (name)
                 self.send ("(")
                 self.variable_init_value (var)
                 self.send (")")

       if any :
          self.style_unindent ()
       else :
          self.style_new_line ()

   # -----------------------------------------------------------------------

   def custom_function_start (self, func) :
       "add initialize to main funtion"
       if func.item_qual == "main" and self.global_initialization :
          self.send (self.initialize_name)
          self.send ("(")
          self.send (")")
          self.send (";")
          self.style_empty_line ()

   def send_program (self, decl_list) :
       "collect global variable initializations"

       # super (ToInitCpp, self).send_program (decl_list)

       any = False
       for decl_item in decl_list.items :
           if decl_item.kind == simpleDecl : # !? namespace
              for item in decl_item.items :
                  if not item.is_function and decl_item.body != None :
                     any = True
       self.global_initialization = any

       if any :
          self.send ("void")
          self.send (self.initialize_name)
          self.send ("(")
          self.send (")")
          self.send (";")
          self.style_empty_line ()

       "send member list without initializers"
       self.style_stack.append (self.global_style)
       self.custom_statements (decl_list.items)
       self.style_stack.pop ()

       if any :
          "initialize function"
          self.send ("void")
          self.send (self.initialize_name)
          self.send ("(")
          self.send (")")
          self.style_new_line ()
          self.send ("{")
          self.style_indent ()
          self.style_no_empty_line ()

          self.style_stack.append (self.init_style)
          # self.custom_statements (decl_list.items)
          for item in decl_list.items :
              if item.kind != extensionStat :
                 self.send_stat (item)
                 self.style_new_line ()
          self.style_stack.pop ()

          self.style_no_empty_line ()
          self.style_unindent ()
          self.send ("}")
          self.style_empty_line ()

   # -----------------------------------------------------------------------

   class Step (object) :
       def __init__ (self) :
           # super ().__init__ ()
           self.lo = None
           self.hi = None

   def display (self, expr) :
       result = ""
       if expr != None :
          if expr.kind == intValue :
             result = expr.value
          elif expr.kind == simpleName :
             result = expr.id
          elif expr.kind == addExpr :
             result = self.display (expr.left) + "+" + self.display (expr.right)
          elif expr.kind == subExpr :
             result = self.display (expr.left) + "-" + self.display (expr.right)
       return result

   def get_expr_value (self, expr) : # redefine get_expr_value
       result = getattr (expr, "item_value", None)
       if result == None :
          if expr.kind == eqExpr :
             if expr.left.kind == simpleName and expr.left.id == self.special_name :
                if expr.right.kind == intValue and expr.right.value == self.special_value :
                   result = True
       return result

   def custom_for_stat (self, stat, target) :
       expr = stat.iter_expr

       expr_list = [ ]
       if expr.kind == commaExpr :
          while expr.kind == commaExpr :
             expr_list.insert (0, expr.right)
             expr = expr.left
          expr_list.insert (0, expr)

       step_list = [ ]
       ok = True
       for expr in expr_list :
           if expr.kind == callExpr and expr.left.kind == simpleName and expr.left.id == "range" :
              params = expr.param_list.items
              if len (params) == 2 :
                 step = self.Step ()
                 step.lo = params [0]
                 step.hi = params [1]
                 step_list.append (step)
              else :
                 ok = False
           else :
             step = self.Step ()
             step.lo = expr
             step.hi = expr
             step_list.append (step)

       if ok :
          self.comment ("expand for loop")
          self.send ("{")
          self.new_line ()
          self.indent ()

          for step in step_list :
             self.comment ("from " + self.display (step.lo) + " to " + self.display (step.hi))

             if step.lo == step.hi :
                expr = step.lo
                # if expr.kind == eqExpr :
                #    self.comment ("equal")
                #    if expr.left.kind == simpleName :
                #       self.comment ("name " + expr.left.id)
                #    if expr.left.kind == simpleName and expr.left.id == target.item_name :
                #       if expr.right.kind == intValue :
                #       if expr.right.kind == intValue :
                #       self.special_name = expr.left.id
                #          self.special_value = expr.right.value
                if expr.kind == intValue :
                         self.special_name = target.item_name
                         self.special_value = expr.value
                         self.comment ("special_name " + self.special_name)
                         self.comment ("special_value " + self.special_value)


             if step.lo == step.hi :
                self.send (target.item_name)
                self.send ("=")
                self.send_expr (step.lo)
                self.send (";")
             else :
                self.send ("for")
                self.send ("(")
                self.send (target.item_name)
                self.send ("=")
                self.send_expr (step.lo)
                self.send (";")
                self.send (target.item_name)
                self.send ("<=")
                self.send_expr (step.hi)
                self.send (";")
                self.send (target.item_name)
                self.send ("++")
                self.send (")")

             self.new_line ()
             self.send_stat (stat.body)
             self.new_line ()
             self.special_name = ""
             self.special_value = ""

          self.unindent ()
          self.send ("}")
          self.new_line ()


# --------------------------------------------------------------------------

class ToQtCpp (ToInitCpp) :

   def __init__ (self) :
       super (ToQtCpp, self).__init__ ()

   # -----------------------------------------------------------------------

   def custom_left (self, expr) :
       var = expr.left.item_decl.item_context.item_context
       self.put_name (var)
       self.put_arrow ()

   def custom_assign (self, expr) :
       done = False
       special = expr.alt_assign
       if special != "" and not done :
          self.custom_left (expr)
          self.send (special)
          self.send ("(")

          if expr.alt_assign_index != "" :
             self.send (expr.alt_assign_index )
             self.send (",")

          param = expr.alt_assign_param
          if param == "<icon>"  :
             self.send ("QIcon")
             self.put_colons ()
             self.send ("fromTheme")
             self.send ("(")
             self.send_expr (expr.right)
             self.send (")")
          elif param == "<color>" :
             self.send ("QColor")
             self.send ("(")
             self.send_expr (expr.right)
             self.send (")")
          elif param == "<shortcut>" :
             self.send ("QKeySequence")
             self.send ("(")
             self.send_expr (expr.right)
             self.send (")")
          else :
             self.send_expr (expr.right)

          self.send (")")
          done = True
       return done

   # -----------------------------------------------------------------------

   """
   def custom_call (self, expr) :
       done = False
       params = expr.param_list
       cnt = len (params.items)

       "target.field (params)"
       if expr.left.kind == fieldExpr :
          target = expr.left.left
          field = expr.left.simp_name.id

          type_name = self.get_foreign_type (target)

          if type_name == "QStringList" :
             if field == "group" :
                if cnt == 1 :
                   self.send_expr (target)
                   self.send ("[")
                   param = params.items [0]
                   if isinstance (param.item_value, int) :
                      self.send (str (param.item_value - 1))
                   else :
                      self.send_expr (param)
                      self.send ("-")
                      self.send ("1")
                   self.send ("]")
                   done = True

       return done

   def get_foreign_type (self, expr) :
       type_name = ""
       if getattr (expr, "item_type", None) != None :
          type = expr.item_type
          if type != None and getattr (type, "type_decl", None) != None :
             type_decl = type.type_decl
             if type_decl.item_context.item_qual == "(foreign)" :
                type_name = type_decl.item_name
       return type_name
   """

   # -----------------------------------------------------------------------

   def send_expr (self, expr) :
       done = False

       """
       if not done :
          "SIGNAL / SLOT"
          if getattr (expr, "macro_name", "") != "" :
             self.send (expr.macro_name)
             self.send ("(")
             self.send (expr.func_name)
             self.send ("(")
             if getattr (expr, "parameters", None) != None :
                self.send_parameter_list (expr.parameters)
             self.send (")")
             self.send (")")
             done = True
       """

       if not done :
          if isinstance (expr, CmmName) :
             "variable prefix"
             only_name = self.only_name_stack [-1]
             if not only_name :
                if getattr (expr, "item_decl", None) != None :
                   ctx = expr.item_decl.item_context
                   while ctx != None and ctx.hidden_scope :
                      ctx = ctx.item_context
                   if ctx != None and ctx.search_only :
                      self.put_name (ctx)
                      self.put_arrow ()

       if not done :
          "read function"
          special = expr.alt_read
          if special != "" :
             if not expr.call_func : # without function call parenthesis
                self.send (special)
                done = True

       if not done :
          if expr.kind == assignExpr :
             done = self.custom_assign (expr)

       if not done :
          if expr.kind == fieldExpr :
             "formal str or var field"
             if expr.var_field or expr.str_field :
                self.send_expr (expr.left)
                done = True
             "convert dot to arrow"
             if isinstance (expr.left.item_type, PointerType) :
                self.send_expr (expr.left)
                self.put_arrow ()
                self.only_name_stack.append (True)
                self.send_expr (expr.field_name)
                self.only_name_stack.pop ()
                done = True

       if not done :
          if expr.kind == ptrFieldExpr :
             self.send_expr (expr.left)
             self.put_arrow ()
             self.only_name_stack.append (True)
             self.send_expr (expr.field_name)
             self.only_name_stack.pop ()
             done = True

       if not done :
          super (ToQtCpp, self).send_expr (expr)

   # -----------------------------------------------------------------------

   def custom_connect (self, expr) :
       self.send ("QObject")
       self.put_colons ()
       self.send ("connect")
       self.send ("(")
       self.send (expr.alt_connect_decl)
       self.send (",")
       if use_qt4 :
          self.send ("SIGNAL")
          self.send ("(")
          self.send (expr.alt_connect_signal + " ()")
          self.send (")")
          self.send (",")
          self.send ("this")
          self.send (",")
          self.send ("SLOT")
          self.send ("(")
          self.send (expr.alt_connect + " ()")
          self.send (")")
       else:
          self.send ("&")
          self.style_no_space ()
          self.send (expr.alt_connect_src)
          self.put_colons ()
          self.send (expr.alt_connect_signal)
          self.send (",")
          self.send ("this")
          self.send (",")
          self.send ("&")
          self.style_no_space ()
          self.send (expr.alt_connect_cls)
          self.put_colons ()
          self.style_no_space ()
          self.send (expr.alt_connect)
       self.send (")")
       self.send (";")
       self.style_new_line ()

   # -----------------------------------------------------------------------

   def send_stat (self, stat) :
       if not getattr (stat, "skip_code", False) :
          done = False

          if stat.kind == simpleStat :
             expr = stat.inner_expr
             if expr.alt_connect != "" :
                self.custom_connect (expr)
                done = True

          if not done :
             super (ToQtCpp, self).send_stat (stat)

          if stat.kind == simpleStat :
             expr = stat.inner_expr
             for item in expr.following_items :
                 self.send_declaration (item)

   # -----------------------------------------------------------------------

   def put_place (self, var) :
       if var.item_place == None :
          self.send ("this")
       else :
          self.put_name (var.item_place)

   # -----------------------------------------------------------------------

   def custom_variable_create (self, var) :
       special = var.alt_create
       if special != "" :
          self.put_name (var)
          self.send ("=")
          if special.startswith ("<") :
              if special == "<menuBar>" :
                 self.send ("menuBar ();")
              elif special == "<addToolBar>" :
                 self.send ("addToolBar (\"\");")
              elif special == "<statusBar>" :
                 self.send ("statusBar ();")
              elif special == "<addMenu>" :
                 self.send ("addMenu (\"\");")
              elif special == "<addAction>" :
                 self.put_place (var)
                 self.put_arrow ()
                 self.send ("addAction (\"\");")

          else :
             self.send ("new")
             self.send (special)
             self.send ("(")
             if var.alt_create_owner :
                self.send ("this")
             if var.alt_create_place :
                self.put_place (var)
             self.send (")")
             self.send (";")

          self.style_new_line ()

   # -----------------------------------------------------------------------

   def custom_variable_setup (self, var) :
       special = var.alt_setup
       if special != "" :
          if special == "<layout>" :
             self.send ("QWidget * temp = new QWidget ();")
             self.style_new_line ()
             self.send ("temp->setLayout (")
             self.put_name (var)
             self.send (");")
             self.style_new_line ()
             self.send ("setCentralWidget (temp);")
             self.style_new_line ()
          elif special == "<setCentralWidget>" :
             self.send ("setCentralWidget (")
             self.put_name (var)
             self.send (");")
             self.style_new_line ()
          else :
             func_name = var.alt_setup
             func_param = var.alt_setup_param
             self.put_place (var)
             self.put_arrow ()
             self.send (func_name)
             self.send ("(")
             self.put_name (var)
             if func_param != "" :
                self.send (",")
                self.send (func_param)
             self.send (")")
             self.send (";")
             self.style_new_line ()

   # -----------------------------------------------------------------------

   def precompiled_header (self) :
       headerName = "precompiled.h"
       win = self.compiler.win;
       fileName = ""
       if win != None :
          fileName = win.outputFileName (headerName)
          win.joinProject (fileName)


       if fileName != "" and not os.path.isfile (fileName) :
          output = Output ()
          output.openFile (fileName)
          output.putLn ("#include <QtCore>")
          output.putLn ("#include <QtGui>")
          if not use_qt4 :
             output.putLn ("#include <QtWidgets>")

          """
          output.style_empty_line ()
          output.putLn ("#include <stdio.h>")
          output.style_empty_line ()

          output.putLn ("#include <iostream>")
          output.putLn ("#include <fstream>")
          output.putLn ("#include <stream>")
          """

          output.close ()

       if self.win != None :
          self.win.joinProject (fileName)

       self.putLn ("#include " + quoteString (headerName))
       self.style_empty_line ()

   def send_program (self, decl_list) :
       if 1 :
          self.precompiled_header ()
       else :
          # self.putLn ("#include <QApplication>")
          self.putLn ("#include <QtCore>")
          self.putLn ("#include <QtGui>")
          if not use_qt4 :
             self.putLn ("#include <QtWidgets>")
          self.style_empty_line ()

       super (ToQtCpp, self).send_program (decl_list)

       # !?
       # for item in self.compiler.foreign_scope.item_list :
       #     if item.item_used :
       #        self.putLn ("import (" + item.item_name + ");")

       if use_qt6 :
          self.putLn ("// compile: -P Qt6 -lstdc++ -fPIC")
       elif use_qt5 :
          self.putLn ("// compile: -P Qt5Widgets -lstdc++ -fPIC")
       else :
          self.putLn ("// compile: -P QtGui -lstdc++ -fPIC")
       self.putLn ("// kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all")


"""
Qt6.pc
------

prefix=/usr
exec_prefix=${prefix}
libdir=${prefix}/lib
includedir=${prefix}/include/qt6

Name: Qt6 Core
Description: Qt 6
Version: 6
Libs: -lQt6Core -lQt6Gui -lQt6Widgets
Cflags: -I${includedir}/QtCore -I${includedir}/QtGui -I${includedir}/QtWidgets -I${includedir}
"""

# --------------------------------------------------------------------------

class ToExtCpp (ToQtCpp) :

   def __init__ (self) :
       super (ToExtCpp, self).__init__ ()

   "CmmExtensionStat"

   def send_extension_stat (self, stat) :
       name = stat.name
       param = stat.param

       if name == "put" :
          self.put (param)
       elif name == "putEol" :
          self.putEol ()
       elif name == "indent" :
          self.indent ()
       elif name == "unindent" :
          self.unindent ()
       elif name == "send" :
          self.send (param)
       elif name == "no_space" :
          self.no_space ()
       elif name == "new_line" :
          self.new_line ()
       elif name == "empty_line" :
          self.empty_line ()
       elif name == "no_empty_line" :
          self.no_empty_line ()

       elif name == "include" :
          self.new_line ()
          self.put ("#include " + param)
          self.putEol ()
       elif name == "directive" :
          self.new_line ()
          self.put (param)
          self.putEol ()
       elif name == "comment" :
          self.put ("// " + param)
          self.putEol ()

       elif name == "kit_block" :
          print ("KIT BLOCK", param)
          for item in stat.items :
              self.send_declaration (item)

       elif name == "code" :
          if stat.into_expr != None :
             self.send_expr (stat.into_expr)
             self.send (".")
             self.send ("append")
             self.send ("(")

          if stat.store_expr != None :
             self.send_expr (stat.store_expr)
             self.send ("=")

          self.send ("code")
          self.send ("(")
          self.indent ()
          self.new_line ()
          for line in stat.ext_source.split ("\n") :
              self.send (quoteString (line))
              self.new_line ()
          self.unindent ()

          self.send (")")

          if stat.into_expr != None :
             self.send (")")

       elif name == "nested_file" :
          print ("NESTED FILE", param)
          self.new_line ()
          self.putLn ("#include " + quoteString (param))

       elif name == "nested_module" :
          # print ("NESTED_MODULE", stat.param)

          if 1 : # if stat.ext_source :
             if self.win != None :
                # print ("NESTED_MODULE (2)", stat.param)
                fileName = stat.param + ".cpp"
                fileName = self.win.outputFileName (fileName)
                self.win.joinProject (fileName)
                output = Output ()
                output.open (fileName)
                save_redirect = self.redirect
                self.redirect = output
                self.send_declaration_list (stat)
                self.redirect = save_redirect
                output.close ()

   def send_expr (self, expr) :
       done = False

       if expr.kind == assignExpr :
          if expr.left.item_type != None and expr.left.item_type.gpu_global :
             self.send ("MOVE_TO_GPU");
             self.send_expr (expr.left)
             self.send ("=")
             self.send_expr (expr.right)
             done = True
          elif expr.right.item_type!= None and expr.right.item_type.gpu_global :
             self.send ("MOVE_FROM_GPU");
             self.send_expr (expr.left)
             self.send ("=")
             self.send_expr (expr.right)
             done = True
       elif expr.kind == callExpr :
          if expr.left.item_type != None and expr.left.item_type.gpu_global :
             self.send ("CALL_GPU");
             self.send_expr (expr.left)
             self.send ("(")
             self.send_expr_list (expr.param_list)
             self.send (")")
             done = True
       elif expr.kind == indexExpr :
          if expr.left.item_type != None and expr.left.item_type.gpu_global :
             self.send ("CALL_GPU");
             self.send_expr (expr.left)
             self.send ("<<<")
             self.send_expr (expr.param)
             self.send (">>>")
             done = True

       if not done :
          super (ToExtCpp, self).send_expr (expr)

# --------------------------------------------------------------------------

class ToCustomCpp (ToExtCpp) :

   def __init__ (self) :
       super (ToCustomCpp, self).__init__ ()

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
