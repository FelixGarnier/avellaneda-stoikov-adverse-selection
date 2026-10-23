"""Profit, inventory dispersion, and fill counts on a grid of sigma and pi.

Gamma is fixed at 0.1. Paths are redrawn for each sigma with the same seed,
so the shock signs match and only the amplitude changes. A higher sigma both
widens the quote, through the gamma * sigma**2 term, and makes the mid move
farther over the informed traders' horizon.
"""

import numpy as np
from src.price import simulate_mid_price
from src.simulator import run_inventory, run_symmetric

S0 = 100.0
gamma = 0.1
T = 1.0
dt = 0.005
k = 1.5
A = 140.0
tau = 0.1
n_paths = 1000
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
        pnl_s, q_s, fills_s, spread_s = run_symmetric(
            paths, spread, A=A, k=k, dt=dt,
            rng=np.random.default_rng(1),
            pi=pi, tau=tau, rng_info=np.random.default_rng(2),
        )
        for name, profit, inventory, n_fills, spr in (
            ("inventory", pnl, q, fills, spread),
            ("symmetric", pnl_s, q_s, fills_s, spread_s),
        ):
            print(
                f"{sigma:6.1f} {pi:4.1f} {name:<10} {spr:7.2f} "
                f"{profit.mean():8.1f} {interval(profit):6.1f} "
                f"{np.std(inventory):6.1f} {n_fills.mean():7.1f}"
            )
