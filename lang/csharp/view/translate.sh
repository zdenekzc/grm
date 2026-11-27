#!/bin/sh
python ../../view/grm/cparser.py ../../view/pas/pas.g  --csharp --ns SharpView --code pas_parser.cs
python ../../view/grm/cproduct.py ../../view/pas/pas.g --csharp --ns SharpView --code pas_product.cs
