#!/usr/bin/env python3
"""Convert docs/*.md to a single Lout document and compile it to PDF.

Usage:  python3 md2lout.py

  - reads the Markdown files of the documentation in a fixed order
    (the same order as docs/README.md),
  - writes _output/grm-docs.lout,
  - converts referenced images (docs/pictures/*.png) to EPS files in
    _output/eps/ (Lout can only include EPS), using ImageMagick,
  - runs `lout` (three passes) on the generated .lout file and
    `ps2pdf` on the result, producing _output/grm-docs.pdf.

Requirements:  lout (http://jeffreykingston.id.au/lout), ghostscript
(ps2pdf), ImageMagick (magick or convert).

The lout binary is taken from $LOUT or from $PATH.  Lout resolves its
relative library directories (include/, font/, ...) against the current
working directory, so the script runs lout from its library directory;
override it with $LOUTLIB if needed.

Notes on the Markdown subset handled:  ATX headings (#, ##, ###),
fenced code blocks, bullet lists ("- "), paragraphs, bold (**x),
italic (*x), inline code (`x`), links [text](url), images ![](path)
and bare URLs.  Images are included in the PDF; inline code is set in
a fixed-width font; links are printed as "text (url)".  Code lines
longer than WRAP_COL are soft-wrapped at a space, with the continuation
indented - the Markdown sources remain the authoritative record.
"""

import os, re, subprocess, sys, glob

# --------------------------------------------------------------------------
# configuration

DOCS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(DOCS, "_output")
EPS = os.path.join(OUT, "eps")
PICTURES = os.path.join(DOCS, "pictures")

# document order: main pages, then the hand-written lexer/parser appendix
FILES = ["README.md",
         "gram.md", "gram_parser.md", "gram_html.md", "gram_lout.md",
         "gram_nullable.md", "gram_symbols.md",
         "parser.md", "parser_tree.md", "product.md", "select.md",
         "choose.md",
         "c1.md", "c2.md", "c3.md", "c3_comp.md", "c3_python.md", "c4.md",
         "cmm_grammar.md", "cmm_comp.md", "cmm_qt.md", "cindex.md",
         "lexer.md", "expr.md", "stat.md",
         "mini_parser.md", "mini_table.md", "pokus.md"]

DOC_TITLE = "grm - grammar toolkit documentation"
DOC_AUTHOR = "Zdeněk Čulík"
WRAP_COL = 72

# --------------------------------------------------------------------------
# Lout text escaping
#
# In Lout prose the characters @ { } | & # ; ^ ~ / " \ are special.
# A maximal run of special characters is enclosed in double quotes:
# a quoted string prints its contents literally, with \" for a quote
# and \\ for a backslash inside.

SPECIAL = set('@{}|&#;^~/') | set('"\\"')

def lout_escape(text):
    out = []
    run = ""
    for ch in text:
        if ch in SPECIAL:
            run += ch
        else:
            if run:
                content = run.replace("\\", "\\\\").replace('"', '\\"')
                out.append('"' + content + '"')
                run = ""
            out.append(ch)
    if run:
        content = run.replace("\\", "\\\\").replace('"', '\\"')
        out.append('"' + content + '"')
    return "".join(out)

# --------------------------------------------------------------------------
# inline Markdown -> Lout

INLINE = re.compile(
    r"(!\[[^\]]*\]\([^)]+\))"     # 1 image
    r"|(\[[^\]]+\]\([^)]+\))"     # 2 link
    r"|(\*\*[^*]+\*\*)"           # 3 bold
    r"|(\*[^*]+\*)"               # 4 italic
    r"|(`[^`]+`)"                 # 5 inline code
    r"|(https?://[^\s)>,]+)"      # 6 bare URL
)

def lout_url(url):
    """Escape a URL, adding zero-width break opportunities after / and -."""
    parts = [p for p in re.split(r"(?<=[/-])", url) if p]
    return " &0i ".join(lout_escape(p) for p in parts)

def lout_inline(text):
    result = []
    pos = 0
    for m in INLINE.finditer(text):
        if m.start() > pos:
            result.append(lout_escape(text[pos:m.start()]))
        token = m.group(0)
        if m.group(1):                          # image -> include graphic
            inside = m.group(1)[3:-1]           # strip "![", ")"
            name, path = inside.split("](", 1)
            result.append(figure(path))
        elif m.group(2):                        # link -> text (url)
            link_text, url = m.group(2)[1:-1].split("](", 1)
            result.append(lout_escape(link_text))
            result.append(" (" + lout_url(url) + ")")
        elif m.group(3):                        # bold
            result.append("@B { " + lout_escape(m.group(3)[2:-2]) + " }")
        elif m.group(4):                        # italic
            result.append("@I { " + lout_escape(m.group(4)[1:-1]) + " }")
        elif m.group(5):                        # inline code
            result.append("@F { " + lout_escape(m.group(5)[1:-1]) + " }")
        else:                                   # bare URL
            url = m.group(6)
            while url and url[-1] in ".,;)":
                url = url[:-1]
            result.append(lout_url(url))
        pos = m.end()
    result.append(lout_escape(text[pos:]))
    return "".join(result)

# --------------------------------------------------------------------------
# images

def eps_for(png_name):
    """Convert the image at docs/<png_name> to _output/eps/<name>.eps."""
    src = os.path.join(DOCS, png_name)
    dst = os.path.join(EPS, os.path.basename(png_name) + ".eps")
    if not os.path.exists(dst):
        tool = None
        for cand in ("magick", "convert"):
            path = shutil_which(cand)
            if path:
                tool = path
                break
        if tool is None:
            return None
        # 15.5 cm printable width at 150 dpi = 915 px; shrink larger images
        subprocess.run([tool, src, "-resize", "915x>",
                        "-density", "150", "eps2:" + dst], check=False)
    if os.path.exists(dst):
        return dst
    return None

def shutil_which(cmd):
    for d in os.environ.get("PATH", "").split(os.pathsep):
        p = os.path.join(d, cmd)
        if os.path.isfile(p) and os.access(p, os.X_OK):
            return p
    return None

def figure(png_name):
    eps = eps_for(png_name)
    if eps:
        return "@IncludeGraphic { " + esc_path(eps) + " }"
    return "@I { [figure " + lout_escape(png_name) + " not available] }"

def esc_path(path):
    """Quote a file name for @IncludeGraphic (a string prints literally)."""
    return '"' + path.replace('"', '') + '"'

# --------------------------------------------------------------------------
# code blocks
#
# Lout's @Verbatim @Begin ... @End @Verbatim would be the natural choice,
# but its scanner terminates on ANY occurrence of @End, @Include or
# @SysInclude inside the text (see LexScanVerbatim in the Lout sources),
# which appears in several of our examples.  Instead every code line is
# emitted as a quoted Lout string (strings print their contents
# literally, with \" for a quote and \\ for a backslash), separated
# by the // line-break symbol, all inside an indented display in
# Courier.  Code lines longer than WRAP_COL are soft-wrapped at a
# space, with the continuation indented - the Markdown sources remain
# the authoritative record.

def code_string(line):
    return '"' + line.replace("\\", "\\\\").replace('"', '\\"') + '"'

def lout_code_block(lines):
    out = [ ]
    for line in lines:
        line = line.rstrip("\n")
        pieces = [ ]
        while len(line) > WRAP_COL:
            cut = line.rfind(" ", 40, WRAP_COL)
            if cut < 0:
                break
            pieces.append(line[:cut])
            line = "      " + line[cut + 1:]
        pieces.append(line)
        out.extend(pieces)
    body = " //\n".join(code_string(p) for p in out)
    return "@ID {\n{ Courier Base -1p } @Font {\n" + body + "\n}\n}"

# --------------------------------------------------------------------------
# block-level Markdown -> Lout

def convert_md(text):
    """Convert one Markdown file to Lout body.  Headings open @Section /
    @SubSection / @SubSubSection galleys, closed at the end of the file.
    In a report, subsections must be bracketed by @BeginSubSections /
    @EndSubSections (and @BeginSubSubSections / @EndSubSubSections)."""
    lines = text.split("\n")
    out = []
    para = []
    code = None
    listitems = None
    opened = [ ]          # stack of heading levels currently open
    groups = [ ]          # stack of open sectioning groups (2 or 3)
    GROUPS = {2: ("@BeginSubSections", "@EndSubSections"),
              3: ("@BeginSubSubSections", "@EndSubSubSections")}

    def close_groups_to(level):
        while groups and groups[-1] >= level:
            out.append(GROUPS[groups.pop()][1])

    def close_para():
        nonlocal para
        if para:
            out.append("@PP")
            out.append(lout_inline(" ".join(para)))
            para = []

    def close_list():
        nonlocal listitems
        if listitems:
            out.append("@PP")
            out.append("@BulletList")
            for item in listitems:
                out.append("    @ListItem { " + lout_inline(item) + " }")
            out.append("@EndList")
            listitems = None

    def close_code():
        nonlocal code
        if code is not None:
            close_para()
            close_list()
            out.append("@PP")
            out.append(lout_code_block(code))
            code = None

    def open_heading(level, title):
        close_para(); close_list(); close_code()
        while opened and opened[-1] >= level:
            close_heading()
        if level == 1:
            close_groups_to(2)
        elif level == 2:
            close_groups_to(3)
            if 2 not in groups:
                out.append(GROUPS[2][0])
                groups.append(2)
        elif level == 3:
            if 2 not in groups:
                out.append(GROUPS[2][0])
                groups.append(2)
            if 3 not in groups:
                out.append(GROUPS[3][0])
                groups.append(3)
        word = ("Section" if level == 1 else
                "SubSection" if level == 2 else "SubSubSection")
        out.append("@" + word + " @Title { " + lout_escape(title) +
                   " } @Begin")
        opened.append(level)

    def close_heading():
        if opened:
            level = opened.pop()
            # a sectioning group belongs to the parent heading, so closing
            # a level-L heading closes only groups nested deeper than L
            close_groups_to(level + 1)
            word = ("Section" if level == 1 else
                    "SubSection" if level == 2 else "SubSubSection")
            out.append("@End @" + word)

    for line in lines:
        if code is not None:
            if line.startswith("```"):
                close_code()
            else:
                code.append(line)
            continue
        if line.startswith("```"):
            code = [ ]
            continue
        m = re.match(r"^(#{1,3})\s+(.*?)\s*#*\s*$", line)
        if m:
            open_heading(len(m.group(1)), m.group(2))
            continue
        if line.startswith("- "):
            close_para(); close_code()
            if listitems is None:
                listitems = [ ]
            listitems.append(line[2:].strip())
            continue
        if line.strip() == "":
            close_para(); close_list()
            continue
        close_list()
        para.append(line.strip())

    close_para(); close_list(); close_code()
    while opened:
        close_heading()
    return "\n".join(out)

# --------------------------------------------------------------------------
# lout discovery and invocation

def find_lout_lib(lout_bin):
    cands = [ ]
    if os.environ.get("LOUTLIB"):
        cands.append(os.environ["LOUTLIB"])
    if lout_bin:
        base = os.path.dirname(os.path.dirname(os.path.abspath(lout_bin)))
        cands += sorted(glob.glob(os.path.join(base, "share", "lout*", "lib")))
        cands.append(os.path.join(base, "lib"))
    cands += sorted(glob.glob("/usr/share/lout*/lib"))
    cands += sorted(glob.glob("/usr/local/share/lout*/lib"))
    cands.append(os.getcwd())
    for c in cands:
        if os.path.exists(os.path.join(c, "include", "report")):
            return c
    return os.getcwd()

def find_lout():
    if os.environ.get("LOUT"):
        return os.environ["LOUT"]
    # a locally built lout from docs/tools/build_lout.py takes precedence
    local = os.path.join(DOCS, "_library", "lout", "bin", "lout")
    if os.path.isfile(local) and os.access(local, os.X_OK):
        return local
    return shutil_which("lout")

# --------------------------------------------------------------------------

def main():
    os.makedirs(EPS, exist_ok=True)
    parts = [
        # latin2 must come first: it adds the Central European (CE)
        # fonts needed for the author's name (Zdeněk Čulík)
        "@SysInclude { latin2 }",
        "@SysInclude { report }",
        "@Report",
        "   @Title { " + lout_escape(DOC_TITLE) + " }",
        "   @Author { " + lout_escape(DOC_AUTHOR) + " }",
        "   @DateLine { Yes }",
        "   @ContentsSeparate { Yes }",
        "   @InitialFont { TimesCE Base 12p }",
        "//",
    ]
    for name in FILES:
        path = os.path.join(DOCS, name)
        if not os.path.exists(path):
            print("warning: missing", path, file=sys.stderr)
            continue
        with open(path, encoding="utf-8") as f:
            text = f.read()
        parts.append(convert_md(text))
    lout_source = "\n".join(parts) + "\n"

    lout_file = os.path.join(OUT, "grm-docs.lout")
    # Lout reads single-byte text: with the latin2 font database the file
    # must be ISO-8859-2 (the document text is ASCII except the author's
    # name; typographic Unicode is normalized to ASCII equivalents)
    latin2 = (lout_source
              .replace("—", "--")   # em dash
              .replace("–", "-")    # en dash
              .replace("‘", "'")    # left single quote
              .replace("’", "'")    # right single quote
              .replace("‚", "'")
              .replace("“", '"')    # double quotes
              .replace("”", '"')
              .replace("…", "...")) # ellipsis
    with open(lout_file, "w", encoding="iso-8859-2", errors="replace") as f:
        f.write(latin2)
    print("wrote", lout_file)

    lout_bin = find_lout()
    if not lout_bin:
        print("error: lout not found (set $LOUT)", file=sys.stderr)
        return 1
    libdir = find_lout_lib(lout_bin)
    print("using lout:", lout_bin, " lib:", libdir)

    # lout writes its cross-reference database (lout.li, lout.ld, ...) into
    # its working directory; stale files from other documents break the run
    for stale in ("lout.li", "lout.ld", "lout.ldx", "lout.ix", "lout.dx"):
        try:
            os.remove(os.path.join(libdir, stale))
        except OSError:
            pass

    ps_file = os.path.join(OUT, "grm-docs.ps")
    r = subprocess.run([lout_bin, "-r3", lout_file, "-o", ps_file],
                       cwd=libdir, capture_output=True, text=True)
    if r.returncode != 0 or not os.path.exists(ps_file):
        print(r.stderr[-4000:], file=sys.stderr)
        print("error: lout failed", file=sys.stderr)
        return 1
    print("wrote", ps_file)

    pdf_file = os.path.join(OUT, "grm-docs.pdf")
    r = subprocess.run(["ps2pdf", ps_file, pdf_file], capture_output=True,
                       text=True)
    if r.returncode != 0 or not os.path.exists(pdf_file):
        print(r.stderr[-2000:], file=sys.stderr)
        print("error: ps2pdf failed", file=sys.stderr)
        return 1
    print("wrote", pdf_file)
    return 0

if __name__ == "__main__":
    sys.exit(main())
