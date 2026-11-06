# Roadmap

Owner: Claude. Current progress lives in [`STATUS.md`](STATUS.md) — this file
describes the plan, not the state.

Milestones are sequenced by dependency, not by date. There are no deadlines
here on purpose: this is an open-source project with no customer waiting, and
inventing dates would only make [`STATUS.md`](STATUS.md) look like a failure.

---

## M0 — Foundation

**Goal:** a repository that a contributor, human or AI, can be dropped into and
be productive in within an hour.

**Scope:** documentation, project scaffold, ignore rules, CI, published
repository. No metric collection.

**Definition of done**

- [x] `docs/` complete: blueprint, vision, architecture, features, roadmap,
      tasks, status, handoff
- [x] `AGENTS.md` plus per-agent files for Claude, Codex, Cursor and Aider
- [x] Ignore rules for git and every AI assistant, covering generated files and
      — critically — the local database and raw battery reports
- [x] `.gitattributes` so Windows development and Linux CI agree on line endings
- [x] `pyproject.toml` with ruff, mypy, pytest and coverage configured
- [x] Package scaffold with the layer boundaries in place and every collector a
      documented stub referencing its task ID
- [x] SQLite schema written
- [x] Annotated example configuration
- [x] CI green on Ubuntu, Windows and macOS across Python 3.10–3.13
- [x] Repository published on GitHub

**Exit criterion:** `uv sync --extra dev` followed by the full quality gate
passes on a clean clone, and `lapguardian --help` runs.

---

## M1 — Windows MVP

**Goal:** `lapguardian scan` produces genuinely useful output on a real Windows
laptop. Windows first because it is the development machine and the largest
share of the target audience.

**Features:** F-01, F-03, F-04, F-07, F-09 (Windows only)

**Definition of done**

- `core/models.py`, `core/provider.py` and `core/health.py` implemented
- `platforms/windows.py` reads battery capacity and cycle count from
  `powercfg /batteryreport /xml`, charge state from `psutil`, free space from
  `shutil.disk_usage()`
- Thermal attempted via CIM and reported honestly as low-confidence or
  unavailable
- `powercfg` temporary file deleted in a `finally` block, verified by a test
- `lapguardian scan` and `lapguardian scan --json` work
- Golden files committed for at least one real Windows battery report, plus the
  failure shapes: empty output, truncated XML, missing `cycle_count`, zero
  design capacity
- Battery wear verified within 2 points against a vendor utility on the same
  machine

**Exit criterion:** someone with a Windows laptop learns something true about
their hardware that they did not already know.

---

## M2 — Cross-platform

**Goal:** the same tool, the same output, on Linux and macOS.

**Features:** F-09 (Linux, macOS)

**Definition of done**

- `platforms/linux.py` handles both the µWh (`energy_full*`) and µAh
  (`charge_full*`) sysfs shapes, globs `BAT*` rather than assuming `BAT0`, and
  sums multi-battery machines
- `platforms/macos.py` parses `ioreg -rn AppleSmartBattery -a` with `plistlib`,
  not a regex
- Golden files for at least one real machine per platform, plus failure shapes
- Live-hardware tests marked and skipping cleanly on CI runners, which have no
  battery
- An unsupported platform returns a provider reporting everything unavailable,
  rather than crashing

**Exit criterion:** `scan` output on Linux and macOS is indistinguishable in
shape from Windows, and every difference in coverage is explained in the output
rather than silently missing.

---

## M3 — Persistence

**Goal:** LapGuardian remembers. This is what the operating system does not do,
and it is the foundation for the advisor.

**Features:** F-06

**Definition of done**

- `storage/db.py` applies `schema.sql`, migrates via `PRAGMA user_version`
- UTC ISO-8601 timestamps throughout; a test asserts no naive datetime reaches
  the database
- `unavailable` rows written, so a metric that stopped being readable is itself
  recorded
- `lapguardian scan --save` and `lapguardian history --days N` work
- Retention enforced on write, `0` meaning keep everything
- Trend arithmetic in `core/health.py`, unit-tested with synthetic series
- Deleting the database file loses history and breaks nothing else

**Exit criterion:** thirty days of saved snapshots produce a trend a user can
read, and a missing reading in the middle of that series does not distort it.

---

## M4 — Advisor

**Goal:** the product. Numbers become advice.

**Features:** F-02, F-05

**Definition of done**

- `core/advisor.py` is a list of independent rule functions, each returning
  zero or one `Advisory`
- Every advisory has severity, a cause naming the measurement, an action, and a
  confidence level
- F-02 charge-habit detection working against history: sustained high state of
  charge on AC, and repeated deep discharge
- Advice names where the hardware setting lives and never offers to change it
- Each rule unit-tested against `FakeProvider`, including the case where it
  correctly stays silent
- No advisory is ever generated from a `MetricUnavailable`
- `--fail-on warn|critical` implemented

**Exit criterion:** a non-technical reader can run `scan`, read the advice, and
act on it without asking anyone what it means.

---

## M5 — Polish

**Goal:** configurable, exportable, pleasant.

**Features:** F-08, F-10, F-11

**Definition of done**

- `config.py` loads TOML with documented defaults; `lapguardian config path`
  works; `lapguardian.example.toml` verified in sync by a test
- `export --format {json,csv,markdown}` with identifier redaction on by default
- `watch --interval N` in the foreground, clean Ctrl-C, no partial writes
- Output verified readable with `NO_COLOR=1` and on a narrow terminal

**Exit criterion:** the gaming-laptop owner can raise the thermal threshold and
stop getting false warnings, and a repair shop can hand a customer a file.

---

## M6 — Release v0.1.0

**Goal:** installable by someone who has never heard of this repository.

**Definition of done**

- The name `lapguardian` checked and claimed on PyPI — **this needs doing
  early, not at M6**, since the name could be taken at any time
- `CHANGELOG.md` complete for 0.1.0
- Version bumped; tagged release with notes
- Published to PyPI; `uv tool install lapguardian` verified on all three
  platforms from a clean machine
- README install instructions updated from source-install to the real thing
- Coverage reported and a baseline recorded

**Exit criterion:** a stranger installs it in one command and gets a correct
reading on hardware none of the maintainers have seen.

---

## After v0.1

Not scheduled, in rough order of value:

- **More golden files.** The only real path to broad hardware support, and the
  contribution the project most needs from strangers.
- **F-12 TUI dashboard.** For people who would rather look than type.
- **Degradation projection.** When will this battery fall below a usable
  capacity, based on this machine's own measured history rather than a generic
  curve. Needs a year of data to be worth anything, which is why F-06 comes
  first.
- **Thermal drift detection.** A heatsink clogging up over months is a slowly
  rising baseline, not a spike. Same dependency on history.
- **System package manager distribution**, so installing it does not require
  knowing what Python is.

And never: anything in the permanent non-goals in [`VISION.md`](VISION.md).
