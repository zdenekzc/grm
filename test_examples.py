#!/usr/bin/env python3
"""Smoke-test every example listed in tools.ini.

For each path:
  1. compile  — run cmm/cmm_run.py to produce <path>.py
  2. start    — execute the generated .py with a short timeout
  3. judge    — TIMEOUT (still alive after timeout = "running OK"),
                EXIT0 (exited cleanly within timeout), or
                FAIL (non-zero exit + first stderr lines).

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

from tools_ini import listExamples


# ANSI colors (tools.py renders them in the editor's Info panel; harmless
# in a plain terminal too).
_RED     = "\x1b[1;31m"
_GREEN   = "\x1b[1;32m"
_YELLOW  = "\x1b[1;33m"
_RESET   = "\x1b[0m"


def compile_one (path) :
    """Run cmm/cmm_run.py on `path`. Returns (ok, generated_py, stderr_tail).

    Stay in the editor's cwd (so relative includes like "set/json.t"
    inside the .t file resolve correctly) and pass `-o .` plus the
    relative path. cmm_run.py joins them as out_dir + path = "./<path>",
    which lands the .py / .cpp next to the .t source."""
    generated = path + ".py"
    cmd = [sys.executable, "cmm/cmm_run.py", "-o", ".", path]
    try :
        proc = subprocess.run (cmd, capture_output = True, text = True,
                               timeout = 30)
    except subprocess.TimeoutExpired :
        return False, generated, "compile timed out (30 s)"
    if proc.returncode != 0 or not os.path.isfile (generated) :
        tail = (proc.stderr or proc.stdout or "").splitlines () [-3:]
        return False, generated, "\n        ".join (tail)
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
    p.add_argument ("--ini", default = "tools.ini",
                    help = "path to the examples manifest (default tools.ini)")
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
