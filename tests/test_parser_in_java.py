#!/usr/bin/env python3
"""
test_parser_in_java.py — java balíček (wrapper nad tests/test_parser_in.py)

Vytvoří _output/parser_in_java/: vygenerované parsery a products
(cparser/cproduct s java = True) pro pas.g i cmm.g, runtime
lang/java/textio.java (Lexer + Output v package parserin), main,
testovací data a run.sh, který každou gramatiku přeloží pomocí javacu
do vlastního <name>_classes a spustí přes java. Pro cmm se vynechává jen
cmm_quicksort (příkazy potřebují reálné predikáty — viz
NOTE_QUICKSORT v tests/test_parser_in.py).
"""

import os, sys

sys.path.insert (0, os.path.dirname (os.path.abspath (__file__)))

import test_parser_in

if __name__ == "__main__" :
   sys.exit (test_parser_in.main (["--lang", "java"] + sys.argv [1 :]))
