#!/bin/sh

python ../../view/grm/pparser.py  ../../view/pas/pas.g --code pas_parser.pas
python ../../view/grm/pproduct.py ../../view/pas/pas.g --code pas_product.pas

# python ../../view/grm/cparser.py  ../../view/pas/pas.g --pascal --code pas_parser.pas
# python ../../view/grm/cproduct.py ../../view/pas/pas.g --pascal --code pas_product.pas
