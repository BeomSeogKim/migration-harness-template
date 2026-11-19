# Code map

A bookmark file per domain, so an agent finds the right place without scanning the
repositories. It lists entry points and the matching legacy location. It does not list
every class.

Prevents: the context window filling up while the agent searches.

Keep it in the repository it describes when you can. If you cannot add documents to
the live code repository, keep the map here and write each repository path next to the
entry.

Example entry:

```text
## order
- Entry point: the order API controller (repo: api, path: src/main/.../OrderController)
- Legacy counterpart: the legacy order service, create flow (repo: legacy, path: ...)
- Rules: docs/knowledge/order.md
```
