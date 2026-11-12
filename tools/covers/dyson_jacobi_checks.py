"""Numerical checks of the Dyson–Jacobi scheme used for the cover (dyson_jacobi.py, same folder), beta = 2, a = b = 2n.

1. Exact moments. For the Dyson–Jacobi process, (E p1, E p2, E p1^2) with p1 = sum x_i, p2 = sum x_i^2 solve a closed
   linear system of ODEs (apply the generator to p1, p2 and p1^2; the repulsion only contributes through
   sum_{i<j} H(x_i, x_j) = (n-1) p1 - (p1^2 - p2)). We compare E p2(t) and Var p1(t) with the scheme, with 95%
   confidence intervals, for several values of theta (step = theta x smallest gap^2): the weak error.
2. Matrix model (here with n = 4, N = 16, for speed). For beta = 2, the eigenvalues of A A^*, A = n x m upper-left block of a Brownian motion U_t on U(N)
   (dU = i dH U - N/2 U dt, E|dH_ij|^2 = dt), form a Dyson–Jacobi process with a = N - m, b = m, on the same time
   scale (Doumerc). U_t is simulated with exponentials exp(i sqrt(h) H) of GUE matrices. No singular drift there:
   an independent way to get the law of p1 at each time, compared with the scheme (two-sample Kolmogorov distance)
   and through the cutoff profile, with bootstrap bands.
Run:  python3 dyson_jacobi_checks.py   (about 10 minutes; writes dyson-jacobi-checks.png and prints a summary)
"""
import os, sys, time
import numpy as np
from scipy.linalg import expm
import matplotlib.pyplot as plt
try:                                            # the scheme lives in dyson_jacobi.py, next to this file
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
except NameError:
    pass
from dyson_jacobi import simulate, equilibrium, ks, start

N_PART, BETA = 8, 2.0
A_, B_ = 2 * N_PART, 2 * N_PART


def exact_moments(n, a, b, x0, times, beta=BETA):
    lam = a + b
    A = np.array([[-lam, 0, 0],
                  [2 + 2 * b + beta * (n - 1), -(2 + 2 * lam - beta), -beta],
                  [2 * n * b + 2, -2, -2 * lam]], float)
    c = np.array([n * b, 0, 0], float)
    v0 = np.array([x0.sum(), (x0 ** 2).sum(), x0.sum() ** 2]); vinf = np.linalg.solve(A, -c)
    V = np.array([vinf + expm(A * t) @ (v0 - vinf) for t in times])
    return V[:, 1], V[:, 2] - V[:, 0] ** 2           # E p2, Var p1


def moments_with_ci(X):
    """E p2 and Var p1 at each time, with 95% half-widths (delta method for the variance)."""
    p1, p2 = X.sum(-1), (X ** 2).sum(-1); M = p1.shape[1]
    m2, h2 = p2.mean(1), 1.96 * p2.std(1) / np.sqrt(M)
    v = p1.var(1); c = p1 - p1.mean(1, keepdims=True)
    hv = 1.96 * np.sqrt(((c ** 2 - v[:, None]) ** 2).mean(1) / M)
    return m2, h2, v, hv


def unitary_model(n, m, Nmat, x0, times, copies, rng, h):
    """Eigenvalues of A A^*, A = U_t[:n, :m], U_t Brownian motion on U(Nmat), started from x0 (principal angles)."""
    th = np.arccos(np.sqrt(x0))
    U = np.tile(np.eye(Nmat, dtype=complex), (copies, 1, 1))
    for i in range(n):                                # rotations in the planes (e_i, e_{m+i}): A A^* = diag(x0)
        c, s = np.cos(th[i]), np.sin(th[i])
        U[:, i, i], U[:, i, m + i], U[:, m + i, i], U[:, m + i, m + i] = c, -s, s, c
    out, t = [], 0.0
    for T in times:
        while T - t > 1e-15:
            k = min(h, T - t)
            G = (rng.standard_normal((copies, Nmat, Nmat)) + 1j * rng.standard_normal((copies, Nmat, Nmat))) / np.sqrt(2)
            w, V = np.linalg.eigh((G + np.conj(np.transpose(G, (0, 2, 1)))) / np.sqrt(2))
            U = (V * np.exp(1j * np.sqrt(k) * w)[:, None, :]) @ np.conj(np.transpose(V, (0, 2, 1))) @ U
            t += k
        A = U[:, :n, :m]
        out.append(np.linalg.eigvalsh(A @ np.conj(np.transpose(A, (0, 2, 1)))))
    return np.array(out)


def bootstrap_ks(sample_t, eq, rng, B=200):
    vals = [ks(rng.choice(s, s.size), eq) for s in sample_t for _ in range(B)]
    v = np.array(vals).reshape(len(sample_t), B)
    return np.quantile(v, 0.025, axis=1), np.quantile(v, 0.975, axis=1)


def main(seed=1, copies=4000):
    rng = np.random.default_rng(seed); n, a, b = N_PART, A_, B_; x0 = start(n)
    eq = equilibrium(n, a, b, 20000, rng).sum(-1)
    cn = np.log(abs(eq.mean() - x0.sum()) / eq.std()) / (a + b)
    times = np.linspace(0, 2.2 * cn, 23)
    Ep2, Vp1 = exact_moments(n, a, b, x0, times)
    fig, axs = plt.subplots(1, 3, figsize=(16, 4.6))
    # ---- 1. weak error against the exact moments
    thetas = [0.4, 0.2, 0.1, 0.05, 0.02]; err = []
    print(f"n = {n}, a = b = {a}, c_n = {cn:.4f}, {copies} copies")
    for th in thetas:
        st = {}; t0 = time.time()
        X = simulate(n, a, b, x0, copies, times, rng, theta=th, stats=st)
        m2, h2, v, hv = moments_with_ci(X)
        e2, ev = np.abs(m2 - Ep2)[1:], np.abs(v - Vp1)[1:]
        err.append((np.max(e2), np.max(h2[1:]), np.max(ev), np.max(hv[1:])))
        print(f"theta = {th:<5}: max|E p2 error| = {err[-1][0]:.4f} (95% CI half-width {err[-1][1]:.4f}), "
              f"max|Var p1 error| = {err[-1][2]:.4f} ({err[-1][3]:.4f}); swaps per million steps = "
              f"{1e6 * st['swaps'] / st['steps']:.1f}; {time.time() - t0:.0f}s", flush=True)
        if th in (0.4, 0.02):
            axs[0].errorbar(times / cn, m2, yerr=h2, fmt="o", ms=3, capsize=2, label=f"scheme, theta = {th}")
    axs[0].plot(times / cn, Ep2, "k-", lw=1.2, label="exact")
    axs[0].set(xlabel="t / c_n", ylabel="E[sum x_i^2]", title=f"Exact second moment (n = {n})"); axs[0].legend()
    E = np.array(err)
    axs[1].errorbar(thetas, E[:, 0], yerr=E[:, 1], fmt="o-", capsize=3, color="C0", label="E[sum x_i^2]")
    axs[1].errorbar(thetas, E[:, 2], yerr=E[:, 3], fmt="s-", capsize=3, color="C1", label="Var(sum x_i)")
    # what Monte Carlo noise alone gives for the largest of 22 errors: about 1.3 x the 95% half-width
    axs[1].plot(thetas, 1.3 * E[:, 1], ":", color="C0", lw=1, label="Monte Carlo noise level")
    axs[1].plot(thetas, 1.3 * E[:, 3], ":", color="C1", lw=1)
    axs[1].set(xscale="log", yscale="log", xlabel="theta (step = theta x gap^2)", ylabel="max error over t",
               title="Weak error vs step (bars: 95% MC)")
    axs[1].set_xticks(thetas); axs[1].set_xticklabels([str(t) for t in thetas]); axs[1].minorticks_off()
    axs[1].legend()
    # ---- 2. matrix model (unitary Brownian motion) against the scheme, through the cutoff profile (n = 4)
    n = 4; a = b = 2 * n; x0 = start(n); m, Nmat = b, a + b
    eq = equilibrium(n, a, b, 20000, rng).sum(-1)
    cn = np.log(abs(eq.mean() - x0.sum()) / eq.std()) / (a + b)
    times = np.linspace(0, 2.2 * cn, 23)
    t0 = time.time()
    Xs = simulate(n, a, b, x0, copies, times, rng, theta=0.02).sum(-1)
    Xm = unitary_model(n, m, Nmat, x0, times, copies, rng, h=0.01 / Nmat).sum(-1)
    Xm2 = unitary_model(n, m, Nmat, x0, times, copies, rng, h=0.005 / Nmat).sum(-1)
    d_s = np.array([ks(p, eq) for p in Xs]); d_m = np.array([ks(p, eq) for p in Xm])
    lo_s, hi_s = bootstrap_ks(Xs, eq, rng); lo_m, hi_m = bootstrap_ks(Xm, eq, rng)
    two = np.array([ks(p, q) for p, q in zip(Xs, Xm)])[1:]
    two_h = np.array([ks(p, q) for p, q in zip(Xm, Xm2)])[1:]
    k = len(two); crit = np.sqrt(-np.log(0.05 / (2 * k)) / 2) * np.sqrt(2 / copies)   # 5%, Bonferroni over the k times
    print(f"matrix model vs scheme: largest two-sample Kolmogorov distance of the law of p1 over {k} times = {two.max():.4f} "
          f"(5% critical value, Bonferroni: {crit:.4f}); matrix model, step h vs h/2: {two_h.max():.4f}; {time.time() - t0:.0f}s")
    u = times / cn
    axs[2].fill_between(u, lo_s, hi_s, alpha=.25, color="C0"); axs[2].plot(u, d_s, "C0-", label="Euler scheme (theta = 0.02)")
    axs[2].fill_between(u, lo_m, hi_m, alpha=.25, color="C3"); axs[2].plot(u, d_m, "C3--", label="matrix model (unitary BM)")
    axs[2].set(xlabel="t / c_n", ylabel="Kolmogorov distance of sum x_i to equilibrium",
               title=f"Cutoff profile (n = {n}): scheme vs matrix model"); axs[2].legend()
    fig.tight_layout()
    try:
        folder = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        folder = os.getcwd()
    path = os.path.join(folder, "dyson-jacobi-checks.png"); fig.savefig(path, dpi=150); plt.close(fig)
    print("wrote", path)


if __name__ == "__main__":
    main()
