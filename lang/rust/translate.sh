#!/bin/sh
python ../../view/grm/cparser.py  ../../view/mini/cmini.g --rust --code mini_parser.rs
python ../../view/grm/cproduct.py ../../view/mini/cmini.g --rust --code mini_product.rs