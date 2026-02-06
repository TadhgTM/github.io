from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .data import ModelData


@dataclass
class EquilibriumResult:
    wages: np.ndarray  # (N,)
    prices: np.ndarray  # (N, S)
    trade_shares: np.ndarray  # (N, N, S)
    revenues: np.ndarray  # (N, S)
    income: np.ndarray  # (N,)
    tariff_revenue: np.ndarray  # (N,)
    real_income: np.ndarray  # (N,)


def _unit_costs(data: ModelData, wages: np.ndarray, prices: np.ndarray) -> np.ndarray:
    # log formulation for stability
    log_w = np.log(wages)
    log_p = np.log(prices)
    io_term = np.einsum("isk,ik->is", data.alpha, log_p)
    log_c = -np.log(data.z) + data.beta * log_w[:, None] + io_term
    return np.exp(log_c)


def _price_index(data: ModelData, costs: np.ndarray, tariff: np.ndarray, iceberg: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    # Delivered cost for importer i, exporter j, sector s
    delivered = costs[None, :, :] * iceberg * tariff
    power = 1.0 - data.sigma[None, None, :]
    term = data.gamma * np.power(delivered, power)
    denom = term.sum(axis=1)
    prices = np.power(denom, 1.0 / power)
    trade_shares = np.where(denom[:, None, :] > 0, term / denom[:, None, :], 0.0)
    return prices, trade_shares


def _solve_income_and_revenue(
    data: ModelData,
    trade_shares: np.ndarray,
    tariff: np.ndarray,
    iceberg: np.ndarray,
    wages: np.ndarray,
    income_init: np.ndarray,
    revenue_init: np.ndarray,
    max_iter: int = 500,
    tol: float = 1e-9,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    income = income_init.copy()
    revenues = revenue_init.copy()

    for _ in range(max_iter):
        # Final consumption expenditure
        exp_final = data.a * income[:, None]

        # Intermediate input expenditure (composite inputs)
        exp_intermediate = np.einsum("isk,is->ik", data.alpha, revenues)

        total_exp = exp_final + exp_intermediate

        # Bilateral expenditure at consumer prices
        flows = trade_shares * total_exp[:, None, :]

        # Tariff revenue
        tariff_component = (tariff - 1.0) / tariff
        tariff_rev = np.sum(tariff_component * flows, axis=(1, 2))

        income_new = wages * data.L + tariff_rev + data.D

        # Producer revenues (strip iceberg + tariff)
        revenues_new = np.sum(flows / (iceberg * tariff), axis=0)

        max_diff = max(
            np.max(np.abs(income_new - income) / (np.abs(income) + 1e-12)),
            np.max(np.abs(revenues_new - revenues) / (np.abs(revenues) + 1e-12)),
        )
        income = 0.5 * income + 0.5 * income_new
        revenues = 0.5 * revenues + 0.5 * revenues_new

        if max_diff < tol:
            return income_new, revenues_new, tariff_rev

    return income, revenues, tariff_rev


def _real_income(data: ModelData, income: np.ndarray, prices: np.ndarray) -> np.ndarray:
    log_price_index = np.sum(data.a * np.log(prices), axis=1)
    price_index = np.exp(log_price_index)
    return income / price_index


def solve_equilibrium(
    data: ModelData,
    tariff: np.ndarray | None = None,
    iceberg: np.ndarray | None = None,
    max_iter: int = 2000,
    tol: float = 1e-8,
    damp: float = 0.3,
    verbose: bool = False,
) -> EquilibriumResult:
    tariff = data.tariff if tariff is None else tariff
    iceberg = data.iceberg if iceberg is None else iceberg

    N, S = data.dims.n_countries, data.dims.n_sectors

    wages = np.ones((N,), dtype=float)
    prices = np.ones((N, S), dtype=float)
    income = wages * data.L + data.D
    revenues = np.ones((N, S), dtype=float)

    for it in range(max_iter):
        costs = _unit_costs(data, wages, prices)
        new_prices, trade_shares = _price_index(data, costs, tariff, iceberg)

        income, revenues, tariff_rev = _solve_income_and_revenue(
            data,
            trade_shares,
            tariff,
            iceberg,
            wages,
            income,
            revenues,
        )

        labor_demand = np.sum(data.beta * revenues, axis=1) / wages
        wages_new = wages * np.power(labor_demand / data.L, damp)
        wages_new = wages_new / wages_new[0]  # normalize numeraire

        # Dampen price updates for stability
        prices_prev = prices
        prices = (1.0 - damp) * prices + damp * new_prices

        max_diff = max(
            np.max(np.abs(wages_new - wages) / (np.abs(wages) + 1e-12)),
            np.max(np.abs(new_prices - prices_prev) / (np.abs(prices_prev) + 1e-12)),
        )
        wages = wages_new

        if verbose and (it % 50 == 0 or max_diff < tol):
            print(f"iter {it:4d} max_diff={max_diff:.3e}")

        if max_diff < tol:
            break

    real_income = _real_income(data, income, prices)

    return EquilibriumResult(
        wages=wages,
        prices=prices,
        trade_shares=trade_shares,
        revenues=revenues,
        income=income,
        tariff_revenue=tariff_rev,
        real_income=real_income,
    )


def welfare_change(base: EquilibriumResult, new: EquilibriumResult) -> np.ndarray:
    # Percent change in real income
    return (new.real_income / base.real_income - 1.0) * 100.0
