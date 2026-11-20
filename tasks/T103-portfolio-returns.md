# T103 Portfolio returns

Tier: sonnet · Depends: none

## Goal
Functions that turn firm returns into an equal-weighted portfolio return and a long-short return.
All firms share the same event date, so their abnormal returns are correlated; running the event
study on one portfolio series is the standard way to get an honest standard error.

## Files
- `src/haze_salience/events/portfolio.py` (new)
- `tests/test_portfolio.py` (new)

## Spec
```python
def portfolio_return(rets: pd.DataFrame, members: list[str], name: str) -> pd.Series
```
Equal-weighted mean of the `members` columns for each day, named `name`. Strict: if any member is
NaN on a day, the portfolio is NaN that day. Raise `ValueError` if `members` is empty or a member
is not a column.

```python
def long_short_return(rets: pd.DataFrame, long: list[str], short: list[str], name: str) -> pd.Series
```
`portfolio_return(long) - portfolio_return(short)`, named `name`. Raise `ValueError` if a name is
in both lists.

## Acceptance tests
- `test_equal_weight_mean`: three columns with hand-written numbers; exact result.
- `test_nan_is_strict`: one NaN in one member makes that day NaN and only that day.
- `test_errors`: empty members, unknown column, overlap between long and short.
- `test_portfolio_event_study_recovers_common_shock`: build five synthetic firms on the
  `calendar` fixture from `tests/conftest.py`, each `r = 1.0*mkt + 0.5*cpo + eps` with independent
  eps (sd 1%), seeded; plant -5% on 2026-10-16 in every firm. Run
  `haze_salience.events.market_model.event_study` on the portfolio with the usual windows
  ((-150, -31), (-10, 10), 100). Assert `ar[0] == approx(-0.05, abs=0.015)` and
  `sigma == approx(0.01 / sqrt(5), rel=0.25)`.
- `test_long_short_cancels_common_factors`: shock only in the long group; the long-short series
  recovers the shock on day 0 and its estimated `mkt` and `cpo` betas are within 0.1 of zero.

## Out of scope
Value weights, changes to `pilot.py`.
