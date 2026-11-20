# T112 Fetch coverage report

Tier: haiku · Depends: T108

## Goal
After `make data`, the owner can see at a glance whether every ticker returned a full history,
which is how delisted or wrong tickers get caught.

## Files
- `src/haze_salience/data/prices.py`
- `src/haze_salience/cli.py` (`cmd_fetch` only)
- `tests/test_prices.py`

## Spec
```python
def coverage_report(prices: pd.DataFrame) -> pd.DataFrame
```
One row per column of `prices`, indexed by ticker, with columns: `first_date`, `last_date`
(first and last non-NaN dates), `n_obs` (non-NaN count), `n_missing` (NaN count between
`first_date` and `last_date` inclusive), and `ends_early` (True if `last_date` is more than 7
calendar days before the frame's last index date).

`cmd_fetch` prints the report as a table and writes it to `data/raw/fetch_report.csv`.

## Acceptance tests
- `test_coverage_report_counts`: a hand-built frame with one complete column, one with an interior
  NaN, and one that stops two weeks early; assert every field.
- `test_coverage_report_all_nan_column`: dates are NaT, `n_obs == 0`, `ends_early` is True.

## Out of scope
Changing `config/universe.yaml`, failing the fetch on `ends_early`.
