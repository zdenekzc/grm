
# Top-level convenience makefile. JIT/LLVM build lives in tools/llvm-tools/,
# the TinyCC python wrapper in tools/tcc-tools/.

all: tools/llvm-tools/jit.so

tools/llvm-tools/jit.so:
	$(MAKE) -C tools/llvm-tools jit.so

tcc.so:
	$(MAKE) -C tools/tcc-tools tcc.so

tcc_cpp.so:
	$(MAKE) -C tools/tcc-tools tcc_cpp.so

tcc-clean:
	$(MAKE) -C tools/tcc-tools clean

# ---------------------------------------------------------------------------

clean:
	- $(MAKE) -C tools/llvm-tools clean
	- $(MAKE) -C tools/tcc-tools  clean
	- rm -f *.o *.so *.bin
	- rm -rf __pycache__ */__pycache__


run:
	$(MAKE) -C tools/llvm-tools run

# wsl --install
# sudo apt update
# sudo apt install mc qtcreator kdevelop kate meld locate
# sudo apt install python3-pybind11 python3-pyqt5 python-is-python3 python3-dev
# sudo apt install qtbase5-dev

# sudo apt install llvm clang llvm-dev libclang-dev libclang-cpp-dev

# WSL Ubuntu 24.04 Noble ... llvm, clang verze 18 nebo 20
# sudo apt install clang-18 llvm-18 libclang-18-dev libclang-cpp18-dev llvm-18-dev
# sudo apt install clang-20 llvm-20 libclang-20-dev libclang-cpp20-dev llvm-20-dev

# pkg-config --list-all
