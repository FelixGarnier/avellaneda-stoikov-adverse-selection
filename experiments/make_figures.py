"""Write the README figures from the same seeds as the grids.

Outputs, under figures/:
    paper_gamma.png    mean P&L and terminal-inventory dispersion versus gamma
    pnl_vs_pi.png      mean P&L and inventory dispersion versus the informed fraction
    gaps_vs_pi.png     pathwise skew and decline versus the informed fraction
    risk_return.png    mean against standard deviation of P&L, by book and gamma
    pnl_vs_sigma.png   mean P&L versus volatility, with and without informed flow
    pnl_vs_tau.png     mean P&L versus the informed horizon
    fills_by_time.png  informed fills by fifth of the horizon

paper_gamma.png uses 1,000 paths and the two strategies of the paper. The
other figures use 20,000 paths and add the no-skew book.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D

from fills_by_time import counts
from avellaneda_stoikov.price import simulate_mid_price
from avellaneda_stoikov.simulator import run_inventory, run_noskew, run_symmetric

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figures"

S0, T, DT = 100.0, 1.0, 0.005
K, A, TAU = 1.5, 140.0, 0.1
PAPER_PATHS = 1000
N_PATHS = 20000

INV = "#1f4e79"
NOS = "#2f6f4e"
SYM = "#b86e00"
PAPER_SERIES = (
    ("inventory", INV, "Inventory"),
    ("symmetric", SYM, "Symmetric"),
)
SERIES = (
    ("inventory", INV, "Inventory"),
    ("noskew", NOS, "No skew"),
    ("symmetric", SYM, "Symmetric"),
)
GAP_SERIES = (
    ("skew", "#6a3d9a", "Skew (inventory − no skew)"),
    ("decline", "#a6373f", "Decline (no skew − symmetric)"),
)


def half_width(x):
    return 1.96 * np.std(x) / np.sqrt(len(x))


def one_cell(paths, sigma, gamma, pi, tau=TAU):
    pnl, q, fills, spread = run_inventory(
        paths, gamma=gamma, sigma=sigma, k=K, A=A, T=T, dt=DT,
        rng=np.random.default_rng(1), pi=pi, tau=tau,
        rng_info=np.random.default_rng(2),
    )
    pnl_n, q_n, fills_n, _ = run_noskew(
        paths, gamma=gamma, sigma=sigma, k=K, A=A, T=T, dt=DT,
        rng=np.random.default_rng(1), pi=pi, tau=tau,
        rng_info=np.random.default_rng(2),
    )
    pnl_s, q_s, fills_s, _ = run_symmetric(
        paths, spread, A=A, k=K, dt=DT,
        rng=np.random.default_rng(1), pi=pi, tau=tau,
        rng_info=np.random.default_rng(2),
    )
    skew = pnl - pnl_n
    decline = pnl_n - pnl_s
    return {
        "inventory": (pnl.mean(), half_width(pnl), q.std(), fills.mean(), pnl.std()),
        "noskew": (pnl_n.mean(), half_width(pnl_n), q_n.std(), fills_n.mean(), pnl_n.std()),
        "symmetric": (pnl_s.mean(), half_width(pnl_s), q_s.std(), fills_s.mean(), pnl_s.std()),
        "skew": (skew.mean(), half_width(skew)),
        "decline": (decline.mean(), half_width(decline)),
    }


def collect_paper():
    """Paper setting: 1,000 paths, no informed flow."""
    paths = simulate_mid_price(S0, 2.0, T, DT, PAPER_PATHS, np.random.default_rng(0))
    return {
        gamma: {0.0: one_cell(paths, 2.0, gamma, 0.0)} for gamma in (0.01, 0.1, 1.0)
    }


def collect():
    paths = simulate_mid_price(S0, 2.0, T, DT, N_PATHS, np.random.default_rng(0))
    by_gamma = {
        gamma: {pi: one_cell(paths, 2.0, gamma, pi) for pi in (0.0, 0.5, 1.0)}
        for gamma in (0.01, 0.1, 1.0)
    }
    by_sigma = {}
    for sigma in (1.0, 2.0, 4.0):
        paths_s = simulate_mid_price(S0, sigma, T, DT, N_PATHS, np.random.default_rng(0))
        by_sigma[sigma] = {
            pi: one_cell(paths_s, sigma, 0.1, pi) for pi in (0.0, 1.0)
        }
    return by_gamma, by_sigma


def style():
    plt.rcParams.update({
        "font.size": 11,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "grid.alpha": 0.3,
        "grid.linestyle": ":",
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "legend.frameon": False,
    })


def paper_gamma(by_gamma):
    gammas = [0.01, 0.1, 1.0]
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.6))
    for ax, metric, ylabel in (
        (axes[0], 0, "Mean terminal wealth"),
        (axes[1], 2, "Std of terminal inventory"),
    ):
        for name, color, label in PAPER_SERIES:
            y = [by_gamma[g][0.0][name][metric] for g in gammas]
            yerr = None if metric == 2 else [by_gamma[g][0.0][name][1] for g in gammas]
            ax.errorbar(
                gammas, y, yerr=yerr, color=color, marker="o",
                linewidth=1.6, capsize=3, label=label,
            )
        ax.set_xscale("log")
        ax.set_xticks(gammas, ["0.01", "0.1", "1"])
        ax.set_xlabel(r"Risk aversion $\gamma$")
        ax.set_ylabel(ylabel)
    axes[0].set_title(r"No informed flow, $\sigma = 2$")
    axes[1].set_title("Inventory dispersion")
    axes[0].legend()
    fig.tight_layout()
    fig.savefig(FIG / "paper_gamma.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def pnl_vs_pi(by_gamma):
    pis = [0.0, 0.5, 1.0]
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.6))
    for ax, metric, ylabel, title in (
        (axes[0], 0, "Mean terminal wealth", r"Profit, $\gamma = 0.1$, $\sigma = 2$"),
        (axes[1], 2, "Std of terminal inventory", r"Inventory, $\tau = 0.1$"),
    ):
        for name, color, label in SERIES:
            y = [by_gamma[0.1][pi][name][metric] for pi in pis]
            yerr = None if metric == 2 else [by_gamma[0.1][pi][name][1] for pi in pis]
            ax.errorbar(
                pis, y, yerr=yerr, color=color, marker="o",
                linewidth=1.6, capsize=3, label=label,
            )
        ax.set_xticks(pis, ["0", "0.5", "1"])
        ax.set_xlabel(r"Informed fraction $\pi$")
        ax.set_ylabel(ylabel)
        ax.set_title(title)
    axes[0].axhline(0.0, color="#666666", linewidth=0.8)
    axes[0].legend()
    fig.tight_layout()
    fig.savefig(FIG / "pnl_vs_pi.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def gaps_vs_pi(by_gamma):
    """Pathwise skew and decline against pi, one panel per gamma."""
    pis = [0.0, 0.5, 1.0]
    gammas = [0.01, 0.1, 1.0]
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.6))
    for ax, gamma in zip(axes, gammas):
        for name, color, label in GAP_SERIES:
            y = [by_gamma[gamma][pi][name][0] for pi in pis]
            yerr = [by_gamma[gamma][pi][name][1] for pi in pis]
            ax.errorbar(
                pis, y, yerr=yerr, color=color, marker="o",
                linewidth=1.6, capsize=3, label=label,
            )
        ax.axhline(0.0, color="#666666", linewidth=0.8)
        ax.set_xticks(pis, ["0", "0.5", "1"])
        ax.set_xlabel(r"Informed fraction $\pi$")
        ax.set_title(rf"$\gamma = {gamma:g}$")
    axes[0].set_ylabel("Gap in mean terminal wealth")
    axes[1].legend(loc="lower right", fontsize=9)
    fig.tight_layout()
    fig.savefig(FIG / "gaps_vs_pi.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def risk_return(by_gamma):
    """Mean against standard deviation of terminal wealth, by book and gamma."""
    gammas = [0.01, 0.1, 1.0]
    markers = {0.01: "o", 0.1: "s", 1.0: "^"}
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.8))
    for ax, pi, title in (
        (axes[0], 0.0, r"No informed flow, $\pi = 0$"),
        (axes[1], 0.5, r"Half informed, $\pi = 0.5$"),
    ):
        for name, color, label in SERIES:
            x = [by_gamma[g][pi][name][4] for g in gammas]
            y = [by_gamma[g][pi][name][0] for g in gammas]
            ax.plot(x, y, color=color, linewidth=1.0, alpha=0.6)
            for g, xi, yi in zip(gammas, x, y):
                ax.plot(xi, yi, color=color, marker=markers[g], markersize=7, linestyle="none")
        ax.set_xlabel("Std of terminal wealth")
        ax.set_title(title)
    axes[0].set_ylabel("Mean terminal wealth")
    books = [
        Line2D([], [], color=color, linewidth=1.6, label=label)
        for _, color, label in SERIES
    ]
    risk = [
        Line2D([], [], color="#444444", marker=markers[g], linestyle="none",
               markersize=7, label=rf"$\gamma = {g:g}$")
        for g in gammas
    ]
    axes[0].legend(handles=books, loc="lower right")
    axes[1].legend(handles=risk, loc="lower right")
    fig.tight_layout()
    fig.savefig(FIG / "risk_return.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def collect_tau():
    out = {}
    for sigma in (2.0, 4.0):
        paths = simulate_mid_price(S0, sigma, T, DT, N_PATHS, np.random.default_rng(0))
        out[sigma] = {
            tau: one_cell(paths, sigma, 0.1, 1.0, tau) for tau in (0.05, 0.1, 0.2)
        }
    return out


def pnl_vs_tau(by_tau):
    taus = [0.05, 0.1, 0.2]
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.6))
    for ax, sigma in ((axes[0], 2.0), (axes[1], 4.0)):
        for name, color, label in SERIES:
            y = [by_tau[sigma][tau][name][0] for tau in taus]
            yerr = [by_tau[sigma][tau][name][1] for tau in taus]
            ax.errorbar(
                taus, y, yerr=yerr, color=color, marker="o",
                linewidth=1.6, capsize=3, label=label,
            )
        ax.axhline(0.0, color="#666666", linewidth=0.8)
        ax.set_xticks(taus, ["0.05", "0.1", "0.2"])
        ax.set_xlabel(r"Informed horizon $\tau$")
        ax.set_title(rf"$\pi = 1$, $\gamma = 0.1$, $\sigma = {sigma:g}$")
    axes[0].set_ylabel("Mean terminal wealth")
    axes[0].legend()
    fig.tight_layout()
    fig.savefig(FIG / "pnl_vs_tau.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def pnl_vs_sigma(by_sigma):
    sigmas = [1.0, 2.0, 4.0]
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.6))
    for ax, pi, title in (
        (axes[0], 0.0, r"No informed flow, $\pi = 0$"),
        (axes[1], 1.0, r"Informed flow only, $\pi = 1$"),
    ):
        for name, color, label in SERIES:
            y = [by_sigma[s][pi][name][0] for s in sigmas]
            yerr = [by_sigma[s][pi][name][1] for s in sigmas]
            ax.errorbar(
                sigmas, y, yerr=yerr, color=color, marker="o",
                linewidth=1.6, capsize=3, label=label,
            )
        ax.axhline(0.0, color="#666666", linewidth=0.8)
        ax.set_xticks(sigmas, ["1", "2", "4"])
        ax.set_xlabel(r"Volatility $\sigma$")
        ax.set_title(title)
    axes[0].set_ylabel("Mean terminal wealth")
    axes[0].legend()
    fig.tight_layout()
    fig.savefig(FIG / "pnl_vs_sigma.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def fills_by_time():
    inv, noskew, sym, _ = counts()
    labels = ["0–0.2", "0.2–0.4", "0.4–0.6", "0.6–0.8", "0.8–1"]
    x = np.arange(len(labels))
    width = 0.26
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    ax.bar(x - width, inv, width, color=INV, label="Inventory")
    ax.bar(x, noskew, width, color=NOS, label="No skew")
    ax.bar(x + width, sym, width, color=SYM, label="Symmetric")
    ax.set_xticks(x, labels)
    ax.set_xlabel(r"Fraction of the horizon $[0, T]$")
    ax.set_ylabel("Fills per 1,000 paths")
    ax.set_title(r"Informed fills by time, $\gamma = 1$, $\pi = 1$, $\sigma = 2$")
    ax.legend()
    fig.tight_layout()
    fig.savefig(FIG / "fills_by_time.png", dpi=160, bbox_inches="tight")
    plt.close(fig)


def main():
    FIG.mkdir(exist_ok=True)
    style()
    paper_gamma(collect_paper())
    by_gamma, by_sigma = collect()
    pnl_vs_pi(by_gamma)
    gaps_vs_pi(by_gamma)
    risk_return(by_gamma)
    pnl_vs_sigma(by_sigma)
    pnl_vs_tau(collect_tau())
    fills_by_time()
    print(f"wrote figures in {FIG}")


if __name__ == "__main__":
    main()
