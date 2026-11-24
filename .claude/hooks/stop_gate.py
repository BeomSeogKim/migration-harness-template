#!/usr/bin/env python3
"""Stop hook: the session cannot end with unreviewed or failing changes.

Prevents: an agent declaring the work finished while the build is red or nobody
independent has looked at the change.

Passes when there are no non-documentation changes (here and in the repositories
listed in harness.json "review_repos"), or when
  1. the build command in harness.json (if set) exits 0, and
  2. .harness/review.pass holds the fingerprint of the current changes.
Escape hatch for work in progress: `touch .harness/skip`.

Off while harness.json says "onboarded": false. Before setup there is no build command
and no review flow to satisfy, and the setup interview must be able to wait for answers.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from harness_lib import changed_paths, fingerprint, load_config  # noqa: E402


def block(reason):
    print(reason, file=sys.stderr)
    sys.exit(2)


def main():
    try:
        payload = json.load(sys.stdin)
    except Exception:
        payload = {}
    root = os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or os.getcwd()
    root = Path(root)

    if (root / ".harness" / "skip").exists():
        return

    config = load_config(root)
    if config.get("onboarded") is False:
        return

    paths = changed_paths(root)
    if not paths:
        return

    build = str(config.get("build_command") or "").strip()
    if build:
        result = subprocess.run(
            build, shell=True, cwd=root, capture_output=True, text=True, timeout=900
        )
        if result.returncode != 0:
            tail = (result.stdout + result.stderr)[-1500:]
            block(f"Stop gate: the build failed. Fix it before ending.\n{tail}")

    marker = root / ".harness" / "review.pass"
    current = fingerprint(root, paths)
    if not marker.exists() or marker.read_text().strip() != current:
        block(
            "Stop gate: these changes have no passing review. Ask the reviewer agent "
            "to review them; it records a PASS with scripts/mark_review_pass.py. "
            f"Changed: {', '.join(paths[:8])}"
        )


if __name__ == "__main__":
    main()
