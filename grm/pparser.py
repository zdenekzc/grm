
# pas_parser.py

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

from toparser import ToParser

# --------------------------------------------------------------------------

class PasParser (ToParser) :

   use_strings = False # True ... use symbol text (in parsing)

   def prindKeywordItem (self, dictionary, inx, name) :
       self.putLn ("begin")
       self.incIndent ()
       if len (dictionary) == 0 :
          self.putLn ("token := " + "keyword_" + name + ";")
       else :
          self.printKeywordDictionary (dictionary, inx+1, name)
       self.decIndent ()
       self.putLn ("end")

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
             self.putLn ("if s[" + str (inx+1) + "] = " + "'" + substr + "'" + " then")
          else :
             self.putLn ("if copy (s, " + str (start_inx+1) + ", " + str (inx+1-start_inx) + ") = " + "'" + substr + "'" + " then")
          self.prindKeywordItem (dictionary, inx, name)
       else :
           first_item = True
           for c in sorted (dictionary.keys ()) :
               if first_item :
                  cmd = "if"
                  first_item = False
               else :
                  cmd = "else if"
               self.putLn (cmd + " s[" + str (inx+1) + "] = "  "'" + c + "'" + " then")
               self.prindKeywordItem (dictionary[c], inx, name+c)

   def selectKeywords (self, grammar) :
       self.putLn ("procedure " + self.class_name + ".lookupKeyword;")
       self.putLn ("var s : string;")
       self.putLn ("var n : integer;")
       self.putLn ("begin")
       self.incIndent ()
       self.putLn ("s := tokenText;")
       self.putLn ("n := length (s);")

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
                cmd = "else if"
             self.putLn (cmd + " n = " + str (size) + " then begin")
             self.incIndent ()
             self.printKeywordDictionary (tree, 0, "")
             self.decIndent ()
             self.putLn ("end")
          size = size + 1

       self.decIndent ()
       self.putLn ("end;")
       self.putLn ()

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
           if level == 1 :
              self.put ("if tokenText = " + "'" + c + "'")
           else :
              self.put ("if inpCh = " + "'" + c + "'")
           self.putLn (" then begin")
           self.incIndent ()
           name = prefix + c
           if name in grammar.separator_dict :
              self.putLn ("token := " + grammar.separator_dict[name].ident + ";")
           if level > 1 :
              self.putLn ("tokenText := tokenText + inpCh;")
              self.putLn ("nextCh;")
           if len (dictionary[c]) != 0 :
              self.selectBranch (grammar, dictionary[c], level+1, prefix+c)
           self.decIndent ()
           self.putLn ("end;")

   def selectSeparators (self, grammar) :
       self.putLn ("procedure " + self.class_name + ".processSeparator;")
       self.putLn ("begin")
       self.incIndent ()

       tree = { }
       for name in grammar.separator_dict :
           self.addToDictionary (tree, name)

       self.selectBranch (grammar, tree, 1, "")

       self.putLn ("if token = separator then begin")
       self.incIndent ()
       self.putLn ("error (" + "'" + "Unknown separator" + "'" + ");")
       self.decIndent ()
       self.putLn ("end;")

       self.decIndent ()
       self.putLn ("end;")
       self.putLn ()

   # -----------------------------------------------------------------------

   def declareEnumTypes (self, grammar) :
       for type in grammar.struct_list :
           self.declareEnum (grammar, type)

   def declareTypes (self, grammar) :
       for type in grammar.struct_list :
           self.declareClass (grammar, type)
       for t in grammar.typedef_list :
          self.putLn (t.new_name + " = " + t.old_name + ";")
       self.style_empty_line ()

   def implementTypes (self, grammar) :
       for type in grammar.struct_list :
           self.implementClass (grammar, type)

   def declareEnum (self, grammar, type) :
       for enum_name in type.enums :
           enum = type.enums [enum_name]
           self.putLn (enum.enum_name + " = (")
           self.incIndent ()
           any = False
           for value in enum.values :
               if any :
                  self.putLn (",")
               any = True
               self.put (value)
           if any :
              self.putLn ()
           self.decIndent ()
           self.putLn (");")
           self.style_empty_line ()

   def declareClass (self, grammar, type) :
       self.put (type.type_name + " = class")
       if type.super_type != None :
          super_name = type.super_type.type_name
       elif type.type_name != self.base_name:
          super_name = self.base_name
       else :
          super_name = ""
       if super_name != "" :
          self.put (" (" + super_name + ")")
       self.putEol ()
       self.putLn ("public")
       self.incIndent ()

       "field declaration"
       for field in type.field_list :
          self.put (field.field_name + ": ")

          if field.is_bool :
             self.put ("boolean")
          elif field.is_enum :
             self.put (field.field_type)
          elif field.is_int :
             self.put ("integer")
          elif field.is_str :
             self.put ("string")
          elif field.is_ptr :
             self.put (field.field_type)
          elif field.is_list :
             self.put ("array of " + field.field_type)
          else :
             self.put (field.field_type) # !?

          self.putLn (";")

       self.style_empty_line ()

       self.putLn ("constructor create;")
       self.style_empty_line ()

       "conversion"
       for c in type.conv_list :
          self.putLn ("function conv_"  + c + " : " + c + "; virtual;")
       if type.super_type != "" :
          c = type.type_name
          self.putLn ("function conv_"  + c + " : " + c + "; virtual;") # override

       "end of class"
       self.style_no_empty_line ()
       self.decIndent ()
       self.putLn ("end;")
       self.putLn ()

   def implementClass (self, grammar, type) :
       "constructor"
       self.putLn ("constructor " + type.type_name + ".create;")
       self.putLn ("begin")
       self.incIndent ()
       self.putLn ("inherited create;")

       for field in type.field_list :

           if field.field_name != type.tag_name :
              self.put (field.field_name + " := ")
              if field.is_bool :
                 self.put ("false")
              elif field.is_enum :
                 self.put (field.field_type + " (0)")
              elif field.is_int :
                 self.put ("0")
              elif field.is_str :
                 self.put ("'" + "'")
              elif field.is_ptr :
                 self.put ("nil")
              elif field.is_list :
                 self.put ("[ ]")
              else :
                 self.put ("nil") # !?
              self.putLn (";")

       if type.tag_name != "" :
          self.putLn (type.tag_name + " := " + type.tag_value + ";")

       self.decIndent ()
       self.putLn ("end;")
       self.style_empty_line ()

       "conversion"
       for c in type.conv_list :
          self.put ("function " + type.type_name + ".conv_"  + c + " : " + c + ";")
          self.putLn (" begin result := nil; end;")
       if type.super_type != "" :
          c = type.type_name
          self.put ("function " + c + ".conv_"  + c + " : " + c + ";")
          self.putLn (" begin result := self; end;")
       self.style_empty_line ()

   # -----------------------------------------------------------------------

   def executeMethod (self, grammar, func_dict, rule_name, no_param = False) :
       if rule_name in func_dict :
          method_name = func_dict [rule_name]
          if no_param :
             self.putLn (method_name + ";")
          else :
             self.putLn (method_name + " (result);")

   def declareMethods (self, grammar, impl) :
       for m in grammar.method_list :
          if m.is_bool :
             self.put ("function")
          else :
             self.put ("procedure")
          self.put (" ")
          if impl :
             self.put (self.class_name + ".")
          self.put (m.method_name + " ")
          if not m.no_param :
             if m.param_type == "" :
                m.param_type = self.base_name
             self.put ("(item: " + m.param_type + ")")
          if m.is_bool :
             self.put (": boolean")
          self.put ("; ")
          if not impl :
             self.putLn ("virtual;")
          if impl :
             if m.is_bool :
                self.putLn ("begin result := false; end;")
             else :
                self.putLn ("begin end;")

   # -----------------------------------------------------------------------

   def declareSymbols (self, grammar) :
       self.putLn (self.symbol_name + " = (")
       self.incIndent ()
       any = False
       for symbol in grammar.symbols :
           if any :
              self.putLn (",")
           any = True

           self.put (symbol.ident)
           """
           self.put (" /* " + str (symbol.inx) + " : ")
           if symbol.text != "" :
              self.put (symbol.text)
           else :
              self.put (symbol.alias)
           self.put (" */")
           """
       self.putEol ()
       self.decIndent ()
       self.putLn (");")
       self.putLn ("")

   # -----------------------------------------------------------------------

   def convertTerminals (self, grammar) :
       self.putLn ("function " + self.class_name + ".tokenToString (value : " + self.symbol_name + ") : string;")
       self.putLn ("begin")
       self.incIndent ()

       for symbol in grammar.symbols :
           self.putLn ("if ord (value) = " + str (symbol.inx) + " then " + "result := " + "'" + symbol.alias + "'" + ";")

       self.putLn ("result := " + "'" + "<unknown symbol>" + "'" + ";")
       self.decIndent ()
       self.putLn ("end;")
       self.putLn ()

   # --------------------------------------------------------------------------

   def declareTranslate (self) :
       self.putLn ("procedure " + self.class_name + ".translate;")
       self.putLn ("begin")
       self.incIndent ()

       self.putLn ("if tokenKind = identToken then begin")
       self.incIndent ()
       self.putLn ("token := identifier;")
       self.putLn ("lookupKeyword;")
       self.decIndent ()
       self.putLn ("end")

       self.putLn ("else if tokenKind = numberToken then begin")
       self.incIndent ()
       self.putLn ("token := number;")
       self.decIndent ()
       self.putLn ("end")

       self.putLn ("else if tokenKind = realToken then begin")
       self.incIndent ()
       self.putLn ("token := real_number;")
       self.decIndent ()
       self.putLn ("end")

       self.putLn ("else if tokenKind = charToken then begin")
       self.incIndent ()
       self.putLn ("token := character_literal;")
       self.decIndent ()
       self.putLn ("end")

       self.putLn ("else if tokenKind = stringToken then begin")
       self.incIndent ()
       self.putLn ("token := string_literal;")
       self.decIndent ()
       self.putLn ("end")

       self.putLn ("else if tokenKind = eofToken then begin")
       self.incIndent ()
       self.putLn ("token := eos;")
       self.decIndent ()
       self.putLn ("end")

       self.putLn ("else begin")
       self.incIndent ()
       self.putLn ("token := separator;")
       self.putLn ("processSeparator;")
       self.decIndent ()
       self.putLn ("end;")

       self.decIndent ()
       self.putLn ("end;")
       self.putLn ()

   # --------------------------------------------------------------------------

   def declareIsSymbol (self) :
       self.putLn ("function " + self.class_name + ".isSymbol (sym : " + self.symbol_name + ") : boolean;")
       self.putLn ("begin")
       self.incIndent ()
       self.putLn ("result := token = sym;")
       self.decIndent ()
       self.putLn ("end;")
       self.style_empty_line ()

       self.putLn ("procedure " + self.class_name + ".checkSymbol (sym : " + self.symbol_name + ");")
       self.putLn ("begin")
       self.incIndent ()
       self.putLn ("if token <> sym then");
       self.incIndent ()
       self.putLn ("error (tokenToString (sym) + " + "'" + " expected" + "'" + ");")
       self.decIndent ()
       self.putLn ("nextToken;");
       self.decIndent ()
       self.putLn ("end;")
       self.style_empty_line ()

       self.putLn ("function " + self.class_name + ".testSymbols (table : array of byte) : boolean;")
       self.putLn ("var pos, bit: integer;")
       self.putLn ("begin")
       self.incIndent ()
       self.putLn ("pos := ord (token) div 8;");
       self.putLn ("bit := ord (token) mod 8;")
       self.putLn ("result := table [pos] and (1 shl bit) <> 0;")
       self.decIndent ()
       self.putLn ("end;")
       self.style_empty_line ()

       self.putLn ("procedure " + self.class_name + ".stop;")
       self.putLn ("begin")
       self.incIndent ()
       self.putLn ("error (" + "'" + "Unexpected" + "'" + " + tokenToString (token));")
       self.decIndent ()
       self.putLn ("end;")
       self.style_empty_line ()


   # --------------------------------------------------------------------------

   def declareStoreLocation (self, grammar) :
       self.putLn ("procedure " + self.class_name + ".storeLocation (item : " + self.base_name + ");")
       self.putLn ("begin")
       self.incIndent ()
       # self.putLn ("item.src_file := FileInx;")
       self.putLn ("item.src_line := TokenLine;")
       self.putLn ("item.src_col := TokenCol;")
       # self.putLn ("item.src_pos = tokenByteOfs;")
       # self.putLn ("item.src_end = charByteOfs;")
       self.decIndent ()
       self.putLn ("end;")
       self.putLn ()

   # --------------------------------------------------------------------------

   def declareCollections (self, grammar) :
       num = 0
       for data in grammar.collections :

           cnt = int ((grammar.symbol_cnt + 7) / 8);
           self.put ("const set_" + str (num) + " : array [0.." + str (cnt-1) + "] of byte = (" )
           sum = 0;
           mask = 1;
           any = False
           for inx in range (grammar.symbol_cnt) :
               if data & 1 << inx :
                  sum += mask
               mask = mask << 1

               if mask >= 256 :
                  if any :
                     self.put (", ")
                  self.put (str (sum))
                  sum = 0
                  mask = 1
                  any = True
           if mask > 1 :
              if any :
                 self.put (", ")
                 self.put (str (sum))
           self.putLn (");")

           self.put ("// set_" + str (num) + " : ")
           for inx in range (grammar.symbol_cnt) :
               if data & 1 << inx :
                  self.put (" ")
                  symbol = grammar.symbols [inx]
                  if symbol.text != "" :
                     self.put (symbol.text)
                  else :
                     self.put (symbol.ident)
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
                    code = code + " or "
                 start = False
                 symbol = grammar.symbols[inx]
                 if symbol.ident != "" and not (self.use_strings and symbol.text != "") :
                    # code = code + "token ==" + symbol.ident
                    code = code + "isSymbol (" + symbol.ident + ")"
                 else :
                    code = code + "tokenText = " + "'" + symbol.text + "'"
       else :
          num = self.findCollection (grammar, collection)
          # code = "set_" + str (num) + " [token / 8] & 1 << token % 8";
          code = "testSymbols (set_" + str (num) + ")";

       if predicate != None :
          if not self.simpleExpression (predicate) :
             if cnt == 0 :
                code =  ""
             elif complex :
                code = "(" + code + ")" + " and "
                complex = False
             else :
                code = code + " and "
             inx = self.registerPredicateExpression (grammar, predicate)
             code = code + "test_" + str (inx)

       if semantic_predicate != None and not test:
          if code == "" :
             code = ""
          else :
             if complex :
                code = "(" + code + ")"
             code = code + " and "
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
              code = code + " or "
           code = code + self.conditionFromAlternative (grammar, ent_result, alt, test)
       return code

   """
   def conditionFromRule (self, grammar, name) :
       if name not in grammar.rule_dict :
          grammar.error ("Unknown rule: " + name)
       rule = grammar.rule_dict [name]
       return self.condition (grammar, rule.first)
   """

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
           self.putLn ("function " + self.class_name + ".test_" + str (inx) + " : boolean;")
           self.putLn ("var position : integer;")
           self.putLn ("begin")
           self.incIndent ()
           self.putLn ("result := true;")
           self.putLn ("position := mark;")
           self.checkFromExpression (grammar, expr)
           self.putLn ("rewind (position);")
           self.decIndent()
           self.putLn ("end;")
           self.putLn ()
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
              if cond == "True" or cond == "":
                 stop = True
              if start :
                 self.put ("if " + cond + " then")
              elif stop:
                 self.putEol ()
                 self.put ("else")
              else :
                 self.putEol ()
                 self.put ("else if " + cond + " then")
              start = False
              self.putLn (" begin")
              self.incIndent ()
           self.checkFromAlternative (grammar, alt, cnt > 1 or reduced)
           if cnt > 1 :
              self.decIndent ()
              self.putLn ("end")
       if cnt > 1 and not stop :
          self.putEol ()
          self.putLn ("else begin")
          self.incIndent ()
          self.putLn ("result := false;")
          self.decIndent ()
          self.put ("end")
       if cnt > 1 :
          self.putLn (";")

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
          self.put ("if")
       elif ebnf.mark == '*' :
          self.put ("while")
       elif ebnf.mark == '+' :
          self.put ("while")

       if ebnf.mark != "" :
          self.put ("result and (")
          cond = self.conditionFromExpression (grammar, ebnf.expr, test = True)
          self.put (" " + cond + " ")
          if ebnf.mark == '?' :
             self.put ("then")
          else :
             self.put ("do")
          self.putLn (" begin")
          self.incIndent ()

       self.checkFromExpression (grammar, ebnf.expr, ebnf.mark != "")

       if ebnf.mark != "" :
          self.decIndent ()
          self.putLn ("end;")

   def checkFromNonterminal (self, grammar, item) :
       self.registerPredicateNonterminal (grammar, item)
       self.putLn ("if result then begin")
       self.incIndent ()
       self.putLn ("if not test_" + item.rule_name + " then begin")
       self.incIndent ()
       self.putLn ("result := false;")
       self.decIndent ()
       self.putLn ("end;")
       self.decIndent ()
       self.putLn ("end;")

   def checkFromTerminal (self, grammar, item, reduced) :
       if not reduced :
          symbol = item.symbol_ref
          self.put ("if result and ")
          if symbol.ident != "" and (symbol.multiterminal or not self.use_strings or symbol.text == "") :
             self.put ("(token <> " + symbol.ident + ")")
          elif symbol.text != "":
             self.put ("(tokenText <> " + "'" + symbol.text + "'" + ")")
          else :
             self.put ("check (" + str (symbol.inx) + ");")
          self.putLn (" then begin")
          self.incIndent ()
          self.putLn ("result := false;")
          self.decIndent ()
          self.putLn ("end;")

       self.putLn ("if result then begin")
       self.incIndent ()
       self.putLn ("nextToken;")
       self.decIndent ()
       self.putLn ("end;")

   # -----------------------------------------------------------------------

   def testFromRule (self, grammar, rule) :
       self.putLn ("function " + self.class_name + ".test_" + rule.name + " : boolean;")
       self.putLn ("begin")
       self.incIndent ()
       self.testFromExpression (grammar, rule.expr)
       self.putLn ("result := true;")
       self.decIndent ()
       self.putLn ("end;")
       self.putEol ()

   def testFromExpression (self, grammar, expr, reduced = False) :
       cnt = len (expr.alternatives)
       start = True
       for alt in expr.alternatives :
           if cnt > 1 :
              cond = self.conditionFromAlternative (grammar, alt.entry_result, alt, test = True)
              if start :
                 self.put ("if")
              else :
                 self.putEol ()
                 self.put ("else if")
              start = False
              self.put (" " + cond + " then")
              self.putLn (" begin")
              self.incIndent ()
           self.testFromAlternative (grammar, alt, cnt > 1 or reduced)
           if cnt > 1 :
              self.decIndent ()
              self.put ("end")
       if cnt > 1 :
          self.putEol ()
          self.putLn ("else begin")
          self.incIndent ()
          self.putLn ("result := false;")
          self.decIndent ()
          self.put ("end")
       self.putLn (";")

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
          self.put ("if")
       elif ebnf.mark == '*' :
          self.put ("while")
       elif ebnf.mark == '+' :
          self.put ("while")

       if ebnf.mark != "" :
          cond = self.conditionFromExpression (grammar, ebnf.current_result, ebnf.expr, test = True)
          self.put (" " + cond + " ")
          if ebnf.mark == '?' :
             self.put ("then")
          else :
             self.put ("do")
          self.putLn (" begin")
          self.incIndent ()

       self.testFromExpression (grammar, ebnf.expr, ebnf.mark != "")

       if ebnf.mark != "" :
          self.decIndent ()
          self.putLn ("end;")

   def testFromNonterminal (self, grammar, item) :
       self.registerPredicateNonterminal (grammar, item)
       self.putLn ("if not test_" + item.rule_name + " then begin")
       self.incIndent ()
       self.putLn ("result := false;")
       self.decIndent ()
       self.putLn ("end;")

   def testFromTerminal (self, grammar, item, reduced) :
       if not reduced :
          symbol = item.symbol_ref
          self.put ("if ")
          if symbol.ident != "" and (symbol.multiterminal or not self.use_strings or symbol.text == "") :
             self.put ("token <> " + symbol.ident)
          elif symbol.text != "" :
             self.put ("tokenText <> " + "'" + symbol.text + "'")
          else :
             self.put ("check (" + str (symbol.inx) + ")")
          self.putLn (" then begin")
          self.incIndent ()
          self.putLn ("result := false;")
          self.decIndent ()
          self.putLn ("end;")

       self.putLn ("nextToken;")

   # -----------------------------------------------------------------------

   def parserFromRules (self, grammar) :
       for rule in grammar.rules :
           self.parserFromRule (grammar, rule)

   def headerFromRule (self, grammar, rule, impl) :
       params = ""
       if rule.rule_mode == "modify" :
          params = "param : " + rule.rule_type
       if rule.store_name != "" :
          if params != "" :
             params = params + ", "
          params = params + "store : " + rule.store_type

       self.put ("function ");
       if impl :
          self.put (self.class_name + ".");
       self.put ("parse_" + rule.name);
       if params != "" :
          self.put (" (" + params + ")")
       self.put (" : " + rule.rule_type)
       self.putLn (";")

   def parserFromRule (self, grammar, rule) :
       grammar.updatePosition (rule)
       self.headerFromRule (grammar, rule, True)

       for sel_alt in rule.expr.alternatives :
           if sel_alt.select_independent :
              inx = str (sel_alt.new_inx)
              self.putLn ("var result" + inx + " : " + sel_alt.select_nonterm.current_type + ";")
           for cnt_alt in sel_alt.select_branches :
               if cnt_alt.continue_new != None :
                  inx = str (cnt_alt.new_inx)
                  self.putLn ("var store" + inx + ": " + rule.rule_type + ";")
                  self.putLn ("var result0" + ": " + cnt_alt.continue_new.new_type + ";")

       self.putLn ("begin")
       self.incIndent ()

       if rule.rule_mode == "modify" :
          self.putLn ("result := param;")
          if grammar.show_tree :
             self.putLn ("if monitor <> nil then monitor.reopenObject (result);")

       if  rule.rule_mode != "new" and rule.rule_mode != "modify" :
          self.putLn ("result := nil;")
       if rule.rule_mode == "new" :
          self.putLn ("result := " + rule.rule_type + ".create;")
          if rule.tag_name != "" :
             self.putLn ("result." + rule.tag_name + " := " + rule.tag_value + ";")
             type = grammar.struct_dict [rule.rule_type]
             if rule.tag_name != type.tag_name or rule.tag_value != type.tag_value :
                grammar.error ("Internal tag mismatch")

          self.putLn ("storeLocation (result);")
          if grammar.show_tree :
             self.putLn ("if monitor != nil then monitor.openObject (result);")

       if rule.store_name != "" :
          self.putLn ("result." + rule.store_name + " := store;")

       self.executeMethod (grammar, grammar.execute_on_begin, rule.name)
       self.executeMethod (grammar, grammar.execute_on_begin_no_param, rule.name, no_param = True)

       self.parserFromExpression (grammar, rule, rule.expr)

       self.executeMethod (grammar, grammar.execute_on_end, rule.name)

       if rule.rule_mode == "new" or rule.rule_mode == "modify" :
          if grammar.show_tree :
             self.putLn ("if monitor != nil then monitor.closeObject;")

       self.putLn ("result := result;")
       self.decIndent ()
       self.putLn ("end;")
       self.putEol ()

   def parserFromExpression (self, grammar, rule, expr) :
       cnt = len (expr.alternatives)
       start = True
       stop = False
       for alt in expr.alternatives :
           if cnt > 1 :
              if stop :
                 grammar.warning ("Cannot construct alternative condition")
              cond = self.conditionFromAlternative (grammar, alt.entry_result, alt)
              if cond == "True" or cond == "":
                 stop = True
              if start :
                 self.put ("if " + cond + " then")
              elif stop:
                 self.putEol ()
                 self.put ("else")
              else :
                 self.putEol ()
                 self.put ("else if " + cond + " then")
              start = False
              self.putLn (" begin")
              self.incIndent ()
           self.parserFromAlternative (grammar, rule, alt)
           if cnt > 1 :
              self.decIndent ()
              self.put ("end")
       if cnt > 1 and not stop:
          self.putEol ()
          self.putLn ("else begin")
          self.incIndent ()
          self.putLn ("stop ();")
          self.decIndent ()
          self.put ("end")
       if cnt > 1 :
          self.putLn (";")
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
                    self.putLn ("if " + func_name + " (result) then begin")
                    self.incIndent ()
                    opened_if = True
              self.parserFromEbnf (grammar, rule, item)
           elif isinstance (item, Assign) :
              value = item.value
              if value == "True" :
                 value = "true"
              elif value == "False" :
                 value = "false"
              self.putLn (item.current_result + "." + item.variable + " := " + value + ";")
           elif isinstance (item, Execute) :
              if item.no_param :
                 self.putLn (item.name + ";")
              else :
                 self.putLn (item.name + " (" + item.current_result + ");")
           elif isinstance (item, New) :
              # self.putLn ("var store: " + rule.rule_type + ";")
              # self.putLn ("var result1: " + item.new_type + ";")
              inx = str (alt.new_inx)
              self.putLn ("store" + inx + " := result;")
              self.putLn (item.current_result + " := " + item.new_type + ".create;")
              self.putLn ("storeLocation (" + item.current_result + ");")
              self.putLn (item.current_result + "."  + item.store_name + " := store" + inx + ";")
              self.putLn ("result := " + item.current_result + ";")
              if grammar.show_tree :
                 self.putLn ("if monitor != nil then monitor.openObject (result1);")
                 opened_branch = True
           elif isinstance (item, Style) :
              pass
           else :
              grammar.error ("Unknown alternative item: " + item.__class__.__name__)
       if opened_branch :
          self.putLn ("if monitor != nil then monitor.closeObject;")
       if opened_if :
           self.decIndent ()
           self.putLn ("end;")

   def parserFromEbnf (self, grammar, rule, ebnf) :
       if ebnf.mark == '?' :
          self.put ("if")
       elif ebnf.mark == '*' :
          self.put ("while")
       elif ebnf.mark == '+' :
          self.put ("while")

       if ebnf.mark != "" :
          cond = self.conditionFromExpression (grammar, ebnf.current_result, ebnf.expr)
          self.put (" " + cond + " ")
          if ebnf.mark == '?' :
             self.put ("then")
          else :
             self.put ("do")
          self.putLn (" begin")
          self.incIndent ()

       self.parserFromExpression (grammar, rule, ebnf.expr)

       if ebnf.mark != "" :
          self.decIndent ()
          self.putLn ("end;")

   def parserFromNonterminal (self, grammar, rule, item) :
       if item.select_item :
          self.executeMethod (grammar, grammar.execute_on_entry_no_param, rule.name, no_param = True)

       if item.select_item :
          "declare result0 variable for select item"
          # if item.item_link.select_independent :
          #    self.putLn ("var result0: " + item.current_type + ";") # declare new result0 variable

       if item.add :
          self.putLn ("setLength (" + item.current_result + ".items, length (" + item.current_result + ".items) + 1); ")
          self.put (item.current_result + ".items [ high (" + item.current_result + ".items)] := ")
       if item.select_item or item.continue_item or item.return_item :
          self.put (item.current_result + " := ")
       if item.variable != ""  :
          self.put (item.current_result + "." + item.variable + " := ")

       self.put ("parse_" + item.rule_name)

       params = ""
       if item.modify or item.rule_ref.rule_mode == "modify" :
          params = item.current_result
       if item.rule_ref.store_name != "" :
          "set params before result 0 is reverted to result"
          if item.store_result != "" :
             params = item.store_result
          else :
             params = item.current_result

       self.put (" (")
       if params != "" :
          self.put (params)
       self.put (")")

       self.putLn (";")

       if item.select_item :
          self.executeMethod (grammar, grammar.execute_on_fork_no_param, rule.name, no_param = True)

   def parserFromTerminal (self, grammar, rule, item) :
       symbol = item.symbol_ref
       if symbol.multiterminal :
          if item.variable != "" :
             self.put (item.current_result+ "." + item.variable + " := ")

          name = symbol.ident
          if name == "identifier" :
             func = "readIdent"
          elif name == "number" :
             func = "readNumber"
          elif name == "real_number" :
             func = "readNumber"
          elif name == "character_literal" :
             func = "readChar"
          elif name == "string_literal" :
             func = "readString"
          else :
             func = "unknown"

          self.putLn (func + ";")
       else :
          if symbol.ident != "" and not (self.use_strings and symbol.text != "") :
             self.putLn ("checkSymbol (" + symbol.ident + ");")
          else :
             self.putLn ("check (" + "'" + symbol.text + "'" + ");")

   # -----------------------------------------------------------------------

   def __init__ (self) :
       super (PasParser, self).__init__ ()
       self.lexer_header = "Lexer"
       self.parser_header = "Parser"
       self.lexer_name = "Lexer"
       self.symbol_name = "Symbol"
       self.base_name = "Basic"
       self.class_name = "Parser"

   # -----------------------------------------------------------------------

   def add_conv (self, grammar, type) :
       if type.super_type != None :
          target = type
          while target.super_type != None :
             target = target.super_type
          target.conv_list.append (type.type_name)

   def parserClass (self, grammar) :
       self.putLn (self.class_name + " = class (" + self.lexer_name + ")")
       self.putLn ("public")
       self.incIndent ()

       self.putLn ("constructor create;")
       self.style_empty_line ()

       for rule in grammar.rules :
          self.headerFromRule (grammar, rule, False)
       self.style_empty_line ()

       self.decIndent ()
       self.putLn ("public")
       self.incIndent ()

       self.putLn ("token: " + self.symbol_name + ";")
       self.putLn ("")

       self.putLn ("procedure lookupKeyword;")
       self.putLn ("procedure processSeparator;")
       self.putLn ("function tokenToString (value :" + self.symbol_name + ") : string;")

       self.style_empty_line ()
       self.putLn ("function isSymbol (sym : " + self.symbol_name + ") : boolean; inline;")
       self.putLn ("procedure checkSymbol (sym : " + self.symbol_name + "); inline;")
       self.putLn ("function testSymbols (table : array of byte) : boolean; inline;")
       self.putLn ("procedure stop;")

       self.style_empty_line ()
       self.putLn ("procedure translate;")
       self.putLn ("procedure storeLocation (item : " + self.base_name + ");")

       self.declareMethods (grammar, False)

       inx = 1
       for expr in grammar.predicates :
           self.putLn ("function test_" + str (inx) + " : boolean;")
           inx = inx + 1
       for rule in grammar.test_list :
           self.putLn ("function test_" + rule.name + " : boolean;")

       self.style_no_empty_line ()
       self.decIndent () # end of class
       self.putLn ("end;")
       self.putLn ()

   # -----------------------------------------------------------------------

   def basicClass (self, grammar) :
       self.putLn (self.base_name + " = class")
       self.putLn ("public")
       self.incIndent ()

       # self.putLn ("src_file : integer;")
       self.putLn ("src_line : integer;")
       self.putLn ("src_col : integer;")

       # self.putLn ("constructor create;")
       # self.style_empty_line ()

       self.decIndent () # end of class
       self.putLn ("end;")
       self.putLn ()

   # -----------------------------------------------------------------------

   def parserPascal (self, grammar) :

       self.putLn ("unit " + self.parser_header + ";")
       self.style_empty_line ()

       self.putLn ("interface")
       self.style_empty_line ()

       self.putLn ("uses " + self.lexer_header + ";")
       self.style_empty_line ()

       self.putLn ("type")
       self.incIndent ()

       initSymbols (grammar)
       self.declareSymbols (grammar)
       self.declareEnumTypes (grammar)

       self.putLn (self.base_name + " = class;")
       for type in grammar.struct_list :
           self.putLn (type.type_name + " = class;")
       self.putLn ()

       self.parserClass (grammar)
       self.basicClass (grammar)
       self.declareTypes (grammar)
       self.decIndent () # end of type section

       self.style_empty_line ();
       self.putLn ("implementation")
       self.style_empty_line ();

       self.declareCollections (grammar)

       self.parserFromRules (grammar)

       self.declarePredicates (grammar)

       self.selectKeywords (grammar)
       self.selectSeparators (grammar)
       self.convertTerminals (grammar)
       self.declareTranslate ()
       self.declareStoreLocation (grammar)

       # constructor
       self.putLn ("constructor " + self.class_name + ".create;")
       self.putLn ("begin")
       self.incIndent ()
       self.putLn ("inherited create (nil);")
       # if grammar.show_tree :
       #    self.putLn ("monitor := nil;")
       self.decIndent ()
       self.putLn ("end;")
       self.putLn ()

       self.declareIsSymbol ();
       self.declareMethods (grammar, True)
       self.style_empty_line ()

       for type in grammar.struct_list :
           self.add_conv (grammar, type)
       self.implementTypes (grammar)

       self.style_empty_line ()
       self.putLn ("end.") # end of unit

# --------------------------------------------------------------------------

if __name__ == "__main__" :
   import optparse

   options = optparse.OptionParser (usage = "usage: %prog [options] input_grammar_file")
   options.add_option ("--code", dest="code", default = "", action="store", help="Output file name")

   (opts, args) = options.parse_args ()

   if len (args) == 0 :
      options.error ("Missing input file name")
   if len (args) > 1 :
      options.error ("Too many input file names")

   inputFileName = args [0]
   outputFileName = opts.code

   grammar = Grammar ()
   grammar.openFile (inputFileName)
   grammar.parseRules ()
   grammar.close ()

   builder = PasParser ()
   builder.lexer_header = "textio"
   builder.parser_header = "pas_parser"
   builder.lexer_name = "TTextInput"
   builder.base_name = "TItem"

   builder.open (outputFileName)
   builder.parserPascal (grammar)
   builder.close ()

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
