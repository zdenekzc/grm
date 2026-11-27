#!/usr/bin/env python3
"""
test_parser_in_vala.py — vala balíček (wrapper nad tests/test_parser_in.py)

Vytvoří _output/parser_in_vala/: vygenerované parsery a products pro
pas.g i cmm.g, podpůrný textio.vala, main, testovací data a run.sh,
který vše sestaví (valac) a spustí na všech datech. Viz
tests/test_parser_in.py.
"""

import os, sys

sys.path.insert (0, os.path.dirname (os.path.abspath (__file__)))

import test_parser_in

if __name__ == "__main__" :
   sys.exit (test_parser_in.main (["--lang", "vala"] + sys.argv [1 :]))
