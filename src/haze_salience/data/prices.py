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
