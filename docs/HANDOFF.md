# Handoff — Multi-Agent Work Division

Owner: Claude. How four AI agents and a human lead work on one codebase without
overwriting each other.

The canonical engineering rules are in [`AGENTS.md`](../AGENTS.md). This file
covers **who does what, and how work passes between them.**

---

## 1. Why file ownership is exclusive

Four agents editing the same files is not a theoretical risk, it is the default
outcome. Two agents that both "improved" `cli.py` in the same hour produce a
conflict neither of them can resolve, because neither has the other's context.

So ownership here is **exclusive, not advisory**. Reading any file is always
fine and often necessary. Editing a file you do not own requires a task that
explicitly assigns it to you.

## 2. Who owns what

| Agent | Role | Owns (may edit) | Reads freely |
|---|---|---|---|
| **Claude** | Architect and reviewer | `src/lapguardian/core/`, `src/lapguardian/storage/`, `docs/ARCHITECTURE.md`, `docs/FEATURES.md`, `docs/TASKS.md`, `docs/ROADMAP.md`, `docs/HANDOFF.md` | everything |
| **Codex** | Platform adapters and tests | `src/lapguardian/platforms/`, `tests/` | everything |
| **Cursor** | CLI, config, refactors | `src/lapguardian/cli.py`, `src/lapguardian/config.py`, `lapguardian.example.toml` | everything |
| **Aider** | Narrow mechanical work | any file, within a single-concern task | everything |
| **Human lead** | Direction and release | `docs/MASTER_BLUEPRINT.md`, `docs/VISION.md`, `LICENSE`, release and PyPI | everything |

`docs/STATUS.md` is written by **whoever completed a task**, one at a time, and
only to record their own work.

Per-agent instructions: [`CLAUDE.md`](../CLAUDE.md), [`CODEX.md`](../CODEX.md),
[`CURSOR.md`](../CURSOR.md), [`AIDER.md`](../AIDER.md).

### Why these splits

- **Claude holds `core/` and `storage/`** because those are where a wrong
  decision is expensive. The layer boundaries and the `MetricUnavailable`
  discipline are the whole architecture, and they need one consistent hand.
- **Codex holds `platforms/` and `tests/`** because they are the same job.
  Sensor coverage is defined by its golden files; whoever writes the parser
  must write the fixture, or the fixture never arrives.
- **Cursor holds the user-facing surface** because CLI and config churn
  frequently and benefit from fast multi-file iteration, while being the lowest
  risk to get wrong.
- **Aider holds nothing exclusively** and therefore has the tightest scope
  rule: one concern per commit, no behaviour change.

## 3. The workflow, every time

```text
 1. Read AGENTS.md, then docs/ARCHITECTURE.md
 2. Pick a task from docs/TASKS.md where:
      - status is `todo`
      - every dependency is `done`
      - the files are yours
 3. Claim it: status -> `in-progress`, your name in Owner. Commit that claim.
 4. Write the failing test
 5. Implement
 6. Run the gate and READ the output:
      uv run ruff check . && uv run ruff format --check .
      uv run mypy src && uv run pytest -v
 7. Update docs/STATUS.md
 8. Commit:  feat(scope): what changed (TASK-0NN)
 9. Open a pull request. Claude reviews.
```

Step 3 matters: **claiming is a commit**, not an intention. An uncommitted
claim is invisible to the other agents.

Step 6 matters: do not report a task done without having run the gate and
looked at what it said. "It should pass" is not a result.

## 4. Collision rules

1. **One task, one agent.** If a task is `in-progress` under another name, pick
   a different one.
2. **Never edit outside your area** without a task that assigns the file.
3. **`docs/STATUS.md`: one writer at a time**, recording only your own work.
4. **Found a problem outside your area?** File an issue and assign it to the
   owner. Do not fix it, however small — a drive-by fix in someone else's file
   is how conflicts start.
5. **Blocked by another agent's unfinished work?** Set your task to `blocked`,
   note what you are waiting for, and pick something else.
6. **The protocol does not fit the hardware?** If `MetricsProvider` cannot
   express what a platform gives you, that is a finding for Claude, not
   something to work around inside the adapter. Open an issue.

## 5. Handoff points

The places where work genuinely crosses an agent boundary. Each is a real
dependency, not a courtesy.

| From | To | Handoff | Blocks |
|---|---|---|---|
| Claude → Codex | `MetricsProvider` protocol and models (TASK-001, TASK-002) | Codex cannot write an adapter against a protocol that does not exist | all of M1–M2 |
| Codex → Cursor | A working provider (TASK-005) | `scan` has nothing to render until something reads a sensor | TASK-009 |
| Claude → Cursor | `Advisory` and `Severity` types (TASK-001) | Cursor needs the shape to render it | TASK-010 |
| Claude → Cursor | Advisor rules (TASK-025 onward) | `--fail-on` needs severities to act on | TASK-030 |
| Codex → Claude | Findings about what the hardware actually provides | May change the protocol or the models | varies |
| Anyone → Claude | Pull request | Review before merge | merge |
| Claude → human lead | M6 readiness | Only the human can publish to PyPI | TASK-035, TASK-036 |

**The critical path right now:** TASK-001 and TASK-002 block almost everything
else. Claude goes first in M1; Codex and Cursor have nothing real to do until
the protocol lands.

## 6. Review

Claude reviews every pull request, including its own work from another session.
Check in this order and stop at the first failure:

1. Does it break a **hard rule** (`AGENTS.md` section 6 — network, telemetry,
   fabricated readings, required elevation, machine data in the repo)? Reject.
2. Does it break a **layer rule** (`AGENTS.md` section 4)? Reject.
3. Does a missing reading become a default value anywhere? Reject.
4. Is there a test, and does it test behaviour rather than implementation?
5. Does `platforms/` code have a timeout, no `shell=True`, explicit decoding,
   and `finally` cleanup?
6. Are the type hints real, or is `Any` being used to silence mypy?
7. Is `docs/STATUS.md` updated?

Say plainly what is wrong and why it matters. Do not approve work you have not
verified by running the gate yourself.

## 7. Context each agent needs

Reading everything every time is slow and expensive. Minimum viable context by
role:

| Agent | Read first | Then |
|---|---|---|
| Claude | `AGENTS.md`, `CLAUDE.md`, `ARCHITECTURE.md` | `FEATURES.md`, `TASKS.md`, `STATUS.md` |
| Codex | `AGENTS.md`, `CODEX.md`, `ARCHITECTURE.md` §7–9 | `core/models.py`, `core/provider.py`, the task |
| Cursor | `AGENTS.md`, `CURSOR.md`, `FEATURES.md` F-07/F-08 | `core/models.py`, the task |
| Aider | `AGENTS.md`, `AIDER.md` | only the task and the files it names |

The AI ignore files already keep generated output, lock files, binary assets
and the local health database out of context. Do not add exceptions to them.

## 8. When an agent gets it wrong

It will happen. The recovery is the same every time:

- **Wrong layer.** Revert and re-do it in the right place. Do not leave logic
  in `cli.py` with a note to move it later — later does not come.
- **A default value substituted for a missing reading.** Treat it as a bug with
  the highest priority, because it corrupts data silently and the corruption is
  nearly undetectable afterwards.
- **Edited someone else's file.** Revert that part, file an issue for the owner.
- **Task marked done without running the gate.** Reopen it. The claim was not
  true.

No blame attached to any of these. The cost is in leaving them in place, not in
making them.
