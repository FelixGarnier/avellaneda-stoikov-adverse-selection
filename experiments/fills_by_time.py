"""Informed fills by fifth of the horizon, at gamma = 1 and pi = 1.

The inventory spread shrinks toward expiry. The no-skew book posts that same
spread centered on the mid. The symmetric book posts its average at every
date. Same paths and the same random draws. Counts are per 1,000 paths.
"""

import numpy as np

from avellaneda_stoikov.flow import apply_fills, draw_fills, keep_fills
from avellaneda_stoikov.price import simulate_mid_price
from avellaneda_stoikov.strategies import quotes, quotes_noskew

S0, SIGMA, T, DT = 100.0, 2.0, 1.0, 0.005
GAMMA, K, A, TAU = 1.0, 1.5, 140.0, 0.1
N_PATHS = 20000
N_BINS = 5


def bin_of(t):
    return min(int(t / (T / N_BINS)), N_BINS - 1)


def fills_and_spread(paths, quote_fn):
    """Fills and mean spread by fifth, for one quoting rule."""
    n_steps = paths.shape[1] - 1
    n_tau = int(round(TAU / DT))
    q = np.zeros(N_PATHS)
    cash = np.zeros(N_PATHS)
    fills = np.zeros(N_BINS)
    spread_sum = np.zeros(N_BINS)
    spread_count = np.zeros(N_BINS)
    rng = np.random.default_rng(1)
    rng_info = np.random.default_rng(2)

    for i in range(n_steps):
        t = i * DT
        mid = paths[:, i]
        bid, ask = quote_fn(mid, q, t)
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
        fills[b] += bid_filled.sum() + ask_filled.sum()
        cash, q = apply_fills(cash, q, bid, ask, bid_filled, ask_filled)

    return fills * 1000 / N_PATHS, spread_sum / spread_count


def counts():
    """Return inventory, no-skew, and symmetric fills, and the spread by fifth.

    Fills are per 1,000 paths. The spread is the one the inventory and
    no-skew books post.
    """
    paths = simulate_mid_price(S0, SIGMA, T, DT, N_PATHS, np.random.default_rng(0))

    def inventory(mid, q, t):
        return quotes(mid, q, GAMMA, SIGMA, K, T, t)

    def noskew(mid, q, t):
        return quotes_noskew(mid, GAMMA, SIGMA, K, T, t)

    inv_fills, spreads = fills_and_spread(paths, inventory)
    noskew_fills, _ = fills_and_spread(paths, noskew)
    mean_spread = spreads.mean()

    def symmetric(mid, q, t):
        return mid - mean_spread / 2, mid + mean_spread / 2

    sym_fills, _ = fills_and_spread(paths, symmetric)
    return inv_fills, noskew_fills, sym_fills, spreads


def main():
    inv_fills, noskew_fills, sym_fills, spreads = counts()
    print(f"mean spread {spreads.mean():.2f}, fills per 1,000 paths")
    print("fifth  spread  inv_fills  noskew_fills  sym_fills")
    for b in range(N_BINS):
        print(
            f"{b + 1:5d}  {spreads[b]:6.2f}  "
            f"{inv_fills[b]:9.1f}  {noskew_fills[b]:12.1f}  {sym_fills[b]:9.1f}"
        )
    print(
        f"total          {inv_fills.sum():9.1f}  "
        f"{noskew_fills.sum():12.1f}  {sym_fills.sum():9.1f}"
    )


if __name__ == "__main__":
    main()
