# Feature Registry

Owner: Claude. Every feature has a stable ID. Tasks in
[`TASKS.md`](TASKS.md) reference these IDs; so do commit messages where useful.

Priorities: **P0** must exist for v0.1 to be worth releasing. **P1** should be
in v0.1. **P2** is after v0.1.

Statuses: `planned` → `in-progress` → `done`. Progress is tracked in
[`STATUS.md`](STATUS.md), not here — this file describes *what*, not *how far*.

---

## F-01 — Battery health report

**Priority** P0 · **Milestone** M1 · **Status** planned

> As a laptop owner, I want to know how much of my battery's original capacity
> is gone, so that I can tell whether a short runtime is wear or just heavy use.

Read the original design capacity and the current full-charge capacity, and
compute wear as `(1 - full_charge / design) * 100`. Report cycle count where
the firmware exposes it, charge level, and AC state.

**Acceptance**

- Wear percentage within 2 points of the vendor utility on the same machine.
- Cycle count is `Optional`; absent and a reported `0` both mean unknown.
- Wear clamped at `0` when firmware reports `full_charge > design` after a
  recalibration, with the anomaly recorded rather than shown as negative.
- Multi-battery machines are summed, and the count is reported.
- Every field carries its `source` so history stays interpretable.

---

## F-02 — Charge-habit advisory

**Priority** P0 · **Milestone** M4 · **Status** planned

> As someone whose laptop lives in a dock, I want to be told that keeping it at
> 100% is what is killing the battery, and what to do instead.

The feature the project exists for. Detect the harmful patterns — sustained
high state of charge on AC power, and repeated deep discharges — and advise the
charge window from the configuration.

**Acceptance**

- Warns after `[battery] plugged_full_warn_hours` on AC at or near full.
  Requires F-06, since it needs history to see a sustained state.
- Advises the `ideal_charge_floor_pct`–`ideal_charge_ceiling_pct` window.
- Warns on repeated discharge below `deep_discharge_warn_pct`.
- Advice names where the setting lives (vendor utility or BIOS) and **never
  offers to change it** — see the non-goals in [`VISION.md`](VISION.md).
- Produces no advisory at all when the habit is already good. Silence is a
  valid and desirable output.

---

## F-03 — Thermal monitoring and throttle detection

**Priority** P0 · **Milestone** M1 · **Status** planned

> As an owner whose laptop "got slow", I want to know whether it is overheating
> and throttling, so that I can clean it instead of replacing it.

Read CPU and, where available, GPU temperature; detect throttling.

**Acceptance**

- Linux: `psutil.sensors_temperatures()` with a `/sys/class/thermal` fallback,
  preferring `x86_pkg_temp`, `coretemp` or `cpu-thermal` zones.
- Windows: attempted via CIM, reported with
  `confidence="unreliable-on-this-platform"` or as unavailable. **This is a
  documented limitation, not a bug** — see
  [`ARCHITECTURE.md`](ARCHITECTURE.md) section 9.
- macOS: `powermetrics` when sudo is available, otherwise unavailable with the
  reason.
- Throttling inferred from current versus maximum clock where no direct flag
  exists, and labelled as inferred.
- A sustained reading, per `[thermal] sustained_window_minutes`, is
  distinguished from a harmless spike. Requires F-06.

---

## F-04 — Storage health

**Priority** P0 · **Milestone** M1 · **Status** planned

> As an owner, I want to know that my almost-full SSD is both slowing down and
> wearing out faster, because nothing else tells me that.

Free space in percentage and absolute terms, device model, and SMART attributes
where privileges allow.

**Acceptance**

- Free space always available on every platform via `shutil.disk_usage()`.
- Warns on both `free_warn_pct` and `free_warn_gb`, so a 4 TB drive at 10% is
  not flagged while a 256 GB drive at 16% still is.
- SMART degrades to `MetricUnavailable(needs_privileges=True)` without
  elevation, and the rest of the metric still works.
- All mounted fixed drives are reported; removable and network drives are
  excluded.

---

## F-05 — Advisor rule engine

**Priority** P0 · **Milestone** M4 · **Status** planned

> As a non-technical user, I want to be told what to do, not shown a table of
> numbers I have to interpret.

A list of small, independent rule functions, each taking the computed metrics
and the settings and returning zero or one `Advisory`.

**Acceptance**

- Every `Advisory` has a severity, a cause naming the actual measurement, an
  action the owner can take today, and a confidence level.
- Adding a rule requires touching no other rule.
- Each rule is unit-tested against the `FakeProvider`, including its silent
  case.
- An advisory built on an unreliable sensor says so.
- No advisory is ever produced from a `MetricUnavailable`.

---

## F-06 — Local history and trend analysis

**Priority** P0 · **Milestone** M3 · **Status** planned

> As an owner, I want to see how my battery has degraded over the past year,
> because a single reading tells me nothing about the direction.

SQLite persistence plus the queries that turn a series of snapshots into a
trend. This is the feature the operating system does not offer, and F-02 and
F-03 both depend on it.

**Acceptance**

- One database file in the platform application-data directory, schema from
  `storage/schema.sql`, migrated via `PRAGMA user_version`.
- Timestamps stored as UTC ISO-8601 text. Naive timestamps are a bug.
- `unavailable` is its own table, so missing readings never sit in the metric
  tables where they could be mistaken for measurements.
- Retention enforced on write per `[history] retention_days`; `0` keeps
  everything.
- Deleting the file loses history and breaks nothing else.

---

## F-07 — Command-line interface

**Priority** P0 · **Milestone** M1 · **Status** planned

> As a user, I want one obvious command that tells me how my laptop is doing.

`scan`, `report`, `history`, `export`, `config path`.

**Acceptance**

- `lapguardian scan` with no arguments produces useful output on a fresh
  install with no configuration file.
- `--json` writes **only** JSON to stdout; human messages go to stderr, so it
  pipes cleanly.
- `--debug` explains what was attempted and why each metric was unavailable,
  without including the hostname or home directory path.
- Output is readable without colour: severity is carried by a word, not only by
  a colour. `NO_COLOR` and `--no-color` are honoured.
- Exit `0` when LapGuardian ran, even if it found critical problems. Non-zero
  only when LapGuardian itself failed. `--fail-on warn|critical` for scripting.
- No emoji — too many Windows terminals mangle them.

---

## F-08 — Configuration and tunable thresholds

**Priority** P1 · **Milestone** M5 · **Status** planned

> As an owner of a gaming laptop that idles at 70 °C, I want to raise the
> thermal threshold so the tool stops crying wolf.

TOML configuration via `pydantic-settings`.

**Acceptance**

- Every field has a default; the tool works with no config file at all.
- `lapguardian config path` prints where the file is expected.
- Every default is documented and defensible in `lapguardian.example.toml`,
  which stays in sync with `config.py` in the same commit.
- An invalid value reports the file path and the offending key, and falls back
  to the default where that is safe.

---

## F-09 — Cross-platform adapters

**Priority** P0 · **Milestone** M1–M2 · **Status** planned

> As a Linux or macOS user, I want the same tool, not a Windows-only utility.

One adapter per OS behind the `MetricsProvider` protocol.

**Acceptance**

- `get_provider()` is the only function in the codebase that branches on the
  operating system.
- Each adapter has golden-file tests, including failure shapes: empty output,
  truncated XML, missing keys, zero design capacity.
- No `shell=True`, an explicit timeout on every subprocess call, explicit
  output decoding, and `finally` cleanup of files OS tools create.
- An unsupported platform returns a provider that reports everything
  unavailable with a clear reason, rather than crashing.

---

## F-10 — Export

**Priority** P1 · **Milestone** M5 · **Status** planned

> As a repair shop, I want to hand the customer a readable report.

`lapguardian export --format {json,csv,markdown} --out FILE`.

**Acceptance**

- All three formats round-trip the same data.
- `redact_identifiers_on_export = true` by default strips hostname and user
  paths.
- Markdown output is readable as plain text.
- Writes only to the path the user gave.

---

## F-11 — Watch mode

**Priority** P2 · **Milestone** M5 · **Status** planned

> As someone diagnosing a thermal problem, I want to watch the numbers while I
> run a load.

`lapguardian watch --interval N`, a foreground polling loop.

**Acceptance**

- Foreground only. **Not a daemon or service** — see
  [`ARCHITECTURE.md`](ARCHITECTURE.md) section 13.
- Ctrl-C exits cleanly without a traceback and without a partial database write.
- Optionally appends snapshots with `--save`, honouring the interval so it does
  not flood the database.

---

## F-12 — TUI dashboard

**Priority** P2 · **Milestone** post-v0.1 · **Status** planned

> As a user who would rather look than type, I want a live view.

A terminal dashboard over the same `core` API.

**Acceptance**

- No logic beyond presentation; reuses `core` unchanged.
- Degrades to `scan` output on a terminal that cannot support it.
- Does not become a reason to add a dependency with network access.

---

## Index

| ID | Feature | Priority | Milestone | Depends on |
|---|---|---|---|---|
| F-01 | Battery health report | P0 | M1 | F-09 |
| F-02 | Charge-habit advisory | P0 | M4 | F-01, F-05, F-06 |
| F-03 | Thermal monitoring and throttle detection | P0 | M1 | F-09 |
| F-04 | Storage health | P0 | M1 | F-09 |
| F-05 | Advisor rule engine | P0 | M4 | F-01, F-03, F-04 |
| F-06 | Local history and trend analysis | P0 | M3 | F-01, F-03, F-04 |
| F-07 | Command-line interface | P0 | M1 | F-01, F-03, F-04 |
| F-08 | Configuration and tunable thresholds | P1 | M5 | — |
| F-09 | Cross-platform adapters | P0 | M1–M2 | — |
| F-10 | Export | P1 | M5 | F-06 |
| F-11 | Watch mode | P2 | M5 | F-07 |
| F-12 | TUI dashboard | P2 | post-v0.1 | F-07 |
