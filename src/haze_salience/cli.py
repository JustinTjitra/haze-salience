"""Command line entry point: `python -m haze_salience {fetch,pilot}`."""

import argparse
import logging
import sys

import pandas as pd

from haze_salience import ROOT
from haze_salience.config import load_events, load_yaml
from haze_salience.data import cpo as cpo_mod
from haze_salience.data import prices as prices_mod

RAW = ROOT / "data" / "raw"


def cmd_fetch() -> None:
    universe, pilot = load_yaml("universe.yaml"), load_yaml("pilot.yaml")
    tickers = [f["ticker"] for f in universe["firms"]]
    tickers += [universe["market_index"]["ticker"], pilot["cpo"]["fallback_ticker"]]
    df = prices_mod.fetch_prices(tickers, str(pilot["fetch_start"]), str(pilot["fetch_end"]))
    path = prices_mod.save_prices(df, RAW)
    print(f"Saved {df.shape[1]} series x {df.shape[0]} days to {path.relative_to(ROOT)}")


def cmd_pilot() -> None:
    from haze_salience.events.pilot import run_pilot
    from haze_salience.events.plot import plot_pilot

    universe, pilot, events = load_yaml("universe.yaml"), load_yaml("pilot.yaml"), load_events()
    prices = prices_mod.load_prices(RAW)
    fallback = pilot["cpo"]["fallback_ticker"]
    out = run_pilot(
        prices,
        universe,
        pilot,
        events,
        lambda: cpo_mod.load_cpo(
            ROOT / pilot["cpo"]["manual_csv"], lambda: prices[fallback].dropna()
        ),
    )
    if out.summary.empty:
        sys.exit("No firm/event produced a result; see warnings above.")
    fig = plot_pilot(out, universe, events, ROOT / pilot["figure"])
    csv = fig.with_name("pilot_car_summary.csv")
    out.summary.to_csv(csv, index=False)

    pct = ["car_pre", "car_day0", "car_post", "car_total", "band_total"]
    show = out.summary.set_index(["event", "firm"])[pct] * 100
    with pd.option_context(
        "display.float_format", "{:+.2f}".format, "display.width", 160, "display.max_columns", None
    ):
        print(f"CPO control: {out.control_label}\nCARs in %:\n{show}")
    for s in out.skipped:
        print(f"skipped: {s}")
    print(f"\nWrote {fig.relative_to(ROOT)} and {csv.relative_to(ROOT)}")


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
