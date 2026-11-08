# haze-salience repo: scaffold and Stage 1 pilot

Date: 2026-11-08 · Status: approved · Research design: [`docs/design.md`](../../design.md)

## Decisions

| Decision | Choice | Why |
| --- | --- | --- |
| Home | Standalone repo `JustinTjitra/haze-salience` | Geospatial dependency stack differs from `influencenetworks`; own URL for the resume line |
| Visibility | Public from day one | A public, tagged pre-registration of the Stage 2 spec answers the multiple-testing threat |
| First scope | Full layout, only the Stage 1 path implemented | The 29 Nov go/no-go depends only on the pilot; Stage 2 loaders are wasted work on a no-go |
| CPO control | Manual Bursa FCPO CSV, CBOT soybean oil (`ZL=F`) fallback | Yahoo has no FCPO series; the Bursa Plantation Index is equity and absorbs the haze shock, so it is not a valid control |
| Tooling | Python package (`src/` layout), `uv`, `Makefile`, `pytest`, `ruff` | One-command reproduction; testable; shows Python fluency |
| Raw data | Gitignored; fetch scripts and a manifest are committed | Redistributing vendor price data is a licensing grey area |

## Layout

```
config/       universe.yaml, events.yaml, pilot.yaml
docs/         design.md, preregistration.md (DRAFT), data_manifest.md
data/         raw/, raw/manual/, interim/, processed/  (gitignored)
src/haze_salience/
  data/       prices.py, cpo.py, firms.py*, concessions.py*, psi.py*   (* Stage 2 stubs)
  events/     market_model.py, plot.py
  cli.py      python -m haze_salience {fetch,pilot}
tests/        offline only: synthetic and fixture data
outputs/figures/pilot_car.png  (committed result)
```

## Stage 1 method

- Simple daily returns on dividend-adjusted closes.
- Trading calendar is the SGX calendar (the dates on which the STI trades). Control series (CPO) are forward-filled onto it, so a Bursa holiday shows a zero return and the catch-up lands on the next shared day.
- Day 0 is the first SGX trading day on or after the event date.
- Market model per firm and event: OLS of r_i on r_STI and r_CPO over trading days [-150, -31] relative to day 0 (120 days ending 30 days before).
- Abnormal return AR = r_i - fitted; CAR accumulated over [-10, +10].
- Band: CAR ± 1.96 · σ̂ · √(days accumulated), with σ̂ the estimation-window residual SD. Descriptive only; with 5 firms and 2 events this is not a hypothesis test, and the README says so.
- The 16 Oct estimation window ends before 5 Oct, so event 1 does not contaminate event 2's betas.
- If a firm has fewer than 100 valid estimation days, skip it for that event and say so.
- Output: one figure, one panel per event, a line per firm, with the control series used stated in the caption.

## Data flow

`make data` fetches prices into `data/raw/` (parquet). `make pilot` reads only the cache, so the analysis is deterministic and tests never touch the network. If `data/raw/manual/fcpo.csv` is missing, the pilot uses soybean oil and labels the figure accordingly.

## Testing

- Market model: synthetic returns with known betas and a planted −8% day-0 shock; betas and CAR recovered within tolerance; band widens with √days.
- Event alignment: an event on a non-trading day maps to the next trading day; short estimation windows are refused.
- CPO: FCPO CSV preferred when present; fallback label when absent; holiday forward-fill produces a zero return then catch-up.
- Prices: cached path read without network; missing cache gives a clear error that names `make data`.

## Pre-registration

`docs/preregistration.md` drafts the Stage 2 main spec with explicit defaults (K = 10 lags, HighPSI = 24h PSI > 100, VIIRS nominal + high confidence, inside-concession exposure per 1,000 ha, date-clustered SEs plus wild-cluster bootstrap). It stays DRAFT until the author tags `prereg-v1`, before any Stage 2 regression is run.

## Known open items

- Universe listing status not verified (`verify: true` in `universe.yaml`); confirm every ticker is still listed on SGX.
- This cloud environment's network blocks Yahoo Finance, so the real pilot figure must be produced after allowing the host or on a local machine.
