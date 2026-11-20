import numpy as np
import pandas as pd
import pytest

from haze_salience.data.psi import daily_psi, high_psi, load_psi, unhealthy_streaks


def _readings(rows):
    return pd.DataFrame(rows, columns=["timestamp", "region", "psi_24h"])


def test_daily_psi_takes_max_region_at_hour():
    readings = _readings(
        [
            # 2026-03-01 at 12:00: max over regions is 95 (not the sum or the mean)
            ("2026-03-01 12:00", "north", 80.0),
            ("2026-03-01 12:00", "south", 95.0),
            ("2026-03-01 12:00", "east", 60.0),
            # 13:00 reading is higher but must be ignored at hour=12
            ("2026-03-01 13:00", "east", 200.0),
            # 2026-03-02 at 12:00: max is 110
            ("2026-03-02 12:00", "north", 110.0),
            ("2026-03-02 12:00", "south", 50.0),
            ("2026-03-02 12:00", "east", 101.0),
        ]
    )
    out = daily_psi(readings)
    assert list(out) == [95.0, 110.0]
    assert isinstance(out.index, pd.DatetimeIndex)
    assert list(out.index) == list(pd.to_datetime(["2026-03-01", "2026-03-02"]))
    assert out.name == "psi"


def test_daily_psi_skips_missing_region_values():
    readings = _readings(
        [
            ("2026-03-01 12:00", "north", np.nan),
            ("2026-03-01 12:00", "south", 70.0),
        ]
    )
    assert daily_psi(readings).iloc[0] == 70.0


def test_daily_psi_missing_hour_is_nan():
    readings = _readings(
        [
            ("2026-03-01 12:00", "north", 80.0),
            # 2026-03-02 has readings, but none at 12:00
            ("2026-03-02 09:00", "north", 150.0),
            ("2026-03-02 15:00", "north", 160.0),
        ]
    )
    out = daily_psi(readings)
    assert out.iloc[0] == 80.0
    assert np.isnan(out.iloc[1])


def test_daily_psi_hour_argument_selects_reading_hour():
    readings = _readings(
        [
            ("2026-03-01 12:00", "north", 80.0),
            ("2026-03-01 15:00", "north", 130.0),
        ]
    )
    assert daily_psi(readings, hour=15).iloc[0] == 130.0


def test_daily_psi_fills_calendar_gaps_with_nan():
    readings = _readings(
        [
            ("2026-03-01 12:00", "north", 80.0),
            ("2026-03-04 12:00", "north", 120.0),
        ]
    )
    out = daily_psi(readings)
    assert list(out.index) == list(
        pd.to_datetime(["2026-03-01", "2026-03-02", "2026-03-03", "2026-03-04"])
    )
    assert out.iloc[0] == 80.0
    assert np.isnan(out.iloc[1])
    assert np.isnan(out.iloc[2])
    assert out.iloc[3] == 120.0


def test_load_psi_is_still_a_stub():
    with pytest.raises(NotImplementedError):
        load_psi()


def test_daily_psi_empty_input_gives_empty_series():
    out = daily_psi(_readings([]))
    assert len(out) == 0
    assert out.name == "psi"


def test_daily_psi_rejects_bad_hour():
    with pytest.raises(ValueError):
        daily_psi(_readings([("2026-03-01 12:00", "north", 80.0)]), hour=24)


def test_high_psi_is_strict_and_keeps_na():
    daily = pd.Series(
        [100.0, 101.0, np.nan, 50.0],
        index=pd.date_range("2026-03-01", periods=4, freq="D"),
        name="psi",
    )
    out = high_psi(daily)
    assert out.dtype == "boolean"
    assert out.iloc[0] == False  # noqa: E712 - 100 is not strictly above 100
    assert out.iloc[1] == True  # noqa: E712 - 101 is above 100
    assert out.iloc[2] is pd.NA
    assert out.iloc[3] == False  # noqa: E712
    assert out.isna().sum() == 1


def test_high_psi_threshold_argument():
    daily = pd.Series([40.0, 60.0], index=pd.date_range("2026-03-01", periods=2, freq="D"))
    out = high_psi(daily, threshold=50)
    assert list(out) == [False, True]


def test_streaks():
    # Jan 1-3 True (length 3), Jan 4 False, Jan 5 True (length 1), Jan 6 NA,
    # Jan 7-9 True (length 3)
    high = pd.Series(
        pd.array([True, True, True, False, True, pd.NA, True, True, True], dtype="boolean"),
        index=pd.date_range("2026-01-01", periods=9, freq="D"),
    )
    out = unhealthy_streaks(high)
    assert list(out.columns) == ["start", "end", "length"]
    assert list(out["start"]) == list(pd.to_datetime(["2026-01-01", "2026-01-05", "2026-01-07"]))
    assert list(out["end"]) == list(pd.to_datetime(["2026-01-03", "2026-01-05", "2026-01-09"]))
    assert list(out["length"]) == [3, 1, 3]


def test_streak_broken_by_missing_calendar_day():
    # Jan 2 is absent from the index, so Jan 1 and Jan 3 are not one run
    high = pd.Series(
        pd.array([True, True], dtype="boolean"),
        index=pd.to_datetime(["2026-01-01", "2026-01-03"]),
    )
    out = unhealthy_streaks(high)
    assert list(out["length"]) == [1, 1]


def test_streaks_empty_when_no_true_days():
    high = pd.Series(
        pd.array([False, pd.NA], dtype="boolean"), index=pd.date_range("2026-01-01", periods=2)
    )
    out = unhealthy_streaks(high)
    assert len(out) == 0
    assert list(out.columns) == ["start", "end", "length"]
