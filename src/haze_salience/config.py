"""Load the YAML configs in config/."""

from pathlib import Path

import yaml

from haze_salience import ROOT


def load_yaml(name: str, root: Path = ROOT) -> dict:
    with open(root / "config" / name) as f:
        return yaml.safe_load(f)


def load_events(root: Path = ROOT) -> dict[str, dict]:
    return {e["id"]: e for e in load_yaml("events.yaml", root)["events"]}
