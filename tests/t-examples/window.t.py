#!/usr/bin/env python

from __future__ import print_function

import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class Item :
   def __init__ (self) :
      super (Item, self).__init__ ()
      self.text = ""
      self.selected = False
      self.size = 0
      self.value = 0.0

class Queue :
   def __init__ (self) :
      super (Queue, self).__init__ ()
      self.subitems = [ ]

class Dialog (QDialog) :

   def __init__ (self, parent, data) :
      super (Dialog, self).__init__ (parent)
      self.data = data

      "vlayout"
      self.vlayout = QVBoxLayout ()
      self.setLayout (self.vlayout)

      "name_layout"
      self.name_layout = QHBoxLayout ()
      self.vlayout.addLayout (self.name_layout)

      "name_label"
      self.name_label = QLabel (self)
      self.name_layout.addWidget (self.name_label)
      self.name_label.setText ("text")

      "name_edit"
      self.name_edit = QLineEdit (self)
      self.name_layout.addWidget (self.name_edit)
      self.name_edit.setText (self.data.text)

      "selected_layout"
      self.selected_layout = QHBoxLayout ()
      self.vlayout.addLayout (self.selected_layout)

      "selected_label"
      self.selected_label = QLabel (self)
      self.selected_layout.addWidget (self.selected_label)
      self.selected_label.setText ("selected")

      "selected_edit"
      self.selected_edit = QCheckBox (self)
      self.selected_layout.addWidget (self.selected_edit)
      self.selected_edit.setChecked (self.data.selected)

      "size_layout"
      self.size_layout = QHBoxLayout ()
      self.vlayout.addLayout (self.size_layout)

      "size_label"
      self.size_label = QLabel (self)
      self.size_layout.addWidget (self.size_label)
      self.size_label.setText ("size")

      "size_edit"
      self.size_edit = QSpinBox (self)
      self.size_layout.addWidget (self.size_edit)
      self.size_edit.setValue (self.data.size)

      "value_layout"
      self.value_layout = QHBoxLayout ()
      self.vlayout.addLayout (self.value_layout)

      "value_label"
      self.value_label = QLabel (self)
      self.value_layout.addWidget (self.value_label)
      self.value_label.setText ("value")

      "value_edit"
      self.value_edit = QDoubleSpinBox (self)
      self.value_layout.addWidget (self.value_edit)
      self.value_edit.setValue (self.data.value)

class ColorButton (QToolButton) :

   def getPixmap (self) :
      pixmap = QPixmap (12, 12)
      pixmap.fill (Qt.transparent)
      painter = QPainter (pixmap)
      painter.setPen (Qt.NoPen)
      painter.setBrush (QBrush (self.color))
      painter.drawEllipse (0, 0, 12, 12)
      painter.end ()
      return pixmap

   def __init__ (self, parent, p_name) :
      super (ColorButton, self).__init__ (parent)
      self.name = ""
      self.color = QColor ()
      parent.addWidget (self)
      self.name = p_name
      self.color = QColor (self.name)
      self.setIcon (QIcon (self.getPixmap ()))
      self.setToolTip (self.name)

   def mousePressEvent (self, event) :
      if event.button () == Qt.LeftButton :
         mimeData = QMimeData ()
         mimeData.setColorData (self.color)
         drag = QDrag (self)
         drag.setMimeData (mimeData)
         drag.setPixmap (self.getPixmap ())
         drag.setHotSpot (QPoint (- 16, - 16))
         dropAction = drag.exec_ (Qt.MoveAction | Qt.CopyAction | Qt.LinkAction)

toolFormat = "application/x-tool"
widgetFormat = "application/x-widget"

class ToolButton (QToolButton) :

   def mousePressEvent (self, event) :
      if event.button () == Qt.LeftButton :
         mimeData = QMimeData ()
         mimeData.setData (self.format, bytes (self.name, encoding = "latin1"))
         drag = QDrag (self)
         drag.setMimeData (mimeData)
         drag.setPixmap (self.icon.pixmap (24, 24))
         drag.setHotSpot (QPoint (- 16, - 16))
         dropAction = drag.exec_ (Qt.MoveAction | Qt.CopyAction | Qt.LinkAction)

   def __init__ (self, parent, p_name, p_icon_name = "", p_format = "") :
      super (ToolButton, self).__init__ (parent)
      self.name = ""
      self.icon = QIcon ()
      self.format = ""
      parent.addWidget (self)
      self.name = p_name
      self.format = p_format
      if self.format == "" :
         self.format = toolFormat
      self.setText (self.name)
      self.setToolTip (self.name)

class Block (QGraphicsRectItem) :

   def __init__ (self) :
      super (Block, self).__init__ ()
      self.setAcceptDrops (True)

   def dragEnterEvent (self, event) :
      mime = event.mimeData ()
      if mime.hasColor () :
         event.setAccepted (True)
      else :
         event.setAccepted (False)

   def dropEvent (self, event) :
      mime = event.mimeData ()
      if mime.hasColor () :
         color = mime.colorData ()
         self.setBrush (color)

class AreaView (QGraphicsView) :

   def __init__ (self, parent) :
      super (AreaView, self).__init__ (parent)
      self.scene = None
      self.scene = QGraphicsScene ()
      self.scene.setSceneRect (0, 0, 800, 600)
      self.setScene (self.scene)
      block = Block ()
      block.setRect (0, 0, 200, 120)
      block.setPos (100, 100)
      block.setPen (QColor ("blue"))
      block.setBrush (QColor ("yellow"))
      block.setToolTip ("block")
      block.setFlags (QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
      self.scene.addItem (block)
      i = 1
      while i <= 2 :
         item = QGraphicsEllipseItem ()
         item.setRect (0, 0, 40, 40)
         item.setPos (40 + (i - 1) * 80, 40)
         item.setPen (QColor ("blue"))
         item.setBrush (QColor ("cornflowerblue"))
         item.setToolTip ("item " + str (i))
         item.setFlags (QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable)
         item.setParentItem (block)
         i += 1

class Builder (QWidget) :

   def __init__ (self, parent) :
      super (Builder, self).__init__ (parent)
      self.setAcceptDrops (True)

   def dragEnterEvent (self, event) :
      mime = event.mimeData ()
      if mime.hasFormat (widgetFormat) :
         event.setAccepted (True)

   def dropEvent (self, event) :
      mime = event.mimeData ()
      if mime.hasFormat (widgetFormat) :
         p = event.pos ()
         x = p.x ()
         y = p.y ()
         w = 80
         h = 40
         name = str (mime.data (widgetFormat), "ascii")
         widget = None
         if name == "QPushButton" :
            item = QPushButton (self)
            item.setText ("Button")
            widget = item
         if name == "QCheckBox" :
            item = QCheckBox (self)
            item.setText ("Check Box")
            widget = item
            w = 120
         if name == "QLineEdit" :
            item = QLineEdit (self)
            item.setText ("Line Edit")
            widget = item
            w = 120
         if name == "QTreeWidget" :
            item = QTreeWidget (self)
            widget = item
            w = 200
            h = 120
         if widget != None :
            widget.setParent (self)
            widget.move (x, y)
            widget.resize (w, h)
            widget.setVisible (True)

class MainWin (QMainWindow) :
   def __init__ (self) :
      super (MainWin, self).__init__ ()

      "example"
      self.example = Item ()
      self.example.text = "abc"
      self.example.selected = True
      self.example.size = 7
      self.example.value = 3.14

      "mainMenu"
      self.mainMenu = self.menuBar ()

      "fileMenu"
      self.fileMenu = QMenu (self)
      self.mainMenu.addMenu (self.fileMenu)
      self.fileMenu.setTitle ("&File")

      "openMenuItem"
      self.openMenuItem = QAction (self)
      self.fileMenu.addAction (self.openMenuItem)
      self.openMenuItem.setText ("&Open...")
      self.openMenuItem.setShortcut ("Ctrl+O")
      self.openMenuItem.triggered.connect (self.method1)

      "saveMenuItem"
      self.saveMenuItem = QAction (self)
      self.fileMenu.addAction (self.saveMenuItem)
      self.saveMenuItem.setText ("Save &As...")
      self.saveMenuItem.setShortcut ("Ctrl+S")
      self.saveMenuItem.setEnabled (False)
      self.saveMenuItem.triggered.connect (self.method2)

      "quitMenuItem"
      self.quitMenuItem = QAction (self)
      self.fileMenu.addAction (self.quitMenuItem)
      self.quitMenuItem.setText ("&Quit")
      self.quitMenuItem.setShortcut ("Ctrl+Q")
      self.quitMenuItem.triggered.connect (self.method3)

      "editMenu"
      self.editMenu = QMenu (self)
      self.mainMenu.addMenu (self.editMenu)
      self.editMenu.setTitle ("&Edit")

      "toolbar"
      self.toolbar = self.addToolBar ("")

      "select_button"
      self.select_button = QToolButton (self)
      self.toolbar.addWidget (self.select_button)
      self.select_button.setText ("select")
      self.select_button.setIcon (QIcon.fromTheme ("window-new"))

      "resize_button"
      self.resize_button = QToolButton (self)
      self.toolbar.addWidget (self.resize_button)
      self.resize_button.setText ("resize")
      self.resize_button.setIcon (QIcon.fromTheme ("view-refresh"))

      "connect_button"
      self.connect_button = QToolButton (self)
      self.toolbar.addWidget (self.connect_button)
      self.connect_button.setText ("connect")
      self.connect_button.setIcon (QIcon.fromTheme ("go-jump"))

      "dialog_button"
      self.dialog_button = QToolButton (self)
      self.toolbar.addWidget (self.dialog_button)
      self.dialog_button.setIcon (QIcon.fromTheme ("weather-clear"))
      self.dialog_button.setToolTip ("Dialog")
      self.dialog_button.clicked.connect (self.method4)

      "palette"
      self.palette = QTabWidget (self)
      self.toolbar.addWidget (self.palette)

      "colorPage"
      self.colorPage = QToolBar (self)
      self.palette.addTab (self.colorPage, "colorPage")
      self.palette.setTabText (0, "Colors")
      ColorButton (self.colorPage, "red")
      ColorButton (self.colorPage, "blue")
      ColorButton (self.colorPage, "green")
      ColorButton (self.colorPage, "yellow")
      ColorButton (self.colorPage, "orange")
      ColorButton (self.colorPage, "silver")
      ColorButton (self.colorPage, "gold")
      ColorButton (self.colorPage, "goldenrod")
      ColorButton (self.colorPage, "lime")
      ColorButton (self.colorPage, "lime green")
      ColorButton (self.colorPage, "yellow green")
      ColorButton (self.colorPage, "green yellow")
      ColorButton (self.colorPage, "forest green")
      ColorButton (self.colorPage, "coral")
      ColorButton (self.colorPage, "cornflower blue")
      ColorButton (self.colorPage, "dodger blue")
      ColorButton (self.colorPage, "royal blue")
      ColorButton (self.colorPage, "wheat")
      ColorButton (self.colorPage, "chocolate")
      ColorButton (self.colorPage, "peru")
      ColorButton (self.colorPage, "sienna")
      ColorButton (self.colorPage, "brown")

      "toolPage"
      self.toolPage = QToolBar (self)
      self.palette.addTab (self.toolPage, "toolPage")
      self.palette.setTabText (1, "Tools")
      ToolButton (self.toolPage, "rectangle", "", toolFormat)
      ToolButton (self.toolPage, "ellipse", "", toolFormat)

      "widgetPage"
      self.widgetPage = QToolBar (self)
      self.palette.addTab (self.widgetPage, "widgetPage")
      self.palette.setTabText (2, "Widgets")
      self.palette.setTabToolTip (2, "Widgets")
      ToolButton (self.widgetPage, "QPushButton", "", widgetFormat)
      ToolButton (self.widgetPage, "QCheckBox", "", widgetFormat)
      ToolButton (self.widgetPage, "QLineEdit", "", widgetFormat)
      ToolButton (self.widgetPage, "QTreeWidget", "", widgetFormat)

      "vlayout"
      self.vlayout = QVBoxLayout ()
      temp = QWidget (self)
      temp.setLayout (self.vlayout)
      self.setCentralWidget (temp)

      "hlayout"
      self.hlayout = QHBoxLayout ()
      self.vlayout.addLayout (self.hlayout)

      "leftTabs"
      self.leftTabs = QTabWidget (self)
      self.hlayout.addWidget (self.leftTabs)
      self.leftTabs.setTabPosition (QTabWidget.West)

      "tree"
      self.tree = QTreeWidget (self)
      self.leftTabs.addTab (self.tree, "tree")

      "branch"
      self.branch = QTreeWidgetItem (self.tree)
      self.tree.addTopLevelItem (self.branch)

      "node1"
      self.node1 = QTreeWidgetItem (self.branch)
      self.node1.setText (0, "red")
      self.node1.setForeground (0, QColor ("red"))

      "node2"
      self.node2 = QTreeWidgetItem (self.branch)
      self.node2.setText (0, "green")
      self.node2.setForeground (0, QColor ("green"))

      "node3"
      self.node3 = QTreeWidgetItem (self.branch)
      self.node3.setText (0, "blue")
      self.node3.setForeground (0, QColor ("blue"))

      self.branch.setText (0, "tree branch")
      self.branch.setForeground (0, QColor ("brown"))
      self.branch.setBackground (0, QColor ("orange"))
      self.branch.setIcon (0, QIcon.fromTheme ("folder"))

      self.tree.expandAll ()

      "classes"
      self.classes = QTreeWidget (self)
      self.leftTabs.addTab (self.classes, "classes")

      "tabWidget"
      self.tabWidget = QTabWidget (self)
      self.hlayout.addWidget (self.tabWidget)

      "areaTab"
      self.areaTab = AreaView (self)
      self.tabWidget.addTab (self.areaTab, "areaTab")

      "builderTab"
      self.builderTab = Builder (self)
      self.tabWidget.addTab (self.builderTab, "builderTab")

      "prop"
      self.prop = QTreeWidget (self)
      self.hlayout.addWidget (self.prop)

      "info"
      self.info = QTextEdit (self)
      self.vlayout.addWidget (self.info)

      "status"
      self.status = self.statusBar ()

      "statusLabel"
      self.statusLabel = QLabel (self)
      self.status.addWidget (self.statusLabel)

   def readFile (self, fileName) :
      file = QFile (fileName)
      if file.open (QIODevice.ReadOnly | QIODevice.Text) :
         data = file.readAll ()
         edit = QTextEdit (self)
         codec = QTextCodec.codecForName ("UTF-8")
         text = codec.toUnicode (data)
         edit.setPlainText (text)
         self.tabWidget.addTab (edit, file.fileName ())
         inx = self.tabWidget.count () - 1
         self.tabWidget.setTabToolTip (inx, file.fileName ())
         self.tabWidget.setCurrentIndex (inx)

   def writeFile (self, fileName) :
      pass

   def openFile (self) :
      fileName = QFileDialog.getOpenFileName (self, "Open file") [0]
      if fileName != "" :
         self.readFile (fileName)

   def saveFile (self) :
      fileName = QFileDialog.getSaveFileName (self, "Save file") [0]
      if fileName != "" :
         self.writeFile (fileName)

   def method1 (self) :
      self.openFile ()

   def method2 (self) :
      self.saveFile ()

   def method3 (self) :
      self.close ()

   def method4 (self) :
      dlg = Dialog (self, self.example)
      dlg.show ()

if __name__ == '__main__' :
   appl = QApplication (sys.argv)
   appl.setApplicationName ("qt-demo")
   win = MainWin ()
   win.show ()
   appl.exec_ ()
