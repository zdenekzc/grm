
# c2py.py

from __future__ import print_function

import os

from input import quoteString
from util import use_pyside2, use_pyside6, use_pyqt5, use_pyqt6, use_qt6, use_py2_qt4
from output import Output
from code_base import *
from cmm_parser import *

# --------------------------------------------------------------------------

class ToPy (Output) :

   python = True

   def __init__ (self) :
       super (ToPy, self).__init__ ()

       self.compiler = None
       self.builder = None
       self.win = None

       self.class_stack = [ ]
       self.empty_stack = [ False ]

       self.ignore_skip = False # ignore skip_code flag

   def openBlock (self) :
       self.empty_stack.append (True)

   def addBlockItem (self) :
       self.empty_stack [-1] = False

   def closeBlock (self) :
       empty = self.empty_stack.pop ()
       if empty :
          self.send ("pass")
          self.style_new_line ()
          self.addBlockItem () # pass statement

   def put_dot (self) :
       self.style_no_space ()
       self.send (".")
       self.style_no_space ()

   # -----------------------------------------------------------------------

   def custom_prefix (self, obj) :
       ctx = obj.item_context
       if isinstance (ctx, Class) :
          self.send ("self")
          self.put_dot ()

   # -----------------------------------------------------------------------

   def put_name (self, obj) :
       if getattr (obj, "mod_rename", None) != None :
          self.addUsage (obj.mod_rename, obj)
       else :
          self.addUsage (obj.item_name, obj)

   def send_simple_name (self, expr) :
       ident = getattr (expr, "id", "")
       if ident == "true" :
          self.send ("True")
       elif ident == "false" :
          self.send ("False")
       elif ident == "NULL" or ident == "null" or ident == "nullptr" : # !?
          self.send ("None")
       else :
          "add identifier/expression from with statement"
          if getattr (expr, "name_owner", None) != None :
             scope = expr.name_owner
             if scope.owner_obj != None or scope.owner_expr != None:
                if scope.owner_parenthesis :
                   self.send ('(')
                if scope.owner_obj != None :
                   self.custom_prefix (scope.owner_obj)
                   self.put_name (scope.owner_obj)
                else :
                   self.send_expr (scope.owner_expr)
                if scope.owner_parenthesis :
                   self.send (')')
                self.put_dot ()

          self.put_dot_name (None, expr)

   def put_dot_name (self, above_expr, expr) :
       done = False

       "read function"
       if expr.alt_read != "" :
          if not expr.call_func : # without function call parenthesis
             # self.custom_prefix (expr.item_decl)
             self.send (expr.alt_read)
             # self.send ("(")
             # self.send (")")
             done = True

       if not done :
          decl = getattr (expr, "item_decl", None)
          decl = getattr (expr, "item_ref", decl)
          if decl != None :
             self.put_name (decl)
          else :
             self.send (expr.id)

   def send_qualified_name (self, expr) :
       if expr.kind == simpleName :
          if getattr (expr, "item_decl", None) != None :
             if getattr (expr, "name_owner", None) == None :
                self.custom_prefix (expr.item_decl)

       if expr.kind == simpleName :
          self.send_simple_name (expr)
       elif expr.kind == globalName : # !?
          self.send_qualified_name (expr.inner_name)
       elif expr.kind == compoundName :
          self.send_qualified_name (expr.left)
          self.put_dot ()
          self.send_qualified_name (expr.right)
       elif expr.kind == contName :
          self.send_simple_name (expr)

   # -----------------------------------------------------------------------

   def send_expr_list (self, param) :
       first = True
       for item in param.items :
           if not first :
              self.send (",")
           first = False
           self.send_expr (item)

   # -----------------------------------------------------------------------

   def send_nested_stat (self, stat) :
       self.style_indent ()
       if stat.kind == compoundStat :
          self.send_compound_stat (stat)
       else :
          self.openBlock ()
          self.send_stat (stat)
          self.closeBlock ()
       self.style_unindent ()

   def send_empty_stat (self, stat) :
       # self.send ("pass")
       # self.style_new_line ()
       pass

   def send_compound_stat (self, stat) :
       self.openBlock ()
       self.send_compound_statements (stat)
       self.closeBlock ()

   def send_compound_statements (self, stat) :
       for item in stat.items :
           if item.kind != emptyStat :
              self.send_stat (item)

   def send_if_stat (self, stat) :
       self.addBlockItem ()
       self.send ("if")
       self.send_condition (stat.cond, extra_init = True)
       self.send (":")
       self.style_new_line ()
       self.send_nested_stat (stat.then_stat)
       if stat.else_stat != None :
          self.send ("else")
          self.send (":")
          self.style_new_line ()
          self.send_nested_stat (stat.else_stat)

   def send_while_stat (self, stat) :
       self.addBlockItem ()
       self.send ("while")
       self.send_condition (stat.cond, extra_init = True)
       self.send (":")
       self.style_new_line ()
       self.send_nested_stat (stat.body)

   def send_for_stat (self, stat) :
       self.addBlockItem ()
       if stat.iter_expr != None :
          " for ( from_expr : iter_expr ) body "
          self.send ("for")
          if stat.from_expr != None :
             self.send_condition (stat.from_expr, no_init = True)
          self.send ("in")
          self.send_expr (stat.iter_expr)
          self.send (":")
          self.style_new_line ()
          self.send_nested_stat (stat.body)
       else:
          " for ( from_expr ; cond_expr ;  step_expr ) body "
          if stat.from_expr != None :
             self.send_condition (stat.from_expr)
          self.style_new_line ()
          self.send ("while")
          if stat.cond_expr != None :
             self.send_expr (stat.cond_expr)
          else :
             self.send ("True")
          self.send (":")
          self.style_new_line ()
          self.style_indent ()
          self.send_stat (stat.body)
          if stat.step_expr != None :
             self.send_expr (stat.step_expr)
             self.style_new_line ()
          self.style_unindent ()

   def send_switch_stat (self, stat) :
       pass # !?

   def send_return_stat (self, stat) :
       self.addBlockItem ()
       self.send ("return")
       if stat.return_expr != None :
          self.send_expr (stat.return_expr)
       self.style_new_line ()

   def stream_io (self, stat) :
       done = False

       expr = stat.inner_expr;

       if expr.kind == shlExpr :
          temp = expr
          args = [ ]
          while temp.kind == shlExpr :
             args.insert (0, temp.right)
             temp = temp.left;
          if temp.kind == simpleName :
             if temp.id == "cout" : # !?
                done = True;

                self.send ("print")
                self.send ("(")

                any = False
                endl = False
                for item in args :
                    if item.kind == simpleName and item.id == "endl" :
                       endl = True
                    else :
                       if any :
                          self.send (",")
                       any = True
                       self.send_expr (item)

                if any :
                   self.send (",")
                any = True
                self.send ("sep")
                self.send ("=")
                self.send (quoteString (""))

                if not endl :
                   if any :
                      self.send (",")
                   self.send ("end")
                   self.send ("=")
                   self.send (quoteString (""))

                self.send (")")
                self.putEol ()
                self.addBlockItem ()

       return done

   def send_simple_stat (self, stat) :
       if stat.body != None :
          self.custom_with_statement (stat)
       elif stat.move_statement :
          self.send_simple_item (stat.inner_expr.item_decl)
       else :

          done = self.stream_io (stat)
          if not done :

             self.addBlockItem ()
             self.send_expr (stat.inner_expr)
             self.style_new_line ()

             "CmmExtensionStat"
             expr = stat.inner_expr
             for item in expr.following_items :
                self.send_declaration (item)

   def custom_with_statement (self, stat) :
       pass

   # -----------------------------------------------------------------------

   def send_simple_declaration (self, simple_decl) :
       for simple_item in simple_decl.items :
           if not simple_item.method_implementation :
              if not simple_item.move_variable :
                 self.send_simple_item (simple_item)

   def send_simple_item (self, simple_item) :
       if not simple_item.is_function :
          var = simple_item
          if not isinstance (var.item_context, Class) :
             "variable, but not class member"
             if var.item_body != None :
                self.style_empty_line ()
             self.addBlockItem ()
             self.variable_declarator (var.declarator)
             if not var.no_init :
                self.variable_initialization (var)
             if not var.cont_line :
                self.style_new_line ()
             self.custom_variable_setup (var)
             if var.item_body != None :
                self.custom_variable_block (var)
                self.style_empty_line ()
       else :
         func = simple_item
         if func.item_body != None :
            if not func.is_destructor :
               "function or constructor implementation"
               self.addBlockItem ()
               self.style_empty_line ()
               self.openSection (func)
               self.send ("def")
               if func.is_constructor :
                  self.send ("__init__")
                  self.send_declarator (func.declarator)
               elif func.method_implementation :
                  self.put_name (func)
                  self.send_func_specifier_list (func.declarator)
               else :
                  self.send_declarator (func.declarator)
               self.send (":")
               self.style_new_line ()
               self.style_indent ()
               self.openBlock ()
               if func.is_constructor :
                  self.constructor_initializers (func.item_context, func)
               self.send_compound_statements (func.item_body)
               self.closeBlock ()
               self.style_unindent ()
               self.style_empty_line ()
               self.closeSection ()

   def variable_initialization (self, var) :
       if var.init != None :
          self.send_initializer (var.init, var.extra_assign)
       else :
          if var.extra_assign :
             self.send (":=") # Python 3.8
          else :
             self.send ("=")
          if len (var.construction_list) != 0 :
             self.initialize_variable_with_value_list (var, var.construction_list)
          else :
             done = self.custom_variable_initialization (var)
             if not done :
                if var.alt_init != ""  and var.alt_init != "<null>" :
                   self.initialize_variable_with_value (var)
                else :
                   self.initialize_variable_with_value_list (var, [ ], allow_pointer = (var.item_body != None))

   def custom_variable_initialization (self, var) :
       return False

   def custom_variable_setup (self, var) :
       pass

   def custom_variable_block (self, var) :
       pass

   def send_condition (self, cond, no_init = False, extra_init = False) :
       if cond.kind == simpleStat :
          expr = cond.inner_expr
          expr.extra_assign = extra_init
          self.send_expr (expr)
       elif cond.kind == simpleDecl :
          any = False
          for item in cond.items :
            if any :
               self.send (",")
            item.cont_line = True
            item.no_init = no_init
            item.extra_assign = extra_init
            self.send_simple_item (item)
            any = True

   def variable_declarator (self, decl) :
       while decl.kind in [nestedDeclarator, pointerDeclarator, referenceDeclarator, arrayDeclarator, functionDeclarator] :
          decl = decl.inner_declarator
       if decl.kind == basicDeclarator :
          name = decl.qual_name
          self.send_qualified_name (name)

   def send_declarator (self, decl) :
       orig_decl = decl
       while decl.kind in [nestedDeclarator, pointerDeclarator, referenceDeclarator, arrayDeclarator, functionDeclarator] :
          decl = decl.inner_declarator
       if decl.kind == basicDeclarator :
          name = decl.qual_name
          self.send_qualified_name (name)
       self.send_func_specifier_list (orig_decl)

   def send_func_specifier_list (self, decl) :
       while decl.kind in [nestedDeclarator, pointerDeclarator, referenceDeclarator, arrayDeclarator,] :
             decl = decl.inner_declarator
       if decl.kind == functionDeclarator :
          self.send_function_specifier (decl)

   def send_function_specifier (self, param) :
       self.send ("(")
       self.send_parameter_declaration_list (param.parameters)
       self.send (")")

   def send_parameter_declaration_list (self, param) :
       first = True
       if len (self.class_stack) != 0 :
          self.send ("self")
          first = False
       for item in param.items :
           if not first :
              self.send (",")
           first = False
           self.send_parameter_declaration (item)

   def send_parameter_declaration (self, param) :
       if param.kind == simpleDecl :
          item = param.items[0]
          self.send_declarator (item.declarator)
          if item.init != None :
             self.send_initializer (item.init)
       if param.kind == simpleStat : # !? pointer declaration with unknown type
          expr = param.inner_expr
          if expr.kind == mulExpr :
             self.send_expr (expr.right)

   def send_initializer (self, param, extra_assign = False) :
       if extra_assign :
          self.send (":=")
       else :
          self.send ("=")
       self.send_initializer_item (param.value)

   def send_initializer_item (self, param) :
       if isinstance (param, CmmInitSimple) :
          self.send_expr (param.inner_expr)
       elif isinstance (param, CmmInitList) :
          self.send_initializer_list (param)

   def send_initializer_list (self, param) :
       inx = 0
       cnt = len (param.items)
       self.send ("[") # !?
       self.style_indent ()
       for item in param.items :
          self.send_initializer_item (item)
          inx = inx + 1
          if inx < cnt :
             self.send (",")
             self.style_new_line ()
       self.style_unindent ()
       self.send ("]")

   # -----------------------------------------------------------------------

   def initialize_variable_with_value (self, var) :
       special = var.alt_init

       if special == "<false>" :
          self.send ("False")
       elif special == "<char_zero>" :
          self.send ("0")
       elif special == "<zero>" :
          self.send ("0")
       elif special == "<float_zero>" :
          self.send ("0.0")
       elif special == "<double_zero>" :
          self.send ("0.0")
       elif special == "<empty_string>" :
          self.send ("\"\"")
       elif special == "<empty_list>" :
          self.send ("[ ]")
       elif special == "<empty_dict>" :
          self.send ("{ }")
       elif special == "<null>" :
          self.send ("None")
       elif special == "<empty_qstring>" :
            if use_py2_qt4 :
                self.send ("QString ()")
            else :
                self.send ("\"\"")
       else :
           self.send ("None")

   def put_value_list (self, value_list) :
       first = True
       for item in value_list :
           if not first :
              self.send (",")
           first = False
           self.send_expr (item)

   def initialize_variable_with_value_list (self, var, value_list, allow_pointer = False) :

       cls = None
       type = var.item_type
       if allow_pointer and isinstance (type, PointerType) :
          type = type.type_from
       if isinstance (type, NamedType) :
          if isinstance (type.type_decl, Class) :
             cls = type.type_decl

       if cls != None and cls.item_name != "QString":
          self.send (cls.item_name) # !?
          self.send ("(")
          self.put_value_list (value_list)
          self.send (")")
       else :
          cnt = len (value_list)
          if cnt == 0 :
             self.initialize_variable_with_value (var)
          elif cnt == 1 :
             self.put_value_list (value_list)
          else :
             self.send ("(")
             self.put_value_list (value_list)
             self.send (")")
             self.compiler.warning_with_location (var, "Initialization with too many items")

       self.style_new_line ()

   # -----------------------------------------------------------------------

   def comment (self, txt) :
       self.style_empty_line ()
       self.send (quoteString (txt))
       self.style_new_line ()

   def initialize_base (self, cls, item, add_parent = False) :
       self.addBlockItem ()
       self.send ("super")
       self.send ("(")
       self.put_name (cls) # class name
       self.send (",")
       self.send ("self")
       self.send (")")
       self.put_dot ()
       self.send ("__init__")

       self.send ("(")

       if add_parent :
          self.send ("parent")
          if item != None and len (item.params.items) != 0 :
             self.send (",")

       if item != None :
          self.send_expr_list (item.params)

       self.send (")")
       self.style_new_line ()

   def initialize_member (self, var, item) :
       self.addBlockItem ()
       self.custom_prefix (var)
       self.put_name (var)
       self.send ("=")

       self.initialize_variable_with_value_list (var, item.params.items)

   # -----------------------------------------------------------------------

   def constructor_initializers (self, cls, func) :
       base_list = [ ]
       var_list = [ ]
       init_vars = { }

       if func != None :
          ctor_init = func.item_simple_decl.ctor_init
          if ctor_init != None :
             for item in ctor_init.items :
                 if item.simp_name.kind == simpleName :
                    name = item.simp_name.id
                    if name in cls.item_dict :
                       var = cls.item_dict [name]
                       if not var.is_function :
                          var_list.append (item)
                          init_vars [name] = True
                    else :
                       base_list.append (item)

       "base classes"
       if len (base_list) ==  0 :
          self.initialize_base (cls, None)

       for item in base_list :
           self.initialize_base (cls, item)

       "initialization from constructor"
       for item in var_list :
           var = cls.item_dict [item.simp_name.id]
           self.initialize_member (var, item)

       "initialization from class declaration"
       if cls.members != None :
          self.custom_constructor_statements (cls.members, init_vars)

       self.custom_construction (cls)

   def custom_constructor_statements (self, block, init_vars) :
       pass

   def custom_construction (self, cls) :
       pass

   def custom_default_constructor (self, cls) :
       pass

   # -----------------------------------------------------------------------

   def send_class_declaration (self, cls) :
       if self.ignore_skip or not cls.skip_code :
          self.class_stack.append (cls)

          self.style_empty_line ()
          self.openSection (cls)

          self.send ("class")
          self.send_simple_name (cls.simp_name)

          if cls.members != None :
             if cls.base_list != None :
                self.send ("(")
                self.send_base_specifier_list (cls.base_list)
                self.send (")")

          self.send (":")
          self.style_new_line ()

          self.style_indent ()
          self.openBlock ()

          self.custom_default_constructor (cls)

          "send member items"
          if cls.members != None :
             for item in cls.members.items :
                 if item.kind == visibilityDecl :
                    pass
                 elif item.kind == simpleDecl :
                    self.send_simple_declaration (item)

          "methods defined outside class"
          for item in cls.implementation_list :
              self.send_simple_item (item)

          "additional (generated) methods"
          for method in cls.methods :
              self.addBlockItem ()
              self.send ("def")
              self.send (method.name)
              self.send ("(")
              self.send ("self")
              self.send (")")
              self.send (":")
              self.style_new_line ()
              self.style_indent ()
              if method.body == None : # !?
                 self.send ("pass")
              else :
                 self.send_compound_stat (method.body)
              self.style_unindent ()
              self.style_empty_line ()

          self.closeBlock ()
          self.style_unindent ()
          self.style_empty_line ()
          self.closeSection ()
          self.class_stack.pop ()

   def send_base_specifier_list (self, param) :
       first = True
       for item in param.items :
          if not first :
             self.send (",")
          first = False
          self.send_base_specifier (item)

   def send_base_specifier (self, param) :
       self.send_qualified_name (param.from_cls)

   def send_ctor_initializer (self, param) :
       for item in param.items :
          self.send_member_initializer (item)

   def send_member_initializer (self, param) :
       self.send_qualified_name (param.qual_name)
       self.send ("=")
       self.send_expr_list (param.params) # !?
       self.style_new_line ()

   # -----------------------------------------------------------------------

   def send_empty_declaration (self, param) :
       pass

   def send_enum_declaration (self, param) :
       pass

   def send_namespace_declaration (self, ns) :
       if self.ignore_skip or not ns.skip_code :
          self.send_declaration_list (ns.members)

   # -----------------------------------------------------------------------

   def send_type_specifiers (self, param) :
       "type conversion used in expressions"

       if param.a_short or param.a_int or param.a_long :
          self.send ("int")
       elif param.a_bool :
          self.send ("bool")
       elif param.a_char == True :
          self.send ("char")
       elif param.a_wchar == True :
          self.send ("wchar_t")
       elif param.a_float == True :
          self.send ("float")
       elif param.a_double == True :
          self.send ("double")
       elif param.a_void == True :
          self.send ("void")

   def send_type_id (self, param) :
       self.send_type_specifiers (param.type_spec)
       # self.send_abstract_declarator (param.declarator)

   # -----------------------------------------------------------------------

   def send_expr (self, expr) :
       if expr.kind == simpleName :
          self.send_qualified_name (expr)
       if expr.kind == globalName :
          self.send_qualified_name (expr)
       if expr.kind == compoundName:
          self.send_qualified_name (expr)
       if expr.kind == intValue :
          self.send (expr.value)
       if expr.kind == realValue :
          self.send (expr.value)
       if expr.kind == charValue :
          self.sendChr (expr.value)
       if expr.kind == stringValue:
          self.sendStr (expr.value)
          for item in expr.items :
             self.sendStr (item.value)
       if expr.kind == thisExpr:
          self.send ("self")
       if expr.kind == subexprExpr:
          self.send ("(")
          self.send_expr (expr.param)
          self.send (")")
       if expr.kind == modernCastExpr :
          self.send_expr (expr.param)
       if expr.kind == typeIdExpr:
          self.send ("typeid")
          self.send ("(")
          self.send_expr (expr.value)
          self.send (")")
       if expr.kind == typeName:
          self.send ("typename")
          self.send_qualified_name (expr.qual_name)
       if expr.kind == typeSpec :
          self.send_type_specifiers (expr)
       if expr.kind == indexExpr:
          self.send_expr (expr.left)
          self.send ("[")
          self.send_expr (expr.param)
          self.send ("]")
       if expr.kind == callExpr:
          self.send_expr (expr.left)
          self.send ("(")
          self.send_expr_list (expr.param_list)
          self.send (")")
       if expr.kind == fieldExpr:
          self.send_expr (expr.left)
          self.put_dot ()
          self.put_dot_name (expr, expr.field_name)
       if expr.kind == ptrFieldExpr:
          self.send_expr (expr.left)
          self.put_dot ()
          self.put_dot_name (expr, expr.field_name)
       if expr.kind == postIncExpr:
          self.send_expr (expr.left)
          self.send ("+=")
          self.send ("1")
       if expr.kind == postDecExpr:
          self.send_expr (expr.left)
          self.send ("-=")
          self.send ("1")
       if expr.kind == incExpr:
          self.send ("++")
          self.send_expr (expr.param)
       if expr.kind == decExpr:
          self.send ("--")
          self.send_expr (expr.param)
       if expr.kind == derefExpr:
          self.send ("*")
          self.send_expr (expr.param)
       if expr.kind == addrExpr:
          # self.send ("&")
          self.send_expr (expr.param)
       if expr.kind == plusExpr:
          self.send ("+")
          self.send_expr (expr.param)
       if expr.kind == minusExpr:
          self.send ("-")
          self.send_expr (expr.param)
       if expr.kind == bitNotExpr:
          self.send ("~")
          self.send_expr (expr.param)
       if expr.kind == logNotExpr:
          self.send ("not")
          self.send_expr (expr.param)
       if expr.kind == sizeofExpr:
          self.send ("sizeof")
          self.send ("(")
          self.send_expr (expr.value)
          self.send (")")
       if expr.kind == newExpr:
          # send ("new")
          if expr.type1 != None :
             self.send_expr (expr.type1.type_spec)
          elif expr.type2 != None :
             self.send ("(")
             self.send_type_id (expr.type2)
             self.send (")")
          self.send ("(")
          if expr.init_list != None :
             self.send_expr_list (expr.init_list)
          self.send (")")
       if expr.kind == deleteExpr:
          self.send ("delete")
          if expr.a_array == True :
             self.send ("[")
             self.send ("]")
          self.send_expr (expr.param)
       # if expr.kind == typecastExpr:
       #    self.send ("type_cast")
       #    self.send ("<")
       #    self.send_type_id (expr.type)
       #    self.send (">")
       #    self.send ("(")
       #    self.send_expr (expr.param)
       #    self.send (")")
       if expr.kind == dotMemberExpr :
          self.send_expr (expr.left)
          self.send (".*")
          self.send_expr (expr.right)
       if expr.kind == arrowMemberExpr :
          self.send_expr (expr.left)
          self.send ("->*")
          self.send_expr (expr.right)
       if expr.kind == mulExpr :
          self.send_expr (expr.left)
          self.send ("*")
          self.send_expr (expr.right)
       if expr.kind == divExpr :
          self.send_expr (expr.left)
          self.send ("/")
          self.send_expr (expr.right)
       if expr.kind == modExpr :
          self.send_expr (expr.left)
          self.send ("%")
          self.send_expr (expr.right)
       if expr.kind == addExpr :
          self.send_expr (expr.left)
          self.send ("+")
          self.send_expr (expr.right)
       if expr.kind == subExpr :
          self.send_expr (expr.left)
          self.send ("-")
          self.send_expr (expr.right)
       if expr.kind == shlExpr :
          self.send_expr (expr.left)
          self.send ("<<")
          self.send_expr (expr.right)
       if expr.kind == shrExpr :
          self.send_expr (expr.left)
          self.send (">>")
          self.send_expr (expr.right)
       if expr.kind == ltExpr :
          self.send_expr (expr.left)
          self.send ("<")
          self.send_expr (expr.right)
       if expr.kind == gtExpr :
          self.send_expr (expr.left)
          self.send (">")
          self.send_expr (expr.right)
       if expr.kind == leExpr :
          self.send_expr (expr.left)
          self.send ("<=")
          self.send_expr (expr.right)
       if expr.kind == geExpr :
          self.send_expr (expr.left)
          self.send (">=")
          self.send_expr (expr.right)
       if expr.kind == eqExpr :
          self.send_expr (expr.left)
          self.send ("==")
          self.send_expr (expr.right)
       if expr.kind == neExpr :
          self.send_expr (expr.left)
          self.send ("!=")
          self.send_expr (expr.right)
       if expr.kind == bitAndExpr :
          self.send_expr (expr.left)
          self.send ("&")
          self.send_expr (expr.right)
       if expr.kind == bitXorExpr :
          self.send_expr (expr.left)
          self.send ("^")
          self.send_expr (expr.right)
       if expr.kind == bitOrExpr :
          self.send_expr (expr.left)
          self.send ("|")
          self.send_expr (expr.right)
       if expr.kind == logAndExpr :
          self.send_expr (expr.left)
          self.send ("and")
          self.send_expr (expr.right)
       if expr.kind == logOrExpr :
          self.send_expr (expr.left)
          self.send ("or")
          self.send_expr (expr.right)
       if expr.kind == assignExpr :
          if expr.left.kind == mulExpr : # !? pointer declaration with unknown type
             self.send_expr (expr.left.right)
          else :
             self.send_expr (expr.left)
          if expr.extra_assign :
             self.send (":=")
          else :
             self.send ("=")
          self.send_expr (expr.right)
       if expr.kind == addAssignExpr :
          self.send_expr (expr.left)
          self.send ("+=")
          self.send_expr (expr.right)
       if expr.kind == subAssignExpr :
          self.send_expr (expr.left)
          self.send ("-=")
          self.send_expr (expr.right)
       if expr.kind == mulAssignExpr :
          self.send_expr (expr.left)
          self.send ("*=")
          self.send_expr (expr.right)
       if expr.kind == divAssignExpr :
          self.send_expr (expr.left)
          self.send ("/=")
          self.send_expr (expr.right)
       if expr.kind == modAssignExpr :
          self.send_expr (expr.left)
          self.send ("%=")
          self.send_expr (expr.right)
       if expr.kind == shlAssignExpr :
          self.send_expr (expr.left)
          self.send ("<<=")
          self.send_expr (expr.right)
       if expr.kind == shrAssignExpr :
          self.send_expr (expr.left)
          self.send (">>=")
          self.send_expr (expr.right)
       if expr.kind == andAssignExpr :
          self.send_expr (expr.left)
          self.send ("&=")
          self.send_expr (expr.right)
       if expr.kind == xorAssignExpr :
          self.send_expr (expr.left)
          self.send ("^=")
          self.send_expr (expr.right)
       if expr.kind == orAssignExpr :
          self.send_expr (expr.left)
          self.send ("|=")
          self.send_expr (expr.right)
       if expr.kind == condExpr :
          self.send ("(") # !?
          self.send_expr (expr.middle)
          self.send ("if")
          self.send_expr (expr.left)
          self.send ("else")
          self.send_expr (expr.right)
          self.send (")")
       # if expr.kind == colonExpr :
       #    self.send_expr (expr.left)
       #    self.send (":")
       #    self.send_expr (expr.right)
       if expr.kind == commaExpr :
          self.send_expr (expr.left)
          self.send (",")
          self.send_expr (expr.right)
       if expr.kind == throwExpr:
          self.send ("throw")
          if expr.param != None :
             self.send_expr (expr.param)

   # -----------------------------------------------------------------------

   def send_stat (self, stat) :
       if self.ignore_skip or not getattr (stat, "skip_code", False) :
          self.put_stat (stat)

   def put_stat (self, stat) :
       if stat.kind == simpleStat :
          self.send_simple_stat (stat)
       elif stat.kind == simpleDecl :
          self.send_simple_declaration (stat)
       # elif stat.kind == emptyStat :
       #    self.send_empty_stat (stat) # no pass, see openBlock, closeBlock
       # elif stat.kind == labeledStat :
       #    self.send_label_stat (stat)
       elif stat.kind == compoundStat :
          self.send_compound_stat (stat)
       elif stat.kind == caseStat :
          self.send_case_stat (stat)
       elif stat.kind == defaultStat :
          self.send_default_stat (stat)
       elif stat.kind == ifStat :
          self.send_if_stat (stat)
       elif stat.kind == switchStat :
          self.send_switch_stat (stat)
       elif stat.kind == whileStat :
          self.send_while_stat (stat)
       elif stat.kind == doStat :
          self.send_do_stat (stat)
       elif stat.kind == forStat :
          self.send_for_stat (stat)
       elif stat.kind == breakStat :
          self.send_break_stat (stat)
       elif stat.kind == continueStat :
          self.send_continue_stat (stat)
       elif stat.kind == returnStat :
          self.send_return_stat (stat)
       elif stat.kind == gotoStat :
          self.send_goto_stat (stat)
       elif stat.kind == tryStat :
          self.send_try_stat (stat)

       elif stat.kind == extensionStat :
          self.send_extension_stat (stat)

   def send_extension_stat (self, stat) :
       pass

   # -----------------------------------------------------------------------

   def send_declaration (self, decl) :
       if decl.kind == classDecl :
          self.send_class_declaration (decl)
       elif decl.kind == enumDecl :
          self.send_enum_declaration (decl)
       # elif decl.kind == typedefDecl) :
       #    self.send_typedef_declaration (decl)
       # elif decl.kind == friendDecl :
       #    self.send_friend_declaration (decl)
       elif decl.kind == namespaceDecl :
          self.send_namespace_declaration (decl)
       # elif decl.kind == externDecl :
       #    self.send_extern_declaration (decl)
       # elif decl.kind == usingDecl :
       #    self.send_using_declaration (decl)
       # elif decl.kind == templateDecl :
       #   send_template_declaration (decl)
       else :
          self.send_stat (decl)

   # -----------------------------------------------------------------------

   def send_declaration_list (self, param) :
       for item in param.items :
          self.send_declaration (item)

   def send_program (self, param) :
       self.send_declaration_list (param)

# --------------------------------------------------------------------------

class ToInitPy (ToPy) :

   def __init__ (self) :
       super (ToInitPy, self).__init__ ()

   # -----------------------------------------------------------------------

   def custom_with_statement (self, stat) :
       done = False

       expr = stat.inner_expr
       if expr.alt_connect != "" :
          self.custom_connect (expr)
          done = True

       if not done :
          self.send_compound_statements (stat.body)

   # -----------------------------------------------------------------------

   def custom_variable_block (self, var) :
       self.send_compound_statements (var.item_body)

  # -----------------------------------------------------------------------

   def custom_default_constructor (self, cls) :
       "lookup constructors"
       any = False
       for item in cls.item_list :
           if getattr (item, "is_constructor", False) :
              any = True
       if not any :
          self.addBlockItem ()
          self.default_constructor (cls)

   def default_constructor (self, cls, add_parent = False) :
       self.send ("def")
       self.send ("__init__")
       self.send ("(")
       self.send ("self")
       if add_parent :
          self.send (",")
          self.send ("parent")
          self.send ("=")
          self.send ("None")
       self.send (")")
       self.send (":")
       self.style_new_line ()
       self.style_indent ()
       self.openBlock ()
       self.constructor_initializers (cls, None) # call custom_constructor_statements
       self.closeBlock ()
       self.style_unindent ()
       self.style_empty_line ()

   # -----------------------------------------------------------------------

   def custom_constructor_statements (self, block, init_vars) :
       "additional constructor initialization"
       for stat in block.items :
          if stat.kind in [simpleStat, ifStat, forStat, whileStat, doStat, switchStat] :
             self.send_stat (stat)
             # self.style_empty_line ()

          if stat.kind == simpleDecl :
             for var in stat.items :
                 if not var.is_function :

                    if var.item_body != None :
                       self.comment (var.item_name)

                    if var.item_name not in init_vars :
                       self.addBlockItem ()
                       self.custom_prefix (var)
                       self.put_name (var)

                       self.variable_initialization (var)
                       self.style_new_line ()
                       self.custom_variable_setup (var)

                    if var.item_body != None :
                       self.custom_constructor_statements (var.item_body, init_vars)
                       self.style_empty_line ()

# --------------------------------------------------------------------------

class ToQtPy (ToInitPy) :

   def __init__ (self) :
       super (ToQtPy, self).__init__ ()

   def custom_prefix (self, obj) :
       ctx = obj.item_context
       objects = [ ]
       while ctx != None and not isinstance (ctx, Class) and not ctx.independent_scope :
          if getattr (ctx, "is_function", False) : # !?
             ctx = None
          else:
             if not ctx.hidden_scope : # !?
                objects.insert (0, ctx)
             ctx = ctx.item_context
       # if ctx != None and not ctx.independent_scope :
       if isinstance (ctx, Class) :
          self.send ("self")
          self.put_dot ()
       for obj in objects :
           self.put_name (obj)
           self.put_dot ()

   # -----------------------------------------------------------------------

   def custom_assign (self, expr) :
       done = False

       if expr.alt_connect != "" :
          self.custom_connect (expr)
          done = True

       special = expr.alt_assign
       if special != "" and not done :
          self.custom_prefix (expr.left.item_decl)
          self.send (special)
          self.send ("(")

          if expr.alt_assign_index != "" :
             self.send (expr.alt_assign_index)
             self.send (",")

          param = expr.alt_assign_param
          if param == "<icon>" :
             self.send ("QIcon")
             self.put_dot ()
             self.send ("fromTheme")
             self.send ("(")
             self.send_expr (expr.right)
             self.send (")")
          elif param == "<color>":
             self.send ("QColor")
             self.send ("(")
             self.send_expr (expr.right)
             self.send (")")
          # elif param == "<shortcut>" :
          #    self.send ("QKeySequence")
          #    self.send ("(")
          #    self.send_expr (expr.right)
          #    self.send (")")
          else :
             self.send_expr (expr.right)

          self.send (")")
          self.style_new_line ()
          done = True

       return done

   # -----------------------------------------------------------------------

   def custom_connect (self, expr) :
       self.addBlockItem ()
       self.send_expr (expr.alt_connect_expr)
       self.put_dot ()
       self.send ("connect")
       self.send ("(")
       self.send ("self")
       self.put_dot ()
       self.send (expr.alt_connect)
       self.send (")")
       self.style_new_line ()

   # -----------------------------------------------------------------------

   def put_place (self, var) :
       if isinstance (var.item_place, Class) :
          self.send ("self")
       elif var.item_place == None : # !?
          self.send ("self")
       elif var.item_place != None :
          self.custom_prefix (var.item_place)
          self.put_name (var.item_place)

   def put_variable (self, var) :
       self.custom_prefix (var)
       self.put_name (var)

   def custom_variable_initialization (self, var) :
       done = False
       special = var.alt_create
       if special == "" :
          special = var.alt_init

       if special != "" :
          if special.startswith ("<") :
              if special == "<menuBar>" :
                 self.send ("self.menuBar ()")
                 done = True
              elif special == "<addToolBar>" :
                 self.send ("self.addToolBar (\"\")")
                 done = True
              elif special == "<statusBar>" :
                 self.send ("self.statusBar ()")
                 done = True
              elif special == "<addMenu>" :
                 self.send ("self.addMenu (\"\")")
                 done = True
              elif special == "<addAction>" :
                 self.send ("self.addAction (\"\")")
                 done = True

              elif special == "<empty_qstring>" :
                 if use_py2_qt4 :
                     self.send ("QString ()")
                 else :
                     self.send ("\"\"")
                 done = True

              elif special == "<empty_qstringlist>" :
                 if use_py2_qt4 :
                    self.send ("QStringList ()")
                 else :
                    self.send ("[ ]")
                 done = True

              elif special == "<empty_qlist>" :
                 self.send ("[ ]")
                 done = True

              elif special == "<empty_qvector>" :
                 self.send ("[ ]")
                 done = True

              elif special == "<empty_qmap>" :
                 self.send ("{ }")
                 done = True

          else :
             self.send (special)
             self.send ("(")
             if var.alt_create_owner :
                self.send ("self")
             if var.alt_create_place :
                self.put_place (var)
             self.send (")")
             done = True

       if not done :
          type_name = self.get_foreign_type (var)
          if type_name == "QJsonObject" :
             self.send ("{")
             self.send ("}")
             done = True
          if type_name == "QJsonArray" :
             self.send ("[")
             self.send ("]")
             done = True


       return done

   def custom_variable_setup (self, var) :

       special = var.alt_setup
       if special != "" :
          if special == "<layout>" :
             self.send ("temp = QWidget (self)")
             self.style_new_line ()
             self.send ("temp.setLayout (")
             self.put_variable (var)
             self.send (")")
             self.style_new_line ()
             self.send ("self.setCentralWidget (temp)")
             self.style_new_line ()
          elif special == "<setCentralWidget>"  :
             self.send ("self.setCentralWidget (")
             self.put_variable (var)
             self.send (")")
             self.style_new_line ()
          else :
             func_name = var.alt_setup
             func_param = var.alt_setup_param
             self.put_place (var)
             self.put_dot ()
             self.send (func_name)
             self.send ("(")
             self.put_variable (var)
             if func_param != "" :
                self.send (",")
                self.send (func_param)
             self.send (")")
             self.style_new_line ()

   # -----------------------------------------------------------------------

   def get_name (self, qual_name) :
       result = ""

       if qual_name.kind == simpleName :
          result = qual_name.id
       elif qual_name.kind == specialName :
          result = qual_name.spec_func.spec_name # !?
       elif qual_name.kind == compoundName :
          result = self.get_name (qual_name.left) + "." + self.get_name (qual_name.right)
       elif qual_name.kind == globalName :
           result = "::" + self.get_name (qual_name.inner_name)
       elif qual_name.kind == destructorName :
           result = "~" + self.get_name (qual_name.inner_name)
       elif qual_name.kind == templateName or qual_name.kind == compoundName and qual_name.template_args != None :
        result = self.get_name (qual_name.left) + "<???>" # !?

       if result == "" :
          result = "???"
       return result

   def get_expr_name (self, expr) :
       return self.get_name (expr)

   # -----------------------------------------------------------------------

   def get_declarator_name (self, declarator) :
       result = ""
       while declarator != None :
          if declarator.kind in [nestedDeclarator, pointerDeclarator, referenceDeclarator, arrayDeclarator, functionDeclarator] :
             declarator = declarator.inner_declarator
          else :
             if declarator.kind == basicDeclarator :
                result = self.get_name (declarator.qual_name)
             declarator = None
       return result

   def get_foreign_type (self, expr) :
       type_name = ""
       if getattr (expr, "item_type", None) != None :
          type = expr.item_type
          if isinstance (type, ReferenceType) :
             type = type.type_from

          if type != None and getattr (type, "type_decl", None) != None :
             type_decl = type.type_decl
             if type_decl.item_context.item_qual == "(foreign)" : # !?
                type_name = type_decl.item_name
       return type_name

   def expr_in_parenthesis (self, expr) :
       if expr.kind in [ simpleName, compoundName, globalName, thisExpr, subexprExpr,
                         intValue, realValue, charValue, stringValue ] :
          self.send_expr (expr)
       else :
          self.send ("(")
          self.send_expr (expr)
          self.send (")")

   def shl_expr (self, expr) :
       done = False

       if expr.left.kind == shlExpr :
          target = expr
          params = [ ]
          while target.kind == shlExpr :
             params.insert (0, target.right)
             target = target.left
          if self.get_foreign_type (target) == "QStringList" :
             self.send_expr (target)
             if len (params) == 1 :
                self.put_dot ()
                self.send ("append")
                self.send ("(")
                self.send_expr (params [0])
                self.send (")")
             else :
                self.send ("+=")
                self.send ("[")
                first = True
                for param in params :
                    if first :
                       first = False
                    else :
                       self.send (",")
                    self.send_expr (param)
                self.send ("]")
             done = True

       # elif self.get_foreign_type (expr.left) == "QStringList" :
       #    self.send_expr (expr.left)
       #    self.put_dot ()
       #    self.send ("append")
       #    self.send ("(")
       #    self.send_expr (expr.right)
       #    self.send (")")
       #    done = True

       # elif expr.left.kind == simpleName and expr.left.id == "cout" : # !?
       #    self.send ("print")
       #    self.send ("(")
       #    self.send_expr (expr.right)
       #    self.send (")")
       #    done = True

       return done

   def without_func (self, func_name, expr) :
       # remove func_name ( )
       if expr.kind == callExpr :
          if expr.left.kind == simpleName and expr.left.id == func_name :
             params = expr.param_list
             if len (params.items) == 1 :
                expr = params.items [0]

                # remove function call without parameters
                if expr.kind == callExpr :
                   params = expr.param_list
                   if len (params.items) == 0 :
                      expr = expr.left

       elif expr.kind == signalSlotExpr :
       # elif getattr (expr, "macro_name", "") != "" :
          self.put (expr.func_name)

       else :
          self.send_expr (expr)

   def connect_func (self, expr) :
       result = False
       if expr.kind == simpleName :
          name = expr.id
          if name == "connect" :
             result = True
       elif expr.kind == compoundName :
          left = expr.left
          right = expr.right
          if left.kind == simpleName :
             if left.id == "QObject" :
                if right.kind == simpleName :
                   if right.id == "connect" :
                      print ("CONNECT")
                      self.putLn ("# CONNECT")
                      result = True
       return result

   def call_expr (self, expr) :
       done = False
       params = expr.param_list
       cnt = len (params.items)

       if expr.left.alt_display != "" :
          if cnt == 1 :
             self.send_expr (expr.left.left)
             self.put_dot ()
             self.send (expr.left.alt_display)
             self.send ("(")
             self.send_expr (params.items [0])
             self.send (")")
             done = True

       if expr.left.alt_store != "" :
          if cnt == 1 :
             self.send_expr (params.items [0])
             self.send ("=")
             self.send_expr (expr.left.left)
             self.put_dot ()
             self.send (expr.left.alt_store)
             self.send ("(")
             self.send (")")
             done = True

       if expr.left.alt_read_json != "" :
          if cnt == 2 :
             # obj.read (name, value)
             # value = obj[name].conv_func()
             self.send_expr (params.items [1])
             self.send ("=")
             self.send_expr (expr.left.left)
             self.send ("[")
             self.send_expr (params.items [0])
             self.send ("]")
             self.put_dot ()
             self.send (expr.left.alt_read_json)
             self.send ("(")
             self.send (")")
             done = True

       if expr.left.alt_write_json != "" :
          if cnt == 2 :
             # obj.write (name, value)
             # obj[name] = value
             self.send_expr (expr.left.left)
             self.send ("[")
             self.send_expr (params.items [0])
             self.send ("]")
             self.send ("=")
             self.send_expr (params.items [1])
             done = True

       if expr.left.alt_read_xml != "" :
          if cnt == 2 :
             # obj.read (name, val)
             # if (obj.hasAttribute (name)) { val = obj.value(name).conv_func(); }
             self.put ("if")
             self.put ("(")

             self.send_expr (expr.left.left)
             self.put_dot ()
             self.send ("hasAttribute")
             self.send ("(")
             self.send_expr (params.items [0])
             self.send (")")

             self.put (")")

             self.put ("{")

             self.send_expr (params.items [1])
             self.send ("=")
             self.send_expr (expr.left.left)
             self.put_dot ()
             self.send ("value")
             self.send ("(")
             self.send_expr (params.items [0])
             self.send (")")
             self.put_dot ()
             self.send (expr.left.alt_read_xml)
             self.send ("(")
             self.send (")")

             self.put (";")
             self.put ("}")
             done = True

       if expr.left.alt_write_xml != "" :
          if cnt == 2 :
             # obj.write (name, value)
             # obj.writeAttribute (name, value)
             self.send_expr (expr.left.left)
             self.put_dot ()
             self.send ("writeAttribute")
             self.send ("(")
             self.send_expr (params.items [0])
             self.send (",")
             self.send_expr (params.items [1])
             self.send (")")
             done = True

       "QString::number"
       if expr.left.kind == compoundName :
          name = self.get_name (expr.left)
          if name == "QString.number" :
             self.send ("str")
             self.send ("(")
             self.send_expr_list (params)
             self.send (")")
             done = True
          elif name == "QFileDialog.getOpenFileName" or name == "QFileDialog.getSaveFileName":
             self.send_expr (expr.left)
             self.send ("(")
             self.send_expr_list (params)
             self.send (")")
             self.send ("[")
             self.send ("0")
             self.send ("]")
             done = True

       "QString ()"
       if expr.left.kind == simpleName :
          if expr.left.id == "QString" :
             self.send ("str")
             self.send ("(")
             self.send_expr_list (params)
             self.send (",")
             self.send (quoteString ("latin1"))
             self.send (",")
             self.send ("errors")
             self.send ("=")
             self.send (quoteString ("ignore"))
             self.send (")")
             done = True

       "connect"
       if self.connect_func (expr.left) :
          if cnt == 3 :
             self.send_expr (params.items [0])
             self.put_dot ()
             self.without_func ("SIGNAL", params.items [1])
             self.put_dot ()
             self.send ("connect")
             self.send ("(")
             self.without_func ("SLOT", params.items [2])
             self.send (")")
             done = True
          if cnt == 4 :
             self.send_expr (params.items [0])
             self.put_dot ()
             self.without_func ("SIGNAL", params.items [1])
             self.put_dot ()
             self.send ("connect")
             self.send ("(")
             self.send_expr (params.items [2])
             self.put_dot ()
             self.without_func ("SLOT", params.items [3])
             self.send (")")
             done = True

       "super"
       if expr.left.class_member != None :
          self.send ("super")
          self.send ("(")
          self.send (expr.left.class_member.item_name) # !?
          self.send (",")
          self.send ("self") # !?
          self.send (")")
          self.put_dot ()
          self.send_expr (expr.left.right)
          self.send ("(")
          self.send_expr_list (expr.param_list)
          self.send (")")
          done = True

       "target.field (params)"
       if expr.left.kind == fieldExpr :
          target = expr.left.left
          field_name = expr.left.field_name
          field = field_name.id

          type_name = self.get_foreign_type (target)
          subst = ""
          # expr.see_type_name = type_name
          # expr.see_name = field

          byte_array_type = (type_name == "QByteArray")
          string_type = (type_name == "QString")
          list_type = (type_name == "QList")
          string_list_type = (type_name == "QStringList")
          variant_type = (type_name == "QVariant")

          if string_type or byte_array_type :
             if cnt == 0 :
                if field == "trimmed" :
                   subst = "strip"
             if cnt == 1 :
                if field == "startsWith" :
                   subst = "startswith"
                if field == "endsWith" :
                   subst = "endswith"
             if field == "indexOf" and (cnt == 1 or cnt == 2) :
                subst = "find"

          if string_type :
             if field == "toLatin1" and cnt == 0 :
                self.send ("bytes")
                self.send ("(")
                self.send_expr (target)
                self.send (",")
                self.send ("encoding")
                self.send ("=")
                self.send (quoteString ("latin1"))
                self.send (")")
                done = True

          if string_type or byte_array_type :
             if field == "length" :
                if cnt == 0 :
                   self.send ("len")
                   self.send ("(")
                   self.send_expr (target)
                   self.send (")")
                   done = True

          if list_type or string_list_type :
             if field == "indexOf" and (cnt == 1 or cnt == 2) :
                subst = "index"
             if field == "length" or field == "size" or field == "count" :
                if cnt == 0 :
                   self.send ("len")
                   self.send ("(")
                   self.send_expr (target)
                   self.send (")")
                   done = True
             if field == "at"  and cnt == 1 :
                self.send_expr (target)
                self.send ("[")
                self.send_expr (params.items [0])
                self.send ("]")
                done = True

          if string_type or byte_array_type or list_type or string_list_type  :
             if field == "mid" :
                if cnt == 2 :
                   self.send_expr (target)
                   self.send ("[")
                   self.send_expr (params.items [0])
                   self.send (":")
                   self.expr_in_parenthesis (params.items [0])
                   self.send ("+")
                   self.expr_in_parenthesis (params.items [1])
                   self.send ("]")
                   done = True
             if field == "isEmpty" :
                if cnt == 0 :
                   self.send ("len")
                   self.send ("(")
                   self.send_expr (target)
                   self.send (")")
                   self.send ("==") # !?
                   self.send ("0")
                   done = True

          if string_type or byte_array_type or list_type or string_list_type or type_name == "QJsonObject" :
             if cnt == 1 :
                if field == "contains" :
                   self.send ("(")
                   self.expr_in_parenthesis (params.items [0])
                   self.send ("in")
                   self.send_expr (target)
                   self.send (")")
                   done = True

          if string_type or byte_array_type :
             if cnt == 1 :
                if field == "left" :
                   self.send_expr (target)
                   self.send ("[")
                   self.send (":")
                   self.expr (params.items [0])
                   self.send ("]")
                   done = True
                if field == "right" :
                   self.send_expr (target)
                   self.send ("[")
                   self.send (":")
                   self.send ("-")
                   self.expr_in_parenthesis (params.items [0])
                   self.send ("]")
                   done = True

          if variant_type :
             # expr.see_variant = 1
             if cnt == 0 :
                if field in ["toBool", "toString", "toInt", "toDouble", "value"] :
                   self.send_expr (target)
                   done = True
          """
          subst_instance = ""
          subst_func = ""
          if target.kind == indexExpr :
             "target[index].field (params)"
             base_type_name = self.get_foreign_type (target.left)
             if base_type_name == "QJsonObject" :
                if cnt == 0 :
                   if field == "isArray" :
                      subst_instance = "list"
                   elif field == "isBool" :
                      subst_instance = "bool"
                   elif field == "isDouble" :
                      subst_instance = "float"
                   elif field == "isString" :
                      subst_instance = "str"
                   elif field == "toArray" :
                      subst_func = "list"
                   elif field == "toBool" :
                      subst_func = "bool"
                   elif field == "toInt" :
                      subst_func = "int"
                   elif field == "toDouble" :
                      subst_func = "float"
                   elif field == "toString" :
                      subst_func = "str"
                   elif field == "toObject" :
                      self.send_expr (target)
                      done = True
                if cnt == 1 :
                   if field == "toInt" :
                      subst_func = "int"
                   elif field == "toDouble" :
                      subst_func = "float"

          if subst_instance != "" :
             self.send ("isinstance")
             self.send ("(")
             self.send_expr (target)
             self.send (",")
             self.send (subst_instance)
             self.send (")")
             done = True

          if subst_func != "" :
             self.send (subst_func)
             self.send ("(")
             self.send_expr (target)
             self.send (")")
             done = True
          """

          if subst != "" :
             self.send_expr (target)
             self.put_dot ()
             self.send (subst)
             self.send ("(")
             self.send_expr_list (params)
             self.send (")")
             done = True

       return done

   def field_or_ptr_expr (self, expr) :
       done = False

       if expr.var_field or expr.str_field :
          self.send_expr (expr.left)
          done = True

       if expr.field_name.id == "exec" :
          if not use_qt6 :
             self.send_expr (expr.left)
             self.put_dot ()
             self.send ("exec_")
             done = True

       if expr.field_name.id == "raise" :
          self.send_expr (expr.left)
          self.put_dot ()
          self.send ("raise_")
          done = True

       return done

   def new_expr (self, expr) :
       done = False
       "new QApplication (argc, argv)"
       if expr.type1 != None :
          if str (getattr (expr.type1.type_spec, "id", "")) == "QApplication" : # !?
             params = [ ]
             for item in expr.init_list.items :
                 name = self.get_expr_name (item)
                 params.append (name)
             if params == ["argc", "argv"] :
                self.send ("QApplication (sys.argv)")
                done = True
       return done

   def delete_expr (self, expr) :
       done = True
       self.send_expr (expr.param)
       self.send ("=")
       self.send ("None")
       self.send (";")
       return done

   def modern_cast_expr (self, expr) :
       done = False
       if expr.cast_kind == dynamicCast :
          """
          self.send ("dynamic_cast")
          self.send ("(")
          self.send_expr (expr.type.type_spec)
          self.send (",")
          self.send_expr (expr.param)
          self.send (")")
          """
          self.send ("(")
          self.send_expr (expr.param)
          self.send ("if")
          self.send ("isinstance")
          self.send ("(")
          self.send_expr (expr.param)
          self.send (",")
          self.send_expr (expr.type.type_spec)
          self.send (")")
          self.send ("else")
          self.send ("None")
          self.send (")")
          done = True
       return done

   def signal_slot_expr (self, expr) :
       self.send (expr.macro_name)
       self.send ('(')
       self.put ('"') # double quote
       self.put (expr.func_name) # double quote
       if expr.parameters != None :
          self.send ("(")
          first = True
          for item in expr.parameters.items :
              if not first :
                 self.send (",")
              first = False
              self.send_parameter_declaration (item)
          self.send (")")
       self.put ('"')
       self.send (')')

   def send_expr (self, expr) :
       done = False

       "assign"
       if expr.kind == assignExpr :
          done = self.custom_assign (expr)
       "string and list methods"
       if expr.kind == callExpr :
          done = self.call_expr (expr)
       "field"
       if expr.kind == fieldExpr or expr.kind == ptrFieldExpr :
          done = self.field_or_ptr_expr (expr)
       "shift left"
       if expr.kind == shlExpr :
          done = self.shl_expr (expr)
       "new"
       if expr.kind == newExpr :
          done = self.new_expr (expr)
       "delete"
       if expr.kind == deleteExpr :
          done = self.delete_expr (expr)
       "dynamic_cast"
       if expr.kind == modernCastExpr :
          done = self.modern_cast_expr (expr)

       "cast"
       if expr.kind == castExpr :
          self.send_expr (expr.left.param) # !?
          self.send ('(')
          self.send_expr (expr.right)
          self.send (')')

       # if getattr (expr, "macro_name", "") != "" :
       #    self.signal_slot_expr (expr)
       # s   done = True

       if not done :
          super (ToQtPy, self).send_expr (expr)

   # -----------------------------------------------------------------------

   def send_simple_declaration (self, param) :
       "int main (int argc, char * * argv)"
       done = False
       if param.body != None and len (param.items) == 1:
          if param.items[0].item_qual == "main" :
             self.putLn ("if __name__ == '__main__' :")
             self.style_indent ()
             self.send_compound_stat (param.body)
             self.style_unindent ()
             self.style_empty_line ()
             done = True
       if not done :
          super (ToQtPy, self).send_simple_declaration (param)

   def send_imports (self) :

       self.putLn ("#!/usr/bin/env python")
       self.putLn ("")
       self.putLn ("from __future__ import print_function")
       self.putLn ("")
       self.putLn ("import sys")
       self.putLn ("")

       if use_pyside6 :
          self.putLn ("from PySide6.QtCore import *")
          self.putLn ("from PySide6.QtGui import *")
          self.putLn ("from PySide6.QtWidgets import *")
       elif use_pyside2 :
          self.putLn ("from PySide2.QtCore import *")
          self.putLn ("from PySide2.QtGui import *")
          self.putLn ("from PySide2.QtWidgets import *")
       elif use_pyqt6 :
          self.putLn ("from PyQt6.QtCore import *")
          self.putLn ("from PyQt6.QtGui import *")
          self.putLn ("from PyQt6.QtWidgets import *")
       elif use_pyqt5 :
          self.putLn ("from PyQt5.QtCore import *")
          self.putLn ("from PyQt5.QtGui import *")
          self.putLn ("from PyQt5.QtWidgets import *")
       elif 0 :
          self.putLn ("from PyQt4.QtCore import *")
          self.putLn ("from PyQt4.QtGui import *")
       else :
          self.putLn ("try :")
          self.style_indent ()
          self.putLn ("from PyQt5.QtCore import *")
          self.putLn ("from PyQt5.QtGui import *")
          self.putLn ("from PyQt5.QtWidgets import *")
          self.style_unindent ()
          self.putLn ("except :")
          self.style_indent ()
          self.putLn ("from PyQt4.QtCore import *")
          self.putLn ("from PyQt4.QtGui import *")
          self.style_unindent ()
       self.style_empty_line ()

       """
       if self.compiler.using_modern_cast :
          self.putLn ("def dynamic_cast (cls, value) :")
          self.style_indent ()
          self.putLn ("if isinstance (value, cls) :")
          self.style_indent ()
          self.putLn ("return value")
          self.style_unindent ()
          self.putLn ("else :")
          self.style_indent ()
          self.putLn ("return None")
          self.style_unindent ()
          self.style_indent ()
          self.style_unindent ()
          self.putLn ("")
       """

   def send_program (self, param) :
       self.send_imports ()
       super (ToQtPy, self).send_program (param)

# --------------------------------------------------------------------------

class ToExtPy (ToQtPy) :

   def __init__ (self) :
       super (ToExtPy, self).__init__ ()

   def get_expr_value (self, expr) :
       return getattr (expr, "item_value", None)

   def get_cond_value (self, cond) :
       if cond.kind == simpleStat :
          return self.get_expr_value (cond.inner_expr)
       else :
          return None

   def send_expr (self, expr) :
       done = False

       "simple indentifier"
       if expr.kind == simpleName : # !?
          if hasattr (expr, "item_decl")  :
             expr.item_value = self.get_expr_value (expr.item_decl)
             " copy loop parameter "

       "true or false constants"
       value = self.get_expr_value (expr)
       if value != None :
          if isinstance (value, bool) :
             if value == True :
                self.send ("True")
             elif value == False :
                self.send ("False")
          elif isinstance (value, str) :
             self.sendStr (value)
          else :
             self.send (str (value))
          done = True

       " && "
       if expr.kind == logAndExpr :
          left = self.get_expr_value (expr.left)
          if left != None :
             if left :
                self.send_expr (expr.right)
                done = True
             else :
                self.send ("False")
                done = True

       " || "
       if expr.kind == logOrExpr :
          left = self.get_expr_value (expr.left)
          if left != None :
             if not left :
                self.send_expr (expr.right)
                done = True
             else :
                self.send ("True")
                done = True

       "function call"
       if expr.kind == callExpr:
          if getattr (expr, "skip_code", False) :
             done = True
          else :
             decl = getattr (expr.left, "item_decl", None)
             if decl != None :
                if getattr (decl, "mod_call", None) != None :
                   call = decl.mod_call
                   call (self, expr)
                   done = True
                   # expr.skip_semicolon = True

       if not done :
          super (ToExtPy, self). send_expr (expr)

   # -----------------------------------------------------------------------

   def send_if_stat (self, stat) :
       done = False

       value = self.get_cond_value (stat.cond)
       if value != None :
          if value :
             self.send_stat (stat.then_stat)
             done = True
          else :
             if stat.else_stat != None :
                self.send_stat (stat.else_stat)
             done = True

       if not done :
          super (ToExtPy, self). send_if_stat (stat)

   def send_for_stat (self, stat) :
       done = False

       target = None
       if stat.from_expr != None :
          expr = stat.from_expr
          target = getattr (expr, "item_decl", None)

       if stat.iter_expr != None :
          value = self.get_expr_value (stat.iter_expr)
          if value != None:
             for item in value :
                if target != None :
                   target.item_value = item
                self.style_new_line ()
                self.send_stat (stat.body)
             done = True

       if not done :
          super (ToExtPy, self). send_for_stat (stat)

   # -----------------------------------------------------------------------

   def send_simple_item (self, simple_item) :
       obj = simple_item
       if self.ignore_skip or not obj.skip_code :
          super (ToExtPy, self). send_simple_item (simple_item)

   # -----------------------------------------------------------------------

   def parameter_names (self, func) :
       result = [ ]
       if func.kind == functionDeclarator :
          for param in func.parameters.items :
              if param.param_expr != None and param.param_expr.item_value != None : # !?
                 name = param.param_expr.item_value
              else :
                 name = self.get_name (param.type_spec.basic_name)
              result.append (name)
       return result

   def custom_icon (self, cls, func) :
       params = self.parameter_names (func)
       self.send ("self.__icon__")
       self.send ("=")
       self.send (quoteString (params [0]))
       self.putEol ()

   def custom_property (self, cls, func) :
       if not hasattr (cls, "properties") :
          cls.properties = True
          self.putLn ("self._properties_ = []")

       params = self.parameter_names (func)
       self.send ("self._properties_.append")
       self.send ("(")
       self.send (quoteString (params [0]))
       self.send (")")
       self.putEol ()

   def custom_combine (self, cls, func) :
       if not hasattr (cls, "combine") :
          cls.combine = True
          self.putLn ("self.__combine__ = []")

       params = self.parameter_names (func)
       self.send ("self.__combine__.append")
       self.send ("((")
       self.send (quoteString (params [0]))
       self.send (",")
       self.send ("self")
       self.put_dot ()
       self.send (params [1])
       self.send ("))")
       self.putEol ()

   def custom_construction (self, cls):
       for item in cls.item_list :
          if isinstance (item, Variable) and item.is_function :
             func = item
             if func.item_name == "icon_" : # !?
                self.custom_icon (cls, func)
             if func.item_name == "combine" : # !?
                self.custom_combine (cls, func)
             if func.item_name == "property" : # !?
                self.custom_property (cls, func)

   # -----------------------------------------------------------------------

   "CmmExtensionStat"

   def send_extension_stat (self, stat) :
       name = stat.name
       param = stat.param

       if name == "empty_line" :
          self.style_empty_line ()

       elif name == "comment" :
          self.put ("# " + param)
          self.putEol ()

       elif name == "code" :
          if stat.into_expr != None :
             self.send_expr (stat.into_expr)
             self.send (".")
             self.send ("append")
             self.send ("(")

          if stat.store_expr != None :
             self.send_expr (stat.store_expr)
             if stat.into_expr != None :
                self.send (":=") # !? Python 3.8
             else :
                self.send ("=")

          self.send ("code")
          self.send ("(")
          self.indent ()
          self.new_line ()
          for line in stat.ext_source.split ("\n") :
              self.send (quoteString (line))
              self.new_line ()
          self.unindent ()

          if stat.into_expr != None or stat.store_expr != None :
             self.send (",")
             self.send ("no_send")
             self.send ("=")
             self.send ("True")
          self.send (")")

          if stat.into_expr != None :
             self.send (")")
          self.new_line ()

       elif name == "kit_block" :
          for item in stat.items :
              self.send_declaration (item)

       elif name == "nested_module" :
          self.new_line ()
          fileName = param
          self.putLn ("from " + fileName + " import *")
          self.style_empty_line ()

          fileName = fileName + ".py"

          if self.win != None :
             fileName = self.win.outputFileName (fileName)
             self.win.joinProject (fileName)

             print ("WRITE", fileName)
             output = Output ()
             output.open (fileName)
             save_redirect = self.redirect
             self.redirect = output
             self.send_imports ()
             # self.send_compound_statements (stat)
             for item in stat.items :
                 if item.kind != emptyStat :
                    self.send_declaration (item)
             self.redirect = save_redirect
             output.close ()

# --------------------------------------------------------------------------

class ToCustomPy (ToExtPy) :

   def __init__ (self) :
       super (ToCustomPy, self).__init__ ()

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
