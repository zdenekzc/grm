
# cmm_comp.py

from __future__ import print_function

import os, sys, copy, inspect

from util import findColor, get_time, use_py2_qt4, use_qt5, use_qt6

from cmm_parser import *
from cmm_product import *
# from cmm_copy import *

from input import quoteString

from code_base import *
# from code import initItem, initDeclaration, initNamespace, initClass, initEnum, initEnumItem, initVariable, initFunction, initTypedef
# from code import Scope, Method
# from code import SimpleType, NamedType, PointerType, ReferenceType, ArrayType, FunctionType

from grammar import Grammar
from toparser  import ToParser
from toproduct import ToProduct

# --------------------------------------------------------------------------

# import sys
# sys.path.append (os.path.expanduser ("/abc/llvm-python"))
# directory with clang/cindex.py from clang (llvm/tools/clang/binndigs/python/clang)

use_clang = True
try :
   from clang import cindex
   from clang.cindex import Index, Config, CursorKind, TypeKind, TranslationUnit
   from gcc_options import gcc_options, pkg_options
except :
   use_clang = False

from input import fileNameToIndex

# --------------------------------------------------------------------------

class CmmCompiler (Parser) :
   def __init__ (self) :
       super (CmmCompiler, self).__init__ ()
       self._other_properties_ = dir (Parser ())

       self.win = None
       self.edit = None

       self.clang_import = False

       self.global_scope = CmmStatSect ()
       initNamespace (self.global_scope)
       self.global_scope.item_name = ""
       self.global_scope.hidden_scope = True # do not print scope name

       self.display = [ self.global_scope ]

       self.remember_constructor = False # identifier on the beginning of member declaration
       self.remember_tilda = False # tilda on the beginning of member declaration
       self.remember_destructor = False # identifier after tilda

       self.remember_global = False # global GPU keyword
       self.remember_leading = False # first identifier in flexible statement

       self.using_modern_cast = False

       self.cast_import = False

       self.init_types ()

   def compile_program (self) :
       self.storeLocation (self.global_scope) # store file name
       while self.token != self.eos :
          self.global_scope.items.append (self.parse_declaration ())
       return self.global_scope

   # scope

   def enter (self, item) :
       inx = len (self.display) - 1
       scope = self.display [inx]
       while scope.search_only and inx > 0 :
          inx = inx - 1
          scope = self.display [inx]
       if inx < 0 :
          self.error ("All scopes are search-only")
       self.enterIntoScope (scope, item)

       last_scope = self.display [-1]
       if last_scope.search_only :
          item.item_place = last_scope # search only last scope

   def enterIntoScope (self, scope, item) :

       scope.item_dict [item.item_name] = item

       scope.item_list.append (item)

       item.item_context = scope

       if hasattr (scope, "item_qual") and scope.item_qual != None and scope.item_qual != "" :
          item.item_qual = scope.item_qual + "." + item.item_name
       else :
          item.item_qual = item.item_name

       # print ("ENTER", item.item_qual)

   def openScope (self, scope) :
       self.display.append (scope)

   def closeScope (self) :
       self.display.pop ()

   def searchScope (self, scope, name) :
       # if scope.item_name.startswith ("(") :
       #   print ("searchScope", scope.item_qual, name)

       result = scope.item_dict.get (name, None)
       if result == None and scope.search_func != None :
          result = scope.search_func (name)
       return result

   def lookup (self, name) :
       # print ("lookup", name)
       result = None
       inx = len (self.display) - 1
       while result == None and inx >= 0 :
          scope = self.display [inx]
          for item in scope.using_list :
              if result == None : # !?
                 result = self.searchScope (item, name)
          if result == None : # !?
             result = self.searchScope (scope, name)
          inx = inx - 1
       return result

   # register scope

   def register (self, scope, name, item) :
       item.item_name = name
       scope.registered_scopes [name] = item

       item.item_context = scope

       if hasattr (scope, "item_qual") and scope.item_qual != None and scope.item_qual != "" :
          item.item_qual = scope.item_qual + "." + item.item_name
       else :
          item.item_qual = item.item_name

   # with statement scope

   def lookupItemAndOwner (self, name) :
       result = None
       owner = None
       inx = len (self.display) - 1
       while result == None and inx >= 0 :
          scope = self.display [inx]
          for item in scope.using_list :
              if result == None : # !?
                 result = self.searchScope (item, name)
                 if result != None :
                    owner = item
          if result == None : # !?
             result = self.searchScope (scope, name)
             if result != None :
                owner = scope
          inx = inx - 1
       return result, owner

   # compound, if, for, while statement scope

   def createLocalScope (self) :
       top = self.display [-1]
       scope = Scope ()
       top.registered_count = top.registered_count + 1
       self.register (top, "(" + str (top.registered_count) + ")", scope)
       return scope

   def openLocalScope (self, cond = None) :
       top = self.display [-1]
       if not top.search_only : # search_only scope => no local scope, search in outer scopes
          scope = self.createLocalScope ()
          scope.hidden_scope = True
          self.openScope (scope)

          if isinstance (cond, CmmSimpleItem) :
             self.enterIntoScope (scope, cond.item_decl)

   def closeLocalScope (self, cond = None) :
       top = self.display [-1]
       if not top.search_only :
          self.closeScope ()

   # stop searching another file in syntax tree

   def on_expr (self, expr) :
       expr.stop_file_search = True

   def on_declarator (self, declarator) :
       declarator.stop_file_search = True

   # namespace

   def on_start_namespace (self, ns_decl) :
       pass

   def on_namespace (self, module) :
       initNamespace (module)
       module.item_name = module.simp_name.id # store name
       self.clear_declaration (module.simp_name) # remove previous item_decl
       self.copy_name_location (module, module.simp_name) # store location
       self.enter (module) # add identifier into scope
       self.selectColor (module, table = "namespaceColors")
       self.markDefn (module) # set attributes in text editor
       self.markOutline (module)
       self.custom_attributes (module)
       self.custom_namespace (module)

   def on_open_namespace (self, module) :
       self.openScope (module) # scope for identifiers
       self.openCompletion (module) # area with text completion

   def on_close_namespace (self, module) :
       self.closeCompletion (module)
       self.closeScope ()

   def on_stop_namespace (self, module) :
       pass

   # class

   def on_start_class (self, cls) :
       initClass (cls)
       # self.openRegion (cls) # region with background color

   def on_class (self, cls) :
       cls.item_name = cls.simp_name.id
       self.clear_declaration (cls.simp_name)
       self.copy_name_location (cls, cls.simp_name)
       self.enter (cls)
       self.selectColor (cls, table = "classColors")
       self.markDefn (cls)
       self.markOutline (cls)
       self.custom_attributes (cls)
       self.custom_class (cls)

   def on_open_class (self, cls) :
       if cls.base_list != None :
          for item in cls.base_list.items :
              if item.from_cls.item_decl != None :
                 cls.base_classes.append (item.from_cls.item_decl)

       self.custom_open_class (cls)
       self.openScope (cls)
       self.openCompletion (cls)

   def on_close_class (self, cls) :
       cls.end_of_class = CmmBasic () # !?
       self.storeLocation (cls.end_of_class)

       self.closeCompletion (cls)
       self.closeScope ()

   def on_stop_class (self, cls) :
       # self.closeRegion ()
       self.custom_stop_class (cls)

   def on_member_initializer (self, initializer) :
       decl = self.lookup (initializer.simp_name.id)
       initializer.simp_name.item_decl = decl

   # enum

   def on_start_enum (self, enum) :
       initEnum (enum)
       self.openRegion (enum) # region with background color

   def on_enum (self, enum) :
       enum.item_name = enum.simp_name.id
       self.clear_declaration (enum.simp_name)
       self.copy_name_location (enum, enum.simp_name)
       self.enter (enum)
       self.selectColor (enum, table = "enumColors")
       self.markDefn (enum)
       self.markOutline (enum)
       self.custom_attributes (enum)

   def on_open_enum (self, enum) :
       self.openScope (enum)
       self.openCompletion (enum)

   def on_enum_item (self, item) :
       initEnumItem (item)
       item.item_name = item.simp_name.id
       self.clear_declaration (item.simp_name)
       self.copy_name_location (item, item.simp_name)
       self.enter (item)
       self.selectColor (item, table = "variableColors")
       self.markDefn (item)
       self.custom_attributes (item)

   def on_close_enum (self, enum) :
       self.closeCompletion (enum)
       self.closeScope ()

   def on_stop_enum (self, enum) :
       self.closeRegion ()

   # typedef

   def on_typedef (self, typedef) :
       initTypedef (typedef)
       self.clear_declarator (typedef.declarator)
       self.copy_declarator_name (typedef, typedef.declarator)
       self.copy_declarator_location (typedef, typedef.declarator)
       self.enter (typedef)
       self.selectColor (typedef, table = "typedefColors")
       self.markDefn (typedef)
       self.markOutline (typedef)
       self.custom_attributes (typedef)

   # using

   def on_using (self, using_declaration) :
       if using_declaration.a_namespace : # !?
          decl = using_declaration.qual_name.item_decl
          if decl != None :
             if decl.kind != namespaceDecl :
                self.error ("Namespace name expected");
             self.display[-1].using_list.append (decl)

   # simple declaration

   def on_simple_declaration (self, simple_decl) :
       self.copy_location (simple_decl, simple_decl.type_spec)

   def on_simple_declarator (self, declarator) :
       return
       while declarator.kind in [nestedDeclarator, pointerDeclarator, referenceDeclarator, arrayDeclarator, functionDeclarator] :
          declarator = declarator.inner_declarator
       if declarator.kind == emptyDeclarator :
          self.error ("Empty declarator")

   def on_simple_item (self, simple_declaration) :

       simple_item = simple_declaration.items [-1] # get above simple declaration

       type_spec = simple_declaration.type_spec
       declarator = simple_item.declarator

       # K2: stencil instance directive 'access <int> numeric;'.
       # Pokud type_spec rezolvuje na pojmenovanou stencil deklaraci,
       # vytáhneme instance_name z deklarátoru, expandujeme a samotný
       # 'numeric' označíme skip_code (existuje jen pro syntaktickou
       # vyplnění — backendy ho přeskočí).
       ts_decl = getattr (type_spec, 'item_decl', None)
       if (ts_decl is not None
               and getattr (ts_decl, 'kind', None) == stencilDecl
               and getattr (ts_decl, 'members', None) is not None) :
          inst_name = self._extract_simple_name (declarator)
          if inst_name is not None :
             arg_types = self._stencil_arg_types (
                getattr (type_spec, 'template_args', None))
             self._instantiate_named_stencil (ts_decl, arg_types, inst_name)
             # Minimální setup pro c2cpp / generátory:
             initVariable (simple_item)
             simple_item.item_simple_decl = simple_declaration
             simple_item.item_name = inst_name
             simple_item.item_qual = inst_name
             simple_item.skip_code = True
             return

       if not (declarator.kind == functionDeclarator and declarator.inner_declarator.kind == emptyDeclarator) :
       # !? if declarator.kind != constructorDeclarator :
          "clear constructor_flag when declaration only starts with class name"
          type_spec.constructor_flag = False
          type_spec.destructor_flag = False

       "is it function"
       func_spec = self.get_function_specifier (declarator)
       if func_spec != None :
          if self.all_value_parameters (func_spec) :
             "variable with constructor parameters"
             initVariable (simple_item)
             simple_item.construction_list = self.value_parameters (func_spec) # after initVariable
             setattr (func_spec, "all_values", True)
          else :
             "fuction declaration"
             initFunction (simple_item)
       else :
          "variable with initialization block"
          initVariable (simple_item)

       "link from simple item to simple declaration"
       simple_item.item_simple_decl = simple_declaration # after initFuction / initVariable

       "name and source location"
       self.clear_declarator (declarator)
       self.copy_declarator_name (simple_item, declarator)
       self.copy_declarator_location (simple_item, declarator) # important for markDefn

       "class context: item_origin, item_label, method_implementation, implementation_list"
       if type_spec.constructor_flag or type_spec.destructor_flag :
          qual_name = simple_declaration.type_spec
          # if not isinstance (qual_name, CmmName) :
          #    self.error ("Name required in constructor or destructor declaration")
       else :
          qual_name = self.get_declarator_name (declarator)
       if qual_name != None and qual_name.kind == compoundName :
          context_name = qual_name.left
          context_decl = getattr (context_name, "item_decl", None)
          if context_decl != None and context_decl.kind == classDecl :
             cls = context_decl
             if cls != None and cls != self.get_class () :
                simple_item.item_origin = cls
                simple_item.item_label = cls.item_name + "::" + self.get_short_name (qual_name.right)
             if cls != None :
                cls.implementation_list.append (simple_item)
                simple_item.method_implementation = True
                simple_item.outer_class = cls # !?

       "type"
       init_type = simple_declaration.type_spec.item_type
       simple_item.item_type = self.get_declarator_type (init_type, declarator)
       # print ("on_simple_item", simple_item.item_name, simple_item.item_type)

       "constructor"
       if type_spec.constructor_flag :
          simple_item.is_constructor = True
          simple_item.item_name = "(constructor)" + self.get_constructor_name (type_spec)
          self.copy_location (simple_item, type_spec)

       "destructor"
       if type_spec.destructor_flag :
          simple_item.is_destructor = True
          simple_item.item_name = "~" + self.get_constructor_name (type_spec)
          self.copy_location (simple_item, type_spec)

       "enter identifier into scope"
       if simple_item.item_origin != None :
          self.openScope (simple_item.item_origin)
       self.enter (simple_item)
       self.custom_attributes (simple_item)
       if simple_item.item_origin != None :
          self.closeScope ()

       "color and mark position in source editor"
       if simple_item.is_function :
          self.selectColor (simple_item, table = "functionColors")
       else :
          self.selectColor (simple_item, table = "variableColors")
       self.markDefn (simple_item)

       "function parameters"
       if simple_item.is_function :
          func_spec = self.get_function_specifier (declarator)
          self.openScope (simple_item)
          self.enter_parameters (func_spec.parameters)
          self.closeScope ()

       "variable initialization"
       if not simple_item.is_function :
          cls = simple_item.item_context
          if isinstance (cls, Class)  :
             cls.init_list.append (simple_item)

       self.custom_simple_item (simple_item)

   def get_constructor_name (self, type_spec) :
       result = ""
       decl = type_spec.item_decl
       if decl == None :
          if type_spec.kind == compoundName :
             decl = type_spec.left.item_decl
       if decl != None :
          result = decl.item_name
       return result

   def get_declarator_name (self, declarator) :
       result = None
       if declarator != None :
          while declarator.kind in [nestedDeclarator, pointerDeclarator, referenceDeclarator, arrayDeclarator, functionDeclarator] :
             declarator = declarator.inner_declarator
          if declarator.kind == basicDeclarator :
             result = declarator.qual_name
       return result

   def copy_declarator_name (self, target, declarator) :
       if declarator != None :
          while declarator.kind in [nestedDeclarator, pointerDeclarator, referenceDeclarator, arrayDeclarator, functionDeclarator] :
             declarator = declarator.inner_declarator
          if declarator.kind == basicDeclarator :
             target.item_name = self.get_short_name (declarator.qual_name) # !?
          else :
             target.item_name = ""

   def copy_declarator_location (self, target, declarator) :
       if declarator != None :
          while declarator.kind in [nestedDeclarator, pointerDeclarator, referenceDeclarator, arrayDeclarator, functionDeclarator] :
             declarator = declarator.inner_declarator
          if declarator.kind == basicDeclarator :
             self.copy_name_location (target, declarator.qual_name)

   def clear_declarator (self, declarator) :
       if declarator != None :
          while declarator.kind in [nestedDeclarator, pointerDeclarator, referenceDeclarator, arrayDeclarator, functionDeclarator] :
             declarator = declarator.inner_declarator
          if declarator.kind == basicDeclarator :
             self.clear_declaration (declarator.qual_name)

   # function

   def on_open_function (self, simple_declaration) :
       simple_item = simple_declaration.items [-1]

       if simple_item.is_function :
          "function, not variable with initialization block"
          func = simple_item
          # print ("OPEN FUNCTION", func.item_qual)

          "method: open class namespace"
          if simple_item.item_origin != None :
             self.openScope (simple_item.item_origin)

          self.openRegion (func) # region with background color
          self.openScope (func) # scope for parameters

          self.openCompletion (func, outside = True)
          self.markOutline (func)

          "scope for local declarations"
          local_scope = Scope ()
          self.register (func, "(local)", local_scope)
          local_scope.hidden_scope = True # do not print (local)
          self.openScope (local_scope)

       self.custom_open_function (simple_item)

   def on_close_function (self, simple_declaration) :
       simple_item = simple_declaration.items [-1]
       simple_item.item_body = simple_declaration.body

       if simple_item.is_function :
          "function, not variable with initialization block"
          func = simple_item
          self.closeCompletion (func, outside = True)
          self.closeScope () # local variables
          self.closeScope () # parameters
          self.closeRegion ()
          if simple_item.item_origin != None :
             self.closeScope ()
          # print ("CLOSE FUNCTION", func.item_qual)

          simple_item.end_of_function = CmmBasic () # !?
          self.storeLocation (simple_item.end_of_function)

       self.custom_close_function (simple_item)
       self.custom_statement (simple_item, simple_declaration.body)

   # function parameters

   def get_function_specifier (self, declarator) :
       result = None

       while declarator.kind in [nestedDeclarator, pointerDeclarator, referenceDeclarator, arrayDeclarator] :
          declarator = declarator.inner_declarator

       if declarator.kind == functionDeclarator :
          result = declarator

       return result

   def all_value_parameters (self, func_spec) :
       result = False
       items = func_spec.parameters.items
       if len (items) > 0 :
          result = True
          for param in items :
              if param.kind != simpleStat :
                 result = False
       return result

   def value_parameters (self, func_spec) :
       result = [ ]
       for param in func_spec.parameters.items :
           if param.kind == simpleStat :
              result.append (param.inner_expr)
       return result

   def enter_parameters (self, param_list) :
       for param in param_list.items :
           if param.kind == simpleDecl : # !?
              simple_item = param.items[0]
              simple_item.item_simple_decl = param
              initVariable (simple_item)
              self.clear_declarator (simple_item.declarator)
              self.copy_declarator_name (simple_item, simple_item.declarator)
              self.copy_declarator_location (simple_item, simple_item.declarator)

              init_type = getattr (param.type_spec, "item_type", None)
              simple_item.item_type = self.get_declarator_type (init_type, simple_item.declarator)

              self.enter (simple_item)
              self.selectColor (simple_item, table = "variableColors")
              self.markDefn (simple_item)

   # simple statement with block statement

   def on_open_expr_block (self, stat) :
       self.custom_open_expr_block (stat)

   def on_close_expr_block (self, stat) :
       self.custom_close_expr_block (stat)

   # statement scope

   def on_simple_statement (self, stat) :
       self.copy_location (stat, stat.inner_expr)
       self.custom_simple_statement (stat)

   def _in_declaration_context (self) :
       """True když jsme v deklarativním kontextu — top-level globalu
       nebo uvnitř stencilu. Falešné jakmile jsme uvnitř funkce. Slouží
       k tomu, aby compound/if na top-level NEOTEVŘELY pomocný scope
       — deklarace pak natéká rovnou do globálu (resp. stencil scope).
       Tím se 'if (CONST) { void f () { ... } }' chová jako podmíněně
       přítomná globální deklarace, ne lokální blok."""
       for scope in self.display :
           if isinstance (scope, CmmSimpleItem) and getattr (scope, 'is_function', False) :
              return False
       return True

   def on_open_compound_statement (self, stat) :
       if self._in_declaration_context () :
          stat._no_scope = True
          return
       stat._no_scope = False
       self.openLocalScope ()

   def on_close_compound_statement (self, stat) :
       if not getattr (stat, '_no_scope', False) :
          self.closeLocalScope ()

   def on_open_if_statement (self, stat) :
       if self._in_declaration_context () :
          stat._no_scope = True
          return
       stat._no_scope = False
       self.openLocalScope (stat.cond)

   def on_close_if_statement (self, stat) :
       if not getattr (stat, '_no_scope', False) :
          self.closeLocalScope ()
       # L: const-fold ihned po parsování top-level if. Tím se prohrávající
       # větev označí skip_code dřív, než následující rozšíření (Generate
       # Module / InstructionsModule) iterují global_scope a generují kód.
       if self._in_declaration_context () :
          self._fold_if_decl_level (stat)

   # Stará verze on_open_for_statement / on_close_for_statement —
   # smazána, použije se sjednocená dole (na řádku ~688) která zahrnuje
   # i M (compile-time for-each).

   def on_open_while_statement (self, stat) :
       self.openLocalScope (stat.cond)

   def on_close_while_statement (self, stat) :
       self.closeLocalScope ()

   def on_open_for_statement (self, stat) :
       """V decl kontextu (top-level / stencil): nepouštíme nový scope
       a snapshotneme global_scope kvůli M (compile-time for-each).
       Jinak normální local scope pro for v těle funkce."""
       if self._in_declaration_context () :
          stat._no_scope = True
          stat._snap_item_count = len (self.global_scope.item_list)
          stat._snap_dict_keys = set (self.global_scope.item_dict.keys ())
          return
       stat._no_scope = False
       self.openLocalScope (stat.from_expr)

   def on_close_for_statement (self, stat) :
       if not getattr (stat, '_no_scope', False) :
          self.closeLocalScope ()
       if getattr (stat, '_snap_item_count', None) is not None :
          self._unfold_ct_for (stat)

   def on_open_switch_statement (self, stat) :
       self.openLocalScope (stat.cond)

   def on_close_switch_statement (self, stat) :
       self.closeLocalScope ()

   # names

   def isScope (self, obj) :
       return (obj != None and
                 (obj.kind == namespaceDecl or
                  obj.kind == classDecl or
                  obj.kind == enumDecl ))

   def isTypeObject (self, obj) :
       return (obj != None and
                 (obj.kind == typedefDecl or
                  obj.kind == classDecl or
                  obj.kind == enumDecl ))

   def on_base_name (self, qual_name) :
       "lookup declaration"

       # if qual_name.item_decl != None :
       #    self.warning ("already has item_decl")

       decl = None
       owner = None
       if qual_name.kind == globalName :
          decl = self.searchScope (self.global_scope, qual_name.inner_name.id)
       elif qual_name.kind == simpleName :
          decl, owner = self.lookupItemAndOwner (qual_name.id)
       elif qual_name.kind == compoundName :
          if qual_name.right.kind == simpleName :
             left_decl = qual_name.left.item_decl
             if self.isScope (left_decl) :
                decl = self.searchScope (left_decl, qual_name.right.id)
       elif qual_name.kind == templateName :
          base_decl = qual_name.left.item_decl
          # Stencil: pokud je 'base_decl' funkce/typ s navázanou
          # stencil_decl, instantiujeme tady (on_base_name se volá
          # AŽ PO on_template_name, takže item_decl by se jinak
          # přepsal zpátky na původní template).
          if (base_decl is not None
                  and getattr (base_decl, 'stencil_decl', None) is not None) :
             inst = self._instantiate_stencil (qual_name, base_decl)
             decl = inst if inst is not None else base_decl
          else :
             decl = base_decl # !? declaration from name without < >, important for variable initialization

       #if self.remember_leading :
       #   if qual_name.kind == simpleName :
       #      qual_name.leading_flag = True # first identifier in flexible statement
       #   self.remember_leading = False

       "class, enum or typedef => type"
       if self.isTypeObject (decl) :
          qual_name.type_flag = True

       "constructor or destructor on the beginning of member declaration"
       if self.remember_destructor :
          if decl == self.get_class () :
             qual_name.destructor_flag = True
          self.remember_destructor = False # back to default value
          self.remember_constructor = False

       if self.remember_constructor :
          cls = self.get_class ()
          if decl == cls or decl != None and cls != None and decl.item_qual == cls.item_qual : # !?
             qual_name.constructor_flag = True
          self.remember_constructor = False # back to default value

       if decl != None and owner == decl.item_context :
          owner = None

       "store item_decl, name_owner"
       qual_name.item_decl = decl
       qual_name.name_owner = owner
       self.custom_base_name (qual_name)

   def is_template_name (self, qual_name) :
       "is declaration a template declaration"
       decl = qual_name.item_decl
       result = decl != None and getattr (decl, "template_decl", None) != None
       # print ("IS TEMPLATE", getattr (qual_name, "id", ""))

       # !? template member function - variant.value <QColor> ()
       # if decl.item_type != None and isinstance (decl.item_type, NamedType) :
       #    if decl.item_type.type_label == "QVariant" :
       if qual_name.kind == simpleName and qual_name.id == "value" :
          result = True

       return result

   def on_template_name (self, qual_name) :
       # Stencil instantiation se odehrává v on_base_name (kde má
       # poslední slovo nad qual_name.item_decl). Tady nastavíme
       # default item_decl na 'left' decl pro případ, že by někdo
       # mezi tím item_decl četl.
       qual_name.item_decl = qual_name.left.item_decl

   def on_cont_name (self, qual_name) :
       left_decl = qual_name.left.item_decl
       right = qual_name.right

       "search name in scope of name before ::"
       if left_decl != None :
          if getattr (left_decl, "item_dict", None) != None :
             if right.kind == simpleName :
                decl = self.searchScope (left_decl, right.id)
                qual_name.item_decl = decl
                if self.isTypeObject (decl) :
                   qual_name.type_flag = True
                right.item_decl = decl # only for visualization
                self.markUsage (right, right.item_decl)

          "constructor"
          if left_decl.kind == classDecl:
             if right.kind == simpleName :
                if right.id == left_decl.item_name :
                   qual_name.type_flag = True
                   qual_name.constructor_flag = True
                   qual_name.item_decl = left_decl

          "destructor"
          if left_decl.kind == classDecl :
             if right.kind == destructorName :
                if right.inner_name.id == left_decl.item_name :
                   qual_name.type_flag = True
                   qual_name.destructor_flag = True
                   qual_name.item_decl = left_decl

   # type or expression

   def on_start_member_item (self, param) :
       "begin of member item - constructor is allowed here"
       if self.token in [ self.identifier, self.keyword_virtual, self.keyword_explicit ] :
          self.remember_constructor = True
       if self.isSeparator ("~") :
          self.remember_tilda = True

   def is_expression (self, expr) :
       "type cannot be simple statement"
       return not expr.type_flag

   def is_binary_expression (self, expr) :
       "type cannot be left operand in binary expression"
       return not expr.type_flag

   def is_value_parameter (self, expr) :
       "parameters without type => value parameter"
       return not expr.type_flag

   def on_middle_bit_not_expr (self, expr) :
       if self.remember_tilda :
          if self.token == self.identifier :
             self.remember_destructor = True
             self.remember_tilda = False # back to default value

   def on_bit_not_expr (self, expr) :
       # ~ type is destructor
       expr.destructor_flag = expr.param.destructor_flag
       expr.type_flag = expr.param.type_flag
       expr.item_decl = expr.param.item_decl

   def is_postfix_expression (self, expr) :
       result = True
       if expr.kind == subexprExpr :
          "after expression in parenthesis, avoid functon call in (int) (double) v"
          result = not expr.type_flag
       elif self.tokenText == "(" :
          "class name at the beginning of member declaration => constructor"
          result = not expr.constructor_flag and not expr.destructor_flag
       elif self.tokenText == "." :
          "class name . field name"
          result = True
       else :
          result = not expr.type_flag
       return result

   def is_cast_expression (self, expr) :
       "is it type in parenthesis"
       return expr.kind == subexprExpr and expr.type_flag

   def is_mul (self) :
       "is it custom operatin with mul priority"
       return False

   def is_add (self) :
       "is it custom operatin with add priority"
       return False

   def is_constructor (self, expr) :
       return expr.constructor_flag or expr.destructor_flag

   def get_class (self) :
       result = None
       cls = self.display [-1]
       if isinstance (cls, Class) :
          result = cls
       return result

   # location and style

   def copy_location (self, target, source) :
       target.src_file = source.src_file
       target.src_line = source.src_line
       target.src_column = source.src_column
       target.src_pos = source.src_pos
       target.src_end = source.src_end
       # target.src_step = source.src_step

   def clear_declaration (self, qual_name) :
       qual_name.item_decl = None

   def copy_name_location (self, target, qual_name) :
       source = qual_name
       if source != None :
          if source.kind == compoundName :
             source = source.right
          self.copy_location (target, source)
          source.item_ref = target

   def copy_style (self, target, source) :
       if source != None :
          if getattr (source, "item_ink", None) != None:
             target.item_ink = source.item_ink
          if getattr (source, "item_paper", None) != None:
             target.item_paper = source.item_paper
          if getattr (source, "item_icon", None) != None:
             target.item_icon = source.item_icon

   # name as a string

   def get_simple_name (self, qual_name) :
       result = ""
       if qual_name.kind == simpleName :
          result = qual_name.id
       return result

   def get_short_name (self, qual_name) :
       result = ""

       if qual_name.kind == simpleName :
          result = qual_name.id
       elif qual_name.kind == specialName :
          result = qual_name.spec_func.spec_name # !?
       elif qual_name.kind == compoundName :
          result = self.get_short_name (qual_name.right)
       elif qual_name.kind == globalName :
           result = self.get_short_name (qual_name.inner_name)
       elif qual_name.kind == destructorName :
           result = "~" + self.get_short_name (qual_name.inner_name)
       elif qual_name.kind == templateName :
           result = self.get_short_name (qual_name.left) # !?

       return result

   def get_name (self, qual_name) :
       result = ""

       if qual_name.kind == simpleName :
          result = qual_name.id
       elif qual_name.kind == specialName :
          result = qual_name.spec_func.spec_name # !?
       elif qual_name.kind == compoundName :
          result = self.get_name (qual_name.left) + "::" + self.get_name (qual_name.right)
       elif qual_name.kind == globalName :
          result = "::" + self.get_name (qual_name.inner_name)
       elif qual_name.kind == destructorName :
          result = "~" + self.get_name (qual_name.inner_name)
       elif qual_name.kind == templateName :
          result = self.get_name (qual_name.left) + "<???>" # !?

       if result == "" :
          result = "???"
       return result

   # type specifiers

   def on_type_name (self, expr) : # !?
       expr.type_flag = True
       expr.item_type = expr.qual_name.item_type

   def on_const_specifier (self, expr) :
       expr.type_flag = True
       expr.type = copy.copy (expr.param.item_type)
       expr.type.type_const = True

   def on_volatile_specifier (self, expr) :
       expr.type_flag = True
       expr.type = copy.copy (expr.param.item_type)
       expr.type.type_volatile = True

   def on_middle_decl_specifier (self, expr) :
       self.remember_destructor = True

   def on_decl_specifier (self, expr) :
       expr.type_flag = True
       # expr.type_flag = expr.param.type_flag
       expr.constructor_flag = expr.param.constructor_flag
       expr.destructor_flag = expr.param.destructor_flag

   def on_type_specifier (self, expr) :
       expr.type_flag = True

       type = self.get_type_spec (expr)
       expr.item_type = type
       self.copy_location (type, expr)
       self.copy_style (type, expr)

       self.custom_type_specifiers (expr, type)

   def get_type_decl (self, obj) :
       result = None
       if obj.item_decl != None :
          decl = obj.item_decl
          if ( decl.kind == classDecl or
               decl.kind == enumDecl or
               decl.kind == typedefDecl or
               isinstance (decl, Unknown) ) :
                  result = decl
       return result

   def get_named_type (self, qual_name) :
       result = NamedType ()
       result.type_label = self.get_name (qual_name)
       result.type_decl = self.get_type_decl (qual_name)
       if qual_name.kind == templateName :
          result.type_label = self.get_name (qual_name.left) # !? name without < >
          result.type_args =  qual_name.template_args
          result.type_args = [ ]
          for arg in qual_name.template_args.items :
              # type_spec = arg.value.type_spec
              # result.type_args.append (type_spec.item_type) # !? missing pointers, ...
              param = arg.value
              item = param.items [0]
              init_type = getattr (param.type_spec, "item_type", None)
              param_type = self.get_declarator_type (init_type, item.declarator)
              result.type_args.append (param_type)
       # result.gpu_global = qual_name.gpu_global
       return result

   def get_type_spec (self, type_spec) :
       result = SimpleType ()

       if type_spec.a_void : result.type_void = True
       elif type_spec.a_bool : result.type_bool = True
       elif type_spec.a_char : result.type_char = True
       elif type_spec.a_wchar : result.type_wchar = True
       elif type_spec.a_short : result.type_short = True
       elif type_spec.a_int : result.type_int = True
       elif type_spec.a_long : result.type_long = True
       elif type_spec.a_float : result.type_float = True
       elif type_spec.a_double : result.type_double = True

       if type_spec.a_signed :
          result.type_signed = True
       elif type_spec.a_unsigned :
          result.type_unsigned = True

       # result.gpu_global = type_spec.gpu_global
       return result

   # declarator type

   def get_declarator_type (self, init_type, declarator) :
       result = init_type
       while declarator != None :

          last = result
          cv_spec = None

          if declarator.kind == pointerDeclarator :
             result = PointerType ()
             result.type_from = last
             cv_spec = declarator.cv_spec

          if declarator.kind == referenceDeclarator :
             result = ReferenceType ()
             result.type_from = last
             cv_spec = declarator.cv_spec

          if cv_spec != None and cv_spec.cv_const :
             result.type_const = True

          if cv_spec != None and cv_spec.cv_volatile :
             result.type_volatile = True

          if declarator.kind != emptyDeclarator :
                last = result
                if declarator.kind == arrayDeclarator :
                   result = ArrayType ()
                   result.type_from = last
                   result.lim = declarator.lim
                if declarator.kind == functionDeclarator :
                   if not self.all_value_parameters (declarator) :
                      result = FunctionType ()
                      result.type_from = last

          if last != None :
             result.gpu_global = last.gpu_global

          if declarator.kind in [nestedDeclarator, pointerDeclarator, referenceDeclarator, arrayDeclarator, functionDeclarator] :
             declarator = declarator.inner_declarator
          else :
             declarator = None

       return result

   # expression

   def on_ident_expr (self, expr) :
       self.markUsage (expr, expr.item_decl)

       if expr.kind == simpleName :
          if expr.name_owner != None :
             owner = expr.name_owner
             txt = ""
             if owner.owner_obj != None :
                txt = owner.owner_obj.item_qual
             if owner.owner_expr != None :
                expr = owner.owner_expr
                if expr.kind == simpleName :
                   txt = expr.id
                else :
                   txt = "(expression)"
             if txt == "" :
                txt = owner.item_qual
             self.markOwner (expr, txt)

       # !?
       if self.get_type_decl (expr) != None :
          expr.item_type = self.get_named_type (expr)

       if expr.item_decl != None and getattr (expr.item_decl, "item_type", None) != None :
          expr.item_type = expr.item_decl.item_type

       "true or false"
       if expr.kind == simpleName :
          ident = expr.id
          if ident == "true" :
             expr.item_value = True
          elif ident == "false" :
             expr.item_value = False

       if hasattr (expr.item_decl, "item_value") :
          expr.item_value = expr.item_decl.item_value

       # self.custom_ident_expr (expr)

   def on_field_expr (self, expr) :
       self.copy_location (expr, expr.left)
       left = expr.left
       right = expr.field_name
       # NO right.item_name = right.id

       if right.kind == templateName : # !? duplicate template name
          right.id = right.left.id

       decl = None
       if left.item_type != None :
          type = left.item_type
          if isinstance (type, PointerType) :
             type = type.type_from
          decl = getattr (type, "type_decl", None)
       elif left.item_decl != None :
          decl = left.item_decl # class name or enum type name
          if decl.kind != classDecl and decl.kind != enumDecl and decl.kind != typedefDecl :
             decl = None

       if decl != None and getattr (decl, "item_dict", None) != None :
          right.item_decl = decl.item_dict.get (right.id)
          expr.item_decl = right.item_decl
          if getattr (right.item_decl, "item_type", None) != None : # !?.
             expr.item_type = right.item_decl.item_type
          self.markUsage (right, right.item_decl)

       self.custom_field (expr)

   def on_ptr_field_expr (self, expr) :
       self.on_field_expr (expr)

   def on_post_inc_expr (self, expr) : # !?
       self.copy_location (expr, expr.left)
       expr.item_type = expr.left.item_type

   def on_post_dec_expr (self, expr) : # !?
       self.copy_location (expr, expr.left)
       expr.item_type = expr.left.item_type

   def on_int_value (self, expr) :
       expr.item_type = self.intType
       text = expr.value
       if text.startswith ("0") :
          if text.startswith ("0x") :
             expr.item_value = int (text[2:], 16)
          elif text.startswith ("0b") :
             expr.item_value = int (text[2:], 2)
          elif text.startswith ("0o") : # !?
             expr.item_value = int (text[2:], 8)
          elif text.startswith ("0q") : # !?
             expr.item_value = int (text[2:], 8)
          elif len (text) > 1 :
             expr.item_value = int (text[1:], 8) # starting zero => octal
          else :
             expr.item_value = 0
       else:
          expr.item_value = int (text)

   def on_real_value (self, expr) :
       expr.item_type = self.doubleType
       expr.item_value = float (expr.value)

   def on_char_value (self, expr) :
       expr.item_type = self.charType
       expr.item_value = expr.value

   def on_string_value (self, expr) :
       expr.item_type = self.stringType

       text = expr.value
       for item in expr.items :
          text = text + item.value
       expr.item_value = text

   def on_this_expr (self, expr) : # !?
       pass

   def on_subexpr_expr (self, expr) : # !?
       expr.item_type = expr.param.item_type
       expr.type_flag = expr.param.type_flag

   def on_index_expr (self, expr) : # !?
       self.copy_location (expr, expr.left)
       pass

   def on_call_expr (self, expr) : # !?
       self.copy_location (expr, expr.left)
       expr.left.call_func = True
       self.custom_call (expr)

   def on_modern_cast_expr (self, expr) : # !?
       self.using_modern_cast = True
       pass

   def on_typeid_expr (self, expr) : # !?
       pass

   def on_inc_expr (self, expr) : # !?
       pass

   def on_dec_expr (self, expr) : # !?
       pass

   def on_deref_expr (self, expr) : # !?
       pass

   def on_addr_expr (self, expr) : # !?
       pass

   def on_plus_expr (self, expr) : # !?
       pass

   def on_minus_expr (self, expr) : # !?
       pass

   def on_log_not_expr (self, expr) : # !?
       pass

   def on_sizeof_expr (self, expr) : # !?
       pass

   def on_allocation_expr (self, expr) : # !?
       pass

   def on_deallocation_expr (self, expr) : # !?
       pass

   def on_throw_expr (self, expr) : # !?
       pass

   def on_cast_formula (self, expr) : # !?
       pass

   def on_binary_expr (self, expr) :
       self.copy_location (expr, expr.left)

       if expr.kind in [mulExpr, divExpr, modExpr,
                        addExpr, subExpr,
                        shlExpr, shrExpr,
                        bitAndExpr, bitOrExpr, bitXorExpr ] :
          "result type"
          a = self.type_number (expr.left)
          b = self.type_number (expr.right)
          inx = a
          if b > inx :
             inx = b
          if inx == self.doubleInx :
             expr.item_type = self.doubleType
          if inx == self.floatInx :
             expr.item_type = self.floatType
          if inx == self.unsignedLongInx :
             expr.item_type = self.unsignedLongType
          if inx == self.longInx :
             expr.item_type = self.longType
          if inx == self.unsignedIntInx :
             expr.item_type = self.unsignedIntType
          if inx == self.intInx :
             expr.item_type = self.intType

          self.custom_binary (expr, inx)

       elif expr.kind in [ltExpr, leExpr, gtExpr, geExpr, eqExpr, neExpr,
                          logAndExpr, logOrExpr ] :
          expr.item_type = self.boolType
          self.custom_relation (expr)

       elif expr.kind in [assignExpr] :
          self.custom_assign (expr)

       self.binary_expr_value (expr)

   # expression value

   def get_expr_value (self, expr) :
       return getattr (expr, "item_value", None)

   def binary_expr_value (self, expr) :
       value = None

       if expr.kind in [ addExpr, subExpr, mulExpr, divExpr, modExpr,
                         shlExpr, shrExpr, bitAndExpr, bitOrExpr, bitXorExpr,
                         ltExpr, gtExpr, leExpr, geExpr, eqExpr, neExpr ] :
          left = self.get_expr_value (expr.left)
          right = self.get_expr_value (expr.right)
          if left != None and right != None :
             if expr.kind == addExpr : value = left + right
             if expr.kind == subExpr : value = left - right
             if expr.kind == mulExpr : value = left * right
             if expr.kind == divExpr : value = left / right
             if expr.kind == modExpr : value = left % right
             if expr.kind == shlExpr : value = left << right
             if expr.kind == shrExpr : value = left >> right

             if expr.kind == bitAndExpr : value = left & right
             if expr.kind == bitOrExpr  : value = left | right
             if expr.kind == bitXorExpr : value = left ^ right

             if expr.kind == ltExpr : value = left < right
             if expr.kind == gtExpr : value = left > right
             if expr.kind == leExpr : value = left <= right
             if expr.kind == geExpr : value = left >= right
             if expr.kind == eqExpr : value = left == right
             if expr.kind == neExpr : value = left != right

       elif expr.kind == logAndExpr :
          left = self.get_expr_value (expr.left)
          if left != None :
             if left == False :
                value = False
             else :
                value = self.get_expr_value (expr.right)

       elif expr.kind == logOrExpr :
          left = self.get_expr_value (expr.left)
          if left != None :
             if left == True :
                value = True
             else :
                value = self.get_expr_value (expr.right)

       expr.item_value = value

   # expression type

   intInx = 1
   unsignedIntInx = 2
   longInx = 3
   unsignedLongInx = 4
   floatInx = 5
   doubleInx = 6
   unknownInx = 7

   def init_types (self) :
       self.intType = SimpleType ()
       self.intType.type_int = True

       self.unsignedIntType = SimpleType ()
       self.unsignedIntType.type_unsigned = True
       self.unsignedIntType.type_int = True

       self.longType = SimpleType ()
       self.longType.type_long = True

       self.unsignedLongType = SimpleType ()
       self.unsignedLongType.type_unsigned = True
       self.unsignedLongType.type_long = True

       self.floatType = SimpleType ()
       self.floatType.type_float = True

       self.doubleType = SimpleType ()
       self.doubleType.type_double = True

       self.boolType = SimpleType ()
       self.boolType.type_bool = True

       self.charType = SimpleType ()
       self.charType.type_char = True

       # self.wcharType = SimpleType ()
       # self.wcharType.type_wchar = True

       # self.voidType = SimpleType ()
       # self.voidType.type_void = True

       self.stringType = NamedType ()
       self.stringType.type_label = "string" # !?

   def type_number (self, expr) :
       inx = self.unknownInx
       type = expr.item_type
       if type != None:
          if isinstance (type, SimpleType) : # !?
             if type.type_double :
                inx = self.doubleInx
             elif type.type_float :
                inx = self.floatInx
             elif type.type_long :
                if type.type_unsigned :
                   inx = self.unsignedLongInx
                else :
                   inx = self.longInx
             elif type.type_int or type.type_short or type.type_wchar or type.type_char or type.type_bool :
                if type.type_unsigned :
                   inx = self.unsignedIntInx
                else :
                   inx = self.intInx
       return inx

   # -----------------------------------------------------------------------

   def custom_namespace (self, ns_decl) :
       pass

   def custom_class (self, cls) :
       pass

   def custom_open_class (self, cls) :
       pass

   def custom_stop_class (self, cls) :
       pass

   def custom_simple_item (self, simple_item) :
       pass

   def custom_attributes (self, decl) :
       pass

   def custom_open_function (self, stat) :
       pass

   def custom_close_function (self, stat) :
       pass

   def custom_open_expr_block (self, stat) :
       pass

   def custom_close_expr_block (self, stat) :
       pass

   def custom_base_name (self, qual_name) :
       pass

   def custom_relation (self, expr) :
       pass

   def custom_binary (self, expr, inx) :
       pass

   def custom_assign (self, expr) :
       pass

   def custom_call (self, expr) :
       pass

   def custom_field (self, expr) :
       pass

   def custom_type_specifiers (self, type_spec, type) :
       pass

   def custom_simple_statement (self, stat) :
       pass

   def custom_statement (self, target, stat) :
       pass

# --------------------------------------------------------------------------

class CmmInitCompiler (CmmCompiler) :

   def __init__ (self) :
       super (CmmInitCompiler, self).__init__ ()

   # initialization block scope

   def openSearchOnlyScope (self, scope) :
       look = copy.copy (scope)
       look.search_only = True

       self.openScope (look)
       # print ("OPEN SEARCH SCOPE", scope.item_qual)
       return look

   # variable initialization

   def custom_simple_item (self, simple_item) :
       if not simple_item.is_function :
          self.variable_initialization (simple_item)

   def variable_initialization (self, simple_item) :
       var = simple_item
       type = var.item_type

       if isinstance (type, SimpleType) :
           if type.type_bool :
              var.alt_init = "<false>"
           if type.type_char or type.type_wchar :
              var.alt_init = "<char_zero>"
           if type.type_short or type.type_int or type.type_long :
              var.alt_init = "<zero>"
           if type.type_float :
              var.alt_init = "<float_zero>"
           if type.type_double :
              var.alt_init = "<double_zero>"

       if isinstance (type, NamedType) :
          if type.type_label == "string" : # !?
              var.alt_init = "<empty_string>"

       if var.alt_init == "" :
          if isinstance (type, PointerType) :
             # declaration with body => automatic new, but now item_body is not known
             # declaration with initialization => initialization value
             if var.init == None :
                var.alt_init = "<null>"

   # variable_declaration { statements }

   def custom_open_function (self, simple_item) :
       if not simple_item.is_function :
          "variable declaration with initialization block"
          self.open_variable_init_block (simple_item)

   def custom_close_function (self, simple_item) :
       if not simple_item.is_function :
          self.close_variable_init_block (simple_item)

   def init_block (self, type) :
       arrow = False
       if type != None and isinstance (type, PointerType) :
          type = type.type_from
          arrow = True
       decl = getattr (type, "type_decl", None )
       if decl != None and decl.kind != classDecl :
          decl = None
       return decl, arrow


   def open_variable_init_block (self, simple_item) :
       decl, arrow = self.init_block (simple_item.item_type)
       if decl != None :
          scope = self.openSearchOnlyScope (decl) # only for lookup, not for declarations
          scope.owner_obj = simple_item
          scope.owner_arrow = arrow
          scope.foreign_obj = simple_item.foreign_obj # add foreign object
          self.openCompletion (decl, outside = True)
          # simple_item.see_block_scope = scope
       simple_item.with_decl = decl

       "foreign objects"
       scope = self.openSearchOnlyScope (simple_item) # only for lookup, not for declarations
       scope.owner_obj = simple_item
       scope.owner_arrow = arrow
       # simple_item.see_foreign_scope = scope
       # simple_item.see_display = self.display [:]

   def close_variable_init_block (self, simple_item) :
       if simple_item.with_decl != None :
          self.closeCompletion (simple_item.with_decl, outside = True)
          self.closeScope ()

       "foreign objects"
       self.closeScope ()

       self.place_variable (simple_item)

   def place_variable (self, var) :
       pass

   # expression { stamements }

   def custom_open_expr_block (self, stat) :
       # super (CmmInitCompiler, self).custom_open_expr_block (stat)

       cls = self.get_class ()
       if cls != None :
          cls.init_list.append (stat) # !? for inititalization in constructor

       expr = stat.inner_expr
       decl, arrow = self.init_block (expr.item_type)
       if decl != None :
          scope = self.openSearchOnlyScope (decl) # only for lookup, not for declarations
          scope.owner_expr = expr
          scope.owner_arrow = arrow
          scope.owner_parenthesis = (expr.kind != simpleName)
          self.openCompletion (decl, outside = True)
          # stat.see_block_scope = scope
       stat.with_decl = decl

       "foreign objects"
       item_decl = expr.item_decl
       if item_decl != None :
          scope = self.openSearchOnlyScope (item_decl) # only for lookup, not for declarations
          scope.owner_expr = expr
          scope.owner_arrow = arrow
          # stat.see_foreign_scope = scope
       stat.second_with_decl = item_decl

   def custom_close_expr_block (self, stat) :
       self.copy_location (stat, stat.inner_expr)
       if stat.with_decl != None :
          self.closeScope ()
          self.closeCompletion (stat.with_decl, outside = True)

       "foreign objects"
       if stat.second_with_decl != None :
          self.closeScope ()

# --------------------------------------------------------------------------

class NoQuote (object) :
   def __init__ (self, value) :
       self.value = value
   def __repr__ (self) :
       return self.value

# --------------------------------------------------------------------------

class CmmQtCompiler (CmmInitCompiler) :

   def __init__ (self) :
       super (CmmQtCompiler, self).__init__ ()

       self.foreign_signal = None
       self.foreign_modules = { }
       # self.foreign_types = { }

       self.clang_translation_unit = None

       self.unknown_scope = self.setup_scope ("(unknown)") # unknown identifiers
       self.extra_scope   = self.setup_scope ("(extra)")   # additional declaration (ie. null)
       self.clang_scope   = self.setup_scope ("(clang)")   # declarations from clang translaion unit
       self.foreign_scope = self.setup_scope ("(foreign)") # declarations from Python modules

       "null"
       var = Variable ()
       initVariable (var)
       var.kind = simpleDecl
       var.item_name = "null"
       var.item_ink = findColor ("null")
       var.mod_rename = "nullptr"
       self.enterIntoScope (self.extra_scope, var)

   # -----------------------------------------------------------------------

   # special scopes

   def setup_scope (self, name) :
       # top = self.display [-1]
       top = self.global_scope
       scope = self.registerInnerScope (top, name)
       scope.search_only = True
       top.item_list.append (scope) # show scope in class tree
       self.display.insert (-1, scope)
       return scope

   def registerInnerScope (self, top, name) :
       if name in top.registered_scopes :
          result = top.registered_scopes [name]
       else :
          result = Scope ()
          result.hidden_scope = True
          self.register (top, name, result)
       return result

   def enter_unknown (self, top, name, qual_name) :
       scope = self.registerInnerScope (top, "(unknown)")
       if name in scope.item_dict :
          unknown = scope.item_dict [name]
       else :
          unknown = Unknown ()
          unknown.kind = -1 # !?
          unknown.item_name = name
          self.enterIntoScope (scope, unknown)
          self.copy_location (unknown, qual_name)
          unknown.item_ink = findColor ("unknown")
       qual_name.item_decl = unknown

   # -----------------------------------------------------------------------

   def is_foreign_field (self, scope, name) :
       result = False
       if scope.foreign_obj != None :
          # print ("IS FIELD", name , "in", scope.item_qual)
          if hasattr (scope.foreign_obj, name) :
             result = True
          elif hasattr (scope.foreign_obj, "is" + name.capitalize ()) :
             result = True
       return result

   # -----------------------------------------------------------------------

   def clang_location (self, item, decl) :
       location = decl.location
       if hasattr (location, "file") and hasattr (location.file, "name"):
           item.src_file = fileNameToIndex (location.file.name)
           item.src_line = location.line
           item.src_column = location.column

   def clang_class (self, scope, decl) :
       name = str (decl.displayname)
       cls = Class ()
       initClass (cls)
       cls.kind = classDecl
       cls.item_name = name
       cls.item_ink = findColor ("clang")
       # if template :
       #    cls.template_decl = cls
       cls.clang_obj = decl
       self.clang_location (cls, decl)
       self.enterIntoScope (scope, cls)

   def clang_decl (self, scope, decl, level = 1) :
       kind = decl.kind

       if kind in [CursorKind.CLASS_DECL,
                   CursorKind.STRUCT_DECL,
                   CursorKind.UNION_DECL] :
          if decl.is_definition () :
             self.clang_class (scope, decl)

       if level <= 3 :
          for item in decl.get_children() :
              self.clang_decl (scope, item, level+1)

   def clang_classes (self) :

       fileName = "examples/qt-classes.cc"
       # args = [ "--include-pch", "qt-classes.pch", "examples/qt-classes.cc", ]
       args = [  # "-c", "-x", "c++",
                 fileName,
              ]

       if use_qt6 :
          opts = pkg_options ("Qt5Widgets") # !?
       elif use_qt5 :
          opts = pkg_options ("Qt5Widgets")
       else :
          opts = pkg_options ("QtGui")
       args = args + opts

       # args = args + gcc_options ("clang++")
       args = args + gcc_options (no_variables = True)
       # two items "-I", "directory" OR one item "-Idirectory", but NOT one item "-I directory"

       print ("args:", args)

       index = cindex.Index.create ()
       start_time = get_time ()
       tu = index.parse (None, args,
                         options = 0*TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD +
                                   1*TranslationUnit.PARSE_INCOMPLETE +
                                   1*TranslationUnit.PARSE_PRECOMPILED_PREAMBLE +
                                   1*TranslationUnit.PARSE_CACHE_COMPLETION_RESULTS +
                                   0*TranslationUnit.PARSE_SKIP_FUNCTION_BODIES +
                                   1*TranslationUnit.PARSE_INCLUDE_BRIEF_COMMENTS_IN_CODE_COMPLETION )
       print ("parse", get_time () - start_time)

       if tu :
          """
          start_time = get_time ()
          tu.reparse ()
          print ("reparse", get_time () - start_time)

          start_time = get_time ()
          tu.reparse ()
          print ("reparse", get_time () - start_time)
          """

          # tu.save ("qt-classes.pch")

          for item in tu.diagnostics :
              print (str (item))

          print ("CLang parsing O.K.")
          self.clang_translation_unit = tu
          self.clang_decl (self.clang_scope, tu.cursor);
          edit = self.win.loadFile (fileName) # !?
          if edit != None :
             edit.clang_translation_unit = tu
          print ("CLang tree O.K.")

   # -----------------------------------------------------------------------

   def foreign_qt_class (self, name, scope, template = False, foreign_obj = None) :
       cls = Class ()
       initClass (cls)
       cls.kind = classDecl
       cls.item_name = name
       cls.item_ink = findColor ("foreign")
       if template :
          cls.template_decl = cls
       cls.foreign_obj = foreign_obj
       self.enterIntoScope (scope, cls)

   def foreign_qt_function (self, name, scope, foreign_obj = None) :
       func = Function ()
       initFunction (func)
       func.item_name = name
       func.item_ink = findColor ("foreign")
       func.foreign_obj = foreign_obj
       self.enterIntoScope (scope, func)

   def foreign_qt_items (self, obj, scope) :
       for name in dir (obj) :
           item = getattr (obj, name)
           if name not in scope.item_dict : # important, do not overwrite Qt namespace with empty Qt class
              if inspect.isclass (item) : # !?
                 self.foreign_qt_class (name, scope, foreign_obj = item)
              if inspect.isfunction (item) : # !?
                 self.foreign_qt_class (name, scope, foreign_obj = item)
              if name == "pyqtSignal" :
                 self.foreign_signal = item
                 # print ("PYQTSIGNAL", self.foreign_signal)

   def foreign_qt_namespace (self) :
       for module in self.foreign_modules :
           name = "Qt"
           if hasattr (module, name) :
               item = getattr (module, name)
               ns = Namespace ()
               initNamespace (ns)
               ns.item_name = name
               ns.item_ink = findColor ("foreign")
               ns.item_expand = False
               self.enterIntoScope (self.foreign_scope, ns)
               self.foreign_qt_items (item, ns)

   def foreign_class (self, name, template = False) :
       self.foreign_qt_class (name, self.foreign_scope, template = template)

   def foreign_classes (self) :

       # self.foreign_signal = None
       # print ("FOREIGN_SIGNAL", self.foreign_signal)

       self.foreign_class ("QList", template = True)
       self.foreign_class ("QVector", template = True)
       if not use_py2_qt4 :
          self.foreign_class ("QString")
          self.foreign_class ("QStringList")
          self.foreign_class ("QJsonObject")
          self.foreign_class ("QJsonArray")
          self.foreign_class ("QJsonValueRef")
          self.foreign_class ("QVariantList")
          self.foreign_class ("QChar")

       "Qt namespace"
       self.foreign_qt_namespace ()

       "Qt classes"
       for module in self.foreign_modules :
           self.foreign_qt_items (module, self.foreign_scope)

       self.foreign_scope.search_func = self.foreign_search

       self.variant_named_type = NamedType ()
       self.variant_named_type.type_label = "QVariant"
       self.variant_named_type.type_decl = self.foreign_scope.item_dict ["QVariant"]

       self.string_named_type = NamedType ()
       self.string_named_type.type_label = "QString"
       self.string_named_type.type_decl = self.foreign_scope.item_dict ["QString"]

   def foreign_search (self, name) :
       for module in self.foreign_modules :
           if name in dir (module) :
               item = getattr (module, name)
               if inspect.isclass (item) : # !?
                  self.foreign_qt_class (name, self.foreign_scope, foreign_obj = item)

   # -----------------------------------------------------------------------

   def enter_foreign_field (self, top, name, qual_name, foreign_ctx) :
       scope = self.registerInnerScope (top, "(foreign)")
       scope.search_only = True # !?
       if name in scope.item_dict :
          item = scope.item_dict [name]
       else :
          item = Variable ()
          initVariable (item)
          item.kind = simpleDecl
          item.item_name = name
          item.foreign_ctx = foreign_ctx
          item.foreign_obj = getattr (foreign_ctx, name, None)
          item.item_ink = findColor ("foreign")
          self.copy_location (item, qual_name)
          self.enterIntoScope (scope, item)
       qual_name.item_decl = item

   # -----------------------------------------------------------------------

   def compile_program (self) :
       # self.setup_extension ()
       if use_clang and self.clang_import :
          self.clang_classes ()
       self.foreign_classes ()
       super (CmmQtCompiler, self).compile_program ()

   # -----------------------------------------------------------------------

   def UpperCase (self, name) :
       return name[0].upper () + name [1:]
       # capitalize () modifies remaining upper case characters

   def read_property (self, expr) :
       "property identifier --> function call"

       var = expr.item_decl

       if var != None and var.foreign_ctx != None :
          name = var.item_name
          target_obj = var.foreign_ctx
          get_name = "is" + self.UpperCase (name)
          set_name = "set" + self.UpperCase (name)

          if hasattr (target_obj, name) and hasattr (target_obj, set_name) :
             expr.alt_read = name

          elif hasattr (target_obj, get_name) and hasattr (target_obj, set_name) :
             expr.alt_read = get_name

          if expr.alt_read != "" :
             self.markText (expr, ink = findColor ("read"), tooltip = "read property " + name)


   def assign_property (self, expr) :
       "assign to property identifier --> set function call"

       left = expr.left
       right = expr.right

       var = left.item_decl

       if var != None and var.foreign_ctx != None :
          name = var.item_name
          target_obj = var.foreign_ctx
          get_name = "is" + self.UpperCase (name)
          set_name = "set" + self.UpperCase (name)
          expr.see = set_name

          if hasattr (target_obj, name) and hasattr (target_obj, set_name) :
             expr.alt_assign = set_name

             if self.is_subtype (target_obj, "QTreeWidgetItem") :
                if name == "text":
                   expr.alt_assign_index = "0"
                elif name == "icon" :
                   expr.alt_assign_index = "0"
                   expr.alt_assign_param = "<icon>"
                elif name == "foreground" :
                   expr.alt_assign_index = "0"
                   expr.alt_assign_param = "<color>"
                elif name == "background" :
                   expr.alt_assign_index = "0"
                   expr.alt_assign_param = "<color>"

             else :
                if name == "icon" :
                   expr.alt_assign_param = "<icon>"
                elif name == "shortcut" :
                   expr.alt_assign_param = "<shortcut>"

          elif hasattr (target_obj, get_name) and hasattr (target_obj, set_name) :
             expr.alt_assign = set_name

          if expr.alt_assign != "" :
             obj = left
             if obj.kind == fieldExpr or obj.kind == ptrFieldExpr :
                obj = obj.field_name
             self.markText (obj, ink = findColor ("write"), tooltip = "set property " + name)

   # -----------------------------------------------------------------------

   def assign_signal (self, expr) :
       "assign to signal identifier --> connect"

       left = expr.left
       right = expr.right

       var = left.item_decl

       if var != None and var.foreign_obj != None :
          # print ("FOREIGN_SIGNAL", self.foreign_signal)
          if isinstance (var.foreign_obj, self.foreign_signal) :
             expr.alt_connect_expr = left
             expr.alt_connect = right.id # !?

             # !?
             owner = var.item_context
             if owner != None :
                owner = owner.item_context
                if owner != None and owner.foreign_obj != None :
                   cls = self.getClass ()
                   if cls != None :
                      expr.alt_connect_cls = cls.item_name # !? qualified name
                      expr.alt_connect_decl = owner.item_name # !?
                      expr.alt_connect_signal = var.item_name
                      expr.alt_connect_src = ""
                      if owner != None :
                         t = owner.item_type
                         if isinstance (t, PointerType) :
                            t = t.type_from
                         if t != None :
                            expr.alt_connect_src = t.type_label

                         if expr.alt_connect_src != "" :
                            txt = ( "connect (" + expr.alt_connect_decl + ", " +
                                     "&" + expr.alt_connect_src + "::" + expr.alt_connect_signal + ", " +
                                     "this, " +
                                     "&" + expr.alt_connect_cls + "::" + expr.alt_connect + ")" )

                            obj = left
                            if obj.kind == fieldExpr or obj.kind == ptrFieldExpr :
                               obj = obj.field_name
                            self.markText (obj, ink = findColor ("signal"), tooltip = "signal " + txt)

   def with_signal (self, stat) :
       "signal identifier { ... } --> connect"

       method = None # function result
       expr = stat.inner_expr
       left = expr
       if expr.kind == callExpr : # !?
          left = expr.left
       if left.kind == simpleName : # !?
          decl = getattr (left, "item_decl", None) # !?
          if decl != None :
             owner = decl.item_context
             if owner != None :
                owner = owner.item_context
                if owner != None and owner.foreign_obj != None :
                   cls = self.getClass ()
                   if cls != None :
                      # print ("CLS", cls.item_qual)
                      method = Method ()
                      method.name = "method" + str (len (cls.methods)+1)
                      cls.methods.append (method)
                      expr.alt_connect = method.name
                      expr.alt_connect_expr = left
                      expr.alt_connect_cls = cls.item_name # !? qualified name
                      expr.alt_connect_decl = owner.item_name # !?
                      expr.alt_connect_signal = left.id
                      expr.alt_connect_src = ""
                      if owner != None :
                         t = owner.item_type
                         if isinstance (t, PointerType) :
                            t = t.type_from
                         if t != None :
                            expr.alt_connect_src = t.type_label

                      if expr.alt_connect_src != "" :
                         txt = ( "connect (" + expr.alt_connect_decl + ", " +
                                  "&" + expr.alt_connect_src + "::" + expr.alt_connect_signal + ", " +
                                  "this, " +
                                  "&" + expr.alt_connect_cls + "::" + expr.alt_connect + ")" )

                         self.markText (left, ink = findColor ("signal"), tooltip = "signal " + txt)
       return method

   def getClass (self) :
       inx = len (self.display) - 1
       obj = None
       while inx > 0 and obj == None :
          tmp = self.display[inx]
          if isinstance (tmp, Class) and not tmp.search_only :
             obj = tmp
          else :
             inx = inx - 1
       return obj

   # -----------------------------------------------------------------------

   # assign to property or signal

   def custom_assign (self, expr) :
       " assign statement --> assign to property or signal "
       self.assign_property (expr)
       self.assign_signal (expr)

   # -----------------------------------------------------------------------

   # class declaration

   def custom_open_class (self, cls) :
       " class declaration --> set class foreign_obj from base class "
       for item in cls.base_classes :
           if cls.foreign_obj == None :
              cls.foreign_obj = item.foreign_obj

   # -----------------------------------------------------------------------

   # custom identifiers

   def custom_base_name (self, qual_name) :
       " identifier in expression --> properties, foreign fields (form Qt base class), unknon fields "

       if qual_name.item_decl != None and qual_name.item_decl.item_context == self.foreign_scope :
          qual_name.item_decl.item_used = True

       if qual_name.item_decl == None and qual_name.kind == simpleName :
          name = qual_name.id
          stop = False

          "foreign local identifiers (Qt field names)"
          inx = len (self.display) - 1
          while inx >= 0 and not stop :
             scope = self.display [inx]
             if scope.foreign_obj != None :
                if self.is_foreign_field (scope, name) :
                   self.enter_foreign_field (scope, name, qual_name, scope.foreign_obj)
                   # print ("FOREIGN FIELD", name, "in", scope.item_qual)
                   stop = True
             inx = inx - 1

          if not stop :
             "unknown identifiers"
             inx = len (self.display) - 1
             while qual_name.item_decl == None and inx >= 0 :
                scope = self.display [inx]
                if scope.default_scope :
                   self.enter_unknown (scope, name, qual_name)
                   # print ("UNKNOWN item", name)
                inx = inx - 1

          self.read_property (qual_name)

       if qual_name.kind == compoundName :
          # if qual_name.left.item_decl == self.get_class () :
          decl = qual_name.left.item_decl
          if decl != None and decl.kind == classDecl : # !?
             cls = self.getClass ()
             # qual_name.see_cls = cls
             # qual_name.see_decl = decl
             if cls != None and decl in cls.base_classes :
                qual_name.class_member = cls

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

   # -----------------------------------------------------------------------

   # custom field names

   def custom_field (self, expr) :
       " .field_name --> read Qt property or special .str, .var, ... fields "

       scope = expr.left.item_decl
       qual_name = expr.field_name
       name = qual_name.id

       # !? .str.
       if name == "str" :
          expr.str_field = True
          expr.item_type = self.string_named_type

       # !? .var.
       if name == "var" :
          expr.var_field = True
          expr.item_type = self.variant_named_type

       # !? .display
       if name == "display" :
          target_obj = None
          if expr.left.item_decl != None :
             target_obj = expr.left.item_decl.foreign_obj

          if self.is_subtype (target_obj, "QTextEdit") :
             expr.alt_display = "setPlainText"

          if self.is_subtype (target_obj, "QLineEdit") :
             expr.alt_display = "setText"

          if self.is_subtype (target_obj, "QCheckBox") :
             expr.alt_display = "setChecked"

          if self.is_subtype (target_obj, "QSpinBox") :
             expr.alt_display = "setValue"

          if self.is_subtype (target_obj, "QDoubleSpinBox") :
             expr.alt_display = "setValue"

       # !? .store
       if name == "store" :
          target_obj = None
          if expr.left.item_decl != None :
             target_obj = expr.left.item_decl.foreign_obj

          if self.is_subtype (target_obj, "QTextEdit") :
             expr.alt_store = "plainText"

          if self.is_subtype (target_obj, "QLineEdit") :
             expr.alt_store = "text"

          if self.is_subtype (target_obj, "QCheckBox") :
             expr.alt_store = "isChecked"

          if self.is_subtype (target_obj, "QSpinBox") :
             expr.alt_store = "value"

          if self.is_subtype (target_obj, "QDoubleSpinBox") :
             expr.alt_store = "value"

       # !? .read
       if name == "read" :
          target_obj = None
          if expr.left.item_decl != None :
             target_obj = expr.left.item_decl.foreign_obj

          if self.get_foreign_type (expr.left) == "QJsonObject" :
             expr.alt_read_json = "toString"

          if self.is_subtype (target_obj, "QXmlStreamAttributes") :
             expr.alt_read_xml = "toString"

       # !? .write
       if name == "write" :
          target_obj = None
          if expr.left.item_decl != None :
             target_obj = expr.left.item_decl.foreign_obj

          if self.get_foreign_type (expr.left) == "QJsonObject" :
             expr.alt_write_json = "toString"

          if self.is_subtype (target_obj, "QXmlStreamAttributes") :
             expr.alt_write_xml = "toString"

       # mark text, read property
       if scope != None and scope.foreign_obj != None :
          if self.is_foreign_field (scope, name) :
             self.enter_foreign_field (scope, name, qual_name, scope.foreign_obj)
             self.markUsage (qual_name, qual_name.item_decl)
             self.read_property (qual_name)
             expr.item_decl = qual_name.item_decl

   # -----------------------------------------------------------------------

   # Qt field initialization

   def find_foreign_obj (self, name) :
       result = None
       if name in self.foreign_scope.item_dict :
          result = self.foreign_scope.item_dict [name].foreign_obj
       return result

   def is_subtype (self, obj, name) :
       type = self.find_foreign_obj (name)
       result = obj != None and type != None and issubclass (obj, type)
       return result

   def custom_simple_item (self, simple_item) :
       " variable initialization --> add Qt initialization "

       if not simple_item.is_function :
          self.variable_initialization (simple_item)
          self.other_initialization (simple_item)
          # if simple_item.item_body != None :
          #    self.place_variable (simple_item)
          # Note: place_variable is moved to target variable initialization
          type = simple_item.item_type
          if isinstance (type, PointerType) :
             type = type.type_from
          if isinstance (type, NamedType):
             simple_item.foreign_obj = getattr (type.type_decl, "foreign_obj", None)

   def other_initialization (self, var) :
       "initialize variables with simple Qt types"
       type = var.item_type

       if type != None and getattr (type, "type_decl", None) != None :
          type_decl = type.type_decl
          if type_decl.item_context.item_qual == "(foreign)" : # !?
             foreign_type = type_decl.item_name
             if foreign_type == "QString" :
                var.alt_init = "<empty_qstring>"
             elif foreign_type == "QStringList" :
                var.alt_init = "<empty_qstringlist>"
             elif foreign_type == "QList" :
                var.alt_init = "<empty_qlist>"
             elif foreign_type == "QVector" :
                var.alt_init = "<empty_qvector>"
             elif foreign_type == "QMap" :
                var.alt_init = "<empty_qmap>"

   def place_variable (self, var) :
       "add variable to target location"

       type = var.item_type
       type_name = ""
       if isinstance (type, PointerType) :
          type = type.type_from
       if getattr (type, "type_label", "") != "" :
          type_name = type.type_label

       local_obj = var.foreign_obj

       target_obj = None
       if var.item_place != None :
          target_obj = var.item_place.foreign_obj
       else :
          target_obj = var.item_context.foreign_obj

       if self.is_subtype (target_obj, "QMainWindow") :
          if self.is_subtype (local_obj, "QMenuBar") :
             var.alt_create = "<menuBar>"
          elif self.is_subtype (local_obj, "QToolBar") :
             var.alt_create = "<addToolBar>"
          elif self.is_subtype (local_obj, "QStatusBar") :
             var.alt_create = "<statusBar>"
          elif self.is_subtype (local_obj, "QLayout")  :
             var.alt_setup = "<layout>"
          elif self.is_subtype (local_obj, "QWidget")  :
             var.alt_setup = "<setCentralWidget>"

       if var.alt_create == "" :
          if self.is_subtype (local_obj, "QTreeWidgetItem") :
             var.alt_create = type_name
             var.alt_create_place = True
          elif self.is_subtype (local_obj, "QTableWidgetItem") :
             var.alt_create = type_name
          elif self.is_subtype (local_obj, "QWidget") :
             var.alt_create = type_name
             var.alt_create_owner = True
          elif self.is_subtype (local_obj, "QAction") :
             var.alt_create = type_name
             var.alt_create_owner = True
          elif self.is_subtype (local_obj, "QLayout") :
             var.alt_create = type_name

       if var.alt_setup == "" :
          if self.is_subtype (target_obj, "QWidget") :
             if self.is_subtype (local_obj, "QLayout") :
                var.alt_setup = "setLayout"

       if self.is_subtype (target_obj, "QLayout") :
          if self.is_subtype (local_obj, "QLayout") :
             var.alt_setup = "addLayout"
          elif self.is_subtype (local_obj, "QWidget") :
             var.alt_setup = "addWidget"

       if self.is_subtype (target_obj, "QMenuBar") and self.is_subtype (local_obj, "QMenu") :
          var.alt_setup = "addMenu"
       elif self.is_subtype (local_obj, "QAction") :
          var.alt_setup = "addAction"
       elif self.is_subtype (target_obj, "QTabWidget") :
          var.alt_setup = "addTab"
          var.alt_setup_param = quoteString (var.item_name) # !?
       elif self.is_subtype (target_obj, "QTreeWidget") :
          var.alt_setup = "addTopLevelItem"

       elif (self.is_subtype (target_obj, "QToolBar") or
             self.is_subtype (target_obj, "QStatusBar") or
             self.is_subtype (target_obj, "QSplitter") ) :
          var.alt_setup = "addWidget"

       elif self.is_subtype (target_obj, "QWidget") and self.is_subtype (local_obj, "QWidget") :
           pass
       elif target_obj != None and self.is_subtype (local_obj, "QWidget") :
          var.alt_setup = "addWidget"

   # -----------------------------------------------------------------------

   "Qt connect"

   def custom_open_expr_block (self, stat) :
       " expression { ... } --> open scope for function called by signal"
       super (CmmQtCompiler, self).custom_open_expr_block (stat)
       method = self.with_signal (stat)
       if method != None :
          stat.remember_method = method
          local_scope = self.createLocalScope ()
          local_scope.independent_scope = True
          self.openScope (local_scope)

   def custom_close_expr_block (self, stat) :
       " expression { ... } --> close scope "
       method = getattr (stat, "remember_method", None)
       if method != None :
          self.closeScope ()
          method.body = stat.body
       super (CmmQtCompiler, self).custom_close_expr_block (stat)

   # -----------------------------------------------------------------------

   # SIGNAL / SLOT expression

   def is_signal_slot (self) :
       " predicate used in cmm.g grammar"
       return self.isKeyword ("SIGNAL") or self.isKeyword ("SLOT")

   """
      { is_signal_slot () }? signal_slot_expr
   """

   """
   signal_slot_expr :
      macro_name:identifier
      '('
      func_name:identifier
      (
         '('
          parameters:parameter_declaration_list
         ')'
      )?
   """

   # -----------------------------------------------------------------------

   """
   Not used:

   def custom_ident_expr (self, expr) :
       if expr.kind == simpleName :
          name = expr.id
          if name == "SIGNAL" or name == "SLOT" :
             expr.macro_name = name
             self.checkSeparator ('(')
             expr.func_name = self.readIdentifier ()
             if self.isSeparator ('(') :
                self.checkSeparator ('(')
                self.parameters = self.parse_parameter_declaration_list ()
                self.checkSeparator (')')
             self.checkSeparator (')')
   """

   # -----------------------------------------------------------------------

   # Move variable

   def custom_simple_statement (self, stat) :
       " only_variable_name ; --> move variable to this location "

       expr = stat.inner_expr
       if expr.kind == simpleName :
          decl = expr.item_decl

          if decl != None and isinstance (decl, Variable) :
             "only variable name => move variable"
             var = decl
             if var.move_variable :
                self.warning ("Variable already moved: " + decl.item_name)
             "move variable"
             stat.move_statement = True
             var.move_variable = True
             var.item_place = self.display [-1]
             self.place_variable (var)
             self.rearrange_variable (var)

   def rearrange_variable (self, var) :
       "move variable to this location"
       if var.item_body != None :
          for stat in var.item_body.items :
              if stat.kind == simpleStat and stat.body != None :
                 self.custom_open_expr_block (stat)
              if stat.kind == simpleDecl :
                 for item in stat.items :
                     if not item.is_function :
                        self.rearrange_variable (item)

# --------------------------------------------------------------------------

class CmmExtCompiler (CmmQtCompiler) :

   def __init__ (self) :
       super (CmmExtCompiler, self).__init__ ()

       "additional attributes"
       self.attribute_modules = [ ]
       self.attribute_dict = { }

       "language extensions"
       self.extension_modules = [ ] # Python modules with compiler extensions
       self.extension_classes = { }
       self.extension_functions = { }
       self.extension_cnt = 0

       "code blocks"
       self.target_stack = [ ]

       self.subst_dict = { }
       self.rename_dict = { }

       "GPU __global__"
       self.remember_global = False

       "options"
       self.skip_functions = False

       "type scope"
       self.type_scope = self.registerInnerScope (self.global_scope, "(type)")

       "expr scope"
       self.expr_cnt = 0
       self.expr_scope = self.registerInnerScope (self.global_scope, "(expr)")

   # -----------------------------------------------------------------------

   "add classes from extension_modules to extension_classes"

   def setup_extension (self) :
       for module in self.extension_modules :
           # print ("EXTENSION MODULE", module)
           all = getattr (module, "__all__", None)
           for name, member in inspect.getmembers (module) :
               if all == None or name in all :
                  if inspect.isclass (member) :
                     if member.__module__ == module.__name__ :
                         # print ("ADD EXTENSION CLASS", name)
                         self.extension_classes [name] = member

   def compile_program (self) :
       self.setup_extension ()
       super (CmmExtCompiler, self).compile_program ()
       # L: const-fold 'if (CONST) { decls }' na top-level. Členy
       # vítězné větve zůstanou v global_scope, prohrávající označíme
       # skip_code.
       self._const_fold_global_ifs ()

   # -----------------------------------------------------------------------

   # type scope

   def enter_type (self, type) :
       name = str (type)
       if name in self.type_scope.item_dict :
          decl = self.type_scope.item_dict [name]
          self.copy_style (type, decl)
       else :
          type.item_name = name
          self.enterIntoScope (self.type_scope, type)
          self.selectColor (type, table = "typeColors")

   # -----------------------------------------------------------------------

   ".fields"

   def custom_field (self, expr) :
       super (CmmExtCompiler, self).custom_field (expr)

       left = expr.left
       right = expr.field_name

       "artificial fields"
       if isinstance (left.item_decl, Class) :
          print ("CUSTOM FIELD", right.id)
          if right.item_decl == None and right.id == "fields" :
             "fields - list of variables declared in class"
             fields = [ ]
             for item in left.item_decl.item_list :
                 if isinstance (item, Variable) and not item.is_function :
                    fields.append (NoQuote (item.item_name))
             expr.item_value = fields

   # -----------------------------------------------------------------------

   def custom_attributes (self, decl) :
       super (CmmExtCompiler, self).custom_attributes (decl)
       if self.display [-1].attr_compile_time :
          decl.attr_compile_time = True

   def custom_stop_class (self, cls) :
       super (CmmExtCompiler, self).custom_stop_class (cls)
       if cls.attr_compile_time :
          if cls.members == None or len (cls.members.items) == 0 :
             cls.skip_code = True

   # -----------------------------------------------------------------------

   "GPU __global__"

   def on_open_flexible_stat (self) :
       self.remember_leading = True

       self.remember_global = False
       if self.isKeyword ("__global__") :
          self.remember_global = True
          self.nextToken ()

   def on_open_simple_stat (self, stat) :
       if self.remember_global :
          error ("Unexpected __global__")

   def on_open_constructor_declaration (self, decl) :
       if self.remember_global :
          error ("Unexpected __global__")

   def on_open_simple_declaration (self, simple_decl) :
       if self.remember_global :
          simple_decl.type_spec.item_type.gpu_global = True

   # -----------------------------------------------------------------------

   def createExtensionStat (self) :
       # https://stackoverflow.com/questions/15247075/how-can-i-dynamically-create-derived-classes-from-a-base-class
       self.extension_cnt = self.extension_cnt + 1
       cls_name = "CmmExtensionStat" + str (self.extension_cnt)
       base_list = (CmmExtensionStat,)
       cls = type (cls_name, base_list, {})

       # result = CmmExtensionStat ()
       result = cls ()
       initExtensionStat (result)
       self.storeLocation (result)
       return result

   # -----------------------------------------------------------------------

   "convert directives, comments and empty lines to declarations"

   def on_declaration (self, decl_list) :
       if self.report_directives :
          for note in self.notes :

             # print ("NOTE", note.name, ", ", note.value)

             "CmmExtensionStat"

             if note.name == "include" :
                result = self.createExtensionStat ()
                result.name = note.name
                result.param = note.value
                decl_list.items.append (result)
                # print ("INCLUDE", result.text)

             elif note.name == "directive" :
                result = self.createExtensionStat ()
                result.name = note.name
                result.param = note.value
                decl_list.items.append (result)
                # print ("DIRECTIVE", result.text)

             elif note.name == "comment" :
                result = self.createExtensionStat ()
                result.name = note.name
                result.param = note.value
                decl_list.items.append (result)
                # print ("COMMENT", result.text)

             elif note.name == "empty_line" :
                result = self.createExtensionStat ()
                result.name = "empty_line"
                decl_list.items.append (result)
                # print ("EMPTY LINE")

             # else :
             #    print ("UNKNOWN NOTE", note.name, ", ", note.value)

          self.notes = [ ]

   # -----------------------------------------------------------------------

   "extension_classes and extension_functions"

   def parse_flexible_stat (self) :
       result = None

       if self.isIdentifier () :
          name = self.tokenText

          "CmmExtensionStat"

          if name == "code" or name == "store" or name == "into":
             result = self.code_block ()

          elif name == "run" :
             result = self.run_block ()

          elif name in self.extension_classes :
             print ("EXTENSION CLASS", name)
             self.setInk ("cornflowerblue")
             cls = self.extension_classes [name]
             obj = cls (self)
             result = self.createExtensionStat ()
             result.name = "extension"
             result.param = name
             self.nextToken ()
             self.check ("{")
             while self.tokenText != "}" :
                name = self.readIdentifier ()
                self.check ("=")
                expr = self.parse_expr ()
                value = None
                if expr.kind == intValue :
                   value = expr.item_value
                if expr.kind == stringValue :
                   value = expr.item_value
                if expr.kind == simpleName :
                   value = expr.id
                   if value == "true" :
                      value = True
                   if value == "false" :
                      value = False
                self.check (";")
                setattr (obj, name, value)
                print ("ITEM", name, "=", value)
             self.check ("}")
             obj.extension_statement = result
             result.extension_object = obj
             obj.compile ()
             # print ("END OF EXTENSION CLASS", name, self.tokenText)

          elif name in self.extension_functions :
             print ("EXTENSION FUNCTION", name)
             self.setInk ("cornflowerblue")
             func = self.extension_functions [name]
             result = func ()

       if result == None :
          result = super (CmmExtCompiler, self).parse_flexible_stat ()

       return result

   # -----------------------------------------------------------------------

   def code_block (self) :

       result = self.createExtensionStat ()
       result.name = "code"
       result.into_expr = None
       result.store_expr = None
       result.items = [ ]

       if self.tokenText == "into" :
          self.nextToken () # skip identifier
          result.info_expr = self.parse_expr ()

       if self.tokenText == "store" :
          self.nextToken () # skip identifier
          result.store_expr = self.parse_expr ()

       self.checkKeyword ("code") # skip identifier
       self.check ("{")

       while not self.isSeparator ("}") :
          item = self.parse_declaration ()
          result.items.append (item)

       self.check ("}")

       product = self.builder.create_cmm_simple_generator ()
       product.openString ()
       for item in result.items :
          product.send_declaration (item)
       code = product.closeString ()
       result.ext_source = code

       return result

   def run_block (self) :
       self.nextToken () # skip identifier
       self.check ("{")

       result = self.createExtensionStat ()
       result.name = "run"
       result.items = [ ]

       while not self.isSeparator ("}") :
          item = self.parse_declaration ()
          result.items.append (item)

       self.check ("}")

       self.builder.invoke_declarations (result.items)
       return result

   # -----------------------------------------------------------------------

   "store namespace attributes (compile_time)"

   def custom_namespace (self, ns) :
       super (CmmExtCompiler, self).custom_namespace (ns)
       "namespace attributes: compile_time"
       for group in ns.attr.items :
           for a in group.items :
               n = self.get_expr_name (a.attr_expr)
               if n == "compile_time" :
                  ns.attr_compile_time = True
                  ns.skip_code = True
               else :
                  self.error ("Unknown namespace attribute: " + n)

   "store class attributes (compile_time)"

   def custom_class (self, cls) :
       super (CmmExtCompiler, self).custom_class (cls)
       "class attributes: compile_time"
       for group in cls.attr.items :
           for a in group.items :
               n = self.get_expr_name (a.attr_expr)
               if n == "compile_time" :
                  cls.attr_compile_time = True
                  cls.skip_code = True
               else :
                  self.error ("Unknown class attribute: " + n)

   # -----------------------------------------------------------------------

   def custom_base_name (self, expr) :
       super (CmmExtCompiler, self).custom_base_name (expr)
       if expr.kind == simpleName :
          if expr.id in self.rename_dict :
             # self.warning ("RENAME " + expr.id + " to " + self.rename_dict [expr.id])
             expr.id = self.rename_dict [expr.id]
             expr.item_name = expr.id
             expr.item_decl = None # !?
             expr.mod_rename = expr.id

   # -----------------------------------------------------------------------

   "store variable attributes (compile_time, field, context)"
   "invoke variable attributes"

   def custom_simple_item (self, simple_item) :
       super (CmmExtCompiler, self).custom_simple_item (simple_item)

       if simple_item.item_name in self.rename_dict :
          # self.warning ("RENAME SIMPLE ITEM " + simple_item.item_name + " to " + self.rename_dict [simple_item.item_name])
          simple_item.item_name = self.rename_dict [simple_item.item_name]
          simple_item.item_decl = None # !?
          simple_item.mod_rename = simple_item.item_name

       "invoke attribute"
       self.invoke_simple_item_attributes (simple_item)

       "store attributes: compile_time, field, context"
       var = simple_item
       for g in var.attr.items :
           for a in g.items :
              n = self.get_expr_name (a.attr_expr)
              if n == "compile_time" :
                 "compile_time"
                 var.attr_compile_time = True
              elif n == "python" :
                 "python - compile_time written in Python"
                 var.attr_python = True
                 var.attr_compile_time = True
              elif n == "field" :
                 "field"
                 var.attr_field = True
                 var.attr_compile_time = True
              elif n == "context" :
                 "context"
                 var.attr_context = True
                 var.attr_compile_time = True
              else :
                 self.error ("Unknown attribute: " + n)

       if var.attr_compile_time :
          var.skip_code = True
          if var.attr_python :
             if not var.attr_field :
                self.check_attribute (var)

   # -----------------------------------------------------------------------

   "invoke simple item attributes (compile_time, field, context)"

   def invoke_simple_item_attributes (self, simple_item) :
       expr = simple_item.item_simple_decl.type_spec # type_spec from above simple declaration
       if expr.kind == simpleName : # !?
          "declaration: T name, where T is expr and name is decl.item_name"
          decl = expr.item_decl
          if decl != None and decl.kind == simpleItem :
             "T is declared as simpleItem"
             if decl.attr_compile_time :
                "T has compile_time attribute"
                if decl.attr_field :
                   "compile_time and field"
                   self.assign_to_field (decl.item_name) # assign True
                else :
                   "compile_time without field"
                   self.invoke_attribute (decl.item_name)

             "is it function"
             dcl = simple_item.declarator # declarator
             if dcl.qual_name == None : # !?
                if dcl.kind == functionDeclarator :
                   "declaration: T name (p1, p2, ...)"
                   values = [ ]
                   if not dcl.cv_spec.cv_const :
                      if not dcl.cv_spec.cv_volatile :
                         if dcl.exception_spec == None :
                            params = dcl.parameters
                            for param in params :
                                if (param.declarator != None or
                                    param.dots or
                                    param.item_value == None) :
                                    self.error ("Invalid attribute value")
                                values.append (param.item_value)
                   if decl.attr_field : # !? decl or dcl
                      self.assign_to_field (decl.item_name, values)
                   else :
                      self.invoke_attribute (decl.item_name, values)

   # -----------------------------------------------------------------------

   "statement containing only identifier with compile_time attribute"

   def custom_simple_statement (self, stat) :
       super (CmmExtCompiler, self).custom_simple_statement (stat)
       expr = stat.inner_expr
       if expr.kind == simpleName : # !?
          decl = expr.item_decl
          if decl != None and decl.kind == simpleDecl and decl.attr_compile_time :
             "statement containing only identifier with compile_time attribute"
             if decl.attr_field :
                "compile_time and field"
                self.assign_to_field (decl.item_name) # assign True
             else :
                "compile_time without field"
                self.invoke_attribute (decl.item_name)

   # -----------------------------------------------------------------------

   def custom_close_function (self, simple_item) :
       super (CmmExtCompiler, self).custom_close_function (simple_item)
       if simple_item.is_function and simple_item.attr_compile_time and not simple_item.attr_python :
          simple_item.python_source = self.builder.translate_declarations ([simple_item.item_simple_decl])
          # https://stackoverflow.com/questions/1463306/how-to-get-local-variables-updated-when-using-the-exec-call
          gdict = globals ()
          gdict ["global_compiler"] = self # !?
          ldict = { }
          self.builder.invoke_python (simple_item.python_source, gdict = gdict, ldict = ldict)
          for key in ldict :
             func = ldict [key]
             simple_item.python_func = func

   # -----------------------------------------------------------------------

   "function call with compile_time attribute"

   def custom_call (self, expr) :
       super (CmmExtCompiler, self).custom_call (expr)
       left = expr.left
       if left.kind == simpleName : # !?
          decl = left.item_decl
          if decl != None and decl.kind == simpleItem and decl.is_function :
             if decl.attr_compile_time :
                "function call with compile_time attribute"

                name = decl.item_name
                values = [ ]
                if decl.attr_context :
                   values.append (expr)

                inx = 0
                for param in expr.param_list.items :
                    inx = inx + 1
                    # if param.attr_context :
                    #    "parameter with context attrbute"
                    #    value = param
                    # else :
                    if 1 :
                       if hasattr (param, "item_value") :
                          value = param.item_value
                       elif decl.attr_compile_time :
                          value = param
                       else :
                          value = None
                          self.error ("Unknown value of attribute parameter: " + name + " " + str (inx))
                    values.append (value)

                 # not now !?
                 # expr.skip_code = True

                if decl.attr_python :
                   self.invoke_attribute (name, values)
                else :
                   self.builder.print_python (decl.python_source)
                   self.target_stack.append (expr)
                   decl.python_func (*values)

   # -----------------------------------------------------------------------

   "store 'field' attribute"

   def get_expr_name (self, expr) :
       return self.get_name (expr)

   def getContext (self) :
       inx = len (self.display) - 1
       obj = None
       cont = True
       while inx > 0 and cont :
          obj = self.display[inx]
          if ( isinstance (obj, Namespace) or
               isinstance (obj, Enum) or
               isinstance (obj, Class) or
               isinstance (obj, Variable) ) :
             cont = False
          else :
             inx = inx - 1
       return obj

   def assign_to_field (self, name, value = True) :
       ctx = self.getContext ()
       setattr (ctx, name, value)
       ctx.item_tooltip = "field " + name
       self.info ("SET FIELD " + getattr (ctx, "item_name", "?") + "." + name + " = " + str (value))

   # -----------------------------------------------------------------------

   "invoke attribute"

   def find_attribute (self, name) :
       result = None
       if name in self.attribute_dict :
          result = self.attribute_dict [name]
       else :
          if hasattr (self, name) :
             result = getattr (self, name)
          if result == None :
             for module in self.attribute_modules :
                 if result == None :
                    result = getattr (module, name, None)
          if result != None :
             self.attribute_dict [name] = result
       if result == None :
          self.error ("Missing attribute implementation: " + name)
       return result

   def check_attribute (self, decl) :
       name = decl.item_name
       self.find_attribute (name) # only check

   def invoke_attribute (self, name, arg_list = [ ]) :
       obj = self.find_attribute (name)
       if obj != None :
          if callable (obj) :
             self.info ("INVOKE " + name)
             obj (*arg_list)
          else :
             self.warning ("INVOKE NOT CALLABLE" + name)
       else :
          self.warning ("UNKNOWN INVOKE " + name)

   # -----------------------------------------------------------------------

   "attributes"

   def ink (self, color) :
       obj = self.getContext ()
       obj.item_ink = findColor (color)
       print ("INK", str (obj), color)

   def paper (self, color) :
       obj = self.getContext ()
       obj.item_paper = findColor (color)
       print ("PAPER", color)

   def _icon (self, name) :
       obj = self.getContext ()
       obj.item_icon = name
       print ("ICON", name)

   def tooltip (self, text) :
       obj = self.getContext ()
       obj.item_tooltip = text
       print ("TOOLTIP", text)

   def alpha (self) :
       self.info ("Function alpha")

   def beta (self) :
       self.info ("Function beta")

   def gamma (self, val) :
       self.info ("Function gamma (" + str (val) + ")")

   def delta (self, param1, param2) :
       self.info ("Function delta")

   # -----------------------------------------------------------------------

   "custom expression colors"

   def custom_type_specifiers (self, type_spec, type) :
       super (CmmExtCompiler, self).custom_type_specifiers (type_spec, type)
       if isinstance (type, SimpleType) :
          self.enter_type (type)
          self.markUsage (type)

   def custom_binary (self, expr, inx) :
       "color int/float/other arithmetic"
       super (CmmExtCompiler, self).custom_binary (expr, inx)
       if inx <= self.longInx :
          color = findColor ("blue")
       elif inx <= self.doubleInx :
          color = findColor ("magenta")
       else :
          color = findColor ("orange")

       self.enter_expr (expr, color)

   def custom_relation (self, expr) :
       "color relation"
       super (CmmExtCompiler, self).custom_relation (expr)
       color = findColor ("lime")
       self.enter_expr (expr, color)

   def enter_expr (self, obj, color) :
       self.expr_cnt = self.expr_cnt + 1
       name = "(" + str (self.expr_cnt) + ")"
       note = obj
       initDeclaration (obj)
       self.copy_location (note, obj)
       self.register (self.expr_scope, name, note)
       self.mark_expr (obj, note, color)

   def mark_expr (self, expr, obj, color) :
       info = obj.item_qual
       tooltip = ""
       if getattr (obj, "item_type", None) != None :
          tooltip = str (obj.item_type)
       # !? self.markText (expr, paper = color, info = info, tooltip = tooltip)
       self.markText (expr, info = info, tooltip = tooltip)

   # -----------------------------------------------------------------------

   "tree of statements in Classes and Navigator"

   def add_assign (self, stat, expr) :
       left = expr.left
       right = expr.right
       name = self.get_expr_name (left)
       if name != "" :
          stat.item_label = "assign to " + name
          stat.item_icon = "assign"

   def add_call (self, stat, expr) :
       left = expr.left
       params = expr.param_list
       name = self.get_expr_name (left)
       if name != "" :
          stat.item_label = "call " + name
          stat.item_icon = "call"

   def add_identifier (self, stat, expr) :
       name = self.get_expr_name (expr)
       if name != "" :
          stat.item_label = "identifier reference " + name
          stat.item_icon = "nothing"

   def add_simple_stat (self, stat) :
       expr = stat.inner_expr
       if expr.kind == simpleName :
          self.add_identifier (stat, expr)
       elif expr.kind == assignExpr :
          self.add_assign (stat, expr)
       elif expr.kind == callExpr :
          self.add_call (stat, expr)

   def add_with_stat (self, stat) :
       expr = stat.inner_expr
       name = self.get_expr_name (expr)
       if expr.kind == simpleName :
          stat.item_label = "with " + name
          stat.item_icon = "with"
       elif expr.kind == callExpr :
          stat.item_label = "define short function " + name
          stat.item_icon = "local-define"

   def add_simple_decl (self, stat) :
       for item in stat.items :
           name = item.item_name
           func = item.is_function

           if func :
              if stat.body != None :
                 stat.item_label = "define local function " + name
                 stat.item_icon = "local-define"
              else :
                 stat.item_label = "declare local function " + name
                 stat.item_icon = "local-declare"
           else :
                 stat.item_label = "declare local variable " + name
                 stat.item_icon = "local-variable"
                 if stat.body != None :
                    stat.item_label = stat.item_label + " (block)"
                 if item.init != None :
                    stat.item_label = stat.item_label + " (assign)"

   def custom_statement (self, target, stat) :
       super (CmmExtCompiler, self).custom_statement (target, stat)
       if stat != None :
          kind = stat.kind
          if kind != emptyStat :

             if not hasattr (target, "item_block") : # item_block ... items visible in Class Tree
                target.item_block = [ ]
             target.item_block.append (stat)

             if kind == simpleStat :
                if stat.body != None :
                   stat.item_label = "with statement"
                   if hasattr (stat.body, "items") :
                      for item in stat.body.items :
                          self.custom_statement (stat, item)
                else :
                   stat.item_label = "simple statement"
             elif kind == simpleDecl :
                stat.item_label = "simple declaration"
                self.add_simple_decl (stat)
                if stat.body != None :
                   for item in stat.body.items :
                      self.custom_statement (stat, item)
             elif kind == compoundStat :
                stat.item_label = "{}"
                for item in stat.items :
                    self.custom_statement (stat, item)
             elif kind == ifStat :
                stat.item_label = "if"
                self.custom_statement (stat, stat.then_stat)
                if stat.else_stat != None :
                   self.custom_statement (stat, stat.else_stat)
             elif kind == forStat:
                stat.item_label = "for"
                self.custom_statement (stat, stat.body)
             elif kind == whileStat:
                stat.item_label = "while"
                self.custom_statement (stat, stat.body)
             elif kind in [doStat, switchStat, caseStat] :
                self.custom_statement (stat, stat.body)

   # -----------------------------------------------------------------------

   # overloaded functions

   """
   def custom_call (self, expr) :
       super (CmmExtCompiler, self).custom_call (expr)
       left = expr.left
       if left.kind == simpleName : # !?
          if isinstance (left.item_decl, CmmFunctions) : # overloaded functions
             print ("FUNCTIONS")
             if len (expr.param_list.items) == 1 :
                arg = expr.param_list.items[0] # just one actual parameter
                if hasattr (arg, "item_type") and arg.item_type != None :
                   print ("searching for: " + arg.type_label)
                   for func in left.item_decl.item_list :
                      print ("point (1)")
                      # is it function
                      inx = len (func.declarator.cont.items) - 1
                      if inx >= 0 :
                         print ("point (2)")
                         c = func.declarator.cont.items [inx]
                         if isinstance (c, CmmFunctionSpecifier) :
                            print ("point (3)")
                            if len (c.parameters.items) == 1 : # just one parameter
                               print ("point (4)")
                               param = c.parameters.items [0]
                               if isinstance (param, CmmParamItem) :
                                  print ("point (5)", param.type_spec)
                                  if getattr (param.type_spec, "item_decl", None) != None :
                                     print ("point (6)", param.type_spec.item_decl)
                                     print ("consider: " + param.type_spec.type_label)
                                     left.item_qual = func.item_qual
                                     self.markUsage (left) # again
   """

   # -----------------------------------------------------------------------

   # templates

   def create_instance (self, qual_name) :
       decl = qual_name.item_decl
       self.info ("create_instance")
       qual_name.template_source = decl.template_decl
       qual_name.template_instance = self.copy_template (decl.template_decl, qual_name.template_args)
       if "template_instance" not in qual_name._fields_ :
          qual_name._fields_.append ("template_instance")

       top = self.global_scope
       top.item_list.append (qual_name.template_instance.inner_declaration)
       self.global_scope.items.append (qual_name.template_instance.inner_declaration)

   def get_instance_identification (self, obj) :
       cnt = getattr (obj, "inst_cnt", 0)
       cnt = cnt + 1
       obj.inst_cnt = cnt
       result = obj.item_qual + "." + "<" + str (cnt) + ">"
       return result

   def copy_template (self, source, args) :
       self.info ("copy_template")
       param_dict = { }
       result = copy.deepcopy (source)

       inx = 0
       cnt = len (args.items)

       if source.params != None :
          for param in source.params.items :
              param_name =  ""
              if isinstance (param, CmmTemplateTypeParam) :
                 param_name = param.simp_name.id
              elif isinstance (param, CmmTemplateValueParam) :
                 if param.type.type_spec.basic_name != None :
                    param_name = param.type.type_spec.basic_name.id
              param_value = ""
              # if inx < cnt :
                 # arg = args.items [inx]
                 # if isinstance (arg, CmmTemplateTypeArg) :
                 #    if arg.type.type_spec.basic_name != None :
                 #       param_value = arg.type.type_spec.basic_name.id
                 # elif isinstance (arg, CmmTemplateValueArg) :
                 #    param_value = arg.value
              inx = inx + 1
              # self.info ("Template parameter: "+ param_name + " = " + param_value)
              param_dict [param_name] = param_value

       self.scan_template (result, param_dict)
       return result

   def scan_template (self, obj, param_dict) :
       if isinstance (obj, CmmTypeSpec) :
          bn = getattr (obj, 'basic_name', None)
          if bn is not None :
             name = getattr (bn, 'id', None)
             if name is not None and name in param_dict :
                bn.id = param_dict [name]

       for name in obj._fields_ :
           field = getattr (obj, name, None)
           if field != None :
              if hasattr (field, "_fields_") :
                 self.scan_template (field, param_dict)
       if hasattr (obj, "items") :
          for item in obj.items :
              if hasattr (item, "_fields_") :
                 self.scan_template (item, param_dict)

   def on_template_declaration (self, decl) :
       # print ("on_template_declaration", decl.inner_declaration, decl)
       decl.inner_declaration.template_decl = decl

   # -----------------------------------------------------------------------
   # 'stencil' šablony — varianta template s textovou instantiací
   # (AST → c2cpp → re-parse). Dva hooky:
   #
   #   on_stencil_params: voláno PŘED parsováním těla. Registrujeme
   #     typové parametry (T) jako falešné typedef do aktuálního scope.
   #     Bez toho by 'T a' v parametrech těla selhalo (parser by T bral
   #     jako výraz). Po dokončení těla už T v scope nevadí — instantiace
   #     beztak pracuje s deep-copy AST.
   #
   #   on_stencil_declaration: voláno PO parsování těla. Naváže
   #     stencil_decl na inner_declaration (analogicky k template_decl)
   #     pro pozdější instanci.

   def on_stencil_params (self, decl) :
       if getattr (decl, 'params', None) is None :
          return
       decl._stencil_param_decls = [ ]
       for p in decl.params.items :
           if isinstance (p, CmmTemplateTypeParam) and p.simp_name is not None :
              name = p.simp_name.id
              # Lehký placeholder typu: enum/typedef/class — všechny
              # vrátí True z isTypeObject a tím flagnou type_flag pro
              # ident_expr 'T' v parametrech a tělech.
              td = CmmTypedefDecl ()
              initTypedef (td)
              td.item_name = name
              td.kind = typedefDecl
              self.copy_location (td, p)
              try :
                 self.enter (td)
                 decl._stencil_param_decls.append (td)
              except Exception as e :
                 print ("stencil: failed to register type param", name, ":", e)

   def on_open_stencil (self, decl) :
       """Vstoupíme do stencilu jako do scope — členské deklarace v
       jeho '{ }' nepůjdou do global, ale do stencil-scope. Instantiace
       je pak vytáhne s manglingem do global. Nasimulujeme to přes
       initScope (analog s class)."""
       initScope (decl)
       decl.item_name = decl.simp_name.id
       decl.hidden_scope = True
       self.display.append (decl) # push scope na zásobník

   def on_close_stencil (self, decl) :
       """Pop stencil scope."""
       if self.display and self.display [-1] is decl :
          self.display.pop ()

   def on_stencil_declaration (self, decl) :
       """Pojmenovaný stencil:
            stencil <name> <typename T> { decl1; decl2; ... }
       Po popnutí scope (close_stencil již proběhl) jen zaregistrujeme
       stencil do okolního scope pod jeho jménem."""
       decl.item_name = decl.simp_name.id
       decl.stencil_decl = decl # samo na sebe — sentinel pro detekci
       decl.template_decl = decl # pro is_template_name v parseru
       try :
          self.enter (decl)
       except Exception as e :
          print ("stencil registration failed:", e)

   # -----------------------------------------------------------------------
   # Stencil instantiation: deep-copy + AST substituce + c2cpp render
   # + registrace v global_scope. Cache podle (stencil id, type args)
   # zajistí, že 'id<int>(7)' a 'id<int>(13)' sdílí jednu instanci.

   def _instantiate_stencil (self, qual_name, target_decl) :
       stencil = getattr (target_decl, 'stencil_decl', None)
       if stencil is None :
          return None
       # K1 stub: pojmenované stenciles s 'members' polem se budou
       # instantiovat v K2 (přes natural-deklarační intercept).
       # Tady jen vyhneme se starém deep-copy path, které neumí novou
       # strukturu.
       if hasattr (stencil, 'members') :
          return None

       # Vytáhni typové argumenty
       args_sect = getattr (qual_name, 'template_args', None)
       arg_types = self._stencil_arg_types (args_sect)
       if not arg_types :
          return None

       # Cache: jednu instanci na unikátní (stencil, types) dvojici
       if not hasattr (self, '_stencil_cache') :
          self._stencil_cache = { }
       cache_key = (id (stencil), tuple (arg_types))
       if cache_key in self._stencil_cache :
          return self._stencil_cache [cache_key]

       # Sestav param_dict: T -> "int"
       param_dict = { }
       if stencil.params is not None :
          params = stencil.params.items
          for inx, p in enumerate (params) :
              if isinstance (p, CmmTemplateTypeParam) and p.simp_name is not None :
                 if inx < len (arg_types) :
                    param_dict [p.simp_name.id] = arg_types [inx]

       # AST-aware copy (copy.deepcopy by se přes item_decl chain
       # dostal až k modulům, což pickle nezvládá). Kopírujeme jen
       # AST strukturu (_fields_ + items); item_decl a podobné
       # back-references zůstanou prázdné — beztak je c2cpp/parser
       # při dalším zpracování dosadí znovu.
       instance = self._ast_copy (stencil)
       self.scan_template (instance, param_dict)

       # Mangling: 'id' -> 'id__int'
       suffix = "_".join (arg_types)
       inst_inner = instance.inner_declaration
       inst_items = getattr (inst_inner, 'items', None)
       inst_item = None
       if inst_items :
          for it in inst_items :
              it.item_name = it.item_name + "__" + suffix
              # Instance už NENÍ template — vyčistíme markery, aby
              # ji další volání nezkoušelo znovu instantiovat.
              it.template_decl = None
              it.stencil_decl = None
              if inst_item is None :
                 inst_item = it
       inst_inner.template_decl = None
       inst_inner.stencil_decl = None

       # Render přes c2cpp pro viditelnou ukázku studentům
       # (nedělá žádnou skutečnou práci v překladu, jen tisk).
       self._render_stencil_instance (stencil, instance, param_dict)

       # Registruj v global_scope: do item_list přidáme přímo
       # CmmSimpleItem (resolved item), do items přidáme syntactic
       # CmmSimpleDecl (wrapper) — tak se chová běžný enter/parse_*.
       if inst_item is not None :
          self.global_scope.item_list.append (inst_item)
          if getattr (inst_item, 'item_name', None) :
             self.global_scope.item_dict [inst_item.item_name] = inst_item
       self.global_scope.items.append (inst_inner)

       self._stencil_cache [cache_key] = inst_item
       return inst_item

   def _ast_copy (self, node, memo = None) :
       """Bezpečná kopie AST: prochází jen ._fields_ a .items, takže
       se nedostane k back-references (item_decl → scope → cmm_comp →
       foreign_modules), které copy.deepcopy nezvládne (modul nelze
       picklovat). Pro stencil instantiation nám stačí čistý AST sub-
       strom — item_decly se beztak po render+substituci znovu vyřeší."""
       if memo is None :
          memo = { }
       if node is None :
          return None
       if id (node) in memo :
          return memo [id (node)]
       if not hasattr (node, '_fields_') :
          return node # primitiva, stringy, čísla — sdílíme

       cls = type (node)
       new = cls.__new__ (cls)
       try :
          cls.__init__ (new)
       except TypeError :
          pass # některé třídy mají povinné argy konstruktoru
       memo [id (node)] = new

       # Jednu utility pro kopii libovolné hodnoty: primitivy → kopie,
       # AST node nebo Type (FunctionType atd.) → rekurze, list → list
       # filtrované rekurze, jinak skip (moduly, callable, dict —
       # typicky back-refs).
       import types as _types
       def cp (v) :
          if v is None : return None
          if isinstance (v, (int, str, bool, float)) : return v
          if isinstance (v, _types.ModuleType) : return None
          if callable (v) : return None
          if hasattr (v, '_fields_') : return self._ast_copy (v, memo)
          # Rekurze i do code.py / cmm_parser.py objektů bez _fields_
          # (Type, CompoundType, NamedType, FunctionType, ...).
          mod = getattr (type (v), '__module__', '')
          if mod in ('code', 'cmm_parser') and hasattr (v, '__dict__') :
             return self._ast_copy (v, memo)
          if isinstance (v, list) : return [ cp (x) for x in v ]
          if isinstance (v, tuple) : return tuple (cp (x) for x in v)
          if isinstance (v, dict) : return None # back-refs / item_dict
          return None

       # Projdi všechny atributy z __dict__ — bezpečně nakopíruj všechno,
       # co je primitivum nebo AST. Tím dostaneme i ne-_fields_ atributy
       # jako item_body, item_type, is_function, item_name atd.
       src = getattr (node, '__dict__', { })
       for attr, val in list (src.items ()) :
           if attr.startswith ('_') : continue
           setattr (new, attr, cp (val))
       return new

   def _eval_const_int (self, expr) :
       """Compile-time vyhodnocení celočíselného výrazu.
       Stejné principy jako v cmm_generate.py + sizeof a logické op."""
       if expr is None : return None
       kind = getattr (expr, 'kind', None)
       if kind == intValue :
          try : return int (expr.value)
          except (ValueError, TypeError) : return None
       if kind == simpleName :
          ident = getattr (expr, 'id', '')
          if ident == 'true'  : return 1
          if ident in ('false', 'nullptr', 'NULL', 'null') : return 0
          decl = getattr (expr, 'item_decl', None)
          if decl is None : return None
          init = getattr (decl, 'init', None)
          if init is None : return None
          inner = getattr (getattr (init, 'value', None), 'inner_expr', None)
          return self._eval_const_int (inner)
       if kind == subexprExpr :
          return self._eval_const_int (expr.param)
       if kind == simpleStat :
          # condition_value wrapper (parser obaluje cond v if/while)
          return self._eval_const_int (expr.inner_expr)
       if kind == minusExpr :
          v = self._eval_const_int (expr.param)
          return - v if v is not None else None
       if kind == plusExpr :
          return self._eval_const_int (expr.param)
       if kind == logNotExpr :
          v = self._eval_const_int (expr.param)
          return None if v is None else (0 if v else 1)
       if kind == bitNotExpr :
          v = self._eval_const_int (expr.param)
          return None if v is None else ~v
       if kind == sizeofExpr :
          val = expr.value
          while val is not None and getattr (val, 'kind', None) == subexprExpr :
             val = val.param
          if val is None : return None
          item_type = getattr (val, 'item_type', None)
          if item_type is None : return 8
          return self._size_of_type (item_type)
       if kind in (addExpr, subExpr, mulExpr, divExpr, modExpr,
                   bitAndExpr, bitOrExpr, bitXorExpr, shlExpr, shrExpr) :
          l = self._eval_const_int (expr.left)
          r = self._eval_const_int (expr.right)
          if l is None or r is None : return None
          if kind == addExpr : return l + r
          if kind == subExpr : return l - r
          if kind == mulExpr : return l * r
          if kind == divExpr : return l // r if r != 0 else None
          if kind == modExpr : return l %  r if r != 0 else None
          if kind == bitAndExpr : return l & r
          if kind == bitOrExpr  : return l | r
          if kind == bitXorExpr : return l ^ r
          if kind == shlExpr : return l << r
          if kind == shrExpr : return l >> r
       if kind in (ltExpr, leExpr, gtExpr, geExpr, eqExpr, neExpr) :
          l = self._eval_const_int (expr.left)
          r = self._eval_const_int (expr.right)
          if l is None or r is None : return None
          if kind == ltExpr : return 1 if l <  r else 0
          if kind == leExpr : return 1 if l <= r else 0
          if kind == gtExpr : return 1 if l >  r else 0
          if kind == geExpr : return 1 if l >= r else 0
          if kind == eqExpr : return 1 if l == r else 0
          if kind == neExpr : return 1 if l != r else 0
       if kind == logAndExpr :
          l = self._eval_const_int (expr.left)
          if l is None : return None
          if l == 0 : return 0 # short-circuit
          r = self._eval_const_int (expr.right)
          return None if r is None else (1 if r != 0 else 0)
       if kind == logOrExpr :
          l = self._eval_const_int (expr.left)
          if l is None : return None
          if l != 0 : return 1
          r = self._eval_const_int (expr.right)
          return None if r is None else (1 if r != 0 else 0)
       return None

   def _size_of_type (self, t) :
       """Velikost typu v bajtech. Pole = element * lim. Struct = sum
       polí qword-zarovnaně. Pointer/Reference/skalár = 8."""
       if isinstance (t, ArrayType) :
          cnt = self._eval_const_int (t.lim) if t.lim is not None else 0
          if cnt is None : cnt = 0
          return self._size_of_type (t.type_from) * cnt
       if isinstance (t, NamedType) :
          td = getattr (t, 'type_decl', None)
          if td is not None and getattr (td, 'kind', None) == classDecl :
             total = 0
             for member in td.item_list :
                 if isinstance (member, CmmSimpleItem) :
                    if not getattr (member, 'is_function', False) :
                       sz = self._size_of_type (member.item_type)
                       sz = (sz + 7) & ~7
                       total += sz
             return total
       return 8

   def _const_fold_global_ifs (self) :
       """Bezpečnostní pass: stejné foldování jako on_close_if_statement,
       ale po dokončení parseu — chytne if-stmts, které z nějakého důvodu
       v on_close hooku nebyly složeny. Zatím nepoužívaný (hook stačí)."""
       for item in self.global_scope.items :
           if getattr (item, 'kind', None) == ifStat :
              self._fold_if_decl_level (item)

   def _fold_if_decl_level (self, if_stat) :
       cond_val = self._eval_const_int (if_stat.cond)
       if cond_val is None :
          return
       if cond_val :
          # Take then — drop else
          if if_stat.else_stat is not None :
             self._mark_decls_skip (if_stat.else_stat)
       else :
          # Take else — drop then
          self._mark_decls_skip (if_stat.then_stat)

   def _unfold_ct_for (self, for_stat) :
       """Compile-time unfold pro 'for (T t : C.fields) <stencil_directive>'.
       Postup:
        1. Snapshot v on_open zachytil počet decl-ů před body.
        2. Body se naparsoval normálně — vytvořil scaffolding instance
           (např. t_value, t_set, t_get když body byl 'acc <int> t;').
        3. Tady vyznačíme scaffolding skip_code, ucpneme jeho položky
           v item_dict a pro každé pole třídy znova zavoláme
           _instantiate_named_stencil s field.item_name.
        Iter_expr musí být fieldExpr 'X.fields' kde X je class."""
       iter_expr = getattr (for_stat, 'iter_expr', None)
       if iter_expr is None : return
       if getattr (iter_expr, 'kind', None) != fieldExpr : return
       cls_decl = getattr (iter_expr.left, 'item_decl', None)
       if cls_decl is None or getattr (cls_decl, 'kind', None) != classDecl :
          return
       if getattr (iter_expr.field_name, 'id', None) != 'fields' :
          return

       # Sbal pole třídy
       fields = [ m for m in cls_decl.item_list
                  if isinstance (m, CmmSimpleItem) and not getattr (m, 'is_function', False) ]

       # Mark scaffolding items skip_code + odstraň z item_dict
       snap = for_stat._snap_item_count
       new_items = self.global_scope.item_list [snap:]
       for it in new_items :
           it.skip_code = True
           nm = getattr (it, 'item_name', None)
           if nm and nm in self.global_scope.item_dict :
              del self.global_scope.item_dict [nm]

       # Také loop var (z from_expr) — ten vznikl PŘED snapshotem
       fe = getattr (for_stat, 'from_expr', None)
       if fe is not None and getattr (fe, 'kind', None) == simpleDecl :
          for it in fe.items :
              it.skip_code = True

       # Najdi stencil instantiation directive v body
       body_decl = self._find_body_simple_decl (for_stat.body)
       if body_decl is None :
          print ("compile-time for: body must contain a stencil instance")
          return
       type_spec = body_decl.type_spec
       ts_decl = getattr (type_spec, 'item_decl', None)
       if ts_decl is None or getattr (ts_decl, 'kind', None) != stencilDecl :
          print ("compile-time for: body must instantiate a stencil")
          return
       arg_types = self._stencil_arg_types (
          getattr (type_spec, 'template_args', None))

       # Per field: re-instantiate s jménem pole
       for f in fields :
           self._instantiate_named_stencil (ts_decl, arg_types, f.item_name)

   def _find_body_simple_decl (self, body) :
       """V těle for-stmtu najdi první CmmSimpleDecl. Tělo může být
       compound nebo jediný stat."""
       if body is None : return None
       kind = getattr (body, 'kind', None)
       if kind == simpleDecl : return body
       if kind == compoundStat :
          for s in body.items :
              r = self._find_body_simple_decl (s)
              if r is not None : return r
       return None

   def _flatten_stencil_member (self, item, out) :
       """Plochý seznam deklarací: pokud je item ifStat s const cond,
       vyhrávající větev se rozbalí (rekurzivně), jinak item se přidá
       tak, jak je. Compound se taky rozbalí."""
       if item is None : return
       kind = getattr (item, 'kind', None)
       if kind == ifStat :
          cv = self._eval_const_int (item.cond)
          if cv is None :
             out.append (item) # nelze const-evalulovat
          elif cv :
             self._flatten_stencil_member (item.then_stat, out)
          elif item.else_stat is not None :
             self._flatten_stencil_member (item.else_stat, out)
       elif kind == compoundStat :
          for sub in item.items :
              self._flatten_stencil_member (sub, out)
       else :
          out.append (item)

   def _mark_decls_skip (self, stat) :
       """Rekurzivně označí všechny vnořené CmmSimpleItems jako
       skip_code. Pro neprovedenou větev top-level if-stat. Pro každý
       drop'd decl, pokud byl v item_dict, přepneme dict na živou
       alternativu (nebo úplně odstraníme), aby symbol resolution v
       následujícím main našel skutečný decl, ne mrtvý."""
       if stat is None : return
       kind = getattr (stat, 'kind', None)
       if kind == compoundStat :
          for s in stat.items :
              self._mark_decls_skip (s)
       elif kind == simpleDecl :
          for it in stat.items :
              it.skip_code = True
              nm = getattr (it, 'item_name', None)
              if nm :
                 self._dict_swap_to_live (nm, it)
       elif kind == ifStat :
          self._mark_decls_skip (stat.then_stat)
          if stat.else_stat is not None :
             self._mark_decls_skip (stat.else_stat)

   def _dict_swap_to_live (self, name, dropped) :
       """Pokud item_dict[name] je dropped, najdi živou alternativu
       v item_list (stejné jméno, ne skip_code) a dosaď. Když není,
       odstraníme."""
       cur = self.global_scope.item_dict.get (name)
       if cur is not dropped :
          return # dict už ukazuje jinam
       for other in self.global_scope.item_list :
           if other is dropped : continue
           if getattr (other, 'skip_code', False) : continue
           if getattr (other, 'item_name', None) == name :
              self.global_scope.item_dict [name] = other
              return
       try :
          del self.global_scope.item_dict [name]
       except KeyError :
          pass

   def _extract_simple_name (self, declarator) :
       """Vytáhne jméno z deklarátoru (např. 'numeric' z 'numeric')."""
       d = declarator
       while d is not None :
          if getattr (d, 'kind', None) == basicDeclarator :
             qn = getattr (d, 'qual_name', None)
             if qn is not None :
                return getattr (qn, 'id', None)
             return None
          # zanořit
          d = getattr (d, 'inner_declarator', None)
       return None

   def _instantiate_named_stencil (self, stencil, arg_types, instance_name) :
       """Vyrobí instanci pojmenovaného stencilu pod instance_name.
       Pro každý člen vyrobí mangled kopii (`<inst>_<member>`),
       provede dvě substituce (typové parametry a interní reference)
       a registruje do global_scope."""

       # Cache (stencil, types, inst_name) — i když inst_name dělá
       # každou instanci jedinečnou, neškodí cache.
       if not hasattr (self, '_stencil_cache') :
          self._stencil_cache = { }
       cache_key = (id (stencil), tuple (arg_types), instance_name)
       if cache_key in self._stencil_cache :
          return

       # Parametry: typové (T → int)
       param_dict = { }
       if stencil.params is not None :
          for inx, p in enumerate (stencil.params.items) :
              if isinstance (p, CmmTemplateTypeParam) and p.simp_name is not None :
                 if inx < len (arg_types) :
                    param_dict [p.simp_name.id] = arg_types [inx]

       # Členové: flattened přes const-evaluable if-stmts.
       # 'if (sizeof(T) > 4) { void big(T); }' se rozvine na 'void big(T);'
       # nebo zmizí podle eval cond.
       raw_members = list (stencil.members.items) if stencil.members else [ ]
       members = [ ]
       for m in raw_members :
           self._flatten_stencil_member (m, members)

       # Member mangling: value → numeric_value, set → numeric_set, ...
       member_dict = { }
       for m in members :
           it_list = getattr (m, 'items', None)
           if it_list :
              for it in it_list :
                  orig = getattr (it, 'item_name', None)
                  if orig :
                     member_dict [orig] = instance_name + '_' + orig

       # Render originálu přes c2cpp + textová substituce — pro
       # výuku ukáže rozbalený kód studentům. Render používá flattened
       # member list (po const-fold ifs), aby studenti viděli co
       # opravdu vznikne, ne syntakticky napsaný stencil.
       self._render_named_stencil (stencil, members, param_dict,
                                   member_dict, instance_name, arg_types)

       # AST substituce + registrace ve dvou fázích, aby item_decl
       # reference uvnitř těl po manglingu ukazovaly na nové (mangled)
       # decly. Phase 1: kopie + substituce + registrace. Phase 2:
       # fixup item_decl podle global_scope.item_dict.
       copied = [ ]
       for m in members :
           m_copy = self._ast_copy (m)
           self.scan_template (m_copy, param_dict)        # T → int
           self._scan_member_names (m_copy, member_dict)  # value → numeric_value (id i item_name)
           inner_items = getattr (m_copy, 'items', None)
           if inner_items :
              for it in inner_items :
                  it.item_simple_decl = m_copy
                  it.template_decl = None
                  it.stencil_decl = None
           self.global_scope.items.append (m_copy)
           if inner_items :
              for it in inner_items :
                  if getattr (it, 'item_name', None) :
                     self.global_scope.item_list.append (it)
                     self.global_scope.item_dict [it.item_name] = it
           copied.append (m_copy)

       # Phase 2: fixup item_decl. Pro každé CmmName uvnitř, jehož id
       # ukazuje na mangled jméno, dosaď nový decl. Bez toho by gener.
       # backendy stále referovaly na původní (před-mangled) decly.
       for m_copy in copied :
           self._fixup_decl_refs (m_copy)

       self._stencil_cache [cache_key] = True

   def _fixup_decl_refs (self, obj) :
       """Po přejmenování AST: pro každou CmmName, jehož id ukazuje na
       jméno v global_scope.item_dict, dosaď item_decl. Tím opravíme
       back-references, které _ast_copy ztratil (původní item_decl
       ukazoval na původní decl, ale my chceme na mangled instanci)."""
       if obj is None :
          return
       if isinstance (obj, CmmName) :
          if getattr (obj, 'kind', None) == simpleName :
             ident = getattr (obj, 'id', None)
             if ident :
                new_decl = self.global_scope.item_dict.get (ident)
                if new_decl is not None :
                   obj.item_decl = new_decl
       for f in getattr (obj, '_fields_', [ ]) :
           v = getattr (obj, f, None)
           if isinstance (v, list) :
              for it in v : self._fixup_decl_refs (it)
           elif hasattr (v, '_fields_') :
              self._fixup_decl_refs (v)
       items = getattr (obj, 'items', None)
       if items is not None and isinstance (items, list) :
          for it in items :
              if hasattr (it, '_fields_') :
                 self._fixup_decl_refs (it)

   def _scan_member_names (self, obj, member_dict) :
       """Walk AST: přejmenuje každé jméno v member_dict (CmmName.id
       i CmmSimpleItem.item_name)."""
       if obj is None :
          return
       if isinstance (obj, CmmName) :
          if getattr (obj, 'kind', None) == simpleName :
             ident = getattr (obj, 'id', None)
             if ident in member_dict :
                obj.id = member_dict [ident]
       if isinstance (obj, CmmSimpleItem) :
          ident = getattr (obj, 'item_name', None)
          if ident in member_dict :
             obj.item_name = member_dict [ident]
       # Rekurze přes _fields_ + items
       for f in getattr (obj, '_fields_', [ ]) :
           v = getattr (obj, f, None)
           if isinstance (v, list) :
              for it in v : self._scan_member_names (it, member_dict)
           elif hasattr (v, '_fields_') :
              self._scan_member_names (v, member_dict)
       items = getattr (obj, 'items', None)
       if items is not None and isinstance (items, list) :
          for it in items :
              if hasattr (it, '_fields_') :
                 self._scan_member_names (it, member_dict)

   def _render_named_stencil (self, stencil, flat_members, param_dict,
                              member_dict, instance_name, arg_types) :
       """Render přes c2cpp + dvojí textová substituce. Pro výuku.
       'flat_members' je po-const-fold seznam (po _flatten_stencil_member)
       — render tak ukáže přesně to, co bude výsledně přeloženo."""
       try :
          import c2cpp, tempfile, os, re
          gen = c2cpp.ToCpp ()
          gen.compiler = self
          tmp = tempfile.NamedTemporaryFile (mode = 'w', suffix = '.cpp',
                                             delete = False)
          tmp.close ()
          try :
             gen.open (tmp.name)
             for m in flat_members :
                 gen.send_declaration (m)
             gen.close ()
             with open (tmp.name) as f :
                text = f.read ()
          finally :
             try : os.unlink (tmp.name)
             except : pass

          # Substituce: nejdřív typové (T → int), pak členové
          for k, v in param_dict.items () :
              text = re.sub (r'\b' + re.escape (k) + r'\b', v, text)
          for k, v in member_dict.items () :
              text = re.sub (r'\b' + re.escape (k) + r'\b', v, text)

          tag = stencil.simp_name.id + ' <' + ', '.join (arg_types) + '> ' + instance_name
          print ()
          print ("=== stencil instance: " + tag + " ===")
          print (text.strip ())
          print ("=== end stencil instance ===")
          print ()
       except Exception as e :
          print ("stencil render skipped:", e)

   def _stencil_arg_types (self, args_sect) :
       """Z CmmTemplateArgSect (.<int, char, ...>) vytáhni názvy typů
       jako stringy. Zatím podporujeme jen základní C typy."""
       if args_sect is None :
          return [ ]
       result = [ ]
       for arg in args_sect.items :
           name = self._stencil_arg_type_name (arg)
           if name is None :
              return [ ] # nepodporovaný argument
           result.append (name)
       return result

   def _stencil_arg_type_name (self, arg) :
       """Z jednoho CmmTemplateArg vytáhni název typu."""
       val = getattr (arg, 'value', None)
       if val is None :
          return None
       ts = getattr (val, 'type_spec', None)
       if ts is None :
          return None
       # CmmTypeSpec má a_int / a_char / a_long / atd. flagy
       for name, flag in [ ('int', 'a_int'), ('char', 'a_char'),
                           ('void', 'a_void'), ('long', 'a_long'),
                           ('short', 'a_short'), ('float', 'a_float'),
                           ('double', 'a_double'), ('bool', 'a_bool') ] :
           if getattr (ts, flag, False) :
              return name
       # Pojmenovaný typ: try basic_name.id
       bn = getattr (ts, 'basic_name', None)
       if bn is not None :
          ident = getattr (bn, 'id', None)
          if ident :
             return ident
       return None

   def _render_stencil_instance (self, stencil, instance, param_dict) :
       """Vyrenderuje původní šablonu přes c2cpp do textu a textově
       nahradí typové parametry. Studentům to ukazuje, co stencil
       'rozvine' — typický postup C++ compilerů.

       Renderujeme PŮVODNÍ stencil (nemutovaná data), ne instance
       (která prošla _ast_copy a mohla ztratit některé item_decly).
       Substituci děláme regex-em na hotovém textu."""
       try :
          import c2cpp, tempfile, os, re
          gen = c2cpp.ToCpp ()
          gen.compiler = self
          tmp = tempfile.NamedTemporaryFile (mode = 'w', suffix = '.cpp',
                                             delete = False)
          tmp.close ()
          try :
             gen.open (tmp.name)
             gen.send_declaration (stencil.inner_declaration)
             gen.close ()
             with open (tmp.name) as f :
                text = f.read ()
          finally :
             try : os.unlink (tmp.name)
             except : pass

          # Textová substituce: jen celá identifikátorová slova
          for tparam, tvalue in param_dict.items () :
              text = re.sub (r'\b' + re.escape (tparam) + r'\b', tvalue, text)

          subst = ", ".join (k + " -> " + v for k, v in param_dict.items ())
          print ()
          print ("=== stencil instance (" + subst + ") ===")
          print (text.strip ())
          print ("=== end stencil instance ===")
          print ()
       except Exception as e :
          # Render je didactic-only — selhání nezpůsobí chybu kompilace.
          print ("stencil render skipped:", e)

   # -----------------------------------------------------------------------

   # -----------------------------------------------------------------------

   """
   def skip_block (self) :
       self.nextToken () # skip identifier

       if self.isString () :
          self.tokenText

       self.check ("{")

       level = 0
       while self.tokenText != "}" or level != 0 :
          if self.tokenText == "{" :
             level = level + 1
          if self.tokenText == "}" :
             level = level - 1
          self.nextToken ()

       self.check ("}")
   """

   # -----------------------------------------------------------------------

   # skip fuction body

   def parse_compound_stat (self) :
       if not self.skip_functions :
          return super (CmmExtCompiler, self).parse_compound_stat ()
       else :
          result = CmmCompoundStat ()
          result.kind = result.compoundStat
          self.storeLocation (result)
          self.check ("{")
          level = 0
          while self.tokenText != "}" or level != 0 :
             if self.tokenText == "{" :
                level = level + 1
             if self.tokenText == "}" :
                level = level - 1
             self.nextToken ()
          self.check ("}")
          return result

   # skip initializer

   def parse_initializer_item (self) :
       if not self.skip_functions :
          return super (CmmExtCompiler, self).parse_initializer_item ()
       else :
          level = 0
          while (self.tokenText != "," and self.tokenText != ";") or level != 0 :
             if self.tokenText == "(" :
                level = level + 1
             if self.tokenText == ")" :
                level = level - 1
             self.nextToken ()
          return None

   def parse_ctor_initializer (self) :
       if not self.skip_functions :
          return super (CmmExtCompiler, self).parse_ctor_initializer ()
       else :
          while self.tokenText != "{" :
             self.nextToken ()
          return None

# --------------------------------------------------------------------------

   def subst (self, name, obj) :
       if isinstance (obj, str) :
          print ("SUBST", name, obj)
          self.rename_dict [name] = obj

   def code (self, source_text, no_send = False) :
       print ("CODE", source_text)

       # save_macros = self.macros
       # self.macros = self.macros.copy ()

       # for name in self.subst_dict :
       #     print ("SUBSTITUTION", name)
       #     self.addMacro (name, self.subst_dict [name])

       items = [ ]
       self.openNestedString (source_text)
       while not self.isEndOfSource () :
           items.append (self.parse_declaration ())
       self.closeNested ()

       # self.macros = save_macros

       if not no_send :
          if len (self.target_stack) != 0 :
             target = self.target_stack [-1]
             target.following_items = target.following_items + items

       return items

   def send_code (self, item) :
       if len (self.target_stack) != 0 :
          target = self.target_stack [-1]
          target.following_items.append (item)

# --------------------------------------------------------------------------

def subst (name, obj) :
    global global_compiler
    global_compiler.subst (name, obj)


def code (source_text, no_send = False) :
    global global_compiler
    global_compiler.code (source_text, no_send)

def send_code (item) :
    global global_compiler
    global_compiler.send_code (item)

# --------------------------------------------------------------------------

class CmmCustomCompiler (CmmExtCompiler) :

   def __init__ (self) :
       super (CmmCustomCompiler, self).__init__ ()

   # -----------------------------------------------------------------------

   """
   def sql (self) :
       print ("SQL")
       self.nextToken () # skip sql keyword
       self.checkSeparator ('{')
       while not self.isSeparator ('}') :
          if self.isKeyword ("create") :
             print ("CREATE")
             self.nextToken ()
             self.checkKeyword ("table")
             name = self.readIdentifier ()
             self.checkSeparator ('(')
             column = self.readIdentifier ()
             while self.isSeparator (',') :
                self.checkSeparator (',')
                column = self.readIdentifier ()
             self.checkSeparator (')')
             self.checkSeparator (';')
          elif self.isKeyword ("select") :
             print ("SELECT")
             self.nextToken ()
             if self.isSeparator ('*') :
                self.nextToken ()
             else :
                column = self.readIdentifier ()
                while self.isSeparator (',') :
                   self.checkSeparator (',')
                   column = self.readIdentifier ()
             self.checkKeyword ("from")
             table = self.readIdentifier ()
             self.checkSeparator (';')
          else:
             self.error ("Unknown sql stattement")

       self.checkSeparator ('}')
    """

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
