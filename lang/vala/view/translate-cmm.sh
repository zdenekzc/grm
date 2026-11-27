#!/bin/sh
python ../../view/grm/cparser.py ../../view/cmm/cmm.g --vala --code pas_parser.vala
python ../../view/grm/cproduct.py ../../view/cmm/cmm.g --vala --code pas_product.vala