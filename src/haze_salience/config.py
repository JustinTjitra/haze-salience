"""Load the YAML configs in config/."""

from pathlib import Path

import yaml

from haze_salience import ROOT
from haze_salience.events_schema import validate_events


def load_yaml(name: str, root: Path = ROOT) -> dict:
    with open(root / "config" / name) as f:
        return yaml.safe_load(f)


def load_events(root: Path = ROOT) -> dict[str, dict]:
    # Imported here: universe.py imports load_yaml from this module.
    from haze_salience.universe import load_universe

    events = load_yaml("events.yaml", root)["events"]
    firm_names = {f["name"] for f in load_universe(root)["firms"]}
    validate_events(events, firm_names)
    return {e["id"]: e for e in events}
