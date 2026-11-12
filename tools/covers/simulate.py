"""Real simulations behind the three paper covers (run: python3 tools/covers/simulate.py, about 20 minutes;
then python3 tools/covers/paint.py). The covers on the site were made with this code, run in several pieces, so a new
run gives the same pictures up to the random draws.

Dyson–Laguerre (arXiv:2509.19798, eq. 1.1), beta = 2:
    dX^i = sqrt(2 X^i) dB^i + ( alpha - X^i + (beta/2) sum_{j!=i} (X^i + X^j)/(X^i - X^j) ) dt
    invariant law  prod x_i^{alpha-(n-1)beta/2-1} e^{-x_i} prod |x_i-x_j|^beta
    -> for beta = 2 and alpha = m integer: eigenvalues of a complex Wishart matrix G G*, G n x m standard complex Gaussian.
Dyson–Jacobi (arXiv:2601.20390, eq. 1.1), beta = 2:
    dX^i = sqrt(2 X^i (1-X^i)) dB^i + ( b - (a+b) X^i + (beta/2) sum_{j!=i} H(X^i,X^j)/(X^i-X^j) ) dt,  H(x,y) = x(1-y)+y(1-x)
    invariant law  prod x^{b-(n-1)beta/2-1} (1-x)^{a-(n-1)beta/2-1} prod |x_i-x_j|^beta
    -> for beta = 2, a = m2, b = m1 integers: eigenvalues of W1 (W1+W2)^{-1} (complex MANOVA), W_k complex Wishart n x m_k.
Metastability (Samuel's notebook metacos_rapport.ipynb):
    dX^i = -X^i dt + (1/N) sum_j J cos(X^j) dt + sigma dB^i,  sigma = sqrt 2, J = sqrt(50 e), N = 80, X_0^i ~ N(alpha, 1), alpha = 6.6358…

Each diffusion is integrated with Euler–Maruyama, with a step adapted to the smallest gap between particles (so the
repulsion never makes two particles cross), and particles re-sorted after each step as a safeguard.
The cutoff profiles are measured, not drawn: for several n we run M independent copies from the same initial condition
and compute, at each time, the Kolmogorov distance between the law of the linear statistic phi = x_1 + ... + x_n at time t
and its law under the exact invariant measure (sampled from the matrix model). This is a lower bound for the total
variation distance to equilibrium.
"""
import numpy as np, pickle, time, sys

import os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "simulations.pkl")


def ks_distance(a, b):
    """sup_x |F_a(x) - F_b(x)| for two samples."""
    a = np.sort(a); b = np.sort(b); z = np.concatenate([a, b])
    return np.max(np.abs(np.searchsorted(a, z, "right") / a.size - np.searchsorted(b, z, "right") / b.size))


def cwishart(n, m, M, rng):
    G = (rng.standard_normal((M, n, m)) + 1j * rng.standard_normal((M, n, m))) / np.sqrt(2)
    return G @ np.conj(np.transpose(G, (0, 2, 1)))


# ---------------------------------------------------------------- Dyson–Laguerre
def laguerre_drift(X, alpha, beta):
    D = X[..., :, None] - X[..., None, :]
    S = X[..., :, None] + X[..., None, :]
    np.einsum("...ii->...i", D)[...] = 1.0
    R = S / D
    np.einsum("...ii->...i", R)[...] = 0.0
    return alpha - X + 0.5 * beta * R.sum(-1)


def run_laguerre_matrix(n, m, M, T, rng, record, M0=None):
    """beta = 2, alpha = m: eigenvalues of M_t M_t^*, where M_t (n x m, complex) is the Ornstein–Uhlenbeck matrix
    dM = -1/2 M dt + dW with E|dW_ij|^2 = dt. Its transitions are Gaussian, so the simulation is exact in law
    (Bru / König–O'Connell: the eigenvalues then solve the Dyson–Laguerre SDE above with beta = 2, alpha = m)."""
    Z = np.zeros((M, n, m), complex) if M0 is None else np.tile(M0, (M, 1, 1)).astype(complex)
    out, t = [], 0.0
    for tr in record:
        h = tr - t
        if h > 0:
            G = (rng.standard_normal(Z.shape) + 1j * rng.standard_normal(Z.shape)) / np.sqrt(2)
            Z = np.exp(-h / 2) * Z + np.sqrt(1 - np.exp(-h)) * G
            t = tr
        out.append(np.linalg.eigvalsh(Z @ np.conj(np.transpose(Z, (0, 2, 1)))))
    return out


def run_laguerre(n, alpha, beta, x0, M, T, rng, record=None, theta=0.02, dt_max=2e-3):
    X = np.tile(x0, (M, 1)).astype(float)
    t, k = 0.0, 0
    grid = np.asarray(record) if record is not None else np.array([])
    out, ti = [], 0
    while ti < grid.size and grid[ti] <= 0: out.append(X.copy()); ti += 1
    while t < T:
        gap = np.min(np.diff(X, axis=-1)) if n > 1 else 1.0
        dt = min(dt_max, theta * gap ** 2 / max(1.0, X.max()), T - t)
        dt = max(dt, 1e-9)
        X = X + laguerre_drift(X, alpha, beta) * dt + np.sqrt(2 * np.clip(X, 0, None) * dt) * rng.standard_normal(X.shape)
        X = np.sort(np.clip(X, 1e-12, None), axis=-1)
        t += dt; k += 1
        while ti < grid.size and grid[ti] <= t + 1e-12: out.append(X.copy()); ti += 1
    return X, out, k


# ---------------------------------------------------------------- Dyson–Jacobi
def jacobi_drift(X, a, b, beta):
    D = X[..., :, None] - X[..., None, :]
    H = X[..., :, None] * (1 - X[..., None, :]) + X[..., None, :] * (1 - X[..., :, None])
    np.einsum("...ii->...i", D)[...] = 1.0
    R = H / D
    np.einsum("...ii->...i", R)[...] = 0.0
    return b - (a + b) * X + 0.5 * beta * R.sum(-1)


def run_jacobi(n, a, b, beta, x0, M, T, rng, record=None, theta=0.02, dt_max=2e-4, robust=True):
    X = np.tile(x0, (M, 1)).astype(float)
    t, k = 0.0, 0
    grid = np.asarray(record) if record is not None else np.array([])
    out, ti = [], 0
    while ti < grid.size and grid[ti] <= 0: out.append(X.copy()); ti += 1
    while t < T:
        # step from the typical smallest gap among the copies (robust=True), or from the smallest one overall
        g = np.minimum(np.min(np.diff(X, axis=-1), axis=-1) if n > 1 else 1.0, np.minimum(X[:, 0], 1 - X[:, -1]))
        gap = np.median(g) if robust else g.min()
        dt = min(dt_max, theta * gap ** 2, T - t)
        dt = max(dt, 1e-10)
        X = X + jacobi_drift(X, a, b, beta) * dt + np.sqrt(2 * np.clip(X * (1 - X), 0, None) * dt) * rng.standard_normal(X.shape)
        X = np.sort(np.clip(X, 1e-12, 1 - 1e-12), axis=-1)
        t += dt; k += 1
        while ti < grid.size and grid[ti] <= t + 1e-12: out.append(X.copy()); ti += 1
    return X, out, k


def manova(n, m1, m2, M, rng):
    W1 = cwishart(n, m1, M, rng); W2 = cwishart(n, m2, M, rng)
    # eigenvalues of W1 (W1+W2)^{-1} = generalized eigenproblem; use L^{-1} W1 L^{-*} with W1+W2 = L L*
    L = np.linalg.cholesky(W1 + W2); Li = np.linalg.inv(L)
    return np.linalg.eigvalsh(Li @ W1 @ np.conj(np.transpose(Li, (0, 2, 1))))


# ---------------------------------------------------------------- metastable cosine model
def run_metastable(N=80, T=800.0, dt=0.01, seed=6, keep_every=10):
    sigma, J = np.sqrt(2.0), np.sqrt(50.0 * np.e)
    A = J * np.exp(-sigma ** 2 / 4)
    from scipy.optimize import brentq
    g = lambda m: m - A * np.cos(m)
    grid = np.linspace(-A - .1, A + .1, 100000); sc = np.where(np.diff(np.signbit(g(grid))))[0]
    roots = np.array(sorted(brentq(g, grid[i], grid[i + 1]) for i in sc))
    stable = roots[1 + A * np.sin(roots) > 0]; unstable = roots[1 + A * np.sin(roots) <= 0]
    alpha = stable.max()
    rng = np.random.default_rng(seed)
    X = rng.normal(alpha, 1.0, N); n = int(T / dt)
    paths = np.empty((n // keep_every + 1, N)); I = np.empty(n // keep_every + 1)
    paths[0] = X; I[0] = (J * np.cos(X)).mean(); s = sigma * np.sqrt(dt)
    for k in range(n):
        X = X + (-X + (J * np.cos(X)).mean()) * dt + s * rng.standard_normal(N)
        if (k + 1) % keep_every == 0:
            paths[(k + 1) // keep_every] = X; I[(k + 1) // keep_every] = (J * np.cos(X)).mean()
    t = np.arange(paths.shape[0]) * dt * keep_every
    return dict(t=t, X=paths, I=I, stable=stable, unstable=unstable, alpha=alpha, N=N, J=J, sigma=sigma, seed=seed)


if __name__ == "__main__":
    what = sys.argv[1:] or ["laguerre", "jacobi", "metastable"]
    R = pickle.load(open(OUT, "rb")) if len(sys.argv) > 1 and __import__("os").path.exists(OUT) else {}
    rng = np.random.default_rng(20260128)
    if "laguerre" in what:
        beta = 2.0; L = {}
        for n in [2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64]:
            alpha = 2 * n                      # alpha = m = 2n (rectangular n x 2n matrices)
            eq = np.real(np.trace(cwishart(n, alpha, 8000, rng), axis1=1, axis2=2))
            # start: all particles at the hard edge 0 (M_0 = 0). c_n = time at which the mean of phi, which relaxes
            # like e^{-t}, is one equilibrium standard deviation away = 1/2 log(alpha n), the paper's lower bound
            cn = np.log(abs(eq.mean()) / eq.std())
            ts = np.linspace(0, 2.2 * cn, 120)
            M = 4000 if n <= 32 else (2500 if n == 48 else 2000)
            t0 = time.time()
            snaps = run_laguerre_matrix(n, alpha, M, ts[-1], rng, ts)
            d = np.array([ks_distance(s.sum(-1), eq) for s in snaps])
            L[n] = dict(t=ts, d=d, cn=cn, alpha=alpha, M=M)
            print(f"laguerre n={n:3d} M={M} {time.time()-t0:.0f}s  c_n={cn:.3f} (1/2 log(alpha n)={0.5*np.log(alpha*n):.3f})  d(0)={d[0]:.2f} d(c_n)={d[np.searchsorted(ts, cn)]:.2f} d(end)={d[-1]:.3f}", flush=True)
        n = 40; alpha = 2 * n; cn = 0.5 * np.log(alpha * n)
        ts = np.linspace(0, 2.2 * cn, 900)
        snaps = run_laguerre_matrix(n, alpha, 1, ts[-1], np.random.default_rng(7), ts)
        eqv = np.sort(np.linalg.eigvalsh(cwishart(n, alpha, 400, rng)).ravel())
        R["laguerre"] = dict(profiles=L, paths=dict(t=ts, X=np.array([s[0] for s in snaps]), n=n, alpha=alpha, cn=cn, eq=eqv), beta=beta)
        pickle.dump(R, open(OUT, "wb"))
    if "jacobi" in what:
        beta = 2.0; Jd = {}
        for n in [2, 3, 4, 6, 8, 12, 16, 24, 32]:
            a = b = 2 * n                      # a = b = 2n (complex MANOVA with m1 = m2 = 2n)
            x0 = 0.75 + 0.25 * (np.arange(n) + 0.5) / n   # all particles in the top quarter [0.75, 1)
            lam = a + b                        # spectral gap: the mean of phi relaxes like e^{-(a+b) t}
            eq = manova(n, b, a, 6000, rng).sum(-1)   # m1 = b (weight x^{b-n}), m2 = a (weight (1-x)^{a-n})
            cn = np.log(abs(eq.mean() - x0.sum()) / eq.std()) / lam
            ts = np.linspace(0, 2.2 * cn, 120)
            M = {2: 3000, 3: 3000, 4: 3000, 6: 2500, 8: 2000, 12: 1500, 16: 1000, 24: 700, 32: 400}[n]
            t0 = time.time()
            _, snaps, steps = run_jacobi(n, a, b, beta, x0, M, ts[-1], rng, record=ts)
            d = np.array([ks_distance(s.sum(-1), eq) for s in snaps])
            Jd[n] = dict(t=ts, d=d, cn=cn, a=a, b=b, M=M, steps=steps)
            print(f"jacobi   n={n:3d} M={M} steps={steps} {time.time()-t0:.0f}s  d(0)={d[0]:.2f} d(cn)={d[np.searchsorted(ts, cn)]:.2f} d(end)={d[-1]:.3f}", flush=True)
        n = 40; a = b = 2 * n; x0 = 0.75 + 0.25 * (np.arange(n) + 0.5) / n; lam = a + b
        eqs = manova(n, b, a, 3000, rng).sum(-1); cn = np.log(abs(eqs.mean() - x0.sum()) / eqs.std()) / lam
        ts = np.linspace(0, 2.2 * cn, 900)
        _, snaps, _ = run_jacobi(n, a, b, beta, x0, 1, ts[-1], np.random.default_rng(7), record=ts)
        eqv = np.sort(manova(n, b, a, 400, rng).ravel())
        R["jacobi"] = dict(profiles=Jd, paths=dict(t=ts, X=np.array([s[0] for s in snaps]), n=n, a=a, b=b, cn=cn, eq=eqv), beta=beta)
        pickle.dump(R, open(OUT, "wb"))
    if "metastable" in what:
        R["metastable"] = run_metastable()
        pickle.dump(R, open(OUT, "wb"))
        m = R["metastable"]; I = m["I"]; sad = m["unstable"][m["unstable"] < m["alpha"]].max()
        cross = np.where(I < sad)[0]
        print("metastable: stable", np.round(m["stable"], 3), "first crossing t =", m["t"][cross[0]] if cross.size else None)
