"""Market-model event study for any events on any exchanges, each on its own trading calendar."""

import logging
from collections.abc import Sequence
from dataclasses import dataclass

import pandas as pd

from haze_salience.events.market_model import EventStudyError, event_study
from haze_salience.events.returns import build_returns, validate_lags
from haze_salience.universe import exchange_view

log = logging.getLogger(__name__)

LEADING_COLUMNS = ["exchange", "event", "firm", "group"]


@dataclass(frozen=True)
class EventRun:
    summary: pd.DataFrame  # one row per exchange, event and firm that produced a result
    skipped: list[str]  # "<exchange> / <firm> / <event id>: <reason>"


def _check_unique(label: str, values: Sequence[str]) -> None:
    repeated = sorted({v for v in values if list(values).count(v) > 1})
    if repeated:
        raise ValueError(f"{label} must not repeat, got repeated {repeated}")


def run_events(
    prices: pd.DataFrame,
    universe: dict,
    events: dict[str, dict],
    event_ids: Sequence[str],
    exchanges: Sequence[str],
    cfg: dict,
    cpo: pd.Series,
    cpo_lags: Sequence[int] = (0,),
) -> EventRun:
    """One long table of event-study results: one row per exchange, event and firm.

    `prices` are wide closes (one column per ticker, firms and indexes); `universe` is the full
    dict from `load_universe()`. Each exchange is run on its own calendar (the dates where its
    index has a price). Factors are `mkt`, `cpo` if 0 is in `cpo_lags`, and `cpo_lag{k}` for each
    k > 0. A firm/event whose study raises `EventStudyError` goes to `skipped` and has no row.
    """
    lags = validate_lags(cpo_lags)
    _check_unique("event_ids", list(event_ids))
    _check_unique("exchanges", list(exchanges))
    unknown_events = [e for e in event_ids if e not in events]
    if unknown_events:
        raise ValueError(f"unknown event ids {unknown_events}; known events: {sorted(events)}")
    known_exchanges = universe["exchanges"]
    unknown_exchanges = [x for x in exchanges if x not in known_exchanges]
    if unknown_exchanges:
        raise ValueError(
            f"unknown exchanges {unknown_exchanges}; known exchanges: {sorted(known_exchanges)}"
        )

    lag_cols = [f"cpo_lag{k}" for k in lags if k > 0]
    factor_cols = ["mkt", *(["cpo"] if 0 in lags else []), *lag_cols]
    estimation_window = tuple(cfg["estimation_window"])
    event_window = tuple(cfg["event_window"])

    rows: list[dict] = []
    skipped: list[str] = []
    for exchange in exchanges:
        view = exchange_view(universe, exchange)
        rets = build_returns(prices, view, cpo, lags)
        factors = rets[factor_cols]
        for event_id in event_ids:
            ev = events[event_id]
            after_close = bool(ev.get("after_close", False))
            for firm in view["firms"]:
                name = firm["name"]
                try:
                    res = event_study(
                        rets[name],
                        factors,
                        ev["date"],
                        estimation_window,
                        event_window,
                        cfg["min_estimation_days"],
                        after_close,
                    )
                except EventStudyError as e:
                    msg = f"{exchange} / {name} / {event_id}: {e}"
                    log.warning("skipped %s", msg)
                    skipped.append(msg)
                    continue
                betas = {"beta_mkt": res.params["mkt"]}
                if 0 in lags:
                    betas["beta_cpo"] = res.params["cpo"]
                betas.update({f"beta_{col}": res.params[col] for col in lag_cols})
                rows.append(
                    {
                        "exchange": exchange,
                        "event": event_id,
                        "firm": name,
                        "group": firm["group"],
                        **res.summary(),
                        **betas,
                    }
                )
    summary = pd.DataFrame(rows) if rows else pd.DataFrame(columns=LEADING_COLUMNS)
    return EventRun(summary, skipped)
