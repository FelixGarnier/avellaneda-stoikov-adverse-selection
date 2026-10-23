import numpy as np
from src.strategies import quotes

if __name__ == "__main__":
    s = 100.0
    gamma = 0.1
    sigma = 2.0
    k = 1.5
    T = 1.0
    cases = [(0, 0.0), (1, 0.0), (0, 0.5), (0, 1.0)]
    for q, t in cases: 
        bid, ask = quotes(s, q, gamma, sigma, k, T, t)
        r = (bid + ask) / 2
        spread = ask - bid
        print(
        f"q={q}, t={t}: r={r:.3f}, spread={spread:.3f}, "
        f"bid={bid:.3f}, ask={ask:.3f}, "
        f"delta_b={s - bid:.3f}, delta_a={ask - s:.3f}"
    )
