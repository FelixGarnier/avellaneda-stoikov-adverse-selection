"""Informed fills by fifth of the horizon, at gamma = 1 and pi = 1.

The inventory spread shrinks toward expiry. The symmetric book posts that
strategy's average spread at every date. Same paths and the same random draws.
"""

import numpy as np

from src.flow import apply_fills, draw_fills, keep_fills
from src.price import simulate_mid_price
from src.strategies import quotes

S0, SIGMA, T, DT = 100.0, 2.0, 1.0, 0.005
GAMMA, K, A, TAU = 1.0, 1.5, 140.0, 0.1
N_PATHS = 1000
N_BINS = 5


def bin_of(t):
    return min(int(t / (T / N_BINS)), N_BINS - 1)


def main():
    paths = simulate_mid_price(S0, SIGMA, T, DT, N_PATHS, np.random.default_rng(0))
    n_steps = paths.shape[1] - 1
    n_tau = int(round(TAU / DT))
    q = np.zeros(N_PATHS)
    cash = np.zeros(N_PATHS)
    inv_fills = np.zeros(N_BINS)
    spread_sum = np.zeros(N_BINS)
    spread_count = np.zeros(N_BINS)
    rng = np.random.default_rng(1)
    rng_info = np.random.default_rng(2)

    for i in range(n_steps):
        t = i * DT
        mid = paths[:, i]
        bid, ask = quotes(mid, q, GAMMA, SIGMA, K, T, t)
        b = bin_of(t)
        spread_sum[b] += ask[0] - bid[0]
        spread_count[b] += 1
        bid_filled, ask_filled = draw_fills(mid - bid, ask - mid, A, K, DT, rng)
        future = paths[:, min(i + n_tau, n_steps)]
        informed_bid = rng_info.random(N_PATHS) < 1.0
        informed_ask = rng_info.random(N_PATHS) < 1.0
        bid_filled, ask_filled = keep_fills(
            bid_filled, ask_filled, bid, ask, future, informed_bid, informed_ask
        )
        inv_fills[b] += bid_filled.sum() + ask_filled.sum()
        cash, q = apply_fills(cash, q, bid, ask, bid_filled, ask_filled)

    mean_spread = spread_sum.sum() / spread_count.sum()
    sym_fills = np.zeros(N_BINS)
    rng = np.random.default_rng(1)
    rng_info = np.random.default_rng(2)
    for i in range(n_steps):
        t = i * DT
        mid = paths[:, i]
        bid = mid - mean_spread / 2
        ask = mid + mean_spread / 2
        bid_filled, ask_filled = draw_fills(mid - bid, ask - mid, A, K, DT, rng)
        future = paths[:, min(i + n_tau, n_steps)]
        informed_bid = rng_info.random(N_PATHS) < 1.0
        informed_ask = rng_info.random(N_PATHS) < 1.0
        bid_filled, ask_filled = keep_fills(
            bid_filled, ask_filled, bid, ask, future, informed_bid, informed_ask
        )
        sym_fills[bin_of(t)] += bid_filled.sum() + ask_filled.sum()

    print(f"mean spread {mean_spread:.2f}")
    print("fifth  spread  inv_fills  sym_fills")
    for b in range(N_BINS):
        print(
            f"{b + 1:5d}  {spread_sum[b] / spread_count[b]:6.2f}  "
            f"{inv_fills[b]:9.0f}  {sym_fills[b]:9.0f}"
        )


if __name__ == "__main__":
    main()
