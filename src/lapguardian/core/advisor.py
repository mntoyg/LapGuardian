"""The rule engine: turns measurements into advice.

This module is the product. Raw sensor values are already available from other
tools; what LapGuardian adds is a sentence a non-expert can act on.

Structure: a list of small, independent rule functions, each taking the
computed metrics and the settings and returning zero or one
:class:`~lapguardian.core.models.Advisory`. Adding a rule must not require
touching any other rule.

Two rules the engine itself must enforce:

* An advisory is never produced from a
  :class:`~lapguardian.core.models.MetricUnavailable`. We do not advise on
  readings we did not take.
* An advisory never offers to change a hardware setting. LapGuardian reads and
  advises; it tells the owner where the setting lives. See the permanent
  non-goals in ``docs/VISION.md``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lapguardian.config import Settings
    from lapguardian.core.models import (
        Advisory,
        BatterySnapshot,
        StorageSnapshot,
        ThermalSnapshot,
    )

__all__ = ["evaluate"]


def evaluate(
    battery: BatterySnapshot | None,
    thermal: list[ThermalSnapshot] | None,
    storage: list[StorageSnapshot] | None,
    settings: Settings,
) -> list[Advisory]:
    """Evaluate every rule and return the advisories that fired.

    An empty list is a valid and desirable result: it means the machine is
    being looked after and there is nothing to say.

    Args:
        battery: Battery reading, or ``None`` when unavailable.
        thermal: Temperature readings, or ``None`` when unavailable.
        storage: Drive readings, or ``None`` when unavailable.
        settings: Thresholds from the configuration.

    Returns:
        Advisories, most severe first.
    """
    # TODO(TASK-025): implement the rule engine. See docs/TASKS.md.
    # TODO(TASK-026): battery wear rules.
    # TODO(TASK-027): charge-habit rules (F-02) - the reason this project exists.
    # TODO(TASK-028): thermal rules, sustained versus spike.
    # TODO(TASK-029): storage rules, on both percentage and absolute free space.
    raise NotImplementedError
