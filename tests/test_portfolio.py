import numpy as np
import pandas as pd
import pytest

from haze_salience.events.market_model import event_study
from haze_salience.events.portfolio import long_short_return, portfolio_return

EST = (-150, -31)
WIN = (-10, 10)
DAY0 = pd.Timestamp("2026-10-16")


def test_equal_weight_mean():
    df = pd.DataFrame(
        {"a": [0.01, 0.02, -0.03], "b": [0.03, 0.00, 0.03], "c": [0.02, 0.04, 0.00]},
        index=pd.bdate_range("2026-01-05", periods=3),
    )
    out = portfolio_return(df, ["a", "b", "c"], "p")
    assert out.name == "p"
    np.testing.assert_allclose(out.to_numpy(), [0.02, 0.02, 0.0], atol=1e-12)
    ab = portfolio_return(df, ["a", "b"], "q")
    np.testing.assert_allclose(ab.to_numpy(), [0.02, 0.01, 0.0], atol=1e-12)


def test_nan_is_strict():
    df = pd.DataFrame(
        {"a": [0.01, np.nan, 0.03], "b": [0.02, 0.02, 0.02]},
        index=pd.bdate_range("2026-01-05", periods=3),
    )
    out = portfolio_return(df, ["a", "b"], "p")
    assert out.isna().tolist() == [False, True, False]
    assert out.iloc[0] == pytest.approx(0.015)
    assert out.iloc[2] == pytest.approx(0.025)


def test_errors():
    df = pd.DataFrame({"a": [0.01], "b": [0.02], "c": [0.03]})
    with pytest.raises(ValueError):
        portfolio_return(df, [], "p")
    with pytest.raises(ValueError):
        portfolio_return(df, ["a", "zzz"], "p")
    with pytest.raises(ValueError):
        long_short_return(df, ["a", "b"], ["b", "c"], "ls")


def _firms(calendar, n_firms, shocked, seed=7):
    rng = np.random.default_rng(seed)
    n = len(calendar)
    mkt = rng.normal(0.0, 0.008, n)
    cpo = rng.normal(0.0, 0.015, n)
    data = {"mkt": mkt, "cpo": cpo}
    for i in range(n_firms):
        data[f"f{i}"] = 1.0 * mkt + 0.5 * cpo + rng.normal(0.0, 0.01, n)
    df = pd.DataFrame(data, index=calendar)
    for col in shocked:
        df.loc[DAY0, col] += -0.05
    return df


def test_portfolio_event_study_recovers_common_shock(calendar):
    firms = [f"f{i}" for i in range(5)]
    df = _firms(calendar, 5, firms)
    port = portfolio_return(df, firms, "port")
    res = event_study(port, df[["mkt", "cpo"]], DAY0, EST, WIN, min_estimation_days=100)
    assert res.ar.loc[0] == pytest.approx(-0.05, abs=0.015)
    assert res.sigma == pytest.approx(0.01 / np.sqrt(5), rel=0.25)


def test_long_short_cancels_common_factors(calendar):
    long = ["f0", "f1", "f2"]
    short = ["f3", "f4", "f5"]
    df = _firms(calendar, 6, long)
    ls = long_short_return(df, long, short, "ls")
    assert ls.name == "ls"
    res = event_study(ls, df[["mkt", "cpo"]], DAY0, EST, WIN, min_estimation_days=100)
    assert res.ar.loc[0] == pytest.approx(-0.05, abs=0.02)
    assert abs(res.params["mkt"]) < 0.1
    assert abs(res.params["cpo"]) < 0.1
