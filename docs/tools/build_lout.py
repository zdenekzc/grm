#!/usr/bin/env python3
"""Download and build the Lout document formatting system.

Usage:  python3 build_lout.py

Layout (both directories are outside git, see .gitignore):

    docs/_import/lout            the Lout sources (shallow git clone of
                                 https://github.com/william8000/lout,
                                 override with $LOUT_URL)
    docs/_import/user-manual.pdf the Lout User's Guide, compiled from
                                 doc/user with the freshly built lout
    docs/_library/lout/bin/lout  the lout binary (+ prg2lout)
    docs/_library/lout/share/lout-<version>/lib   library files

docs/tools/md2lout.py finds the binary in docs/_library/lout/bin
automatically, or you can point to it explicitly:

    export LOUT=$PWD/docs/_library/lout/bin/lout

Requires: git, make, a C compiler (gcc), ghostscript (ps2pdf).
Building the User's Guide takes a few minutes.
"""

import os, glob, subprocess, sys

TOOLS = os.path.dirname(os.path.abspath(__file__))
DOCS = os.path.dirname(TOOLS)
IMPORT = os.path.join(DOCS, "_import")
LIBRARY = os.path.join(DOCS, "_library")
SRC = os.path.join(IMPORT, "lout")
PREFIX = os.path.join(LIBRARY, "lout")
URL = os.environ.get("LOUT_URL", "https://github.com/william8000/lout")

def run(cmd, **kw):
    print("+", " ".join(cmd))
    return subprocess.run(cmd, **kw)

def build_lout():
    """Compile lout and install it under PREFIX; return True on success."""
    # The makefile bakes the library directory into the binary; it derives
    # it from PREFIX as $(PREFIX)/share/lout-$(VERSION)/lib.
    build = ["make", "PREFIX=" + PREFIX]
    r = run(build + ["clean"], cwd=SRC, capture_output=True)
    r = run(build, cwd=SRC, capture_output=True)
    if r.returncode != 0:
        err = r.stderr.decode(errors="replace")[-3000:] if r.stderr else ""
        sys.stderr.write(err)
        print("error: make failed", file=sys.stderr)
        return False
    r = run(build + ["install"], cwd=SRC, capture_output=True)
    if r.returncode != 0:
        print("error: make install failed", file=sys.stderr)
        return False
    return True

def verify():
    lout_bin = os.path.join(PREFIX, "bin", "lout")
    libs = sorted(glob.glob(os.path.join(PREFIX, "share", "lout*", "lib")))
    ok = (os.path.isfile(lout_bin) and os.access(lout_bin, os.X_OK)
          and libs
          and os.path.exists(os.path.join(libs[-1], "include", "report")))
    return (lout_bin, libs[-1] if libs else None) if ok else (None, None)

def build_user_manual(lout_bin):
    """Compile the Lout User's Guide (doc/user) into _import."""
    manual_dir = os.path.join(SRC, "doc", "user")
    ps = os.path.join(manual_dir, "user.ps")
    env = os.environ.copy()
    # the guide pipes program examples through prg2lout
    env["PATH"] = os.path.join(PREFIX, "bin") + os.pathsep + env["PATH"]
    # stale cross-reference databases break the run
    for stale in glob.glob(os.path.join(manual_dir, "*.ld")) + \
                 glob.glob(os.path.join(manual_dir, "*.ldx")) + \
                 glob.glob(os.path.join(manual_dir, "*.li")) + \
                 [ps]:
        try:
            os.remove(stale)
        except OSError:
            pass
    r = run([lout_bin, "-r4", "all", "-o", ps], cwd=manual_dir, env=env)
    if r.returncode != 0 or not os.path.exists(ps):
        print("error: building the User's Guide failed", file=sys.stderr)
        return False
    pdf = os.path.join(IMPORT, "user-manual.pdf")
    r = run(["ps2pdf", ps, pdf])
    if r.returncode != 0 or not os.path.exists(pdf):
        print("error: ps2pdf failed for the User's Guide", file=sys.stderr)
        return False
    return True

def main():
    os.makedirs(IMPORT, exist_ok=True)

    # ------------------------------------------------------------------ fetch
    if not os.path.exists(os.path.join(SRC, "makefile")):
        if os.path.exists(SRC):
            subprocess.run(["rm", "-rf", SRC])
        r = run(["git", "clone", "--depth", "1", URL, SRC])
        if r.returncode != 0:
            print("error: git clone failed", file=sys.stderr)
            return 1
    else:
        print("source already present:", SRC)

    # ------------------------------------------------------------------ build
    if not build_lout():
        return 1
    lout_bin, loutlib = verify()
    if not lout_bin:
        print("error: build incomplete - no working lout", file=sys.stderr)
        return 1
    print()
    print("lout built successfully:")
    print("  binary :", lout_bin)
    print("  prg2lout:", os.path.join(PREFIX, "bin", "prg2lout"))
    print("  lib    :", loutlib)

    # ------------------------------------------------- the Lout User's Guide
    print()
    if build_user_manual(lout_bin):
        print("User's Guide:", os.path.join(IMPORT, "user-manual.pdf"))
    else:
        print("warning: the User's Guide could not be built; "
              "lout itself is ready to use", file=sys.stderr)

    print()
    print("docs/tools/md2lout.py will find the binary automatically; or use:")
    print("  export LOUT=" + lout_bin)
    return 0

if __name__ == "__main__":
    sys.exit(main())
