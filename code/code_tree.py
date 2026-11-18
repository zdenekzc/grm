#!/usr/bin/env python

from __future__ import print_function

import os, sys, re, inspect

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from input import fileNameToIndex, indexToFileName
from util import use_qt4, Text, qstring_to_str, bytearray_to_str, qstringref_to_str, variant_to_str

from tree import Tree, TreeItem, branchContinue, callContinue

from util import findColor
# from util import use_qt4, use_pyqt6, use_pyside6, findColor, findIcon, Text, setResizeMode, str_to_bytearray, qstringlist_to_list, empty_qstringlist, menu_exec
# from edit import Editor

from grammar import Grammar, Rule, Expression, Alternative, Ebnf, Nonterminal, Terminal

# --------------------------------------------------------------------------

def OutlineProperties (tree, editor) :
    fileName = editor.getFileName ()
    fileInx = fileNameToIndex (fileName)
    branch = tree
    block = editor.document().firstBlock()
    while block.isValid () :
       iterator = block.begin ()
       while not iterator.atEnd () :
          fragment = iterator.fragment ();
          if fragment.isValid () :
             fmt = fragment.charFormat ()
             if fmt.hasProperty (Text.outlineProperty) :
                name = str (fmt.stringProperty (Text.outlineProperty))
                node = TreeItem (branch, name)
                node.src_file = fileInx
                node.src_line = block.blockNumber () + 1
             elif fmt.hasProperty (Text.defnProperty) :
                name = str (fmt.stringProperty (Text.defnProperty))
                node = TreeItem (branch, name)
                node.src_file = fileInx
                node.src_line = block.blockNumber () + 1
          iterator += 1
       block = block.next ()

# --------------------------------------------------------------------------

def UiTree (widget) :
    branch = UiBranch (widget)
    # if branch != None :
    #    callContinue (branch)
    return branch

def UiBranch (widget) :
    branch = None

    title = widget.objectName ()
    title = qstring_to_str (title)

    if title != "" and not title.startswith ("qt_") :

       branch = TreeItem (None)
       branch.setText (0, title)
       branch.obj = widget
       branch.addIcon ("class")
       widget._qt_properties_ = True # show Qt properties
       UiSignals (branch, widget)
       UiSlots (branch, widget)
       UiMethods (branch, widget)
       UiProperties (branch, widget)
       UiMembers (branch, widget)

       branch.continue_func = UiContinue

    return branch

def UiContinue (branch) :
    for child in branch.obj.children () :
        node = UiBranch (child)
        if node != None :
           branch.addChild (node)

def UiSignals (target, data) :
    branch = None
    typ = data.metaObject ()
    cnt = typ.methodCount ()
    for inx in range (cnt) :
        method = typ.method (inx)
        if method.methodType () == QMetaMethod.Signal :
           if branch == None :
              branch = TreeItem (target)
              branch.setText (0, "signals")
              branch.setInk ("blue")
           if use_qt4 :
              title = qstring_to_str (method.signature ())
           else :
              title = bytearray_to_str (method.methodSignature ())
           node = TreeItem (branch, title)
           node.setInk ("blue")
           node.addIcon ("function")

def UiSlots (target, data) :
    branch = None
    typ = data.metaObject ()
    cnt = typ.methodCount ()
    for inx in range (cnt) :
        method = typ.method (inx)
        if method.methodType () == QMetaMethod.Signal :
           if branch == None :
              branch = TreeItem (target)
              branch.setText (0, "slots")
              branch.setInk ("green")
           if use_qt4 :
              title = qstring_to_str (method.signature ())
           else :
              title = bytearray_to_str (method.methodSignature ())
           node = TreeItem (branch, title)
           node.setInk ("green")
           node.addIcon ("function")

def UiMethods (target, data) :
    branch = None
    typ = data.metaObject ()
    cnt = typ.methodCount ()
    for inx in range (cnt) :
        method = typ.method (inx)
        kind = method.methodType ()
        if kind != QMetaMethod.Signal and kind != QMetaMethod.Slot :
           if branch == None :
              branch = TreeItem (target)
              branch.setText (0, "methods")
              branch.setInk ("red")
           node = TreeItem (branch)
           if use_qt4 :
              node.setText (0, method.signature ())
           else:
              node.setText (0, bytearray_to_str (method.methodSignature ()))
           node.setInk ("red")

def UiProperties (target, data) :
    branch = None
    typ = data.metaObject ()
    cnt = typ.propertyCount ()
    for inx in range (cnt) :
        if branch == None :
           branch = TreeItem (target)
           branch.setText (0, "properties")
           branch.setInk ("orange")
        prop = typ.property (inx)
        txt = prop.name () + " : " + prop.typeName ()
        try :
           txt = txt + " = " + variant_to_str (prop.read (data))
        except :
           pass
        node = TreeItem (branch)
        node.setText (0, txt)
        node.setInk ("green")
        if prop.isUser () :
           node.setInk ("red")
           # print ("USER PROPERTY", prop.name ())

def UiMembers (target, data) :
    branch = None
    members = inspect.getmembers (data)
    for member in members :
        (name, obj) = member
        if branch == None :
           branch = TreeItem (target)
           branch.setText (0, "members")
           branch.setInk ("goldenrod")
        node = TreeItem (branch)
        node.setText (0, name)
        if inspect.isdatadescriptor (obj) or inspect.isgetsetdescriptor (obj) or inspect.ismemberdescriptor (obj)  :
           node.setInk ("red")
        elif inspect.isbuiltin (obj) :
           node.setInk ("green")
        elif inspect.ismethoddescriptor (obj) or inspect.ismethod (obj) or inspect.isfunction (obj) or inspect.isbuiltin (obj) or inspect.isroutine (obj)  :
           node.setInk ("blue")
        else :
           node.setInk ("orange")

# --------------------------------------------------------------------------

def ReflectionTree (target, obj) :
    typ = obj.metaObject ()

    for inx in range (typ.propertyCount ()) :
        prop = typ.property (inx)
        txt = prop.name () + " : " + prop.typeName ()
        node = TreeItem (target)
        node.setText (0, txt)
        node.addIcon ("variable")
        node.setForeground (0, findColor ("green"))

    for inx in range (typ.methodCount ()) :
        method = typ.method (inx)
        if use_qt4 :
           txt = qstring_to_str (method.signature ())
        else :
           txt = bytearray_to_str (method.methodSignature ())
        node = TreeItem (target)
        node.setText (0, txt)
        kind = method.methodType ()
        if kind == method.Signal :
           node.addIcon ("signal")
           node.setForeground (0, findColor ("red"))
        elif kind == method.Slot :
           node.addIcon ("slot")
           node.setForeground (0, findColor ("orange"))
        else :
           node.addIcon ("function")
           node.setForeground (0, findColor ("blue"))

        param_names = method.parameterNames()
        param_types = method.parameterTypes ()
        for k in range (method.parameterCount()) :
            txt = bytearray_to_str (param_names [k]) + " : " + bytearray_to_str (param_types [k])
            param_node = TreeItem (node)
            param_node.setText (0, txt)
        result_node = TreeItem (node)
        result_node.setText (0, "return " + method.typeName ())

# --------------------------------------------------------------------------

def XmlTree (tree, fileName) :
    top = TreeItem (tree)

    f = QFile (fileName)
    if f.open (QFile.ReadOnly | QFile.Text) :
       XmlItems (top, fileName, f)
       f.close ()

    return top

def XmlTreeFromEditor (tree, edit) :
    fileName = edit.getFileName ()
    top = TreeItem (tree)

    text = edit.toPlainText ()
    data = str_to_bytearray (text)
    stream = QBuffer ()
    stream.setData (data)
    if stream.open (QFile.ReadOnly | QFile.Text) :
       XmlItems (top, fileName, stream)
    stream.close ()

    return top

def XmlItems (top, fileName, stream) :

    fileInx = fileNameToIndex (fileName)
    top.src_file = fileInx

    fileInfo = QFileInfo (fileName)
    top.setText (0, fileInfo.fileName ())

    top.setForeground (0, findColor ("green"))
    top.setExpanded (True)

    reader = QXmlStreamReader (stream)
    current = top

    while not reader.atEnd() :
       if reader.isStartElement () :
          item = TreeItem (current)
          item.setText (0, qstringref_to_str (reader.name ()))
          item.setForeground (0, findColor ("blue"))
          item.src_file = fileInx
          item.src_line = reader.lineNumber ()
          item.setExpanded (True)
          current = item

          attrs = reader.attributes ()
          cnt = attrs.size ()
          for i in range (cnt) :
             a = attrs.at (i) # QXmlStreamAttribute
             node = TreeItem (item)
             node.setText (0, qstringref_to_str (a.name ()) + " = " + qstringref_to_str (a.value ()))
             node.setForeground (0, findColor ("goldenrod"))

          """
          if qstringref_to_str (reader.name ()) == "widget" :
             decl = TreeItem (top)
             decl.setText (0, qstringref_to_str (attrs.value ("name")) + " : " + qstringref_to_str (attrs.value ("class")))
             decl.setForeground (0, findColor ("orange"))
             decl.src_file = fileInx
             decl.src_line = reader.lineNumber ()
         """

       elif reader.isEndElement () :
          current = current.parent ()

       elif reader.isCharacters () and not reader.isWhitespace () :
          item = TreeItem (current)
          item.setText (0, qstringref_to_str (reader.text ()))
          item.setForeground (0, findColor ("limegreen"))
          item.src_file = fileInx
          item.src_line = reader.lineNumber ()

       reader.readNext ()

    if reader.hasError() :
       item = TreeItem (top)
       item.setText (0, reader.errorString ())
       item.setForeground (0, findColor ("red"))

# --------------------------------------------------------------------------

"Scope of identifiers - win.showClasses () and Navigator"

class IdentifierTree (object) :
   def __init__ (self, tree, data) :
       if getattr (data, "item_name", "") == "" :
          self.showScope (tree, data)
       else :
          self.showItem (tree, None, data)
       branchContinue (tree)

   def showItem (self, above, scope, data) :
       name = getattr (data, "item_label", "")
       if name == "" :
          name = getattr (data, "item_name", "")
          context = getattr (data, "item_context", None)
          if context != None and context != scope :
             name = getattr (context, "item_name", "") + "::" + name
       node = TreeItem (above, name)
       node.obj = data
       node.setupTreeItem ()
       node.continue_func = lambda : self.showScope (node, data)

   def showScope (self, branch, scope) :
       if hasattr (scope, "item_list") :
          for item in scope.item_list :
              self.showItem (branch, scope, item)
       if hasattr (scope, "item_block") :
          for item in scope.item_block :
              self.showItem (branch, scope, item)

# --------------------------------------------------------------------------

# list of grammar rules from grammar data (used by Navigator)

def GrammarRules (tree, editor, grammar) :
    fileName = editor.getFileName ()
    fileInx = fileNameToIndex (fileName)
    grammar.item_list = [ ] # similar to compiler data
    for rule in grammar.rules :
        node = TreeItem (tree, rule.name)
        node.obj = rule
        rule.item_icon = "class"
        grammar.item_list.append (rule)

# list of grammar rules from text file (used by Navigator)

def GrammarNames (tree, editor) :
    fileName = editor.getFileName ()
    fileInx = fileNameToIndex (fileName)
    source = str (editor.toPlainText ())
    lineNum = 0
    for line in source.split ("\n") :
        lineNum = lineNum + 1
        pattern = "(\s*)(\w\w*)\s*(<.*>)\s*:\s*"
        m = re.match (pattern, line)
        if m :
           name = m.group (2)
           node = TreeItem (tree, name)
           node.src_file = fileInx
           node.src_line = lineNum
           node.addIcon ("class")

# --------------------------------------------------------------------------

"Grammar tree with details - win.displayGrammarData () - Tree Tab"

class GrammarTree (object) :
   def __init__ (self, tree, grammar, fileInx, module) :
       if module == None :
          module = sys.modules ["grammar"]

       self.grammar = grammar
       self.module = module
       self.fileInx = fileInx

       if getattr (self.grammar, "symbols", None) != None :
          self.addSymbols (tree)
       self.addTypes (tree)
       self.addGroups (tree)

       for rule in grammar.rules :
          self.addRule (tree, rule)

       branchContinue (tree)

   def addSymbols (self, above) :
       branch = TreeItem (above, "symbols")
       branch.continue_func = lambda : self.addSymbolsCont (branch)

   def addSymbolsCont (self, branch) :
       for symbol in self.grammar.symbols :
           TreeItem (branch, str (symbol.inx) + " " + symbol.alias)

   def addTypes (self, above) :
       branch = TreeItem (above, "types")
       branch.continue_func = lambda : self.addTypesCont (branch)

   def addTypesCont (self, branch) :
       for type in self.grammar.struct_list :
           name = getattr (type, "type_label", "")
           if name == "" :
              name = getattr (type, "type_name", "")
           node = TreeItem (branch, name)
           node.addIcon ("class")
           node.obj = type
           for enum in type.enum_list :
               leaf = TreeItem (node, enum.enum_name)
               leaf.addIcon ("enum")
               leaf.obj = enum
           for field in type.field_list :
               leaf = TreeItem (node, field.field_name)
               leaf.addIcon ("variable")
               leaf.obj = field

   def addGroups (self, above) :
       node = TreeItem (above, "groups")
       node.continue_func = lambda : self.updateGroups (node) # later, aftet product is generated

   def updateGroups (self, branch) :
       for group in self.grammar.group_list :
           node = TreeItem (branch, group.group_name)
           node.addIcon ("class")
           node.obj = group
           for rule in self.grammar.rules :
               if rule.hide_group == group :
                  leaf = TreeItem (node, "hide " + rule.name)
                  leaf.addIcon ("flag-red")
                  leaf.obj = rule
           for rule in self.grammar.rules :
               if rule.subst_group == group :
                  leaf = TreeItem (node, "subst " + rule.name)
                  leaf.addIcon ("flag-green")
                  leaf.obj = rule
           for rule in self.grammar.rules :
               if rule.rewrite_group == group or rule.reuse_group == group :
                  leaf = TreeItem (node, rule.name)
                  leaf.addIcon ("flag-blue")
                  leaf.obj = rule

   def addRule (self, above, rule) :
       node = TreeItem (above, rule.name)
       node.obj = rule
       # node.setToolTip (0, "line " + str (rule.src_line))
       node.addIcon ("class")
       node.continue_func = lambda : self.addRuleCont (node, rule)

   def addRuleCont (self, node, rule) :
       self.addInfo (node, rule)
       self.addBranch (node, rule.expr)

   def addBranch (self, above, data) :
       txt = ""
       if isinstance (data, self.module.Expression) :
          txt = "expression"
       elif isinstance (data, self.module.Alternative) :
          txt = "alternative"
       elif isinstance (data, self.module.Ebnf) :
          txt = "ebnf " + data.mark
       elif isinstance (data, self.module.Nonterminal) :
          txt = "nonterminal "
          if data.variable != "" :
             txt = txt + data.variable + ":"
          txt = txt + data.rule_name
       elif isinstance (data, self.module.Terminal) :
          if data.multiterminal_name != "" :
             if data.variable != "" :
                txt = txt + data.variable + ":"
             txt = "terminal " + data.multiterminal_name
          else :
             txt = "terminal " + data.text
       else:
          txt = data.__class__.__name__

       node = TreeItem (above, txt)

       # if hasattr (data, "src_line") :
       #    node.src_file = self.fileInx
       #    node.src_line = data.src_line
       node.obj = data

       if isinstance (data, self.module.Nonterminal) :
          node.addIcon ("function")
       if isinstance (data, self.module.Terminal) :
          node.addIcon ("variable")
       if isinstance (data, self.module.Ebnf) :
          node.addIcon ("block")

       self.addInfo (node, data)

       if isinstance (data, self.module.Expression) :
          for t in data.alternatives :
             self.addBranch (node, t)
       elif isinstance (data, self.module.Alternative) :
          for t in data.items :
             self.addBranch (node, t)
       elif isinstance (data, self.module.Ebnf) :
          self.addBranch (node, data.expr)

   def addInfo (self, above, data) :
       if getattr (data, "nullable", False) :
          above.setForeground (0, QBrush (Qt.red))

       if hasattr (data, "first") :
          branch = TreeItem (above, "first")
          branch.addIcon ("info")
          branch.setForeground (0, QBrush (Qt.blue))
          if getattr (data, "nullable", False) :
             node = TreeItem (branch, "<empty>")
             node.setForeground (0, QBrush (Qt.red))
          for inx in range (self.grammar.symbol_cnt) :
              if data.first & 1 << inx :
                 name = self.grammar.symbols [inx].alias
                 node = TreeItem (branch, name)
                 node.setForeground (0, QBrush (Qt.blue))

       if hasattr (data, "follow") :
          branch = TreeItem (above, "follow")
          branch.addIcon ("info")
          branch.setForeground (0, QBrush (Qt.blue))
          for inx in range (self.grammar.symbol_cnt) :
              if data.follow & 1 << inx :
                 name = self.grammar.symbols [inx].alias
                 node = TreeItem (branch, name)
                 node.setForeground (0, QBrush (Qt.blue))

# --------------------------------------------------------------------------

"Compiler data - win.displayCompilerData () - Tree Tab"

class CompilerTree (object) :
   def __init__ (self, tree, data) :
       self.stack = [ data ]
       self.showStructure (tree, "", data)

   def showStructure (self, above, name, data) :
       if name != "" :
          name = name + " : "

       if data == None :
          TreeItem (above, name + "None")
       elif isinstance (data, int) :
          TreeItem (above, name + "int = " + str (data))
       elif isinstance (data, str) :
          TreeItem (above, name + "string = " + data)
       else :
          text = name + "object " + data.__class__.__name__

          note = ""
          if getattr (data, "id", None) != None:
             note = note + " (id: " + str (data.id) + ")" # !? identifiers
          if getattr (data, "item_name", None) != None:
             note = note + " (item_name: " + str (data.item_name) + ")"
          if getattr (data, "item_decl", None) != None:
             note = note + " (item_decl: " + str (data.item_decl) + ")"
          if getattr (data, "item_type", None) != None:
             note = note + " (item_type: " + str (data.item_type) + ")"
          if getattr (data, "item_label", None) != None:
             note = note + " (item_label: " + str (data.item_label) + ")"
          if note != "" :
             text = text + note

          branch = TreeItem (above, text)
          if note != "" :
             branch.setToolTip (0, note [1:])
          branch.obj = data # show data object in property window
          branch.setupTreeItem ()

          branch.continue_func = lambda : self.showBranch (branch, data)

   def showBranch (self, branch, data) :
       # print ("showBranch", branch.text(0), data)

       if hasattr (data, "_fields_") :
          for ident in data._fields_ :
              if ident != "body" and ident != "ctor_init":
                 self.showStructureItem (branch, data, ident)
       # elif hasattr (data, "__dict__") : # !?
       #    for ident in data.__dict__ :
       #        self.showStructureItem (branch, data, ident)

       if hasattr (data, "items") and not isinstance (data, dict) :
          for item in data.items :
             self.showStructure (branch, "", item)

       if hasattr (data, "ctor_init") :
          self.showStructureItem (branch, data, "ctor_init")
       if hasattr (data, "body") :
          self.showStructureItem (branch, data, "body")

   def showStructureItem  (self, above, data, ident) :
       if ident != "items" :
          if hasattr (data, ident) :
             item = data.__dict__ [ident]
             if item in self.stack :
                print ("recursion",  ident, str (item))
                temp = TreeItem (above, "recursion")
                temp.addIcon ("error")
             else :
                self.stack.append (item)
                self.showStructure (above, ident, item)
                self.stack.pop ()

# --------------------------------------------------------------------------

def lookupCompilerData (tree, editor, line, column) :
    if isinstance (editor, QPlainTextEdit) :
       fileName = editor.getFileName ()
       fileInx = fileNameToIndex (fileName)

       # print ("Lookup", "line=", line, "column=", column)
       node = lookup (tree, tree.invisibleRootItem (), fileInx, line, column)

       if node != None :
          # print ("FOUND", node.text (0))
          tree.setCurrentItem (node)
          tree.scrollToItem (node)
          node.setExpanded (True)

# --------------------------------------------------------------------------

def compare (obj, line, column) :

    greater = False

    node_line = getattr (obj, "src_line", 0)
    node_column = getattr (obj, "src_column", 0)

    if node_line > 0 :
       if node_column > 0 and column > 0 :
          greater = node_line > line or node_line == line and node_column > column
       else :
          greater = node_line > line

    return greater

def add_icon (node, icon_name) :
    node.setIcon (0, findIcon (icon_name))

def lookup (tree, branch, fileInx, line, column) :
    inx = 0
    cnt = branch.childCount ()

    if getattr (branch, "continue_func", None) != None :
        callContinue (branch)

    answer = None
    stop = False
    possible = [ ]

    while inx < cnt and not stop :
       "visit node"
       node = branch.child (inx)

       if getattr (node, "continue_func", None) != None :
          callContinue (node)

       "get obj"
       obj = getattr (node, "obj", None)
       if obj == None :
          obj = node

       if 0 :
          print ("lookup", "line=", getattr (obj, "src_line", 0),
                           "column=", getattr (obj, "src_column", 0),
                           branch.text (0))

       if getattr (obj, "src_file", 0) != fileInx :
          # another file
          if not getattr (obj, "stop_file_search", False) :
             possible.append (node)
       else :
          greater = compare (obj, line, column)
          if greater :
             # add_icon (node, "stop")
             stop = True
          else :
             # add_icon (node, "gtk-dialog-info")
             answer = node

       "next node"
       inx = inx + 1

    if answer != None :
       # add_icon (answer, "games-hint")
       tmp = lookup (tree, answer, fileInx, line, column)
       if tmp != None :
          answer = tmp
          # print ("answer is", answer.text (0))

    if answer == None :
       for node in possible :
           if answer == None :
              # add_icon (node, "documentinfo")
              answer = lookup (tree, node, fileInx, line, column)

    # if answer != None :
    #    print ("ANSWER", answer.text (0))
    return answer

# --------------------------------------------------------------------------

# Python classes and methods - Navigator and win.displayPythonCode () - Tree Tab

class PythonTree (object) :
   def __init__ (self, tree, editor) :
       fileName = editor.getFileName ()
       self.src_file = fileNameToIndex (fileName)
       source = str (editor.toPlainText ())

       lineNum = 0
       cls_branch = None
       for line in source.split ("\n") :
           lineNum = lineNum + 1
           pattern = "(\s*)(class|def)\s\s*(\w*)"
           m = re.match (pattern, line)
           if m :
              target = tree
              if m.group (1) != "" and cls_branch != None :
                 target = cls_branch

              is_class = m.group (2) == "class"

              name = m.group (3)
              if is_class :
                 name = "class " + name

              node = TreeItem (target, name)
              node.src_file = self.src_file
              node.src_line = lineNum

              if is_class :
                 node.addIcon ("class")
              else :
                 node.addIcon ("function")

              if is_class :
                 cls_branch = node

# --------------------------------------------------------------------------

"Macro description - ckit/preproc_view.py"

class Description (object) :
   def __init__ (self) :
      self.defn_ref = None
      self.in_parameters = False

      self.invoke_doc = QTextDocument ()
      self.source_doc = QTextDocument ()
      self.result_doc = QTextDocument ()

      self.invoke_cursor = QTextCursor (self.invoke_doc)
      self.source_cursor = QTextCursor (self.source_doc)
      self.result_cursor = QTextCursor (self.result_doc)

class DescriptionWindow (QMainWindow):

   def __init__ (self, parent, desc) :
       super (DescriptionWindow, self).__init__ (parent)

       defn = desc.defn_ref
       code = "#define " + defn.name
       if defn.params != None :
          code = code + "("
          any = False
          for param in defn.params :
              if any :
                 code = code + ","
              any = True
              code = code + param
          code = code + ")"
       code = code + " " + defn.code

       self.splitter = QSplitter ()
       self.splitter.setOrientation (Qt.Vertical)

       self.define_edit = QTextEdit ()
       self.invoke_edit = QTextEdit ()
       self.source_edit = QTextEdit ()
       self.result_edit = QTextEdit ()

       self.splitter.addWidget (self.define_edit)
       self.splitter.addWidget (self.invoke_edit)
       self.splitter.addWidget (self.source_edit)
       self.splitter.addWidget (self.result_edit)

       self.define_edit.setPlainText (code)
       self.invoke_edit.setDocument (desc.invoke_doc)
       self.source_edit.setDocument (desc.source_doc)
       self.result_edit.setDocument (desc.result_doc)

       self.setCentralWidget (self.splitter)
       self.setWindowTitle (defn.name)
       self.show ()

# --------------------------------------------------------------------------

class Navigator (QStackedWidget) :
   def __init__ (self, win, toolTabs) :
       super (Navigator, self).__init__ (win)
       self.active = False
       self.win = win
       self.toolTabs = toolTabs
       self.toolTabs.currentChanged.connect (self.onToolChanged)
       self.win.tabChanged.connect (self.onEditorChanged)

   def onToolChanged (self) :
       self.active = self.toolTabs.currentWidget () == self
       if self.active :
          self.showNavigator ()

   def onEditorChanged (self) :
       if self.active :
          self.showNavigator ()

   def releaseNavigator (self, w) : # called from edit.py
       tree = getattr (w, "navigator_tree", None)
       if tree != None :
          if tree.keep :
             tree.takeTopLevelItem (0)
             tree.keep = False
          self.removeWidget (tree)
          w.navigator_tree = None

   def showNavigator (self) : # called from edit.py
       # print ("show navigator")

       w = self.win.getCurrentTab ()
       editor = self.win.getEditor ()

       tree = getattr (w, "navigator_tree", None)
       if tree == None :
          tree = Tree (self)
          tree.win = self.win # change win
          tree.keep = False
          self.addWidget (tree)
          w.navigator_tree = tree
       self.setCurrentWidget (tree)

       data = getattr (w, "navigator_data", None)

       if hasattr (w, "showNavigator") :
          w.showNavigator (tree) # use showNavigator method
       elif isinstance (data, QTreeWidgetItem) :
          self.showTreeData (tree, data) # add QTree...
       elif isinstance (data, Grammar) and editor != None :
          GrammarRules (tree, editor, data) # tree of grammar rules
       elif data != None and hasattr (data, "item_list") :
          IdentifierTree (tree, data)
       elif editor != None :
          # showNavigator by file name 3xtension"
          fileName = editor.getFileName ()
          name, ext = os.path.splitext (fileName)
          if ext == ".py" :
             PythonTree (tree, editor) # Python classes and functions
          elif ext == ".g" :
             GrammarNames (tree, editor) # rule names
          else :
             OutlineProperties (tree, editor) # show outline and definition properties

   # tree

   def showTreeData (self, tree, data) :
       if isinstance (data, QTreeWidgetItem) :
          tree.addTopLevelItem (data)
          tree.keep = True
          tree.expandItem (data)
          branchContinue (tree)

# --------------------------------------------------------------------------

class Memo (Tree) :
   def __init__ (self, win, toolTabs) :
       super (Memo, self).__init__ (win)
       self.win = win
       self.toolTabs = toolTabs
       self.itemDoubleClicked.connect (self.onItemDoubleClicked)

   def showMemo (self, editor, name) : # called from view.py

       self.toolTabs.setCurrentWidget (self)

       # print ("show memo (1)", name)
       obj = editor.findObjectByName (name)
       if obj != None :
          # print ("show memo (2)", obj.item_name)
          branch = TreeItem (self, obj.item_name)
          branch.obj = obj
          branch.setupTreeItem ()
          branch.setExpanded (True)
          if hasattr (obj, "item_list") :
             for item in obj.item_list :
                 node = TreeItem (branch, item.item_name)
                 node.obj = item
                 node.setupTreeItem ()
          if getattr (obj, "foreign_obj") != None :
             instance = obj.foreign_obj ()
             ReflectionTree (branch, instance)

   def onItemSelectionChanged (self) :
       pass # do not jump to object declaration

   def onItemDoubleClicked (self, node, column) :
       name = node.text (0)
       editor = self.win.getEditor ()
       cursor = editor.textCursor ()
       cursor.insertText (name)

# --------------------------------------------------------------------------

class References (Tree) :
   def __init__ (self, win, toolTabs) :
       super (References, self).__init__ (win)
       self.win = win
       self.toolTabs = toolTabs

   def showReferences (self, editor, name) : # called from edit.py
       self.clear ()
       fileName = editor.getFileName ()
       fileInx = fileNameToIndex (fileName)
       block = editor.document().firstBlock()
       while block.isValid () :
          iterator = block.begin ()
          while not iterator.atEnd () :
             fragment = iterator.fragment();
             if fragment.isValid () :
                fmt = fragment.charFormat ()
                if fmt.hasProperty (Text.infoProperty) :
                   value = str (fmt.stringProperty (Text.infoProperty))
                   if value == name :
                      line = block.blockNumber() + 1
                      text = str (block.text ())
                      text = "line " + str (line) + ": " + text.strip()
                      node = TreeItem (self, text)
                      node.src_file = fileInx
                      node.src_line = line
             iterator += 1
          block = block.next ()
       self.toolTabs.setCurrentWidget (self)

   def onItemSelectionChanged (self) :
       pass # do not jump to object declaration

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
