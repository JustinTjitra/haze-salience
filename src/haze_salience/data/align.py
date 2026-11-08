"""Put series from different exchanges on one trading calendar."""

import pandas as pd


def align_to_calendar(calendar: pd.DatetimeIndex, prices: pd.Series | pd.DataFrame):
    """Reindex prices onto `calendar`, forward-filling gaps.

    Used for control series that trade on a different calendar (e.g. Bursa FCPO vs SGX).
    A day the control market is closed gets the previous price, so its return is zero and
    the move shows up on the next shared trading day instead of being dropped.
    Dates not on the calendar are discarded after filling.
    """
    calendar = pd.DatetimeIndex(calendar)
    union = prices.index.union(calendar)
    return prices.reindex(union).sort_index().ffill().reindex(calendar)


def simple_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Simple daily returns; the first row is dropped."""
    return prices.pct_change(fill_method=None).iloc[1:]
