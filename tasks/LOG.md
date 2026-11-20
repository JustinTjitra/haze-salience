# Run log

Newest entry first. One entry per run of the loop: date and time (UTC), tasks finished (with commit
hashes), tasks blocked and why, and what the owner needs to do.

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
