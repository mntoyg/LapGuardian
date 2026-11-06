-- LapGuardian local history schema.
--
-- One SQLite file in the platform application-data directory. It never leaves
-- the machine. Applied and migrated by lapguardian/storage/db.py via
-- PRAGMA user_version.
--
-- Two design notes worth knowing before changing anything here:
--
-- 1. Timestamps are UTC ISO-8601 TEXT. SQLite has no date type; ISO-8601 text
--    sorts correctly as text and survives the user changing timezone. Naive
--    local timestamps would silently corrupt the trend, which is the one thing
--    this project offers that the operating system does not. Lint rule DTZ
--    enforces the Python side of this.
--
-- 2. `unavailable` is a real table, not a null in a metric table. Knowing that
--    a metric stopped being readable is itself a signal, and keeping
--    non-readings out of the metric tables means nothing in those tables can
--    be mistaken for a measurement.

PRAGMA foreign_keys = ON;

-- One row per scan.
CREATE TABLE IF NOT EXISTS snapshots (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    taken_at      TEXT    NOT NULL,          -- UTC ISO-8601
    app_version   TEXT    NOT NULL,
    os_name       TEXT    NOT NULL,
    os_version    TEXT    NOT NULL,
    machine_model TEXT,
    cpu_model     TEXT
);

CREATE INDEX IF NOT EXISTS idx_snapshots_taken_at
    ON snapshots (taken_at);

CREATE TABLE IF NOT EXISTS battery_metrics (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id             INTEGER NOT NULL
        REFERENCES snapshots (id) ON DELETE CASCADE,
    present                 INTEGER NOT NULL,   -- 0 or 1
    charge_pct              REAL,
    on_ac_power             INTEGER,            -- 0, 1 or NULL when unknown
    design_capacity_wh      REAL,
    full_charge_capacity_wh REAL,
    cycle_count             INTEGER,            -- NULL when firmware omits it
    battery_count           INTEGER NOT NULL DEFAULT 1,
    source                  TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_battery_snapshot
    ON battery_metrics (snapshot_id);

CREATE TABLE IF NOT EXISTS thermal_metrics (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id         INTEGER NOT NULL
        REFERENCES snapshots (id) ON DELETE CASCADE,
    sensor_label        TEXT    NOT NULL,
    temp_c              REAL,
    is_throttling       INTEGER,                -- 0, 1 or NULL when unknown
    throttling_inferred INTEGER NOT NULL DEFAULT 0,
    confidence          TEXT    NOT NULL,       -- see core.models.Confidence
    source              TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_thermal_snapshot
    ON thermal_metrics (snapshot_id);

CREATE TABLE IF NOT EXISTS storage_metrics (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id  INTEGER NOT NULL
        REFERENCES snapshots (id) ON DELETE CASCADE,
    mount        TEXT    NOT NULL,
    device_model TEXT,
    total_bytes  INTEGER NOT NULL,
    free_bytes   INTEGER NOT NULL,
    smart_ok     INTEGER,                       -- NULL without elevation
    source       TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_storage_snapshot
    ON storage_metrics (snapshot_id);

CREATE TABLE IF NOT EXISTS advisories (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id INTEGER NOT NULL
        REFERENCES snapshots (id) ON DELETE CASCADE,
    severity    TEXT    NOT NULL,               -- see core.models.Severity
    metric      TEXT    NOT NULL,
    cause       TEXT    NOT NULL,
    action      TEXT    NOT NULL,
    confidence  TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_advisories_snapshot
    ON advisories (snapshot_id);

-- A metric we could not read, and why. See design note 2 above.
CREATE TABLE IF NOT EXISTS unavailable (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    snapshot_id      INTEGER NOT NULL
        REFERENCES snapshots (id) ON DELETE CASCADE,
    metric           TEXT    NOT NULL,
    reason           TEXT    NOT NULL,
    needs_privileges INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_unavailable_snapshot
    ON unavailable (snapshot_id);
