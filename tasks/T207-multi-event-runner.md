# T207 Multi-event runner across exchanges and seasons

Tier: sonnet · Depends: T204, T206

## Goal
One function runs the market-model event study for any list of events on any list of exchanges,
each exchange on its own trading calendar, and returns one long table. The pilot is the special
case "SGX, two events of 2026"; this runner is what the 2015, 2019 and 2023 events and the IDX
names will go through.

## Files
- `src/haze_salience/events/runner.py` (new)
- `tests/test_runner.py` (new)

## Spec
```python
@dataclass(frozen=True)
class EventRun:
    summary: pd.DataFrame   # one row per exchange, event and firm that produced a result
    skipped: list[str]      # "<exchange> / <firm> / <event id>: <reason>"

def run_events(
    prices: pd.DataFrame,            # wide closes, one column per ticker (firms and indexes)
    universe: dict,                  # the full dict from load_universe()
    events: dict[str, dict],         # {id: event}, as load_events() returns
    event_ids: Sequence[str],
    exchanges: Sequence[str],
    cfg: dict,                       # estimation_window, event_window, min_estimation_days
    cpo: pd.Series,                  # control price series on its own calendar
    cpo_lags: Sequence[int] = (0,),
) -> EventRun
```
- For each exchange, in the order given: `view = exchange_view(universe, exchange)` and
  `rets = build_returns(prices, view, cpo, cpo_lags)`. Factors are `mkt`, then `cpo` if 0 is in
  `cpo_lags`, then `cpo_lag{k}` for each `k > 0` (the same rule `run_pilot` uses).
- For each event id, in the order given, and each firm of the exchange, in universe order: call
  `event_study` with the event's `date`, the windows from `cfg` and
  `after_close=bool(event.get("after_close", False))`.
- A firm/event that raises `EventStudyError` is appended to `skipped` in the format above and
  produces no row. Nothing else is caught.
- Summary columns, in this order: `exchange`, `event`, `firm`, `group`, then every key of
  `EventResult.summary()`, then `beta_mkt`, `beta_cpo` (only if 0 is in `cpo_lags`) and
  `beta_cpo_lag{k}`.
- Raise `ValueError` before doing any work if an event id is not in `events` or an exchange is
  not in the universe. Lag validation comes from `build_returns`.
- An event id repeated in `event_ids`, or an exchange repeated in `exchanges`, is a `ValueError`.
- Do not read files, the clock or the network. Do not import from `pilot.py`.

## Acceptance tests (synthetic prices, seeded `numpy.random.default_rng`, built in the test file)
Build one `prices` frame with two indexes that have **different holidays** (an SGX-style and an
IDX-style index), two firms per exchange, and a universe dict in the `load_universe()` shape.
- `test_rows_and_columns`: two exchanges × two events × two firms → 8 rows; the leading columns
  are `exchange, event, firm, group`; `skipped == []`.
- `test_day0_follows_each_exchange_calendar`: an event dated on a day that is a holiday on one
  exchange only gets a later `day0` on that exchange and the event's own date on the other.
- `test_after_close_is_honoured`: an event with `after_close: true` dated on a trading day gets
  the next trading day as `day0`.
- `test_planted_shock_recovered`: -8% planted in one firm on one event day, firm noise sd 1%;
  that row's `car_day0 == approx(-0.08, abs=0.04)` (four standard deviations of the noise).
- `test_matches_run_pilot_for_one_exchange`: for the SGX-style exchange alone, every value in
  the columns shared with `run_pilot(...).summary` firm rows (`car_day0`, `car_0_1`, `t_day0`,
  `sigma`, `beta_mkt`, `beta_cpo`) is exactly equal (`pandas.testing.assert_series_equal`) to
  what `run_pilot` gives for the same prices, events, windows and `cpo_lags=(0, 1)`. `run_pilot`
  takes the exchange view and a `load_cpo` callable; the test adapts the inputs. This test may
  import `run_pilot`; `runner.py` may not.
- `test_missing_ticker_is_skipped`: a firm whose ticker is not in `prices` appears in `skipped`
  for every event, with the exchange and firm name in the message, and has no row.
- `test_event_after_data_is_skipped`: an event dated after the last trading day is skipped for
  every firm and the other event still produces rows.
- `test_bad_arguments_raise`: unknown event id, unknown exchange, repeated event id, repeated
  exchange.

## Out of scope
Portfolios, abnormal volume, figures, reports, a CLI command, fetching IDX prices, refactoring
`run_pilot` to use this runner, season-long windows (T203 covers those).
