# Task Backlog

Owner: Claude (grooming). Any agent may claim an unclaimed task.

**How to use this file**

1. Find a task whose status is `todo` and whose dependencies are `done`.
2. Change its status to `in-progress` and put your name in Owner.
   **One task, one agent.** Never work on a task someone else has claimed.
3. Write the failing test first.
4. Implement, staying inside the files your role owns — see
   [`HANDOFF.md`](HANDOFF.md).
5. Run the full gate: `ruff check`, `ruff format --check`, `mypy src`, `pytest`.
6. Set the status to `done`, update [`STATUS.md`](STATUS.md), and commit with
   the task ID in the message.

Statuses: `todo` · `in-progress` · `blocked` · `done`

Code stubs in `src/` carry `# TODO(TASK-0NN):` comments pointing back here.

---

## M0 — Foundation

| ID | Task | Owner | Status |
|---|---|---|---|
| TASK-000 | Documentation set, scaffold, ignore rules, CI, publish repository | Claude | done |

---

## M1 — Windows MVP

### TASK-001 — Snapshot models and `MetricUnavailable`

**Owner** Claude · **Status** todo · **File** `core/models.py` · **Feature** F-01, F-03, F-04 · **Depends on** —

Frozen dataclasses with `slots=True`: `SystemInfo`, `BatterySnapshot`,
`ThermalSnapshot`, `StorageSnapshot`, plus `MetricUnavailable`, `Advisory` and
`Severity`.

**Acceptance**

- Every field the hardware might not provide is `Optional`.
- `taken_at` is timezone-aware UTC; a test asserts a naive datetime is rejected.
- Each snapshot carries a `source` string.
- `MetricUnavailable` has `metric`, `reason` and `needs_privileges`.
- No import of `platform`, `sys.platform`, `subprocess` or `psutil`.
- `mypy --strict` clean.

### TASK-002 — `MetricsProvider` protocol

**Owner** Claude · **Status** todo · **File** `core/provider.py` · **Feature** F-09 · **Depends on** TASK-001

The seam between domain and hardware. A `typing.Protocol` with
`system_info()`, `battery()`, `thermal()`, `storage()`.

**Acceptance**

- `core/` contains no implementation of it.
- `FakeProvider` in `tests/conftest.py` satisfies it, verified by mypy.

### TASK-003 — Battery wear and health arithmetic

**Owner** Claude · **Status** todo · **File** `core/health.py` · **Feature** F-01 · **Depends on** TASK-001

`wear_pct = (1 - full_charge / design) * 100`, computed only when both values
are present and design capacity is positive.

**Acceptance**

- Returns `None`, never `0.0`, when an input is missing.
- Wear clamped at `0` when firmware reports `full_charge > design`, with the
  anomaly flagged rather than returned as a negative number.
- Zero or negative design capacity returns `None`, does not raise.
- Multi-battery totals summed correctly.
- Tested with no hardware at all.

### TASK-004 — Provider factory

**Owner** Codex · **Status** todo · **File** `platforms/__init__.py` · **Feature** F-09 · **Depends on** TASK-002

`get_provider()` returning the adapter for the current OS. **The only function
in the codebase that branches on the operating system.**

**Acceptance**

- An unrecognised platform returns a null provider that reports everything
  unavailable with a clear reason, rather than raising.
- Tested by monkeypatching the platform string.

### TASK-005 — Windows battery via `powercfg`

**Owner** Codex · **Status** todo · **File** `platforms/windows.py` · **Feature** F-01 · **Depends on** TASK-002

Parse `powercfg /batteryreport /xml /output <tempfile>` for design capacity,
full-charge capacity and cycle count.

**Acceptance**

- Temp file written to a private directory and **deleted in a `finally`
  block** — a test asserts the file is gone even when parsing raises.
- Argument list, no `shell=True`, explicit timeout, explicit output decoding.
- Non-zero exit or unparseable output becomes `MetricUnavailable` with a
  reason, never an exception reaching the CLI.
- Golden-file tests, including empty output, truncated XML, missing
  `cycle_count`, and zero design capacity.

### TASK-006 — Windows charge state

**Owner** Codex · **Status** todo · **File** `platforms/windows.py` · **Feature** F-01 · **Depends on** TASK-005

Charge percentage, AC state and time remaining via `psutil.sensors_battery()`;
battery identity via CIM `Win32_Battery`.

**Acceptance** `None` from `psutil` (no battery, as on CI runners) becomes
`present=False`, not a crash.

### TASK-007 — Windows thermal (honest best effort)

**Owner** Codex · **Status** todo · **File** `platforms/windows.py` · **Feature** F-03 · **Depends on** TASK-002

Attempt `MSAcpi_ThermalZoneTemperature` in `root\WMI`; infer throttling from
`Win32_Processor` clock speeds.

**Acceptance**

- Unit conversion correct: `celsius = raw / 10 - 273.15`.
- Readings reported with `confidence="unreliable-on-this-platform"`.
- A missing class, an empty result, or an implausible value becomes
  `MetricUnavailable` with a reason the user can understand.
- Inferred throttling is labelled as inferred.
- **Do not attempt to make this reliable.** See
  [`ARCHITECTURE.md`](ARCHITECTURE.md) section 9.

### TASK-008 — Windows storage

**Owner** Codex · **Status** todo · **File** `platforms/windows.py` · **Feature** F-04 · **Depends on** TASK-002

Free space via `shutil.disk_usage()`; device model and SMART via
`Get-PhysicalDisk` and `Get-StorageReliabilityCounter`.

**Acceptance**

- Free space works as a normal user, always.
- SMART without elevation becomes
  `MetricUnavailable(needs_privileges=True)` and the rest still works.
- Fixed drives only; removable and network drives excluded.
- PowerShell invoked with `-NoProfile -NonInteractive` and `ConvertTo-Json`,
  not table parsing.

### TASK-009 — `scan` command

**Owner** Cursor · **Status** todo · **File** `cli.py` · **Feature** F-07 · **Depends on** TASK-003, TASK-005

`lapguardian scan`, `--json`, `--debug`.

**Acceptance**

- Useful output on a fresh install with no config file.
- `--json` puts **only** JSON on stdout; human messages go to stderr.
- `--debug` explains each unavailable metric **without** printing the hostname
  or home directory path.
- Exit `0` when it ran, even with critical findings.
- **No threshold comparisons in this file.** They belong in `core/advisor.py`.

### TASK-010 — Rich rendering

**Owner** Cursor · **Status** todo · **File** `cli.py` · **Feature** F-07 · **Depends on** TASK-009

**Acceptance**

- Readable with `NO_COLOR=1`: severity carried by a word, not only a colour.
- Unavailable metrics show the reason, never a blank or a zero.
- No emoji.
- Correct on an 80-column terminal.

### TASK-011 — Windows golden files

**Owner** Codex · **Status** todo · **Dir** `tests/fixtures/windows/` · **Feature** F-09 · **Depends on** TASK-005

**Acceptance** At least one real battery report, hostname and username scrubbed,
plus the four failure shapes. Each has a test asserting the parsed snapshot
field by field.

---

## M2 — Cross-platform

| ID | Task | Owner | File | Status | Depends on |
|---|---|---|---|---|---|
| TASK-012 | Linux battery from sysfs — handle both µWh (`energy_full*`) and µAh (`charge_full*`), glob `BAT*`, sum multi-battery | Codex | `platforms/linux.py` | todo | TASK-002 |
| TASK-013 | Linux thermal — `psutil.sensors_temperatures()` with `/sys/class/thermal` fallback, prefer `x86_pkg_temp` / `coretemp` / `cpu-thermal` | Codex | `platforms/linux.py` | todo | TASK-002 |
| TASK-014 | Linux storage, optional `smartctl --json=c` | Codex | `platforms/linux.py` | todo | TASK-002 |
| TASK-015 | macOS battery — `ioreg -rn AppleSmartBattery -a` via `plistlib`, **not** a regex | Codex | `platforms/macos.py` | todo | TASK-002 |
| TASK-016 | macOS thermal (`powermetrics`, sudo-optional) and storage (`system_profiler -json`) | Codex | `platforms/macos.py` | todo | TASK-002 |
| TASK-017 | Golden files for Linux and macOS, plus failure shapes | Codex | `tests/fixtures/` | todo | TASK-012, TASK-015 |
| TASK-018 | Null provider for unsupported platforms | Codex | `platforms/__init__.py` | todo | TASK-004 |

---

## M3 — Persistence

| ID | Task | Owner | File | Status | Depends on |
|---|---|---|---|---|---|
| TASK-019 | Connection, `schema.sql` application, `PRAGMA user_version` migration | Claude | `storage/db.py` | todo | TASK-001 |
| TASK-020 | Write a snapshot set, including `unavailable` rows | Claude | `storage/db.py` | todo | TASK-019 |
| TASK-021 | Query history by day range | Claude | `storage/db.py` | todo | TASK-019 |
| TASK-022 | Trend arithmetic over a snapshot series, robust to gaps | Claude | `core/health.py` | todo | TASK-021 |
| TASK-023 | `scan --save` and `history --days N` | Cursor | `cli.py` | todo | TASK-020 |
| TASK-024 | Retention enforced on write; `0` keeps everything | Claude | `storage/db.py` | todo | TASK-020 |

**Cross-cutting acceptance for M3:** a test asserts that no naive datetime can
reach the database. Naive timestamps silently corrupt the trend, which is the
one thing this project offers that the OS does not.

---

## M4 — Advisor

| ID | Task | Owner | File | Status | Depends on |
|---|---|---|---|---|---|
| TASK-025 | Rule-engine skeleton: independent rule functions, each returning zero or one `Advisory` | Claude | `core/advisor.py` | todo | TASK-001 |
| TASK-026 | Battery wear rules against `wear_warn_pct` / `wear_critical_pct` | Claude | `core/advisor.py` | todo | TASK-025 |
| TASK-027 | **Charge-habit rules (F-02)** — sustained high charge on AC, repeated deep discharge, ideal window advice | Claude | `core/advisor.py` | todo | TASK-025, TASK-022 |
| TASK-028 | Thermal rules, including sustained-versus-spike and low-confidence handling | Claude | `core/advisor.py` | todo | TASK-025, TASK-022 |
| TASK-029 | Storage rules on both percentage and absolute free space | Claude | `core/advisor.py` | todo | TASK-025 |
| TASK-030 | `--fail-on warn\|critical` | Cursor | `cli.py` | todo | TASK-025 |

**Cross-cutting acceptance for M4:** no advisory is ever produced from a
`MetricUnavailable`; every rule has a test for the case where it correctly says
nothing; every advisory names a real action and never offers to change a
hardware setting.

---

## M5 — Polish

| ID | Task | Owner | File | Status | Depends on |
|---|---|---|---|---|---|
| TASK-031 | Settings model, TOML source, documented defaults | Cursor | `config.py` | todo | — |
| TASK-032 | `config path` command, plus a test asserting `lapguardian.example.toml` matches the model | Cursor | `cli.py` | todo | TASK-031 |
| TASK-033 | `export --format {json,csv,markdown}` with identifier redaction on by default | Cursor | `cli.py` | todo | TASK-021 |
| TASK-034 | `watch --interval N`, foreground, clean Ctrl-C, no partial writes | Cursor | `cli.py` | todo | TASK-009 |

---

## M6 — Release

| ID | Task | Owner | Status | Notes |
|---|---|---|---|---|
| TASK-035 | **Check and claim the name `lapguardian` on PyPI** | human lead | todo | Do this early. The name can be taken at any time and the whole release depends on it. |
| TASK-036 | Complete `CHANGELOG.md`, bump version, tag, publish, verify `uv tool install` on all three platforms | human lead | todo | Depends on TASK-035 |

---

## Housekeeping and chores

| ID | Task | Owner | Status |
|---|---|---|---|
| TASK-040 | Add type hints anywhere `mypy --strict` still needs them | Aider | todo |
| TASK-041 | Google-style docstrings on all public API | Aider | todo |
| TASK-042 | Audit for `os.path` usage and convert to `pathlib` | Aider | todo |
| TASK-043 | Audit for naive `datetime.now()` and convert to `datetime.now(tz=timezone.utc)` | Aider | todo |
| TASK-044 | Record a coverage baseline and add it to CI output | Codex | todo |

Aider: remember that these are mechanical. If a type hint reveals a bug, file
an issue — do not fix the bug in a hint commit, and never silence mypy with a
default value for a missing reading.
