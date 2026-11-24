---
description: Set up this migration harness for a project. Interviews the user one short question at a time, then writes harness.json, the AGENTS.md project section, and starter code-map and knowledge files.
argument-hint: "[optional: what you are migrating, from what to what]"
---

# Set up the migration harness

Prevents: a harness that guards the wrong targets, a stop gate with no build check,
and agents treating template placeholders as facts about the project.

You are configuring this copy of the migration harness for the user's project. If
`$ARGUMENTS` is not empty, take it as the answer to question 1 and confirm it.

## How to ask

- One short question per message, numbered `(n/9)`. Give a default in every question,
  inferred from the repositories when you can. Say once that "ok" accepts the default
  and "skip" leaves the value as a placeholder to fill later.
- Infer defaults cheaply: top-level build files of the repositories named so far,
  `git remote -v`, `git symbolic-ref --short refs/remotes/origin/HEAD`, and
  `command -v codex gemini`. Do not scan whole repositories.
- Write nothing until the user confirms the summary at the end.
- Never record passwords, tokens, keys, or connection strings that carry credentials.
  Production markers are host names or words. Write roles, not people's names.

## Questions

1. What are you migrating, from what to what? Example: "the legacy billing service
   to a new billing service". Default: none; "skip" keeps the placeholder.
2. Which repositories are involved? For each: a short name, its role (legacy, new,
   shared), where it is checked out on this machine, and whether agents change it.
   Default: only this repository, as the new system. Offer to link each one at
   `repos/<name>`.
3. Which languages and stack does each side use? Default: what the build files show
   (`build.gradle(.kts)` or `pom.xml`: JVM; `package.json`: Node.js; `go.mod`: Go;
   `pyproject.toml` or `requirements.txt`: Python; `Cargo.toml`: Rust; `*.csproj`:
   .NET; `composer.json`: PHP; `Gemfile`: Ruby).
4. Which command builds and tests the code agents change? The stop gate runs it before
   a turn with changes may end, so it should finish in a few minutes (the gate gives
   up after 15). Default from the build files: `./gradlew test`, `mvn -q verify`,
   `npm test`, `go test ./...`, `cargo test`, `python -m pytest`, `dotnet test`.
   For several repositories, chain them: `(cd repos/a && ...) && (cd repos/b && ...)`.
   Empty means no build check.
5. What marks production in a command: host names, database names, profiles,
   contexts, or words? Default: `prod`, `production`. If agents reach databases or
   environments through tools other than mysql, psql, sqlite3, sqlcmd, sqlplus, or
   mongosh (for example a migration tool, kubectl, or ssh), name them too.
6. Which domain areas should the code map start with? Up to five. Default: the
   top-level modules or packages of the new system's repository, or "none yet".
7. Who are the domain practitioners (roles, not names), and how do their rules reach
   you: meetings, tickets, documents? Default: "the product owner and the operations
   team, through a weekly meeting and tickets".
8. Is there a record of real values outside the code to reconcile against, such as
   a ledger, a billing export, or a report people trust? Default: the legacy database
   (weaker: it shares the legacy system's mistakes).
9. Which tool from a different model vendor reviews plans and changes? It must read
   the review request on stdin, print findings, and change nothing. Default:
   `codex exec --sandbox read-only -` if `codex` is installed, else
   `gemini --approval-mode plan -p "Review the request on stdin."` if `gemini` is,
   else none.

## Confirm

Show one summary: the answers, `harness.json` as it will be written, the files you
will create or change, the links under `repos/`, and what stays a placeholder.
Protected branches default to `main`, `master`, and the default branch of each
repository agents change; show them here instead of asking.

Then ask once: "Write these files and commit them? (yes / write only / no)".
After setup the stop gate is on, and it treats uncommitted non-documentation files,
such as `harness.json`, as unreviewed changes. So:

- yes: write, then commit.
- write only: write, then `touch .harness/skip` so the gate lets this turn end, and
  tell the user to commit and then delete `.harness/skip`.
- no: write nothing, and leave `"onboarded": false`.

## Write

1. `harness.json`: set `"onboarded": true`, `build_command`, `production_markers`,
   `protected_branches`, `target_commands`, `review_repos` (the repositories agents
   change, as `repos/<name>` or the given path), and `review_command`. Keep any other
   keys. Check it parses: `python3 -c 'import json; json.load(open("harness.json"))'`.
2. For each repository the user agreed to link: `mkdir -p repos` and
   `ln -s <checkout path> repos/<name>`. Skip names that already exist.
3. `AGENTS.md`: replace the placeholders under "This migration" with the answers.
   Answers that were skipped stay as placeholders. Change nothing else in the file.
4. For each domain area (lowercase, hyphenated): create `docs/code-map/<area>.md`
   from `docs/code-map/_template.md` and `docs/knowledge/<area>.md` from
   `docs/knowledge/_template.md`. Fill in only what you know (the area, repository
   names); leave the rest as placeholders, with `Status: unconfirmed`. Never
   overwrite an existing file.
5. Run `python3 -m unittest discover -s .claude/hooks -p '*_test.py'` and report the
   last line. A failure means the hooks will not work on this machine; say so.
6. On "yes", if this is a git repository: stage only the files you wrote, plus the
   harness files if git does not track them yet (`.claude/`, `AGENTS.md`,
   `CLAUDE.md`, `harness.json`, `.gitignore`, `docs/`, `scripts/`, `verification/`),
   and commit with the message "Set up the migration harness". Never push.

## Report

Tell the user, briefly:

- What you wrote and committed, file by file.
- What is still theirs to do:
  - Fill the code-map entries and the knowledge rules with practitioners, and mark
    confirmed ones; P0 rules first.
  - Give agents a database account that cannot write to production. The guard only
    matches command text.
  - Try `review_command` once by hand with a small request.
  - Turn the source of truth into the first queries in `verification/`.
  - Delete the parts of the harness they do not need.
- That the hooks are Claude Code only; other agents follow `AGENTS.md` and the
  documents without them.
