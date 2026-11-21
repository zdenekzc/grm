#!/usr/bin/env python3
"""Smoke-test every example listed in view/tools.ini.

For each path:
  1. compile  — run cmm/cmm_run.py to produce <path>.py
  2. start    — execute the generated .py with a short timeout
  3. judge    — TIMEOUT (still alive after timeout = "running OK"),
                EXIT0 (exited cleanly within timeout), or
                FAIL (non-zero exit + first stderr lines).

The generated .t.py / .t.cpp files land in a subdirectory of _output/
(gitignored) — the .t sources themselves stay clean.

Usage:
  ./test_examples.py                # default 2 s run timeout
  ./test_examples.py --timeout 5    # longer per-example wait

Exit code is the number of FAIL examples (0 = all good).
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

# Generated outputs go to _output/ (gitignored); cmm_run.py joins
# out_dir + path, so a .t source at tests/t-examples/button.t produces
# _output/tests/t-examples/button.t.py — the directory must exist.
OUT_DIR = os.path.join (ROOT, "_output")


# ANSI colors (tools.py renders them in the editor's Info panel; harmless
# in a plain terminal too).
_RED     = "\x1b[1;31m"
_GREEN   = "\x1b[1;32m"
_YELLOW  = "\x1b[1;33m"
_RESET   = "\x1b[0m"


def compile_one (path) :
    """Run cmm/cmm_run.py on `path`. Returns (ok, generated_py, stderr_tail).

    Stay in the repository root (so relative includes like "set/json.t"
    inside the .t file resolve correctly) and pass `-o _output` plus the
    relative path. cmm_run.py joins them as out_dir + path, which lands
    the generated .py / .cpp under _output/tests/t-examples/."""
    generated = os.path.join (OUT_DIR, path + ".py")
    target_dir = os.path.dirname (generated)
    if not os.path.isdir (target_dir) :
        os.makedirs (target_dir)
    cmd = [sys.executable, "cmm/cmm_run.py", "-o", OUT_DIR, path]
    try :
        proc = subprocess.run (cmd, capture_output = True, text = True,
                               timeout = 30)
    except subprocess.TimeoutExpired :
        return False, generated, "compile timed out (30 s)"
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


def main () :
    p = argparse.ArgumentParser (description = __doc__)
    p.add_argument ("--timeout", type = float, default = 2.0,
                    help = "seconds to keep each generated program alive (default 2)")
    p.add_argument ("--ini", default = None,
                    help = "path to the examples manifest (default: tools.ini next to tools_ini.py)")
    args = p.parse_args ()

    sections = listExamples (args.ini)
    if not sections :
        sys.exit ("no examples found in " + args.ini)

    fails = 0
    total = 0
    started = time.time ()

    for title, files in sections :
        print ()
        print ("== " + title + " (" + str (len (files)) + " examples) ==")
        for path in files :
            total += 1
            tag = path
            ok, gen, err = compile_one (path)
            if not ok :
                print ("  " + _RED + "COMPILE-FAIL" + _RESET +
                       "  " + tag + " — " + err)
                fails += 1
                continue
            verdict, detail = run_one (gen, args.timeout)
            if verdict == "FAIL" :
                fails += 1
                color = _RED
            elif verdict == "EXIT0" :
                color = _GREEN
            else :  # TIMEOUT — usually means a GUI loop, that's the success case here
                color = _GREEN
            print ("  " + color + verdict.ljust (12) + _RESET +
                   "  " + tag + " — " + detail)

    elapsed = time.time () - started
    print ()
    summary = ("summary: " + str (total - fails) + "/" + str (total) +
               " ok in " + ("%.1f" % elapsed) + " s")
    if fails == 0 :
        print (_GREEN + summary + _RESET)
    else :
        print (_RED + summary + " (" + str (fails) + " failed)" + _RESET)
    sys.exit (fails)


if __name__ == "__main__" :
    main ()
