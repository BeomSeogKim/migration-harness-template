#!/usr/bin/env python3
"""SessionStart hook: point a fresh copy of the harness at the setup flow.

Prevents: migration work starting on an unconfigured harness, where the guard knows
no production target, the stop gate has no build command, and the agent reads the
placeholders in AGENTS.md as if they were facts.

Nudges while harness.json is missing or does not say "onboarded": true. It only adds
context and a one-line notice; it never blocks. Any error of its own prints nothing
and exits 0, so a broken nudge cannot get in the way of a session.
"""
import json
import os
import sys
from pathlib import Path

NOTICE = "Migration harness is not set up yet. Run /setup, or ask Claude to set it up."

CONTEXT = """\
This repository holds the migration harness template, and it has not been set up for a
project yet (harness.json does not say "onboarded": true). Until it is, the stop gate
is off, the guard uses default production markers, and the values in <angle brackets>
in AGENTS.md are unknown, not facts.

In your first reply, tell the user this in one sentence and offer to run the setup
interview now. It is defined in .claude/commands/setup.md (the /setup command); follow
that file. If the user's first message is a greeting or asks how to start, begin the
interview with its first question instead of only offering. If they ask for something
else, do that and offer setup once afterwards; do not raise it again in this session.
"""


def needs_setup(root):
    path = Path(root) / "harness.json"
    if not path.exists():
        return True
    config = json.loads(path.read_text())
    return config.get("onboarded") is not True


def main():
    try:
        payload = json.load(sys.stdin)
    except ValueError:
        payload = {}
    root = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()
    if needs_setup(root):
        json.dump(
            {
                "systemMessage": NOTICE,
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": CONTEXT,
                },
            },
            sys.stdout,
        )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # fail open: print nothing, never block the session
    sys.exit(0)
