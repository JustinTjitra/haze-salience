# data/

Everything under here is gitignored. See [`docs/data_manifest.md`](../docs/data_manifest.md) for sources.

- `raw/`: as downloaded (`make data` writes `raw/prices.parquet`)
- `raw/manual/`: hand-downloaded or hand-built files (`fcpo.csv`, later `parents.csv`)
- `interim/`: cleaned intermediate tables
- `processed/`: the firm-day panel (Stage 2)
