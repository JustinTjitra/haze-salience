# T203 Season abnormal returns

Tier: sonnet · Depends: T202, T102

## Goal
Daily abnormal returns for one firm over one haze season, from a market model estimated on that
year's pre-season window. This is the outcome variable of the Stage 2 panel and of season-long
event work.

## Files
- `src/haze_salience/events/season_ar.py` (new)
- `tests/test_season_ar.py` (new)

## Spec
```python
@dataclass(frozen=True)
class SeasonAR:
    year: int
    params: pd.Series
    sigma: float
    n_estimation: int
    ar: pd.Series      # indexed by date, every trading day in the season window
    ar_se: pd.Series   # same index; sigma * sqrt(1 + x' (X'X)^-1 x), as in T102

def season_abnormal_returns(
    firm: pd.Series, factors: pd.DataFrame, windows: SeasonWindows, min_estimation_days: int
) -> SeasonAR
```
- `firm` and `factors` share a trading-day index (raise `EventStudyError` otherwise).
- Estimation rows: dates in `[est_start, est_end]` with no NaN in firm or factors. Fewer than
  `min_estimation_days` → `EventStudyError`.
- Season rows: dates in `[season_start, season_end]`. `ar` is NaN where the firm or a factor is
  NaN. No season rows at all → `EventStudyError`.
- Reuse, do not copy, whatever helper T102 introduced for the forecast-error term; if T102 inlined
  it, factor it out into a private function in `market_model.py` and use it from both places
  (then `market_model.py` and its tests are also in scope, with no behaviour change).

## Acceptance tests
- `test_recovers_betas_and_zero_mean_ar`: multi-year synthetic returns with known betas; for 2026
  the betas are within tolerance and the season mean AR is within 3 standard errors of zero.
- `test_planted_season_shock`: -6% on one season day is recovered on that date.
- `test_estimation_excludes_season`: a large shift applied to every season day leaves `params`
  unchanged.
- `test_ar_index_is_season_only`: first and last index dates lie inside the season window.
- `test_too_few_estimation_days_raises`, `test_no_season_rows_raises`,
  `test_nan_factor_gives_nan_ar`.

## Out of scope
Looping over firms or seasons, saving a panel, fire exposure.
