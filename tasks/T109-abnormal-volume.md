# T109 Abnormal volume

Tier: haiku · Depends: none

## Goal
A standardised abnormal-volume measure around an event. Volume is an attention outcome: a spike
without a price move, or the reverse, tells the two stories apart.

## Files
- `src/haze_salience/events/volume.py` (new)
- `tests/test_volume.py` (new)

## Spec
```python
def abnormal_volume(
    volume: pd.Series,
    event_date,
    estimation_window: tuple[int, int],
    event_window: tuple[int, int],
    min_estimation_days: int,
) -> pd.Series
```
- `volume` is indexed by trading day. Day 0 comes from
  `haze_salience.events.market_model.locate_day0`.
- Work in logs: `v = log(volume)`, with zero or negative volume treated as NaN.
- Result: `(v_τ - mean_est) / std_est` for each offset τ in the event window, indexed by a
  `RangeIndex` named `offset` (same convention as `EventResult.ar`). `mean_est` and `std_est`
  (ddof=1) are over the valid days of the estimation window. Offsets outside the data are NaN.
- Raise `EventStudyError` if the estimation window starts before the data or has fewer than
  `min_estimation_days` valid days.

## Acceptance tests
- `test_spike_is_detected`: seeded log-normal volume (sd 0.3 in logs) with day 0 multiplied by 5;
  z at offset 0 is `approx(log(5) / 0.3, abs=1.0)` and larger than every other offset.
- `test_offsets_and_index_name`: index is `range(lo, hi + 1)` and named `offset`.
- `test_zero_volume_is_nan`: a zero-volume day in the event window gives NaN there only.
- `test_too_few_estimation_days_raises` and `test_window_before_data_raises`.

## Out of scope
Wiring into the pilot (T110), turnover (needs shares outstanding), plots.
