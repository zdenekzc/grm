# rustc --color=always mini_parser.rs -o mini_parser.bin 2>&1 | less -R
# rustc --color=always example.rs -o example.bin 2>&1 | less -R
rustc --color=always mini_parser.rs -o mini_parser.bin 2>&1 | python ../vala-view/filter.py
