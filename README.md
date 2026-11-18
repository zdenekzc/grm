# grm — grammar toolkit

A small toolkit for working with grammars: parsing a grammar file (an
EBNF-like notation with attributes), analyzing it, and generating
recursive-descent parsers and related code in several target languages.

The toolkit is developed as supporting material for compiler-construction
teaching.

## Grammar file format

A grammar is a set of rules written in an EBNF-like notation:

```
simple : string_literal | identifier | ebnf ;

alternative : ( simple )* ;

description : alternative ( "|" alternative )* ;

rule : identifier ":" description ";" ;

grammar : ( rule )* ;
```

Terminals are quoted string literals, nonterminals are identifiers, and
`( ... )` groups may be followed by `?`, `*` or `+`. A complete example is
the grammar describing the notation itself; larger example grammars
(`cmm.g`, `pas.g`, ...) can be found in the
[simple-view](https://github.com/zdenekzc/simple-view) project.

## Tools

Run the tools from within the `grm/` directory (the modules import each
other by plain file name):

| Tool            | Purpose |
| --------------- | ------- |
| `grammar.py`    | Core data model — reads a `.g` file, builds `Grammar`/`Rule`/`Expression`/`Alternative` objects |
| `lexer.py`      | Base lexer — reads source text, produces tokens (`token`, `tokenText`) |
| `toparser.py`   | Generates a recursive-descent parser in Python |
| `cparser.py`    | Generates a recursive-descent parser in C, C++, C#, Java, Pascal or Vala (`--c`, `--cpp`, `--csharp`, `--java`, `--pascal`, `--vala`) |
| `pparser.py`    | Generates a recursive-descent parser in Pascal |
| `cproduct.py`   | Generates a *product* (AST builder / semantic action skeleton) in C, C++, C#, Java, Pascal, Vala, JavaScript or Rust |
| `pproduct.py`   | Generates a product in Pascal |
| `toproduct.py`  | Generates a product in Python |
| `tocopy.py`     | Copies/transforms the grammar structure |
| `tohtml.py`     | Renders the grammar as an HTML page |
| `tolout.py`     | Renders the grammar for the lout document formatting system |
| `recognize.py`  | Runs a recognizer over a sample source file (test harness) |
| `symbols.py`    | Symbol table utilities |
| `gram_plugin.py`| Plugin integrating the toolkit into the [simple-view](https://github.com/zdenekzc/simple-view) GUI environment |

Most generators follow the same command-line shape:

```
python3 toparser.py grammar.g -o parser.py
python3 cparser.py  grammar.g --cpp --code parser.cpp
python3 tohtml.py   grammar.g -o grammar.html
```

Requires Python 3. No third-party packages are needed for the command-line
tools (`gram_plugin.py` additionally needs the simple-view environment and Qt).

## Layout

```
grm/    the toolkit (run the tools from this directory)
```

## Related projects

- [simple-view](https://github.com/zdenekzc/simple-view) — GUI environment
  and example grammars; the support modules (`input.py`, `output.py`,
  `lexer.py`, `code*.py`, `gcc_options.py`) originate there.

## License

Licensed under the [GNU General Public License v3.0](LICENSE).
