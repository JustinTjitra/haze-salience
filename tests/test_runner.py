import numpy as np
import pandas as pd
import pytest
from pandas.testing import assert_series_equal

from haze_salience.events.pilot import run_pilot
from haze_salience.events.runner import EventRun, run_events
from haze_salience.universe import exchange_view

SG_HOLIDAY = pd.Timestamp("2026-10-12")  # SGX closed, IDX open
ID_HOLIDAY = pd.Timestamp("2026-10-20")  # IDX closed, SGX open
SHOCK_DAY = pd.Timestamp("2026-10-16")

UNIVERSE = {
    "exchanges": {"SGX": {"index_ticker": "^STI"}, "IDX": {"index_ticker": "^JKSE"}},
    "firms": [
        {"name": "Sing A", "ticker": "AAA.SI", "exchange": "SGX", "group": "named"},
        {"name": "Sing B", "ticker": "BBB.SI", "exchange": "SGX", "group": "other"},
        {"name": "Jak C", "ticker": "CCC.JK", "exchange": "IDX", "group": "named"},
        {"name": "Jak D", "ticker": "DDD.JK", "exchange": "IDX", "group": "other"},
    ],
}
EVENTS = {
    "e1": {"date": "2026-10-05", "label": "First"},
    "e2": {"date": SHOCK_DAY.date().isoformat(), "label": "Second"},
    "hol": {"date": SG_HOLIDAY.date().isoformat(), "label": "SG holiday"},
    "idhol": {"date": ID_HOLIDAY.date().isoformat(), "label": "ID holiday"},
    "late": {"date": "2026-10-07", "label": "After close", "after_close": True},
    "future": {"date": "2027-06-01", "label": "After the data"},
}
CFG = {"estimation_window": [-100, -31], "event_window": [-5, 5], "min_estimation_days": 60}


def _levels(r):
    return 100 * np.cumprod(1 + r)


def make_prices(seed=11):
    rng = np.random.default_rng(seed)
    full = pd.bdate_range("2026-01-01", "2026-11-06")
    sg_cal = full.drop(SG_HOLIDAY)
    id_cal = full.drop(ID_HOLIDAY)
    cpo_ret = rng.normal(0, 0.015, len(full))
    cpo = pd.Series(_levels(cpo_ret), index=full).drop(pd.Timestamp("2026-09-01"))
    cols = {}
    for cal, idx, firms in [
        (sg_cal, "^STI", {"AAA.SI": (1.0, 0.4), "BBB.SI": (0.8, 0.6)}),
        (id_cal, "^JKSE", {"CCC.JK": (0.9, 0.5), "DDD.JK": (1.1, 0.2)}),
    ]:
        mkt = rng.normal(0, 0.008, len(cal))
        c = pd.Series(cpo_ret, index=full).reindex(cal).to_numpy()
        cols[idx] = pd.Series(_levels(mkt), index=cal)
        for ticker, (bm, bc) in firms.items():
            r = bm * mkt + bc * c + rng.normal(0, 0.01, len(cal))
            if ticker == "AAA.SI":
                r[cal.get_loc(SHOCK_DAY)] -= 0.08
            cols[ticker] = pd.Series(_levels(r), index=cal)
    return pd.DataFrame(cols), cpo


def run(event_ids, exchanges=("SGX", "IDX"), prices=None, universe=UNIVERSE, **kw):
    df, cpo = make_prices() if prices is None else prices
    return run_events(df, universe, EVENTS, event_ids, exchanges, CFG, cpo, **kw)


def test_rows_and_columns():
    out = run(["e1", "e2"])
    assert isinstance(out, EventRun)
    assert out.skipped == []
    assert len(out.summary) == 8
    assert list(out.summary.columns[:4]) == ["exchange", "event", "firm", "group"]
    assert list(out.summary.columns[-2:]) == ["beta_mkt", "beta_cpo"]
    assert list(out.summary["exchange"]) == ["SGX"] * 4 + ["IDX"] * 4
    assert list(out.summary["event"][:4]) == ["e1", "e1", "e2", "e2"]
    assert list(out.summary["group"][:2]) == ["named", "other"]


def test_beta_columns_follow_lags():
    cols = run(["e1"], cpo_lags=(0, 1, 2)).summary.columns
    assert list(cols[-4:]) == ["beta_mkt", "beta_cpo", "beta_cpo_lag1", "beta_cpo_lag2"]
    cols = run(["e1"], cpo_lags=(1,)).summary.columns
    assert list(cols[-2:]) == ["beta_mkt", "beta_cpo_lag1"]
    assert "beta_cpo" not in cols


def test_day0_follows_each_exchange_calendar():
    s = run(["hol"]).summary.set_index(["exchange", "firm"])["day0"]
    assert s.loc["SGX"].eq("2026-10-13").all()
    assert s.loc["IDX"].eq("2026-10-12").all()
    s = run(["idhol"]).summary.set_index(["exchange", "firm"])["day0"]
    assert s.loc["SGX"].eq("2026-10-20").all()
    assert s.loc["IDX"].eq("2026-10-21").all()


def test_after_close_is_honoured():
    s = run(["late"]).summary
    assert s["day0"].eq("2026-10-08").all()
    assert run(["e1"]).summary["day0"].eq("2026-10-05").all()


@pytest.mark.parametrize("seed", [1, 2, 3, 11, 42, 99])
def test_planted_shock_recovered(seed):
    out = run(["e2"], prices=make_prices(seed))
    row = out.summary.set_index(["exchange", "firm"]).loc[("SGX", "Sing A")]
    assert row["car_day0"] == pytest.approx(-0.08, abs=0.04)
    other = out.summary.set_index(["exchange", "firm"]).loc[("SGX", "Sing B")]
    assert abs(other["car_day0"]) < 0.04


def test_matches_run_pilot_for_one_exchange():
    df, cpo = make_prices()
    ours = run(["e1", "e2"], exchanges=("SGX",), prices=(df, cpo), cpo_lags=(0, 1)).summary
    view = exchange_view(UNIVERSE, "SGX")
    pilot_cfg = {**CFG, "events": ["e1", "e2"]}
    theirs = run_pilot(df, view, pilot_cfg, EVENTS, lambda: (cpo, "cpo"), cpo_lags=(0, 1)).summary
    theirs = theirs[theirs["kind"] == "firm"].reset_index(drop=True)
    assert len(ours) == len(theirs) == 4
    for col in ["car_day0", "car_0_1", "t_day0", "sigma", "beta_mkt", "beta_cpo"]:
        assert_series_equal(ours[col], theirs[col], check_exact=True)


def test_missing_ticker_is_skipped():
    universe = {
        **UNIVERSE,
        "firms": [
            *UNIVERSE["firms"],
            {"name": "Ghost", "ticker": "GGG.SI", "exchange": "SGX", "group": "other"},
        ],
    }
    out = run(["e1", "e2"], universe=universe)
    assert len(out.skipped) == 2
    for event_id, msg in zip(["e1", "e2"], out.skipped, strict=True):
        assert msg.startswith(f"SGX / Ghost / {event_id}: ")
    assert "Ghost" not in set(out.summary["firm"])
    assert len(out.summary) == 8


def test_event_after_data_is_skipped():
    out = run(["future", "e1"])
    assert len(out.skipped) == 4
    assert all(" / future: " in m for m in out.skipped)
    assert set(out.summary["event"]) == {"e1"}
    assert len(out.summary) == 4


def test_bad_arguments_raise():
    with pytest.raises(ValueError, match="unknown event"):
        run(["e1", "nope"])
    with pytest.raises(ValueError, match="unknown exchange"):
        run(["e1"], exchanges=("SGX", "NYSE"))
    with pytest.raises(ValueError, match="repeat"):
        run(["e1", "e1"])
    with pytest.raises(ValueError, match="repeat"):
        run(["e1"], exchanges=("SGX", "SGX"))
    with pytest.raises(ValueError, match="duplicate"):
        run(["e1"], cpo_lags=(0, 0))
