"""Smoke tests.

These keep CI meaningful from day one of M0, before any metric collection
exists. They assert the things that must never break: the package imports, the
CLI starts, the layer boundary holds, and the schema is valid SQL.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path

from typer.testing import CliRunner

import lapguardian
from lapguardian.cli import app
from lapguardian.core.models import MetricUnavailable, Severity
from lapguardian.core.provider import MetricsProvider

from .conftest import FakeProvider, utc_now

runner = CliRunner()


def test_package_has_version() -> None:
    assert isinstance(lapguardian.__version__, str)
    assert lapguardian.__version__


def test_cli_help_runs() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "lapguardian" in result.output.lower()


def test_cli_version_runs() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0


def test_unimplemented_command_fails_loudly() -> None:
    """An unimplemented command must say so, not pretend to succeed."""
    result = runner.invoke(app, ["scan"])
    assert result.exit_code != 0


def test_fake_provider_satisfies_the_protocol() -> None:
    """The test double and the production contract must not drift apart."""
    assert isinstance(FakeProvider(), MetricsProvider)


def test_core_does_not_import_the_platform_layer() -> None:
    """The layer boundary from AGENTS.md section 4, asserted rather than trusted.

    If ``core`` ever imports an OS-specific module, the advisor stops being
    testable without hardware, which is the single assumption the whole test
    strategy rests on.
    """
    core = Path(lapguardian.__file__).parent / "core"
    forbidden = ("import psutil", "import subprocess", "from lapguardian.platforms")
    offenders = [
        f"{path.name}: {needle}"
        for path in core.glob("*.py")
        for needle in forbidden
        if needle in path.read_text(encoding="utf-8")
    ]
    assert offenders == []


def test_metric_unavailable_carries_a_reason() -> None:
    """A missing reading must explain itself; that is the whole point of the type."""
    unavailable = MetricUnavailable(metric="thermal.cpu", reason="no sensor")
    assert unavailable.reason
    assert unavailable.needs_privileges is False


def test_severity_values_are_stable() -> None:
    """These strings are written into the database, so they are a contract."""
    assert [s.value for s in Severity] == ["ok", "info", "warn", "critical"]


def test_test_timestamps_are_timezone_aware() -> None:
    """Naive datetimes silently corrupt the history trend, so tests avoid them."""
    now = utc_now()
    assert isinstance(now, datetime)
    assert now.tzinfo is not None


def test_schema_is_valid_sql() -> None:
    """The schema must apply cleanly to an empty database."""
    schema = Path(lapguardian.__file__).parent / "storage" / "schema.sql"
    conn = sqlite3.connect(":memory:")
    try:
        conn.executescript(schema.read_text(encoding="utf-8"))
        tables = {
            row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        }
    finally:
        conn.close()
    assert {
        "snapshots",
        "battery_metrics",
        "thermal_metrics",
        "storage_metrics",
        "advisories",
        "unavailable",
    } <= tables
