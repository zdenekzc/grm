#!/usr/bin/env python

from __future__ import print_function

import sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

class Record :
   def __init__ (self) :
      super (Record, self).__init__ ()

class Collection :
   def __init__ (self) :
      super (Collection, self).__init__ ()
      self.items = [ ]

class var :
   def __init__ (self) :
      super (var, self).__init__ ()

class string :
   def __init__ (self) :
      super (string, self).__init__ ()

class ListIO :
   def __init__ (self) :
      super (ListIO, self).__init__ ()

   def read (self, v, obj, name) :
      if (name in obj) and obj [name].isArray () :
         array = obj [name].toArray ()
         for item in array :
            field.append (readRecord (item.toObject ()))

   def write (self, obj, name) :
      array = []
      for r in field :
         array.append (writeRecord (r))
      obj [name] = array

class ColorIO :
   def __init__ (self) :
      super (ColorIO, self).__init__ ()

   def read (self, c, obj, field_name) :
      if (field_name in obj) and obj [field_name].isString () :
         s = obj [field_name].toString ()
         if QColor.isValidColor (s) :
            c = QColor (s)

   def write (self, c, obj, field_name) :
      obj [field_name] = c.name ()

class BoolIO :
   def __init__ (self) :
      super (BoolIO, self).__init__ ()

   def read (self, b, obj, name) :
      if (name in obj) and obj [name].isBool () :
         b = obj [name].toBool ()

   def write (self, b, obj, name) :
      obj [name] = b

class IntIO :
   def __init__ (self) :
      super (IntIO, self).__init__ ()

   def read (self, n, obj, name) :
      if (name in obj) and obj [name].isDouble () :
         n = obj [name].toInt (0)

   def write (self, n, obj, name) :
      obj [name] = n

class DoubleIO :
   def __init__ (self) :
      super (DoubleIO, self).__init__ ()

   def read (self, v, obj, name) :
      if (name in obj) and obj [name].isDouble () :
         v = obj [name].toDouble (0)

   def write (self, v, obj, name) :
      obj [name] = v

class StringIO :
   def __init__ (self) :
      super (StringIO, self).__init__ ()

   def read (self, s, obj, name) :
      if (name in obj) and obj [name].isString () :
         s = obj [name].toString ()

   def write (self, s, obj, name) :
      obj [name] = s

class StdStringIO :
   def __init__ (self) :
      super (StdStringIO, self).__init__ ()

   def read (self, s, obj, name) :
      if (name in obj) and obj [name].isString () :
         s = obj [name].toString ().toStdString ()

   def write (self, s, obj, name) :
      obj [name] = QString.fromStdString (s)

def readRecord (obj) :
   result = plastic.Record ()
   plastic.READ (result, obj)
   return result

def writeRecord (data) :
   obj = { }
   plastic.WRITE (data, obj)
   return obj

def readCollection (obj) :
   result = plastic.Collection ()
   if ("items" in obj) and obj ["items"].isArray () :
      list = obj ["items"].toArray ()
      for item in list :
         data = set.readRecord (item.toObject ())
         result.items.append (data)
   return result

def writeCollection (data) :
   obj = { }
   array = []
   for item in data.items :
      array.append (set.writeRecord (item))
   obj ["items"] = array
   return obj

def readFile (fileName) :
   result = None
   f = QFile (fileName)
   if f.open (QFile.ReadOnly) :
      code = f.readAll ()
      doc = QJsonDocument.fromJson (code)
      obj = doc.object ()
      result = set.readCollection (obj)
   else :
      QMessageBox.warning (None, "Open File Error", "Cannot read file: " + fileName)
   return result

def writeFile (fileName, input) :
   f = QFile (fileName)
   if f.open (QFile.WriteOnly) :
      obj = set.writeCollection (input)
      doc = QJsonDocument (obj)
      f.write (doc.toJson ())
   else :
      QMessageBox.warning (None, "Save File Error", "Cannot write file: " + fileName)

def openFile (window) :
   result = None
   fileName = QFileDialog.getOpenFileName (window, "Open JSON file") [0]
   if fileName != "" :
      result = set.readFile (fileName)
   return result

def saveFile (input, window) :
   fileName = QFileDialog.getSaveFileName (window, "Save JSON file") [0]
   if fileName != "" :
      set.writeFile (fileName, input)
