# T208 PSI bulk CSV reader

Tier: haiku · Depends: T205, T115

## Goal
The "Historical 24-hr PSI" CSV from data.gov.sg can be read into the long table that
`daily_psi` (T205) takes. Schema confirmed on the live dataset by T115: see `docs/feasibility.md`,
section 3.

## Files
- `src/haze_salience/data/psi.py` (add one function; change nothing that exists, including the
  `load_psi` stub and its test)
- `tests/test_psi.py` (add tests; change no existing test)

## Spec
```python
REGIONS = ("north", "south", "east", "west", "central")

def read_psi_bulk_csv(path) -> pd.DataFrame
```
- Input columns: `24hr_psi` (timestamp text, **day first**, hour without leading zero, for example
  `25/9/2015 0:00` or `1/4/2014 13:00`) and one column per region in `REGIONS`. An `_id` column
  may or may not be present; ignore it. Column order does not matter.
- Output: long frame with columns `timestamp` (tz-naive `datetime64`, parsed with the explicit
  format `%d/%m/%Y %H:%M`, never by inference), `region` (one of `REGIONS`), `psi_24h` (float).
  One row per timestamp and region, sorted by `timestamp` then by the order of `REGIONS`, with a
  fresh `RangeIndex`.
- Region values arrive as text. Convert with `pd.to_numeric(..., errors="coerce")`: an empty or
  non-numeric cell becomes NaN and the row is kept.
- Raise `ValueError` naming what is wrong if: the `24hr_psi` column or any region column is
  missing; any timestamp does not match the format; the same timestamp appears twice.
- Timestamps are kept exactly as written. Do not shift `0:00` to the previous day and do not
  localise: which hour represents a day is a DECIDE item for the owner.

## Acceptance tests (all on small CSVs written to `tmp_path`)
- `test_read_psi_bulk_csv_long_shape`: two timestamps → 10 rows, the three columns, the right
  dtypes, and the exact values for one timestamp.
- `test_read_psi_bulk_csv_is_day_first`: `1/4/2014 1:00` parses to 1 April 2014 01:00, and
  `25/9/2015 0:00` to 25 September 2015 00:00.
- `test_read_psi_bulk_csv_ignores_id_and_column_order`.
- `test_read_psi_bulk_csv_non_numeric_is_nan`: an empty cell and a `-` cell give NaN, other
  cells in the row are unaffected.
- `test_read_psi_bulk_csv_errors`: missing region column, missing timestamp column, a timestamp
  in another format (`2015-09-25 00:00`), a duplicated timestamp. Each message names the problem.
- `test_read_psi_bulk_csv_feeds_daily_psi`: the output passed to `daily_psi(..., hour=12)` gives
  the hand-computed maximum across regions for each date.

## Out of scope
Downloading the file, the real-time API (the bulk file ends on 1 Oct 2026, so October and
November 2026 need that API: a separate task once the owner asks for it), choosing the reading
hour, implementing `load_psi`.
