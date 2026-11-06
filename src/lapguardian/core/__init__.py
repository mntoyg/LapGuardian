"""Domain layer: hardware-agnostic models, health arithmetic and advice.

Nothing in this package may import ``platform``, ``sys.platform``,
``subprocess``, ``psutil``, or anything from ``lapguardian.platforms``. The
domain depends only on the :class:`~lapguardian.core.provider.MetricsProvider`
protocol it defines itself, which is what allows the advisor to be tested
without any real hardware.

See ``AGENTS.md`` section 4 for the enforceable layer rules.
"""
