#!/usr/bin/env python3
"""
test_parser_in_csharp.py — csharp balíček (wrapper nad tests/test_parser_in.py)

Vytvoří _output/parser_in_csharp/: vygenerované parsery a products
(cparser/cproduct s csharp = True) pro pas.g i cmm.g, runtime
lang/csharp/textio.cs (Lexer + Output), main, testovací data a run.sh,
který vše přeloží mcs a spustí přes mono. Pro cmm se vynechává jen
cmm_quicksort (příkazy potřebují reálné predikáty — viz
NOTE_QUICKSORT v tests/test_parser_in.py).
"""

import os, sys

sys.path.insert (0, os.path.dirname (os.path.abspath (__file__)))

import test_parser_in

if __name__ == "__main__" :
   sys.exit (test_parser_in.main (["--lang", "csharp"] + sys.argv [1 :]))
