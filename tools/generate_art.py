"""Generate the hero image and the cover artworks from small simulations.

Each picture is a real simulation of the object studied in the paper/memoir:
  hero      : Dyson Brownian motion (beta = 2), eigenvalues of a Hermitian Brownian matrix
  laguerre  : Dyson-Laguerre process (eigenvalues of a complex Wishart process)
  jacobi    : Dyson-Jacobi process (singular values^2 of a corner of a unitary Brownian motion)
  cutoff    : distance-to-equilibrium profiles d_n(t) with cutoff at t_n = log(n)/2
  turbulence: tracer paths in a random field with Kolmogorov -5/3 spectrum
  nbody     : Vlasov phase mixing (filamentation in a pendulum potential)
  uncertainty: band-limited function on a thick set (Logvinenko-Sereda)
"""
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, to_rgb
from PIL import Image

OUT = sys.argv[1]
rng = np.random.default_rng(20260128)


def canvas(px, bg, w=None):
    w = w or px
    fig = plt.figure(figsize=(w / 200, px / 200), dpi=200)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_axis_off()
    fig.patch.set_facecolor(bg)
    ax.set_facecolor(bg)
    return fig, ax


def gradient_bg(ax, c1, c2, extent, vertical=True, n=512):
    a = np.linspace(0, 1, n)[:, None] if vertical else np.linspace(0, 1, n)[None, :]
    c1, c2 = np.array(to_rgb(c1)), np.array(to_rgb(c2))
    img = c1[None, None, :] * (1 - a[..., None]) + c2[None, None, :] * a[..., None]
    if vertical:
        img = np.repeat(img, 2, axis=1)
    else:
        img = np.repeat(img, 2, axis=0)
    ax.imshow(img, extent=extent, aspect="auto", origin="upper", zorder=0, interpolation="bicubic")


def glow_lines(ax, xs, ys, colors, lw=1.0, alpha=0.9, glow=True):
    for x, y, c in zip(xs, ys, colors):
        if glow:
            for k, a in [(6, 0.035), (3.2, 0.07), (1.8, 0.16)]:
                ax.plot(x, y, color=c, lw=lw * k, alpha=a, solid_capstyle="round", zorder=2)
        ax.plot(x, y, color=c, lw=lw, alpha=alpha, solid_capstyle="round", zorder=3)


def save(fig, name, q=86):
    png = f"{OUT}/{name}.png"
    fig.savefig(png, dpi=200, facecolor=fig.get_facecolor())
    plt.close(fig)
    Image.open(png).convert("RGB").save(f"{OUT}/{name}.webp", "WEBP", quality=q, method=6)
    Image.open(png).convert("RGB").save(f"{OUT}/{name}.jpg", "JPEG", quality=84, optimize=True, progressive=True)


# ---------------------------------------------------------------- Dyson BM (hero)
def dyson_bm(n, steps, T=1.0):
    dt = T / steps
    H = np.zeros((n, n), complex)
    ev = np.zeros((steps + 1, n))
    for k in range(1, steps + 1):
        G = (rng.standard_normal((n, n)) + 1j * rng.standard_normal((n, n))) / np.sqrt(2)
        H += np.sqrt(dt) * (G + G.conj().T) / np.sqrt(2)
        ev[k] = np.linalg.eigvalsh(H)
    return np.linspace(0, T, steps + 1), ev


def hero():
    n, steps = 46, 900
    t, ev = dyson_bm(n, steps)
    W, Hpx = 1800, 1800
    fig, ax = canvas(Hpx, "#31261e", W)
    gradient_bg(ax, "#3d2c22", "#31261e", [-1, 1, 1, 0])
    span = 2 * np.sqrt(n)  # semicircle edge at time 1
    cmap = LinearSegmentedColormap.from_list("h", ["#f6c27a", "#f08a6c", "#d9577a", "#f6c27a"])
    xs, ys, cs = [], [], []
    for i in range(n):
        x = ev[:, i] / span * 1.9
        y = t ** 0.85 * 1.08
        xs.append(x); ys.append(y); cs.append(cmap(abs(i - (n - 1) / 2) / ((n - 1) / 2)))
    glow_lines(ax, xs, ys, cs, lw=0.9, alpha=0.85)
    ax.set_xlim(-1, 1); ax.set_ylim(1, -0.02)
    save(fig, "hero")


def hero_light():
    """Same Dyson Brownian motion as hero(), drawn tone-on-tone for the light sand theme."""
    n, steps = 46, 900
    t, ev = dyson_bm(n, steps)
    W, Hpx = 1800, 1800
    fig, ax = canvas(Hpx, "#c8baa1", W)
    gradient_bg(ax, "#c4b59b", "#c9bba3", [-1, 1, 1, -0.02])
    span = 2 * np.sqrt(n)
    cmap = LinearSegmentedColormap.from_list("hl", ["#8a6a48", "#b4482f", "#8c2c3a", "#8a6a48"])
    xs, ys, cs = [], [], []
    for i in range(n):
        xs.append(ev[:, i] / span * 1.9); ys.append(t ** 0.85 * 1.08)
        cs.append(cmap(abs(i - (n - 1) / 2) / ((n - 1) / 2)))
    for x, y in zip(xs, ys):   # soft light halo under each path
        ax.plot(x, y, color="#e9dfcc", lw=2.6, alpha=0.35, solid_capstyle="round", zorder=2)
    glow_lines(ax, xs, ys, cs, lw=0.9, alpha=0.72, glow=False)
    ax.set_xlim(-1, 1); ax.set_ylim(1, -0.02)
    save(fig, "hero-light")


# ---------------------------------------------------------------- Dyson-Laguerre
def laguerre():
    n, m, steps = 22, 30, 700
    dt = 1 / steps
    X = np.zeros((n, m), complex)
    ev = np.zeros((steps + 1, n))
    for k in range(1, steps + 1):
        X += np.sqrt(dt / 2) * (rng.standard_normal((n, m)) + 1j * rng.standard_normal((n, m)))
        ev[k] = np.linalg.eigvalsh(X @ X.conj().T)
    t = np.linspace(0, 1, steps + 1)
    fig, ax = canvas(1200, "#0e3a37")
    gradient_bg(ax, "#0b2f2d", "#1d6a5b", [0, 1, 1, 0], vertical=False)
    top = ev.max() * 1.04
    cmap = LinearSegmentedColormap.from_list("l", ["#fff3d6", "#bff0d8", "#7fd6c0"])
    xs = [t * 0.92 + 0.04 for _ in range(n)]
    ys = [0.06 + 0.88 * (ev[:, i] / top) ** 0.8 for i in range(n)]
    glow_lines(ax, xs, ys, [cmap(i / (n - 1)) for i in range(n)], lw=1.25)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    save(fig, "cover-dyson-laguerre")


# ---------------------------------------------------------------- Dyson-Jacobi
def jacobi():
    N, p, steps = 40, 18, 900
    dt = 2.2 / steps
    U = np.eye(N, dtype=complex)
    ev = np.zeros((steps + 1, p))
    ev[0] = 1.0
    for k in range(1, steps + 1):
        G = (rng.standard_normal((N, N)) + 1j * rng.standard_normal((N, N))) / np.sqrt(2)
        Hh = (G + G.conj().T) / np.sqrt(2) / np.sqrt(N)
        w, V = np.linalg.eigh(Hh)
        U = U @ (V @ np.diag(np.exp(1j * np.sqrt(dt) * w)) @ V.conj().T)
        A = U[:p, :p]
        ev[k] = np.clip(np.linalg.eigvalsh(A @ A.conj().T), 0, 1)
    t = np.linspace(0, 1, steps + 1)
    fig, ax = canvas(1200, "#ecb3bf")
    gradient_bg(ax, "#f3c6cc", "#e39aac", [0, 1, 1, 0])
    cmap = LinearSegmentedColormap.from_list("j", ["#5b1028", "#8c2342", "#b8405e"])
    xs = [0.06 + 0.88 * ev[:, i] for i in range(p)]
    ys = [0.04 + 0.92 * t ** 0.7 for _ in range(p)]
    glow_lines(ax, xs, ys, [cmap(i / (p - 1)) for i in range(p)], lw=1.3, alpha=0.9, glow=False)
    for x, y, c in zip(xs, ys, [cmap(i / (p - 1)) for i in range(p)]):
        ax.plot(x, y, color=c, lw=4, alpha=0.08)
    ax.set_xlim(0, 1); ax.set_ylim(1, 0)
    save(fig, "cover-dyson-jacobi")


# ---------------------------------------------------------------- cutoff profiles
def cutoff():
    from math import erfc
    fig, ax = canvas(1200, "#1b1442")
    gradient_bg(ax, "#2a1a5e", "#120d2e", [0, 1, 1, 0])
    t = np.linspace(0, 1, 800)
    cmap = LinearSegmentedColormap.from_list("c", ["#ffd1f0", "#c9a2ff", "#7aa8ff"])
    ns = np.unique(np.round(np.geomspace(2, 4e6, 38)).astype(int))
    tmax = np.log(ns.max()) / 2 + 2.5
    xs, ys, cs = [], [], []
    for j, n in enumerate(ns):
        tn = np.log(n) / 2
        s = t * tmax
        d = np.array([0.5 * erfc((x - tn) / (0.9 / np.sqrt(2)) * 1.0) for x in s])
        d = np.minimum(1, d)
        xs.append(0.05 + 0.9 * t); ys.append(0.12 + 0.76 * d); cs.append(cmap(j / (len(ns) - 1)))
    glow_lines(ax, xs, ys, cs, lw=1.0, alpha=0.8)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    save(fig, "cover-cutoff")


# ---------------------------------------------------------------- turbulence
def turbulence():
    K = 60
    k = rng.normal(size=(K, 2))
    k = k / np.linalg.norm(k, axis=1, keepdims=True) * np.geomspace(1.5, 28, K)[:, None]
    amp = np.linalg.norm(k, axis=1) ** (-5 / 6 - 0.5)
    phase = rng.uniform(0, 2 * np.pi, K)

    def vel(x, y, s):
        # divergence-free field from a stream function psi = sum a cos(k.x + phi + w s)
        arg = np.outer(x, k[:, 0]) + np.outer(y, k[:, 1]) + phase + 0.6 * s * np.linalg.norm(k, axis=1) ** (2 / 3)
        sn = np.sin(arg) * amp
        u = -(sn * k[:, 1]).sum(1)
        v = (sn * k[:, 0]).sum(1)
        return u, v

    P = 420
    x = rng.uniform(-0.1, 1.1, P); y = rng.uniform(-0.1, 1.1, P)
    steps, h = 140, 0.0016
    tr = np.zeros((steps, P, 2))
    for s in range(steps):
        tr[s, :, 0], tr[s, :, 1] = x, y
        u, v = vel(x, y, s * h)
        x = x + h * u; y = y + h * v
    fig, ax = canvas(1200, "#c2401f")
    gradient_bg(ax, "#e2622b", "#9c2618", [0, 1, 1, 0])
    cmap = LinearSegmentedColormap.from_list("t", ["#fff1d9", "#ffd29b", "#ffb07a"])
    for i in range(P):
        c = cmap(rng.uniform())
        ax.plot(tr[:, i, 0], tr[:, i, 1], color=c, lw=0.9, alpha=0.75, solid_capstyle="round")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    save(fig, "cover-turbulence")


# ---------------------------------------------------------------- Vlasov phase mixing
def nbody():
    M = 90000
    q = rng.normal(1.5, 0.42, M); p = rng.normal(0.0, 0.30, M)
    dt, T = 0.025, 95.0
    for _ in range(int(T / dt)):  # leapfrog, pendulum H = p^2/2 - cos q
        p -= 0.5 * dt * np.sin(q); q += dt * p; p -= 0.5 * dt * np.sin(q)
    q = (q + np.pi) % (2 * np.pi) - np.pi
    fig, ax = canvas(1200, "#0b1430")
    gradient_bg(ax, "#13214a", "#070d22", [-np.pi, np.pi, 2.6, -2.6])
    e = 0.5 * p ** 2 - np.cos(q)
    cmap = LinearSegmentedColormap.from_list("n", ["#e9f6ff", "#8fd3ff", "#4aa3ff"])
    ax.scatter(q, p, s=0.10, c=cmap((e - e.min()) / (np.ptp(e) + 1e-9)), alpha=0.55, linewidths=0, zorder=3)
    ax.set_xlim(-np.pi, np.pi); ax.set_ylim(-2.6, 2.6)
    save(fig, "cover-nbody")


# ---------------------------------------------------------------- Logvinenko-Sereda
def uncertainty():
    fig, ax = canvas(1200, "#f0c43c")
    gradient_bg(ax, "#f5d35a", "#e7a923", [0, 1, 1, 0])
    # thick set: union of intervals of density gamma in each period
    period, gamma = 0.0625, 0.42
    for a in np.arange(0, 1, period):
        ax.axvspan(a + 0.5 * period * (1 - gamma), a + 0.5 * period * (1 + gamma), color="#1a1408", alpha=0.10, lw=0, zorder=1)
    x = np.linspace(0, 1, 2400)
    for j, (w, a, c) in enumerate([(18, 0.30, "#1a1408"), (26, 0.22, "#3b2a0c"), (34, 0.15, "#5c4210")]):
        f = a * np.sinc(w * (x - 0.5)) * np.cos(2 * np.pi * (w / 2.2) * (x - 0.5))
        ax.plot(x, 0.5 + f + (j - 1) * 0.0, color=c, lw=2.2 - 0.5 * j, alpha=0.95 - 0.2 * j, zorder=3)
    ax.set_xlim(0, 1); ax.set_ylim(0.1, 0.9)
    save(fig, "cover-uncertainty")


# ---------------------------------------------------------------- metastable confinement (OU-cosine mean field)
def metastable():
    N, steps, T = 26, 900, 14.0
    dt = T / steps
    J, sig = 1.2, 0.42
    X = np.sort(rng.normal(0, 0.9, N))
    paths = np.zeros((steps + 1, N)); paths[0] = X
    for k in range(1, steps + 1):
        inter = (J / N) * np.sin(X[None, :] - X[:, None]).sum(1)
        X = X + (-0.55 * X + inter) * dt + sig * np.sqrt(dt) * rng.standard_normal(N)
        paths[k] = X
    # light smoothing so each particle reads as a thread
    ker = np.exp(-np.linspace(-2, 2, 15) ** 2); ker /= ker.sum()
    sm = np.array([np.convolve(np.pad(paths[:, i], 7, mode="edge"), ker, mode="valid") for i in range(N)]).T
    t = np.linspace(0, 1, sm.shape[0])
    fig, ax = canvas(1200, "#3d0d1c")
    gradient_bg(ax, "#5c1428", "#2a0812", [0, 1, 1, 0])
    span = np.abs(sm).max() * 1.1
    # the confining well, drawn as a soft glow band
    yy = np.linspace(0, 1, 600)[:, None]
    glow = np.exp(-((yy - 0.5) / 0.16) ** 2) * 0.16
    rgba = np.zeros((600, 2, 4)); rgba[..., :3] = to_rgb("#ffcfa8"); rgba[..., 3] = np.repeat(glow, 2, axis=1)
    ax.imshow(rgba, extent=[0, 1, 0, 1], aspect="auto", origin="lower", zorder=1, interpolation="bicubic")
    sm = sm[: int(len(sm) * 0.985)]; t = np.linspace(0, 1, sm.shape[0])
    cmap = LinearSegmentedColormap.from_list("m", ["#ffe9c7", "#f6b98a", "#ef8f9c"])
    xs, ys, cs = [], [], []
    for i in range(N):
        xs.append(0.04 + 0.92 * t); ys.append(0.5 + 0.30 * sm[:, i] / span); cs.append(cmap(i / (N - 1)))
    glow_lines(ax, xs, ys, cs, lw=1.0, alpha=0.85)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    save(fig, "cover-metastable")


# ---------------------------------------------------------------- cutoff covers for the two Dyson papers
def cutoff_profiles(ax, colors, n_curves=26, lw=1.15, glow=True, shift=0.0):
    from math import erf
    s = np.linspace(0, 1, 900)
    xs, ys, cs = [], [], []
    for j in range(n_curves):
        steep = 3.2 * (1.16 ** j)                 # windows shrink: profiles converge to a step
        d = np.array([0.5 * (1 - erf((v - 0.5 - shift) * steep)) for v in s])
        xs.append(0.06 + 0.88 * s); ys.append(0.16 + 0.68 * d); cs.append(colors(j / (n_curves - 1)))
    glow_lines(ax, xs, ys, cs, lw=lw, alpha=0.9, glow=glow)


def cover_laguerre_cutoff():
    # faint Dyson-Laguerre paths in the background, cutoff profiles on top — pink
    n, m, steps = 18, 26, 500
    dt = 1 / steps
    X = np.zeros((n, m), complex); ev = np.zeros((steps + 1, n))
    for k in range(1, steps + 1):
        X += np.sqrt(dt / 2) * (rng.standard_normal((n, m)) + 1j * rng.standard_normal((n, m)))
        ev[k] = np.linalg.eigvalsh(X @ X.conj().T)
    t = np.linspace(0, 1, steps + 1)
    fig, ax = canvas(1200, "#f1c3cd")
    gradient_bg(ax, "#f7d6dc", "#e49aae", [0, 1, 1, 0])
    top = ev.max() * 1.05
    for i in range(n):
        ax.plot(0.06 + 0.88 * t, 0.10 + 0.80 * (ev[:, i] / top) ** 0.8, color="#ffffff", lw=0.9, alpha=0.32, zorder=1)
    cmap = LinearSegmentedColormap.from_list("lc", ["#c25a7c", "#8c2342", "#4e0c22"])
    cutoff_profiles(ax, cmap, glow=False, lw=1.35)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    save(fig, "cover-dyson-laguerre")


def cover_jacobi_cutoff():
    # faint Dyson-Jacobi paths in the background, cutoff profiles on top — green
    N, p, steps = 34, 14, 500
    dt = 2.0 / steps
    U = np.eye(N, dtype=complex); ev = np.zeros((steps + 1, p)); ev[0] = 1.0
    for k in range(1, steps + 1):
        G = (rng.standard_normal((N, N)) + 1j * rng.standard_normal((N, N))) / np.sqrt(2)
        Hh = (G + G.conj().T) / np.sqrt(2) / np.sqrt(N)
        w, V = np.linalg.eigh(Hh)
        U = U @ (V @ np.diag(np.exp(1j * np.sqrt(dt) * w)) @ V.conj().T)
        A = U[:p, :p]
        ev[k] = np.clip(np.linalg.eigvalsh(A @ A.conj().T), 0, 1)
    t = np.linspace(0, 1, steps + 1)
    fig, ax = canvas(1200, "#0e3a37")
    gradient_bg(ax, "#0b2f2d", "#1d6a5b", [0, 1, 1, 0], vertical=False)
    for i in range(p):
        ax.plot(0.06 + 0.88 * t, 0.10 + 0.80 * ev[:, i], color="#bff0d8", lw=0.8, alpha=0.18, zorder=1)
    cmap = LinearSegmentedColormap.from_list("jc", ["#fff3d6", "#bff0d8", "#7fd6c0"])
    cutoff_profiles(ax, cmap, lw=1.1)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    save(fig, "cover-dyson-jacobi")


# ---------------------------------------------------------------- metastable jump (as in the paper's Figure 1)
def metastable_jump():
    K, steps = 9, 1400
    t = np.linspace(0, 1, steps)
    lo, hi = 0.24, 0.76
    jumps = np.sort(rng.uniform(0.18, 0.92, K))
    jumps[rng.integers(K)] = 2.0          # one particle system never leaves the well
    fig, ax = canvas(1200, "#3d0d1c")
    gradient_bg(ax, "#5c1428", "#2a0812", [0, 1, 1, 0])
    for y0, a in [(lo, 0.10), (hi, 0.08)]:
        yy = np.linspace(0, 1, 600)[:, None]
        g = np.exp(-((yy - y0) / 0.07) ** 2) * a
        rgba = np.zeros((600, 2, 4)); rgba[..., :3] = to_rgb("#ffcfa8"); rgba[..., 3] = np.repeat(g, 2, axis=1)
        ax.imshow(rgba, extent=[0, 1, 0, 1], aspect="auto", origin="lower", zorder=1, interpolation="bicubic")
    cmap = LinearSegmentedColormap.from_list("mj", ["#ffe9c7", "#f6b98a", "#ef8f9c"])
    xs, ys, cs = [], [], []
    for k in range(K):
        noise = np.convolve(rng.standard_normal(steps), np.ones(9) / 9, mode="same")
        spikes = np.convolve(np.where(rng.uniform(size=steps) < 0.004, rng.exponential(0.035, steps), 0), [0.4, 1, 0.4], mode="same")
        level = np.where(t < jumps[k], lo, hi) + (k - K / 2) * 0.006
        ramp = 1 / (1 + np.exp(np.clip(-(t - jumps[k]) / 0.0015, -60, 60)))      # the jump itself is almost instantaneous
        y = lo + (hi - lo) * ramp + 0.016 * noise + spikes * (1 - ramp) + (k - K / 2) * 0.009
        xs.append(0.05 + 0.90 * t); ys.append(y); cs.append(cmap(k / (K - 1)))
    glow_lines(ax, xs, ys, cs, lw=0.9, alpha=0.85)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    save(fig, "cover-metastable")


which = sys.argv[2:] or ["hero", "laguerre", "jacobi", "cutoff", "turbulence", "nbody", "uncertainty", "metastable"]
for w in which:
    globals()[w]()
    print("done", w)
