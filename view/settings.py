# settings.py

from __future__ import print_function

import os, inspect

from lexer import Lexer

# --------------------------------------------------------------------------

class SettingsData (object) : # Python 2.7 requires (object)
   pass

# --------------------------------------------------------------------------

class CommandData (SettingsData) :
   _name_field_ = "title"
   _read_note_ = True # read qmake parameters
   _user_fields_ = [ ] #
   def __init__ (self) :
       super (CommandData, self).__init__ ()

       self.title = ""
       self.icon = ""
       self.shortcut = ""
       self.tooltip = ""
       self.toolbar = 0 # position in toolbar
       self.ext = "" # valid only for this file extension

       self.cd = "" # current directory
       self.set = [] # set environment variables
       self.env = [] # environment names

       self.cmd = "" # shell command
       self.python_cmd = False # True => use Python executable as cmd
       # self.jscript = "" # java script
       self.url = [] # web

       self.module = "" # Python module
       self.cls = "" # class
       self.func = "" # function

       self.load = [ ] # pre-load modules

       self.plugin = "" # parameters for builder from env.py
       self.param = ""

       self.enableMonitor = False # show tree output from monitor object
       self.compilerOptions = "" # "-D TST"
       self.ignore_all_includes = False
       self.fast_output = False # generated files without colors
       self.clang_import = False
       # self.example_number = 0 # roll to example

       self.addWin = False # add main window as parameter
       self.askFileName = "" # show file dialog
       self.addFileName = False # add file name as parameter

       # private variable
       self._action_ = None

# --------------------------------------------------------------------------

class PluginData (SettingsData) :

   _name_dict_ = { "module" : "module_name",
                   "cls" : "cls_name" } # rename fields

   _name_list_ = [ "title", "key" ] # , "reread_menu", "reload_module" ] # other valid fields

   _name_field_ = "title" # field after type name

   def __init__ (self) :
       super (PluginData, self).__init__ ()

       self.title = "" # menu title
       self.key = "" # plugin identifier
       self.module_name = "" # Python module
       self.cls_name = "" # Python class

       # self.reread_menu = False # refresh menu on opening menu
       # self.reload_module = False # reload module on menu click

       # private variables
       self.module = None
       self.cls = None
       self.menu = None

class MenuData (SettingsData) :
   _name_field_ = "title"
   def __init__ (self) :
       super (MenuData, self).__init__ ()
       self.title = ""
       self.plugin = "" # plugin name for following menu items
       self.middle = False # middle ... insert after plugin menu

"Menu"

class MenuItem (CommandData) :
   _name_field_ = "title"
   _read_note_ = True # read qmake parameters
   def __init__ (self) :
       super (MenuItem, self).__init__ ()

class MenuSeparator (SettingsData) :
   def __init__ (self) :
       super (MenuSeparator, self).__init__ ()

"Shortcut"

class ShortcutData (SettingsData) :
   def __init__ (self) :
       super (ShortcutData, self).__init__ ()
       self.name = ""
       self.icon = ""
       self.shortcut = ""
       self.toolbar = 0

       # private variable
       self._action_ = None

"Colors"

class ColorData (SettingsData) :
   def __init__ (self) :
       super (ColorData, self).__init__ ()
       self.name = ""
       self.value = ""

class ColorTableData (SettingsData) :
   _read_list_ = True # add strings to 'items' list
   def __init__ (self) :
       super (ColorTableData, self).__init__ ()
       self.name = ""
       self.items = [ ]

"Icons"

class IconData (SettingsData) :
   _read_dict_ = True # add names and values to 'items' dictionary
   def __init__ (self) :
       super (IconData, self).__init__ ()
       self.path = ""
       self.items = { }

"Python Path"

class PythonPathData (SettingsData) :
   _read_list_ = True # add strings to 'items' list
   def __init__ (self) :
       super (PythonPathData, self).__init__ ()
       self.items = [ ]

"Open File"

class OpenFileData (SettingsData) :
   def __init__ (self) :
       super (OpenFileData, self).__init__ ()
       self.name = ""

# --------------------------------------------------------------------------

class ConfigData (object) :
   def __init__ (self) :
       super (ConfigData, self).__init__ ()
       self.win = None

       # data from files
       self.clear ()

   def clear (self) :
       self.plugin_list = [ ]
       self.command_list = [ ]
       self.menu_list = [ ]
       self.page_list = [ ]
       self.color_list = [ ]
       self.color_table_list = [ ]
       self.icon_list = [ ]
       self.shortcut_list = [ ] # refresh not implemented
       self.path_list = [ ]
       self.setup_list = [ ] # used only during window creation
       self.open_list = [ ]

# --------------------------------------------------------------------------

typeNameDict = {
                 "Command"    : "CommandData",
                 "Plugin"     : "PluginData",
                 "Menu"       : "MenuData",
                 "Shortcut"   : "ShortcutData",
                 "Color"      : "ColorData",
                 "ColorTable" : "ColorTableData",
                 "Icons"      : "IconData",
                 "PythonPath" : "PythonPathData",
                 "OpenFile"   : "OpenFileData",
                } # translate type names

def findClass (type_name) :
    cls = None
    if type_name in typeNameDict :
       type_name = typeNameDict [type_name] # rename
    cls = globals().get (type_name, None)
    if cls != None and not issubclass (cls, SettingsData):
       cls = None
    return cls

def isTypeName (type_name) :
    cls = findClass (type_name)
    return cls != None

def createObject (type_name) :
    obj = None
    cls = findClass (type_name)
    if cls != None:
       obj = cls ()
    return obj

def renameField (obj, name) :
    if name.startswith ('_') or name == "items" :
       name = ""
    else :
       if hasattr (obj, "_name_dict_") and name in obj._name_dict_ :
          name = obj._name_dict_ [name] # rename
       else :
          if hasattr (obj, "_name_list_") :
             if name not in obj._name_list_ :
                name = ""
          else :
             if not hasattr (obj, name) :
                name = ""
    return name

def readBoolValue (input) :
    if input.isKeyword ("true") or input.isKeyword ("True") or input.isNumber () and input.tokenText == "1" :
       input.nextToken ()
       value = True
    elif input.isKeyword ("false") or input.isKeyword ("False") or input.isNumber () and input.tokenText == "0":
       input.nextToken ()
       value = False
    else :
       input.error ("Boolean expected")
    return value

def readSimpleString (input) :
    if input.isIdentifier () :
       txt = input.readIdentifier ()
    else :
       txt = input.readString ()
    return txt

def readStringValue (input) :
    if input.isIdentifier () :
       txt = input.tokenText
       while input.ch > ' ' and input.ch not in [ ',', ';', '{', '}', '[', ']' ] :
          txt = txt + input.ch
          input.nextChar ()
       input.nextToken ()
    else :
       txt = input.readString ()
    return txt

def readValue (input, obj, name) :
    orig = getattr (obj, name, None)

    if isinstance (orig, bool) :
       value = readBoolValue (input)
       setattr (obj, name, value)
    elif isinstance (orig, int) :
       value = input.readSignedNumber ()
       setattr (obj, name, value)
    elif isinstance (orig, float) :
       value = input.readSignedReal ()
       setattr (obj, name, value)
    elif isinstance (orig, str) :
       value = readStringValue (input)
       setattr (obj, name, value)
    elif isinstance (orig, list) :
       value = readStringValue (input)
       orig.append (value)
    else :
       input.error ("Unknown field: " + name)

    if input.isSeparator (';') :
       input.nextToken ()

def readList (input) :
    result = [ ]
    if input.isSeparator ('[') :
       input.checkSeparator ('[')
       while not input.isSeparator (']') :
          value = readStringValue (input)
          result.append (value)
          if input.isSeparator (',') :
             input.nextToken ()
       input.checkSeparator (']')
    else :
       value = readStringValue (input)
       result.append (value)
    return result

def readBlock (input, type_name) :
    # print ("READ BLOCK", type_name)
    if not isTypeName (type_name) :
       input.error ("Unknown type name: " + type_name)
    obj = createObject (type_name)

    if input.isIdentifier () or input.isString () :
       name = getattr (obj, "_name_field_", "") # declared name field
       if name == "" :
          name = renameField (obj, "name") # standard name field
       if name != "" :
          # print ("READ NAME", type_name)
          value = readSimpleString (input)
          setattr (obj, name, value)

    if input.isSeparator (';') :
       input.nextToken ()
    elif input.isSeparator ('{') :
       read_list = getattr (obj, "_read_list_", False)
       read_dict = getattr (obj, "_read_dict_", False)
       read_code = getattr (obj, "_read_code_", False)
       read_note = getattr (obj, "_read_note_", False)

       if read_code :
          obj.code = readCodeBlock (input)
       else :
          input.check ('{')
          while not input.isSeparator ('}') :
             if read_code :
                value = readStringValue (input)
             if read_list :
                value = readList (input)
                obj.items = obj.items + value
                if input.isSeparator (',') or input.isSeparator (';') :
                   input.nextToken ()
             else :
                name = input.readIdentifier ()
                if not read_dict and isTypeName (name) :
                   readNestedBlock (input, obj, name)
                # elif read_note and name in qmake_notes :
                #    readNote (input, obj, name)
                else :
                   orig_name = name
                   name = renameField (obj, name)
                   if name != "" :
                      input.check ('=')
                      readValue (input, obj, name)
                   else  :
                      name = orig_name
                      if read_dict :
                         input.check ('=')
                         value = readStringValue (input)
                         obj.items [name] = value
                      else :
                         input.error ("Unknown field: " + name)

          input.check ('}')

    return obj

def readSetting (conf, input) :
     type_name = input.readIdentifier ()
     if type_name == "Cmd" :
        readCmdBlock (input, conf)
     else :
        obj = readBlock (input, type_name)
        if isinstance (obj, MenuData) or isinstance (obj, MenuItem) or isinstance (obj, MenuSeparator) : # before CommandData
           conf.menu_list.append (obj)
        elif isinstance (obj, CommandData) :
           conf.command_list.append (obj)
        elif isinstance (obj, PluginData) :
           conf.plugin_list.append (obj)
        elif isinstance (obj, ShortcutData) :
           conf.shortcut_list.append (obj)
        elif isinstance (obj, ColorData) :
           conf.color_list.append (obj)
        elif isinstance (obj, ColorTableData) :
           conf.color_table_list.append (obj)
        elif isinstance (obj, IconData) :
           conf.icon_list.append (obj)
        elif isinstance (obj, PythonPathData) :
           conf.path_list.append (obj)
        elif isinstance (obj, OpenFileData) :
           conf.open_list.append (obj)
        else :
           input.error ("Invalid settings item: " + type_name)

# --------------------------------------------------------------------------

def readData (conf, fileName) :
    input = Lexer ()
    input.openFile (fileName)
    while not input.isEndOfSource () :
        readSetting (conf, input)
    input.close ()

def initConfig (file_name) :
    conf = ConfigData ()
    readData (conf, file_name)
    return conf

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
