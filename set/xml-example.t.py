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

def readItem (reader) :
   result = Item ()
   attr = reader.attributes ()
   if attr.hasAttribute ("text") :
      result.text = attr.value ("text").qstr.toString ()
   elif attr.hasAttribute ("selected") :
      result.selected = attr.value ("selected").toString () == "true"
   elif attr.hasAttribute ("size") :
      ok = False
      val = attr.value ("size").toInt (ok)
      if ok :
         result.size = val
   return result

def writeItem (writer, item) :
   writer.writeStartElement ("Item")
   writer.writeAttribute ("text", item.text)
   writer.writeAttribute ("selected", ("true" if item.selected else "false"))
   writer.writeAttribute ("size", str (item.size))
   writer.writeEndElement ()

def readData (reader) :
   result = Data ()
   while not reader.atEnd () :
      if reader.isStartElement () :
         name = reader.name ().toString ()
         if name == "Item" :
            item = readItem (reader)
            result.subitems.append (item)
      reader.readNext ()
   return result

def writeData (writer, data) :
   writer.writeStartElement ("Data")
   for item in data.subitems :
      writeItem (writer, item)
   writer.writeEndElement ()

def readXmlFile (fileName) :
   result = None
   file = QFile (fileName)
   if file.open (QFile.ReadOnly | QFile.Text) :
      reader = QXmlStreamReader (file)
      result = readData (reader)
   return result

def writeXmlFile (fileName, data) :
   file = QFile (fileName)
   if file.open (QFile.WriteOnly | QFile.Text) :
      writer = QXmlStreamWriter (file)
      writer.setAutoFormatting (True)
      writer.writeStartDocument ()
      writeData (writer, data)
      writer.writeEndDocument ()

def openXmlFile (window) :
   result = None
   fileName = QFileDialog.getOpenFileName (window, "Open XML file") [0]
   if fileName != "" :
      result = readXmlFile (fileName)
   return result

def saveXmlFile (data, window) :
   fileName = QFileDialog.getSaveFileName (window, "Save XML file") [0]
   if fileName != "" :
      writeXmlFile (fileName, data)

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
      self.data = openXmlFile (self)
      self.item = self.data.subitems [0]
      self.displayData ()

   def method2 (self) :
      self.storeData ()
      saveXmlFile (self.data, self)

   def method3 (self) :
      self.close ()

if __name__ == '__main__' :
   appl = QApplication (sys.argv)
   window = Window ()
   window.show ()
   appl.exec_ ()
