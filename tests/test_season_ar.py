import numpy as np
import pandas as pd
import pytest

from haze_salience.events.market_model import EventStudyError
from haze_salience.events.season_ar import season_abnormal_returns
from haze_salience.seasons import SeasonWindows

MIN_DAYS = 60
ALPHA, B_MKT, B_CPO = 0.0002, 1.2, 0.5
SD_MKT, SD_CPO, SD_EPS = 0.008, 0.015, 0.01
W2026 = SeasonWindows(
    year=2026,
    season_start=pd.Timestamp("2026-08-01"),
    season_end=pd.Timestamp("2026-11-30"),
    est_start=pd.Timestamp("2026-02-01"),
    est_end=pd.Timestamp("2026-06-30"),
)


def make_data(seed=7):
    """Four years of weekdays; r = 0.0002 + 1.2 mkt + 0.5 cpo + eps (sd 1%)."""
    idx = pd.bdate_range("2023-01-02", "2026-12-31")
    rng = np.random.default_rng(seed)
    n = len(idx)
    mkt = rng.normal(0.0, SD_MKT, n)
    cpo = rng.normal(0.0, SD_CPO, n)
    firm = ALPHA + B_MKT * mkt + B_CPO * cpo + rng.normal(0.0, SD_EPS, n)
    factors = pd.DataFrame({"mkt": mkt, "cpo": cpo}, index=idx)
    return pd.Series(firm, index=idx, name="firm"), factors


def test_recovers_betas_and_zero_mean_ar():
    firm, factors = make_data()
    res = season_abnormal_returns(firm, factors, W2026, MIN_DAYS)
    n = res.n_estimation
    # Tolerance = 3 standard errors of each OLS coefficient given the simulated noise:
    # SE(beta_j) = sd_eps / (sd_j * sqrt(n)); SE(alpha) = sd_eps / sqrt(n).
    assert abs(res.params["mkt"] - B_MKT) < 3 * SD_EPS / (SD_MKT * np.sqrt(n))
    assert abs(res.params["cpo"] - B_CPO) < 3 * SD_EPS / (SD_CPO * np.sqrt(n))
    assert abs(res.params["const"] - ALPHA) < 3 * SD_EPS / np.sqrt(n)
    # Mean of m season ARs has SE about mean(ar_se) / sqrt(m).
    m = len(res.ar)
    assert abs(res.ar.mean()) < 3 * res.ar_se.mean() / np.sqrt(m)
    assert res.year == 2026


def test_planted_season_shock():
    firm, factors = make_data()
    base = season_abnormal_returns(firm, factors, W2026, MIN_DAYS)
    day = pd.Timestamp("2026-10-14")
    shocked = firm.copy()
    shocked.loc[day] -= 0.06
    res = season_abnormal_returns(shocked, factors, W2026, MIN_DAYS)
    assert res.ar.loc[day] - base.ar.loc[day] == pytest.approx(-0.06, abs=1e-12)
    # The recovered AR is -6% plus ordinary forecast noise (4 SE leaves room for rare tails).
    assert abs(res.ar.loc[day] + 0.06) < 4 * res.ar_se.loc[day]


def test_estimation_excludes_season():
    firm, factors = make_data()
    base = season_abnormal_returns(firm, factors, W2026, MIN_DAYS)
    shifted = firm.copy()
    in_season = (shifted.index >= W2026.season_start) & (shifted.index <= W2026.season_end)
    shifted[in_season] += 0.05
    res = season_abnormal_returns(shifted, factors, W2026, MIN_DAYS)
    pd.testing.assert_series_equal(res.params, base.params)
    assert res.sigma == base.sigma
    assert (res.ar - base.ar).to_numpy() == pytest.approx(0.05)


def test_ar_index_is_season_only():
    firm, factors = make_data()
    res = season_abnormal_returns(firm, factors, W2026, MIN_DAYS)
    assert res.ar.index[0] >= W2026.season_start
    assert res.ar.index[-1] <= W2026.season_end
    assert res.ar.index.equals(res.ar_se.index)
    expected = firm.index[(firm.index >= W2026.season_start) & (firm.index <= W2026.season_end)]
    assert res.ar.index.equals(expected)


def test_too_few_estimation_days_raises():
    firm, factors = make_data()
    with pytest.raises(EventStudyError):
        season_abnormal_returns(firm, factors, W2026, 500)
    # NaNs in the estimation window count against the minimum.
    holed = firm.copy()
    est = (holed.index >= W2026.est_start) & (holed.index <= W2026.est_end)
    holed[est] = np.nan
    with pytest.raises(EventStudyError):
        season_abnormal_returns(holed, factors, W2026, MIN_DAYS)


def test_no_season_rows_raises():
    firm, factors = make_data()
    cut = firm.index <= pd.Timestamp("2026-07-31")
    with pytest.raises(EventStudyError):
        season_abnormal_returns(firm[cut], factors[cut], W2026, MIN_DAYS)


def test_nan_factor_gives_nan_ar():
    firm, factors = make_data()
    day = pd.Timestamp("2026-09-09")
    factors = factors.copy()
    factors.loc[day, "mkt"] = np.nan
    res = season_abnormal_returns(firm, factors, W2026, MIN_DAYS)
    assert np.isnan(res.ar.loc[day])
    assert np.isnan(res.ar_se.loc[day])
    assert res.ar.drop(day).notna().all()


def test_mismatched_index_raises():
    firm, factors = make_data()
    with pytest.raises(EventStudyError):
        season_abnormal_returns(firm.iloc[1:], factors, W2026, MIN_DAYS)
