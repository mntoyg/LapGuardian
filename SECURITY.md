# Security and Privacy Policy

LapGuardian reads hardware sensors on a personal computer. That makes it both
a privacy-sensitive tool and a program that touches operating-system
internals. This document states exactly what it does and does not do.

## Supported versions

| Version | Supported |
|---|---|
| `main` (pre-release) | yes |
| `0.1.x` | once released |

LapGuardian has not had a tagged release yet. Until v0.1.0, security fixes land
on `main`.

## Reporting a vulnerability

**Do not open a public GitHub issue for a security problem.**

Use GitHub private reporting: go to the
[Security tab](https://github.com/mntoyg/LapGuardian/security/advisories/new)
and open a draft advisory. Include the affected version, your operating system,
reproduction steps, and the impact as you see it.

Expect an acknowledgement within 7 days. We aim to ship a fix, or explain why
the behaviour is intended, within 30 days. We will credit you in the advisory
and the changelog unless you ask us not to.

## Privacy stance

This is a commitment, not a configuration default.

### LapGuardian does not

- Make **any** network request. There is no update check, no analytics, no
  crash reporting, no license check. The project has no server.
- Create an account, a device ID, an install ID, or any other identifier.
- Send your data anywhere, including to the maintainers.
- Read your files, your browser data, your clipboard, or your processes beyond
  what is needed for the metrics listed below.

The `[privacy] allow_network = false` key in the config exists as a tripwire:
it is there so that a future contributor cannot quietly introduce a network
call without a visible, reviewable flag.

### Where your data lives

All data stays in the local SQLite database in your own platform
application-data directory:

| OS | Default location |
|---|---|
| Windows | `%LOCALAPPDATA%\LapGuardian\history.db` |
| Linux | `$XDG_DATA_HOME/lapguardian/history.db`, else `~/.local/share/lapguardian/history.db` |
| macOS | `~/Library/Application Support/LapGuardian/history.db` |

Delete that file and LapGuardian has no memory of you. It is listed in
`.gitignore` and in every AI ignore file so it can never be committed or read
by a coding assistant.

## What LapGuardian reads

Only hardware and filesystem telemetry about the machine it runs on.

| Category | Data | Why |
|---|---|---|
| Battery | Design capacity, full-charge capacity, cycle count, charge percentage, AC state | Compute wear and detect harmful charge habits |
| Thermal | CPU and GPU temperature, fan speed where exposed, throttle flags | Detect sustained heat |
| Storage | Device model, total and free bytes, SMART attributes where permitted | Detect a dangerously full or failing drive |
| System | OS name and version, CPU model, machine model | Interpret the readings and file useful bug reports |

The machine model and OS version are collected because a battery reading is
meaningless without knowing what hardware produced it. They never leave your
computer. Exports strip hostname and user paths by default
(`redact_identifiers_on_export = true`).

## Operating-system commands we invoke

LapGuardian shells out to vendor and OS tools, because that is where this data
lives. Every invocation follows the same rules:

- Commands are built as **argument lists, never shell strings**. `shell=True`
  is forbidden by the project lint configuration.
- Executables are resolved from absolute or well-known system paths, not from a
  mutable `PATH` lookup where a planted binary could win.
- Every call has a **timeout** and its failure is non-fatal.
- Output is parsed defensively and treated as untrusted text.

| OS | Commands | Privileges |
|---|---|---|
| Windows | `powercfg /batteryreport /xml`, WMI and CIM queries (`Win32_Battery`, `MSAcpi_ThermalZoneTemperature`, `Win32_LogicalDisk`), `Get-PhysicalDisk` | Normal user; SMART needs Administrator |
| Linux | reads `/sys/class/power_supply/`, `/sys/class/thermal/`, `/proc`; optionally `smartctl` | Normal user; `smartctl` needs root |
| macOS | `pmset -g batt`, `ioreg -rn AppleSmartBattery`, `system_profiler`; optionally `powermetrics` | Normal user; `powermetrics` needs sudo |

### Temporary files

`powercfg /batteryreport` must write a file to disk, and that file contains
your machine name and user profile path. LapGuardian writes it to a private
temporary directory, parses it, and **deletes it in a `finally` block**. The
filename patterns are also in `.gitignore` and every AI ignore file as a second
line of defence.

### Privileges

**LapGuardian never requires elevation to run.** Metrics that need
Administrator or root are optional. Without elevation it reports them as
unavailable with the reason, and everything else still works. The tool will
never silently prompt for elevation or re-launch itself elevated.

## Threat model

In scope:

- Leaking machine-identifying data off the device.
- Command injection through sensor output or configuration values.
- Path traversal or arbitrary writes through configured paths.
- A dependency introducing a network call or telemetry.

Out of scope:

- An attacker who already has administrator access to the machine.
- Hardware or firmware that reports false sensor values.
- Malicious forks of this project.

## Dependencies

The runtime dependency set is deliberately small: `typer`, `rich`, `psutil`,
`pydantic`, `pydantic-settings`. Dependabot watches them weekly. A pull request
that adds a dependency making network calls will not be merged.
