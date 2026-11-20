import numpy as np
import pandas as pd
import pytest

from haze_salience.events.market_model import EventStudyError
from haze_salience.events.volume import abnormal_volume

EST = (-150, -31)
WIN = (-10, 10)


def _lognormal_volume(calendar, seed=42, sd=0.3):
    rng = np.random.default_rng(seed)
    return pd.Series(np.exp(rng.normal(np.log(1e6), sd, len(calendar))), index=calendar)


def test_known_answer_z_scores():
    """Estimation logs 1, 2, 3 have mean 2 and SD 1; day-0 log 4 gives z = 2."""
    calendar = pd.bdate_range("2026-01-05", periods=10)
    volume = pd.Series(np.exp([0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 2.0, 0.0, 0.0, 0.0]), index=calendar)
    z = abnormal_volume(volume, calendar[5], (-3, -1), (0, 1), min_estimation_days=3)
    assert list(z.index) == [0, 1]
    assert z.loc[0] == pytest.approx(2.0)
    assert z.loc[1] == pytest.approx(0.0)


def test_after_close_shifts_day0_by_one_day():
    """Same estimation logs as the known-answer test; an event on 4 Jan after the close has day 0
    on 5 Jan, so z at day 0 is the 5 Jan log (4.0) against estimation logs 1, 2, 3."""
    calendar = pd.bdate_range("2026-01-05", periods=10)
    volume = pd.Series(np.exp([0.0, 0.0, 1.0, 2.0, 3.0, 4.0, 2.0, 0.0, 0.0, 0.0]), index=calendar)
    z = abnormal_volume(
        volume, calendar[4], (-3, -1), (0, 1), min_estimation_days=3, after_close=True
    )
    assert z.loc[0] == pytest.approx(2.0)
    assert z.loc[1] == pytest.approx(0.0)


def test_spike_is_detected(calendar):
    volume = _lognormal_volume(calendar)
    day0 = pd.Timestamp("2026-10-16")
    volume.loc[day0] *= 5

    z = abnormal_volume(volume, day0, EST, WIN, min_estimation_days=100)

    assert z.loc[0] == pytest.approx(np.log(5) / 0.3, abs=3.0)
    assert z.loc[0] > z.drop(0).max()


def test_offsets_and_index_name(calendar):
    volume = _lognormal_volume(calendar)
    z = abnormal_volume(volume, "2026-10-16", EST, WIN, min_estimation_days=100)
    assert z.index.name == "offset"
    assert isinstance(z.index, pd.RangeIndex)
    assert list(z.index) == list(range(WIN[0], WIN[1] + 1))


def test_offsets_outside_data_are_nan():
    calendar = pd.bdate_range("2026-01-05", periods=10)
    volume = pd.Series(np.exp(np.arange(10) * 0.1), index=calendar)
    # Day 0 is position 6 of 10, so offset 4 (position 10) falls past the end of the data.
    z = abnormal_volume(volume, calendar[6], (-6, -2), (-1, 4), min_estimation_days=5)
    assert list(z.index) == list(range(-1, 5))
    assert z.loc[-1:3].notna().all()
    assert z.loc[4:].isna().all()


def test_zero_volume_is_nan(calendar):
    volume = _lognormal_volume(calendar)
    day0 = pd.Timestamp("2026-10-16")
    volume.loc[calendar[calendar.get_loc(day0) + 3]] = 0.0

    z = abnormal_volume(volume, day0, EST, WIN, min_estimation_days=100)

    assert np.isnan(z.loc[3])
    assert z.drop(3).notna().all()


def test_too_few_estimation_days_raises():
    calendar = pd.bdate_range("2026-01-05", periods=10)
    volume = pd.Series(np.exp(np.arange(10) * 0.1), index=calendar)
    volume.iloc[2:4] = 0.0  # two of the three estimation days are now missing
    with pytest.raises(EventStudyError):
        abnormal_volume(volume, calendar[5], (-3, -1), (0, 1), min_estimation_days=3)


def test_window_before_data_raises(calendar):
    volume = _lognormal_volume(calendar)
    with pytest.raises(EventStudyError):
        abnormal_volume(volume, calendar[10], EST, WIN, min_estimation_days=100)
