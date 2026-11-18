
# llvm_import.py - model based tree

from __future__ import print_function

import os, sys

from util import import_qt_modules, findIcon
import_qt_modules (globals ())

from llvm_code import use_clang, clang_compile

if use_clang :
   from clang.cindex import Index, Config, CursorKind, TypeKind, TranslationUnit
   from gcc_options import gcc_options, pkg_options

# clang.cindex.Config.set_library_path ("/usr/lib/llvm")
# clang.cindex.Config.set_library_file ("/usr/lib/llvm/libclang.so")

# --------------------------------------------------------------------------

class ItemData :
   def __init__ (self, above) :
       # super (ItemData, self).__init__ ()

       self.text = ""
       self.icon = None
       self.ink = None

       self.display = False # True => self.cursor is valid
       self.cursor = None

       self.display2 = False # True => self.cursor is valid
       self.cursor2 = None

       self.location = None
       self.start = None
       self.stop = None

       self.subitems = [ ]

       self.up = above

       if above != None :
          above.subitems.append (self)

   def addIcon (self, icon_name) :
       self.icon = findIcon (icon_name)

   def setup (self, cursor) :
       self.cursor = cursor
       self.display = True
       self.cursor2 = cursor
       self.display2 = True

   def clean (self) :
       self.display = False
       self.cursor = None

   def get_subitems (self) :
       if self.display :
          add_subitems (self)
          self.clean ()

# --------------------------------------------------------------------------

def add_subitems (item) :
    for t in item.cursor.get_children () :
        new_item (item, t)

def new_item (above, cursor) :
    txt = str (cursor.spelling)
    txt = str (cursor.kind).replace ("CursorKind.", "", 1) + ": " + txt

    item = ItemData (above)
    item.text = txt
    item.setup (cursor)

    if (cursor.kind == CursorKind.CLASS_DECL or
        cursor.kind == CursorKind.STRUCT_DECL or
        cursor.kind == CursorKind.UNION_DECL) :
            item.addIcon ("code-class")
    elif (cursor.kind == CursorKind.FUNCTION_DECL or
          cursor.kind == CursorKind.CXX_METHOD or
          cursor.kind == CursorKind.CONSTRUCTOR or
          cursor.kind == CursorKind.DESTRUCTOR) :
             item.addIcon ("code-function")
    elif (cursor.kind == CursorKind.VAR_DECL or
          cursor.kind == CursorKind.PARM_DECL or
          cursor.kind == CursorKind.FIELD_DECL) :
             item.addIcon ("code-variable")

    item.location = cursor.location
    item.start = cursor.extent.start
    item.stop = cursor.extent.end

    start = item.start
    stop = item.stop

    if hasattr (start, "file") and hasattr (start.file, "name"):
       pass
    else :
       start = item.location

    if hasattr (start, "file") and hasattr (start.file, "name"):
       item.fileName = start.file.name
       item.line = start.line
       item.column = start.column
       if item.stop.file != None and item.fileName == stop.file.name :
          item.stop_line = stop.line
          item.stop_column = stop.column
       else :
          item.end_line = -1
          item.end_column = -1

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
             result = item.text
          if role == Qt.DecorationRole :
             item = index.internalPointer ()
             if item.icon != None :
                result = item.icon
          if role == Qt.ForegroundRole :
             item = index.internalPointer ()
             if item.ink != None :
                result = item.ink
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
             parentItem.get_subitems ()
             if line < len (parentItem.subitems) :
                childItem = parentItem.subitems [line]
          if childItem != None :
             result = self.createIndex (line, column, childItem)
       return result

   def parent (self, index) :
       result = QModelIndex ()
       if index.isValid () :
          childItem = index.internalPointer ()
          parentItem = childItem.up
          if parentItem != None and parentItem != self.root :
             parentItem.get_subitems ()
             pos = parentItem.subitems.index (childItem)
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
          parentItem.get_subitems ()
          cnt = len (parentItem.subitems)
       return cnt

# --------------------------------------------------------------------------

def add_property (prop, name, value) :
    node = QTreeWidgetItem (prop)
    node.setText (0, name)
    node.setText (1, str (value))
    prop.addTopLevelItem (node)

def show_properties (prop, item) :
    prop.clear ()
    if item.display2 :
       obj = item.cursor2
       for name in dir (obj) :
           try :
              add_property (prop, name, getattr (obj, name))
           except :
              pass

# --------------------------------------------------------------------------

def getCompletionList (self) :
       result = [ ]

       fileName = ""
       for edit_name in self.win.editors :
           if self.win.editors [edit_name] == self :
              fileName = edit_name

       tu = self.win.translation_unit
       if tu != None :
          # print ("using CLang completion")
          tu.reparse ()
          cursor = self.textCursor ()
          # fileName = self.getFileName ()
          line = cursor.blockNumber () + 1
          column = columnNumber (cursor) + 1
          source = self.toPlainText ()
          answer = tu.codeComplete (fileName, line, column,
                      unsaved_files = [ (fileName, source) ],
                      include_macros = True,
                      include_code_patterns = True,
                      include_brief_comments = True)

          for t in answer.results :
             print (t)
             item = QStandardItem (str (t))
             result.append (item)

       return result

# --------------------------------------------------------------------------

class LlvmTree (QWidget):

    def __init__ (self, win=None):
        super (LlvmTree, self).__init__ (win)
        self.win = win

        self.translation_unit = None
        self.translation_index = None
        self.source_model = None
        self.filter_model = None

        self.filterLine = QLineEdit ()
        self.treeView = QTreeView ()

        self.treeView.setHeaderHidden (True)

        self.layout = QVBoxLayout ()
        self.layout.addWidget (self.filterLine)
        self.layout.addWidget (self.treeView)
        self.layout.setContentsMargins (0, 0, 0, 0)

        self.setLayout (self.layout)

        self.treeView.clicked.connect (self.treeView_clicked)
        self.filterLine.textChanged.connect (self.filterLine_textChanged)

    def treeView_clicked (self, index) :
        item = self.filter_model.mapToSource (index).internalPointer ()
        txt = ""
        if hasattr (item, "fileName") :
           txt = item.text + ": " + item.fileName + ", line: " + str (item.line) + ", column: " + str (item.column)
           self.win.loadFile (item.fileName, item.line, item.column) # item.stop_line, item.stop_column)

        self.win.showProperties (item)
        if item.display2 :
           for name in dir (item.cursor2) :
               try :
                  value = getattr (item.cursor2, name)
                  self.win.prop.additionalLine (name, value)
               except :
                  pass

        self.win.showStatus (txt)

    def filterLine_textChanged (self, text) :
        if self.filter_model != None :
           self.filter_model.setFilterFixedString (text)

    def complete (self):
        if self.translation_unit != None :

           fileName = ""
           edit = self.editTabs.currentWidget ()
           for name in self.editors :
               if self.editors [name] == edit :
                  fileName = name

           cursor = edit.textCursor ()
           line = cursor.blockNumber () + 1
           column = cursor.positionInBlock () + 1

           print (fileName, str (line), str (column))

           answer = self.translation_unit.codeComplete (fileName, line, column,
                                                        unsaved_files=None,
                                                        include_macros=False,
                                                        include_code_patterns=False,
                                                        include_brief_comments=False)
           if answer != None :
              menu = QMenu (self);
              for t in answer.results :
                 print (t)
                 for u in t.string :
                   if u.isKindTypedText () :
                      action = QAction (u.spelling, menu)
                      menu.addAction (action)
              # menu.exec_ (QCursor.pos())

    def translate (self, args) :
        for arg in args :
            if os.path.isfile (arg) :
               self.win.loadFile (arg)

        # print ("ARGS:", args)
        index = Index.create ()
        tu = index.parse (None, args)
        if tu :
           for item in tu.diagnostics :
               print (item)

           # tu.save (self.win.outputFileName ("llvm.data"))

           # tu.reparse ()
           self.show_translation_unit (index, tu)

    def show_translation_unit (self, index, tu) :
        top = ItemData (None)
        top.text = "translation unit"
        top.addIcon  ("text-plain");

        # tst = ItemData (top)
        # tst.text = "test item"
        # tst.addIcon ("text-plain");
        # tst.ink = QColor ("blue")

        self.translation_index = index # important, keep index
        self.translation_unit = tu

        top.setup (tu.cursor)
        add_subitems (top)
        top.clean ()

        # self.model = TreeModel (self, top)
        # self.treeView.setModel (self.model)

        self.source_model = TreeModel (self, top)
        self.filter_model = QSortFilterProxyModel (self)
        self.filter_model.setSourceModel (self.source_model)
        self.filter_model.setFilterFixedString (self.filterLine.text ())
        self.treeView.setModel (self.filter_model)

        item = self.treeView.model().index (0, 0, QModelIndex ())
        self.treeView.expand (item)

# --------------------------------------------------------------------------

def llvm_tree (win, fileName) :
    if not use_clang :
       print ("MISSING clang")
    else :
       t = LlvmTree (win)
       win.leftTabs.addTab (t, "LLVM Tree")
       win.showTab (t)
       win.showSideTabAction (win.tabsMenu, "LLVM Tree", t, "Meta+J", "")
       opts = gcc_options ("clang")
       opts = opts + pkg_options ("Qt5Widgets")
       other = [ ]
       # other = ["-S", "-emit-llvm" ]
       t.translate (other + [fileName] + opts)
   
# --------------------------------------------------------------------------

# Debian 9: apt-get install clang-7 llvm-7 python-clang-7

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
