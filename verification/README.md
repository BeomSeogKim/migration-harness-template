# Verification

Checks for migrated data. The correct answer lives outside the code you are checking.

Prevents: data that loads cleanly and is still wrong. Row counts and foreign keys can
all pass while an amount is wrong.

Two kinds of check:

1. Structural checks, in `reconcile.sql`: row counts, orphaned foreign keys, NOT NULL
   columns, and totals compared between source and target. They find loading bugs.
2. A source of truth outside the code. If the business keeps its own record of real
   amounts or states (a ledger, a billing export, a count a practitioner trusts),
   compare the migrated data with that record. This is the check that finds
   a wrong value that is structurally valid.

A reconciliation proves what the source covers and nothing more. It is not a proof that
all data is correct, and the source itself can be wrong or go out of date. Write down
which source you used and the date.
