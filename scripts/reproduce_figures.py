from __future__ import annotations

import csv
import sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src.model import plot_laffer_curve


def _read_curve(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    with path.open("r", newline="") as f:
        rows = list(csv.DictReader(f))
    tariff = np.array([float(r["tariff_rate"]) for r in rows])
    revenue = np.array([float(r["revenue_change"]) for r in rows])
    welfare = np.array([float(r["welfare_change"]) for r in rows])
    return tariff, revenue, welfare


def main() -> None:
    base = Path("data/inputs/figures")
    out_dir = Path("out/figures")
    out_dir.mkdir(parents=True, exist_ok=True)

    if not base.exists():
        print("No figure inputs found. Add CSVs to data/inputs/figures/ and retry.")
        return

    for path in base.glob("*.csv"):
        try:
            tariff, revenue, welfare = _read_curve(path)
        except Exception as exc:
            print(f"Skipping {path.name}: {exc}")
            continue

        title = path.stem.replace("_", " ").title()
        out_path = out_dir / f"{path.stem}.png"
        plot_laffer_curve(tariff, revenue, welfare, title, out_path)
        print(f"Wrote {out_path}")


if __name__ == "__main__":
    main()
