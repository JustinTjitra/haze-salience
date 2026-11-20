# T102 Forecast-error variance and residuals

Tier: sonnet · Depends: none

## Goal
`EventResult` carries a correct per-day standard error for each abnormal return (including the
error from estimating the market model) and the estimation-window residuals, so later tasks can
build test statistics and placebo p-values.

## Files
- `src/haze_salience/events/market_model.py`
- `tests/test_market_model.py`

## Spec
Add two fields to `EventResult` (after `band`) and fill them in `event_study`:

- `ar_se: pd.Series`, indexed by offset like `ar`. For event-window day τ with regressor row
  `x_τ` (constant first, then the factors, same column order as the estimation design `X`):
  `ar_se[τ] = sigma * sqrt(1 + x_τ' (X'X)^{-1} x_τ)`.
  `X` is the estimation design restricted to the valid rows actually used in the fit. Use
  `np.linalg.solve` or `pinv`, not an explicit inverse of an ill-conditioned matrix. Where `ar` is
  NaN (offset outside the data), `ar_se` is NaN.
- `resid: pd.Series`, the OLS residuals over the estimation window, indexed by date (valid rows only).

Add to `summary()`: `"t_day0": ar[0] / ar_se[0]`.

Do not change `band`, `car`, `sigma` or any existing key of `summary()`.

## Acceptance tests (add to `tests/test_market_model.py`)
- `test_ar_se_matches_hand_formula`: recompute `ar_se` for offsets -10, 0 and 10 inside the test
  with plain numpy from the fixture data (build `X` yourself) and compare with `pytest.approx`.
- `test_ar_se_at_least_sigma`: every non-NaN `ar_se` is ≥ `sigma`, and with 120 estimation days
  and ordinary factor values every one is < `1.05 * sigma`.
- `test_ar_se_grows_with_extreme_factor`: set the market return on day 0 to 10 standard
  deviations; `ar_se[0]` is then larger than `ar_se[1]` by at least 5%.
- `test_resid_properties`: `len(resid) == n_estimation`; mean is 0 to 1e-10;
  `sqrt(sum(resid**2) / (n - 3)) == approx(sigma)`.
- `test_t_day0_in_summary`: equals `ar[0] / ar_se[0]`.
- All existing tests still pass unchanged.

## Out of scope
Patell/BMP statistics, cross-sectional adjustments, any change to `pilot.py` or `plot.py`.
