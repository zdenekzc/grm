"""Resolve "go to declaration" / "go to implementation" requests from
Editor.mousePressEvent (Ctrl+Click and Ctrl+Shift+Click).

Returns (filename, line, column) on success, None if the symbol could not
be resolved. Caller is responsible for opening the target file.

Backends:
  .py        -> regex search for `def NAME` / `class NAME` in the buffer
                (and across other open editors via `extra_buffers`)
  .c/.cc/... -> libclang via complete_clang.clangResolve
"""

import os, re


_CPP_EXTS = (".c", ".cc", ".cpp", ".cxx", ".h", ".hpp", ".hh", ".cu")


def _word_at (source, line, column) :
    """Return the identifier under (line, column). Both 1-based."""
    lines = source.split ("\n")
    if line < 1 or line > len (lines) :
        return ""
    text = lines [line - 1]
    col = column - 1
    if col < 0 or col >= len (text) :
        return ""
    if not (text [col].isalnum () or text [col] == "_") :
        return ""
    start = col
    while start > 0 and (text [start - 1].isalnum () or text [start - 1] == "_") :
        start -= 1
    end = col
    while end < len (text) and (text [end].isalnum () or text [end] == "_") :
        end += 1
    return text [start : end]


def _python_lookup (name, source, filename) :
    """Find `def NAME` / `class NAME` in `source`. Return (filename, line,
    column) at the start of the identifier, or None."""
    if not name :
        return None
    pattern = re.compile (r"^(\s*)(?:def|class)\s+" + re.escape (name) + r"\b")
    for i, raw in enumerate (source.split ("\n")) :
        m = pattern.match (raw)
        if m :
            # Column = position of the name itself (after `def`/`class `).
            kw_end = raw.find (name, m.end (1))
            return (filename, i + 1, (kw_end + 1) if kw_end >= 0 else 1)
    return None


def pythonGoto (filename, source, line, column, extra_buffers = None) :
    """Look up the identifier at line:column in `source`, then in any other
    `extra_buffers` (list of (filename, source)). Returns first match."""
    name = _word_at (source, line, column)
    if not name :
        return None
    hit = _python_lookup (name, source, filename)
    if hit :
        return hit
    for fname, fsrc in (extra_buffers or []) :
        if fname == filename :
            continue
        hit = _python_lookup (name, fsrc, fname)
        if hit :
            return hit
    return None


def goto (filename, source, line, column, kind = "declaration",
          extra_buffers = None) :
    """Top-level dispatcher. `kind` is "declaration" or "definition".
    Returns (target_file, target_line, target_column) or None."""
    ext = os.path.splitext (filename) [1].lower ()
    if ext == ".py" :
        return pythonGoto (filename, source, line, column, extra_buffers)
    if ext in _CPP_EXTS :
        try :
            from complete_clang import clangResolve
        except ImportError as e :
            print ("goto: clang backend missing:", e)
            return None
        return clangResolve (filename, source, line, column, kind)
    return None
