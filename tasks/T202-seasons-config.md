# T202 Seasons configuration

Tier: haiku · Depends: none

## Goal
One place defines the haze seasons and their windows.

## Files
- `config/seasons.yaml` (new)
- `src/haze_salience/seasons.py` (new)
- `tests/test_seasons.py` (new)

## Spec
`config/seasons.yaml`:
```yaml
# Defaults from the draft pre-registration; not frozen until prereg-v1.
years: [2015, 2019, 2023, 2026]
season_window: {start: "08-01", end: "11-30"}        # month-day, inclusive
estimation_window: {start: "02-01", end: "06-30"}    # same year, inclusive
```
`src/haze_salience/seasons.py`:
```python
@dataclass(frozen=True)
class SeasonWindows:
    year: int
    season_start: pd.Timestamp
    season_end: pd.Timestamp
    est_start: pd.Timestamp
    est_end: pd.Timestamp

def load_seasons(root=ROOT) -> dict
def season_windows(year: int, cfg: dict) -> SeasonWindows
def all_season_windows(cfg: dict) -> list[SeasonWindows]
def season_of(date, cfg: dict) -> int | None     # the season year whose window contains date
```
Validation (`ValueError`): the estimation window must end before the season window starts; years
unique and sorted.

## Acceptance tests
- `test_repo_seasons_load`: four years; 2026 windows are 2026-08-01..2026-11-30 and
  2026-02-01..2026-06-30.
- `test_season_of`: 2019-09-15 → 2019; 2019-07-31 → None; 2020-09-15 → None; boundaries inclusive.
- `test_overlapping_windows_raise`.

## Out of scope
Trading calendars, data-defined season windows.
