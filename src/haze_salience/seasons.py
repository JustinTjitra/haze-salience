"""Haze seasons: the years and month-day windows defined in config/seasons.yaml."""

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from haze_salience import ROOT
from haze_salience.config import load_yaml


@dataclass(frozen=True)
class SeasonWindows:
    year: int
    season_start: pd.Timestamp
    season_end: pd.Timestamp
    est_start: pd.Timestamp
    est_end: pd.Timestamp


def load_seasons(root: Path = ROOT) -> dict:
    cfg = load_yaml("seasons.yaml", root)
    _validate(cfg)
    return cfg


def _window(year: int, win: dict) -> tuple[pd.Timestamp, pd.Timestamp]:
    """Inclusive same-year window from a month-day pair such as {start: "08-01", end: "11-30"}."""
    start = _month_day(year, win["start"])
    end = _month_day(year, win["end"])
    if end < start:
        raise ValueError(f"window {win} ends before it starts in {year}")
    return start, end


def _month_day(year: int, value: str) -> pd.Timestamp:
    month, day = (int(part) for part in str(value).split("-"))
    return pd.Timestamp(year=year, month=month, day=day)


def _validate(cfg: dict) -> None:
    years = list(cfg["years"])
    if years != sorted(set(years)):
        raise ValueError(f"years must be unique and sorted ascending, got {years}")
    for year in years:
        est_start, est_end = _window(year, cfg["estimation_window"])
        season_start, _ = _window(year, cfg["season_window"])
        if not est_end < season_start:
            raise ValueError(
                f"estimation window ends {est_end.date()} but season window starts "
                f"{season_start.date()} in {year}; estimation must end before the season"
            )


def season_windows(year: int, cfg: dict) -> SeasonWindows:
    _validate(cfg)
    if year not in cfg["years"]:
        raise ValueError(f"{year} is not a season year in {list(cfg['years'])}")
    est_start, est_end = _window(year, cfg["estimation_window"])
    season_start, season_end = _window(year, cfg["season_window"])
    return SeasonWindows(
        year=year,
        season_start=season_start,
        season_end=season_end,
        est_start=est_start,
        est_end=est_end,
    )


def all_season_windows(cfg: dict) -> list[SeasonWindows]:
    _validate(cfg)
    return [season_windows(year, cfg) for year in cfg["years"]]


def season_of(date, cfg: dict) -> int | None:
    """The season year whose season window contains date (inclusive), or None."""
    day = pd.Timestamp(date).normalize()
    for win in all_season_windows(cfg):
        if win.season_start <= day <= win.season_end:
            return win.year
    return None
