# LapGuardian — Master Blueprint

**The master document.** Everything else in `docs/` elaborates on something
here. Owner: project lead. Changes go through an issue, not a direct edit.

Last updated: 2026-11-06. Status: M0 Foundation.

---

## 1. The problem

Most laptops do not die of old age. They die of neglect that nobody warned the
owner about.

### 1.1 Batteries are destroyed by habit, not by use

A lithium-ion cell ages on two clocks at once: cycle ageing from charging and
discharging, and **calendar ageing**, which runs faster the higher the state of
charge and the higher the temperature. A laptop that lives permanently in a
docking station at 100% is on the worst possible setting for calendar ageing,
and it never looks like it is doing anything wrong.

Two years later the owner notices the battery lasts forty minutes. By then the
capacity is gone and cannot be recovered.

### 1.2 Heat accumulates invisibly

Dust blocks the heatsink fins. Thermal paste dries out. The machine responds by
throttling, which is the correct engineering decision and a terrible user
experience. The owner does not see a temperature; they see a laptop that "got
slow", conclude it is old, and replace it.

### 1.3 A permanently full SSD wears faster and runs slower

An SSD at 97% capacity has little spare area for the controller to work with.
Write amplification rises, sustained write performance collapses, and the
drive's endurance is consumed faster. Nothing in the operating system frames
this as a hardware-health issue.

### 1.4 Why this matters beyond one laptop

A laptop retired at three years instead of six doubles its lifetime
manufacturing footprint per year of service, and manufacturing dominates a
laptop's total emissions. Multiply by the number of people who replace a
working machine because "it got slow" and the waste is enormous — and most of
it is avoidable with information the operating system already has but does not
present.

### 1.5 Why existing tools do not solve it

| Category | Why it falls short |
|---|---|
| Vendor utilities (MSI Center, Lenovo Vantage, Dell Power Manager) | One brand only. Often bundled with advertising and account sign-in. Frequently stop receiving updates before the hardware does. |
| Hardware monitors (HWiNFO, CrystalDiskInfo, LibreHardwareMonitor) | Excellent data, aimed at enthusiasts. They display sensors; they do not tell a non-technical owner what to change. |
| Built-in OS tools | `powercfg /batteryreport` produces a report almost nobody knows exists, in a format almost nobody can read. macOS shows a one-word "condition". |
| Cloud-based "PC health" apps | Require an account, upload telemetry, and often monetise the data. The wrong trade for a tool whose whole subject is your own hardware. |

The gap: **no cross-platform, brand-neutral, offline tool that measures these
three things, explains them in plain language, and remembers the trend.**

## 2. What LapGuardian is

A command-line tool that:

1. **Measures** battery wear against original design capacity, cycle count,
   thermals and throttling, and storage pressure — using data the operating
   system already has.
2. **Explains** the readings as advice with a severity level and a concrete
   action, not as a wall of sensor values.
3. **Remembers**, by writing every scan to a local SQLite database, so the
   owner can see degradation over months instead of guessing.
4. **Works on any laptop** — Windows, Linux, macOS, any brand.
5. **Stays private.** No account, no cloud, no telemetry, no network calls at
   all. The data never leaves the machine.

### Target user

- Someone who owns a laptop they would like to keep for six years instead of
  three, and who is comfortable running a command.
- A developer or sysadmin who wants a scriptable health check across a fleet of
  mixed hardware.
- A repair shop or refurbisher assessing a used machine before resale.

### Success criteria

| | Measure |
|---|---|
| Correctness | Battery wear matches the vendor utility on the same machine, within 2 percentage points |
| Coverage | Battery and storage metrics work on every machine tested; thermal coverage is honest about where it does not |
| Honesty | Zero cases of a fabricated reading. Unavailable is always reported as unavailable, with a reason |
| Usability | A non-technical owner can read `lapguardian scan` and know what to do next |
| Privacy | Zero network calls in the shipped binary, verifiable by inspection |
| Portability | CI green on Linux, Windows and macOS across Python 3.10–3.13 |

## 3. Scope

### In scope for v0.1

- Battery health: design vs full-charge capacity, wear percentage, cycle count
- Charge-habit advice (the plugged-in-at-100% problem)
- Thermal readings and throttle detection, where the platform allows it
- Storage: free space, device model, SMART where permitted
- Rule-based advisor with severity and actionable advice
- Local SQLite history and trend reporting
- CLI: `scan`, `report`, `history`, `export`, `config path`
- TOML configuration with documented, tunable thresholds
- Windows, Linux and macOS adapters

### Out of scope — for now

- TUI dashboard (F-12, after v0.1)
- `watch` polling mode (F-11, M5)
- Background daemon or service

### Out of scope — permanently

These are commitments, not a backlog. See [`VISION.md`](VISION.md).

- Any network call, for any reason
- Accounts, device identifiers, telemetry
- A cloud dashboard or fleet-management backend
- A bundled kernel driver for sensor access
- Vendor SDKs that would break brand neutrality
- Writing to the battery, EC, or firmware — LapGuardian **reads and advises**;
  it never changes a hardware setting

The last one deserves emphasis: it is tempting to offer to set a charge
threshold directly. Doing so means writing to vendor-specific embedded
controllers, which risks bricking hardware and requires per-brand code. We tell
the user where the setting is instead.

## 4. Tech stack

| Concern | Choice | Why |
|---|---|---|
| Language | Python 3.10+ | The OS introspection libraries are mature, and contributors with unusual hardware are more likely to be able to run and patch it |
| CLI | Typer | Type-hint-driven, so the CLI signature and the type checker agree |
| Output | Rich | Readable tables that degrade to plain text |
| Metrics | `psutil` + per-OS adapters | `psutil` covers the portable parts; native tools cover the rest |
| Storage | `sqlite3` (stdlib) | Zero dependencies, one file, queryable by the user with any tool |
| Config | `pydantic-settings` + TOML | Validation and documented defaults |
| Packaging | `uv` + `hatchling` | Fast, reproducible, modern |
| Lint + format | `ruff` | One tool, including the security and pathlib rules this project needs |
| Types | `mypy --strict` | `Optional` discipline is load-bearing here, not cosmetic |
| Tests | `pytest` | Markers make hardware-dependent tests skip cleanly |
| CI | GitHub Actions | 3 OS × 4 Python versions |

Runtime dependencies are deliberately few: `typer`, `rich`, `psutil`,
`pydantic`, `pydantic-settings`. A tool that promises no network calls should
have a dependency tree small enough to audit.

## 5. Structure

```text
LapGuardian/
├── AGENTS.md                   # the engineering contract
├── CLAUDE.md CODEX.md CURSOR.md AIDER.md
├── README.md LICENSE CONTRIBUTING.md SECURITY.md
├── CODE_OF_CONDUCT.md CHANGELOG.md
├── .gitignore .gitattributes
├── .aiignore .claudeignore .codexignore
├── .cursorignore .cursorindexingignore .aiderignore
├── pyproject.toml
├── lapguardian.example.toml
├── docs/
│   ├── MASTER_BLUEPRINT.md     # this file
│   ├── VISION.md
│   ├── ARCHITECTURE.md
│   ├── FEATURES.md
│   ├── ROADMAP.md
│   ├── TASKS.md
│   ├── STATUS.md
│   └── HANDOFF.md
├── src/lapguardian/
│   ├── cli.py config.py
│   ├── core/        # domain — knows nothing about any OS
│   ├── platforms/   # the only place OS calls live
│   └── storage/     # SQLite
├── tests/
│   ├── conftest.py
│   └── fixtures/    # golden files per OS
└── .github/
    ├── workflows/ci.yml
    ├── ISSUE_TEMPLATE/
    └── dependabot.yml
```

The layer boundaries are explained in [`ARCHITECTURE.md`](ARCHITECTURE.md) and
enforced in [`AGENTS.md`](../AGENTS.md) section 4.

## 6. Roadmap

| Milestone | Goal |
|---|---|
| **M0 Foundation** | Documentation, scaffold, ignore rules, CI green, repository published |
| **M1 Windows MVP** | `scan` works for real on Windows: battery, thermal, storage, CLI |
| **M2 Cross-platform** | Linux and macOS adapters, golden-file coverage |
| **M3 Persistence** | SQLite history, `history` command, trend analysis |
| **M4 Advisor** | Rule engine, charge-habit advice, severity output |
| **M5 Polish** | Configuration, export formats, `watch` mode |
| **M6 Release v0.1.0** | PyPI, GitHub release, changelog |

Definitions of done are in [`ROADMAP.md`](ROADMAP.md). Current progress is in
[`STATUS.md`](STATUS.md) — that file, and only that file, is the source of
truth for what is finished.

## 7. How the work is divided

Four AI agents and a human lead, with exclusive file ownership to prevent
collisions. See [`HANDOFF.md`](HANDOFF.md).

| Agent | Owns |
|---|---|
| Claude | `core/`, architecture and planning docs, code review |
| Codex | `platforms/`, `tests/` |
| Cursor | `cli.py`, `config.py`, cross-file refactors |
| Aider | Narrow mechanical work anywhere, one concern per commit |

## 8. Principal risks

| Risk | Mitigation |
|---|---|
| Windows CPU temperature is unreachable without a kernel driver | Accepted as a documented limitation. Report unavailable or low-confidence; battery and storage carry the value. See [`ARCHITECTURE.md`](ARCHITECTURE.md) section 9 |
| Sensor coverage across thousands of models is unbounded work | Golden-file testing lets contributors add hardware support without the maintainers owning the machine |
| A plausible-looking fabricated reading corrupts history silently | `MetricUnavailable` is a first-class type, enforced in review; defaults for missing readings are a rejectable offence |
| Scope creep into a fleet-management product | Permanent non-goals in [`VISION.md`](VISION.md) |
| The name `lapguardian` may be taken on PyPI | Must be checked and claimed before M6 |
| Four agents editing the same files | Exclusive ownership in [`HANDOFF.md`](HANDOFF.md); one task, one agent |
