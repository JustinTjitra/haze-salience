import re

import numpy as np
import pandas as pd
import pytest

from haze_salience.events.pilot import run_pilot
from haze_salience.events.report import write_pilot_report

UNIVERSE = {
    "market_index": {"ticker": "^STI"},
    "firms": [
        {"name": "Named Co", "ticker": "AAA.SI", "greenpeace_named_2026": True},
        {"name": "Other Co", "ticker": "BBB.SI", "greenpeace_named_2026": False},
    ],
}
EVENTS = {
    "e1": {"date": "2026-10-05", "label": "Report", "verified": True},
    "e2": {"date": "2026-10-16", "label": "Statement", "verified": True},
}
CFG = {
    "events": ["e1", "e2"],
    "estimation_window": [-150, -31],
    "event_window": [-10, 10],
    "min_estimation_days": 100,
}
META = {
    "generated": "2026-11-20 10:00 UTC",
    "data_start": "2025-12-01",
    "data_end": "2026-11-06",
    "figure": "pilot_car.png",
}
HEADINGS = [
    "# Stage 1 pilot report",
    "## Events",
    "## Event e1: Report",
    "### Firms",
    "### Portfolios",
    "## Event e2: Statement",
    "### Firms",
    "### Portfolios",
    "## Skipped",
    "## How to read this",
    "## Figure",
]


@pytest.fixture
def prices():
    """SGX calendar with a holiday; CPO on a different calendar; -9% hit to Named Co on 16 Oct."""
    rng = np.random.default_rng(7)
    cal = pd.bdate_range("2025-12-01", "2026-11-06").drop(pd.Timestamp("2026-08-10"))
    n = len(cal)
    mkt = rng.normal(0, 0.008, n)
    cpo = rng.normal(0, 0.015, n)
    a = 1.0 * mkt + 0.4 * cpo + rng.normal(0, 0.01, n)
    b = 0.8 * mkt + 0.6 * cpo + rng.normal(0, 0.01, n)
    a[cal.get_loc(pd.Timestamp("2026-10-16"))] -= 0.09
    to_level = lambda r: 100 * np.cumprod(1 + r)  # noqa: E731
    df = pd.DataFrame(
        {"^STI": to_level(mkt), "AAA.SI": to_level(a), "BBB.SI": to_level(b)}, index=cal
    )
    cpo_series = pd.Series(to_level(cpo), index=cal).drop(pd.Timestamp("2026-09-01"))
    return df, cpo_series


@pytest.fixture
def volumes(prices):
    """Lognormal daily volumes for both firms, on the pilot calendar."""
    df, _ = prices
    rng = np.random.default_rng(42)
    return pd.DataFrame(
        {t: np.exp(rng.normal(np.log(1e6), 0.3, len(df.index))) for t in ("AAA.SI", "BBB.SI")},
        index=df.index,
    )


def _run(prices, events=EVENTS, volumes=None, df=None):
    base, cpo = prices
    return run_pilot(
        base if df is None else df,
        UNIVERSE,
        CFG,
        events,
        lambda: (cpo, "test CPO"),
        volumes=volumes,
    )


def _write(tmp_path, output, events=EVENTS, name="report.md"):
    path = write_pilot_report(output, UNIVERSE, events, META, tmp_path / name)
    return path.read_text(encoding="utf-8")


def _headings(text):
    return re.findall(r"^#{1,6} .*$", text, flags=re.MULTILINE)


def _section(text, start, end=None):
    """Text from the line starting with `start` up to the line starting with `end`."""
    i = text.index(start)
    j = text.index(end, i + len(start)) if end else len(text)
    return text[i:j]


def _cells(section, first_cell):
    for line in section.splitlines():
        if line.startswith(f"| {first_cell} |"):
            return [c.strip() for c in line.strip().strip("|").split("|")]
    raise AssertionError(f"no row {first_cell!r} in section")


def test_report_sections_in_order(prices, tmp_path):
    text = _write(tmp_path, _run(prices))
    assert _headings(text) == HEADINGS


def test_report_numbers_match_summary(prices, tmp_path):
    out = _run(prices)
    text = _write(tmp_path, out)
    row = out.summary.set_index(["event", "firm"]).loc[("e2", "Named Co")]
    cells = _cells(_section(text, "## Event e2", "### Portfolios"), "Named Co")
    assert cells == [
        "Named Co",
        f"{row['car_pre'] * 100:.2f}%",
        f"{row['car_day0'] * 100:.2f}%",
        f"{row['t_day0']:.2f}",
        f"{row['p_placebo_day0']:.3f}",
        f"{row['car_0_1'] * 100:.2f}%",
        f"{row['p_placebo_0_1']:.3f}",
        f"{row['car_post'] * 100:.2f}%",
    ]


def test_events_table_shows_day0_and_flags(prices, tmp_path):
    out = _run(prices)
    text = _write(tmp_path, out)
    events_section = _section(text, "## Events", "## Event e1")
    assert "| e2 | Statement | 2026-10-16 | 2026-10-16 | no | yes |" in events_section


def test_unverified_warning(prices, tmp_path):
    out = _run(prices)
    text = _write(tmp_path, out)
    assert "Unverified events" not in text

    unverified = {**EVENTS, "e2": {"date": "2026-10-16", "label": "Statement"}}  # key missing
    text = _write(tmp_path, _run(prices, unverified), unverified, name="unv.md")
    assert "**Unverified events: results are provisional.**" in text
    table = _section(text, "## Events", "**Unverified")
    assert "| e2 | Statement | 2026-10-16 | 2026-10-16 | no | no |" in table


def test_confound_line(prices, tmp_path):
    confounded = {
        **EVENTS,
        "e1": {**EVENTS["e1"], "confounds": "Haze levels also rose that week."},
    }
    text = _write(tmp_path, _run(prices, confounded), confounded)
    assert text.count("Confound: Haze levels also rose that week.") == 1
    e1_section = _section(text, "## Event e1", "## Event e2")
    assert "Confound: Haze levels also rose that week." in e1_section
    e2_section = _section(text, "## Event e2", "## Skipped")
    assert "Confound:" not in e2_section


def test_report_is_deterministic(prices, tmp_path):
    out = _run(prices)
    a = write_pilot_report(out, UNIVERSE, EVENTS, META, tmp_path / "r1.md")
    b = write_pilot_report(out, UNIVERSE, EVENTS, META, tmp_path / "r2.md")
    assert a.read_bytes() == b.read_bytes()


def test_no_interpretive_words(prices, tmp_path, volumes):
    text = _write(tmp_path, _run(prices, volumes=volumes)).lower()
    for word in ("significant", "confirms", "proves", "strong"):
        assert word not in text


def test_skipped_bullets(prices, tmp_path):
    base, _ = prices
    short = base.copy()
    short.loc[:"2026-08-31", "BBB.SI"] = np.nan  # Other Co: too little estimation data
    out = _run(prices, df=short)
    text = _write(tmp_path, out)
    section = _section(text, "## Skipped", "## How to read this")
    bullets = [line for line in section.splitlines() if line.startswith("- ")]
    assert bullets == [f"- {s}" for s in out.skipped]
    assert len(bullets) == 8


def test_skipped_none(prices, tmp_path):
    out = _run(prices)
    assert out.skipped == []
    text = _write(tmp_path, out)
    assert _section(text, "## Skipped", "## How to read this").strip() == "## Skipped\n\nNone"


def test_abvol_column_and_blank_portfolio_cells(prices, volumes, tmp_path):
    out = _run(prices, volumes=volumes)
    text = _write(tmp_path, out)
    firms = _section(text, "### Firms", "### Portfolios")
    assert "| Firm | car_pre | car_day0 | t_day0 | p_placebo_day0 | car_0_1 |" in firms
    assert "| car_post | abvol_day0 |" in firms
    e2 = _section(text, "## Event e2", "## Skipped")
    cells = _cells(e2, "All firms")
    assert cells[-1] == ""  # abvol is NaN for portfolios and prints blank
    assert _cells(e2, "Named Co")[-1] != ""  # firm rows carry abvol
