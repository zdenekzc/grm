
# clang_tree.py
#
# Parse the current C/C++ file with libclang and fill the existing "Classes"
# tab with a navigation tree of:
#   namespace / class / struct / union / function / method / var / field /
#   function-parameters
#
# Double-click on any node jumps to its source location (handled by tree.py
# via the src_file/src_line/src_column attributes we set on each item).

import os, subprocess

from PyQt5.QtCore    import Qt
from PyQt5.QtWidgets import QApplication

from clang.cindex import Index, CursorKind

from util import findIcon, readEmbeddedOptions
from tree import TreeItem

# --------------------------------------------------------------------------

# Cached path to clang's own resource dir (contains stddef.h etc.); without it
# libclang can't parse any real-world C/C++ file.

_clang_resource_dir = None

def clangResourceDir () :
    global _clang_resource_dir
    if _clang_resource_dir is None :
       try :
          out = subprocess.check_output (["clang", "-print-resource-dir"])
          _clang_resource_dir = out.decode ("utf-8", "replace").strip ()
       except (OSError, subprocess.CalledProcessError) as e :
          print ("clang -print-resource-dir failed:", e)
          _clang_resource_dir = ""
    return _clang_resource_dir

def parseArgs (options, fileName) :
    "Build libclang arg list, injecting -resource-dir so builtin headers resolve."
    args = [ ]
    rd = clangResourceDir ()
    if rd != "" :
       args.append ("-resource-dir=" + rd)
    args.extend (options)
    args.append (fileName)
    return args

# --------------------------------------------------------------------------

# Cursor kinds we want to show, mapped to icon names.

KIND_ICONS = {
    CursorKind.NAMESPACE         : "code-context",
    CursorKind.CLASS_DECL        : "code-class",
    CursorKind.STRUCT_DECL       : "code-class",
    CursorKind.UNION_DECL        : "code-class",
    CursorKind.CLASS_TEMPLATE    : "code-class",
    CursorKind.FUNCTION_DECL     : "code-function",
    CursorKind.CXX_METHOD        : "code-function",
    CursorKind.CONSTRUCTOR       : "code-function",
    CursorKind.DESTRUCTOR        : "code-function",
    CursorKind.FUNCTION_TEMPLATE : "code-function",
    CursorKind.VAR_DECL          : "code-variable",
    CursorKind.FIELD_DECL        : "code-variable",
}

CONTAINER_KINDS = {
    CursorKind.NAMESPACE,
    CursorKind.CLASS_DECL,
    CursorKind.STRUCT_DECL,
    CursorKind.UNION_DECL,
    CursorKind.CLASS_TEMPLATE,
}

FUNCTION_KINDS = {
    CursorKind.FUNCTION_DECL,
    CursorKind.CXX_METHOD,
    CursorKind.CONSTRUCTOR,
    CursorKind.DESTRUCTOR,
    CursorKind.FUNCTION_TEMPLATE,
}

# --------------------------------------------------------------------------

def setLocation (item, cursor) :
    "Store source location so double-click on the tree item jumps to it."
    loc = cursor.location
    if loc.file != None :
       item.src_file   = loc.file.name
       item.src_line   = loc.line
       item.src_column = loc.column

def labelFor (cursor) :
    if cursor.kind in FUNCTION_KINDS :
       # displayname includes parameter types, e.g. "foo(int, char*)"
       return cursor.displayname or cursor.spelling or "(anonymous)"
    return cursor.spelling or "(anonymous)"

def addNode (parent, cursor) :
    "Add `cursor` under `parent` if it is interesting; otherwise descend."
    if cursor.kind in KIND_ICONS :
       item = TreeItem (parent, labelFor (cursor))
       item.addIcon (KIND_ICONS [cursor.kind])
       setLocation (item, cursor)

       if cursor.kind in FUNCTION_KINDS :
          for param in cursor.get_arguments () :
              ptype = param.type.spelling
              pname = param.spelling or ""
              text  = (ptype + " " + pname).strip ()
              p = TreeItem (item, text)
              p.addIcon ("code-variable")
              setLocation (p, param)

       elif cursor.kind in CONTAINER_KINDS :
          for child in cursor.get_children () :
              addNode (item, child)

    elif cursor.kind == CursorKind.LINKAGE_SPEC :
       # `extern "C" { ... }` — flatten into the parent
       for child in cursor.get_children () :
           addNode (parent, child)

# --------------------------------------------------------------------------

def sameFile (a, b) :
    try :
       return os.path.samefile (a, b)
    except OSError :
       return os.path.normpath (a) == os.path.normpath (b)

# --------------------------------------------------------------------------
# Qt Usage Tree — show only declarations from Qt headers that are *used*
# in the current source file, grouped by class.
# --------------------------------------------------------------------------

QT_PATH_HINTS = ("/qt5/", "/qt6/", "/qt/")

def isQtHeader (path) :
    if path == None :
       return False
    p = path.replace ("\\", "/").lower ()
    for hint in QT_PATH_HINTS :
        if hint in p :
           return True
    return False

def extentText (extent) :
    "Read the source bytes covered by a libclang SourceRange."
    start, end = extent.start, extent.end
    if start.file == None or end.file == None :
       return ""
    if start.file.name != end.file.name :
       return ""
    try :
       with open (start.file.name, "rb") as f :
            f.seek (start.offset)
            data = f.read (end.offset - start.offset)
       return data.decode ("utf-8", "replace")
    except OSError :
       return ""

def signatureText (cursor) :
    "Single-line declaration of `cursor`, including default-parameter values."
    text = extentText (cursor.extent)
    if text == "" :
       return cursor.displayname or cursor.spelling
    # truncate at the body so inline definitions don't bloat the tooltip
    inx = text.find ("{")
    if inx >= 0 :
       text = text [:inx]
    text = " ".join (text.split ())
    if text.endswith (";") :
       text = text [:-1].rstrip ()
    return text

def collectQtRefs (tu_cursor, sourceFile, refs) :
    "Walk the AST; for each cursor in sourceFile, record the Qt-header decl it references."
    for c in tu_cursor.walk_preorder () :
        loc = c.location
        if loc.file is None or not sameFile (loc.file.name, sourceFile) :
           continue
        target = c.referenced
        # Cursor.__eq__ explodes on None; libclang returns a *null cursor*
        # (not Python None) when there is no referent, detected by location.
        if target is None :
           continue
        tloc = target.location
        if tloc.file is None or not isQtHeader (tloc.file.name) :
           continue
        refs.append (target)

def classNameOf (cursor) :
    "Best-effort class name for grouping; '<global>' for free symbols."
    if cursor.kind in (CursorKind.CLASS_DECL, CursorKind.STRUCT_DECL,
                       CursorKind.UNION_DECL, CursorKind.CLASS_TEMPLATE) :
       return cursor.spelling
    sem = cursor.semantic_parent
    if sem is not None and sem.kind in (CursorKind.CLASS_DECL, CursorKind.STRUCT_DECL,
                                        CursorKind.UNION_DECL, CursorKind.CLASS_TEMPLATE) :
       return sem.spelling
    return "<global>"

def buildQtUsageTree (win, fileName) :
    "Show a tree of Qt classes/methods actually referenced from fileName."
    if fileName == "" :
       print ("Qt Usage Tree: no file open")
       return

    win.classes.clear ()

    options = readEmbeddedOptions (fileName).split ()
    args    = parseArgs (options, fileName)
    print ("Qt usage parse:", " ".join (args))
    QApplication.processEvents ()

    try :
       index = Index.create ()
       tu    = index.parse (None, args)
    except Exception as e :
       print ("Clang parse error:", e)
       return

    if tu == None :
       print ("Clang: empty translation unit")
       return

    for diag in tu.diagnostics :
        # only surface real errors — Qt headers emit a lot of warnings
        if diag.severity >= 3 :
           print ("clang:", diag.spelling)

    refs = [ ]
    collectQtRefs (tu.cursor, fileName, refs)

    # group by class; deduplicate by USR
    by_class = { }
    seen     = set ()
    for r in refs :
        usr = r.get_usr ()
        if usr in seen :
           continue
        seen.add (usr)
        by_class.setdefault (classNameOf (r), [ ]).append (r)

    if len (by_class) == 0 :
       print ("Qt Usage Tree: nothing recognized from Qt headers — did you set `// compile : -P Qt5Widgets` (or similar)?")
       return

    root = TreeItem (win.classes, os.path.basename (fileName) + " — Qt usage")
    root.addIcon ("text-x-c++src")
    root.src_file = fileName

    for cls_name in sorted (by_class.keys ()) :
        members  = by_class [cls_name]
        cls_item = TreeItem (root, cls_name)
        cls_item.addIcon ("code-class")

        # if the class declaration itself is in refs, anchor navigation to it
        for m in members :
            if m.kind in (CursorKind.CLASS_DECL, CursorKind.STRUCT_DECL,
                          CursorKind.CLASS_TEMPLATE) and m.spelling == cls_name :
               setLocation (cls_item, m)
               cls_item.setToolTip (0, signatureText (m))
               break

        for m in sorted (members, key = lambda c : (c.spelling or "", c.displayname or "")) :
            if m.kind in (CursorKind.CLASS_DECL, CursorKind.STRUCT_DECL,
                          CursorKind.CLASS_TEMPLATE) and m.spelling == cls_name :
               continue
            label = m.displayname or m.spelling or "(?)"
            mi = TreeItem (cls_item, label)
            if m.kind in FUNCTION_KINDS :
               mi.addIcon ("code-function")
            elif m.kind in (CursorKind.VAR_DECL, CursorKind.FIELD_DECL,
                            CursorKind.PARM_DECL, CursorKind.ENUM_CONSTANT_DECL) :
               mi.addIcon ("code-variable")
            else :
               mi.addIcon ("code-context")
            setLocation (mi, m)
            mi.setToolTip (0, signatureText (m))

        cls_item.setExpanded (True)

    root.setExpanded (True)
    win.showTab (win.classes)

# --------------------------------------------------------------------------

def buildClangTree (win, fileName) :
    "Parse fileName and fill win.classes with the navigation tree."
    if fileName == "" :
       print ("Clang Tree: no file open")
       return

    win.classes.clear ()

    # Reuse the gcc compile options embedded in the source (// compile : ...).
    # libclang ignores -l/-L flags during parsing but uses -I, -D, -std= etc.
    options = readEmbeddedOptions (fileName).split ()
    args    = parseArgs (options, fileName)
    print ("Clang parse:", " ".join (args))
    QApplication.processEvents ()

    try :
       index = Index.create ()
       tu    = index.parse (None, args)
    except Exception as e :
       print ("Clang parse error:", e)
       return

    if tu == None :
       print ("Clang: empty translation unit")
       return

    for diag in tu.diagnostics :
        print ("clang:", diag.spelling)

    root = TreeItem (win.classes, os.path.basename (fileName))
    root.addIcon ("text-x-c++src")
    root.src_file = fileName

    # Show only entries declared in this file (skip everything from headers).
    for child in tu.cursor.get_children () :
        loc = child.location
        if loc.file != None and sameFile (loc.file.name, fileName) :
           addNode (root, child)

    root.setExpanded (True)
    win.showTab (win.classes)

# --------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
