"""Return table for one exchange, on that exchange's own trading calendar."""

from collections.abc import Sequence

import pandas as pd

from haze_salience.data.align import align_to_calendar, simple_returns


def validate_lags(cpo_lags: Sequence[int]) -> list[int]:
    """Return `cpo_lags` as a list; raise ValueError on negative or duplicate lags."""
    lags = list(cpo_lags)
    if any(k < 0 for k in lags):
        raise ValueError(f"cpo_lags must be non-negative, got {lags}")
    if len(set(lags)) != len(lags):
        raise ValueError(f"cpo_lags must not contain duplicates, got {lags}")
    return lags


def build_returns(
    prices: pd.DataFrame,
    view: dict,
    cpo: pd.Series,
    cpo_lags: Sequence[int] = (0,),
) -> pd.DataFrame:
    """Simple returns of firms, market, control and control lags on the index's calendar.

    `prices` are wide closes (one column per ticker); `view` is `exchange_view(...)`.
    The calendar is the dates where the index ticker has a price. Columns: one per firm name
    (prices reindexed to the calendar, not filled; a ticker missing from `prices` gives an
    all-NaN column), `mkt`, `cpo` (control forward-filled onto the calendar) and `cpo_lag{k}`
    for each k > 0, the control's return k calendar days earlier. The first calendar day is
    dropped by `simple_returns`; lags are shifted after that drop. `cpo` is always present,
    whether or not 0 is in `cpo_lags`.
    """
    lags = validate_lags(cpo_lags)
    index_ticker = view["market_index"]["ticker"]
    calendar = prices[index_ticker].dropna().index
    nan = pd.Series(float("nan"), index=calendar)
    levels = pd.DataFrame(
        {
            f["name"]: prices[f["ticker"]].reindex(calendar) if f["ticker"] in prices else nan
            for f in view["firms"]
        }
    )
    levels["mkt"] = prices[index_ticker].reindex(calendar)
    levels["cpo"] = align_to_calendar(calendar, cpo)
    rets = simple_returns(levels)
    for k in lags:
        if k > 0:
            rets[f"cpo_lag{k}"] = rets["cpo"].shift(k)
    return rets
