#!/bin/bash
#
# setup-tcc-cpp.sh
#
# Build a *patched* TCC + tcc-cpp.so wrapper.  The patches add a "C++ light"
# layer on top of TinyCC: `new`, `delete`, `class` (= struct), `obj.method()`,
# `ptr->method()` and `Type::method()`, all rewritten to plain C calls of the
# form __CXX_<Type>_<method>(self, args...).
#
# Sources of the patches: ../../../../tinycc/tcc-h.diff, ../../../../tinycc/tcc-gen.diff
#
# This script is **not run by `make`** by default.  Invoke explicitly with
#   make tcc-cpp.so
# or
#   ./setup-tcc-cpp.sh
#
# Output: tcc-cpp.so in the current directory.
# Heads-up: as of writing the patches do not apply cleanly to upstream TCC
# (mob branch or release_0_9_27).  This script reports the failure and
# stops — fix the diffs and re-run.

set -e

cd "$(dirname "$0")"

PATCH_DIR=../../../../tinycc
TCC_DIR=tcc-cpp-src
TCC_REPO=https://repo.or.cz/tinycc.git

# 1. clone (separate checkout from vanilla tcc-src/)

if [ ! -d "$TCC_DIR" ] ; then
   echo "==> cloning $TCC_REPO into $TCC_DIR"
   git clone "$TCC_REPO" "$TCC_DIR"
fi

# 2. apply patches (idempotent — skip if already applied)

cd "$TCC_DIR"

if grep -q TOK_NEW tcc.h 2>/dev/null ; then
   echo "==> patches appear to be already applied (TOK_NEW present in tcc.h) — skipping"
else
   for diff in tcc-h.diff tcc-gen.diff ; do
       p="$(realpath ../$PATCH_DIR/$diff)"
       if [ ! -f "$p" ] ; then
          echo "ERROR: patch not found: $p"
          exit 1
       fi
       echo "==> applying $p"
       if ! patch -p1 < "$p" ; then
          echo "ERROR: $diff failed to apply.  Inspect tcc-cpp-src/*.rej for details."
          exit 1
       fi
   done
fi

# 3. configure + build + install

INSTALL_DIR="$(pwd)/install"

if [ ! -f config.mak ] ; then
   echo "==> configuring TCC (prefix=$INSTALL_DIR)"
   ./configure --prefix="$INSTALL_DIR"
fi

echo "==> building patched TCC"
make
make install

cd ..

# 4. build tcc-cpp.so (reuse the existing tcc-export.cc and tcc.h)

LIBTCC_A="$TCC_DIR/install/lib/libtcc.a"
TCC_LIB_PATH="$(pwd)/$TCC_DIR/install/lib/tcc"

if [ ! -f "$LIBTCC_A" ] ; then
   echo "ERROR: $LIBTCC_A not found after install"
   exit 1
fi

echo "==> building tcc_cpp.so (Python module name: tcc_cpp)"
g++ -O2 -fPIC -shared tcc-export.cc -o tcc_cpp.so \
    -DMODULE_NAME=tcc_cpp \
    -I "$TCC_DIR" \
    "$LIBTCC_A" \
    -DTCC_LIB_PATH="\"$TCC_LIB_PATH\"" \
    $(python3 -m pybind11 --includes) \
    -ldl

echo "==> done. tcc_cpp.so built. Try: python -c 'import tcc_cpp; print(tcc_cpp)'"
