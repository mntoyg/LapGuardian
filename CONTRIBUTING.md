# Contributing to LapGuardian

Thanks for considering a contribution. This project exists to keep working
laptops out of landfill, and the hardest part of it — reading sensors reliably
across thousands of machine models — is something no single developer can do
alone.

## Before you write code

1. Read [`AGENTS.md`](AGENTS.md). It is the engineering contract: stack,
   commands, coding standards, commit format, and hard rules. It applies to
   human and AI contributors equally.
2. Read [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) so your change lands in
   the right layer.
3. Pick an item from [`docs/TASKS.md`](docs/TASKS.md). If what you want to do
   is not there, open an issue first so we can agree on the shape of it before
   you spend time.

## Development setup

LapGuardian uses [uv](https://docs.astral.sh/uv/). Install it, then:

```bash
git clone https://github.com/mntoyg/LapGuardian.git
cd LapGuardian
uv sync --extra dev
```

That creates `.venv/` and installs the project in editable mode along with the
dev tooling.

## The quality gate

Every one of these must pass before you open a pull request. CI runs the same
commands on Linux, Windows and macOS across Python 3.10 to 3.13.

```bash
uv run ruff check .
```

```bash
uv run ruff format --check .
```

```bash
uv run mypy src
```

```bash
uv run pytest -v
```

To fix formatting rather than just check it:

```bash
uv run ruff format .
```

```bash
uv run ruff check --fix .
```

## Testing philosophy

Hardware is the untrustworthy part of this system, so the tests are built to
keep it out of the way of the logic:

- **`core/` is tested without hardware.** It depends on the `MetricsProvider`
  protocol, never on an operating system. Use the fake provider fixture in
  `tests/conftest.py`.
- **Platform parsers are tested with golden files.** Capture the real output of
  a command on a real machine, commit it to `tests/fixtures/<os>/`, and assert
  that the parser turns it into the expected snapshot. This is how we support
  hardware none of us owns.
- **Integration tests are marked and skipped elsewhere.** Use
  `@pytest.mark.windows`, `@pytest.mark.needs_battery`,
  `@pytest.mark.needs_admin` and friends. A test that cannot run must skip with
  a clear reason, never fail.

If you own unusual hardware, **a golden file is a first-class contribution.**
Run the relevant command, scrub your hostname and username out of the output,
and send it in.

## Commit messages

[Conventional Commits](https://www.conventionalcommits.org/), with the task ID
at the end when one applies:

```text
feat(core): add battery wear calculation (TASK-003)
fix(platforms): handle missing cycle_count on Linux (TASK-011)
docs(architecture): document the privilege boundary
test(platforms): add golden file for Dell XPS 13 battery report
chore(ci): pin setup-uv to v5
```

Allowed types: `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `style`,
`chore`, `build`, `ci`, `revert`.

Scopes map to the code layout: `core`, `platforms`, `storage`, `cli`, `config`,
`docs`, `ci`.

## Pull requests

- One task per pull request. If you found a second problem on the way, file it
  as an issue rather than widening the diff.
- Fill in the PR template, including the task ID.
- Update [`docs/STATUS.md`](docs/STATUS.md) in the same PR.
- A PR that changes behaviour without a test will be asked for a test.

## Hard rules

These exist because they are the whole promise of the project. A pull request
that breaks one will be rejected on principle, not on style:

1. **No network calls.** Not for updates, not for analytics, not for anything.
2. **No telemetry, no accounts, no identifiers.**
3. **Never fabricate a reading.** A metric that cannot be read is
   `MetricUnavailable` with a reason. Zero is a measurement, not a fallback.
4. **Never require administrator privileges to run.** Elevated metrics are
   strictly optional extras.
5. **Never write outside the user's own application-data directory** without
   them asking, and clean up temporary files that OS tools create.

## Reporting a bug

Use the bug report template. Include your OS version, laptop model, and the
output of `lapguardian scan --debug`. Scrub anything personal first — and if
the debug output contains something personal that we did not expect, that is
itself a bug worth reporting.

## Security

Do not open a public issue for a vulnerability. See [`SECURITY.md`](SECURITY.md).

## Code of conduct

By participating you agree to [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).
