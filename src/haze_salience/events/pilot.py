"""Stage 1 pilot: CARs for the SGX names around each pilot event."""

import logging
from collections.abc import Callable
from dataclasses import dataclass, field

import pandas as pd

from haze_salience.data.align import align_to_calendar, simple_returns
from haze_salience.events.market_model import (
    EventResult,
    EventStudyError,
    event_study,
    locate_day0,
)
from haze_salience.events.portfolio import long_short_return, portfolio_return

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


def run_pilot(
    prices: pd.DataFrame,
    universe: dict,
    pilot_cfg: dict,
    events: dict[str, dict],
    load_cpo: Callable[[], tuple[pd.Series, str]],
) -> PilotOutput:
    """`prices` are wide closes (one column per ticker); `load_cpo` returns (series, label)."""
    index_ticker = universe["market_index"]["ticker"]
    calendar = prices[index_ticker].dropna().index  # SGX trading days

    cpo, control_label = load_cpo()
    levels = pd.DataFrame(
        {f["name"]: prices[f["ticker"]].reindex(calendar) for f in universe["firms"]}
    )
    levels["mkt"] = prices[index_ticker].reindex(calendar)
    levels["cpo"] = align_to_calendar(calendar, cpo)
    rets = simple_returns(levels)
    factors = rets[["mkt", "cpo"]]

    results: dict[str, dict[str, EventResult]] = {}
    portfolios: dict[str, dict[str, EventResult]] = {}
    rows, skipped = [], []
    named_flag = {f["name"]: f.get("greenpeace_named_2026", False) for f in universe["firms"]}
    window = tuple(pilot_cfg["estimation_window"])
    event_window = tuple(pilot_cfg["event_window"])
    day0_positions = {e: locate_day0(rets.index, events[e]["date"]) for e in pilot_cfg["events"]}
    for event_id in pilot_cfg["events"]:
        ev = events[event_id]
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
                )
            except EventStudyError as e:
                msg = f"{name} / {event_id}: {e}"
                log.warning("skipped %s", msg)
                skipped.append(msg)
                continue
            results[event_id][name] = res
            rows.append(
                {
                    "event": event_id,
                    "kind": "firm",
                    "firm": name,
                    "greenpeace_named": firm.get("greenpeace_named_2026", False),
                    **res.summary(),
                    "beta_mkt": res.params["mkt"],
                    "beta_cpo": res.params["cpo"],
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
                    "beta_cpo": res.params["cpo"],
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
