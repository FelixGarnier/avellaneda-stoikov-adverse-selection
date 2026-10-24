import numpy as np

from src.price import simulate_mid_price


def test_shape_and_initial_column():
    paths = simulate_mid_price(100.0, 2.0, 1.0, 0.005, 20, np.random.default_rng(0))
    assert paths.shape == (20, 201)
    assert np.all(paths[:, 0] == 100.0)


def test_seed_reproducibility():
    args = (100.0, 2.0, 1.0, 0.005, 30)
    a = simulate_mid_price(*args, np.random.default_rng(0))
    b = simulate_mid_price(*args, np.random.default_rng(0))
    assert np.array_equal(a, b)


def test_terminal_moments_match_sigma_squared_t():
    paths = simulate_mid_price(100.0, 2.0, 1.0, 0.005, 4000, np.random.default_rng(1))
    terminal = paths[:, -1]
    assert abs(terminal.mean() - 100.0) < 0.15
    assert abs(terminal.var() - 4.0) < 0.25
