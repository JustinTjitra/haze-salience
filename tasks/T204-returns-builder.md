# T204 Returns builder per exchange

Tier: sonnet · Depends: T201

## Goal
One function builds the return table (firms, market, CPO and its lags) for an exchange on that
exchange's own trading calendar. `run_pilot` uses it, and later runners use it for IDX.

## Files
- `src/haze_salience/events/returns.py` (new)
- `src/haze_salience/events/pilot.py`
- `tests/test_returns.py` (new)

## Spec
```python
def build_returns(
    prices: pd.DataFrame,          # wide closes, one column per ticker
    view: dict,                    # exchange_view(...): {"market_index": {...}, "firms": [...]}
    cpo: pd.Series,                # control price series on its own calendar
    cpo_lags: Sequence[int] = (0,),
) -> pd.DataFrame
```
- Calendar = dates where the index ticker has a price.
- Columns: one per firm **name** (prices reindexed to the calendar, no filling), `mkt`, `cpo`
  (control forward-filled onto the calendar with `align_to_calendar`), and `cpo_lag{k}` for each
  `k > 0`. Values are simple returns (`simple_returns`), so the first calendar day is dropped.
- A firm whose ticker is not a column of `prices` gets an all-NaN column (the caller skips it).
- Same lag validation as T107.

Refactor `run_pilot` to call `build_returns` instead of building the table inline. No behaviour
change: every existing pilot test must pass without edits.

## Acceptance tests
- `test_calendar_follows_index`: a day where the index has no price is absent even if firms have
  prices.
- `test_control_holiday_forward_fill`: a control-market holiday gives a zero `cpo` return that day
  and the catch-up the next day.
- `test_two_exchanges_get_different_calendars`: one `prices` frame with an SGX-style and an
  IDX-style index that have different holidays → two tables with different indexes.
- `test_missing_ticker_is_all_nan`, `test_lag_columns`.
- Existing `tests/test_pilot.py` passes unchanged.

## Out of scope
Currency conversion, fetching IDX prices, Dimson lags of the market factor.
