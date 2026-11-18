#!/usr/bin/env python

from __future__ import print_function

import sys, os, re, inspect

from util import import_qt_modules
import_qt_modules (globals ())

from util import findColor, findIcon, use_qt4, use_pyqt6, use_pyside6, qstring_to_str, variant_to_str, dialog_to_str, menu_exec, setResizeMode

import util

from prop import ObjectBrowser

from tools import SettingsData

# --------------------------------------------------------------------------

class OptionDialog (QDialog) :
   def __init__ (self, win) :
       super (OptionDialog, self).__init__ (win)

       self.win = win
       self.page_count = 0
       self.current_tab = None
       self.page_dict = { }

       "toolBar with buttons"
       self.toolBar = QToolBar ()
       self.toolBar.setOrientation (Qt.Vertical)

       "stackWidget for option pages"
       self.stackWidget = QStackedWidget ()

       "toolBar and stackWidget - central dialog area"
       self.hlayout = QHBoxLayout ()
       self.hlayout.addWidget (self.toolBar)
       self.hlayout.addWidget (self.stackWidget)

       self.buttonBox = QDialogButtonBox (QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
       self.buttonBox.accepted.connect (self.accept)
       self.buttonBox.rejected.connect (self.reject)

       "ok and cancel at the bottom"
       self.vlayout = QVBoxLayout ()
       self.vlayout.addLayout (self.hlayout)
       self.vlayout.addWidget (self.buttonBox)
       self.setLayout (self.vlayout)

   def addPage (self, name, icon, widget, create_widget = None) :

       if isinstance (icon, str) :
          icon = findIcon (icon)

       if widget != None :
          self.stackWidget.addWidget (widget)

       button = QPushButton ()
       button.setText (name)
       if icon != None :
          button.setIcon (icon)
          button.setIconSize (QSize (24, 24))
       # button.setMinimumSize (80, 80)
       button.setMinimumSize (80, 64)

       button.widget = widget
       button.create_widget = create_widget

       button.clicked.connect (lambda param, self=self, button=button: self.openPage (button))
       self.toolBar.addWidget (button)
       self.page_dict [name] = widget

   def openPage (self, button) :
       if button.create_widget != None :
          if button.widget == None  :
             button.widget = button.create_widget ()
             self.stackWidget.addWidget (button.widget)
          else :
             self.stackWidget.setCurrentWidget (button.widget) # show empty page
             self.show ()
             button.create_widget (button.widget)
          button.create_widget = None # do not call again
       self.stackWidget.setCurrentWidget (button.widget)

   def addSimplePage (self, name, icon) :
       box = OptionsBox ()
       box.win = self.win
       self.addPage (name, icon, box)
       self.current_page = None
       self.current_tab = box
       return box

# --------------------------------------------------------------------------

class ActionList :
   def __init__ (self, win) :
       self.win = win
       self.action_dict = { }

       for item in self.win.menuBar().actions() :
           prefix = "Menu " + item.text () + " / "
           if not use_pyside6 and not use_pyqt6 : # !?
              for action in item.menu().actions() :
                 self.addAction (action, prefix)

       for action in self.win.actions() :
           self.addAction (action)

       for desc in self.win.conf.shortcut_list :
           self.getAction (desc)

   def simplifyName (self, name) :
       name = qstring_to_str (name)
       # print ("simplifyName", name)
       name = name.lower ()
       name = name.replace ("&", "")
       name = name.replace ("/", "")
       name = " ".join (name.split())
       # print ("result simplifyName", name, "...", type (name))
       return name

   def addAction (self, action, prefix = "") :
       # name = qstring_to_str (action.text ())
       name = qstring_to_str (action.text ())
       if prefix != "" :
          self.addSimpleAction (action, prefix + name)
       self.addSimpleAction (action, name)

   def addSimpleAction (self, action, name) :
       name = self.simplifyName (name)
       if name != None and name != "" :
          # print ("ADD ", name, "...", type (name))
          self.action_dict [name] = action

   def getAction (self, desc) :

       name = self.simplifyName (desc.name)
       action = self.action_dict.get (name, None)
       if action == None :
          print ("Unknown action:", name)
       else :
          if desc.icon != "" :
             icon_obj = findIcon (desc.icon)
             if icon_obj != None :
                action.setIcon (icon_obj)
          if desc.shortcut != "" :
             shortcuts = action.shortcuts ()
             shortcuts.append (desc.shortcut)
             action.setShortcuts (shortcus)

          desc._action_ = action # store action

       return action

# --------------------------------------------------------------------------

class Notes (OptionDialog) :
   def __init__ (self, win) :
       super (Notes, self).__init__ (win)

       self.setWindowTitle ("Notes")
       self.buttonBox.setStandardButtons (QDialogButtonBox.Cancel)

       self.shortcutPage ()
       self.colorCachePage ()
       self.colorNamesPage ()
       self.iconCachePage ()
       # self.iconPathPage ()
       self.pathPage ()
       self.modulePage ()
       self.globalVariablesPage ()
       self.winVariablePage ()
       self.configPage ()
       # self.toolIniPage ()
       self.iniPage ("options.ini", "clementine", self.win.settings)
       self.iniPage ("edit.ini", "text-editor", self.win.session)

   # -----------------------------------------------------------------------

   def winVariablePage (self) :
       listView = ObjectBrowser (self, self.win)
       self.addPage ("win object", "code-class", listView)

   # -----------------------------------------------------------------------

   def globalVariablesPage (self) :
       listView = QListWidget ()
       self.addPage ("global variables", "variable", listView)
       for item in globals () :
          listView.addItem (item)
       listView.itemDoubleClicked.connect (self.showVariable)

   def showVariable (self, item) :
       name = qstring_to_str (item.text ())
       ObjectBrowser (self.win, globals () [name])

   # -----------------------------------------------------------------------

   def pathPage (self) :
       listView = QListWidget ()
       self.addPage ("sys path", "rosegarden", listView)
       for item in sys.path :
          listView.addItem (item)

   def modulePage (self) :
       listView = QListWidget ()
       self.addPage ("modules", "kdf", listView)
       # for item in self.win.loaded_modules :
       #    listView.addItem (item)
       for item in sorted (sys.modules) :
          listView.addItem (item)
       listView.itemDoubleClicked.connect (self.showModule)
       listView.itemClicked.connect (self.alternativeShowModule)

   def showModule (self, item) :
       name = qstring_to_str (item.text ())
       ObjectBrowser (self.win, sys.modules [name])

   def alternativeShowModule (self, item) :
       mask = Qt.ShiftModifier | Qt.ControlModifier | Qt.AltModifier | Qt.MetaModifier
       mod = QApplication.keyboardModifiers () & mask
       if mod == Qt.ControlModifier :
          # print ("CTRL CLICK")
          self.showModule (item)

   # -----------------------------------------------------------------------

   def resizeFirstColumn (self, treeView) :
       setResizeMode (treeView.header(), 0, QHeaderView.ResizeToContents)

   def resizeSecondColumn (self, treeView) :
       setResizeMode (treeView.header(), 1, QHeaderView.ResizeToContents)

   def colorCachePage (self) :
       treeView = QTreeWidget (self)
       treeView.setHeaderLabels (["Name", "Value"])
       self.resizeFirstColumn (treeView)
       self.addPage ("color cache",  "color-management", treeView)

       for name in util.color_cache :
          self.displayColor (treeView, name, util.color_cache [name])

       treeView.sortByColumn (0, Qt.AscendingOrder)

   def colorNamesPage (self) :
       treeView = QTreeWidget (self)
       treeView.setHeaderLabels (["Name", "Value"])
       self.resizeFirstColumn (treeView)
       self.addPage ("color names", "gimp", treeView)

       for name in util.color_map :
          self.displayColor (treeView, name, util.color_map [name])

       treeView.sortByColumn (0, Qt.AscendingOrder)

   def displayColor (self, branch, name, color) :
       node = QTreeWidgetItem (branch)
       node.setText (0, name)
       node.setToolTip (0, name)
       if color.lightness () < 220 and color.alpha () != 0 :
          node.setForeground (0, color)
       node.setData (0, Qt.DecorationRole, color)
       node.setText (1, str (color.red ()) + ", " + str (color.green ())+ ", " + str (color.blue ()))

   # -----------------------------------------------------------------------

   def iconCachePage (self) :
       treeView = QTreeWidget (self)
       self.addPage ("icon cache", "choqok", treeView)

       for name in util.icon_cache :
           icon = util.icon_cache [name]
           self.displayIcon (treeView, name, icon)

       treeView.sortByColumn (0, Qt.AscendingOrder)

   def displayIcon (self, branch, name, icon) :
       node = QTreeWidgetItem (branch)
       node.setText (0, name)
       node.setToolTip (0, name)
       node.setIcon (0, icon)

   # -----------------------------------------------------------------------

   def iconPathPage (self) :
       listView = QListWidget ()
       self.addPage ("icon path", "rosegarden", listView)
       for item in util.icon_path :
          listView.addItem (item)

   # -----------------------------------------------------------------------

   def iniPage (self, name, icon, ini) :
       treeView = QTreeWidget (self)
       treeView.setHeaderLabels (["Name", "Value"])
       self.resizeFirstColumn (treeView)
       self.addPage (name, icon, treeView)
       for group in ini.childGroups () :
           branch = QTreeWidgetItem (treeView)
           branch.setText (0, "[" + group + "]")
           branch.setIcon (0, findIcon ("folder"))
           ini.beginGroup (group)
           for key in ini.childKeys () :
               value = ini.value (key)
               item = QTreeWidgetItem (branch)
               item.setText (0, key)
               item.setText (1, variant_to_str (value))
           ini.endGroup ()

   # -----------------------------------------------------------------------

   def configPage (self) :
       treeView = QTreeWidget (self)
       treeView.setHeaderLabels (["Name", "Value"])
       self.resizeFirstColumn (treeView)
       self.addPage ("tools.cfg", "tools-wizard", treeView)
       for member in inspect.getmembers (self.win.conf) :
           name, value = member
           if name.endswith ("_list") :
              branch = QTreeWidgetItem (treeView)
              branch.setText (0, name)
              branch.setIcon (0, findIcon ("folder"))
              self.showConfigList (branch, value)

   def showConfigList (self, branch, data) :
       for value in data :
           self.showConfigItem (branch, "", value)

   def showConfigDict (self, branch, data) :
       for name in data :
           value = data [name]
           self.showConfigItem (branch, name, value)

   def showConfigItem (self, branch, name, value) :
       if isinstance (value, bool) or isinstance (value, int) or isinstance (value, float) or isinstance (value, str) :
          if name == "" :
             name = "(item)"
             self.showConfigValue (branch, name, value)
       else :
          self.showConfigValue (branch, name, value)

   def showConfigValue (self, branch, name, value) :
       if isinstance (value, bool) or isinstance (value, int) or isinstance (value, float) or isinstance (value, str) :
          item = QTreeWidgetItem (branch)
          item.setText (0, name)
          item.setText (1, str (value))
       elif isinstance (value, SettingsData) :
          self.showConfigData (branch, name, value)

   def showConfigData (self, branch, title, data) :
       item = QTreeWidgetItem (branch)
       item.setText (0, data.__class__.__name__)
       item.setIcon (0, findIcon ("folder"))

       if title == "" :
          if hasattr (data, "_name_field_") :
             title = getattr (data, data._name_field_, "")
       if title == "" :
          if hasattr (data, "name") :
             title = str (data.name)
       item.setText (1, title)

       for member in inspect.getmembers (data) :
           name, value = member
           if not inspect.iscode (value) and not name.startswith ("__"):
              if name == "items" :
                 if isinstance (value, list) :
                    self.showConfigList (item, value)
                 elif isinstance (value, dict) :
                    self.showConfigDict (item, value)
              else :
                 self.showConfigValue (item, name, value)

   # -----------------------------------------------------------------------

   def shortcutPage (self) :

       treeView = QTreeWidget ()
       treeView.setHeaderLabels (["Name", "Shortcut", "Invisible"])
       self.name_column = 0
       self.key_column = 1
       self.invisible_column = 2
       self.resizeFirstColumn (treeView)
       self.resizeSecondColumn (treeView)
       header = treeView.header ()
       header.hideSection (self.invisible_column)
       # name_column = 0
       # header.setSectionResizeMode (name_column, QHeaderView.ResizeToContents)
       self.addPage ("shortcuts", "key-enter", treeView)

       for item in self.win.menuBar().actions() :
           self.displayMainMenuAction (treeView, item)
           prefix = "Menu " + item.text () + " / "
           for action in item.menu().actions() :
               self.displayAction (treeView, action, prefix)

       for action in self.win.actions() :
           self.showItem (branch, action)
       for item in self.win.children() :
           if isinstance (item, QShortcut) :
              self.displayShortcut (treeView, item)

       for inx in [1, 2, 3, 4, 5] :
           self.formalShortcut (treeView, "Go to bookmark " + str (inx), "Ctrl+" + str (inx))
           self.formalShortcut (treeView, "Set bookmark " + str (inx), "Ctrl+Shift+" + str (inx))
           self.formalShortcut (treeView, "Set bookmark " + str (inx), "Win+" + str (inx))

       if 0 :
          # remove items without shortcuts
          inx = treeView.topLevelItemCount () - 1
          while inx > 0 :
             item = treeView.topLevelItem (inx)
             if item.text (self.key_column) == "" : # no shortcut
                treeView.takeTopLevelItem (inx)
             inx = inx - 1

       self.setKeys (treeView)
       treeView.sortByColumn (self.invisible_column, Qt.AscendingOrder)

   def displayMainMenuAction (self, treeView, item) :
       node = QTreeWidgetItem (treeView)
       text = str (item.text ())
       node.setText (self.name_column, "Menu " +text)
       inx = text.find ('&')
       if inx >= 0 and inx+1 < len (text) :
          c = text [inx+1]
          node.setText (1, "Alt+" + c.upper ())
       icon  = item.icon ()
       node.setIcon (self.name_column, icon)

   def displayAction (self, treeView, action, prefix = "") :
       for shortcut in action.shortcuts () :
           node = QTreeWidgetItem (treeView)
           node.setText (self.name_column, prefix + action.text())
           node.setIcon (self.name_column, action.icon ())
           node.setText (self.key_column,  self.keySequenceToString (shortcut))

   def displayShortcut (self, treeView, shortcut) :
       node = QTreeWidgetItem (treeView)
       node.setText (self.name_column, shortcut.objectName ())
       node.setText (self.key_column,  self.keySequenceToString (shortcut.key()))

   def formalShortcut (self, treeView, name, shortcut) :
       node = QTreeWidgetItem (treeView)
       node.setText (self.name_column, name)
       node.setText (self.key_column,  shortcut)

   def keySequenceToString (self, shortcut) :
       text = shortcut.toString ()
       text = qstring_to_str (text)
       text = text.replace ("Meta+", "Win+")
       return text

   def setKeys (self, treeView) :
       cnt = treeView.topLevelItemCount ()
       for inx in range (cnt) :
          item = treeView.topLevelItem (inx)
          text = qstring_to_str (item.text (self.key_column))

          key = "T"
          if text == "" :
             key = "Z"

          if text.startswith ("Win+") :
             key = key + "W"
             text = text [4:]
          else :
             key = key + "Z"

          if text.startswith ("Alt+") :
             key = key + "A"
             text = text [4:]
          else :
             key = key + "Z"

          if text.startswith ("Ctrl+") :
             key = key + "C"
             text = text [5:]
          else :
             key = key + "Z"

          if text.startswith ("Shift+") :
             key = key + "S"
             text = text [6:]
          else :
             key = key + "Z"

          if text == "Left" :
             key = key + "a"
          elif text == "Right" :
             key = key + "b"
          elif text == "Up" :
             key = key + "c"
          elif text == "Down" :
             key = key + "d"
          elif text == "Ins" :
             key = key + "e"
          elif text == "Del" :
             key = key + "f"
          elif text == "Home" :
             key = key + "g"
          elif text == "End" :
             key = key + "h"
          elif text == "PgUp" :
             key = key + "i"
          elif text == "PgDown" :
             key = key + "j"
          elif text.startswith ("F") and len (text) > 1 :
             if len (text) == 2 : # F1 .. F9
                key = key + "l"
             else :
                key = key + "m" # F10 .. F12
          elif len (text) > 1 :
             key = key + "k" # before F1 and F12
          elif text >= "0" and text <= "9":
             key = key + "o"
          elif text >= "A" and text <= "Z":
             key = key + "p" # before digits
          elif text == "-" :
             key = key + "na"
          elif text == "=" :
             key = key + "nb"
          elif text == "\\" :
             key = key + "nc"
          elif text == "[" :
             key = key + "nd"
          elif text == "]" :
             key = key + "ne"
          elif text == ";" :
             key = key + "nf"
          elif text == "'" :
             key = key + "ng"
          elif text == "<" :
             key = key + "nh"
          elif text == ">" :
             key = key + "ni"
          elif text == "/" :
             key = key + "nj"
          else :
             key = key + "nk" # before digits

          key = key + text
          item.setText (self.invisible_column, key)

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
