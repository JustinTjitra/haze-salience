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


