#!/bin/bash
#
# setup-tcc.sh
#
# Bootstrap the TinyCC sources and build a Python module (tcc.so) that
# wraps libtcc via pybind11.
#
#   1) git clone https://repo.or.cz/tinycc.git tcc-src   (only if missing)
#   2) ./configure --prefix=$(pwd)/install && make && make install
#   3) g++ tcc-export.cc -> tcc.so, statically linking libtcc.a
#
# Idempotent: re-running only repeats the missing steps.

set -e

cd "$(dirname "$0")"

TCC_DIR=tcc-src
TCC_REPO=https://repo.or.cz/tinycc.git

# 1. clone

if [ ! -d "$TCC_DIR" ] ; then
   echo "==> cloning $TCC_REPO"
   git clone "$TCC_REPO" "$TCC_DIR"
fi

# 2. configure + build + local install

cd "$TCC_DIR"
INSTALL_DIR="$(pwd)/install"

if [ ! -f config.mak ] ; then
   echo "==> configuring TCC (prefix=$INSTALL_DIR)"
   ./configure --prefix="$INSTALL_DIR"
fi

if [ ! -f libtcc.a ] ; then
   echo "==> building TCC"
   make
fi

if [ ! -f "$INSTALL_DIR/lib/libtcc.a" ] ; then
   echo "==> installing TCC into $INSTALL_DIR"
   make install
fi

cd ..

# 3. build the pybind11 wrapper

LIBTCC_A="$TCC_DIR/install/lib/libtcc.a"
TCC_LIB_PATH="$(pwd)/$TCC_DIR/install/lib/tcc"

if [ ! -f "$LIBTCC_A" ] ; then
   echo "ERROR: $LIBTCC_A not found after install"
   exit 1
fi

echo "==> building tcc.so (pybind11 wrapper)"
g++ -O2 -fPIC -shared tcc-export.cc -o tcc.so \
    -I "$TCC_DIR" \
    "$LIBTCC_A" \
    -DTCC_LIB_PATH="\"$TCC_LIB_PATH\"" \
    $(python3 -m pybind11 --includes) \
    -ldl

echo "==> done. tcc.so built. Try: python -c 'import tcc; print(tcc)'"
