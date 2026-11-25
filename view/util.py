#!/usr/bin/env python

import sys, os, re, time, importlib, inspect, optparse, traceback, subprocess
from collections import namedtuple

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

# --------------------------------------------------------------------------

# Compatibility flags (PyQt5 + Python 3 stack)

use_python3 = True
use_py2_qt4 = False
use_webkit  = False

# PyQt-binding flags. The ported 10-view code base supports four bindings;
# this project locks to PyQt5 so all alternatives are constant False —
# `if use_pyqt6 ...` branches compile out trivially.
use_pyqt4   = False
use_pyqt5   = True
use_pyqt6   = False
use_pyside2 = False
use_pyside6 = False
use_qt4     = use_pyqt4
use_qt5     = use_pyqt5 or use_pyside2
use_qt6     = use_pyqt6 or use_pyside6

# QtDBus and python-xlib are optional. When present, Info.goToKDevelop()
# can talk to a running KDevelop and raise its window. Both detected at
# import time so flags + symbols are visible via `from util import *`.

try :
    from PyQt5.QtDBus import QDBusConnection, QDBusInterface
    use_dbus = True
except ImportError :
    use_dbus = False

try :
    from Xlib import display as _xdisplay, X as _xconst
    from Xlib.protocol import event as _xevent
    use_xlib = True
except ImportError :
    use_xlib = False


def activateWindowByPid (pid) :
    """Raise the X11 window owned by `pid`. No-op on Wayland or when
    python-xlib is missing — KDevelop still receives the openDocument
    DBus call, it just won't pop to the front."""
    if not use_xlib :
        return
    try :
        d = _xdisplay.Display ()
    except Exception as e :
        print ("activateWindowByPid: cannot open X display:", e)
        return
    try :
        net_wm_pid        = d.intern_atom ("_NET_WM_PID")
        net_active_window = d.intern_atom ("_NET_ACTIVE_WINDOW")
        root              = d.screen ().root

        def find (window) :
            try :
                prop = window.get_full_property (net_wm_pid, _xconst.AnyPropertyType)
                if prop and prop.value and len (prop.value) > 0 and prop.value [0] == pid :
                    return window
                for child in window.query_tree ().children :
                    found = find (child)
                    if found is not None :
                        return found
            except Exception :
                pass
            return None

        target = find (root)
        if target is None :
            return

        data = (32, [2, _xconst.CurrentTime, 0, 0, 0])
        ev = _xevent.ClientMessage (window = target,
                                    client_type = net_active_window,
                                    data = data)
        mask = _xconst.SubstructureRedirectMask | _xconst.SubstructureNotifyMask
        root.send_event (ev, event_mask = mask)
        target.configure (stack_mode = _xconst.Above)
        d.sync ()
    finally :
        d.close ()

# --------------------------------------------------------------------------

# Options

def command_line_options () :

    options = optparse.OptionParser ()
    options.add_option ("-o", "--no-redirect", dest="no_redirect", action="store_true", help="Do not redirect standard output")

    global opts
    global open_args
    (opts, open_args) = options.parse_args ()

command_line_options ()

# --------------------------------------------------------------------------

# Tree items reference source files by an opaque "file index" elsewhere in
# the codebase. In this simplified version the index *is* the file name.

def indexToFileName (index) :
    return index

def fileNameToIndex (fileName) :
    return fileName

# --------------------------------------------------------------------------

def bytearray_to_str (b) :
    return str (b, "ascii")

def simple_bytearray_to_str (b) :
    return str (b, "ascii", errors="ignore")

def str_to_bytearray (a) :
    return bytearray (a, "ascii", errors="ignore")

def qstring_to_str (s) :
    return s

def qstringref_to_str (s) :
    return s

def qstring_starts_with (s, t) :
    return s.startswith (t)

def qstring_ends_with (s, t) :
    return str (s).endswith (t)

def empty_qstringlist () :
    return [ ]

def qstringlist_to_list (obj) :
    return obj

def mouse_event_pos (e) :
    return e.pos ()

def dialog_to_str (s) :
    return s[0]

def menu_exec (menu, point) :
    return menu.exec_ (point)

def dialog_exec (dlg) :
    return dlg.exec_ ()

def list_count (obj) :
    return len (obj)

def sort_list (obj, compare) :
    obj.sort (key = cmp_to_key (compare))

def variant_to_str (v) :
    return str (v) # boolean -> str

def create_variant (v) :
    return v

def is_variant (v) :
    return False

def get_time () :
    return time.process_time ()

# --------------------------------------------------------------------------

def columnNumber (cursor) :
    return cursor.columnNumber ()
    # return cursor.positionInBlock ()

def setResizeMode (header, section, mode) :
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
       return str (result)

   def boolean (self, name, init = False) :
       s = self.value (name, "")
       result = init
       if s == "true" or s == "True" or s == "1" :
          result = True
       elif s == "false" or s == "False" or s == "0" :
          result = False
       return result

# --------------------------------------------------------------------------

# Text Properties

class Text (object) :

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

# --------------------------------------------------------------------------

color_map = { }
color_names = [ ]

def findColorNames () :
    color_names = [ str (name) for name in QColor.colorNames () ]
    for name in color_names :
        color_map [name] = QColor (name)

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

# --------------------------------------------------------------------------

# Fonts

def setEditFont (edit) :
    # if not opts.simple :
    #    font = QFont ("Luxi Mono", 14)
    #    font.setFixedPitch (True)
    #    edit.setFont (font)
    pass

# --------------------------------------------------------------------------

# Embedded compile / run options
#   C/C++:   // compile : -O2 -Wall -lm
#   Python:  #  compile : --some-flag
#   pkg-config:  // compile : -P gtk+-3.0 -O2
#   (each `-P pkg` is replaced by `pkg-config --cflags --libs pkg`)

def expandPkgConfig (options) :
    "Replace every `-P pkgname` token with the output of `pkg-config --cflags --libs pkgname`."
    tokens = options.split ()
    result = [ ]
    i = 0
    while i < len (tokens) :
       if tokens [i] == "-P" and i + 1 < len (tokens) :
          pkg = tokens [i + 1]
          try :
             flags = subprocess.check_output (
                ["pkg-config", "--cflags", "--libs", pkg],
                stderr = subprocess.STDOUT,
             ).decode ("utf-8", "ignore").strip ()
             result.extend (flags.split ())
          except (OSError, subprocess.CalledProcessError) as e :
             # surface the failure but keep compiling so the user sees gcc's own error too
             output = e.output.decode ("utf-8", "ignore").strip () if hasattr (e, "output") and e.output else str (e)
             print ("pkg-config", pkg + ":", output)
          i += 2
       else :
          result.append (tokens [i])
          i += 1
    return " ".join (result)

def readEmbeddedOptions (fileName) :
    "Scan first lines of a source file for a `compile :` directive."
    result = ""
    try :
       with open (fileName, "r", errors = "ignore") as f :
            for i, line in enumerate (f) :
                if i >= 40 :   # only scan the file header
                   break
                m = re.match (r"\s*(//|#)\s*compile\s*:\s*(.*)", line)
                if m :
                   result = m.group (2).strip ()
                   break
    except OSError as e :
       print ("readEmbeddedOptions:", e)
    return expandPkgConfig (result)

# --------------------------------------------------------------------------

# Main-window registry. set_win() is called from the editor entry point so
# any module can reach the live window via get_win () without tedious
# parameter passing.

main_win = None

def set_win (w) :
    global main_win
    main_win = w

def get_win () :
    return main_win

# Plugins enumerate loaded Qt modules to find DBus / Designer extensions
# at runtime. With the binding pinned to PyQt5 this just lists every
# loaded PyQt5.* module.

def find_qt_modules () :
    return [m for name, m in sys.modules.items ()
            if name.startswith ("PyQt5.") and m is not None]

# --------------------------------------------------------------------------

# Qt symbol injection. Plugins (cmm_plugin, cmm_plugin-style code) use
# "from util import import_qt_modules; import_qt_modules (globals ())" to
# get the Qt namespaces without hard-coding the binding. PyQt5-only port
# of the gibbon machinery — QtCore/QtGui/QtWidgets are imported above.

qt_modules = [ ]
qt_symbols = { }
qt_common_symbols = { }

def qt_module_name (name) :
    return "PyQt5." + name

def store_qt_module (module_name, m) :
    symbols = { }
    for name in dir (m) :
        if not name.startswith ("_") :
           symbols [name] = getattr (m, name)
    qt_modules.append (m)
    qt_symbols [module_name] = symbols
    return symbols

def store_qt_modules () :
    # "from PyQt5.QtWidgets import *" does not bind the module names,
    # so pick them from sys.modules instead.
    for name in [ "QtCore", "QtGui", "QtWidgets" ] :
        m = sys.modules.get (qt_module_name (name))
        if m is not None :
           qt_common_symbols.update (store_qt_module (qt_module_name (name), m))

def additional_qt_module (target, name) :
    name = qt_module_name (name)
    if name in qt_symbols :
       symbols = qt_symbols [name]
    else :
       m = importlib.import_module (name)
       symbols = store_qt_module (name, m)
    target.update (symbols)

def import_qt_modules (target, additional_names = [ ]) :
    target.update (qt_common_symbols)
    for name in additional_names :
        additional_qt_module (target, name)

store_qt_modules ()

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
