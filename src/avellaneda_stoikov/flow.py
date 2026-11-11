"""Order-flow draws, inventory accounting, and the informed-trader filter."""

import numpy as np


def draw_fills(delta_bid, delta_ask, A, k, dt, rng):
    """Bernoulli fills at intensity ``A * exp(-k * delta)``.

    ``delta_bid`` is the distance from the mid down to the bid, and
    ``delta_ask`` the distance from the mid up to the ask. The two sides use
    independent uniforms, so both can fill on the same step. The probability
    is capped at 1, which matters when a quote crosses the mid and ``delta``
    becomes negative.

    Parameters
    ----------
    delta_bid, delta_ask : float or ndarray
    A, k, dt : float
        Arrival scale, decay of intensity with distance, time step.
    rng : numpy.random.Generator

    Returns
    -------
    bid_filled, ask_filled : ndarray of bool
        A bid fill means someone sells to the market maker. An ask fill means
        someone buys from the market maker.
    """
    delta_bid = np.asarray(delta_bid, dtype=float)
    delta_ask = np.asarray(delta_ask, dtype=float)
    p_bid = np.minimum(A * np.exp(-k * delta_bid) * dt, 1.0)
    p_ask = np.minimum(A * np.exp(-k * delta_ask) * dt, 1.0)
    bid_filled = rng.random(p_bid.shape) < p_bid
    ask_filled = rng.random(p_ask.shape) < p_ask
    return bid_filled, ask_filled


def apply_fills(cash, q, bid, ask, bid_filled, ask_filled):
    """Update cash and inventory after a step's fills.

    A bid fill buys one unit: cash falls by the bid and inventory rises by 1.
    An ask fill sells one unit: cash rises by the ask and inventory falls by 1.
    Both can happen on the same step. ``True`` counts as 1, so the same
    expression works for scalars and for one value per path.

    Returns
    -------
    cash, q
    """
    cash = cash - bid * bid_filled + ask * ask_filled
    q = q + bid_filled - ask_filled
    return cash, q


def keep_fills(bid_filled, ask_filled, bid, ask, future_mid, informed_bid, informed_ask):
    """Drop fills that an informed trader would refuse.

    Uninformed fills are kept. An informed seller hits the bid only when it is
    strictly above the future mid. An informed buyer lifts the ask only when
    it is strictly below the future mid. Otherwise the order is cancelled.
    A side that was not filled stays unfilled: this function never creates a
    trade. The future mid is an input. The quoting rule must not see it.

    Returns
    -------
    bid_filled, ask_filled : ndarray of bool
    """
    bid_filled = np.asarray(bid_filled, dtype=bool)
    ask_filled = np.asarray(ask_filled, dtype=bool)
    informed_bid = np.asarray(informed_bid, dtype=bool)
    informed_ask = np.asarray(informed_ask, dtype=bool)

    keep_bid = ~informed_bid | (bid > future_mid)
    keep_ask = ~informed_ask | (ask < future_mid)
    return bid_filled & keep_bid, ask_filled & keep_ask
