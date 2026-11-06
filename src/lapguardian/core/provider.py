"""The seam between the domain and the hardware.

:class:`MetricsProvider` is the only contract the domain knows about. Concrete
implementations live in :mod:`lapguardian.platforms`; the domain never imports
them. Tests supply a fake provider instead, which is what lets the advisor be
tested on a runner with no battery.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from lapguardian.core.models import (
    BatterySnapshot,
    MetricUnavailable,
    StorageSnapshot,
    SystemInfo,
    ThermalSnapshot,
)

__all__ = ["MetricsProvider"]


@runtime_checkable
class MetricsProvider(Protocol):
    """Reads hardware health metrics for the host it runs on.

    Implementations must never raise. Anything that cannot be read is returned
    as :class:`~lapguardian.core.models.MetricUnavailable` with a reason the
    user can understand. Nothing from ``subprocess``, CIM or ``/sys`` should
    ever surface above this boundary.
    """

    def system_info(self) -> SystemInfo:
        """Return identifying details about this machine."""
        ...

    def battery(self) -> BatterySnapshot | MetricUnavailable:
        """Return the current battery reading, or why it is unavailable."""
        ...

    def thermal(self) -> list[ThermalSnapshot] | MetricUnavailable:
        """Return readings for every readable temperature sensor."""
        ...

    def storage(self) -> list[StorageSnapshot] | MetricUnavailable:
        """Return readings for every fixed drive."""
        ...
