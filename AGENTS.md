# Migration agent contract

This repository is the control center for a data and code migration done with AI agents.
Read this file first. `CLAUDE.md` is a symlink to it; edit `AGENTS.md` only.

Every rule below names the failure it exists to prevent. If a rule stops preventing
anything, delete it.

## This migration

Filled in by the setup flow in `.claude/commands/setup.md` (`/setup` in Claude Code;
other agents read the file and follow it). If `harness.json` does not say
`"onboarded": true`, offer to run it before other work. Until then, every value in
<angle brackets> is unknown: ask, do not assume.

- Migrating: <legacy system and stack> to <new system and stack>
- Repositories: <name: role (legacy, new, shared), path, whether agents change it>
- Build and test: `build_command` in `harness.json`
- Domain areas: <area, area>, each with `docs/code-map/<area>.md` and `docs/knowledge/<area>.md`
- Practitioners: <roles, not names>; rules reach us through <meetings, tickets, documents>
- Source of truth outside the code: <ledger, export, legacy database, or none yet>
- Second reviewer: <tool and vendor, or none>, run through `review_command` in `harness.json`

Prevents: an agent filling unknown project facts with plausible guesses.

## Before you explore

1. Read `docs/code-map/` for where things live. Do not scan whole repositories.
   Prevents: the context window filling up with exploration before any work starts.
2. Read the matching entry in `docs/knowledge/` before implementing a rule from the
   legacy system, P0 entries first. If there is none, say so and ask; do not guess.
   Prevents: implementing something that looks like the legacy behavior but is not.

## Before you change anything

3. For any change that touches money, state transitions, a public contract, a data
   schema, or more than one domain, or whose reach you cannot tell, write a plan from
   `docs/plans/_template.md`. If unsure, plan. Have the reviewer agent review it (it
   also asks the second vendor in `review_command`), then stop. A human approves the
   plan before you write code.
   Prevents: a week of work in a direction nobody asked for.
4. Work in the smallest scope that can be verified. Prefer one domain per task.
   Prevents: changes that cannot be reviewed.

## While you work

5. Delegate reading-heavy work to a sub agent (`.claude/agents/`: `domain-analyst`
   for research, `migrator` for an approved plan, `verifier` for checks, `reviewer`
   for review) and keep only its summary. Do not let sub agents call other sub agents.
   Prevents: context exhaustion and chains of agents nobody is watching.
6. When you delegate, restate the rules the sub agent needs in the prompt. A sub agent
   does not see this conversation.
   Prevents: a sub agent answering against the wrong system.

## Before you say you are done

7. Migrated data is checked against a source outside the code, not against the code.
   The verifier agent runs the queries in `verification/` and reports the numbers.
   Rules a practitioner confirmed go into a test spec (`verification/`) before the
   code, and the tests are written from it.
   Prevents: data that loads cleanly and is still wrong, and tests that share the
   code's misunderstanding.
8. The agent that wrote the change does not review it. The reviewer agent reviews it
   and gets a second review from a different model vendor (`review_command` in
   `harness.json`); a human decides which findings to apply.
   Prevents: the same misunderstanding passing both writing and review.
9. The session cannot end while the build fails or the review has not passed
   (`.claude/hooks/stop_gate.py`). Commit migration code only after the review
   passes; the gate sees uncommitted changes only.
   Prevents: finishing with unreviewed changes.

## Hard lines

10. Never force-push, push to a protected branch, drop or truncate tables, delete
    without a `WHERE`, or touch a production target. `.claude/hooks/guard.py` blocks
    these (targets and branches come from `harness.json`); do not look for a way
    around it.
    Prevents: the one mistake that cannot be undone.
