# tests — test suites and example sources

This directory holds the test suites and the C-- example programs they
compile and run. All generated artifacts land in `_output/` (gitignored):
`_output/generate/` for the iced-x86 backend, `_output/llvm/` for the
LLVM backend.

## Test suites

### test_generate.py — iced-x86 backend

Compiles each example from [`tests/examples/`](examples/) with the full
compiler (`cmm_parser` + `cmm_comp`) and runs it through
`cmm/cmm_generate.py`, which emits x86-64 machine code directly
(iced-x86, RWX memory via `mmap`, called through `ctypes`).

Checks per example: `main ()` runs (the `main returned:` line appears)
and the program output ends with the expected line (`O.K.`, for `btree`
the last inserted value `800`).

Artifacts in `_output/generate/` per program:

- `<program>.asm` — disassembly listing of the emitted machine code
- `<program>.cc` — copy of the source
- `<program>.sh` — launcher script (runs the example through
  `cmm/cmm_iced.py`; the raw machine code cannot run standalone — it
  carries baked absolute addresses of libc functions)

### test_llvm.py — LLVM backend

The same examples through `cmm/cmm_llvm.py`: the compiler emits LLVM IR
(llvmlite) which is JIT-executed via MCJIT. Same checks as above.

Artifacts in `_output/llvm/` per program:

- `<program>.ll` — LLVM IR (runnable through `lli` as well)
- `<program>.bin` — executable ELF, linked from the object file with
  `gcc`; run it directly
- `<program>.cc` — copy of the source

### test_t_examples.py — `.t` examples smoke test

Reads the example list from `view/tools.ini` (the same manifest the
IDE's Examples menu uses), compiles each `.t` example with
`cmm/cmm_run.py` and runs the generated Python for a few seconds —
GUI examples are expected to stay alive (TIMEOUT = pass), console
examples to exit cleanly.

The generated `.t.py` / `.t.cpp` files land in `_output/t-examples/`
(gitignored), so the `.t` sources themselves stay clean; the generated
`.t.py` gets the executable bit.

### test_set.py — `set/` examples smoke test

The same machinery, for the `set/` sample sources (JSON, XML, text
I/O). Generated outputs go to `_output/set/`. The compile must run
from the repository root — `cmm/cmm_set.py` reads its data files
(`set/json.t`, ...) relative to the cwd.

### test_parser_in_vala.py, test_parser_in_python.py, test_parser_in_csharp.py, test_parser_in_cpp.py, test_parser_in_java.py — parser packages

Replaces `test_parsers.py`: for every supported target language it
builds a self-contained package in `_output/parser_in_<lang>/` that
the user can inspect and run on its own:

- the generated parser and product for `tests/grammar/pas.g` and
  `cmm/cmm.g` (the same settings as the Grammar menu actions)
- a `<name>_main.<ext>` wiring parser + product together
- the supporting runtime sources copied next to them
  (`lang/vala/textio.vala` for vala, `code/lexer.py` + `input.py` +
  `output.py` for python, `lang/csharp/textio.cs` for csharp,
  `lang/cpp/utils/` for cpp, `lang/java/textio.java` for java)
- `data/` with the example inputs from `tests/parsers/` and their
  `.expected` outputs (per language; vala, csharp and java inherit the
  ones from `tests/parsers/`, python and cpp record their own on first
  run, `--record` forces a rewrite — C++ `TextOutput` formats differently)
- `<name>_test.bin` binaries (vala, cpp) / `<name>_test.exe` (csharp) /
  `<name>_classes/` (java) and a `run.sh` that rebuilds everything and
  runs all the cases

Status: **vala** fully works (5/5); **python**, **csharp**, **cpp** and
**java** work for `pas.g` and for `cmm.g`'s `cmm_min.cc` (4/4 each). `cmm_min.cc` is intentionally
declaration-only — a bare generated parser has the semantic predicates
(`is_expression`, ...) only as stubs, so it cannot tell statements
like `x = 1 + 2 * 3;` from declarations; the real implementations live
in the compiler (`cmm/cmm.g` → `cmm_comp.CmmCustomCompiler`).
`cmm_quicksort.cc` stays as a vala-only case (it pins the degraded
GLib-critical parse); python, csharp, cpp and java skip it because their
`error ()` raises instead (see `NOTE_QUICKSORT` in `test_parser_in.py`).
**pascal** still has an incomplete runtime: the generated Pascal parser
is `class (Lexer)` but `lang/pascal/` has no source lexer with
`nextToken`/`mark`/`rewind` (`textio.pas` only does data I/O —
`binio.pas` itself now compiles with `fpc -S2`; `lang/pascal/gibbon/pas/lex0.pas`
is the best base for an adapter). That package reports SKIP with the
reason. For cpp, `lang/cpp/utils/parser_lexer.h` adapts `EnvInput` to
the generated parser (queued `nextToken`, `readIdent` from `tokenKind`);
`pas.g` gets the `CmmBasic` stub via `-DPARSER_BASIC_STUB`.

```
./tests/test_parser_in_vala.py        # vala package
./tests/test_parser_in_python.py      # python package
./tests/test_parser_in_csharp.py      # csharp package
./tests/test_parser_in_cpp.py         # cpp package
./tests/test_parser_in_java.py        # java package
python3 tests/test_parser_in.py --lang all
```

## Example sources

### examples/ — C-- programs

| Program | Content | Notes |
| ------- | ------- | ----- |
| `dama.cc` | 8 queens, prints all 92 solutions | |
| `veze.cc` | Hanoi towers | `main (int, char *[])` — backends call it with fabricated arguments |
| `jezdec.cc` | knight's tour | |
| `avl.cc` | AVL tree with rotations | |
| `btree.cc` | B-tree insertion | |
| `quicksort.cc` | quicksort of random data | |
| `heapsort.cc` | heapsort of random data | |
| `classes.cc` | classes, inheritance, static members | compiles, but the backends do not support constructors — computes wrong |
| `dictionary.cc` | `Dictionary<K, V>` template | needs templates — not supported by C-- yet |
| `sequence.cc` | `Sequence<T>` template | needs templates — not supported by C-- yet |
| `strings.cc` | `std::string` operations | needs `std::string` — not supported by C-- yet |

The first seven are the ones the test suites run. printf calls resolve
to libc at run time; the stub headers in `cmm/include/` provide the
declarations for the `#include` lines.

### t-examples/ — `.t` GUI examples

Qt examples for the simple-view IDE (application, button, component,
window, ...) wired into the Examples menu via `view/tools.ini`. The
generated `.t.cpp` / `.t.py` outputs are not kept in git — the test
writes them into `_output/tests/t-examples/`.

## Running

From the repository root:

```
./tests/test_generate.py        # iced-x86 backend, 7 examples
./tests/test_llvm.py            # LLVM backend, 7 examples
./tests/test_t_examples.py      # .t GUI examples smoke test
./tests/test_set.py             # set/ examples smoke test
```

Each script takes `-v` for verbose output and exits with the number of
failures (0 = all good).
