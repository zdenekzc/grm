"""Code completion dispatcher invoked by Editor.getCompletionList().

Two backends:
  - Python: identifiers extracted from the buffer + keyword + builtins
  - C/C++: libclang TU.codeComplete (see tools/llvm-tools/complete_clang.py)

Each returns a list of unique strings; QCompleter then prefix-filters
them against the word under cursor.
"""

import os, re, builtins, keyword


_IDENT_RE = re.compile (r"\b[A-Za-z_][A-Za-z0-9_]*\b")

# Cached static parts so we don't rebuild on every keystroke.
_PY_KEYWORDS = set (keyword.kwlist) | set (
    name for name in dir (builtins) if not name.startswith ("_")
)


def pythonCompletions (source) :
    """Identifiers in `source` plus Python keywords and builtins."""
    words = set (_IDENT_RE.findall (source))
    words |= _PY_KEYWORDS
    return sorted (words)


_CPP_EXTS  = (".c", ".cc", ".cpp", ".cxx", ".h", ".hpp", ".hh", ".cu")


def getCompletions (filename, source, line, column) :
    """Return list of completion names. Empty list = no suggestions."""
    ext = os.path.splitext (filename) [1].lower ()
    if ext == ".py" :
        return pythonCompletions (source)
    if ext in _CPP_EXTS :
        try :
            from complete_clang import clangCompletions
        except ImportError as e :
            print ("complete: clang backend missing:", e)
            return []
        return clangCompletions (filename, source, line, column)
    # Unknown language: still offer buffer-local identifiers so Ctrl+Space
    # is at least mildly useful for plain-text / ad-hoc files.
    return sorted (set (_IDENT_RE.findall (source)))
