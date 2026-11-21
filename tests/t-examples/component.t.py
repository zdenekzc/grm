#!/usr/bin/env python

from __future__ import print_function

import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class Item (QLineEdit) :
   def __init__ (self) :
      super (Item, self).__init__ ()
      self.value = ""

class Simple (QPushButton) :
   def __init__ (self) :
      super (Simple, self).__init__ ()
      self.b = False
      self.c = 0
      self.w = 0
      self.s = 0
      self.i = 0
      self.l = 0
      self.u = 0
      self.v = 0
      self.f = 0.0
      self.d = 3.14
      self.t = "text"

   def add (self, p) :
      self.i += 1

class Example (QMainWindow) :
   def __init__ (self) :
      super (Example, self).__init__ ()

      "mainMenu"
      self.mainMenu = self.menuBar ()

      "file"
      self.file = QMenu (self)
      self.mainMenu.addMenu (self.file)
      self.file.setTitle ("&File")

      "quit"
      self.quit = QAction (self)
      self.file.addAction (self.quit)
      self.quit.setText ("&Quit")
      self.quit.setShortcut ("Ctrl+Q")
      self.quit.triggered.connect (self.method1)

      "toolbar"
      self.toolbar = self.addToolBar ("")

      "tool_button"
      self.tool_button = QToolButton (self)
      self.toolbar.addWidget (self.tool_button)
      self.tool_button.setText ("first")
      self.tool_button.setIcon (QIcon.fromTheme ("weather-clear"))

      "tool_button_2"
      self.tool_button_2 = QToolButton (self)
      self.toolbar.addWidget (self.tool_button_2)
      self.tool_button_2.setText ("second")
      self.tool_button_2.setIcon (QIcon.fromTheme ("applications-toys"))

      "vlayout"
      self.vlayout = QVBoxLayout ()
      temp = QWidget (self)
      temp.setLayout (self.vlayout)
      self.setCentralWidget (temp)

      "hlayout"
      self.hlayout = QHBoxLayout ()
      self.vlayout.addLayout (self.hlayout)

      "button"
      self.button = QPushButton (self)
      self.hlayout.addWidget (self.button)
      self.button.setText ("Abc")
      self.button.clicked.connect (self.method2)

      "check_box"
      self.check_box = QCheckBox (self)
      self.hlayout.addWidget (self.check_box)
      self.check_box.setText ("On")
      self.check_box.setChecked (True)
      self.check_box.toggled.connect (self.method3)

      "edit"
      self.edit = QLineEdit (self)
      self.hlayout.addWidget (self.edit)
      self.edit.setText ("Edit")

      "tree"
      self.tree = QTreeWidget (self)
      self.vlayout.addWidget (self.tree)

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

      "status"
      self.status = self.statusBar ()

      "lab"
      self.lab = QLabel (self)
      self.status.addWidget (self.lab)
      self.lab.setText ("status bar")

   def method1 (self) :
      self.close ()

   def method2 (self) :
      self.button.setText ("Click")

   def method3 (self) :
      if self.check_box.isChecked () :
         self.check_box.setText ("On")
      else :
         self.check_box.setText ("Off")

def func (window) :
   window.tree.expandAll ()
   window.show ()

if __name__ == '__main__' :
   appl = QApplication (sys.argv)
   QIcon.setThemeName ("oxygen")
   window = Example ()
   func (window)
   appl.exec_ ()
