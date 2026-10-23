"""Inventory-aware quotes from Avellaneda and Stoikov (2008), eqs. (29)-(30)."""

import numpy as np


def quotes(s, q, gamma, sigma, k, T, t):
    """Bid and ask centered on the reservation price.

    The reservation price lies below the mid when inventory is long, by
    ``q * gamma * sigma**2 * (T - t)``. Both quotes shift by that amount.
    The spread does not depend on inventory in this approximation:

        gamma * sigma**2 * (T - t) + (2 / gamma) * log(1 + gamma / k)

    The first term is inventory risk and vanishes at ``t = T``. The second is
    the markup that balances edge per fill against arrival intensity, and it
    stays positive at expiry. Distances used by the fill intensity are
    measured from the mid, not from the reservation price, so a long inventory
    makes the ask more likely to trade than the bid.

    Parameters
    ----------
    s : float or ndarray
        Current mid.
    q : float or ndarray
        Inventory, in number of shares. Positive means long.
    gamma, sigma, k, T, t : float
        Risk aversion, volatility, intensity decay, horizon, current time.

    Returns
    -------
    bid, ask : float or ndarray
    """
    r = s - q * gamma * sigma**2 * (T - t)
    spread = gamma * sigma**2 * (T - t) + 2 / gamma * np.log(1 + gamma / k)
    bid = r - spread / 2
    ask = r + spread / 2
    return bid, ask
