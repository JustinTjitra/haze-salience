"""Standardised abnormal volume around an event.

Volume is an attention outcome. For each event, log volume on the event window is compared
with the mean and standard deviation of log volume over an estimation window that ends before
the event window starts:

    z_tau = (log v_tau - mean_est) / std_est

The z-score is descriptive, like the market-model band in `market_model`: it ignores
autocorrelation and cross-firm correlation, so it is not a test on its own.
"""

import numpy as np
import pandas as pd

from haze_salience.events.market_model import EventStudyError, locate_day0


def abnormal_volume(
    volume: pd.Series,
    event_date,
    estimation_window: tuple[int, int],
    event_window: tuple[int, int],
    min_estimation_days: int,
    after_close: bool = False,
) -> pd.Series:
    """Standardised log-volume abnormality for each offset in `event_window`.

    `volume` is indexed by trading day. Offsets are trading-day offsets from day 0, the first
    trading day on or after `event_date` (strictly after it when `after_close` is set). Zero or
    negative volume is treated as missing. The result is indexed by a RangeIndex named `offset`;
    offsets outside the data are NaN.
    """
    day0 = locate_day0(pd.DatetimeIndex(volume.index), event_date, after_close)
    est_lo, est_hi = estimation_window
    win_lo, win_hi = event_window
    if day0 + est_lo < 0:
        raise EventStudyError(
            f"Estimation window for {event_date} starts before the start of the data; "
            "fetch more history."
        )

    raw = volume.astype(float)
    logv = np.log(raw.where(raw > 0))
    est = logv.iloc[day0 + est_lo : day0 + est_hi + 1].dropna()
    n_valid = len(est)
    # The sample SD (ddof=1) needs at least two valid days, whatever the caller asks for.
    need = max(min_estimation_days, 2)
    if n_valid < need:
        raise EventStudyError(
            f"Only {n_valid} valid estimation days of volume around {event_date} (need {need})."
        )
    mean_est = float(est.mean())
    std_est = float(est.std(ddof=1))
    if not std_est > 0:
        raise EventStudyError(
            f"Estimation-window log volume has zero variance around {event_date}."
        )

    offsets = pd.RangeIndex(win_lo, win_hi + 1, name="offset")
    positions = day0 + np.asarray(offsets)
    in_range = (positions >= 0) & (positions < len(logv))
    values = np.full(len(offsets), np.nan)
    values[in_range] = logv.to_numpy()[positions[in_range]]
    z = (values - mean_est) / std_est
    return pd.Series(z, index=offsets, name="z")
