
# code.py

from __future__ import print_function

# --------------------------------------------------------------------------

def initItem (self) :
    self.item_name = ""
    self.item_context = None
    self.item_qual = ""

    self.item_icon = None
    self.item_ink = None
    self.item_paper = None
    self.item_tooltip = None

    if not hasattr (self, "src_file") :
       self.src_file = -1
       self.src_line = -1
       self.src_column = -1
       self.src_pos = -1
       self.src_end = -1
       # self.src_step = -1

class Item (object) :
   def __init__ (self) :
       initItem (self)

   def __str__ (self) :
       return decl_to_text (self)

# --------------------------------------------------------------------------

def initDeclaration (self) :
    initItem (self)

    if not hasattr (self, "item_decl") :
       self.item_decl = None

    self.item_used = False

    self.item_type = None

    self.foreign_ctx = None

    self.item_origin = None # class
    self.item_place = None # widget
    # self.item_owner = None # variable / expression

    self.item_label = ""
    self.item_block = [ ]

    self.attr_compile_time = False
    self.attr_python = False
    self.attr_field = False
    self.attr_context = False

    self.method_implementation = False # method defined outside class
    self.construction_list = [ ] # expressions from function specifier

    self.template_decl = None

# class Declaration (Item) :
   # def __init__ (self) :
       # super (Declaration, self).__init__ ()
       # initDeclaration (self)

# --------------------------------------------------------------------------

def initScope (self) :
    initDeclaration (self)
    self.item_dict = { }
    self.item_list = [ ]

    self.registered_scopes = { }
    self.registered_count = 0

    self.default_scope = False # default scope for unknown identifiers
    self.independent_scope = False # True ... do not print scope name and above names
    self.hidden_scope = False # True ... do not print scope name
    self.search_only = False # True ... only for lookup, not for declarations

    self.using_list = [ ]
    self.template_list = [ ] # scopes with template parameters

    self.search_func = None

    self.foreign_obj = None

    self.owner_obj = None # variable
    self.owner_expr = None # expression
    self.owner_arrow = False
    self.owner_parenthesis = False

    self.decl_flag = False # temporary variable

class Scope (Item) :
   def __init__ (self) :
       super (Scope, self).__init__ ()
       initScope (self)

   def add (self, item) : # qt_import.py
       self.item_dict [item.item_name] = item
       self.item_list.append (item)

       item.item_context = self

       if self.item_qual != "" :
          item.item_qual = self.item_qual + "." + item.item_name
       else :
          item.item_qual = item.item_name

# --------------------------------------------------------------------------

def initNamespace (self) :
    initScope (self)
    self.item_icon = "namespace"
    self.item_expand = True
    self.skip_code = False
    self.transparent_namespace = False # True => skip namespace declaration, keep members

# class Namespace (Scope) :
   # def __init__ (self) :
       # super (Namespace, self).__init__ ()
       # initNamespace (self)

# --------------------------------------------------------------------------

def initClass (self) :
    initScope (self)
    self.item_icon = "class"
    self.base_classes = [ ]
    self.skip_code = False
    self.init_list = [ ] # variables and with statements
    self.implementation_list = [ ] # out of class method implementations
    self.methods = [ ] # additional (generated) methods
    # self.constructor_count
    # self.member_visibility

# class Class (Scope) :
   # def __init__ (self) :
       # super (Class, self).__init__ ()
       # initClass (self)

# --------------------------------------------------------------------------

def initEnum (self) :
    initScope (self)
    self.item_icon = "enum"

def initEnumItem (self) :
    initDeclaration (self)
    self.item_icon = "variable"

# class Enum (Scope) :
   # def __init__ (self) :
       # super (Enum, self).__init__ ()
       # initEnum (self)

# class EnumItem (Declaration) :
   # def __init__ (self) :
       # super (EnumItem, self).__init__ ()
       # initItemEnum (self)

# --------------------------------------------------------------------------

def initVariable (self) :
    initScope (self)
    self.item_icon = "variable"

    self.is_function = False
    self.is_constructor = False
    self.is_destructor = False

    self.item_simple_decl = None # outer CmmSimpleDeclaration
    self.item_body = None

    self.python_source = "" # Python code for instant function
    self.python_func = None

    self.skip_code = False
    self.move_variable = False # variable moved to another place
    self.with_decl = None # temporary, declaration form outer with statent

    self.alt_init = ""
    self.alt_create = ""
    self.alt_create_place = False
    self.alt_create_owner = False
    self.alt_setup = ""
    self.alt_setup_param = ""

# class Variable (Scope) :
   # def __init__ (self) :
       # super (Variable, self).__init__ ()
       # initVariable (self)

# --------------------------------------------------------------------------

def initFunction (self) :
    initVariable (self)
    self.is_function = True
    self.item_icon = "function"

    self.python_source = "";
    self.python_func = None;

# def Function () :
    # result = Variable ()
    # result.is_function = True
    # result.item_icon = "function"
    # return result

# --------------------------------------------------------------------------

def initTypedef (self) :
    initDeclaration (self)
    self.item_icon = "type"
    self.item_type = None

    self.is_function = False
    self.is_typedef = True

# class Typedef (Declaration) :
   # def __init__ (self) :
       # super (Typedef, self).__init__ ()
       # initTypedef (self)

# --------------------------------------------------------------------------

"CmmExtensionStat"

def initExtensionStat (self) :
    self.name = ""
    # put, putEol, indent, unindent, send, no_space, new_line, empty_line, no_empty_line
    # include, directive, comment
    # nested_module, nested_file
    # extension
    # code, run
    # kit_block

    self.param = ""
    # include, directive, comment,
    # nested_file, nested_module

    self.items = [ ] # run, code, nested_block

    self.into_expr = "" # code
    self.store_expr = "" # code
    self.ext_source = "" # code

    self.python_source = "" # run

# --------------------------------------------------------------------------

# extra variables
  # extension_statement
  # extension_object
  # global_compiler

# --------------------------------------------------------------------------

# class TreeItem
#
#    expand_func  ... expand subitems
#    expand_one   ... expand one item
#    expand_item  ... show expansion for item with expamd_one
#
#    obj

#    region_begin
#    region_end
#    region_begin_file
#    region_end_file

#    jump_table
#    jump_label
#    jump_mark

#    alt_assign
#    alt_assign_index
#    alt_assign_param
#    alt_read
#    alt_display
#    alt_store
#    alt_connect
#    alt_connect_expr
#    alt_connect_cls
#    alt_connect_decl
#    alt_connect_signal
#    alt_connect_src

#    mod_rename
#    mod_call
#    mod_decl

#    mode
#    kind

#    type_flag
#    constructor_flag
#    destructor_flag

#    item_ref
#    name_owner
#    skip_semicolon
#
#    _only_properties_
#    _other_properties_
#    _qt_properties_
#    _properties_
#
#    link_obj
#    link_tree_node
#
#    extension_object
#
#    _fields_
#    items
#
#    description
#
#    method showNavigator ()


# class Editor
#    // clang_cursor
#    translation_unit
#    compiler_data
#    navigator_data
#    navigator_tree

# --------------------------------------------------------------------------

class Type (Item) :
   def __init__ (self) :
       super (Type, self).__init__ ()
       self.type_const = False
       self.type_volatile = False

       self.gpu_global = False # extension

   def __str__ (self) :
       return type_to_text (self)

class CompoundType (Type) :
   def __init__ (self) :
       super (CompoundType, self).__init__ ()
       self.type_from = None

# --------------------------------------------------------------------------

class SimpleType (Type) :
   def __init__ (self) :
       super (SimpleType, self).__init__ ()

       self.type_void = False
       self.type_bool = False
       self.type_char = False
       self.type_wchar = False
       self.type_short = False
       self.type_int = False
       self.type_long = False
       self.type_float = False
       self.type_double = False

       self.type_signed = False
       self.type_unsigned = False


class NamedType (Type) :
   def __init__ (self) :
       super (NamedType, self).__init__ ()
       self.type_label = ""
       self.type_decl = None
       self.type_args = None

# --------------------------------------------------------------------------

class PointerType (CompoundType) :
   def __init__ (self) :
       super (PointerType, self).__init__ ()

class ReferenceType (CompoundType) :
   def __init__ (self) :
       super (ReferenceType, self).__init__ ()

class ArrayType (CompoundType) :
   def __init__ (self) :
       super (ArrayType, self).__init__ ()
       self.lim = None

class FunctionType (CompoundType) :
   def __init__ (self) :
       super (FunctionType, self).__init__ ()

# --------------------------------------------------------------------------

class Unknown (Item) :
   def __init__ (self) :
       super (Unknown, self).__init__ ()

# --------------------------------------------------------------------------

class Method (object) :
   def __init__ (self) :
       self.name = ""
       self.body = None

# --------------------------------------------------------------------------

def type_to_text (t) :
    result = ""

    if isinstance (t, CompoundType) :
       if isinstance (t, PointerType) :
          result = "pointer to " + type_to_text (t.type_from)
       elif isinstance (t, ReferenceType) :
          result = "reference to " + type_to_text (t.type_from)
       elif isinstance (t, FunctionType) :
          result = "function returning " + type_to_text (t.type_from)
       elif isinstance (t, ArrayType) :
          result = "array of " +  type_to_text (t.type_from)

    elif isinstance (t, NamedType) :
       result = t.type_label

    elif isinstance (t, SimpleType) :
       result = "<simple type>" # !?
       if t.type_void : result = "void"
       elif t.type_bool : result = "bool"
       elif t.type_char : result = "char"
       elif t.type_wchar : result = "wchar_t"
       elif t.type_short : result = "short"
       elif t.type_int : result = "int"
       elif t.type_long : result = "long"
       elif t.type_float : result = "float"
       elif t.type_double : result = "double"

       if t.type_signed :
          result = "signed " + result
       elif t.type_unsigned :
          result = "unsigned " + result

    if t != None :
       if t.type_const:
          result = "const " + result
       if t.type_volatile :
          result = "volatile " + result

    if t.gpu_global :
       result = "__global__ " + result

    return result

# --------------------------------------------------------------------------

def decl_to_text (decl) :
    result = ""

    ctx = decl.item_context
    while ctx != None :
       if ctx.item_name != "" :
          result = ctx.item_name + "." + result
       ctx = ctx.item_context

    if decl.item_name != "" :
       result = result + decl.item_name

    if result == "" :
       result = "???"

    return result

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
