"""Command line entry point: `python -m haze_salience {fetch,pilot}`."""

import argparse
import logging
import sys

import pandas as pd

from haze_salience import ROOT
from haze_salience.config import load_events, load_yaml
from haze_salience.data import cpo as cpo_mod
from haze_salience.data import prices as prices_mod
from haze_salience.universe import exchange_view, load_universe

RAW = ROOT / "data" / "raw"


def cmd_fetch() -> None:
    pilot = load_yaml("pilot.yaml")
    universe = exchange_view(load_universe(), pilot["exchange"])
    tickers = [f["ticker"] for f in universe["firms"]]
    tickers += [universe["market_index"]["ticker"], pilot["cpo"]["fallback_ticker"]]
    frames = prices_mod.fetch_ohlcv(tickers, str(pilot["fetch_start"]), str(pilot["fetch_end"]))
    close, volume = frames["close"], frames["volume"]
    path = prices_mod.save_prices(close, RAW)
    vol_path = prices_mod.save_volumes(volume, RAW)
    print(f"Saved {close.shape[1]} series x {close.shape[0]} days to {path.relative_to(ROOT)}")
    print(f"Saved volumes for {volume.shape[1]} series to {vol_path.relative_to(ROOT)}")
    report = prices_mod.coverage_report(close)
    report_path = RAW / "fetch_report.csv"
    report.to_csv(report_path)
    with pd.option_context("display.width", 160, "display.max_columns", None):
        print(f"Coverage (ends_early = last date more than 7 days before the frame end):\n{report}")
    print(f"Wrote {report_path.relative_to(ROOT)}")


def cmd_pilot() -> None:
    from datetime import UTC, datetime

    from haze_salience.events.pilot import run_pilot
    from haze_salience.events.plot import plot_pilot
    from haze_salience.events.report import write_pilot_report

    pilot, events = load_yaml("pilot.yaml"), load_events()
    universe = exchange_view(load_universe(), pilot["exchange"])
    prices = prices_mod.load_prices(RAW)
    try:
        volumes = prices_mod.load_volumes(RAW)
    except FileNotFoundError:
        volumes = None
        print("Volume not available: no cached volumes, so no abnormal volume columns.")
    fallback = pilot["cpo"]["fallback_ticker"]
    manual = ROOT / pilot["cpo"]["manual_csv"]
    lags = pilot["cpo"]["manual_lags" if manual.exists() else "fallback_lags"]
    out = run_pilot(
        prices,
        universe,
        pilot,
        events,
        lambda: cpo_mod.load_cpo(manual, lambda: prices[fallback].dropna()),
        cpo_lags=lags,
        volumes=volumes,
    )
    if out.summary.empty:
        sys.exit("No firm/event produced a result; see warnings above.")
    fig = plot_pilot(out, universe, events, ROOT / pilot["figure"])
    csv = fig.with_name("pilot_car_summary.csv")
    out.summary.to_csv(csv, index=False)
    report = write_pilot_report(
        out,
        universe,
        events,
        {
            "generated": datetime.now(UTC).strftime("%Y-%m-%d %H:%M UTC"),
            "data_start": str(prices.index.min().date()),
            "data_end": str(prices.index.max().date()),
            "figure": fig.name,  # the report is written beside the figure
        },
        fig.with_name("pilot_report.md"),
    )

    pct = ["car_pre", "car_day0", "car_post", "car_total", "band_total"]
    show = out.summary.set_index(["event", "firm"])[pct] * 100
    with pd.option_context(
        "display.float_format", "{:+.2f}".format, "display.width", 160, "display.max_columns", None
    ):
        print(f"CPO control: {out.control_label}\nCARs in %:\n{show}")
    for s in out.skipped:
        print(f"skipped: {s}")
    print(f"\nWrote {fig.relative_to(ROOT)} and {csv.relative_to(ROOT)}")
    print(f"Wrote {report.relative_to(ROOT)}")


def main(argv=None) -> None:
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(message)s")
    p = argparse.ArgumentParser(prog="haze_salience")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("fetch", help="Fetch prices into data/raw/ (needs network)")
    sub.add_parser("pilot", help="Stage 1 CAR plot from cached prices")
    args = p.parse_args(argv)
    try:
        {"fetch": cmd_fetch, "pilot": cmd_pilot}[args.cmd]()
    except (FileNotFoundError, RuntimeError) as e:
        sys.exit(f"error: {e}")


if __name__ == "__main__":
    main()
