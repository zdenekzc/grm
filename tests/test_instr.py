"""
test_instr.py — testy pro cmm/cmm_instr.py (LLVM backend).

Sourozenec test_generate.py: stejné AST builders, stejné testy,
jiný backend.

Zatímco cmm_generate.py emituje x86_64 strojový kód přímo přes
iced-x86 + mmap, cmm_instr.py jde přes LLVM:

    AST (CmmExpr/CmmStat/...)
        │
        │  cmm_instr.code_program ()
        ▼
    LLVM IR  (alloca / load / store / GEP / call / ...)
        │
        │  llvmlite.binding (parse_assembly + opt + MCJIT)
        ▼
    optimalizovaný x86_64 strojový kód
        │
        │  ee.get_function_address("main") + ctypes.CFUNCTYPE
        ▼
    spuštění a kontrola návratu

Pro stejný program by oba backendy měly vrátit stejnou hodnotu.
Tento test verifikuje, že to skutečně tak je — sdílí AST builders
s test_generate.py importem, takže každá změna helpers se promítne
do obou test runnerů zároveň.

Spuštění:

    python3 view-mini/test/test_instr.py            # tichý souhrn
    python3 view-mini/test/test_instr.py -v         # + LLVM IR + assembly
"""

from __future__ import print_function

import os, sys, io, contextlib

# ---------------------------------------------------------------------------
# Cesty: sdílíme s test_generate.py přesně.

HERE = os.path.dirname (os.path.abspath (__file__))
ROOT = os.path.abspath (os.path.join (HERE, ".."))
for sub in [ "", "code", "grm", "_output", "cmm" ] :
   path = os.path.join (ROOT, sub) if sub else ROOT
   if path not in sys.path :
      sys.path.insert (0, path)

# Importujeme všechny AST buildery + FakeCompiler ze sourozeneckého testu.
# Když přibyde nový builder, oba backendy ho mají automaticky.
from test_generate import (
   FakeCompiler,
   lit, name, binop, index_expr, deref, addr, call,
   pre_inc, pre_dec, post_inc, post_dec,
   make_var, int_array, int_ptr, make_func,
   assign_stat, cassign_stat, expr_stat, with_init,
   ret, ifs, whiles, cmpd,
)
# Kind konstanty potřebné pro test funkce
from cmm_parser import (
   addExpr, subExpr, mulExpr, ltExpr, gtExpr, addAssignExpr,
)
import cmm_instr

# ---------------------------------------------------------------------------
# Test runner — stejný pattern jako test_generate, jen volá InstructionsModule.

def run_test (label, decls, expected, verbose = False) :
   """Postaví FakeCompiler s globálními decl-y, zavolá
   InstructionsModule.compile (), zachytí stdout a porovná
   návratovou hodnotu main () proti expected.

   Test bezpečně přepneme do tempdir, protože LLVM backend píše
   instr.o do cwd a my nechceme znečišťovat repository."""
   import tempfile

   compiler = FakeCompiler ()
   compiler.global_scope.item_list = decls

   buf = io.StringIO ()
   olddir = os.getcwd ()
   with tempfile.TemporaryDirectory () as tmpdir :
      try :
         os.chdir (tmpdir)
         with contextlib.redirect_stdout (buf) :
            cmm_instr.InstructionsModule (compiler).compile ()
      finally :
         os.chdir (olddir)
   captured = buf.getvalue ()

   if verbose :
      sys.stdout.write (captured)

   actual = None
   for line in captured.splitlines () :
      if line.startswith ("main returned:") :
         actual = int (line.split (":") [1].strip ())
         break

   ok = actual == expected
   marker = "PASS" if ok else "FAIL"
   print ("  [%s] %-50s expected %d, got %s" % (marker, label, expected, actual))
   return ok

# ---------------------------------------------------------------------------
# Testy — copy-paste struktur z test_generate.py, jen místo run_test
# voláme náš lokální (LLVM-backed) run_test.

def test_basic_arith (verbose) :
   """int main () { int x = 6; int y = 7; return x * y; }"""
   x = make_var ("x"); y = make_var ("y")
   body = cmpd ([
      with_init (x, lit (6)),
      with_init (y, lit (7)),
      ret (binop (mulExpr, name (x), name (y))),
   ])
   return run_test ("basic arith: 6 * 7", [ make_func ("main", [ ], body) ], 42, verbose)

def test_factorial (verbose) :
   """fact (5) přes while + rekurzivní volání mezi funkcemi"""
   from cmm_parser import mulAssignExpr, subAssignExpr
   n = make_var ("n"); r = make_var ("r")
   fact = make_func ("fact", [ n ], cmpd ([
      with_init (r, lit (1)),
      whiles (binop (gtExpr, name (n), lit (1)), cmpd ([
         cassign_stat (mulAssignExpr, name (r), name (n)),
         cassign_stat (subAssignExpr, name (n), lit (1)),
      ])),
      ret (name (r)),
   ]))
   main = make_func ("main", [ ], cmpd ([ ret (call (fact, [ lit (5) ])) ]))
   return run_test ("factorial: fact (5)", [ fact, main ], 120, verbose)

def test_max (verbose) :
   """max (a, b) přes if/else"""
   a = make_var ("a"); b = make_var ("b")
   mx = make_func ("max", [ a, b ], cmpd ([
      ifs (binop (gtExpr, name (a), name (b)), ret (name (a)), ret (name (b)))
   ]))
   main = make_func ("main", [ ], cmpd ([ ret (call (mx, [ lit (7), lit (13) ])) ]))
   return run_test ("if/else: max (7, 13)", [ mx, main ], 13, verbose)

def test_global (verbose) :
   """int g; main: g = 100; return g + 23;"""
   g = make_var ("g")
   main = make_func ("main", [ ], cmpd ([
      assign_stat (name (g), lit (100)),
      ret (binop (addExpr, name (g), lit (23))),
   ]))
   return run_test ("global scalar", [ g, main ], 123, verbose)

def test_global_array (verbose) :
   """int g[5]; main: vyplň g[i]=i*10, vrať součet"""
   g = int_array ("g", 5); i = make_var ("i"); s = make_var ("sum")
   main = make_func ("main", [ ], cmpd ([
      with_init (i, lit (0)),
      whiles (binop (ltExpr, name (i), lit (5)), cmpd ([
         assign_stat (index_expr (g, name (i)), binop (mulExpr, name (i), lit (10))),
         cassign_stat (addAssignExpr, name (i), lit (1)),
      ])),
      with_init (s, lit (0)),
      assign_stat (name (i), lit (0)),
      whiles (binop (ltExpr, name (i), lit (5)), cmpd ([
         cassign_stat (addAssignExpr, name (s), index_expr (g, name (i))),
         cassign_stat (addAssignExpr, name (i), lit (1)),
      ])),
      ret (name (s)),
   ]))
   return run_test ("global int g[5]: sum of i*10", [ g, main ], 100, verbose)

def test_pointer (verbose) :
   """int g[3]; int * p = &g[1]; return *p;"""
   g = int_array ("g", 3); p = int_ptr ("p")
   main = make_func ("main", [ ], cmpd ([
      assign_stat (index_expr (g, lit (0)), lit (11)),
      assign_stat (index_expr (g, lit (1)), lit (22)),
      assign_stat (index_expr (g, lit (2)), lit (33)),
      with_init (p, addr (index_expr (g, lit (1)))),
      ret (deref (name (p))),
   ]))
   return run_test ("pointer: *(&g[1])", [ g, main ], 22, verbose)

def test_compound_assign (verbose) :
   """x = 5; x += 7; return x;"""
   x = make_var ("x")
   main = make_func ("main", [ ], cmpd ([
      with_init (x, lit (5)),
      cassign_stat (addAssignExpr, name (x), lit (7)),
      ret (name (x)),
   ]))
   return run_test ("compound: x += 7 (x=5)", [ main ], 12, verbose)

def test_array_compound (verbose) :
   """g[1] = 40; g[1] += 2; return g[1];"""
   g = int_array ("g", 3)
   main = make_func ("main", [ ], cmpd ([
      assign_stat (index_expr (g, lit (1)), lit (40)),
      cassign_stat (addAssignExpr, index_expr (g, lit (1)), lit (2)),
      ret (index_expr (g, lit (1))),
   ]))
   return run_test ("compound on arr[i]: g[1] += 2", [ g, main ], 42, verbose)

def test_post_increment (verbose) :
   """int y = x++; return x*10 + y;"""
   x = make_var ("x"); y = make_var ("y")
   main = make_func ("main", [ ], cmpd ([
      with_init (x, lit (5)),
      with_init (y, post_inc (name (x))),
      ret (binop (addExpr,
                  binop (mulExpr, name (x), lit (10)),
                  name (y))),
   ]))
   return run_test ("postfix x++: returns old", [ main ], 65, verbose)

# ---------------------------------------------------------------------------

ALL_TESTS = [
   test_basic_arith,
   test_factorial,
   test_max,
   test_global,
   test_global_array,
   test_pointer,
   test_compound_assign,
   test_array_compound,
   test_post_increment,
]

def main () :
   verbose = "-v" in sys.argv or "--verbose" in sys.argv

   print ("Running %d tests through LLVM backend%s ..." %
          (len (ALL_TESTS), " (verbose)" if verbose else ""))

   passed = 0
   for test in ALL_TESTS :
      if test (verbose) :
         passed += 1

   total = len (ALL_TESTS)
   print ()
   print ("%d / %d passed" % (passed, total))
   sys.exit (0 if passed == total else 1)

if __name__ == "__main__" :
   main ()

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
