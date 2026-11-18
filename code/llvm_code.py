
# code_clang.py

from __future__ import print_function

import os, sys

from util import import_qt_modules
import_qt_modules (globals ()) # QTextCursor

use_clang = True

if use_clang :
   # sys.path.append (os.path.expanduser ("/abc/llvm-python"))
   # directory with clang/cindex.py from clang (llvm/tools/clang/binndigs/python/clang)
   try :
      # from clang import cindex
      from clang.cindex import Index, Config, CursorKind, TypeKind, TranslationUnit
      from gcc_options import gcc_options, pkg_options
      print ("found clang.cindex")
   except :
      use_clang = False
      print ("missing clang.cindex")

from util import get_time, findColor, use_qt5, use_qt6
from input import fileNameToIndex, indexToFileName
from code import *
from code_cls import *

# --------------------------------------------------------------------------

cache_opt = [ ]
cache_pkg = [ ]

def clang_compile (args, with_qt = False) :
    tu = None
    if use_clang :

       global cache_opt
       global cache_pkg

       if len (cache_opt) == 0 :
          cache_opt = gcc_options (gcc="clang", no_variables = True)
          # two items "-I", "directory", one item "-Idirectory", NOT one item "-I directory"

       if with_qt and len (cache_pkg) == 0  :
          if use_qt6 :
             cache_pkg = pkg_options ("Qt6Widgets")
          elif use_qt5 :
             cache_pkg = pkg_options ("Qt5Widgets")
          else :
             cache_pkg = pkg_options ("QtGui")

       args = args + cache_opt

       if with_qt :
          args = args + cache_pkg

       print ("args:", args)

       index = Index.create ()
       start_time = get_time ()
       tu = index.parse (None, args,
                         options = 0*TranslationUnit.PARSE_DETAILED_PROCESSING_RECORD +
                                   1*TranslationUnit.PARSE_INCOMPLETE +
                                   1*TranslationUnit.PARSE_PRECOMPILED_PREAMBLE +
                                   1*TranslationUnit.PARSE_CACHE_COMPLETION_RESULTS +
                                   1*TranslationUnit.PARSE_SKIP_FUNCTION_BODIES +       # <--
                                   1*TranslationUnit.PARSE_INCLUDE_BRIEF_COMMENTS_IN_CODE_COMPLETION )

       print ("parse", get_time () - start_time)

       if tu :
          for item in tu.diagnostics :
              print (str (item))

          """
          start_time = get_time ()
          tu.reparse ()
          print ("reparse", get_time () - start_time)

          start_time = get_time ()
          tu.reparse ()
          print ("reparse", get_time () - start_time)
          """

          # tu.save ("qt-classes.pch")

    return tu

# --------------------------------------------------------------------------

class CLangImport :

   def __init__ (self, win, fileNames) :
       self.win = win

       self.global_scope = Scope ()

       self.library_scope = Scope ()
       self.library_scope.item_name = "(library)"
       self.library_scope.item_icon = "folder-orange"
       self.global_scope.add (self.library_scope) # !?

       self.qt_scope = Scope ()
       self.qt_scope.item_name = "(qt)"
       self.qt_scope.item_icon = "folder-green"
       self.global_scope.add (self.qt_scope) # !?

       self.display = [self.library_scope, self.global_scope]

       self.file_scope = None
       self.current_file = 0
       self.known_items = { }

       self.clang_sources (fileNames)

   def enterIntoScope (self, scope, item) :
       scope.item_dict [item.item_name] = item
       scope.item_list.append (item)
       item.item_context = scope

       if hasattr (scope, "item_qual") and scope.item_qual != None and scope.item_qual != "" :
          item.item_qual = scope.item_qual + "." + item.item_name
       else :
          item.item_qual = item.item_name

   def enter (self, item) :
       scope = self.display [-1]
       if item.src_file == self.current_file or scope != self.file_scope:
          self.enterIntoScope (scope, item)
       else :
          path = indexToFileName (item.src_file)
          if path.startswith ("/usr/include/qt") :
             self.enterIntoScope (self.qt_scope, item)
          elif path.startswith ("/usr/include/") :
             self.enterIntoScope (self.library_scope, item)

   def location (self, item, decl) :
       location = decl.location
       if hasattr (location, "file") and hasattr (location.file, "name"):
           item.src_file = fileNameToIndex (location.file.name)
           item.src_line = location.line
           item.src_column = location.column
       id = decl.get_usr ()
       # item.item_tooltip = id
       self.known_items [id] = decl

   def is_new (self, decl) :
       return decl.get_usr () not in self.known_items

   def add_type (self, item, decl) :
       type = decl.type
       if type != None :
          item.item_tooltip = type.spelling

   def subitems (self, decl) :
       for item in decl.get_children () :
           self.clang_decl (item)

   def subitems_with_scope (self, target, decl) :
       self.display.append (target)
       self.subitems (decl)
       self.display.pop ()

   def is_new (self, decl) :
       return decl.get_usr () not in self.known_items

   def clang_namespace (self, decl) :
       ns = Namespace ()
       ns.item_name = str (decl.displayname)
       ns.clang_obj = decl
       self.location (ns, decl)
       self.enter (ns)
       self.subitems_with_scope (ns, decl)

   def clang_class (self, decl) :
       if decl.is_definition () :
          if self.is_new (decl) :
             cls = Class ()
             cls.item_name = str (decl.displayname)
             cls.clang_obj = decl
             self.location (cls, decl)
             self.add_type (cls, decl)
             self.enter (cls)
             self.subitems_with_scope (cls, decl)

   def clang_enum (self, decl) :
       if self.is_new (decl) :
          enum = Enum ()
          initEnum (enum)
          enum.item_name = str (decl.displayname)
          enum.clang_obj = decl
          self.location (enum, decl)
          self.add_type (enum, decl)
          self.enter (enum)
          self.subitems_with_scope (enum, decl)

   def clang_function (self, decl) :
       if True : # if self.is_new (decl) :
          func = Function ()
          func.item_name = str (decl.displayname)
          func.clang_obj = decl
          self.location (func, decl)
          self.add_type (func, decl)
          self.enter (func)

   def clang_variable (self, decl) :
       if self.is_new (decl) :
          var = Variable ()
          var.item_name = str (decl.displayname)
          var.clang_obj = decl
          self.location (var, decl)
          self.add_type (var, decl)
          self.enter (var)

   def clang_decl (self, decl) :
       kind = decl.kind

       if kind == CursorKind.NAMESPACE :
            self.clang_namespace (decl)

       elif kind in [ CursorKind.CLASS_DECL,
                      CursorKind.STRUCT_DECL,
                      CursorKind.UNION_DECL ] :
          if decl.is_definition () :
             target = self.clang_class (decl)

       elif kind == CursorKind.ENUM_DECL :
            self.clang_enum (decl)

       elif kind in [ CursorKind.FUNCTION_DECL ,
                      CursorKind.CXX_METHOD,
                      CursorKind.CONSTRUCTOR,
                      CursorKind.DESTRUCTOR ] :
            self.clang_function (decl)

       elif kind in [ CursorKind.VAR_DECL,
                      CursorKind.PARM_DECL,
                      CursorKind.FIELD_DECL,
                      CursorKind.ENUM_CONSTANT_DECL ] :
            self.clang_variable (decl)

       elif kind == CursorKind.TRANSLATION_UNIT:
          self.subitems (decl)

   def move_classes (self, scope) :
       classes = [ ]
       other = [ ]
       for item in scope.item_list :
           name = item.item_name
           if isinstance (item, Class) and not name.startswith ("QTypeInfo") and not name.startswith ("QMetaType") :
              classes.append (item)
           else :
              other.append (item)
       # scope.item_list = classes + other
       scope.item_list = classes
       nested_scope = Scope ()
       nested_scope.item_name = "(other)"
       nested_scope.item_list = other
       scope.item_list.append (nested_scope)

   def clang_source (self, fileName) :

       tu = clang_compile (["-x", "c++", fileName], with_qt = True)

       if tu :
          edit = self.win.loadFile (fileName) # , hiddenFile = True)
          # hidden ... not necessary visible to user

          # edit.clang_cursor = tu.cursor
          edit.translation_unit = tu

          for item in tu.diagnostics :
              print (str (item))

          short_name = os.path.basename (fileName)
          print ("CLang parsing", short_name, "O.K.")

          self.current_file = fileNameToIndex (fileName)

          self.file_scope = Scope ()
          self.file_scope.item_name = short_name # !?
          self.file_scope.item_icon = "folder"
          self.file_scope.item_expand = True
          self.global_scope.add (self.file_scope)
          self.display.append (self.file_scope)

          self.clang_decl (tu.cursor)

          self.display.pop ()
          self.file_scope = None

   def clang_sources (self, fileNames) :
       if use_clang :
          for fileName in fileNames :
              self.clang_source (fileName)
          self.move_classes (self.qt_scope)
          self.win.showClasses (self.global_scope)
          print ("CLang tree O.K.")

   # ------------------------------------------------------------------------

   """
   def addType (self, branch, note, type, level):
       kind = type.kind
       if kind != TypeKind.INVALID :
          name = type.spelling

          txt = str (kind).replace ("TypeKind.", "", 1)
          txt = "TYPE " + txt
          if note != "" :
             txt = note + " " + txt

          item = TreeItem (branch, txt + " " + name)
          # item.item_icon = "type"
          # item.setupTreeItem ()

          if level <= 3 :
             if kind == TypeKind.FUNCTIONPROTO :
                for e in type.argument_types () :
                   self.addType (item, "ARGUMENT", e, level+1)
                e = type.get_result ()
                if e != None:
                   self.addType (item, "RESULT", e, level+1)

             if kind == TypeKind.CONSTANTARRAY :
                e = type.get_array_element_type ()
                if e != None:
                   self.addType (item, "ELEMENT", e, level+1)

             if kind == TypeKind.POINTER :
                e = type.get_pointee ()
                if e != None:
                   self.addType (item, "POINTER TO", e, level+1)
   """

   # -----------------------------------------------------------------------

   """
   def createCompletionList (self) :

       items = [ ]
       if self.translation_unit != None :

          edit = self.win.getEditor ()
          fileName = edit.getFileName ()

          cursor = edit.textCursor ()
          line = cursor.blockNumber () + 1
          column = columnNumber (cursor) + 1

          print (fileName, str (line), str (column))

          answer = self.translation_unit.codeComplete (fileName, line, column,
                                                       unsaved_files = None,
                                                       include_macros = False,
                                                       include_code_patterns = False,
                                                       include_brief_comments = False)
          if answer != None :
             for t in answer.results :
                # print ("CLANG ANSWER", t)
                for u in t.string :
                   # print ("CLANG STRING", u)
                   if u.isKindTypedText () :
                      items.append (u.spelling)
                      # print ("CLANG ", u.spelling)

       return items
       """

# --------------------------------------------------------------------------

def clang_import_tree (win, fileNames) :
    CLangImport (win, fileNames)

# clang slots : qt-creator-4.14.1/src/tools/clangbackend/source/fulltokeninfo.cpp

# --------------------------------------------------------------------------

def select (edit, start_line, start_col, stop_line, stop_col) :
    cursor = edit.textCursor ()
    cursor.movePosition (QTextCursor.Start)
    cursor.movePosition (QTextCursor.NextBlock, QTextCursor.MoveAnchor, start_line-1)
    cursor.movePosition (QTextCursor.NextCharacter, QTextCursor.MoveAnchor, start_col-1)

    if start_line == stop_line :
       cursor.movePosition (QTextCursor.NextCharacter, QTextCursor.KeepAnchor, stop_col-start_col+1)
    else :
       cursor.movePosition (QTextCursor.NextBlock, QTextCursor.KeepAnchor, stop_line-start_line)
       cursor.movePosition (QTextCursor.StartOfLine, QTextCursor.KeepAnchor)
       cursor.movePosition (QTextCursor.NextCharacter, QTextCursor.KeepAnchor, stop_col)

    edit.setTextCursor (cursor)
    return cursor

def place (edit, start_line, start_col) :
    cursor = edit.textCursor ()
    cursor.movePosition (QTextCursor.Start)
    cursor.movePosition (QTextCursor.NextBlock, QTextCursor.MoveAnchor, start_line-1)
    cursor.movePosition (QTextCursor.NextCharacter, QTextCursor.MoveAnchor, start_col-1)

    edit.setTextCursor (cursor)
    return cursor

def write_declaration (win, ins_decl, ins_acs, ins_func, ins_params) :
    print ("DECLARATON", ins_func, ins_params)
    edit = win.loadFile (str (ins_decl.extent.end.file))
    text_cursor = place (edit, ins_decl.extent.end.line, ins_decl.extent.end.column+1)
    if ins_acs :
       text_cursor.insertText ("\n" + "private slots:")
    text_cursor.insertText ("\n" + "\n" + 4 * " " + "void " + ins_func + " " + ins_params + ";")

def write_implementation (win, cursor, ins_cls, ins_func, ins_params) :
    print ("METHOD", ins_cls, "::", ins_func, ins_params)
    edit = win.loadFile (str (cursor.extent.end.file))
    text_cursor = place (edit, cursor.extent.start.line, cursor.extent.start.column)
    text_cursor.insertText ("\n" + "void " + ins_cls + "::" + ins_func + " " + ins_params + "\n{\n\n}\n\n")

def scan_class (win, cursor, ins_cls, ins_func, ins_params) :
    ins_acs = False
    ins_decl = None

    target_acs = False
    last = None

    for dcl in cursor.get_children () :
        if dcl.kind == CursorKind.CXX_ACCESS_SPEC_DECL :
           # if not (last_acs is None) and not (last is last_acs):
           #    print ("LAST ACCESS DECL", str (last.extent.end.file), last.extent.end.line, last.extent.end.column)

           # last_acs = dcl

           acs_file = str (dcl.location.file)
           acs_line = dcl.location.line
           acs_col = dcl.location.column

           end_file = str (dcl.extent.end.file)
           end_line = dcl.extent.end.line
           end_col = dcl.extent.end.column

           edit = win.loadFile (acs_file)
           text_cursor = select (edit, acs_line, acs_col, end_line, end_col)
           text = str (text_cursor.selectedText ())

           target_acs = (text.find ("private") >= 0 and (text.find ("slots") >= 0 or text.find ("QT_SLOTS")))
           target_acs = text.find ("private") >= 0 and (ins_decl is None)
           if target_acs :
              print ("ACCESS", text)
              ins_decl = last

        last = dcl
        if target_acs :
           ins_decl = last

    if ins_decl is None :
       ins_decl = last
       ins_acs = True

    if not (ins_decl is None) :
       write_declaration (win, ins_decl, ins_acs, ins_func, ins_params)

def read_window_file (win, fileName, ins_cls = "MainWindow", ins_func = "on_nextButton_clicked", ins_params = "()" ) :
    fileDir = os.path.basename (fileName)
    headerName = os.path.splitext (fileName) [0] + ".h"
    tu = clang_compile ([ fileName ], with_qt = True)

    if tu :
       done = False
       for cursor in tu.cursor.get_children () :
           if cursor.kind == CursorKind.CLASS_DECL :
              cls_name = cursor.spelling
              cls_file = str (cursor.location.file)
              if cls_file == headerName :
                 print ("CLASS", cls_name, "in", cls_file)
                 if cls_name == ins_cls :
                    print ("CLASS", ins_cls)
                    scan_class (win, cursor, ins_cls, ins_func, ins_params)

           if ( cursor.kind == CursorKind.CXX_METHOD or
                cursor.kind == CursorKind.CONSTRUCTOR or
                cursor.kind == CursorKind.DESTRUCTOR) :
              if str (cursor.location.file) == fileName :
                 above = cursor.semantic_parent
                 if str (above.spelling) == ins_cls : # and str (cursor.spelling) == str (ins_decl.spelling) :
                    if not done :
                       done = True
                       write_implementation (win, cursor, ins_cls, ins_func, ins_params)

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
