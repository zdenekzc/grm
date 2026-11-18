# LLVM/Clang JIT Python module — `make` produces jit.so which is imported
# by view.py's "JIT C++ File" action. Built with the system clang/llvm
# (override by uncommenting the version-pinned blocks).

PYBIND_CXXFLAGS += -fPIC $(shell python3 -m pybind11 --includes)

LDFLAGS += -lstdc++

LLVM_CXXFLAGS += -fPIC $(shell llvm-config --cxxflags)
LDFLAGS += $(shell llvm-config --ldflags --link-shared --libs)
LDFLAGS += -lclang-cpp
RESOURCE_DIR = $(shell clang -print-resource-dir)

# CXXFLAGS += $(shell llvm-config-18 --cxxflags)
# LDFLAGS += $(shell llvm-config-18 --ldflags --link-shared --libs)
# LDLIBS += -lclang-cpp18
# RESOURCE_DIR = $(shell clang-18 -print-resource-dir)

# CXXFLAGS += $(shell llvm-config-20 --cxxflags)
# LDFLAGS += $(shell llvm-config-20 --ldflags --link-shared --libs)
# LDFLAGS += -lclang-cpp20
# RESOURCE_DIR = $(shell clang-20 -print-resource-dir)


all: jit.so

jit.so:	jit.o jit-export.o
	gcc jit.o jit-export.o -shared -o jit.so $(LDFLAGS) $(LDLIBS)

jit-export.o: jit-export.cc jit.h
	gcc -c jit-export.cc -o jit-export.o $(PYBIND_CXXFLAGS)

jit.o: jit.h jit.cc
	echo RESOURCE_DIR=$(RESOURCE_DIR)
	gcc -c jit.cc -o jit.o $(LLVM_CXXFLAGS) -DRESOURCE_DIR=\"$(RESOURCE_DIR)\"

clean:
	- rm -f *.o *.so
	- rm -rf __pycache__

run:
	python run.py

# Required packages:
# Fedora:        dnf install llvm-devel clang-devel pybind11-devel
# Debian/Ubuntu: apt install llvm-dev libclang-dev libclang-cpp-dev python3-pybind11
