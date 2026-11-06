"""macOS metrics adapter.

Data sources, with their traps:

* **Battery** - ``ioreg -rn AppleSmartBattery -a`` returns a property list.
  Parse it with :mod:`plistlib`, never with a regular expression. Relevant
  keys: ``DesignCapacity``, ``AppleRawMaxCapacity``, ``CycleCount``,
  ``PermanentFailureStatus``.
* **Charge level and AC state** - ``pmset -g batt`` or ``psutil``.
* **Temperature** - ``powermetrics --samplers smc`` needs sudo, so it is an
  optional extra. LapGuardian never prompts for elevation. Apple Silicon
  exposes different SMC keys from Intel.
* **Storage** - ``system_profiler SPStorageDataType -json``.
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

__all__ = ["MacOSProvider"]


class MacOSProvider:
    """Reads health metrics on macOS."""

    def system_info(self) -> SystemInfo:
        """Return OS, machine model and CPU model."""
        # TODO(TASK-015): implement. See docs/TASKS.md.
        raise NotImplementedError

    def battery(self) -> BatterySnapshot | MetricUnavailable:
        """Return the battery reading, or why it is unavailable."""
        # TODO(TASK-015): parse ioreg -a output with plistlib.
        raise NotImplementedError

    def thermal(self) -> list[ThermalSnapshot] | MetricUnavailable:
        """Return temperature readings when powermetrics is usable."""
        # TODO(TASK-016): powermetrics, sudo-optional. Never prompt.
        raise NotImplementedError

    def storage(self) -> list[StorageSnapshot] | MetricUnavailable:
        """Return readings for every fixed drive."""
        # TODO(TASK-016): system_profiler SPStorageDataType -json.
        raise NotImplementedError
