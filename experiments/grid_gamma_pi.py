"""Profit, inventory dispersion, and fill counts on a grid of gamma and pi.

Sigma is fixed at 2, the value used by Avellaneda and Stoikov. Paths are
drawn once. Fill and informed-label generators are reseeded in every cell,
so the cells differ only by risk aversion and the informed fraction.
"""

import numpy as np
from src.price import simulate_mid_price
from src.simulator import run_inventory, run_symmetric

S0 = 100.0
sigma = 2.0
T = 1.0
dt = 0.005
k = 1.5
A = 140.0
tau = 0.1
n_paths = 1000
gammas = [0.01, 0.1, 1.0]
pis = [0.0, 0.5, 1.0]

paths = simulate_mid_price(S0, sigma, T, dt, n_paths, np.random.default_rng(0))

def interval(x):
    return 1.96 * np.std(x) / np.sqrt(len(x))

print(
    f"{'gamma':>6} {'pi':>4} {'strategy':<10} {'spread':>7} "
    f"{'profit':>8} {'+/-':>6} {'std_q':>6} {'fills':>7}"
)

for gamma in gammas:
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
                f"{gamma:6.2f} {pi:4.1f} {name:<10} {spr:7.2f} "
                f"{profit.mean():8.1f} {interval(profit):6.1f} "
                f"{np.std(inventory):6.1f} {n_fills.mean():7.1f}"
            )

