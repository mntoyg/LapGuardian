<div align="center">

# LapGuardian

**Your laptop is dying faster than it has to. LapGuardian tells you why, and what to do about it.**

A privacy-first, offline health advisor for the three things that actually kill laptops:
**battery wear**, **heat**, and **a full disk**.

[![CI](https://github.com/mntoyg/LapGuardian/actions/workflows/ci.yml/badge.svg)](https://github.com/mntoyg/LapGuardian/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-261230.svg)](https://github.com/astral-sh/ruff)

</div>

> **Status: M0 - Foundation.** The architecture, documentation and project
> scaffold are in place. Metric collection is not implemented yet. See
> [`docs/STATUS.md`](docs/STATUS.md) for exactly what works today and
> [`docs/ROADMAP.md`](docs/ROADMAP.md) for what lands next.

---

## The problem

Most laptops do not die of old age. They die of neglect that nobody warned the owner about.

- **Batteries are kept at 100% for years.** A lithium-ion cell held at a high
  state of charge ages on the calendar, not just on cycles. Two years of
  living in a docking station can cost more capacity than two years of
  unplugging daily.
- **Heat accumulates silently.** Dust blocks the fins, thermal paste dries out,
  and the machine quietly throttles. The owner concludes "it got slow" and
  buys a new one.
- **The SSD runs at 97% full forever.** Less spare area means more write
  amplification, slower writes, and faster wear.

None of this is visible in a normal operating system. There is no dial that
says *your battery has lost 31% of its original capacity and here is the habit
that caused it*. So people replace working hardware, and the old machine
becomes e-waste.

## What LapGuardian does

| | |
|---|---|
| **Measures** | Battery wear against original design capacity, cycle count, thermals, throttling, and free space - using the data your OS already has. |
| **Explains** | Plain-language advice with a severity level, not a wall of raw sensor values. |
| **Remembers** | Every scan is written to a local SQLite file, so you can see the trend over months instead of guessing. |
| **Works anywhere** | No vendor lock-in. Windows, Linux and macOS, any brand. |
| **Stays yours** | No account, no cloud, no telemetry, no network calls. Ever. See [`SECURITY.md`](SECURITY.md). |

## Install

LapGuardian is not published to PyPI yet. Until then, install from source:

```bash
git clone https://github.com/mntoyg/LapGuardian.git
cd LapGuardian
uv sync --extra dev
uv run lapguardian --help
```

Once v0.1.0 ships:

```bash
uv tool install lapguardian
```

## Usage (target design)

```bash
# One-off health check, human readable
lapguardian scan

# Full report including history trend
lapguardian report

# Append a snapshot to the local database (good for a scheduled task)
lapguardian scan --save

# What has my battery done over the last 90 days?
lapguardian history --days 90

# Machine-readable output
lapguardian scan --json
lapguardian export --format markdown --out health.md
```

Example of the output `scan` is designed to produce:

```
LapGuardian  -  2026-11-06 14:32

 Battery        WARN      Wear 23%  (design 52.0 Wh -> full-charge 40.0 Wh)
                          412 cycles - plugged in and full for 9h
 Thermals       OK        CPU package 61 C  (peak today 78 C)
 Storage        WARN      C: 11% free  (48 GB of 476 GB)

 Advice
  !  Your battery has lost 23% of its original capacity. Set a charge
     limit of 80% in your vendor utility or BIOS if one is available.
  !  Free at least 24 GB on C: to get back above the 15% threshold.
  i  Nothing to do about thermals right now.

 2 warnings, 0 critical.  Snapshot saved.
```

## Platform support

| Metric | Windows | Linux | macOS | Notes |
|---|---|---|---|---|
| Battery design vs full-charge capacity | planned | planned | planned | `powercfg /batteryreport`, `/sys/class/power_supply`, `ioreg` |
| Cycle count | planned | planned | planned | Not exposed by every firmware |
| Charge level / AC state | planned | planned | planned | via `psutil` |
| CPU temperature | partial | planned | partial | **Known limitation** - see [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md#known-limitations) |
| Free disk space | planned | planned | planned | Always available |
| SMART attributes | optional | optional | optional | Needs administrator or root |

LapGuardian is built to **degrade gracefully**: a metric it cannot read is
reported as unavailable with the reason, never guessed and never a crash.

## Documentation

| Document | What is in it |
|---|---|
| [`docs/MASTER_BLUEPRINT.md`](docs/MASTER_BLUEPRINT.md) | The master document - problem, scope, stack, structure |
| [`docs/VISION.md`](docs/VISION.md) | Long-term direction and the permanent non-goals |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Layers, interfaces, data sources per OS, schema, limitations |
| [`docs/FEATURES.md`](docs/FEATURES.md) | Feature registry F-01 to F-12 with priorities |
| [`docs/ROADMAP.md`](docs/ROADMAP.md) | Milestones M0 to M6 and their definitions of done |
| [`docs/TASKS.md`](docs/TASKS.md) | The actual backlog with acceptance criteria |
| [`docs/STATUS.md`](docs/STATUS.md) | Single source of truth for progress |
| [`docs/HANDOFF.md`](docs/HANDOFF.md) | How work is split across AI agents and humans |
| [`AGENTS.md`](AGENTS.md) | The engineering contract every contributor follows |

## Contributing

Read [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`AGENTS.md`](AGENTS.md), pick an
open item from [`docs/TASKS.md`](docs/TASKS.md), and open a pull request.

Reports from unusual hardware are especially valuable. If `lapguardian scan`
cannot read something on your machine, that is a bug worth filing - sensor
coverage is the hardest part of this project.

## License

MIT. See [`LICENSE`](LICENSE).
