import numpy as np
import pandas as pd
import pytest

from haze_salience.events.market_model import EventStudyError, event_study, locate_day0

EST = (-150, -31)
WIN = (-10, 10)


def test_locate_day0_on_trading_day(calendar):
    assert calendar[locate_day0(calendar, "2026-10-16")] == pd.Timestamp("2026-10-16")


def test_locate_day0_rolls_weekend_forward(calendar):
    # 2026-10-03 is a Saturday -> Monday 2026-10-05
    assert calendar[locate_day0(calendar, "2026-10-03")] == pd.Timestamp("2026-10-05")


def test_locate_day0_after_data_raises(calendar):
    with pytest.raises(EventStudyError):
        locate_day0(calendar, "2027-01-04")


def test_recovers_betas_and_planted_shock(synthetic_returns):
    df = synthetic_returns.copy()
    day0 = pd.Timestamp("2026-10-16")
    df.loc[day0, "firm"] += -0.08

    res = event_study(df["firm"], df[["mkt", "cpo"]], day0, EST, WIN, min_estimation_days=100)

    assert res.n_estimation == 120
    assert res.params["mkt"] == pytest.approx(1.2, abs=0.25)
    assert res.params["cpo"] == pytest.approx(0.5, abs=0.15)
    assert res.sigma == pytest.approx(0.01, rel=0.2)
    # Day-0 AR carries the shock (plus one day of 1% noise)
    assert res.ar.loc[0] == pytest.approx(-0.08, abs=0.03)
    # The jump in CAR from day -1 to day 0 is the day-0 AR
    assert res.car.loc[0] - res.car.loc[-1] == pytest.approx(res.ar.loc[0])
    assert list(res.ar.index) == list(range(-10, 11))


def test_band_grows_with_sqrt_days(synthetic_returns):
    df = synthetic_returns
    res = event_study(df["firm"], df[["mkt", "cpo"]], "2026-10-16", EST, WIN, 100)
    # band half-width at offset tau covers (tau + 11) days
    assert res.band.loc[-10] == pytest.approx(1.96 * res.sigma * 1.0)
    assert res.band.loc[10] == pytest.approx(1.96 * res.sigma * np.sqrt(21))


def test_estimation_window_excludes_event_period(synthetic_returns):
    """A huge shock inside the event window must not move the betas."""
    df = synthetic_returns.copy()
    base = event_study(df["firm"], df[["mkt", "cpo"]], "2026-10-16", EST, WIN, 100)
    df.loc["2026-10-05":"2026-10-30", "firm"] -= 0.05
    shocked = event_study(df["firm"], df[["mkt", "cpo"]], "2026-10-16", EST, WIN, 100)
    pd.testing.assert_series_equal(base.params, shocked.params)


def test_window_before_data_start_raises(synthetic_returns):
    df = synthetic_returns
    with pytest.raises(EventStudyError, match="before the start"):
        event_study(df["firm"], df[["mkt", "cpo"]], "2026-01-15", EST, WIN, 100)


def test_too_few_valid_estimation_days_raises(synthetic_returns):
    df = synthetic_returns.copy()
    day0 = locate_day0(df.index, "2026-10-16")
    df.iloc[day0 - 150 : day0 - 60, df.columns.get_loc("firm")] = np.nan  # 90 missing
    with pytest.raises(EventStudyError, match="valid estimation days"):
        event_study(df["firm"], df[["mkt", "cpo"]], "2026-10-16", EST, WIN, 100)


def test_summary_windows(synthetic_returns):
    df = synthetic_returns
    res = event_study(df["firm"], df[["mkt", "cpo"]], "2026-10-16", EST, WIN, 100)
    s = res.summary()
    assert s["car_pre"] == pytest.approx(res.ar.loc[-10:-1].sum())
    assert s["car_day0"] == pytest.approx(res.ar.loc[0])
    assert s["car_post"] == pytest.approx(res.ar.loc[0:10].sum())


def _fixture_design(df, factors=("mkt", "cpo")):
    day0 = locate_day0(df.index, "2026-10-16")
    est = slice(day0 - 150, day0 - 30)
    X = np.column_stack([np.ones(120), df[list(factors)].iloc[est].to_numpy()])
    return day0, X


def test_ar_se_matches_hand_formula(synthetic_returns):
    df = synthetic_returns
    res = event_study(df["firm"], df[["mkt", "cpo"]], "2026-10-16", EST, WIN, 100)
    day0, X = _fixture_design(df)
    xtx_inv = np.linalg.inv(X.T @ X)
    for tau in (-10, 0, 10):
        x = np.array([1.0, df["mkt"].iloc[day0 + tau], df["cpo"].iloc[day0 + tau]])
        expected = res.sigma * np.sqrt(1 + x @ xtx_inv @ x)
        assert res.ar_se.loc[tau] == pytest.approx(expected)


def test_ar_se_at_least_sigma(synthetic_returns):
    df = synthetic_returns
    res = event_study(df["firm"], df[["mkt", "cpo"]], "2026-10-16", EST, WIN, 100)
    se = res.ar_se.dropna()
    assert len(se) == 21
    assert (se >= res.sigma).all()
    assert (se < 1.05 * res.sigma).all()


def test_ar_se_grows_with_extreme_factor(synthetic_returns):
    df = synthetic_returns.copy()
    day0 = pd.Timestamp("2026-10-16")
    df.loc[day0, "mkt"] = 10 * df["mkt"].std()
    res = event_study(df["firm"], df[["mkt", "cpo"]], day0, EST, WIN, 100)
    assert res.ar_se.loc[0] > 1.05 * res.ar_se.loc[1]


def test_resid_properties(synthetic_returns):
    df = synthetic_returns
    res = event_study(df["firm"], df[["mkt", "cpo"]], "2026-10-16", EST, WIN, 100)
    n = res.n_estimation
    assert len(res.resid) == n
    assert isinstance(res.resid.index, pd.DatetimeIndex)
    assert abs(res.resid.mean()) < 1e-10
    assert np.sqrt((res.resid**2).sum() / (n - 3)) == pytest.approx(res.sigma)


def test_t_day0_in_summary(synthetic_returns):
    df = synthetic_returns
    res = event_study(df["firm"], df[["mkt", "cpo"]], "2026-10-16", EST, WIN, 100)
    assert res.summary()["t_day0"] == pytest.approx(res.ar.loc[0] / res.ar_se.loc[0])
