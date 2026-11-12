import os
import numpy as np
from scipy.optimize import brentq
from scipy.ndimage import gaussian_filter
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb

BG = ("#a72144", "#520b1d")                     # Sanzo Wada: Red · Pale Lemon Yellow
LINES = ["#ffefae", "#eeb760", "#f9c1ce"]
N, SIGMA, J = 80, np.sqrt(2.0), np.sqrt(50.0 * np.e)


def equilibria():
    """Solutions of m = A cos(m), and whether they are stable for dm/dt = -m + A cos(m)."""
    A = J * np.exp(-SIGMA ** 2 / 4)
    g = lambda m: m - A * np.cos(m)
    grid = np.linspace(-A - 0.1, A + 0.1, 100_000)
    roots = np.array([brentq(g, grid[i], grid[i + 1]) for i in np.where(np.diff(np.signbit(g(grid))))[0]])
    return roots, 1 + A * np.sin(roots) > 0


def simulate(T=800.0, dt=0.01, seed=None, keep_every=10):
    roots, stable = equilibria()
    alpha = roots[stable].max()                 # upper well, 6.636
    rng = np.random.default_rng(seed)
    X = rng.normal(alpha, 1.0, N)
    steps = int(T / dt); paths = np.empty((steps // keep_every + 1, N)); paths[0] = X
    for k in range(steps):
        X = X + (-X + (J * np.cos(X)).mean()) * dt + SIGMA * np.sqrt(dt) * rng.standard_normal(N)
        if (k + 1) % keep_every == 0: paths[(k + 1) // keep_every] = X
    return np.arange(paths.shape[0]) * dt * keep_every, paths


def figure(seed=None):
    t, X = simulate(seed=seed); T = t[-1]
    fig = plt.figure(figsize=(6, 6), dpi=200); ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off()
    a = np.linspace(0, 1, 512)[:, None, None]
    ax.imshow(np.repeat(np.array(to_rgb(BG[0])) * (1 - a) + np.array(to_rgb(BG[1])) * a, 2, axis=1),
              extent=(0, 1, 1, 0), aspect="auto", zorder=0, interpolation="bicubic")
    X0, X1, Y0, Y1 = 0.06, 0.94, 0.14, 0.86
    lo, hi = -2.2, 10.6                         # positions shown
    bx = lambda s: X0 + (X1 - X0) * np.asarray(s) / T
    by = lambda x: Y0 + (Y1 - Y0) * (np.asarray(x) - lo) / (hi - lo)
    # density of the cloud
    H, _, _ = np.histogram2d(np.repeat(t, N), X.ravel(), bins=[360, 240], range=[[0, T], [lo, hi]])
    H = gaussian_filter(H.T, (1.2, 2.0)); H = (H / H.max()) ** 0.7
    for col, al, k in [(LINES[2], 0.55, 1.0), (LINES[0], 0.50, 2.2)]:
        rgba = np.zeros(H.shape + (4,)); rgba[..., :3] = to_rgb(col); rgba[..., 3] = al * H ** k
        ax.imshow(rgba, extent=[X0, X1, Y0, Y1], origin="lower", aspect="auto", interpolation="bicubic", zorder=1)
    # three particles, and the mean
    for i in np.random.default_rng(3).choice(N, 3, replace=False):
        ax.plot(bx(t[::20]), by(X[::20, i]), color=LINES[2], lw=0.5, alpha=0.45, zorder=2)
    x, y = bx(t[::5]), by(X.mean(1)[::5])
    for k, al in [(6, 0.035), (3.2, 0.07), (1.8, 0.16)]: ax.plot(x, y, color=LINES[0], lw=1.2 * k, alpha=al, zorder=3)
    ax.plot(x, y, color=LINES[0], lw=1.2, alpha=0.95, zorder=4)
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
    save(figure(), "metastable")
