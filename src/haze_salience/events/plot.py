"""Pilot figure: one panel per event, one CAR line per firm."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.ticker import MultipleLocator  # noqa: E402


def plot_pilot(output, universe: dict, events: dict[str, dict], out_path: str | Path) -> Path:
    named = {f["name"]: f.get("greenpeace_named_2026", False) for f in universe["firms"]}
    colors = dict(zip(named, plt.get_cmap("tab10").colors, strict=False))
    event_ids = list(output.results)

    fig, axes = plt.subplots(1, len(event_ids), figsize=(6 * len(event_ids), 4.5), sharey=True)
    axes = np.atleast_1d(axes)
    for ax, event_id in zip(axes, event_ids, strict=True):
        ev = events[event_id]
        firm_results = output.results[event_id]
        if firm_results:
            # Typical noise envelope: median firm's +/-95% band around zero
            band = np.median([r.band.to_numpy() for r in firm_results.values()], axis=0)
            offsets = next(iter(firm_results.values())).band.index
            ax.fill_between(
                offsets, -band * 100, band * 100, color="0.9", label="typical ±95% noise"
            )
        for name, res in firm_results.items():
            ax.plot(
                res.car.index,
                res.car * 100,
                color=colors[name],
                linestyle="-" if named[name] else "--",
                linewidth=1.8,
                label=f"{name}{' (named)' if named[name] else ''}",
            )
        ax.axvline(0, color="k", linewidth=0.8)
        ax.axhline(0, color="k", linewidth=0.5)
        # Mark the other pilot events that fall inside this window (exact trading-day offset)
        lo, hi = output.event_window
        for other_id in event_ids:
            if other_id == event_id or not firm_results:
                continue
            off = output.day0_positions[other_id] - output.day0_positions[event_id]
            if lo <= off <= hi:
                ax.axvline(off, color="0.4", linestyle=":", linewidth=1)
                label = f" {events[other_id]['label']}"
                ax.text(off, ax.get_ylim()[1], label, fontsize=8, va="top", color="0.3")
        ax.set_title(f"{ev['label']} ({ev['date']})")
        ax.set_xlabel("Trading days relative to event")
        ax.xaxis.set_major_locator(MultipleLocator(5))
        ax.xaxis.set_minor_locator(MultipleLocator(1))
    axes[0].set_ylabel("Cumulative abnormal return (%)")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="lower center",
        ncol=min(len(labels), 6),
        fontsize=8,
        frameon=False,
        bbox_to_anchor=(0.5, 0.04),
    )
    fig.suptitle("Stage 1 pilot: SGX palm oil CARs, market model on STI + CPO")
    fig.text(
        0.01,
        0.01,
        f"CPO control: {output.control_label}. Estimation window [-150, -31] trading days. "
        "Descriptive only: 5 firms, 2 events.",
        fontsize=8,
        color="0.3",
    )
    fig.tight_layout(rect=(0, 0.12, 1, 0.95))
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return out_path
