# CODEX.md — Codex in LapGuardian

> **Read [`AGENTS.md`](AGENTS.md) first.** It is the canonical engineering
> contract: stack, commands, layer rules, coding standards, hard rules,
> workflow and commit format. This file only covers what is specific to Codex.
> Nothing here overrides `AGENTS.md`.

## Your role

Codex owns the **platform adapters and the test suite** — the hardest and most
valuable part of this project.

**You own:**

- `src/lapguardian/platforms/` — `windows.py`, `linux.py`, `macos.py`, and the
  `get_provider()` factory.
- `tests/` — including every golden file under `tests/fixtures/`.

**You do not own:** `core/` (Claude), `cli.py` and `config.py` (Cursor).
Read them to understand the contract you implement, but do not edit them. If
the `MetricsProvider` protocol does not fit what the hardware can give you,
**that is a finding worth raising, not something to work around** — open an
issue and assign it to Claude rather than bending the adapter.

## The contract you implement

Every adapter implements `core.provider.MetricsProvider` and returns
`core.models` objects. It never imports from `cli.py` or `storage/`.

The one rule that matters more than any other:

> **A reading you could not take is `MetricUnavailable(reason=...)`. It is
> never `0`, never `-1`, never `None` smuggled in as a number, and never an
> exception that escapes the adapter.**

`0 °C` is a measurement. So is `0 Wh`. If you report either because a parse
failed, you have corrupted the user's long-term trend data in a way that is
very hard to detect later.

## Data sources per platform

### Windows

| Metric | Source | Notes |
|---|---|---|
| Design and full-charge capacity, cycle count | `powercfg /batteryreport /xml /output <tempfile>` | **The file contains the machine name and user profile path.** Write to a private temp dir, parse, `finally: unlink()`. |
| Charge level, AC state, time remaining | `psutil.sensors_battery()` | Reliable. |
| Battery name, chemistry | CIM `Win32_Battery` | |
| CPU temperature | CIM `MSAcpi_ThermalZoneTemperature` in `root\WMI` | **Unreliable on most laptops.** Returns nothing, or a constant, or the chipset rather than the CPU. Values are in tenths of a Kelvin: `celsius = raw / 10 - 273.15`. Report unavailable rather than guessing. |
| Throttling | CIM `Win32_Processor` `CurrentClockSpeed` vs `MaxClockSpeed` | Indirect but better than nothing. |
| Disk free | `shutil.disk_usage()` | Always works. |
| Disk model, SMART | `Get-PhysicalDisk`, `Get-StorageReliabilityCounter` | **Needs Administrator.** Degrade cleanly. |

Invoke PowerShell as an argument list with `-NoProfile -NonInteractive
-OutputFormat Text` (or `ConvertTo-Json` and parse JSON — preferred, it is far
less fragile than parsing table output). **Decode stdout explicitly**; do not
rely on the console code page.

### Linux

| Metric | Source | Notes |
|---|---|---|
| Design and full-charge capacity | `/sys/class/power_supply/BAT*/energy_full_design` and `energy_full` | Some kernels expose `charge_full_design` / `charge_full` in µAh instead of µWh. Handle both; multiply charge by `voltage_min_design` to get energy. |
| Cycle count | `/sys/class/power_supply/BAT*/cycle_count` | **Frequently absent or `0`.** Absent and zero both mean unknown here. |
| Charge level, AC state | `/sys/class/power_supply/BAT*/capacity`, `AC*/online`, or `psutil` | |
| CPU temperature | `psutil.sensors_temperatures()`, else `/sys/class/thermal/thermal_zone*/temp` | Values in millidegrees. Prefer the zone whose `type` is `x86_pkg_temp`, `coretemp` or `cpu-thermal`. |
| Disk free | `shutil.disk_usage()` | |
| SMART | `smartctl --json=c -A <device>` | **Needs root.** Use the JSON output. |

Glob for `BAT*`; do not assume `BAT0`. Multi-battery laptops exist — sum them
and say how many were found.

### macOS

| Metric | Source | Notes |
|---|---|---|
| Design and current capacity, cycle count, condition | `ioreg -rn AppleSmartBattery -a` | `-a` gives a plist; parse it with `plistlib`, not a regex. Keys: `DesignCapacity`, `AppleRawMaxCapacity`, `CycleCount`, `PermanentFailureStatus`. |
| Charge level, AC state | `pmset -g batt` or `psutil` | |
| CPU temperature | `powermetrics --samplers smc` | **Needs sudo.** Optional metric — never prompt. Apple Silicon exposes different SMC keys from Intel. |
| Disk model, free space | `system_profiler SPStorageDataType -json` | |

## Testing: golden files are the deliverable

You cannot test a Dell XPS battery report on a GitHub runner. So:

1. Capture the **real output** of a command on a real machine.
2. **Scrub identifiers** — hostname, username, serial numbers, file paths.
3. Commit it to `tests/fixtures/<windows|linux|macos>/<descriptive-name>.<ext>`.
4. Write a test that feeds the file to the parser and asserts the resulting
   snapshot, field by field.

A parser with a golden file is supported hardware. A parser without one is a
guess. Aim for coverage of the **failure shapes** too: empty output, truncated
XML, a missing `cycle_count` key, a zero design capacity.

Live-hardware tests carry a marker and must **skip**, not fail, elsewhere:

```python
@pytest.mark.windows
@pytest.mark.needs_battery
def test_reads_real_battery() -> None: ...
```

CI runners have no battery. `psutil.sensors_battery()` returns `None` there.

## Subprocess discipline

Repeated here because it is your whole surface area:

- **No `shell=True`.** Argument lists only. Lint rule `S` enforces this.
- **Explicit `timeout` on every call.** A hung vendor tool must not hang the
  CLI.
- **Never interpolate config or sensor output into a command.**
- **Explicit encoding** on `subprocess.run(..., text=True, encoding=...)`.
- **`finally` cleanup** for any file an OS tool creates.
- A non-zero exit code is a `MetricUnavailable`, not an exception.

## Before you commit

```bash
uv run ruff check . && uv run ruff format --check . && uv run mypy src && uv run pytest -v
```

Then update your row in [`docs/STATUS.md`](docs/STATUS.md), and commit as
`feat(platforms): ... (TASK-0NN)`.
