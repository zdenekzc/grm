
# cmm_generate.py
#
# Generuje x86_64 strojový kód z cmm AST přes iced-x86, výsledek
# umístí do RWX paměti přes mmap a zavolá ji přes ctypes (path α).
#
# Záměrně psané jako didaktický příklad: "naivní" code generator
# založený na akumulátoru v RAX. Každý výraz se vyhodnotí do RAX,
# u binárních operací se levá strana mezi-uloží na zásobník přes
# PUSH/POP. Žádný register allocator, žádné peephole optimalizace
# — důraz je na čitelnost vygenerovaného kódu pro studenty.
#
# Volací konvence: System V x86_64 (RDI, RSI, RDX, RCX, R8, R9 pro
# prvních 6 argumentů, vše int64).

from __future__ import print_function

import os, sys, ctypes, mmap

use_iced = True
try :
   import iced_x86 as ix
except ImportError :
   print ("missing iced-x86 (try: pip install --user iced-x86)")
   use_iced = False

from code import *
from cmm_parser import *

# ---------------------------------------------------------------------------

if use_iced :
   ARG_REGS = [ ix.Register.RDI, ix.Register.RSI, ix.Register.RDX,
                ix.Register.RCX, ix.Register.R8,  ix.Register.R9 ]

   class Addr (object) :
      """Strukturovaný popis adresy [base + index*scale + displ].
      Vlastní třída, protože iced-x86 MemoryOperand je opaque
      (nemá gettery) — nešlo by k němu zpětně přičítat field offset
      ve fieldExpr / ptrFieldExpr. Materializace na iced
      MemoryOperand až v okamžiku použití přes .to_mem ()."""

      def __init__ (self, base = None, index = None, scale = 1, displ = 0) :
          self.base = base if base is not None else ix.Register.NONE
          self.index = index if index is not None else ix.Register.NONE
          self.scale = scale
          self.displ = displ

      def shifted (self, off) :
          return Addr (self.base, self.index, self.scale, self.displ + off)

      def to_mem (self) :
          return ix.MemoryOperand (base = self.base, index = self.index,
             scale = self.scale, displ = self.displ)

   SETCC_TABLE = {
      ltExpr : ix.Code.SETL_RM8,
      leExpr : ix.Code.SETLE_RM8,
      gtExpr : ix.Code.SETG_RM8,
      geExpr : ix.Code.SETGE_RM8,
      eqExpr : ix.Code.SETE_RM8,
      neExpr : ix.Code.SETNE_RM8,
   }

# ---------------------------------------------------------------------------

class Asm (object) :
   """Sběrač instrukcí + jmenné labely. Použití:
        a = Asm ()
        a.emit (instr)
        a.label ("loop")
        a.jcc (Code.JE_REL32_64, "end")
        ...
        bytes_, label_addr = a.encode_at (base_address)

   Implementace dvouprůchodová: první průchod pomocí Encoderu
   změří velikost každé instrukce a tím spočítá adresy labelů,
   druhý průchod sestaví výslednou instrukční stopu s rozřešenými
   cíli skoků a zakóduje přes BlockEncoder."""

   def __init__ (self) :
       self.entries = [ ]   # ('i', inst) | ('l', name) | ('b', code, name) | ('c', name)

   def emit (self, inst) :
       self.entries.append (('i', inst))

   def label (self, name) :
       self.entries.append (('l', name))

   def jcc (self, code, label_name) :
       """Podmíněný i bezpodmíněný skok na label (kód určuje, který)."""
       self.entries.append (('b', code, label_name))

   def call (self, label_name) :
       """call <label> (přímé volání v rámci tohoto bloku)."""
       self.entries.append (('c', label_name))

   def encode_at (self, base_addr) :
       # první průchod: změř a najdi adresy labelů
       offset = 0
       label_addr = { }
       enc1 = ix.Encoder (64)
       for e in self.entries :
           kind = e [0]
           if kind == 'l' :
              label_addr [e [1]] = base_addr + offset
           elif kind == 'i' :
              sz = enc1.encode (e [1], base_addr + offset)
              enc1.take_buffer ()
              offset += sz
           elif kind == 'b' :
              # placeholder se stejným cílem jako adresa instrukce —
              # iced si zvolí 32-bit displacement, velikost stejná jako
              # později s reálným cílem
              tmp = ix.Instruction.create_branch (e [1], base_addr + offset)
              sz = enc1.encode (tmp, base_addr + offset)
              enc1.take_buffer ()
              offset += sz
           elif kind == 'c' :
              tmp = ix.Instruction.create_branch (ix.Code.CALL_REL32_64, base_addr + offset)
              sz = enc1.encode (tmp, base_addr + offset)
              enc1.take_buffer ()
              offset += sz

       # druhý průchod: sestav instrukce s rozřešenými cíli
       instructions = [ ]
       for e in self.entries :
           kind = e [0]
           if kind == 'i' :
              instructions.append (e [1])
           elif kind == 'b' :
              tgt = label_addr.get (e [2])
              if tgt is None :
                 raise RuntimeError ("undefined label: " + e [2])
              instructions.append (ix.Instruction.create_branch (e [1], tgt))
           elif kind == 'c' :
              tgt = label_addr.get (e [1])
              if tgt is None :
                 raise RuntimeError ("undefined label: " + e [1])
              instructions.append (ix.Instruction.create_branch (ix.Code.CALL_REL32_64, tgt))
           # 'l' nic neemituje

       # fix_branches=False zakáže BlockEncoderu zkracovat rel32 na rel8
       # (jinak by se neshodovalo s velikostmi z Encoderu v pass 1)
       enc = ix.BlockEncoder (64, fix_branches = False)
       enc.add_many (instructions)
       return enc.encode (base_addr), label_addr

# ---------------------------------------------------------------------------

class GenerateModule (object) :

   def __init__ (self, compiler) :
       super (GenerateModule, self).__init__ ()
       self.compiler = compiler

   def compile (self) :
       if not use_iced :
          print ("MISSING iced-x86")
          return
       self.code_program ()

   # -----------------------------------------------------------------------

   def code_program (self) :
       self.asm = Asm ()
       self.label_counter = 0
       self.func_decls = [ ]
       self.global_decls = [ ]
       self.globals_base = 0
       self.globals_size = 0
       self.globals_mem = None
       # Stringové literály: oddělená RW page, do které je dopisujeme
       # postupně při generování kódu. Adresy se rovnou zapečou do
       # instrukčního proudu jako 64-bit immediate.
       self.strings_mem = mmap.mmap (-1, 4096,
          prot = mmap.PROT_READ | mmap.PROT_WRITE)
       self.strings_base = ctypes.addressof (
          ctypes.c_char.from_buffer (self.strings_mem))
       self.strings_off = 0

       # Pass 0: rozlož všechny top-level struktury (gen_field_off pro
       # každý člen, gen_struct_size na class_decl). Dělá se předem, aby
       # si _calc_size níže mohl rovnou sáhnout na velikost struktury.
       for decl in self.compiler.global_scope.item_list :
           if getattr (decl, 'kind', None) == classDecl :
              self._struct_layout (decl)
              print ("STRUCT", decl.item_name, "size", decl.gen_struct_size)

       # Pass 1: rozmist globální proměnné v data oblasti. Dělá se před
       # generováním kódu funkcí, protože _addr_of pro globální simpleName
       # potřebuje znát globals_base + offset (vkládá se do kódu jako
       # 64-bitová konstanta).
       for decl in self.compiler.global_scope.item_list :
           if isinstance (decl, CmmSimpleItem) and not decl.is_function :
              if getattr (decl, 'skip_code', False) : continue
              size = self._calc_size (decl.item_type)
              size = (size + 7) & ~7 # zarovnání na qword
              decl.gen_global_off = self.globals_size
              self.globals_size += size
              self.global_decls.append (decl)
              print ("VARIABLE", decl.item_name, "size", size, "off",
                     hex (decl.gen_global_off))

       # Alokuj data oblast (zero-initialized, RW). Velikost zaokrouhli
       # na celou stránku; mmap to stejně dělá.
       if self.globals_size > 0 :
          page = 4096
          gsize = ((self.globals_size + page - 1) // page) * page
          self.globals_mem = mmap.mmap (-1, gsize,
             prot = mmap.PROT_READ | mmap.PROT_WRITE)
          self.globals_base = ctypes.addressof (
             ctypes.c_char.from_buffer (self.globals_mem))
          print ("globals at", hex (self.globals_base), "size",
                 self.globals_size)

          # Pre-fill: globální int proměnné s literálním inicializátorem
          # (`const int N = 20;`) zapíšeme do dataové oblasti přímo z
          # Pythonu — generátor jinak nemá kdy initializátory spustit.
          # Komplexnější výrazy by chtěly modul-init funkci; pro v1
          # stačí compile-time evaluace přes _eval_const_int.
          for decl in self.global_decls :
              init = getattr (decl, 'init', None)
              if init is None :
                 continue
              inner = getattr (getattr (init, 'value', None), 'inner_expr', None)
              v = self._eval_const_int (inner)
              if v is None :
                 continue
              self.globals_mem.seek (decl.gen_global_off)
              self.globals_mem.write (v.to_bytes (8, 'little', signed = True))

       # Pass 1.5: rozřeš deklarace bez těla jako externí funkce přes
       # libc symboly (ctypes.CDLL(None) viděl celý loadovaný proces).
       # Adresa se pak vkládá do kódu při call jako 64-bit immediate.
       for decl in self.compiler.global_scope.item_list :
           if isinstance (decl, CmmSimpleItem) and decl.is_function :
              if getattr (decl, 'skip_code', False) : continue
              if getattr (decl, 'item_body', None) is None :
                 if not hasattr (self, '_libc') :
                    self._libc = ctypes.CDLL (None)
                 try :
                    fn = getattr (self._libc, decl.item_name)
                    decl.gen_extern_addr = ctypes.cast (fn, ctypes.c_void_p).value
                    print ("EXTERN", decl.item_name, "at",
                       hex (decl.gen_extern_addr))
                    self.func_decls.append (decl)
                 except (AttributeError, OSError) as e :
                    print ("could not resolve extern", decl.item_name, ":", e)

       # Pass 2: kódování funkcí (jen ty s tělem)
       for decl in self.compiler.global_scope.item_list :
           if isinstance (decl, CmmSimpleItem) and decl.is_function :
              if getattr (decl, 'skip_code', False) : continue
              if getattr (decl, 'item_body', None) is None :
                 continue
              print ("FUNCTION", decl.item_name)
              self.code_function (decl)
              self.func_decls.append (decl)

       if not self.func_decls :
          print ("no functions to generate")
          return

       # Přidělíme spustitelnou paměť. mmap musíme držet na úrovni instance,
       # aby paměť nezmizela před voláním funkce.
       page_size = 65536
       self.exec_mem = mmap.mmap (-1, page_size,
          prot = mmap.PROT_READ | mmap.PROT_WRITE | mmap.PROT_EXEC)
       base_addr = ctypes.addressof (ctypes.c_char.from_buffer (self.exec_mem))

       code_bytes, label_addr = self.asm.encode_at (base_addr)
       if len (code_bytes) > page_size :
          print ("emitted code too big:", len (code_bytes), ">", page_size)
          return

       self.exec_mem.seek (0)
       self.exec_mem.write (code_bytes)

       print ("emitted", len (code_bytes), "bytes at", hex (base_addr))
       self._disassemble (code_bytes, base_addr)

       # Pokud existuje main () s 0 parametry, zavolej ji a vypiš návrat.
       for decl in self.func_decls :
           if decl.item_name == "main" and len (decl.item_list) == 0 :
              fn_addr = label_addr [self._func_label (decl)]
              fn = ctypes.CFUNCTYPE (ctypes.c_int64) (fn_addr)
              result = fn ()
              print ("main returned:", result)
              return

   def _disassemble (self, code_bytes, base_addr) :
       decoder = ix.Decoder (64, code_bytes, ip = base_addr)
       formatter = ix.Formatter (ix.FormatterSyntax.INTEL)
       formatter.first_operand_char_index = 8
       for inst in decoder :
           text = formatter.format (inst)
           print ("  %016x: %s" % (inst.ip, text))

   # -----------------------------------------------------------------------
   # labely

   def _func_label (self, decl) :
       return "func_" + decl.item_name

   def _new_label (self, prefix) :
       self.label_counter += 1
       return "%s_%d" % (prefix, self.label_counter)

   # -----------------------------------------------------------------------
   # funkce: prolog, frame layout, parametry, epilog

   def code_function (self, decl) :
       self.cur_epilog = self._new_label ("epilog")
       self.frame_off = 0

       params = list (decl.item_list) if decl.item_list else [ ]

       # Sloty pro parametry: prvních 6 dostane stack slot (do něj se v
       # prologu přesypou z RDI..R9), další jsou už na zásobníku
       # od volajícího (na adresách [rbp+16+8*i]).
       for inx, p in enumerate (params) :
           if inx < 6 :
              self.frame_off -= 8
              p.gen_frame_off = self.frame_off
              p.gen_in_reg = True
           else :
              p.gen_frame_off = 16 + 8 * (inx - 6)
              p.gen_in_reg = False

       # Sloty pro lokální proměnné
       self._calc_frame (decl.item_body)

       # Frame zarovnaný na 16 B kvůli volací konvenci
       frame_size = ((- self.frame_off) + 15) & ~15

       # Prolog
       self.asm.label (self._func_label (decl))
       self.asm.emit (ix.Instruction.create_reg (ix.Code.PUSH_R64, ix.Register.RBP))
       self.asm.emit (ix.Instruction.create_reg_reg (ix.Code.MOV_R64_RM64,
          ix.Register.RBP, ix.Register.RSP))
       if frame_size > 0 :
          self.asm.emit (ix.Instruction.create_reg_i32 (ix.Code.SUB_RM64_IMM32,
             ix.Register.RSP, frame_size))

       # Přesypání registrových parametrů do jejich slotů
       for inx, p in enumerate (params) :
           if inx < 6 and getattr (p, 'gen_in_reg', False) :
              src = ARG_REGS [inx]
              mem = ix.MemoryOperand (ix.Register.RBP, displ = p.gen_frame_off)
              self.asm.emit (ix.Instruction.create_mem_reg (ix.Code.MOV_RM64_R64,
                 mem, src))

       # Tělo
       self.code_stat (decl.item_body)

       # Epilog (sem také míří return)
       self.asm.label (self.cur_epilog)
       self.asm.emit (ix.Instruction.create_reg_reg (ix.Code.MOV_R64_RM64,
          ix.Register.RSP, ix.Register.RBP))
       self.asm.emit (ix.Instruction.create_reg (ix.Code.POP_R64, ix.Register.RBP))
       self.asm.emit (ix.Instruction.create (ix.Code.RETNQ))

   def _calc_frame (self, stat) :
       """Rekurzivně projde tělo funkce a každé lokální proměnné přiřadí
       gen_frame_off (offset od RBP). Děláme to dopředu, ještě před
       generováním kódu, abychom v prologu znali velikost framu."""
       if stat is None :
          return
       kind = getattr (stat, 'kind', None)
       if kind == compoundStat :
          for it in stat.items :
              self._calc_frame (it)
       elif kind == ifStat :
          self._calc_frame (stat.then_stat)
          self._calc_frame (stat.else_stat)
       elif kind == whileStat :
          self._calc_frame (stat.body)
       elif kind == forStat :
          self._calc_frame (stat.from_expr)
          self._calc_frame (stat.body)
       elif kind == simpleDecl :
          for item in stat.items :
              size = self._calc_size (item.item_type)
              size = max (size, 8) # i prázdná pole zaberou aspoň qword
              size = (size + 7) & ~7 # zarovnání na qword
              self.frame_off -= size
              item.gen_frame_off = self.frame_off

   # -----------------------------------------------------------------------
   # příkazy

   def code_stat (self, stat) :
       if stat is None :
          return
       kind = stat.kind
       if kind == compoundStat :
          for it in stat.items :
              self.code_stat (it)
       elif kind == ifStat :
          self.code_if (stat)
       elif kind == whileStat :
          self.code_while (stat)
       elif kind == forStat :
          self.code_for (stat)
       elif kind == returnStat :
          self.code_return (stat)
       elif kind == simpleStat :
          self.code_expr (stat.inner_expr)
       elif kind == simpleDecl :
          self.code_local_decl (stat)
       elif kind == emptyStat :
          pass
       else :
          print ("unsupported statement kind", kind)

   def code_local_decl (self, stat) :
       """int x; nebo int x = expr; (uvnitř funkce). Sloty už máme z
       _calc_frame; tady jen vyhodnotíme případné inicializátory."""
       for item in stat.items :
           init = getattr (item, 'init', None)
           if init is None :
              continue
           init_value = getattr (init, 'value', None)
           if init_value is None :
              continue
           # CmmInitSimple má inner_expr, CmmInitList neumíme
           inner = getattr (init_value, 'inner_expr', None)
           if inner is None :
              print ("init: only simple initializers supported")
              continue
           self.code_expr (inner)
           self._store_local (item, ix.Register.RAX)

   def code_if (self, stat) :
       end_lab = self._new_label ('endif')
       if stat.else_stat is None :
          # if (cond) then_stat
          self.code_expr (stat.cond)
          self._test_rax_jz (end_lab)
          self.code_stat (stat.then_stat)
          self.asm.label (end_lab)
       else :
          else_lab = self._new_label ('else')
          self.code_expr (stat.cond)
          self._test_rax_jz (else_lab)
          self.code_stat (stat.then_stat)
          self.asm.jcc (ix.Code.JMP_REL32_64, end_lab)
          self.asm.label (else_lab)
          self.code_stat (stat.else_stat)
          self.asm.label (end_lab)

   def code_while (self, stat) :
       loop_lab = self._new_label ('loop')
       end_lab  = self._new_label ('endloop')
       self.asm.label (loop_lab)
       self.code_expr (stat.cond)
       self._test_rax_jz (end_lab)
       self.code_stat (stat.body)
       self.asm.jcc (ix.Code.JMP_REL32_64, loop_lab)
       self.asm.label (end_lab)

   def code_for (self, stat) :
       """for (init; cond; step) body  →  init; while (cond) { body; step; }
       Forma 'for (decl : iter)' není podporovaná."""
       if getattr (stat, 'iter_expr', None) is not None :
          print ("for-each not supported")
          return
       if getattr (stat, 'from_expr', None) is not None :
          self.code_stat (stat.from_expr)

       loop_lab = self._new_label ('forloop')
       end_lab  = self._new_label ('endfor')
       self.asm.label (loop_lab)
       if getattr (stat, 'cond_expr', None) is not None :
          self.code_expr (stat.cond_expr)
          self._test_rax_jz (end_lab)
       self.code_stat (stat.body)
       if getattr (stat, 'step_expr', None) is not None :
          self.code_expr (stat.step_expr)
       self.asm.jcc (ix.Code.JMP_REL32_64, loop_lab)
       self.asm.label (end_lab)

   def code_return (self, stat) :
       ret_expr = getattr (stat, 'return_expr', None)
       if ret_expr is not None :
          self.code_expr (ret_expr)
       self.asm.jcc (ix.Code.JMP_REL32_64, self.cur_epilog)

   # -----------------------------------------------------------------------
   # výrazy: každý code_expr necháva výsledek v RAX

   def code_expr (self, expr) :
       if expr is None :
          self._zero_rax ()
          return

       kind = expr.kind

       if   kind == intValue   : self._mov_imm_rax (int (expr.value))
       elif kind == stringValue: self._emit_string (expr)
       elif kind == simpleName :
          # Vestavěné konstanty: true=1, false / nullptr / NULL / null = 0.
          # Cmm_comp tato jména obvykle nerezoluje — projdou jako name
          # bez item_decl, takže _load_lvalue by skončil chybou.
          ident = getattr (expr, 'id', '')
          if ident == 'true' :
             self._mov_imm_rax (1)
          elif ident in ('false', 'nullptr', 'NULL', 'null') :
             self._zero_rax ()
          else :
             self._load_lvalue (expr, ix.Register.RAX)
       elif kind == indexExpr  : self._load_lvalue (expr, ix.Register.RAX)
       elif kind == derefExpr  : self._load_lvalue (expr, ix.Register.RAX)
       elif kind == fieldExpr  : self._load_lvalue (expr, ix.Register.RAX)
       elif kind == ptrFieldExpr: self._load_lvalue (expr, ix.Register.RAX)
       elif kind == addrExpr   : self.code_addr (expr)
       elif kind == sizeofExpr : self.code_sizeof (expr)
       elif kind == newExpr    : self.code_new (expr)
       elif kind == subexprExpr: self.code_expr (expr.param)
       elif kind == simpleStat : self.code_expr (expr.inner_expr) # condition_value wrapper
       elif kind in [ assignExpr,
                      addAssignExpr, subAssignExpr, mulAssignExpr,
                      divAssignExpr, modAssignExpr,
                      andAssignExpr, orAssignExpr, xorAssignExpr,
                      shlAssignExpr, shrAssignExpr ] :
          self.code_assign (expr)
       elif kind == callExpr   : self.code_call (expr)
       elif kind == logAndExpr : self.code_log_and (expr)
       elif kind == logOrExpr  : self.code_log_or (expr)
       elif kind == logNotExpr : self.code_log_not (expr)
       elif kind == minusExpr  : self.code_unary (expr, ix.Code.NEG_RM64)
       elif kind == plusExpr   : self.code_expr (expr.param) # +x je x
       elif kind == bitNotExpr : self.code_unary (expr, ix.Code.NOT_RM64)
       elif kind == incExpr    : self.code_inc_dec (expr.param,  +1, prefix = True)
       elif kind == decExpr    : self.code_inc_dec (expr.param,  -1, prefix = True)
       elif kind == postIncExpr: self.code_inc_dec (expr.left,   +1, prefix = False)
       elif kind == postDecExpr: self.code_inc_dec (expr.left,   -1, prefix = False)
       elif kind in [ addExpr, subExpr, mulExpr, divExpr, modExpr,
                      bitAndExpr, bitOrExpr, bitXorExpr,
                      shlExpr, shrExpr ] :
          self.code_binop (expr)
       elif kind in [ ltExpr, leExpr, gtExpr, geExpr, eqExpr, neExpr ] :
          self.code_compare (expr)
       else :
          print ("unsupported expr kind", kind)
          self._zero_rax ()

   # -----------------------------------------------------------------------
   # pomocné: přístup do RAX, načítání/ukládání proměnných

   def _zero_rax (self) :
       self.asm.emit (ix.Instruction.create_reg_reg (ix.Code.XOR_R64_RM64,
          ix.Register.RAX, ix.Register.RAX))

   def _mov_imm_rax (self, value) :
       """RAX = value (int64)."""
       self.asm.emit (ix.Instruction.create_reg_i64 (ix.Code.MOV_R64_IMM64,
          ix.Register.RAX, value))

   def _emit_string (self, expr) :
       """Stringový literál: zapíšeme bajty + nulový terminátor do
       strings_mem a do RAX vyemitujeme jeho adresu jako 64-bit
       immediate. Parser dodává expr.value už s rozparsovanými
       escape sekvencemi (skutečný \\n jako bajt 0x0a)."""
       text = getattr (expr, 'value', '')
       data = text.encode ('utf-8') + b'\x00'
       if self.strings_off + len (data) > len (self.strings_mem) :
          print ("string literal overflow:", repr (text))
          self._zero_rax ()
          return
       addr = self.strings_base + self.strings_off
       self.strings_mem.seek (self.strings_off)
       self.strings_mem.write (data)
       self.strings_off += len (data)
       self._mov_imm_rax (addr)

   def _test_rax_jz (self, label_name) :
       """test rax, rax; je <label>"""
       self.asm.emit (ix.Instruction.create_reg_reg (ix.Code.TEST_RM64_R64,
          ix.Register.RAX, ix.Register.RAX))
       self.asm.jcc (ix.Code.JE_REL32_64, label_name)

   def _eval_const_int (self, expr) :
       """Vyhodnoť výraz na celé číslo, pokud jde — nebo vrať None.
       Podporuje:
         - intValue (literál)
         - simpleName ukazující na proměnnou s celočíselným const initem
         - subexpr (závorky)
         - unární minus / plus
         - binární +, -, *, /, %, &, |, ^, <<, >>
       Stačí pro typické 'const int N = 20; int a[N];' nebo
       'const int Max = 4; int key[Max+1];' kde Max+1 musí být
       compile-time vyhodnoceno na velikost pole."""
       if expr is None :
          return None
       kind = getattr (expr, 'kind', None)
       if kind == intValue :
          try : return int (expr.value)
          except (ValueError, TypeError) : return None
       if kind == simpleName :
          decl = getattr (expr, 'item_decl', None)
          if decl is None :
             return None
          init = getattr (decl, 'init', None)
          if init is None :
             return None
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
                    bitAndExpr, bitOrExpr, bitXorExpr,
                    shlExpr, shrExpr ] :
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

   def _calc_size (self, t) :
       """Velikost typu v bajtech. Vše atomické (int, char, ukazatel,
       reference) je qword (8 B) — naivní celočíselný model. Pole
       je element_size * lim, kde lim může být literál nebo simpleName
       odkazující na const int. NamedType odkazující na strukturu
       (CmmClassDecl) si nechá spočítat layout přes _struct_layout."""
       if isinstance (t, ArrayType) :
          cnt = self._eval_const_int (t.lim) or 0
          return self._calc_size (t.type_from) * cnt
       if isinstance (t, NamedType) :
          type_decl = getattr (t, 'type_decl', None)
          if type_decl is not None and getattr (type_decl, 'kind', None) == classDecl :
             return self._struct_layout (type_decl)
       return 8

   def _lookup_field_off (self, left, field_name, deref_pointer) :
       """Najdi offset pole v rodičovské struktuře. Cmm_comp obvykle
       nastaví field_name.item_decl na členský CmmSimpleItem (s
       gen_field_off po _struct_layout) — to je rychlá cesta. Když ale
       cmm_comp jméno nerozřeší (typicky když 'left' jde přes
       ReferenceType, který front-end nedereferencuje), spadneme zpět
       na lookup podle jména skrze left.item_type: postupně odstraníme
       reference, případně jeden pointer (pro ptrFieldExpr) a hledáme
       v member listu příslušné CmmClassDecl."""
       fdecl = getattr (field_name, 'item_decl', None)
       if fdecl is not None and hasattr (fdecl, 'gen_field_off') :
          return fdecl.gen_field_off

       fname = getattr (field_name, 'id', None)
       if fname is None :
          print ("unknown field: ?")
          return None

       t = getattr (left, 'item_type', None)
       while isinstance (t, ReferenceType) :
          t = t.type_from
       if deref_pointer :
          if not isinstance (t, PointerType) :
             print ("unknown field:", fname, "(no pointer base)")
             return None
          t = t.type_from
          while isinstance (t, ReferenceType) :
             t = t.type_from
       if not isinstance (t, NamedType) :
          print ("unknown field:", fname, "(non-class type)")
          return None
       type_decl = getattr (t, 'type_decl', None)
       if type_decl is None or getattr (type_decl, 'kind', None) != classDecl :
          print ("unknown field:", fname, "(no class decl)")
          return None
       self._struct_layout (type_decl) # idempotent
       for member in type_decl.item_list :
           if not isinstance (member, CmmSimpleItem) : continue
           if getattr (member, 'is_function', False) : continue
           if getattr (member, 'item_name', '') == fname :
              return getattr (member, 'gen_field_off', None)
       print ("unknown field:", fname)
       return None

   def _struct_layout (self, class_decl) :
       """Rozmísti pole struktury: postupně přiřaď gen_field_off každému
       členu (CmmSimpleItem v class_decl.item_list, vynech metody),
       celkovou velikost ulož do class_decl.gen_struct_size. Memoizace:
       pokud gen_struct_size už existuje, layout proběhl, vrátíme."""
       cached = getattr (class_decl, 'gen_struct_size', None)
       if cached is not None :
          return cached
       off = 0
       for member in class_decl.item_list :
           if not isinstance (member, CmmSimpleItem) :
              continue
           if getattr (member, 'is_function', False) :
              continue
           sz = self._calc_size (member.item_type)
           sz = (sz + 7) & ~7 # zarovnání každého pole na qword
           member.gen_field_off = off
           off += sz
       class_decl.gen_struct_size = off
       return off

   def _addr_of (self, expr, helper) :
       """Vrátí Addr ukazující na lvalue 'expr', nebo None při chybě.
       Může emitnout instrukce, které využijí 'helper' register
       (a tím ho přepíší).

       Pro lokální proměnnou / parametr nic neemituje — vrátí rovnou
       Addr(RBP, displ=frame_off). Pro globální proměnnou emituje
           mov helper, imm64 (= globals_base + offset)
       a vrátí Addr(helper). Pro arr[i] používá SIB s indexem v RDX.
       Pro *p vyhodnotí pointer do helperu. Pro obj.f / p->f
       přičte field_off k displ."""
       if expr is None :
          return None
       kind = expr.kind
       if kind == subexprExpr :
          return self._addr_of (expr.param, helper)
       if kind == simpleName :
          decl = expr.item_decl
          if decl is None :
             print ("unknown variable", getattr (expr, 'id', '?'))
             return None
          if hasattr (decl, 'gen_frame_off') :
             # Reference parametr (int &, T * &): slot drží adresu
             # původní proměnné, přístup k 'p' = přístup *přes* tu
             # adresu. Načteme adresu ze slotu do helperu a vrátíme
             # [helper] — chování shodné s 'derefExpr p'.
             if isinstance (decl.item_type, ReferenceType) :
                slot = ix.MemoryOperand (base = ix.Register.RBP,
                   displ = decl.gen_frame_off)
                self.asm.emit (ix.Instruction.create_reg_mem (
                   ix.Code.MOV_R64_RM64, helper, slot))
                return Addr (base = helper)
             return Addr (base = ix.Register.RBP, displ = decl.gen_frame_off)
          if hasattr (decl, 'gen_global_off') :
             addr_val = self.globals_base + decl.gen_global_off
             self.asm.emit (ix.Instruction.create_reg_i64 (
                ix.Code.MOV_R64_IMM64, helper, addr_val))
             return Addr (base = helper)
          print ("variable has no slot:", getattr (decl, 'item_name', '?'))
          return None
       if kind == indexExpr :
          # arr[i]: spočítej index do RAX, pushni, spočítej adresu pole
          # přes lea do helperu, popni index do RDX, vrať [helper + RDX*8].
          self.code_expr (expr.param)
          self.asm.emit (ix.Instruction.create_reg (ix.Code.PUSH_R64,
             ix.Register.RAX))
          base_addr = self._addr_of (expr.left, helper)
          if base_addr is None :
             self.asm.emit (ix.Instruction.create_reg (ix.Code.POP_R64,
                ix.Register.RAX))
             return None
          self.asm.emit (ix.Instruction.create_reg_mem (ix.Code.LEA_R64_M,
             helper, base_addr.to_mem ()))
          self.asm.emit (ix.Instruction.create_reg (ix.Code.POP_R64,
             ix.Register.RDX))
          return Addr (base = helper, index = ix.Register.RDX, scale = 8)
       if kind == derefExpr :
          # *p: vyhodnoť p (ukazatel) do RAX. Pokud caller chce výsledek
          # v jiném registru než RAX, přesuň. Vrátíme Addr(helper).
          self.code_expr (expr.param)
          if helper != ix.Register.RAX :
             self.asm.emit (ix.Instruction.create_reg_reg (ix.Code.MOV_R64_RM64,
                helper, ix.Register.RAX))
          return Addr (base = helper)
       if kind == fieldExpr :
          # obj.f : addr_of(obj) + field_off, jen rozšíříme displacement
          inner = self._addr_of (expr.left, helper)
          if inner is None :
             return None
          off = self._lookup_field_off (expr.left, expr.field_name,
                                        deref_pointer = False)
          if off is None :
             return None
          return inner.shifted (off)
       if kind == ptrFieldExpr :
          # p->f : vyhodnoť pointer p do RAX, přesuň do helperu, pak
          # přidej offset pole — přesně jako *p, ale s nenulovým displ.
          self.code_expr (expr.left)
          if helper != ix.Register.RAX :
             self.asm.emit (ix.Instruction.create_reg_reg (ix.Code.MOV_R64_RM64,
                helper, ix.Register.RAX))
          off = self._lookup_field_off (expr.left, expr.field_name,
                                        deref_pointer = True)
          if off is None :
             return None
          return Addr (base = helper, displ = off)
       print ("unsupported lvalue kind:", kind)
       return None

   def _load_lvalue (self, expr, helper) :
       """RAX = hodnota lvalue 'expr'. helper je register, který může
       _addr_of využít k výpočtu adresy (a tím ho přepsat)."""
       addr = self._addr_of (expr, helper)
       if addr is None :
          self._zero_rax ()
          return
       self.asm.emit (ix.Instruction.create_reg_mem (ix.Code.MOV_R64_RM64,
          ix.Register.RAX, addr.to_mem ()))

   def _store_local (self, decl, src_reg) :
       """[rbp + decl.gen_frame_off] = src_reg"""
       if not hasattr (decl, 'gen_frame_off') :
          print ("store to var without slot:", getattr (decl, 'item_name', '?'))
          return
       mem = ix.MemoryOperand (ix.Register.RBP, displ = decl.gen_frame_off)
       self.asm.emit (ix.Instruction.create_mem_reg (ix.Code.MOV_RM64_R64,
          mem, src_reg))

   # -----------------------------------------------------------------------
   # přiřazení, volání

   def code_assign (self, expr) :
       """Plain '=' nebo compound '+=' '-=' atd.

       Plain (assignExpr): rhs do RAX, push, _addr_of(lhs, helper=RCX),
       pop rax, mov [mem], rax.

       Compound: rhs do RAX, push, _addr_of(lhs, helper=R8) (R8 zvolený,
       aby RCX zůstalo volné pro shift count / div divisor), načti staré
       *mem do RAX, pop rcx (=rhs), spočítej novou hodnotu, ulož.
       Pro /= a %= musíme push/pop RDX okolo cqo+idiv (RDX se používá
       jako index v mem pro arr[i] případy, a IDIV ho navíc přepisuje
       zbytkem). mini-asm.cc commit 825a2f5 řeší stejný problém v C++."""
       kind = expr.kind

       if kind == assignExpr :
          self.code_expr (expr.right)
          self.asm.emit (ix.Instruction.create_reg (ix.Code.PUSH_R64, ix.Register.RAX))
          addr = self._addr_of (expr.left, ix.Register.RCX)
          self.asm.emit (ix.Instruction.create_reg (ix.Code.POP_R64, ix.Register.RAX))
          if addr is None :
             return
          self.asm.emit (ix.Instruction.create_mem_reg (ix.Code.MOV_RM64_R64,
             addr.to_mem (), ix.Register.RAX))
          return

       # compound
       self.code_expr (expr.right)
       self.asm.emit (ix.Instruction.create_reg (ix.Code.PUSH_R64, ix.Register.RAX))
       addr = self._addr_of (expr.left, ix.Register.R8)
       if addr is None :
          self.asm.emit (ix.Instruction.create_reg (ix.Code.POP_R64, ix.Register.RAX))
          return
       mem = addr.to_mem ()
       # RAX = staré *mem, RCX = rhs
       self.asm.emit (ix.Instruction.create_reg_mem (ix.Code.MOV_R64_RM64,
          ix.Register.RAX, mem))
       self.asm.emit (ix.Instruction.create_reg (ix.Code.POP_R64, ix.Register.RCX))

       if kind == addAssignExpr :
          self.asm.emit (ix.Instruction.create_reg_reg (ix.Code.ADD_R64_RM64,
             ix.Register.RAX, ix.Register.RCX))
       elif kind == subAssignExpr :
          self.asm.emit (ix.Instruction.create_reg_reg (ix.Code.SUB_R64_RM64,
             ix.Register.RAX, ix.Register.RCX))
       elif kind == mulAssignExpr :
          self.asm.emit (ix.Instruction.create_reg_reg (ix.Code.IMUL_R64_RM64,
             ix.Register.RAX, ix.Register.RCX))
       elif kind == andAssignExpr :
          self.asm.emit (ix.Instruction.create_reg_reg (ix.Code.AND_R64_RM64,
             ix.Register.RAX, ix.Register.RCX))
       elif kind == orAssignExpr :
          self.asm.emit (ix.Instruction.create_reg_reg (ix.Code.OR_R64_RM64,
             ix.Register.RAX, ix.Register.RCX))
       elif kind == xorAssignExpr :
          self.asm.emit (ix.Instruction.create_reg_reg (ix.Code.XOR_R64_RM64,
             ix.Register.RAX, ix.Register.RCX))
       elif kind == shlAssignExpr :
          self.asm.emit (ix.Instruction.create_reg_reg (ix.Code.SHL_RM64_CL,
             ix.Register.RAX, ix.Register.CL))
       elif kind == shrAssignExpr :
          self.asm.emit (ix.Instruction.create_reg_reg (ix.Code.SAR_RM64_CL,
             ix.Register.RAX, ix.Register.CL))
       elif kind in [ divAssignExpr, modAssignExpr ] :
          # cqo přepíše RDX (možný index v mem); idiv ho přepíše zbytkem.
          # Schováme RDX, spočítáme do R9 požadovaný výsledek, obnovíme RDX.
          self.asm.emit (ix.Instruction.create_reg (ix.Code.PUSH_R64, ix.Register.RDX))
          self.asm.emit (ix.Instruction.create (ix.Code.CQO))
          self.asm.emit (ix.Instruction.create_reg (ix.Code.IDIV_RM64, ix.Register.RCX))
          src = ix.Register.RAX if kind == divAssignExpr else ix.Register.RDX
          self.asm.emit (ix.Instruction.create_reg_reg (ix.Code.MOV_R64_RM64,
             ix.Register.R9, src))
          self.asm.emit (ix.Instruction.create_reg (ix.Code.POP_R64, ix.Register.RDX))
          self.asm.emit (ix.Instruction.create_mem_reg (ix.Code.MOV_RM64_R64,
             mem, ix.Register.R9))
          self.asm.emit (ix.Instruction.create_reg_reg (ix.Code.MOV_R64_RM64,
             ix.Register.RAX, ix.Register.R9))
          return
       else :
          print ("unsupported compound assign kind:", kind)
          return

       self.asm.emit (ix.Instruction.create_mem_reg (ix.Code.MOV_RM64_R64,
          mem, ix.Register.RAX))

   def code_addr (self, expr) :
       """&x : adresa lvalue do RAX. Funguje pro libovolný lvalue, který
       _addr_of zvládne — &x (lokál/glob/param), &arr[i], &*p, ..."""
       addr = self._addr_of (expr.param, ix.Register.RAX)
       if addr is None :
          self._zero_rax ()
          return
       self.asm.emit (ix.Instruction.create_reg_mem (ix.Code.LEA_R64_M,
          ix.Register.RAX, addr.to_mem ()))

   def _type_of_expr (self, expr) :
       """Z AST výrazu zjisti jeho typ (Type), pokud lze. Při neúspěchu
       vrať None. Projde subexpr-závorky."""
       while expr is not None and getattr (expr, 'kind', None) == subexprExpr :
          expr = expr.param
       if expr is None :
          return None
       return getattr (expr, 'item_type', None)

   def code_sizeof (self, expr) :
       """sizeof (T) nebo sizeof (variable) → compile-time velikost
       v bajtech. Cmm_comp dosadí na expr.value.item_type typ argumentu;
       my zavoláme _calc_size."""
       t = self._type_of_expr (expr.value)
       if t is None :
          print ("sizeof: unknown type, using 8")
          self._mov_imm_rax (8)
          return
       size = self._calc_size (t)
       self._mov_imm_rax (size)

   def _ensure_calloc (self) :
       """Líně rozřeš libc calloc (pro 'new T'). Adresa cachovaná na
       instanci, aby ji nečetli libc opakovaně."""
       if not hasattr (self, '_calloc_addr') :
          if not hasattr (self, '_libc') :
             self._libc = ctypes.CDLL (None)
          self._calloc_addr = ctypes.cast (
             self._libc.calloc, ctypes.c_void_p).value
       return self._calloc_addr

   def code_new (self, expr) :
       """new T  →  calloc (1, sizeof (T)).  Výsledek (ukazatel) v RAX.
       Calloc je zvolen místo malloc, aby uživatel nemusel volat init
       ručně — paměť přijde vynulovaná, takže cnt=0, ref[i]=null atd.
       jsou výchozí hodnoty 'po výrobě'."""
       size = 8
       type1 = getattr (expr, 'type1', None)
       type2 = getattr (expr, 'type2', None)
       ts = None
       if type1 is not None :
          ts = getattr (type1, 'type_spec', None)
       elif type2 is not None :
          ts = getattr (type2, 'type_spec', None)
       if ts is not None :
          t = getattr (ts, 'item_type', None)
          if t is not None :
             size = self._calc_size (t)

       # Pole 'new T[n]' zatím nepodporujeme (jen jediný objekt).
       calloc_addr = self._ensure_calloc ()
       # rdi = 1 (počet prvků), rsi = size (velikost prvku)
       self.asm.emit (ix.Instruction.create_reg_i64 (ix.Code.MOV_R64_IMM64,
          ix.Register.RDI, 1))
       self.asm.emit (ix.Instruction.create_reg_i64 (ix.Code.MOV_R64_IMM64,
          ix.Register.RSI, size))
       self.asm.emit (ix.Instruction.create_reg_i64 (ix.Code.MOV_R64_IMM64,
          ix.Register.R10, calloc_addr))
       self.asm.emit (ix.Instruction.create_reg_reg (ix.Code.XOR_R32_RM32,
          ix.Register.EAX, ix.Register.EAX))
       self.asm.emit (ix.Instruction.create_reg (ix.Code.CALL_RM64,
          ix.Register.R10))

   def code_call (self, expr) :
       """Vyhodnotí argumenty, naskládá do RDI..R9 v System V pořadí,
       provede CALL na label cílové funkce. Maximum 6 argumentů.

       Pokud cílová funkce má parametr s ReferenceType (např.
       'Item *& p'), místo evaluace na hodnotu emitujeme 'lea' a
       předáme adresu argumentu. Z volajícího pohledu je to zhruba
       'enter (& root, ...)' — ale '& root' za vás napsal překladač."""
       callee = expr.left
       args = list (expr.param_list.items) if expr.param_list else [ ]

       # Pokud známe cílovou funkci, podívej se na typy parametrů,
       # abychom u referencí věděli předat adresu.
       params = [ ]
       if callee.kind == simpleName and callee.item_decl is not None :
          params = list (getattr (callee.item_decl, 'item_list', [ ]))

       # Default args: pokud volání má méně argumentů než deklarace
       # a chybějící parametry mají init, doplň je. Stejné jako kdyby
       # uživatel napsal hodnotu sám. Init expression musí být ve
       # formě CmmInitSimple.inner_expr (typicky literál nebo nullptr).
       while len (args) < len (params) :
           param = params [len (args)]
           init = getattr (param, 'init', None)
           if init is None : break
           inner = getattr (getattr (init, 'value', None), 'inner_expr', None)
           if inner is None : break
           args.append (inner)

       if len (args) > 6 :
          print ("more than 6 args not supported, truncating")
          args = args [: 6]

       for inx, a in enumerate (args) :
           is_ref = (inx < len (params)
              and isinstance (getattr (params [inx], 'item_type', None),
                              ReferenceType))
           if is_ref :
              # Adresu lvalue do RAX (lea)
              addr = self._addr_of (a, ix.Register.RAX)
              if addr is None :
                 self._zero_rax ()
              else :
                 self.asm.emit (ix.Instruction.create_reg_mem (
                    ix.Code.LEA_R64_M, ix.Register.RAX, addr.to_mem ()))
           else :
              self.code_expr (a)
           self.asm.emit (ix.Instruction.create_reg (ix.Code.PUSH_R64,
              ix.Register.RAX))

       # Pak je v opačném pořadí pop do správných argumentových registrů.
       for inx in range (len (args) - 1, -1, -1) :
           self.asm.emit (ix.Instruction.create_reg (ix.Code.POP_R64, ARG_REGS [inx]))

       if callee.kind in (simpleName, templateName) and callee.item_decl is not None \
             and getattr (callee.item_decl, 'is_function', False) :
          target = callee.item_decl
          ext_addr = getattr (target, 'gen_extern_addr', None)
          if ext_addr is not None :
             # Extern volání (printf atd.): adresu načteme do R10 a použijeme
             # indirect call. R10 je caller-saved a System V ji nepoužívá pro
             # předávání argumentů, takže nehrozí kolize s args v RDI..R9.
             # 'xor eax, eax' před voláním nuluje AL (System V požaduje, aby
             # u variadických funkcí AL obsahoval počet vector args; pro
             # celočíselné args 0). Pro nevariadické je to neškodné — RAX je
             # tak jako tak caller-saved a nese návratovou hodnotu.
             self.asm.emit (ix.Instruction.create_reg_i64 (
                ix.Code.MOV_R64_IMM64, ix.Register.R10, ext_addr))
             self.asm.emit (ix.Instruction.create_reg_reg (
                ix.Code.XOR_R32_RM32, ix.Register.EAX, ix.Register.EAX))
             self.asm.emit (ix.Instruction.create_reg (
                ix.Code.CALL_RM64, ix.Register.R10))
          else :
             self.asm.call (self._func_label (target))
       else :
          n = getattr (getattr (callee, 'item_decl', None), 'item_name', '?')
          print ("unsupported call target:", n)
          self._zero_rax ()

   # -----------------------------------------------------------------------
   # binární a unární operátory

   def code_binop (self, expr) :
       """RAX = left OP right
       Strategie: vyhodnoť left do RAX, push, vyhodnoť right do RAX,
       přesuň do RCX (mov rcx, rax), pop původní left zpátky do RAX,
       proveď operaci."""
       self.code_expr (expr.left)
       self.asm.emit (ix.Instruction.create_reg (ix.Code.PUSH_R64, ix.Register.RAX))
       self.code_expr (expr.right)
       self.asm.emit (ix.Instruction.create_reg_reg (ix.Code.MOV_R64_RM64,
          ix.Register.RCX, ix.Register.RAX))                       # RCX = right
       self.asm.emit (ix.Instruction.create_reg (ix.Code.POP_R64, ix.Register.RAX))  # RAX = left

       kind = expr.kind
       if   kind == addExpr :
          self.asm.emit (ix.Instruction.create_reg_reg (ix.Code.ADD_R64_RM64,
             ix.Register.RAX, ix.Register.RCX))
       elif kind == subExpr :
          self.asm.emit (ix.Instruction.create_reg_reg (ix.Code.SUB_R64_RM64,
             ix.Register.RAX, ix.Register.RCX))
       elif kind == mulExpr :
          self.asm.emit (ix.Instruction.create_reg_reg (ix.Code.IMUL_R64_RM64,
             ix.Register.RAX, ix.Register.RCX))
       elif kind == divExpr :
          # cqo: sign-extend RAX do RDX:RAX, pak idiv RCX → RAX = quot
          self.asm.emit (ix.Instruction.create (ix.Code.CQO))
          self.asm.emit (ix.Instruction.create_reg (ix.Code.IDIV_RM64, ix.Register.RCX))
       elif kind == modExpr :
          self.asm.emit (ix.Instruction.create (ix.Code.CQO))
          self.asm.emit (ix.Instruction.create_reg (ix.Code.IDIV_RM64, ix.Register.RCX))
          # zbytek je v RDX → přesuň do RAX
          self.asm.emit (ix.Instruction.create_reg_reg (ix.Code.MOV_R64_RM64,
             ix.Register.RAX, ix.Register.RDX))
       elif kind == bitAndExpr :
          self.asm.emit (ix.Instruction.create_reg_reg (ix.Code.AND_R64_RM64,
             ix.Register.RAX, ix.Register.RCX))
       elif kind == bitOrExpr :
          self.asm.emit (ix.Instruction.create_reg_reg (ix.Code.OR_R64_RM64,
             ix.Register.RAX, ix.Register.RCX))
       elif kind == bitXorExpr :
          self.asm.emit (ix.Instruction.create_reg_reg (ix.Code.XOR_R64_RM64,
             ix.Register.RAX, ix.Register.RCX))
       elif kind == shlExpr :
          # shl rax, cl  (cl je low 8 bitů z rcx)
          self.asm.emit (ix.Instruction.create_reg_reg (ix.Code.SHL_RM64_CL,
             ix.Register.RAX, ix.Register.CL))
       elif kind == shrExpr :
          # arithmetic shift (zachovává znaménko)
          self.asm.emit (ix.Instruction.create_reg_reg (ix.Code.SAR_RM64_CL,
             ix.Register.RAX, ix.Register.CL))

   def code_compare (self, expr) :
       """RAX = (left CMP right) ? 1 : 0"""
       self.code_expr (expr.left)
       self.asm.emit (ix.Instruction.create_reg (ix.Code.PUSH_R64, ix.Register.RAX))
       self.code_expr (expr.right)
       self.asm.emit (ix.Instruction.create_reg_reg (ix.Code.MOV_R64_RM64,
          ix.Register.RCX, ix.Register.RAX))
       self.asm.emit (ix.Instruction.create_reg (ix.Code.POP_R64, ix.Register.RAX))
       self.asm.emit (ix.Instruction.create_reg_reg (ix.Code.CMP_R64_RM64,
          ix.Register.RAX, ix.Register.RCX))
       self.asm.emit (ix.Instruction.create_reg (SETCC_TABLE [expr.kind], ix.Register.AL))
       self.asm.emit (ix.Instruction.create_reg_reg (ix.Code.MOVZX_R64_RM8,
          ix.Register.RAX, ix.Register.AL))

   def code_unary (self, expr, code) :
       self.code_expr (expr.param)
       self.asm.emit (ix.Instruction.create_reg (code, ix.Register.RAX))

   def code_inc_dec (self, target, delta, prefix) :
       """++x / --x / x++ / x-- pro lvalue 'target'.
       prefix=True  vrátí novou hodnotu (po ±1)
       prefix=False vrátí starou hodnotu (před ±1)

       Strategie: spočítej adresu, načti starou hodnotu, ulož starou
       (pro postfix) nebo přepočítej (pro prefix), zapiš novou."""
       addr = self._addr_of (target, ix.Register.RCX)
       if addr is None :
          self._zero_rax ()
          return
       mem = addr.to_mem ()
       # RAX = current value
       self.asm.emit (ix.Instruction.create_reg_mem (ix.Code.MOV_R64_RM64,
          ix.Register.RAX, mem))
       if prefix :
          # ++x / --x: nejdřív uprav, pak ulož; výsledek = nová hodnota
          add_code = ix.Code.ADD_RM64_IMM8 if delta > 0 else ix.Code.SUB_RM64_IMM8
          self.asm.emit (ix.Instruction.create_reg_i32 (add_code,
             ix.Register.RAX, abs (delta)))
          self.asm.emit (ix.Instruction.create_mem_reg (ix.Code.MOV_RM64_R64,
             mem, ix.Register.RAX))
       else :
          # x++ / x--: zachovej starou v RAX, novou spočítej v RDX a ulož
          # (RDX nemůže být součástí mem — addr_of používá RCX jako bázi
          # a RDX jen jako index; po ne-indexExpr cestě je RDX volný,
          # po indexExpr cestě je RDX součástí mem a my bychom ho přepsali.
          # Pro postfix proto použijeme R8 jako temp — ten addr_of nikdy
          # nepoužívá.)
          self.asm.emit (ix.Instruction.create_reg_reg (ix.Code.MOV_R64_RM64,
             ix.Register.R8, ix.Register.RAX))
          add_code = ix.Code.ADD_RM64_IMM8 if delta > 0 else ix.Code.SUB_RM64_IMM8
          self.asm.emit (ix.Instruction.create_reg_i32 (add_code,
             ix.Register.R8, abs (delta)))
          self.asm.emit (ix.Instruction.create_mem_reg (ix.Code.MOV_RM64_R64,
             mem, ix.Register.R8))
          # RAX zůstává se starou hodnotou (pro hodnotu výrazu x++)

   def code_log_not (self, expr) :
       """!x  =  (x == 0)"""
       self.code_expr (expr.param)
       self.asm.emit (ix.Instruction.create_reg_reg (ix.Code.TEST_RM64_R64,
          ix.Register.RAX, ix.Register.RAX))
       self.asm.emit (ix.Instruction.create_reg (ix.Code.SETE_RM8, ix.Register.AL))
       self.asm.emit (ix.Instruction.create_reg_reg (ix.Code.MOVZX_R64_RM8,
          ix.Register.RAX, ix.Register.AL))

   def code_log_and (self, expr) :
       """x && y se short-circuit vyhodnocením."""
       false_lab = self._new_label ('and_false')
       end_lab   = self._new_label ('and_end')
       self.code_expr (expr.left)
       self._test_rax_jz (false_lab)
       self.code_expr (expr.right)
       self._test_rax_jz (false_lab)
       self._mov_imm_rax (1)
       self.asm.jcc (ix.Code.JMP_REL32_64, end_lab)
       self.asm.label (false_lab)
       self._zero_rax ()
       self.asm.label (end_lab)

   def code_log_or (self, expr) :
       """x || y se short-circuit vyhodnocením."""
       true_lab = self._new_label ('or_true')
       end_lab  = self._new_label ('or_end')
       self.code_expr (expr.left)
       self.asm.emit (ix.Instruction.create_reg_reg (ix.Code.TEST_RM64_R64,
          ix.Register.RAX, ix.Register.RAX))
       self.asm.jcc (ix.Code.JNE_REL32_64, true_lab)
       self.code_expr (expr.right)
       self.asm.emit (ix.Instruction.create_reg_reg (ix.Code.TEST_RM64_R64,
          ix.Register.RAX, ix.Register.RAX))
       self.asm.jcc (ix.Code.JNE_REL32_64, true_lab)
       self._zero_rax ()
       self.asm.jcc (ix.Code.JMP_REL32_64, end_lab)
       self.asm.label (true_lab)
       self._mov_imm_rax (1)
       self.asm.label (end_lab)

# ---------------------------------------------------------------------------

# kate: indent-width 1; show-tabs true; replace-tabs true; remove-trailing-spaces all
