#!/usr/bin/env python3
"""Download and build the Lout document formatting system into docs/_library.

Usage:  python3 build_lout.py

The Lout sources are cloned (shallow) from
https://github.com/william8000/lout (override with $LOUT_URL) into
docs/_library/src, compiled and installed into

    docs/_library/bin/lout        the lout binary (+ prg2lout)
    docs/_library/lib             its library files (include, font, ...)

The directory docs/_library is not part of the git repository (see
.gitignore).  docs/tools/md2lout.py finds the binary there automatically,
or you can point to it explicitly:

    export LOUT=$PWD/docs/_library/bin/lout

Requires: git, make, a C compiler (gcc), nothing else.
"""

import os, glob, shutil, subprocess, sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.dirname(TOOLS)
LIB = os.path.join(DOCS, "_library")
SRC = os.path.join(LIB, "src")
URL = os.environ.get("LOUT_URL", "https://github.com/william8000/lout")

def run(cmd, **kw):
    print("+", " ".join(cmd))
    return subprocess.run(cmd, **kw)

def main():
    os.makedirs(LIB, exist_ok=True)

    # ------------------------------------------------------------------ fetch
    if not os.path.exists(os.path.join(SRC, "makefile")):
        if os.path.exists(SRC):
            shutil.rmtree(SRC)
        r = run(["git", "clone", "--depth", "1", URL, SRC])
        if r.returncode != 0:
            print("error: git clone failed", file=sys.stderr)
            return 1
    else:
        print("source already present:", SRC)

    # ------------------------------------------------------------------ build
    # The makefile bakes the library directory into the binary; it derives
    # it from PREFIX as $(PREFIX)/share/lout-$(VERSION)/lib.
    build = ["make", "PREFIX=" + LIB]
    r = run(build + ["clean"], cwd=SRC, capture_output=True)
    r = run(build, cwd=SRC, capture_output=True)
    if r.returncode != 0:
        sys.stderr.write(r.stderr[-3000:].decode(errors="replace")
                         if isinstance(r.stderr, bytes) else r.stderr[-3000:])
        print("error: make failed", file=sys.stderr)
        return 1
    r = run(build + ["install"], cwd=SRC, capture_output=True)
    if r.returncode != 0:
        print("error: make install failed", file=sys.stderr)
        return 1

    # ----------------------------------------------------------------- verify
    lout_bin = os.path.join(LIB, "bin", "lout")
    libs = sorted(glob.glob(os.path.join(LIB, "share", "lout*", "lib")))
    loutlib = libs[-1] if libs else None
    if not (os.path.isfile(lout_bin) and
            os.access(lout_bin, os.X_OK) and
            loutlib and
            os.path.exists(os.path.join(loutlib, "include", "report"))):
        print("error: build incomplete - no", lout_bin, file=sys.stderr)
        return 1

    ver = subprocess.run([lout_bin], capture_output=True)
    print()
    print("lout built successfully:")
    print("  binary :", lout_bin)
    print("  prg2lout:", os.path.join(LIB, "bin", "prg2lout"))
    print("  lib    :", loutlib)
    print()
    print("docs/tools/md2lout.py will find it automatically; or use:")
    print("  export LOUT=" + lout_bin)
    return 0

if __name__ == "__main__":
    sys.exit(main())
