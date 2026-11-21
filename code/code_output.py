
# code_output.py

from __future__ import print_function

from input import quoteString
from output import Output
# from code import *
from code_cls import *

# --------------------------------------------------------------------------

# Reserved words a grammar-derived identifier may collide with. Escaped by
# CodeOutput.identifier (): C# "@name", Rust "r#name". Words that cannot be
# raw identifiers in Rust (self, crate, super, ...) are left out on purpose.
csharp_keywords = {
   "abstract", "as", "base", "bool", "break", "byte", "case", "catch",
   "char", "checked", "class", "const", "continue", "decimal", "default",
   "delegate", "do", "double", "else", "enum", "event", "explicit",
   "extern", "false", "finally", "fixed", "float", "for", "foreach",
   "goto", "if", "implicit", "in", "int", "interface", "internal", "is",
   "lock", "long", "namespace", "new", "null", "object", "operator",
   "out", "override", "params", "private", "protected", "public",
   "readonly", "ref", "return", "sbyte", "sealed", "short", "sizeof",
   "stackalloc", "static", "string", "struct", "switch", "this", "throw",
   "true", "try", "typeof", "uint", "ulong", "unchecked", "unsafe",
   "ushort", "using", "virtual", "void", "volatile", "while",
}

rust_keywords = {
   "as", "break", "const", "continue", "else", "enum", "extern", "false",
   "fn", "for", "if", "impl", "in", "let", "loop", "match", "mod",
   "move", "mut", "pub", "ref", "return", "static", "struct", "trait",
   "true", "type", "unsafe", "use", "where", "while", "async", "await",
   "dyn", "abstract", "become", "box", "do", "final", "macro",
   "override", "priv", "typeof", "unsized", "virtual", "yield", "try",
}

# --------------------------------------------------------------------------

class CodeOutput (Output) :

   def __init__ (self) :
       super (CodeOutput, self).__init__ ()

       self.code = Namespace ()

       self.pascal = False
       self.csharp = False
       self.java = False
       self.js = False
       self.vala = False
       self.rust = False
       self.c = False
       self.cpp = False
       self.set_consts ()

   # -----------------------------------------------------------------------

   def get_header_symbol (self, fileName) :
       name = ""
       for c in fileName :
           if c >= 'A' and c <= 'Z' or c >= 'a' and c <= 'z' or c >= '0' and c <= '9' or c == '_' :
              name = name + c.upper ()
           else :
              name = name + '_'
       return name

   def put_header_ifdef (self, name) :
       if self.c or self.cpp :
          self.putLn ("#ifndef " + name)
          self.putLn ("#define " + name)
          self.putLn ()

   def put_header_endif (self, name) :
       if self.c or self.cpp :
          self.putLn ()
          self.putLn ("#endif //" + name)
   # -----------------------------------------------------------------------

   "class"

   def put_class_forw (self, name) :
       if self.c :
          self.putLn ("struct " + name + ";")
       elif self.cpp:
          self.putLn ("class " + name + ";")

   def put_class (self, name, above = "", public = False) :
       if name not in self.code.item_dict :
          cls_obj = Class ()
          cls_obj.item_name = name
          self.code.add (cls_obj)
       else :
          cls_obj = self.code.item_dict [name]

       cls_obj.super_class = above

       self.openSection (name)
       if self.pascal :
          # self.send ("type")
          self.send (name)
          self.send ("=")
          self.send ("class")
          if above != "" :
             self.send ("(")
             self.send (above)
             self.send (")")

       elif self.rust :
          if public :
             self.send ("pub")
          self.send ("struct")
          self.send (name)
          self.new_line ()
          self.send ("{")
          if above != "" :
             self.new_line ()
             self.indent ()
             self.send ("inner")
             self.send (":")
             self.send (above)
             self.send (",")
             self.unindent ()
             self.new_line ()

       elif self.c :
          self.send ("struct")
          self.send (name)
          self.new_line ()
          self.send ("{")
          if above != "" :
             self.new_line ()
             self.indent ()
             self.send (above)
             # self.send (" ")
             self.send ("inner")
             self.send (";")
             self.unindent ()
             self.new_line ()
       else :

          if self.csharp or self.vala :
             self.send ("public")
          if self.java and public :
             self.send ("public")

          self.send ("class")
          self.send (name)
          if above != "" :
             if self.js or self.java :
                self.send ("extends")
                self.send (above)
             elif self.csharp or self.vala :
                self.send (":")
                self.send (above)
             else :
                self.send (":")
                self.send ("public")
                self.send (above)
          self.new_line ()
          self.send ("{")

       self.new_line ()
       self.indent ()
       # self.indent ()
       self.no_empty_line ()

   def put_class_end (self) :
       self.no_empty_line ()
       self.new_line ()
       # self.unindent ()
       self.unindent ()
       if self.pascal :
          self.send ("end")
          self.send (";")
       elif self.csharp or self.java or self.vala or self.rust :
          self.send ("}")
       else :
          self.send ("}")
          self.send (";")
       self.closeSection ()
       self.empty_line ()

   def put_public (self) :
       if not self.js and not self.csharp and not self.java and not self.vala and not self.rust and not self.c:
          self.unindent ()
          self.send ("public")
          self.indent ()
          if not self.pascal :
             self.no_space ()
             self.send (":")
          self.new_line ()

   def put_member (self, type, name) :
       "class data memeber"
       type = self.rename_type (type)

       if self.pascal :
          self.send (name)
          self.send (":")
          self.send (type)
          self.send (";")
          self.new_line ()

       elif self.js :
          pass
          # self.send ("var")
          # self.send (name)
          # self.send (";")
          # self.new_line ()

       elif self.rust :
          if name == "type" :
             name = "type_" # !?
          self.send (name)
          self.send (":")
          self.send (type)
          self.send (",")
          self.new_line ()

       else :
          if (self.csharp or self.java or self.vala) :
             self.send ("public")
          self.send (type)
          self.send (name)
          self.send (";")
          self.new_line ()

   # -----------------------------------------------------------------------

   "enum"

   def put_enum (self, name) :
       if name not in self.code.item_dict :
          enum_obj = Class ()
          enum_obj.item_name = name
          self.code.add (enum_obj)
       else :
          enum_obj = self.code.item_dict [name]

       self.openSection (name)
       if self.pascal :
          # self.send ("type")
          self.send (name)
          self.send ("=")
          self.new_line ()
          self.send ("(")
       elif self.js :
          self.send ("//")
          self.send ("enum")
          self.send (name)
          self.new_line ()
       else :
          if self.rust :
             self.putLn ("#[derive(Eq, PartialEq)]")
          if self.csharp or self.vala :
             self.send ("public")
          self.send ("enum")
          self.send (name)
          self.new_line ()
          self.send ("{")
       self.new_line ()
       self.indent ()
       self.remember_enum = 0

   def put_enum_item (self, name) :
       self.simpleSection (name)
       if self.js :
          self.send (name)
          self.send ("=")
          self.send (str (self.remember_enum))
          self.send (";")
          self.new_line ()
       else :
          if self.remember_enum > 0 :
             self.send (",")
             self.new_line ()
          self.send (name)
       self.remember_enum = self.remember_enum + 1

   def put_enum_end (self) :
       self.unindent ()
       if not self.js :
          self.new_line ()
          if self.pascal :
             self.send (")")
          else :
             self.send ("}")
          if not self.csharp and not self.java and not self.vala and not self.rust :
             self.send (";")
       self.closeSection ()
       self.empty_line ()

   # -----------------------------------------------------------------------

   "set"

   def put_set (self, name, cnt) :
       self.simpleSection (name)
       if self.csharp or self.vala :
          self.put ("private byte [] " + name + " = {" )
       elif self.java :
          self.put ("private short [] " + name + " = {" )
       elif self.pascal :
          self.put ("const " + name + " : array [0 .. " + str (cnt-1) + "] of byte = (" )
       elif self.vala :
          self.put ("private byte [] " + name + " = {" )
       elif self.js :
          self.put ("const " + name + " = [" )
       elif self.rust :
          self.put ("const " + name + " : [ u8 ; " + str (cnt) + " ]  = [" )
       else :
          self.put ("const unsigned char " + name + " [" + str (cnt) + "] = {" )
       self.remember_set = 0

   def put_set_item (self, value) :
       if self.remember_set > 0 :
          self.put (", ")
       self.put (str (value))
       self.remember_set = self.remember_set + 1

   def put_set_end (self) :
       if self.pascal :
          self.putLn (");")
       elif self.js :
          self.putLn ("];")
       elif self.rust :
          self.putLn ("];")
       else :
          self.putLn ("};")

   # -----------------------------------------------------------------------

   "function"

   def put_func (self, name, type = "", cls = "", constructor = False, inline = False, virtual = False, override = False, alt_name = "") :
       if alt_name == "" :
          alt_name = name
       scope = self.code
       if cls != "" :
          scope = self.code.item_dict [cls]
       if alt_name not in scope.item_dict :
          func_obj = Function ()
          func_obj.item_name = alt_name
          scope.add (func_obj)
       else :
          func_obj = scope.item_dict [alt_name]
       self.remember_func = func_obj

       type = self.rename_type (type)

       func_obj.type = type
       func_obj.cls = cls
       func_obj.is_constructor = constructor
       func_obj.inline = inline
       func_obj.virtual = virtual
       func_obj.override = override

       func_obj.param_list = [ ]
       func_obj.init_list = [ ]
       func_obj.var_list = [ ]
       func_obj.code = ""

   def put_param (self, name, type, ref = False, array = False) :
       type = self.rename_type (type)
       self.remember_func.param_list.append ([name, type, ref, array])

   def put_init (self, name, value) :
       "constructor initalization"
       self.remember_func.init_list.append ([name, value])

   def put_var (self, name, type) :
       "local variable"
       if not self.pascal or name != "result" :
          type = self.rename_type (type)
          self.remember_func.var_list.append ([type, name])

   def put_func_decl (self) :
       "only function declaration/header"
       self.remember_func = None

   def put_func_body (self) :
       self.openString ()

   def put_func_end (self) :
       # self.unindent ()
       # self.no_empty_line ()
       self.remember_func.code = self.closeString ()
       self.remember_func = None

   def put_proc (self, name, params = [], type = "", constructor = False) :
       "short variant - put_func, put_param, put_func_decl"
       if not self.csharp and not self.java and not self.vala:
          self.put_func (name, type, constructor = constructor)
          for param in params :
              self.put_param (param[0], param[1])
          self.put_func_decl ()

   def put_local_start (self, type, name) :
       "local variable declaration (as statement)"
       type = self.rename_type (type)
       self.put_var (name, type)

       if self.pascal :
          pass

       elif self.js :
          self.send ("var")
          self.put (" ")

       elif  self.rust :
          self.send ("let")
          self.send ("mut")
          self.put (" ")

       else :
          self.send (type)
          self.put (" ")

   def put_local (self, type, name, value = None) :
       "local variable declaration (as statement)"
       type = self.rename_type (type)
       self.put_var (name, type)

       if self.pascal :
          if value != None :
             self.send (name)
             self.send (":=")
             self.send (value)
             self.send (";")
             self.new_line ()

       elif self.js :
          self.send ("var")
          self.send (name)
          if value != None :
             self.send ("=")
             self.send (value)
          self.send (";")
          self.new_line ()

       elif self.rust :
          self.send ("let")
          self.send ("mut")
          self.send (name)
          if value == None :
             self.send (":")
             self.send (type)
          if value != None :
             self.send ("=")
             self.send (value)
          self.send (";")
          self.new_line ()

       else :
          self.send (type)
          self.send (name)
          if value != None:
             self.send ("=")
             self.send (value)
          self.send (";")
          self.new_line ()

   # -----------------------------------------------------------------------

   "write function"

   def put_func_parameter (self, name, type, ref, array) :
       if self.pascal :
          self.send (name)
          self.no_space ()
          self.send (":")
          self.send (type)
       elif self.rust :
          if ref :
             self.send ("&")
          self.send ("mut")
          self.send (name)
          self.send (":")
          self.send (type)
       elif self.js :
          self.send (name)
       else :
          self.send (type)
          if ref :
             if self.c :
                self.send ("*")
             if self.cpp :
                self.send ("&")
          # C#/Vala need the array specifier as part of the type
          # ("short[] table"); Java also accepts it after the name.
          if array and (self.csharp or self.vala) :
             self.send ("[ ]")
          self.send (name)
          if array and not (self.csharp or self.vala) :
             self.send ("[ ]")

   def put_func_header (self, func_obj, with_cls = False) :

       name = func_obj.item_name
       type = func_obj.type

       if self.csharp or self.java or self.vala:
          self.send ("public")

       if func_obj.inline :
          if self.cpp :
             if not with_cls :
                self.send ("inline")

       if func_obj.virtual :
          if self.cpp :
             if not with_cls :
                self.send ("virtual")
          elif self.csharp :
             # C# needs the base method marked virtual for the derived
             # "override" methods (conv_*).
             self.send ("virtual")

       if func_obj.override :
          if self.csharp or self.vala :
             self.send ("override")
          elif self.cpp :
             self.send ("virtual")

       if self.pascal :
          if func_obj.is_constructor :
             self.send ("constructor")
          elif func_obj.type == "" :
             self.send ("procedure")
          else :
             self.send ("function")
          if func_obj.cls != "" and with_cls :
             self.send (func_obj.cls)
             self.no_space ()
             self.send (".")
             self.no_space ()
          if func_obj.is_constructor :
             self.send ("Create")
          else :
             self.send (name)
       elif self.js :
          if func_obj.is_constructor :
             self.send ("constructor")
          else :
             if func_obj.cls == "" :
                self.send ("function")
             self.send (name)
       elif self.rust :
          if func_obj.is_constructor :
             self.send ("fn")
             self.send ("new")
             self.send ("(")
             self.send (")")
             self.send ("->")
             self.send (func_obj.cls)
          else :
             self.send ("fn")
             self.send (name)
       else :
          if type == "" :
             type = "void"
          if not func_obj.is_constructor :
             self.send (type)
          if with_cls :
             if func_obj.cls != "" :
                if self.cpp :
                   self.send (func_obj.cls)
                   self.no_space ()
                   self.send ("::")
                   self.no_space ()
          self.send (name)

       "parameters"
       if not self.rust or not func_obj.is_constructor :
          cnt = len (func_obj.param_list)
          if not self.pascal or cnt > 0 :
             self.send ("(")

          if self.rust :
             self.send ("& mut self")
             if len (func_obj.param_list) != 0 :
                self.send (",")

          inx = 0
          for param in func_obj.param_list :
              self.put_func_parameter (param[0], param [1], param [2], param[3])
              inx = inx + 1
              if inx < cnt :
                 if self.pascal :
                    self.send (";")
                 else :
                    self.send (",")

          if not self.pascal or cnt > 0 :
             self.send (")")

       "end of fuction header"
       if self.pascal :
          if type != "" :
             self.send (":")
             self.send (type)
          self.send (";")
          if not with_cls :
             # if func_obj.inline :
             #    self.send ("inline")
             #    self.send (";")
             if func_obj.virtual :
                self.send ("virtual")
                self.send (";")
             if func_obj.override :
                self.send ("override")
                self.send (";")

       if self.rust :
          if type != "" :
             self.send ("->")
             self.send (type)

   def put_func_declaration (self, func_obj) :
       self.put_func_header (func_obj)
       if not self.pascal :
          self.send (";")
       self.new_line ()

   def put_initialization (self, func_obj) :
       cls_name = func_obj.cls
       self.send (cls_name)
       self.new_line ()
       self.put_begin ()

       if cls_name in self.code.item_dict :
          cls_obj = self.code.item_dict [cls_name]

          super_name = cls_obj.super_class
          if super_name != "" :
             self.send ("inner")
             self.send (":")
             self.send (super_name)
             self.no_space ()
             self.send ("::")
             self.no_space ()
             self.send ("new")
             self.send ("(")
             self.send (")")
             self.send (",")
             self.new_line ()

          for init in func_obj.init_list :
              self.send (init [0])
              self.send (":")
              self.send (init [1])
              self.send (",")
              self.new_line ()

       self.put_end ()

   def put_func_implementation (self, func_obj, with_cls = False) :
       self.simpleSection (func_obj.item_name)
       self.empty_line ()
       self.put_func_header (func_obj, with_cls = with_cls)

       "constructor initialization"
       if not self.pascal and not self.csharp and not self.java and not self.vala and not self.js and not self.rust :
          cnt = len (func_obj.init_list)
          if cnt > 0 :
             self.send (":")
             self.new_line ()
             self.indent ()
             inx = 0
             for init in func_obj.init_list :
                 self.send (init [0])
                 self.send ("(")
                 self.send (init [1])
                 self.send (")")
                 inx = inx + 1
                 if inx < cnt :
                    self.send (",")
                    self.new_line ()
             self.unindent ()

       self.new_line ()

       "local variables"
       if self.pascal :
          if len (func_obj.var_list) != 0 :
             self.send ("var")
             self.indent ()
             for var in func_obj.var_list :
                 self.send (var [1])
                 self.send (":")
                 self.send (var [0])
                 self.send (";")
                 self.new_line ()
             self.unindent ()

       "function body"
       self.put_begin ()

       "initialization"
       if self.pascal or self.csharp or self.java or self.vala or self.js :
          for init in func_obj.init_list :
              self.put_assign (self.access + init [0], init [1])
              self.new_line ()

       if func_obj.is_constructor and self.rust :
          self.put_initialization (func_obj)
       else :
          "function code"
          self.no_empty_line ()
          for line in func_obj.code.splitlines () :
              self.putLn (line)
          self.no_empty_line ()

       self.put_end (semicolon = True)
       self.empty_line ()

   # -----------------------------------------------------------------------

   def put_method_declarations (self, cls_name) :
       cls_obj = self.code.item_dict [cls_name]
       for func_obj in cls_obj.item_list :
           if isinstance (func_obj, Function) :
                 if self.csharp or self.java or self.vala or self.js or self.rust :
                    self.put_func_implementation (func_obj)
                 elif func_obj.inline and not self.pascal :
                    self.put_func_implementation (func_obj)
                 else :
                    self.put_func_declaration (func_obj)

   def put_method_implementations (self, cls_name) :
       if not self.csharp and not self.java and not self.vala and not self.js and not self.rust :
          cls_obj = self.code.item_dict [cls_name]
          for func_obj in cls_obj.item_list :
              if isinstance (func_obj, Function) :
                    if not func_obj.inline or self.pascal :
                       self.put_func_implementation (func_obj, with_cls = True)

   # -----------------------------------------------------------------------

   "statements"

   def put_begin (self, only_one = False) :
       if not only_one or self.rust:
          if self.pascal :
             self.send ("begin")
          else :
             self.send ("{")
       self.new_line ()
       self.indent ()
       self.no_empty_line ()

   def put_end (self, semicolon = False, only_one = False) :
       # semicolon ... add semicolon to Pascal source
       self.no_empty_line ()
       self.new_line ()
       self.unindent ()
       if not only_one or self.rust:
          if self.pascal :
             self.send ("end")
             if semicolon :
                self.send (";")
          else :
             self.send ("}")
       self.new_line ()

   def put_if (self) :
       self.send ("if")
       if not self.pascal :
          self.send ("(")

   def put_then (self) :
       if self.pascal :
          self.send ("then")
       else :
          self.send (")")
       self.new_line ()

   def put_if_else (self) :
       self.new_line ()
       self.send ("else")
       self.new_line ()

   def put_while (self) :
       self.send ("while")
       if not self.pascal :
          self.send ("(")

   def put_do (self) :
       if self.pascal :
          self.send ("do")
       else :
          self.send (")")
       self.new_line ()

   def put_return (self, value) :
       if self.pascal :
          if value != "result" :
             self.send ("result")
             self.send (":=")
             self.send (value)
             self.send (";")
       else :
          self.send ("return")
          self.send (value)
          self.send (";")
       self.new_line ()

   def put_assign (self, var, value) :
       if self.pascal :
          self.send (var)
          self.send (":=")
          self.send (value)
          self.send (";")
       else :
          self.send (var)
          self.send ("=")
          self.send (value)
          self.send (";")
       self.new_line ()

   def put_inc (self, var) :
       if self.pascal :
          self.send ("inc")
          self.send ("(")
          self.put (var)
          self.send (")")
          self.send (";")
       else :
          self.put (var)
          self.send ("++")
          self.send (";")
       self.new_line ()

   def put_monitor (self, func, param = "") :
       self.put_if ()
       self.send ("monitor")
       self.put_then ()
       self.indent ()
       if param == "" :
          self.putLn ("monitor" + self.arrow + func + self.call + ";")
       else :
          self.putLn ("monitor" + self.arrow + func + "(" + param + ");")
       self.unindent ()

   # -----------------------------------------------------------------------

   "type"

   def pointer (self, type) :
       if self.pascal or self.csharp or self.java or self.vala :
          # return "^ " + type # classic pointer
          return type # object pointer
       elif self.rust :
          return type # without Option and Box
       else :
          return type + " *"

   def pointer_permanent (self, type) :
       if self.rust :
          return "Option <Box<" + type + ">>"
       else :
          return self.pointer (type)

   # def pointer_decl (self, type) :
   #     if self.pascal or self.csharp or self.java  :
   #        return type + " "
   #     else :
   #        return type + " * "

   def store_pointer (self, param) :
       if self.rust :
          return "Some ( Box::new (" + param + "))"
       else :
          return param

   def put_store_pointer (self) :
       if self.rust :
          self.send ("Some")
          self.send ("(")
          self.send ("Box::new")
          self.send ("(")

   def put_store_pointer_end (self) :
       if self.rust :
          self.send (")")
          self.send (")")

   def put_store_box (self) :
       if self.rust :
          self.send ("Box::new")
          self.send ("(")

   def put_store_box_end (self) :
       if self.rust :
          self.send (")")

   def vector (self, type) :
       if self.pascal :
          return "array of " + type
       elif self.csharp or self.vala :
          return "List < " + type + " >"
       elif self.java :
          return "ArrayList < " + type + " >"
       elif self.rust :
          return "Vec<Box<" + type + ">>"
          # return "Vec<" + self.pointer (type) + ">"
       elif self.c :
          return "GArray *"
       else :
          return "vector < " + type + " >"

   def put_typedef (self, old_type, new_type) :
       if self.pascal :
          return "type " + new_type + " = " + old_type + ";"
       else :
          return "typedef " + old_type + " " + new_type + ";"

   def rename_type (self, name) :
       if name == "bool" :
          if self.java or self.pascal :
             name = "boolean"
       if name == "int" :
          if self.pascal :
             name = "integer"
          if self.rust :
             name = "i32"
       if name == "string" :
          if self.java or self.rust :
             name = "String"
          if self.c :
             name = "const char *"
       if name == "ptr" : # !?
             name = "void"
       return name

   def identifier (self, name) :
       """Escape a grammar-derived identifier that collides with a
       keyword of the target language ("params" in C#, "type" in Rust).
       Applies to the last dotted component only, so composed names like
       "inner.type" become "inner.r#type"."""
       if "." in name :
          head, _, tail = name.rpartition (".")
          return head + "." + self.identifier (tail)
       if self.csharp and name in csharp_keywords :
          return "@" + name
       if self.rust and name in rust_keywords :
          return "r#" + name
       return name

   # -----------------------------------------------------------------------

   "expression"

   def quote (self, value) :
       if self.pascal :
          return quoteString (value, "'")
       else :
          return quoteString (value)

   def quote_char (self, value) :
       return quoteString (value, "'")

   def vector_item (self, index) :
       if self.java :
          return ".get (" + index + ")"
       else :
          return "[" + index + "]"

   def vector_size (self) :
       if self.csharp or self.vala :
          return ".Count"
       else :
          return ".size ()"

   def put_vector_add (self, param) :
       if self.pascal :
          self.putLn ("setLength (" + param + ", length (" + param + ") + 1); ")
          self.put (param + " [ high (" + param + ")] := ")
       elif self.c :
          self.put (self.push_back + " (" + param + ", ")
       else :
          self.put (param + "." + self.push_back + " (")

   def put_vector_add_end (self) :
       if self.c :
          self.put (", 1")
       if not self.pascal :
          self.put (")")

   def string_item (self, name, index) :
       if self.java :
          return name + ".charAt (" + index + ")"
       else :
          return name + "[" + index + "]"

   def string_compare (self, first, second) :
       if self.java :
          return first + ".equals (" + second + ")"
       elif self.c :
          return "strcmp (" + first + ", " + second + ")"
       else :
          return first + self.equal + second

   def string_length (self, expr) :
       if self.csharp or self.vala :
          return expr + ".Length"
       elif self.java :
          return expr + ".length ()"
       elif self.rust :
          return expr + ".len ()"
       elif self.c :
          return "strlen (" + expr + ")"
       else :
          return expr + ".length ()"

   def new (self, type) :
       if self.pascal :
          return type + ".Create"
       elif self.c :
          return "( " + type + " * ) calloc (1, sizeof (" + type + "))"
       elif self.rust :
          return type + "::new ()"
       elif self.csharp or self.java or self.vala:
          return "new " + type + " ()"
       else :
          return "new " + type

   def is_class (self, expr, type) :
       return expr + self.arrow + "conv_" + type + self.call + self.unequal + self.null
       """
       if self.pascal :
          return expr + " is " + type
       elif self.csharp :
          return expr + " is " + type
       elif self.java :
          return expr + " instanceof " + type
       else :
          return "dynamic_cast < " + type + " * > (" + expr + ")" + self.unequal + self.null
       """

   def type_cast (self, type, expr) :
       return expr + self.arrow + "conv_" + type + self.call
       """
       if self.pascal :
          return expr + " as " + type
       elif self.csharp :
          return expr + " as " + type
       elif self.java :
          return "(" + type + ") " + expr
       else :
          return "dynamic_cast < " + self.pointer (type) + " > (" + expr + ")"
       """

   # -----------------------------------------------------------------------

   def set_consts (self) :
       if self.pascal :
          # self.arrow = "^." # Pascal pointer
          self.arrow = "." # Pascal object
          self.assign = " := "
          self.equal = " = "
          self.unequal = " <> "
          self.log_and = " and "
          self.log_or = " or "
          self.log_not = "not " # one space
          self.bit_and = " & "
          self.shl = " shl "
          self.div = " div "
          self.mod = " mod "
          self.this = "self"
          self.null = "nil"
          self.call = ""
          self.push_back = "add"
          self.substr = "substr" # !?
       else :
          if self.js or self.csharp or self.java or self.vala or self.rust :
             self.arrow = "."
          else :
             self.arrow = "->"
          self.assign = " = "
          self.equal = " == "
          self.unequal = " != "
          self.log_and = " && "
          self.log_or = " || "
          self.log_not = "!"
          self.bit_and = " & "
          self.shl = " << "
          self.div = " / "
          self.mod = " % "

          self.call = " ()"

          if self.rust:
             self.this = "self"
          elif self.c:
             self.this = "self"
          else :
             self.this = "this"

          if self.rust:
             self.string_suffix = ".to_string ()"
          else :
             self.string_suffix = ""

          if self.csharp or self.java or self.vala or self.js :
             self.null = "null"
          elif self.rust:
             self.null = "None"
          else :
             self.null = "NULL"


          if self.csharp or self.vala :
             self.push_back = "Add"
          elif self.java :
             self.push_back = "add"
          elif self.rust :
             self.push_back = "push"
          elif self.c :
             self.push_back = "g_array_append_vals"
          else :
             self.push_back = "push_back"

          if self.csharp or self.vala :
             self.substr = "Substring"
          elif self.java  :
             self.substr = "substring"
          else :
             self.substr = "substr"

       if self.js :
          self.access = "this."
       elif self.rust :
          self.access = "self."
       else :
          self.access = ""

       if self.js :
          self.nested = "this."
       elif self.rust :
          self.nested = "self.inner."
       else :
          self.nested = ""

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
