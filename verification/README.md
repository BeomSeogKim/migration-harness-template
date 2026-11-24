# Verification

Checks for migrated data and behavior. The correct answer lives outside the code you
are checking.

Prevents: data that loads cleanly and is still wrong, and behavior that passes tests
written from the same misunderstanding as the code. Row counts and foreign keys can
all pass while an amount is wrong.

Three kinds of check:

1. Structural checks, in `reconcile.sql`: row counts, orphaned foreign keys, required
   columns, status values, and totals compared between source and target. Run them
   at every migration step. They find loading bugs.
2. A source of truth outside the code. If the business keeps its own record of real
   amounts or states (a ledger, a billing export, a count a practitioner trusts),
   compare the migrated data with that record. This is the check that finds
   a wrong value that is structurally valid. Where no such record exists, the legacy
   database is the judge.
3. A test spec (`test-spec-template.md`) for rules a practitioner confirmed, written
   before the code, and the tests and end-to-end checks written from it.

A reconciliation proves what the source covers and nothing more. It is not a proof that
all data is correct, and the source itself can be wrong or go out of date. Write down
which source you used and the date.
