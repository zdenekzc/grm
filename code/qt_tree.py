
# qt_import.py - model based tree

from __future__ import print_function

from util import import_qt_modules, findIcon
import_qt_modules (globals ())

import os, sys
import inspect, types

from util import use_qt4, use_pyqt5, use_pyside2, qt_module_names, variant_to_str, findIcon
from tree import Tree
from code_cls import *
from code_tree import IdentifierTree

# --------------------------------------------------------------------------

class TreeModel (QAbstractItemModel) :

   def __init__ (self, parent, root) :
       super (TreeModel, self).__init__ (parent)
       self.root = root

   def columnCount (self, parent) :
       return 1

   def data (self, index, role) :
       result = QVariant ()
       if index.isValid () :
          if role == Qt.DisplayRole :
             item = index.internalPointer ()
             result = item.item_name
          if role == Qt.DecorationRole :
             item = index.internalPointer ()
             if item.item_icon != None :
                result = findIcon (item.item_icon)
          if role == Qt.ForegroundRole :
             item = index.internalPointer ()
             if item.item_ink != None :
                result = item.item_ink
       return result

   def index (self, line, column, parent) :
       result = QModelIndex ()
       if self.hasIndex (line, column, parent) :
          parentItem = None
          if not parent.isValid () :
             parentItem = self.root
          else :
             parentItem = parent.internalPointer ()
          childItem = None
          if parentItem != None :
             # parentItem.get_subitems ()
             if line < len (parentItem.item_list) :
                childItem = parentItem.item_list [line]
          if childItem != None :
             result = self.createIndex (line, column, childItem)
       return result

   def parent (self, index) :
       result = QModelIndex ()
       if index.isValid () :
          childItem = index.internalPointer ()
          parentItem = childItem.item_context
          if parentItem != None and parentItem != self.root :
             # parentItem.get_subitems ()
             pos = parentItem.item_list.index (childItem)
             result = self.createIndex (pos, 0, parentItem)
       return result

   def rowCount (self, parent) :
       parentItem = None
       if not parent.isValid () :
          parentItem = self.root
       else :
          parentItem = parent.internalPointer ()
       cnt = 0
       if parentItem != None :
          if hasattr (parentItem, "item_list") :
             # parentItem.get_subitems ()
             cnt = len (parentItem.item_list)
       return cnt

# --------------------------------------------------------------------------

class MyProxyModel (QSortFilterProxyModel) :

    def __init__ (self, parent=None):
        super (MyProxyModel, self).__init__ (parent)
        self.pattern = ""

    def filterAcceptsRow (self, sourceRow, sourceParent) :
        result = True
        if not sourceParent.isValid () : # top level item
           column0 = self.sourceModel().index (sourceRow, 0, sourceParent)
           text = variant_to_str (self.sourceModel().data (column0, Qt.DisplayRole))
           result = text.find (self.pattern) >= 0
        return result

# --------------------------------------------------------------------------

def named_type (text) :
    result = NamedType ()
    result.type_label = text
    return result

def displayProperty (target, prop) :
    var = Variable ()
    var.item_name = prop.name ()
    var.item_type = named_type (prop.typeName ()) # !?
    var.comment = "property"
    var.item_ink = "green"
    target.add (var)

def displayProperties (target, data) :
    typ = data.metaObject ()
    cnt = typ.propertyCount ()
    for inx in range (cnt) :
        prop = typ.property (inx)
        displayProperty (target, prop)

# --------------------------------------------------------------------------

def void_type () :
    result = SimpleType ()
    result.type_void = True
    return result

def displayMethod (target, method) :
    if use_qt4 :
       sign = method.signature ()
    else :
       sign = bytearray_to_str (method.methodSignature ())
    inx = sign.find ("(")
    if inx >= 0 :
       name =  sign [ : inx ]
    else :
       name = sign

    func = Function ()
    func.item_name = name

    kind = method.methodType ()
    if kind == QMetaMethod.Signal :
       func.item_ink = "blue"
       func.comment = "signal"
    elif kind == QMetaMethod.Slot :
       func.item_ink = "orange"
       func.comment = "slot"
    else :
       func.item_ink = "red"
       func.comment = "method"

    typ = method.typeName ()
    if typ != "" :
       func.result_type = named_type (method.typeName ())
    else :
        func.result_type = void_type ()

    func.comment = "method: " + sign

    names = method.parameterNames ()
    types = method.parameterTypes ()
    inx = 0
    for name in names :
        var = Variable ()
        var.item_name = name
        var.item_type = named_type (str (types [inx]))
        func.add (var)

    target.add (func)

def displayMethods (target, data) :
    typ = data.metaObject ()
    cnt = typ.methodCount ()
    for inx in range (cnt) :
        method = typ.method (inx)
        displayMethod (target, method)

# --------------------------------------------------------------------------

def findClass (target, name, obj) :
    if name in target.item_dict :
       cls = target.item_dict [name]
    else :
       cls = displayClass (target, name, obj)
    return cls

def displayClass (target, name, obj) :
    cls = None
    if name not in target.item_dict :
       base_classes = [ ]
       for base in obj.__bases__ :
           base_name = base.__name__
           answer = findClass (target, base_name, base)
           base_classes.append (answer)

       cls = Class ()
       cls.item_name = name
       target.add (cls) # after item_name
       cls.comment = inspect.getdoc (obj)
       cls.data = obj
       cls.base_classes = base_classes

       if hasattr (obj, "metaObject") :
          try :
             data = obj ()
             cls.method_dict = { }
             # displayProperties (cls, data)
             # displayMethods (cls, data)
             displayMembers (cls, data)
          except :
             pass
       # displayMembers (cls, obj)

    return cls

# --------------------------------------------------------------------------

def get_first (txt, mark) :
    answer = txt.split (mark, 1)
    if len (answer) == 2 :
       return answer[0], answer [1]
    else :
       return "", answer [0]

def get_type (txt) :
    answer = txt.split (" -> ", 1)
    if len (answer) == 2 :
       return answer[0], answer [1]
    else :
       return answer [0], ""

def displayBuiltin (target, name, data) :
    if str (type (data)) == "<type 'builtin_function_or_method'>" :
    # if inspect.ismethod (data) :
       txt = data.__doc__
       txt, result_type = get_type (txt)
       cls, txt = get_first (txt, ".")
       name, txt = get_first (txt, "(")
       if txt.startswith ("(") and txt.endswith (")") :
          txt = txt [ 1: -2 ]
          params = txt.split (",")
       else :
          params = [ ]

       result = Function ()
       result.item_name = name
       # result.result_type = named_type (result_type)
       # for param in params :
       #    var = Varaiable ()
       #    var.item_name = param # !?
       #    func.paramaters.append (var)

       result.comment = data.__doc__
       result.data = data
       result.params = params
       target.add (result)

    else  :
       func = Function ()
       func.item_name = name
       func.comment = data.__doc__
       func.data = data
       target.add (func)

def displayConst (target, name, data) :
    result = EnumItem () # !?
    result.item_name = name
    result.item_icon = "flag"
    result.comment = data.__doc__
    result.type = type (data)
    result.data = data
    target.add (result)

def displayFunction (target, name, data) :
    result = Function ()
    result.item_name = name
    target.add (result)
    target.parameters = [ ]
    (args, varargs, keywords, defaults) = inspect.getargspec (data)
    for arg in args :
        param = Variable ()
        param.item_name = arg
        result.add (param)
        result.parameters.add (param)
    result.comment = data.__doc__
    result.data = data

def displayOther (target, name, data) :
    result = Declaration () # !?
    result.item_name = name
    result.comment = data.__doc__
    result.type = type (data)
    result.data = data
    target.add (result)

def displayMember (target, name, obj) :
    if name.startswith ("__") :
       pass
    elif inspect.isbuiltin (obj) :
       displayBuiltin (target, name, obj)
    elif inspect.isclass (obj) :
       if target.item_context == None : # !?
          displayClass (target, name, obj) # !?
       elif name not in target.item_context.item_dict :
          displayClass (target.item_context, name, obj) # !?
    elif inspect.ismethod (obj) or inspect.isfunction (obj) or type (obj) == types.FunctionType :
       # if name not in target.item_dict :
       displayFunction (target, name, obj)
    elif isinstance (obj, int) :
       displayConst (target, name, obj)
    else :
       displayOther (target, name, obj)

def displayMembers (target, data) :
    members = inspect.getmembers (data)
    for member in members :
        (name, obj) = member
        displayMember (target, name, obj)

# --------------------------------------------------------------------------

def displayModule (target, module) :
    members = inspect.getmembers (module)
    for member in members :
        (name, obj) = member
        displayMember (target, name, obj)

def displayModules (module_names) :
    result = Namespace ()
    result.item_name = "Qt Classes"
    for module_name in module_names :
       print ("MODULE", module_name)
       displayModule (result, sys.modules [module_name])
    return result

def displayQt (win) :
    data = displayModules (qt_module_names ())
    """
    if use_pyside2 :
       data = displayModules (["PySide2.QtWidgets", "PySide2.QtGui", "PySide2.QtCore"])
    elif use_pyqt5 :
       data = displayModules (["PyQt5.QtWidgets", "PyQt5.QtGui", "PyQt5.QtCore"])
    else :
       data = displayModuless (["PyQt4.QtGui", "PyQt4.QtCore"])
    """

    data.item_list.sort (key = lambda item : item.item_name)
    return data

# --------------------------------------------------------------------------

class QtTree (QWidget):

    def __init__ (self, win=None):
        super (QtTree, self).__init__ (win)
        self.win = win

        self.source_tree_widget = None

        self.source_model = None
        self.filter_model = None

        self.filterLine = QLineEdit ()
        self.treeView = QTreeView ()

        self.treeView.setHeaderHidden (True)

        self.layout = QVBoxLayout ()
        self.layout.addWidget (self.filterLine)
        self.layout.addWidget (self.treeView)
        # self.layout.setContentsMargins (0, 0, 0, 0)
        self.layout.setContentsMargins (4, 4, 4, 4)

        self.setLayout (self.layout)

        self.treeView.clicked.connect (self.treeView_clicked)
        self.filterLine.textChanged.connect (self.filterLine_textChanged)

    def setData (self, data) :
        self.source_model = TreeModel (self, data)

        # self.filter_model = QSortFilterProxyModel (self)
        self.filter_model = MyProxyModel (self)
        self.filter_model.setSourceModel (self.source_model)
        self.filter_model.pattern = self.filterLine.text ()
        self.filter_model.setFilterFixedString (self.filterLine.text ())

        self.treeView.setModel (self.filter_model)

    def treeView_clicked (self, index) :
        item = self.filter_model.mapToSource (index).internalPointer ()
        self.win.showProperties (item)

    def filterLine_textChanged (self, text) :
        if self.filter_model != None :
           self.filter_model.pattern = text
           self.filter_model.setFilterFixedString (text)

# --------------------------------------------------------------------------

def qt_tree (win) :

    box = QtTree (win)
    win.leftTabs.addTab (box, "Qt Tree")
    win.leftTabs.setCurrentWidget (box)
    win.showSideTabAction (win.tabsMenu, "Qt Tree", box, "Meta+Q", "QtProject-qtcreator")
    win.showTab (box)

    data = displayQt (win)
    box.setData (data)

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
