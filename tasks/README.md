# Task board and loop protocol

Work is cut into small tasks. Each task is one brief (`tasks/T###-*.md`), one coder, one commit.
If something breaks, `git log --oneline` tells you which task did it.

## Roles and tiers

| Tier | Who | Used for |
| --- | --- | --- |
| `haiku` | Cheapest coder | Mechanical work: parsers, config, wiring, validators, report templates |
| `sonnet` | Mid-priced coder | Logic with a way to be subtly wrong: statistics, alignment, spatial joins |
| `planner` | The session's own (expensive) model | Choosing tasks, writing and repairing briefs, reviewing diffs, debugging what coders could not fix, real-data runs |

The planner never writes task code that a coder could write. The coders never plan.

## One run of the loop

1. **Sync.** `git fetch origin main`, check out `main`, `git merge --ff-only origin/main`. If that
   fails, stop and report; never force anything. Set the git identity from `CLAUDE.md`.
2. **Health check.** `uv sync`, `make test`, `make lint`. If `main` is red before you changed
   anything, repairing it is the only job of this run: find the commit that broke it, fix it as
   `FIX T###: ...`, or revert that commit with `git revert` and set the task back to `ready`.
3. **Read state.** This file, `tasks/DECISIONS.md`, the top entries of `tasks/LOG.md`.
4. **Pick up to three tasks**, in board order, with status `ready`, every dependency `done`, every
   gate open and every `Needs` item available. Check a `Needs` item cheaply (for a host: one
   request). If it is not available, leave the task `waiting`.
5. **For each picked task:**
   1. Tier `planner`: do it yourself. Otherwise start **one** coder with the Agent tool, with
      `model` set to the task's tier, and give it: the path of the brief, the instruction to read
      `CLAUDE.md` first, and the instruction not to commit.
   2. **Verify** (planner, always):
      - `git status`: every changed file is listed under "Files" in the brief; nothing in
        `tasks/PROTECTED.txt` changed.
      - The acceptance tests named in the brief exist and assert what the brief says. No existing
        test was weakened, deleted or skipped.
      - `make test` and `make lint` pass.
      - Read the diff. Does it do what the brief says, and nothing else?
   3. **Pass:** set the task to `done` in the board below, commit code and board together as
      `T###: <title>`, push.
   4. **Fail:** send the specific failure back to the same coder once. If it fails again, discard
      the changes (`git checkout -- . && git clean -fd`) and retry once with the next tier up
      (`haiku` → `sonnet` → planner), passing on what went wrong. If that fails too, set the task to
      `blocked`, write what happened at the bottom of its brief, commit that as `PLAN: block T###`,
      and go on to the next task.
6. **Keep the queue stocked.** If fewer than three tasks are `ready` and a `needs-brief` task has
   its gates open, write its brief (same format as the others, sized for one coder and one commit;
   split it if it is not) and commit as `PLAN: brief T###`.
7. **Log.** Add an entry at the top of `tasks/LOG.md`: time (UTC), tasks done with commit hashes,
   tasks blocked or waiting and why, anything the owner must do. Commit as `LOG: run <date>`, push.
8. **Nothing to do?** If no task could be picked and no brief could be written, log that and pause
   the schedule named "haze-salience task loop" if you have the tools to. Do not invent work.
9. **Report** to the owner in at most six lines.

Hard limits are in [`../CLAUDE.md`](../CLAUDE.md). They apply to planner and coders alike.

## Status values

`ready` · `needs-brief` (scope known, brief not written yet) · `waiting` (on an owner action, a gate
or network access; the reason is in the Needs column) · `blocked` (tried and failed; notes in the
brief) · `done`

## Owner actions

| ID | Action | Why | Status |
| --- | --- | --- | --- |
| O1 | Verify the 2026 events against original sources and update `config/events.yaml` (`verified: true`, correct dates). Leads are in `reports/Haze salience project sources.md` | Results may only use verified events | open |
| O2 | Approve network access for the data hosts | The loop cannot fetch real data without it | done 20 Nov: environment `haze-salience` allows Yahoo Finance, FIRMS, Global Forest Watch, data.gov.sg, Crossref |
| O3 | Download the Bursa FCPO CSV and run `make pilot` locally; commit the outputs | Manual data never reaches the cloud loop, which can only use the soybean-oil fallback | open |
| O4 | Decide G1 (go/no-go) in `tasks/DECISIONS.md` by 29 Nov | Opens or closes Phase 3 | open |
| O5 | Build the concession-to-parent table (`config/parents.csv`) | Highest-effort input; only after G1 = go | open |
| O6 | Request FIRMS archive extracts for 2015, 2019, 2023 (emailed download) | The API may not serve old seasons | open |
| O7 | Resolve the DECIDE items and tag `prereg-v1` | Required before any Stage 2 run on real data | open |
| O8 | Manual novelty search (SSRN, Google Scholar) | Could not be done from the research sandbox | open |

## Board

### Phase 1: finish the pilot

| ID | Title | Tier | Depends | Needs | Status |
| --- | --- | --- | --- | --- | --- |
| [T101](T101-ci-workflow.md) | CI workflow | haiku | | | done |
| [T102](T102-forecast-error-variance.md) | Forecast-error variance and residuals | sonnet | | | done |
| [T103](T103-portfolio-returns.md) | Portfolio returns | sonnet | | | done |
| [T104](T104-portfolios-in-pilot.md) | Portfolios in the pilot | sonnet | T103 | | done |
| [T105](T105-placebo-pvalues.md) | Placebo p-values | sonnet | | | done |
| [T106](T106-summary-short-windows.md) | Short windows and p-values in the summary | haiku | T102, T105 | | done |
| [T107](T107-lagged-control.md) | Lagged control term | sonnet | T104 | | done |
| [T108](T108-volume-fetch.md) | Volume fetch and cache | haiku | | | done |
| [T109](T109-abnormal-volume.md) | Abnormal volume | haiku | | | done |
| [T110](T110-volume-in-pilot.md) | Volume in the pilot | haiku | T107, T108, T109 | | done |
| [T111](T111-after-close-day0.md) | After-close day-0 rule | haiku | T110 | | ready |
| [T112](T112-fetch-coverage-report.md) | Fetch coverage report | haiku | T108 | | done |
| [T113](T113-pilot-report.md) | Pilot report writer | haiku | T106, T111 | | ready |
| [T114](T114-pilot-real-data-run.md) | Real-data pilot run | planner | T112, T113 | Network: Yahoo Finance | ready |
| [T115](T115-feasibility-check.md) | Feasibility check on live pages (concessions, FIRMS, PSI) | planner | | Network | done |
| G1 | Go/no-go (owner, O4) | owner | T114, T115 | | waiting |

### Phase 2: infrastructure both stories need

| ID | Title | Tier | Depends | Needs | Status |
| --- | --- | --- | --- | --- | --- |
| [T201](T201-universe-idx.md) | Universe with IDX names | haiku | T113 | | ready |
| [T202](T202-seasons-config.md) | Seasons configuration | haiku | | | ready |
| [T203](T203-season-abnormal-returns.md) | Season abnormal returns | sonnet | T202, T102 | | ready |
| [T204](T204-returns-builder.md) | Returns builder per exchange | sonnet | T201 | | ready |
| [T205](T205-psi-daily-measure.md) | PSI daily measure and streaks | haiku | | | ready |
| [T206](T206-events-schema.md) | Events schema validator | haiku | T201 | | ready |
| T207 | Multi-event runner across exchanges and seasons | sonnet | T204, T206 | | needs-brief |
| T208 | PSI file reader for the data.gov.sg bulk CSV | haiku | T205, T115 | Schema from T115 | needs-brief |
| T209 | IDX price-limit day flags | sonnet | T204 | Verified 2015 to 2026 rule history | waiting |

### Phase 3: diffusion chain (only after G1 = go)

| ID | Title | Tier | Depends | Needs | Status |
| --- | --- | --- | --- | --- | --- |
| T301 | Parent-link table template and validator (`config/parents.csv`) | haiku | G1 | | waiting |
| T302 | FIRMS request builder and date chunking | haiku | G1 | Network: FIRMS, to confirm the API | waiting |
| T303 | FIRMS CSV parser, confidence filter, local-date assignment | sonnet | T302 | | waiting |
| T304 | FIRMS archive CSV reader | haiku | T303 | | waiting |
| T305 | Concession loader and geometry clean-up | sonnet | G1 | Network: GFW, to confirm fields | waiting |
| T306 | Spatial join: hotspots inside concessions | sonnet | T303, T305 | | waiting |
| T307 | Buffer-ring exposure (2 km, 5 km) | sonnet | T306 | | waiting |
| T308 | Exposure panel: firm-day counts, area scaling, lags | sonnet | T301, T306 | | waiting |
| T309 | Panel assembly and schema checks | sonnet | T203, T208, T308 | | waiting |
| T310 | Main panel regression | sonnet | T309 | | waiting |
| T311 | Cumulative-effect test (sum of lag coefficients) | sonnet | T310 | | waiting |
| T312 | Wild-cluster bootstrap | sonnet | T310 | | waiting |
| T313 | Robustness runner | sonnet | T311, T312 | | waiting |
| T314 | Stage 2 tables and figures | haiku | T313 | | waiting |
| G2 | Pre-registration frozen (owner, O7) | owner | | | waiting |
| T320 | Stage 2 run on real data | planner | T314, G2 | Network and data; tag `prereg-v1` | waiting |

### Phase 4: write-up

| ID | Title | Tier | Depends | Needs | Status |
| --- | --- | --- | --- | --- | --- |
| T401 | Research-note skeleton wired to outputs | planner | T114 | | needs-brief |
| T402 | Check every citation against Crossref and fix `docs/` references | sonnet | | Network: Crossref | needs-brief |

## Brief format

```
# T### Title
Tier · Depends · Status lives in the board, not here
## Goal            one or two sentences: what exists after this task that did not before
## Files           the only files the coder may create or change
## Spec            signatures, behaviour, edge cases
## Acceptance tests  named tests and what each must assert
## Out of scope    what not to do
```
