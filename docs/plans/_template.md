# Plan: <short title>

Status: draft | approved by <role> on <YYYY-MM-DD> | rejected

An agent writes this before changing code and then stops. A human approves it.
Required when the change touches money, state transitions, a public contract, a data
schema, or more than one domain. Skip it for a small change inside one domain.

## Problem
What is wrong or missing, and how you know (files and lines, query results).

## Approach
What you will change. Name the alternatives you rejected and why.

## Scope
Files and domains touched. What you will not touch.

## Verification
How a reviewer or a query can tell it is right: the test you will write first, and the
reconciliation queries from `verification/` you will run.

## Risks and rollback
What can go wrong, and how to undo the change.

## Knowledge used
The `docs/knowledge/` entries this plan relies on. If one is `unconfirmed`, say so here.

Prevents: building for a week in a direction nobody asked for.
