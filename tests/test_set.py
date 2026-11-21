#!/usr/bin/env python3
"""Smoke-test the set/ examples (sample sources: JSON, XML, text I/O).

The same machinery as tests/test_t_examples.py, just for the
[set-examples] section of view/tools.ini. The generated .t.py / .t.cpp
files land in _output/set/ (gitignored); the generated .t.py gets the
executable bit.

Usage:
  ./tests/test_set.py                # default 2 s run timeout
  ./tests/test_set.py --timeout 5    # longer per-example wait

Exit code is the number of FAIL examples (0 = all good).
"""

from __future__ import print_function

import os, sys, argparse, time

sys.path.insert (0, os.path.dirname (os.path.abspath (__file__)))

from test_t_examples import run_examples, _GREEN, _RED, _RESET

SECTION_PREFIX = "set/"

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

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
