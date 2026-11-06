"""Settings: thresholds and paths, loaded from TOML with documented defaults.

Every field has a default, so LapGuardian works correctly with no
configuration file at all. ``lapguardian.example.toml`` documents why each
default has the value it has, and must be updated in the same commit as any
change here.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

__all__ = ["Settings", "config_file_path", "data_dir"]


class Settings(BaseModel):
    """Runtime configuration for LapGuardian.

    Defaults are starting points for a typical consumer laptop, not
    manufacturer specifications. A gaming laptop idles hotter than an
    ultrabook, which is why these are tunable.
    """

    # TODO(TASK-031): implement the real settings model with a TOML source,
    # nested sections ([battery], [thermal], [storage], [history], [report],
    # [privacy]) and validation. See docs/TASKS.md and lapguardian.example.toml.


def data_dir() -> Path:
    """Return the platform application-data directory for LapGuardian.

    Windows uses ``%LOCALAPPDATA%``, Linux ``$XDG_DATA_HOME`` falling back to
    ``~/.local/share``, and macOS ``~/Library/Application Support``.

    Nothing is ever written next to the executable or inside the repository.
    """
    # TODO(TASK-031): implement. See docs/TASKS.md.
    raise NotImplementedError


def config_file_path() -> Path:
    """Return where the configuration file is expected to live.

    Printed by ``lapguardian config path``. The file need not exist.
    """
    # TODO(TASK-031): implement. See docs/TASKS.md.
    raise NotImplementedError
