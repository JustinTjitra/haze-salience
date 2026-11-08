# Data manifest

Raw and derived data are **never committed** (`data/` is gitignored). This file says where each input
comes from and how to get it. Licence notes are a summary; check each provider's current terms before
redistributing anything.

| Layer | Source | How to get it | Path | Stage | Status |
| --- | --- | --- | --- | --- | --- |
| SGX prices, STI | Yahoo Finance via `yfinance` | `make data` | `data/raw/prices.parquet` | 1 | Automated |
| Soybean oil (CPO fallback) | Yahoo Finance `ZL=F` | `make data` | same file | 1 | Automated |
| Bursa FCPO | Investing.com or Barchart daily history | Manual download, see below | `data/raw/manual/fcpo.csv` | 1 | **Manual** |
| Fire hotspots | NASA FIRMS (VIIRS S-NPP, MODIS) | API with free MAP_KEY | `data/raw/firms/` | 2 | Not started |
| Concessions | Global Forest Watch oil palm concessions | Download | `data/raw/concessions/` | 2 | Not started |
| Concession to parent | Annual and sustainability reports, RSPO | Hand-built table with confidence per link | `data/raw/manual/parents.csv` | 2 | Not started |
| IDX prices, JCI | Yahoo Finance or IDX downloads | TBD | `data/raw/` | 2 | Not started |
| PSI | NEA via data.gov.sg | API | `data/raw/psi/` | 2 | Archive depth unknown, check 2015 coverage first |
| Wind | ERA5 (Copernicus CDS) | CDS API | `data/raw/era5/` | 3 | Not started |

## Bursa FCPO CSV

Yahoo Finance has no Bursa FCPO series, so this one is manual.

1. Download daily history for Bursa Malaysia crude palm oil futures (continuous front-month), covering
   at least `fetch_start` to `fetch_end` in `config/pilot.yaml`.
   - Investing.com: "Crude Palm Oil Futures Historical Data", daily, then *Download* (free account).
   - Barchart: the FCPO continuous contract, *Download* historical data.
2. Save it as `data/raw/manual/fcpo.csv`. Both vendors' column layouts are parsed as-is (date column
   `Date`/`Time`, price column `Price`/`Close`/`Last`/`Settle`; thousands separators are fine).
3. Re-run `make pilot`. The figure caption shows which control was used.

Note the roll: a continuous series jumps when the front month rolls. On roll days the "return" is partly
a calendar spread. Ignored for the pilot; handle it in Stage 2 if the CPO beta turns out to matter.

**Do not use the Bursa Plantation Index as the control.** It is an equity index of the same sector,
so the haze shock moves it too, and controlling for it would absorb the effect being measured.

## Soybean oil fallback caveats

- CBOT closes after SGX, so the same-date ZL=F return partly reflects news from after the SGX close.
  This makes it a noisier control than FCPO, which trades in the same time zone.
- El Niño hits palm supply specifically; soybean oil only captures the broader vegetable-oil move.

## Licences (summary, verify before redistributing)

- **Yahoo Finance:** personal-use terms; do not redistribute the price data. Fetch scripts only.
- **Investing.com / Barchart:** vendor terms; personal use. Do not commit the CSV.
- **NASA FIRMS:** NASA open data policy.
- **Global Forest Watch:** most datasets CC BY 4.0; check the concession layer's own page.
- **data.gov.sg:** Singapore Open Data Licence.
- **ERA5:** Copernicus licence (attribution required).
