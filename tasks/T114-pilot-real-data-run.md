# T114 Real-data pilot run

Tier: planner · Depends: T112, T113 · Needs: network access to Yahoo Finance (owner action O2)

## Goal
The Stage 1 pilot outputs, produced from real data, are committed for the owner's go/no-go.

## Steps
1. Check access: one request to `https://query1.finance.yahoo.com`. If the proxy refuses it, leave
   this task `waiting` and log that O2 is still open. Do not try other routes.
2. `make data`. Read the coverage report. If a ticker fails or `ends_early` is true, do not edit
   the universe: record it in the log for the owner and continue with the firms that loaded
   (remove nothing from config; the pilot skips firms without data).
3. `make pilot`. Read the report it wrote.
4. Commit exactly these files as `DATA T114: pilot run on real data`:
   `outputs/figures/pilot_car.png`, `outputs/figures/pilot_car_summary.csv`,
   `outputs/figures/pilot_report.md`.
5. Log: the data range, which control was used, which firms were skipped, and the path of the
   report. Do not characterise the result as good or bad and do not make the G1 decision.

## Checks before committing
- The control label in the report is the soybean-oil fallback with lags (the FCPO CSV is manual
  data on the owner's machine and cannot be present here). The log must say that the owner's local
  run with FCPO (O3) supersedes these outputs.
- `git status` shows nothing under `data/` staged.
- The report carries the "Unverified events" line unless the owner has set `verified: true`.

## Out of scope
Interpreting the result, editing events or universe, re-running with different windows to see what
changes (that is specification search).
