import numpy as np
import pandas as pd
import pytest

from haze_salience.events.placebo import placebo_pvalue


def test_exact_small_case():
    base = np.array([-3, -2, -1, 0, 1, 2, 3], dtype=float)
    x = np.tile(base, 4)  # 28 residuals >= 1 + 20
    # Each value appears 4 times; observed = -2 -> values <= -2: {-3, -2} -> 8 of 28.
    expected = (1 + 8) / (1 + 28)
    assert placebo_pvalue(pd.Series(x), -2.0, 1) == pytest.approx(expected)
    # upper tail: values >= 2: {2, 3} -> 8
    assert placebo_pvalue(pd.Series(x), 2.0, 1, tail="upper") == pytest.approx(expected)
    # two-sided: |values| >= 3 -> {-3, 3} -> 8
    assert placebo_pvalue(pd.Series(x), -3.0, 1, tail="two") == pytest.approx(expected)


def test_length_two_uses_consecutive_sums():
    head = np.array([1.0, -2.0, 0.5, 3.0, -1.0])
    x = np.concatenate([head, np.zeros(20)])
    sums = np.convolve(x, [1, 1], "valid")
    assert len(sums) == len(x) - 1
    # Hand check of the first sums.
    assert sums[:3].tolist() == [-1.0, -1.5, 3.5]
    for obs in (-1.5, 0.0, 3.5):
        expected = (1 + np.sum(sums <= obs)) / (1 + len(sums))
        assert placebo_pvalue(pd.Series(x), obs, 2) == pytest.approx(expected)


def test_monotone():
    rng = np.random.default_rng(1)
    x = pd.Series(rng.normal(size=100))
    obs = np.linspace(-6, 6, 50)
    p = [placebo_pvalue(x, o, 3) for o in obs]
    assert all(a <= b for a, b in zip(p, p[1:], strict=False))


def test_bounds():
    rng = np.random.default_rng(2)
    x = pd.Series(rng.normal(size=60))
    n_windows = 60 - 5 + 1
    for o in (-100.0, -1.0, 0.0, 2.0, 100.0):
        p = placebo_pvalue(x, o, 5)
        assert 0 < p <= 1
    assert placebo_pvalue(x, -1e9, 5) == pytest.approx(1 / (1 + n_windows))
    assert placebo_pvalue(x, 1e9, 5) == pytest.approx(1.0)


def test_nans_dropped():
    x = np.arange(30, dtype=float)
    with_nan = np.insert(x, 10, np.nan)
    assert placebo_pvalue(pd.Series(with_nan), 5.0, 2) == placebo_pvalue(pd.Series(x), 5.0, 2)


def test_uniform_under_null():
    rng = np.random.default_rng(12345)
    p = np.array(
        [placebo_pvalue(pd.Series(s[:140]), s[140], 1) for s in rng.normal(size=(400, 141))]
    )
    assert abs(p.mean() - 0.5) < 0.05
    assert abs(np.mean(p < 0.10) - 0.10) < 0.05


def test_errors():
    x = pd.Series(np.arange(40, dtype=float))
    with pytest.raises(ValueError):
        placebo_pvalue(x, 0.0, 0)
    with pytest.raises(ValueError):
        placebo_pvalue(x, 0.0, 1, tail="bad")
    with pytest.raises(ValueError):
        placebo_pvalue(x, float("nan"), 1)
    with pytest.raises(ValueError):
        placebo_pvalue(x.iloc[:20], 0.0, 1)  # needs >= 21
    with pytest.raises(ValueError):
        placebo_pvalue(x.iloc[:24], 0.0, 5)  # needs >= 25
