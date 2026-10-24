import numpy as np

from src.flow import apply_fills, draw_fills, keep_fills


def test_fill_frequency_matches_intensity():
    n = 20_000
    rng = np.random.default_rng(0)
    bid, ask = draw_fills(np.full(n, 1.0), np.full(n, 1.0), 140.0, 1.5, 0.005, rng)
    expected = 140.0 * np.exp(-1.5) * 0.005
    assert abs(bid.mean() - expected) < 0.01
    assert abs(ask.mean() - expected) < 0.01
    assert (bid & ask).sum() > 0


def test_doubling_distance_divides_frequency_by_exp_k():
    n = 40_000
    rng = np.random.default_rng(1)
    near, _ = draw_fills(np.full(n, 1.0), np.full(n, 1.0), 140.0, 1.5, 0.005, rng)
    far, _ = draw_fills(np.full(n, 2.0), np.full(n, 2.0), 140.0, 1.5, 0.005, rng)
    assert abs(near.mean() / far.mean() - np.exp(1.5)) < 0.35


def test_apply_fills_signs():
    assert apply_fills(0.0, 0, 99.0, 101.0, True, False) == (-99.0, 1)
    assert apply_fills(0.0, 0, 99.0, 101.0, False, True) == (101.0, -1)
    cash, q = apply_fills(0.0, 0, 99.0, 101.0, True, True)
    assert cash == 2.0 and q == 0


def test_keep_fills_rules():
    assert keep_fills(True, True, 99.0, 101.0, 100.0, False, False) == (True, True)
    assert keep_fills(True, True, 99.5, 100.5, 99.0, True, True) == (True, False)
    assert keep_fills(True, True, 99.5, 100.5, 101.0, True, True) == (False, True)
    assert keep_fills(True, True, 99.5, 100.5, 100.0, True, True) == (False, False)
    assert keep_fills(False, False, 99.5, 100.5, 99.0, True, True) == (False, False)
