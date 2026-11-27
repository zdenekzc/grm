# Dvě větve generátoru: `gram` (C++) vs `grm` (Python)

Interní srovnání pro projekty `/abc/cecko/cmm` a `/abc/boef/cmm`
(2026-11-27). Cílem je přehledně oddělit, co dělá generátor, co dělá
lexer a kde se obě větve liší v rozhraní.

## 1. Rychlá mapa

| | `gram` | `grm` |
|---|---|---|
| jazyk generátoru | C++ (podmnožina CMini) | Python 3 |
| kde | `/abc/cecko/gram` (a `/abc/gibbon/src/gram`) | `/abc/boef/grm` (a `/abc/grm/grm`) |
| podpůrné moduly | `gram/utils`: `textio`, `envio`, `conv`, `str`, `inf`, … | `code/`: `lexer.py`, `input.py`, `output.py`, `code_output.py`, … |
| dokumentace | `/abc/cecko/gram/README.txt`, `/abc/cecko/README.txt` | `/abc/grm/wiki`, `/abc/grm/docs` |
| kdo používá | cecko, gibbon (`src/gram`), historicky první verze | boef, `/abc/grm`, další projekty |
| výstup pro cmm | `cmm_lexer.*`, `cmm_parser.*`, `cmm_data.*`, `cmm_product.*`, `cmm_description.tpp` | `cmm_parser.*` (AST + parser), `cmm_product.*`; lexer je ruční `EnvInput` |
| lexer | generovaný `CmmLexer : EnvInput` | ruční `EnvInput : TextInput`, parser ho dědí |
| gramatika | `options { … }`, `extension { … }`, `<primitive>` pravidla | direktivy `< header >`, `< struct >`, CLI volby; primitiva vestavěná |

Obě větve používají **stejný běhový lexer** `textio`/`envio`: v boefu
`utils/textio.*` a `utils/envio.*` jsou bajtově shodné s
`/abc/cecko/gram/textio.*` a `envio.*` (ověřeno sha256):

```
textio.h   1b366c4e…   textio.cc  54ce5b32…
envio.h    411a27c8…   envio.cc   615c0f33…
```

Rozdíly tedy nejsou v implementaci lexeru, ale v tom, **co generátor
vygeneruje a jak se napojí na lexer**.

## 2. Jak se generuje v cecko/cmm

`/abc/cecko/cmm/Makefile`:

```make
GRAM = $(top_srcdir)/gram/gram-gpp.bin
cmm_PRODUCTS = cmm_lexer.hpp cmm_lexer.cpp cmm_parser.hpp cmm_parser.cpp \
               cmm_data.hpp cmm_data.cpp cmm_product.hpp cmm_product.cpp \
               cmm_description.tpp

$(BUILD)/cmm-gram.stamp: cmm.g $(GRAM)
	$(GRAM) input_dir=. output_dir=. cmm.g
```

Jména souborů a tříd jsou v `cmm.g` v bloku `options { … }`:

```
common_header = cmm_data;   common_name = cmm_data;
lexer_name = cmm_lexer;     lexer_class = CmmLexer;
lexer_super_class = EnvInput;
parser_name = cmm_parser;   parser_class = CmmParser;
product_name = cmm_product; product_class = CmmProduct;
product_super_class = TextOutput;
with_stack = true;
rule_prefix = parse_;
conv_func_prefix = to;      conv_func_remove = Cmm;
tag_remove = Cmm;           tag_suffix = _Kind;
```

Vygenerované soubory (ověřeno spuštěním `gram-gpp.bin` do `/tmp/cecko_gen`):

- `cmm_lexer.hpp/.cpp` — `class CmmLexer : public EnvInput`,
  `static const int NONE/IDENT/NUMBER/…/KEYWORD_*`,
  `conv(int)`, `delimiter()`, `keyword(string)`, `storeLocation(CmmBasic*)`,
  `virtual translate()`.
- `cmm_parser.hpp/.cpp` — `class CmmParser : public CmmLexer`,
  `Sequence<CmmBasic*> stack`, `stack_push/pop`, metody `parse_*`.
- `cmm_data.hpp/.cpp` — AST třídy, enum `CmmBasic_kind`, konverze `toBasic_kind`.
- `cmm_product.hpp/.cpp`, `cmm_description.tpp`.

Něco zůstává ručně:

- `CmmLexer::translate()` a `CmmLexer::storeLocation()` jsou v
  `/abc/cecko/cmm/comp.cc:39-90` (nikoli v generovaném `cmm_lexer.cpp`).
- `translate()` pracuje s **zděděným** `symbol` z `TextInput`:

```cpp
void CmmLexer::translate ()
{
   switch (tokenKind)
   {
      case nameToken:   symbol = keyword (tokenTxt); ... break;
      case numberToken: symbol = NUMBER; break;
      ...
      case separatorToken: symbol = delimiter (); ... break;
   }
}
```

- `with_stack = true` vygeneruje do `CmmParser` pole `stack` a
  `stack_push/stack_pop`; generované `parse_*` je používají.

## 3. Jak se generuje v boef/cmm

`/abc/boef/cmm/Makefile`:

```make
GRM_DIR = $(top_srcdir)/grm

$(BUILD)/cmm-grammar.stamp: $(GRAMMAR_DEPS)
	cd $(GRM_DIR) && python3 cparser.py --cpp --lexer envio.h \
	   --lexer-class EnvInput --class CmmParser --lexer-alias CmmLexer \
	   --namespace-open OPEN_NAMESPACE --namespace-close CLOSE_NAMESPACE \
	   --members ../cmm/cmm_members \
	   --parser-members ../cmm/cmm_members/CmmParser.inc \
	   --header ../cmm/cmm_parser.hpp --code ../cmm/cmm_parser.cpp ../cmm/cmm.g

	cd $(GRM_DIR) && python3 cproduct.py --cpp --class CmmProduct \
	   --super TextOutput --parser cmm_parser.hpp \
	   --namespace-open OPEN_NAMESPACE --namespace-close CLOSE_NAMESPACE \
	   --members ../cmm/cmm_members \
	   --header ../cmm/cmm_product.hpp --code ../cmm/cmm_product.cpp ../cmm/cmm.g
```

Vygenerované soubory:

- `cmm_parser.hpp/.cpp` — **AST třídy i parser** v jednom;
  `class CmmParser : public EnvInput`, `CmmSymbol token`,
  `translate()`, `lookupKeyword()`, `processSeparator()`,
  `isSymbol/checkSymbol/testSymbols/stop`, `storeLocation`, `parse_*`.
- `cmm_product.hpp/.cpp` — `CmmProduct : TextOutput`.
- **Negeneruje se lexer**; lexer je ruční `EnvInput` z `utils/envio.h`
  (a `TextInput` z `utils/textio.h`).
- `cmm_data.hpp` v boefu **není** (generuje ho až `gram` v cecku).

Doplňky, které cecko nezná:

- `--members DIR` — `#include` ručních `<Třída>.inc` do generovaných tříd.
- `--parser-members FILE` — ruční členy třídy parseru (`CmmParser.inc`).
- `--lexer-alias CmmLexer` — `typedef CmmParser CmmLexer;` (řádek 1239
  `cmm_parser.hpp`).
- `--namespace-open/close` — makra `OPEN_NAMESPACE`/`CLOSE_NAMESPACE`.

## 4. Rozhraní parser ↔ lexer

### cecko

```
CmmParser : CmmLexer : EnvInput : TextInput
```

- `symbol` je skutečné pole `InputSymbol` v `TextInput`; `translate()` ho
  nastavuje.
- `isSymbol`, `testSymbols`, `checkSymbol`, `stop`, `mark`, `rewind`
  dědí parser z `EnvInput`.
- `readIdent`, `readNumber`, `readReal`, `readQuotedCharAsString`,
  `readQuotedString` dědí z `TextInput`.
- `storeLocation` a `translate` jsou ruční metody `CmmLexer`
  (`comp.cc`), zbytek (keyword/delimiter tabulky) generuje `gram`.
- `stack` je generovaný v parseru (`with_stack = true`).

### boef

```
CmmParser : EnvInput : TextInput
typedef CmmParser CmmLexer;          // --lexer-alias
```

- Parser má vlastní `CmmSymbol token`; `translate()` mapuje `tokenKind`
  na `token`, `lookupKeyword()` a `processSeparator()` jsou generované.
- `isSymbol/checkSymbol/testSymbols/stop` jsou generované v `CmmParser`
  a pracují s `CmmSymbol token`.
- `symbol` je v `CmmParser.inc` **reference alias**:

```cpp
CmmSymbol & symbol = token;   // stare jmeno pro token
static constexpr CmmSymbol IDENT = identifier;
...
```

- `readIdent` je v `CmmParser.inc` přepsané, protože
  `TextInput::readIdent` testuje zděděný `symbol`, kdežto grm nastavuje
  `token`:

```cpp
string readIdent ()
{
   if (token != identifier) error ("Identifier expected");
   string result = tokenTxt;
   nextToken ();
   return result;
}
```

- `stack` se negeneruje (`grm` `with_stack` neumí); zdroje mají
  `#ifndef PYTHON_GRM` (`comp.cc:2440`).

### Tabulka rozdílů

| věc | cecko (`gram`) | boef (`grm`) |
|---|---|---|
| třída lexeru | generovaná `CmmLexer : EnvInput` | ruční `EnvInput`; `CmmLexer` je `typedef` |
| třída parseru | `CmmParser : CmmLexer` | `CmmParser : EnvInput` |
| nositel symbolu | `InputSymbol symbol` v `TextInput` | `CmmSymbol token` v parseru |
| staré jméno | `symbol` (skutečné pole) | `CmmSymbol & symbol = token` v `.inc` |
| konstanty symbolů | `static const int` v `CmmLexer` | `enum CmmSymbol` + `static constexpr` v `.inc` |
| `translate/lookupKeyword/processSeparator` | `translate` ruční v `comp.cc`, keyword/delimiter generované v `CmmLexer` | vše generované v `CmmParser` |
| `isSymbol/checkSymbol/testSymbols` | zděděné z `EnvInput` | generované v `CmmParser` |
| `readIdent` | zděděné `TextInput::readIdent` (testuje `symbol`) | přepsané v `CmmParser.inc` (testuje `token`) |
| AST/data | `cmm_data.hpp/.cpp` zvlášť | součást `cmm_parser.hpp/.cpp` |
| `stack` | generovaný (`with_stack = true`) | negenerovaný, `#ifndef PYTHON_GRM` |
| `cmm_description.tpp` | generovaný | negenerovaný |

## 5. `tokenTxt` a `tokenVal` (literály)

`textio` je v obou větvích stejný a má obě položky:

```cpp
string tokenTxt; // original token
string tokenVal; // value of string
char   tokenSym; // value of separator
```

Semantika (`utils/textio.cc` / `cecko/gram/textio.cc`, řádky 1912–1913,
1942–1943, 2409–2434):

- `tokenTxt` — text tak, jak je na vstupu: u znakového/řetězcového
  literálu **včetně uvozovek a escape sekvencí**.
- `tokenVal` — skutečná hodnota uvnitř literálu: **bez uvozovek a s
  dekódovanými escape sekvencemi**.
- `readIdent/readNumber/readReal` vracejí `tokenTxt`.
- `readChar/readString` vracejí `tokenVal` (dekódovanou hodnotu).
- `readQuotedCharAsString/readQuotedString` vracejí `tokenTxt`
  (s uvozovkami a escape sekvencemi).

V obou `cmm.g` je pro C-- zvolena varianta **s uvozovkami**:

- cecko `cmm.g:778-791`:

```
identifier <primitive> <identifier> : <symbol IDENT> <function readIdent>;
number <primitive>:                  <symbol NUMBER> <function readNumber>;
real_number <primitive>:             <symbol REAL_NUMBER> <function readReal>;
character_literal <primitive>:       <symbol CHAR_LITERAL> <function readQuotedCharAsString>;
string_literal <primitive>:          <symbol STRING_LITERAL> <function readQuotedString>;
```

- boef `cmm.g` primitiva neobsahuje; `grm/cparser.py` je má vestavěná a
  `parserFromTerminal` mapuje `character_literal` na
  `readQuotedCharAsString`, `string_literal` na `readQuotedString`.

Důsledek: **C-- AST v obou C++ variantách dostane literál s uvozovkami**
(např. `'\n'`, `"abc"`), ne dekódovanou hodnotu. `tokenVal` je v obou
případech k dispozici v lexeru (a v ručně psaných `execute` metodách),
ale generovaný parser ho pro C-- nepoužívá.

Rozdíl v možnostech generátoru:

- `gram` dovoluje u každého primitiva zvolit jinou funkci
  (`readChar`, `readString`, vlastní `<function …>`), takže gramatika
  může snadno přejít na dekódované hodnoty.
- `grm` má primitiva vestavěná a mapování `readQuoted*` je pevné
  v `cparser.py`; změna by znamenala zásah do generátoru (nebo
  doplnění vlastní `<execute>` metody).

Pozor na **Python backend** (`toparser.py` + `code/lexer.py`): ten mapuje
`character_literal`/`string_literal` na `readCharacter`/`readString`.
V `code/lexer.py` je `tokenText` už **dekódovaný** (bez uvozovek) a
`tokenValue` je naopak zpětně ocitovaný (`quoteString`). Pythonem
generovaný parser tedy dostane jinou podobu literálu než C++ parser
ze stejné gramatiky.

## 6. `PYTHON_GRM` a kompatibilita zdrojů

Boef kompiluje s `-DPYTHON_GRM` (`boef-makefiles.py`). Větve v kódu
vybírají mezi rozhraními:

| | cecko (bez `PYTHON_GRM`) | boef (`PYTHON_GRM`) |
|---|---|---|
| hlavička AST/parseru | `cmm_data.hpp` | `cmm_parser.hpp` |
| enum kind | `CmmBasic_kind` | `CmmBasicKind` |
| přístup | `CmmMemberVisibility_access` | `CmmMemberVisibilityAccess` |
| konverze kind | `toBasic_kind` | `toCmmBasicKind` |
| `derived_from` | běžná funkce | `#define derived_from cls_derived_from` (C++20 `std::derived_from`) |
| `stack` | generovaný `stack`/`stack_push`/`stack_pop` | negenerovaný, kód pod `#ifndef PYTHON_GRM` |

Příklady: `comp.h:7-20`, `c2cpp.h:12-17`, `instr-asm.h:8-25`,
`basic.cc:31-34`, `comp.cc:2440`.

## 7. Co si pamatovat při přenosu mezi větvemi

1. **Název symbolu**: cecko `symbol`, boef `token` (+ alias `symbol`).
2. **Kdo vlastní translate**: cecko `CmmLexer`, boef `CmmParser`.
3. **Matching metody**: cecko z `EnvInput`, boef generované v parseru.
4. **`readIdent`**: cecko `TextInput` testuje `symbol`; boef má vlastní
   přepsání testující `token`.
5. **`stack`**: cecko generuje, boef ne (guard `#ifndef PYTHON_GRM`).
6. **AST hlavička**: `cmm_data.hpp` vs `cmm_parser.hpp`.
7. **Literály**: C++ obě varianty `readQuoted*` = `tokenTxt`
   (s uvozovkami); Python backend = `readCharacter/readString` =
   dekódovaný `tokenText`.
8. **Gramatika**: cecko `options`/`extension`/`<primitive>`; boef
   direktivy a CLI, primitiva vestavěná, `str`/`utiny`, `list` vs
   `Sequence<T*>`.
9. **Mark/rewind**: obě větve mají default `mark_type = int`, ale
   `EnvInput::mark()` vrací `InputItem *`; `cmm.g` nepoužívá syntaktické
   predikáty, takže se to neprojeví. Při přidání `[ … ] =>` je potřeba
   `mark_type` nastavit na `InputItem *` (nebo použít lexer s `int mark`).

## 8. Ověřovací příkazy

```sh
# cecko: C++ generátor
make -C /abc/cecko/gram gram-gpp.bin
cd /abc/cecko/cmm && /abc/cecko/gram/gram-gpp.bin \
     input_dir=. output_dir=/tmp/cecko_gen cmm.g
ls /tmp/cecko_gen
# -> cmm_lexer.hpp/cpp cmm_parser.hpp/cpp cmm_data.hpp/cpp
#    cmm_product.hpp/cpp
# cmm_description.tpp se pise do aktualniho adresare (ne do output_dir)

# boef: Python generátor
cd /abc/boef/grm
python3 cparser.py  --cpp --lexer envio.h --lexer-class EnvInput \
        --class CmmParser --lexer-alias CmmLexer \
        --header ../cmm/cmm_parser.hpp --code ../cmm/cmm_parser.cpp \
        ../cmm/cmm.g
python3 cproduct.py --cpp --class CmmProduct --super TextOutput \
        --header ../cmm/cmm_product.hpp --code ../cmm/cmm_product.cpp \
        ../cmm/cmm.g

# stejný lexer:
sha256sum /abc/cecko/gram/textio.h /abc/boef/utils/textio.h
```

## 9. Odkazy

- `cmm.g` (cecko): `/abc/cecko/cmm/cmm.g` — `options`, `extension`,
  `<primitive>` pravidla.
- `cmm.g` (boef): `/abc/boef/cmm/cmm.g` — hlavička s popisem konverze,
  `< header >`, `< struct >`, bez `options`.
- cecko generátor: `/abc/cecko/gram/grammar.cc` (třídy/opce),
  `parsing.cc` (generování parseru/lexeru), `product.cc`.
- Python generátor: `/abc/boef/grm/cparser.py` (`parserFromTerminal`,
  `declareTranslate`, `declareStruct`), `cproduct.py`,
  `/abc/boef/code/lexer.py` (Python lexer).
- Rozhraní: `/abc/boef/cmm/cmm_parser.hpp`,
  `/abc/boef/cmm/cmm_members/CmmParser.inc`,
  `/abc/cecko/cmm/comp.cc` (`CmmLexer::translate`),
  `/abc/boef/utils/textio.h`, `/abc/cecko/gram/textio.h`.
- Dokumentace generátoru: `/abc/grm/wiki`, `/abc/grm/docs`,
  `/abc/cecko/gram/README.txt`.
