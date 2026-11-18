"""
test_generate.py — testy pro cmm/cmm_generate.py.

Standardní průběh překladu:

    source.t (text)
       │
       │  parser  (cmm_parser.py, vygenerovaný z cmm.g)
       ▼
    syntaktický strom — CmmExpr, CmmStat, CmmDecl objekty
       │
       │  cmm_comp.py (sémantická analýza: jména, scope, typy)
       ▼
    sémantický strom — uzly mají item_decl, item_type, …
       │
       │  cmm_generate.py (genezace x86_64 přes iced-x86, mmap, ctypes)
       ▼
    spustitelný strojový kód, případně rovnou zavolaná main ()

Tento soubor přeskakuje prvních DVA kroky (parser + sémantika) a staví
strom rovnou v Pythonu pomocí pomocných funkcí níže. Tím dovolí
testovat generátor izolovaně — bez .t souboru, bez Qt, bez celého
cmm_comp. Pro studenty ukazuje:

  * jak vypadají AST objekty zevnitř (jaká jména polí mají)
  * co konkrétně cmm_generate.py očekává od cmm_comp.py
    (přiřazené item_decl, item_name, item_type, is_function …)
  * jak málo stačí na vyzkoušení malé funkce v JIT režimu

Spuštění:

    python3 view-mini/test/test_generate.py             # vše
    python3 view-mini/test/test_generate.py -v          # + dis-asm
"""

from __future__ import print_function

import os, sys, io, contextlib

# ---------------------------------------------------------------------------
# Cesty: testovací soubor leží v view-mini/test/, k modulům musíme nahoru.
# grm/ musí být v sys.path PŘED code_base — repo modul, ne stdlib `code`
# (stejné pořadí jako v cmm/cmm_run.py).

HERE = os.path.dirname (os.path.abspath (__file__))
ROOT = os.path.abspath (os.path.join (HERE, ".."))   # view-mini/
for sub in ["", "grm", "code", "_output", "cmm"] :
   path = os.path.join (ROOT, sub) if sub else ROOT
   if path not in sys.path :
      sys.path.insert (0, path)

# Standardní cmm moduly. cmm_parser musí být vygenerovaný v _output/
# (`python3 cmm/cmm_run.py examples/instr.t` ho zařídí, pokud ještě
# neexistuje).
from cmm_parser import (
   CmmIntValue, CmmName, CmmBinaryExpr, CmmAssignExpr, CmmCallExpr,
   CmmExprList, CmmIndexExpr, CmmDerefExpr, CmmAddrExpr,
   CmmIncExpr, CmmDecExpr, CmmPostIncExpr, CmmPostDecExpr,
   CmmSimpleItem, CmmSimpleDecl, CmmSimpleStat, CmmCompoundStat,
   CmmReturnStat, CmmIfStat, CmmWhileStat,
   intValue, simpleName, addExpr, subExpr, mulExpr, divExpr, modExpr,
   ltExpr, leExpr, gtExpr, geExpr, eqExpr, neExpr,
   addAssignExpr, subAssignExpr, mulAssignExpr, divAssignExpr,
   modAssignExpr, andAssignExpr, orAssignExpr, xorAssignExpr,
   shlAssignExpr, shrAssignExpr,
   assignExpr, callExpr, indexExpr, derefExpr, addrExpr,
   incExpr, decExpr, postIncExpr, postDecExpr,
   simpleStat, simpleDecl, compoundStat, returnStat, ifStat, whileStat,
)
import code_base as code_mod
import cmm_generate

# ---------------------------------------------------------------------------
# FakeCompiler — minimální atrapa toho, co od kompilátoru čeká
# GenerateModule.compile (). Skutečný CmmCustomCompiler dělá
# sémantickou analýzu, my jen poskytneme global_scope s naplněným
# item_listem a stub pro 'win' (IDE okno, v CLI je None).

class FakeCompiler (object) :

   def __init__ (self) :
       # global_scope musí být Scope z code.py (kvůli initNamespace,
       # který nastaví offsets, item_dict, item_list, …). Cmm_generate
       # iteruje přes global_scope.item_list a hledá CmmSimpleItem
       # (proměnné a funkce) i CmmClassDecl (struktury).
       self.global_scope = code_mod.Scope ()
       code_mod.initNamespace (self.global_scope)
       self.global_scope.item_list = [ ]
       self.win = None

# ---------------------------------------------------------------------------
# AST builders — funkce pro stavbu uzlů. Pojmenování zhruba kopíruje
# C výrazy (lit, name, binop, ...). Každá vrátí připravený objekt
# odpovídající třídy z cmm_parser.

# --- výrazy ---------------------------------------------------------

def lit (n) :
   "Celočíselný literál (int): lit(42) = AST uzel pro 42."
   e = CmmIntValue ()
   e.kind = intValue
   e.value = n
   return e

def name (decl) :
   """Odkaz na proměnnou / funkci / parametr — simpleName.
   decl je CmmSimpleItem, který reprezentuje danou entitu."""
   e = CmmName ()
   e.kind = simpleName
   e.item_decl = decl   # cmm_comp by toto vyplnil ze symbol table
   e.id = decl.item_name
   return e

def binop (kind, left, right) :
   "Binární výraz: binop(addExpr, lit(1), lit(2)) = 1+2."
   e = CmmBinaryExpr ()
   e.kind = kind
   e.left = left
   e.right = right
   return e

def index_expr (arr_decl, i_expr) :
   "arr[i] — pole se předává jako decl, index jako výraz."
   e = CmmIndexExpr ()
   e.kind = indexExpr
   e.left = name (arr_decl)
   e.param = i_expr
   return e

def deref (p_expr) :
   "*p — dereference ukazatele."
   e = CmmDerefExpr ()
   e.kind = derefExpr
   e.param = p_expr
   return e

def addr (target_expr) :
   "&x — adresa lvalue."
   e = CmmAddrExpr ()
   e.kind = addrExpr
   e.param = target_expr
   return e

def call (callee_decl, args) :
   "Volání funkce: callee_decl je CmmSimpleItem funkce, args list výrazů."
   c = CmmCallExpr ()
   c.kind = callExpr
   c.left = name (callee_decl)
   pl = CmmExprList ()
   pl.items = args
   c.param_list = pl
   return c

def pre_inc (target) :
   e = CmmIncExpr (); e.kind = incExpr; e.param = target; return e

def pre_dec (target) :
   e = CmmDecExpr (); e.kind = decExpr; e.param = target; return e

def post_inc (target) :
   e = CmmPostIncExpr (); e.kind = postIncExpr; e.left = target; return e

def post_dec (target) :
   e = CmmPostDecExpr (); e.kind = postDecExpr; e.left = target; return e

# --- proměnné a funkce (CmmSimpleItem) ------------------------------

def make_var (nm, item_type = None, is_func = False) :
   """Vytvoř CmmSimpleItem s rozumným defaultem typu (int).
   Cmm_comp normálně vyplňuje item_type ze syntaxe deklarace; tady to
   děláme ručně. is_func odlišuje funkci od proměnné."""
   item = CmmSimpleItem ()
   if is_func :
      code_mod.initFunction (item)
   else :
      code_mod.initVariable (item)
   item.item_name = nm
   item.is_function = is_func
   if item_type is None :
      t = code_mod.SimpleType ()
      t.type_int = True
      item_type = t
   item.item_type = item_type
   return item

def int_array (nm, count) :
   "int nm[count]"
   int_t = code_mod.SimpleType (); int_t.type_int = True
   arr_t = code_mod.ArrayType (); arr_t.type_from = int_t; arr_t.lim = lit (count)
   return make_var (nm, item_type = arr_t)

def int_ptr (nm) :
   "int * nm"
   int_t = code_mod.SimpleType (); int_t.type_int = True
   p_t = code_mod.PointerType (); p_t.type_from = int_t
   return make_var (nm, item_type = p_t)

def make_func (nm, params, body) :
   "int nm (params) { body }"
   f = make_var (nm, is_func = True)
   f.item_list = params
   f.item_body = body
   return f

# --- příkazy --------------------------------------------------------

def assign_stat (lhs, rhs) :
   "Příkaz 'lhs = rhs;' — vyrobíme assignExpr a obalíme do CmmSimpleStat."
   a = CmmAssignExpr ()
   a.kind = assignExpr
   a.left = lhs
   a.right = rhs
   s = CmmSimpleStat ()
   s.kind = simpleStat
   s.inner_expr = a
   return s

def cassign_stat (kind, lhs, rhs) :
   "Compound: 'lhs += rhs;' atd. — kind určuje operátor."
   a = CmmAssignExpr ()
   a.kind = kind
   a.left = lhs
   a.right = rhs
   s = CmmSimpleStat ()
   s.kind = simpleStat
   s.inner_expr = a
   return s

def expr_stat (e) :
   "Výraz jako příkaz: 'foo();' — užitečné pro volání bez návratu."
   s = CmmSimpleStat ()
   s.kind = simpleStat
   s.inner_expr = e
   return s

def with_init (item, init_expr) :
   """Deklarace s inicializací: 'int item_name = init_expr;'.
   CmmSimpleDecl má items=[item]; init je vnořený CmmInitializer
   s value (CmmInitSimple) jehož inner_expr je samotný výraz."""
   decl = CmmSimpleDecl ()
   decl.kind = simpleDecl
   decl.items = [ item ]
   if init_expr is not None :
      class _Stub : pass
      simple = _Stub (); simple.inner_expr = init_expr
      initz = _Stub (); initz.value = simple
      item.init = initz
   return decl

def ret (expr) :
   "return expr;"
   r = CmmReturnStat ()
   r.kind = returnStat
   r.return_expr = expr
   return r

def ifs (cond, then_stat, else_stat = None) :
   "if (cond) then_stat else else_stat — else je volitelný."
   s = CmmIfStat ()
   s.kind = ifStat
   s.cond = cond
   s.then_stat = then_stat
   s.else_stat = else_stat
   return s

def whiles (cond, body) :
   "while (cond) body"
   s = CmmWhileStat ()
   s.kind = whileStat
   s.cond = cond
   s.body = body
   return s

def cmpd (stats) :
   "Složený příkaz '{ stats }'."
   c = CmmCompoundStat ()
   c.kind = compoundStat
   c.items = stats
   return c

# ---------------------------------------------------------------------------
# Test runner — spustí program, zkontroluje návratovou hodnotu main ().

def run_test (label, decls, expected, verbose = False) :
   """Postaví FakeCompiler s globálními decl-y, zavolá GenerateModule
   a porovná návratovou hodnotu main () proti expected.

   GenerateModule píše dis-asm a hlášky na stdout. Pro test parser
   linky 'main returned: N' vždy zachytíme stdout do bufferu; v
   -v módu pak buffer ještě vypíšeme tak, jak by se chovala
   normální stdout."""
   compiler = FakeCompiler ()
   compiler.global_scope.item_list = decls

   buf = io.StringIO ()
   with contextlib.redirect_stdout (buf) :
      cmm_generate.GenerateModule (compiler).compile ()
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
# Konkrétní testy. Každý je samostatná funkce, aby šel spustit izolovaně.

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
   """int fact (int n) { int r = 1; while (n > 1) { r *= n; n -= 1; } return r; }
      int main () { return fact (5); }"""
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
   """int max (int a, int b) { if (a > b) return a; else return b; }
      int main () { return max (7, 13); }"""
   a = make_var ("a"); b = make_var ("b")
   mx = make_func ("max", [ a, b ], cmpd ([
      ifs (binop (gtExpr, name (a), name (b)), ret (name (a)), ret (name (b)))
   ]))
   main = make_func ("main", [ ], cmpd ([ ret (call (mx, [ lit (7), lit (13) ])) ]))
   return run_test ("if/else: max (7, 13)", [ mx, main ], 13, verbose)

def test_global (verbose) :
   """int g; int main () { g = 100; return g + 23; }"""
   g = make_var ("g")
   main = make_func ("main", [ ], cmpd ([
      assign_stat (name (g), lit (100)),
      ret (binop (addExpr, name (g), lit (23))),
   ]))
   return run_test ("global scalar", [ g, main ], 123, verbose)

def test_global_array (verbose) :
   """int g[5]; int main () {
        for (i in 0..4) g[i] = i * 10;
        for (i in 0..4) sum += g[i];
        return sum;            // 0 + 10 + 20 + 30 + 40 = 100
      }
   """
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
   """int g[3]; int main () { g[0]=11; g[1]=22; g[2]=33;
                               int * p = &g[1]; return *p; }
   """
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
   """int main () { int x = 5; x += 7; return x; }"""
   x = make_var ("x")
   main = make_func ("main", [ ], cmpd ([
      with_init (x, lit (5)),
      cassign_stat (addAssignExpr, name (x), lit (7)),
      ret (name (x)),
   ]))
   return run_test ("compound: x += 7 (x=5)", [ main ], 12, verbose)

def test_array_compound (verbose) :
   """int g[3]; int main () { g[1] = 40; g[1] += 2; return g[1]; }
      Test, že compound op nezahyne na RDX coby index v arr[i]."""
   g = int_array ("g", 3)
   main = make_func ("main", [ ], cmpd ([
      assign_stat (index_expr (g, lit (1)), lit (40)),
      cassign_stat (addAssignExpr, index_expr (g, lit (1)), lit (2)),
      ret (index_expr (g, lit (1))),
   ]))
   return run_test ("compound on arr[i]: g[1] += 2", [ g, main ], 42, verbose)

def test_post_increment (verbose) :
   """int main () { int x = 5; int y = x++; return x * 10 + y; }
      x++ vrátí starou hodnotu (5), x se zvedne na 6 -> 65."""
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
# Hlavní spouštění

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

   print ("Running %d tests%s ..." %
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
