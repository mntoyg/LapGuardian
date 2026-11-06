"""Windows metrics adapter.

Data sources, with their traps:

* **Battery capacity and cycle count** - ``powercfg /batteryreport /xml``.
  The report it writes contains the machine name and the user profile path, so
  it goes to a private temporary directory and is deleted in a ``finally``
  block.
* **Charge level and AC state** - ``psutil.sensors_battery()``, which returns
  ``None`` on a machine with no battery.
* **CPU temperature** - ``MSAcpi_ThermalZoneTemperature`` in the WMI root
  namespace. Unreliable on most consumer laptops: frequently absent, constant,
  or reporting a chipset zone rather than the CPU package. Values are in tenths
  of a Kelvin. Readings are reported as low confidence, and this is a
  documented limitation rather than a bug to fix. See
  ``docs/ARCHITECTURE.md`` section 9.
* **Storage** - ``shutil.disk_usage()`` always works; ``Get-PhysicalDisk`` and
  ``Get-StorageReliabilityCounter`` need Administrator for SMART.

PowerShell is invoked with ``-NoProfile -NonInteractive`` and
``ConvertTo-Json``, because parsing JSON is far less fragile than parsing
table output. Standard output is decoded explicitly rather than relying on the
console code page.
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

__all__ = ["WindowsProvider"]


class WindowsProvider:
    """Reads health metrics on Windows."""

    def system_info(self) -> SystemInfo:
        """Return OS, machine model and CPU model."""
        # TODO(TASK-005): implement. See docs/TASKS.md.
        raise NotImplementedError

    def battery(self) -> BatterySnapshot | MetricUnavailable:
        """Return the battery reading, or why it is unavailable."""
        # TODO(TASK-005): parse powercfg /batteryreport /xml; delete the temp
        # file in a finally block.
        # TODO(TASK-006): charge level and AC state via psutil.
        raise NotImplementedError

    def thermal(self) -> list[ThermalSnapshot] | MetricUnavailable:
        """Return temperature readings, honestly labelled as low-confidence."""
        # TODO(TASK-007): attempt MSAcpi_ThermalZoneTemperature; convert from
        # tenths of a Kelvin; infer throttling from Win32_Processor clocks.
        raise NotImplementedError

    def storage(self) -> list[StorageSnapshot] | MetricUnavailable:
        """Return readings for every fixed drive."""
        # TODO(TASK-008): free space via shutil, SMART via Get-PhysicalDisk.
        raise NotImplementedError
