import numpy as np
from src.flow import draw_fills, apply_fills, keep_fills

if __name__ == "__main__":
    """
    rng = np.random.default_rng(0)
    A = 140
    k = 1.5
    dt = 0.005
    n_paths = 10_000
    delta_bid = np.full(n_paths, 1.0)
    delta_ask = np.full(n_paths, 1.0)
    bid_filled, ask_filled = draw_fills(delta_bid, delta_ask, A, k, dt, rng)
    frequency_bid = np.mean(bid_filled)
    frequency_ask = np.mean(ask_filled)
    print((bid_filled & ask_filled).sum())
    print(frequency_bid)
    print(frequency_ask)
    """
    """
    print(apply_fills(0.0, 0, 99.0, 101.0, True, False))
    print(apply_fills(0.0, 0, 99.0, 101.0, False, True))
    print(apply_fills(0.0, 0, 99.0, 101.0, True, True))
    """
    print(keep_fills(True, True, 99.0, 101.0, 100.0, False, False))
    print(keep_fills(True, True, 99.5, 100.5, 99.0, True, True))
    print(keep_fills(True, True, 99.5, 100.5, 101.0, True, True))
    print(keep_fills(True, True, 99.5, 100.5, 100.0, True, True))
    print(keep_fills(False, False, 99.5, 100.5, 99.0, True, True))
