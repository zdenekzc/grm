#!/usr/bin/env python3
"""
test_parser_in_cpp.py — cpp balíček (wrapper nad tests/test_parser_in.py)

Vytvoří _output/parser_in_cpp/: vygenerované parsery a products
(cparser/cproduct s cpp = True) pro pas.g i cmm.g, C++ runtime
lang/cpp/utils (TextInput/EnvInput/TextOutput) s adaptérem
parser_lexer.h, main, testovací data a run.sh, který vše přeloží g++
a spustí. Pro cmm se vynechává jen cmm_quicksort (příkazy potřebují
reálné predikáty — viz NOTE_QUICKSORT v tests/test_parser_in.py).
"""

import os, sys

sys.path.insert (0, os.path.dirname (os.path.abspath (__file__)))

import test_parser_in

if __name__ == "__main__" :
   sys.exit (test_parser_in.main (["--lang", "cpp"] + sys.argv [1 :]))
