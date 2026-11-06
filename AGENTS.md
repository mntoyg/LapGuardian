# AGENTS.md — Engineering Contract for LapGuardian

**This is the canonical contract for every contributor, human or AI.**
`CLAUDE.md`, `CODEX.md`, `CURSOR.md` and `AIDER.md` are thin role files that
point back here. If you are an agent and you read only one file, read this one.

Do not duplicate the rules below into another file. When something changes, it
changes here, once.

---

## 1. What this project is

LapGuardian is an offline, privacy-first CLI that measures laptop **battery
wear**, **thermals** and **storage pressure**, turns the readings into
actionable advice, and logs them locally so the owner can see long-term trends.
The goal is to keep working laptops out of landfill.

Read [`docs/MASTER_BLUEPRINT.md`](docs/MASTER_BLUEPRINT.md) for the why, and
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for the how, before your first
change.

## 2. Stack

| Concern | Choice |
|---|---|
| Language | Python 3.10+ (must work on 3.10 through 3.13) |
| CLI | Typer + Rich |
| Metrics | `psutil` plus per-OS adapters that shell out to native tools |
| Storage | SQLite via the standard library `sqlite3` |
| Config | `pydantic-settings` + TOML |
| Packaging | `uv` + `hatchling` |
| Lint / format | `ruff` (both) |
| Types | `mypy --strict` |
| Tests | `pytest` |
| CI | GitHub Actions, 3 OS × 4 Python versions |

Do not introduce a new runtime dependency without an issue and a reason. The
dependency list is short on purpose.

## 3. Commands

Everything runs through `uv`. Never call `pip` or a global `python`.

```bash
uv sync --extra dev          # set up or refresh the environment
uv run lapguardian --help    # run the CLI
uv run ruff check .          # lint
uv run ruff format .         # format (use --check in CI)
uv run mypy src              # type check
uv run pytest -v             # tests
uv run pytest --cov          # tests with coverage
```

**All four of `ruff check`, `ruff format --check`, `mypy src` and `pytest` must
pass before you commit.** Do not claim a task is done without running them and
seeing the output.

## 4. Layout and layer rules

```text
src/lapguardian/
├── cli.py          # Typer commands. Presentation only.
├── config.py       # Settings model, TOML loading, threshold defaults.
├── core/           # Domain. Knows NOTHING about any operating system.
│   ├── models.py   # Snapshot dataclasses + MetricUnavailable
│   ├── provider.py # MetricsProvider Protocol — the seam
│   ├── health.py   # Wear and health arithmetic
│   └── advisor.py  # Rule engine producing Advisory objects
├── platforms/      # One adapter per OS. The ONLY place OS calls live.
│   ├── windows.py
│   ├── linux.py
│   └── macos.py
└── storage/        # SQLite persistence.
    ├── schema.sql
    └── db.py
```

The layer rules are not stylistic. They are what makes this project testable
on hardware none of us owns:

1. **`core/` must not import `platform`, `sys.platform`, `subprocess`,
   `psutil`, or anything under `platforms/`.** It depends only on the
   `MetricsProvider` protocol it defines itself.
2. **`platforms/` must not import from `cli.py` or `storage/`.** An adapter
   reads sensors and returns `core.models` objects. That is all it does.
3. **`cli.py` contains no business logic.** It parses arguments, calls `core`,
   and renders. If you are writing an `if` about battery health in `cli.py`,
   it belongs in `core/advisor.py`.
4. **Only `storage/db.py` touches SQLite.**
5. Dependency direction is one-way: `cli` → `core` ← `platforms`, and
   `cli` → `storage`. `core` is at the bottom and depends on nothing.

## 5. Coding standards

- **Type hints are mandatory**, on every function, parameter and return.
  `mypy --strict` is enforced, including in tests you add type hints to.
- **Google-style docstrings** on every public module, class and function.
  `ruff` enforces this via pydocstyle.
- **Line length 100.**
- **`pathlib`, never `os.path`.** Enforced by lint rule `PTH`.
- **Never `print()`.** Use the Rich console from the CLI layer, or return data.
  Enforced by lint rule `T20`.
- **Timezone-aware datetimes only.** `datetime.now(tz=timezone.utc)`, never
  `datetime.now()`. Enforced by lint rule `DTZ`. Naive timestamps corrupt the
  history trend silently, which is the worst kind of bug here.
- **Dataclasses for snapshots**, pydantic for config and for anything parsed
  from user input.

### Subprocess rules

Shelling out to OS tools is unavoidable in `platforms/`. It is also the main
attack surface, so it is tightly constrained:

- **`shell=True` is forbidden.** Build an argument list.
- **Every call needs an explicit `timeout`.** A hung vendor tool must not hang
  the CLI.
- **Resolve executables from a known absolute path** where possible, rather
  than relying on `PATH`.
- **Never interpolate configuration or sensor output into a command.**
- **Treat all output as untrusted text.** Parse defensively; a surprising
  format is a `MetricUnavailable`, not an exception that escapes.
- **Clean up files OS tools create**, in a `finally` block. See the
  `powercfg /batteryreport` note in [`SECURITY.md`](SECURITY.md).

### Error handling

- A metric that cannot be read returns **`MetricUnavailable(reason=...)`**.
- **Never substitute a default for a missing reading.** `0 °C` and `0 Wh` are
  measurements. If you did not measure it, say so.
- Exceptions from adapters are caught at the adapter boundary and converted.
  Nothing from `subprocess`, `WMI` or `/sys` should surface in the CLI.
- The CLI exits `0` when it ran, even if it found problems. Non-zero means
  LapGuardian itself failed. Use `--fail-on warn|critical` for scripting.

## 6. Hard rules — non-negotiable

These are the project's promise to its users. Breaking one is grounds for
rejecting a change regardless of how good the rest of it is.

1. **No network calls.** No update check, no analytics, no crash reporting, no
   telemetry. If you find yourself importing `requests`, `httpx`, `urllib`, or
   `socket`, stop.
2. **No accounts, no identifiers, no device IDs.**
3. **Never fabricate a reading.** See error handling above.
4. **Never require elevation.** Administrator or root unlocks *extra* metrics.
   The tool must be fully useful without it, and must never silently re-launch
   itself elevated.
5. **Never write outside the platform application-data directory** or a private
   temp dir, without the user asking.
6. **Never commit real machine data.** The local database, raw battery reports,
   and anything with a hostname or user path stay out of the repository. They
   are already in `.gitignore` and in every AI ignore file — do not add
   exceptions.

## 7. Testing

- `core/` is tested with the **fake provider** fixture in `tests/conftest.py`.
  No hardware, no mocking of `subprocess`.
- `platforms/` parsers are tested with **golden files** in
  `tests/fixtures/<os>/`. Capture real output, scrub identifiers, commit it,
  assert the parsed snapshot. This is how the project supports hardware the
  maintainers do not own.
- Tests that need real hardware carry a marker and **skip** elsewhere:
  `windows`, `linux`, `macos`, `needs_battery`, `needs_admin`.
  CI runners have no battery — a test that fails there instead of skipping is a
  broken test.
- **Write the test first.** For a bug, write the failing test that reproduces
  it before you fix anything.

## 8. Workflow — follow this every time

1. **Read** this file, then [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).
2. **Claim a task** from [`docs/TASKS.md`](docs/TASKS.md): set its status to
   `in-progress` and put your agent name in the Owner column. One task, one
   agent. Never work on a task someone else has claimed.
3. **Write the failing test.**
4. **Implement**, staying inside the files your role owns (see
   [`docs/HANDOFF.md`](docs/HANDOFF.md)).
5. **Run the full gate** from section 3 and read the actual output.
6. **Update [`docs/STATUS.md`](docs/STATUS.md)** — mark the task done, refresh
   the milestone percentage, update the date.
7. **Commit** using the format in section 9.

## 9. Commits

[Conventional Commits](https://www.conventionalcommits.org/) with the task ID
in parentheses at the end:

```text
feat(core): add battery wear calculation (TASK-003)
fix(platforms): handle missing cycle_count on Linux (TASK-011)
test(platforms): add golden file for ThinkPad T14 battery report (TASK-012)
docs(architecture): document the privilege boundary
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `style`, `chore`,
`build`, `ci`, `revert`.
Scopes: `core`, `platforms`, `storage`, `cli`, `config`, `docs`, `ci`.

**Commit messages, code, comments and docstrings are written in English.**
Issue discussion may be in any language.

## 10. Do not touch

- `LICENSE`
- `.gitignore`, `.gitattributes`, and the AI ignore files — unless the task is
  specifically about them
- Another agent's in-progress task
- `docs/MASTER_BLUEPRINT.md` and `docs/VISION.md` — these are owned by the
  project lead. Propose changes in an issue.
- `docs/STATUS.md` — edit it, but only one agent at a time, and only to record
  your own task. Never rewrite someone else's row.

## 11. Known traps

Things that have already been thought about. Do not rediscover them the hard
way:

- **Windows CPU temperature via `MSAcpi_ThermalZoneTemperature` is
  unreliable.** Many laptops return nothing or a constant. A kernel driver
  would be needed for real coverage and that is out of scope. Report
  unavailable; do not guess. See
  [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).
- **`powercfg /batteryreport` writes a file containing the machine name and
  user path.** Temp dir, parse, delete in `finally`.
- **SMART needs elevation on every OS.** Degrade to free-space-only.
- **CI runners have no battery.** `psutil.sensors_battery()` returns `None`.
- **`cycle_count` is absent on a lot of firmware**, including most Linux
  laptops. `Optional`, not `int`.
- **Windows console encoding.** Decode subprocess output explicitly; do not
  rely on the locale default.
