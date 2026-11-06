# Status

**This file is the single source of truth for project progress.** If a task is
not marked done here, it is not done — regardless of what any other document,
commit message or conversation says.

`PROGRESS.md` does not exist by design. Two overlapping progress trackers
edited by four agents will always drift apart, and then neither can be trusted.

**Last updated:** 2026-11-06 · **Updated by:** Claude · **Milestone:** M0 Foundation

---

## Milestone progress

| Milestone | Progress | State |
|---|---|---|
| M0 Foundation | 100% | **done** |
| M1 Windows MVP | 0% | next |
| M2 Cross-platform | 0% | not started |
| M3 Persistence | 0% | not started |
| M4 Advisor | 0% | not started |
| M5 Polish | 0% | not started |
| M6 Release v0.1.0 | 0% | not started |

Definitions of done are in [`ROADMAP.md`](ROADMAP.md).

## What works today

```bash
uv sync --extra dev
uv run lapguardian --help
```

That is the honest extent of it. The CLI starts, prints help, and every
subcommand exits with a message saying it is not implemented yet.

**No metric collection exists.** Every collector in `platforms/` and every
function in `core/` is a documented stub that raises `NotImplementedError` and
carries a `# TODO(TASK-0NN):` comment pointing at
[`TASKS.md`](TASKS.md).

This is deliberate: M0 delivered the structure, the contracts and the quality
gate, so that M1 onward is implementation rather than architecture.

## In progress

Nothing. No task is claimed.

## Blocked

Nothing.

## Needs a decision from the human lead

| Item | Why it matters |
|---|---|
| **TASK-035 — claim `lapguardian` on PyPI** | Not checked yet. The name can be taken by anyone at any time, and M6 depends on it. Worth doing now rather than at release. |
| Local folder is named `LabGuardian`, project and repository are `LapGuardian` | Intentional and harmless — the `Lap` spelling is from "laptop". Renaming the folder is a local operation that does not affect git. Noted so nobody "fixes" it. |

## Completed

### M0 — Foundation (2026-11-06)

| Task | What landed |
|---|---|
| TASK-000 | Full documentation set, project scaffold, ignore rules, CI, repository published |

Specifically:

- **Documentation** — `MASTER_BLUEPRINT.md`, `VISION.md`, `ARCHITECTURE.md`,
  `FEATURES.md` (F-01 to F-12), `ROADMAP.md` (M0 to M6), `TASKS.md`,
  `HANDOFF.md`, and this file.
- **Contributor contract** — `AGENTS.md` as the canonical rules, with
  `CLAUDE.md`, `CODEX.md`, `CURSOR.md` and `AIDER.md` as thin role files that
  reference it rather than duplicating it.
- **Open-source basics** — `README.md`, `LICENSE` (MIT), `CONTRIBUTING.md`,
  `SECURITY.md`, `CODE_OF_CONDUCT.md`, `CHANGELOG.md`.
- **Ignore rules** — `.gitignore`, `.gitattributes`, and `.aiignore`,
  `.claudeignore`, `.codexignore`, `.cursorignore`, `.cursorindexingignore`,
  `.aiderignore`. All of them exclude the local health database and raw battery
  reports, which contain the machine name and user paths.
- **Packaging** — `pyproject.toml` with hatchling, and ruff, mypy, pytest and
  coverage configured rather than left at defaults.
- **Scaffold** — `src/lapguardian/` with the layer boundaries in place:
  `core/` (no OS knowledge), `platforms/` (the only place OS calls live),
  `storage/`, `cli.py`, `config.py`.
- **Schema** — `storage/schema.sql`, written in full including the
  `unavailable` table.
- **Config example** — `lapguardian.example.toml`, every threshold annotated
  with why it has that value.
- **CI** — GitHub Actions across Ubuntu, Windows and macOS on Python 3.10 to
  3.13, plus issue and pull request templates and Dependabot.

## Architectural decisions recorded so far

| Decision | Rationale |
|---|---|
| `core/` imports nothing OS-specific | Lets the advisor — the actual product — be tested with a fake provider on any runner |
| `MetricUnavailable` is a first-class type, not `None` | A missing reading must never become `0`; that silently corrupts the long-term trend |
| Golden-file testing for platform parsers | The only way to support hardware the maintainers do not own |
| UTC ISO-8601 text timestamps in SQLite | Sorts correctly, survives timezone changes; lint rule `DTZ` enforces it in code |
| `unavailable` is its own table | A metric that stopped being readable is itself a signal, and it keeps non-readings out of the metric tables |
| No daemon in v0.1 | The user's own scheduler does the same job without asking for trust we have not earned |
| We never write to hardware | Vendor EC writes are per-brand and risk bricking a machine. We say where the setting is |
| Windows thermal accepted as unreliable | Real access needs a kernel driver, which is out of scope. Reported honestly rather than guessed |

## Known limitations shipped as-is

These are documented constraints, not open bugs. See
[`ARCHITECTURE.md`](ARCHITECTURE.md) section 9.

- Windows CPU temperature is unreliable or unavailable without a kernel driver.
- SMART attributes need elevation on every platform.
- `cycle_count` is absent on much firmware, especially on Linux.
- CI runners have no battery, so live-hardware tests must skip there.

---

## How to update this file

Do it in the same commit as the work, not afterwards.

1. Move your task from the relevant milestone section into **Completed**, with
   the date.
2. Update the milestone percentage in the table.
3. Update **In progress** and **Blocked**.
4. Change the **Last updated** line at the top, including your name.
5. If you made an architectural decision, add a row to the decisions table with
   the reason. Future contributors need the reason more than the decision.

**One agent edits this file at a time**, and only to record its own work. Never
rewrite another agent's row.
