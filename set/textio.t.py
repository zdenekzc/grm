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

   def read (self, v, name) :
      if isIdent (name) :
         nextToken ()
         checkSeparator ("=")
         checkSeparator ("[")
         while not isSeparator ("]") :
            v.append (readRecord ())
            if not isSeparator ("]") :
               checkSeparator (",")
         checkSeparator ("]")
         checkSeparator (";")

   def write (self, name) :
      send (name)
      send ("=")
      first = True
      for r in field :
         if first :
            first = False
         else :
            send (",")
         writeRecord (r)
      send (";")
      style_new_line ()

class ColorIO :
   def __init__ (self) :
      super (ColorIO, self).__init__ ()

   def read (self, c, field_name) :
      if isIdent (field_name) :
         nextToken ()
         checkSeparator ("=")
         s = readString ()
         if QColor.isValidColor (s) :
            c = QColor (s)
         checkSeparator (";")

   def write (self, c, field_name) :
      send (field_name)
      send ("=")
      put (c.name ())
      send (";")
      style_new_line ()

class BoolIO :
   def __init__ (self) :
      super (BoolIO, self).__init__ ()

   def read (self, b, name) :
      if isIdent (name) :
         nextToken ()
         checkSeparator ("=")
         b = readBool ()
         checkSeparator (";")

   def write (self, b, name) :
      send (name)
      send ("=")
      putBool (b)
      send (";")
      style_new_line ()

class IntIO :
   def __init__ (self) :
      super (IntIO, self).__init__ ()

   def read (self, n, name) :
      if isIdent (name) :
         nextToken ()
         checkSeparator ("=")
         n = readInt ()
         checkSeparator (";")

   def write (self, n, name) :
      send (name)
      send ("=")
      putInt (n)
      send (";")
      style_new_line ()

class DoubleIO :
   def __init__ (self) :
      super (DoubleIO, self).__init__ ()

   def read (self, v, name) :
      if isIdent (name) :
         nextToken ()
         checkSeparator ("=")
         v = readDouble ()
         checkSeparator (";")

   def write (self, v, name) :
      send (name)
      send ("=")
      putDouble (v)
      send (";")
      style_new_line ()

class StringIO :
   def __init__ (self) :
      super (StringIO, self).__init__ ()

   def read (self, s, name) :
      if isIdent (name) :
         nextToken ()
         checkSeparator ("=")
         s = readString ()
         checkSeparator (";")

   def write (self, s, name) :
      send (name)
      send ("=")
      putString (s)
      send (";")
      style_new_line ()

class StdStringIO :
   def __init__ (self) :
      super (StdStringIO, self).__init__ ()

   def read (self, s, name) :
      if isIdent (name) :
         nextToken ()
         checkSeparator ("=")
         s = readString ().toStdString ()
         checkSeparator (";")

   def write (self, s, name) :
      send (name)
      send ("=")
      putString (QString.fromStdString (s))
      send (";")
      style_new_line ()

def readRecord () :
   result = plastic.Record ()
   plastic.READ (result)
   return result

def writeRecord (data) :
   plastic.WRITE (data)
   return obj

def readCollection () :
   result = plastic.Collection ()
   checkSeparator ("[")
   while not isSeparator ("]") :
      data = set.readRecord ()
      result.items.append (data)
      if not isSeparator ("]") :
         checkSeparator (",")
   checkSeparator ("[")
   return result

def writeCollection (data) :
   put ("[")
   style_new_line ()
   style_indent ()
   first = True
   for item in data.items :
      if first :
         first = False
      else :
         put (",")
         style_new_line ()
      set.writeRecord ()
   style_unindent ()
   put ("]")
   style_new_line ()

def readFile (fileName) :
   result = None
   f = None
   f.open (fileName)
   result = set.readCollection ()
   f.close ()
   return result

def writeFile (fileName, input) :
   f = None
   f.open (fileName)
   set.writeCollection (input)
   f.close ()

def openFile (window) :
   result = None
   fileName = QFileDialog.getOpenFileName (window, "Open data file") [0]
   if fileName != "" :
      result = set.readFile (fileName)
   return result

def saveFile (input, window) :
   fileName = QFileDialog.getSaveFileName (window, "Save data file") [0]
   if fileName != "" :
      set.writeFile (fileName, input)
