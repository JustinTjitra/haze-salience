import pandas as pd
import pytest
import yfinance

from haze_salience.data.prices import (
    coverage_report,
    fetch_ohlcv,
    load_prices,
    load_volumes,
    save_prices,
    save_volumes,
)


def test_round_trip_through_cache(tmp_path):
    df = pd.DataFrame(
        {"F34.SI": [3.0, 3.1], "^STI": [3500.0, 3510.0]},
        index=pd.to_datetime(["2026-10-15", "2026-10-16"]),
    )
    save_prices(df, tmp_path)
    out = load_prices(tmp_path)
    pd.testing.assert_frame_equal(out, df, check_freq=False, check_names=False)


def test_missing_cache_points_to_make_data(tmp_path):
    with pytest.raises(FileNotFoundError, match="make data"):
        load_prices(tmp_path)


def test_fetch_ohlcv_splits_columns(monkeypatch):
    idx = pd.date_range("2026-10-15", periods=3, freq="D", tz="Asia/Singapore")
    cols = pd.MultiIndex.from_tuples(
        [("Close", "F34.SI"), ("Close", "^STI"), ("Volume", "F34.SI"), ("Volume", "^STI")]
    )
    raw = pd.DataFrame(
        [
            [3.0, 3500.0, 1000.0, 2000.0],
            [3.1, 3510.0, 1100.0, 2100.0],
            [3.2, 3520.0, 1200.0, 2200.0],
        ],
        index=idx,
        columns=cols,
    )
    # Reversed row order: the result must come back sorted.
    monkeypatch.setattr(yfinance, "download", lambda tickers, **kwargs: raw.iloc[::-1])

    out = fetch_ohlcv(["F34.SI", "^STI"], "2026-10-15", "2026-10-17")

    assert set(out) == {"close", "volume"}
    for frame in out.values():
        assert list(frame.columns) == ["F34.SI", "^STI"]
        assert frame.index.tz is None
        assert frame.index.is_monotonic_increasing
        assert frame.index[0] == pd.Timestamp("2026-10-15")
    assert out["close"]["F34.SI"].tolist() == [3.0, 3.1, 3.2]
    assert out["close"]["^STI"].tolist() == [3500.0, 3510.0, 3520.0]
    assert out["volume"]["F34.SI"].tolist() == [1000.0, 1100.0, 1200.0]
    assert out["volume"]["^STI"].tolist() == [2000.0, 2100.0, 2200.0]


def test_fetch_ohlcv_single_ticker(monkeypatch):
    idx = pd.date_range("2026-10-15", periods=2, freq="D", tz="Asia/Singapore")
    raw = pd.DataFrame({"Close": [3.0, 3.1], "Volume": [1000.0, 1100.0]}, index=idx)
    monkeypatch.setattr(yfinance, "download", lambda tickers, **kwargs: raw)

    out = fetch_ohlcv(["F34.SI"], "2026-10-15", "2026-10-16")

    assert list(out["close"].columns) == ["F34.SI"]
    assert list(out["volume"].columns) == ["F34.SI"]
    assert out["close"]["F34.SI"].tolist() == [3.0, 3.1]
    assert out["volume"]["F34.SI"].tolist() == [1000.0, 1100.0]


def test_fetch_raises_on_missing_ticker(monkeypatch):
    idx = pd.date_range("2026-10-15", periods=2, freq="D", tz="Asia/Singapore")
    cols = pd.MultiIndex.from_tuples(
        [("Close", "F34.SI"), ("Close", "BAD.SI"), ("Volume", "F34.SI"), ("Volume", "BAD.SI")]
    )
    raw = pd.DataFrame(
        [[3.0, float("nan"), 1000.0, 0.0], [3.1, float("nan"), 1100.0, 0.0]],
        index=idx,
        columns=cols,
    )
    monkeypatch.setattr(yfinance, "download", lambda tickers, **kwargs: raw)

    with pytest.raises(RuntimeError, match="BAD.SI"):
        fetch_ohlcv(["F34.SI", "BAD.SI"], "2026-10-15", "2026-10-16")


def test_volume_round_trip(tmp_path):
    df = pd.DataFrame(
        {"F34.SI": [1000.0, 1100.0], "^STI": [2000.0, 2100.0]},
        index=pd.to_datetime(["2026-10-15", "2026-10-16"]),
    )
    path = save_volumes(df, tmp_path)
    assert path.name == "volumes.parquet"
    out = load_volumes(tmp_path)
    pd.testing.assert_frame_equal(out, df, check_freq=False, check_names=False)


def test_missing_volume_cache_points_to_make_data(tmp_path):
    with pytest.raises(FileNotFoundError, match="make data"):
        load_volumes(tmp_path)


def _coverage_frame():
    idx = pd.date_range("2026-10-01", periods=30, freq="D")  # last index date 2026-10-30
    values = [float(i) for i in range(30)]
    full = pd.Series(values, index=idx)
    gap = pd.Series(values, index=idx)
    gap.iloc[[10, 11]] = float("nan")  # two interior NaN, dates 2026-10-11 and 2026-10-12
    early = pd.Series(values, index=idx)
    early.iloc[16:] = float("nan")  # last value 2026-10-16, two weeks before the frame end
    return pd.DataFrame({"FULL": full, "GAP": gap, "EARLY": early})


def test_coverage_report_counts():
    report = coverage_report(_coverage_frame())

    assert list(report.index) == ["FULL", "GAP", "EARLY"]
    assert list(report.columns) == ["first_date", "last_date", "n_obs", "n_missing", "ends_early"]

    full = report.loc["FULL"]
    assert full["first_date"] == pd.Timestamp("2026-10-01")
    assert full["last_date"] == pd.Timestamp("2026-10-30")
    assert full["n_obs"] == 30
    assert full["n_missing"] == 0
    assert bool(full["ends_early"]) is False

    gap = report.loc["GAP"]
    assert gap["first_date"] == pd.Timestamp("2026-10-01")
    assert gap["last_date"] == pd.Timestamp("2026-10-30")
    assert gap["n_obs"] == 28
    assert gap["n_missing"] == 2
    assert bool(gap["ends_early"]) is False

    early = report.loc["EARLY"]
    assert early["first_date"] == pd.Timestamp("2026-10-01")
    assert early["last_date"] == pd.Timestamp("2026-10-16")
    assert early["n_obs"] == 16
    assert early["n_missing"] == 0
    assert bool(early["ends_early"]) is True


def test_coverage_report_all_nan_column():
    idx = pd.date_range("2026-10-01", periods=5, freq="D")
    prices = pd.DataFrame({"DEAD": [float("nan")] * 5, "OK": [1.0] * 5}, index=idx)

    report = coverage_report(prices)

    dead = report.loc["DEAD"]
    assert pd.isna(dead["first_date"])
    assert pd.isna(dead["last_date"])
    assert dead["n_obs"] == 0
    assert dead["n_missing"] == 0
    assert bool(dead["ends_early"]) is True
    assert report.loc["OK", "n_obs"] == 5


def test_coverage_report_ends_early_threshold_is_strictly_over_seven_days():
    idx = pd.date_range("2026-10-01", periods=20, freq="D")  # last index date 2026-10-20
    seven = pd.Series(1.0, index=idx)
    seven.iloc[13:] = float("nan")  # last value 2026-10-13: exactly 7 days early
    eight = pd.Series(1.0, index=idx)
    eight.iloc[12:] = float("nan")  # last value 2026-10-12: 8 days early
    report = coverage_report(pd.DataFrame({"SEVEN": seven, "EIGHT": eight}, index=idx))

    assert pd.Timestamp(report.loc["SEVEN", "last_date"]) == pd.Timestamp("2026-10-13")
    assert bool(report.loc["SEVEN", "ends_early"]) is False
    assert bool(report.loc["EIGHT", "ends_early"]) is True
