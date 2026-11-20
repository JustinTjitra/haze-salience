"""Stage 1 pilot: CARs for the SGX names around each pilot event."""

import logging
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from haze_salience.data.align import align_to_calendar, simple_returns
from haze_salience.events.market_model import (
    EventResult,
    EventStudyError,
    event_study,
    locate_day0,
)
from haze_salience.events.portfolio import long_short_return, portfolio_return
from haze_salience.events.volume import abnormal_volume

log = logging.getLogger(__name__)


@dataclass
class PilotOutput:
    results: dict[str, dict[str, EventResult]]  # event id -> firm name -> result
    summary: pd.DataFrame
    control_label: str
    skipped: list[str]
    day0_positions: dict[str, int]  # event id -> position of day 0 on the SGX calendar
    event_window: tuple[int, int]
    portfolios: dict[str, dict[str, EventResult]] = field(default_factory=dict)
    # event id -> portfolio name -> result


def _cpo_betas(res: EventResult, lags: list[int], lag_cols: dict[int, str]) -> dict[str, float]:
    out = {"beta_cpo": res.params["cpo"]} if 0 in lags else {}
    out.update({f"beta_{col}": res.params[col] for col in lag_cols.values()})
    return out


def _abvol_cols(
    volumes: pd.DataFrame,
    ticker: str,
    calendar: pd.DatetimeIndex,
    event_date: str,
    window: tuple[int, int],
    event_window: tuple[int, int],
    min_estimation_days: int,
    after_close: bool = False,
) -> dict[str, float]:
    """`abvol_day0` (z at offset 0) and `abvol_0_1` (mean of z at offsets 0 and 1).

    NaN when the ticker is missing from `volumes` or the abnormal-volume study cannot be run.
    """
    nan = {"abvol_day0": np.nan, "abvol_0_1": np.nan}
    if ticker not in volumes.columns:
        return nan
    try:
        z = abnormal_volume(
            volumes[ticker].reindex(calendar),
            event_date,
            window,
            event_window,
            min_estimation_days,
            after_close,
        )
    except EventStudyError:
        return nan
    return {"abvol_day0": float(z.loc[0]), "abvol_0_1": float(z.loc[[0, 1]].mean())}


def run_pilot(
    prices: pd.DataFrame,
    universe: dict,
    pilot_cfg: dict,
    events: dict[str, dict],
    load_cpo: Callable[[], tuple[pd.Series, str]],
    cpo_lags: Sequence[int] = (0,),
    volumes: pd.DataFrame | None = None,
) -> PilotOutput:
    """`prices` are wide closes (one column per ticker); `load_cpo` returns (series, label).

    `cpo_lags` lists the lags of the control's return used as factors: 0 is `cpo`, k > 0 is
    `cpo_lag{k}`, the control's return k SGX days earlier.

    `volumes` are optional wide daily volumes (one column per ticker). When given, each firm row
    gets `abvol_day0` and `abvol_0_1` and portfolio rows get NaN in both; when None the columns
    are absent.
    """
    lags = list(cpo_lags)
    if any(k < 0 for k in lags):
        raise ValueError(f"cpo_lags must be non-negative, got {lags}")
    if len(set(lags)) != len(lags):
        raise ValueError(f"cpo_lags must not contain duplicates, got {lags}")
    index_ticker = universe["market_index"]["ticker"]
    calendar = prices[index_ticker].dropna().index  # SGX trading days

    cpo, control_label = load_cpo()
    extra_lags = [k for k in lags if k > 0]
    if extra_lags:
        control_label += " + lags " + ", ".join(str(k) for k in extra_lags)
    levels = pd.DataFrame(
        {f["name"]: prices[f["ticker"]].reindex(calendar) for f in universe["firms"]}
    )
    levels["mkt"] = prices[index_ticker].reindex(calendar)
    levels["cpo"] = align_to_calendar(calendar, cpo)
    rets = simple_returns(levels)
    factors = rets[["mkt", "cpo"]].copy()
    lag_cols = {k: f"cpo_lag{k}" for k in extra_lags}
    for k, col in lag_cols.items():
        factors[col] = rets["cpo"].shift(k)
    if 0 not in lags:
        factors = factors.drop(columns="cpo")

    results: dict[str, dict[str, EventResult]] = {}
    portfolios: dict[str, dict[str, EventResult]] = {}
    rows, skipped = [], []
    named_flag = {f["name"]: f.get("greenpeace_named_2026", False) for f in universe["firms"]}
    window = tuple(pilot_cfg["estimation_window"])
    event_window = tuple(pilot_cfg["event_window"])
    day0_positions = {
        e: locate_day0(rets.index, events[e]["date"], bool(events[e].get("after_close", False)))
        for e in pilot_cfg["events"]
    }
    for event_id in pilot_cfg["events"]:
        ev = events[event_id]
        after_close = bool(ev.get("after_close", False))
        results[event_id] = {}
        for firm in universe["firms"]:
            name = firm["name"]
            try:
                res = event_study(
                    rets[name],
                    factors,
                    ev["date"],
                    tuple(pilot_cfg["estimation_window"]),
                    tuple(pilot_cfg["event_window"]),
                    pilot_cfg["min_estimation_days"],
                    after_close,
                )
            except EventStudyError as e:
                msg = f"{name} / {event_id}: {e}"
                log.warning("skipped %s", msg)
                skipped.append(msg)
                continue
            results[event_id][name] = res
            abvol = (
                {}
                if volumes is None
                else _abvol_cols(
                    volumes,
                    firm["ticker"],
                    calendar,
                    ev["date"],
                    window,
                    event_window,
                    pilot_cfg["min_estimation_days"],
                    after_close,
                )
            )
            rows.append(
                {
                    "event": event_id,
                    "kind": "firm",
                    "firm": name,
                    "greenpeace_named": firm.get("greenpeace_named_2026", False),
                    **res.summary(),
                    "beta_mkt": res.params["mkt"],
                    **_cpo_betas(res, lags, lag_cols),
                    **abvol,
                }
            )

        # Portfolios: members are the firms that produced a result for this event
        members = list(results[event_id])
        named = [m for m in members if named_flag[m]]
        not_named = [m for m in members if not named_flag[m]]
        # (name, long members, short members or None, n_members, buildable)
        specs: list[tuple[str, list[str], list[str] | None, int, bool]] = [
            ("All firms", members, None, len(members), len(members) >= 2),
            ("Named", named, None, len(named), len(named) >= 1),
            ("Not named", not_named, None, len(not_named), len(not_named) >= 1),
            (
                "Named minus not named",
                named,
                not_named,
                len(members),
                len(named) >= 1 and len(not_named) >= 1,
            ),
        ]
        portfolios[event_id] = {}
        for pname, longs, shorts, n_members, buildable in specs:
            if not buildable:
                msg = f"{pname} / {event_id}: cannot be built from {len(members)} firm(s)"
                log.warning("skipped %s", msg)
                skipped.append(msg)
                continue
            try:
                if shorts is None:
                    series = portfolio_return(rets, longs, pname)
                else:
                    series = long_short_return(rets, longs, shorts, pname)
                res = event_study(
                    series,
                    factors,
                    ev["date"],
                    window,
                    event_window,
                    pilot_cfg["min_estimation_days"],
                    after_close,
                )
            except EventStudyError as e:
                msg = f"{pname} / {event_id}: {e}"
                log.warning("skipped %s", msg)
                skipped.append(msg)
                continue
            portfolios[event_id][pname] = res
            rows.append(
                {
                    "event": event_id,
                    "kind": "portfolio",
                    "firm": pname,
                    "greenpeace_named": None,
                    "n_members": n_members,
                    **res.summary(),
                    "beta_mkt": res.params["mkt"],
                    **_cpo_betas(res, lags, lag_cols),
                    **({} if volumes is None else {"abvol_day0": np.nan, "abvol_0_1": np.nan}),
                }
            )
    return PilotOutput(
        results,
        pd.DataFrame(rows),
        control_label,
        skipped,
        day0_positions,
        tuple(pilot_cfg["event_window"]),
        portfolios,
    )
