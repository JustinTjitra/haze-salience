# T206 Events schema validator

Tier: haiku · Depends: T201

## Goal
`config/events.yaml` is checked on load, so a typo in a date or a firm name fails loudly.

## Files
- `src/haze_salience/events_schema.py` (new)
- `src/haze_salience/config.py` (`load_events` calls the validator)
- `tests/test_events_schema.py` (new)

## Spec
```python
KINDS = {"ngo_report", "salience", "government", "regulatory", "company_response", "price_move"}

def validate_events(events: list[dict], firm_names: set[str]) -> None
```
Collect every problem and raise one `ValueError` listing them all. Rules:
- Required: `id` (unique string), `date` (a `datetime.date`), `kind` (in `KINDS`), `label`,
  `description`, `source` (starts with `http://` or `https://`), `verified` (bool).
- Optional: `after_close` (bool), `time_sgt` (string `HH:MM`, 00:00 to 23:59), `firms_named`
  (list; every entry must be in `firm_names`), `confounds` (string), `notes` (string).
- Any other key is an error (catches misspelt keys).

`load_events` validates with the firm names from `load_universe()` and still returns
`{id: event}`.

## Acceptance tests
- `test_repo_events_are_valid`: the real `config/events.yaml` passes.
- One test per rule: missing key, duplicate id, bad kind, non-http source, non-bool `verified`,
  bad `time_sgt`, unknown firm in `firms_named`, unknown key.
- `test_all_problems_reported_at_once`: two problems in one file → both in the message.

## Out of scope
Editing `config/events.yaml` (protected). If the real file fails validation, stop and report.
