# TinyCC Python wrapper. `make` produces tcc.so via setup-tcc.sh which
# clones libtcc, builds it and links our pybind11 wrapper against it.
# `make tcc_cpp.so` builds the patched "C++ light" variant — patches live
# in ../../../../tinycc/tcc-{h,gen}.diff.

all: tcc.so

tcc.so:	tcc-export.cc tcc.h setup-tcc.sh
	./setup-tcc.sh

tcc_cpp.so:	tcc-export.cc tcc.h setup-tcc-cpp.sh
	./setup-tcc-cpp.sh

clean:
	- rm -rf tcc-src tcc-cpp-src
	- rm -f *.o *.so
	- rm -rf __pycache__
