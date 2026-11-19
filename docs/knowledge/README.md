# Knowledge

Domain rules the agents must follow, one file per topic. Copy `_template.md`.

Prevents: the agent re-implementing something that looks like the legacy behavior but
is not, and repeating a mistake that was already found once.

Sources, in the order of how much to trust them:

1. A practitioner who works with the process confirmed it.
2. The legacy code does it, and a practitioner agrees it is intended.
3. A reconciliation against a source outside the code found a wrong value
   (see `verification/`).

An entry without a source is a guess. Mark it `unconfirmed` and do not build on it.

Entries go stale. Put a date on each one and re-check the ones you rely on.
