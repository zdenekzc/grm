# GRM backendy — zjištění a převzaté soubory

Interní poznámka ze 2026-11-27. Shrnuje srovnání Python generátorů
s `/abc/grm`, průzkum `/abc/gibbon` a co z něj bylo převzato do `lang/`.
Plán oprav je v `PLAN.md` (úkol 7), inventář `lang/` v `lang/README.md`.
Srovnání obou generátorových větví (`gram` v C++ vs `grm` v Pythonu)
a jejich rozhraní parser/lexer je v `GRAM_VS_GRM.md`.

## 1. Python `toparser` / `toproduct` vs `/abc/grm`

Ověřeno, že Python cesta v `/abc/grm/cmm` funguje:

```sh
cd /abc/grm/cmm
python3 cmm_compile.py ../tests/parsers/cmm_min.cc
# -> C++ i Python kód zapsán, rc=0
```

Vygenerované soubory v `/abc/grm/cmm` (`cmm_parser.py` 139 KB,
`cmm_product.py` 38 KB) jsou z tamějšího (staršího) `cmm.g`.

### Původní srovnání souborů

| soubor | boef vs `/abc/grm/grm/` |
|---|---|
| `toproduct.py` | původně **bajtově shodný** (sha256 `1e5a5924…`) |
| `toparser.py` | 11 změnových řádků; upstream má novější opravu deklarace metod bez parametru (`m.no_param`, výjimka `predicate_on_choose`) |
| `cparser.py` | 413 změnových řádků; boef má navíc `--members`, `--parser-members`, `--namespace-open/close` a novější opravy |
| `cproduct.py` | 163 změnových řádků; boef má nullable catch-all, stejný typ select alternativy, postfixové uzly, `virtual` send funkce, primitiva přes `send_*` |
| `cmm.g` | 1228 změnových řádků; boef je výrazně novější |

### Původní chyba

`toparser.py` na boef `cmm.g` fungoval (rc=0). `toproduct.py` (shodný
s upstreamem) selhával:

```
/abc/boef/cmm/cmm.g:1357:4: error: Cannot find condition
(rule: reference_declarator), tokenText=
```

Příčina: `reference_declarator` měl

```
( '&' | "&&" <set a_rvalue = true> )
```

Alternativa s holým `'&'` nemá v AST pole, podle kterého by produkt poznal,
že nastala. Upstream `cmm.g` má jen `'&'`, proto tam produkt projde.

### Oprava (2026-11-27)

**Pravidlo gramatiky:** každá alternativa, která neobsahuje pojmenovaný
neterminál (`name:some_rule`), musí mít `<set ...>`, aby produkt měl podle
čeho rozhodnout. Aplikováno na `reference_declarator`:

```
( '&' <set a_rvalue = true> | "&&" <set a_rrvalue = true> )
```

Tím zmizela první chyba a C++ produkt navíc začal pro `'&'` skutečně
vypisovat `&` (dřív generoval `if (false) { send ("&"); }`).

**`toproduct.py` — převzato z `cproduct.py`:**

1. `codeStore`: iteruje `rule.store_orig` (u rewrite group může být prázdné;
   původní `rule.store_orig [0]` končil `IndexError`).
2. `codeSelect`: alternativa stejného typu jako select (`flexible_stat`
   s typem `CmmItem`) jde na konec; přidán `catch_all_alt` a v
   `codeSimpleSelection` se poslední taková alternativa vypíše jako `else`.
3. CLI `--parser MODULE`: produkt vypíše `from MODULE import *`, takže má
   enum konstanty a třídy uzlů (dřív je měl jen produkt generovaný z IDE).

### Výsledek

```sh
cd grm
python3 toparser.py  ../cmm/cmm.g -o /tmp/pybackend/cmm_parser.py
python3 toproduct.py --parser cmm_parser ../cmm/cmm.g \
        -o /tmp/pybackend/cmm_product.py
# + code/lexer.py, input.py, output.py a main.py (Parser/Product)
python3 main.py /abc/grm/tests/parsers/cmm_min.cc
```

Výstup je správný:

```
int N;
int a [N];
int t;
void swap (int & r, int & s)
{
}
void quicksort (int r, int s)
{
}
int main ()
{
}
```

Stejně pro `pas.g` a `tests/parsers/pas_program.pas` (`parse_module_decl`).

Omezení zůstává stejné jako upstream: holý parser má sémantické predikáty
(`is_expression`, …) jen jako stuby vracející `False`, takže programy se
příkazy (např. `cmm_quicksort.cc`) potřebují reálné predikáty z kompilátoru.

`toparser.py` stále není srovnaný s upstreamem v jednom hunku (deklarace
metod bez parametru); na generování boef `cmm.g` to nemá vliv.

## 2. Vala: generovaný parser a view

Vala je první jazyk mimo C++, kde se parser podařilo rozchodit i s view.

### Opravy generátorů

- `cparser.py`: `old_lists`, `old_aux`, `old_conv` a `sequence_lists` se
  uplatní jen pro C++ (`and self.cpp`). Boef je přidal kvůli cecku a cmm
  (`Sequence<T*>`, intruzivní seznamy, `properties`/`subitems`, stará jména
  `toXxx`), ale do Vala/C#/Java/… generovaly neplatný kód (`PropertyIfc`,
  `TreeIfc`, `Sequence`, `nullptr`).
- `cproduct.py`: `multiterminalFunctions()` se volá i v jednosouborových
  backendech (C#, Java, Pascal, JS, Vala, Rust). Boef změnil
  `productFromTerminal` na `send_<primitiva>` (identifier, number, …), ale
  implementace `send_identifier` aj. vznikaly jen v C++ `productCode`.
- `lang/pas.g` (z gibbonu) deklaruje `< struct CmmBasic >`, takže Vala
  nepotřebuje stub bázové třídy.

### Parser

```sh
cd lang/vala/view
make          # vygeneruje pas_parser.vala/pas_product.vala a přeloží view
```

Ověřeno i bez GUI: `Parser.openString`, `nextToken`, `parse_module_decl`
a `Product.send_module_decl` na `program Demo; begin end.` dají
`programDemo;beginend.` — přesně `pas_program.expected`.

### View

Původní gibbon `vala-view` používal `Gtk.SourceView` (gtksourceview3),
který v tomto prostředí není. Portováno na `Gtk.TextView`; navíc má akci
**Parse Pascal**, která text z editoru předá vygenerovanému parseru a
výsledek produktu vypíše na kartu `Parser output`.

```sh
cd lang/vala/view && make
timeout 3 ./vala-view.bin      # rc=124 => Gtk.main běží
```

## 3. Průzkum `/abc/gibbon`

Hledány byly lexery použitelné s generovanými parsery a malá IDE.
Rozhodující je API: aktuální `cparser.py` chce `token`, `tokenKind`
(`nameToken`, `numberToken`, …), `tokenTxt`, `processSeparator`,
`readIdent`, `readNumber`, `readReal`, `readQuotedCharAsString`,
`readQuotedString`, `mark`/`rewind`, `testSymbols`, `getTokenFileInx/Line/Col`.
`pparser.py` chce `TTextInput` s `TokenKind`, `TokenText`, `NextToken`,
`Mark`, `Rewind`, `ReadIdent`, `CheckSeparator`.

### Přímo použitelné

- `other/mix/pas-parser/textio.pas` — kompletní Pascal lexer pro
  `pparser.py`/`pproduct.py` (`Parser = class (TTextInput)`).
  Gibbon `binio.pas` se ale nepřeloží (`adr^` nad `Pointer`, `PChar`
  u ShortString); použit byl FPC opravený `/abc/grm/lang/pascal/binio.pas`.
  Kombinace `textio.pas` + tento `binio.pas` projde `fpc` (rc=0).
- `other/mix/java-view/` — Swing mini IDE; `javac -d out src/jview/*.java`
  projde (rc=0). `build.xml` odkazuje na chybějící `nbproject/build-impl.xml`.
- `other/mix/csharp-view/` — WinForms mini IDE; `mcs` projde bez `Output.cs`
  (rc=0). `Output.cs` duplikuje třídu `Output` z `Lexer.cs`; csproj ho
  neobsahuje.
- `other/mix/vala-view/` — GTK3 + gtksourceview3 mini IDE; `gtksourceview3-devel`
  v tomto prostředí chybí.
- `other/mix/pascal-view/` — Lazarus mini IDE; `lexerunit.pas` je jen stub
  (prázdné metody), pro lexer je třeba `pas-parser/textio.pas`.
- `other/mix/js/jsview.html` + `jsview.py` — prohlížečové mini IDE
  (easyui + ACE, CDN závislosti); `python3 jsview.py -p 1234`.
- `other/kit/fltk-view/` — jedno-souborové C++/FLTK mini IDE; `fltk-devel`
  je nainstalované, `fltk-config --version` = 1.3.11 a `make` projde (rc=0).
  Pozor: `pkg-config fltk` nic nenajde, správný test je `fltk-config`.
- `other/python/edit-mini/` — PyQt5 mini IDE; import projde, GUI chce X.
- `other/mix/vala-view/lexer.vala` — starší API, ale kompletní Vala lexer.
- `src/klanguage/parsing/cmm_lexer0.cc,h` — samostatný C++ lexer
  (jen standardní hlavičky), starší API.

### Starší API — nutná adaptace

- `other/learn/pw-builder/Builder/Lexer.cs` — kompletní C# lexer
  (`token`/`tokenText`/`readIdentifier`).
- `other/mix/js/lexer.js` — JS lexer s `lookupKeyword`/`processSeparator`,
  starší názvy.
- `other/mix/vala-view/lexer.vala` — `tokenKind` jako int, `tokenText`,
  `readIdentifier`.
- `src/klanguage/parsing/cmm_lexer0.*` — `tokenKind`/`tokenText`/`readIdent`.
- `other/mix/rust/lexer.rs` — jen kostra (`readIdentifier` vrací `""`);
  přeloží se, ale lexer nedělá nic.

### Nepoužitelné

- `other/pascal/cpp_c/` — C front-end pro DOS (`<alloc.h>`, `<mem.h>`).
- `pascal-view/lexerunit.pas` — prázdný stub.
- Java lexery v gibbonu jsou stuby nebo pro jiný projekt; jediný rozumný
  je minimální `other/learn/java-gitlab/.../Lexer.java`.

## 4. Co bylo převzato do `lang/`

Celkem 91 souborů, 1,3 MB. Struktura a stav:

| adresář | obsah | stav |
|---|---|---|
| `lang/cpp/` | `fltk-view/` (FLTK IDE), `lexer0/` (starší C++ lexer) | C++ runtime v boefu je `utils/textio.h` + `envio.h` |
| `lang/csharp/` | `lexer.cs`, `view/` (WinForms) | lexer starší API; IDE projde `mcs` |
| `lang/java/` | `lexer.java` (minimální), `view/` (Swing) | IDE projde `javac` |
| `lang/js/` | `lexer.js`, `view/` (jsview) | lexer starší API; IDE v prohlížeči |
| `lang/pascal/` | `textio.pas` + `binio.pas` (pparser runtime), `main.pas`, `makefile`, `translate.sh`, `view/` (Lazarus) | runtime projde `fpc`; `pparser` má chybu `string_pole := nil` |
| `lang/python/` | `edit-mini/` (PyQt5) | import projde |
| `lang/rust/` | `lexer.rs` (kostra), `example*.rs` | kostra, nepoužitelné bez doplnění |
| `lang/vala/` | `lexer.vala` (starší API), `textio.vala` (aktuální API z `/abc/grm/lang`), `view/` | `textio.vala` projde `valac -C` |
| `lang/pas.g` | ukázková gramatika z gibbonu | pro zkoušení backendů |

Pro C#, Java, JS a Rust se v gibbonu **nenašel** lexer s aktuálním API.
Projekty `*‑view` jsou použitelné jako malá IDE samy o sobě, ale generovaný
parser v nich není zapojený.

## 5. Ověřovací příkazy

```sh
javac -d /tmp/jview-out lang/java/view/src/jview/*.java        # rc=0
mcs -r:System.Windows.Forms -r:System.Drawing \
    lang/csharp/view/{Lexer,Parser,MainWindow,MainWindow.Designer,Program}.cs \
    lang/csharp/view/Properties/AssemblyInfo.cs                # rc=0 (bez Output.cs)
valac -C lang/vala/textio.vala                                 # rc=0 (2 warningy)
cd lang/vala/view && make                                      # rc=0 (parser + view)
cd lang/vala/view && timeout 3 ./vala-view.bin                 # rc=124 (GUI běží)
cd lang/pascal && fpc -Fu. -Mdelphiunicode textio.pas          # rc=0 (27 warningů)
cd lang/cpp/fltk-view && make                                  # rc=0, fltk-view.bin
cd lang/python/edit-mini && python3 -c "import view"           # rc=0
node --check lang/js/lexer.js                                  # rc=0
rustc --crate-type lib --edition 2015 lang/rust/lexer.rs       # rc=0 (jen kostra)
pkg-config --modversion gtksourceview-3.0                      # chybí (view už ho nepotřebuje)
```

## 6. Další kroky

Viz `PLAN.md`, úkol 7:

1. přenést jeden hunk z `/abc/grm/grm/toparser.py` (metody bez parametru);
2. rozhodnout, zda adaptovat starší lexery (C#, Java, JS, Rust)
   na aktuální API, nebo je nechat jen jako referenci;
3. doladit cesty v ostatních převzatých `translate.sh`/`makefile` a
   `pparser` opravit `string_pole := nil`.

Hotovo: grammar pravidlo pro `<set>` u alternativ bez `name:rule`,
`toproduct.py` (store_orig, catch-all select, `--parser`), ověření Python
backendu na `cmm.g` i `pas.g`, Vala parser + `lang/vala/view`, gating
C++-specifických voleb v `cparser.py` a `multiterminalFunctions` v
jednosouborových produktech; FLTK mini IDE se buildí.
