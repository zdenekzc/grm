#!/usr/bin/env python3
"""Smoke-test the .t GUI examples (tests/t-examples/).

For each example listed in view/tools.ini:
  1. compile  — run cmm/cmm_run.py to produce <name>.t.py
  2. start    — execute the generated .t.py with a short timeout
  3. judge    — TIMEOUT (still alive after timeout = "running OK"),
                EXIT0 (exited cleanly within timeout), or
                FAIL (non-zero exit + first stderr lines).

The generated .t.py / .t.cpp files land in _output/t-examples/
(gitignored) — the .t sources themselves stay clean, and the generated
.t.py gets the executable bit (it has a #! line).

Usage:
  ./tests/test_t_examples.py                # default 2 s run timeout
  ./tests/test_t_examples.py --timeout 5    # longer per-example wait

Exit code is the number of FAIL examples (0 = all good).

The set/ examples (.t files with JSON/XML/textio data) are tested the
same way by tests/test_set.py, which reuses run_examples () from here.
"""

import os
import sys
import subprocess
import argparse
import time

HERE = os.path.dirname (os.path.abspath (__file__))
ROOT = os.path.abspath (os.path.join (HERE, ".."))
sys.path.insert (0, os.path.join (ROOT, "view"))   # tools_ini

from tools_ini import listExamples

# The [section] of view/tools.ini this test covers — matched by the
# path prefix of the listed files (listExamples () returns section
# titles, not section names).
SECTION_PREFIX = "tests/t-examples/"

# Generated outputs go to _output/t-examples/ (gitignored). cmm_run.py
# joins out_dir + path, so we run it from the source's directory with
# the bare file name: out_dir=_output/t-examples + button.t →
# _output/t-examples/button.t.py.
OUT_DIR = os.path.join (ROOT, "_output")

# ANSI colors (tools.py renders them in the editor's Info panel; harmless
# in a plain terminal too).
_RED     = "\x1b[1;31m"
_GREEN   = "\x1b[1;32m"
_YELLOW  = "\x1b[1;33m"
_RESET   = "\x1b[0m"


def compile_one (path) :
    """Run cmm/cmm_run.py on `path` (repo-relative). Returns
    (ok, generated_py, stderr_tail).

    Compile from the repository root: cmm_set.py reads its data files
    ("set/json.t", ...) relative to the cwd, so it must not change.
    cmm_run.py joins out_dir + path, which would nest the output as
    _output/tests/t-examples/... — after the compile we move the
    generated files one directory up, to _output/t-examples/
    (resp. _output/set/ for the set/ sources)."""
    src_dir = os.path.dirname (path)
    name = os.path.basename (path)
    out_sub = os.path.basename (src_dir)
    final_dir = os.path.join (OUT_DIR, out_sub)
    if not os.path.isdir (final_dir) :
        os.makedirs (final_dir)
    # cmm_run.py nevytváří adresáře — ten vnořený (_output/tests/…)
    # musí existovat, i když ho hned poté přesuneme o úroveň výš.
    nested = os.path.join (OUT_DIR, src_dir)
    if not os.path.isdir (nested) :
        os.makedirs (nested)
    generated = os.path.join (final_dir, name + ".py")
    cmd = [sys.executable, os.path.join (ROOT, "cmm", "cmm_run.py"),
           "-o", OUT_DIR, path]
    try :
        proc = subprocess.run (cmd, capture_output = True, text = True,
                               timeout = 30, cwd = ROOT)
    except subprocess.TimeoutExpired :
        return False, generated, "compile timed out (30 s)"
    # cmm_run.py wrote OUT_DIR/<src_dir>/<name>.t.{py,cpp} — move them
    # one directory up, to _output/<out_sub>/.
    for ext in (".py", ".cpp") :
        nested_file = os.path.join (nested, name + ext)
        if os.path.isfile (nested_file) :
            os.replace (nested_file, os.path.join (final_dir, name + ext))
    # Uklid prázdných vnořených adresářů (_output/tests/t-examples → …).
    d = nested
    while d != OUT_DIR and os.path.isdir (d) :
        try :
            os.rmdir (d)   # projde jen když je adresář prázdný
        except OSError :
            break
        d = os.path.dirname (d)
    if proc.returncode != 0 or not os.path.isfile (generated) :
        tail = (proc.stderr or proc.stdout or "").splitlines () [-3:]
        return False, generated, "\n        ".join (tail)
    # Vygenerovaný .t.py je spustitelný skript (má #! na prvním řádku).
    os.chmod (generated, 0o755)
    return True, generated, ""


def run_one (py_path, timeout) :
    """Try to run the generated .py for `timeout` seconds. Returns
    (verdict, detail) where verdict is 'TIMEOUT', 'EXIT0' or 'FAIL'."""
    cmd = [sys.executable, py_path]
    proc = subprocess.Popen (cmd, stdout = subprocess.PIPE,
                                  stderr = subprocess.PIPE,
                                  text = True)
    try :
        out, err = proc.communicate (timeout = timeout)
    except subprocess.TimeoutExpired :
        proc.terminate ()
        try :
            proc.wait (timeout = 2)
        except subprocess.TimeoutExpired :
            proc.kill ()
        return "TIMEOUT", "still alive after " + str (timeout) + " s"
    if proc.returncode == 0 :
        return "EXIT0", "exited cleanly"
    tail = (err or out).splitlines () [-3:]
    return "FAIL", "\n        ".join (tail) or ("rc=" + str (proc.returncode))


def run_examples (section_prefix, timeout, verbose = False) :
    """Compile and run every tools.ini example whose path starts with
    `section_prefix`. Returns (ok_count, total). Shared with
    tests/test_set.py."""
    sections = listExamples (None)
    files = [ ]
    title = None
    for name, section_files in sections :
        if section_files and section_files [0].startswith (section_prefix) :
            title = name
            files = section_files
            break
    if not files :
        sys.exit ("no examples with prefix " + section_prefix + " in tools.ini")

    ok_count = 0
    for path in files :
        ok, gen, err = compile_one (path)
        if not ok :
            print ("  " + _RED + "COMPILE-FAIL" + _RESET +
                   "  " + path + " — " + err)
            continue
        verdict, detail = run_one (gen, timeout)
        if verdict == "FAIL" :
            color = _RED
        else :
            # TIMEOUT — usually means a GUI loop, that's the success case
            ok_count += 1
            color = _GREEN if verdict == "EXIT0" else _YELLOW
        print ("  " + color + verdict.ljust (12) + _RESET +
               "  " + path + " — " + detail)
    return ok_count, len (files)


def main () :
    p = argparse.ArgumentParser (description = __doc__)
    p.add_argument ("--timeout", type = float, default = 2.0,
                    help = "seconds to keep each generated program alive (default 2)")
    args = p.parse_args ()

    started = time.time ()
    print ("== " + SECTION_PREFIX + " ==")
    ok, total = run_examples (SECTION_PREFIX, args.timeout)

    elapsed = time.time () - started
    print ()
    summary = ("summary: " + str (ok) + "/" + str (total) +
               " ok in " + ("%.1f" % elapsed) + " s")
    if ok == total :
        print (_GREEN + summary + _RESET)
    else :
        print (_RED + summary + " (" + str (total - ok) + " failed)" + _RESET)
    sys.exit (total - ok)


if __name__ == "__main__" :
    main ()
