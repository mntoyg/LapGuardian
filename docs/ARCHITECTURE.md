# Architecture

**Status:** authoritative for implementation. Owner: Claude.
Last updated: 2026-11-06.

This document describes how LapGuardian is put together and, more importantly,
*why* the boundaries are where they are. Read [`AGENTS.md`](../AGENTS.md)
section 4 for the enforceable version of the layer rules.

---

## 1. The design problem

LapGuardian has one genuinely hard constraint: **the hardware is unreliable and
inconsistent, and the maintainers own almost none of it.**

A battery report on a 2019 ThinkPad, a 2024 MacBook Air and a Windows tablet
look nothing alike. Some firmware reports cycle count; most Linux laptops do
not. CPU temperature on Windows is effectively unavailable without a kernel
driver. SMART needs root everywhere.

Everything below follows from that. The architecture exists to keep the mess
in one place, behind one interface, so that the part of the program that holds
the actual value — turning numbers into advice — can be written and tested with
no hardware at all.

## 2. Layers

```text
                        ┌─────────────────────────┐
                        │        cli.py           │  presentation
                        │   Typer + Rich          │
                        └───────┬─────────┬───────┘
                                │         │
                   ┌────────────▼──┐   ┌──▼────────────┐
                   │     core/     │   │   storage/    │  persistence
                   │  domain logic │   │    SQLite     │
                   └───────▲───────┘   └───────────────┘
                           │
                 implements│MetricsProvider
                           │
                   ┌───────┴───────┐
                   │  platforms/   │  hardware access
                   │ win/linux/mac │
                   └───────────────┘
```

Dependency direction is one-way and `core/` is at the bottom:

- `cli` → `core`, `cli` → `storage`, `cli` → `platforms` (factory only)
- `platforms` → `core` (for the models and the protocol it implements)
- `core` → **nothing**

### Why `core` depends on nothing

`core/` must not import `platform`, `sys.platform`, `subprocess`, `psutil`, or
anything under `platforms/`. It defines `MetricsProvider` as a `Protocol` and
accepts any object satisfying it.

The payoff is that the entire advisor rule engine — the part users actually
care about — is tested by handing it a `FakeProvider` with whatever readings
the test needs. No mocking of `subprocess`, no hardware, no platform markers,
runs identically on every CI runner.

### The seam

```python
# src/lapguardian/core/provider.py
class MetricsProvider(Protocol):
    """Reads hardware metrics for one host."""

    def system_info(self) -> SystemInfo: ...
    def battery(self) -> BatterySnapshot | MetricUnavailable: ...
    def thermal(self) -> ThermalSnapshot | MetricUnavailable: ...
    def storage(self) -> list[StorageSnapshot]: ...
```

`platforms/__init__.py` exposes a single factory:

```python
def get_provider() -> MetricsProvider:
    """Return the metrics provider for the current operating system."""
```

This is the only function in the codebase that branches on the operating
system. Anything else that needs to know what OS it is running on is a bug.

## 3. Modules

| Module | Responsibility | Must not |
|---|---|---|
| `cli.py` | Parse arguments, call `core`, render with Rich | Contain any threshold comparison or health logic |
| `config.py` | Settings model, TOML loading, documented defaults | Read anything outside the app-data dir |
| `core/models.py` | `SystemInfo`, `BatterySnapshot`, `ThermalSnapshot`, `StorageSnapshot`, `MetricUnavailable`, `Advisory`, `Severity` | Import anything OS-specific |
| `core/provider.py` | The `MetricsProvider` protocol | Contain an implementation |
| `core/health.py` | Wear, health score, trend arithmetic | Know where numbers came from |
| `core/advisor.py` | Rule engine producing `Advisory` objects | Format output |
| `platforms/windows.py` | Windows adapter | Import `cli` or `storage` |
| `platforms/linux.py` | Linux adapter | Import `cli` or `storage` |
| `platforms/macos.py` | macOS adapter | Import `cli` or `storage` |
| `storage/db.py` | SQLite connection, migration, read and write | Contain health logic |
| `storage/schema.sql` | The schema, as DDL | — |

## 4. Data flow

A `lapguardian scan --save` runs as:

```text
 1. cli        parse args, load Settings from TOML + defaults
 2. platforms  get_provider()                 -> concrete adapter
 3. adapter    read sensors                   -> *Snapshot | MetricUnavailable
 4. core       health.compute(snapshots)      -> derived metrics (wear %, etc.)
 5. core       advisor.evaluate(metrics, cfg) -> list[Advisory]
 6. storage    db.save(snapshot_set)          -> rows in SQLite
 7. cli        render(snapshots, advisories)  -> Rich output / JSON
```

Steps 4 and 5 are pure functions of their inputs. That is deliberate: they are
the most valuable and most frequently changed code in the project, so they are
the easiest to test.

## 5. Domain model

Snapshots are frozen dataclasses. Every field that the hardware might not
provide is `Optional`.

```python
@dataclass(frozen=True, slots=True)
class BatterySnapshot:
    """A single reading of battery state."""

    taken_at: datetime  # always timezone-aware, UTC
    present: bool
    charge_pct: float | None
    on_ac_power: bool | None
    design_capacity_wh: float | None
    full_charge_capacity_wh: float | None
    cycle_count: int | None
    battery_count: int  # multi-battery laptops exist
    source: str  # e.g. "powercfg-xml", "sysfs"
```

`source` is recorded because the same field read two different ways is not the
same quality of measurement, and that matters when interpreting a long history.

### `MetricUnavailable`

```python
@dataclass(frozen=True, slots=True)
class MetricUnavailable:
    """A metric that could not be read, and why."""

    metric: str
    reason: str  # shown to the user verbatim
    needs_privileges: bool = False
```

**This is the single most important type in the codebase.** The rule it exists
to enforce:

> A reading that was not taken is `MetricUnavailable`. It is never `0`, never
> `-1`, and never a default.

`0 °C` and `0 Wh` are measurements. Substituting either for a failed parse
silently corrupts the user's long-term trend — the one thing LapGuardian offers
that the operating system does not — and the corruption is nearly undetectable
after the fact.

### Derived metrics

```text
battery_wear_pct = (1 - full_charge_capacity / design_capacity) * 100
```

Computed only when both values are present and design capacity is positive.
Some firmware reports `full_charge > design` after a recalibration; clamp the
wear at `0` and record that it happened rather than reporting a negative
number.

## 6. Advisories

```python
class Severity(StrEnum):
    OK = "ok"
    INFO = "info"
    WARN = "warn"
    CRITICAL = "critical"


@dataclass(frozen=True, slots=True)
class Advisory:
    """One piece of actionable advice."""

    severity: Severity
    metric: str
    cause: str  # names the actual measurement
    action: str  # something the owner can do today
    confidence: str  # "measured" | "estimated" | "unreliable-on-this-platform"
```

The rule engine in `core/advisor.py` is a list of small, independently testable
rule functions, each taking the computed metrics and the settings and returning
zero or one `Advisory`. Adding a rule must not require touching any other rule.

`confidence` exists because of the Windows thermal problem (section 9). An
advisory built on an unreliable sensor must say so rather than presenting a
guess as a measurement.

### Quality bar

Raw numbers are not the product. Anyone can read a sensor. The value is advice
a non-technical owner can act on today.

- **Good:** *"Your battery has lost 23% of its original capacity. Set a charge
  limit of 80% in your vendor utility or BIOS if one is available."*
- **Bad:** *"Battery wear 23%. Consider battery maintenance."* — no action, and
  "maintenance" means nothing to the reader.

## 7. Platform data sources

Full details, including the exact keys and unit conversions, are in
[`CODEX.md`](../CODEX.md). Summary:

### Windows

| Metric | Source |
|---|---|
| Design / full-charge capacity, cycle count | `powercfg /batteryreport /xml /output <tempfile>` |
| Charge level, AC state | `psutil.sensors_battery()` |
| Battery identity, chemistry | CIM `Win32_Battery` |
| CPU temperature | CIM `MSAcpi_ThermalZoneTemperature` (`root\WMI`) — see section 9 |
| Throttling | CIM `Win32_Processor`: `CurrentClockSpeed` vs `MaxClockSpeed` |
| Disk free | `shutil.disk_usage()` |
| Disk model, SMART | `Get-PhysicalDisk`, `Get-StorageReliabilityCounter` (Administrator) |

### Linux

| Metric | Source |
|---|---|
| Design / full-charge capacity | `/sys/class/power_supply/BAT*/energy_full_design`, `energy_full` (µWh) or `charge_full_design`, `charge_full` (µAh) |
| Cycle count | `/sys/class/power_supply/BAT*/cycle_count` — often absent |
| Charge level, AC state | `.../capacity`, `.../AC*/online` |
| CPU temperature | `psutil.sensors_temperatures()`, else `/sys/class/thermal/thermal_zone*/temp` (millidegrees) |
| Disk free | `shutil.disk_usage()` |
| SMART | `smartctl --json=c -A <device>` (root) |

Glob `BAT*`; never assume `BAT0`. Multi-battery laptops exist.

### macOS

| Metric | Source |
|---|---|
| Design / current capacity, cycle count, condition | `ioreg -rn AppleSmartBattery -a`, parsed with `plistlib` |
| Charge level, AC state | `pmset -g batt` or `psutil` |
| CPU temperature | `powermetrics --samplers smc` (sudo, optional) |
| Disk model, free space | `system_profiler SPStorageDataType -json` |

## 8. Privilege boundary

**LapGuardian never requires elevation to run.** This is a hard rule, not a
preference.

| Metric | Normal user | Elevated |
|---|---|---|
| Battery capacity, cycles, charge | yes | — |
| Disk free space | yes | — |
| CPU temperature (Linux, macOS Intel) | yes | — |
| CPU temperature (Windows) | partial, unreliable | still unreliable |
| CPU temperature (macOS `powermetrics`) | no | yes |
| SMART attributes | no | yes |

Without elevation, elevated metrics are reported as
`MetricUnavailable(needs_privileges=True)` with a message explaining what the
user would gain by running elevated. The tool never prompts for elevation and
never re-launches itself elevated.

## 9. Known limitations

These are design constraints, not bugs to be filed. They are written down so
nobody rediscovers them the expensive way.

### Windows CPU temperature is effectively unavailable

`MSAcpi_ThermalZoneTemperature` is the only CPU temperature source reachable
without a kernel driver, and on most consumer laptops it either does not exist,
returns a constant, or reports a chipset zone rather than the CPU package.
Vendors expose real sensors through proprietary EC interfaces that require a
signed driver.

Real coverage would mean bundling something like LibreHardwareMonitor's driver,
which is a large change in the project's trust and installation story.
**That is out of scope.** On Windows, LapGuardian reports thermal readings with
`confidence="unreliable-on-this-platform"`, or unavailable, and says why.

Battery and storage advice — the larger share of the value — are unaffected.

### SMART needs elevation everywhere

Degrade to free-space-only. A full disk is the more common and more actionable
problem anyway.

### `cycle_count` is frequently absent

Especially on Linux. It is `int | None`, and both a missing file and a reported
`0` mean "unknown" — no shipped battery has zero cycles by the time a user runs
this.

### `powercfg /batteryreport` writes to disk

The report contains the machine name and user profile path. Write to a private
temp directory, parse, and delete in a `finally` block. The filename patterns
are also in `.gitignore` and every AI ignore file as a second line of defence.

### CI runners have no battery

`psutil.sensors_battery()` returns `None` on GitHub Actions runners. Tests
needing real hardware carry a marker and must skip, not fail.

## 10. Storage

SQLite via the standard library. One file, in the platform application-data
directory. Schema lives in `storage/schema.sql`; `storage/db.py` applies it and
handles migration via `PRAGMA user_version`.

```text
snapshots         id, taken_at (UTC ISO-8601), app_version, os_name, os_version,
                  machine_model, cpu_model
battery_metrics   snapshot_id FK, present, charge_pct, on_ac_power,
                  design_capacity_wh, full_charge_capacity_wh, cycle_count,
                  battery_count, source
thermal_metrics   snapshot_id FK, sensor_label, temp_c, is_throttling, source
storage_metrics   snapshot_id FK, mount, device_model, total_bytes, free_bytes,
                  smart_ok, source
advisories        snapshot_id FK, severity, metric, cause, action, confidence
unavailable       snapshot_id FK, metric, reason, needs_privileges
```

Notes on the design:

- **`unavailable` is a real table.** Knowing that a metric stopped being
  readable is itself a signal, and it keeps missing data out of the metric
  tables where it could be mistaken for a reading.
- **Timestamps are stored as UTC ISO-8601 text.** SQLite has no date type;
  text sorts correctly and survives timezone changes. Naive timestamps would
  silently break the trend, which is why lint rule `DTZ` is enabled.
- Indexes on `snapshots.taken_at` and on each `snapshot_id` foreign key.
- Retention is enforced on write, controlled by `[history] retention_days`.

## 11. Error handling

- Adapters catch everything at their own boundary and return
  `MetricUnavailable`. Nothing from `subprocess`, CIM or `/sys` reaches the CLI.
- Every subprocess call has an explicit timeout. A hung vendor tool must not
  hang the CLI.
- Configuration errors are reported with the file path and the offending key,
  and the tool continues with defaults where that is safe.
- Exit code `0` means LapGuardian ran, even if it found critical problems.
  Non-zero means LapGuardian itself failed. `--fail-on warn|critical` exists
  for scripting.

## 12. Testing strategy

| Layer | How it is tested |
|---|---|
| `core/` | Pure unit tests with `FakeProvider` from `tests/conftest.py`. No hardware, no mocking of `subprocess`. Runs on every runner. |
| `platforms/` parsers | **Golden files** in `tests/fixtures/<os>/`: real captured output, identifiers scrubbed, committed, parsed, asserted field by field. Includes failure shapes — empty output, truncated XML, missing keys, zero design capacity. |
| `platforms/` live reads | Marked `windows` / `linux` / `macos` / `needs_battery` / `needs_admin`. **Skip** elsewhere, never fail. |
| `storage/` | Against an in-memory or `tmp_path` database. |
| `cli.py` | Typer's `CliRunner` with a fake provider injected. |

A parser with a golden file is supported hardware. A parser without one is a
guess. Golden files from unusual machines are among the most valuable
contributions this project can receive.

## 13. Things deliberately not in the design

- **No daemon or background service in v0.1.** `lapguardian scan --save` from
  the user's own scheduler (Task Scheduler, cron, launchd) does the same job
  without asking for trust we have not earned.
- **No GUI.** A TUI dashboard is F-12, after v0.1.
- **No vendor SDKs.** They are per-brand, often closed, and would break the
  "works on any laptop" promise.
- **No kernel driver.** See section 9.
- **No network layer at all.** See [`SECURITY.md`](../SECURITY.md).
