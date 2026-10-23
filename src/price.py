"""Mid-price paths for the Avellaneda-Stoikov discrete-time simulation."""

import numpy as np


def simulate_mid_price(S_0, sigma, T, dt, n_paths, rng):
    """Arithmetic random walk with no drift.

    Each step adds ``+sigma * sqrt(dt)`` or ``-sigma * sqrt(dt)`` with equal
    probability, independently across paths and times. The terminal variance
    is ``sigma**2 * T``. Column 0 is the initial price, before any shock.

    Parameters
    ----------
    S_0, sigma, T, dt : float
        Initial mid, volatility, horizon, and time step. ``T / dt`` is the
        number of steps.
    n_paths : int
    rng : numpy.random.Generator
        Draws the signs. The seed is chosen by the caller so two strategies
        can share one set of paths.

    Returns
    -------
    ndarray, shape (n_paths, n_steps + 1)
    """
    n_steps = int(round(T / dt))
    signs = rng.choice([-1, 1], size=(n_paths, n_steps))
    increments = signs * sigma * np.sqrt(dt)
    paths = np.empty((n_paths, n_steps + 1))
    paths[:, 0] = S_0
    paths[:, 1:] = S_0 + np.cumsum(increments, axis=1)
    return paths
