"""LapGuardian: an offline battery, thermal and storage health advisor.

LapGuardian reads hardware health metrics from the local machine, turns them
into actionable advice, and records them in a local SQLite database so the
owner can see long-term degradation trends.

It makes no network requests. See ``SECURITY.md`` in the project root.
"""

__all__ = ["__version__"]

__version__ = "0.0.0"
