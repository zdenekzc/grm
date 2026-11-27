#!/usr/bin/env python

import os, sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

# from input import fileNameToIndex, indexToFileName

from util import *
from edit import Editor

# --------------------------------------------------------------------------

# class TreeItem
#    src_file
#    src_line
#    src_column
#    src_pos

# --------------------------------------------------------------------------

class TreeItem (QTreeWidgetItem) :
   def __init__ (self, parent, text = "") :
       super (TreeItem, self).__init__ (parent)
       self.setText (0, text)

   def addIcon (self, icon_name) :
       self.setIcon (0, findIcon (icon_name))

   def addToolTip (self, text) :
       self.setToolTip (0, text)

   def setInk (self, color_name) :
       self.setForeground (0, findColor (color_name))

   def setPaper (self, color_name) :
       self.setBackground (0, findColor (color_name))

   # -----------------------------------------------------------------------

   def setupTreeItem (self) :
       tree_node = self
       obj = tree_node
       if hasattr (obj, "obj") :
          obj = obj.obj
       elif getattr (obj, "item_decl", None) != None : # typically in ident_expr
          obj = obj.item_decl

       if hasattr (obj, "item_icon") :
          if isinstance (obj.item_icon, str) :
             tree_node.setIcon (0, findIcon (obj.item_icon))
          elif isinstance (obj.item_icon, QIcon) :
             tree_node.setIcon (0, obj.item_icon)

       if getattr (obj, "item_tooltip", None) != None :
          tree_node.setToolTip (0, obj.item_tooltip)

       if hasattr (obj, "item_ink") :
          if isinstance (obj.item_ink, str) :
             tree_node.setForeground (0, findColor (obj.item_ink))
          elif obj.item_ink != None :
             tree_node.setForeground (0, obj.item_ink)

       if hasattr (obj, "item_paper") :
          if isinstance (obj.item_paper, str) :
             tree_node.setBackground (0, findColor (obj.item_paper))
          elif obj.item_paper != None :
             tree_node.setBackground (0, obj.item_paper)

# --------------------------------------------------------------------------

def treeItemCoordinates (obj) :

    fileName = None
    line = None
    column= None
    pos = None

    if hasattr (obj, "src_file") :
       fileName = indexToFileName (obj.src_file)

    if hasattr (obj, "src_line") :
       line = obj.src_line

    if hasattr (obj, "src_column") :
       column = obj.src_column

    if hasattr (obj, "src_pos") :
       pos = obj.src_pos

    return (fileName, line, column, pos)

# --------------------------------------------------------------------------

def treeItemLocation (tree_node) :

    fileName = None
    line = None
    column = None
    pos = None

    saveFileName = None

    "fileName, line, column (from node to root)"
    node = tree_node
    save_node = None
    while node != None and (fileName == None or line == None) :
       fileName, line, column, pos = treeItemCoordinates (node)
       if saveFileName == None :
          saveFileName = fileName
       node = node.parent ()

    if line == None or line == 0:
       "again with objects"
       node = tree_node

       fileName = None
       line = None
       column = None
       pos = None

       while node != None and (fileName == None or line == None) :
          obj = getattr (node, "obj", None)
          if obj != None :
             fileName, line, column, pos = treeItemCoordinates (obj)
          if saveFileName == None :
             saveFileName = fileName
          node = node.parent ()

    if fileName == None :
       fileName, line, column, pos = saveFileName, None, None, None

    return (fileName, line, column, pos)

# --------------------------------------------------------------------------

def treeItemSource (win, node) :
    if win != None :
       fileName, line, column, pos = treeItemLocation (node)
       if fileName != None :

          text = "file: " + fileName
          if line != None :
             text = text + ", line: " + str (line)
             if column != None :
                text = text + ", column: " + str (column)
          win.showStatus ("tree item: " + text)

          edit = win.loadFile (fileName, line, column)
          if edit != None and line == None and pos != None :
             edit.selectLineByPosition (pos)

# --------------------------------------------------------------------------

def treeItemProperties (win, node) :
    if win != None :
       obj = getattr (node, "obj", None)
       if obj != None :
          win.showProperties (obj)
       else :
          win.showProperties (node)

# --------------------------------------------------------------------------

class Tree (QTreeWidget):

    def __init__ (self, win = None) :
        super (Tree, self).__init__ (win)
        self.win = win

        self.header ().hide ()
        self.setAlternatingRowColors (True)

        self.setContextMenuPolicy (Qt.CustomContextMenu)
        self.customContextMenuRequested.connect (self.onContextMenu)

        # self.setDragDropMode (self.DragDrop)
        # self.setDragDropMode (self.InternalMove)

        self.setDragEnabled (True)
        self.viewport().setAcceptDrops (True) # <-- accept draging from another widgets

        self.setDropIndicatorShown (True)
        self.setSelectionMode (QAbstractItemView.SingleSelection)

        self.setAcceptDrops (True)

        self.setExpandsOnDoubleClick (False)
        self.itemExpanded.connect (self.onItemExpanded)
        self.itemSelectionChanged.connect (self.onItemSelectionChanged)
        self.itemActivated.connect (self.onItemActivated) # not used
        self.itemClicked.connect (self.onItemClicked)
        self.itemDoubleClicked.connect (self.onItemDoubleClicked)

    # stackoverflow.com/questions/25222906/how-to-stop-qtreewidget-from-creating-the-item-duplicates-on-drag-and-drop

    def mimeTypes (self) :
        result = empty_qstringlist ()
        result.append ("application/x-view-widget")
        return result

    def supportedDropActions (self) :
        return Qt.CopyAction | Qt.MoveAction

    def dropMimeData (self, target, index, mime, action) :
        if mime.hasFormat ("application/x-view-widget") :
           name = bytearray_to_str (mime.data ("application/x-view-widget"))
           print ("drop", name)
           # self.win.builder.addComponent (name, QPoint (0, 0), target)
           # target == None ... top of tree
           return True
        return False

    def onItemExpanded (self, branch) :
        cnt = branch.childCount ()
        for inx in range (cnt) :
            node = branch.child (inx)
            if getattr (node, "expand_item", False) :
               node.setExpanded (True)

    def expandAllItems (self, node) :
        node.setExpanded (True)
        cnt = node.childCount ()
        inx = 0
        while inx < cnt :
           t = node.child (inx)
           self.expandAllItems (t)
           inx = inx + 1

    def expandFirstItems (self, node) :
        cnt = node.childCount ()
        while cnt > 0 :
           node.setExpanded (True)
           node = node.child (0) # first
           cnt = node.childCount ()

    def expandLastItems (self, node) :
        cnt = node.childCount ()
        while cnt > 0 :
           node.setExpanded (True)
           node = node.child (cnt-1) # last
           cnt = node.childCount ()

    def onItemSelectionChanged (self) :
        # keyboard or mouse
        # print ("SELECTION CHANGED")
        for node in self.selectedItems () :
            treeItemProperties (self.win, node)

    def onItemActivated (self, node, column) :
        # only mouse
        # print ("ITEM ACTIVATED")
        pass

    def onItemClicked (self, node, column) :
        # only mouse
        mask = Qt.ShiftModifier | Qt.ControlModifier | Qt.AltModifier | Qt.MetaModifier
        mod = QApplication.keyboardModifiers () & mask
        if mod == Qt.ControlModifier :
           # print ("CONTROL CLICK")
           self.expandFirstItems (node)
        elif mod == Qt.ShiftModifier :
           # print ("SHIFT CLICK")
           self.expandLastItems (node)
        elif mod == Qt.ShiftModifier | Qt.ControlModifier:
           # print ("CONTROL SHIFT CLICK")
           self.expandAllItems (node)
        else :
           # print ("CLICK")
           pass

    def onItemDoubleClicked (self, node, column) :
        # only mouse
        # print ("DOUBLE CLICK")
        treeItemSource (self.win, node)

    def onContextMenu (self, pos) :
        node = self.itemAt (pos)

        menu = QMenu (self)

        act = menu.addAction ("tree node properties")
        act.triggered.connect (lambda param, win=self.win, node=node: win.showProperties (node))

        if hasattr (node, "obj") :
           act = menu.addAction ("obj properties")
           act.triggered.connect (lambda param, win=self.win, node=node: win.showProperties (node.obj))

        if hasattr (node, "obj") :
           act = menu.addAction ("jump to declaration")
           act.triggered.connect (lambda param, win=self.win, node=node: treeItemSource (win, node))

        if hasattr (node, "obj") :
           obj = node.obj
        else :
           obj = node

        # expand branch

        menu.addSeparator ()

        act = menu.addAction ("expand subitems")
        act.triggered.connect (lambda param, self=self, node=node: self.expandAllItems (node))

        act = menu.addAction ("expand first subitems")
        act.triggered.connect (lambda param, self=self, node=node: self.expandFirstItems (node))

        act = menu.addAction ("expand last subitems")
        act.triggered.connect (lambda param, self=self, node=node: self.expandLastItems (node))

        # show menu

        menu_exec (menu, self.mapToGlobal (QPoint (pos)))

# --------------------------------------------------------------------------

class IconProvider (QFileIconProvider) :
   def __init__ (self) :
       super (IconProvider, self).__init__ ()
       self.database = None
       try :
          self.database = QMimeDatabase ()
       except :
          pass
       self.formats = QImageReader.supportedImageFormats()

   def icon (self, fileInfo) :
       result = None
       if fileInfo.suffix () in self.formats and fileInfo.size () < 10240 :
          result = QIcon (fileInfo.filePath ())
       if result == None or result.isNull() :
          if self.database != None :
             info = self.database.mimeTypeForFile (fileInfo)
             result = QIcon.fromTheme (info.iconName ())
          if result == None or result.isNull() :
             result =  super (IconProvider, self).icon (fileInfo)
       return result

class Files (QTreeView):

   def __init__ (self, win) :
       super (Files, self).__init__ (win)
       self.win = win

       path = QDir.currentPath ()
       # path = "/usr/share/icons"

       model = QFileSystemModel ()
       model.setRootPath (path)
       # model = QDirModel ()

       # model.setReadOnly (True)
       # model.dataChanged.connect (lambda: model.sort (0))
       model.setIconProvider (IconProvider ())

       self.setModel (model)
       self.setCurrentIndex (model.index (path))

       header = self.header ()
       setResizeMode (header, 0, QHeaderView.ResizeToContents)
       setResizeMode (header, 1, QHeaderView.Fixed)
       header.hideSection (2)
       header.hideSection (3)

       self.activated.connect (self.onActivated)

       self.setContextMenuPolicy (Qt.CustomContextMenu)
       self.customContextMenuRequested.connect (self.onContextMenu)

   def onActivated (self, index) :
       if self.win != None :
          fileName = self.model().filePath (index)
          # self.win.showStatus (fileName)
          self.win.loadFile (fileName)

   def onContextMenu (self, pos) :
       menu = QMenu (self)

       prog_dir = sys.path [0]
       dir_list = [ prog_dir, os.path.join (prog_dir, "_output"),  os.path.join (prog_dir, "examples")]
       dir_list = dir_list + qstringlist_to_list (QIcon.themeSearchPaths())
       dir_list = dir_list + qstringlist_to_list (QIcon.fallbackSearchPaths())

       for path in dir_list :
          act = menu.addAction (path)
          act.triggered.connect (lambda param, self=self, path=path: self.showPath (path))

       menu_exec (menu, self.mapToGlobal (QPoint (pos)))

   def showPath (self, path) :
       model = self.model ()
       inx = model.index (path)
       self.setCurrentIndex (inx)

# --------------------------------------------------------------------------

class Documents (Tree) :
   def __init__ (self, win, toolTabs, editTabs) :
       super (Documents, self).__init__ (win)
       self.active = False
       self.win = win
       self.toolTabs = toolTabs
       self.editTabs = editTabs
       self.toolTabs.currentChanged.connect (self.onToolChanged)
       self.editTabs.currentChanged.connect (self.onEditorChanged)
       self.itemActivated.connect (self.onTreeItemActivated)
       self.header ().hide ()

   def onToolChanged (self) :
       self.active = self.toolTabs.currentWidget () == self
       if self.active :
          self.showData ()

   def onEditorChanged (self) :
       if self.active :
          self.showData ()

   def onTreeItemActivated (self, tree_node) :
       if hasattr (tree_node, "widget") :
          self.editTabs.setCurrentWidget (tree_node.widget)

   def showData (self) :
       self.clear ()
       # print ("showDocuments")
       cnt = self.editTabs.count ()
       for inx in range (cnt) :
           w = self.editTabs.widget (inx)
           if isinstance (w, Editor) :
              fileName = w.getFileName ()
              text = os.path.basename (fileName)
              node = TreeItem (self, text)
              node.setToolTip (0, fileName)
              node.fileName = fileName
              node.setIcon (0, findIcon ("document-open"))
              node.widget = w # !?
              node.obj = w # show properties
           else :
              text = self.editTabs.tabText (inx)
              node = TreeItem (self, text)
              node.setIcon (0, findIcon ("document-closed"))
              node.widget = w
              node.obj = w

# --------------------------------------------------------------------------

class Bookmarks (Tree) :
   def __init__ (self, win, toolTabs, editTabs) :
       super (Bookmarks, self).__init__ (win)
       self.active = False
       self.win = win
       self.toolTabs = toolTabs
       self.editTabs = editTabs
       self.toolTabs.currentChanged.connect (self.onToolChanged)

   def onToolChanged (self) :
       self.active = self.toolTabs.currentWidget () == self
       if self.active :
          self.showBookmarks ()

   def activate (self) :
       if self.active :
          self.showBookmarks ()

   def showBookmarks (self) :
       self.clear ()
       # print ("showBookmarks")
       cnt = self.editTabs.count ()
       for inx in range (cnt) :
           editor = self.editTabs.widget (inx)
           any = False
           branch = None
           if isinstance (editor, Editor) :
              fileName = editor.getFileName ()
              bookmarks = editor.getBookmarks ()
              document = None
              for bookmark in bookmarks :
                  if branch == None :
                     text = os.path.basename (fileName)
                     # text = text + " in " + os.path.dirname (fileName)
                     branch = TreeItem (self, text)
                     branch.src_file = fileNameToIndex (fileName)
                     branch.setToolTip (0, fileName)
                     branch.setIcon (0, findIcon ("document-open"))
                     branch.setExpanded (True)
                     document = editor.document ()

                  text = document.findBlockByLineNumber (bookmark.line-1).text ()
                  text = "line " + str (bookmark.line) + ": " + text
                  node = TreeItem (branch, text)
                  node.src_file = branch.src_file
                  node.src_line = bookmark.line
                  node.src_column = bookmark.column
                  node.setIcon (0, findIcon ("bookmarks"))

                  index = bookmark.mark
                  if index >= 1 and index <= len (Editor.bookmark_colors) :
                     node.setBackground (0, Editor.bookmark_colors [index-1])

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
