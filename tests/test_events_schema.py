import datetime as dt

import pytest
import yaml

from haze_salience.config import load_events
from haze_salience.events_schema import KINDS, validate_events

FIRMS = {"First Resources", "Bumitama Agri"}


def _event(**overrides):
    event = {
        "id": "test_event",
        "date": dt.date(2026, 10, 5),
        "kind": "ngo_report",
        "label": "Test report",
        "description": "A test event.",
        "source": "https://example.org/report",
        "verified": False,
    }
    event.update(overrides)
    return event


def _without(key):
    event = _event()
    del event[key]
    return event


def _problems(events, firms=FIRMS):
    with pytest.raises(ValueError) as info:
        validate_events(events, firms)
    return str(info.value)


def test_valid_events_pass():
    full = _event(
        id="full",
        after_close=True,
        time_sgt="23:59",
        firms_named=["First Resources", "Bumitama Agri"],
        confounds="Same week as a PSI streak.",
        notes="Check the date.",
    )
    validate_events([_event(), full, _event(id="midnight", time_sgt="00:00")], FIRMS)


@pytest.mark.parametrize("kind", sorted(KINDS))
def test_every_kind_is_accepted(kind):
    validate_events([_event(kind=kind)], FIRMS)


@pytest.mark.parametrize(
    "key", ["id", "date", "kind", "label", "description", "source", "verified"]
)
def test_missing_required_key(key):
    assert f"missing '{key}'" in _problems([_without(key)])


def test_duplicate_id():
    msg = _problems([_event(id="same"), _event(id="same")])
    assert "duplicate id 'same'" in msg


@pytest.mark.parametrize("bad_id", ["", 7, None])
def test_id_must_be_non_empty_string(bad_id):
    assert "must be a non-empty string" in _problems([_event(id=bad_id)])


def test_bad_kind():
    assert "has kind 'rumour'" in _problems([_event(kind="rumour")])


@pytest.mark.parametrize("kind", [["ngo_report"], None])
def test_kind_not_hashable_or_none_is_rejected(kind):
    assert "has kind" in _problems([_event(kind=kind)])


@pytest.mark.parametrize(
    "source", ["ftp://example.org/x", "example.org/report", "www.example.org", ""]
)
def test_non_http_source(source):
    assert "must start with http:// or https://" in _problems([_event(source=source)])


@pytest.mark.parametrize("verified", [1, 0, "yes", None])
def test_non_bool_verified(verified):
    assert "has verified" in _problems([_event(verified=verified)])


def test_verified_true_is_accepted():
    validate_events([_event(verified=True)], FIRMS)


@pytest.mark.parametrize("value", [dt.datetime(2026, 10, 5, 0, 0), "2026-10-05", 20261005])
def test_date_must_be_plain_date(value):
    assert "must be an unquoted date" in _problems([_event(date=value)])


@pytest.mark.parametrize("value", ["24:00", "23:60", "9:30", "0930", "12:5", 930, "1:30 pm"])
def test_bad_time_sgt(value):
    assert "must be HH:MM from 00:00 to 23:59" in _problems([_event(time_sgt=value)])


def test_unknown_firm_in_firms_named():
    msg = _problems([_event(firms_named=["First Resources", "Acme Palm"])])
    assert "unknown firm 'Acme Palm'" in msg


def test_firms_named_must_be_list():
    assert "must be a list" in _problems([_event(firms_named="First Resources")])


def test_unknown_key_is_an_error():
    event = _event()
    event["dat"] = event.pop("date")
    msg = _problems([event])
    assert "unknown key 'dat'" in msg
    assert "missing 'date'" in msg


@pytest.mark.parametrize("key,value", [("after_close", 1), ("confounds", ["x"]), ("notes", 3)])
def test_optional_field_types(key, value):
    assert f"has {key}" in _problems([_event(**{key: value})])


def test_all_problems_reported_at_once():
    msg = _problems([_event(id="a", kind="rumour"), _event(id="b", verified=1)])
    assert "has kind 'rumour'" in msg
    assert "has verified 1" in msg


def test_repo_events_are_valid():
    events = load_events()
    assert events
    assert all(e["kind"] in KINDS for e in events.values())


def _root_with(tmp_path, events):
    (tmp_path / "config").mkdir(parents=True)
    universe = {
        "exchanges": {"SGX": {"index_name": "STI", "index_ticker": "^STI", "currency": "SGD"}},
        "firms": [
            {
                "name": "Alpha",
                "ticker": "AAA.SI",
                "exchange": "SGX",
                "group": "Alpha",
                "greenpeace_named_2026": False,
                "verify": True,
            }
        ],
    }
    (tmp_path / "config" / "universe.yaml").write_text(yaml.safe_dump(universe))
    (tmp_path / "config" / "events.yaml").write_text(yaml.safe_dump({"events": events}))
    return tmp_path


def test_load_events_returns_by_id_and_checks_universe_names(tmp_path):
    root = _root_with(tmp_path / "ok", [_event(firms_named=["Alpha"])])
    assert list(load_events(root)) == ["test_event"]


def test_load_events_rejects_firm_not_in_universe(tmp_path):
    root = _root_with(tmp_path / "bad", [_event(firms_named=["Beta"])])
    with pytest.raises(ValueError, match="unknown firm 'Beta'"):
        load_events(root)
