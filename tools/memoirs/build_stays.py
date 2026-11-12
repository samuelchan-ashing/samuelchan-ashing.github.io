#!/usr/bin/env python3
"""Turn the research-stay LaTeX sources into static pages in the site's reader design.

    python3 build_stays.py <site_dir>

Steps per memoir: clean the LaTeX (title block, abstract, TOC, bibliography),
compile each TikZ picture to SVG, convert with pandoc (MathML), then reshape
pandoc's HTML into the same structure as arXiv's LaTeXML output so paper.css
styles it identically, and write stays/<slug>.html from the template.
"""
import html
import json
import pathlib
import re
import subprocess
import sys
import tempfile
import unicodedata
import urllib.parse

import pypandoc
from bs4 import BeautifulSoup, NavigableString, Tag

HERE = pathlib.Path(__file__).resolve().parent
SRC = HERE / "src"
SITE = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else HERE.parent.parent
OUT = SITE / "stays"
FIG = OUT / "figures"

STAYS = json.loads((HERE / "stays.json").read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- LaTeX helpers
def find_env(text, name, start=0):
    """Return (begin_index, end_index_exclusive, inner) of the first \\begin{name}...\\end{name}, handling nesting."""
    b = text.find("\\begin{%s}" % name, start)
    if b < 0:
        return None
    depth, i = 0, b
    pat = re.compile(r"\\(begin|end)\{%s\}" % re.escape(name))
    for m in pat.finditer(text, b):
        depth += 1 if m.group(1) == "begin" else -1
        if depth == 0:
            inner_start = text.index("}", b) + 1
            return b, m.end(), text[inner_start:m.start()]
    raise ValueError("unbalanced " + name)


def strip_comments(tex):
    return re.sub(r"(?<!\\)%.*", "", tex)


def split_doc(tex):
    i = tex.index("\\begin{document}")
    j = tex.rindex("\\end{document}")
    return tex[:i], tex[i + len("\\begin{document}"):j]


def starred_theorems(preamble):
    return set(re.findall(r"\\newtheorem\*\{([^}]+)\}", preamble))


def theorem_names(preamble):
    return set(re.findall(r"\\newtheorem\*?\{([^}]+)\}", preamble))


# --------------------------------------------------------------------------- TikZ → SVG
def tikz_preamble(preamble):
    keep = []
    drop = re.compile(r"\\usepackage(\[[^\]]*\])?\{(geometry|fancyhdr|titlesec|hyperref|lastpage|appendix|comment|float|enumitem|babel|stackengine)\}|\\(pagestyle|fancy|lhead|rhead|chead|lfoot|rfoot|cfoot|titleformat|geometry|setlength)|rulewidth")
    for line in preamble.splitlines():
        if line.strip().startswith("\\documentclass") or drop.search(line):
            continue
        pk = re.match(r"\s*\\usepackage(?:\[[^\]]*\])?\{([^}]*)\}", line)
        if pk and any(subprocess.run(["kpsewhich", p.strip() + ".sty"], capture_output=True).returncode for p in pk.group(1).split(",")):
            continue  # package not installed here: skip it
        keep.append(line)
    keep.append("\\providecommand{\\mathds}[1]{\\mathbb{#1}}")
    return "\\documentclass[tikz,border=6pt]{standalone}\n" + "\n".join(keep)


def compile_tikz(preamble, pictures, slug):
    FIG.mkdir(parents=True, exist_ok=True)
    pre = tikz_preamble(preamble)
    out = []
    for k, pic in enumerate(pictures, 1):
        name = f"{slug}-{k}.svg"
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d)
            (p / "fig.tex").write_text(pre + "\n\\begin{document}\n" + pic + "\n\\end{document}\n", encoding="utf-8")
            r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "fig.tex"], cwd=d, capture_output=True, text=True)
            if r.returncode != 0 or not (p / "fig.pdf").exists():
                err = "\n".join(l for l in r.stdout.splitlines() if l.startswith("!"))[:600]
                print(f"   TikZ {k}: FAILED {err}")
                out.append(None)
                continue
            subprocess.run(["pdftocairo", "-svg", "fig.pdf", str(FIG / name)], cwd=d, check=True)
            out.append(name)
            print(f"   TikZ {k}: {name}")
    return out


# --------------------------------------------------------------------------- body clean-up
def clean_body(body, cfg, preamble):
    info = {"abstract": "", "keywords": []}
    body = strip_comments(body)

    # front matter: everything before the first numbered (sub)section/chapter goes, except the abstract
    m = re.search(r"\\(chapter|section)\{", body)
    front, body = body[: m.start()], body[m.start():]
    ab = find_env(front, "abstract")
    if ab:
        info["abstract"] = ab[2]
    kw = re.search(r"\\textsc\{Keywords\}\s*:\s*([^}]*)\}", front)
    if kw:
        info["keywords"] = [w.strip() for w in kw.group(1).split(",") if w.strip()]

    body = body.replace("\\tableofcontents", "")
    body = re.sub(r"\\(newpage|clearpage|bigskip|medskip|smallskip|noindent|parindent0cm)\b", " ", body)
    body = re.sub(r"\\vspace\*?\{[^}]*\}", " ", body)
    body = body.replace("\\begin{appendix}", "\\appendix").replace("\\end{appendix}", "")
    body = body.replace("\\appendix", "\n\\section*{APPENDIXMARK}\n")
    # the memoirs' own list / proof-outline / brace environments → standard LaTeX pandoc knows
    labels = {"\\num": "(1)", "\\lettre": "(a)", "\\rom": "(i)", "\\etapes": "(1)"}
    def itemnum(m):
        arg = m.group(1)
        lab = next((v for k, v in labels.items() if k.replace("\\\\", "\\") in arg), "(1)")
        return "\\begin{enumerate}[%s]" % lab
    body = re.sub(r"\\begin\{itemnum\}\{([^}]*)\}", itemnum, body)
    body = body.replace("\\end{itemnum}", "\\end{enumerate}")
    body = body.replace("\\begin{itempuce}", "\\begin{itemize}").replace("\\end{itempuce}", "\\end{itemize}")
    body = re.sub(r"\\begin\{trame\}\{", r"\\begin{proof}\\begin{trameintro}{", body)
    body = body.replace("\\end{trame}", "\\end{enumerate}\\end{proof}")
    body = re.sub(r"\\begin\{trameintro\}\{((?:[^{}]|\{[^{}]*\})*)\}", r"\1\n\\begin{enumerate}[(1)]", body)
    body = re.sub(r"\\begin\{acc\}(.*?)\\end\{acc\}", acc_to_cases, body, flags=re.S)

    # math constructs texmath does not read
    body = re.sub(r"\$\s*\\empty\s*\$", "", body)
    body = re.sub(r"\\empty\b", "", body)
    body = re.sub(r"\\mbox\{\\tiny\s*([^{}]*?)\\ref\{[^}]*\}\}", r"\\text{\1}", body)
    body = re.sub(r"\\tag\{\$([^$]*)\$\}", r"\\qquad (\1)", body)
    body = re.sub(r'"(\\(?:Lra|Llra|Longrightarrow|Longleftarrow|Rightarrow|Leftarrow|Leftrightarrow|Longleftrightarrow))"', r"\\text{“}\1\\text{”}", body)
    body = re.sub(r"\\hfill\b", " ", body)
    body = re.sub(r"\\(breve|check|widetilde|widehat|tilde|hat|bar|vec|dot|ddot)\s*(\\(?:mathcal|mathrm|mathbf|mathbb|mathscr)\{[^}]*\}|\\[A-Za-z]+)", r"\\\1{\2}", body)
    body = number_equations(body)
    body = re.sub(r"\\begin\{eqnarray\*?\}(.*?)\\end\{eqnarray\*?\}", eqnarray_to_align, body, flags=re.S)

    # custom layout environments → plain content
    for env in ("changemargin", "center", "flushleft", "flushright", "minipage"):
        body = re.sub(r"\\begin\{%s\}(\{[^}]*\})*" % env, "", body)
        body = body.replace("\\end{%s}" % env, "")

    # TikZ pictures → SVG images
    pics, k, start = [], 0, 0
    while True:
        e = find_env(body, "tikzpicture", start)
        if not e:
            break
        pics.append(body[e[0]:e[1]])
        body = body[:e[0]] + f"\\includegraphics{{TIKZ{len(pics)}}}" + body[e[1]:]
        start = e[0] + 1
    if pics:
        names = compile_tikz(preamble, pics, cfg["slug"])
        for i, n in enumerate(names, 1):
            body = body.replace(f"\\includegraphics{{TIKZ{i}}}", f"\\includegraphics{{figures/{n}}}" if n else "")

    # bibliography → numbered list we can restyle; keep keys for \cite
    keys = []
    e = find_env(body, "thebibliography")
    if e:
        inner = re.sub(r"^\{[^}]*\}", "", e[2].strip())
        items = re.split(r"\\bibitem(?:\[[^\]]*\])?\{([^}]*)\}", inner)
        parts = []
        for j in range(1, len(items), 2):
            keys.append(items[j])
            parts.append("\\item " + items[j + 1].strip())
        bib = "\n\\section*{BIBLIOMARK}\n\\begin{enumerate}\n" + "\n".join(parts) + "\n\\end{enumerate}\n"
        body = body[:e[0]] + bib + body[e[1]:]
    info["bibkeys"] = keys
    return body, info


def number_equations(body):
    """Number equations like LaTeX does (article: one global counter), turn \\label into \\tag,
    and replace \\ref / \\eqref to equation labels by their number (pandoc does not number equations)."""
    counter, labels = 0, {}
    pat = re.compile(r"\\begin\{(equation|eqnarray|align|gather)\}(.*?)\\end\{\1\}", re.S)

    def sub(m):
        nonlocal counter
        env, inner = m.group(1), m.group(2)
        lines = re.split(r"\\\\(?!\[)", inner) if env != "equation" else [inner]
        out = []
        for ln in lines:
            if not ln.strip():
                continue
            if re.search(r"\\(nonumber|notag)\b", ln):
                out.append(re.sub(r"\\(nonumber|notag)\b", "", ln))
                continue
            counter += 1
            lab = re.search(r"\\label\{([^}]*)\}", ln)
            if lab:
                labels[lab.group(1)] = counter
            out.append(re.sub(r"\\label\{[^}]*\}", "", ln).rstrip() + f" \\tag{{{counter}}}")
        return "\\begin{%s*}" % env + " \\\\ ".join(out) + "\\end{%s*}" % env

    body = pat.sub(sub, body)
    for k, v in labels.items():
        body = re.sub(r"\\eqref\{%s\}" % re.escape(k), f"({v})", body)
        body = re.sub(r"\\ref\{%s\}" % re.escape(k), str(v), body)
    return body


def eqnarray_to_align(m):
    lines = re.split(r"\\\\", m.group(1))
    out = []
    for ln in lines:
        parts = ln.split("&")
        out.append(parts[0] + "&" + " ".join(p.strip() for p in parts[1:]) if len(parts) == 3 else ln)
    return "\\begin{align*}" + " \\\\ ".join(out) + "\\end{align*}"


def acc_to_cases(m):
    rows = [r for r in re.split(r"\\\\", m.group(1)) if r.strip()]
    out = []
    for r in rows:
        cells = []
        for cell in r.split("&"):
            parts = cell.split("$")
            bits = []
            for k, part in enumerate(parts):
                if k % 2:
                    bits.append(part.replace("\\dps", ""))
                elif part.strip():
                    bits.append("\\text{ %s }" % part.strip())
            cells.append(" ".join(bits))
        out.append(" & ".join(cells))
    return "\\begin{cases} " + " \\\\ ".join(out) + " \\end{cases}"


def preamble_for_pandoc(preamble):
    preamble = re.sub(r"\\renewcommand\{\\endproof\}.*", "", preamble)
    preamble = re.sub(r"\\newenvironment\{(itempuce|itemnum|trame|acc|changemargin)\}.*?(?=\n\\(?:newcommand|newenvironment|newtheorem|theoremstyle|usepackage|renewcommand|DeclareMathOperator|def|title|author|date)|\n%|\Z)", "", preamble, flags=re.S)
    extra = r"""
\providecommand{\mathds}[1]{\mathbb{#1}}
\renewcommand{\mathds}[1]{\mathbb{#1}}
\providecommand{\vv}[1]{\vec{#1}}
\providecommand{\textsc}[1]{#1}
\renewcommand{\mtext}[1]{\text{#1}}
\renewcommand{\deff}[5]{\begin{array}{lccl} #1 & #2 & \longrightarrow & #4\\ & #3 & \longmapsto & #5 \end{array}}
\renewcommand{\textm}[1]{\;\;\text{#1}}
"""
    return preamble + extra


# --------------------------------------------------------------------------- HTML reshaping
def reshape(html_text, cfg, info, preamble):
    soup = BeautifulSoup(html_text, "html.parser")
    lang = cfg["lang"]
    thm_envs = theorem_names(preamble)
    starred = starred_theorems(preamble)
    proof_word = "Démonstration." if lang == "fr" else "Proof."

    # --- sections
    appendix = False
    app_letters = iter("ABCDEFGHIJ")
    for sec in soup.find_all("section", recursive=False):
        if sec.get("id") == "footnotes" or "footnotes" in sec.get("class", []):
            continue
        h = sec.find(re.compile("^h[1-6]$"), recursive=False)
        title = h.get_text(" ", strip=True) if h else ""
        if title == "APPENDIXMARK":
            sec.decompose() if not sec.find("section") else sec.unwrap()
            appendix = True
            continue
        letter = next(app_letters) if appendix and title != "BIBLIOMARK" else None
        fix_section(sec, 1, letter)

    # --- theorem-like environments
    for div in soup.find_all("div"):
        cls = [c for c in div.get("class", []) if c in thm_envs]
        if not cls:
            continue
        env = cls[0]
        div["class"] = ["ltx_theorem", "ltx_theorem_" + env]
        p = div.find("p")
        strong = p.contents[0] if p and p.contents else None
        if not isinstance(strong, Tag) or strong.name not in ("strong", "em"):
            continue
        label = strong.get_text()
        if env in starred:
            label = re.sub(r"\s*\d+(\.\d+)*$", "", label)
        h6 = soup.new_tag("h6", attrs={"class": "ltx_title ltx_runin ltx_title_theorem"})
        tag = soup.new_tag("span", attrs={"class": "ltx_tag ltx_tag_theorem"})
        tag.string = label
        h6.append(tag)
        strong.decompose()
        # optional name "(…)." possibly containing math
        first = p.contents[0] if p.contents else None
        if isinstance(first, NavigableString) and first.lstrip().startswith("("):
            name_nodes, done = [], False
            while p.contents and not done:
                node = p.contents[0]
                if isinstance(node, NavigableString) and ")" in node:
                    s = str(node)
                    cut = s.rindex(")") + 1
                    name_nodes.append(NavigableString(s[:cut]))
                    rest = s[cut:].lstrip()
                    rest = rest[1:] if rest.startswith(".") else rest
                    node.replace_with(NavigableString(rest.lstrip()))
                    done = True
                else:
                    name_nodes.append(node.extract())
            name_text = "".join(str(n) for n in name_nodes)
            if re.fullmatch(r"\s*\(\s*\)\s*", name_text):
                name_nodes = []  # empty optional name "()"
            if name_nodes:
                h6.append(NavigableString(" "))
            for n in name_nodes:
                h6.append(n if not isinstance(n, NavigableString) else NavigableString(str(n).lstrip() if n is name_nodes[0] else str(n)))
        elif isinstance(first, NavigableString):
            s = str(first).lstrip()
            first.replace_with(NavigableString(s[1:].lstrip() if s.startswith(".") else s))
        div.insert(0, h6)
        if not p.get_text(strip=True) and not p.find("math"):
            p.decompose()

    # --- proofs
    for div in soup.find_all("div", class_="proof"):
        div["class"] = ["ltx_proof"]
        p = div.find("p")
        if p and p.contents and isinstance(p.contents[0], Tag) and p.contents[0].name == "em" and p.contents[0].get_text().strip().rstrip(".") in ("Proof", "Démonstration", "Preuve"):
            p.contents[0].decompose()
        h6 = soup.new_tag("h6", attrs={"class": "ltx_title ltx_runin ltx_title_proof"})
        h6.string = proof_word
        div.insert(0, h6)

    # --- display math scrolls sideways on phones
    for m in soup.find_all("math", attrs={"display": "block"}):
        ann = m.find("annotation")
        tags = re.findall(r"\\tag\{(\d+)\}", ann.get_text()) if ann else []
        w = soup.new_tag("span", attrs={"class": "x-scroll x-block" + (" eqn" if tags else "")})
        m.wrap(w)
        if tags:  # LaTeX equation numbers (texmath drops \tag)
            no = soup.new_tag("span", attrs={"class": "eqno"})
            for t in tags:
                i = soup.new_tag("span")
                i.string = f"({t})"
                no.append(i)
            w.append(no)

    # --- footnotes inline (tap to open), like arXiv's
    notes = {}
    fsec = soup.find("section", class_="footnotes")
    if fsec:
        for li in fsec.find_all("li"):
            back = li.find("a", class_="footnote-back")
            if back:
                back.decompose()
            notes[li.get("id")] = li.decode_contents().strip()
        fsec.decompose()
    for k, a in enumerate(soup.find_all("a", class_="footnote-ref"), 1):
        fid = a.get("href", "#")[1:]
        content = notes.get(fid, "")
        content = re.sub(r"^<p>(.*)</p>$", r"\1", content, flags=re.S)
        new = BeautifulSoup(
            f'<span class="ltx_note ltx_role_footnote"><sup class="ltx_note_mark">{k}</sup>'
            f'<span class="ltx_note_outer"><span class="ltx_note_content">{content}</span></span></span>', "html.parser")
        a.replace_with(new)

    # --- bibliography
    keys = info.get("bibkeys", [])
    unique = len(set(keys)) == len(keys)
    for sec in soup.find_all("section"):
        h = sec.find(re.compile("^h[1-6]$"), recursive=False)
        if not h or h.get_text(strip=True) != "BIBLIOMARK":
            continue
        sec["class"] = ["ltx_bibliography"]
        sec["id"] = "bib"
        h.name = "h2"
        h["class"] = ["ltx_title", "ltx_title_bibliography"]
        h.string = "Références" if lang == "fr" else "References"
        ol = sec.find("ol")
        if ol:
            ol.name = "ul"
            ol.attrs = {"class": "ltx_biblist"}
            for n, li in enumerate(ol.find_all("li", recursive=False), 1):
                li["class"] = ["ltx_bibitem"]
                if unique and n <= len(keys):
                    li["id"] = "bib." + re.sub(r"[^A-Za-z0-9_.-]", "_", keys[n - 1])
                body = li.decode_contents().strip()
                body = re.sub(r"^<p>(.*)</p>$", r"\1", body, flags=re.S)
                li.clear()
                li.append(BeautifulSoup(f'<span class="ltx_tag ltx_tag_bibitem">[{n}]</span><span class="ltx_bibblock">{body}</span>', "html.parser"))
    # citations
    num = {k: i for i, k in enumerate(keys, 1)} if unique else {}
    for sp in soup.find_all("span", class_="citation"):
        cites = sp.get("data-cites", "").split()
        extra = sp.get_text(" ", strip=True)
        links = []
        for c in cites:
            if c in num:
                links.append(f'<a href="#bib.{re.sub(r"[^A-Za-z0-9_.-]", "_", c)}" class="ltx_ref">{num[c]}</a>')
        if not links:
            continue
        inner = ", ".join(links) + (", " + html.escape(extra.strip("[]()")) if extra else "")
        sp.replace_with(BeautifulSoup(f'<cite class="ltx_cite">[{inner}]</cite>', "html.parser"))

    # --- tidy: lists, images, empty paragraphs
    for img in soup.find_all("img"):
        img["loading"] = "lazy"
        img["decoding"] = "async"
        for a in ("style", "width", "height"):
            if a in img.attrs:
                del img[a]
    for p in soup.find_all("p"):
        if not p.get_text(strip=True) and not p.find(["math", "img"]):
            p.decompose()
    return soup


def fix_section(sec, level, letter):
    """pandoc <section class=levelN><hN><span class=header-section-number>…</span> Title</hN> → LaTeXML-like."""
    names = {1: ("ltx_section", "h2", "ltx_title_section"), 2: ("ltx_subsection", "h3", "ltx_title_subsection"),
             3: ("ltx_subsubsection", "h4", "ltx_title_subsubsection"), 4: ("ltx_paragraph", "h4", "ltx_title_paragraph")}
    cls, tag, tcls = names.get(level, names[4])
    if letter and level == 1:
        cls = "ltx_appendix"
        tcls = "ltx_title_appendix"
    sec["class"] = [cls]
    h = sec.find(re.compile("^h[1-6]$"), recursive=False)
    if h:
        h.name = tag
        h["class"] = ["ltx_title", tcls]
        for a in ("data-number",):
            if a in h.attrs:
                del h[a]
        n = h.find("span", class_="header-section-number")
        if n:
            number = n.get_text(strip=True)
            if letter:
                number = re.sub(r"^\d+", letter, number)
            n["class"] = ["ltx_tag", "ltx_tag_" + cls.replace("ltx_", "")]
            n.string = (("Appendix " + number) if (letter and level == 1) else number + ("." if level > 1 else ""))
            if level > 1:
                n.insert_after(NavigableString(" "))
            nxt = n.next_sibling
            if isinstance(nxt, NavigableString) and level == 1:
                nxt.replace_with(NavigableString(str(nxt).lstrip()))
    if "data-number" in sec.attrs:
        del sec["data-number"]
    for child in sec.find_all("section", recursive=False):
        fix_section(child, level + 1, letter)


# --------------------------------------------------------------------------- page assembly
def text_of(node):
    c = BeautifulSoup(str(node), "html.parser")
    for t in c.select(".ltx_tag, .ltx_note"):
        t.decompose()
    for m in c.find_all("math"):
        sem = m.find("semantics")
        first = sem.find(True) if sem else None
        m.replace_with(first.get_text() if first else m.get("alttext", ""))
    return re.sub(r"\s+", " ", c.get_text()).strip()


def html_of(node):
    c = BeautifulSoup(str(node), "html.parser")
    root = c.find(True)
    for t in root.select(".ltx_tag, .ltx_note"):
        t.decompose()
    for t in root.find_all(attrs={"id": True}):
        del t["id"]
    return root.decode_contents().strip()


def tracks_of(soup):
    out = []
    for sec in soup.find_all("section", recursive=False):
        h = sec.find(re.compile("^h[1-6]$"), recursive=False)
        tag = h.find("span", class_="ltx_tag") if h else None
        num = re.sub(r"^Appendix\s*", "", tag.get_text(strip=True)).rstrip(".") if tag else ""
        is_bib = "ltx_bibliography" in sec.get("class", [])
        subs = [text_of(x) for x in sec.find_all("section", recursive=False) for x in [x.find(re.compile("^h[1-6]$"), recursive=False)] if x]
        out.append({"id": sec.get("id"), "num": num, "title_html": html_of(h) if h else "", "subs": subs, "bib": is_bib})
    return out


def reading_minutes(soup):
    c = BeautifulSoup(str(soup), "html.parser")
    formulas = 0
    for m in c.find_all("math"):
        formulas += 6 if m.get("display") == "block" else 1
        m.decompose()
    words = len(c.get_text(" ").split())
    return max(1, round((words + 2 * formulas) / 200))


def to_html_fragment(tex, preamble):
    return pypandoc.convert_text(preamble + "\n\\begin{document}\n" + tex + "\n\\end{document}\n", "html5", format="latex",
                                 extra_args=["--mathml", "--wrap=none"])


def build(cfg):
    print(f"== {cfg['slug']}")
    tex = (SRC / cfg["src"]).read_text(encoding="utf-8")
    preamble, body = split_doc(tex)
    body, info = clean_body(body, cfg, preamble)
    pre = preamble_for_pandoc(preamble)
    args = ["--mathml", "--section-divs", "--number-sections", "--wrap=none"]
    if cfg.get("book"):
        args.append("--top-level-division=chapter")
    raw = pypandoc.convert_text(pre + "\n\\begin{document}\n" + body + "\n\\end{document}\n", "html5", format="latex", extra_args=args)
    soup = reshape(raw, cfg, info, preamble)
    abstract = to_html_fragment(strip_comments(info["abstract"]), pre) if info["abstract"] else ""
    abstract = re.sub(r"<p>\s*</p>", "", abstract)
    leftover = len(re.findall(r'class="math (inline|display)"', str(soup)))
    unresolved = re.findall(r'data-reference="([^"]+)"[^>]*>\[[^<]*\]<', str(soup))
    print(f"   math unconverted: {leftover}, unresolved refs: {unresolved[:8]}")
    page = render_page(cfg, soup, abstract, info)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{cfg['slug']}.html").write_text(page, encoding="utf-8")
    print(f"   wrote stays/{cfg['slug']}.html ({len(page)//1024} KB)")


def esc(s):
    return html.escape(s, quote=True)


def pdf_href(name):
    """Link from stays/<page>.html to a PDF given relative to the site root (e.g. pdf/cutoff-2024.pdf).
    PDF names are kept ASCII so the links work on any host (GitHub Pages is case- and accent-sensitive)."""
    if not (SITE / name).is_file():
        raise FileNotFoundError(SITE / name)
    return "../" + urllib.parse.quote(name)


def build_pdf_only(cfg):
    """Memoir without usable sources: same page, chapters open the PDF at the right page."""
    print(f"== {cfg['slug']} (PDF chapters)")
    href = pdf_href(cfg["pdf"])
    off = cfg.get("pdf_offset", 0)
    tracks = "\n".join(
        f'        <li class="row"><a href="{href}#page={p + off}" target="_blank" rel="noopener">\n'
        f'          <span class="row-lead num">{esc(n)}</span>\n'
        f'          <span class="row-body"><span class="row-title">{esc(t)}</span>'
        + (f'<span class="row-sub one">{esc(" · ".join(subs))}</span>' if subs else "")
        + '</span>\n          <span class="row-trail chev"><svg class="icon"><use href="#i-doc"/></svg></span></a></li>'
        for n, t, p, subs in cfg["chapters"])
    page = render_page(cfg, None, cfg.get("abstract_html", ""), {"keywords": []}, tracks_html=tracks)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"{cfg['slug']}.html").write_text(page, encoding="utf-8")
    print(f"   wrote stays/{cfg['slug']}.html")


def render_page(cfg, soup, abstract_html, info, tracks_html=None):
    tpl = (HERE / "stay_template.html").read_text(encoding="utf-8")
    tracks = tracks_of(soup) if soup is not None else []
    n_sec = sum(1 for t in tracks if not t["bib"]) if soup is not None else len(cfg.get("chapters", []))
    mins = reading_minutes(soup) if soup is not None else 0
    track_html = tracks_html or "\n".join(
        f'        <li class="row"><a href="#{esc(t["id"])}">\n'
        f'          <span class="row-lead num">{"<svg class=\"icon\"><use href=\"#i-list\"/></svg>" if t["bib"] else esc(t["num"])}</span>\n'
        f'          <span class="row-body"><span class="row-title">{t["title_html"]}</span>'
        + (f'<span class="row-sub one">{esc(" · ".join(t["subs"]))}</span>' if t["subs"] else "")
        + '</span>\n          <span class="row-trail dots"><svg class="icon"><use href="#i-dots"/></svg></span></a></li>'
        for t in tracks)
    kws = cfg.get("keywords") or info.get("keywords") or []
    others = [s for s in STAYS if s["slug"] != cfg["slug"]]
    more = "\n".join(
        f'        <li class="card"><a href="{esc(s["slug"])}.html" title="{esc(s["title"])}">\n'
        f'          <div class="art"><img src="../assets/img/covers/{esc(s["cover"])}" alt="" width="800" height="800" loading="lazy"><span class="badge">Memoir</span></div>\n'
        f'          <div class="card-title">{esc(s["short"])}</div>\n'
        f'          <div class="card-sub">{esc(s["year"])} · {esc(s["place"])}</div></a></li>' for s in others)
    foot = [f'{esc(cfg["kind"])}, {esc(cfg["host"])}',
            esc(" · ".join(x for x in (cfg["supervision"], cfg.get("duration")) if x)),
            (f'{n_sec} sections, about {mins} min of reading' if soup is not None else f'{n_sec} chapters · each opens the PDF at its page')
            + (" · in French" if cfg["lang"] == "fr" else "")]
    rep = {
        "{{TITLE}}": esc(cfg["title"]),
        "{{SHORT}}": esc(cfg["short"]),
        "{{DESCRIPTION}}": esc(cfg["description"]),
        "{{TINT}}": esc(cfg["tint"]),
        "{{COVER}}": esc(cfg["cover"]),
        "{{AUTHORS}}": esc(cfg["authors"]),
        "{{ORIGINAL}}": (f'<div class="album-journal only-en" lang="{cfg["lang"]}">Original title: <em>{esc(cfg["original_title"])}</em></div>' if cfg.get("original_title") else ""),
        "{{META}}": esc(" · ".join([cfg["kind_short"], cfg["year"], cfg["place"]])),
        "{{PDF}}": esc(pdf_href(cfg["pdf"])),
        "{{LANG}}": cfg["lang"],
        "{{ABSTRACT}}": abstract_html,
        "{{TRACKS}}": track_html,
        "{{FOOT}}": "".join(f"<span>{f}</span>" for f in foot),
        "{{KEYWORDS}}": "".join(f'<li class="chip">{esc(k)}</li>' for k in kws),
        "{{LANGNOTE}}": ('<p class="lang-note only-en">This report is written in French.</p>' if cfg["lang"] == "fr" else ""),
        "{{BODY}}": str(soup) if soup is not None else "",
        "{{MORE}}": more,
    }
    for k, v in rep.items():
        tpl = tpl.replace(k, v)
    if soup is None:  # no HTML text: drop the empty article
        tpl = re.sub(r'\s*<article class="paper".*?</article>', "", tpl, flags=re.S)
    return tpl


if __name__ == "__main__":
    only = sys.argv[2:]
    for cfg in STAYS:
        if only and cfg["slug"] not in only:
            continue
        build(cfg) if cfg.get("src") else build_pdf_only(cfg)
