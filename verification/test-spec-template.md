# Test spec: <area or plan>

Copy to `verification/test-spec-<area>.md`. One row per rule that the tests must
prove, above all the rules that are in no code or document: behavior that lives in how
people operate, found by asking a practitioner how they handle a case and how often
it happens. Write the rows before the code. Tests and end-to-end checks are written
from the rows, not from the new implementation.

Prevents: tests written from the new code passing the same misunderstanding the code
has.

| # | Rule (knowledge entry) | Given | When | Then (expected) | Expected value from | Covered by |
|---|---|---|---|---|---|---|
| 1 | `docs/knowledge/<area>.md` <rule> | <starting state> | <action> | <result> | <practitioner role, date> | <test path> / <end-to-end check> / not yet |

Run the end-to-end checks in an environment set up like the one practitioners use,
before release and again after release.
