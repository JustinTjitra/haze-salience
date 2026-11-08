import pandas as pd

from haze_salience.data.align import align_to_calendar, simple_returns


def test_forward_fill_holiday_gives_zero_then_catch_up():
    cal = pd.to_datetime(["2026-10-12", "2026-10-13", "2026-10-14"])
    # Control market closed on the 13th
    s = pd.Series([100.0, 110.0], index=pd.to_datetime(["2026-10-12", "2026-10-14"]))
    r = simple_returns(align_to_calendar(cal, s).to_frame("x"))["x"]
    assert r.loc["2026-10-13"] == 0.0
    assert r.loc["2026-10-14"] == 0.10 or abs(r.loc["2026-10-14"] - 0.10) < 1e-12


def test_dates_off_calendar_are_dropped():
    cal = pd.to_datetime(["2026-10-12", "2026-10-14"])
    s = pd.Series([1.0, 2.0, 3.0], index=pd.to_datetime(["2026-10-12", "2026-10-13", "2026-10-14"]))
    out = align_to_calendar(cal, s)
    assert list(out.index) == list(cal)
    assert list(out) == [1.0, 3.0]
