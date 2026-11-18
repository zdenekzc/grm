"""Clang-backed completion for C/C++ source. Cached translation units so a
second Ctrl+Space on the same file is fast (~tens of ms); the first
parse pays for the precompiled preamble (~hundreds of ms).
"""

from clang.cindex import Index, TranslationUnit


_index = None
_tu_cache = {}   # filename -> TranslationUnit


def _index_singleton () :
    global _index
    if _index is None :
        _index = Index.create ()
    return _index


def _open_tu (filename, source, args) :
    """Return a TU for `filename`, parsed from in-memory `source`. Builds
    a precompiled preamble + caches completion results so reparses are
    cheap. Re-creates the TU when args change so option edits take effect."""
    cached = _tu_cache.get (filename)
    if cached is not None and cached [1] == args :
        return cached [0]
    opts = (TranslationUnit.PARSE_PRECOMPILED_PREAMBLE
            | TranslationUnit.PARSE_INCOMPLETE
            | TranslationUnit.PARSE_CACHE_COMPLETION_RESULTS)
    tu = _index_singleton ().parse (
        filename, args = args,
        unsaved_files = [(filename, source)],
        options = opts,
    )
    _tu_cache [filename] = (tu, args)
    return tu


def clangCompletions (filename, source, line, column, args = None) :
    """Return a list of completion names at `line:column` (both 1-based)
    in `filename`. `source` is the in-memory text. `args` is a list of
    clang command-line flags (e.g. ['-std=c++17', '-I/usr/include/qt5'])."""
    if args is None :
        args = ["-std=c++17"]
    try :
        tu = _open_tu (filename, source, tuple (args))
        results = tu.codeComplete (
            filename, line, column,
            unsaved_files = [(filename, source)],
            include_macros = True,
        )
    except Exception as e :
        print ("clangCompletions error:", e)
        return []
    if results is None :
        return []
    out = []
    seen = set ()
    for r in sorted (results.results, key = lambda x : x.string.priority) :
        # CompletionString is iterable; the typed-text chunk holds the
        # name the user actually types (others are signature/type info).
        for chunk in r.string :
            if chunk.isKindTypedText () :
                name = chunk.spelling
                if isinstance (name, bytes) :
                    name = name.decode ("utf-8", "replace")
                if name and name not in seen :
                    seen.add (name)
                    out.append (name)
                break
    return out


def clangResolve (filename, source, line, column, kind = "declaration") :
    """Return (target_file, target_line, target_column) for the symbol at
    `line:column` (1-based). `kind` is "declaration" (cursor.referenced)
    or "definition" (cursor.get_definition()). Returns None if nothing
    sensible was found."""
    try :
        tu = _open_tu (filename, source, ("-std=c++17",))
        # reparse with current source so cursor positions match the buffer
        tu.reparse (unsaved_files = [(filename, source)])
        loc = tu.get_location (filename, (line, column))
        cur = tu.cursor.from_location (tu, loc)
    except Exception as e :
        print ("clangResolve error:", e)
        return None
    if cur is None or not cur.location.file :
        return None

    if kind == "definition" :
        target = cur.get_definition ()
        if target is None or target.location.file is None :
            # No body in this TU — fall back to the declaration so the user
            # at least lands on the prototype rather than nowhere.
            target = cur.referenced
    else :
        target = cur.referenced
        if target is None :
            target = cur.get_definition ()

    if target is None or target.location.file is None :
        return None
    tloc = target.location
    return (tloc.file.name, tloc.line, tloc.column)


def invalidate (filename = None) :
    """Drop cached TU(s). Call after the user edits compile flags or
    deletes the file. With filename=None, drops everything."""
    if filename is None :
        _tu_cache.clear ()
    else :
        _tu_cache.pop (filename, None)
