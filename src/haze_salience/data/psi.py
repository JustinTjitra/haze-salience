"""Stage 2: Singapore NEA 24-hour PSI history (data.gov.sg), the salience measure for H2.

Not implemented until the Stage 1 pilot passes the 29 Nov go/no-go. First check how far back
the archive goes; the 2015 season is needed.

This module turns regional PSI readings into the daily salience measure, the high-PSI flag and
unhealthy streaks. `read_psi_bulk_csv` reads the data.gov.sg "Historical 24-hr PSI" CSV into the
long table that `daily_psi` takes. The archive reader `load_psi` is a later task and still raises.
"""

import pandas as pd

REGIONS = ("north", "south", "east", "west", "central")
_BULK_TIMESTAMP_COLUMN = "24hr_psi"
_BULK_TIMESTAMP_FORMAT = "%d/%m/%Y %H:%M"


def load_psi(*args, **kwargs):
    raise NotImplementedError("Stage 2: implement after the pilot go/no-go.")


def daily_psi(readings: pd.DataFrame, hour: int = 12) -> pd.Series:
    """Maximum 24-hour PSI across regions at one reading hour, one value per calendar day.

    `readings` has columns `timestamp` (tz-naive Singapore time), `region` and `psi_24h`. Only
    readings whose timestamp hour equals `hour` are used; the day's value is the maximum
    `psi_24h` over regions (missing values are skipped). The index runs over every calendar day
    from the first to the last date in `readings`, and a day with no reading at that hour is NaN.
    """
    if not 0 <= hour <= 23:
        raise ValueError(f"hour must be in 0..23, got {hour}")
    if readings.empty:
        return pd.Series(dtype=float, index=pd.DatetimeIndex([]), name="psi")

    ts = pd.to_datetime(readings["timestamp"]).reset_index(drop=True)
    values = readings["psi_24h"].astype(float).reset_index(drop=True)
    dates = ts.dt.normalize()
    at_hour = ts.dt.hour == hour

    peak = values[at_hour].groupby(dates[at_hour]).max()
    calendar = pd.date_range(dates.min(), dates.max(), freq="D")
    return peak.reindex(calendar).rename("psi")


def high_psi(daily: pd.Series, threshold: float = 100) -> pd.Series:
    """Flag days whose PSI is strictly above `threshold`.

    Returns a pandas nullable boolean series: True where `daily > threshold`, False otherwise,
    and <NA> where `daily` is NaN.
    """
    flags = (daily > threshold).astype("boolean")
    return flags.mask(daily.isna())


def unhealthy_streaks(high: pd.Series) -> pd.DataFrame:
    """Maximal runs of consecutive True days in a flag series from `high_psi`.

    Returns columns `start`, `end` and `length` (calendar days, inclusive), one row per run.
    A run is broken by a False, by <NA>, or by a missing calendar day in the index.
    """
    idx = pd.DatetimeIndex(high.index)
    flags = high.fillna(False).astype(bool).to_numpy()

    runs: list[tuple[pd.Timestamp, pd.Timestamp]] = []
    start = prev = None
    one_day = pd.Timedelta(days=1)
    for ts, flag in zip(idx, flags, strict=True):
        if flag and start is not None and ts - prev == one_day:
            prev = ts
            continue
        if start is not None:
            runs.append((start, prev))
            start = prev = None
        if flag:
            start = prev = ts
    if start is not None:
        runs.append((start, prev))

    out = pd.DataFrame(runs, columns=["start", "end"])
    out["start"] = pd.to_datetime(out["start"])
    out["end"] = pd.to_datetime(out["end"])
    out["length"] = ((out["end"] - out["start"]).dt.days + 1).astype("int64")
    return out


def read_psi_bulk_csv(path) -> pd.DataFrame:
    """Read the data.gov.sg "Historical 24-hr PSI" CSV into a long table of regional readings.

    The file has a `24hr_psi` column of day-first timestamps (for example `25/9/2015 0:00`) and
    one text column per region in `REGIONS`; an `_id` column is ignored. The output has columns
    `timestamp` (tz-naive, parsed with the explicit format `%d/%m/%Y %H:%M`), `region` and
    `psi_24h` (float), one row per timestamp and region, sorted by timestamp then by the order of
    `REGIONS`. Empty or non-numeric region cells become NaN. Timestamps are kept as written: no
    shift of the 0:00 reading and no timezone is applied.

    Raises ValueError if a column is missing, a timestamp does not match the format, or a
    timestamp appears more than once.
    """
    wide = pd.read_csv(path, dtype=str, keep_default_na=False)

    if _BULK_TIMESTAMP_COLUMN not in wide.columns:
        raise ValueError(f"PSI bulk CSV is missing the timestamp column {_BULK_TIMESTAMP_COLUMN!r}")
    missing = [region for region in REGIONS if region not in wide.columns]
    if missing:
        raise ValueError(f"PSI bulk CSV is missing region column(s): {', '.join(missing)}")

    raw = wide[_BULK_TIMESTAMP_COLUMN]
    stamps = pd.to_datetime(raw, format=_BULK_TIMESTAMP_FORMAT, errors="coerce")
    bad = stamps.isna()
    if bad.any():
        row = int(bad.idxmax())
        raise ValueError(
            f"PSI bulk CSV row {row + 1}: timestamp {raw.iloc[row]!r} does not match "
            f"the format {_BULK_TIMESTAMP_FORMAT!r} (day first, for example '25/9/2015 0:00')"
        )
    duplicated = stamps.duplicated(keep="first")
    if duplicated.any():
        dup = stamps[duplicated].iloc[0]
        raise ValueError(f"PSI bulk CSV has the timestamp {dup} more than once")

    parts = []
    for rank, region in enumerate(REGIONS):
        parts.append(
            pd.DataFrame(
                {
                    "timestamp": stamps.to_numpy(),
                    "region": region,
                    "psi_24h": pd.to_numeric(wide[region], errors="coerce")
                    .astype(float)
                    .to_numpy(),
                    "_rank": rank,
                }
            )
        )
    long = pd.concat(parts, ignore_index=True)
    long = long.sort_values(["timestamp", "_rank"], kind="stable")
    long = long.drop(columns="_rank").reset_index(drop=True)
    long["timestamp"] = long["timestamp"].astype("datetime64[ns]")
    return long
