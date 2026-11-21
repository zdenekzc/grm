# lexers — legacy lexer sources and the target Lexer API

The files here are historical lexer implementations (2002–2022) used by
older versions of the generated parsers. They are kept for reference;
the **target API** is the one in the newer toolchain
(`/abc/gibbon/src/utils/textio.*` + `envio.*`, and its fork under
`/abc/gibbon/boef/utils/`). The generators in `grm/` emit code for that
new API.

## Token fields

| Field | Meaning |
| ----- | ------- |
| `tokenKind` | lexical kind: `TokenKind` enum (`nameToken`, `numberToken`, `realToken`, `charToken`, `stringToken`, `separatorToken`, …, `eofToken`) |
| `tokenTxt` | original token text from the input — **for string/char literals including quotes and escape sequences** |
| `tokenVal` | the value of the literal — **without quotes, escape sequences decoded** (`tokenVal [0]` for a character) |
| `tokenSym` | the separator character |
| `inpCh` | the current input character (lookahead for long separators) |
| `token` | symbol of the grammar (`CmmSymbol` enum), set by the generated `translate ()` |
| `symbol` | (`EnvInput`) generic input symbol; `isSymbol ()`, `testSymbols ()`, `LA (i)` |

## Literal reading (textio.cc, verified)

| Generator emits | Lexer method | Returns |
| --------------- | ------------ | ------- |
| `readIdent ()` | `readIdent` | `tokenTxt` after `nextToken ()` |
| `readNumber ()` | `readNumber` | `tokenTxt` |
| `readReal ()` | `readReal` | `tokenTxt` |
| `readQuotedCharAsString ()` | `readQuotedCharAsString` | `tokenTxt` — **with** quotes (C-- stores `'\n'` whole) |
| `readQuotedString ()` | `readQuotedString` | `tokenTxt` — **with** quotes |
| — (available) | `readCharAsString ()` | `tokenVal` — without quotes |
| — (available) | `readString ()` | `tokenVal` — without quotes |
| — (available) | `readChar ()` | `tokenVal [0]` |

## API mapping: what changed against the legacy lexers

| Legacy | Current target |
| ------ | -------------- |
| `tokenText` | `tokenTxt` |
| `ch` | `inpCh` |
| `identToken` | `nameToken` |
| (no real numbers) | `realToken` |
| `readIdentifier` | `readIdent` |
| `readNumber` (also for reals) | `readNumber` / `readReal` |
| `readChar` | `readQuotedCharAsString` (quoted) or `readCharAsString` |
| `readString` | `readQuotedString` (quoted) or `readString` |
| `src_col` | `src_column` |
| `size` field on tokens | not used |

The generated parser derives from the lexer class (`Parser : public
Lexer`, with `utils/lexer.h` providing `typedef EnvInput Lexer;`) and
defines `isSymbol`, `checkSymbol`, `testSymbols`, `tokenToString`,
`lookupKeyword`, `processSeparator` and `translate` itself.
