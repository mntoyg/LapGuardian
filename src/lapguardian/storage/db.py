"""SQLite persistence for the local health history.

The only module that touches SQLite. It contains no health logic: it stores
what it is given and reads it back.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import sqlite3
    from datetime import datetime
    from pathlib import Path

    from lapguardian.core.models import (
        Advisory,
        BatterySnapshot,
        MetricUnavailable,
        StorageSnapshot,
        SystemInfo,
        ThermalSnapshot,
    )

__all__ = ["connect", "prune", "query_history", "save_snapshot"]

SCHEMA_VERSION = 1
"""Schema version, compared against ``PRAGMA user_version`` on connect."""


def connect(path: Path) -> sqlite3.Connection:
    """Open the history database, creating and migrating it as needed.

    Applies ``schema.sql`` on a fresh file and migrates an existing one by
    comparing ``PRAGMA user_version`` against :data:`SCHEMA_VERSION`.

    Args:
        path: Database file path. Parent directories are created.

    Returns:
        An open connection with foreign keys enabled.
    """
    # TODO(TASK-019): implement. See docs/TASKS.md.
    raise NotImplementedError


def save_snapshot(
    conn: sqlite3.Connection,
    system: SystemInfo,
    battery: BatterySnapshot | MetricUnavailable,
    thermal: list[ThermalSnapshot] | MetricUnavailable,
    storage: list[StorageSnapshot] | MetricUnavailable,
    advisories: list[Advisory],
) -> int:
    """Write one complete scan, in a single transaction.

    Unavailable metrics are written to the ``unavailable`` table rather than as
    nulls in a metric table, so nothing in the metric tables can be mistaken
    for a measurement.

    Args:
        conn: Open connection.
        system: Machine identity for this scan.
        battery: Battery reading, or why it was unavailable.
        thermal: Temperature readings, or why they were unavailable.
        storage: Drive readings, or why they were unavailable.
        advisories: Advice produced for this scan.

    Returns:
        The new ``snapshots.id``.

    Raises:
        ValueError: If any timestamp is naive rather than timezone-aware.
    """
    # TODO(TASK-020): implement. Reject naive datetimes explicitly - a naive
    # timestamp here silently corrupts the trend. See docs/TASKS.md.
    raise NotImplementedError


def query_history(
    conn: sqlite3.Connection,
    since: datetime,
) -> list[int]:
    """Return the ids of snapshots taken at or after a point in time.

    Args:
        conn: Open connection.
        since: Timezone-aware lower bound.

    Returns:
        Snapshot ids, oldest first.
    """
    # TODO(TASK-021): implement. See docs/TASKS.md.
    raise NotImplementedError


def prune(conn: sqlite3.Connection, retention_days: int) -> int:
    """Delete snapshots older than the retention window.

    Args:
        conn: Open connection.
        retention_days: Days of history to keep. ``0`` keeps everything.

    Returns:
        Number of snapshots deleted.
    """
    # TODO(TASK-024): implement, called on write. See docs/TASKS.md.
    raise NotImplementedError
