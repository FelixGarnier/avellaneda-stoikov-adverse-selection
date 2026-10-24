import numpy as np

from src.price import simulate_mid_price
from src.simulator import run_inventory, run_symmetric


def test_no_arrivals_leave_wealth_and_inventory_at_zero():
    paths = simulate_mid_price(100.0, 2.0, 1.0, 0.005, 40, np.random.default_rng(0))
    pnl, q, fills, spread = run_inventory(
        paths, gamma=0.1, sigma=2.0, k=1.5, A=0.0, T=1.0, dt=0.005,
        rng=np.random.default_rng(1),
    )
    assert np.all(pnl == 0.0)
    assert np.all(q == 0.0)
    assert np.all(fills == 0.0)
    assert abs(spread - 1.491770422751424) < 1e-12


def test_symmetric_spread_is_the_inventory_average():
    paths = simulate_mid_price(100.0, 2.0, 1.0, 0.005, 20, np.random.default_rng(0))
    _, _, _, spread = run_inventory(
        paths, gamma=0.1, sigma=2.0, k=1.5, A=0.0, T=1.0, dt=0.005,
        rng=np.random.default_rng(1),
    )
    _, _, _, spread_s = run_symmetric(
        paths, spread, A=0.0, k=1.5, dt=0.005, rng=np.random.default_rng(1),
    )
    assert abs(spread_s - spread) < 1e-9


def test_zero_informed_share_matches_the_published_seed():
    paths = simulate_mid_price(100.0, 2.0, 1.0, 0.005, 1000, np.random.default_rng(0))
    pnl, _, _, _ = run_inventory(
        paths, gamma=0.1, sigma=2.0, k=1.5, A=140.0, T=1.0, dt=0.005,
        rng=np.random.default_rng(1), pi=0.0,
    )
    assert abs(pnl.mean() - 64.904) < 0.01
