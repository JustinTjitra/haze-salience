"""Market-model event study on a trading-day index.

Day 0 is the first trading day on or after the event date. For each firm and event, OLS of
the firm return on factor returns over the estimation window gives the normal return; the
abnormal return (AR) is the residual over the event window and CAR accumulates it from the
first day of the event window.

The band is +/- 1.96 * sigma * sqrt(days accumulated), with sigma the estimation-window
residual SD. It ignores parameter-estimation error and cross-firm correlation, so treat it
as descriptive, not as a test.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd
import statsmodels.api as sm


class EventStudyError(ValueError):
    pass


@dataclass(frozen=True)
class EventResult:
    day0: pd.Timestamp
    params: pd.Series
    sigma: float
    n_estimation: int
    ar: pd.Series  # indexed by trading-day offset
    car: pd.Series
    band: pd.Series  # half-width of the ~95% band around CAR

    def summary(self) -> dict:
        ar = self.ar
        return {
            "day0": self.day0.date().isoformat(),
            "n_estimation": self.n_estimation,
            "sigma": self.sigma,
            "car_pre": ar.loc[:-1].sum(),  # drift before the event
            "car_day0": ar.loc[0],
            "car_post": ar.loc[0:].sum(),  # day 0 through end of window
            "car_total": ar.sum(),
            "band_total": self.band.iloc[-1],
        }


def locate_day0(index: pd.DatetimeIndex, event_date) -> int:
    """Position of the first trading day on or after `event_date`."""
    pos = int(pd.DatetimeIndex(index).searchsorted(pd.Timestamp(event_date), side="left"))
    if pos >= len(index):
        raise EventStudyError(f"Event date {event_date} is after the last trading day in the data.")
    return pos


def event_study(
    firm: pd.Series,
    factors: pd.DataFrame,
    event_date,
    estimation_window: tuple[int, int],
    event_window: tuple[int, int],
    min_estimation_days: int,
) -> EventResult:
    """Run the market model for one firm and one event. `firm` and `factors` share an index."""
    if not firm.index.equals(factors.index):
        raise EventStudyError("firm and factors must share the same trading-day index.")
    index = firm.index
    day0 = locate_day0(index, event_date)
    est_lo, est_hi = estimation_window
    win_lo, win_hi = event_window
    if not est_hi < win_lo:
        raise EventStudyError("Estimation window must end before the event window starts.")
    if day0 + est_lo < 0:
        raise EventStudyError(
            f"Estimation window for {event_date} starts before the start of the data; "
            "fetch more history."
        )

    est = slice(day0 + est_lo, day0 + est_hi + 1)
    y = firm.iloc[est]
    X = sm.add_constant(factors.iloc[est], has_constant="add")
    valid = y.notna() & X.notna().all(axis=1)
    n_valid = int(valid.sum())
    if n_valid < min_estimation_days:
        raise EventStudyError(
            f"Only {n_valid} valid estimation days for {firm.name} around {event_date} "
            f"(need {min_estimation_days})."
        )
    fit = sm.OLS(y[valid], X[valid]).fit()
    sigma = float(np.sqrt(fit.scale))

    offsets = pd.RangeIndex(win_lo, win_hi + 1, name="offset")
    positions = day0 + np.asarray(offsets)
    in_range = (positions >= 0) & (positions < len(index))
    Xw = sm.add_constant(factors, has_constant="add").iloc[positions[in_range]]
    ar_vals = firm.iloc[positions[in_range]].to_numpy() - Xw.to_numpy() @ fit.params.to_numpy()
    ar = pd.Series(np.nan, index=offsets, name="ar")
    ar[in_range] = ar_vals
    car = ar.cumsum().rename("car")
    band = pd.Series(
        1.96 * sigma * np.sqrt(np.arange(1, len(offsets) + 1)), index=offsets, name="band"
    )

    return EventResult(
        day0=pd.Timestamp(index[day0]),
        params=fit.params.rename(None),
        sigma=sigma,
        n_estimation=n_valid,
        ar=ar,
        car=car,
        band=band,
    )
