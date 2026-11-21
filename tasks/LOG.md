# Run log

Newest entry first. One entry per run of the loop: date and time (UTC), tasks finished (with commit
hashes), tasks blocked and why, and what the owner needs to do.

## 2026-11-21 00:53 UTC run 9: nothing to do, schedule paused

- No owner commits since run 8; `tasks/DECISIONS.md` unchanged (G1 and G2 open); no tag
  `prereg-v1`.
- Health check: `make test` (194 passed) and `make lint` green. No code was changed.
- No task could be picked: nothing is `ready`. No brief was written: T401 and T402 are the only
  `needs-brief` rows, and both need the owner first (see run 7). Everything else is `waiting` on
  G1, G2, or an owner input.
- Per step 8 of the protocol, the schedule "haze-salience task loop" is paused after this entry.
  It is disabled, not deleted.
- **To restart the loop, the owner does one or more of these, then re-enables the schedule:**
  1. Record G1 in `tasks/DECISIONS.md` (due 29 Nov). `go` opens T301, T302 and T305 (the latter
     two need a brief; T302 also needs a FIRMS MAP_KEY and T305 a reachable concession download).
  2. Say what T402 should produce, given that the files holding the citations are protected.
  3. Say whether T401 should start before G1.
  4. Supply the verified IDX price-limit rule history for T209.
- Owner actions still open: O1, O3, O4, O7, O8; the two test changes flagged in runs 2 and 3.

## 2026-11-20 20:56 UTC run 8

- No owner commits since run 7; `tasks/DECISIONS.md` unchanged (G1 and G2 open).
- Health check before changes: `make test` (174 passed) and `make lint` green.
- Done: T207 Multi-event runner across exchanges and seasons (`c8b524a`, sonnet), T208 PSI file
  reader for the data.gov.sg bulk CSV (`f7df75d`, haiku). Both first pass against the briefs written
  in run 7, with no repairs. Suite is now 194 tests. Only two tasks were eligible.
- Review notes. T207: lags are validated before any work, not inside `build_returns` as the
  brief worded it (same error); an empty run returns a frame with only the four leading columns;
  the exact-equality test against `run_pilot` passes; the planted-shock test runs over six seeds.
  T208: the reader was tested on hand-written CSVs only; it has not been run on the real file,
  which has not been downloaded.
- No network call was made; `make data` and `make pilot` were not run.
- **The board is now out of work the loop can do.** Nothing is `ready`. T401 and T402 are
  `needs-brief` and need the owner first (see run 7: T401 depends on the shape G1 gives the
  note; T402's targets are protected files). T209 waits on a verified IDX rule history. All of
  Phase 3 waits on G1. If the board is unchanged at the next run, the loop logs that and pauses
  its schedule.
- Not checked: the GitHub Actions result for these pushes.
- Owner actions still open: O4 (G1, due 29 Nov), O1, O3, O7, O8; the T401 and T402 questions;
  the concession download and FIRMS MAP_KEY from run 4; the two test changes flagged in runs 2
  and 3.

## 2026-11-20 17:01 UTC run 7

- Health check before changes: `make test` (109 passed) and `make lint` green.
- Done, one at a time as the protocol now says: T203 Season abnormal returns (`d428e6f`, sonnet),
  T204 Returns builder per exchange (`abbf545`, sonnet), T206 Events schema validator (`0684652`,
  haiku). All first pass, no brief repairs. Suite is now 174 tests.
- T204 is a refactor of `run_pilot`. Besides the coder's before/after comparison on synthetic
  data, the planner re-ran `run_pilot` on the cached real prices from run 6 and the summary is
  byte-identical to the committed `outputs/figures/pilot_car_summary.csv`. Nothing under
  `outputs/` was rewritten.
- Review notes. T203: `market_model.py` gained a private `_forecast_error` helper, as the brief
  allowed, with no behaviour change; test tolerances are 3 standard errors, and the coder checked
  seeds 1 to 20. T204: a firm whose ticker is missing from the price frame is now skipped with a
  message instead of raising `KeyError`, as the brief specifies. T206: the real
  `config/events.yaml` passes; beyond the brief, `label` and `description` must be non-empty
  strings. Note for the owner: `time_sgt` must be quoted in YAML (`"10:30"`), because an unquoted
  `10:30` is read as the number 630 and is rejected.
- Briefs written, queue was empty: T207 (`0e37fb7`) and T208 (`55802eb`), both now `ready`. T208 adds a
  new function and leaves the `load_psi` stub, because T205's tests pin that stub.
- Not briefed, and why. T401 (note skeleton): the shape of the note depends on G1, and the
  write-up phase is planned for January; a brief now would be guesswork. T402 (citations):
  the references live in `docs/design.md`, `docs/preregistration.md`, `reports/` and
  `research_notes/`, all protected, so the task as titled ("fix `docs/` references") cannot be
  done by the loop. **Owner: say whether T402 should produce a findings file instead, and when
  T401 should start.**
- Gap found, no task created: the PSI bulk file ends on 1 Oct 2026, so October and November
  2026 need the real-time API. A reader for it is not on the board.
- No network call was made; `make data` and `make pilot` were not run.
- Blocked or waiting: G1 (owner). Next in board order: T207, T208. After those, everything left
  is `waiting` on G1 or on the owner, so the loop will pause itself unless the board changes.
- Not checked: the GitHub Actions result for these pushes.
- Owner actions still open: O1, O3, O4 (due 29 Nov), O7, O8; the concession download and FIRMS
  MAP_KEY from run 4; the two test changes flagged in runs 2 and 3.

## 2026-11-20 16:43 UTC run 6

- Synced the owner's protocol change `bf8ddad` (pick one task at a time, follow a dependency
  chain) and followed it: T113, then T114, then T201.
- Health check before changes: `make test` (94 passed) and `make lint` green.
- Done: T113 Pilot report writer (`f7a2ca9`, haiku), T114 Real-data pilot run (`c169c94`, planner),
  T201 Universe with IDX names (`b3c5d5a`, haiku). Suite is now 109 tests.
- **T114, the first run on real data.** Outputs: `outputs/figures/pilot_report.md`,
  `pilot_car_summary.csv`, `pilot_car.png`.
  - Data: Yahoo Finance, 2025-12-01 to 2026-11-06, 242 calendar rows, 236 observations for each
    of the 7 series. Coverage report: no ticker failed, none `ends_early`.
  - Control: `CBOT soybean oil (ZL=F), FCPO proxy + lags 1`. The FCPO CSV is manual data and was
    not present. **The owner's local run with FCPO (O3) supersedes these outputs.**
  - Firms skipped: none. Portfolios skipped: none.
  - Both events are `verified: false`, so the report carries "Unverified events: results are
    provisional." `pm_statement_2026` was run as dated, 16 Oct without `after_close`.
  - Volume: Indofood Agri Resources (5JS.SI) has 8 zero-volume days in the fetch window; they
    are treated as missing by the abnormal-volume measure.
  - Nothing under `data/` is committed. The result is not characterised here; G1 is the owner's.
- T201: the six IDX names and tickers were added verbatim from the brief, all `verify: true`.
  The coder noted that `docs/design.md` spells one firm "Sawit Sumber Mas" where the brief has
  "Sawit Sumbermas Sarana"; the brief's spelling was kept and `docs/design.md` (protected) was
  not touched. The SGX view passed to the pilot is unchanged, so the T114 outputs still match
  the code.
- Review notes, T113: the "How to read this" text says "With five firms", which goes stale if
  the SGX universe changes; the events table lists only the pilot's events.
- Blocked or waiting: G1 now has both inputs (T114, T115) and waits on the owner. Next in board
  order: T203, T204, T206.
- Not checked: the GitHub Actions result for these pushes.
- **Owner:** read `outputs/figures/pilot_report.md` and `docs/feasibility.md`, then decide G1
  (O4, due 29 Nov). Before relying on the pilot: O1 (verify the two events), O3 (FCPO run), and
  the `verify: true` tickers. Still open from earlier runs: O7, O8, the concession download,
  the FIRMS MAP_KEY, and the two test changes flagged in runs 2 and 3.

## 2026-11-20 16:37 UTC run 5

- Health check before changes: `make test` (70 passed) and `make lint` green.
- Done: T111 After-close day-0 rule (`2276aa4`, haiku), T202 Seasons configuration (`c23f8af`, haiku),
  T205 PSI daily measure and streaks (`77f2bcd`, haiku). All first pass, no brief repairs. Suite is
  now 94 tests.
- Review notes, all choices the briefs left open. T202: `season_windows` raises `ValueError` for
  a year not listed in the config. T205: the daily calendar spans all readings, not only those at
  the chosen hour; a missing calendar day breaks a streak; an hour outside 0..23 raises. T111:
  `config/events.yaml` was not touched; `pm_statement_2026` is still dated 16 Oct without
  `after_close`, which gives the same day 0 as 15 Oct with it.
- No network call was made; `make data` and `make pilot` were not run.
- Blocked or waiting: nothing new. Next in board order: T113 (report writer), then T114 (first
  real-data pilot run, planner), which needs T113 and so falls in a later run. T203 is also ready.
- Not checked: the GitHub Actions result for these pushes.
- Owner actions still open: O1, O3, O4 (due 29 Nov), O7, O8; the concession download and FIRMS
  MAP_KEY from run 4; the two test changes flagged in runs 2 and 3.

## 2026-11-20 16:02 UTC run 4

- Health check before changes: `make test` (62 passed) and `make lint` green.
- Done: T112 Fetch coverage report (`4794908`, haiku), T110 Volume in the pilot (`c5f249e`,
  haiku), T115 Feasibility check on live pages (`dabf593`, planner). All first pass. Suite is now
  70 tests.
- T115 findings are in `docs/feasibility.md`, each with its URL. In short: PSI bulk file covers
  1 Apr 2014 to 1 Oct 2026 hourly (2015 included; Oct and Nov 2026 only via the real-time API);
  FIRMS API template, limits and product names read, S-NPP coverage ends 2 Nov 2026, but whether
  the API serves 2015/2019/2023 needs a MAP_KEY to check; the GFW Indonesia concession layer
  (1845 polygons, `company` and `group_comp` fields) was read as metadata only, not opened.
- Hosts refused by the network policy: `gis-gfw.wri.org`, `www.globalforestwatch.org`,
  `data-api.globalforestwatch.org`, `api-production.data.gov.sg`. The concession zip on
  `gfw2-data.s3.amazonaws.com` answered AccessDenied from S3 itself. Not worked around.
- Review notes. T110: `abvol_0_1` is a skip-NaN mean, so if offset 1 is missing it equals the
  offset-0 value; the brief does not say which. T110 and T112 both edit `cli.py` (different
  functions) and were committed separately. T112 adds one test beyond the brief (the 7-day
  threshold). No real price data was fetched; `make data` and `make pilot` were not run.
- Blocked or waiting: nothing new. T208's `Needs` (PSI schema) is now met by T115; its brief is
  not written because more than three tasks are `ready`. Next in board order: T111, then T113,
  then T114 (the first real-data run).
- Not checked: the GitHub Actions result for these pushes.
- **Owner:** (1) try the concession download in a browser, or allow `gis-gfw.wri.org`;
  (2) supply a FIRMS MAP_KEY if Phase 3 goes ahead (O6 may be unnecessary if the API serves the
  old seasons); (3) still open: O1, O3, O4 (due 29 Nov), O7, O8, and the two test changes
  flagged in runs 2 and 3.

## 2026-11-20 12:57 UTC run 3

- Health check before changes: `make test` (47 passed) and `make lint` green.
- Done: T106 Short windows and p-values in the summary (`68d5afc`, haiku), T107 Lagged control
  term (`de1aca7`, sonnet), T109 Abnormal volume (`df128f4`, haiku, second pass). Suite is now 62
  tests.
- T109 brief defect: `test_spike_is_detected` asked for `abs=1.0` on the day-0 z-score, but day 0
  carries its own noise of 1.0 in z units, so that was a one-standard-deviation band (64% pass
  rate over 2000 seeds, measured by the coder, who stopped instead of picking a seed). The
  planner repaired the brief (`da208e5`): tolerance 3.0, plus an exact known-answer test.
  **Owner: this loosened a tolerance the brief had set; check you agree.**
- Review notes. T107: if `cpo_lags` omits 0, the `cpo` factor and `beta_cpo` are dropped; the
  brief does not cover that case and nothing uses it. T109: raises `EventStudyError` when the
  estimation-window log volume has zero variance (not in the original brief, accepted).
  T106: the placebo p-values are NaN when the offsets are outside the event window; other
  `ValueError`s from `placebo_pvalue` (fewer than `length + 20` residuals) still propagate.
- No network call was made; `make data` and `make pilot` were not run.
- Blocked or waiting: nothing new. Next in board order: T110, then T111 and T112.
- Not checked: the GitHub Actions result for these pushes.
- Owner actions still open: O1, O3, O4 (due 29 Nov), O6, O7, O8.

## 2026-11-20 08:56 UTC run 2

- Health check before changes: `make test` (32 passed) and `make lint` green.
- Done: T105 Placebo p-values (`f679b5a`, sonnet), T108 Volume fetch and cache (`1829693`, haiku),
  T104 Portfolios in the pilot (`ec1095b`, sonnet, second pass). Suite is now 47 tests.
- T104 brief defect: the spec contradicted two assertions in the existing
  `test_short_history_firm_is_skipped_not_fatal` (written when the summary and `skipped` held
  firms only). The coder stopped and reported it. The planner repaired the brief (`b98a3ca`): the
  assertions are now scoped to firms and the total skip count is pinned at 8. **Owner: this
  changed an existing test; check you agree it keeps the test's meaning.** The planner also had
  the coder narrow a `(EventStudyError, ValueError)` catch to `EventStudyError`, as the brief says.
- Review notes: T105 adds one test beyond the brief (`test_nans_dropped`); the null-uniformity
  test uses seed 12345, and the coder reports seeds 0 to 29 also pass. T108 removed the unused
  `CACHE_FILE` constant from `prices.py`. No network call was made; `make data` was not run.
- Blocked or waiting: nothing new. Next in board order: T106, T107, T109.
- Not checked: the GitHub Actions result for these pushes.
- Owner actions still open: O1, O3, O4 (due 29 Nov), O6, O7, O8.

## 2026-11-20 07:54 UTC run 1

- Health check before changes: `make test` (20 passed) and `make lint` green.
- Done: T102 Forecast-error variance and residuals (`1ab1015`, sonnet), T103 Portfolio returns
  (`b3297c7`, sonnet), T101 CI workflow (`2936659`, haiku). Each passed on the first attempt;
  suite is now 32 tests. The workflow file was accepted by the push.
- Review note, T103: the brief gave no tolerance for day-0 AR in
  `test_long_short_cancels_common_factors`; the coder used abs 0.02 (noise sd of the long-short
  series is about 0.8%).
- Blocked or waiting: nothing new. Next in board order: T104, T105, T108 (T106 follows T105).
- Not checked this run: whether the first CI run on GitHub went green.
- Owner actions still open: O1, O3, O4 (due 29 Nov), O6, O7, O8.

## 2026-11-20 setup

- Project guide, task board and briefs written in an interactive session. No loop run yet.
- Network: the `haze-salience` environment now allows Yahoo Finance, FIRMS, Global Forest Watch,
  data.gov.sg and Crossref (all confirmed reachable). No real price data has been looked at: the
  pilot's statistics (T102 to T113) are specified before the first real run (T114) on purpose.
- Owner actions open: O1, O3, O4 (see `tasks/README.md`).
