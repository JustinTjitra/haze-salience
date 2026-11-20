from pathlib import Path

import yaml

WORKFLOW = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "ci.yml"


def _load():
    with WORKFLOW.open() as fh:
        return yaml.safe_load(fh)


def _triggers(doc):
    # PyYAML (YAML 1.1) parses the bare key `on` as the boolean True.
    return doc["on"] if "on" in doc else doc[True]


def test_ci_runs_lint_and_tests():
    steps = _load()["jobs"]["test"]["steps"]
    runs = [step.get("run") for step in steps]

    assert "make lint" in runs
    assert "make test" in runs

    sync = runs.index("uv sync")
    assert sync < runs.index("make lint")
    assert sync < runs.index("make test")


def test_ci_triggers():
    triggers = _triggers(_load())

    assert "pull_request" in triggers
    assert "push" in triggers
    assert triggers["push"]["branches"] == ["main"]
