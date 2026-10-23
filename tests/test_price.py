import numpy as np
from src.price import simulate_mid_price

if __name__ == "__main__":
    rng = np.random.default_rng(0)
    S_0 = 100.0
    sigma = 2.0
    T = 1.0
    dt = 0.005
    n_paths = 1000
    paths = simulate_mid_price(S_0, sigma, T, dt, n_paths, rng)
    print(paths.shape)
    print(paths[:, -1].mean())
    print(paths[:, -1].var())