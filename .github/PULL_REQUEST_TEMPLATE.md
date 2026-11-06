## What this changes

<!-- One or two sentences. -->

**Task:** TASK-0NN <!-- from docs/TASKS.md; write "none" for a drive-by docs fix -->
**Feature:** F-NN <!-- from docs/FEATURES.md, if applicable -->

## Checklist

### The gate

Run these and confirm you read the output. "It should pass" is not a result.

- [ ] `uv run ruff check .`
- [ ] `uv run ruff format --check .`
- [ ] `uv run mypy src`
- [ ] `uv run pytest -v`

### Correctness

- [ ] There is a test, and it tests behaviour rather than implementation
- [ ] For a bug fix: the test failed before the fix and passes after
- [ ] Test count did not drop, and nothing newly skips that was running before

### The hard rules (`AGENTS.md` section 6)

- [ ] No network imports or calls added
- [ ] No telemetry, accounts or identifiers added
- [ ] **No missing reading turned into a default.** A metric that could not be
      read is `MetricUnavailable`, never `0`, `-1` or a fallback
- [ ] Still fully usable without Administrator or root
- [ ] No machine-identifying data committed — no local database, no raw battery
      report, no hostname or user path in a fixture

### Layer rules (`AGENTS.md` section 4)

- [ ] `core/` imports nothing OS-specific
- [ ] `platforms/` does not import `cli` or `storage`
- [ ] No threshold comparison or health logic in `cli.py`

### For changes under `platforms/`

- [ ] No `shell=True`; arguments passed as a list
- [ ] Explicit `timeout` on every subprocess call
- [ ] Output decoded explicitly, not left to the locale
- [ ] Any file an OS tool created is deleted in a `finally` block
- [ ] A golden file is committed, with identifiers scrubbed

### Housekeeping

- [ ] `docs/STATUS.md` updated in this PR
- [ ] `lapguardian.example.toml` updated, if `config.py` changed
- [ ] I stayed inside the files my role owns (`docs/HANDOFF.md`)

## Notes for the reviewer

<!-- Anything you are unsure about, or decisions worth a second opinion. -->
