# T110 Volume in the pilot

Tier: haiku · Depends: T107, T108, T109

## Goal
The pilot summary reports abnormal volume for each firm and event when volume data is available.

## Files
- `src/haze_salience/events/pilot.py`
- `src/haze_salience/cli.py` (`cmd_pilot` only)
- `tests/test_pilot.py`

## Spec
- `run_pilot(..., volumes: pd.DataFrame | None = None)`, a new keyword argument (wide frame, one
  column per ticker, like `prices`).
- When `volumes` is given: for each firm row compute
  `abnormal_volume(volumes[ticker].reindex(calendar), ...)` with the pilot's windows and add
  `abvol_day0` (z at offset 0) and `abvol_0_1` (mean of offsets 0 and 1). If the ticker is missing
  from `volumes` or `EventStudyError` is raised, both are NaN (no skip, no exception).
- Portfolio rows get NaN in both columns. When `volumes` is None the columns are absent.
- `cmd_pilot`: load volumes with `load_volumes`; if the cache file is missing, pass `None` and
  print one line saying volume was not available.

## Acceptance tests
- `test_volume_columns_present_when_given`: synthetic volumes with a 5x spike for "Named Co" on
  16 Oct → its `abvol_day0` for event `e2` is > 3; the other firm's is between -3 and 3.
- `test_volume_columns_absent_by_default`.
- `test_missing_volume_ticker_gives_nan`.

## Out of scope
Volume figure, turnover, report text.
