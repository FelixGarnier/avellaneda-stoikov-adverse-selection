"""Informed-only P&L on a grid of horizon tau and volatility.

Gamma is 0.1 and pi is 1. Paths for a given sigma are drawn once, with seed 0.
The same fill and label seeds are reused in every cell.
"""

import numpy as np

from src.price import simulate_mid_price
from src.simulator import run_inventory, run_symmetric

S0, T, DT = 100.0, 1.0, 0.005
GAMMA, K, A, PI = 0.1, 1.5, 140.0, 1.0
N_PATHS = 1000
SIGMAS = (2.0, 4.0)
TAUS = (0.05, 0.1, 0.2)


def half_width(x):
    return 1.96 * np.std(x) / np.sqrt(len(x))


def main():
    print(
        f"{'sigma':>6} {'tau':>5} {'strategy':<10} "
        f"{'profit':>8} {'+/-':>6} {'fills':>7}"
    )
    for sigma in SIGMAS:
        paths = simulate_mid_price(S0, sigma, T, DT, N_PATHS, np.random.default_rng(0))
        for tau in TAUS:
            pnl, _, fills, spread = run_inventory(
                paths, gamma=GAMMA, sigma=sigma, k=K, A=A, T=T, dt=DT,
                rng=np.random.default_rng(1), pi=PI, tau=tau,
                rng_info=np.random.default_rng(2),
            )
            pnl_s, _, fills_s, _ = run_symmetric(
                paths, spread, A=A, k=K, dt=DT,
                rng=np.random.default_rng(1), pi=PI, tau=tau,
                rng_info=np.random.default_rng(2),
            )
            for name, profit, n_fills in (
                ("inventory", pnl, fills),
                ("symmetric", pnl_s, fills_s),
            ):
                print(
                    f"{sigma:6.1f} {tau:5.2f} {name:<10} "
                    f"{profit.mean():8.2f} {half_width(profit):6.2f} {n_fills.mean():7.2f}"
                )


if __name__ == "__main__":
    main()
