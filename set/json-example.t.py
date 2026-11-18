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

class Data :
   def __init__ (self) :
      super (Data, self).__init__ ()
      self.subitems = [ ]

def readItem (obj) :
   result = Item ()
   if ("text" in obj) and obj ["text"].isString () :
      result.text = obj ["text"].toString ()
   if ("selected" in obj) and obj ["selected"].isBool () :
      result.selected = obj ["selected"].toBool ()
   if ("size" in obj) and obj ["size"].isDouble () :
      result.size = obj ["size"].toInt (0)
   if ("value" in obj) and obj ["value"].isDouble () :
      result.value = obj ["value"].toDouble (0)
   return result

def writeItem (data) :
   obj = { }
   obj ["text"] = data.text
   obj ["selected"] = data.selected
   obj ["size"] = data.size
   obj ["value"] = data.value
   return obj

def readData (obj) :
   result = Data ()
   if ("items" in obj) and obj ["items"].isArray () :
      list = obj ["items"].toArray ()
      for item in list :
         data = readItem (item.toObject ())
         result.subitems.append (data)
   return result

def writeData (data) :
   obj = { }
   array = []
   for item in data.subitems :
      array.append (writeItem (item))
   obj ["items"] = array
   return obj

def readFile (fileName) :
   result = None
   f = QFile (fileName)
   if f.open (QFile.ReadOnly) :
      code = f.readAll ()
      doc = QJsonDocument.fromJson (code)
      obj = doc.object ()
      result = readData (obj)
   else :
      QMessageBox.warning (None, "Open File Error", "Cannot read file: " + fileName)
   return result

def writeFile (fileName, input) :
   f = QFile (fileName)
   if f.open (QFile.WriteOnly) :
      obj = writeData (input)
      doc = QJsonDocument (obj)
      f.write (doc.toJson ())
   else :
      QMessageBox.warning (None, "Save File Error", "Cannot write file: " + fileName)

def openFile (window) :
   result = None
   fileName = QFileDialog.getOpenFileName (window, "Open JSON file") [0]
   if fileName != "" :
      result = readFile (fileName)
   return result

def saveFile (input, window) :
   fileName = QFileDialog.getSaveFileName (window, "Save JSON file") [0]
   if fileName != "" :
      writeFile (fileName, input)

class Window (QMainWindow) :
   def __init__ (self) :
      super (Window, self).__init__ ()

      "item"
      self.item = Item ()
      self.item.text = "abc"
      self.item.selected = True
      self.item.size = 7
      self.item.value = 3.14

      "data"
      self.data = Data ()
      self.data.subitems.append (self.item)

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
      self.saveMenuItem.triggered.connect (self.method2)

      "quitMenuItem"
      self.quitMenuItem = QAction (self)
      self.fileMenu.addAction (self.quitMenuItem)
      self.quitMenuItem.setText ("&Quit")
      self.quitMenuItem.setShortcut ("Ctrl+Q")
      self.quitMenuItem.triggered.connect (self.method3)

      "vlayout"
      self.vlayout = QVBoxLayout ()
      temp = QWidget (self)
      temp.setLayout (self.vlayout)
      self.setCentralWidget (temp)

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
      self.name_edit.setText (self.item.text)

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
      self.selected_edit.setChecked (self.item.selected)

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
      self.size_edit.setValue (self.item.size)

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
      self.value_edit.setValue (self.item.value)

   def displayData (self) :
      self.name_edit.setText (self.item.text)
      self.selected_edit.setChecked (self.item.selected)
      self.size_edit.setValue (self.item.size)
      self.value_edit.setValue (self.item.value)

   def storeData (self) :
      self.item.text = self.name_edit.text ()
      self.item.selected = self.selected_edit.isChecked ()
      self.item.size = self.size_edit.value ()
      self.item.value = self.value_edit.value ()

   def method1 (self) :
      self.data = openFile (self)
      self.item = self.data.subitems [0]
      self.displayData ()

   def method2 (self) :
      self.storeData ()
      saveFile (self.data, self)

   def method3 (self) :
      self.close ()

if __name__ == '__main__' :
   appl = QApplication (sys.argv)
   window = Window ()
   window.show ()
   appl.exec_ ()
