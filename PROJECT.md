# Projekt — přehled (interní poznámka)

Soubor popisuje, jak spolu v tomto stromu souvisí jednotlivé podprojekty.
Externí dokumentace pro uživatele je v `README.md` a `docs/`; tento soubor
slouží jako orientační mapa projektu.

## Podprojekty

### grm — generátor parserů (jádro projektu)

- Adresář `grm/` — napsaný v Pythonu. Gramatika se zapisuje v EBNF-like
  notaci s atributy (např. `cmm/cmm.g`, `lang/pascal/pas.g`).
- Nástroje: `grammar.py` (model gramatiky), `toparser.py` (generování
  rekurzivního sestupu), `cparser.py`, `pparser.py` (generátory pro C a
  Pascal), `toproduct.py`/`cproduct.py`/`pproduct.py` (produkty),
  `tohtml.py`, `tolout.py` (výstupy dokumentace), `recognize.py`
  (testování rozpoznávání), `symbols.py`.
- Jazyky, pro které se generují parsery: Python, C, Pascal (a dále
  např. Vala — viz `lang/`).
- Spouští se z adresáře `grm/` (viz README).

### cmm — překladač jazyka C-- (hlavní aplikační příklad)

- Adresář `cmm/`. Vstupní gramatika je `cmm/cmm.g` — z ní grm generuje
  parser (`cmm_parser.py`) a produkt (`cmm_product.py`).
- Překladač: `cmm_compile.py` / `cmm_comp.py`, backendy `cmm_iced.py`
  (JIT/exekuce přes iced-x86) a `cmm_llvm.py` (LLVM).
- Podpůrné moduly jsou ve `code/` (sdílené s view; původem z projektu
  simple-view). Pozor: kopie modulů přímo v `cmm/` nejsou referencí,
  referencí je `code/` (viz poznámka v README a MEMORY).
- Příklady programů v C--: `tests/examples/`, další v `cmm/examples/`.
- Tento projekt se odlišuje právě cmm napsaným v Pythonu — cmm vzniklo
  jako jeden z prvních experimentů s AI, již v květnu 2026.

### view — malé IDE (PyQt5)

- Adresář `view/` — GUI prostředí simple-view: editace souborů
  (`edit.py`, `complete.py`, `goto.py`, `grep.py`, `lookup.py`),
  strom projektu (`tree.py`), okno (`window.py`), nástroje
  (`tools.py`, `tools.ini`).
- Do view je zapojen cmm (překlad a spouštění C-- přímo z IDE) a
  Grammar menu (`gram_plugin.py`) — z něj se spouští generování
  parserů (např. „to Pascal Parser“, „to Vala Parser“).
- Příklady GUI pro Examples menu: `tests/t-examples/` (`.t` soubory),
  ukázkové gramatiky/rozpoznávače: `set/` (`.t` pro JSON, XML, textio —
  ve variantách `.py`, `.cpp`).

### cmini — překladač CMini pro soubory `.cc` / `.h`

- Externí projekt `/abc/cmini` (pravidla viz `/abc/cmini/ZASADY.md`).
- Soubory `.cc` (a `.h`) v našich projektech se mají dát přeložit
  pomocí cmini — nezávislost na plném C++. CMini je jednoduché C
  s třídami; `.cc` jsou zdrojové, ne generované soubory.
- V grm/cmm/view se `.cc` objevují např. jako výstupy generátorů
  (generovaný parser/produkt ve variantě C) a jako testovací vstupy.

## Dokumentace

- `wiki/` — původní česká wiki dokumentace ke grm (zdroj).
- `docs/` — přeložená (anglická) verze, generovaná do PDF přes
  `md2lout.py` + Lout (viz docs/README.md). Pokyny k úpravám:
  editovat `wiki/` i `docs/`, PDF se skládá z modulů v `docs/`.

## Vztahy v jedné větě

`grm` čte gramatiky (`.g`) a generuje parsery/produkty (`.py`, C/Pascal/
Vala) → `cmm` je ukázkový zákazník grm (překladač C-- postavený na
`cmm.g`) → `view` je IDE, které cmm i grm ovládá z GUI → soubory `.cc`
produkované projektem se překládají externím `cmini` (`/abc/cmini`).

## Další související adresáře

- `lang/` — gramatiky jiných jazyků (js, pascal, rust, vala).
- `tests/` — testy (`test_parsers.py` end-to-end spouští vygenerované
  parsery; `test_llvm.py`, `test_set.py`, `test_t_examples.py`).
- `code/` — sdílené moduly (lexer, textio, generování kódu).
