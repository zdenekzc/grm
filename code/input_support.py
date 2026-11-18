
# support.py

from __future__ import print_function

import sys, os

from util import import_qt_modules
import_qt_modules (globals ())

from util import findColor, findIcon, color_map, get_win, Text
from input import fileNameToIndex, indexToFileName
from tree import TreeItem

# --------------------------------------------------------------------------

class Support (object) :

   def __init__ (self, win, parser) :
       self.win = win
       self.parser = parser

       self.colorInx = 0
       self.regionInx = 0
       self.regions = [ ]

       self.usedFiles = { }

       self.cursor = None
       self.cursor_file_inx = -1

   def refreshCursor (self, fileInx) :
       if fileInx not in self.usedFiles :
          fileName = indexToFileName( (fileInx))
          edit = self.win.loadFile (fileName) # open file if editor does not existsraise
          if edit != None :
             self.win.resetEditorStyle (edit) # reset colors and properties, keep extra selection (bookmarks)
             self.usedFiles [fileInx] = edit
             edit.textCursor ().beginEditBlock ()
       else :
          edit = self.usedFiles [fileInx]

       if edit != None :
          self.cursor = edit.textCursor ()
          self.cursor_file_inx = fileInx
       else :
          self.cursor = None

   def closeSupport (self) :
       for edit in self.usedFiles.values () :
           edit.textCursor ().endEditBlock ()

   def selectToken (self, prev = False) :
       if prev :
          # select previous token
          self.refreshCursor (self.parser.prevFileInx)
          if self.cursor != None :
             self.cursor.setPosition (self.parser.prevByteOfs)
             self.cursor.setPosition (self.parser.prevEndOfs, QTextCursor.KeepAnchor)
       else :
          # select following token
          self.refreshCursor (self.parser.tokenFileInx)
          if self.cursor != None :
             self.cursor.setPosition (self.parser.tokenByteOfs)
             self.cursor.setPosition (self.parser.charByteOfs, QTextCursor.KeepAnchor)

   # colors

   def nextColor (self) :
       h = (35 * self.colorInx) % 360
       # h = (60 * self.colorInx) % 360
       color = QColor.fromHsv (h, 255, 255)
       self.colorInx = self.colorInx + 1
       return color

   def nextRegionColor (self) :
       h = (45 * self.regionInx) % 300
       color = QColor.fromHsv (h, 255, 255).lighter (195)
       self.regionInx = self.regionInx + 1
       return color

   def colorByName (self, name) :
       c = None
       if name in color_map : # is it color name
          c = color_map [name]
          h = c.hue ()
          if h < 0 :
             v = c.value ()
             if v < 16 or v > 240 :
                c = None
       return c

   # color region

   def openRegion (self, obj) :
       self.regions.append (obj)
       obj.region_begin = self.parser.tokenByteOfs
       obj.region_begin_file = self.parser.tokenFileInx

   def closeRegion (self) :
       obj = self.regions.pop ()
       obj.region_end = self.parser.prevEndOfs
       obj.region_end_file = self.parser.prevFileInx

       # paper color
       if len (self.regions) == 0 :
          if obj.region_begin_file == obj.region_end_file :
             self.refreshCursor (obj.region_begin_file)
             if self.cursor != None :
                self.cursor.setPosition (obj.region_begin)
                self.cursor.setPosition (obj.region_end, QTextCursor.KeepAnchor)

                fmt = self.cursor.blockFormat ()
                color = self.nextRegionColor ()
                fmt.setBackground (color)
                self.cursor.setBlockFormat (fmt)

   # include files - display in project tree

   def openingInclude (self) :
       fileName = self.parser.getFileName ()
       self.win.projectOpenInclude (fileName)

   def closingInclude (self) :
       self.win.projectCloseInclude ()

   # text completion area

   def openCompletion (self, obj, outside = False) :
       self.selectToken (prev = not outside)
       if self.cursor != None :
          fmt = self.cursor.charFormat ()
          fmt.setProperty (Text.openProperty, obj.item_qual)
          self.cursor.setCharFormat (fmt)

   def closeCompletion (self, obj, outside = False) :
       self.selectToken (prev = outside)
       if self.cursor != None :
          fmt = self.cursor.charFormat ()
          fmt.setProperty (Text.closeProperty, obj.item_qual)
          self.cursor.setCharFormat (fmt)

   # token definition / usage

   def selectColor (self, obj, defn = True, table = "") :
       color = None
       back_color = None

       # color = self.nextColor ()

       if hasattr (obj, "item_ink") :
          color = obj.item_ink
       if hasattr (obj, "item_paper") :
          back_color = obj.item_paper

       if not defn :
          decl = getattr (obj, "item_decl", None)

          if decl != None :
             if hasattr (decl, "item_ink") :
                color = decl.item_ink
             if hasattr (decl, "item_paper") :
                back_color = decl.item_paper

       if hasattr (obj, "item_name") :
          c = self.colorByName (obj.item_name)
          if c != None : # found color with name
             color = c
             # back_color = c.lighter (180)

       if color == None :
          # print ("selectColor", "name=", getattr (obj, "item_name", "?"), "colorInx=", self.colorInx, obj)
          if table == "" :
             color = self.nextColor ()
          else :
             color = getattr (self.win, table).nextColor ()

       # if back_color == None :
       #    # (h, s, v, a) = color.getHsv ()
       #    # h = (h + 30) % 360
       #    # back_color = QColor.fromHsv (h, s, v)
       #    back_color = color
       #    back_color = back_color.lighter (180)
       #    # back_color = self.nextColor ().lighter (180)

       obj.item_ink = color
       obj.item_paper = back_color
       # self.parser.info ("selectColor name=" + getattr (obj, "item_name", "?") + ", color=" + color.name () + ", colorInx=" + str(self.colorInx))

   def findObject (self, obj) :
       pos_found = False
       if hasattr (obj, "src_pos") and hasattr (obj, "src_end") : # !?
             self.refreshCursor (obj.src_file)
             if obj.src_pos != -1 and obj.src_end != -1 and self.cursor != None :
                self.cursor.setPosition (obj.src_pos)
                self.cursor.setPosition (obj.src_end, QTextCursor.KeepAnchor)
                pos_found = True
       return pos_found

   def markObject (self, obj, ref = None, defn = False) :

       if ref == None :
          ref = obj

       # self.selectColor (obj, defn) # !?
       color = getattr (ref, "item_ink", None)
       back_color = getattr (ref, "item_paper", None)
       info = getattr (ref, "item_qual", None)

       pos_found = self.findObject (obj)

       if pos_found :
          # set attributes
          fmt = self.cursor.charFormat ()
          if color != None :
             fmt.setForeground (color)
          if back_color != None :
             fmt.setBackground (back_color)
          if defn :
             fmt.setFontUnderline (True) # important
             if color != None :
                fmt.setUnderlineColor (color)
          if info != None :
             fmt.setProperty (Text.infoProperty, info)
             if defn :
                fmt.setProperty (Text.defnProperty, info)
          elif color != None or back_color != None :
             fmt.setProperty (Text.infoProperty, "") # no highlighting
          self.cursor.setCharFormat (fmt)

   def markDefn (self, obj) :
       self.markObject (obj, defn = True)

   def markUsage (self, obj, ref_obj = None) :
       self.markObject (obj, ref_obj, defn = False)

   def markOwner (self, obj, owner) :
       pos_found = self.findObject (obj)
       if pos_found :
          fmt = self.cursor.charFormat ()
          fmt.setProperty (Text.ownerProperty, owner)
          self.cursor.setCharFormat (fmt)

   def markText (self, obj, ink = None, paper = None, info = "", tooltip = "") :
       if hasattr (obj, "src_pos") : # !?
          self.refreshCursor (obj.src_file)
          if self.cursor != None :
             self.cursor.setPosition (obj.src_pos)
             self.cursor.setPosition (obj.src_end, QTextCursor.KeepAnchor)
             fmt = self.cursor.charFormat ()
             # fmt.setProperty (Text.infoProperty, "") # no higligting
             if info != "" :
                fmt.setProperty (Text.infoProperty, info)
             if tooltip != "" :
                fmt.setToolTip (tooltip)
             if ink != None :
                fmt.setForeground (ink)
             if paper != None :
                fmt.setBackground (paper)
             self.cursor.setCharFormat (fmt)

   # prev / next function

   def markOutline (self, obj) :
       if hasattr (obj, "item_qual") :
          self.selectToken (prev = True)
          if self.cursor != None :
             fmt = self.cursor.charFormat ()
             fmt.setProperty (Text.outlineProperty, obj.item_qual)
             self.cursor.setCharFormat (fmt)

   # text attributes

   def setInk (self, ink, prev = False) :
       if isinstance (ink, str) :
          ink = findColor (ink)
       self.selectToken (prev)
       if self.cursor != None :
          fmt = self.cursor.charFormat ()
          fmt.setForeground (ink)
          self.cursor.setCharFormat (fmt)

   def setPaper (self, paper, prev = False) :
       if isinstance (paper, str) :
          paper = findColor (paper)
       self.selectToken (prev)
       if self.cursor != None :
          fmt = self.cursor.charFormat ()
          fmt.setBackground (paper)
          self.cursor.setCharFormat (fmt)

   def addToolTip (self, tooltip, prev = False) :
       self.selectToken (prev)
       if self.cursor != None :
          fmt = self.cursor.charFormat ()
          fmt.setToolTip (tooltip)
          self.cursor.setCharFormat (fmt)

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
