#!/bin/sh
python ../../view/grm/cparser.py ../../view/cmm/cmm.g --csharp --code pas_parser.cs
python ../../view/grm/cproduct.py ../../view/cmm/cmm.g --csharp --code pas_product.cs