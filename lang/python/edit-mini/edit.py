#!/usr/bin/env python

import sys, os

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from util import *

use_highlight = False
try :
    import highlight
    if hasattr (highlight, "Highlighter") :
       use_highlight = True
       print ("found highlight")
except :
    pass

# --------------------------------------------------------------------------

def isLetter (c) :
    return c >= 'A' and c <= 'Z' or c >= 'a' and c <= 'z' or c == '_'

def isDigit (c) :
    return c >= '0' and c <= '9'

def isLetterOrDigit (c) :
    return c >= 'A' and c <= 'Z' or c >= 'a' and c <= 'z' or c == '_' or c >= '0' and c <= '9'

class Highlighter (QSyntaxHighlighter) :

   def __init__ (self, parent = None) :
       super (Highlighter, self).__init__ (parent)
       self.enabled = True
       self.enable_info_property = True

       self.keywordFormat = QTextCharFormat ()
       self.keywordFormat.setForeground (findColor ("darkRed"))

       self.identifierFormat = QTextCharFormat ()
       self.identifierFormat.setForeground (findColor ("darkRed"))

       self.qidentifierFormat = QTextCharFormat ()
       self.qidentifierFormat.setForeground (findColor ("green"))

       self.numberFormat = QTextCharFormat ()
       self.numberFormat.setForeground (findColor ("blue"))

       self.realFormat = QTextCharFormat ()
       self.realFormat.setForeground (findColor ("magenta"))

       self.characterFormat = QTextCharFormat ()
       self.characterFormat.setForeground (findColor ("cornflowerblue"))

       self.stringFormat = QTextCharFormat ()
       self.stringFormat.setForeground (findColor ("blue"))

       self.separatorFormat = QTextCharFormat ()
       self.separatorFormat.setForeground (findColor ("orange"))

       self.commentFormat = QTextCharFormat ()
       self.commentFormat.setForeground (findColor ("gray"))

   def isEnabled (self) :
       return self.enabled

   def setEnabled (self, value) :
       self.enabled = value

   def highlightBlock (self, text) :
       if not self.enabled :
          return

       # print ("highlightBlock", self.currentBlock().blockNumber())

       use_cursor = self.enable_info_property
       if use_cursor :
          cursor = QTextCursor (self.currentBlock())
          cursor_inx = 0

       cnt = len (text)
       inx = 0

       inside_comment = self.previousBlockState () == 1
       start_comment = 0

       while inx < cnt :
          if inside_comment :
             if inx == 0 :
                inx = 1
             while inx < cnt and (text [inx-1] != '*' or text [inx] != '/')  :
                inx = inx + 1
             if inx < cnt:
                inx = inx + 1
                self.setFormat (start_comment, inx-start_comment, self.commentFormat)
                inside_comment = False
          else :

             while inx < cnt and text [inx] <= ' ' :
                inx = inx + 1

             start = inx

             if inx < cnt :
                c = text [inx]

                if use_cursor :
                   cursor.movePosition (QTextCursor.NextCharacter, QTextCursor.MoveAnchor, inx+1-cursor_inx)
                   cursor_inx = inx+1
                   fmt = cursor.charFormat ()

                if isLetter (c) :
                   while inx < cnt and isLetterOrDigit (text [inx]) :
                      inx = inx + 1

                   if use_cursor and fmt.hasProperty (Text.infoProperty) :
                      pass # no higligting for identifier with infoProperty
                   else :
                      if c == 'Q' :
                          self.setFormat (start, inx-start, self.qidentifierFormat)
                      else :
                          self.setFormat (start, inx-start, self.identifierFormat)

                elif isDigit (c) :
                   while inx < cnt and isDigit (text [inx]) :
                      inx = inx + 1
                   if inx < cnt and text [inx] == '.' :
                      inx = inx + 1
                      while inx < cnt and isDigit (text [inx]) :
                         inx = inx + 1
                   if inx < cnt and text [inx] == 'e' :
                      inx = inx + 1
                      if inx < cnt and text [inx] in ['+', '-' ] :
                         inx = inx + 1
                      while inx < cnt and isDigit (text [inx]) :
                         inx = inx + 1
                   while inx < cnt and text [inx] in ['u', 'l', 'f' ] :
                      inx = inx + 1

                   if use_cursor and fmt.hasProperty (Text.infoProperty) :
                      pass # no higligting for identifier with infoProperty
                   else :
                      self.setFormat (start, inx-start, self.numberFormat)

                elif c == '"' :
                   inx = inx + 1
                   while inx < cnt and text [inx] != '"' :
                      inx = inx + 1
                   inx = inx + 1
                   if use_cursor and fmt.hasProperty (Text.infoProperty) :
                      pass # no higligting for identifier with infoProperty
                   else :
                      self.setFormat (start, inx-start, self.stringFormat)

                elif c == '\'' :
                   inx = inx + 1
                   while inx < cnt and text [inx] != '\'' :
                      inx = inx + 1
                   inx = inx + 1
                   if use_cursor and fmt.hasProperty (Text.infoProperty) :
                      pass # no higligting for identifier with infoProperty
                   else :
                      self.setFormat (start, inx-start, self.characterFormat)

                elif c == '/' :
                   inx = inx + 1
                   if inx < cnt and text [inx] == '/' :
                      inx = cnt # end of line
                      self.setFormat (start, inx-start, self.commentFormat)
                   elif inx < cnt and text [inx] == '*' :
                      inx = inx + 1 # skip asterisk
                      inside_comment = True
                      start_comment = inx - 2 # back to slash
                   else :
                      if use_cursor and fmt.hasProperty (Text.infoProperty) :
                         pass # no higligting for identifier with infoProperty
                      else :
                         self.setFormat (start, inx-start, self.separatorFormat)

                else :
                   inx = inx + 1
                   if use_cursor and fmt.hasProperty (Text.infoProperty) :
                      pass # no higligting for identifier with infoProperty
                   else :
                      self.setFormat (start, inx-start, self.separatorFormat)

       if inside_comment :
          self.setFormat (start_comment, inx-start_comment, self.commentFormat)
          self.setCurrentBlockState (1)
       else :
          self.setCurrentBlockState (0)

# --------------------------------------------------------------------------

class CompletionTextEdit (QPlainTextEdit) :

   def __init__ (self, parent = None) :
       super (CompletionTextEdit, self).__init__ (parent)

       self.win = None
       self.completer = None

       self.minLength = 1
       self.automatic_completion = False
       # self.automatic_completion == False ... popup is displayed only when Ctrl+Space is pressed

       localList = [ ]
       localCompleter = QCompleter (localList, self)
       self.setCompleter (localCompleter, filtered = True)

   def setCompleter (self, completer, filtered = False) :
       if self.completer :
           # self.disconnect (self.completer, SIGNAL ("activated(const QString&)"),  self.insertCompletion)
           self.completer.activated.disconnect (self.insertCompletion)
       if completer == None :
           return

       completer.setWidget (self)

       if filtered :
          completer.setCompletionMode (QCompleter.PopupCompletion)
       else :
          completer.setCompletionMode (QCompleter.UnfilteredPopupCompletion)

       completer.setCaseSensitivity (Qt.CaseInsensitive)

       self.completer = completer
       # self.connect (self.completer, SIGNAL ("activated(const QString&)"), self.insertCompletion)
       self.completer.activated.connect (self.insertCompletion)

   def insertCompletion (self, completion) :
       if self.completer.widget() == self :
          tc = self.textCursor ()
          if use_py2_qt4 :
             extra = completion.length() - self.completer.completionPrefix().length()
          else :
             extra = len (completion) - len (self.completer.completionPrefix())
          if extra != 0 :
             tc.movePosition (QTextCursor.Left)
             tc.movePosition (QTextCursor.EndOfWord)
          if use_py2_qt4 :
             tc.insertText (completion.right (extra))
          else :
             tc.insertText (completion [-extra : ])
          self.setTextCursor (tc)

   def textUnderCursor (self) :
       tc = self.textCursor ()
       tc.select (QTextCursor.WordUnderCursor)
       return tc.selectedText ()

   def focusInEvent (self, event) :
       if self.completer :
           self.completer.setWidget (self);
       QPlainTextEdit.focusInEvent (self, event)

   def focusOutEvent (self, event) :
       QPlainTextEdit.focusOutEvent (self, event)

   def keyPressEvent (self, event) :
       if self.completer != None and self.completer.popup().isVisible() :
           if event.key () in (
              Qt.Key_Enter,
              Qt.Key_Return,
              Qt.Key_Escape,
              Qt.Key_Tab,
              Qt.Key_Backtab) :
                 event.ignore ()
                 return

       mask = Qt.ShiftModifier | Qt.ControlModifier | Qt.AltModifier | Qt.MetaModifier
       mod = event.modifiers () & mask

       isShortcut = mod == Qt.ControlModifier and event.key () == Qt.Key_Space # Ctrl + Space

       if self.completer == None or not isShortcut :
           QPlainTextEdit.keyPressEvent (self, event) # do not process the shortcut when we have a completer
           if not self.automatic_completion :
              return

       ctrlOrShift = mod in (Qt.ControlModifier, Qt.ShiftModifier)
       if self.completer == None or (ctrlOrShift and event.text () == "") : # unicode has not isEmpty method
           # ctrl or shift key on it's own
           return

       eow = "~!@#$%^&*()_+{}|:\"<>?,./;'[]\\-=" # end of word
       if use_py2_qt4 :
          eow = QString (eow)

       hasModifier = ((event.modifiers () != Qt.NoModifier) and not ctrlOrShift)

       # completionList = [ ]
       completionList = self.getCompletionList ()
       if self.win.generateCompletionList != None :
          completionList =  completionList + self.win.generateCompletionList ()
       if len (completionList) == 0 :
          completionList = [ "alpha", "beta", "gamma", "delta" ]
       if 0 :
          model = QStringListModel (completionList, self.completer)
       else :
          model = QStandardItemModel (self.completer)
          for obj in completionList :
             if isinstance (obj, str) :
                # item = QStandardItem (findIcon ("class"), obj)
                item = QStandardItem (obj)
             else :
                item = self.createModelItem (obj)
             model.appendRow (item)
       self.completer.setModel (model)

       completionPrefix = self.textUnderCursor ()
       # print ("completion", completionPrefix, "," , completionList)

       if use_py2_qt4 :
          if (not isShortcut
              and (hasModifier or
                   event.text ().isEmpty () or
                   completionPrefix.length () < self.minLength or
                   eow.contains (event.text().right(1)) )) :
              self.completer.popup ().hide ()
              # print ("hide completer")
              return
       else :
          if (not isShortcut
              and (hasModifier or
                   event.text () == "" or
                   len (completionPrefix) < self.minLength or
                   event.text()[-1] in eow )) :
              self.completer.popup ().hide ()
              # print ("hide completer")
              return

       if completionPrefix != self.completer.completionPrefix () :
           self.completer.setCompletionPrefix (completionPrefix)
           popup = self.completer.popup ()
           popup.setCurrentIndex (self.completer.completionModel ().index (0,0))

       cr = self.cursorRect ()
       cr.setWidth (self.completer.popup ().sizeHintForColumn (0) +
                    self.completer.popup ().verticalScrollBar ().sizeHint ().width ())
       self.completer.complete (cr) # popup it

   def createModelItem (self, obj) :
       # see setupTreeItem in tree.py

       item = QStandardItem (obj.item_name)
       item.setToolTip (obj.item_qual)

       if hasattr (obj, "item_icon") :
          if isinstance (obj.item_icon, str) :
             item.setIcon (findIcon (obj.item_icon))
          elif isinstance (obj.item_icon, QIcon) :
             item.setIcon (obj.item_icon)

       if getattr (obj, "item_tooltip", None) != None :
          item.setToolTip (obj.item_tooltip)

       if hasattr (obj, "item_ink") :
          if isinstance (obj.item_ink, str) :
             item.setForeground (findColor (obj.item_ink))
          elif obj.item_ink != None :
             item.setForeground (obj.item_ink)

       if hasattr (obj, "item_paper") :
          if isinstance (obj.item_paper, str) :
             item.setBackground (findColor (obj.item_paper))
          elif obj.item_paper != None :
             item.setBackground (obj.item_paper)

       # column = QStandardItem ("type")
       # item.appendColumn ([column])

       return item

   def getCompletionList (self) :
       return [ "alpha", "beta", "gamma" ]

# http://doc.qt.io/qt-5/qtwidgets-tools-customcompleter-example.html
# http://rowinggolfer.blogspot.cz/2010/08/qtextedit-with-autocompletion-using.html

# --------------------------------------------------------------------------

class IndentationTextEdit (CompletionTextEdit) :

   def __init__ (self, parent = None) :
       super (IndentationTextEdit, self).__init__ (parent)

   def getFileName (self) :
       return ""

   def getCommentMark (self) :
       name, ext = os.path.splitext (self.getFileName ())
       mark = ""
       if ext in [".py", ".sh"] :
          mark = "#"
       else :
          mark = "//"
       return mark

   def linesInSelection (self) :
       cursor = self.textCursor ()
       cursor.beginEditBlock ()
       if cursor.hasSelection () :
           start = cursor.selectionStart ()
           stop = cursor.selectionEnd ()

           cursor.setPosition (stop)
           stop_line = cursor.blockNumber ()

           cursor.setPosition (start)
           start_line = cursor.blockNumber ()

           for n in range (stop_line - start_line + 1) :
               cursor.movePosition (QTextCursor.StartOfLine)
               yield cursor
               cursor.movePosition (QTextCursor.NextBlock)
       else :
           cursor.movePosition (QTextCursor.StartOfLine)
           yield cursor
       cursor.endEditBlock ()

   def comment (self) :
       mark = self.getCommentMark () + " "
       for cursor in self.linesInSelection () :
           cursor.insertText (mark)

   def uncomment (self) :
       mark = self.getCommentMark ()
       for cursor in self.linesInSelection () :
           line = cursor.block().text ()
           inx = 0
           cnt = len (line)
           while inx < cnt and line [inx] <= ' ' :
               cursor.movePosition (QTextCursor.NextCharacter)
               inx = inx + 1
           m = len (mark)
           if inx + m <= cnt and line [ inx : inx + m ] == mark :
              for i in range (m) :
                 cursor.deleteChar ()
              inx = inx + m
              if inx < cnt and line [ inx ] == ' ' :
                 cursor.deleteChar ()

   def indent (self) :
       delta = 1
       for cursor in self.linesInSelection () :
           cursor.insertText (" " * delta)

   def unindent (self) :
       delta = 1
       for cursor in self.linesInSelection () :
           # Grab the current line
           line = cursor.block().text ()

           # If the line starts with a tab character, delete it
           if qstring_starts_with (line, "\t") :
               # Delete next character
               cursor.deleteChar ()
               cursor.insertText (" " * (delta-1))

           # Otherwise, delete all spaces until a non-space character is met
           else :
               for char in line [:delta] :
                   if char != " " :
                       break
                   cursor.deleteChar ()

# https://www.binpress.com/tutorial/building-a-text-editor-with-pyqt-part-2/145

# --------------------------------------------------------------------------

class Bookmark (object) :
   def __init__ (self) :
       # self.fileName = ""
       self.line = 0
       self.column = 0
       self.mark = 0

class BookmarkTextEdit (IndentationTextEdit) :

   bookmark_colors = [ QColor (Qt.yellow).lighter (160),
                       QColor (Qt.green).lighter (160),
                       QColor (Qt.blue).lighter (160),
                       QColor (Qt.red).lighter (160),
                       QColor (Qt.gray).lighter (140) ]

   def __init__ (self, parent=None) :
       super (BookmarkTextEdit, self).__init__ (parent)

   def keyPressEvent (self, e) :
       modifiers = e.modifiers ()
       if not (modifiers & Qt.KeypadModifier) :
          mask = Qt.ShiftModifier | Qt.ControlModifier | Qt.AltModifier | Qt.MetaModifier
          mod = modifiers & mask
          key = e.key ()
          if mod == Qt.ControlModifier :
             if key >= Qt.Key_1 and key <= Qt.Key_5 :
                # Ctrl 1 ... Ctrl 5
                self.gotoBookmark (key - Qt.Key_0)
                return
          elif mod == Qt.MetaModifier :
             if key >= Qt.Key_1 and key <= Qt.Key_5 :
                # Win 1 ... Win 5
                self.setBookmark (key - Qt.Key_0)
                return
          elif mod == Qt.ControlModifier | Qt.ShiftModifier :
             # Ctrl Shift 1 ... Ctrl Shift 5
             if key == Qt.Key_Exclam : # ord ('!')
                # self.setBookmark (1)
                self.gotoPrevBookmark (1)
                return
             if key == Qt.Key_At :
                # self.setBookmark (2)
                self.gotoPrevBookmark (2)
                return
             if key == Qt.Key_NumberSign :
                # self.setBookmark (3)
                self.gotoPrevBookmark (3)
                return
             if key == Qt.Key_Dollar :
                # self.setBookmark (4)
                self.gotoPrevBookmark (4)
                return
             if key == Qt.Key_Percent :
                # self.setBookmark (5)
                self.gotoPrevBookmark (5)
                return
       super (BookmarkTextEdit, self).keyPressEvent (e)

   def setBookmark (self, markType = 1) :
       line = self.textCursor ().blockNumber ()
       selections = self.extraSelections ()

       found = False
       inx = 0
       cnt = len (selections)
       while inx < cnt and not found :
          item = selections [inx]
          if item.format.hasProperty (Text.bookmarkProperty) :
             if item.format.intProperty (Text.bookmarkProperty) == markType :
                if item.cursor.blockNumber () == line :
                   del selections [inx]
                   self.setExtraSelections (selections)
                   found = True
          inx = inx + 1

       if not found :
          lineColor = self.bookmark_colors [markType-1]
          item = QTextEdit.ExtraSelection ()
          item.format.setBackground (lineColor)
          item.format.setProperty (Text.bookmarkProperty, markType)
          item.format.setProperty (QTextFormat.FullWidthSelection, create_variant (True))
          item.cursor = self.textCursor ()
          selections.append (item)
          self.setExtraSelections (selections)

       if self.win != None :
          self.win.bookmarks.activate ()

   def gotoBookmark (self, markType = 0) :
       line = self.textCursor ().blockNumber ()
       selections = self.extraSelections ()
       found = False
       for item in selections :
           if not found :
              if item.format.hasProperty (Text.bookmarkProperty) :
                 if item.format.intProperty (Text.bookmarkProperty) == markType :
                    if item.cursor.blockNumber () > line :
                       self.setTextCursor (item.cursor)
                       found = True
       for item in selections :
          if not found :
              if item.format.hasProperty (Text.bookmarkProperty) :
                 if item.format.intProperty (Text.bookmarkProperty) == markType :
                    self.setTextCursor (item.cursor)
                    found = True

   def gotoPrevBookmark (self, markType = 0) :
       line = self.textCursor ().blockNumber ()
       selections = self.extraSelections ()
       found = False
       for item in selections :
           if item.format.hasProperty (Text.bookmarkProperty) :
              if markType == 0 or item.format.intProperty (Text.bookmarkProperty) == markType :
                 if item.cursor.blockNumber () < line :
                    self.setTextCursor (item.cursor)

   def gotoNextBookmark (self, markType = 0) :
       line = self.textCursor ().blockNumber ()
       selections = self.extraSelections ()
       found = False
       for item in selections :
           if not found :
              if item.format.hasProperty (Text.bookmarkProperty) :
                 if markType == 0 or item.format.intProperty (Text.bookmarkProperty) == markType :
                    if item.cursor.blockNumber () > line :
                       self.setTextCursor (item.cursor)
                       found = True

   def clearBookmarks (self) :
       "clear all bookmarks in one document"
       selections = self.extraSelections ()
       inx = 0
       cnt = list_count (selections)
       while inx < cnt :
           if selections [inx].format.hasProperty (Text.bookmarkProperty) :
              del selections [inx]
              cnt = cnt - 1
           else :
              inx = inx + 1
       self.setExtraSelections (selections)
       if self.win != None :
          self.win.bookmarks.activate ()

   def getBookmarks (self) :
       result = [ ]
       selections = self.extraSelections ()
       for item in selections :
           if item.format.hasProperty (Text.bookmarkProperty) :
              cursor = item.cursor
              answer = Bookmark ()
              answer.line = cursor.blockNumber () + 1
              answer.column = columnNumber (cursor) + 1
              answer.mark = item.format.intProperty (Text.bookmarkProperty)
              result.append (answer)
       return result

   def setBookmarks (self, bookmarks) :
       selections = self.extraSelections ()
       max = len (self.bookmark_colors)
       for item in bookmarks :
           item = QTextEdit.ExtraSelection ()
           item.cursor = self.textCursor () # important
           item.cursor.movePosition (QTextCursor.Start)
           if item.line > 0 :
              item.cursor.movePosition (QTextCursor.NextBlock, QTextCursor.MoveAnchor, item.line - 1)

           index = item.mark
           if index < 1 :
              index = 1
           if index > max :
              index = max
           item.format.setBackground (self.bookmark_colors [index-1])
           item.format.setProperty (Text.bookmarkProperty, index)

           item.format.setProperty (QTextFormat.FullWidthSelection, create_variant (True))

           selections.append (item)
       self.setExtraSelections (selections)

# --------------------------------------------------------------------------

class SimpleTextEdit (BookmarkTextEdit) :

   def __init__ (self, parent=None) :
       super (SimpleTextEdit, self).__init__ (parent)

       self.setLineWrapMode (QPlainTextEdit.NoWrap)

       self.setMouseTracking (True) # report mouse move

       if use_highlight :
          self.highlighter = highlight.Highlighter (self.document ()) # compiled version
          print ("using highlight.Highlighter")
       else :
          self.highlighter = Highlighter (self.document ()) # important: keep reference to highlighter

       self.lastCursor = None
       self.lastUnderline = None
       self.lastUnderlineColor = None

       # self.clang_cursor = None
       self.translation_unit = None

       self.cursorPositionChanged.connect (self.onCursorPositionChanged)

   def showStatus (self, text) :
       if self.win != None :
          self.win.showStatus (text)

   def onCursorPositionChanged (self) :
       cursor = self.textCursor ()
       line = cursor.blockNumber () + 1
       column = columnNumber (cursor) + 1
       # self.win.addHistory (self, line, column)

       # if self.win != None and self.win.show_cursor_pos :
       #   self.showStatus ("Line: " + str (line) + " Col: " + str (column))

   def selectLine (self, line) :
       cursor = self.textCursor ()
       cursor.movePosition (QTextCursor.Start)
       cursor.movePosition (QTextCursor.NextBlock, QTextCursor.MoveAnchor, line-1)
       cursor.movePosition (QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
       self.setTextCursor (cursor)
       self.ensureCursorVisible ()

   def selectLineByPosition (self, pos) :
       cursor = self.textCursor ()
       cursor.setPosition (pos)
       cursor.movePosition (QTextCursor.StartOfLine)
       cursor.movePosition (QTextCursor.EndOfLine, QTextCursor.KeepAnchor)
       self.setTextCursor (cursor)
       self.ensureCursorVisible ()

   def select (self, start_line, start_col, stop_line, stop_col) :
       cursor = self.textCursor ()
       cursor.movePosition (QTextCursor.Start)
       cursor.movePosition (QTextCursor.NextBlock, QTextCursor.MoveAnchor, start_line-1)
       cursor.movePosition (QTextCursor.NextCharacter, QTextCursor.MoveAnchor, start_col-1)

       if start_line == stop_line :
          cursor.movePosition (QTextCursor.NextCharacter, QTextCursor.KeepAnchor, stop_col-start_col+1)
       else :
          cursor.movePosition (QTextCursor.NextBlock, QTextCursor.KeepAnchor, stop_line-start_line)
          cursor.movePosition (QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
          cursor.movePosition (QTextCursor.NextCharacter, QTextCursor.KeepAnchor, stop_col)

       self.setTextCursor (cursor)

   def event (self, e) :
       type = e.type()
       "show tooltip for current word"
       if type == QEvent.ToolTip :
          tooltip = ""
          cursor = self.cursorForPosition (e.pos())
          cursor.select (QTextCursor.WordUnderCursor)
          if cursor.selectedText() != "" :
             fmt = cursor.charFormat ()
             if fmt.hasProperty (QTextFormat.TextToolTip) :
                tooltip = fmt.toolTip()
             if tooltip == "" :
               if fmt.hasProperty (Text.defnProperty) :
                  tooltip = fmt.stringProperty (Text.defnProperty)
             if tooltip == "" :
               if fmt.hasProperty (Text.infoProperty) :
                  tooltip = fmt.stringProperty (Text.infoProperty)
          if tooltip != "" :
             QToolTip.showText (e.globalPos(), tooltip)
          else :
             QToolTip.hideText ()
          return True
       else :
          return super (SimpleTextEdit, self).event (e)

   def mouseMoveEvent (self, e) :

       "hide previous cursor underline"
       if self.lastCursor != None :
          fmt = self.lastCursor.charFormat ()
          fmt.setFontUnderline (self.lastUnderline)
          fmt.setUnderlineColor (self.lastUnderlineColor)
          self.lastCursor.setCharFormat (fmt)
          self.lastCursor = None

       mask = Qt.ShiftModifier | Qt.ControlModifier | Qt.AltModifier | Qt.MetaModifier
       mod = e.modifiers () & mask

       "Ctrl Mouse Move : underline word under cursor"
       if mod == Qt.ControlModifier :
          cursor = self.cursorForPosition (mouse_event_pos  (e))
          if cursor.selectedText() == "" :
             cursor.select (QTextCursor.WordUnderCursor)
          fmt = cursor.charFormat ()
          if fmt.hasProperty (Text.defnProperty) :
             self.lastCursor = cursor
             self.lastUnderline = fmt.fontUnderline ()
             self.lastUnderlineColor = fmt.underlineColor ()
             fmt.setFontUnderline (True)
             fmt.setUnderlineColor (Qt.red)
             cursor.setCharFormat (fmt)
          elif fmt.hasProperty (Text.infoProperty) :
             self.lastCursor = cursor
             self.lastUnderline = fmt.fontUnderline ()
             self.lastUnderlineColor = fmt.underlineColor ()
             fmt.setFontUnderline (True)
             fmt.setUnderlineColor (Qt.blue)
             cursor.setCharFormat (fmt)
       super (SimpleTextEdit, self).mouseMoveEvent (e)

   def mouseDoubleClickEvent (self, e) :
       mask = Qt.ShiftModifier | Qt.ControlModifier | Qt.AltModifier | Qt.MetaModifier
       mod = e.modifiers () & mask
       button = e.button ()
       cursor = self.cursorForPosition (mouse_event_pos (e))
       if button == Qt.LeftButton :
          print ("DOUBLE CLICK")
          self.localProperties (cursor)
       super (SimpleTextEdit, self).mouseDoubleClickEvent (e)

   def mousePressEvent (self, e) :
       mask = Qt.ShiftModifier | Qt.ControlModifier | Qt.AltModifier | Qt.MetaModifier
       mod = e.modifiers () & mask
       button = e.button ()
       cursor = self.cursorForPosition (mouse_event_pos (e))
       if button == Qt.LeftButton :

          "Ctrl Mouse : jump to the object recorded in the text format"
          if mod == Qt.ControlModifier :
             print ("CTRL")
             self.localJump (cursor)

          "Ctrl Shift Mouse : show properties of that object"
          if mod == Qt.ControlModifier | Qt.ShiftModifier :
             print ("CTRL SHIFT")
             self.localProperties (cursor)

          "Win Mouse : open file in KDevelop"
          if mod == Qt.MetaModifier :
             print ("WIN")
             self.localKDevelop (cursor)

          if mod == Qt.ShiftModifier : # extend selection on Linux Mate
             print ("SHIFT")

          if mod == Qt.AltModifier : # move window on Linux Mate
             print ("ALT")

          if mod == Qt.AltModifier | Qt.ShiftModifier : # move window on Linux Mate
             print ("ALT SHIFT")

       super (SimpleTextEdit, self).mousePressEvent (e)

   def localProperties (self, cursor) :
       cursor.select (QTextCursor.WordUnderCursor)
       fmt = cursor.charFormat ()
       if fmt.hasProperty (Text.infoProperty) :
          name = str (fmt.stringProperty (Text.infoProperty))
          obj = self.findObjectByName (name)
          if obj != None :
             self.win.showProperties (obj)

   def localJump (self, cursor) :
       cursor.select (QTextCursor.WordUnderCursor)
       fmt = cursor.charFormat ()
       if fmt.hasProperty (Text.infoProperty) :
          name = str (fmt.stringProperty (Text.infoProperty))
          obj = self.findObjectByName (name)
          if obj != None :
             self.jumpToObject (obj)

   def localKDevelop (self, cursor) :
       line = cursor.blockNumber () + 1
       column = columnNumber (cursor) + 1
       self.win.info.goToKDevelop (self.getFileName (), line, column)

   def jumpToObject (self, obj) :
       if obj != None and self.win != None :
          # show properties before editor selection
          self.win.showProperties (obj)

          if hasattr (obj, "src_file") :
             fileName = indexToFileName (obj.src_file)
             line = None
             column = None
             pos = None

             if hasattr (obj, "src_line") :
                line = obj.src_line

             if hasattr (obj, "src_column") :
                column = obj.src_column

             if hasattr (obj, "src_pos") :
                pos = obj.src_pos

             if fileName == self.getFileName () :
                edit = self
             else :
                edit = self.win.loadFile (fileName)

             if edit != None:
                if line != None:
                   edit.selectLine (line)
                elif pos != None :
                   edit.selectLineByPosition (pos)


   def getNavigatorData (self) :
       data = getattr (self, "navigator_data", None)
       return data

   def findObjectByName (self, qual_name) :
       qual_name = str (qual_name)
       # data = self.getNavigatorData ()
       data = self.win.compiler_data
       if data != None :
          name_list = qual_name.split (".")
          for name in name_list :
              answer = None
              if hasattr (data, "item_dict") :
                 answer = data.item_dict.get (name)
              if answer == None and hasattr (data, "registered_scopes") :
                 answer = data.registered_scopes.get (name)
              if answer == None and isinstance (data, dict) : # !?
                 answer = data.get (name)
              if answer == None :
                 return None
              data = answer
       return data

   def findContextName (self, cursor) :
       "identifier from openProperty"
       result = ""
       found = False
       level = 0 # number of closePropert(ies)
       first = True # compare position in first block
       position = cursor.position ()
       block = cursor.block ()
       while not found and block.isValid () :
          begin = block.begin ()

          iterator = block.end ()
          stop = False
          if iterator != begin :
             iterator -= 1 # important
          else :
             stop = True # do not decrement begin iterator
          while not stop and not found :
             fragment = iterator.fragment ();
             ok = True
             if first :
                ok = fragment.position () < position
             if ok :
                fmt = fragment.charFormat ()
                if fmt.hasProperty (Text.closeProperty) :
                   level += 1
                if fmt.hasProperty (Text.openProperty) :
                   if level == 0 :
                      result = str (fmt.stringProperty (Text.openProperty))
                      found = True
                   level -= 1
             if iterator != begin : # inside second while statement
                iterator -= 1
             else :
                stop = True
          block = block.previous ()
          first = False

       return result

   def findContextObject (self, cursor) :
       obj = None
       name = self.findContextName (cursor)
       if name !=  "" :
          obj = self.findObjectByName (name)
       if obj == None :
          data = self.getNavigatorData ()
          if data != None :
             if isinstance (data, QTreeWidgetItem) : # !?
                if data.childCount () == 1 :
                   if getattr (data, "src_file", 0) == 0 :
                      data = data.child (0)
          if data != None :
             fileInx = fileNameToIndex (self.getFileName ())
             line = cursor.blockNumber ()
             column = cursor.columnNumber ()
             if hasattr (data, "item_list") :
                obj = self.searchCompilerData (data, fileInx, line, column)
             elif isinstance (data, QTreeWidgetItem) :
                node = self.searchNavigatorData (data, fileInx, line, column)
                if node != None :
                   obj = getattr (node, "obj", None)
       return obj

   def searchNavigatorData (self, branch, fileInx, line, column) :
       "only for findContextObject"
       result = None
       found_inx = -1
       cnt = branch.childCount ()
       for inx in range (cnt) :
           node = branch.child (inx)
           # print ("search in", node.text (0))
           if getattr (node, "src_file", 0) == fileInx :
                 greater = False # when node has only src_file and no src_line
                 if hasattr (node, "src_line") :
                    # print ("line", node.src_line, " ... ", line)
                    if hasattr (node, "src_column") :
                       greater = node.src_line > line or node.src_line == line and node.src_column >= column
                    else :
                       greater = node.src_line > line
                 if not greater :
                    found_inx = inx
                 else :
                    break

       if found_inx >= 0 :
          node = branch.child (found_inx)
          # print ("found", node.text (0))
          if node.childCount () > 0 :
             # search in sub-tree
             result = self.searchNavigatorData (node, fileInx, line, column)
          if result == None :
             # otherwise use result from this branch
             result = node

       # if result != None :
       #    print ("result", result.text (0))
       return result

   def searchCompilerData (self, branch, fileInx, line, column) :
       "only for findContextObject"
       result = None
       found_node = None
       for node in branch.item_list :
           if getattr (node, "src_file", 0) == fileInx :
                 greater = False # when node has only src_file and no src_line
                 if hasattr (node, "src_line") :
                    # print ("line", node.src_line, " ... ", line)
                    if hasattr (node, "src_column") :
                       greater = node.src_line > line or node.src_line == line and node.src_column >= column
                    else :
                       greater = node.src_line > line
                 if not greater :
                    found_node = node
                 else :
                    break

       if found_node != None  :
          if hasattr (node, "item_list") :
             # search in sub-tree
             result = self.searchCompilerData (found_node, fileInx, line, column)
          if result == None :
             # otherwise use result from this branch
             result = found_node

       # if result != None :
       #    print ("result", result)
       return result

   def displayProperty (self, menu, format, title, property) :
       if format.hasProperty (property) :
          menu.addAction (title + ": " + str (format.stringProperty (property)))

   def getObjectName (self, obj) :
       result = getattr (obj, "item_qual", "")
       if result == "" :
          result = getattr (obj, "name", "") # Rule class
       return result

   def contextMenuEvent (self, e) :
       menu = self.createStandardContextMenu ()

       cursor = self.cursorForPosition (e.pos ())
       self.setTextCursor (cursor) # move cursor to mouse position

       cursor.select (QTextCursor.WordUnderCursor)

       if self.win != None :
          menu.addSeparator ()

          obj = None
          fmt = cursor.charFormat ()
          if fmt.hasProperty (Text.infoProperty) :
             name = str (fmt.stringProperty (Text.infoProperty))
             act = menu.addAction ("Show Memo")
             act.triggered.connect (lambda param, self = self, name = name: self.showMemo (name))

             act = menu.addAction ("Show References")
             # act.setShortcut ("Ctrl+Y")
             act.triggered.connect (lambda param, self = self, name = name: self.showReferences (name))

             obj = self.findObjectByName (name)

          if obj != None :
             act = menu.addAction ("Show Properties")
             act.triggered.connect (lambda param, self = self, obj = obj: self.win.showProperties (obj))

       "again with original cursor - important for column number"
       cursor = self.textCursor ()
       fileName = self.getFileName ()
       line = cursor.blockNumber () + 1
       column = columnNumber (cursor) + 1

       act = menu.addAction ("Go to KDevelop")
       act.triggered.connect (lambda param, self = self, fileName = fileName, line = line, column = column:
                              self.win.info.goToKDevelop (self.getFileName (), line, column))

       act = menu.addAction ("Go to QtCreator")
       act.triggered.connect (lambda param, self = self, fileName = fileName, line = line, column = column:
                              self.win.info.goToQtCreator (self.getFileName (), line, column))

       act = menu.addAction ("Go to Notepad")
       act.triggered.connect (lambda param, self = self, fileName = fileName, line = line, column = column:
                              self.win.info.goToNotepad (self.getFileName (), line, column))

       menu.addSeparator ()

       text = "line: " + str (line)
       text = text + ", column: " + str (column)
       menu.addAction (text)

       # menu.addAction ("selected text: " + cursor.selectedText ())

       # fmt = cursor.charFormat ()
       self.displayProperty (menu, fmt, "tooltip", QTextFormat.TextToolTip)
       self.displayProperty (menu, fmt, "info", Text.infoProperty)
       self.displayProperty (menu, fmt, "defn", Text.defnProperty)
       self.displayProperty (menu, fmt, "owner", Text.ownerProperty)
       # self.displayProperty (menu, fmt, "open", Text.openProperty)
       # self.displayProperty (menu, fmt, "close", Text.closeProperty)
       # self.displayProperty (menu, fmt, "outline", Text.outlineProperty)

       # cursor.select (QTextCursor.BlockUnderCursor)
       # fmt = cursor.blockFormat ()
       # self.displayProperty (menu, fmt, "block tooltip", QTextFormat.TextToolTip)

       menu_exec (menu, e.globalPos())

   def getCompletionList (self) :
       "Completion words: the tree-based context attached to the document."
       result = [ ]
       cursor = self.textCursor ()
       obj = self.findContextObject (cursor)
       if obj == None :
          obj = self.getNavigatorData ()
       while obj != None :
          if hasattr (obj, "item_list") :
             for item in obj.item_list :
                 # result.append (item.item_name)
                 result.append (item)
          obj = getattr (obj, "item_context", None)
       return result

   def getCursorInfo (self) :
       name = ""
       cursor = self.textCursor ()
       cursor.select (QTextCursor.WordUnderCursor)
       fmt = cursor.charFormat ()
       if fmt.hasProperty (Text.infoProperty) :
          name = str (fmt.stringProperty (Text.infoProperty))
       return name

   def showMemo (self, name = "") :
       if name == "" :
          name = self.getCursorInfo ()
       if self.win != None :
          self.win.showMemo (self, name)

   def showReferences (self, name = "") :
       if name == "" :
          name = self.getCursorInfo ()
       if self.win != None :
          self.win.showReferences (self, name)

   def enlargeFont (self) :
       font = self.document().defaultFont()
       if font.pixelSize () > 0 :
          font.setPixelSize (font.pixelSize () + 1)
       else :
          font.setPointSize (font.pointSize () + 1)
       self.document().setDefaultFont (font)

   def shrinkFont (self) :
       font = self.document().defaultFont()
       if font.pixelSize () > 0 :
          if font.pixelSize () > 8 :
             font.setPixelSize (font.pixelSize () - 1)
       else :
          if font.pointSize () > 8 :
             font.setPointSize (font.pointSize () - 1)
       self.document().setDefaultFont (font)

   def moveLines (self, up) :
       cursor = self.textCursor ()
       cursor.beginEditBlock ()

       length = 0
       if not cursor.hasSelection () :
          cursor.movePosition (QTextCursor.StartOfBlock)
          cursor.movePosition (QTextCursor.NextBlock, QTextCursor.KeepAnchor)
          # NO cursor.select (QTextCursor.LineUnderCursor)
       else :
          start = cursor.selectionStart ()
          stop = cursor.selectionEnd ()

          cursor.setPosition (start)
          cursor.movePosition (QTextCursor.StartOfBlock)

          cursor.setPosition (stop, QTextCursor.KeepAnchor)
          if not cursor.atBlockStart () :
             cursor.movePosition (QTextCursor.NextBlock, QTextCursor.KeepAnchor)
             if not cursor.atBlockStart () :
                cursor.movePosition (QTextCursor.End)
                cursor.insertBlock () # to prevent some bug
                cursor.insertBlock () # to prevent some bug
                print ("step 1")
                # again
                cursor.setPosition (start)
                cursor.movePosition (QTextCursor.StartOfBlock)
                cursor.setPosition (stop, QTextCursor.KeepAnchor)
                cursor.movePosition (QTextCursor.NextBlock, QTextCursor.KeepAnchor)
                print ("step 2")
                # return

          length = cursor.selectionEnd () - cursor.selectionStart ()

       self.setTextCursor (cursor) # important
       self.cut ()
       self.setTextCursor (cursor)

       if up :
          cursor.movePosition (QTextCursor.PreviousBlock)
       else :
          cursor.movePosition (QTextCursor.NextBlock)
       self.setTextCursor (cursor)
       self.paste ()

       if length == 0 :
          cursor.movePosition (QTextCursor.PreviousBlock)
       else :
          cursor.setPosition (cursor.position () - length, QTextCursor.KeepAnchor)

       self.setTextCursor (cursor)
       cursor.endEditBlock ()

   def moveLinesUp (self) :
       self.moveLines (True)

   def moveLinesDown (self) :
       self.moveLines (False)

# --------------------------------------------------------------------------

class Editor (SimpleTextEdit) :

   def __init__ (self, parent=None) :
       super (Editor, self).__init__ (parent)

       self.win = self
       self.editorTab = None
       self.findBox = None

       self.origFileName = ""
       self.origTimeStamp = 0
       self.origText = ""
       self.closeWithoutQuestion = False

       "variables for all document tabs, not only editors"
       self.compiler_data = None
       self.navigator_data = None
       self.navigator_tree = None

       setEditFont (self)

   def findText (self) :
       if self.findBox :
          self.findBox.edit = self
          self.copyNonEmptySelectedText ()
          self.findBox.openFind ()

   def findNext (self) :
       if self.findBox :
          self.findBox.edit = self
          self.findBox.findNext ()

   def findPrev (self) :
       if self.findBox :
          self.findBox.edit = self
          self.findBox.findPrev ()

   def replaceText (self) :
       if self.findBox :
          self.findBox.edit = self
          self.copyNonEmptySelectedText ()
          self.findBox.openReplace ()

   def findIncremental (self) :
       self.findText ()
       if self.findBox :
          self.copySelectedText ()
          self.findBox.incremental = True

   def goToLine (self) :
       if self.findBox :
          self.findBox.edit = self
          self.findBox.openGoToLine ()

   def copySelectedText (self) :
       if self.findBox :
          text = self.textCursor ().selectedText ()
          self.findBox.searchCombo.lineEdit().setText (text)

   def copyNonEmptySelectedText (self) :
       if self.findBox :
          text = self.textCursor ().selectedText ()
          if text != "" :
             self.findBox.searchCombo.lineEdit().setText (text)

   def clearSearchResults (self) :
       selections = self.extraSelections ()
       inx = 0
       cnt = list_count (selections)
       while inx < cnt :
           if selections [inx].format.hasProperty (Text.searchProperty) :
              del selections [inx]
              cnt = cnt - 1
           else :
              inx = inx + 1
       self.setExtraSelections (selections)

   # open / save file

   def getFileName (self) :
       return self.origFileName

   def simpleReadFile (self, fileName) :
       f = open (fileName)
       text = f.read ()
       self.setPlainText (text)

   def readFileData (self, fileName) :
       text = ""
       f = QFile (fileName)
       if not f.open (QIODevice.ReadOnly) :
          raise IOError (qstring_to_str (f.errorString()))
       else :
          try :
             stream = QTextStream (f)
             stream.setCodec ("UTF-8")
             text = stream.readAll ()
          except Exception as e :
             QMessageBox.warning (self, "Read File Error", "Cannot read file %s: %s" % (fileName, e))
          finally :
             f.close ()
       return text

   def writeFileData (self, fileName) :
       text = self.toPlainText ()
       f = QFile (fileName)
       if not f.open (QIODevice.WriteOnly) :
              raise IOError (qstring_to_str (f.errorString ()))
       else :
          try :
             stream = QTextStream (f)
             stream.setCodec ("UTF-8")
             stream << text
             self.document ().setModified (False)
             self.origText = text
          except Exception as e :
             QMessageBox.warning (self, "Write File Error", "Failed to save %s: %s" % (fileName, e))
          finally :
             f.close ()
             # QMessageBox.information (self, "File Save", "File written %s" % (fileName))

   def readFile (self, fileName) :
       fileName = os.path.abspath (fileName)
       self.origFileName = fileName
       self.origTimeStamp = os.path.getmtime (fileName)
       text = self.readFileData (fileName)

       self.setExtraSelections ([ ])

       self.setPlainText (text)
       self.document ().setModified (False)
       # self.origText = text
       self.origText = self.toPlainText () # end of lines may be changed

       if not self.highlighter.isEnabled () :
          self.highlighter.setEnabled (True)

       fi = QFileInfo (fileName)
       self.setWindowTitle (fi.fileName ())

   def writeFile (self, fileName) :
       fileName = os.path.abspath (fileName)
       self.origFileName = fileName
       # print ("writeFile", fileName)
       self.writeFileData (fileName)
       self.origTimeStamp = os.path.getmtime (fileName)

   def isModified (self) :
       # return self.document ().isModified ()
       text = self.toPlainText ()
       return text != self.origText

   def isNewerOnDisk (self) :
       result = False
       if os.path.getmtime (self.origFileName) > self.origTimeStamp :
          result = True
       return result

   def isDifferentOnDisk (self) :
       result = False
       text = self.readFileData (self.origFileName)
       if text != self.toPlainText () :
          "text changed"
          result = True
       return result

   def openFile (self) :
       fileName = dialog_to_str (QFileDialog.getOpenFileName (self, "Open File"))
       if fileName != "" :
          self.readFile (fileName)

   def saveFile (self) :
       self.writeFile (self.origFileName)

   def saveFileAs (self) :
       fileName = dialog_to_str (QFileDialog.getSaveFileName (self, "Save File As", self.origFileName))
       if fileName != "" :
          self.writeFile (fileName)

# --------------------------------------------------------------------------

def alt_no_opt () :
    return None

def alt_or (a, b) :
    if a is None :
       return b
    else :
       return a | b

def alt_find (edit, text, opt) :
    if opt is None :
        return edit.find (text)
    else :
       # return edit.find (text, options = opt)
       return edit.find (text, opt)

def alt_find_cursor (edit, text, cursor, opt) :
    if opt is None :
       return edit.find (text, cursor)
    else :
       return edit.find (text, cursor, opt)

# --------------------------------------------------------------------------

class FindBox (QWidget) :

   def __init__ (self, parent = None) :
       super (FindBox, self).__init__ (parent)

       self.edit = None
       self.small = False
       self.incremental = False

       self.red = QColor (Qt.red).lighter (160)
       self.green = QColor (Qt.green).lighter (160)

       self.vlayout = QVBoxLayout ()
       self.setLayout (self.vlayout)

       self.hlayout = QHBoxLayout ()
       self.vlayout.addLayout (self.hlayout)

       self.closeButton = QToolButton ()
       self.closeButton.setIcon (QIcon.fromTheme ("dialog-close"))
       self.closeButton.setShortcut ("Esc")
       self.closeButton.clicked.connect (self.closePressed)
       self.hlayout.addWidget (self.closeButton)

       self.searchLabel = QLabel ()
       self.searchLabel.setText ("Find:")
       self.hlayout.addWidget (self.searchLabel)

       self.searchCombo = QComboBox ()
       self.searchCombo.setEditable (True)
       self.hlayout.addWidget (self.searchCombo)

       self.orig_palette = self.searchCombo.palette ()

       self.clearButton = QToolButton ()
       self.clearButton.setIcon (QIcon.fromTheme ("edit-clear-list"))
       self.clearButton.clicked.connect (self.searchCombo.clearEditText)
       self.hlayout.addWidget (self.clearButton)

       self.wholeWords = QCheckBox ()
       self.wholeWords.setText ("Whole &words")
       self.hlayout.addWidget (self.wholeWords)
       self.wholeWords.toggled.connect (self.updateSearchResults)

       self.matchCase = QCheckBox ()
       self.matchCase.setText ("Match &case")
       self.hlayout.addWidget (self.matchCase)
       self.matchCase.stateChanged.connect (self.updateSearchResults)

       self.regularExpr = QCheckBox ()
       self.regularExpr.setText ("&Regular expr")
       self.hlayout.addWidget (self.regularExpr)
       self.regularExpr.stateChanged.connect (self.updateSearchResults)

       self.nextButton = QPushButton ()
       self.nextButton.setText ("&Next")
       self.nextButton.clicked.connect (self.findNext)
       self.hlayout.addWidget (self.nextButton)

       self.prevButton = QPushButton ()
       self.prevButton.setText ("&Prev")
       self.prevButton.clicked.connect (self.findPrev)
       self.hlayout.addWidget (self.prevButton)

       self.hlayout.setStretch (2, 10)

       # replace text

       self.hlayout2 = QHBoxLayout ()
       self.vlayout.addLayout (self.hlayout2)

       self.replaceLabel = QLabel ()
       self.replaceLabel.setText ("Replace:")
       self.hlayout2.addWidget (self.replaceLabel)

       self.replaceCombo = QComboBox ()
       self.replaceCombo.setEditable (True)
       self.hlayout2.addWidget (self.replaceCombo)

       self.replaceButton = QPushButton ()
       self.replaceButton.setText ("&Replace")
       self.replaceButton.clicked.connect (self.replaceNext)
       self.hlayout2.addWidget (self.replaceButton)

       self.hlayout2.setStretch (1, 10)

       # go to line number

       self.hlayout3 = QHBoxLayout ()
       self.vlayout.addLayout (self.hlayout3)

       self.lineClose = QToolButton ()
       self.lineClose.setIcon (QIcon.fromTheme ("dialog-close"))
       self.lineClose.setShortcut ("Esc")
       self.lineClose.clicked.connect (self.hide)
       self.hlayout3.addWidget (self.lineClose)

       self.lineLabel = QLabel ()
       self.lineLabel.setText ("Go to line:")
       self.hlayout3.addWidget (self.lineLabel)

       self.lineNumber = QSpinBox ()
       self.hlayout3.addWidget (self.lineNumber)

       self.goButton = QPushButton ()
       self.goButton.setText ("Go")
       self.goButton.clicked.connect (self.goToLineNumber)
       self.hlayout3.addWidget (self.goButton)

       self.hlayout3.addStretch ()

       self.searchCombo.lineEdit().returnPressed.connect (self.returnPressed)
       self.searchCombo.editTextChanged.connect (self.textChanged)

       self.lineNumber.editingFinished.connect (self.goToLineNumber)

   def resizeEvent (self, e) :
       w = e.size().width()
       if w < 640 :
          if not self.small :
             self.wholeWords.setText ("&Words")
             self.matchCase.setText ("&Case")
             self.regularExpr.setText ("&Regular")
             self.small = True
       else :
          if self.small :
             self.wholeWords.setText ("Whole &words")
             self.matchCase.setText ("Match &case")
             self.regularExpr.setText ("&Regular expr")
             self.small = False
       super (FindBox, self).resizeEvent (e)

   def returnPressed (self) :
       self.findNext ()

   def closePressed (self) :
       self.hide ()
       if self.edit != None :
          self.edit.clearSearchResults ()

   def textChanged (self, text) :
       self.findNext ()
       if self.edit != None :
          self.setColor (text)

   def updateSearchResults (self) :
       text = self.searchCombo.currentText ()
       self.setColor (text)

   def setColor (self, text) :
       if self.edit == None :
          self.searchCombo.lineEdit().setPalette (self.orig_palette)
       else :
          opt = alt_no_opt ()
          if self.wholeWords.isChecked () :
             # opt = opt | QTextDocument.FindWholeWords
             opt = alt_or (opt, QTextDocument.FindWholeWords)
          if self.matchCase.isChecked () :
             # opt = opt | QTextDocument.FindCaseSensitively
             opt = alt_or (opt, QTextDocument.FindCaseSensitively)

          if self.incremental :
             cursor = self.edit.textCursor ()
             cursor.setPosition (self.start)
             self.edit.setTextCursor (cursor)
          else :
             cursor = self.edit.textCursor ()
             pos = cursor.position ()

          if self.regularExpr.isChecked () :
             query = QRegularExpression (text)
          else :
             query = text

          # ok = self.edit.find (query, opt)
          ok = alt_find (self.edit, query, opt)
          if not ok :
             # ok = self.edit.find (query, opt | QTextDocument.FindBackward)
             ok = alt_find (self.edit, query, alt_or (opt, QTextDocument.FindBackward))

          if not self.incremental :
             cursor.setPosition (pos)
             self.edit.setTextCursor (cursor)

          if ok :
             color = self.green
          else :
             color = self.red
          widget = self.searchCombo.lineEdit()
          palette = widget.palette ()
          role = widget.backgroundRole ()
          palette.setColor (role, color)
          widget.setPalette (palette)

          self.highlightSearchResults (query, opt)

   def highlightSearchResults (self, query, opt) :
       # old_cursor = self.edit.textCursor ()
       self.edit.clearSearchResults ()
       selections = self.edit.extraSelections ()
       document = self.edit.document ()
       # cursor = document.find (query, opt)
       cursor = alt_find (document, query, opt)
       color = findColor ("yellow")

       while not cursor.isNull () :
          item = QTextEdit.ExtraSelection ()
          item.format.setBackground (color)
          item.format.setProperty (Text.searchProperty, 1)
          item.cursor = cursor
          selections.append (item)
          # cursor = document.find (query, cursor, opt)
          cursor = alt_find_cursor (document, query, cursor, opt)

       self.edit.setExtraSelections (selections)
       # self.edit.setTextCursor (old_cursor)

   def setEdit (self, edit) :
       self.edit = edit
       text = self.searchCombo.currentText ()
       self.setColor (text)

   def openMode (self, mode) :
       self.closeButton.setVisible (mode <= 2)
       self.searchLabel.setVisible (mode <= 2)
       self.searchCombo.setVisible (mode <= 2)
       self.clearButton.setVisible (mode <= 2)
       self.wholeWords.setVisible (mode <= 2)
       self.matchCase.setVisible (mode <= 2)
       self.nextButton.setVisible (mode <= 2)
       self.prevButton.setVisible (mode <= 2)

       self.replaceLabel.setVisible (mode == 2)
       self.replaceCombo.setVisible (mode == 2)
       self.replaceButton.setVisible (mode == 2)

       self.lineClose.setVisible (mode == 3)
       self.lineLabel.setVisible (mode == 3)
       self.lineNumber.setVisible (mode == 3)
       self.goButton.setVisible (mode == 3)

   def openFind (self) :
       self.openMode (1)
       self.show ()
       self.searchCombo.setFocus ()
       self.searchCombo.lineEdit ().selectAll () # enable editing
       self.start = 0
       if self.edit != None :
          self.start = self.edit.textCursor().position()

   def openReplace (self) :
       self.openMode (2)
       self.show ()
       self.searchCombo.setFocus ()
       self.searchCombo.lineEdit ().selectAll () # enable editing
       self.start = 0
       if self.edit != None :
          self.start = self.edit.textCursor().position()

   def openGoToLine (self) :
       self.openMode (3)
       cursor = self.edit.textCursor ()
       document = self.edit.document ()
       self.lineNumber.setMinimum (1)
       self.lineNumber.setMaximum (document.blockCount ())
       self.lineNumber.setValue (cursor.blockNumber () + 1) #  number
       self.lineNumber.setFocus ()
       self.lineNumber.selectAll () # enable editing
       self.show ()

   def goToLineNumber (self) :
       self.edit.selectLine (self.lineNumber.value ())

   def findNext (self) :
       self.findStep (False)

   def findPrev (self) :
       self.findStep (True)

   def replaceNext (self) :
       self.findStep (back = False, repl = True)

   def findStep (self, back, repl = False) :
       text = self.searchCombo.currentText ()
       if text != "" :
          if self.searchCombo.findText (text) == -1 :
             self.searchCombo.addItem (text)

          # opt = QTextDocument.FindFlags ()
          opt = None
          if self.wholeWords.isChecked () :
             # opt = opt | QTextDocument.FindWholeWords
             opt = alt_or (opt, QTextDocument.FindWholeWords)
          if self.matchCase.isChecked () :
             opt = alt_or (opt, QTextDocument.FindCaseSensitively)
          if back :
             opt = alt_or (opt, QTextDocument.FindBackward)

          if self.regularExpr.isChecked () :
             query = QRegularExpression (text)
          else :
             query = text

          if self.edit != None :
             # ok = self.edit.find (query, opt)
             ok = alt_find (self.edit, query, opt)
             if ok and repl :
                replaceText = self.replaceCombo.currentText ()
                cursor = self.edit.textCursor ()
                cursor.removeSelectedText ()
                cursor.insertText (replaceText)

                color = findColor ("lime")
                item = QTextEdit.ExtraSelection ()
                item.format.setBackground (color)
                item.format.setProperty (Text.searchProperty, 1)
                item.cursor = cursor
                selections = self.edit.extraSelections ()
                selections.append (item)
                self.edit.setExtraSelections (selections)

             if not ok :
                if back :
                   self.edit.moveCursor (QTextCursor.End)
                else :
                   self.edit.moveCursor (QTextCursor.Start)
                # self.edit.find (query, opt)
                alt_find (self.edit, query, opt)

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
