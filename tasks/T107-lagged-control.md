# T107 Lagged control term

Tier: sonnet · Depends: T104

## Goal
When the CPO control is the soybean-oil fallback, the market model includes the control's previous
day as well. CBOT settles after SGX closes, so an SGX day's return overlaps two CBOT sessions.

## Files
- `src/haze_salience/events/pilot.py`
- `src/haze_salience/cli.py`
- `config/pilot.yaml`
- `tests/test_pilot.py`

## Spec
- `run_pilot(..., cpo_lags: Sequence[int] = (0,))`, a new keyword argument after `load_cpo`.
  For each lag `k` in `cpo_lags`: lag 0 is the existing column `cpo`; lag `k > 0` is
  `rets["cpo"].shift(k)` in a column named `cpo_lag{k}`. All of them are factors, for firms and
  for portfolios. Reject negative or duplicate lags with `ValueError`.
- Summary: keep `beta_cpo`; add `beta_cpo_lag{k}` for each extra lag.
- When any lag > 0 is used, append `" + lags 1"` (the lags, comma separated) to `control_label`.
- `config/pilot.yaml`: under `cpo:` add `manual_lags: [0]` and `fallback_lags: [0, 1]`.
- `cli.cmd_pilot`: pass `manual_lags` if the manual CSV exists, otherwise `fallback_lags`.

## Acceptance tests
- `test_default_has_no_lag_columns`: calling `run_pilot` without `cpo_lags` gives no
  `beta_cpo_lag1` column and an unchanged `control_label`.
- `test_lagged_control_is_recovered`: build a firm whose return depends on yesterday's CPO return
  with coefficient 0.5 (and on today's with 0.4); with `cpo_lags=(0, 1)` assert
  `beta_cpo_lag1 == approx(0.5, abs=0.15)` and `beta_cpo == approx(0.4, abs=0.15)`.
- `test_label_mentions_lags`: label ends with `" + lags 1"`.
- `test_bad_lags_raise`: `(-1,)` and `(0, 0)`.
- All existing pilot tests pass.

## Out of scope
Dimson betas for the market factor, changes to `data/cpo.py`.
