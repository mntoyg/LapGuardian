# AIDER.md — Aider in LapGuardian

> **Read [`AGENTS.md`](AGENTS.md) first.** It is the canonical engineering
> contract: stack, commands, layer rules, coding standards, hard rules,
> workflow and commit format. This file only covers what is specific to Aider.
> Nothing here overrides `AGENTS.md`.

## Your role

Aider handles **narrow, mechanical work** across the codebase. You may touch
any file, but only within a tightly scoped task — you are the only agent
without an exclusive area, and that privilege comes with the strictest scope
limit.

**Good tasks for you:**

- Adding or correcting type hints to satisfy `mypy --strict`.
- Writing or fixing Google-style docstrings.
- Mechanical renames and import reordering.
- Replacing `os.path` with `pathlib` (lint rule `PTH`).
- Replacing naive `datetime.now()` with `datetime.now(tz=timezone.utc)`
  (lint rule `DTZ`).
- Applying a single `ruff` rule across the project.
- Fixing a typo in a docstring, comment or document.

**Not your tasks:**

- Designing anything. Architecture and domain decisions belong to Claude.
- Writing a platform adapter or a parser. That is Codex.
- Changing CLI behaviour or config defaults. That is Cursor.
- Anything that changes what the program does.

If a task you picked up turns out to require a design decision, **stop and hand
it back**. Note what you found in the task row in
[`docs/TASKS.md`](docs/TASKS.md) and leave it unclaimed. A half-finished
mechanical change that quietly altered behaviour is the most expensive kind of
contribution.

## Scope discipline

- **One concern per commit.** Type hints in one commit, docstrings in another,
  even if you noticed both in the same file.
- **Add only the files you need** to the chat. Aider works better and cheaper
  with a small context, and a small context is also what keeps the diff narrow.
- **Never reformat a file you are not otherwise changing.** A whitespace-only
  diff across twenty files hides real changes from review.
- **Do not change behaviour.** If a type hint reveals a bug, do not fix the
  bug — file an issue and leave the hint correct or the file untouched.

## Hard rules that bite mechanical changes

Two of the project's hard rules are easy to break while "just tidying":

1. **Never turn a missing reading into a default.** You will see
   `MetricUnavailable` and `Optional[float]` all over `core/` and `platforms/`.
   Do not simplify `Optional[float]` to `float` with a `0.0` default to make
   mypy happy. That corrupts the user's history data silently. If mypy
   complains, the fix is a narrower type or an explicit check — never a
   fallback value.
2. **Never add a network import.** Not `requests`, `httpx`, `urllib`, or
   `socket`, not even in a docstring example.

Also: **`print()` is forbidden** (lint rule `T20`), and `datetime.now()`
without a timezone is forbidden (lint rule `DTZ`). If you are converting the
latter, use `timezone.utc`, not the local timezone — the history trend depends
on it.

## Before you commit

```bash
uv run ruff check . && uv run ruff format --check . && uv run mypy src && uv run pytest -v
```

The test count must not drop and no test may start skipping that was not
skipping before. Check that, do not assume it.

Then update your row in [`docs/STATUS.md`](docs/STATUS.md), and commit as
`style(...)`, `refactor(...)`, `docs(...)` or `chore(...)` with the task ID:

```text
refactor(platforms): replace os.path with pathlib (TASK-021)
docs(core): add missing docstrings to models (TASK-022)
```
