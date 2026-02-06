from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import csv
import numpy as np


@dataclass
class ModelDims:
    n_countries: int
    n_sectors: int


@dataclass
class ModelData:
    dims: ModelDims
    countries: list[str]
    sectors: list[str]

    # Preferences and endowments
    a: np.ndarray  # (N, S)
    L: np.ndarray  # (N,)
    D: np.ndarray  # (N,)

    # Technology
    alpha: np.ndarray  # (N, S, S)
    beta: np.ndarray  # (N, S)
    z: np.ndarray  # (N, S)

    # Trade
    sigma: np.ndarray  # (S,)
    gamma: np.ndarray  # (N, N, S)
    tariff: np.ndarray  # (N, N, S) gross (1 + rate)
    iceberg: np.ndarray  # (N, N, S)

    # Baseline flows (consumer prices)
    trade_flows: np.ndarray | None = None  # (N, N, S)

    def validate(self) -> None:
        N, S = self.dims.n_countries, self.dims.n_sectors
        assert self.a.shape == (N, S)
        assert self.L.shape == (N,)
        assert self.D.shape == (N,)
        assert self.alpha.shape == (N, S, S)
        assert self.beta.shape == (N, S)
        assert self.z.shape == (N, S)
        assert self.sigma.shape == (S,)
        assert self.gamma.shape == (N, N, S)
        assert self.tariff.shape == (N, N, S)
        assert self.iceberg.shape == (N, N, S)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="") as f:
        return list(csv.DictReader(f))


def _infer_size(rows: list[dict[str, str]], key: str) -> int:
    max_id = max(int(r[key]) for r in rows)
    return max_id + 1


def load_inputs(base_dir: str | Path = "data/inputs") -> ModelData:
    base = Path(base_dir)

    countries_rows = _read_csv(base / "countries.csv")
    sectors_rows = _read_csv(base / "sectors.csv")

    n_countries = _infer_size(countries_rows, "country_id")
    n_sectors = _infer_size(sectors_rows, "sector_id")
    dims = ModelDims(n_countries=n_countries, n_sectors=n_sectors)

    countries = [""] * n_countries
    for r in countries_rows:
        countries[int(r["country_id"])] = r.get("country_code") or r.get("country_name") or ""

    sectors = [""] * n_sectors
    for r in sectors_rows:
        sectors[int(r["sector_id"])] = r.get("sector_code") or r.get("sector_name") or ""

    # Trade flows
    trade_rows = _read_csv(base / "trade_flows.csv")
    trade_flows = np.zeros((n_countries, n_countries, n_sectors), dtype=float)
    for r in trade_rows:
        i = int(r["importer_id"])
        j = int(r["exporter_id"])
        s = int(r["sector_id"])
        trade_flows[i, j, s] = float(r["value"])

    # Tariffs (baseline)
    tariff = np.ones((n_countries, n_countries, n_sectors), dtype=float)
    tariff_rows = _read_csv(base / "tariffs_baseline.csv")
    for r in tariff_rows:
        i = int(r["importer_id"])
        j = int(r["exporter_id"])
        s = int(r["sector_id"])
        rate = float(r["rate"])
        tariff[i, j, s] = 1.0 + rate

    # IO coefficients
    io_rows = _read_csv(base / "io_coeffs.csv")
    alpha = np.zeros((n_countries, n_sectors, n_sectors), dtype=float)
    for r in io_rows:
        i = int(r["country_id"])
        s = int(r["sector_id"])
        k = int(r["input_sector_id"])
        alpha[i, s, k] = float(r["share"])

    beta = 1.0 - alpha.sum(axis=2)
    if np.any(beta < -1e-8):
        raise ValueError("Labor shares implied by io_coeffs are negative. Check IO shares.")

    # Elasticities
    elast_rows = _read_csv(base / "elasticities.csv")
    sigma = np.zeros((n_sectors,), dtype=float)
    for r in elast_rows:
        s = int(r["sector_id"])
        sigma[s] = float(r["sigma"])

    # Labor endowments
    labor_rows = _read_csv(base / "labor_endowments.csv")
    L = np.zeros((n_countries,), dtype=float)
    for r in labor_rows:
        i = int(r["country_id"])
        L[i] = float(r["labor"])

    # Trade balance
    balance_rows = _read_csv(base / "trade_balance.csv")
    D = np.zeros((n_countries,), dtype=float)
    for r in balance_rows:
        i = int(r["country_id"])
        D[i] = float(r["balance"])

    # Optional iceberg costs
    iceberg = np.ones((n_countries, n_countries, n_sectors), dtype=float)
    iceberg_path = base / "iceberg_costs.csv"
    if iceberg_path.exists():
        ice_rows = _read_csv(iceberg_path)
        for r in ice_rows:
            i = int(r["importer_id"])
            j = int(r["exporter_id"])
            s = int(r["sector_id"])
            iceberg[i, j, s] = float(r["iceberg"])

    # Optional Armington weights
    gamma = None
    gamma_path = base / "gamma_weights.csv"
    if gamma_path.exists():
        gamma = np.zeros((n_countries, n_countries, n_sectors), dtype=float)
        g_rows = _read_csv(gamma_path)
        for r in g_rows:
            i = int(r["importer_id"])
            j = int(r["exporter_id"])
            s = int(r["sector_id"])
            gamma[i, j, s] = float(r["gamma"])
    else:
        # Infer from baseline trade shares
        denom = trade_flows.sum(axis=1, keepdims=True)
        with np.errstate(divide="ignore", invalid="ignore"):
            gamma = np.where(denom > 0, trade_flows / denom, 0.0)

    # Optional productivity
    z = np.ones((n_countries, n_sectors), dtype=float)
    z_path = base / "productivity.csv"
    if z_path.exists():
        z_rows = _read_csv(z_path)
        for r in z_rows:
            i = int(r["country_id"])
            s = int(r["sector_id"])
            z[i, s] = float(r["z"])

    # Utility weights (optional)
    a = np.full((n_countries, n_sectors), 1.0 / n_sectors, dtype=float)
    a_path = base / "utility_weights.csv"
    if a_path.exists():
        a_rows = _read_csv(a_path)
        a = np.zeros((n_countries, n_sectors), dtype=float)
        for r in a_rows:
            i = int(r["country_id"])
            s = int(r["sector_id"])
            a[i, s] = float(r["weight"])

        # Normalize to sum to 1
        a_sum = a.sum(axis=1, keepdims=True)
        a = np.where(a_sum > 0, a / a_sum, a)

    data = ModelData(
        dims=dims,
        countries=countries,
        sectors=sectors,
        a=a,
        L=L,
        D=D,
        alpha=alpha,
        beta=beta,
        z=z,
        sigma=sigma,
        gamma=gamma,
        tariff=tariff,
        iceberg=iceberg,
        trade_flows=trade_flows,
    )
    data.validate()
    return data
