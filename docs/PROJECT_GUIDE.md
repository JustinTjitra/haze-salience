# Project guide

Last updated: 2026-11-20. This is the working plan. The research design it implements is
[`design.md`](design.md); the task board that executes it is [`../tasks/README.md`](../tasks/README.md).

## 1. The question

**Does public, satellite-observable fire information reach palm oil stock prices immediately, or only
once haze makes it salient to investors?**

Fires in plantation concessions are visible from space within hours and published free by NASA. If
prices respond to that information only when Singapore's air turns bad, that is direct evidence of
attention-driven slow information diffusion.

## 2. Deliverables

| # | Deliverable | Done when |
| --- | --- | --- |
| D1 | **Stage 1 pilot result**: abnormal returns of the SGX palm oil names around the October 2026 events | `make pilot` run on real data; figure, summary table and report committed under `outputs/figures/` |
| D2 | **Go/no-go decision** (owner) | Recorded in `tasks/DECISIONS.md` by 29 Nov 2026 |
| D3 | **Firm-day panel**: fire exposure, abnormal returns, PSI, controls for four haze seasons | `data/processed/panel.parquet` builds from one command; schema tests pass |
| D4 | **Frozen pre-registration** (owner) | `docs/preregistration.md` tagged `prereg-v1` before any Stage 2 regression on real data |
| D5 | **Stage 2 result**: tests of H1 and H2 with few-cluster inference, plus robustness table | Tables and figures committed under `outputs/stage2/`, produced after D4 |
| D6 | **Research note** (4 to 6 pages) | `docs/note.md` with method, results, threats, and a one-sentence headline number |
| D7 | **Reproducible repository** | A stranger can run `make setup data pilot` and get D1; CI is green |

Target dates: D1 and D2 by 29 Nov 2026; D3 to D5 by 28 Jan 2027; D6 and D7 by 31 Jan 2027.
Stage 3 (wind instrument) is after that date.

## 3. Methodology in brief

**Signal.** Fire exposure for firm *i* on day *t* = NASA FIRMS hotspots inside *i*'s concessions,
per 1,000 ha of concession area. A buffer version counts hotspots in a ring outside the boundary.

**Attention shock.** Singapore's 24-hour PSI. It depends on wind as much as on fires, so it moves
investor attention without changing what any one firm's concessions are doing.

**Stage 1, pilot event study (2026 only).** Market model on the STI and crude palm oil for each SGX
name; abnormal returns around the dated attention events. Reads: did the early NGO report move the
named firms, and how large was the mid-October move once the government spoke?

**Stage 2, panel regression (2015, 2019, 2023, 2026).** Daily abnormal return on ten lags of fire
exposure, the exposure × high-PSI interaction, and controls, with firm and season fixed effects.
H1 is the cumulative lag effect; H2 is the interaction. Inference is built for a small number of
firms.

**Stage 3, wind instrument.** High-PSI instrumented with the share of southerly to south-westerly
wind hours at Singapore.

**Discipline.** The Stage 2 specification is pre-registered and frozen before it is run on real
data. A null result is reported as a result.

## 4. Main features of the codebase

| Feature | Where | Status |
| --- | --- | --- |
| Price fetch and offline cache | `src/haze_salience/data/prices.py` | Done |
| CPO control: FCPO CSV with soybean oil fallback, labelled in outputs | `data/cpo.py` | Done |
| Calendar alignment across exchanges | `data/align.py` | Done |
| Market-model event study with CAR and band | `events/market_model.py` | Done |
| Pilot runner, figure, summary CSV | `events/pilot.py`, `events/plot.py`, `cli.py` | Done, not yet run on real data |
| Small-sample inference for the pilot (forecast-error variance, portfolios, placebo p-values) | `events/` | Phase 1 tasks |
| Multi-exchange, multi-season event runner | `events/`, `config/` | Phase 2 tasks |
| PSI salience measure | `data/psi.py` | Phase 2 tasks |
| FIRMS loader, concession loader, spatial join, exposure panel | `data/`, `spatial/` | Phase 3, after the gate |
| Panel regression, cumulative-effect test, wild-cluster bootstrap | `panel/` | Phase 3, after the gate |
| Offline tests on synthetic data with planted effects | `tests/` | Ongoing: every task adds its own |

## 5. Plan of action

Work is split into small tasks (one commit each) on the [task board](../tasks/README.md). Phases:

**Phase 1. Finish the pilot (now to 29 Nov).**
1. Harden pilot inference so five firms sharing one event date are handled honestly: forecast-error
   variance, equal-weighted and named-minus-unnamed portfolios, placebo p-values, short windows.
2. Handle the soybean-oil timing problem (CBOT closes after SGX) with a lagged control term.
3. Add abnormal volume as a second, attention-flavoured outcome.
4. Owner: verify the event dates and tickers; download the FCPO CSV.
5. Run the pilot on real data and commit the outputs (needs network access to Yahoo Finance).
6. **Gate G1 (owner, by 29 Nov): go/no-go.**

**Phase 2. Infrastructure both stories need (can start now).**
7. Universe with IDX names and per-exchange calendars; seasons configuration; season-long abnormal
   returns; multi-event runner; PSI daily measure and high-PSI flag; events schema with a `verified`
   flag.

**Phase 3. Diffusion chain (only after G1 = go).**
8. FIRMS client and cleaning; concession loader; parent-link table (owner builds the content);
   spatial join and buffers; exposure panel with lags.
9. Panel assembly; main regression; cumulative-effect test; bootstrap; robustness runner; tables.
10. **Gate G2 (owner): resolve the DECIDE items and freeze the pre-registration (`prereg-v1`).**
11. Run Stage 2 on real data, once.

**Phase 4. Write-up (January).**
12. Note skeleton with tables and figures wired in; owner writes the interpretation.

**Phase 5. Stage 3 wind instrument (after 31 Jan).**

### Go/no-go at G1

Proposed reading of the pilot, to be confirmed by the owner **before** looking at the real output:

| Reaction to the early NGO report | Reaction in mid-October | Reading | Next step |
| --- | --- | --- | --- |
| No | Yes | Inattention until salience | Go: full diffusion design |
| Yes | Yes | Partial underreaction | Go: full diffusion design |
| Yes | No | NGO news priced; statement was not news | Go, with H3 moved up |
| No | No | No measurable price effect | Rescope to the regulatory-event story; skip Phase 3 |

"Reaction" = the named-firm (or all-firm) portfolio abnormal return over days [0, +1] is negative with
a placebo p-value below 0.10. This threshold is a planning rule for a five-firm pilot, not a claim of
statistical significance.

## 6. Who does what

| Role | Does | Does not |
| --- | --- | --- |
| **Owner** | Decisions at G1 and G2; verifies event dates and tickers; builds the concession-to-parent table; downloads manual data; approves network access and keys; writes the interpretation | |
| **Planner** (expensive model) | Picks tasks, writes and repairs task briefs, reviews every diff, solves problems the coders could not, runs real-data tasks, keeps the log | Make owner decisions; edit protected files |
| **Coder** (cheaper model, one per task) | Implements exactly one task brief with tests | Touch files outside the brief; change tests to make them pass |

The loop protocol, tiers and hard limits are in [`../tasks/README.md`](../tasks/README.md) and
[`../CLAUDE.md`](../CLAUDE.md).

## 7. Open risks found by the source research (20 Nov 2026)

All of these come from search-result summaries and still need checking on the original pages. Full
notes: [`../reports/Haze salience project sources.md`](../reports/Haze%20salience%20project%20sources.md).

| # | Risk | Why it matters | Action |
| --- | --- | --- | --- |
| R1 | **Event timing.** The Prime Minister's statement appears to have been a Facebook post late on Thu 15 Oct, after the close; the share fall was Fri 16 Oct. The unhealthy-PSI streak appears to have started on 5 Oct, the same day as the Greenpeace report | Day 0 = 16 Oct still holds, but 5 Oct is confounded: NGO report and the start of the haze streak coincide. Singapore press coverage of the report seems to date from about 15 Oct | Owner verifies and updates `config/events.yaml`; the pilot report must state the confound |
| R2 | **More events than the design lists.** SGX RegCo queries (15 to 16 Oct), company denials (15 to 16 Oct), NEA notices (about 16, 19 and 23 Oct), a second Greenpeace report (13 Nov) | H3 needs the full list; some fall inside the pilot's event window | Add to `events.yaml` once verified |
| R3 | **S-NPP VIIRS reportedly stopped delivering data on 1 to 2 Nov 2026 and was non-nominal from July 2026** | The draft pre-registration uses S-NPP for all four seasons | New DECIDE item: sensor choice (MODIS for all seasons, or NOAA-20 from 2019 with MODIS for 2015) |
| R4 | **IDX lower price limit reportedly asymmetric (7%) from 19 Oct 2026** | Limit days mimic drift; the rule differs by season | Verify the full 2015 to 2026 rule history before the limit-day flag task is briefed |
| R5 | **Concession polygons may be hard to get.** GFW's oil palm layer is described as incomplete and its download details are unconfirmed; Indonesian official data are restricted; other atlases have no bulk download | Without polygons there is no firm-level exposure, so this decides whether Phase 3 is feasible at all | Confirm a usable source **before** G1; if none, the regulatory-event story is the fallback regardless of the pilot |
| R6 | **Historical FIRMS data may need a manual archive request** (emailed link) | The loop cannot fetch 2015, 2019, 2023 unattended | Owner requests the archive extracts once |
| R7 | **Inference choice.** A methods reviewer argued date-clustering alone may understate standard errors and suggested two-way clustering or Driscoll-Kraay | Changes the confirmatory p-values | New DECIDE item in the pre-registration |
| R8 | **Novelty not fully checked.** No prior study linking hotspots to palm oil stock returns was found, but SSRN and Google Scholar could not be searched directly | Positioning of the note | Owner runs a manual search before claiming novelty |

## 8. Integrity rules

1. No Stage 2 regression on real data before `prereg-v1` exists.
2. Nothing synthetic is ever written to `outputs/`. Synthetic data lives only in `tests/`.
3. Raw data is never committed. Sources and licences are in [`data_manifest.md`](data_manifest.md).
4. Events are facts with sources. An event is used in a reported result only if `verified: true`.
5. Every reported number can be regenerated by a command in the README.
