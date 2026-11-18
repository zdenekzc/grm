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

COLLECTION_NAME = ""
RECORD_NAME = ""

class BoolIO :
   def __init__ (self) :
      super (BoolIO, self).__init__ ()

   def read (self, b, a, name) :
      if a.hasAttribute (name) :
         b = a.value (name).toString () == "true"

   def write (self, b, w, name) :
      w.writeAttribute (name, ("true" if b else "false"))

   def python_write (self, b, w, name) :
      if b :
         w.writeAttribute (name, "true")
      else :
         w.writeAttribute (name, "false")

class IntIO :
   def __init__ (self) :
      super (IntIO, self).__init__ ()

   def read (self, n, a, name) :
      if a.hasAttribute (name) :
         ok = False
         val = a.value (name).toInt (ok)
         if ok :
            n = val

   def write (self, n, w, name) :
      w.writeAttribute (name, str (n))

class StringIO :
   def __init__ (self) :
      super (StringIO, self).__init__ ()

   def read (self, s, a, name) :
      if a.hasAttribute (name) :
         s = a.value (name).qstr.toString ()

   def write (self, s, w, name) :
      w.writeAttribute (name, s)

class StdStringIO :
   def __init__ (self) :
      super (StdStringIO, self).__init__ ()

   def read (self, s, a, name) :
      if a.hasAttribute (name) :
         s = a.value (name).qstr.toString ().toStdString ()

   def write (self, s, w, name) :
      w.writeAttribute (name, QString.fromStdString (s))

def readRecord (reader) :
   result = plastic.Record ()
   attr = reader.attributes ()
   plastic.READ (reader, attr, result)
   return result

def writeRecord (writer, item) :
   writer.writeStartElement (plastic.RECORD_NAME)
   plastic.WRITE (writer, item)
   writer.writeEndElement ()

def readCollection (reader) :
   result = plastic.Collection ()
   while not reader.atEnd () :
      if reader.isStartElement () :
         name = reader.name ().toString ()
         if name == plastic.RECORD_NAME :
            item = set.readRecord (reader)
            result.items.append (item)
      reader.readNext ()
   return result

def writeCollection (writer, data) :
   writer.writeStartElement (plastic.COLLECTION_NAME)
   for item in data.items :
      set.writeRecord (writer, item)
   writer.writeEndElement ()

def readXmlFile (fileName) :
   result = None
   file = QFile (fileName)
   if file.open (QFile.ReadOnly | QFile.Text) :
      reader = QXmlStreamReader (file)
      result = set.readCollection (reader)
   return result

def writeXmlFile (fileName, data) :
   file = QFile (fileName)
   if file.open (QFile.WriteOnly | QFile.Text) :
      writer = QXmlStreamWriter (file)
      writer.setAutoFormatting (True)
      writer.writeStartDocument ()
      set.writeCollection (writer, data)
      writer.writeEndDocument ()

def openXmlFile (window) :
   result = None
   fileName = QFileDialog.getOpenFileName (window, "Open XML file") [0]
   if fileName != "" :
      result = set.readXmlFile (fileName)
   return result

def saveXmlFile (data, window) :
   fileName = QFileDialog.getSaveFileName (window, "Save XML file") [0]
   if fileName != "" :
      set.writeXmlFile (fileName, data)
