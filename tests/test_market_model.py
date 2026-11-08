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
