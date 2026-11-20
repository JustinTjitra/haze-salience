# T106 Short windows and p-values in the summary

Tier: haiku · Depends: T102, T105

## Goal
`EventResult.summary()` reports the short-window numbers the go/no-go decision uses.

## Files
- `src/haze_salience/events/market_model.py`
- `tests/test_market_model.py`

## Spec
Add these keys to the dict returned by `summary()` (keep all existing keys):

| Key | Value |
| --- | --- |
| `car_0_1` | sum of `ar` over offsets 0..1 |
| `car_0_3` | sum of `ar` over offsets 0..3 |
| `p_placebo_day0` | `placebo_pvalue(self.resid, ar[0], 1, "lower")` |
| `p_placebo_0_1` | `placebo_pvalue(self.resid, car_0_1, 2, "lower")` |

If the needed offsets are outside the event window or NaN, the value is NaN (do not raise).
Import `placebo_pvalue` from `haze_salience.events.placebo`.

## Acceptance tests
- `test_summary_short_windows`: `car_0_1` and `car_0_3` equal the sums of `ar` over those offsets.
- `test_summary_placebo_pvalues`: with the planted -8% shock, `p_placebo_day0 < 0.02`; without a
  shock the value is between 0 and 1.
- `test_summary_short_window_outside_event_window`: with `event_window=(-10, 0)`, `car_0_1` and
  `p_placebo_0_1` are NaN and nothing raises.

## Out of scope
Changing the CLI printout or the figure.
