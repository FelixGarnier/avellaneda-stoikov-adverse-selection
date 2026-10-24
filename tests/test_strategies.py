import numpy as np

from src.strategies import quotes


def test_spread_matches_the_paper_formula():
    gamma, sigma, k = 0.1, 2.0, 1.5
    for t in (0.0, 0.5, 1.0):
        bid, ask = quotes(100.0, 0, gamma, sigma, k, 1.0, t)
        expected = gamma * sigma**2 * (1.0 - t) + (2 / gamma) * np.log(1 + gamma / k)
        assert abs((ask - bid) - expected) < 1e-12
        assert abs((bid + ask) / 2 - 100.0) < 1e-12


def test_long_inventory_shifts_the_center_down():
    bid, ask = quotes(100.0, 1, 0.1, 2.0, 1.5, 1.0, 0.0)
    assert abs((bid + ask) / 2 - 99.6) < 1e-12
    assert 100.0 - bid > ask - 100.0
