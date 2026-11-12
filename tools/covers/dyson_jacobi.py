import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, to_rgb

BG = ("#004f46", "#002e28")                     # Sanzo Wada: Dusky Green · Ivory Buff
LINES = ["#ebd3a2", "#cfe3c9", "#9cc9b4"]
U_MAX = 2.2
BETA = 2.0


# ------------------------------------------------------------------------------------------- simulation
def drift(X, a, b):
    D = X[:, :, None] - X[:, None, :]
    H = X[:, :, None] * (1 - X[:, None, :]) + X[:, None, :] * (1 - X[:, :, None])
    np.einsum("kii->ki", D)[...] = 1.0
    R = H / D
    np.einsum("kii->ki", R)[...] = 0.0
    return b - (a + b) * X + 0.5 * BETA * R.sum(-1)


def simulate(n, a, b, x0, copies, times, rng, theta=0.05, dt_max=2e-4, stats=None):
    """Euler–Maruyama scheme in which every copy has its own clock and its own step
        dt = theta * (smallest gap of that copy)^2,
    the gaps including the distances to 0 and 1: one step moves a particle by a small fraction of the distance to its
    neighbours, which keeps the singular repulsion under control. The record times are hit exactly, and a copy stops
    once it has reached the last one. If two particles still swap during a step, the copy is re-sorted; `stats`
    (a dict) receives how often that happened. With theta = 0.05, no bias is detectable at Monte Carlo precision
    (exact moments, and the beta = 2 matrix model) and swaps happen about once every 3 million steps."""
    times = np.asarray(times, float); last = len(times)
    X = np.tile(np.asarray(x0, float), (copies, 1))
    out = np.empty((last, copies, n))
    t, nxt = np.zeros(copies), np.zeros(copies, int)
    steps = swaps = 0
    while True:
        due = np.flatnonzero((nxt < last) & (times[np.minimum(nxt, last - 1)] <= t))
        while due.size:                         # record the copies that have reached their next time
            out[nxt[due], due] = X[due]; nxt[due] += 1
            due = due[(nxt[due] < last) & (times[np.minimum(nxt[due], last - 1)] <= t[due])]
        act = np.flatnonzero(nxt < last)
        if act.size == 0: break
        Xa = X[act]
        gaps = np.minimum(np.diff(Xa, axis=1).min(1) if n > 1 else 1.0, np.minimum(Xa[:, 0], 1 - Xa[:, -1]))
        left = times[nxt[act]] - t[act]
        dt = np.minimum(np.minimum(dt_max, theta * gaps ** 2), left)
        Xa = Xa + drift(Xa, a, b) * dt[:, None] + np.sqrt(2 * np.clip(Xa * (1 - Xa), 0, None) * dt[:, None]) * rng.standard_normal(Xa.shape)
        bad = (np.diff(Xa, axis=1) <= 0).any(1) if n > 1 else np.zeros(act.size, bool)
        swaps += int(bad.sum()); steps += act.size
        X[act] = np.sort(np.clip(Xa, 1e-12, 1 - 1e-12), axis=1)
        t[act] = np.where(dt >= left, times[nxt[act]], t[act] + dt)
    if stats is not None: stats.update(steps=steps, swaps=swaps)
    return out                                  # shape (len(times), copies, n)


def equilibrium(n, a, b, copies, rng):
    """Exact samples of the invariant law (beta = 2): eigenvalues of W1 (W1 + W2)^{-1}."""
    def wishart(m):
        G = (rng.standard_normal((copies, n, m)) + 1j * rng.standard_normal((copies, n, m))) / np.sqrt(2)
        return G @ np.conj(np.transpose(G, (0, 2, 1)))
    W1, W2 = wishart(b), wishart(a)
    Li = np.linalg.inv(np.linalg.cholesky(W1 + W2))
    return np.linalg.eigvalsh(Li @ W1 @ np.conj(np.transpose(Li, (0, 2, 1))))


def ks(a, b):
    a, b = np.sort(a), np.sort(b); z = np.concatenate([a, b])
    return np.max(np.abs(np.searchsorted(a, z, "right") / a.size - np.searchsorted(b, z, "right") / b.size))


def start(n): return 0.75 + 0.25 * (np.arange(n) + 0.5) / n


def profile(n, copies, rng):
    a = b = 2 * n
    eq = equilibrium(n, a, b, 6000, rng).sum(-1)
    cn = np.log(abs(eq.mean() - start(n).sum()) / eq.std()) / (a + b)
    u = np.linspace(0, U_MAX, 120)
    phi = simulate(n, a, b, start(n), copies, u * cn, rng).sum(-1)
    return u, np.array([ks(p, eq) for p in phi]), cn


# ------------------------------------------------------------------------------------------- drawing
def ramp(cols, k): cm = LinearSegmentedColormap.from_list("r", cols); return [cm(i / max(1, k - 1)) for i in range(k)]


def glow_line(ax, x, y, c, lw):
    for k, al in [(6, 0.035), (3.2, 0.07), (1.8, 0.16)]: ax.plot(x, y, color=c, lw=lw * k, alpha=al, solid_capstyle="round", zorder=2)
    ax.plot(x, y, color=c, lw=lw, alpha=0.95, solid_capstyle="round", zorder=3)


def figure(seed=None):
    rng = np.random.default_rng(seed)
    fig = plt.figure(figsize=(6, 6), dpi=200); ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off()
    a = np.linspace(0, 1, 512)[None, :, None]
    ax.imshow(np.repeat(np.array(to_rgb(BG[0])) * (1 - a) + np.array(to_rgb(BG[1])) * a, 2, axis=0),
              extent=(0, 1, 0, 1), aspect="auto", zorder=0, interpolation="bicubic")
    X0, X1, Y0, Y1 = 0.06, 0.94, 0.14, 0.86
    bx = lambda u: X0 + (X1 - X0) * np.asarray(u) / U_MAX
    by = lambda v: Y0 + (Y1 - Y0) * np.asarray(v)
    # one path with n = 40 particles
    n = 40; aa = bb = 2 * n
    eq = equilibrium(n, aa, bb, 3000, rng).sum(-1)
    cn = np.log(abs(eq.mean() - start(n).sum()) / eq.std()) / (aa + bb)
    u = np.linspace(0, U_MAX, 900)
    X = simulate(n, aa, bb, start(n), 1, u * cn, rng)[:, 0, :]
    for i in range(n):
        ax.plot(bx(u), by(X[:, i]), color=LINES[-1], lw=0.75, alpha=0.32, solid_capstyle="round", zorder=1)
    # measured cutoff profiles
    copies = {2: 4000, 3: 4000, 4: 4000, 6: 3000, 8: 3000, 12: 2000, 16: 1500, 24: 1000, 32: 800}
    for (n, m), c in zip(copies.items(), ramp(LINES, len(copies))):
        u, d, _ = profile(n, m, rng)
        glow_line(ax, bx(u), by(d), c, 1.25)
        print(f"n = {n:2d} done", flush=True)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    return fig


# ------------------------------------------------------------------------------------------- output
def save(fig, name):
    """Write name.png next to this script (or in the current folder when the code is pasted in a notebook)."""
    try:
        folder = os.path.dirname(os.path.abspath(__file__))
    except NameError:                           # no file: code pasted into a notebook or a Python prompt
        folder = os.getcwd()
    path = os.path.join(folder, name + ".png")
    fig.savefig(path, dpi=200, facecolor=fig.get_facecolor()); plt.close(fig)
    print("wrote", path)
    try:                                        # in a notebook, show the picture as well
        from IPython import get_ipython
        from IPython.display import Image, display
        shell = get_ipython()
        if shell is not None and "IPKernelApp" in shell.config: display(Image(path, width=480))
    except ImportError:
        pass
    return path


if __name__ == "__main__":
    save(figure(), "dyson-jacobi")
