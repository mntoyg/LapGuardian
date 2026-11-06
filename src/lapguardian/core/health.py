"""Health arithmetic: wear, derived metrics and trends.

Pure functions of their inputs, with no knowledge of where the numbers came
from. This is the most frequently changed code in the project, so it is also
the easiest to test.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence

    from lapguardian.core.models import BatterySnapshot

__all__ = ["battery_wear_pct", "capacity_trend_wh_per_month"]


def battery_wear_pct(
    design_capacity_wh: float | None,
    full_charge_capacity_wh: float | None,
) -> float | None:
    """Return battery wear as a percentage of original design capacity.

    Wear is ``(1 - full_charge / design) * 100``.

    Returns ``None`` rather than a zero whenever the inputs do not support a
    real answer. Returning ``0.0`` for a missing reading would mean "this
    battery is like new", which is a very different and much worse claim than
    "we do not know".

    Some firmware reports a full-charge capacity above the design capacity
    after a recalibration. The result is clamped at ``0`` in that case rather
    than returned as a negative number.

    Args:
        design_capacity_wh: Original capacity as manufactured.
        full_charge_capacity_wh: Capacity the battery now charges to.

    Returns:
        Wear percentage in the range 0 to 100, or ``None`` if it cannot be
        computed.
    """
    # TODO(TASK-003): implement. See docs/TASKS.md.
    raise NotImplementedError


def capacity_trend_wh_per_month(snapshots: Sequence[BatterySnapshot]) -> float | None:
    """Return the rate of capacity loss over a series of snapshots.

    Must be robust to gaps in the series: a month with no readings, or a month
    where the capacity was unavailable, is a gap and not a change.

    Args:
        snapshots: Battery snapshots, in any order.

    Returns:
        Watt-hours of full-charge capacity lost per month, or ``None`` when
        there is not enough data to say.
    """
    # TODO(TASK-022): implement. See docs/TASKS.md.
    raise NotImplementedError
