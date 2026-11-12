# WIP - haze-salience

**Does public, satellite-observable fire information reach palm oil stock prices immediately, or only
once haze makes it salient to investors?**

In 2026, NASA FIRMS showed plantation fires in near real time from August, Greenpeace named specific
SGX-listed firms on 5 October, and the big price move came on 16 October, when Singapore's prime
minister said the government was looking into which firms were responsible. This project measures
that lag directly: the underlying information is observable from space, timestamped daily and public,
which makes it a clean test of gradual information diffusion (Hong and Stein 1999).

Full research design: [`docs/design.md`](docs/design.md).

## Status

| Stage | What | Status |
| --- | --- | --- |
| 1 | Pilot event study: 5 SGX names around 5 Oct and 16 Oct 2026 | Code and tests done; awaiting real data run |
| 2 | Panel regression over the 2015, 2019, 2023, 2026 haze seasons | Pre-registration [drafted](docs/preregistration.md), not frozen |
| 3 | Wind instrument for salience (ERA5) | Not started |

## Reproduce the pilot

Requires [uv](https://docs.astral.sh/uv/).

```bash
make setup     # create the environment
make data      # fetch SGX prices, the STI and soybean oil from Yahoo Finance
make pilot     # writes outputs/figures/pilot_car.png and pilot_car_summary.csv
```

For the main CPO control, first download a Bursa FCPO daily CSV to `data/raw/manual/fcpo.csv`
([how](docs/data_manifest.md#bursa-fcpo-csv)). Without it, the pilot falls back to CBOT soybean oil
and says so in the figure caption.

```bash
make test      # offline: synthetic data with known betas and a planted shock
make lint
```

## Pilot method

- Simple daily returns on adjusted closes, on the SGX trading calendar. The CPO series is
  forward-filled onto it, so a Bursa holiday is a zero return followed by the catch-up.
- Day 0 = first SGX trading day on or after the event date.
- Market model per firm and event: OLS on STI and CPO returns over trading days [-150, -31].
  The 16 Oct estimation window ends before 5 Oct, so the first event does not contaminate the second.
- AR and CAR over [-10, +10], with a band of ±1.96 σ √days from the estimation residuals.

**How to read it.** With 5 firms and 2 events this is descriptive, not a test. The cumulative band
gets wide fast (around ±11% by day +10 for a stock with 1.2% daily idiosyncratic volatility), so a
large one-day drop can stay inside it. Judge the events on the day-0 and short-window ARs in
`pilot_car_summary.csv` (`car_day0` against 1.96 σ), and on pre-event drift (`car_pre`). The
question the pilot answers first: did the 5 October report move prices at all?

## Layout

```
config/            universe, hand-coded events, pilot parameters
docs/              research design, Stage 2 pre-registration, data manifest
src/haze_salience/
  data/            prices (yfinance + cache), CPO (FCPO CSV / soybean fallback), Stage 2 stubs
  events/          market model, pilot orchestration, figure
  cli.py           python -m haze_salience {fetch,pilot}
tests/             offline tests
outputs/figures/   committed results
```

Raw data is never committed; see [`docs/data_manifest.md`](docs/data_manifest.md).

## License

Code: MIT. Data belongs to its providers; see the manifest.
