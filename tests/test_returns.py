import numpy as np
import pandas as pd
import pytest

from haze_salience.events.returns import build_returns

CAL = pd.bdate_range("2026-01-01", "2026-03-31")


def _view(index, firms):
    return {
        "market_index": {"ticker": index},
        "firms": [{"name": n, "ticker": t} for n, t in firms.items()],
    }


def _levels(values):
    """Wide closes from {col: list of prices} on a 5-day business calendar."""
    idx = pd.bdate_range("2026-01-05", periods=5)
    return pd.DataFrame(values, index=idx)


def test_calendar_follows_index():
    prices = _levels({"IDX": [100, 101, np.nan, 103, 104], "AAA": [10, 11, 12, 13, 14]})
    rets = build_returns(prices, _view("IDX", {"A": "AAA"}), prices["AAA"])
    gone = prices.index[2]
    assert gone not in rets.index
    # first calendar day dropped, 3 returns remain (4 index days)
    assert list(rets.index) == [prices.index[i] for i in (1, 3, 4)]
    assert rets.loc[prices.index[3], "A"] == pytest.approx(13 / 11 - 1)  # return over the gap
    assert rets.loc[prices.index[3], "mkt"] == pytest.approx(103 / 101 - 1)


def test_control_holiday_forward_fill():
    prices = _levels({"IDX": [100.0, 101, 102, 103, 104]})
    holiday = prices.index[2]
    cpo = pd.Series([50.0, 55.0, 60.0, 66.0], index=prices.index.drop(holiday))
    rets = build_returns(prices, _view("IDX", {}), cpo)
    assert rets.loc[holiday, "cpo"] == 0.0
    # catch-up on the next day: 55 -> 60 is the move missed on the holiday
    assert rets.loc[prices.index[3], "cpo"] == pytest.approx(60 / 55 - 1)
    assert rets.loc[prices.index[1], "cpo"] == pytest.approx(55 / 50 - 1)


def test_two_exchanges_get_different_calendars():
    idx = pd.bdate_range("2026-02-02", periods=8)
    sgx_hol, idx_hol = idx[2], idx[5]
    prices = pd.DataFrame(
        {
            "^STI": np.linspace(100, 107, 8),
            "^JKSE": np.linspace(200, 214, 8),
            "AAA.SI": np.linspace(10, 17, 8),
            "BBB.JK": np.linspace(20, 27, 8),
        },
        index=idx,
    )
    prices.loc[sgx_hol, "^STI"] = np.nan
    prices.loc[idx_hol, "^JKSE"] = np.nan
    cpo = pd.Series(np.linspace(50, 57, 8), index=idx)
    sg = build_returns(prices, _view("^STI", {"A": "AAA.SI"}), cpo)
    jk = build_returns(prices, _view("^JKSE", {"B": "BBB.JK"}), cpo)
    assert sgx_hol not in sg.index and sgx_hol in jk.index
    assert idx_hol not in jk.index and idx_hol in sg.index
    assert not sg.index.equals(jk.index)
    assert list(sg.columns) == ["A", "mkt", "cpo"]
    assert list(jk.columns) == ["B", "mkt", "cpo"]


def test_missing_ticker_is_all_nan():
    prices = _levels({"IDX": [100.0, 101, 102, 103, 104], "AAA": [10.0, 11, 12, 13, 14]})
    view = _view("IDX", {"A": "AAA", "Ghost": "ZZZ"})
    rets = build_returns(prices, view, prices["AAA"])
    assert rets["Ghost"].isna().all() and len(rets["Ghost"]) == 4
    assert rets["A"].notna().all()


def test_lag_columns():
    prices = _levels({"IDX": [100.0, 101, 102, 103, 104]})
    cpo = pd.Series([10.0, 11.0, 12.1, 12.1, 13.31], index=prices.index)
    rets = build_returns(prices, _view("IDX", {}), cpo, cpo_lags=(0, 1, 2))
    assert list(rets.columns) == ["mkt", "cpo", "cpo_lag1", "cpo_lag2"]
    c = rets["cpo"].to_numpy()  # [0.1, 0.1, 0.0, 0.1]
    assert c == pytest.approx([0.1, 0.1, 0.0, 0.1])
    assert rets["cpo_lag1"].isna().tolist() == [True, False, False, False]
    assert rets["cpo_lag1"].to_numpy()[1:] == pytest.approx(c[:-1])
    assert rets["cpo_lag2"].isna().tolist() == [True, True, False, False]
    assert rets["cpo_lag2"].to_numpy()[2:] == pytest.approx(c[:-2])


def test_default_has_no_lag_columns():
    prices = _levels({"IDX": [100.0, 101, 102, 103, 104]})
    rets = build_returns(prices, _view("IDX", {}), prices["IDX"])
    assert list(rets.columns) == ["mkt", "cpo"]


def test_lag_validation():
    prices = _levels({"IDX": [100.0, 101, 102, 103, 104]})
    with pytest.raises(ValueError, match="non-negative"):
        build_returns(prices, _view("IDX", {}), prices["IDX"], cpo_lags=(0, -1))
    with pytest.raises(ValueError, match="duplicates"):
        build_returns(prices, _view("IDX", {}), prices["IDX"], cpo_lags=(1, 1))
