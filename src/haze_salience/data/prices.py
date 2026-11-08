"""Daily price fetch (network) and cache (offline)."""

from pathlib import Path

import pandas as pd

CACHE_FILE = "prices.parquet"


def fetch_prices(tickers: list[str], start: str, end: str) -> pd.DataFrame:
    """Dividend- and split-adjusted daily closes from Yahoo Finance, one column per ticker.

    `end` is inclusive here (yfinance treats it as exclusive, so we add a day).
    """
    import yfinance as yf

    end_excl = (pd.Timestamp(end) + pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    raw = yf.download(
        tickers, start=start, end=end_excl, auto_adjust=True, progress=False, group_by="column"
    )
    if raw is None or raw.empty:
        raise RuntimeError(f"No data returned for {tickers}; check network access and tickers.")
    close = raw["Close"]
    if isinstance(close, pd.Series):
        close = close.to_frame(tickers[0])
    missing = [t for t in tickers if t not in close.columns or close[t].dropna().empty]
    if missing:
        raise RuntimeError(f"No prices for {missing}; possibly delisted or wrong ticker.")
    close.index = pd.DatetimeIndex(close.index).tz_localize(None).normalize()
    close.columns.name = None
    return close.sort_index()


def save_prices(prices: pd.DataFrame, cache_dir: str | Path) -> Path:
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / CACHE_FILE
    prices.to_parquet(path)
    return path


def load_prices(cache_dir: str | Path) -> pd.DataFrame:
    path = Path(cache_dir) / CACHE_FILE
    if not path.exists():
        raise FileNotFoundError(f"{path} not found. Run `make data` first to fetch prices.")
    return pd.read_parquet(path)
