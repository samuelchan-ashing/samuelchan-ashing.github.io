import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle

# Ornstein–Uhlenbeck process dX = -X dt + sqrt(2) dB in R^n, started at X_0 = (1, ..., 1); equilibrium N(0, I_n).
# Cutoff at c_n = log(n) / 2: we plot the simulated distance to equilibrium against t / c_n, for n = 2 ... 2^18.
U_MAX = 2.0                                     # time axis: t / c_n from 0 to 2, the cutoff in the middle
NS = sorted({int(round(2 ** (k / 2))) for k in range(2, 37)})


# ------------------------------------------------------------------------------------------- simulation
def simulate_tv(n, u, samples, rng):
    """Monte Carlo estimate of the total variation distance between Law(X_t) and N(0, I_n) at the times t = u c_n.
    X_t = e^{-t} X_0 + sqrt(1 - e^{-2t}) Z with Z ~ N(0, I_n): we draw `samples` vectors Z (n coordinates each) and
    keep S1 = <Z, (1, ..., 1)> and S2 = |Z|^2, which is all the likelihood ratio L = dLaw(X_t) / dN(0, I_n) needs;
    then TV = E[(1 - 1/L)_+] under Law(X_t)."""
    S1, S2 = np.zeros(samples), np.zeros(samples)
    chunk = max(1, (1 << 22) // samples)
    for start in range(0, n, chunk):
        Z = rng.standard_normal((samples, min(chunk, n - start)), dtype=np.float32)
        S1 += Z.sum(1, dtype=np.float64); S2 += np.einsum("ij,ij->i", Z, Z, dtype=np.float64)
    t = np.maximum(np.asarray(u, float), 1e-9)[:, None] * 0.5 * np.log(n)
    e = np.exp(-t); eps = e * e; s = np.sqrt(-np.expm1(-2 * t))
    logL = -0.5 * n * np.log1p(-eps) - 0.5 * eps * (S2 - n) + e * s * S1
    return np.mean(-np.expm1(-np.clip(logL, 0, None)), axis=1)


def profiles(seed=None, samples=8000):
    rng = np.random.default_rng(seed); u = np.linspace(0, U_MAX, 500)
    curves = []
    for n in NS:
        curves.append(simulate_tv(n, u, samples, rng))
        print(f"n = {n} done", flush=True)
    return u, curves


def figure(dark=False, curves=None, seed=None):
    u, ds = curves if curves is not None else profiles(seed)
    bg, block = ("#31271d", "#53402b") if dark else ("#f0ebe3", "#f3dcae")
    cols = ["#eeb760", "#e7889d", "#f4bfcb", "#fdeee6"] if dark else ["#b8862e", "#a72144", "#7d133a", "#4b3317"]
    fig = plt.figure(figsize=(12, 7.5), dpi=200); ax = fig.add_axes([0, 0, 1, 1]); ax.set_axis_off()
    fig.patch.set_facecolor(bg); ax.set_facecolor(bg)
    ax.add_patch(Rectangle((0, .2), .5, .62, color=block, lw=0, zorder=1))   # before the cutoff time
    cm = LinearSegmentedColormap.from_list("r", cols)
    for j, d in enumerate(ds):
        ax.plot(u / U_MAX, .2 + .62 * d, color=cm(j / (len(ds) - 1)), lw=1.1, alpha=.85, zorder=3)
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
    curves = profiles()                         # one simulation, drawn in light and dark
    save(figure(dark=False, curves=curves), "ornstein-uhlenbeck")
    save(figure(dark=True, curves=curves), "ornstein-uhlenbeck-dark")
