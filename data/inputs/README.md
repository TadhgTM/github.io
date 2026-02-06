# Input Data Schemas

All files are CSV with a header row. Use UTF‑8 and commas.

## `countries.csv`
Columns:
- `country_id` (int, 0‑based recommended)
- `country_code` (string, e.g. USA, CAN)
- `country_name` (string)

## `sectors.csv`
Columns:
- `sector_id` (int, 0‑based recommended)
- `sector_code` (string, e.g. C24)
- `sector_name` (string)

## `trade_flows.csv`
Baseline bilateral flows at **consumer prices**.

Columns:
- `importer_id`
- `exporter_id`
- `sector_id`
- `value` (float, currency units)

## `tariffs_baseline.csv`
Baseline ad‑valorem tariff rates (gross rate = 1 + rate).

Columns:
- `importer_id`
- `exporter_id`
- `sector_id`
- `rate` (float, e.g. 0.05 for 5%)

## `io_coeffs.csv`
Input‑output coefficients (cost shares) by country, sector of production, and input sector.

Columns:
- `country_id`
- `sector_id` (output sector)
- `input_sector_id`
- `share` (float)

## `elasticities.csv`
Sectoral trade elasticities (Fontagné et al. 2022).

Columns:
- `sector_id`
- `sigma` (float)

## `labor_endowments.csv`
Labor supply by country.

Columns:
- `country_id`
- `labor` (float)

## `trade_balance.csv`
Exogenous trade imbalance by country.

Columns:
- `country_id`
- `balance` (float)

## Optional: `iceberg_costs.csv`
If you have iceberg trade costs (non‑tariff trade costs).

Columns:
- `importer_id`
- `exporter_id`
- `sector_id`
- `iceberg` (float, >= 1)

## Optional: `gamma_weights.csv`
Armington weights. If omitted, they will be inferred from baseline trade shares.

Columns:
- `importer_id`
- `exporter_id`
- `sector_id`
- `gamma` (float)

## Optional: `productivity.csv`
Sectoral productivity.

Columns:
- `country_id`
- `sector_id`
- `z` (float)

## Optional: `utility_weights.csv`
Household utility weights (final demand shares).

Columns:
- `country_id`
- `sector_id`
- `weight` (float)
