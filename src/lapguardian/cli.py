"""Command-line interface.

Presentation only. This module parses arguments, calls into
:mod:`lapguardian.core`, and renders the result. It contains no business logic:
if a comparison here would need to change when a threshold changes, that
comparison belongs in :mod:`lapguardian.core.advisor`.

Output conventions:

* ``--json`` writes only JSON to stdout, so it pipes cleanly. Human messages go
  to stderr.
* Severity is carried by a word as well as a colour, so the output is readable
  with ``NO_COLOR=1`` and in a log file.
* No emoji: too many Windows terminals mangle them.
* Exit ``0`` means LapGuardian ran, even if it found critical problems.
  Non-zero means LapGuardian itself failed.
"""

from __future__ import annotations

import typer
from rich.console import Console

from lapguardian import __version__

__all__ = ["app", "main"]

app = typer.Typer(
    name="lapguardian",
    help=(
        "Battery, thermal and storage health advisor for any laptop. "
        "Offline, privacy-first, no telemetry."
    ),
    no_args_is_help=True,
    add_completion=False,
)
config_app = typer.Typer(help="Inspect configuration.", no_args_is_help=True)
app.add_typer(config_app, name="config")

# Human-facing output goes to stderr so that stdout stays clean for --json.
err = Console(stderr=True)

_NOT_YET = (
    "Not implemented yet. The project is at milestone M0 (foundation): "
    "documentation, architecture and scaffold are in place, metric collection "
    "is not. See docs/STATUS.md for what works today and docs/ROADMAP.md for "
    "what lands next."
)


def _not_implemented(task: str) -> None:
    """Report an unimplemented command and exit non-zero.

    Args:
        task: The task ID in ``docs/TASKS.md`` that will implement it.

    Raises:
        typer.Exit: Always, with code 1.
    """
    err.print(f"[yellow]lapguardian:[/yellow] {_NOT_YET}")
    err.print(f"[dim]Tracked as {task} in docs/TASKS.md.[/dim]")
    raise typer.Exit(code=1)


@app.callback()
def _root() -> None:
    """Battery, thermal and storage health advisor for any laptop."""


@app.command()
def version() -> None:
    """Print the LapGuardian version and exit."""
    err.print(f"lapguardian {__version__}")


@app.command()
def scan(
    save: bool = typer.Option(False, "--save", help="Append a snapshot to the local history."),
    as_json: bool = typer.Option(False, "--json", help="Emit JSON on stdout and nothing else."),
    debug: bool = typer.Option(False, "--debug", help="Explain every unavailable metric."),
) -> None:
    """Run a one-off health check."""
    # TODO(TASK-009): implement. See docs/TASKS.md.
    # TODO(TASK-010): Rich rendering, readable without colour.
    # TODO(TASK-023): --save, once storage lands.
    _not_implemented("TASK-009")


@app.command()
def report() -> None:
    """Show a full report, including the history trend."""
    # TODO(TASK-023): implement, depends on history. See docs/TASKS.md.
    _not_implemented("TASK-023")


@app.command()
def history(
    days: int = typer.Option(90, "--days", min=1, help="How far back to look."),
) -> None:
    """Show how the machine has changed over time."""
    # TODO(TASK-023): implement. See docs/TASKS.md.
    _not_implemented("TASK-023")


@app.command()
def export(
    fmt: str = typer.Option("markdown", "--format", help="One of: json, csv, markdown."),
    out: str = typer.Option(..., "--out", help="File to write."),
) -> None:
    """Write a health report to a file."""
    # TODO(TASK-033): implement. See docs/TASKS.md.
    _not_implemented("TASK-033")


@app.command()
def watch(
    interval: int = typer.Option(30, "--interval", min=1, help="Seconds between readings."),
) -> None:
    """Poll the sensors in the foreground until interrupted."""
    # TODO(TASK-034): implement. Foreground only, never a daemon.
    _not_implemented("TASK-034")


@config_app.command("path")
def config_path() -> None:
    """Print where the configuration file is expected to live."""
    # TODO(TASK-032): implement. See docs/TASKS.md.
    _not_implemented("TASK-032")


def main() -> None:
    """Console-script entry point."""
    app()
