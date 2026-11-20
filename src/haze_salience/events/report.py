"""Markdown report of the Stage 1 pilot numbers.

The report states numbers and caveats and does not interpret them. Every number in it is
copied from `PilotOutput.summary` or the event configuration, formatted as specified.
"""

from collections.abc import Callable
from pathlib import Path

import pandas as pd

from haze_salience.events.pilot import PilotOutput

HOW_TO_READ = (
    "With five firms the results are descriptive: they show how these names moved around "
    "these dates, and they do not on their own identify a cause. The placebo p-value is the "
    "share of estimation-window windows at least as negative as the event-window value, so a "
    "small value means few placebo windows were that negative. The cumulative band widens "
    "quickly as the window lengthens, so the short windows (day 0, and day 0 to 1) are the "
    "relevant ones."
)


def _blank(x) -> bool:
    return x is None or bool(pd.isna(x))


def _pct(x) -> str:
    return "" if _blank(x) else f"{float(x) * 100:.2f}%"


def _num(x) -> str:
    return "" if _blank(x) else f"{float(x):.2f}"


def _p(x) -> str:
    return "" if _blank(x) else f"{float(x):.3f}"


def _cell(text) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def _table(headers: list[str], rows: list[list[str]]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    lines += ["| " + " | ".join(row) + " |" for row in rows]
    return lines


def _yes_no(flag: bool) -> str:
    return "yes" if flag else "no"


def _confound_text(value) -> str:
    if isinstance(value, list | tuple):
        value = "; ".join(str(v) for v in value)
    return " ".join(str(value).split())


def _day0_used(summary: pd.DataFrame, event_id: str) -> str:
    if summary.empty:
        return ""
    sub = summary[summary["event"] == event_id]
    return "" if sub.empty else str(sub["day0"].iloc[0])


def _event_table(output: PilotOutput, events: dict[str, dict]) -> list[str]:
    headers = ["Id", "Label", "Recorded date", "Day 0 used", "After close", "Verified"]
    rows = []
    for event_id in output.day0_positions:
        ev = events.get(event_id, {})
        rows.append(
            [
                _cell(event_id),
                _cell(ev.get("label", "")),
                _cell(ev.get("date", "")),
                _cell(_day0_used(output.summary, event_id)),
                _yes_no(bool(ev.get("after_close", False))),
                # A missing key counts as not verified.
                _yes_no(ev.get("verified", False) is True),
            ]
        )
    return _table(headers, rows)


def _result_table(summary: pd.DataFrame, event_id: str, kind: str, name_header: str) -> list[str]:
    sub = (
        summary[(summary["event"] == event_id) & (summary["kind"] == kind)]
        if not summary.empty
        else summary
    )
    if sub.empty:
        return ["No rows.", ""]
    cols: list[tuple[str, Callable[[object], str]]] = [
        ("car_pre", _pct),
        ("car_day0", _pct),
        ("t_day0", _num),
        ("p_placebo_day0", _p),
        ("car_0_1", _pct),
        ("p_placebo_0_1", _p),
        ("car_post", _pct),
    ]
    if "abvol_day0" in summary.columns:
        cols.append(("abvol_day0", _num))
    headers = [name_header] + [name for name, _ in cols]
    rows = [[_cell(r["firm"])] + [fmt(r[name]) for name, fmt in cols] for _, r in sub.iterrows()]
    return _table(headers, rows) + [""]


def write_pilot_report(
    output: PilotOutput,
    universe: dict,
    events: dict[str, dict],
    meta: dict,
    out_path,
) -> Path:
    """Write the pilot report to `out_path` and return its path.

    `universe` is accepted for the common report signature; firm rows follow the order of
    `output.summary`, which already follows the universe. `meta` needs `generated`,
    `data_start`, `data_end` (strings) and `figure` (the figure's path relative to the report).
    Nothing is read from the clock or the file system.
    """
    out_path = Path(out_path)
    lines: list[str] = [
        "# Stage 1 pilot report",
        "",
        f"Generated {meta['generated']}. Data from {meta['data_start']} to {meta['data_end']}. "
        f"CPO control: {output.control_label}.",
        "",
        "## Events",
        "",
    ]
    lines += _event_table(output, events)
    lines.append("")
    if any(events.get(e, {}).get("verified", False) is not True for e in output.day0_positions):
        lines += ["**Unverified events: results are provisional.**", ""]

    for event_id in output.day0_positions:
        ev = events.get(event_id, {})
        lines += [f"## Event {event_id}: {ev.get('label', '')}", ""]
        if ev.get("confounds"):
            lines += [f"Confound: {_confound_text(ev['confounds'])}", ""]
        lines += ["### Firms", ""]
        lines += _result_table(output.summary, event_id, "firm", "Firm")
        lines += ["### Portfolios", ""]
        lines += _result_table(output.summary, event_id, "portfolio", "Portfolio")

    lines += ["## Skipped", ""]
    if output.skipped:
        lines += [f"- {s}" for s in output.skipped]
    else:
        lines.append("None")
    lines.append("")

    lines += ["## How to read this", "", HOW_TO_READ, ""]
    lines += ["## Figure", "", f"![Pilot CARs]({meta['figure']})", ""]

    out_path.write_text("\n".join(lines), encoding="utf-8")
    return out_path
