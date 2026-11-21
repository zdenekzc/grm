"""Builds the top-level &Examples menu from tools.ini.

The INI uses ConfigParser syntax — see tools.ini for the schema. Each
section becomes a submenu, each path under `files` an action. The
action runs cmm/cmm_run.py on a .t source (or cmm/cmm_iced.py on a .cc
C-- program) via win.runCommand so output streams into the Info panel
(with ANSI colors, courtesy of tools.py).

Missing tools.ini -> no menu. Failure to parse a section is logged and
that section is skipped; the rest of the menu is still built.
"""

import os
import configparser

from PyQt5.QtWidgets import QAction


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


def installExamplesMenu (win, ini_path = "tools.ini") :
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
                lambda checked = False, f = path : _runCmm (win, f))
            sub.addAction (act)
    return top


def _runCmm (win, path) :
    """Compile the example; .cc C-- programs run natively, .t sources
    go through cmm_run.py.

    cmm_run.py joins out_dir + path, so both must be absolute —
    os.path.join then keeps the source path intact and the generated
    .t.py / .t.cpp land next to the source (cwd stays the project root
    for the relative includes inside the .t files)."""
    if path.endswith (".cc") :
        cmd = "python3 cmm/cmm_iced.py " + _shquote (path)
    else :
        src = os.path.abspath (path)
        cmd = ("python3 cmm/cmm_run.py -o " + _shquote (os.path.dirname (src)) +
               " " + _shquote (src))
    win.runCommand (cmd)


def _shquote (s) :
    return "'" + s.replace ("'", "'\\''") + "'"
