"""Hardware access: one adapter per operating system.

This is the only package allowed to call into the operating system. Adapters
implement :class:`~lapguardian.core.provider.MetricsProvider` and return
:mod:`lapguardian.core.models` objects. They must not import from
``lapguardian.cli`` or ``lapguardian.storage``.

Subprocess discipline applies to everything here, because this is the whole
attack surface: argument lists and never ``shell=True``, an explicit timeout on
every call, explicit output decoding, no interpolation of configuration or
sensor output into a command, and ``finally`` cleanup of any file an OS tool
creates. See ``AGENTS.md`` section 5 and ``SECURITY.md``.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lapguardian.core.provider import MetricsProvider

__all__ = ["get_provider"]


def get_provider() -> MetricsProvider:
    """Return the metrics provider for the current operating system.

    This is the only function in the codebase that branches on the operating
    system. Anything else that needs to know what platform it is running on is
    a bug.

    An unrecognised platform gets a null provider that reports every metric as
    unavailable with a clear reason, rather than raising: an unsupported OS
    should produce a useful message, not a traceback.

    Returns:
        An adapter satisfying the MetricsProvider protocol.
    """
    # TODO(TASK-004): dispatch on sys.platform. See docs/TASKS.md.
    # TODO(TASK-018): null provider for unsupported platforms.
    raise NotImplementedError
