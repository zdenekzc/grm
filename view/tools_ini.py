"""Builds the top-level &Examples menu from tools.ini.

The INI uses ConfigParser syntax — see tools.ini for the schema. Each
section becomes a submenu, each path under `files` an action that
opens the example file in the editor (nothing is compiled or run from
this menu).

Missing tools.ini -> no menu. Failure to parse a section is logged and
that section is skipped; the rest of the menu is still built.
"""

import os
import configparser

from PyQt5.QtWidgets import QAction

# Project root (the directory above view/); the example paths in
# tools.ini are relative to it.
ROOT = os.path.dirname (os.path.dirname (os.path.abspath (__file__)))


def listExamples (ini_path = None) :
    """Parse tools.ini and return a list of (title, [paths]) pairs, in
    the same order sections appear in the file. Used by both the menu
    builder and the batch smoke test (test_t_examples.py). Example paths
    stay relative to the process working directory (the project root)."""
    if ini_path is None :
        ini_path = os.path.join (os.path.dirname (os.path.abspath (__file__)), "tools.ini")
    result = []
    if not os.path.isfile (ini_path) :
        return result
    cfg = configparser.ConfigParser ()
    try :
        cfg.read (ini_path)
    except configparser.Error as e :
        print ("tools.ini parse error:", e)
        return result
    for section in cfg.sections () :
        try :
            title = cfg.get (section, "title", fallback = section)
            raw   = cfg.get (section, "files", fallback = "")
        except configparser.Error as e :
            print ("tools.ini [" + section + "] error:", e)
            continue
        files = raw.split ()
        if files :
            result.append ((title, files))
    return result


def installExamplesMenu (win, ini_path = None) :
    """None -> tools.ini next to this module (not relative to the
    working directory, so the IDE works from any cwd)."""
    sections = listExamples (ini_path)
    if not sections :
        print ("tools.ini empty or missing — Examples menu skipped")
        return None

    top = win.addTopMenu ("&Examples")
    for title, files in sections :
        sub = top.addMenu (title)
        for path in files :
            act = QAction (os.path.basename (path), win)
            act.setToolTip (path)
            act.triggered.connect (
                lambda checked = False, f = path : _openExample (win, f))
            sub.addAction (act)
    return top


def _openExample (win, path) :
    """Open the example in the editor (paths in tools.ini are relative
    to the project root; the menu only opens files, it does not compile
    or run them)."""
    if not os.path.isabs (path) :
        path = os.path.join (ROOT, path)
    win.loadFile (path)
