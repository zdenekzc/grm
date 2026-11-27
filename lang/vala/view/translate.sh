#!/bin/sh
# vygeneruje Vala parser a produkt z lang/pas.g pomoci grm/ v boefu
# (spousteno z adresare lang/vala/view)
GRM=$(cd ../../../grm && pwd) || exit 1
G=$(cd ../../ && pwd)/pas.g
python3 "$GRM/cparser.py"  "$G" --vala --class Parser --code pas_parser.vala || exit 1
python3 "$GRM/cproduct.py" "$G" --vala --class Product --super Output \
        --parser pas_parser --code pas_product.vala || exit 1
