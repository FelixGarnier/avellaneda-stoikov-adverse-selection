import numpy as np
from src.price import simulate_mid_price
from src.simulator import run_inventory, run_symmetric

if __name__ == "__main__":
    paths = simulate_mid_price(100.0, 2.0, 1.0, 0.005, 1000, np.random.default_rng(0))
    gammas = [0.1] # [0.01, 0.1, 1.0]
    
    for gamma in gammas:
        # Inventory strategy
        pnl, q, fills, mean_spread = run_inventory(
            paths, gamma=gamma, sigma=2.0, k=1.5,
            A=140.0, T=1.0, dt=0.005, rng=np.random.default_rng(1), 
            pi=0.5, tau=0.1, rng_info=np.random.default_rng(2), 
        )
        inv_row = [
            "Inventory",
            f"{mean_spread:.2f}",
            f"{pnl.mean():.1f}",
            f"{np.std(pnl):.1f}",
            f"{q.mean():.2f}",
            f"{np.std(q):.1f}",
            f"{fills.mean():.2f}"
        ]
        
        # Symmetric strategy
        pnl_s, q_s, fills_s, mean_spread_s = run_symmetric(
            paths, mean_spread, A=140.0, k=1.5, 
            dt=0.005, rng=np.random.default_rng(1),
            pi=0.5, tau=0.1, rng_info=np.random.default_rng(2),
        )
        sym_row = [
            "Symmetric",
            f"{mean_spread_s:.2f}",
            f"{pnl_s.mean():.1f}",
            f"{np.std(pnl_s):.1f}",
            f"{q_s.mean():.2f}",
            f"{np.std(q_s):.1f}",
            f"{fills_s.mean():.2f}"
        ]
        
        # Print comparative table for this gamma
        print(f"\n==== Résultats pour gamma = {gamma} ====\n")
        print(
            f"{'Strategy':<12} {'Average Spread':>15} {'Profit':>8} {'Std (Profit)':>14} {'Final q':>10} {'Std (Final q)':>15} {'#Exec (fills)':>15}\n"
            + "-" * 95
        )
        print(
            f"{inv_row[0]:<12} {inv_row[1]:>15} {inv_row[2]:>8} {inv_row[3]:>14} {inv_row[4]:>10} {inv_row[5]:>15} {inv_row[6]:>15}"
        )
        print(
            f"{sym_row[0]:<12} {sym_row[1]:>15} {sym_row[2]:>8} {sym_row[3]:>14} {sym_row[4]:>10} {sym_row[5]:>15} {sym_row[6]:>15}"
        )
  
