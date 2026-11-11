"""Pathwise simulators for the inventory, no-skew, and symmetric books."""

import numpy as np

from avellaneda_stoikov.flow import apply_fills, draw_fills, keep_fills
from avellaneda_stoikov.strategies import quotes, quotes_noskew


def _run(paths, quote_fn, A, k, dt, rng, q_0, pi, tau, rng_info):
    n_paths, n_times = paths.shape
    n_steps = n_times - 1
    n_tau = int(round(tau / dt))
    cash = np.zeros(n_paths)
    q = np.full(n_paths, q_0, dtype=float)
    spreads = np.empty(n_steps)
    fills = np.zeros(n_paths)

    for i in range(n_steps):
        mid = paths[:, i]
        bid, ask = quote_fn(mid, q, i * dt)
        spreads[i] = ask[0] - bid[0]
        bid_filled, ask_filled = draw_fills(mid - bid, ask - mid, A, k, dt, rng)
        if pi > 0.0:
            future_mid = paths[:, min(i + n_tau, n_steps)]
            informed_bid = rng_info.random(n_paths) < pi
            informed_ask = rng_info.random(n_paths) < pi
            bid_filled, ask_filled = keep_fills(
                bid_filled, ask_filled, bid, ask, future_mid, informed_bid, informed_ask
            )
        cash, q = apply_fills(cash, q, bid, ask, bid_filled, ask_filled)
        fills += bid_filled.astype(int) + ask_filled.astype(int)

    pnl = cash + q * paths[:, -1]
    return pnl, q, fills, float(spreads.mean())


def run_inventory(paths, gamma, sigma, k, A, T, dt, rng, q_0=0.0, pi=0.0, tau=0.1, rng_info=None):
    """Run the inventory strategy on a fixed set of mid paths.

    At each date the quotes are computed from the mid at the start of the
    step. The terminal column of ``paths`` is used only to mark leftover
    inventory. Wealth is ``cash + q * s_T``.

    When ``pi > 0``, each candidate fill is informed with probability ``pi``,
    using ``rng_info`` rather than ``rng``. Informed orders are then filtered
    by ``keep_fills`` against the mid ``tau`` ahead, clipped at the terminal
    date. ``pi = 0`` does not touch ``rng``, so it reproduces the simulation
    without adverse selection.

    Parameters
    ----------
    paths : ndarray, shape (n_paths, n_steps + 1)
    gamma, sigma, k, A, T, dt : float
        Risk aversion, volatility, intensity parameters, horizon, time step.
    rng : numpy.random.Generator
        Fill draws only.
    q_0 : float
        Initial inventory on every path.
    pi, tau : float
        Informed probability and the horizon those traders see.
    rng_info : numpy.random.Generator or None
        Required when ``pi > 0``.

    Returns
    -------
    pnl, q_final, n_fills : ndarray, shape (n_paths,)
    mean_spread : float
        Time average of the quoted spread. It does not depend on the path.
    """

    def quote_fn(mid, q, t):
        return quotes(mid, q, gamma, sigma, k, T, t)

    return _run(paths, quote_fn, A, k, dt, rng, q_0, pi, tau, rng_info)


def run_noskew(paths, gamma, sigma, k, A, T, dt, rng, q_0=0.0, pi=0.0, tau=0.1, rng_info=None):
    """Run the inventory strategy's spread centered on the mid.

    At each date the spread is the one ``run_inventory`` posts, so it still
    declines toward ``T``. The quotes ignore inventory: a long position is
    not pulled back toward zero. Against ``run_inventory`` the only
    difference is the skew.

    Fill and informed-flow conventions match ``run_inventory``. Pass a fresh
    generator with the same seed if the strategies must see the same
    uniforms.

    Returns
    -------
    pnl, q_final, n_fills : ndarray, shape (n_paths,)
    mean_spread : float
        Time average of the quoted spread, equal to that of ``run_inventory``.
    """

    def quote_fn(mid, q, t):
        return quotes_noskew(mid, gamma, sigma, k, T, t)

    return _run(paths, quote_fn, A, k, dt, rng, q_0, pi, tau, rng_info)


def run_symmetric(paths, spread, A, k, dt, rng, q_0=0.0, pi=0.0, tau=0.1, rng_info=None):
    """Run the symmetric benchmark on the same paths as ``run_inventory``.

    Quotes are ``mid ± spread / 2`` at every date. ``spread`` should be the
    average spread quoted by the inventory strategy. There is no reservation
    price: a long inventory is not pulled back toward zero. This book differs
    from ``run_inventory`` by the skew and by the constant spread. Use
    ``run_noskew`` to remove the skew alone.

    Fill and informed-flow conventions match ``run_inventory``. Pass a fresh
    generator with the same seed if the two strategies must see the same
    uniforms.

    Returns
    -------
    pnl, q_final, n_fills : ndarray, shape (n_paths,)
    mean_spread : float
        Equal to the input ``spread``.
    """

    def quote_fn(mid, q, t):
        return mid - spread / 2, mid + spread / 2

    return _run(paths, quote_fn, A, k, dt, rng, q_0, pi, tau, rng_info)
