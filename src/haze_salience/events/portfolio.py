"""Equal-weighted portfolio and long-short return series."""

from __future__ import annotations

import pandas as pd


def portfolio_return(rets: pd.DataFrame, members: list[str], name: str) -> pd.Series:
    """Equal-weighted mean of `members` columns per day; NaN if any member is NaN that day."""
    if not members:
        raise ValueError("members must not be empty")
    missing = [m for m in members if m not in rets.columns]
    if missing:
        raise ValueError(f"members not in columns: {missing}")
    out = rets[list(members)].mean(axis=1, skipna=False)
    out.name = name
    return out


def long_short_return(
    rets: pd.DataFrame, long: list[str], short: list[str], name: str
) -> pd.Series:
    """Long portfolio return minus short portfolio return."""
    overlap = sorted(set(long) & set(short))
    if overlap:
        raise ValueError(f"names in both long and short: {overlap}")
    out = portfolio_return(rets, long, "long") - portfolio_return(rets, short, "short")
    out.name = name
    return out
