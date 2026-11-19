# migration-harness-template

A small starting point for doing a migration with AI coding agents. It holds the rules,
documents, checks, and two hooks that kept an agent-assisted migration honest. It
contains no company code, schema, or data.

Companion to a Korean blog post on doing migrations with AI.
Each file below names the failure it prevents. Delete what you do not need.

## What is here

| Path | What it is | Failure it prevents |
|---|---|---|
| `AGENTS.md` (`CLAUDE.md` links to it) | The contract an agent reads first | Rules scattered across tools and drifting apart |
| `docs/code-map/` | Bookmarks to where things live | Context filled by exploration |
| `docs/knowledge/` | Domain rules with a source and a date | Re-implementing behavior that only looks the same |
| `docs/plans/_template.md` | A plan an agent writes and a human approves | Work in a direction nobody asked for |
| `verification/` | Reconciliation queries and a source outside the code | Data that loads cleanly and is still wrong |
| `.claude/agents/` | `migrator`, `reviewer`, `domain-analyst` | Context exhaustion, self-review |
| `.claude/hooks/guard.py` | Denies force-push, default-branch push, destructive SQL, production targets | The mistake that cannot be undone |
| `.claude/hooks/stop_gate.py` | The session cannot end with a red build or an unreviewed change | Finishing with unreviewed work |
| `harness.json` | Build command and production markers | |

## Use it

1. Copy the files into your control-center repository (or a new one).
2. Set `build_command` and `production_markers` in `harness.json`.
3. Fill in `docs/code-map/` and `docs/knowledge/` from your own system.
4. Point your agent at `AGENTS.md`. The hooks are wired for Claude Code in
   `.claude/settings.json`; other tools can use `AGENTS.md` and the documents as they are.

Run the hook tests (Python 3, no dependencies):

```sh
python3 -m unittest discover -s .claude/hooks -p '*_test.py'
```

## How the review gate works

The reviewer agent runs `scripts/mark_review_pass.py` after a review with no blocking
findings. That records a fingerprint of the changed files in `.harness/review.pass`.
The stop gate blocks the session end unless the fingerprint matches the current
changes, so editing code after the review invalidates the PASS. For work in progress,
`touch .harness/skip`.

## Limits

- The review mark depends on role separation. Nothing technical stops the agent that
  wrote the code from running the marker script; the instructions and the reviewer
  being a different agent are what hold the line.
- `guard.py` matches command text. It stops the common mistakes, not a determined
  workaround. Back it with the permissions of the database account you give agents.
- A reconciliation proves only what its source covers.
- Written for Claude Code hooks. Check the current hook documentation if a hook
  does not fire.
