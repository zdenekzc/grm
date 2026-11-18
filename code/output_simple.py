
# output_simplefied.py

from __future__ import print_function

import sys, os

from util import import_qt_modules
import_qt_modules (globals ())

from util import findColor, findIcon, Text
from input import fileNameToIndex
from tree import TreeItem

# --------------------------------------------------------------------------

class SimpleSections (object) :
   def __init__ (self, branch, edit) :
       self.branch = branch
       self.init_branch = branch
       self.edit = edit
       self.cursor = self.edit.textCursor ()
       self.fileInx = fileNameToIndex (self.edit.getFileName ())
       self.lineNum = 1
       self.code = ""
       self.shortFileName = os.path.basename (self.edit.getFileName ())
       self.jumpMark = 0

   # text output

   def open (self) :
       self.edit.clear () # empty file

   def close (self) :
       self.cursor.insertText (self.code)
       self.edit.saveFile () # flush

   def write (self, text) :
       self.lineNum = self.lineNum + text.count ('\n')
       self.code += text

   # sections

   def openSection (self, obj) :
       text = ""
       if hasattr (obj, "item_name") :
          text = obj.item_name
       else :
          text = str (obj)
       # print ("openSection", text)

       new_branch = TreeItem (self.branch, text)
       new_branch.obj = obj
       new_branch.src_file = self.fileInx
       new_branch.src_line = self.lineNum
       new_branch.setupTreeItem ()
       self.branch = new_branch

       if not isinstance (obj, str) :
          if not hasattr (obj, "jump_table") :
             obj.jump_table = [ ]
          obj.jump_table.append (self.branch)

       self.branch.jump_label = self.shortFileName
       self.branch.jump_mark = self.jumpMark

   def closeSection (self) :
       if isinstance (self.branch, QTreeWidgetItem) :
          # obj = self.branch.obj
          # if hasattr (obj, "item_name") :
             # print ("closeSection", obj.item_name, obj)

          above = self.branch.parent ()
          # if above != None :
          if isinstance (above, QTreeWidgetItem) :
             self.branch = above
          else :
             self.branch = self.init_branch

   def simpleSection (self, obj) :
       self.openSection (obj)
       self.closeSection ()

   # ink, paper, ...

   def setInk (self, ink) :
       pass

   def setPaper (self, paper) :
       pass

   def addToolTip (self, text, tooltip) :
       pass

   def addDefinition (self, text, defn) :
       pass

   def addUsage (self, text, usage) :
       pass

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
