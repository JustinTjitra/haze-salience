"""Daily abnormal returns for one firm over one haze season.

The market model is estimated on the year's pre-season window (never on season days); the
abnormal return is the residual on every trading day of the season window.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd
import statsmodels.api as sm

from haze_salience.events.market_model import EventStudyError, _forecast_error
from haze_salience.seasons import SeasonWindows


@dataclass(frozen=True)
class SeasonAR:
    year: int
    params: pd.Series
    sigma: float
    n_estimation: int
    ar: pd.Series  # indexed by date, every trading day in the season window
    ar_se: pd.Series  # sigma * sqrt(1 + x' (X'X)^-1 x), as in event_study


def season_abnormal_returns(
    firm: pd.Series, factors: pd.DataFrame, windows: SeasonWindows, min_estimation_days: int
) -> SeasonAR:
    """Market-model abnormal returns for one firm over one season. Shared trading-day index."""
    if not firm.index.equals(factors.index):
        raise EventStudyError("firm and factors must share the same trading-day index.")
    index = pd.DatetimeIndex(firm.index)

    in_est = (index >= windows.est_start) & (index <= windows.est_end)
    X_all = sm.add_constant(factors, has_constant="add")
    valid = in_est & firm.notna().to_numpy() & X_all.notna().all(axis=1).to_numpy()
    n_valid = int(valid.sum())
    if n_valid < min_estimation_days:
        raise EventStudyError(
            f"Only {n_valid} valid estimation days for {firm.name} in {windows.year} "
            f"(need {min_estimation_days})."
        )

    in_season = (index >= windows.season_start) & (index <= windows.season_end)
    positions = np.flatnonzero(in_season)
    if len(positions) == 0:
        raise EventStudyError(f"No trading days in the {windows.year} season window.")

    fit = sm.OLS(firm[valid], X_all[valid]).fit()
    sigma = float(np.sqrt(fit.scale))
    X_fit = X_all[valid].to_numpy(dtype=float)
    # NaN inputs propagate to NaN in both outputs.
    ar_vals, se_vals = _forecast_error(
        firm, factors, positions, fit.params.to_numpy(), X_fit, sigma
    )
    season_index = index[positions]
    return SeasonAR(
        year=windows.year,
        params=fit.params.rename(None),
        sigma=sigma,
        n_estimation=n_valid,
        ar=pd.Series(ar_vals, index=season_index, name="ar"),
        ar_se=pd.Series(se_vals, index=season_index, name="ar_se"),
    )
