import numpy as np
import pandas as pd
import pytest

from haze_salience.data.psi import (
    daily_psi,
    high_psi,
    load_psi,
    read_psi_bulk_csv,
    unhealthy_streaks,
)


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


BULK_HEADER = "_id,24hr_psi,north,south,east,west,central\n"


def _write_bulk(tmp_path, text, name="psi_bulk.csv"):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


def test_read_psi_bulk_csv_long_shape(tmp_path):
    path = _write_bulk(
        tmp_path,
        BULK_HEADER + "1,25/9/2015 0:00,50,60,55,70,65\n" + "2,1/4/2014 13:00,101,80,90,120,110\n",
    )
    out = read_psi_bulk_csv(path)
    assert len(out) == 10
    assert list(out.columns) == ["timestamp", "region", "psi_24h"]
    assert pd.api.types.is_datetime64_dtype(out["timestamp"])
    assert out["timestamp"].dt.tz is None
    assert pd.api.types.is_float_dtype(out["psi_24h"])
    assert out.index.equals(pd.RangeIndex(10))
    # Sorted by timestamp, then by REGIONS order: the 2014 timestamp comes first
    early = out.iloc[:5]
    assert set(early["timestamp"]) == {pd.Timestamp("2014-04-01 13:00")}
    assert list(early["region"]) == ["north", "south", "east", "west", "central"]
    assert list(early["psi_24h"]) == [101.0, 80.0, 90.0, 120.0, 110.0]
    late = out.iloc[5:]
    assert set(late["timestamp"]) == {pd.Timestamp("2015-09-25 00:00")}
    assert list(late["psi_24h"]) == [50.0, 60.0, 55.0, 70.0, 65.0]


def test_read_psi_bulk_csv_is_day_first(tmp_path):
    path = _write_bulk(
        tmp_path,
        BULK_HEADER + "1,25/9/2015 0:00,1,1,1,1,1\n" + "2,1/4/2014 1:00,2,2,2,2,2\n",
    )
    stamps = read_psi_bulk_csv(path).drop_duplicates("timestamp")["timestamp"]
    assert list(stamps) == [
        pd.Timestamp("2014-04-01 01:00"),
        pd.Timestamp("2015-09-25 00:00"),
    ]


def test_read_psi_bulk_csv_ignores_id_and_column_order(tmp_path):
    reference = read_psi_bulk_csv(
        _write_bulk(tmp_path, BULK_HEADER + "1,25/9/2015 0:00,50,60,55,70,65\n", "ref.csv")
    )
    no_id = read_psi_bulk_csv(
        _write_bulk(
            tmp_path,
            "24hr_psi,north,south,east,west,central\n25/9/2015 0:00,50,60,55,70,65\n",
            "no_id.csv",
        )
    )
    shuffled = read_psi_bulk_csv(
        _write_bulk(
            tmp_path,
            "central,west,_id,east,24hr_psi,south,north\n65,70,7,55,25/9/2015 0:00,60,50\n",
            "shuffled.csv",
        )
    )
    pd.testing.assert_frame_equal(no_id, reference)
    pd.testing.assert_frame_equal(shuffled, reference)
    assert shuffled.loc[shuffled["region"] == "north", "psi_24h"].item() == 50.0


def test_read_psi_bulk_csv_non_numeric_is_nan(tmp_path):
    path = _write_bulk(
        tmp_path,
        BULK_HEADER + "1,25/9/2015 0:00,,-,55,70,65\n",
    )
    out = read_psi_bulk_csv(path).set_index("region")["psi_24h"]
    assert np.isnan(out["north"])
    assert np.isnan(out["south"])
    assert out["east"] == 55.0
    assert out["west"] == 70.0
    assert out["central"] == 65.0
    assert len(out) == 5


def test_read_psi_bulk_csv_errors(tmp_path):
    no_region = _write_bulk(
        tmp_path,
        "_id,24hr_psi,north,south,east,west\n1,25/9/2015 0:00,50,60,55,70\n",
        "no_region.csv",
    )
    with pytest.raises(ValueError, match="central"):
        read_psi_bulk_csv(no_region)

    no_timestamp = _write_bulk(
        tmp_path,
        "_id,north,south,east,west,central\n1,50,60,55,70,65\n",
        "no_timestamp.csv",
    )
    with pytest.raises(ValueError, match="24hr_psi"):
        read_psi_bulk_csv(no_timestamp)

    other_format = _write_bulk(
        tmp_path,
        BULK_HEADER + "1,2015-09-25 00:00,50,60,55,70,65\n",
        "other_format.csv",
    )
    with pytest.raises(ValueError, match="does not match"):
        read_psi_bulk_csv(other_format)

    duplicated = _write_bulk(
        tmp_path,
        BULK_HEADER + "1,25/9/2015 0:00,50,60,55,70,65\n2,25/9/2015 0:00,51,61,56,71,66\n",
        "duplicated.csv",
    )
    with pytest.raises(ValueError, match="more than once"):
        read_psi_bulk_csv(duplicated)


def test_read_psi_bulk_csv_feeds_daily_psi(tmp_path):
    # Day 1 (25 Sep 2015) at 12:00: max is 150 (south). The 0:00 reading (999) and the
    # 13:00 reading (300) must be ignored at hour=12.
    # Day 2 (26 Sep 2015) at 12:00: max is 120 (north).
    path = _write_bulk(
        tmp_path,
        BULK_HEADER
        + "1,25/9/2015 0:00,999,10,10,10,10\n"
        + "2,25/9/2015 12:00,60,150,80,40,90\n"
        + "3,25/9/2015 13:00,300,20,20,20,20\n"
        + "4,26/9/2015 12:00,120,30,40,50,60\n"
        + "5,26/9/2015 0:00,500,10,10,10,10\n",
    )
    out = daily_psi(read_psi_bulk_csv(path), hour=12)
    assert list(out.index) == list(pd.to_datetime(["2015-09-25", "2015-09-26"]))
    assert list(out) == [150.0, 120.0]
