import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, to_rgb

BG = ("#f8b6ba", "#f5d0c4")                     # Sanzo Wada: Corinthian Pink · Brick Red
LINES = ["#d4785a", "#a84222", "#6e2a14"]
U_MAX = 2.2                                     # time axis: t / c_n from 0 to 2.2


# ------------------------------------------------------------------------------------------- simulation
def eigenvalue_paths(n, m, times, copies, rng):
    """Exact simulation of the eigenvalues of M_t M_t^* at the given times (M_0 = 0)."""
    M = np.zeros((copies, n, m), complex)
    out, t = [], 0.0
    for s in times:
        h = s - t
        if h > 0:                               # exact Gaussian transition of the OU matrix over a step h
            G = (rng.standard_normal(M.shape) + 1j * rng.standard_normal(M.shape)) / np.sqrt(2)
            M = np.exp(-h / 2) * M + np.sqrt(1 - np.exp(-h)) * G
            t = s
        out.append(np.linalg.eigvalsh(M @ np.conj(np.transpose(M, (0, 2, 1)))))
    return np.array(out)                        # shape (len(times), copies, n)


def ks(a, b):
    """Kolmogorov distance between two samples."""
    a, b = np.sort(a), np.sort(b); z = np.concatenate([a, b])
    return np.max(np.abs(np.searchsorted(a, z, "right") / a.size - np.searchsorted(b, z, "right") / b.size))


def trace_samples(n, m, samples, rng):
    """tr(G G^*) for `samples` simulated n x m matrices G with independent standard complex Gaussian entries."""
    T, k = np.zeros(samples), 2 * n * m         # 2 n m real numbers: real and imaginary parts
    chunk = max(1, (1 << 22) // samples)
    for start in range(0, k, chunk):
        Z = rng.standard_normal((samples, min(chunk, k - start)), dtype=np.float32)
        T += np.einsum("ij,ij->i", Z, Z, dtype=np.float64)
    return T / 2


def profile(n, u, samples, rng):
    """Kolmogorov distance between the law of the sum X^1_t + ... + X^n_t and its equilibrium law, at t = u c_n,
    c_n = 1/2 log(alpha n). The sum of the particles is tr(M_t M_t^*), and from M_0 = 0 the matrix M_t has the law of
    sqrt(1 - e^{-t}) G: we simulate G, and an independent copy for the equilibrium."""
    T, eq = trace_samples(n, 2 * n, samples, rng), trace_samples(n, 2 * n, samples, rng)
    t = np.asarray(u) * 0.5 * np.log(2 * n * n)
    return np.array([ks(-np.expm1(-s) * T, eq) for s in t])


# ------------------------------------------------------------------------------------------- drawing
def ramp(cols, k): cm = LinearSegmentedColormap.from_list("r", cols); return [cm(i / max(1, k - 1)) for i in range(k)]


def figure(seed=None):
    fig = plt.figure(figsize=(6, 6), dpi=200); ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off()
    a = np.linspace(0, 1, 512)[:, None, None]
    ax.imshow(np.repeat(np.array(to_rgb(BG[0])) * (1 - a) + np.array(to_rgb(BG[1])) * a, 2, axis=1),
              extent=(0, 1, 1, 0), aspect="auto", zorder=0, interpolation="bicubic")
    X0, X1, Y0, Y1 = 0.06, 0.94, 0.14, 0.86
    bx = lambda u: X0 + (X1 - X0) * np.asarray(u) / U_MAX
    by = lambda v: Y0 + (Y1 - Y0) * np.asarray(v)
    # one path with n = 40 particles
    n = 40; cn = 0.5 * np.log(2 * n * n); u = np.linspace(0, U_MAX, 900)
    X = eigenvalue_paths(n, 2 * n, u * cn, 1, np.random.default_rng(seed))[:, 0, :]
    S = np.sqrt(np.clip(X, 0, None)); S /= S.max()
    for i in range(n):
        ax.plot(bx(u), by(S[:, i]), color="#ffffff", lw=0.9, alpha=0.55, solid_capstyle="round", zorder=1)
    # simulated cutoff profiles, n = 2 ... 256
    rng = np.random.default_rng(None if seed is None else seed + 1)
    ns = [2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 96, 128, 192, 256]; u = np.linspace(0, U_MAX, 400)
    for n, c in zip(ns, ramp(LINES, len(ns))):
        ax.plot(bx(u), by(profile(n, u, 6000, rng)), color=c, lw=1.2, alpha=0.92, solid_capstyle="round", zorder=3)
        print(f"n = {n} done", flush=True)
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
    save(figure(), "dyson-laguerre")
