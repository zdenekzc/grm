
# cmm_llvm.py

from __future__ import print_function

import os, sys
# from ctypes import CFUNCTYPE, c_double
import ctypes
from time import time

use_llvmlite = True

try :
   import numpy as np
except :
   print ("missing numpy")
   use_llvmlite = False

try :
   # Fedora 34
   # root: dnf install numpy
   # user: pip install llvmlite
   #       export PYTHONPATH=$HOME/.local/lib/python3.9/site-packages/

   incl_dir = os.path.expanduser ("~/.local/lib/python3.9/site-packages")
   if incl_dir not in sys.path :
      if os.path.exists (incl_dir) :
         sys.path.insert (1, incl_dir)
         print ("ADD", incl_dir)

   work_dir = os.path.abspath (sys.path [0])
   incl_dir = os.path.join (work_dir, "_library/llvmlite-0.40.0rc1")
   if incl_dir not in sys.path :
      if os.path.exists (incl_dir) :
         sys.path.insert (1, incl_dir)
         print ("ADD", incl_dir)

   # import numpy as np
   import llvmlite.binding as llvm
   import llvmlite.ir as ir
except :
   print ("missing llvmlite")
   use_llvmlite = False

# from input import quoteString
# from lexer import LexerInput
# from output import Output
# from code import SimpleType, NamedType
from code_base import *
from cmm_parser import *

# --------------------------------------------------------------------------

class InstructionsModule (object) :

   def __init__ (self, compiler) :
       super (InstructionsModule, self).__init__ ()
       self.compiler = compiler

   def compile (self) :

       if not use_llvmlite :
          print ("MISSING llvmlite")

       if use_llvmlite :
          # self.example1 ()
          # self.example2 ()
          # self.example3 ()
          self.code_program ()

   # -----------------------------------------------------------------------

   def example1 (self) :
       # llvmlite/examples/ll_fpadd.py

       llvm.initialize ()
       llvm.initialize_native_target ()
       llvm.initialize_native_asmprinter ()

       llvm_ir = """
          ; ModuleID = "examples/ir_fpadd.py"
          target triple = "unknown-unknown-unknown"
          target datalayout = ""

          define double @"fpadd"(double %".1", double %".2")
          {
          entry:
            %"res" = fadd double %".1", %".2"
            ret double %"res"
          }
          """

       # Create a target machine representing the host
       target = llvm.Target.from_default_triple ()
       target_machine = target.create_target_machine ()
       # And an execution engine with an empty backing module
       backing_mod = llvm.parse_assembly ("")
       engine = llvm.create_mcjit_compiler (backing_mod, target_machine)

       # Create a LLVM module object from the IR
       mod = llvm.parse_assembly (llvm_ir)
       mod.verify ()
       # Now add the module and make sure it is ready for execution
       engine.add_module (mod)
       engine.finalize_object ()
       engine.run_static_constructors ()

       # Look up the function pointer (a Python int)
       func_ptr = engine.get_function_address ("fpadd")

       # Run the function via ctypes
       cfunc = ctypes.CFUNCTYPE (ctypes.c_double, ctypes.c_double, ctypes.c_double) (func_ptr)
       res = cfunc (1.0, 3.5)
       print ("RESULT fpadd(...) =", res)

   # -----------------------------------------------------------------------

   def example2 (self) :
       # llvmlite/examples/llvmir.py

       module = ir.Module()
       fntype = ir.FunctionType (ir.IntType (32), [ ir.IntType (32), ir.IntType (32) ])
       func = ir.Function (module, fntype, name="fce")

       bb_entry = func.append_basic_block ()

       builder = ir. IRBuilder()
       builder.position_at_end (bb_entry)

       stackint = builder.alloca (ir.IntType (32))
       builder.store (ir.Constant (stackint.type.pointee, 123), stackint)
       myint = builder.load (stackint)

       addinstr = builder.add (func.args[0], func.args[1])
       mulinstr = builder.mul (addinstr, ir.Constant (ir.IntType(32), 123))
       pred = builder.icmp_signed ('<', addinstr, mulinstr)
       builder.ret (mulinstr)

       bb_block = func.append_basic_block ()
       builder.position_at_end (bb_block)

       bb_exit = func.append_basic_block ()

       pred = builder.trunc (addinstr, ir.IntType(1))
       builder.cbranch (pred, bb_block, bb_exit)

       builder.position_at_end (bb_exit)
       builder.ret (myint)

       print (module)

   # -----------------------------------------------------------------------

   def example3 (self) :
       # llvmlite/examples/sum.py

       llvm.initialize()
       llvm.initialize_native_target()
       llvm.initialize_native_asmprinter()

       t1 = time()

       module = ir.Module ()
       fnty = ir.FunctionType (ir.IntType(32), [ ir.IntType(32).as_pointer(), ir.IntType(32) ])
       func = ir.Function (module, fnty, name="sum")

       bb_entry = func.append_basic_block ()
       bb_loop = func.append_basic_block ()
       bb_exit = func.append_basic_block ()

       builder = ir.IRBuilder ()
       builder.position_at_end (bb_entry)

       builder.branch (bb_loop)
       builder.position_at_end (bb_loop)

       index = builder.phi (ir.IntType(32))
       index.add_incoming (ir.Constant(index.type, 0), bb_entry)
       accum = builder.phi (ir.IntType(32))
       accum.add_incoming (ir.Constant(accum.type, 0), bb_entry)

       ptr = builder.gep (func.args[0], [index])
       value = builder.load (ptr)

       added = builder.add (accum, value)
       accum.add_incoming (added, bb_loop)

       indexp1 = builder.add (index, ir.Constant (index.type, 1))
       index.add_incoming (indexp1, bb_loop)

       cond = builder.icmp_unsigned ('<', indexp1, func.args[1])
       builder.cbranch(cond, bb_loop, bb_exit)

       builder.position_at_end (bb_exit)
       builder.ret(added)

       strmod = str (module)

       t2 = time()

       print("-- generate IR:", t2-t1)

       t3 = time()

       llmod = llvm.parse_assembly (strmod)

       t4 = time()

       print("-- parse assembly:", t4-t3)

       print (llmod)

       pmb = llvm.create_pass_manager_builder ()
       pmb.opt_level = 2
       pm = llvm.create_module_pass_manager ()
       pmb.populate (pm)

       t5 = time ()

       pm.run (llmod)

       t6 = time ()

       print ("-- optimize:", t6-t5)

       t7 = time ()

       target_machine = llvm.Target.from_default_triple().create_target_machine()

       with llvm.create_mcjit_compiler(llmod, target_machine) as ee:
           ee.finalize_object ()
           cfptr = ee.get_function_address ("sum")

           t8 = time ()
           print ("-- JIT compile:", t8 - t7)

           print (target_machine.emit_assembly (llmod))

           cfunc = ctypes.CFUNCTYPE (ctypes.c_int, ctypes.POINTER (ctypes.c_int), ctypes.c_int) (cfptr)
           A = np.arange (10, dtype=np.int32)
           res = cfunc (A.ctypes.data_as (ctypes.POINTER (ctypes.c_int)), A.size)

           print (res, A.sum ())

   # -----------------------------------------------------------------------

   def _eval_const_int (self, expr) :
       """Compile-time vyhodnocení celočíselného výrazu — pro velikosti
       polí 'int p[Max+1]' apod. Stejná logika jako v cmm_generate.py."""
       if expr is None :
          return None
       kind = getattr (expr, 'kind', None)
       if kind == intValue :
          try : return int (expr.value)
          except (ValueError, TypeError) : return None
       if kind == simpleName :
          decl = getattr (expr, 'item_decl', None)
          if decl is None : return None
          init = getattr (decl, 'init', None)
          if init is None : return None
          inner = getattr (getattr (init, 'value', None), 'inner_expr', None)
          return self._eval_const_int (inner)
       if kind == subexprExpr :
          return self._eval_const_int (expr.param)
       if kind == minusExpr :
          v = self._eval_const_int (expr.param)
          return -v if v is not None else None
       if kind == plusExpr :
          return self._eval_const_int (expr.param)
       if kind in [ addExpr, subExpr, mulExpr, divExpr, modExpr,
                    bitAndExpr, bitOrExpr, bitXorExpr, shlExpr, shrExpr ] :
          l = self._eval_const_int (expr.left)
          r = self._eval_const_int (expr.right)
          if l is None or r is None : return None
          if kind == addExpr : return l + r
          if kind == subExpr : return l - r
          if kind == mulExpr : return l * r
          if kind == divExpr : return l // r if r != 0 else None
          if kind == modExpr : return l %  r if r != 0 else None
          if kind == bitAndExpr : return l & r
          if kind == bitOrExpr  : return l | r
          if kind == bitXorExpr : return l ^ r
          if kind == shlExpr : return l << r
          if kind == shrExpr : return l >> r
       return None

   def _llvm_struct_type (self, class_decl) :
       """Lazily vyrobí ir.IdentifiedStructType pro CmmClassDecl. Členy
       dostanou gen_field_llvm_idx (pozice v LLVM struct, počítáno od 0).
       Identifikovaný typ se ukládá DŘÍV než se zaplňují členové, aby
       self-referenční struktury (Item s Item * ref) měly opaque typ
       k dispozici během rekurze."""
       cached = getattr (class_decl, 'gen_llvm_type', None)
       if cached is not None :
          return cached
       struct_t = self.module.context.get_identified_type (class_decl.item_name)
       class_decl.gen_llvm_type = struct_t

       member_types = [ ]
       for member in class_decl.item_list :
           if not isinstance (member, CmmSimpleItem) : continue
           if getattr (member, 'is_function', False) : continue
           member.gen_field_llvm_idx = len (member_types)
           mt = self.code_type (member.item_type)
           if mt is None : mt = ir.IntType (32)
           member_types.append (mt)
       struct_t.set_body (* member_types)
       return struct_t

   def code_type (self, t) :
       """cmm Type → LLVM IR typ. int=i32, void=void, char=i8, bool=i32
       (zjednodušení, abychom nemuseli truncovat při logických
       operacích). Pole = ir.ArrayType (NE VectorType — to je SIMD).
       Pointer/Reference = elementový typ + as_pointer (). NamedType
       odkazující na strukturu jde přes _llvm_struct_type."""
       if isinstance (t, SimpleType) :
          if t.type_void : return ir.VoidType ()
          if t.type_char : return ir.IntType (8)
          # int / bool / unspecified → i32
          return ir.IntType (32)
       if isinstance (t, ArrayType) :
          cnt = self._eval_const_int (t.lim) or 0
          elem = self.code_type (t.type_from)
          if elem is None : elem = ir.IntType (32)
          return ir.ArrayType (elem, cnt)
       if isinstance (t, (PointerType, ReferenceType)) :
          inner = self.code_type (t.type_from)
          # LLVM nemá ukazatel-na-void; void* lowerujeme na i8* (standardní
          # konvence — LLVM dříve než opaque pointers takhle modeloval
          # void*). Stejně tak pro neznámé typy.
          if inner is None or isinstance (inner, ir.VoidType) :
             inner = ir.IntType (8)
          return inner.as_pointer ()
       if isinstance (t, NamedType) :
          type_decl = getattr (t, 'type_decl', None)
          if type_decl is not None :
             kind = getattr (type_decl, 'kind', None)
             if kind == classDecl :
                return self._llvm_struct_type (type_decl)
             if kind == typedefDecl :
                # Stencil placeholder T (registrovaný v on_stencil_params
                # jako typedef-marker, aby parser zvládl 'T a' v parametru).
                # Po substituci scan_template má basic_name.id = "int" v
                # CmmTypeSpec, ale item_type pořád ukazuje na typedef
                # placeholder. Pro účely demonstrace bereme typedef jako
                # i32 — to je výchozí typ celého naivního compileru.
                return ir.IntType (32)
       return None

   def code_global_variable (self, decl) :
       t = self.code_type (decl.item_type)
       if t is None : t = ir.IntType (32)
       gv = ir.GlobalVariable (self.module, t, decl.item_name)
       # Zkusíme literální init na compile-time (typicky const int N = 20).
       init = getattr (decl, 'init', None)
       init_val = None
       if init is not None and isinstance (t, ir.IntType) :
          inner = getattr (getattr (init, 'value', None), 'inner_expr', None)
          v = self._eval_const_int (inner)
          if v is not None :
             init_val = ir.Constant (t, v)
       if init_val is None :
          init_val = ir.Constant (t, None) # zero-init
       gv.initializer = init_val
       decl.code = gv

   def _coerce (self, val, target_type) :
       """Pokud val.type != target_type, zkus jednoduchou koerci.
       Stačí pro 'int * p = nullptr' (i32 0 -> ptr null) a pár podobných."""
       if val.type == target_type :
          return val
       if isinstance (target_type, ir.PointerType) and isinstance (val.type, ir.IntType) :
          return self.builder.inttoptr (val, target_type)
       if isinstance (target_type, ir.IntType) and isinstance (val.type, ir.PointerType) :
          return self.builder.ptrtoint (val, target_type)
       if isinstance (val.type, ir.IntType) and isinstance (target_type, ir.IntType) :
          if val.type.width < target_type.width :
             # i1 (boolean) zext, ostatní širší sext (jako C signed int)
             if val.type.width == 1 :
                return self.builder.zext (val, target_type)
             return self.builder.sext (val, target_type)
          if val.type.width > target_type.width :
             return self.builder.trunc (val, target_type)
       return val # vzdáme to a necháme LLVM si stěžovat

   def code_local_variable (self, decl) :
       t = self.code_type (decl.item_type)
       if t == None :
          t = ir.IntType (32)
       decl.code = self.builder.alloca (t, name = decl.item_name)
       # Initializátor: int x = expr; — vyhodnoť a ulož do alloca slotu.
       init = getattr (decl, 'init', None)
       if init is not None :
          inner = getattr (getattr (init, 'value', None), 'inner_expr', None)
          if inner is not None :
             self.code_expr (inner)
             if inner.code is not None :
                self.builder.store (self._coerce (inner.code, t), decl.code)

   def _declare_function (self, decl) :
       """Vytvoří ir.Function (signaturu) pro decl a uloží do decl.code.
       Body se přidá později v code_function. Oddělené, aby šly všechny
       funkce nejdřív deklarovat (pro forward references)."""
       ret_t = decl.item_type
       if isinstance (ret_t, FunctionType) :
          ret_t = ret_t.type_from
       result_type = self.code_type (ret_t)
       if result_type is None :
          result_type = ir.VoidType ()

       param_types = [ ]
       for param in decl.item_list :
           pt = self.code_type (param.item_type)
           if pt is None :
              pt = ir.IntType (32)
           param_types.append (pt)

       is_extern = getattr (decl, 'item_body', None) is None
       func_type = ir.FunctionType (result_type, param_types,
                                    var_arg = is_extern)
       fn = ir.Function (self.module, func_type, name = decl.item_name)
       decl.code = fn
       return fn

   def code_function (self, decl) :
       # Signatura už existuje (z pre-passu v code_program); jen ji
       # vytáhneme a vyemitujeme tělo.
       if getattr (decl, 'code', None) is None :
          self._declare_function (decl)
       self.func = decl.code
       result_type = decl.code.function_type.return_type
       self._return_type = result_type # pro returnStat

       is_extern = getattr (decl, 'item_body', None) is None
       if is_extern :
          # Žádné basic bloky → declare-only.
          return

       entry_block = self.func.append_basic_block ()
       self.builder = ir.IRBuilder ()
       self.builder.position_at_end (entry_block)

       # Parametry: hodnotové přesypeme do alloca slotu (aby se na ně dalo
       # přiřazovat skrz code_ref/store stejně jako na lokály). Reference
       # nechají Argument jako rovnou ten ukazatel — caller předal adresu
       # původní proměnné a my k ní budeme rovnou loadovat/storovat.
       inx = 0
       for param in decl.item_list :
           arg = self.func.args [inx]
           arg.name = param.item_name
           if isinstance (param.item_type, ReferenceType) :
              param.code = arg
           else :
              slot = self.builder.alloca (arg.type, name = param.item_name)
              self.builder.store (arg, slot)
              param.code = slot
           inx = inx + 1

       self.code_stat (decl.item_body)
       # Implicit terminátor: pokud uživatelská funkce 'spadla' bez
       # explicitního return (typicky void), doplníme ret. Pokud blok
       # už terminován (return uvnitř), neemitujeme nic — LLVM by si
       # stěžovalo na druhý terminátor.
       if not self.builder.block.is_terminated :
          if isinstance (result_type, ir.VoidType) :
             self.builder.ret_void ()
          else :
             self.builder.ret (ir.Constant (result_type, 0))

   # -----------------------------------------------------------------------

   def _to_i1 (self, val) :
       """LLVM cbranch chce i1 (bool). Naše porovnání už i1 vrací,
       ale 'if (x)' kde x je i32 potřebuje icmp != 0."""
       if val.type == ir.IntType (1) :
          return val
       return self.builder.icmp_signed ('!=', val, ir.Constant (val.type, 0))

   def code_if_stat (self, stat) :
       self.code_expr (stat.cond)
       cond_i1 = self._to_i1 (stat.cond.code)
       then_block = self.func.append_basic_block ()
       stop_block = self.func.append_basic_block ()
       if stat.else_stat == None :
          self.builder.cbranch (cond_i1, then_block, stop_block)
          self.builder.position_at_end (then_block)
          self.code_stat (stat.then_stat)
          if not self.builder.block.is_terminated :
             self.builder.branch (stop_block)
       else :
          else_block = self.func.append_basic_block ()
          self.builder.cbranch (cond_i1, then_block, else_block)

          self.builder.position_at_end (then_block)
          self.code_stat (stat.then_stat)
          if not self.builder.block.is_terminated :
             self.builder.branch (stop_block)

          self.builder.position_at_end (else_block)
          self.code_stat (stat.else_stat)
          if not self.builder.block.is_terminated :
             self.builder.branch (stop_block)

       self.builder.position_at_end (stop_block)

   def code_while_stat (self, stat) :
       start_block = self.func.append_basic_block ()
       cont_block = self.func.append_basic_block ()
       stop_block = self.func.append_basic_block ()

       # Předchozí blok skočí do start_blocku (jinak by byl bez
       # terminátoru — LLVM by si stěžovalo).
       self.builder.branch (start_block)

       self.builder.position_at_end (start_block)
       self.code_expr (stat.cond)
       self.builder.cbranch (self._to_i1 (stat.cond.code),
                             cont_block, stop_block)

       self.builder.position_at_end (cont_block)
       self.code_stat (stat.body)
       if not self.builder.block.is_terminated :
          self.builder.branch (start_block)

       self.builder.position_at_end (stop_block)

   def code_for_stat (self, stat) :
       self.code_stat (stat.from_expr)
       if stat.iter_expr != None :
          self.code_expr (stat.iter_expr)
          self.code_stat (stat.body)
          return
       start_block = self.func.append_basic_block ()
       cont_block = self.func.append_basic_block ()
       stop_block = self.func.append_basic_block ()

       self.builder.branch (start_block)
       self.builder.position_at_end (start_block)
       if getattr (stat, 'cond_expr', None) is not None :
          self.code_expr (stat.cond_expr)
          self.builder.cbranch (self._to_i1 (stat.cond_expr.code),
                                cont_block, stop_block)
       else :
          self.builder.branch (cont_block)

       self.builder.position_at_end (cont_block)
       self.code_stat (stat.body)
       if getattr (stat, 'step_expr', None) is not None :
          self.code_expr (stat.step_expr)
       if not self.builder.block.is_terminated :
          self.builder.branch (start_block)

       self.builder.position_at_end (stop_block)

   def code_and_or (self, expr) :
       """x && y / x || y. Bez short-circuitu pro jednoduchost — oba
       operandy se vyhodnotí vždy, výsledek je AND/OR z i1 hodnot.
       To je didakticky čistší a pro většinu studentských programů
       (kde y nemá vedlejší účinky a indexy nejdou mimo) funkčně
       ekvivalentní. Plnohodnotný short-circuit by potřeboval bloky
       a phi node, viz cmm_generate.py."""
       self.code_expr (expr.left)
       self.code_expr (expr.right)
       l = self._to_i1 (expr.left.code)
       r = self._to_i1 (expr.right.code)
       if expr.kind == logAndExpr :
          result = self.builder.and_ (l, r)
       else :
          result = self.builder.or_ (l, r)
       # Vraťme hodnotu jako i32, aby se chovala jako 1/0 v
       # aritmetice (matchuje zbytek našeho kódu).
       expr.code = self.builder.zext (result, ir.IntType (32))

   def code_stat (self, stat) :
       if stat is None :
          return
       if stat.kind == ifStat :
          self.code_if_stat (stat)
       elif stat.kind == whileStat :
          self.code_while_stat (stat)
       elif stat.kind == forStat :
          self.code_for_stat (stat)
       elif stat.kind == compoundStat :
          for item in stat.items :
             self.code_stat (item)
       elif stat.kind == simpleStat :
          self.code_expr (stat.inner_expr)
       elif stat.kind == simpleDecl :
          for item in stat.items :
              self.code_local_variable (item)
       elif stat.kind == returnStat :
          if getattr (stat, 'return_expr', None) is not None :
             self.code_expr (stat.return_expr)
             self.builder.ret (stat.return_expr.code)
          else :
             self.builder.ret_void ()
       elif stat.kind == emptyStat :
          pass

   # -----------------------------------------------------------------------

   def code_assign (self, expr) :
       """Plain '=' nebo compound '+=' '-=' atd. Pro plain stačí
       store; pro compound: load staré hodnoty, op s rhs, store
       zpátky. Výsledek expression-context je nová hodnota (RAX-like
       — vrací se v expr.code)."""
       kind = expr.kind
       left = expr.left
       right = expr.right
       self.code_expr (right)
       self.code_ref (left)
       if left.code is None :
          expr.code = right.code
          return

       rhs = self._coerce (right.code, left.code.type.pointee)

       if kind == assignExpr :
          self.builder.store (rhs, left.code)
          expr.code = rhs
          return

       # Compound: nahraj starou hodnotu, kombinuj, ulož
       old = self.builder.load (left.code)
       if   kind == addAssignExpr : new_val = self.builder.add  (old, rhs)
       elif kind == subAssignExpr : new_val = self.builder.sub  (old, rhs)
       elif kind == mulAssignExpr : new_val = self.builder.mul  (old, rhs)
       elif kind == divAssignExpr : new_val = self.builder.sdiv (old, rhs)
       elif kind == modAssignExpr : new_val = self.builder.srem (old, rhs)
       elif kind == andAssignExpr : new_val = self.builder.and_ (old, rhs)
       elif kind == orAssignExpr  : new_val = self.builder.or_  (old, rhs)
       elif kind == xorAssignExpr : new_val = self.builder.xor  (old, rhs)
       elif kind == shlAssignExpr : new_val = self.builder.shl  (old, rhs)
       elif kind == shrAssignExpr : new_val = self.builder.ashr (old, rhs)
       else :
          print ("unsupported compound assign:", kind)
          expr.code = old
          return
       self.builder.store (new_val, left.code)
       expr.code = new_val

   def _llvm_sizeof (self, t) :
       """sizeof(t) jako i32 konstanta. LLVM standardní trik:
           ptrtoint (getelementptr (T*, null, 1) to i32)
       LLVM si to umí složit na konstantu při optimalizaci."""
       if t is None or isinstance (t, ir.VoidType) :
          return ir.Constant (ir.IntType (32), 0)
       null_ptr = ir.Constant (t.as_pointer (), None)
       one = ir.Constant (ir.IntType (32), 1)
       return null_ptr.gep ([ one ]).ptrtoint (ir.IntType (32))

   def _ensure_calloc (self) :
       """Líně deklaruj 'i8 * calloc (i32, i32)' na úrovni modulu — pro
       'new T'. JIT si malloc/calloc z procesu už dohledá sám."""
       if hasattr (self, '_calloc_func') :
          return self._calloc_func
       fty = ir.FunctionType (ir.IntType (8).as_pointer (),
                              [ ir.IntType (32), ir.IntType (32) ])
       self._calloc_func = ir.Function (self.module, fty, name = 'calloc')
       return self._calloc_func

   def code_sizeof (self, expr) :
       """sizeof (T) nebo sizeof (var) -> compile-time int."""
       val = expr.value
       while val is not None and getattr (val, 'kind', None) == subexprExpr :
          val = val.param
       item_type = getattr (val, 'item_type', None) if val is not None else None
       t = self.code_type (item_type) if item_type is not None else None
       if t is None :
          t = ir.IntType (32)
       expr.code = self._llvm_sizeof (t)

   def code_new (self, expr) :
       """new T -> calloc (1, sizeof (T)) + bitcast i8* na T*."""
       type1 = getattr (expr, 'type1', None)
       type2 = getattr (expr, 'type2', None)
       ts = None
       if type1 is not None : ts = getattr (type1, 'type_spec', None)
       elif type2 is not None : ts = getattr (type2, 'type_spec', None)
       inner_type = getattr (ts, 'item_type', None) if ts is not None else None
       result_type = self.code_type (inner_type) if inner_type is not None else None
       if result_type is None :
          result_type = ir.IntType (32)
       size = self._llvm_sizeof (result_type)
       calloc = self._ensure_calloc ()
       one = ir.Constant (ir.IntType (32), 1)
       raw = self.builder.call (calloc, [ one, size ])
       expr.code = self.builder.bitcast (raw, result_type.as_pointer ())

   def code_inc_dec (self, expr) :
       """++x / x++ / --x / x--. prefix vrací novou hodnotu, postfix
       starou. Vše přes code_ref + load + add/sub + store."""
       kind = expr.kind
       prefix = (kind in [ incExpr, decExpr ])
       target = expr.param if prefix else expr.left
       self.code_ref (target)
       if target.code is None :
          expr.code = ir.Constant (ir.IntType (32), 0)
          return
       old = self.builder.load (target.code)
       one = ir.Constant (old.type, 1)
       if kind in [ incExpr, postIncExpr ] :
          new_val = self.builder.add (old, one)
       else :
          new_val = self.builder.sub (old, one)
       self.builder.store (new_val, target.code)
       expr.code = new_val if prefix else old

   def _lookup_field_idx (self, left, field_name, deref_pointer) :
       """Najdi gen_field_llvm_idx pro field. Cmm_comp obvykle nastaví
       field_name.item_decl rovnou; když ne (typicky když left jde přes
       ReferenceType nebo unresolved typedef), spadneme zpět na lookup
       skrz left.item_type."""
       fdecl = getattr (field_name, 'item_decl', None)
       if fdecl is not None and hasattr (fdecl, 'gen_field_llvm_idx') :
          return fdecl.gen_field_llvm_idx
       fname = getattr (field_name, 'id', None)
       if fname is None : return None
       t = getattr (left, 'item_type', None)
       while isinstance (t, ReferenceType) :
          t = t.type_from
       if deref_pointer :
          if not isinstance (t, PointerType) : return None
          t = t.type_from
          while isinstance (t, ReferenceType) :
             t = t.type_from
       if not isinstance (t, NamedType) : return None
       type_decl = getattr (t, 'type_decl', None)
       if type_decl is None or getattr (type_decl, 'kind', None) != classDecl :
          return None
       self._llvm_struct_type (type_decl) # ensure laid out
       for member in type_decl.item_list :
           if not isinstance (member, CmmSimpleItem) : continue
           if getattr (member, 'is_function', False) : continue
           if getattr (member, 'item_name', '') == fname :
              return getattr (member, 'gen_field_llvm_idx', None)
       return None

   def code_ref (self, expr) :
       """Spočítá pointer (LLVM hodnota typu T*) na lvalue 'expr'.
       Ulož do expr.code. Pokrývá:
         - simpleName: alloca/global pointer
         - subexprExpr: rekurze
         - derefExpr (*p): hodnota p (ta je sama pointer)
         - indexExpr (arr[i]): GEP do pole [0, index]
         - fieldExpr (obj.f): GEP do struktury [0, field_idx]
         - ptrFieldExpr (p->f): GEP s p jako bází [0, field_idx]
       Při neúspěchu nastaví expr.code = None (caller musí ošetřit)."""
       expr.code = None
       i32 = ir.IntType (32)
       zero = ir.Constant (i32, 0)

       if expr.kind == simpleName :
          decl = getattr (expr, 'item_decl', None)
          if decl is None or getattr (decl, 'code', None) is None :
             nm = getattr (expr, 'id', '?')
             # Speciální jména (true/false/nullptr) nejsou lvalue,
             # nemůžeme je adresovat — fallback na alokovanou
             # 'unknown' proměnnou, ať to alespoň neshodí builder.
             expr.code = self.builder.alloca (i32, name = "unknown_" + nm)
          else :
             expr.code = decl.code
          return

       if expr.kind == subexprExpr :
          self.code_ref (expr.param)
          expr.code = expr.param.code
          return

       if expr.kind == derefExpr :
          # *p — hodnota p je sama lvalue address
          self.code_expr (expr.param)
          expr.code = expr.param.code
          return

       if expr.kind == indexExpr :
          # arr[i] — chceme GEP do pole. Pro lokální/globální pole
          # alloca/global vrací 'pointer to [N x T]' a chceme ukazatel
          # na element, takže použijeme GEP s [0, i].
          self.code_ref (expr.left)
          self.code_expr (expr.param)
          if expr.left.code is None or expr.param.code is None :
             return
          expr.code = self.builder.gep (expr.left.code,
             [ zero, expr.param.code ])
          return

       if expr.kind == fieldExpr :
          self.code_ref (expr.left)
          if expr.left.code is None : return
          idx = self._lookup_field_idx (expr.left, expr.field_name,
                                        deref_pointer = False)
          if idx is None :
             print ("unknown field:", getattr (expr.field_name, 'id', '?'))
             return
          expr.code = self.builder.gep (expr.left.code,
             [ zero, ir.Constant (i32, idx) ])
          return

       if expr.kind == ptrFieldExpr :
          # p->f — vyhodnoť pointer p na hodnotu, ten už je báze
          self.code_expr (expr.left)
          if expr.left.code is None : return
          idx = self._lookup_field_idx (expr.left, expr.field_name,
                                        deref_pointer = True)
          if idx is None :
             print ("unknown field:", getattr (expr.field_name, 'id', '?'))
             return
          expr.code = self.builder.gep (expr.left.code,
             [ zero, ir.Constant (i32, idx) ])
          return

       print ("unsupported lvalue kind", expr.kind)

   def code_expr (self, expr) :
       expr.code = None

       # if expr.kind == simpleDecl :
       #    expr.code = self.builder.load (expr.item_decl.code)

       if expr.kind == simpleStat :
          self.code_stat (expr)
          expr.code = expr.inner_expr.code

       elif expr.kind == simpleName :
          ident = getattr (expr, 'id', '')
          if ident == 'true' :
             expr.code = ir.Constant (ir.IntType (32), 1)
          elif ident in ('false', 'nullptr', 'NULL', 'null') :
             # Pro null pointery potřebujeme správný typ ukazatele —
             # tady ale nevíme, na co ukazujeme. Použijeme i32 nulu;
             # caller (typicky srovnání nebo init) si ji případně přetypuje.
             expr.code = ir.Constant (ir.IntType (32), 0)
          else :
             # Lvalue → load přes code_ref
             self.code_ref (expr)
             # code_ref dosadil expr.code = pointer; LOAD z něj.
             # Ale pozor: pro decl jehož code je sama hodnota (např.
             # parametr funkce — ir.Argument není pointer), neexistuje
             # alloca a code_ref vrací rovnou expr.code = decl.code.
             # Detekce přes kind type:
             if expr.code is not None and isinstance (expr.code.type,
                                                     ir.PointerType) :
                expr.code = self.builder.load (expr.code)

       elif expr.kind == intValue :
          expr.code = ir.Constant (ir.IntType (32), str (expr.value))

       elif expr.kind == stringValue :
          # Private global s array of i8, GEP na první znak → i8*.
          if not hasattr (self, '_string_count') :
             self._string_count = 0
          text = getattr (expr, 'value', '')
          data = bytearray (text.encode ('utf-8') + b'\x00')
          arr_t = ir.ArrayType (ir.IntType (8), len (data))
          gv_name = ".str." + str (self._string_count)
          self._string_count += 1
          gv = ir.GlobalVariable (self.module, arr_t, gv_name)
          gv.linkage = 'private'
          gv.global_constant = True
          gv.initializer = ir.Constant (arr_t, data)
          zero = ir.Constant (ir.IntType (32), 0)
          expr.code = self.builder.gep (gv, [ zero, zero ])

       elif expr.kind == subexprExpr :
          self.code_expr (expr.param)
          expr.code = expr.param.code

       elif expr.kind in [ assignExpr,
                           addAssignExpr, subAssignExpr, mulAssignExpr,
                           divAssignExpr, modAssignExpr,
                           andAssignExpr, orAssignExpr, xorAssignExpr,
                           shlAssignExpr, shrAssignExpr ] :
          self.code_assign (expr)

       elif expr.kind in [ incExpr, decExpr, postIncExpr, postDecExpr ] :
          self.code_inc_dec (expr)

       elif expr.kind in [ indexExpr, derefExpr, fieldExpr, ptrFieldExpr ] :
          # Univerzální lvalue read: pointer přes code_ref, pak load
          self.code_ref (expr)
          if expr.code is not None :
             expr.code = self.builder.load (expr.code)

       elif expr.kind == addrExpr :
          # &x — adresa lvalue je rovnou výsledek code_ref
          self.code_ref (expr.param)
          expr.code = expr.param.code

       elif expr.kind == sizeofExpr :
          self.code_sizeof (expr)

       elif expr.kind == newExpr :
          self.code_new (expr)

       elif expr.kind == callExpr :
          left = expr.left

          # Najdeme deklarovanou funkci (pro typy parametrů, defaulty, refs)
          callee = None
          callee_params = [ ]
          if left.kind in (simpleName, templateName) :
             d = getattr (left, 'item_decl', None)
             if d is not None :
                callee = getattr (d, 'code', None)
                callee_params = list (getattr (d, 'item_list', [ ]))
          if callee is None :
             self.code_ref (left)
             callee = left.code

          # Posbírej argumenty + doplň defaulty z param.init (Phase F4).
          src_args = list (expr.param_list.items) if expr.param_list else [ ]
          while len (src_args) < len (callee_params) :
              p = callee_params [len (src_args)]
              init = getattr (p, 'init', None)
              if init is None : break
              inner = getattr (getattr (init, 'value', None), 'inner_expr', None)
              if inner is None : break
              src_args.append (inner)

          # Vyhodnoť každý argument — pro reference param přes code_ref
          # (předáváme adresu), jinak code_expr (hodnotu). Provede se
          # také type-coercion, ať volání printf("text", 5) nepadne na
          # i32 vs i32 mismatch.
          args = [ ]
          for inx, item in enumerate (src_args) :
              is_ref = (inx < len (callee_params)
                 and isinstance (getattr (callee_params [inx], 'item_type', None),
                                 ReferenceType))
              if is_ref :
                 self.code_ref (item)
              else :
                 self.code_expr (item)
              v = item.code
              # Zajisti správný typ pro deklarované parametry funkce
              # (var-arg externí jdou tak jak jsou).
              fn_type = callee.function_type if hasattr (callee, 'function_type') else None
              if fn_type is not None and inx < len (fn_type.args) :
                 v = self._coerce (v, fn_type.args [inx])
              args.append (v)

          expr.code = self.builder.call (callee, args)

       elif expr.kind == logAndExpr or expr.kind == logOrExpr :
          self.code_and_or (expr)

       elif expr.kind in [ addExpr, subExpr, mulExpr, divExpr, modExpr,
                           shlExpr, shrExpr,
                           bitAndExpr, bitOrExpr, bitXorExpr ] :
          left = expr.left
          right = expr.right
          self.code_expr (left)
          self.code_expr (right)
          if expr.kind == addExpr :
             expr.code = self.builder.add (left.code, right.code)
          elif expr.kind == subExpr :
             expr.code = self.builder.sub (left.code, right.code)
          elif expr.kind == mulExpr :
             expr.code = self.builder.mul (left.code, right.code, name = "multiply")
          elif expr.kind == divExpr :
             expr.code = self.builder.sdiv (left.code, right.code)
          elif expr.kind == modExpr :
             expr.code = self.builder.srem (left.code, right.code)
          elif expr.kind == shlExpr :
             expr.code = self.builder.shl (left.code, right.code)
          elif expr.kind == shrExpr :
             expr.code = self.builder.ashr (left.code, right.code)
          elif expr.kind == bitAndExpr :
             expr.code = self.builder.and_ (left.code, right.code)
          elif expr.kind == bitOrExpr :
             expr.code = self.builder.or_ (left.code, right.code)
          elif expr.kind == bitXorExpr :
             expr.code = self.builder.xor (left.code, right.code)

       elif expr.kind in [ ltExpr, leExpr, gtExpr, geExpr, eqExpr, neExpr ] :
          left = expr.left
          right = expr.right
          self.code_expr (left)
          self.code_expr (right)
          # Type matching: 't == nullptr' nebo 'p < arr' atd. — pokud
          # jeden je pointer a druhý int, převedeme int na pointer
          # (typicky 'i32 0' -> 'null'). Stejně tak při různých šířkách
          # int sjednotíme.
          lt = left.code.type
          rt = right.code.type
          if isinstance (lt, ir.PointerType) and isinstance (rt, ir.IntType) :
             right.code = self._coerce (right.code, lt)
          elif isinstance (rt, ir.PointerType) and isinstance (lt, ir.IntType) :
             left.code = self._coerce (left.code, rt)
          elif isinstance (lt, ir.IntType) and isinstance (rt, ir.IntType) :
             if lt.width < rt.width : left.code = self.builder.sext (left.code, rt)
             elif lt.width > rt.width : right.code = self.builder.sext (right.code, lt)

          cmp_map = { ltExpr: "<", leExpr: "<=", gtExpr: ">",
                      geExpr: ">=", eqExpr: "==", neExpr: "!=" }
          cmp = cmp_map [expr.kind]
          if isinstance (left.code.type, ir.PointerType) :
             # icmp pro pointery: pro == / != stejná instrukce, pro
             # ordering použij unsigned (LLVM nemá signed pointer order).
             expr.code = self.builder.icmp_unsigned (cmp, left.code, right.code)
          else :
             expr.code = self.builder.icmp_signed (cmp, left.code, right.code)

       elif expr.kind == minusExpr :
          param = expr.param
          self.code_expr (param)
          expr.code = self.builder.neg (param.code)

       elif expr.kind == bitNotExpr :
          param = expr.param
          self.code_expr (param)
          expr.code = self.builder.not_ (param.code)

       elif expr.kind == logNotExpr :
          # !x → (x == 0). Konvertujeme na i1 a XORujeme s true.
          self.code_expr (expr.param)
          cond_i1 = self._to_i1 (expr.param.code)
          flipped = self.builder.xor (cond_i1, ir.Constant (ir.IntType (1), 1))
          expr.code = self.builder.zext (flipped, ir.IntType (32))

       if expr.code == None :
          expr.code = ir.Constant (ir.IntType (32), 42) # !?

   # -----------------------------------------------------------------------

   def code_program (self) :
       # llvmlite < 0.45: explicit initialization of all targets.
       # llvmlite >= 0.48: llvm.initialize () raises RuntimeError (init is
       # automatic), the old pass manager API is gone as well.
       try :
          llvm.initialize ()
          llvm.initialize_native_target ()
          llvm.initialize_native_asmprinter ()
          llvm.initialize_all_targets ()
          llvm.initialize_all_asmprinters ()
       except RuntimeError :
          try :
             llvm.initialize_native_target ()
             llvm.initialize_native_asmprinter ()
          except RuntimeError :
             pass

       self.module = ir.Module ()

       # Pre-pass: jen DEKLARACE všech funkcí (ir.Function bez basic
       # bloků, decl.code bude pointovat na ni). Tím dovolíme funkcím
       # navzájem se volat bez ohledu na pořadí v item_list — to je
       # důležité pro stencil instance, které se přidávají do scope
       # uprostřed parseru main, takže by jinak byly za main.
       for decl in self.compiler.global_scope.item_list :
           if isinstance (decl, CmmSimpleItem) and decl.is_function :
              if getattr (decl, 'template_decl', None) is not None :
                 continue
              if getattr (decl, 'skip_code', False) :
                 continue
              if getattr (decl, 'code', None) is None :
                 self._declare_function (decl)

       # Main pass: emit těla funkcí + globální proměnné
       for decl in self.compiler.global_scope.item_list :
           if isinstance (decl, CmmSimpleItem) :
              if getattr (decl, 'template_decl', None) is not None :
                 continue
              if getattr (decl, 'skip_code', False) :
                 continue
              if decl.is_function :
                 print ("FUNCTION", decl.item_name)
                 self.code_function (decl)
              else :
                 print ("VARIABLE", decl.item_name)
                 self.code_global_variable (decl)

       print (self.module)

       strmod = str (self.module)
       # print ("SOURCE")
       # print (strmod)
       llmod = llvm.parse_assembly (strmod)
       # print ("ASSEMBLY")
       # print (llmod)

       target = llvm.Target.from_default_triple ()
       # target = llvm.Target.from_triple ("i386-pc-linux-gnu")
       # target = llvm.Target.from_triple ("x86_64-pc-linux-gnu")

       # target = llvm.Target.from_triple ("x86_64-w64-windows-gnu")
       # target = llvm.Target.from_triple ("i686-pc-windows-gnu")
       # target = llvm.Target.from_triple ("x86_64-pc-windows-gnu")

       # arm : initialize_all_targets, initialize_all_asmprinters
       # target = llvm.Target.from_triple ("arm-none-eabi")
       # target = llvm.Target.from_triple ("arm64-unknown-linux")

       # target = llvm.Target.from_triple ("riscv32-unknown-linux")
       # target = llvm.Target.from_triple ("riscv64-unknown-linux")

       # target = llvm.Target.from_triple ("wasm32-unknown-unknown")
       # target = llvm.Target.from_triple ("wasm64-unknown-unknown")

       machine = target.create_target_machine ()

       # Optimize. Old pass manager (llvmlite < 0.45) vs new pass manager
       # (create_pass_builder) — the old one no longer exists in 0.48.
       try :
          pmb = llvm.create_pass_manager_builder ()
          pmb.opt_level = 2
          pm = llvm.create_module_pass_manager ()
          pmb.populate (pm)
          pm.run (llmod)
       except AttributeError :
          pto = llvm.PipelineTuningOptions ()
          pto.speed_level = 2
          pass_builder = llvm.create_pass_builder (machine, pto)
          pm = pass_builder.getModulePassManager ()
          pm.run (llmod, pass_builder)
       # print ("OPTIMIZED")
       # print (llmod)

       with llvm.create_mcjit_compiler (llmod, machine) as ee:
           ee.finalize_object ()
           print (machine.emit_assembly (llmod))

           # Pokud existuje main () s 0 parametry, zavolej ji a vypiš návrat
           # — chování odpovídá cmm_generate.py, takže shodný test runner
           # může parsovat 'main returned: N' z obou backendů.
           main_decl = None
           for d in self.compiler.global_scope.item_list :
               if (isinstance (d, CmmSimpleItem) and getattr (d, 'is_function', False)
                       and d.item_name == "main"
                       and len (d.item_list) in (0, 2)
                       and getattr (d, 'item_body', None) is not None) :
                  main_decl = d
                  break
           if main_decl is not None :
              try :
                 fn_addr = ee.get_function_address ("main")
                 if fn_addr :
                    if len (main_decl.item_list) == 0 :
                       fn = ctypes.CFUNCTYPE (ctypes.c_int32) (fn_addr)
                       result = fn ()
                    else :
                       # main (int argc, char * argv []) — umělé argumenty,
                       # volání odpovídá spuštění programu bez parametrů.
                       argv0 = ctypes.create_string_buffer (b"cmm")
                       argv = (ctypes.c_void_p * 2) (
                          ctypes.cast (argv0, ctypes.c_void_p).value, None)
                       fn = ctypes.CFUNCTYPE (ctypes.c_int32,
                          ctypes.c_int32, ctypes.c_void_p) (fn_addr)
                       result = fn (1, ctypes.cast (argv, ctypes.c_void_p))
                    print ("main returned:", result)
              except Exception as e :
                 print ("main JIT call failed:", e)

           obj = machine.emit_object (llmod)
           # win.outputFileName routes the .o into the IDE's _output dir;
           # in CLI mode (cmm_run.py) win is None — fall back to cwd.
           if self.compiler.win is not None :
              fileName = self.compiler.win.outputFileName ("instr.o")
           else :
              fileName = "instr.o"
           f = open (fileName, "wb")
           f.write (obj)
           f.close()

       # see llvmlite/tests/test_binding.py

# --------------------------------------------------------------------------

# llc instr.ll -x86-asm-syntax=intel -mtriple=i386-pc-linux-gnu
# lli

# https://stackoverflow.com/questions/15036909/clang-how-to-list-supported-target-architectures
# clang -print-targets

# i386-pc-linux-gnu
# x86_64-pc-linux-gnu

# x86_64-w64-windows-gnu # same as x86_64-w64-mingw32
# i686-pc-windows-gnu # MSVC
# x86_64-pc-windows-gnu # MSVC 64-BIT

# arm-none-eabi
# arm64-unknown-linux

# riscv32-unknown-linux
# riscv64-unknown-linux

# nvptx-unknown-unknown
# nvptx64-unknown-unknown

# wasm32-unknown-unknown
# wasm64-unknown-unknown

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
