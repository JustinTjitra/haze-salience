# T205 PSI daily measure and streaks

Tier: haiku · Depends: none

## Goal
Turn regional PSI readings into the daily salience measure and the high-PSI flag, and count
unhealthy streaks so media claims ("12 straight days") can be checked against data.

## Files
- `src/haze_salience/data/psi.py` (replace the stub's body; keep `load_psi` raising
  `NotImplementedError`, since the file reader is a later task)
- `tests/test_psi.py` (new)

## Spec
```python
def daily_psi(readings: pd.DataFrame, hour: int = 12) -> pd.Series
```
`readings` has columns `timestamp` (tz-naive Singapore time), `region`, `psi_24h`. For each
calendar date, take the readings whose timestamp hour equals `hour` and return the maximum
`psi_24h` across regions. A date with no reading at that hour is NaN. Output is indexed by date
(DatetimeIndex, one row per calendar day from first to last date), named `psi`.

```python
def high_psi(daily: pd.Series, threshold: float = 100) -> pd.Series
```
Pandas nullable boolean: `True` where `daily > threshold` (strictly), `False` otherwise, `<NA>`
where `daily` is NaN.

```python
def unhealthy_streaks(high: pd.Series) -> pd.DataFrame
```
Columns `start`, `end`, `length` (calendar days): one row per maximal run of consecutive `True`
days. `<NA>` breaks a run.

## Acceptance tests
- `test_daily_psi_takes_max_region_at_hour`: hand-built readings for two days and three regions.
- `test_daily_psi_missing_hour_is_nan`, `test_daily_psi_fills_calendar_gaps_with_nan`.
- `test_high_psi_is_strict_and_keeps_na`: 100 → False, 101 → True, NaN → `<NA>`.
- `test_streaks`: a series with runs of length 3 and 1 separated by False and by `<NA>`.

## Out of scope
Reading any file or API, choosing the reading hour (a DECIDE item; 12 is only the default).
