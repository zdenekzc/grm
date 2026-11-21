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

The generated `.t.py` / `.t.cpp` files land in a subdirectory of
`_output/` (gitignored), so the `.t` sources themselves stay clean.

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
./tests/test_t_examples.py        # .t examples smoke test
```

Each script takes `-v` for verbose output and exits with the number of
failures (0 = all good).
