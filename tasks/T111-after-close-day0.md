# T111 After-close day-0 rule

Tier: haiku · Depends: T110

## Goal
An event announced after the market close is recorded with its true date and still gets the right
day 0 (the next trading day). Needed because the 2026 government statement appears to have been
posted on the evening of 15 Oct.

## Files
- `src/haze_salience/events/market_model.py`
- `src/haze_salience/events/volume.py`
- `src/haze_salience/events/pilot.py`
- `tests/test_market_model.py`, `tests/test_volume.py`, `tests/test_pilot.py`

## Spec
- `locate_day0(index, event_date, after_close: bool = False)`: with `after_close=True`, return the
  position of the first trading day **strictly after** `event_date`. Same error if none exists.
- `event_study(..., after_close: bool = False)` and `abnormal_volume(..., after_close=...)` pass it
  through.
- `run_pilot` reads `ev.get("after_close", False)` for each event and passes it everywhere day 0
  is computed, including `day0_positions`.

## Acceptance tests
- `test_after_close_moves_to_next_trading_day`: Thursday 2026-10-15 with `after_close=True` → Friday
  2026-10-16; with `False` → 2026-10-15.
- `test_after_close_on_friday_rolls_to_monday`: 2026-10-16 with `after_close=True` → 2026-10-19.
- `test_after_close_on_non_trading_day`: Saturday 2026-10-17 → Monday 2026-10-19 either way.
- `test_pilot_honours_after_close`: an event dated 2026-10-15 with `after_close: true` gives the
  same summary numbers as the same event dated 2026-10-16 without it.
- Existing tests pass unchanged (the default is `False`).

## Out of scope
Editing `config/events.yaml` (protected; the owner sets `after_close` there).
