# T113 Pilot report writer

Tier: haiku · Depends: T106, T111

## Goal
`make pilot` writes a self-contained Markdown report of the pilot numbers, so the go/no-go
decision is made from one page. The report states numbers and caveats; it does not interpret.

## Files
- `src/haze_salience/events/report.py` (new)
- `src/haze_salience/cli.py` (`cmd_pilot` only)
- `tests/test_report.py` (new)

## Spec
```python
def write_pilot_report(output, universe: dict, events: dict[str, dict], meta: dict, out_path) -> Path
```
`meta` carries `generated` (string timestamp), `data_start`, `data_end` (strings) and
`figure` (relative path of the figure). The function must not read the clock or the file system
beyond writing `out_path`, so tests are deterministic.

Sections, in order:
1. Title and one line: generated time, data range, CPO control used (`output.control_label`).
2. **Events**: table of id, label, recorded date, day 0 actually used, `after_close`, `verified`
   (missing key counts as false). If any event is not verified, a bold line right under the table:
   "Unverified events: results are provisional."
3. One section per event with two tables, firms then portfolios. Columns (percent with two
   decimals for returns, three decimals for p-values, blank for missing): `car_pre`, `car_day0`,
   `t_day0`, `p_placebo_day0`, `car_0_1`, `p_placebo_0_1`, `car_post`, and `abvol_day0` when the
   column exists. If the event has a `confounds` field, print it as "Confound: ..." above the tables.
4. **Skipped**: bullet list of `output.skipped`, or "None".
5. **How to read this**: fixed text saying that with five firms the results are descriptive, that
   the placebo p-value is the share of estimation-window windows at least as negative, and that
   the cumulative band widens quickly so short windows are the relevant ones.
6. The figure, as a Markdown image link to `meta["figure"]`.

No sentence may be generated from the numbers (no "significant", "strong", "confirms").

`cmd_pilot` writes the report next to the figure as `pilot_report.md` and prints its path.

## Acceptance tests
- `test_report_sections_in_order`: headings appear in the order above.
- `test_report_numbers_match_summary`: a known summary value appears formatted as specified.
- `test_unverified_warning`: present when an event lacks `verified: true`, absent when all have it.
- `test_confound_line`: printed only for events with a `confounds` field.
- `test_report_is_deterministic`: two calls with the same inputs produce identical files.
- `test_no_interpretive_words`: the output contains none of "significant", "confirms", "proves".

## Out of scope
PDF or HTML output, deciding go/no-go, editing README.
