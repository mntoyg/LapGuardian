# CURSOR.md — Cursor in LapGuardian

> **Read [`AGENTS.md`](AGENTS.md) first.** It is the canonical engineering
> contract: stack, commands, layer rules, coding standards, hard rules,
> workflow and commit format. This file only covers what is specific to Cursor.
> Nothing here overrides `AGENTS.md`.

## Your role

Cursor owns the **user-facing surface and cross-file refactors**.

**You own:**

- `src/lapguardian/cli.py` — Typer commands, arguments, Rich rendering.
- `src/lapguardian/config.py` — the settings model, TOML loading, defaults.
- `lapguardian.example.toml` — kept in sync with `config.py`.
- Multi-file mechanical refactors, when a task assigns one.

**You do not own:** `core/` (Claude), `platforms/` and `tests/` (Codex).

## The one rule for `cli.py`

**No business logic.** `cli.py` parses arguments, calls into `core`, and
renders the result. If you are writing a comparison about battery health,
temperature or disk thresholds in the CLI layer, it belongs in
`core/advisor.py` — raise it with Claude instead of putting it here.

A good test of this: if `cli.py` grows an `if` that would need to change when
a threshold changes, the logic is in the wrong file.

## CLI design

Target commands (see [`docs/FEATURES.md`](docs/FEATURES.md) F-07):

| Command | Purpose |
|---|---|
| `lapguardian scan` | One-off health check, human readable |
| `lapguardian scan --save` | Also append a snapshot to the local database |
| `lapguardian scan --json` | Machine-readable output |
| `lapguardian report` | Full report including history trend |
| `lapguardian history --days N` | Trend over time |
| `lapguardian export --format {json,csv,markdown}` | Write a report to a file |
| `lapguardian watch` | Polling loop (F-11, later) |
| `lapguardian config path` | Print where the config file is expected |

Conventions:

- `--json` output goes to **stdout only**, with nothing else on stdout, so it
  can be piped. Human messages and warnings go to stderr.
- `--debug` prints what was attempted and why a metric was unavailable. It is
  what bug reports will contain, so it must be useful and must not include
  the user's hostname or home path.
- `--no-color` and `NO_COLOR` are both honoured. Rich handles most of this;
  verify it rather than assuming.
- Exit code `0` means LapGuardian ran, even if it found problems. Non-zero
  means LapGuardian itself failed. `--fail-on warn|critical` exists for
  scripting.

## Rendering

- Rich tables and panels, but **readable without colour**. Severity must be
  carried by a word or symbol as well as a colour — a red cell is invisible to
  a colour-blind user and to a log file.
- A metric that is unavailable shows the **reason**, not a blank or a zero.
  `Thermals  unavailable  (no readable sensor on this machine)` is the correct
  shape.
- No emoji in output. Plenty of Windows terminals still mangle them.
- Keep the default output short enough to read at a glance. Detail belongs
  behind `report` and `--debug`.
- No `print()` — lint rule `T20` will reject it. Use the Rich console.

## `config.py`

- `pydantic-settings` with a TOML source. Every field has a default, so the
  tool works with no config file at all.
- Every default must be **defensible and documented** in
  `lapguardian.example.toml`. Do not invent a threshold; if you are unsure
  what a reasonable value is, ask in the task rather than guessing.
- **When you change a field, update `lapguardian.example.toml` in the same
  commit.** A drifted example file is worse than none.
- Config paths come from the platform application-data directory. Never write
  config or data next to the executable or into the repository.
- `[privacy] allow_network = false` is a tripwire, not a feature switch. Do not
  add code that reads it as permission to make a request.

## Refactors

When a task assigns you a cross-file refactor:

- Keep it **mechanical**. A rename, a move, an extraction. If it changes
  behaviour, it is not a refactor — split it into two commits.
- Do not widen the diff with unrelated cleanups you noticed on the way. File
  an issue instead.
- Run the full gate before and after, and confirm the test count did not drop.

## Before you commit

```bash
uv run ruff check . && uv run ruff format --check . && uv run mypy src && uv run pytest -v
```

Then update your row in [`docs/STATUS.md`](docs/STATUS.md), and commit as
`feat(cli): ... (TASK-0NN)` or `feat(config): ... (TASK-0NN)`.
