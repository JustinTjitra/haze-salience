"""Stage 1 pilot: CARs for the SGX names around each pilot event."""

import logging
from collections.abc import Callable
from dataclasses import dataclass

import pandas as pd

from haze_salience.data.align import align_to_calendar, simple_returns
from haze_salience.events.market_model import (
    EventResult,
    EventStudyError,
    event_study,
    locate_day0,
)

log = logging.getLogger(__name__)


@dataclass
class PilotOutput:
    results: dict[str, dict[str, EventResult]]  # event id -> firm name -> result
    summary: pd.DataFrame
    control_label: str
    skipped: list[str]
    day0_positions: dict[str, int]  # event id -> position of day 0 on the SGX calendar
    event_window: tuple[int, int]


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
    rows, skipped = [], []
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
                    "firm": name,
                    "greenpeace_named": firm.get("greenpeace_named_2026", False),
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
    )
