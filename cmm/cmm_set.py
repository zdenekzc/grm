
# cmm_set.py

from __future__ import print_function

import os, shutil

from input import quoteString
from lexer import LexerInput
from output import Output
from code_base import SimpleType, NamedType

# DescriptionModule
from cmm_parser import *
from cmm_product import *
from cmm_comp import *
from c2cpp import *

__all__ = [
            "CodeModule",
            "PropertyTableModule", "PropertyTreeModule", "DialogModule",
            "JsonIO", "XmlIO", "TextIO", "FuncIO",
            "ColorButtonModule", "ToolButtonModule",
            "EditModule",
            "TreeModule", "TableModule",
            "TraceModule",
            "PluginModule"
          ]

# --------------------------------------------------------------------------

def getitem_func (self, name) :
    return self.item_dict [name]

def get_func (self, name) :
    return self.item_dict.get (name, None)

# def lookup_func (self, name) :
#     return self.lookup (name)

def rename_func (self, name) :
    self.mod_rename = name

def decl_func (self, method) :
    self.mod_decl = method

def call_func (self, method) :
    self.mod_call = method

# CmmCompiler.__getitem__ = lookup_func

CmmDecl.__getitem__ = getitem_func
CmmDecl.get = get_func

CmmStat.rename = rename_func
CmmStat.on_decl = decl_func
CmmStat.on_call = call_func

# --------------------------------------------------------------------------

class ProgramBuildingSet (object) :

   def __init__ (self, compiler) :
       super (ProgramBuildingSet, self).__init__ ()
       self.compiler = compiler

   def get (self, name) :
       "get module parameter"
       return getattr (self, name, "")

   def find (self, obj, name) :
       "find identifier in namespace or class"
       return obj.item_dict [name]

   def rename (self, obj, name) :
       obj.mod_rename = name

   def assignValue (self, obj, value) :
       obj.mod_rename = value

   def callFunction (self, obj, func) :
       obj.mod_call = func

   # -----------------------------------------------------------------------

   def readSource (self, fileName, target = None) :
       compiler = self.compiler

       if target == None :
          target = compiler.global_scope

       # save_extensions = compiler.extension_classes
       # compiler.extension_classes = { }
       compiler.openNestedFile (fileName)
       # compiler.info ("AFTER OPEN, token = " + compiler.tokenToText () + " ... " + str (compiler.token))
       while not compiler.isEndOfSource () :
           decl = compiler.parse_declaration ()
           target.items.append (decl)
       compiler.closeNested ()
       # compiler.extension_classes = save_extensions

   # -----------------------------------------------------------------------

   def readSourceFiles (self, * args) :
       compiler = self.compiler

       save_macros = compiler.macros
       compiler.addMacro ("Q_OBJECT", "")
       compiler.addMacro ("slots", "")
       compiler.addMacro ("override", "")

       save_ignore_incl = compiler.ignore_all_includes
       compiler.ignore_all_includes = True

       ext_source = len (args) == 1 and args [0].endswith (".t")

       module_name = args [0]
       module_name = os.path.basename (module_name)
       module_name = os.path.splitext (module_name) [0]
       module_name = module_name.replace ("-", "_")
       module_name = module_name.replace (".", "_")

       block = compiler.createExtensionStat ()
       block.name = "nested_module"
       block.param = module_name
       block.ext_source = ext_source
       block.items = [ ]
       compiler.global_scope.items.append (block)
       print ("MODULE", module_name)

       for arg in args :
           print ("READ", arg)
           self.readSource (arg, block)

           file_name = os.path.basename (arg)
           if ext_source :
              file_name = module_name + ".cpp"

           stat = compiler.createExtensionStat ()
           stat.name = "nested_file"
           stat.param = file_name
           stat.items = [ ]
           compiler.global_scope.items.append (stat)

           if not ext_source :
              if compiler.win != None :
                 outFileName = compiler.win.outputFileName (os.path.basename (arg))
                 print ("WRITE", outFileName)
                 shutil.copyfile (arg, outFileName)

       compiler.ignore_all_includes = save_ignore_incl
       compiler.macros = save_macros

   def readRecipe (self, fileName) :
       compiler = self.compiler

       recipe = Namespace ()
       recipe.items = [ ]
       initNamespace (recipe)

       recipe.item_name = "_recipe_namespace_" # !?

       compiler.openScope (recipe)
       self.readSource (fileName)
       compiler.closeScope ()

       dcl_ns = recipe ["plastic"]
       dcl_ns.skip_code = True
       dcl_ns.hidden_scope = True

       io_ns = recipe ["building"]
       io_ns.skip_code = True
       io_ns.hidden_scope = True

       code_ns = recipe ["set"]
       code_ns.skip_code = True
       code_ns.hidden_scope = True

       return recipe

   def writeRecipe (self, items) :
       product = ToCpp ()
       product.python = False
       product.openString ()
       for item in items :
           product.send_stat (item)
       code = product.closeString ()
       # print ("CODE", code)

       compiler = self.compiler
       compiler.openNestedString (code)
       while not compiler.isEndOfSource () :
           decl = compiler.parse_declaration ()
           compiler.global_scope.items.append (decl)
       compiler.closeNested ()

   # -----------------------------------------------------------------------

   def get_param (self, call_expr, name) :
       func = call_expr.left.item_decl
       # print ("GET PARAM", func.item_qual, name)
       inx = -1
       k = 0
       for param in func.item_list :
           if param.item_name == name :
              inx = k
              # print ("PARAM", inx, param.item_qual)
           k = k + 1

       if inx < 0 :
          self.compiler.error ("Unknown parameter " + name + " in " + func.iten_qual)

       value = None
       if inx >= 0 :
          if inx < len (call_expr.param_list.items) :
              value = call_expr.param_list.items [inx]
          else :
              value = "!? OUT OF RANGE"

          # if value.kind == simpleName :
          #   value = value.id
          value = self.compiler.get_name (value)
          # print ("VALUE", value)
       return value

   def code_func (self, output, iocls, iofunc, params = [ ]) :
       func = iocls.item_dict [iofunc]
       # NO output.style_new_line ()
       # output.send ("// CODE_FUNC (" + func.item_qual + ");")

       inx = 0
       for p in func.item_list :
           if inx < len (params) :
              p.mod_rename = params [inx]
              inx = inx + 1
              # output.send (p.item_name + " ... " + p.mod_rename)
              # output.style_new_line ()

       body = func.item_body
       if len (body.items) == 1 :
          output.send_stat (body.items [0])
       else :
          output.send_stat (body)
       output.style_new_line ()

   # -----------------------------------------------------------------------

   def setup_mark (self, field) :
       mark = ""
       t = field.item_type
       if isinstance (t, SimpleType) :
          if t.type_bool :
             mark = "bool"
          if t.type_int :
             if t.type_unsigned :
                mark = "uint"
             else :
                mark = "int"
          if t.type_long :
             if t.type_unsigned :
                mark = "ulong"
             else :
                mark = "long"
          if t.type_float :
             mark = "float"
          if t.type_double :
             mark = "double"
       elif isinstance (t, NamedType) :
          if t.type_label == "string" :
             mark = "string"
          if t.type_label == "QString" :
             mark = "QString"
          if t.type_label == "QStringList" :
             mark = "QStringList"
          if t.type_label == "QColor" :
              mark = "QColor"
          if t.type_label == "QFont" :
              mark = "QFont"
          if t.type_label == "FileName" : # !?
              mark = "FileName"
          # if t.type_label == "QList" :
          #   mark = "QList"
          # if isinstance (t.type_decl, Enum) :
          #    mark = "enum"
       field.mark = mark

       # if field.mark == "QList" :
       #    field.list_arg = None
       #    if t.type_args != None and len (t.type_args) == 1 :
       #       a = t.type_args [0]
       #       if isinstance (a, PointerType) :
       #          a = a.type_from
       #       if isinstance (a, NamedType) :
       #          field.list_arg = a.type_label


   def all_items (self, cls) :
       items = cls.item_list
       if cls.base_list != None :
           for base in cls.base_list.items :
               base_cls = base.from_cls.item_decl
               if base_cls != None :
                  items = items + self.all_items (base_cls)
       return items

   def setup_cls (self, cls, ns, iocls_field = "iocls") :
       fields = [ ]

       for field in self.all_items (cls) :
           self.setup_mark (field)
           iocls = None

           if field.mark == "bool" :
              iocls = ns.item_dict.get ("BoolIO", None)
           if field.mark == "int" :
              iocls = ns.item_dict.get ("IntIO", None)
           if field.mark == "double" :
              iocls = ns.item_dict.get ("DoubleIO", None)
           if field.mark == "QString" :
              iocls = ns.item_dict.get ("StringIO", None)
           if field.mark == "QStringList" :
              iocls = ns.item_dict.get ("StringListIO", None)
           if field.mark == "QColor" :
              iocls = ns.item_dict.get ("ColorIO", None)
           if field.mark == "QFont" :
              iocls = ns.item_dict.get ("FontIO", None)
           if field.mark == "FileName" :
              iocls = ns.item_dict.get ("FileNameIO", None)

           # field.iocls = iocls
           setattr (field, iocls_field, iocls)
           if iocls != None :
              fields.append (field)

       cls.fields = fields
       return fields

   def setup_dlg (self, cls, ns) :
       fields = [ ]

       for field in self.all_items (cls) :
           self.setup_mark (field)
           iocls = None

           if field.mark == "QString" :
              iocls = ns.item_dict.get ("LineEditIO", None)
           if field.mark == "bool" :
              iocls = ns.item_dict.get ("CheckBoxIO", None)
           if field.mark == "int" :
              iocls = ns.item_dict.get ("SpinBoxIO", None)
           if field.mark == "double" :
              iocls = ns.item_dict.get ("DoubleSpinBoxIO", None)
           # if field.mark == "double" :
           #    iocls = ns.item_dict.get ("DoubleIO", None)

           field.iocls = iocls
           if iocls != None :
              fields.append (field)

       cls.fields = fields
       return fields

# --------------------------------------------------------------------------

"""
class DeclOutput (Output) :
   def __init__ (self, decl) :
       super (DeclOutput, self).__init__ ()
       self.decl = decl
       self.openString ()

   def close (self) :
       pass
       #text = self.closeString ()
       #for line in text.split ("\n") :
           #print ("LINE:", line)
           #stat = CmmOutputStat ()
           #stat.name = "put"
           #stat.text = line
           #self.decl.items.append (stat)

   def cmd (self, name, text = None) :
       stat = CmmExtensionStat ()
       stat.name = name
       stat.param = text
       self.decl.items.append (stat)

   # put

   def indent (self) :
       self.cmd ("indent")

   def unindent (self) :
       self.cmd ("unindent")

   def put (self, txt) :
       self.cmd ("put", txt)

   def putEol (self) :
       self.cmd ("putEol", txt)

   def putLn (self, txt = "") :
       if txt != "":
          self.cmd (txt)
       self.putEol ()

   def send (self, txt) :
       self.cmd ("send", txt)

   def style_no_space (self) :
       self.cmd ("style_no_space")

   def style_new_line (self) :
       self.cmd ("style_new_line")

   def style_empty_line (self) :
       self.cmd ("style_empty_line")

   def style_no_empty_line (self) :
       self.cmd ("style_no_empty_line")
"""

# --------------------------------------------------------------------------

class CodeModule (ProgramBuildingSet) :
   def __init__ (self, compiler) :
       super (CodeModule, self).__init__ (compiler)

   def compile (self) :
       compiler = self.compiler
       fileName = self.get ("code")
       self.readSourceFiles (fileName)

# --------------------------------------------------------------------------

class PropertyTableModule (ProgramBuildingSet) :
   def __init__ (self, compiler) :
       super (PropertyTableModule, self).__init__ (compiler)

   def compile (self) :
       compiler = self.compiler
       self.readSourceFiles ("set/prop-table.h", "set/prop-table.cc")
       recipe = self.readRecipe ("set/prop-table.t")

       # parameters from DialogModule { ... }
       record_param = self.get ("Record")
       properties_param = self.get ("Properties")

       # find Record class in your code
       cls = compiler.lookup (record_param)

       # plastic namespace - source of hidden declarations
       decl_ns = recipe ["plastic"]

       # find and rename Record class
       r = decl_ns ["Record"]
       r.rename (record_param)

       # building namespace - IO classes with display and store methods
       io_ns = recipe ["building"]

       self.fields = self.setup_cls (cls, io_ns)

       # set namespace - common code
       code_ns = recipe ["set"]

       # find and rename class for whole dialog
       d = code_ns ["Properties"]
       d.rename (properties_param)
       d.on_decl (self.on_decl) # during class declaration call on_decl
       d ["init"].on_decl (self.on_init)  # instead of init method call on_init
       d ["display"].on_decl (self.on_display)
       d ["store"].on_decl (self.on_store)

       self.writeRecipe (code_ns.members.items)

   def on_decl (self, output, cls) :
       for field in self.fields :
           name = field.item_name
           node = name + "_node";
           output.send ("QTableWidgetItem");
           output.send ("*")
           output.send (node)
           output.send (";")
           output.style_new_line ()

   def on_init (self, output, func) :
       for field in self.fields :
           name = field.item_name
           node = name + "_node";
           output.send (node)
           output.send ("=")
           output.send ("this") # !? Python converter
           output.send ("->")
           output.send ("addTableLine")
           output.send ("(")
           output.send (quoteString (name));
           output.send (")")
           output.send (";")
           output.style_new_line ()

   def on_display (self, output, func) :
       data = "data"
       for field in self.fields :
           name = field.item_name
           node = name + "_node";
           self.code_func (output, field.iocls, "display", [ node, data + "->" + name ])

   def on_store (self, output, func) :
       data = "data"
       for field in self.fields :
           name = field.item_name
           node = name + "_node";
           self.code_func (output, field.iocls, "store", [ node, data + "->" + name ])

# --------------------------------------------------------------------------

class PropertyTreeModule (ProgramBuildingSet) :
   def __init__ (self, compiler) :
       super (PropertyTreeModule, self).__init__ (compiler)

   def compile (self) :
       compiler = self.compiler
       recipe = self.readSourceFiles ("set/prop-tree.h", "set/prop-tree.cc")
       recipe = self.readRecipe ("set/prop-tree.t")

       # parameters from DialogModule { ... }
       record_param = self.get ("Record")
       properties_param = self.get ("Properties")

       # find Record class in your code
       cls = compiler.lookup (record_param)

       # plastic namespace - source of hidden declarations
       decl_ns = recipe ["plastic"]

       # find and rename Record class
       r = decl_ns ["Record"]
       r.rename (record_param)

       # building namespace - IO classes with display and store methods
       io_ns = recipe ["building"]

       self.fields = self.setup_cls (cls, io_ns)

       # set namespace - common code
       code_ns = recipe ["set"]

       # find and rename class for whole dialog
       d = code_ns ["Properties"]
       d.rename (properties_param)
       d.on_decl (self.on_decl) # during class declaration call on_decl
       d ["init"].on_decl (self.on_init)  # instead of init method call on_init
       d ["display"].on_decl (self.on_display)
       d ["store"].on_decl (self.on_store)

       self.writeRecipe (code_ns.members.items)

   def on_decl (self, output, cls) :
       for field in self.fields :
           name = field.item_name
           node = name + "_node";
           output.send ("QTreeWidgetItem");
           output.send ("*")
           output.send (node)
           output.send (";")
           output.style_new_line ()

   def on_init (self, output, func) :
       print ("ON INIT")
       for field in self.fields :
           name = field.item_name
           node = name + "_node";
           print ("INIT", node)
           output.send (node)
           output.send ("=")
           output.send ("this") # !? Python converter
           output.send ("->")
           output.send ("addTreeItem")
           output.send ("(")
           output.send (quoteString (name));
           output.send (")")
           output.send (";")
           output.style_new_line ()

   def on_display (self, output, func) :
       data = "data"
       for field in self.fields :
           name = field.item_name
           node = name + "_node";
           self.code_func (output, field.iocls, "display", [ node, data + "->" + name ])

   def on_store (self, output, func) :
       data = "data"
       for field in self.fields :
           name = field.item_name
           node = name + "_node";
           self.code_func (output, field.iocls, "store", [ node, data + "->" + name ])

# --------------------------------------------------------------------------

class TreeModule (ProgramBuildingSet) :
   def __init__ (self, compiler) :
       super (TreeModule, self).__init__ (compiler)

   def compile (self) :
       compiler = self.compiler
       self.readSource ("set/tree-model.t")

       record_param = self.get ("Record")
       name_param   = self.get ("name")
       above_param  = self.get ("above")
       items_param  = self.get ("items")
       root_param   = self.get ("root")

       r = compiler.lookup ("Record")
       r.skip_code = True # do not write Record declaration, actual class is already declared

       self.rename (r, record_param) # rename class Record
       self.rename (self.find (r, "name"), name_param) # rename field Record.name
       self.rename (self.find (r, "above"), above_param)
       self.rename (self.find (r, "items"), items_param)

       t = compiler.lookup ("TreeModel")
       self.rename (self.find (t, "rootItem"), root_param) # rename TreeModel.rootItem

# --------------------------------------------------------------------------

class JsonIO (ProgramBuildingSet) :
   def __init__ (self, compiler) :
       super (JsonIO, self).__init__ (compiler)

   def compile (self) :
       compiler = self.compiler
       self.readSource ("set/json.t")

       # parameters from JsonIO
       record_param = self.get ("Record")
       collection_param = self.get ("Collection")
       items_param = self.get ("items")

       cls = compiler.lookup (record_param)
       lst = compiler.lookup (collection_param)

       dcl_ns = compiler.lookup ("plastic")
       dcl_ns.skip_code = True
       dcl_ns.hidden_scope = True

       r = self.find (dcl_ns, "Record")
       c = self.find (dcl_ns, "Collection")

       self.rename (r, record_param)
       self.rename (c, collection_param)
       self.rename (self.find (c, "items"), items_param) # rename Collection.items

       self.callFunction (self.find (dcl_ns, "READ"),  self.on_read)
       self.callFunction (self.find (dcl_ns, "WRITE"), self.on_write)

       io_ns = compiler.lookup ("building")
       io_ns.skip_code = True
       io_ns.hidden_scope = True

       self.fields = self.setup_cls (cls, io_ns)

       code_ns = compiler.lookup ("set")
       code_ns.hidden_scope = True

       self.rename (self.find (code_ns, "readRecord"), "read" + cls.item_name)
       self.rename (self.find (code_ns, "writeRecord"), "write" + cls.item_name)
       self.rename (self.find (code_ns, "readCollection"), "read" + lst.item_name)
       self.rename (self.find (code_ns, "writeCollection"), "write" + lst.item_name)

   def on_read (self, output, func) :
       "void READ (var data, QJsonObject obj);"
       data = self.get_param (func, "data")
       obj = self.get_param (func, "obj")

       if output.python :
          arrow = "."
       else :
          arrow = "->"

       for field in self.fields :
           "read (var n, QJsonObject obj, QString name)"
           name = field.item_name
           self.code_func (output, field.iocls, "read", [ data + arrow + name, obj, quoteString (name) ])

   def on_write (self, output, func) :
       "void WRITE (var data, QJsonObject obj);"
       obj = self.get_param (func, "obj")
       data = self.get_param (func, "data")

       if output.python :
          arrow = "."
       else :
          arrow = "->"

       for field in self.fields :
           "write (var n, QJsonObject obj, QString name)"
           name = field.item_name
           self.code_func (output, field.iocls, "write", [ data + arrow + name, obj, quoteString (name) ])

# --------------------------------------------------------------------------

class XmlIO (ProgramBuildingSet) :
   def __init__ (self, compiler) :
       super (XmlIO, self).__init__ (compiler)

   def compile (self) :

       compiler = self.compiler
       self.readSource ("set/xml.t")

       # parameters from JsonIO
       record_param = self.get ("Record")
       collection_param = self.get ("Collection")
       items_param = self.get ("items")

       cls = compiler.lookup (record_param)
       lst = compiler.lookup (collection_param)

       dcl_ns = compiler.lookup ("plastic")
       dcl_ns.skip_code = True
       dcl_ns.hidden_scope = True

       r = self.find (dcl_ns, "Record")
       c = self.find (dcl_ns, "Collection")

       self.rename (r, record_param)
       self.rename (c, collection_param)
       self.rename (self.find (c, "items"), items_param)

       self.assignValue (self.find (dcl_ns, "COLLECTION_NAME"), quoteString (lst.item_name))
       self.assignValue (self.find (dcl_ns, "RECORD_NAME"),     quoteString (cls.item_name))

       self.callFunction (self.find (dcl_ns, "READ"),  self.on_read)
       self.callFunction (self.find (dcl_ns, "WRITE"), self.on_write)

       io_ns = compiler.lookup ("building")
       io_ns.skip_code = True
       io_ns.hidden_scope = True

       self.fields = self.setup_cls (cls, io_ns)

       code_ns = compiler.lookup ("set")
       code_ns.hidden_scope = True

       self.rename (self.find (code_ns, "readRecord"), "read" + cls.item_name)
       self.rename (self.find (code_ns, "writeRecord"), "write" + cls.item_name)
       self.rename (self.find (code_ns, "readCollection"), "read" + lst.item_name)
       self.rename (self.find (code_ns, "writeCollection"), "write" + lst.item_name)

   def on_read (self, output, call_expr) :
       "void READ (QXmlStreamReader & reader, QXmlStreamAttributes & attr, var data);"
       reader = self.get_param (call_expr, "reader")
       attr = self.get_param (call_expr, "attr")
       data = self.get_param (call_expr, "data")

       if output.python :
          arrow = "."
       else :
          arrow = "->"

       inx = 0
       for field in self.fields :
           "read (var v, QXmlStreamAttributes & a, QString name)"
           if inx > 0 :
              if output.python :
                 output.put ("el") # !? if -> elif
              else :
                 output.put ("else ")
           name = field.item_name
           self.code_func (output, field.iocls, "read", [ data + arrow + name, attr, quoteString (name) ])
           inx = inx + 1

   def on_write (self, output, func) :
       "void WRITE (QXmlStreamWriter & writer, var data);"
       writer = self.get_param (func, "writer")
       data = self.get_param (func, "data")

       if output.python :
          arrow = "."
       else :
          arrow = "->"

       for field in self.fields :
           "write (var v, QXmlStreamWriter & w, QString name)"
           name = field.item_name
           self.code_func (output, field.iocls, "write", [ data + arrow + name, writer, quoteString (name) ])

# --------------------------------------------------------------------------

class TextIO (ProgramBuildingSet) :
   def __init__ (self, compiler) :
       super (TextIO, self).__init__ (compiler)

   def compile (self) :
       compiler = self.compiler
       self.readSource ("set/textio.t")

       # parameters from TextIO
       record_param = self.get ("Record")
       collection_param = self.get ("Collection")
       items_param = self.get ("items")

       cls = compiler.lookup (record_param)
       lst = compiler.lookup (collection_param)

       dcl_ns = compiler.lookup ("plastic")
       dcl_ns.skip_code = True
       dcl_ns.hidden_scope = True

       r = self.find (dcl_ns, "Record")
       c = self.find (dcl_ns, "Collection")

       self.rename (r, record_param)
       self.rename (c, collection_param)
       self.rename (self.find (c, "items"), items_param) # rename Collection.items

       self.callFunction (self.find (dcl_ns, "READ"),  self.on_read)
       self.callFunction (self.find (dcl_ns, "WRITE"), self.on_write)

       io_ns = compiler.lookup ("building")
       io_ns.skip_code = True
       io_ns.hidden_scope = True

       self.fields = self.setup_cls (cls, io_ns)

       code_ns = compiler.lookup ("set")
       code_ns.hidden_scope = True

       self.rename (self.find (code_ns, "readRecord"), "read" + cls.item_name)
       self.rename (self.find (code_ns, "writeRecord"), "write" + cls.item_name)
       self.rename (self.find (code_ns, "readCollection"), "read" + lst.item_name)
       self.rename (self.find (code_ns, "writeCollection"), "write" + lst.item_name)

   def on_read (self, output, func) :
       "void READ (var data);"
       data = self.get_param (func, "data")

       if output.python :
          arrow = "."
       else :
          arrow = "->"

       for field in self.fields :
           "read (var n, QJsonObject obj, QString name)"
           name = field.item_name
           self.code_func (output, field.iocls, "read", [ data + arrow + name, quoteString (name) ])

   def on_write (self, output, func) :
       "void WRITE (var data);"
       data = self.get_param (func, "data")

       if output.python :
          arrow = "."
       else :
          arrow = "->"

       for field in self.fields :
           "write (var n, QJsonObject obj, QString name)"
           name = field.item_name
           self.code_func (output, field.iocls, "write", [ data + arrow + name, quoteString (name) ])

# --------------------------------------------------------------------------

class FuncIO (ProgramBuildingSet) :
   def __init__ (self, compiler) :
       super (FuncIO, self).__init__ (compiler)

   def compile (self) :
       compiler = self.compiler
       recipe = self.readRecipe ("set/funcio.t")

       # parameters from FuncIO
       record_param = self.get ("Record")

       cls = compiler.lookup (record_param)

       dcl_ns = recipe ["plastic"]
       dcl_ns.skip_code = True
       dcl_ns.hidden_scope = True

       r = dcl_ns ["Record"]

       self.rename (r, record_param)

       io_ns = recipe ["building"]
       io_ns.skip_code = True
       io_ns.hidden_scope = True

       code_ns = recipe ["set"]
       code_ns.hidden_scope = True

       self.cls = cls
       self.io_ns = io_ns
       self.callFunction (dcl_ns ["CALL"], self.on_call)

       # self.writeRecipe (code_ns.members.items)

   def on_call (self, output, func_param) :
       cls = self.cls
       ns = self.io_ns

       for field in self.all_items (cls) :
           if field.is_function :
              func = field
              output.putLn ("if (isIdent (" + quoteString (func.item_name) + "))")
              output.putLn ("{")
              output.incIndent ()
              output.putLn ("nextToken ();");
              output.putLn ("checkSeparator (" + quoteString ("(") + ");");

              param_names = [ ]
              first = True

              for field in func.item_list :
                  if first :
                     first = False
                  else :
                     output.putLn ("checkSeparator (" + quoteString (",") + ");");

                  param_names.append (field.item_name)

                  self.setup_mark (field)

                  iofunc = None
                  if field.mark == "QString" :
                     iofunc = ns.item_dict.get ("stringParam", None)
                  if field.mark == "bool" :
                     iofunc = ns.item_dict.get ("boolParam", None)
                  if field.mark == "int" :
                     iofunc = ns.item_dict.get ("intParam", None)
                  if field.mark == "double" :
                     iofunc = ns.item_dict.get ("doubleParam", None)

                  self.code_func (output, ns, iofunc.item_name, [field.item_name])

              output.putLn ("checkSeparator (" + quoteString (")") + ");");
              output.putLn ("checkSeparator (" + quoteString (";") + ");");

              output.put ("data")
              output.put ("->")
              output.put (func.item_name)
              output.put ("(")
              first = True
              for param in param_names :
                 if first :
                    first = False
                 else :
                     output.put (",")
                 output.put (param)
              output.put (")")
              output.put (";")
              output.putEol ()
              output.decIndent ()
              output.putLn ("}")

# --------------------------------------------------------------------------

class TableModule (ProgramBuildingSet) :
   def __init__ (self, compiler) :
       super (TableModule, self).__init__ (compiler)

   def compile (self) :
       compiler = self.compiler
       self.readSource ("set/table-model.t")

       # parameters from TableModule
       record_param = self.get ("Record")
       collection_param = self.get ("Collection")
       items_param = self.get ("items")
       store_param = self.get ("store")

       # user class
       cls = compiler.lookup (record_param)

       dcl_ns = compiler.lookup ("plastic") # find namespace with auxiliary declaration
       dcl_ns.skip_code = True # do not write declarations from this namespace
       dcl_ns.hidden_scope = True # do not use namespace in qualified names

       r = self.find (dcl_ns, "Record")
       c = self.find (dcl_ns, "Collection")

       self.rename (r, record_param) # rename Record
       self.rename (c, collection_param) # rename Collection
       self.rename (self.find (c, "items"), items_param) # rename Collection.items

       io_ns = compiler.lookup ("building") # find namespace with specific classes for input / output
       io_ns.skip_code = True
       io_ns.hidden_scope = True

       fields = self.setup_cls (cls, io_ns, "table_iocls") # list of fields with io classes
       self.fields = fields

       code_ns = compiler.lookup ("set") # namespace with code
       code_ns.transparent_namespace = True # write namespace content without surrounding namespace declaration
       code_ns.hidden_scope = True

       tv = self.find (code_ns, "TableView")
       tm = self.find (code_ns, "TableModel")

       self.rename (self.find (tv, "store"), store_param) # rename TableView.store
       self.rename (self.find (tm, "store"), store_param) # rename TableModel.store

       # define COLUMN_COUNT as string, call python function to generate code for HEADER_DATA, ...
       self.assignValue  (self.find (dcl_ns, "COLUMN_COUNT"), str (len (fields)))
       self.callFunction (self.find (dcl_ns, "HEADER_DATA"),  self.on_header_data) # when HEADER_DATA is encountered, call on_header_data
       self.callFunction (self.find (dcl_ns, "RECALL_DATA"),  self.on_recall_data)
       self.callFunction (self.find (dcl_ns, "STORE_DATA"),   self.on_store_data)

   def put_if (self, output, inx, column) :
       if output.python :
          if inx > 0 :
              output.put ("elif ")
          else :
              output.put ("if ")
          output.putLn (column + " == " + str (inx) + " :")
       else :
          if inx > 0 :
              output.put ("else ")
          output.putLn ("if (" + column + " == " + str (inx) + ")")

   def on_header_data (self, output, func) :
       result = self.get_param (func, "result")
       column = self.get_param (func, "column")

       if output.python :
          semicolon = ""
       else :
          semicolon = ";"

       inx = 0
       for field in self.fields :
           self.put_if (output, inx, column)
           output.indent ()
           output.putLn (result + " = " + quoteString (field.item_name) + semicolon)
           output.unindent ()
           inx = inx + 1

   def on_recall_data (self, output, func) :
       # actual values for RECALL_DATA (result, item, column) parameters
       result = self.get_param (func, "result")
       item = self.get_param (func, "item")
       column = self.get_param (func, "column")

       if output.python :
          arrow = "."
       else :
          arrow = "->"

       inx = 0
       for field in self.fields :
           self.put_if (output, inx, column)
           output.indent ()
           # call recall_data from field.iocls class with two parameteres  (result, item->field_name)
           self.code_func (output, field.table_iocls, "recall_data", [result, item + arrow + field.item_name])
           output.unindent ()
           inx = inx + 1

   def on_store_data (self, output, func) :
       item = self.get_param (func, "item")
       column = self.get_param (func, "column")
       value = self.get_param (func, "value")

       if output.python :
          arrow = "."
       else :
          arrow = "->"

       inx = 0
       for field in self.fields :
           self.put_if (output, inx, column)
           output.indent ()
           self.code_func (output, field.table_iocls, "store_data", [item + arrow + field.item_name, value])
           output.unindent ()
           inx = inx + 1

# --------------------------------------------------------------------------

class DialogModule (ProgramBuildingSet) :
   def __init__ (self, compiler) :
       super (DialogModule, self).__init__ (compiler)

   def compile (self) :
       compiler = self.compiler
       recipe = self.readRecipe ("set/dialog.t")

       # parameters from DialogModule { ... }
       record_param = self.get ("Record")
       dialog_param = self.get ("Dialog")

       # find Record class in your code
       cls = compiler.lookup (record_param)

       # plastic namespace - source of hidden declarations
       dcl_ns = recipe ["plastic"]
       dcl_ns.skip_code = True
       dcl_ns.hidden_scope = True

       # find and rename Record class
       r = dcl_ns ["Record"]
       r.rename (record_param)

       # building namespace - IO classes with display and store methods
       io_ns = recipe ["building"]
       io_ns.skip_code = True
       io_ns.hidden_scope = True

       self.io_ns = io_ns
       self.fields = self.setup_dlg (cls, io_ns)

       # set namespace - common code
       code_ns = recipe ["set"]
       code_ns.skip_code = True
       code_ns.hidden_scope = True

       # find and rename Dialog class
       d = code_ns ["Dialog"]
       d.rename (dialog_param)
       d.on_decl (self.on_decl) # during class declaration call on_decl
       d ["init"].on_decl (self.on_init)  # instead of init method call on_init
       d ["display"].on_decl (self.on_display)
       d ["store"].on_decl (self.on_store)

       self.writeRecipe (code_ns.members.items)

   def on_decl (self, output, cls) :
       for field in self.fields :
           for item in field.iocls.item_list :
               if hasattr (item, "is_function") :
                  if not item.is_function :
                     output.send_expr (item.item_simple_decl.type_spec)
                     output.send_simple_item (item)
                     output.send (";")
                     output.style_new_line ()

   def on_init (self, output, func) :
       data = "data"
       for field in self.fields :
           self.code_func (output, field.iocls, "init")
           name = field.item_name
           widget_id = field.iocls.item_list[0].item_name # !? first declared identifier
           self.code_func (output, self.io_ns, "addItem", ["layout", quoteString (name), widget_id])
           output.style_empty_line ()

   def on_display (self, output, func) :
       data = "data"
       for field in self.fields :
           name = field.item_name
           self.code_func (output, field.iocls, "display", [ data + "->" + name ])

   def on_store (self, output, func) :
       data = "data"
       for field in self.fields :
           name = field.item_name
           self.code_func (output, field.iocls, "store", [ data + "->" + name ])


# --------------------------------------------------------------------------

class ColorButtonModule (ProgramBuildingSet) :
   def __init__ (self, compiler) :
       super (ColorButtonModule, self).__init__ (compiler)

   def compile (self) :
       self.readSourceFiles ("set/color-button.h", "set/color-button.cc")

# --------------------------------------------------------------------------

class ToolButtonModule (ProgramBuildingSet) :
   def __init__ (self, compiler) :
       super (ToolButtonModule, self).__init__ (compiler)

   def compile (self) :
       self.readSourceFiles ("set/tool-button.h", "set/tool-button.cc")

# --------------------------------------------------------------------------

class EditModule (ProgramBuildingSet) :
   def __init__ (self, compiler) :
       super (EditModule, self).__init__ (compiler)

   def compile (self) :
       self.readSourceFiles ("set/edit.h", "set/edit.cc")

# --------------------------------------------------------------------------

class PropertyModule (ProgramBuildingSet) :
   def __init__ (self, compiler) :
       super (PropertyModule, self).__init__ (compiler)

   def compile (self) :
       self.readSourceFiles ("set/prop-table.h", "set/prop-table.cc")

# --------------------------------------------------------------------------

class TraceModule (ProgramBuildingSet) :
   def __init__ (self, compiler) :
       super (EditModule, self).__init__ (compiler)

   def compile (self) :
       self.readSourceFiles ("set/trace.h", "set/trace.cc")

# --------------------------------------------------------------------------

class DescriptionModule (ProgramBuildingSet) :
   def __init__ (self, compiler) :
       super (DescriptionModule, self).__init__ (compiler)

   def add_args (self, parser, args) :
       for key in args.keys () :
           value = args [key]
           print ("ARG", key, "=", value)
           item = Variable ()
           initVariable (item)
           item.item_name = key
           item.mod_rename = value
           parser.enter (item)

   def decl (self, code, **args) :
       if not isinstance (code, str) :
          product = ToCpp ()
          product.openString ()
          product.send_stat (code)
          code = product.closeString ()
          print ("CODE", code)

       parser = CmmCompiler ()
       self.add_args (parser, args)

       parser.openString (code)
       result = parser.parse_declaration ()
       parser.close ()
       return result

   def stat (self, code, **args) :
       parser = CmmCompiler ()
       self.add_args (parser, args)

       parser.openString (code)
       result = parser.parse_stat ()
       parser.close ()
       return result

   def add (self, target, item) :
       if isinstance (target, Namespace) :
          target.members.items.append (item)
       elif isinstance (target, Class) :
          target.members.items.append (item)
       elif isinstance (target, CmmSimpleItem) :
          target.body.items.append (item)

   def compile (self) :
       compiler = self.compiler
       self.readSource ("set/description.t")

       record_param = self.get ("Record")

       basic_param = self.get ("Basic")
       if basic_param == "" :
          basic_param = record_param

       r = compiler.lookup ("Record")
       b = compiler.lookup ("Basic")
       self.rename (r, record_param)
       self.rename (b, basic_param)

       dcl_ns = compiler.lookup ("plastic")
       dcl_ns.skip_code = True
       dcl_ns.hidden_scope = True

       io_ns = compiler.lookup ("building")
       io_ns.skip_code = True
       io_ns.hidden_scope = True

       code_ns = compiler.lookup ("set")
       code_ns.hidden_scope = True

       d = self.find (code_ns, "RecordDesc")
       self.rename (d, record_param + "Desc")

       code = """
       class ItemDesc : public TypeDesc
       {
       public :
          // ItemDesc ()
          // {
          // }

          Item * createInstance ()
          {
             return new Item;
          }
       };
       """

       # c = self.decl ("class C { };")
       c = self.decl (d)

       r = self.decl ("void read (void * data) { }", read = "readItem")
       w = self.decl ("void write (void * data) { }", write = "writeItem")

       s = self.stat ("a = b;", a = "A", b = "B")

       # d.members.items.append (r)
       # d.members.items.append (w)
       code_ns.members.items.append (c)
       c.members.items.append (r)
       c.members.items.append (w)
       w.body.items.append (s)

# --------------------------------------------------------------------------

class PluginModule (ProgramBuildingSet) :
   def __init__ (self, compiler) :
       super (PluginModule, self).__init__ (compiler)

   def compile (self) :
       compiler = self.compiler

       # self.readSource ("set/kplugin/kplugin.t")

       self.setup ("id", "kview")
       name = self.id
       self.setup ("name", name)

       self.input_subdir = "set/kplugin"
       self.output_subdir = name

       self.setup ("json_name", name + ".json")
       self.setup ("description", name)
       self.setup ("icon", "")

       self.setup ("qrc_name", name + ".qrc")
       self.setup ("prefix_name", "/kxmlgui5/" + name)

       self.setup ("rc_name", name + ".rc")
       self.setup ("gui_name", name)
       self.setup ("action_name", name + "_run")

       self.setup ("plugin_name", name)

       self.fileSubst (self.json_name,   "kplugin.json",   quote = ["description", "icon", "name", "id"])
       self.fileSubst (self.qrc_name,    "kplugin.qrc",    subst = ["rc_name"], quote = ["prefix_name"])
       self.fileSubst (self.rc_name,     "kplugin.rc",     quote = ["gui_name", "action_name"])
       self.fileSubst ("CMakeLists.txt", "CMakeLists.txt", subst = ["plugin_name", "json_name", "qrc_name"])

       self.readSource (os.path.join (self.input_subdir, "module.t"))
       self.readSourceWithDirectives ("module.h")
       self.readSourceWithDirectives ("module.cc")

   def setup (self, name, value) :
       if getattr (self, name, "") == "" :
          setattr (self, name, value)

   def isLetter (self, c) :
       return c >= 'A' and c <= 'Z' or c >= 'a' and c <= 'z' or c == '_'

   def isDigit (self, c) :
       return c >= '0' and c <= '9'

   def isLetterOrDigit (self, c) :
       return self.isLetter (c) or self.isDigit (c)

   def fileSubst (self, output_name, input_name, subst = [ ], quote = [ ]) :
       output_name = os.path.join (self.output_subdir, output_name)
       output_name = self.compiler.win.outputFileName (output_name, with_subdir = True)
       input_name = os.path.join (self.input_subdir, input_name)

       input = LexerInput ()
       input.openFile (input_name)

       output = Output ()
       output.openFile (output_name)

       input.readChar ()
       while input.ch != '\0' :
          if not self.isLetter (input.ch) :
             output.put (input.ch)
             input.readChar ()
          else :
             txt = input.ch
             input.readChar ()
             while self.isLetterOrDigit (input.ch) :
                txt = txt + input.ch
                input.readChar ()
             if txt in subst :
                txt = getattr (self, txt)
             elif txt in quote :
                txt = quoteString (getattr (self, txt))
             output.put (txt)

       # NO input.close ()
       output.close ()

   def readSourceWithDirectives (self, fileName) :
       # print ("readSourceWithDirectives", fileName)

       fileName = os.path.join (self.input_subdir, fileName)

       compiler = self.compiler

       compiler.report_directives = True
       compiler.report_comments = True
       compiler.report_empty_lines = True

       save_macros = compiler.macros
       compiler.addMacro ("Q_OBJECT", "") # !?
       compiler.addMacro ("Q_SLOTS", "") # !?
       compiler.addMacroWithParams ("Q_UNUSED", ["x"], "") # !?

       compiler.openNestedFile (fileName)
       decl_list = compiler.global_scope
       while not compiler.isEndOfSource () :
           compiler.on_declaration (decl_list) # convert notes to statements
           decl = compiler.parse_declaration ()
           decl_list.items.append (decl)
       compiler.on_declaration (decl_list)
       compiler.closeNested ()

       compiler.macros = save_macros

       compiler.report_directives = False
       compiler.report_comments = False
       compiler.report_empty_lines = False

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
