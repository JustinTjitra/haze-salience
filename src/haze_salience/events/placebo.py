"""Distribution-free placebo p-values for event-window abnormal returns."""

from __future__ import annotations

import numpy as np
import pandas as pd

_TAILS = ("lower", "upper", "two")


def placebo_pvalue(resid: pd.Series, observed: float, length: int, tail: str = "lower") -> float:
    """Placebo p-value of an event-window sum among estimation-window residual sums.

    The placebo statistics are the sums of every run of ``length`` consecutive residuals
    (overlapping windows, ``n - length + 1`` of them, after dropping NaNs). With ``S_j`` the
    placebo sums and ``W`` their count:

    - ``tail="lower"``: ``(1 + #{S_j <= observed}) / (1 + W)``
    - ``tail="upper"``: ``(1 + #{S_j >= observed}) / (1 + W)``
    - ``tail="two"``: ``(1 + #{|S_j| >= |observed|}) / (1 + W)``

    Caveat: event-window abnormal returns have slightly larger variance than estimation-window
    residuals (forecast error), so this p-value is mildly anti-conservative.

    Raises ``ValueError`` if ``length < 1``, ``tail`` is unknown, ``observed`` is NaN, or there
    are fewer than ``length + 20`` residuals.
    """
    if length < 1:
        raise ValueError(f"length must be >= 1, got {length}")
    if tail not in _TAILS:
        raise ValueError(f"tail must be one of {_TAILS}, got {tail!r}")
    if observed is None or np.isnan(observed):
        raise ValueError("observed must not be NaN")
    x = pd.Series(resid).dropna().to_numpy(dtype=float)
    if len(x) < length + 20:
        raise ValueError(f"need at least length + 20 = {length + 20} residuals, got {len(x)}")
    sums = np.convolve(x, np.ones(length), "valid")
    if tail == "lower":
        count = int(np.sum(sums <= observed))
    elif tail == "upper":
        count = int(np.sum(sums >= observed))
    else:
        count = int(np.sum(np.abs(sums) >= abs(observed)))
    return (1 + count) / (1 + len(sums))
