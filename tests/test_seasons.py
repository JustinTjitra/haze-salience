import pandas as pd
import pytest

from haze_salience.seasons import all_season_windows, load_seasons, season_of, season_windows

CFG = {
    "years": [2015, 2019],
    "season_window": {"start": "08-01", "end": "11-30"},
    "estimation_window": {"start": "02-01", "end": "06-30"},
}


def test_repo_seasons_load():
    cfg = load_seasons()
    assert cfg["years"] == [2015, 2019, 2023, 2026]
    wins = all_season_windows(cfg)
    assert [w.year for w in wins] == [2015, 2019, 2023, 2026]
    w26 = season_windows(2026, cfg)
    assert w26.season_start == pd.Timestamp("2026-08-01")
    assert w26.season_end == pd.Timestamp("2026-11-30")
    assert w26.est_start == pd.Timestamp("2026-02-01")
    assert w26.est_end == pd.Timestamp("2026-06-30")


def test_season_of():
    assert season_of(pd.Timestamp("2019-09-15"), CFG) == 2019
    assert season_of(pd.Timestamp("2019-07-31"), CFG) is None
    assert season_of(pd.Timestamp("2020-09-15"), CFG) is None
    assert season_of(pd.Timestamp("2019-08-01"), CFG) == 2019
    assert season_of(pd.Timestamp("2019-11-30"), CFG) == 2019
    assert season_of(pd.Timestamp("2019-12-01"), CFG) is None
    # A timestamp late on the final day is still inside the inclusive window.
    assert season_of(pd.Timestamp("2019-11-30 15:00"), CFG) == 2019


def test_overlapping_windows_raise():
    overlapping = {**CFG, "estimation_window": {"start": "02-01", "end": "08-15"}}
    with pytest.raises(ValueError):
        all_season_windows(overlapping)
    with pytest.raises(ValueError):
        season_of(pd.Timestamp("2019-09-15"), overlapping)


def test_years_must_be_unique_and_sorted():
    with pytest.raises(ValueError):
        all_season_windows({**CFG, "years": [2019, 2015]})
    with pytest.raises(ValueError):
        all_season_windows({**CFG, "years": [2015, 2015]})
