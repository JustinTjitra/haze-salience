"""Schema checks for config/events.yaml. Every problem is collected and reported at once."""

import datetime as dt
import re

KINDS = {"ngo_report", "salience", "government", "regulatory", "company_response", "price_move"}
REQUIRED = ("id", "date", "kind", "label", "description", "source", "verified")
OPTIONAL = ("after_close", "time_sgt", "firms_named", "confounds", "notes")
TIME_SGT = re.compile(r"([01]\d|2[0-3]):[0-5]\d")


def validate_events(events: list[dict], firm_names: set[str]) -> None:
    problems: list[str] = []
    if not isinstance(events, list):
        problems.append("'events' must be a list")
        events = []

    seen: dict[str, int] = {}
    for i, event in enumerate(events):
        if not isinstance(event, dict):
            problems.append(f"event #{i} is not a mapping")
            continue
        name = _name(event, i)
        _check_keys(event, name, problems)
        _check_id(event, i, seen, problems)
        _check_fields(event, name, firm_names, problems)

    if problems:
        raise ValueError("invalid events: " + "; ".join(problems))


def _name(event: dict, i: int) -> str:
    ev_id = event.get("id")
    if isinstance(ev_id, str) and ev_id:
        return f"event {ev_id!r}"
    return f"event #{i}"


def _check_keys(event: dict, name: str, problems: list[str]) -> None:
    for key in REQUIRED:
        if key not in event:
            problems.append(f"{name} is missing '{key}'")
    for key in event:
        if key not in REQUIRED and key not in OPTIONAL:
            problems.append(f"{name} has unknown key {key!r}")


def _check_id(event: dict, i: int, seen: dict[str, int], problems: list[str]) -> None:
    if "id" not in event:
        return
    ev_id = event["id"]
    if not isinstance(ev_id, str) or not ev_id:
        problems.append(f"event #{i} has id {ev_id!r}; it must be a non-empty string")
    elif ev_id in seen:
        problems.append(f"duplicate id {ev_id!r} (events #{seen[ev_id]} and #{i})")
    else:
        seen[ev_id] = i


def _check_fields(event: dict, name: str, firm_names: set[str], problems: list[str]) -> None:
    if "date" in event:
        value = event["date"]
        # datetime.datetime is a subclass of date, so it is rejected explicitly.
        if isinstance(value, dt.datetime) or not isinstance(value, dt.date):
            problems.append(
                f"{name} has date {value!r}; it must be an unquoted date such as 2026-10-05"
            )
    if "kind" in event:
        value = event["kind"]
        if not isinstance(value, str) or value not in KINDS:
            problems.append(f"{name} has kind {value!r}; it must be one of {sorted(KINDS)}")
    for key in ("label", "description"):
        if key in event and not _nonempty_str(event[key]):
            problems.append(f"{name} has {key} {event[key]!r}; it must be a non-empty string")
    if "source" in event:
        value = event["source"]
        if not isinstance(value, str) or not value.startswith(("http://", "https://")):
            problems.append(f"{name} has source {value!r}; it must start with http:// or https://")
    if "verified" in event and not isinstance(event["verified"], bool):
        problems.append(f"{name} has verified {event['verified']!r}; it must be true or false")
    if "after_close" in event and not isinstance(event["after_close"], bool):
        problems.append(
            f"{name} has after_close {event['after_close']!r}; it must be true or false"
        )
    if "time_sgt" in event:
        value = event["time_sgt"]
        if not isinstance(value, str) or not TIME_SGT.fullmatch(value):
            problems.append(f"{name} has time_sgt {value!r}; it must be HH:MM from 00:00 to 23:59")
    if "firms_named" in event:
        _check_firms_named(event["firms_named"], name, firm_names, problems)
    for key in ("confounds", "notes"):
        if key in event and not isinstance(event[key], str):
            problems.append(f"{name} has {key} {event[key]!r}; it must be a string")


def _check_firms_named(value, name: str, firm_names: set[str], problems: list[str]) -> None:
    if not isinstance(value, list):
        problems.append(f"{name} has firms_named {value!r}; it must be a list")
        return
    for firm in value:
        if not isinstance(firm, str) or firm not in firm_names:
            problems.append(f"{name} names unknown firm {firm!r} in firms_named")


def _nonempty_str(value) -> bool:
    return isinstance(value, str) and bool(value.strip())
