import copy

import pytest
import yaml

from haze_salience.universe import exchange_view, firms_on, index_ticker, load_universe

VALID = {
    "exchanges": {
        "SGX": {"index_name": "Straits Times Index", "index_ticker": "^STI", "currency": "SGD"},
        "IDX": {
            "index_name": "Jakarta Composite Index",
            "index_ticker": "^JKSE",
            "currency": "IDR",
        },
    },
    "firms": [
        {
            "name": "Alpha",
            "ticker": "AAA.SI",
            "exchange": "SGX",
            "group": "Alpha",
            "greenpeace_named_2026": False,
            "verify": True,
        },
        {
            "name": "Beta",
            "ticker": "BBB.JK",
            "exchange": "IDX",
            "group": "Beta",
            "greenpeace_named_2026": False,
            "verify": True,
        },
    ],
}


def _root_with(tmp_path, data):
    (tmp_path / "config").mkdir(parents=True)
    (tmp_path / "config" / "universe.yaml").write_text(yaml.safe_dump(data))
    return tmp_path


def test_repo_universe_is_valid():
    universe = load_universe()
    sgx, idx = firms_on(universe, "SGX"), firms_on(universe, "IDX")
    assert len(sgx) == 5
    assert len(idx) == 6
    assert {f["exchange"] for f in sgx} == {"SGX"}
    assert {f["exchange"] for f in idx} == {"IDX"}
    groups = {f["name"]: f["group"] for f in sgx}
    assert groups["Golden Agri-Resources"] == "Sinar Mas"
    assert groups["Indofood Agri Resources"] == "Salim"
    assert groups["First Resources"] == "First Resources"
    assert all(f["verify"] is True and f["greenpeace_named_2026"] is False for f in idx)


def test_firms_on_and_index_ticker():
    assert [f["name"] for f in firms_on(VALID, "IDX")] == ["Beta"]
    assert [f["name"] for f in firms_on(VALID, "SGX")] == ["Alpha"]
    assert index_ticker(VALID, "IDX") == "^JKSE"
    assert index_ticker(VALID, "SGX") == "^STI"
    with pytest.raises(ValueError, match="unknown exchange 'NYSE'"):
        firms_on(VALID, "NYSE")
    with pytest.raises(ValueError, match="unknown exchange 'NYSE'"):
        index_ticker(VALID, "NYSE")


def test_exchange_view_shape():
    view = exchange_view(load_universe(), "SGX")
    assert set(view) == {"market_index", "firms"}
    assert view["market_index"] == {"ticker": "^STI"}
    assert len(view["firms"]) == 5
    assert {f["exchange"] for f in view["firms"]} == {"SGX"}


def test_validation_errors(tmp_path):
    dup_ticker = copy.deepcopy(VALID)
    dup_ticker["firms"][1]["ticker"] = "AAA.SI"
    with pytest.raises(ValueError, match="duplicate ticker 'AAA.SI'"):
        load_universe(_root_with(tmp_path / "a", dup_ticker))

    unknown = copy.deepcopy(VALID)
    unknown["firms"][1]["exchange"] = "NYSE"
    with pytest.raises(ValueError, match="unknown exchange 'NYSE'"):
        load_universe(_root_with(tmp_path / "b", unknown))

    no_group = copy.deepcopy(VALID)
    del no_group["firms"][0]["group"]
    with pytest.raises(ValueError, match="'Alpha' is missing 'group'"):
        load_universe(_root_with(tmp_path / "c", no_group))

    no_index = copy.deepcopy(VALID)
    del no_index["exchanges"]["IDX"]["index_ticker"]
    with pytest.raises(ValueError, match="'IDX' has no index_ticker"):
        load_universe(_root_with(tmp_path / "d", no_index))


def test_validation_reports_every_problem(tmp_path):
    bad = copy.deepcopy(VALID)
    bad["firms"][1]["ticker"] = "AAA.SI"
    bad["firms"][1]["exchange"] = "NYSE"
    with pytest.raises(ValueError) as err:
        load_universe(_root_with(tmp_path, bad))
    assert "duplicate ticker" in str(err.value)
    assert "unknown exchange" in str(err.value)
