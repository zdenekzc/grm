
# cparser.py

from __future__ import print_function

if __name__ == "__main__" :
   import os, sys
   work_dir = os.path.abspath (sys.path [0])
   module_dir = os.path.join (work_dir, "..", "code")
   sys.path.insert (1, module_dir)

from grammar import Grammar, Rule, Expression, Alternative, Ebnf, Nonterminal, Terminal, Assign, Execute, New, Style
from output import Output
from symbols import Symbol, initSymbols
from input import quoteString
from code_cls import *

from toparser import ToParser

# --------------------------------------------------------------------------

class CParser (ToParser) :

   use_strings = False # True ... use symbol text (in parsing)

   # -----------------------------------------------------------------------

   def symbolItem (self, name) :
       if self.csharp or self.java :
          return self.symbol_name + "." + name
       elif self.rust :
          return self.symbol_name + "::" + name
       else :
          return name

   def enumItem (self, grammar, name) :
       if self.csharp or self.java :
          if name in grammar.enum_item_dict :
             return grammar.enum_item_dict [name] + "." + name
          else :
             return name
       elif self.rust :
          if name in grammar.enum_item_dict :
             return grammar.enum_item_dict [name] + "::" + name
          else :
             return name
       else :
          return name

   def fieldItem (self, grammar, type_name, name) :
       result = name

       if self.rust :
          type_name = self.subst (grammar, type_name)
          type = grammar.struct_dict [type_name]
          result = ""
          while type != None and name not in type.fields :
             result = "inner." + result
             type = type.super_type
          if type != None :
             result = result + type.fields [name].composed_name

       # "params" (C#) / "type" (Rust) must be escaped at the use site,
       # consistently with the declaration in declareStruct ().
       return self.identifier (result)

   def newItem (self, grammar, type_name) :
       if self.rust :
          type_name = self.subst (grammar, type_name)
       result = self.new (type_name)
       return result

   def subst (self, grammar, type_name) :
       if type_name in grammar.struct_dict :
          type = grammar.struct_dict [type_name]
          type_name = type.subst_name
       return type_name

   # def newBox (self, param) :
   #     if self.rust :
   #        return "Box::new (" + param + ")"
   #     else :
   #        return param

   def storeLoc (self, param) :
       if self.rust :
          self.putLn (self.access + "storeLocation (" + param + ".inner);")
       else :
          self.putLn (self.access + "storeLocation (" + param + ");")

   # -----------------------------------------------------------------------

   def printKeywordItem (self, dictionary, inx, name) :
       self.put_begin ()
       self.incIndent ()
       if len (dictionary) == 0 :
          self.put_assign (self.access + "token", self.symbolItem ("keyword_" + name))
       else :
          self.printKeywordDictionary (dictionary, inx+1, name)
       self.decIndent ()
       self.put_end (semicolon = True)

   def printKeywordDictionary (self, dictionary, inx, name) :
       if self.pascal :
          base_inx = 1
       else :
          base_inx = 0
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
          self.put_if ()
          if start_inx == inx :
             self.send (self.string_item ("s", str (inx + base_inx)) + self.equal + self.quote_char (substr))
          else :
             self.send (self.string_compare ("s." + self.substr + " (" + str (start_inx+base_inx) + "," + str (inx+1-start_inx+base_inx) + ")", self.quote (substr)))
          self.put_then ()
          self.printKeywordItem (dictionary, inx, name)
       else :
           first_item = True
           for c in sorted (dictionary.keys ()) :
               if not first_item :
                  self.send ("else")
               first_item = False
               self.put_if ()
               self.send (self.string_item ("s", str (inx + base_inx)) + self.equal + "'" + c + "'")
               self.put_then ()
               self.printKeywordItem (dictionary[c], inx, name+c)

   def selectKeywords (self, grammar) :
       self.put_func ("lookupKeyword", cls = self.class_name)
       self.put_func_body ()
       self.put_local ("string", "s", self.nested + "tokenTxt")
       self.put_local ("int", "n", self.string_length ("s"))

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
             if not first_item :
                self.send ("else")
             first_item = False
             self.put_if ()
             self.send ("n" + self.equal + str (size))
             self.put_then ()
             self.put_begin ()
             self.printKeywordDictionary (tree, 0, "")
             self.put_end ()
          size = size + 1

       self.put_func_end ()

   # -----------------------------------------------------------------------

   def printDictionary (self, dictionary) :
       for c in sorted (dictionary.keys ()) :
           self.putLn ("'" + c + "'" + " :")
           self.incIndent ()
           if len (dictionary[c]) == 0 :
              self.putLn ("//")
           else :
              printDictionary (dictionary[c])
           self.decIndent ()

   # -----------------------------------------------------------------------

   def selectBranch (self, grammar, dictionary, level, prefix) :
       for c in sorted (dictionary.keys ()) :
           self.put_if ()
           if level == 1 :
              self.send (self.string_compare (self.nested + "tokenTxt", self.quote (c)))
           else :
              self.send (self.nested + "inpCh" + self.equal + "'" + c + "'")
           self.put_then ()
           self.put_begin ()
           name = prefix + c
           if name in grammar.separator_dict :
              self.put_assign (self.access + "token", self.symbolItem (grammar.separator_dict[name].ident))
           if level > 1 :
              if self.vala :
                 # string + char is not allowed in Vala
                 self.put_assign (self.nested + "tokenTxt", self.nested + "tokenTxt + " + self.nested + "inpCh.to_string ()")
              else :
                 self.put_assign (self.nested + "tokenTxt", self.nested + "tokenTxt + " + self.nested + "inpCh")
              self.putLn (self.nested + "nextCh" + self.call + ";")
           if len (dictionary[c]) != 0 :
              self.selectBranch (grammar, dictionary[c], level+1, prefix+c)
           self.put_end ()

   def selectSeparators (self, grammar) :
       self.put_func ("processSeparator", cls = self.class_name)
       self.put_func_body ()

       # A replayed token may already contain a composed multi-character
       # separator (C++ mark/rewind replays the translated token): map the
       # full text back to the symbol without consuming inpCh again.
       for name in grammar.separator_dict :
           if len (name) > 1 :
              self.put_if ()
              self.send (self.string_compare (self.nested + "tokenTxt",
                                              self.quote (name)))
              self.put_then ()
              self.put_begin ()
              self.put_assign (self.access + "token",
                               self.symbolItem (grammar.separator_dict [name].ident))
              self.put_end ()

       tree = { }
       for name in grammar.separator_dict :
           self.addToDictionary (tree, name)

       self.selectBranch (grammar, tree, 1, "")

       self.put_if ()
       self.send (self.nested + "token" + self.equal + self.symbolItem ("separator")) # !?
       self.put_then ()
       self.put_begin ()
       self.putLn (self.access + "stop (" + self.quote ("Unknown separator") + self.string_suffix + ");")
       self.put_end (semicolon = True)

       self.put_func_end ()

   # -----------------------------------------------------------------------

   def composeStructures (self, grammar) :
       for type in grammar.struct_list :
           for sub_type_name in type.conv_list :
               sub_type = grammar.struct_dict [sub_type_name]
               sub_type.subst_name = type.type_name
               sub_type.skip_decl = True
               for field in sub_type.field_list :
                   name = field.field_name
                   add = True
                   if name in type.fields :
                      if field.field_type == type.fields [name].field_type :
                         add = False
                      else :
                         if sub_type.tag_value != "" :
                            name = name + "_from_" + sub_type.tag_value
                         else :
                            name = name + "_from_" + sub_type.type_name
                   if add :
                      field.composed_name = name
                      type.fields [name] = field
                      type.field_list.append (field)

   # -----------------------------------------------------------------------

   def declareEnumTypes (self, grammar) :
       for enum in grammar.enum_list :
           if self.vala and len (enum.values) == 0 :
              # an empty enum is illegal in Vala: emit a placeholder value
              self.put_enum (enum.enum_name)
              self.put_enum_item ("none")
              self.put_enum_end ()
              continue
           self.put_enum (enum.enum_name)
           for value in enum.values :
               self.put_enum_item (value)
           self.put_enum_end ()
       for type in grammar.struct_list :
           self.declareEnum (grammar, type)

   def declareEnum (self, grammar, type) :
       for enum_name in type.enums :
           enum = type.enums [enum_name]
           if self.vala and len (enum.values) == 0 :
              self.put_enum (enum.enum_name)
              self.put_enum_item ("none")
              self.put_enum_end ()
              continue
           self.put_enum (enum.enum_name)
           for value in enum.values :
               self.put_enum_item (value)
           self.put_enum_end ()

   def basicClass (self) :
       self.put_class (self.base_name)
       self.put_class_end ()

   def add_conv (self, grammar, type) :
       if type.super_type != None :
          target = type
          while target.super_type != None :
             target = target.super_type
          target.conv_list.append (type.type_name)

   def declareStructures (self, grammar) :
       for type in grammar.struct_list :
           self.add_conv (grammar, type)
       if self.rust :
          self.composeStructures (grammar)
       for type in grammar.struct_list :
           if not type.skip_decl : # skip Rust composed types
              self.declareStruct (grammar, type)
       for t in grammar.typedef_list :
           if t.old_name != "" :
              self.put_typedef (t.old_name, t.new_name)
           else :
              self.put_class_forw (t.new_name)
       self.empty_line ()

   def implementStructures (self, grammar) :
       for type in grammar.struct_list :
           self.put_method_implementations (type.type_name)

   def declareStruct (self, grammar, type) :
       if type.super_type != None :
          super_name = type.super_type.type_name
       elif type.type_name != self.base_name:
          super_name = self.base_name
       else :
          super_name = ""

       self.put_class (type.type_name, above = super_name)
       self.put_public ()

       "field declaration"
       for field in type.field_list :
          field_type = ""
          if field.is_bool :
             field_type = "bool"
          elif field.is_enum :
             field_type = field.field_type
          elif field.is_utiny :
             field_type = "unsigned char"
          elif field.is_tiny :
             field_type = "signed char"
          elif field.is_ushort :
             field_type = "unsigned short"
          elif field.is_short :
             field_type = "short"
          elif field.is_uint :
             field_type = "unsigned int"
          elif field.is_int :
             field_type = "int"
          elif field.is_ulong :
             field_type = "unsigned long long"
          elif field.is_long :
             field_type = "long long"
          elif field.is_str :
             field_type = "string"
          elif field.is_ptr :
             field_type = self.pointer_permanent (self.subst (grammar, field.field_type))
          elif field.is_list :
             field_type = self.vector (self.pointer (self.subst (grammar, field.field_type)))
          else :
             # Reference-like field. An untyped pointer ('ptr' / the bare
             # '*') substitutes to nothing or to 'ptr'/'void' — use the
             # base class so e.g. Java does not get an illegal
             # 'public void field;'.
             elem = self.subst (grammar, field.field_type)
             if elem in ("", "ptr", "void") :
                elem = self.base_name
             field_type = self.pointer_permanent (elem)

          name = field.field_name
          if field.composed_name != "" :
             name = field.composed_name
          name = self.identifier (name)

          self.put_member (field_type, name)
       self.empty_line ()

       "constructor"
       # self.put_public ()
       cls = type.type_name
       self.put_func (type.type_name, constructor = True, cls = cls, inline = True)
       for field in type.field_list :
           if field.field_name != type.tag_name :
              if field.is_bool :
                 value = "false"
              elif field.is_enum :
                 value = field.field_type + " (0)"
                 if len (field.enum_type.values) != 0 :
                    if self.csharp or self.java or self.vala :
                       value = field.field_type + "." + field.enum_type.values[0]
                    elif self.rust :
                       value = field.field_type + "::" + field.enum_type.values[0]
                 elif self.vala :
                    # empty enum got a placeholder 'none' value for Vala
                    value = field.field_type + ".none"
                 elif self.csharp :
                    # an empty C# enum has no member to name: cast zero
                    value = "(" + field.field_type + ") 0"
                 elif self.java :
                    # Java enums are objects; there is no zero value
                    value = "null"
              elif field.is_utiny :
                 value = "0"
              elif field.is_tiny :
                 value = "0"
              elif field.is_ushort :
                 value = "0"
              elif field.is_short :
                 value = "0"
              elif field.is_uint :
                 value = "0"
              elif field.is_int :
                 value = "0"
              elif field.is_ulong :
                 value = "0"
              elif field.is_long :
                 value = "0"
              elif field.is_str :
                 value = self.quote ("") + self.string_suffix
              elif field.is_ptr :
                 value = self.null
              elif field.is_list :
                 if self.vala :
                    # plain array: new T [] { }
                    value = "new " + self.vector (self.pointer (field.field_type)) + " { }"
                 elif self.csharp or self.java :
                    value = "new " + self.vector (self.pointer (field.field_type)) + " ()"
                 elif self.rust :
                    value = "Vec::<Box<" + self.subst (grammar, field.field_type) + ">>::new()"
                 elif self.js :
                    value = "[]"
                 else :
                    value = "" # C/C++: default-initialized member
              else :
                 # reference-like field (ptr / struct reference): default
                 # is the language's null — an empty value would emit the
                 # invalid "field =;" outside C/C++ initializer lists.
                 value = self.null
              self.put_init (self.identifier (field.composed_name), value)
       "constructor body"
       self.put_func_body ()
       if type.tag_name != "" :
          self.put_assign (self.access + type.tag_name, self.enumItem (grammar, type.tag_value))
       self.put_func_end ()

       "conversion"
       if not self.rust :
          for c in type.conv_list :
             self.put_func ("conv_"  + c, self.pointer (c), virtual=True, cls = cls, inline = True)
             self.put_func_body ()
             self.put_return (self.null)
             self.put_func_end ()

          if type.super_type != "" :
             c = type.type_name

             over = False
             # the conv_ declaration lives on the ROOT of the hierarchy
             # (add_conv walks up), so "override" must be decided against
             # every ancestor, not just the direct superclass — otherwise
             # C#/Vala/Pascal emit "virtual" and the method HIDES the base
             # version instead of overriding it (conv_ then returns null)
             s = type.super_type
             while s != None and s != "" :
                if c in s.conv_list :
                   over = True
                s = s.super_type

             self.put_func ("conv_" + c, self.pointer (c), override = over, virtual = not over, cls = cls, inline = True)
             self.put_func_body ()
             self.put_return (self.this)
             self.put_func_end ()

       if self.rust :
          self.put_class_end ()
          self.send ("impl")
          self.send (type.type_name)
          self.new_line ()
          self.put_begin ()

       self.put_method_declarations (type.type_name)

       "end of class"
       self.put_class_end ()

   # -----------------------------------------------------------------------

   def executeMethod (self, grammar, func_dict, rule_name, no_param = False) :
       if rule_name in func_dict :
          method_name = func_dict [rule_name]
          if no_param :
             self.putLn (self.access + method_name + self.call + ";")
          else :
             self.putLn (self.access + method_name + " (result);")

   def declareCustomMethods (self, grammar) :
       for m in grammar.method_list :
          type = ""
          if m.is_bool :
             type = "bool"
          self.put_func (m.method_name, type = type, virtual = True, cls = self.class_name)
          if not m.no_param :
             if m.param_type == "" :
                m.param_type = self.base_name
             self.put_param ("item", self.pointer (self.subst (grammar, m.param_type)))
          self.put_func_body ()
          if m.is_bool :
             self.put_return ("false")
          self.put_func_end ()

   # -----------------------------------------------------------------------

   def declareSymbols (self, grammar) :
       self.put_enum (self.symbol_name)
       for symbol in grammar.symbols :
           self.put_enum_item (symbol.ident)
       self.put_enum_end ()

   # -----------------------------------------------------------------------

   def convertTerminals (self, grammar) :
       self.put_func ("tokenToString", cls = self.class_name, type = "string")
       self.put_param ("value", self.symbol_name)
       self.put_func_body ()

       for symbol in grammar.symbols :
           self.put_if ()
           self.send ("value")
           self.send (self.equal)
           if self.csharp or self.java :
              self.send (self.symbol_name + "." + grammar.symbols [symbol.inx].ident)
           else :
              self.send (str (symbol.inx))
           self.put_then ()
           self.put_begin (only_one = True)
           self.put_return (self.quote (symbol.alias))
           self.put_end (only_one = True)

       self.put_return (self.quote ("<unknown symbol>"))
       self.put_func_end ()

   # --------------------------------------------------------------------------

   def declareTranslate (self) :
       # Vala/C#/C++: Lexer.nextToken () calls the virtual translate ();
       # the generated parser overrides it (Java methods are virtual
       # implicitly, so Java needs no override keyword)
       self.put_func ("translate", cls = self.class_name,
                      override = self.vala or self.csharp or self.cpp)
       self.put_func_body ()

       self.put_if ()
       self.send (self.access + "tokenKind" + self.equal + self.nested + "nameToken")
       self.put_then ()
       self.put_begin ()
       self.put_assign (self.access + "token", self.symbolItem ("identifier"))
       self.putLn (self.access + "lookupKeyword" + self.call + ";")
       self.put_end ()

       self.send ("else")
       self.put_if ()
       self.send (self.access + "tokenKind" + self.equal + self.nested + "numberToken")
       self.put_then ()
       self.put_begin ()
       self.put_assign (self.access + "token", self.symbolItem ("number"))
       self.put_end ()

       self.send ("else")
       self.put_if ()
       self.send (self.access + "tokenKind" + self.equal + self.nested + "realToken")
       self.put_then ()
       self.put_begin ()
       self.put_assign (self.access + "token", self.symbolItem ("real_number"))
       self.put_end ()

       self.send ("else")
       self.put_if  ()
       self.send (self.access + "tokenKind" + self.equal + self.nested + "charToken")
       self.put_then ()
       self.put_begin ()
       self.put_assign (self.access + "token", self.symbolItem ("character_literal"))
       self.put_end ()

       self.send ("else")
       self.put_if ()
       self.send (self.access + "tokenKind" + self.equal + self.nested + "stringToken")
       self.put_then ()
       self.put_begin ()
       self.put_assign (self.access + "token", self.symbolItem ("string_literal"))
       self.put_end ()

       self.send ("else")
       self.put_if ()
       self.send (self.access + "tokenKind" + self.equal + self.nested + "eofToken")
       self.put_then ()
       self.put_begin ()
       self.put_assign (self.access + "token", self.symbolItem ("eos"))
       self.put_end ()

       self.putLn ("else")
       self.new_line ()
       self.put_begin ()
       self.put_assign (self.access + "token", self.symbolItem ("separator"))
       self.putLn (self.access + "processSeparator" + self.call + ";")
       self.put_end ()

       self.put_func_end ()

   # --------------------------------------------------------------------------

   def declareIsSymbol (self, grammar) :
       self.put_func ("isSymbol", type = "bool", cls = self.class_name, inline = True)
       self.put_param ("sym", self.symbol_name)
       self.put_func_body ()
       self.put_return (self.access + "token" + self.equal +"sym")
       self.put_func_end ()

       self.put_func ("checkSymbol", cls = self.class_name, inline = True)
       self.put_param ("sym", self.symbol_name)
       self.put_func_body ()
       self.put_if ()
       self.send (self.access + "token" + self.unequal +"sym")
       self.put_then ()
       self.put_begin ()
       self.putLn (self.access + "stop (" + self.access + "tokenToString (sym)" + self.string_suffix + " + " + self.quote (" expected") + self.string_suffix + ");")
       self.put_end (semicolon = True)
       self.putLn (self.nested + "nextToken" + self.call + ";")
       self.put_func_end ()

       self.put_func ("testSymbols", type = "bool", cls = self.class_name, inline = True)
       # The parameter type must match how condition () emits the set_N
       # tables in this language (short[] in Java/C#, array of byte in
       # Pascal, const unsigned char in C/C++).
       if self.rust :
          cnt = int ((grammar.symbol_cnt + 7) / 8)
          self.put_param ("table", "[u8;" + str (cnt) + "]")
       elif self.vala :
          self.put_param ("table", "uchar", array = True)
       elif self.java :
          self.put_param ("table", "short", array = True)
       elif self.csharp :
          self.put_param ("table", "byte", array = True)
       elif self.pascal :
          self.put_param ("table", "array of byte")
       else :
          self.put_param ("table", "const unsigned char", array = True)
       self.put_func_body ()
       # token is an enum in the typed targets; arithmetic needs the
       # underlying integer (Java/C#/Vala cast, Pascal ord, Rust as-cast).
       if self.java :
          tok = self.nested + "token.ordinal ()"
       elif self.csharp or self.vala :
          tok = "(int) " + self.nested + "token"
       elif self.rust :
          tok = self.nested + "token as i32"
       elif self.pascal :
          tok = "ord (" + self.nested + "token)"
       else :
          tok = self.nested + "token"
       self.put_local ("int", "pos", tok + self.div + "8")
       self.put_local ("int", "bit", tok + self.mod + "8")
       bit_test = "table [pos] " + self.bit_and + " (1" + self.shl + "bit)"
       if self.java or self.csharp or self.vala or self.rust :
          bit_test = "(" + bit_test + ")" + self.unequal + "0"
       self.put_return (bit_test)
       self.put_func_end ()

       self.put_func ("stop", cls = self.class_name, inline = True)
       self.put_param ("msg", "string")
       self.put_func_body ()
       self.putLn (self.access + "error (msg);")
       self.put_func_end ()

       self.put_func ("stop", cls = self.class_name, inline = True, alt_name = "stop_str")
       self.put_func_body ()
       self.putLn (self.access + "stop (" + self.quote ("Unexpected ") + self.string_suffix + " + " + self.access + "tokenToString (" + self.access + "token));")
       self.put_func_end ()

   # --------------------------------------------------------------------------

   def declareStoreLocation (self, grammar) :
       self.put_func ("storeLocation", cls = self.class_name)
       self.put_param ("item", self.pointer (self.base_name))
       self.put_func_body ()
       self.put_assign ("item" + self.arrow + "src_file", self.nested + "getTokenFileInx" + self.call)
       self.put_assign ("item" + self.arrow + "src_line", self.nested + "getTokenLine" + self.call)
       self.put_assign ("item" + self.arrow + "src_column", self.nested + "getTokenCol" + self.call)
       self.put_func_end ()

   # --------------------------------------------------------------------------

   """
   def declareCollections (self, grammar) :
       num = 0
       for data in grammar.collections :
           cnt = int ((grammar.symbol_cnt + 7) / 8)
           self.put_set_decl ("set_" + str (num), cnt)
   """

   def implementCollections (self, grammar) :
       num = 0
       for data in grammar.collections :

           cnt = int ((grammar.symbol_cnt + 7) / 8)
           self.put_set ("set_" + str (num), cnt)
           sum = 0
           mask = 1
           for inx in range (grammar.symbol_cnt) :
               if data & 1 << inx :
                  sum += mask
               mask = mask << 1

               if mask >= 256 :
                  self.put_set_item (sum)
                  sum = 0
                  mask = 1
           if mask > 1 :
              self.put_set_item (sum)
           self.put_set_end ()

           self.put ("// set_" + str (num) + " : ")
           for inx in range (grammar.symbol_cnt) :
               if data & 1 << inx :
                  self.put (" ")
                  symbol = grammar.symbols [inx]
                  if symbol.text != "" :
                     self.put (symbol.text)
                  else :
                     self.put (self.enumItem (grammar, symbol.ident))
           self.putEol ()
           self.putLn ()
           num = num + 1

   # --------------------------------------------------------------------------

   def findCollection (self, grammar, collection) :
       "collection is set of (at least four) symbols"
       if collection not in grammar.collections :
          error ("Unknown (not registered) collections")
       return grammar.collections.index (collection)

   def condition (self, grammar, ent_result, collection, predicate = None, semantic_predicate = None, test = False) :
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
                    code = code + self.log_or
                 start = False
                 symbol = grammar.symbols[inx]
                 if symbol.ident != "" and not (self.use_strings and symbol.text != "") :
                    # code = code + "token ==" + symbol.ident
                    code = code + self.access + "isSymbol (" + self.symbolItem (symbol.ident) + ")"
                 else :
                    code = code + self.access + "tokenTxt" + self.equal + self.quote (symbol.text)
       else :
          num = self.findCollection (grammar, collection)
          # code = "set_" + str (num) + " [token / 8] & 1 << token % 8"
          code = self.access + "testSymbols (set_" + str (num) + ")"

       if predicate != None :
          if not self.simpleExpression (predicate) :
             if cnt == 0 :
                code =  ""
             elif complex :
                code = "(" + code + ")" + self.log_and
                complex = False
             else :
                code = code + self.log_and
             inx = self.registerPredicateExpression (grammar, predicate)
             code = code + self.access + "test_" + str (inx) + " ()"

       if semantic_predicate != None and not test:
          if code == "" :
             code = ""
          else :
             if complex :
                code = "(" + code + ")"
             code = code + self.log_and
          code = code + semantic_predicate + " (" + ent_result + ")"

       return code

   def conditionFromAlternative (self, grammar, ent_result, alt, test = False) :
       code = ""
       done = False
       if alt.continue_alt :
          # semantic predicates inside choose
          for item in alt.items :
              if not done and isinstance (item, Ebnf) :
                 ebnf = item
                 code = self.conditionFromExpression (grammar, ent_result, ebnf.expr, test)
                 done = True
       if not done :
          code = self.condition (grammar, ent_result, alt.first, alt.predicate, alt.semantic_predicate, test)
       return code

   def conditionFromExpression (self, grammar, ent_result, expr, test = False) :
       code = ""
       for alt in expr.alternatives :
           if code != "" :
              code = code + self.log_or
           code = code + self.conditionFromAlternative (grammar, ent_result, alt, test)
       return code

   # -----------------------------------------------------------------------

   def registerPredicateExpression (self, grammar, expr) :
       if expr in grammar.predicates :
          return grammar.predicates.index (expr) + 1
       else :
          grammar.predicates.append (expr)
          return len (grammar.predicates)

   def registerPredicateNonterminal (self, grammar, item) :
       rule = item.rule_ref
       if rule not in grammar.test_dict :
          grammar.test_dict [rule] = True
          grammar.test_list.append (rule)

   def declarePredicates (self, grammar) :
       inx = 1
       for expr in grammar.predicates :
           self.put_func ("test_" + str (inx), type = "bool", cls = self.class_name)
           self.put_func_body ()
           self.put_local ("bool", "result", "true")
           self.put_local (self.mark_type, "position", "mark" + self.call)
           self.checkFromExpression (grammar, expr)
           self.putLn (self.access + "rewind (position);")
           self.put_return ("result")
           self.put_func_end ()
           inx = inx + 1

       for rule in grammar.test_list :
           self.testFromRule (grammar, rule)

# --------------------------------------------------------------------------

   def checkFromExpression (self, grammar, expr, reduced = False) :
       cnt = len (expr.alternatives)
       start = True
       stop = False
       for alt in expr.alternatives :
           if cnt > 1 :
              if stop :
                 gram.warning ("Cannot construct alternative condition")
              cond = self.conditionFromAlternative (grammar, alt, test = True)
              if cond == "True" or cond == "" :
                 stop = True
              if stop:
                 self.send ("else")
                 self.new_line ()
              else :
                 if not start :
                    self.send ("else")
                 self.put_if ()
                 self.send (cond)
                 self.put_then ()
              start = False
              self.put_begin ()
           self.checkFromAlternative (grammar, alt, cnt > 1 or reduced)
           if cnt > 1 :
              self.put_end ()
       if cnt > 1 and not stop :
          self.send ("else")
          self.new_line ()
          self.put_begin ()
          self.put_assign ("result", "false")
          self.put_end ()

   def checkFromAlternative (self, grammar, alt, reduced) :
       inx = 1
       for item in alt.items :
           if isinstance (item, Terminal) :
              self.checkFromTerminal (grammar, item, inx == 1 and reduced)
           elif isinstance (item, Nonterminal) :
              self.checkFromNonterminal (grammar, item)
           elif isinstance (item, Ebnf) :
              self.checkFromEbnf (grammar, item)
           inx = inx + 1

   def checkFromEbnf (self, grammar, ebnf) :
       if ebnf.mark == '?' :
          self.put_if ()
       elif ebnf.mark == '*' :
          self.put_while ()
       elif ebnf.mark == '+' :
          self.put_while ()

       if ebnf.mark != "" :
          self.put ("result" + self.log_and + "(")
          cond = self.conditionFromExpression (grammar, ebnf.expr, test = True)
          self.send (cond)
          self.put_then ()
          if ebnf.mark == '?' :
             self.put_then ()
          elif ebnf.mark == '*' :
             self.put_do ()
          elif ebnf.mark == '+' :
             self.put_do ()
          self.put_begin ()

       self.checkFromExpression (grammar, ebnf.expr, ebnf.mark != "")

       if ebnf.mark != "" :
          self.put_end (semicolon = True)

   def checkFromNonterminal (self, grammar, item) :
       self.registerPredicateNonterminal (grammar, item)
       self.put_if ()
       self.send ("result")
       self.put_then ()
       self.put_begin ()
       self.put_if ()
       self.send (self.log_not + self.access + "test_" + item.rule_name + self.call)
       self.put_then ()
       self.put_begin ()
       self.put_assign ("result", "false")
       self.put_end ()
       self.put_end (semicolon = True)

   def checkFromTerminal (self, grammar, item, reduced) :
       if not reduced :
          symbol = item.symbol_ref
          self.put_if ()
          self.send ("result" + self.log_and)
          if symbol.ident != "" and (symbol.multiterminal or not self.use_strings or symbol.text == "") :
             self.put ("token" + self.unequal + self.symbolItem (symbol.ident))
          elif symbol.text != "" :
             self.put ("tokenTxt" + self.unequal + self.quote (symbol.text))
          else :
             self.put (self.access + "check (" + str (symbol.inx) + ");")
          self.put_then ()
          self.put_begin ()
          self.put_assign ("result", "false")
          self.put_end (semicolon = True)

       self.put_if ()
       self.send ("result")
       self.put_then ()
       self.put_begin ()
       self.putLn (self.nested + "nextToken" + self.call + ";")
       self.put_end (semicolon = True)

   # -----------------------------------------------------------------------

   def testFromRule (self, grammar, rule) :
       self.put_func ("test_" + rule.name, type = "bool", cls = self.class_name)
       self.put_func_body ()
       self.testFromExpression (grammar, rule.expr)
       self.put_return ("true")
       self.put_func_end ()

   def testFromExpression (self, grammar, expr, reduced = False) :
       cnt = len (expr.alternatives)
       start = True
       for alt in expr.alternatives :
           if cnt > 1 :
              cond = self.conditionFromAlternative (grammar, alt.entry_result, alt, test = True)
              if not start :
                 self.send ("else")
              self.put_if ()
              start = False
              self.send (cond )
              self.put_then ()
              self.put_begin ()
           self.testFromAlternative (grammar, alt, cnt > 1 or reduced)
           if cnt > 1 :
              self.put_end ()
       if cnt > 1 :
          self.send ("else")
          self.put_begin ()
          self.put_return ("false")
          self.put_end (semicolon = True)

   def testFromAlternative (self, grammar, alt, reduced) :
       inx = 1
       for item in alt.items :
           if isinstance (item, Terminal) :
              self.testFromTerminal (grammar, item, inx == 1 and reduced)
           elif isinstance (item, Nonterminal) :
              self.testFromNonterminal (grammar, item)
           elif isinstance (item, Ebnf) :
              self.testFromEbnf (grammar, item)
           inx = inx + 1

   def testFromEbnf (self, grammar, ebnf) :
       if ebnf.mark == '?' :
          self.put_if ()
       elif ebnf.mark == '*' :
          self.put_while ()
       elif ebnf.mark == '+' :
          self.put_while ()

       if ebnf.mark != "" :
          cond = self.conditionFromExpression (grammar, ebnf.current_result, ebnf.expr, test = True)
          self.send (cond)
          if ebnf.mark == '?' :
             self.put_then ()
          elif ebnf.mark == '*' :
             self.put_do ()
          elif ebnf.mark == '+' :
             self.put_do ()
          self.put_begin ()

       self.testFromExpression (grammar, ebnf.expr, ebnf.mark != "")

       if ebnf.mark != "" :
          self.put_end (semicolon = True)

   def testFromNonterminal (self, grammar, item) :
       self.registerPredicateNonterminal (grammar, item)
       self.put_if ()
       self.send(self.log_not + self.access + "test_" + item.rule_name + " ()")
       self.put_then ()
       self.put_begin ()
       self.put_return ("false")
       self.put_end (semicolon = True)

   def testFromTerminal (self, grammar, item, reduced) :
       if not reduced :
          symbol = item.symbol_ref
          self.put_if ()
          if symbol.ident != "" and (symbol.multiterminal or not self.use_strings or symbol.text == "") :
             self.put (self.access + "token" + self.unequal + self.symbolItem (symbol.ident))
          elif symbol.text != "" :
             self.put (self.access + "tokenTxt" + self.unequal + self.quote (symbol.text))
          else :
             self.put (self.access + "check (" + str (symbol.inx) + ")")
          self.put_then ()
          self.put_begin ()
          self.put_return ("false")
          self.put_end (semicolon = True)

       self.putLn (self.nested + "nextToken" + self.call + ";")

   # -----------------------------------------------------------------------

   def parserFromRules (self, grammar) :
       for rule in grammar.rules :
           self.parserFromRule (grammar, rule)

   def headerFromRule (self, grammar, rule, only_header = False, cls = "") :
       params = ""

       self.put_func ("parse_" + rule.name, self.pointer (self.subst (grammar, rule.rule_type)), cls)

       if rule.rule_mode == "modify" :
          self.put_param ("result", self.pointer (self.subst (grammar, rule.rule_type)))
       if rule.store_name != "" :
          self.put_param ("store", self.pointer (self.subst (grammar, rule.store_type)))

       if only_header :
          self.put_func_decl ()

   def parserFromRule (self, grammar, rule) :
       grammar.updatePosition (rule)
       self.headerFromRule (grammar, rule, cls = self.class_name)

       self.put_func_body ()

       if rule.rule_mode == "modify" :
          if grammar.show_tree :
             self.put_monitor (self.access + "reopenObject", "result")

       if rule.rule_mode != "new" and rule.rule_mode != "modify" :
          if self.rust :
             self.put_local (self.pointer (self.subst (grammar, rule.rule_type)), "result")
          else :
             self.put_local (self.pointer (self.subst (grammar, rule.rule_type)), "result", self.null)
       if rule.rule_mode == "new" :
          self.put_local (self.pointer (self.subst (grammar, rule.rule_type)), "result" , self.newItem (grammar, rule.rule_type))
          if rule.tag_name != "" :
             self.put_assign ("result" + self.arrow + self.fieldItem (grammar, rule.rule_type, rule.tag_name), self.enumItem (grammar, rule.tag_value))
             type = grammar.struct_dict [rule.rule_type]
             if rule.tag_name != type.tag_name or rule.tag_value != type.tag_value :
                grammar.error ("Internal tag mismatch")

          self.storeLoc ("result")
          if grammar.show_tree :
             self.put_monitor (self.access + "openObject", "result")

       if rule.store_name != "" :
          self.put_assign ("result" + self.arrow + self.fieldItem (grammar, rule.rule_type, rule.store_name), self.store_pointer ("store"))

       self.executeMethod (grammar, grammar.execute_on_begin, rule.name)
       self.executeMethod (grammar, grammar.execute_on_begin_no_param, rule.name, no_param = True)

       self.parserFromExpression (grammar, rule, rule.expr)

       self.executeMethod (grammar, grammar.execute_on_end, rule.name)

       if rule.rule_mode == "new" or rule.rule_mode == "modify" :
          if grammar.show_tree :
             self.put_monitor ("closeObject")

       self.put_return ("result")
       self.put_func_end ()
       self.empty_line ()

   def parserFromExpression (self, grammar, rule, expr) :
       # Nullable alternatives go last (same as toparser.py): a nullable
       # alternative has no condition of its own and becomes the final
       # "else" branch. Without the reorder a nullable alternative in the
       # middle would be emitted as "else" and the alternatives after it
       # as another "else" — "else { } else { }" is invalid in every
       # brace language.
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
              cond = self.conditionFromAlternative (grammar, alt.entry_result, alt)
              if cond == "True" or cond == "" :
                 stop = True
              if stop:
                 self.send ("else")
                 self.new_line ()
              else :
                 if not start :
                    self.send ("else")
                 self.put_if ()
                 self.send (cond)
                 self.put_then ()
              start = False
              self.put_begin ()
           self.parserFromAlternative (grammar, rule, alt)
           if cnt > 1 :
              self.put_end ()
       if cnt > 1 and not stop:
          self.send ("else")
          self.put_begin ()
          self.putLn (self.access + "stop (" +  self.quote ("Unexpected token") + self.string_suffix + ");")
          self.put_end (semicolon = True)
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
                    self.put_if ()
                    self.send (self.access + func_name + " (result)")
                    self.put_then ()
                    self.put_begin ()
                    opened_if = True
              self.parserFromEbnf (grammar, rule, item)
           elif isinstance (item, Assign) :
              value = item.value
              if value == "True" :
                 value = "true"
              elif value == "False" :
                 value = "false"
              else :
                 value = self.enumItem (grammar, value)
              self.put_assign (item.current_result + self.arrow + self.fieldItem (grammar, rule.rule_type, item.variable), value)
           elif isinstance (item, Execute) :
              if item.no_param :
                 self.putLn (self.access + item.name + self.call + ";")
              else :
                 self.putLn (self.access + item.name + " (" + item.current_result + ");")
           elif isinstance (item, New) :
              self.put_local (self.pointer (self.subst (grammar, rule.rule_type)), "store", "result")
              self.put_local (self.pointer (self.subst (grammar, item.new_type)), item.current_result, self.newItem (grammar, item.new_type))
              self.storeLoc (item.current_result)
              self.put_assign (item.current_result + self.arrow + self.fieldItem (grammar, rule.rule_type, item.store_name), self.store_pointer ("store"))
              self.put_assign ("result", item.current_result)
              if grammar.show_tree :
                 self.put_monitor ("openObject", item.current_result)
                 opened_branch = True
           elif isinstance (item, Style) :
              pass
           else :
              grammar.error ("Unknown alternative item: " + item.__class__.__name__)
       if opened_branch :
          self.put_monitor ("closeObject")
       if opened_if :
           self.put_end (semicolon = True)

   def parserFromEbnf (self, grammar, rule, ebnf) :
       if ebnf.mark == '?' :
          self.put_if ()
       elif ebnf.mark == '*' :
          self.put_while ()
       elif ebnf.mark == '+' :
          self.put_while ()

       if ebnf.mark != "" :
          cond = self.conditionFromExpression (grammar, ebnf.current_result, ebnf.expr)
          self.send (cond )
          if ebnf.mark == '?' :
             self.put_then ()
          elif ebnf.mark == '*' :
             self.put_do ()
          elif ebnf.mark == '+' :
             self.put_do ()
          self.put_begin ()

       self.parserFromExpression (grammar, rule, ebnf.expr)

       if ebnf.mark != "" :
          self.put_end (semicolon = True)

   def parserFromNonterminal (self, grammar, rule, item) :
       if item.select_item :
          self.executeMethod (grammar, grammar.execute_on_entry_no_param, rule.name, no_param = True)

       if item.select_item :
          "declare result0 variable for select item"
          if item.item_link.select_independent :
             self.put_local_start (self.pointer (self.subst (grammar, item.current_type)), item.current_result) # declare new result0 variable

       if item.add :
          # if self.pascal :
          self.put_vector_add (item.current_result + self.arrow + self.fieldItem (grammar, rule.rule_type, "items"))
          # else :
          # self.put (item.current_result + self.arrow + "items." + self.push_back + " (:")
       if item.select_item or item.continue_item or item.return_item :
          self.put (item.current_result + self.assign)
       if item.variable != ""  :
          self.put (item.current_result + self.arrow +
                    self.identifier (item.variable) + self.assign)

       if item.variable != "" :
          self.put_store_pointer ()
       if item.add :
          self.put_store_box ()

       self.put (self.access + "parse_" + item.rule_name)

       params = ""
       if item.modify or item.rule_ref.rule_mode == "modify" :
          params = item.current_result
       if item.rule_ref.store_name != "" :
          "set params before result0 is reverted to result"
          if item.store_result != "" :
             params = item.store_result
          else :
             params = item.current_result

       self.put (" (")
       if params != "" :
          self.put (params)
       self.put (")")

       if item.variable != "" :
          self.put_store_pointer_end ()
       if item.add :
          self.put_store_box_end ()
       if item.add :
          self.put_vector_add_end () # close append parameters
       self.putLn (";")

       if item.select_item :
          self.executeMethod (grammar, grammar.execute_on_fork_no_param, rule.name, no_param = True)

   def parserFromTerminal (self, grammar, rule, item) :
       symbol = item.symbol_ref
       if symbol.multiterminal :
          if item.variable != "" :
             self.put (item.current_result + self.arrow + self.fieldItem (grammar, rule.rule_type, item.variable) + self.assign)

          name = symbol.ident
          if name == "identifier" :
             func = "readIdent"
          elif name == "number" :
             func = "readNumber"
          elif name == "real_number" :
             func = "readReal"
          elif name == "character_literal" :
             # with quotes (like C++): C-- stores '\n' whole, not just the char
             func = "readQuotedCharAsString"
          elif name == "string_literal" :
             func = "readQuotedString"
          else :
             func = "unknown"

          self.putLn (self.nested + func + self.call + ";")
       else :
          if symbol.ident != "" and not (self.use_strings and symbol.text != "") :
             self.putLn (self.access + "checkSymbol (" +self.symbolItem (symbol.ident) + ");")
          else :
             self.putLn (self.access + "check (" + self.quote (symbol.text) + ");")

   # -----------------------------------------------------------------------

   def __init__ (self) :
       super (CParser, self).__init__ ()
       self.lexer_header = "lexer.h"
       self.parser_header = "parser.h"
       self.lexer_name = "Lexer"
       self.symbol_name = "CmmSymbol"
       self.base_name = "CmmBasic"
       self.mark_type = "int" # type of mark () / rewind () parameter
       self.class_name = "Parser"

   # -----------------------------------------------------------------------

   def declareParser (self, grammar) :

       if not self.c :
          self.put_class (self.class_name, above = self.lexer_name)
          self.put_public ()

       self.put_member (self.symbol_name, "token")
       self.empty_line ()

       self.put_proc (self.class_name, constructor = True)

       self.parserFromRules (grammar)
       self.declarePredicates (grammar)

       self.declareIsSymbol (grammar)

       self.selectKeywords (grammar)
       self.selectSeparators (grammar)
       self.convertTerminals (grammar)

       self.declareTranslate ()
       self.declareStoreLocation (grammar)

       self.declareCustomMethods (grammar)

       if self.csharp or self.java or self.vala :
          self.implementCollections (grammar)

       # constructor
       self.put_func (self.class_name, cls = self.class_name, constructor = True)
       self.put_func_body ()
       # if grammar.show_tree :
       #    self.putLn ("monitor = NULL")
       self.put_func_end ()

       if self.rust :
          self.put_class_end ()
          self.send ("impl")
          self.send (self.class_name)
          self.new_line ()
          self.put_begin ()

       self.put_method_declarations (self.class_name)

       if not self.c :
          self.put_class_end ()

   def implementParser (self, grammar) :
       self.put_method_implementations (self.class_name)

   # -----------------------------------------------------------------------

   def parserCSharp (self, grammar, ns) :

       self.putLn ("using System.Collections.Generic;")
       self.empty_line ()

       self.send ("namespace")
       self.send (ns)
       self.putEol ()
       self.put_begin ()

       initSymbols (grammar)
       self.declareSymbols (grammar)
       self.declareEnumTypes (grammar)

       self.declareParser (grammar)

       # self.basicClass ()
       self.declareStructures (grammar)

       self.empty_line ()
       self.put_end () # end of namespace

   # -----------------------------------------------------------------------

   def parserJava (self, grammar, ns) :

       self.send ("package")
       self.send (ns)
       self.send (";")
       self.putEol ()
       self.empty_line ()

       self.putLn ("import java.util.ArrayList;")
       self.empty_line ()

       initSymbols (grammar)
       self.declareSymbols (grammar)
       self.declareEnumTypes (grammar)

       self.declareParser (grammar)

       # self.basicClass ()
       self.declareStructures (grammar)

   # -----------------------------------------------------------------------

   def parserPascal (self, grammar, ns) :

       self.putLn ("unit " + ns + ";")
       self.empty_line ()

       self.putLn ("interface")
       self.empty_line ()

       self.putLn ("uses LexerUnit;")
       self.empty_line ()

       self.putLn ("type")
       self.indent ()

       initSymbols (grammar)
       self.declareSymbols (grammar)
       self.declareEnumTypes (grammar)

       # self.putLn (self.base_name + " = class;")
       for type in grammar.struct_list :
           self.putLn (type.type_name + " = class;")
       self.putLn ()

       # self.basicClass ()
       self.declareParser (grammar)
       self.declareStructures (grammar)

       self.unindent () # end of type section

       self.empty_line ()
       self.putLn ("implementation")
       self.empty_line ()

       self.implementCollections (grammar)
       self.implementParser (grammar)
       self.implementStructures (grammar)

       self.empty_line ()
       self.putLn ("end.")

   # -----------------------------------------------------------------------

   def parserVala (self, grammar, ns) :

       if ns != "" :
          self.send ("namespace")
          self.send (ns)
          self.putEol ()
          self.put_begin ()

       initSymbols (grammar)
       self.declareSymbols (grammar)
       self.declareEnumTypes (grammar)

       self.declareParser (grammar)

       # self.basicClass ()
       self.declareStructures (grammar)

       if ns != "" :
          self.empty_line ()
          self.put_end () # end of namespace

   # -----------------------------------------------------------------------

   def parserJavaScript (self, grammar, ns = "") :
       # ns parameter is important for buildAnotherParser in env.py

       initSymbols (grammar)
       self.declareSymbols (grammar)
       self.declareEnumTypes (grammar)

       # self.basicClass ()
       self.declareStructures (grammar)

       self.declareParser (grammar)
       self.implementParser (grammar)
       self.implementCollections (grammar)

   # -----------------------------------------------------------------------

   def parserRust (self, grammar, ns = "") :
       # ns parameter is important for buildAnotherParser in env.py

       self.putLn ()
       self.putLn ("#![allow(warnings, unused)]")
       self.putLn ()

       self.putLn ("mod lexer;")
       self.putLn ("use lexer::Lexer;")
       self.putLn ()

       initSymbols (grammar)
       self.declareSymbols (grammar)
       self.declareEnumTypes (grammar)

       # self.basicClass ()
       self.declareStructures (grammar)

       self.declareParser (grammar)

       self.implementParser (grammar)
       self.implementCollections (grammar)

   # -----------------------------------------------------------------------

   def parserHeader (self, grammar, header_name = "") :
       # header_name = the header file being written (the CLI passes its
       # --header value; library users pass their target name). It only
       # feeds the include-guard symbol.
       if header_name == "" :
          header_name = self.parser_header
       header_symbol = self.get_header_symbol (header_name)
       self.put_header_ifdef (header_symbol)

       self.putLn ("#include " + quoteString (self.lexer_header))
       for name in grammar.header_list :
          self.putLn ("#include " + quoteString (name))
       if not self.c :
          self.putLn ("#include <string>")
          self.putLn ("#include <vector>")
          self.putLn ("using std::string;")
          self.putLn ("using std::vector;")
       self.putLn ()

       # self.putLn ("class " + self.base_name + ";")
       for type in grammar.struct_list :
           self.put_class_forw (type.type_name)
       self.putLn ()

       initSymbols (grammar)
       self.declareSymbols (grammar)
       self.declareEnumTypes (grammar)
       # self.basicClass ()
       self.declareParser (grammar)
       self.declareStructures (grammar)

       self.put_header_endif (header_symbol)

   def parserCode (self, grammar) :
       "call parserCode after parserHeader"

       "parser generation"
       self.putLn ("#include " + quoteString (self.parser_header))
       self.empty_line ()

       self.implementCollections (grammar)
       self.implementParser (grammar)
       self.implementStructures (grammar)

# --------------------------------------------------------------------------

if __name__ == "__main__" :

   import optparse

   options = optparse.OptionParser (usage = "usage: %prog [options] input_grammar_file")

   options.add_option ("--code",   dest="code",   default = "",    action="store",      help="Output file name")
   options.add_option ("--header", dest="header", default = "",    action="store",      help="Output header file name")

   options.add_option ("--cpp",    dest="cpp",    default = False, action="store_true", help="C++")
   options.add_option ("--c",      dest="c",      default = False, action="store_true", help="C")
   options.add_option ("--csharp", dest="csharp", default = False, action="store_true", help="C#")
   options.add_option ("--java",   dest="java",   default = False, action="store_true", help="Java")
   options.add_option ("--pascal", dest="pascal", default = False, action="store_true", help="Pascal")
   options.add_option ("--vala",   dest="vala",   default = False, action="store_true", help="Vala")
   options.add_option ("--js",     dest="js",     default = False, action="store_true", help="Java Script")
   options.add_option ("--rust",   dest="rust",   default = False, action="store_true", help="Rust")

   options.add_option ("--ns", "--namespace", "--package", "--unit", dest="ns", default = "", action="store", help="C# namespace, Java package, Pascal unit")
   options.add_option ("--lexer",  dest="lexer", default = "", action="store", help="lexer header name")
   options.add_option ("--class",  dest="class_name", default = "", action="store", help="Parser class name")
   options.add_option ("--lexer-class", dest="lexer_name", default = "", action="store", help="Base class of the parser (lexer)")
   options.add_option ("--base",   dest="base_name", default = "", action="store", help="Base class of the generated structures")
   options.add_option ("--symbol", dest="symbol_name", default = "", action="store", help="Name of the symbol enumeration")
   options.add_option ("--mark-type", dest="mark_type", default = "", action="store", help="Type of mark () / rewind () (default int)")

   (opts, args) = options.parse_args ()

   if len (args) == 0 :
      options.error ("Missing input file name")
   if len (args) > 1 :
      options.error ("Too many input file names")

   inputFileName = args [0]
   headerFileName = opts.header
   codeFileName = opts.code

   product = CParser ()

   if opts.class_name != "" :
      product.class_name = opts.class_name
   if opts.lexer_name != "" :
      product.lexer_name = opts.lexer_name
   if opts.base_name != "" :
      product.base_name = opts.base_name
   if opts.symbol_name != "" :
      product.symbol_name = opts.symbol_name
   if opts.mark_type != "" :
      product.mark_type = opts.mark_type

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
      product.parser_header = os.path.basename (headerFileName)

   if opts.lexer != "" :
      product.lexer_header = opts.lexer

   grammar = Grammar ()
   grammar.openFile (inputFileName)
   grammar.parseRules ()
   grammar.close ()

   if product.csharp :
      product.open (codeFileName)
      product.parserCSharp (grammar, opts.ns)
      product.close ()
   elif product.java :
      product.open (codeFileName)
      product.parserJava (grammar, opts.ns)
      product.close ()
   elif product.pascal :
      product.open (codeFileName)
      product.parserPascal (grammar, opts.ns)
      product.close ()
   elif product.vala :
      product.open (codeFileName)
      product.parserVala (grammar, opts.ns)
      product.close ()
   elif product.js :
      product.open (codeFileName)
      product.parserJavaScript (grammar)
      product.close ()
   elif product.rust :
      product.open (codeFileName)
      product.parserRust (grammar)
      product.close ()
   else :
      product.open (headerFileName)
      product.parserHeader (grammar, headerFileName)
      product.close ()

      product.open (codeFileName)
      product.parserCode (grammar)
      product.close ()

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
