"""Paint the three paper covers from tools/covers/simulations.pkl (made by simulate.py) into assets/img/covers/.

    metastable.webp      the particle system of the cosine model: density of the N = 80 particles over time (glow),
                         three individual particles, and the empirical mean, which jumps from the well at 6.64 to 1.38
    dyson-jacobi.webp    measured cutoff profiles (Kolmogorov distance to equilibrium of x_1 + ... + x_n, against t / c_n)
                         for n = 2 ... 32, over the trajectories of one Dyson–Jacobi run with n = 40 particles
    dyson-laguerre.webp  the same for Dyson–Laguerre (n = 2 ... 64), over one run with n = 40 (singular values sqrt(x_i))
Colours: Sanzo Wada combinations (Red · Pale Lemon Yellow, Dusky Green · Ivory Buff, Corinthian Pink · Brick Red).
"""
import os, pickle, numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, to_rgb
from scipy.ndimage import gaussian_filter
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "..", "assets", "img", "covers")
R = pickle.load(open(os.path.join(HERE, "simulations.pkl"), "rb"))
COVERS = {
    "metastable":     dict(bg=("#a72144", "#520b1d"), lines=["#ffefae", "#eeb760", "#f9c1ce"], dark=True),
    "dyson-jacobi":   dict(bg=("#004f46", "#002e28"), lines=["#ebd3a2", "#cfe3c9", "#9cc9b4"], dark=True),
    "dyson-laguerre": dict(bg=("#f8b6ba", "#f5d0c4"), lines=["#d4785a", "#a84222", "#6e2a14"], dark=False),
}
X0, X1, Y0, Y1 = 0.06, 0.94, 0.14, 0.86


def canvas(bg1, bg2, vertical=True, extent=(0, 1, 1, 0)):
    fig = plt.figure(figsize=(6, 6), dpi=200); ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off()
    fig.patch.set_facecolor(bg1); ax.set_facecolor(bg1)
    a = np.linspace(0, 1, 512)[:, None] if vertical else np.linspace(0, 1, 512)[None, :]
    c1, c2 = np.array(to_rgb(bg1)), np.array(to_rgb(bg2))
    img = c1 * (1 - a[..., None]) + c2 * a[..., None]
    img = np.repeat(img, 2, axis=1) if vertical else np.repeat(img, 2, axis=0)
    ax.imshow(img, extent=extent, aspect="auto", origin="upper", zorder=0, interpolation="bicubic")
    return fig, ax


def lines(ax, xs, ys, cols, lw, glow, alpha=0.88):
    for x, y, c in zip(xs, ys, cols):
        if glow:
            for k, a in [(6, 0.035), (3.2, 0.07), (1.8, 0.16)]: ax.plot(x, y, color=c, lw=lw * k, alpha=a, solid_capstyle="round", zorder=2)
        ax.plot(x, y, color=c, lw=lw, alpha=alpha, solid_capstyle="round", zorder=3)


def ramp(cols, n): cm = LinearSegmentedColormap.from_list("r", cols); return [cm(i / max(1, n - 1)) for i in range(n)]


def save(fig, name):
    png = os.path.join(OUT, name + ".png")
    fig.savefig(png, dpi=200, facecolor=fig.get_facecolor()); plt.close(fig)
    Image.open(png).convert("RGB").resize((800, 800), Image.LANCZOS).save(os.path.join(OUT, name + ".webp"), "WEBP", quality=88, method=6)
    os.remove(png)


def box_x(u, umax): return X0 + (X1 - X0) * np.asarray(u) / umax
def box_y(v): return Y0 + (Y1 - Y0) * np.asarray(v)


def profiles(ax, P, cols, glow, lw=1.25, umax=2.2):
    ns = sorted(P)
    for n, c in zip(ns, ramp(cols, len(ns))):
        u = P[n]["t"] / P[n]["cn"]; keep = u <= umax
        lines(ax, [box_x(u[keep], umax)], [box_y(P[n]["d"][keep])], [c], lw, glow, alpha=0.95)


def threads(ax, t, X, cn, ytrans, col, lw=0.7, alpha=0.30, umax=2.2):
    u = t / cn; keep = u <= umax
    for i in range(X.shape[1]):
        ax.plot(box_x(u[keep], umax), box_y(ytrans(X[keep, i])), color=col, lw=lw, alpha=alpha, solid_capstyle="round", zorder=1)


def jacobi():
    cv = COVERS["dyson-jacobi"]; (bg1, bg2), cols = cv["bg"], cv["lines"]
    fig, ax = canvas(bg1, bg2, vertical=False, extent=(0, 1, 0, 1)); d = R["jacobi"]; p = d["paths"]
    threads(ax, p["t"], p["X"], p["cn"], lambda x: x, cols[-1], lw=0.75, alpha=0.32)
    profiles(ax, d["profiles"], cols, cv["dark"])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); save(fig, "dyson-jacobi")


def laguerre():
    cv = COVERS["dyson-laguerre"]; (bg1, bg2), cols = cv["bg"], cv["lines"]
    fig, ax = canvas(bg1, bg2); d = R["laguerre"]; p = d["paths"]; top = np.sqrt(p["X"].max())
    threads(ax, p["t"], p["X"], p["cn"], lambda x: np.sqrt(np.clip(x, 0, None)) / top, "#ffffff", lw=0.9, alpha=0.55)
    profiles(ax, d["profiles"], cols, cv["dark"], lw=1.4)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); save(fig, "dyson-laguerre")


def metastable():
    cv = COVERS["metastable"]; (bg1, bg2), cols = cv["bg"], cv["lines"]
    fig, ax = canvas(bg1, bg2); m = R["metastable"]; t, X = m["t"], m["X"]; T = t[-1]
    lo, hi = -2.2, 10.6
    yv = lambda x: (np.asarray(x) - lo) / (hi - lo)
    H, _, _ = np.histogram2d(np.repeat(t, X.shape[1]), X.ravel(), bins=[360, 240], range=[[0, T], [lo, hi]])
    H = gaussian_filter(H.T, (1.2, 2.0)); H = (H / H.max()) ** 0.7
    for col, a, k in [(cols[2], 0.55, 1.0), (cols[0], 0.50, 2.2)]:
        rgba = np.zeros(H.shape + (4,)); rgba[..., :3] = to_rgb(col); rgba[..., 3] = a * H ** k
        ax.imshow(rgba, extent=[X0, X1, box_y(0), box_y(1)], origin="lower", aspect="auto", interpolation="bicubic", zorder=1)
    rng = np.random.default_rng(3)
    for i in rng.choice(X.shape[1], 3, replace=False):
        ax.plot(box_x(t[::20], T), box_y(yv(X[::20, i])), color=cols[2], lw=0.5, alpha=0.45, zorder=2)
    lines(ax, [box_x(t[::5], T)], [box_y(yv(X.mean(1)[::5]))], [cols[0]], 1.2, cv["dark"], alpha=0.95)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); save(fig, "metastable")


if __name__ == "__main__":
    jacobi(); laguerre(); metastable(); print("covers written to", os.path.normpath(OUT))
