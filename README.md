# migration-harness-template

A small starting point for doing a migration with AI coding agents, for any stack and
any domain. It holds the rules, documents, checks, and hooks that kept an
agent-assisted migration honest, and a setup interview that fits them to your project.
It contains no company code, schema, or data.

Companion to a Korean blog post on doing migrations with AI.
Each file below names the failure it prevents. Delete what you do not need.

## What is here

| Path | What it is | Failure it prevents |
|---|---|---|
| `AGENTS.md` (`CLAUDE.md` links to it) | The contract an agent reads first, with a project section that setup fills | Rules scattered across tools and drifting apart |
| `.claude/commands/setup.md` | The setup interview (`/setup`) | A harness running on placeholders and someone else's defaults |
| `.claude/hooks/onboarding.py` | SessionStart hook that offers setup until `harness.json` says `"onboarded": true` | Migration work starting on an unconfigured harness |
| `docs/code-map/` | Bookmarks to where things live, one file per domain area | Context filled by exploration |
| `docs/knowledge/` | Domain rules with a source, a date, and a priority (P0, P1, P2) | Re-implementing behavior that only looks the same |
| `docs/plans/_template.md` | A plan an agent writes, a second vendor reviews, and a human approves | Work in a direction nobody asked for |
| `verification/` | Reconciliation queries, a source outside the code, and a test spec | Data that loads cleanly and is still wrong |
| `.claude/agents/` | `migrator`, `reviewer`, `domain-analyst`, `verifier` | Context exhaustion, self-review |
| `.claude/hooks/guard.py` | Denies force-push, protected-branch push, destructive SQL, production targets | The mistake that cannot be undone |
| `.claude/hooks/stop_gate.py` | A turn cannot end with a red build or an unreviewed change, here or in the linked repositories | Finishing with unreviewed work |
| `harness.json` | The settings the hooks and agents read (below) | Hooks guarding someone else's branches and targets |

### harness.json

| Key | Meaning |
|---|---|
| `onboarded` | `false` until setup finishes. While it is `false`, the stop gate is off and the SessionStart hook offers setup. |
| `build_command` | Run by the stop gate before a turn with changes may end. Empty means no build check. |
| `production_markers` | Words or hosts that mean production. The guard denies database and target commands that name them. |
| `protected_branches` | Branches agents never push to. Default `main`, `master`. |
| `target_commands` | Tools besides the built-in database clients (mysql, mariadb, psql, pgcli, sqlite3, sqlcmd, sqlplus, mongosh) that reach a database or an environment, such as a migration tool, `kubectl`, or `ssh`. |
| `review_repos` | Other repositories agents change, relative to this one (for example `repos/new-api`). The stop gate checks them too. |
| `review_command` | A reviewer from another model vendor that reads a review request on stdin, for example `codex exec --sandbox read-only -`. |

## Use it

1. Copy the files, including `.claude/`, into your control-center repository or a new
   one, and commit them. Keep `CLAUDE.md` a symlink:

   ```sh
   rsync -a --exclude .git migration-harness-template/ your-repo/
   ```

2. Open Claude Code in that folder and accept the workspace trust prompt; Claude Code
   runs no hooks in an untrusted folder. The SessionStart hook tells Claude the harness
   is not set up.
3. Type `/setup`, or say hello and accept the offer. Setup asks nine short questions,
   each with a default: what you migrate from and to, the repositories, the stack, the
   build and test command, what marks production, the first domain areas, who the
   practitioners are, the source of truth outside the code, and the second-vendor
   reviewer. It shows a summary and, on your yes, writes `harness.json`, the project
   section of `AGENTS.md`, a code-map and a knowledge file per domain area, and links
   under `repos/`, then commits them.
4. Do what the setup report lists as manual: fill the knowledge with practitioners,
   give agents a database account that cannot write to production, and try the review
   command once.

Other agents (Codex, Gemini CLI) read `AGENTS.md`. Ask them to follow
`.claude/commands/setup.md`, or edit `harness.json` and `AGENTS.md` by hand. The hooks
run only in Claude Code.

Run the hook tests (Python 3, no dependencies):

```sh
python3 -m unittest discover -s .claude/hooks -p '*_test.py'
```

## How the review gate works

The reviewer agent runs `scripts/mark_review_pass.py` after a review with no blocking
findings. That records a fingerprint of the changed files, here and in `review_repos`,
in `.harness/review.pass`. The stop gate blocks the end of a turn unless the
fingerprint matches the current changes, so editing code after the review invalidates
the PASS. For work in progress, `touch .harness/skip`.

## Limits

- The review mark depends on role separation. Nothing technical stops the agent that
  wrote the code from running the marker script; the instructions and the reviewer
  being a different agent are what hold the line.
- The stop gate sees uncommitted changes only. A change committed before its review
  passes the gate; `AGENTS.md` asks agents to commit after the review, and nothing
  enforces that.
- Claude Code ends a turn after eight consecutive stop-hook blocks with no tool call in
  between (per its hook documentation, November 2026), so the gate can be outlasted.
- `guard.py` matches command text. It stops the common mistakes, not a determined
  workaround: it does not read SQL files passed with `-f`, and a bare `git push` while
  a protected branch is checked out is not caught. Back it with the permissions of the
  database account you give agents.
- A reconciliation proves only what its source covers.
- What was verified, on macOS with Python 3.14 and Claude Code 2.1.331:
  - All hook unit tests pass, including the onboarding hook's fail-open cases.
  - In a throwaway copy, `claude -p "hello" --output-format stream-json --verbose
    --include-hook-events --setting-sources project` showed the SessionStart hook
    firing on startup and exiting 0, and Claude's first reply read
    `.claude/commands/setup.md` and asked its first question. The Stop hook fired and
    let the turn end, because the gate is off before setup.
- What was not verified: an interactive session (the trust prompt, and whether the
  hook's one-line notice shows in the terminal UI), a full setup interview through to
  the written files and the commit, other operating systems, and the example
  `review_command` values beyond their `--help` output.
