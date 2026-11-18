#!/usr/bin/env python
#
# Top-level &Grammar menu. Every action operates on the .g file currently
# loaded in the editor and writes the converted output next to it. The
# old CodePlugin / win.outputFileName / win.reloadFile machinery is gone;
# everything happens in plain functions of (win) and Python file IO.

from __future__ import print_function

import os

from PyQt5.QtWidgets import QAction

from grammar  import Grammar
from tohtml   import ToHtml
from tolout   import ToLout
from toparser import ToParser
from toproduct import ToProduct
from cparser  import CParser
from cproduct import CProduct


def installGrammarPlugin (win) :
    """Register a top-level &Grammar menu on `win`. Each action requires
    that the active editor's file ends in .g; otherwise it shows a
    status-bar message and returns. The handler reloads the freshly
    written file in the editor so the user sees the result."""
    menu = win.addTopMenu ("&Grammar")
    menu.aboutToShow.connect (lambda : _refreshEnabled (win, menu))

    _addAction (win, menu, "to &Python Parser", "Ctrl+F5",
                lambda : _toParser (win))
    _addAction (win, menu, "to &C++ Parser",    "Ctrl+F6",
                lambda : _toCppParser (win))
    _addAction (win, menu, "to &HTML",          None,
                lambda : _toHtml (win))
    _addAction (win, menu, "to &Lout",          None,
                lambda : _toLout (win))
    return menu


def _addAction (win, menu, title, shortcut, slot) :
    act = QAction (title, win)
    if shortcut :
        act.setShortcut (shortcut)
    act.triggered.connect (slot)
    act.need_grammar = True
    menu.addAction (act)


def _refreshEnabled (win, menu) :
    is_gram = bool (_currentGrammar (win))
    for act in menu.actions () :
        if getattr (act, "need_grammar", False) :
            act.setEnabled (is_gram)


def _currentGrammar (win) :
    "Return path to current .g file or None."
    e = win.getEditor ()
    if e is None :
        return None
    name = e.getFileName ()
    return name if name.lower ().endswith (".g") else None


def _openGrammar (win) :
    "Parse the current editor's text into a Grammar; returns (path, grammar) or None."
    e = win.getEditor ()
    if e is None :
        return None
    path = e.getFileName ()
    grammar = Grammar ()
    grammar.openString (str (e.toPlainText ()))
    grammar.setFileName (path)
    return path, grammar


def _writeAndReload (win, src_path, suffix, write_func) :
    """Compute target path = <src>.<suffix>, call write_func(target),
    print the result to the Info panel, and re-load the file in the
    editor if it was open. Returns the target path."""
    target = os.path.splitext (src_path) [0] + suffix
    write_func (target)
    print ("wrote", target)
    if hasattr (win, "loadFile") :
        win.loadFile (target)
    return target


# --- actions ---------------------------------------------------------------

def _toHtml (win) :
    parsed = _openGrammar (win)
    if parsed is None : return
    src, grammar = parsed
    grammar.parseRules ()
    def write (target) :
        p = ToHtml () ; p.open (target)
        p.htmlFromRules (grammar) ; p.close ()
    _writeAndReload (win, src, ".html", write)


def _toLout (win) :
    parsed = _openGrammar (win)
    if parsed is None : return
    src, grammar = parsed
    grammar.parseRules ()
    def write (target) :
        p = ToLout () ; p.open (target)
        p.loutFromRules (grammar) ; p.close ()
    _writeAndReload (win, src, ".lout", write)


def _toParser (win) :
    parsed = _openGrammar (win)
    if parsed is None : return
    src, grammar = parsed
    parser_path  = os.path.splitext (src) [0] + "_parser.py"
    product_path = os.path.splitext (src) [0] + "_product.py"

    p = ToParser ()
    p.open (parser_path, with_simple = True)
    p.parserFromGrammar (grammar)
    p.close ()
    print ("wrote", parser_path)

    parserModuleName = os.path.splitext (os.path.basename (parser_path)) [0]
    q = ToProduct ()
    q.open (product_path, with_simple = True)
    q.productFromGrammar (grammar, parserModuleName)
    q.close ()
    print ("wrote", product_path)

    if hasattr (win, "loadFile") :
        win.loadFile (parser_path)


def _toCppParser (win) :
    parsed = _openGrammar (win)
    if parsed is None : return
    src, grammar = parsed
    parser_path  = os.path.splitext (src) [0] + "_parser.cpp"
    product_path = os.path.splitext (src) [0] + "_product.cpp"

    p = CParser ()
    p.open (parser_path)
    p.parserFromGrammar (grammar)
    p.close ()
    print ("wrote", parser_path)

    parserModuleName = os.path.splitext (os.path.basename (parser_path)) [0]
    q = CProduct ()
    q.open (product_path)
    q.productFromGrammar (grammar, parserModuleName)
    q.close ()
    print ("wrote", product_path)

    if hasattr (win, "loadFile") :
        win.loadFile (parser_path)
