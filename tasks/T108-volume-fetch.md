# T108 Volume fetch and cache

Tier: haiku · Depends: none

## Goal
`make data` stores daily trading volume next to closing prices, and the Yahoo download-splitting
logic gets its first test.

## Files
- `src/haze_salience/data/prices.py`
- `src/haze_salience/cli.py` (`cmd_fetch` only)
- `tests/test_prices.py`

## Spec
- New `fetch_ohlcv(tickers, start, end) -> dict[str, pd.DataFrame]` with keys `"close"` and
  `"volume"`: one `yf.download` call (same arguments as today), split into two wide frames with
  one column per ticker, tz-naive normalised DatetimeIndex, sorted. The existing "no data" and
  "no prices for [tickers]" errors still apply (based on close).
- `fetch_prices(tickers, start, end)` stays and returns `fetch_ohlcv(...)["close"]`.
- Generalise the cache: `save_frame(df, cache_dir, name)` and `load_frame(cache_dir, name)` writing
  and reading `<name>.parquet`; a missing file raises `FileNotFoundError` whose message contains
  "make data". `save_prices` / `load_prices` stay as thin wrappers with `name="prices"`. Add
  `save_volumes` / `load_volumes` with `name="volumes"`.
- `cmd_fetch` calls `fetch_ohlcv` once and saves both frames.

## Acceptance tests
- `test_fetch_ohlcv_splits_columns`: monkeypatch `yfinance.download` to return a small DataFrame
  with MultiIndex columns (`("Close", ticker)`, `("Volume", ticker)`, for two tickers) and a
  tz-aware index; assert both frames have the two ticker columns, a tz-naive index, and the right
  values.
- `test_fetch_ohlcv_single_ticker`: the monkeypatched download returns flat columns
  (`Close`, `Volume`); result frames have one column named after the ticker.
- `test_fetch_raises_on_missing_ticker`: one ticker's close is all NaN → `RuntimeError` naming it.
- `test_volume_round_trip` and `test_missing_volume_cache_points_to_make_data`.
- Existing price-cache tests pass unchanged.

## Out of scope
Using volume anywhere (T109, T110), retries, rate-limit handling.
