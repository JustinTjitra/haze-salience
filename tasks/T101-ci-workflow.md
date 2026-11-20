# T101 CI workflow

Tier: haiku · Depends: none

## Goal
Every push and pull request runs lint and tests on GitHub, so a broken commit is visible at once.

## Files
- `.github/workflows/ci.yml` (new)
- `tests/test_ci_config.py` (new)

## Spec
- Triggers: `push` to `main`, and `pull_request`.
- One job on `ubuntu-latest`: check out the repo, install uv with the `astral-sh/setup-uv` action
  (pin a major version tag), then run `uv sync`, `make lint`, `make test`, each as its own step.
- No secrets, no caching beyond what the uv action does by default, no matrix.

## Acceptance tests
- `test_ci_runs_lint_and_tests`: load the YAML with `yaml.safe_load`; assert the job's steps
  include one whose `run` is `make lint` and one whose `run` is `make test`, and that `uv sync`
  runs before both.
- `test_ci_triggers`: the workflow triggers on `pull_request` and on `push` to `main`. Note that
  PyYAML parses the key `on` as the boolean `True`; handle that in the test.

## Out of scope
Badges, README edits, releases, coverage upload.

## Planner note
If the push is rejected because the token may not write workflow files, set this task to `waiting`
(Needs: owner adds the file through the GitHub web UI) and paste the file content into the log.
