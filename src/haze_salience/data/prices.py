"""Daily price and volume fetch (network) and cache (offline)."""

from pathlib import Path

import pandas as pd

PRICES = "prices"
VOLUMES = "volumes"


def fetch_ohlcv(tickers: list[str], start: str, end: str) -> dict[str, pd.DataFrame]:
    """Dividend- and split-adjusted daily closes and volumes from Yahoo Finance.

    Returns {"close": frame, "volume": frame}, each with one column per ticker and a
    tz-naive, sorted DatetimeIndex. `end` is inclusive here (yfinance treats it as
    exclusive, so we add a day).
    """
    import yfinance as yf

    end_excl = (pd.Timestamp(end) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    raw = yf.download(
        tickers, start=start, end=end_excl, auto_adjust=True, progress=False, group_by="column"
    )
    if raw is None or raw.empty:
        raise RuntimeError(f"No data returned for {tickers}; check network access and tickers.")

    out = {}
    for key, field in (("close", "Close"), ("volume", "Volume")):
        wide = raw[field]
        if isinstance(wide, pd.Series):
            wide = wide.to_frame(tickers[0])
        wide.index = pd.DatetimeIndex(wide.index).tz_localize(None).normalize()
        wide.columns.name = None
        out[key] = wide.sort_index()

    close = out["close"]
    missing = [t for t in tickers if t not in close.columns or close[t].dropna().empty]
    if missing:
        raise RuntimeError(f"No prices for {missing}; possibly delisted or wrong ticker.")
    return out


def fetch_prices(tickers: list[str], start: str, end: str) -> pd.DataFrame:
    """Dividend- and split-adjusted daily closes from Yahoo Finance, one column per ticker."""
    return fetch_ohlcv(tickers, start, end)["close"]


def save_frame(df: pd.DataFrame, cache_dir: str | Path, name: str) -> Path:
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / f"{name}.parquet"
    df.to_parquet(path)
    return path


def load_frame(cache_dir: str | Path, name: str) -> pd.DataFrame:
    path = Path(cache_dir) / f"{name}.parquet"
    if not path.exists():
        raise FileNotFoundError(f"{path} not found. Run `make data` first to fetch {name}.")
    return pd.read_parquet(path)


def save_prices(prices: pd.DataFrame, cache_dir: str | Path) -> Path:
    return save_frame(prices, cache_dir, PRICES)


def load_prices(cache_dir: str | Path) -> pd.DataFrame:
    return load_frame(cache_dir, PRICES)


def save_volumes(volumes: pd.DataFrame, cache_dir: str | Path) -> Path:
    return save_frame(volumes, cache_dir, VOLUMES)


def load_volumes(cache_dir: str | Path) -> pd.DataFrame:
    return load_frame(cache_dir, VOLUMES)


EARLY_END_DAYS = 7


def coverage_report(prices: pd.DataFrame) -> pd.DataFrame:
    """Per-ticker history coverage, one row per column of `prices`.

    Columns: `first_date` and `last_date` (first and last non-NaN dates, NaT if the column
    is all NaN), `n_obs` (non-NaN count), `n_missing` (NaN count between first_date and
    last_date inclusive) and `ends_early` (True if last_date is more than 7 calendar days
    before the frame's last index date, or if the column has no data at all).
    """
    frame_end = pd.Timestamp(prices.index.max()) if len(prices.index) else pd.NaT
    rows = []
    for ticker in prices.columns:
        s = prices[ticker]
        valid = s.dropna()
        if valid.empty:
            first = last = pd.NaT
            n_missing = 0
            ends_early = True
        else:
            first, last = valid.index.min(), valid.index.max()
            in_span = (s.index >= first) & (s.index <= last)
            n_missing = int(s[in_span].isna().sum())
            ends_early = bool((frame_end - last) > pd.Timedelta(days=EARLY_END_DAYS))
        rows.append(
            {
                "first_date": first,
                "last_date": last,
                "n_obs": int(len(valid)),
                "n_missing": n_missing,
                "ends_early": ends_early,
            }
        )
    out = pd.DataFrame(
        rows,
        index=pd.Index(list(prices.columns), name="ticker"),
        columns=["first_date", "last_date", "n_obs", "n_missing", "ends_early"],
    )
    out["first_date"] = pd.to_datetime(out["first_date"])
    out["last_date"] = pd.to_datetime(out["last_date"])
    out["n_obs"] = out["n_obs"].astype("int64")
    out["n_missing"] = out["n_missing"].astype("int64")
    out["ends_early"] = out["ends_early"].astype(bool)
    return out
