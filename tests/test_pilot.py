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
    assert len(out.summary) == 4
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
    assert set(out.summary["firm"]) == {"Named Co"}
    assert len(out.skipped) == 2
