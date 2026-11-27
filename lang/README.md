# lang — lexery a malá IDE pro jazykové backendy grm

Soubory v tomto adresáři nejsou součástí buildu boefu. Slouží jako
**běhové lexery** a **ukázky malých IDE** pro parsery, které generuje
`grm/` do jiných jazyků než C++. Zdroj je `/abc/gibbon` (a dva soubory
z `/abc/grm/lang`, viz tabulka); nic se needituje, jen se odsud kopíruje
do projektu, který daný jazyk používá.

## Co generovaný parser od lexeru čeká

Parser z `cparser.py` (C-like backendy) volá:

```
nextToken ()                       // načti další token
token                              // symbol gramatiky (enum)
tokenKind                          // druh tokenu: nameToken, numberToken,
                                   // realToken, charToken, stringToken,
                                   // separatorToken, eofToken
tokenTxt                           // původní text tokenu (s uvozovkami)
processSeparator ()                // po separatoru (víceznakové operátory)
readIdent (), readNumber (), readReal (),
readQuotedCharAsString (), readQuotedString ()
mark () / rewind (pos)             // predikáty (test_*)
testSymbols (table)                // rozhodovací množiny
getTokenFileInx/Line/Col (), error (), stop ()
```

`pparser.py` (Pascal) generuje `Parser = class (TTextInput)` a čeká
`TokenKind`, `TokenText`, `NextToken`, `Mark`, `Rewind`, `ReadIdent`,
`ReadNumber`, `CheckSeparator`, `Error` — tomu odpovídá
`pascal/textio.pas`.

## Inventář

| cesta | zdroj | co to je | stav |
|---|---|---|---|
| `cpp/lexer0/cmm_lexer0.cc,h` | gibbon `src/klanguage/parsing/` | samostatný C++ lexer (jen standardní hlavičky), starší API: `tokenKind`/`tokenText`/`readIdent`/`translate` | použitelné pro starší generátor; současný C++ používá `utils/textio.h` + `envio.h` (EnvInput) |
| `cpp/fltk-view/` | gibbon `other/kit/fltk-view/` | jedno-souborové mini IDE (editor, strom, menu) nad FLTK | build: `make` (fltk-devel 1.3.11; `pkg-config fltk` nic nenajde, správný test je `fltk-config`) |
| `csharp/lexer.cs` | gibbon `other/learn/pw-builder/Builder/Lexer.cs` | kompletní C# lexer (ident, čísla, reálná čísla, znaky, řetězce, komentáře), starší API `token`/`tokenText`/`readIdentifier` | nutná adaptace na `tokenTxt`/`tokenKind`/`readIdent`/`processSeparator` |
| `csharp/view/` | gibbon `other/mix/csharp-view/` | WinForms mini IDE (editor, strom, PropertyGrid, CodeDom); `Parser0` je ruční demo | `mcs` projde bez `Output.cs` a bez generovaných `pas_parser.cs`/`pas_product.cs`; GUI potřebuje X/Mono |
| `java/lexer.java` | gibbon `other/learn/java-gitlab/.../Lexer.java` | minimální Java lexer (ident, číslo, separator) | jen demonstrace, neplnohodnotný lexer pro C-- |
| `java/view/` | gibbon `other/mix/java-view/` | Swing mini IDE (editor, strom, tabulka, překlad přes `javax.tools`) | `javac -d out src/jview/*.java` projde; `build.xml` odkazuje na chybějící `nbproject/build-impl.xml` |
| `js/lexer.js` | gibbon `other/mix/js/lexer.js` | JS lexer se `lookupKeyword`/`processSeparator`, starší API `token`/`tokenText` | nutná adaptace na nové názvy (`tokenTxt`, `readIdent`, …) |
| `js/view/` | gibbon `other/mix/js/jsview.html,jsview.py` | prohlížečové mini IDE (easyui + ACE editor + strom) | `python3 jsview.py -p 1234`, otevřít `http://localhost:1234/jsview.html`; CDN závislosti |
| `pascal/textio.pas` | gibbon `other/mix/pas-parser/` | **kompletní Pascal lexer** pro `pparser.py`/`pproduct.py`: `TokenKind`, `TokenText`, `NextToken`, `Mark`/`Rewind`, `ReadIdent`, `ReadNumber`, `CheckSeparator` | přímo použitelné s `Parser = class (TTextInput)`; `pparser` zatím generuje `string_pole := nil` (FPC: nekompatibilní typ) |
| `pascal/binio.pas` | **`/abc/grm/lang/pascal/`** (ne gibbon) | binární I/O, na kterém `textio.pas` stojí | gibbon verze nešla přeložit (`adr^` nad `Pointer`, `PChar` u ShortString); tato FPC verze projde |
| `pascal/main.pas`, `makefile`, `translate.sh` | tamtéž | kostra programu a build pro `pas_parser`/`pas_product` | cesty v `makefile`/`translate.sh` míří na gibbon `view/`; upravit na `../../../grm` a `../../pas.g` |
| `pascal/view/` | gibbon `other/mix/pascal-view/` | Lazarus mini IDE | `lexerunit.pas` je jen stub (prázdné metody); pro lexer použít `../textio.pas` |
| `rust/lexer.rs` | gibbon `other/mix/rust/` | kostra Rust lexeru (`readIdentifier`/`readNumber` vrací `""`) | **nepoužitelné** bez doplnění; `example.rs`, `example2.rs` jsou ukázky vstupu |
| `vala/lexer.vala` | gibbon `other/mix/vala-view/` | Vala lexer, starší API (`tokenKind` jako int, `tokenText`, `readIdentifier`) | nutná adaptace na `tokenTxt`/`TokenKind`/`translate` |
| `vala/textio.vala` | **`/abc/grm/lang/vala/`** (ne gibbon) | současný Vala lexer: `TokenKind`, `tokenTxt`, `translate`, `mark`/`rewind` | **přímo použitelné** s `cparser.py --vala` |
| `vala/view/` | gibbon `other/mix/vala-view/`, upraveno | GTK3 mini IDE; původní `Gtk.SourceView` nahrazen `Gtk.TextView` (gtksourceview3 tady není), přidána akce **Parse Pascal** | `make` vygeneruje `pas_parser.vala`/`pas_product.vala` z `lang/pas.g` a přeloží; `make run` spustí GUI |
| `pas.g` | gibbon `view/pas/pas.g` | ukázková gramatika Pascal (menší než `/abc/grm/tests/grammar/pas.g`) | pro rychlé vyzkoušení všech backendů |

`python/` se nekopíruje — kompletní PyQt5 view už je přímo v `/abc/grm/view/`.

## Současné (kompatibilní) runtimes

| jazyk | runtime | poznámka |
|---|---|---|
| C++ | `/abc/boef/utils/textio.h` + `envio.h` (`EnvInput`) | přímo v boefu, nic se nekopíruje |
| Python | `/abc/boef/code/lexer.py` | přímo v boefu |
| Vala | `lang/vala/textio.vala` | z `/abc/grm/lang/vala`, aktuální API; `lang/vala/view` je nad ním postavené mini IDE s akcí Parse Pascal |
| Pascal | `lang/pascal/textio.pas` + `binio.pas` | `textio` z gibbonu, `binio` z `/abc/grm/lang`; `pparser`/`pproduct` rodina |

Pro C#, Java, JS a Rust se v gibbonu **nenašel** lexer s aktuálním API —
jen starší generace (`token`/`tokenText`, `readIdentifier`), která se musí
přejmenovat a doplnit (`processSeparator`, `translate`, `mark`/`rewind`,
rozhodovací tabulky). Projekty `java-view` a `csharp-view` jsou použitelné
jako malá IDE samy o sobě; generovaný parser v nich ale není zapojený.

## Vala: parser + view

Ověřeno, že generovaný Vala parser z `lang/pas.g` funguje s `vala/textio.vala`:

```sh
cd lang/vala/view
make                     # vygeneruje parser/product a přeloží view
timeout 3 ./vala-view.bin  # rc=124 => GUI běží (Gtk.main)
```

`Parse Pascal` v menu vezme text z editoru, zavolá `Parser.openString /
nextToken / parse_module_decl` a výsledek produktu vypíše na kartu
`Parser output`. Pro `program Demo; begin end.` je výstup
`programDemo;beginend.` (stejný jako `pas_program.expected`).

## Ověření při kopírování (2026-11-27)

```
javac -d /tmp/jview-out lang/java/view/src/jview/*.java        # rc=0
mcs -r:System.Windows.Forms -r:System.Drawing \
    lang/csharp/view/{Lexer,Parser,MainWindow,MainWindow.Designer,Program}.cs \
    lang/csharp/view/Properties/AssemblyInfo.cs                # rc=0 (bez Output.cs)
valac -C lang/vala/textio.vala                                 # rc=0 (2 warningy)
cd lang/pascal && fpc -Fu. -Mdelphiunicode textio.pas          # rc=0 (27 warningů)
fpc -Fu. -Mdelphiunicode pas_parser.pas                        # pparser: nil u string pole
cd lang/cpp/fltk-view && make                                  # rc=0 (fltk-view.bin)
cd lang/vala/view && make && timeout 3 ./vala-view.bin         # rc=0 / 124 (GUI běží)
node --check lang/js/lexer.js                                  # rc=0
rustc --crate-type lib --edition 2015 lang/rust/lexer.rs       # rc=0 (jen kostra)
pkg-config --modversion gtksourceview-3.0                      # chybí
```
