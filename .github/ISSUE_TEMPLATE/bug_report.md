---
name: Bug report
about: Something LapGuardian got wrong, or a metric it cannot read on your machine
title: "[bug] "
labels: bug
---

## What happened

<!-- What did you expect, and what did you get instead? -->

## Your machine

Sensor coverage is the hardest part of this project, so hardware details are
not optional here.

- **Operating system and version:**
- **Laptop make and model:**
- **CPU:**
- **LapGuardian version:** <!-- output of `lapguardian version` -->
- **Python version:** <!-- output of `python --version` -->
- **Running elevated?** <!-- Administrator / sudo / no -->

## Output of `lapguardian scan --debug`

<!--
Paste it in the block below.

Please scrub anything personal first. If you find your hostname, username or
home directory path in there, that is itself a bug worth telling us about -
`--debug` is not supposed to include them.
-->

```text

```

## A reading that looks wrong?

If LapGuardian reported a number you believe is incorrect, what does your
vendor utility or operating system report instead?

| | LapGuardian | What you expected |
|---|---|---|
| Metric | | |

## Would you be willing to contribute a golden file?

If a parser is getting your hardware wrong, the fix usually needs the real
output of the underlying command. Captured output with identifiers scrubbed is
the most valuable thing you can send, and it makes your machine permanently
supported. See `CONTRIBUTING.md`.

- [ ] Yes, I can capture and scrub the raw command output
