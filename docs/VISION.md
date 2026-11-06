# Vision

Owner: project lead. Changes go through an issue, not a direct edit.

---

## The one-sentence version

**A laptop should last as long as its owner needs it to, and the information
needed to make that happen should belong to the owner.**

## Why this project exists

The emissions of a laptop are dominated by its manufacture, not its use. So the
most effective thing an owner can do for the environment is not to buy a more
efficient machine — it is to keep the one they have for twice as long.

Most people cannot, not because they do not want to, but because nothing tells
them what is going wrong until it is too late to fix. The battery is already
worn out. The heatsink was already clogged for two years. The SSD has already
been running at 2% free since 2024.

All three of those are measurable on day one and all three are addressable with
a habit change or a can of compressed air. The data exists. The operating
system has it. Nobody surfaces it in a form a normal person can act on.

LapGuardian is a small tool with a narrow claim: **close that gap, and nothing
else.**

## What we are optimising for

In priority order, and the order matters when they conflict:

1. **Honesty.** A reading we did not take is reported as not taken. Never a
   plausible default, never an estimate presented as a measurement. A tool
   about hardware health that quietly invents numbers is worse than no tool,
   because it destroys the one thing it uniquely offers: a trustworthy history.
2. **Privacy.** The subject of this tool is the user's own machine. There is no
   version of that data we have any business seeing.
3. **Actionability.** Sensor dumps already exist and are excellent. Our
   contribution is the sentence that tells a non-expert what to do today.
4. **Breadth of hardware.** Brand neutrality is the point. A tool that only
   works on one vendor's laptops leaves out most of the laptops.
5. **Longevity of the tool itself.** It would be absurd for software about
   keeping hardware alive to stop working after two years. Few dependencies, no
   server to shut down, no account system to deprecate.

## Permanent non-goals

These are commitments. They are not a backlog, and a pull request implementing
one will be declined on principle.

### No network, ever

No update check. No analytics. No crash reporting. No license validation. No
"anonymous usage statistics". The project has no server and will not acquire
one.

This is absolute because it is the only version of the promise that can be
verified. "We only send anonymous data" cannot be checked by a user; "there is
no networking code in this program" can.

The `[privacy] allow_network = false` key in the config exists as a tripwire so
that a future contributor cannot introduce a request without a visible,
reviewable flag.

### No accounts, no identifiers

No sign-in, no device ID, no install ID, no fingerprint. The tool does not know
who you are and has no mechanism to find out.

### No cloud dashboard, no fleet management

That is a different product with a different business model and a different
relationship to the user's data. If someone wants it, the SQLite file is right
there and documented — build it separately.

### We read and advise; we never write to hardware

The most requested feature this project will ever get is "just set the charge
limit for me". We will not.

Doing so means writing to vendor-specific embedded controllers. It is
per-brand, undocumented, and carries a real risk of leaving someone with a
laptop that will not charge. LapGuardian tells you where the setting is in your
vendor utility or BIOS. You change it.

The same applies to fan curves, power limits and firmware. This tool will never
make a hardware state change.

### No bundled kernel driver

Real CPU temperature access on Windows needs one. It would also mean shipping a
signed driver, an installer, and a trust story completely unlike "a Python CLI
you can read". The honest answer is to document the limitation.

### No vendor SDKs

They are per-brand, frequently closed, and would quietly turn "works on any
laptop" into "works best on the brands we had time for".

## What the long term looks like

Not features for their own sake — these are the directions that would still
serve the one-sentence version above.

**Near term, after v0.1.** A TUI dashboard for people who want to watch rather
than query. Export formats that a repair shop can hand to a customer. More
golden files, which is the only real path to broad hardware support.

**Further out.** Richer trend analysis: projecting when a battery will fall
below a usable capacity, based on that machine's own measured history rather
than a generic curve. Detecting that thermals have drifted upward over months,
which is what a clogged heatsink actually looks like. These are the features
that need a year of history to be worth anything, which is why the local
database matters from the start.

**Possibly.** A desktop GUI, if someone who cares about GUIs wants to own it.
Packaging for the system package managers, so that installing it does not
require knowing what Python is.

**Never.** Anything in the non-goals above.

## How we will know it worked

Not by stars or downloads.

- Someone writes in to say they found 30% battery wear they did not know about
  and changed how they charge.
- A refurbisher uses it to grade used machines and tells a buyer the truth about
  a battery.
- A contributor who owns hardware none of the maintainers have ever seen sends
  a golden file, and that machine becomes supported.
- Somebody keeps a laptop a year longer than they otherwise would have.

One laptop not replaced is the whole point. Everything else is bookkeeping.
