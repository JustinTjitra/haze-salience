import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def calendar():
    """~1 year of weekday trading dates."""
    return pd.bdate_range("2025-11-03", "2026-11-06")


@pytest.fixture
def synthetic_returns(calendar):
    """Known data-generating process: r = 0.0002 + 1.2 * mkt + 0.5 * cpo + eps (sd 1%)."""
    rng = np.random.default_rng(42)
    n = len(calendar)
    mkt = rng.normal(0.0, 0.008, n)
    cpo = rng.normal(0.0, 0.015, n)
    eps = rng.normal(0.0, 0.01, n)
    firm = 0.0002 + 1.2 * mkt + 0.5 * cpo + eps
    return pd.DataFrame({"firm": firm, "mkt": mkt, "cpo": cpo}, index=calendar)
