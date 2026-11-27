#!/bin/sh

python ../../view/grm/toparser.py  ../../view/pas/pas.g --code pas_parser.py
python ../../view/grm/toproduct.py ../../view/pas/pas.g --code pas_product.py

python ../../view/grm/cparser.py  ../../view/pas/pas.g --header pas_parser.hpp --code pas_parser.cpp
python ../../view/grm/cproduct.py ../../view/pas/pas.g --header pas_product.hpp --code pas_product.cpp --parser pas_parser.h

python ../../view/grm/cparser.py  ../../view/pas/pas.g --pascal --code pas_parser.pas --ns Pas_Parser
python ../../view/grm/cproduct.py ../../view/pas/pas.g --pascal --code pas_product.pas --ns Pas_Product --parser Pas_Parser
