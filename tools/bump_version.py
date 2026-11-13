"""Adds (or updates) ?v=<date-time> on the CSS and JS files referenced by the HTML pages, so that after an upload
browsers fetch the new files instead of mixing them with old copies from their cache.
Run from the root of the site before uploading:  python3 tools/bump_version.py"""
import glob, os, re, time
root = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
v = time.strftime("%Y%m%d%H%M")
files = glob.glob(os.path.join(root, "*.html")) + glob.glob(os.path.join(root, "stays", "*.html")) + [os.path.join(root, "tools", "memoirs", "stay_template.html")]
for p in files:
    if not os.path.exists(p): continue
    s = open(p, encoding="utf-8").read()
    t = re.sub(r'((?:src|href)="(?:\.\./)?assets/(?:css|js)/[\w.-]+\.(?:css|js))(?:\?v=\d+)?"', lambda m: f'{m.group(1)}?v={v}"', s)
    if t != s: open(p, "w", encoding="utf-8").write(t)
print("version", v, "in", len(files), "pages")
