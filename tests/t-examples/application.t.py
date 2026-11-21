#!/usr/bin/env python

from __future__ import print_function

import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

if __name__ == '__main__' :
   appl = QApplication (sys.argv)
   window = QMainWindow ()
   tree = QTreeWidget ()
   root = QTreeWidgetItem ()
   root.setText (0, "root")
   root.setForeground (0, QColor ("brown"))
   tree.addTopLevelItem (root)
   branch = QTreeWidgetItem ()
   branch.setText (0, "branch")
   branch.setForeground (0, QColor ("lime"))
   root.addChild (branch)
   i = 1
   while i <= 3 :
      item = QTreeWidgetItem ()
      item.setText (0, "item " + str (i))
      color_name = ""
      if i == 1 :
         color_name = "red"
      else :
         if i == 2 :
            color_name = "blue"
         else :
            if i == 3 :
               color_name = "orange"
      color = QColor (color_name)
      item.setForeground (0, color)
      branch.addChild (item)
      i += 1
   tree.expandAll ()
   window.setCentralWidget (tree)
   window.show ()
   appl.exec_ ()
