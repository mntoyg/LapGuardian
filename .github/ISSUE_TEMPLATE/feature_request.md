---
name: Feature request
about: Something LapGuardian should do
title: "[feature] "
labels: enhancement
---

## The problem

<!--
What are you unable to do today? Describe the situation, not the solution.
-->

## What you would like

<!-- What should LapGuardian do about it? -->

## Have you checked the existing plans?

A lot is already designed but not yet built. Please check before filing:

- [ ] I checked [`docs/FEATURES.md`](../../docs/FEATURES.md) (F-01 to F-12) and
      this is not already there
- [ ] I checked [`docs/ROADMAP.md`](../../docs/ROADMAP.md) and this is not
      already planned for a later milestone
- [ ] I checked the permanent non-goals in
      [`docs/VISION.md`](../../docs/VISION.md)

## About those non-goals

Some things will never be added, however often they are requested. The most
common ones:

- **Anything involving a network request** — no update check, no analytics, no
  cloud sync. This is the project's core promise and the only version of it
  that a user can verify.
- **Accounts, device IDs or telemetry.**
- **Changing a hardware setting for you** — setting a charge threshold, a fan
  curve or a power limit. That means writing to vendor-specific embedded
  controllers, which is per-brand and risks leaving someone with a laptop that
  will not charge. LapGuardian tells you where the setting is; you change it.
- **A bundled kernel driver**, which is what real Windows temperature access
  would require.

If your request is one of these, it will be closed with a pointer to
`docs/VISION.md` — not because it is a bad idea, but because it is a different
product.
