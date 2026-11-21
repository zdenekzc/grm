#!/usr/bin/env python

from __future__ import print_function

import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class MyWindow (QWidget) :

   def __init__ (self) :
      super (MyWindow, self).__init__ ()

      "button"
      self.button = QPushButton (self)
      self.button.setText ("Button")
      self.button.move (100, 100)
      self.button.clicked.connect (self.method1)

      self.setup ()

   def setup (self) :
      self.resize (320, 240)
      self.show ()

   def method1 (self) :
      self.button.setText ("Click")

if __name__ == '__main__' :
   appl = QApplication (sys.argv)
   window = MyWindow ()
   window.show ()
   appl.exec_ ()
