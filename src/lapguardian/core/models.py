"""Domain models: snapshots, advisories, and the unavailable-metric type.

These are plain data declarations with no behaviour. Nothing here imports
anything operating-system specific.

The most important type in this module is :class:`MetricUnavailable`. A reading
that could not be taken is represented by it, never by a zero or a default:
``0 C`` and ``0 Wh`` are measurements, and substituting either for a failed
read silently corrupts the long-term trend that is the whole point of the
project.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum

__all__ = [
    "Advisory",
    "BatterySnapshot",
    "Confidence",
    "MetricUnavailable",
    "Severity",
    "StorageSnapshot",
    "SystemInfo",
    "ThermalSnapshot",
]


class Severity(str, Enum):
    """How urgently the owner should act on an advisory."""

    OK = "ok"
    INFO = "info"
    WARN = "warn"
    CRITICAL = "critical"


class Confidence(str, Enum):
    """How much the reading behind an advisory can be trusted.

    ``UNRELIABLE_PLATFORM`` exists because of Windows CPU temperature, which
    cannot be read dependably without a kernel driver. An advisory built on
    such a sensor must say so rather than presenting a guess as a measurement.
    """

    MEASURED = "measured"
    ESTIMATED = "estimated"
    UNRELIABLE_PLATFORM = "unreliable-on-this-platform"


@dataclass(frozen=True, slots=True)
class MetricUnavailable:
    """A metric that could not be read, and the reason why.

    Attributes:
        metric: Dotted name of what was being read, e.g. ``"battery.cycles"``.
        reason: Human-readable explanation, shown to the user verbatim.
        needs_privileges: True when elevation would have made it readable.
    """

    metric: str
    reason: str
    needs_privileges: bool = False


@dataclass(frozen=True, slots=True)
class SystemInfo:
    """Identifying details needed to interpret a set of readings.

    A battery reading is meaningless without knowing what hardware produced
    it. None of this leaves the machine; exports redact it by default.
    """

    os_name: str
    os_version: str
    machine_model: str | None
    cpu_model: str | None


@dataclass(frozen=True, slots=True)
class BatterySnapshot:
    """A single reading of battery state.

    Attributes:
        taken_at: Timezone-aware UTC timestamp. Naive datetimes are a bug.
        present: False when the machine has no battery, as on a CI runner.
        charge_pct: Current charge level, if readable.
        on_ac_power: Whether mains power is connected, if readable.
        design_capacity_wh: Original capacity as manufactured.
        full_charge_capacity_wh: Capacity the battery now charges to.
        cycle_count: Charge cycles. Absent on much firmware; a reported ``0``
            also means unknown, since no shipped battery has zero cycles.
        battery_count: Number of batteries found. Multi-battery laptops exist.
        source: How the values were obtained, e.g. ``"powercfg-xml"``. The same
            field read two different ways is not the same quality of
            measurement, and that matters when reading a long history.
    """

    taken_at: datetime
    present: bool
    charge_pct: float | None
    on_ac_power: bool | None
    design_capacity_wh: float | None
    full_charge_capacity_wh: float | None
    cycle_count: int | None
    battery_count: int
    source: str


@dataclass(frozen=True, slots=True)
class ThermalSnapshot:
    """A single temperature reading from one sensor.

    Attributes:
        taken_at: Timezone-aware UTC timestamp.
        sensor_label: Which sensor this came from, e.g. ``"x86_pkg_temp"``.
        temp_c: Degrees Celsius.
        is_throttling: True when throttling was detected, None when unknown.
        throttling_inferred: True when throttling was derived from clock speed
            rather than read from a flag.
        confidence: How much this reading can be trusted on this platform.
        source: How the value was obtained.
    """

    taken_at: datetime
    sensor_label: str
    temp_c: float | None
    is_throttling: bool | None
    throttling_inferred: bool
    confidence: Confidence
    source: str


@dataclass(frozen=True, slots=True)
class StorageSnapshot:
    """A single reading for one fixed drive.

    Attributes:
        taken_at: Timezone-aware UTC timestamp.
        mount: Mount point or drive letter.
        device_model: Drive model, if readable.
        total_bytes: Capacity of the filesystem.
        free_bytes: Free space on the filesystem.
        smart_ok: SMART overall health, None when not readable without
            elevation.
        source: How the values were obtained.
    """

    taken_at: datetime
    mount: str
    device_model: str | None
    total_bytes: int
    free_bytes: int
    smart_ok: bool | None
    source: str


@dataclass(frozen=True, slots=True)
class Advisory:
    """One piece of actionable advice.

    Raw numbers are not the product; anyone can read a sensor. The value is a
    sentence a non-expert can act on today, which is why ``action`` is required
    and must name something the owner can actually do.

    Attributes:
        severity: How urgent this is.
        metric: What it is about, e.g. ``"battery.wear"``.
        cause: Plain-language cause, naming the actual measurement.
        action: Something the owner can do today. Never an offer to change a
            hardware setting on their behalf.
        confidence: How much the underlying reading can be trusted.
    """

    severity: Severity
    metric: str
    cause: str
    action: str
    confidence: Confidence
