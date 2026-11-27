#!/usr/bin/env python3
"""
test_parser_in_python.py — python balíček (wrapper nad tests/test_parser_in.py)

Vytvoří _output/parser_in_python/: vygenerované parsery a products
(toparser/toproduct produkují Python) pro pas.g i cmm.g, podpůrné
zdroje code/lexer.py + input.py + output.py, main, testovací data
a run.sh, který vše spustí přes python3. Pro cmm se vynechává jen
cmm_quicksort (příkazy potřebují reálné predikáty — viz
NOTE_QUICKSORT v tests/test_parser_in.py).
"""

import os, sys

sys.path.insert (0, os.path.dirname (os.path.abspath (__file__)))

import test_parser_in

if __name__ == "__main__" :
   sys.exit (test_parser_in.main (["--lang", "python"] + sys.argv [1 :]))
