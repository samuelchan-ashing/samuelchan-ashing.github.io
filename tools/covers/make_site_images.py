"""Builds the site's pictures from the four self-contained scripts of this folder (the code shown on the site),
with fixed random seeds (seed 6 for the metastable cover: the jump falls mid-picture):
the paper covers (800 x 800 WebP in assets/img/covers/) and the home picture (assets/img/hero.webp, hero-dark.webp).
Run from anywhere:  python3 tools/covers/make_site_images.py [metastable] [dyson_laguerre] [ornstein_uhlenbeck] [dyson_jacobi]
(no argument: all four; dyson_jacobi takes about 15 minutes). Then run build_code_js.py if a script was edited."""
import importlib.util, io, os, sys
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "..", "..", "assets", "img")


def load(name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, name + ".py"))
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def webp(fig, path, size=None, quality=88):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=200, facecolor=fig.get_facecolor()); plt.close(fig)
    im = Image.open(buf).convert("RGB")
    if size: im = im.resize((size, size), Image.LANCZOS)
    im.save(path, "WEBP", quality=quality, method=6)
    print("wrote", os.path.normpath(path))


COVERS = {"metastable": "metastable", "dyson_laguerre": "dyson-laguerre", "dyson_jacobi": "dyson-jacobi"}
SEEDS = {"metastable": 6, "dyson_laguerre": 7, "dyson_jacobi": 20260128}   # the scripts draw new randomness at each run; the site keeps these
todo = sys.argv[1:] or ["metastable", "dyson_laguerre", "ornstein_uhlenbeck", "dyson_jacobi"]
for name in todo:
    m = load(name)
    if name in COVERS:
        webp(m.figure(seed=SEEDS[name]), os.path.join(IMG, "covers", COVERS[name] + ".webp"), size=800)
    elif name == "ornstein_uhlenbeck":
        curves = m.profiles(seed=2026)          # one simulation for both pictures
        webp(m.figure(dark=False, curves=curves), os.path.join(IMG, "hero.webp"), quality=86)
        webp(m.figure(dark=True, curves=curves), os.path.join(IMG, "hero-dark.webp"), quality=86)
