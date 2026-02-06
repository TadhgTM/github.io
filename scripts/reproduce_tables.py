from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

from src.model.data import load_inputs
from src.model.equilibrium import solve_equilibrium, welfare_change


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="") as f:
        return list(csv.DictReader(f))


def print_table(title: str, rows: list[dict[str, str]], max_rows: int | None = None) -> None:
    print("\n" + title)
    print("-" * len(title))
    if not rows:
        print("(no rows)")
        return

    headers = list(rows[0].keys())
    print(" | ".join(headers))
    print(" | ".join(["---"] * len(headers)))

    for idx, row in enumerate(rows):
        if max_rows is not None and idx >= max_rows:
            print(f"... ({len(rows) - max_rows} more rows)")
            break
        print(" | ".join(str(row[h]) for h in headers))


def show_targets() -> None:
    base = Path("data/targets")
    print_table("Table 1: Tariffs", _read_csv(base / "table1_tariffs.csv"))
    print_table("Table 1: Welfare", _read_csv(base / "table1_welfare.csv"))
    print_table("Table 2: Tariffs", _read_csv(base / "table2_tariffs.csv"))
    print_table("Table 2: Welfare", _read_csv(base / "table2_welfare.csv"))


def from_model() -> None:
    inputs_dir = Path("data/inputs")
    if not (inputs_dir / "countries.csv").exists():
        raise SystemExit("Missing input data. Add CSVs to data/inputs and retry.")

    data = load_inputs(inputs_dir)

    # Baseline equilibrium
    base_eq = solve_equilibrium(data)

    # Load scenario tariffs (optional)
    scenario_path = inputs_dir / "scenario_tariffs.csv"
    if not scenario_path.exists():
        raise SystemExit(
            "Missing data/inputs/scenario_tariffs.csv. "
            "Provide scenario tariff matrices to compute model outputs."
        )

    print("Baseline real income (by country):")
    for code, val in zip(data.countries, base_eq.real_income):
        print(f"  {code}: {val:.6f}")

    print("\nScenario tariff matrices detected, but scenario parsing is not implemented yet.")
    print("Add a parser for scenario_tariffs.csv once you decide its schema.")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--targets", action="store_true", help="Print paper target tables")
    parser.add_argument("--from-model", action="store_true", help="Compute tables from calibrated model")
    args = parser.parse_args()

    if args.from_model:
        from_model()
    else:
        show_targets()


if __name__ == "__main__":
    main()
