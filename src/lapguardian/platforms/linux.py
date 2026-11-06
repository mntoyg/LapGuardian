"""Linux metrics adapter.

Data sources, with their traps:

* **Battery capacity** - ``/sys/class/power_supply/BAT*/``. Some kernels expose
  ``energy_full_design`` and ``energy_full`` in microwatt-hours; others expose
  ``charge_full_design`` and ``charge_full`` in microamp-hours, which must be
  multiplied by ``voltage_min_design`` to get energy. Both shapes must be
  handled.
* **Cycle count** - ``cycle_count``, frequently absent or reported as ``0``.
  Both mean unknown; no shipped battery has zero cycles.
* **Temperature** - ``psutil.sensors_temperatures()``, falling back to
  ``/sys/class/thermal/thermal_zone*/temp`` in millidegrees. Prefer the zone
  whose type is ``x86_pkg_temp``, ``coretemp`` or ``cpu-thermal``.
* **SMART** - ``smartctl --json=c -A``, which needs root.

Always glob ``BAT*``; never assume ``BAT0``. Multi-battery laptops exist, and
their capacities are summed with the count reported.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lapguardian.core.models import (
        BatterySnapshot,
        MetricUnavailable,
        StorageSnapshot,
        SystemInfo,
        ThermalSnapshot,
    )

__all__ = ["LinuxProvider"]


class LinuxProvider:
    """Reads health metrics on Linux."""

    def system_info(self) -> SystemInfo:
        """Return OS, machine model and CPU model."""
        # TODO(TASK-012): implement. See docs/TASKS.md.
        raise NotImplementedError

    def battery(self) -> BatterySnapshot | MetricUnavailable:
        """Return the battery reading, or why it is unavailable."""
        # TODO(TASK-012): read sysfs, handling both uWh and uAh shapes.
        raise NotImplementedError

    def thermal(self) -> list[ThermalSnapshot] | MetricUnavailable:
        """Return temperature readings from the preferred CPU zone."""
        # TODO(TASK-013): psutil first, /sys/class/thermal as fallback.
        raise NotImplementedError

    def storage(self) -> list[StorageSnapshot] | MetricUnavailable:
        """Return readings for every fixed drive."""
        # TODO(TASK-014): free space, optional smartctl --json=c.
        raise NotImplementedError
