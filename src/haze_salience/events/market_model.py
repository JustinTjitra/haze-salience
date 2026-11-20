"""Market-model event study on a trading-day index.

Day 0 is the first trading day on or after the event date, or the first trading day strictly
after it when the event was announced after the close (`after_close`). For each firm and event,
OLS of the firm return on factor returns over the estimation window gives the normal return; the
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

from haze_salience.events.placebo import placebo_pvalue


class EventStudyError(ValueError):
    pass


def _forecast_error(
    firm: pd.Series,
    factors: pd.DataFrame,
    positions: np.ndarray,
    params: np.ndarray,
    X_fit: np.ndarray,
    sigma: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Abnormal return and its forecast SE at integer `positions` of the shared index.

    AR = y - x'b; SE = sigma * sqrt(1 + x' (X'X)^-1 x) with X_fit the rows used in the fit.
    """
    xw = sm.add_constant(factors, has_constant="add").iloc[positions].to_numpy(dtype=float)
    ar = firm.iloc[positions].to_numpy() - xw @ params
    leverage = np.einsum("ij,ji->i", xw, np.linalg.pinv(X_fit.T @ X_fit) @ xw.T)
    return ar, sigma * np.sqrt(1.0 + leverage)


def _sum_offsets(ar: pd.Series, offsets: range) -> float:
    """Sum of `ar` over `offsets`; NaN if any of those offsets is outside the window or NaN."""
    vals = ar.reindex(list(offsets)).to_numpy(dtype=float)
    if np.isnan(vals).any():
        return float("nan")
    return float(vals.sum())


def _placebo_lower(resid: pd.Series, observed: float, length: int) -> float:
    """Lower-tail placebo p-value; NaN (not an error) when the observed value is NaN."""
    if np.isnan(observed):
        return float("nan")
    return placebo_pvalue(resid, observed, length, "lower")


@dataclass(frozen=True)
class EventResult:
    day0: pd.Timestamp
    params: pd.Series
    sigma: float
    n_estimation: int
    ar: pd.Series  # indexed by trading-day offset
    car: pd.Series
    band: pd.Series  # half-width of the ~95% band around CAR
    ar_se: pd.Series  # per-day forecast SE of the AR, incl. market-model estimation error
    resid: pd.Series  # estimation-window OLS residuals, indexed by date (valid rows only)

    def summary(self) -> dict:
        ar = self.ar
        car_0_1 = _sum_offsets(ar, range(0, 2))
        car_0_3 = _sum_offsets(ar, range(0, 4))
        day0_ar = float(ar.reindex([0]).iloc[0])
        return {
            "day0": self.day0.date().isoformat(),
            "n_estimation": self.n_estimation,
            "sigma": self.sigma,
            "car_pre": ar.loc[:-1].sum(),  # drift before the event
            "car_day0": ar.loc[0],
            "car_post": ar.loc[0:].sum(),  # day 0 through end of window
            "car_total": ar.sum(),
            "band_total": self.band.iloc[-1],
            "t_day0": self.ar.loc[0] / self.ar_se.loc[0],
            "car_0_1": car_0_1,  # short window: day 0 and day 1
            "car_0_3": car_0_3,  # short window: day 0 through day 3
            "p_placebo_day0": _placebo_lower(self.resid, day0_ar, 1),
            "p_placebo_0_1": _placebo_lower(self.resid, car_0_1, 2),
        }


def locate_day0(index: pd.DatetimeIndex, event_date, after_close: bool = False) -> int:
    """Position of day 0 for an event dated `event_date`.

    By default this is the first trading day on or after `event_date`. With `after_close=True`
    (news posted after the market closed) it is the first trading day strictly after it.
    """
    side = "right" if after_close else "left"
    pos = int(pd.DatetimeIndex(index).searchsorted(pd.Timestamp(event_date), side=side))
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
    after_close: bool = False,
) -> EventResult:
    """Run the market model for one firm and one event. `firm` and `factors` share an index."""
    if not firm.index.equals(factors.index):
        raise EventStudyError("firm and factors must share the same trading-day index.")
    index = firm.index
    day0 = locate_day0(index, event_date, after_close)
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
    X_fit = X[valid].to_numpy(dtype=float)
    ar_vals, se_vals = _forecast_error(
        firm, factors, positions[in_range], fit.params.to_numpy(), X_fit, sigma
    )
    ar = pd.Series(np.nan, index=offsets, name="ar")
    ar[in_range] = ar_vals
    car = ar.cumsum().rename("car")
    band = pd.Series(
        1.96 * sigma * np.sqrt(np.arange(1, len(offsets) + 1)), index=offsets, name="band"
    )
    ar_se = pd.Series(np.nan, index=offsets, name="ar_se")
    ar_se[in_range] = se_vals
    resid = fit.resid.rename("resid")

    return EventResult(
        day0=pd.Timestamp(index[day0]),
        params=fit.params.rename(None),
        sigma=sigma,
        n_estimation=n_valid,
        ar=ar,
        car=car,
        band=band,
        ar_se=ar_se,
        resid=resid,
    )
