#!/usr/bin/env python3
"""cmm_compile.py — compile one .t source with artifacts under _output/.

Runs cmm/cmm_run.py from the project root — .t sources reference data
files like "set/json.t" relative to the cwd, so the compile must not
change directory — and relocates the generated .t.py / .t.cpp one
directory up, to _output/<source directory name>/ (tests/t-examples →
_output/t-examples, set → _output/set). Same layout as
tests/test_t_examples.py; the .t sources themselves stay clean.

Used by the IDE's "Run T File" action (view/view.py), which afterwards
loads both generated files into the editor and runs the .py.

Usage: python3 cmm/cmm_compile.py <example path>
"""

from __future__ import print_function

import os, sys, subprocess

ROOT = os.path.dirname (os.path.dirname (os.path.abspath (__file__)))
OUT_DIR = os.path.join (ROOT, "_output")

def main () :
    if len (sys.argv) != 2 :
        sys.exit ("usage: cmm_compile.py <example path>")

    path = sys.argv [1]
    if not os.path.isabs (path) :
        path = os.path.join (os.getcwd (), path)
    rel = os.path.relpath (path, ROOT)
    src_dir = os.path.dirname (rel)
    name = os.path.basename (rel)

    final_dir = os.path.join (OUT_DIR, os.path.basename (src_dir))
    nested = os.path.join (OUT_DIR, src_dir)
    if not os.path.isdir (final_dir) :
        os.makedirs (final_dir)
    # cmm_run.py nevytváří adresáře — vnořený cíl musí existovat.
    if not os.path.isdir (nested) :
        os.makedirs (nested)

    cmd = [sys.executable, os.path.join (ROOT, "cmm", "cmm_run.py"),
           "-o", OUT_DIR, rel]
    proc = subprocess.run (cmd, cwd = ROOT)
    if proc.returncode != 0 :
        sys.exit (proc.returncode)

    # Přesuň vygenerované soubory o úroveň výš do _output/<sub>/.
    for ext in (".py", ".cpp") :
        nested_file = os.path.join (nested, name + ext)
        if os.path.isfile (nested_file) :
            target = os.path.join (final_dir, name + ext)
            os.replace (nested_file, target)
            print ("wrote", target)

    # Uklid prázdných vnořených adresářů (_output/tests/t-examples → …).
    d = nested
    while d != OUT_DIR and os.path.isdir (d) :
        try :
            os.rmdir (d)   # projde jen když je adresář prázdný
        except OSError :
            break
        d = os.path.dirname (d)

if __name__ == "__main__" :
    main ()

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
