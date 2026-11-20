# T201 Universe with IDX names

Tier: haiku · Depends: T113

## Goal
The universe file knows both exchanges and the IDX firms, and code asks for "the SGX firms" or
"the IDX firms" through one small module. The pilot keeps using SGX only.

## Files
- `config/universe.yaml`
- `config/pilot.yaml` (add `exchange: SGX`)
- `src/haze_salience/universe.py` (new)
- `src/haze_salience/cli.py`
- `tests/test_universe.py` (new)

## Spec
`config/universe.yaml`, new shape (keep every existing SGX firm entry and its fields, add
`group`):

```yaml
exchanges:
  SGX: {index_name: Straits Times Index, index_ticker: "^STI", currency: SGD}
  IDX: {index_name: Jakarta Composite Index, index_ticker: "^JKSE", currency: IDR}
firms:
  - {name: First Resources, ticker: EB5.SI, exchange: SGX, group: First Resources, ...}
  ...
```
Add these IDX firms, all with `verify: true` and `greenpeace_named_2026: false`:

| name | ticker | group |
| --- | --- | --- |
| Astra Agro Lestari | AALI.JK | Astra |
| SMART (Sinar Mas Agro Resources) | SMAR.JK | Sinar Mas |
| London Sumatra | LSIP.JK | Salim |
| Salim Ivomas Pratama | SIMP.JK | Salim |
| Sawit Sumbermas Sarana | SSMS.JK | Sawit Sumbermas |
| Dharma Satya Nusantara | DSNG.JK | Dharma Satya |

Groups for the SGX firms: Golden Agri-Resources → `Sinar Mas`; Indofood Agri Resources → `Salim`;
the other three use their own name. Remove the old top-level `market_index` key.

`src/haze_salience/universe.py`:
```python
def load_universe(root=ROOT) -> dict                  # the parsed YAML, validated
def firms_on(universe: dict, exchange: str) -> list[dict]
def index_ticker(universe: dict, exchange: str) -> str
def exchange_view(universe: dict, exchange: str) -> dict
    # {"market_index": {"ticker": ...}, "firms": [...]}: the shape run_pilot and plot_pilot expect
```
Validation in `load_universe` (raise `ValueError` listing every problem): each firm has `name`,
`ticker`, `exchange`, `group`; names and tickers are unique; each firm's exchange is a key of
`exchanges`; each exchange has `index_ticker`.

`cli.py`: `cmd_fetch` and `cmd_pilot` use `exchange_view(load_universe(), pilot["exchange"])`
instead of the raw YAML. Behaviour for SGX is unchanged.

## Acceptance tests
- `test_repo_universe_is_valid`: `load_universe()` on the real config; 5 SGX and 6 IDX firms.
- `test_firms_on_and_index_ticker`.
- `test_exchange_view_shape`: has `market_index.ticker == "^STI"` and only SGX firms.
- `test_validation_errors`: duplicate ticker, unknown exchange, missing `group` each raise and the
  message names the problem.
- All pilot tests pass unchanged (they build their own universe dicts).

## Out of scope
Fetching IDX prices, changing `run_pilot`'s signature, verifying tickers (they stay `verify: true`).
