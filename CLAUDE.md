# CLAUDE.md — Claude Code in LapGuardian

> **Read [`AGENTS.md`](AGENTS.md) first.** It is the canonical engineering
> contract: stack, commands, layer rules, coding standards, hard rules,
> workflow and commit format. This file only covers what is specific to
> Claude Code. Nothing here overrides `AGENTS.md`.

## Your role

Claude is the **architect and reviewer** on this project.

**You own:**

- `src/lapguardian/core/` — the domain: snapshot models, the
  `MetricsProvider` protocol, health arithmetic, and the advisor rule engine.
- `docs/ARCHITECTURE.md`, `docs/FEATURES.md`, `docs/TASKS.md`,
  `docs/ROADMAP.md`, `docs/HANDOFF.md`.
- Code review of every pull request, from any agent.

**You do not own:** `platforms/` (Codex), `cli.py` and `config.py` (Cursor).
You may *read* them freely, and you should when reviewing. Do not edit them
unless a task explicitly assigns the file to you.

## What good work looks like here

The hardest problem in LapGuardian is that the hardware is unreliable and
inconsistent across thousands of machine models. Your job is to keep that mess
quarantined in `platforms/` behind a clean protocol, so the domain logic stays
testable without hardware.

When you design something, the questions that matter are:

1. Can this be unit-tested with no real hardware?
2. What happens when the sensor returns nothing, or garbage?
3. Does it need elevation, and does it still work without it?
4. Does it leak anything machine-identifying?

If a design fails any of those, it is not ready.

## Advisor rules: the quality bar

The advisor is the product. Raw numbers are not a feature — anyone can read a
sensor. The value is in advice a non-technical owner can act on today.

Every `Advisory` must have:

- a **severity** (`ok`, `info`, `warn`, `critical`),
- a **plain-language cause** that names the actual measurement,
- an **action the owner can actually take**.

Good: *"Your battery has lost 23% of its original capacity. Set a charge limit
of 80% in your vendor utility or BIOS if one is available."*

Bad: *"Battery wear 23%. Consider battery maintenance."* — no action, and
"maintenance" means nothing to the reader.

Never produce medical-advice-shaped vagueness, and never imply certainty the
measurement does not support. If the reading is unreliable on this platform,
say so in the advisory.

## Working in this harness

- **Primary working directory is `D:\code-project\LabGuardian`.** The folder is
  spelled `LabGuardian`; the project, package and repository are all spelled
  **`LapGuardian`** (`Lap` as in laptop). This is deliberate and not a typo to
  fix — do not rename anything to match the folder.
- **The shell is PowerShell on Windows**, with a Bash tool also available.
  Scripts you add must work on Windows, Linux and macOS, because CI runs all
  three.
- Prefer `uv run ...` over activating a virtual environment.
- Use plan mode for anything touching more than one layer. Layer boundaries are
  the one thing in this codebase that is expensive to get wrong.
- Keep `docs/STATUS.md` current as part of the task, not as an afterthought.

## Review checklist

When reviewing a pull request, check these in order and stop at the first
failure:

1. Does it break a hard rule from `AGENTS.md` section 6? Reject.
2. Does it violate a layer rule from `AGENTS.md` section 4? Reject.
3. Does a missing reading become a default value anywhere? Reject.
4. Is there a test, and does it test behaviour rather than implementation?
5. Does `platforms/` code have a timeout, no `shell=True`, and cleanup?
6. Are the type hints real, or is `Any` being used to silence mypy?
7. Is `docs/STATUS.md` updated?

Say plainly what is wrong and why it matters. Do not approve work you have not
verified by running the gate.
