#!/usr/bin/env python

from __future__ import print_function

import sys
import inspect

from util import import_qt_modules
import_qt_modules (globals ())

from util import color_map, findColor, mouse_event_pos, menu_exec, is_variant, findIcon, use_pyqt6
from code import Item, Type
from tree import TreeItem

# --------------------------------------------------------------------------

class PropInfo (object) :
    def __init__ (self) :
        self.name = ""
        self.group = 0
        self.name_item = None # QTableWidgetItem
        self.value_item = None # QTableWidgetItem
        self.widget = None
    def setNameColor (self, color) :
        if color != None :
           self.name_item.setForeground (color)
    def setValueColor (self, color) :
        if color != None :
           self.value_item.setForeground (color)
    def setValuePaper (self, color) :
        if color != None :
           self.value_item.setBackground (color)
    def setValueIcon (self, icon) :
        if icon != None :
           if isinstance (icon, str) :
              if icon != "" :
                 self.value_item.setIcon (findIcon (icon))
           else :
              self.value_item.setIcon (icon)

# --------------------------------------------------------------------------

class ItemEditor (QWidget) :
    def __init__ (self, parent = None) :
        super (ItemEditor, self).__init__ (parent)

        self.line_edit = None
        self.combo_box = None
        self.button = None

# --------------------------------------------------------------------------

class ListDelegate (QItemDelegate):

    def __init__ (self, parent=None) :
        super (ListDelegate, self).__init__ (parent)

    def createEditor(self, parent, option, index) :
        editor = ItemEditor (parent)

        layout =  QHBoxLayout (editor)
        layout.setMargin (0)
        layout.setSpacing (0)
        editor.setLayout (layout)

        if True :
           editor.combo_box = QComboBox (editor)
           layout.addWidget (editor.combo_box)
           editor.combo_box.addItems (["abc", "def", "klm"])
        else :
           editor.line_edit = QLineEdit (editor)
           layout.addWidget (editor.line_edit)

        if True :
           print ("Button ...")
           editor.button = QPushButton (editor)
           editor.button.setText ("...")
           editor.button.setMaximumWidth (32)
           layout.addWidget (editor.button)

        return editor

    def setEditorData (self, editor, index) :
        text = index.model().data(index, Qt.DisplayRole).toString()
        if editor.combo_box != None :
           i = editor.combo_box.findText (text)
           if i == -1:
              i = 0
           editor.combo_box.setCurrentIndex (i)

    def setModelData (self, editor, model, index) :
        if editor.combo_box != None :
           model.setData (index, editor.combo_box.currentText())

# --------------------------------------------------------------------------

def setupTreeNode (node, data) :

    text = str (data)
    if text.find ("\n") >= 0 :
       text = " ".join (text.splitlines ())
    if text == "" :
       text = "object"

    type_info = str (type (data))
    text = text + " : " +  type_info

    node.setText (0, text)
    node.setToolTip (0, type_info)
    node.data = data

# --------------------------------------------------------------------------

class Property (QTableWidget) :

   def __init__ (self, win=None, browser=None) :
       super (Property, self).__init__ (win)
       self.win = win
       self.browser = browser
       self.branch = None
       self.data = None
       self.prop_list = [ ]

       self.setColumnCount (2)
       self.setRowCount (1)
       self.setHorizontalHeaderLabels (["Name", "Value"])
       self.horizontalHeader().setStretchLastSection (True)
       self.verticalHeader().setVisible (False)

       self.setContextMenuPolicy (Qt.CustomContextMenu)
       self.customContextMenuRequested.connect (self.onContextMenu)

       header = self.horizontalHeader()
       header.setContextMenuPolicy (Qt.CustomContextMenu)
       header.customContextMenuRequested.connect (self.onContextMenu)

       self.setAlternatingRowColors (True)
       if not use_pyqt6 :
          self.setEditTriggers (QTableWidget.AllEditTriggers) # !?
       self.setSelectionBehavior (QTableWidget.SelectItems)
       self.setSelectionMode (QTableWidget.SingleSelection)


   def showProperty (self, name, value, name_color = None, value_color = None, group = 0) :
       result = PropInfo ()
       result.name = name
       result.group = group

       if isinstance (name, QByteArray) :
          name = str (name)

       link_value = None
       try :
          if value != None and not isinstance (value, int) and not isinstance(value, float) and not isinstance (value, str) :
             link_value = value
       except :
          pass

       item = QTableWidgetItem ()
       item.setText (name)
       item.link_obj = link_value
       item.setFlags (item.flags () & ~ Qt.ItemIsEditable)

       result.name_item = item

       item = QTableWidgetItem ()
       item.setText (str (value))
       item.link_obj = link_value

       if is_variant (value) :
          value = value.toString();
          item.setText (value) # again

       if isinstance (value, QPen) :
          value = value.color ()

       if isinstance (value, QBrush) :
          value = value.color ()

       if isinstance (value, QColor) :
          item.setData (Qt.DecorationRole, value)
          text = value.name ()
          for name in color_map :
             if color_map [name] == value :
                text = name
          item.setText (text) # again

       if isinstance (value, bool) :
          if value :
             state = Qt.Checked
          else :
             state = Qt.Unchecked
          item.setData (Qt.CheckStateRole, state)

       if isinstance (value, dict) :
          txt = "";
          for k in value :
             if len (txt) != 0 :
                txt = txt + ", "
             txt = txt + str (k)
          txt = "{ " + txt + " }"
          item.setText (txt) # again

       if isinstance (value, QTextDocument) :
          result.widget = QTextEdit ()
          result.widget.setDocument (value)

       if hasattr (value, "item_qual") :
          if not isinstance (value, Item) and not isinstance (value, Type) :
             txt = type (value).__name__ + " " + value.item_qual
             item.setText (txt) # again

       if inspect.isbuiltin (value) :
          text = item.text ()
          doc = str (inspect.getdoc (value))
          # if doc != "" :
          text = text + " ... " + doc
          item.setText (text) # again

       if 0 :
          try :
             text = "signature: " + str (inspect.signature (value)) + ", " + text
             item.setText (text) # again
          except :
             pass

       result.value_item = item
       result.setNameColor (name_color)
       result.setValueColor (value_color)
       self.prop_list.append (result)
       return result

   def showDictionary (self, data) :
       for key in data :
           self.showProperty (str (key), data [key])

   def showList (self, data) :
       inx = 0
       for value in data :
           self.showProperty (str (inx), value)
           inx = inx + 1

   def showMethod (self, data) :
       func = data
       name = func.__name__

       self.showProperty ("(type)", type (data).__name__)
       self.showProperty ("(name)", name)

       (args, varargs, keywords, defaults) = inspect.getargspec (func)
       if len (args) == 1 and args[0] == "self" :
          if name.startswith ("is_") or name.startswith ("get_") : # !? cindex functions
             try :
                value = func ()
                self.showProperty ("(result)", value)
             except :
                pass

       self.showProperty ("(args)", args)
       self.showProperty ("(varargs)", varargs)
       self.showProperty ("(keywords)", keywords)
       self.showProperty ("(defaults)", defaults)

       self.showProperty ("(doc)", getattr(func, "__doc__", ""))

       # for key in dir (data) :
       #     value = getattr (data, key)
       #     self.showProperty (key, value)

   def showText (self, data) :
       self.showProperty ("", str (data))

   def addQtProperties (self, data) :
       save = self.prop_list
       self.prop_list = [ ]
       green = findColor ("green")

       typ = data.metaObject ()
       cnt = typ.propertyCount ()
       for inx in range (typ.propertyCount ()) :
           prop = typ.property (inx)
           name = prop.name ()
           value = prop.read (data)
           item = self.showProperty (name, value)
           item.setNameColor (green)
       self.prop_list = self.prop_list + save

   def showClass (self, data) :

       dark_blue = findColor ("#00316e")
       light_blue = findColor ("#0095ff")
       brown = findColor ("brown")

       self.showProperty ("(type)", type (data).__name__,
                          name_color = dark_blue, value_color = dark_blue, group = 1)

       name = getattr (data, "item_name", "")
       if name != "" :
          item = self.showProperty ("(name)", name, name_color = dark_blue, group = 2)
          item.setValueColor (getattr (data, "item_ink", None))
          item.setValuePaper (getattr (data, "item_paper", None))
          item.setValueIcon (getattr (data, "item_icon", None))

       if hasattr (data, "_only_properties_") : # !?

          for key in data._only_properties_ :
              value = getattr (data, key)
              self.showProperty (key, value)

       else :

          # for member in inspect.getmembers (data) :
          #     key, value = member
          #     self.showProperty (key, value)

          # for key in data.__dir__ () :
          #     value = getattr (data, key)
          #     self.showProperty (key, value)

          if hasattr (data, "__dict__") :
             for key in data.__dict__ :
                 value = data.__dict__ [key]
                 self.showProperty (key, value)

          if hasattr (data, "_properties_") :
             for key in data._properties_ :
                 value = getattr (data, key)
                 value = value ()
                 self.showProperty (key, value)

       last = [ "src_file", "src_line", "src_column", "src_pos", "src_end",
                "region_begin", "region_end", "region_begin_file", "region_end_file",
                "item_icon", "item_ink", "item_paper", "item_tooltip",
                "item_expand",
                "item_name", "item_context", "item_qual",
                "item_dict", "item_list",
                "item_decl", "item_used", "item_type", "item_value", "item_body",
                "item_ref",
                "item_origin", "item_place", "item_owner",
                "item_label", "item_block",
                "jump_table", "jump_label", "jump_mark",
                "type_label", "type_decl", "type_args", "type_from",
                "type_const", "type_volatile", "type_signed", "type_unsigned",
                "type_void", "type_bool", "type_char", "type_wchar",
                "type_short", "type_int", "type_long", "type_float", "type_double",
                "alt_assign", "alt_assign_index", "alt_assign_param",
                "alt_read",
                "alt_display", "alt_store",
                "alt_connect", "alt_connect_expr", "alt_connect_cls", "alt_connect_decl", "alt_connect_signal", "alt_connect_src",
                "alt_init", "alt_create", "alt_create_place", "alt_create_owner",
                "alt_setup", "alt_setup_param",
                "alt_move_variable", "alt_move_expr",
                "attr_compile_time", "attr_python", "attr_field", "attr_context",
                "gpu_global",
                "mod_rename", "mod_call", "mod_decl",
                "skip_code", "skip_semicolon" ]

       fields = getattr (data, "_fields_", [ ])
       other = getattr (data, "_other_properties_", { })

       for item in self.prop_list :
           key = item.name
           if item.group == 0 :
              if key in fields :
                 item.group = 100
              elif key in last :
                 item.group = 300 + last.index (key)
                 if key.startswith ("src_") :
                    item.setNameColor (brown)
                 elif key.startswith ("item_") :
                    item.setNameColor (light_blue)
                 elif key.startswith ("alt_") :
                    item.setNameColor (brown)
                 elif key.startswith ("attr_") :
                    item.setNameColor (brown)
                 else :
                    item.setNameColor (dark_blue)
              elif key in other :
                 item.group = 400
              elif key.startswith ("see_") :
                 item.group = 500
                 item.setNameColor (light_blue)
              elif key.startswith ("__") :
                 item.group = 600
              else :
                 # default
                 item.group = 200
                 item.setNameColor (dark_blue)

       self.prop_list.sort (key = lambda item : "%3i" % item.group + item.name)

       if getattr (data, "_qt_properties_", False) :
       # if hasattr (data, "metaObject") :
          "add qt properties"
          self.addQtProperties (data)

   def showProperties (self, data) :
       self.data = data
       self.branch = getattr (data, "link_tree_node", None)
       inx = 0
       for item in self.prop_list :
           if item.widget != None :
              self.setCellWidget (inx, 1, None)
           inx = inx + 1
       self.prop_list = [ ]
       if not (data is None ) : # sometimes == (__eq__) is redefined
          if isinstance (data, list) or isinstance (data, tuple):
             self.showList (data)
          elif isinstance (data, dict) :
             self.showDictionary (data)
          elif inspect.ismethod (data) :
             self.showMethod (data)
          elif isinstance (data, QColor) :
             self.showText (data)
          else :
             self.showClass (data)
       cnt = len (self.prop_list)
       self.setRowCount (cnt)
       inx = 0
       for item in self.prop_list :
           self.setItem (inx, 0, item.name_item)
           if item.widget != None :
              self.setCellWidget (inx, 1, item.widget)
           else :
              self.setItem (inx, 1, item.value_item)
           inx = inx + 1

   def additionalPythonProperties (self) :
       data = self.data

       # for member in inspect.getmembers (data) :
       #     key, value = member
       #     self.showProperty (key, value)

       for key in data.__dir__ () :
           value = getattr (data, key)
           self.showProperty (key, value)

       self.additionalProperties ()

   def additionalQtProperties (self) :
       self.addQtProperties (self.data)
       self.additionalProperties ()

   def additionalProperties (self) :
       old_cnt = self.rowCount ()
       cnt = len (self.prop_list)
       self.setRowCount (cnt)
       inx = 0
       for item in self.prop_list :
           if inx >= old_cnt :
              self.setItem (inx, 0, item.name_item)
              if item.widget != None :
                 self.setCellWidget (inx, 1, item.widget)
              else :
                 self.setItem (inx, 1, item.value_item)
           inx = inx + 1

   def additionalLine (self, name, value) :
       cnt = self.rowCount ()
       self.setRowCount (cnt+1)
       inx = cnt

       item = QTableWidgetItem ()
       item.setText (name)
       self.setItem (inx, 0, item)

       item = QTableWidgetItem ()
       item.setText (str (value))
       item.link_obj = value
       self.setItem (inx, 1, item)

   def additionalLines (self, data_list) :
       cnt = self.rowCount ()
       self.setRowCount (cnt + len (data_list))

       inx = cnt
       for data in data_list :

          item = QTableWidgetItem ()
          item.setText (data [0])
          self.setItem (inx, 0, item)

          item = QTableWidgetItem ()
          item.setText (data [1])
          self.setItem (inx, 1, item)

          inx = inx + 1

   def changeObject (self, data) :
       if self.browser != None :
          self.browser.changeObject (data)
       elif self.branch != None:
          self.changeBranch (data)
       else :
          ObjectBrowser (self.win, data) # create new object browser

   def changeBranch (self, data) :

       node = TreeItem (self.branch)
       setupTreeNode (node, data)
       node.data = None
       node.obj = data
       node.setupTreeItem ()
       self.branch.setExpanded (True)
       self.branch.setSelected (False)
       node.setSelected (True)
       self.branch = node

   def mousePressEvent (self, e) :
       mask = Qt.ShiftModifier | Qt.ControlModifier | Qt.AltModifier | Qt.MetaModifier
       mod = e.modifiers () & mask
       button = e.button ()

       if mod == Qt.ControlModifier and button == Qt.LeftButton:
          # print ("CTRL CLICK")
          item = self.itemAt (mouse_event_pos (e))
          if item != None :
             obj = getattr (item, "link_obj", None)
             if not (obj is None) :
                self.changeObject (obj)

       if mod == Qt.ControlModifier + Qt.ShiftModifier :
          # print ("CTRL SHIFT CLICK")
          if self.browser == None :
             self.changeObject (self.data)

   def onContextMenu (self, pos) :
       item = self.itemAt (pos)
       menu = QMenu (self)
       any = False

       if self.browser == None :
          act = menu.addAction ("show whole object")
          act.triggered.connect (lambda param, self=self, data=self.data : self.changeObject (data))
          any = True

       if getattr (item, "link_obj", None) != None :
          act = menu.addAction ("show this item")
          act.triggered.connect (lambda param, self=self, data=item.link_obj : self.changeObject (data))
          any = True

       act = menu.addAction ("show python properties")
       act.triggered.connect (lambda param, self=self : self.additionalPythonProperties ())
       any = True

       if hasattr (self.data, "metaObject") and not getattr (self.data, "_qt_properties_", False) :
          act = menu.addAction ("show qt properties")
          act.triggered.connect (lambda param, self=self : self.additionalQtProperties ())
          any = True

       if any :
          menu_exec (menu, self.mapToGlobal (QPoint (pos)))

# --------------------------------------------------------------------------

class ObjectBrowser (QDialog) :

   def __init__ (self, win = None, data = None) :
       super (ObjectBrowser, self).__init__ (win)
       self.win = win

       self.treeView = QTreeWidget ()
       self.treeView.currentItemChanged.connect (self.onCurrentItemChanged)
       self.treeView.setHeaderHidden (True)

       self.propView = Property (win = self, browser = self)

       self.splitter = QSplitter ()
       self.splitter.addWidget(self.treeView)
       self.splitter.addWidget(self.propView)
       self.splitter.setStretchFactor (0, 1)
       self.splitter.setStretchFactor (1, 2)

       self.layout = QVBoxLayout ()
       self.layout.addWidget (self.splitter)
       self.setLayout (self.layout)

       self.setWindowTitle ("Object browser")
       self.changeObject (data)

       self.resize (400, 520)
       self.show ()

   def onCurrentItemChanged(self, current, previous) :
       self.propView.showProperties (current.data)

   def changeObject (self, data) :

       target = self.treeView.currentItem ()
       if target != None :
          node = QTreeWidgetItem (target)
          target.setExpanded (True)
       else :
          node = QTreeWidgetItem (self.treeView)

       if not inspect.ismethod (data) : # strange method call (cindex methods)
           setupTreeNode (node, data)

       self.treeView.setCurrentItem (node)

       self.propView.showProperties (data)

# --------------------------------------------------------------------------

if __name__ == '__main__' :
   app = QApplication (sys.argv)
   window = Property ()
   window.show ()
   app.exec_ ()

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
