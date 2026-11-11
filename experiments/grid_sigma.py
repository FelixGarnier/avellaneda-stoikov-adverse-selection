"""Profit, inventory dispersion, and fill counts on a grid of sigma and pi.

Gamma is fixed at 0.1. Paths are redrawn for each sigma with the same seed,
so the shock signs match and only the amplitude changes. A higher sigma both
widens the quote, through the gamma * sigma**2 term, and makes the mid move
farther over the informed traders' horizon.
"""

import numpy as np
from avellaneda_stoikov.price import simulate_mid_price
from avellaneda_stoikov.simulator import run_inventory, run_noskew, run_symmetric

S0 = 100.0
gamma = 0.1
T = 1.0
dt = 0.005
k = 1.5
A = 140.0
tau = 0.1
n_paths = 20000
sigmas = [1.0, 2.0, 4.0]
pis = [0.0, 0.5, 1.0]

def interval(x):
    return 1.96 * np.std(x) / np.sqrt(len(x))

print(
    f"{'sigma':>6} {'pi':>4} {'strategy':<10} {'spread':>7} "
    f"{'profit':>8} {'+/-':>6} {'std_q':>6} {'fills':>7}"
)

for sigma in sigmas:
    paths = simulate_mid_price(S0, sigma, T, dt, n_paths, np.random.default_rng(0))
    for pi in pis:
        pnl, q, fills, spread = run_inventory(
            paths, gamma=gamma, sigma=sigma, k=k, A=A, T=T, dt=dt,
            rng=np.random.default_rng(1),
            pi=pi, tau=tau, rng_info=np.random.default_rng(2),
        )
        pnl_n, q_n, fills_n, spread_n = run_noskew(
            paths, gamma=gamma, sigma=sigma, k=k, A=A, T=T, dt=dt,
            rng=np.random.default_rng(1),
            pi=pi, tau=tau, rng_info=np.random.default_rng(2),
        )
        pnl_s, q_s, fills_s, spread_s = run_symmetric(
            paths, spread, A=A, k=k, dt=dt,
            rng=np.random.default_rng(1),
            pi=pi, tau=tau, rng_info=np.random.default_rng(2),
        )
        for name, profit, inventory, n_fills, spr in (
            ("inventory", pnl, q, fills, spread),
            ("noskew", pnl_n, q_n, fills_n, spread_n),
            ("symmetric", pnl_s, q_s, fills_s, spread_s),
        ):
            print(
                f"{sigma:6.1f} {pi:4.1f} {name:<10} {spr:7.2f} "
                f"{profit.mean():8.2f} {interval(profit):6.2f} "
                f"{np.std(inventory):6.2f} {n_fills.mean():7.2f}"
            )
        # Pathwise gaps: the skew alone, then the declining spread alone.
        skew = pnl - pnl_n
        decline = pnl_n - pnl_s
        total = pnl - pnl_s
        print(
            f"{sigma:6.1f} {pi:4.1f} gaps       "
            f"skew {skew.mean():+.2f} +/- {interval(skew):.2f}   "
            f"decline {decline.mean():+.2f} +/- {interval(decline):.2f}   "
            f"total {total.mean():+.2f} +/- {interval(total):.2f}"
        )
