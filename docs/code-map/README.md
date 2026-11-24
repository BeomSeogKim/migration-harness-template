# Code map

A bookmark file per domain area (copy `_template.md`), so an agent finds the right
place without scanning the repositories. It lists entry points and the matching legacy
location. It does not list every class.

Prevents: the context window filling up while the agent searches.

Keep it in the repository it describes when you can. If you cannot add documents to
the live code repository, keep the map here and write each repository path next to the
entry.

When the code lives in other repositories, link each one under `repos/<name>` (a
symlink to your local checkout; `repos/` is git-ignored because checkouts live in
different places on different machines). Entries then use paths such as
`repos/<name>/src/...`, which resolve the same way for every agent and every machine.
List the repositories agents change in `review_repos` in `harness.json` so the stop
gate checks them too.
