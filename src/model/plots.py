from __future__ import annotations

from pathlib import Path
import os
import numpy as np

# Avoid font/cache warnings on restricted environments
os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

import matplotlib.pyplot as plt


def plot_laffer_curve(
    tariff_rates: np.ndarray,
    revenue_changes: np.ndarray,
    welfare_changes: np.ndarray,
    title: str,
    out_path: str | Path,
) -> None:
    out_path = Path(out_path)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].plot(tariff_rates, revenue_changes, lw=2)
    axes[0].set_title("Tariff Revenue Change")
    axes[0].set_xlabel("US Tariff Rate (%)")
    axes[0].set_ylabel("Billions USD")

    axes[1].plot(tariff_rates, welfare_changes, lw=2, color="tab:red")
    axes[1].set_title("Welfare Change")
    axes[1].set_xlabel("US Tariff Rate (%)")
    axes[1].set_ylabel("Billions USD")

    fig.suptitle(title)
    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=200)
    plt.close(fig)


def plot_multi_scenarios(
    tariff_rates: np.ndarray,
    curves: dict[str, np.ndarray],
    title: str,
    ylabel: str,
    out_path: str | Path,
) -> None:
    out_path = Path(out_path)
    fig, ax = plt.subplots(figsize=(6, 4))

    for label, values in curves.items():
        ax.plot(tariff_rates, values, lw=2, label=label)

    ax.set_title(title)
    ax.set_xlabel("US Tariff Rate (%)")
    ax.set_ylabel(ylabel)
    ax.legend(frameon=False)

    fig.tight_layout()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=200)
    plt.close(fig)
