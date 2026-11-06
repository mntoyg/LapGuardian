# Changelog

All notable changes to LapGuardian are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added — M0 Foundation

- Master blueprint, vision, architecture and roadmap documentation under `docs/`.
- Feature registry (`docs/FEATURES.md`), backlog (`docs/TASKS.md`) and the
  single progress source of truth (`docs/STATUS.md`).
- Engineering contract in `AGENTS.md`, with per-agent instruction files for
  Claude, Codex, Cursor and Aider.
- Ignore rules for git and for every AI coding assistant in use, covering
  generated files, lock files, binary assets and — importantly — the local
  health database and raw battery reports that contain machine-identifying
  data.
- `.gitattributes` to keep line endings consistent between Windows development
  and Linux CI.
- Python packaging with `pyproject.toml` (hatchling), pinned tool
  configuration for ruff, mypy, pytest and coverage.
- Package scaffold under `src/lapguardian/` with the layer boundaries in place:
  `core/` (hardware-agnostic domain), `platforms/` (per-OS adapters),
  `storage/` (SQLite) and `cli.py`.
- SQLite schema (`src/lapguardian/storage/schema.sql`).
- Annotated example configuration (`lapguardian.example.toml`).
- GitHub Actions CI across Ubuntu, Windows and macOS on Python 3.10–3.13;
  issue and pull request templates; Dependabot.

### Notes

No metric collection is implemented in M0. Every collector is a documented stub
that raises `NotImplementedError` and references its task ID in
`docs/TASKS.md`.

[Unreleased]: https://github.com/mntoyg/LapGuardian/commits/main
