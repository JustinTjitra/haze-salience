import pandas as pd
import pytest
import yfinance

from haze_salience.data.prices import (
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
