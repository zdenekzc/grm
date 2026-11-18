# Machine-Generated Syntactic Analyzers

## A Grammar Describing the Grammar

[grammar](gram.md)

## Parser for the Grammar Description

[Reading the grammar description and storing it in a tree structure](gram_parser.md)

## Displaying the Grammar

[Display using HTML](gram_html.md)

[Display using the LOUT program](gram_lout.md)

## Sets of Symbols with which the Individual Grammar Rules Begin

[Nullable rules](gram_nullable.md)

[Symbol sets](gram_symbols.md)

## Syntactic Analyzer

[Parser (and also lexer)](parser.md)

## Program

http://github.com/zdenekzc/plain-grammar

# Object-Oriented Syntactic Trees

## A Syntactic Analyzer Creating a Syntactic Tree

[parser creating a tree](parser_tree.md)

## Printing a Program Stored in the Syntactic Tree

[product](product.md)

## Select

[select](select.md)

## Choose

[choose](choose.md)

## Program

http://github.com/zdenekzc/easy-grammar

# Examples

## Examples in the tutorial Directory

[c1 — a simple grammar for expressions and statements](c1.md)

[c2 — displaying the syntactic tree](c2.md)

[c3 — grammar with simplified declarations](c3.md)

[c3 — processing of declarations](c3_comp.md)

[c3 — conversion to Python](c3_python.md)

[c4 — syntactic predicates, instruction generation](c4.md)

http://github.com/zdenekzc/simple-view

## C--

[grammar of C--, semantic predicates](cmm_grammar.md)

[processing of declarations](cmm_comp.md)

[conversion to Python, PyQt](cmm_qt.md)

## CLang and Python

[cindex](cindex.md)

[peachpy](http://kmlinux.fjfi.cvut.cz/~culikzde/prekl/peachpy-fedora34.tgz)

# TCC

http://repo.or.cz/tinycc.git/blob/HEAD:/i386-gen.c#l699 gen_opi /* generate an integer binary operation */

http://repo.or.cz/tinycc.git/blob/HEAD:/x86_64-gen.c#l1705 gen_opi

http://repo.or.cz/tinycc.git/blob/HEAD:/tccgen.c#l6370 expr_landor

http://repo.or.cz/tinycc.git/blob/HEAD:/tccgen.c#l6943 block

http://repo.or.cz/tinycc.git/blob/HEAD:/i386-gen.c#l518 gfunc_prolog

https://repo.or.cz/tinycc.git/blob/HEAD:/x86_64-gen.c#l938 gfunc_prolog

http://repo.or.cz/tinycc.git/blob/HEAD:/tccgen.c#l8298 gen_function

http://repo.or.cz/tinycc.git/blob/HEAD:/tccgen.c#l8436 decl

http://repo.or.cz/tinycc.git/blob/HEAD:/tccgen.c#l383 tccgen_compile

http://repo.or.cz/tinycc.git/blob/HEAD:/libtcc.c#l776 tcc_compile_string

http://repo.or.cz/tinycc.git/blob/HEAD:/tccelf.c#l2809 elf_output_file

# Notes

[dots](dots.md)

http://tomassetti.me/a-tutorial-on-how-to-write-a-compiler-using-llvm

https://mukulrathi.com/create-your-own-programming-language/llvm-ir-cpp-api-tutorial/

http://mlir.llvm.org ( http://www.youtube.com/MLIRCompiler )

http://anoopsarkar.github.io/compilers-class/llvm-practice.html

http://llvm.org/docs/tutorial/MyFirstLanguageFrontend/LangImpl03.html

http://llvm.org/docs/tutorial/MyFirstLanguageFrontend/LangImpl05.html

lldb example http://github.com/llvm/llvm-project/blob/main/lldb/examples/python/disasm.py

createDiagnostics, llvm 20 https://maskray.me/blog/2025-03-09-compiling-c++-with-clang-api

llvm lite http://llvmlite.readthedocs.io/en/latest/user-guide/index.html

cpu0 http://jonathan2251.github.io/lbd/asm.html

Gede is a graphical frontend (GUI) to GDB written in C++ and using the Qt4 toolkit https://github.com/Nanoseb/gede

gdbgui - A modern, browser-based frontend to gdb https://www.gdbgui.com/

PeachPy - https://github.com/Maratyszcza/PeachPy

tcc - https://github.com/C-Chads/tinycc

8cc - https://github.com/rui314/8cc

chibicc - https://github.com/rui314/chibicc

http://github.com/learn-llvm/awesome-llvm

https://assignments.lrde.epita.fr/tools/llvm/irbuilder.html

https://asmjit.com/

https://github.com/zyantific/zasm

https://fileadmin.cs.lth.se/cs/Education/EDAN65/2021/lectures/L11.pdf

https://stackoverflow.com/questions/54465457/extracting-subvector-from-vector-register-in-llvm-ir

https://stackoverflow.com/questions/23873113/cuda-compilation-of-llvm-ir-using-nvptx

https://github.com/tendra/tendra

https://github.com/cksystemsteaching/selfie

https://github.com/anael-seghezzi/CToy

https://mapping-high-level-constructs-to-llvm-ir.readthedocs.io

https://docs.nvidia.com/cuda/nvjitlink/index.html#getting-started

https://docs.nvidia.com/cuda/archive/11.1.1/pdf/NVRTC_User_Guide.pdf

https://modal.com/gpu-glossary/host-software/nvrtc

https://docs.nvidia.com/cuda/cuda-driver-api/index.html

https://docs.nvidia.com/cuda/cuda-binary-utilities/index.html#instruction-set-ref

https://stackoverflow.com/questions/56564582/what-does-a-program-the-assembly-that-uses-a-gpu-even-look-like

C++26 Reflection https://isocpp.org/files/papers/P2996R4.html

Seed7 https://seed7.sourceforge.net/

Leslie Lamport TLA+ https://lamport.azurewebsites.net/tla/learning.html

https://en.wikipedia.org/wiki/List_of_object-oriented_programming_languages

clang precompiled preamble CINDEXTEST_PREAMBLE_FILE

g++ -std=c++20 -fmodules-ts -xc++-system-header iostream

g++ -std=c++20 -fmodules-ts main.cpp

https://llvmlite.readthedocs.io/en/latest/user-guide/ir/ir-builder.html

https://mapping-high-level-constructs-to-llvm-ir.readthedocs.io

https://acl.inf.ethz.ch/teaching/fastcode/2020/slides/07-simd-avx.pdf

https://github.com/AntKrotov/oberon-07-compiler/blob/master/source/X86.ob07

https://github.com/veselink1/refl-cpp

https://blog.rink.nu/2023/02/12/behind-the-magic-of-magic_enum/

https://thinkingeek.com/2016/01/06/tiny-gcc-front-part-2/

https://stackoverflow.com/questions/18672191/gcc-c-exception-handling-implementation

https://itanium-cxx-abi.github.io/cxx-abi/abi-eh.html

https://gabrieleserra.ml/blog/2020-08-27-an-introduction-to-gcc-and-gccs-plugins.html#InstrumentcodewithGCCcompilingoptions

gimple_build_call gimple_build_assign gimple_build_cond gimple_build_try

https://gcc.gnu.org/onlinedocs/gccint/GIMPLE.html

https://tldp.org/HOWTO/GCC-Frontend-HOWTO-7.html

https://gcc.gnu.org/onlinedocs/jit/topics/expressions.html#c.GCC_JIT_BINARY_OP_LOGICAL_AND

https://github.com/gcc-mirror/gcc/blob/master/gcc/jit/jit-playback.cc#L2355 add_assignment

https://github.com/gcc-mirror/gcc/blob/master/gcc/jit/jit-recording.cc#L7425 recording::assignment::replay_into recording::assignment::write_reproducer

https://github.com/gcc-mirror/gcc/blob/master/gcc/cp/cp-tree.h#L8012 cp-tree.h begin_try_block

https://gcc.gnu.org/onlinedocs/gccint/Example.html define_insn

https://kristerw.blogspot.com/2017/08/gcc-target-description-macros-and.html

https://atgreen.github.io/ggx/

http://moxielogic.org/blog/qemu-says-hello-world.html

https://github.com/ghaerr/ncc

https://fevtyp.com/naive/
