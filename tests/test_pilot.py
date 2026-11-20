import numpy as np
import pandas as pd
import pytest

from haze_salience.events.pilot import run_pilot
from haze_salience.events.plot import plot_pilot

UNIVERSE = {
    "market_index": {"ticker": "^STI"},
    "firms": [
        {"name": "Named Co", "ticker": "AAA.SI", "greenpeace_named_2026": True},
        {"name": "Other Co", "ticker": "BBB.SI", "greenpeace_named_2026": False},
    ],
}
EVENTS = {
    "e1": {"date": "2026-10-05", "label": "Report"},
    "e2": {"date": "2026-10-16", "label": "Statement"},
}
CFG = {
    "events": ["e1", "e2"],
    "estimation_window": [-150, -31],
    "event_window": [-10, 10],
    "min_estimation_days": 100,
}


@pytest.fixture
def prices():
    """SGX calendar with a holiday; CPO on a different calendar; -9% hit to Named Co on 16 Oct."""
    rng = np.random.default_rng(7)
    cal = pd.bdate_range("2025-12-01", "2026-11-06").drop(pd.Timestamp("2026-08-10"))  # SG holiday
    n = len(cal)
    mkt = rng.normal(0, 0.008, n)
    cpo = rng.normal(0, 0.015, n)
    a = 1.0 * mkt + 0.4 * cpo + rng.normal(0, 0.01, n)
    b = 0.8 * mkt + 0.6 * cpo + rng.normal(0, 0.01, n)
    a[cal.get_loc(pd.Timestamp("2026-10-16"))] -= 0.09
    to_level = lambda r: 100 * np.cumprod(1 + r)  # noqa: E731
    df = pd.DataFrame(
        {"^STI": to_level(mkt), "AAA.SI": to_level(a), "BBB.SI": to_level(b)}, index=cal
    )
    # Bursa closed on a day SGX trades
    cpo_series = pd.Series(to_level(cpo), index=cal).drop(pd.Timestamp("2026-09-01"))
    return df, cpo_series


def test_run_pilot_end_to_end(prices, tmp_path):
    df, cpo = prices
    out = run_pilot(df, UNIVERSE, CFG, EVENTS, lambda: (cpo, "test CPO"))

    assert out.skipped == []
    assert (out.summary["kind"] == "firm").sum() == 4
    assert out.day0_positions["e2"] - out.day0_positions["e1"] == 9
    hit = out.summary.set_index(["event", "firm"]).loc[("e2", "Named Co")]
    assert hit["car_day0"] == pytest.approx(-0.09, abs=0.035)
    assert out.control_label == "test CPO"

    fig = plot_pilot(out, UNIVERSE, EVENTS, tmp_path / "fig.png")
    assert fig.exists() and fig.stat().st_size > 10_000


def test_short_history_firm_is_skipped_not_fatal(prices):
    df, cpo = prices
    df = df.copy()
    df.loc[:"2026-08-31", "BBB.SI"] = np.nan  # listed late: too little estimation data
    out = run_pilot(df, UNIVERSE, CFG, EVENTS, lambda: (cpo, "test CPO"))
    firm_rows = out.summary[out.summary["kind"] == "firm"]
    assert set(firm_rows["firm"]) == {"Named Co"}
    assert sum(m.startswith("Other Co / ") for m in out.skipped) == 2
    assert len(out.skipped) == 8


PORTFOLIOS = {"All firms", "Named", "Not named", "Named minus not named"}


def test_summary_has_portfolio_rows(prices):
    df, cpo = prices
    out = run_pilot(df, UNIVERSE, CFG, EVENTS, lambda: (cpo, "test CPO"))
    for event_id in CFG["events"]:
        sub = out.summary[out.summary["event"] == event_id]
        port = sub[sub["kind"] == "portfolio"]
        assert set(port["firm"]) == PORTFOLIOS
        assert port["greenpeace_named"].isna().all()
        assert set(sub[sub["kind"] == "firm"]["firm"]) == {"Named Co", "Other Co"}
        assert set(out.portfolios[event_id]) == PORTFOLIOS
        assert set(out.results[event_id]) == {"Named Co", "Other Co"}
    assert (out.summary.query("kind == 'portfolio'")["n_members"] == 2).any()


def test_named_minus_not_named_captures_planted_shock(prices):
    df, cpo = prices
    out = run_pilot(df, UNIVERSE, CFG, EVENTS, lambda: (cpo, "test CPO"))
    row = out.summary.set_index(["event", "firm"]).loc[("e2", "Named minus not named")]
    assert row["car_day0"] == pytest.approx(-0.09, abs=0.04)


def test_portfolio_members_exclude_skipped_firms(prices):
    df, cpo = prices
    df = df.copy()
    df.loc[:"2026-08-31", "BBB.SI"] = np.nan  # "Other Co" skipped
    out = run_pilot(df, UNIVERSE, CFG, EVENTS, lambda: (cpo, "test CPO"))
    for event_id in CFG["events"]:
        assert set(out.portfolios[event_id]) == {"Named"}
        for name in ("All firms", "Not named", "Named minus not named"):
            assert any(m.startswith(f"{name} / {event_id}") for m in out.skipped)


@pytest.fixture
def lagged_prices():
    """Firm 'Named Co' returns load 0.4 on today's CPO return and 0.5 on yesterday's."""
    rng = np.random.default_rng(11)
    cal = pd.bdate_range("2025-12-01", "2026-11-06")
    n = len(cal)
    mkt = rng.normal(0, 0.008, n)
    cpo = rng.normal(0, 0.015, n)
    cpo_prev = np.concatenate([[0.0], cpo[:-1]])
    a = 1.0 * mkt + 0.4 * cpo + 0.5 * cpo_prev + rng.normal(0, 0.005, n)
    b = 0.8 * mkt + rng.normal(0, 0.01, n)
    to_level = lambda r: 100 * np.cumprod(1 + r)  # noqa: E731
    df = pd.DataFrame(
        {"^STI": to_level(mkt), "AAA.SI": to_level(a), "BBB.SI": to_level(b)}, index=cal
    )
    return df, pd.Series(to_level(cpo), index=cal)


def test_default_has_no_lag_columns(prices):
    df, cpo = prices
    out = run_pilot(df, UNIVERSE, CFG, EVENTS, lambda: (cpo, "test CPO"))
    assert "beta_cpo_lag1" not in out.summary.columns
    assert "beta_cpo" in out.summary.columns
    assert out.control_label == "test CPO"


def test_lagged_control_is_recovered(lagged_prices):
    df, cpo = lagged_prices
    out = run_pilot(df, UNIVERSE, CFG, EVENTS, lambda: (cpo, "test CPO"), cpo_lags=(0, 1))
    row = out.summary.set_index(["event", "firm"]).loc[("e1", "Named Co")]
    assert row["beta_cpo_lag1"] == pytest.approx(0.5, abs=0.15)
    assert row["beta_cpo"] == pytest.approx(0.4, abs=0.15)
    assert "beta_cpo_lag1" in out.summary.columns
    assert out.summary["beta_cpo_lag1"].notna().all()


def test_label_mentions_lags(lagged_prices):
    df, cpo = lagged_prices
    out = run_pilot(df, UNIVERSE, CFG, EVENTS, lambda: (cpo, "test CPO"), cpo_lags=(0, 1))
    assert out.control_label == "test CPO + lags 1"


@pytest.mark.parametrize("bad", [(-1,), (0, 0)])
def test_bad_lags_raise(prices, bad):
    df, cpo = prices
    with pytest.raises(ValueError):
        run_pilot(df, UNIVERSE, CFG, EVENTS, lambda: (cpo, "test CPO"), cpo_lags=bad)
