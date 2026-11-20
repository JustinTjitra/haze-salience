# T104 Portfolios in the pilot

Tier: sonnet · Depends: T103

## Goal
The pilot summary contains portfolio rows next to the firm rows: all firms, the firms named by
Greenpeace, the firms not named, and named minus not-named.

## Files
- `src/haze_salience/events/pilot.py`
- `src/haze_salience/events/plot.py` (only to keep portfolios out of the firm lines)
- `tests/test_pilot.py`

## Spec
In `run_pilot`, after the firm loop for each event:

- Members are the firms that produced a result for **that** event (skipped firms are left out).
- Build these series with `haze_salience.events.portfolio` and run `event_study` on each with the
  same factors and windows:
  - `"All firms"`: every member (needs ≥ 2).
  - `"Named"`: members with `greenpeace_named_2026: true` (needs ≥ 1).
  - `"Not named"`: the rest (needs ≥ 1).
  - `"Named minus not named"`: long-short of the two groups (needs both groups non-empty).
- A portfolio that cannot be built, or whose `event_study` raises `EventStudyError`, is skipped
  with a message appended to `skipped`, exactly like a firm.
- Add a column `kind` to the summary: `"firm"` or `"portfolio"`. Portfolio rows put the portfolio
  name in `firm`, `greenpeace_named = None`, and add `n_members`.
- Store portfolio results in a new `PilotOutput` field
  `portfolios: dict[str, dict[str, EventResult]]` (event id → portfolio name → result).
  `results` keeps firms only, so the figure is unchanged.

## Acceptance tests (in `tests/test_pilot.py`)
- `test_summary_has_portfolio_rows`: with the existing two-firm fixture, each event has rows for
  the four portfolios with `kind == "portfolio"`; firm rows have `kind == "firm"`.
- `test_named_minus_not_named_captures_planted_shock`: the fixture plants -9% in "Named Co" on
  16 Oct; for event `e2` the long-short `car_day0 == approx(-0.09, abs=0.04)`.
- `test_portfolio_members_exclude_skipped_firms`: in the short-history fixture, "Other Co" is
  skipped, so "Not named" and "Named minus not named" are skipped with a message and "All firms"
  is skipped too (fewer than 2 members).
- `test_run_pilot_end_to_end` still passes; update its `len(out.summary) == 4` assertion to count
  firm rows only.
- The figure test still passes and `plot_pilot` draws firm lines only.

## Out of scope
New statistics, report text, CLI output changes.
