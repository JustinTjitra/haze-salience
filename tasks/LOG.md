# Run log

Newest entry first. One entry per run of the loop: date and time (UTC), tasks finished (with commit
hashes), tasks blocked and why, and what the owner needs to do.

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
