#!/usr/bin/env python

from __future__ import print_function

import sys, os, time, inspect, importlib, optparse

import traceback
from collections import namedtuple

# from lexer import Lexer

# --------------------------------------------------------------------------

__all__ = [
            "use_pyside6",
            "use_pyside2",
            "use_pyqt6",
            "use_pyqt5",
            "use_pyqt4",

            "use_qt6", # use_pyqt6 or use_pyside6
            "use_qt5", # use_pyqt5 or use_pyside2
            "use_qt4", # use_pyqt4

            "use_python3",
            "use_py2_qt4", # use_qt4 and not use_python3

            "opts",
            "open_args",

            "import_qt_modules",
            "optional_qt_module",
            "optional_qt_modules",
            "qt_common_symbols",
            "qt_module_names",

            "print_traceback",
            "print_complete_traceback",
            "get_time",

            "bytearray_to_str",
            "simple_bytearray_to_str",
            "str_to_bytearray",
            "qstring_starts_with",
            "qstring_ends_with",
            "qstring_to_str",
            "qstringref_to_str",
            "qstringlist_to_list",
            "empty_qstringlist",
            "dialog_to_str",
            "menu_exec",
            "dialog_exec",
            "mouse_event_pos",
            "list_count",
            "sort_list",
            "variant_to_str",
            "create_variant",
            "is_variant",

            "columnNumber",
            "setResizeMode",

            "firstValidUrl",

            "Text",
            "Settings",

            "loadModule",

            "color_map",
            "get_win",
            "set_win",

            "findIcon",
            "findColor",
            "refreshIcons",
            "refreshColors",
            "refreshColorTables",
            "refreshModulePath",

            "setApplStyle",
            "setEditFont",
            "resizeMainWindow",
            "resizeDetailWindow",
            "setZoomFont",
          ]

# --------------------------------------------------------------------------

if sys.version_info >= (3,) :
   use_python3 = True
else :
   use_python3 = False

if use_python3 :
   from functools import cmp_to_key

   def cmp (a, b):
       if a > b :
          return 1
       elif a == b :
          return 0
       else :
          return -1

# --------------------------------------------------------------------------

# enabled libraries
enable_pyside6 = False
enable_pyside2 = False
enable_pyqt6 = False
enable_pyqt5 = True

if not use_python3 :
   enable_pyside6 = False
   enable_pyside2 = False
   enable_pyqt6 = False
   enable_pyqt5 = False

# used libraries
use_pyside6 = False
use_pyside2 = False
use_pyqt6 = False
use_pyqt5 = False
use_pyqt4 = False

# --------------------------------------------------------------------------

# Options

def command_line_options () :

    options = optparse.OptionParser ()
    options.add_option ("-s", "--simple", dest="simple", action="store_true", help="Simple UI (without styles)")

    options.add_option ("-e", "--no-hook", dest="no_hook", action="store_true", help="Do not install exception hook")
    options.add_option ("-n", "--no-notify", dest="no_notify", action="store_true", help="Do not install event notification")
    options.add_option ("-o", "--no-redirect", dest="no_redirect", action="store_true", help="Do not redirect standard output")
    options.add_option ("-f", "--no-highlight", dest="no_highlight", action="store_true", help="Do not highlight source")

    options.add_option ("--pyqt4", "--qt4", dest="pyqt4", action="store_true", help="Use PyQt4")
    options.add_option ("--pyqt6", "--qt6",  dest="pyqt6", action="store_true", help="Use PyQt6")
    options.add_option ("--pyside2", dest="pyside2", action="store_true", help="Use PySize2")
    options.add_option ("--pyside6", dest="pyside6", action="store_true", help="Use PySize6")

    global opts
    global open_args
    (opts, open_args) = options.parse_args ()

    global enable_pyqt5
    global enable_pyqt6
    global enable_pyside2
    global enable_pyside6
    if opts.pyqt4 :
       enable_pyside6 = False
       enable_pyside2 = False
       enable_pyqt6 = False
       enable_pyqt5 = False

    if opts.pyqt6 :
       enable_pyqt6 = True

    if opts.pyside2 :
       enable_pyside2 = True

    if opts.pyside6 :
       enable_pyside6 = True

command_line_options ()

# --------------------------------------------------------------------------

if enable_pyside6 :
   try :
      print ("trying PySide6")
      from PySide6 import QtCore
      from PySide6 import QtGui
      from PySide6 import QtWidgets
      use_pyside6 = True
      print ("found PySide6")
   except :
      print ("missing PySide6")

if enable_pyside2 and not use_pyside6 :
   try :
      print ("trying PySide2")
      from PySide2 import QtCore
      from PySide2 import QtGui
      from PySide2 import QtWidgets
      use_pyside2 = True
      print ("found PySide2")
   except :
      print ("missing PySide2")

if enable_pyqt6 and not use_pyside6 and not use_pyside2 :
   try :
      print ("trying PyQt6")
      from PyQt6 import QtCore
      from PyQt6 import QtGui
      from PyQt6 import QtWidgets
      use_pyqt6 = True
      print ("found PyQt6")
   except :
      print ("missing PyQt6")

if enable_pyqt5 and not use_pyside6 and not use_pyside2 and not use_pyqt6 :
   try :
      print ("trying PyQt5")
      from PyQt5 import QtCore
      from PyQt5 import QtGui
      from PyQt5 import QtWidgets
      use_pyqt5 = True
      print ("found PyQt5")
   except :
      print ("missing PyQt5")

if not use_pyside6 and not use_pyside2 and not use_pyqt6 and not use_pyqt5 :
   print ("trying PyQt4")
   # import sip
   # Do not use sip, build
   # python27 configure.py --sip-module PyQt4.sip
   # make && make install
   # https://stackoverflow.com/questions/55424762/importerror-no-module-named-sip-python2-7-pyqt4
   from PyQt4 import QtCore
   from PyQt4 import QtGui
   use_pyqt4 = True
   print ("found PyQt4")

use_qt4 = use_pyqt4
use_qt5 = use_pyqt5 or use_pyside2
use_qt6 = use_pyqt6 or use_pyside6

use_new_qt = use_pyside6 or use_pyside2 or use_pyqt6 or use_pyqt5
use_py2_qt4 = use_qt4 and not use_python3

# --------------------------------------------------------------------------

qt_modules = [ ]
qt_symbols = { }
qt_common_symbols = { }

def qt_module_name (name) :
    if use_pyside6 :
       result = "PySide6." + name
    elif use_pyside2 :
       result = "PySide2." + name
    elif use_pyqt6 :
       result = "PyQt6." + name
    elif use_pyqt5 :
       result = "PyQt5." + name
    else :
       result = "PyQt4." + name
    return result

def store_qt_module (module_name, m) :
    # print ("STORE MODULE", module_name)
    symbols = { }
    module_symbols = dir (m)
    for name in module_symbols :
        if not name.startswith ("_") :
           symbols [name] = getattr (m, name)
    qt_modules.append (m)
    qt_symbols [module_name] = symbols
    return symbols

def store_qt_modules  () :
    global_symbols = globals ()
    module_names = [ "QtCore", "QtGui", "QtWidgets" ]

    for name in global_symbols :
        obj = global_symbols [name]
        if inspect.ismodule (obj) :
           if name in module_names :
              symbols = store_qt_module (qt_module_name (name), obj)
              qt_common_symbols.update (symbols)

def additional_qt_module (target, name) :
    name = qt_module_name (name)
    if name in qt_symbols :
       symbols = qt_symbols [name]
    else :
       m = importlib.import_module (name)
       symbols = store_qt_module (name, m)
    target.update (symbols)

def import_qt_modules  (target, additional_names = [ ]) :
    target.update (qt_common_symbols)
    for name in additional_names :
        additional_qt_module (target, name)

def optional_qt_module (target, name) :
    result = False
    name = qt_module_name (name)
    if name in qt_symbols :
       symbols = qt_symbols [name]
       result = True
    else :
       try :
          m = importlib.import_module (name)
          result = True
       except :
          pass
       if result :
          symbols = store_qt_module (name, m)
       if result :
          print ("found", name)
       else :
          print ("missing", name)
    if result :
       target.update (symbols)
    return result

def optional_qt_modules (target, names) :
    result = True
    for name in names :
        result = result and optional_qt_module (target, name)
    return result

def qt_module_names () :
    return [ module.__name__ for module in qt_modules]

store_qt_modules ()
import_qt_modules (globals ()) # import all symbols from Qt modules

# --------------------------------------------------------------------------

def find_qt_modules  () :
    result = [ ]

    if use_pyside6 :
       prefix = "PySide6."
    elif use_pyside2 :
       prefix = "PySide2."
    elif use_pyqt6 :
       prefix = "PyQt6."
    elif use_pyqt5 :
       prefix = "PyQt5."
    else :
       prefix = "PyQt4."

    for m in sys.modules :
        if m.startswith (prefix) :
           result.append (sys.modules [m])

    return result

# --------------------------------------------------------------------------

def get_module (module_name) :
    if module_name in sys.modules :
       module = sys.modules [module_name]
    else :
       module = importlib.import_module (module_name)
    return module

def import_all_from (target, module_name) :
    module = get_module (module_name)
    module_symbols = dir (module)
    symbols = { }
    for name in module_symbols :
        if not name.startswith ("_") :
           symbols [name] = getattr (module, name)
    target.update (symbols)

def import_from (target, module_name, object_name) :
    module = get_module (module_name)
    target [object_name] = getattr (module, object_name )

def import_module (target, module_name) :
    module = get_module (module_name)
    target [module_name] = module

# --------------------------------------------------------------------------

loaded_modules = { }

def loadModule (fileName) :
    global loaded_modules
    # print ("LOAD MODULE", fileName)
    module = None
    try :
       add = False
       fileName = os.path.abspath (fileName)
       dirName = os.path.dirname (fileName)
       if dirName not in sys.path :
          sys.path.insert (1, dirName)
          # print ("ADD", dirName)
          add = True
       name, ext = os.path.splitext (os.path.basename (fileName))
       if name in sys.modules : # or name in loaded_modules :
          "check also loaded modules, items from sys.modules deleted by unloadModules"
          if name in sys.modules :
             m = sys.modules [name]
          # else :
          #    m = loaded_modules [name]
       else :
          print ("LOAD", name)
       module = importlib.import_module (name)
       loaded_modules [name] = module
    finally :
       if add :
          del sys.path [1]

    return module

def refreshModulePath (conf) :
    for desc in conf.path_list :
        for desc_item in desc.items :
            item = os.path.expanduser (desc_item)
            if item not in sys.path :
               sys.path.append (item)
               # print ("ADD", item)
               # conf.dynamic_module_path.append (item)

# --------------------------------------------------------------------------

# add missing enum constants

if use_pyqt6 :

   enums = [
       (Qt, "ContextMenuPolicy"),
       (Qt, "Orientation"),
       (Qt, "ItemDataRole"),
       (Qt, "ItemFlag"),
       (Qt, "CheckState"),
       (Qt, "CaseSensitivity"),
       (Qt, "KeyboardModifier"),
       (Qt, "Key"),
       (Qt, "ShortcutContext"),
       (Qt, "MouseButton"),
       (QAbstractItemView, "SelectionMode"),
       (QAbstractItemView, "SelectionBehavior"),
       (QAbstractItemView, "EditTrigger"),
       (QAbstractSlider, "SliderAction"),
       (QCompleter, "CompletionMode"),
       (QDialog, "DialogCode"),
       (QDialogButtonBox, "StandardButton"),
       (QEvent, "Type"),
       (QHeaderView, "ResizeMode"),
       (QIODevice, "OpenModeFlag"),
       (QMetaMethod, "MethodType"),
       (QPalette, "ColorGroup"),
       (QPlainTextEdit, "LineWrapMode"),
       (QSizePolicy, "Policy"),
       (QSettings, "Format"),
       (QStyle, "StyleHint"),
       (QTabWidget, "TabPosition"),
       (QTextCursor, "MoveMode"),
       (QTextCursor, "MoveOperation"),
       (QTextCursor, "SelectionType"),
       (QTextDocument, "FindFlag"),
       (QTextFormat, "Property"),
       (QProcess, "ProcessChannelMode"),
   ]

   for module, enum_name in enums:
       for entry in getattr (module, enum_name):
           if enum_name == "KeyboardModifier" :
              setattr (module, entry.name, entry.value) # Debian 12
           else :
              setattr (module, entry.name, entry)

# --------------------------------------------------------------------------

def bytearray_to_str (b) :
    if use_pyside2 or use_pyside6 :
       return str (b.data (), "ascii")
    elif use_python3 :
       return str (b, "ascii")
    else :
       return str (b)

def simple_bytearray_to_str (b) :
    # if use_pyside2 or use_pyside6 :
    #   return str (b.data (), "ascii")
    if use_python3 :
       # return str (b, "latin_1",errors="replace")
       # return str (b, "ascii", errors="replace")
       # return str (b, "cp1252", errors="replace")
       return str (b, "ascii", errors="ignore")
    else :
       return str (b)

def str_to_bytearray (a) :
    if use_py2_qt4 :
       return str (a)
    else :
       return bytearray (a, "ascii", errors="ignore")

def qstring_to_str (s) :
    if use_py2_qt4 :
       if isinstance (s, QString) :
          return str (s.toAscii())
       else :
          return str (s)
    else :
       return s

def qstringref_to_str (s) :
    if use_py2_qt4 :
       return str (s.toString ())
    else :
       return s

def qstring_starts_with (s, t) :
    if use_py2_qt4 :
       return s.startsWith (t)
    else :
       return s.startswith (t)

def qstring_ends_with (s, t) :
    if use_py2_qt4 :
       return s.endsWith (t)
    else :
       return str (s).endswith (t)

def empty_qstringlist () :
    if use_py2_qt4 :
       return QStringList ()
    else :
       return [ ]

def qstringlist_to_list (obj) :
    if use_py2_qt4 :
       return [ str (item) for item in obj ]
    else :
       return obj

def mouse_event_pos (e) :
    if use_pyqt6 :
       p = e.position ()
       return QPoint (p.x(), p.y())
    else :
       return e.pos ()

def dialog_to_str (s) :
    # get file name from open file dialog results
    if use_py2_qt4 :
       return str (s)
    else :
       return s[0]

def menu_exec (menu, point) :
    if use_qt6 :
       # menu.exec () # python 2 => syntax error
       return getattr (menu, "exec") (point)
    else :
       return menu.exec_ (point)

def dialog_exec (dlg) :
    if use_qt6 :
       # dlg.exec () # python 2 => syntax error
       return getattr (dlg, "exec") ()
    else :
       return dlg.exec_ ()

def list_count (obj) :
    return len (obj)
    # if use_py2_qt4 :
    #    return obj.count ()
    # else :
    #    return len (obj)

def sort_list (obj, compare) :
    if use_python3 :
       obj.sort (key = cmp_to_key (compare))
    else :
       obj.sort (compare)

def variant_to_str (v) :
    if use_py2_qt4 :
       return str (v) # Fedora 14
       # return str (v.toString ())
    else :
       return str (v) # boolean -> str

def create_variant (v) :
    if use_py2_qt4 :
       return QVariant (v)
    else :
       return v

def is_variant (v) :
    if use_py2_qt4 :
       return isinstance (v, QVariant)
    else :
       return False

def get_time () :
    if sys.version_info >= (3,5) :
       return time.process_time ()
    else :
       return time.clock ()

# --------------------------------------------------------------------------

def columnNumber (cursor) :
    return cursor.columnNumber ()
    # return cursor.positionInBlock ()

def setResizeMode (header, section, mode) :
    if use_qt4 :
       header.setResizeMode (section, mode)
    else :
       header.setSectionResizeMode (section, mode)
    "mode = QHeaderView.ResizeToContents or QHeaderView.Fixed"

# --------------------------------------------------------------------------

def firstValidUrl (string_list) :
    url = None
    for value in string_list :
        url = QUrl (value)
        if not url.isValid () :
           url = None
        else:
           if url.isLocalFile () :
              path = url.toLocalFile ()
              if not QFile.exists (path) :
                 url = None

    if url == None :
       result = ""
    else :
       result = url.toString ()
    return result

# --------------------------------------------------------------------------

"from https://fman.io/blog/pyqt-excepthook/"
def add_missing_frames (tb):
    result = None
    if tb != None :
       fake_tb = namedtuple ('fake_tb', ('tb_frame', 'tb_lasti', 'tb_lineno', 'tb_next'))
       result = fake_tb (tb.tb_frame, tb.tb_lasti, tb.tb_lineno, tb.tb_next)
       frame = tb.tb_frame.f_back
       while frame != None :
          result = fake_tb (frame, frame.f_lasti, frame.f_lineno, result)
          frame = frame.f_back
    return result

def print_traceback (exc_type, exc_value, exc_traceback) :
    enriched_traceback = add_missing_frames (exc_traceback)
    traceback.print_exception (exc_type, exc_value, enriched_traceback)

def print_complete_traceback () :
    exc_type, exc_value, exc_traceback = sys.exc_info()
    print_traceback (exc_type, exc_value, exc_traceback)

# --------------------------------------------------------------------------

class Settings (QSettings):

   def __init__ (self, fileName, formatType) :
       super (Settings, self).__init__ (fileName, formatType)

   def string (self, name, init = "") :
       result = self.value (name, init)
       if use_py2_qt4 :
          return str (result.toString ())
       else :
          return str (result)

   def string_shortcut (self, name, init = "") :
       result = self.string (name, init)
       result = result.replace ("Win+", "Meta+")
       return result

   def boolean (self, name, init = False) :
       s = self.value (name, "")
       result = init
       if s == "true" or s == "True" or s == "1" :
          result = True
       elif s == "false" or s == "False" or s == "0" :
          result = False
       return result

   def hasPrefix (self, prefix, name) :
       ok = False
       if name == prefix :
          ok = True
       elif name.startswith (prefix) :
          first = name [ len (prefix) ]
          if first == '-' or first == '_' or first >= '0' and first <= '9' :
             ok = True
       return ok

   def removePrefix (self, prefix, name) :
       if name == prefix :
          name = ""
       elif name.startswith (prefix) :
          inx = len (prefix)
          first = name [inx]
          if first == '-' or first == '_' :
             inx = inx + 1
          elif first >= '0' and first <= '9' :
             while inx < len (prefix) and name [inx] >= '0' and name [inx] <= '9' :
               inx = inx + 1
          name = name [ inx : ]
       return name

   def groupsWithPrefix (self, prefix) :
       groups = self.childGroups ()
       result = [ ]
       for grp in groups :
           group = qstring_to_str (grp)
           if self.hasPrefix (prefix, group) :
              result.append (group)
       return result

   def keysWithPrefix (self, prefix) :
       keys = self.allKeys ()
       result = [ ]
       for qkey in keys :
           key = qstring_to_str (qkey)
           if self.hasPrefix (prefix, key) :
              result.append (key)
       return result

   def valuesWithPrefix (self, prefix) :
       keys = self.keysWithPrefix (prefix)
       result = [ ]
       for key in self.keysWithPrefix (prefix) :
           result.append (self.string (key))
       return result

   def valuesFromGroup (self, group) :
       self.beginGroup (group)
       result = [ ]
       for key in self.allKeys () :
           result.append (self.string (key))
       self.endGroup ()
       return result

# --------------------------------------------------------------------------

# Main Window

main_win = None

def set_win (w) :
    global main_win
    main_win = w

def get_win () :
    global main_win
    return main_win

def open_file (fileName, line = 0, column = 0) :
    global main_win
    main_win.loadFile (fileName, line, column)

# --------------------------------------------------------------------------

# Text Properties

class Text (object) :

   if use_pyqt6 : # !? ArchLinux python-pyqt6 6.0.0-2
      QTextFormat.UserProperty = 0x10000

   bookmarkProperty = QTextFormat.UserProperty
   locationProperty = QTextFormat.UserProperty + 1 # source location in output window
   infoProperty = QTextFormat.UserProperty + 2 # qualified name for identifier
   defnProperty = QTextFormat.UserProperty + 3
   ownerProperty = QTextFormat.UserProperty + 4 # owner object / expression, only for information
   openProperty = QTextFormat.UserProperty + 5 # open class / function
   closeProperty = QTextFormat.UserProperty + 6
   outlineProperty = QTextFormat.UserProperty + 7 # used by prev / next function, item in navigator tree
   searchProperty = QTextFormat.UserProperty + 8 # text search results

# --------------------------------------------------------------------------

# Colors

color_cache = { }

def findColor (name):
    global color_cache
    if not isinstance (name, str) :
       return name # !?
    elif name in color_cache :
       return color_cache [name]
    else :
       color = QColor (name)
       color_cache [name] = color
       return color

def defineColor (alias, color):
    global color_cache
    if isinstance (color, QColor) :
       color_cache [alias] = color
    else :
       color_cache [alias] = findColor (color)

def refreshColors (conf) :
    for desc in conf.color_list :
        defineColor (desc.name, desc.value)

if use_pyqt6 : # !? ArchLinux python-pyqt6 6.0.0-2
   Qt.yellow = QColor ("yellow")
   Qt.green = QColor ("green")
   Qt.blue = QColor ("blue")
   Qt.red = QColor ("red")
   Qt.gray = QColor ("gray")

# --------------------------------------------------------------------------

color_map = { }
color_names = [ ]

def findColorNames () :
    color_names = [ str (name) for name in QColor.colorNames () ]
    for name in color_names :
        color_map [name] = QColor (name)

# --------------------------------------------------------------------------

class ColorTable (object) :
    def __init__ (self, conf, name, table) :
        super (ColorTable, self).__init__ ()
        self.name = name
        self.table = table

        if conf != None :
           for desc in conf.color_table_list :
               if desc.name == name :
                  for value in desc.items :
                      self.table.append (value)

        self.inx = 0
        self.cnt = len (self.table)

    def nextColor (self) :
        color = findColor (self.table [self.inx])
        self.inx = (self.inx + 1) % self.cnt
        return color

def refreshColorTables (conf) :
    win = conf.win

    win.namespaceColors = ColorTable (conf, "namespaceColors", [ "olive" ])
    win.classColors = ColorTable (conf, "classColors", [ "blue", "orange", "gold" ])
    win.enumColors = ColorTable (conf, "enumColors", [ "orange" ])
    win.typedefColors = ColorTable (conf, "enumColors", [ "cyan" ])

    win.variableColors = ColorTable (conf, "variableColors",
       [ "#b15928", "#ff7f00", "#b2df8a", "#a6cee3",
         "#1f78b4", "#6a3d9a", "#cab2d6",
       ])

    win.functionColors = ColorTable (conf, "functionColors", ["#c65c8a", "#70a845", "#a361c7", "#b68f40", "#6587cd", "#cc5a43", "#4aac8d"])

    win.typeColors = ColorTable (conf, "typeColors",
       [ "#995729",
         "#D847D0", "#B56AC5", "#E96F0C", "#DC7161",
         "#4D7279", "#01AAF1", "#D2A237", "#C83E93",
         "#5D7DF7", "#EFBB51", "#108BBB", "#5C84B8", "#02F8BC",
         "#A5A9F7", "#F28E64", "#A461E6", "#6372D3" ])

# --------------------------------------------------------------------------

# Icons

icon_path = [ ]
icon_cache = { }

def addIconDir (path, conf = None):
    global icon_path
    path = os.path.expanduser (path)
    path = os.path.abspath (path)
    if path not in icon_path :
       icon_path.append (path)

def findIcon (name):
    global icon_path, icon_cache
    if name in icon_cache :
       icon = icon_cache [name]
    else :
       icon = None
       for path in icon_path :
           file_name = os.path.join (path, name + ".png")
           if os.path.isfile (file_name) :
              icon = QIcon (os.path.join (path, name + ".png"))
              break
       if icon == None :
          icon = QIcon.fromTheme (name)
       icon_cache [name] = icon
    return icon

def defineIcon (alias, name):
    global icon_cache
    if alias not in icon_cache : # if alias is not already defined
       icon = findIcon (name)
       if icon != None :
          icon_cache [alias] = icon # store icon under new name

def refreshIcons (conf):
    for desc in conf.icon_list :
        if desc.path != "" :
           addIconDir (desc.path)
        for name, value in desc.items.items () :
           defineIcon (name, value)

# --------------------------------------------------------------------------

# Fonts

def setEditFont (edit) :
    # if not opts.simple :
    #    font = QFont ("Luxi Mono", 14)
    #    font.setFixedPitch (True)
    #    edit.setFont (font)
    pass

def setZoomFont (edit) :
    edit.setStyleSheet ("QPlainTextEdit {font-size: 18pt}")
    # font = QFont ("Luxi Mono", 18)
    # font.setPointSize (18)
    # font.setFixedPitch (True)
    # edit.setFont (font)

# --------------------------------------------------------------------------

# Window size

def resizeDetailWindow (window) :
    if not opts.simple :
       window.resize (800, 640)

def resizeMainWindow (window) :
    if not opts.simple :
       window.resize (1200, 800)
       # window.middle.resize (640, 480)

# --------------------------------------------------------------------------

# Application style

def setApplStyle (app) :

    # command_line_options ()

    if not opts.simple :
       app.setStyleSheet ("QTabBar::tab:selected {color: blue }"
                          "QWidget {font-size: 12pt}"
                          "Editor {font-family: \"Luxi Mono\" ; font-size: 14pt}"
                          # "QToolTip { color: #000; background-color: yellow; border 1px solid}"
                         )

    if not opts.simple :
       app.setStyle (QStyleFactory.create ("Fusion"))

    if not opts.simple :
       QIcon.setThemeName ("oxygen")
       if getattr (QtCore, "QT_VERSION", 0) > 0x050c00 :
          try :
             QIcon.setFallbackThemeName ("breeze")
             # QIcon.setFallbackThemeName ("mate")

             paths = QIcon.fallbackSearchPaths ()
             paths.append ("/usr/share/kdevelop/pics")
             paths.append ("/usr/share/icons/breeze/apps/48")
             paths.append ("/usr/share/icons/mate/48x48/apps")
             paths.append ("/usr/share/icons/mate/48x48/actions")
             QIcon.setFallbackSearchPaths (paths)
          except :
             pass

       # /usr/share/icons/oxygen
       # dnf install oxygen-icon-theme

       # /usr/share/kdevelop/pics

    findColorNames ()

    defineIcon ("file", "folder")

    defineIcon ("namespace", "namespace")
    defineIcon ("class",     "code-class")
    defineIcon ("enum",      "code-class")
    defineIcon ("function",  "code-function")
    defineIcon ("variable",  "field")
    defineIcon ("type",      "typedef")
    defineIcon ("block",     "code-block")

    defineIcon ("assign",     "edit-rename")
    defineIcon ("call",       "draw-rectangle")
    # defineIcon ("define",     "draw-polygon")
    defineIcon ("with",       "draw-ellipse")
    defineIcon ("nothing",    "draw-donut")

    defineIcon ("local-variable",  "view-list-text")
    defineIcon ("local-declare",   "view-list-tree")
    defineIcon ("local-define",    "view-list-details")

    defineColor ("ink", QColor (0, 0, 0))
    defineColor ("paper", QColor (255, 255, 255))

    defineColor ("namespace", "green")
    defineColor ("class",     "blue")
    defineColor ("function",  "brown")
    defineColor ("variable",  "orange")

    defineColor ("attr",      "orange")
    defineColor ("clang",     "cornflowerblue")

    defineColor ("foreign",   "lime")
    defineColor ("read",      "chartreuse")
    defineColor ("write",     "darkgreen")

    defineColor ("signal",    "darkolivegreen")
    defineColor ("slot",      "seagreen")
    defineColor ("method",    "forestgreen")
    defineColor ("property",  "darkgreen")

    defineColor ("unknown",   "red")
    defineColor ("null",      "orangered")

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
