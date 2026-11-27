#!/bin/bash
valac lexer.vala pas_parser.vala --color 2>&1 | python filter.py
# valac lexer.vala pas_parser.vala --color 2>&1 | python filter.py 3<&0- </dev/tty
