#!/bin/sh
python ../../../../view/grm/cparser.py  ../../../../view/pas/pas.g --java --code pas_parser.java  --ns jview
python ../../../../view/grm/cproduct.py ../../../../view/pas/pas.g --java --code pas_product.java --ns jview