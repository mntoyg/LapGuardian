"""Shared fixtures.

The important one is :class:`FakeProvider`. The whole point of the layer
boundary in ``AGENTS.md`` section 4 is that the domain can be tested by handing
it fabricated readings, with no hardware, no mocking of ``subprocess``, and no
platform markers. Tests for ``core/`` should use this and nothing else.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from lapguardian.core.models import (
    BatterySnapshot,
    Confidence,
    MetricUnavailable,
    StorageSnapshot,
    SystemInfo,
    ThermalSnapshot,
)


class FakeProvider:
    """A MetricsProvider that returns whatever the test asks for.

    Satisfies the MetricsProvider protocol structurally. Pass a
    MetricUnavailable for any metric to exercise the degraded paths, which is
    where most real bugs live.
    """

    def __init__(
        self,
        battery: BatterySnapshot | MetricUnavailable | None = None,
        thermal: list[ThermalSnapshot] | MetricUnavailable | None = None,
        storage: list[StorageSnapshot] | MetricUnavailable | None = None,
    ) -> None:
        self._battery = battery if battery is not None else healthy_battery()
        self._thermal = thermal if thermal is not None else []
        self._storage = storage if storage is not None else []

    def system_info(self) -> SystemInfo:
        return SystemInfo(
            os_name="FakeOS",
            os_version="1.0",
            machine_model="Fake Laptop 15",
            cpu_model="Fake CPU",
        )

    def battery(self) -> BatterySnapshot | MetricUnavailable:
        return self._battery

    def thermal(self) -> list[ThermalSnapshot] | MetricUnavailable:
        return self._thermal

    def storage(self) -> list[StorageSnapshot] | MetricUnavailable:
        return self._storage


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp.

    Tests must never build a naive datetime: the production code rejects them,
    and a test that uses one is testing something the program will not accept.
    """
    return datetime.now(tz=timezone.utc)


def healthy_battery() -> BatterySnapshot:
    """Return a battery with no meaningful wear."""
    return BatterySnapshot(
        taken_at=utc_now(),
        present=True,
        charge_pct=72.0,
        on_ac_power=False,
        design_capacity_wh=52.0,
        full_charge_capacity_wh=51.0,
        cycle_count=84,
        battery_count=1,
        source="fake",
    )


def worn_battery() -> BatterySnapshot:
    """Return a battery that has lost roughly a quarter of its capacity."""
    return BatterySnapshot(
        taken_at=utc_now(),
        present=True,
        charge_pct=100.0,
        on_ac_power=True,
        design_capacity_wh=52.0,
        full_charge_capacity_wh=40.0,
        cycle_count=412,
        battery_count=1,
        source="fake",
    )


def unreadable_thermal() -> MetricUnavailable:
    """Return the Windows thermal reality: present, but not readable."""
    return MetricUnavailable(
        metric="thermal.cpu",
        reason="no readable temperature sensor on this machine",
        needs_privileges=False,
    )


@pytest.fixture
def fake_provider() -> FakeProvider:
    """A provider reporting a healthy machine."""
    return FakeProvider()


@pytest.fixture
def worn_provider() -> FakeProvider:
    """A provider reporting a worn battery and unreadable thermals."""
    return FakeProvider(battery=worn_battery(), thermal=unreadable_thermal())


@pytest.fixture
def unreliable_confidence() -> Confidence:
    """The confidence level used for sensors we cannot trust on this platform."""
    return Confidence.UNRELIABLE_PLATFORM
