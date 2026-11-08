"""Crude palm oil price control: Bursa FCPO from a manual CSV, soybean oil as fallback.

Yahoo Finance has no Bursa FCPO series, so FCPO comes from a one-off vendor download
(see docs/data_manifest.md). Do not substitute the Bursa Plantation Index: it is equity,
so the haze shock moves it too, and controlling for it absorbs the effect under study.
"""

from collections.abc import Callable
from pathlib import Path

import pandas as pd

FCPO_LABEL = "Bursa FCPO (manual CSV)"
FALLBACK_LABEL = "CBOT soybean oil (ZL=F), FCPO proxy"

_DATE_COLS = ("date", "time", "timestamp")
_PRICE_COLS = ("price", "close", "last", "settle", "settlement")


def _pick(columns, candidates, what):
    lower = {c.strip().lower(): c for c in columns}
    for cand in candidates:
        if cand in lower:
            return lower[cand]
    raise ValueError(
        f"Could not find a {what} column among {list(columns)}; expected one of {candidates}"
    )


def load_fcpo_csv(path: str | Path) -> pd.Series:
    """Parse a daily FCPO CSV in Investing.com or Barchart format into a price series."""
    df = pd.read_csv(path, dtype=str)
    date_col = _pick(df.columns, _DATE_COLS, "date")
    price_col = _pick(df.columns, _PRICE_COLS, "price")
    dates = pd.to_datetime(df[date_col], format="mixed")
    prices = pd.to_numeric(df[price_col].str.replace(",", "", regex=False))
    s = pd.Series(prices.to_numpy(), index=pd.DatetimeIndex(dates).normalize(), name="CPO")
    return s[~s.index.duplicated(keep="last")].sort_index()


def load_cpo(manual_csv: str | Path, fallback: Callable[[], pd.Series]) -> tuple[pd.Series, str]:
    """Return (price series, label) for the CPO control, preferring the manual FCPO CSV."""
    manual_csv = Path(manual_csv)
    if manual_csv.exists():
        return load_fcpo_csv(manual_csv), FCPO_LABEL
    return fallback().rename("CPO"), FALLBACK_LABEL
