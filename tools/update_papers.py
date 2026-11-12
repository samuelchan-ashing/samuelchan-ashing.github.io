#!/usr/bin/env python3
"""Save a local copy of each paper's arXiv HTML into papers/<id>.html.

The site normally reads https://arxiv.org/html/<id> live in the visitor's
browser. These copies are only a fallback, used when arXiv is unreachable.
Run it from the site folder whenever you post a new version:

    python3 tools/update_papers.py            # every paper listed in assets/js/data.js
    python3 tools/update_papers.py 2601.20390 # just one

Only the Python standard library is needed.
"""
import pathlib
import re
import sys
import time
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "assets" / "js" / "data.js"
OUT = ROOT / "papers"


def paper_ids():
    text = DATA.read_text(encoding="utf-8")
    return re.findall(r'\bid:\s*"([^"]+)"', text)


def fetch(arxiv_id):
    req = urllib.request.Request(
        f"https://arxiv.org/html/{arxiv_id}",
        headers={"User-Agent": "personal-website-cache/1.0 (samuel.chan-ashing@ens.psl.eu)"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode("utf-8", errors="replace")


def trim(html):
    """Keep only what the reader uses: the version watermark and the article."""
    wm = re.search(r'<div id="watermark-tr">.*?</div>', html, re.S)
    art = re.search(r"<article\b.*?</article>", html, re.S)
    if not art:
        raise ValueError("no <article> found (is there an HTML version on arXiv?)")
    title = re.search(r"<title>(.*?)</title>", html, re.S)
    return (
        "<!DOCTYPE html>\n<html lang=\"en\"><head><meta charset=\"UTF-8\">"
        f"<title>{title.group(1).strip() if title else ''}</title></head><body>\n"
        f"{wm.group(0) if wm else ''}\n{art.group(0)}\n</body></html>\n"
    )


def main():
    ids = sys.argv[1:] or paper_ids()
    OUT.mkdir(exist_ok=True)
    for k, arxiv_id in enumerate(ids):
        if k:
            time.sleep(3)  # be polite to arXiv
        try:
            html = trim(fetch(arxiv_id))
        except Exception as e:  # keep going with the other papers
            print(f"  {arxiv_id}: FAILED ({e})")
            continue
        path = OUT / f"{arxiv_id}.html"
        path.write_text(html, encoding="utf-8")
        print(f"  {arxiv_id}: saved {path.relative_to(ROOT)} ({len(html) // 1024} KB)")


if __name__ == "__main__":
    main()
