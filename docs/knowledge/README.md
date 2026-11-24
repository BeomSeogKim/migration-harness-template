# Knowledge

Domain rules the agents must follow: one file per domain area (copy `_template.md`),
one section per rule.

Prevents: the agent re-implementing something that looks like the legacy behavior but
is not, and repeating a mistake that was already found once.

Sources, in the order of how much to trust them:

1. A practitioner who works with the process confirmed it.
2. The legacy code does it, and a practitioner agrees it is intended.
3. A reconciliation against a source outside the code found a wrong value
   (see `verification/`).

An entry without a source is a guess. Mark it `unconfirmed` and do not build on it.

Priority decides what an agent reads first, because reading everything fills the
context window:

- **P0**: money and data integrity. Read before any change in the area.
- **P1**: how the core flows behave.
- **P2**: background and explanations of the legacy system.

Entries go stale, and an agent follows a stale entry as readily as a current one.
Put a date on each entry and re-check the ones you rely on. When a rule changes,
edit or delete the old entry in the same change instead of adding a second one.
