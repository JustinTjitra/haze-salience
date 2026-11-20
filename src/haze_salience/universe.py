"""Exchanges, their index and their firms, as defined in config/universe.yaml."""

from pathlib import Path

from haze_salience import ROOT
from haze_salience.config import load_yaml

FIRM_FIELDS = ("name", "ticker", "exchange", "group")


def load_universe(root: Path = ROOT) -> dict:
    universe = load_yaml("universe.yaml", root)
    _validate(universe)
    return universe


def firms_on(universe: dict, exchange: str) -> list[dict]:
    _known_exchange(universe, exchange)
    return [f for f in universe["firms"] if f["exchange"] == exchange]


def index_ticker(universe: dict, exchange: str) -> str:
    _known_exchange(universe, exchange)
    return universe["exchanges"][exchange]["index_ticker"]


def exchange_view(universe: dict, exchange: str) -> dict:
    """One exchange in the shape run_pilot and plot_pilot expect."""
    return {
        "market_index": {"ticker": index_ticker(universe, exchange)},
        "firms": firms_on(universe, exchange),
    }


def _known_exchange(universe: dict, exchange: str) -> None:
    if exchange not in universe["exchanges"]:
        known = sorted(universe["exchanges"])
        raise ValueError(f"unknown exchange {exchange!r}; known exchanges: {known}")


def _validate(universe: dict) -> None:
    problems: list[str] = []
    exchanges = universe.get("exchanges")
    if not isinstance(exchanges, dict) or not exchanges:
        problems.append("'exchanges' must be a non-empty mapping")
        exchanges = {}
    for code, spec in exchanges.items():
        if not isinstance(spec, dict) or not spec.get("index_ticker"):
            problems.append(f"exchange {code!r} has no index_ticker")

    firms = universe.get("firms")
    if not isinstance(firms, list) or not firms:
        problems.append("'firms' must be a non-empty list")
        firms = []
    names: dict[str, int] = {}
    tickers: dict[str, int] = {}
    for i, firm in enumerate(firms):
        if not isinstance(firm, dict):
            problems.append(f"firm #{i} is not a mapping")
            continue
        label = f"firm {firm['name']!r}" if firm.get("name") else f"firm #{i}"
        for field in FIRM_FIELDS:
            if not firm.get(field):
                problems.append(f"{label} is missing '{field}'")
        if firm.get("exchange") and exchanges and firm["exchange"] not in exchanges:
            problems.append(f"{label} has unknown exchange {firm['exchange']!r}")
        if firm.get("name"):
            if firm["name"] in names:
                problems.append(
                    f"duplicate name {firm['name']!r} (firms #{names[firm['name']]} and #{i})"
                )
            names.setdefault(firm["name"], i)
        if firm.get("ticker"):
            if firm["ticker"] in tickers:
                problems.append(
                    f"duplicate ticker {firm['ticker']!r} (firms #{tickers[firm['ticker']]} "
                    f"and #{i})"
                )
            tickers.setdefault(firm["ticker"], i)

    if problems:
        raise ValueError("invalid universe: " + "; ".join(problems))
