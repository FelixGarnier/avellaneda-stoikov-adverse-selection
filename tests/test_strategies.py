import numpy as np

from avellaneda_stoikov.strategies import quotes, quotes_noskew


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


def test_noskew_has_the_inventory_spread_centered_on_the_mid():
    gamma, sigma, k = 0.1, 2.0, 1.5
    for t in (0.0, 0.5, 1.0):
        bid, ask = quotes(100.0, 2, gamma, sigma, k, 1.0, t)
        nbid, nask = quotes_noskew(100.0, gamma, sigma, k, 1.0, t)
        assert abs((nask - nbid) - (ask - bid)) < 1e-12
        assert abs((nbid + nask) / 2 - 100.0) < 1e-12
    nbid, nask = quotes_noskew(100.0, gamma, sigma, k, 1.0, 0.0)
    assert abs(nbid - 99.1541) < 1e-3
    assert abs(nask - 100.8459) < 1e-3
