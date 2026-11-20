# T105 Placebo p-values

Tier: sonnet · Depends: none

## Goal
A distribution-free p-value for an event-window abnormal return: where does it fall among all
same-length sums of estimation-window residuals? With five firms, this is more trustworthy than a
normal approximation.

## Files
- `src/haze_salience/events/placebo.py` (new)
- `tests/test_placebo.py` (new)

## Spec
```python
def placebo_pvalue(resid: pd.Series, observed: float, length: int, tail: str = "lower") -> float
```
- Placebo statistics: the sums of every run of `length` consecutive residuals (overlapping
  windows; `n - length + 1` of them). NaNs in `resid` are dropped first.
- `tail="lower"`: `(1 + #{S_j <= observed}) / (1 + n_windows)`.
  `tail="upper"`: same with `>=`. `tail="two"`: `(1 + #{|S_j| >= |observed|}) / (1 + n_windows)`.
- Raise `ValueError` if `length < 1`, if `tail` is unknown, if `observed` is NaN, or if there are
  fewer than `length + 20` residuals.

Docstring must state the caveat: event-window abnormal returns have slightly larger variance than
residuals (forecast error), so this p-value is mildly anti-conservative.

## Acceptance tests
- `test_exact_small_case`: residuals `[-3, -2, -1, 0, 1, 2, 3]` repeated to satisfy the length
  rule; compute the expected lower-tail p-value for `length=1` by hand in the test and compare.
- `test_length_two_uses_consecutive_sums`: for a short hand-written series (padded to satisfy the
  length rule) check the placebo set equals `np.convolve(x, [1, 1], "valid")`.
- `test_monotone`: a more negative `observed` never gives a larger lower-tail p-value.
- `test_bounds`: result is in `(0, 1]`; `observed` below every placebo gives `1 / (1 + n_windows)`.
- `test_uniform_under_null`: seeded; draw 400 independent normal series of length 141, use the
  last value as `observed` and the first 140 as `resid`; mean p is within 0.05 of 0.5 and the
  share of p < 0.10 is within 0.05 of 0.10.
- `test_errors`: each `ValueError` case.

## Out of scope
Wiring into `summary()` (T106), block bootstrap, cross-sectional tests.
