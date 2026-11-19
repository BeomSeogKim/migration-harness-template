#!/usr/bin/env python3
"""PreToolUse guard for Bash: the lines an agent must not cross.

Prevents: the mistakes that cannot be undone — rewriting shared history, dropping
data, deleting without a WHERE, or touching a production database.

It denies instead of asking. A prompt the agent can talk its way past is not a
boundary. Production markers come from harness.json ("production_markers"), for
example ["prod", "prd", "live", "db.example.com"].
"""
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from harness_lib import load_config  # noqa: E402

DB_CLIENT = re.compile(r"(?:^|[;&|(\s])(mysql|mariadb|psql|pgcli|sqlite3|sqlcmd|mongosh)(?:\s|$)", re.I)
RULES = [
    (
        re.compile(r"git\s+push\b[^;&|]*(?:\s-f\b|--force\b|--force-with-lease\b|\s\+\S)", re.I),
        "force-pushing rewrites shared history",
    ),
    (
        re.compile(r"git\s+push\b[^;&|]*\s(?:origin\s+)?(?:HEAD:)?(?:refs/heads/)?(?:main|master)\b", re.I),
        "pushing to the default branch skips review",
    ),
    (
        re.compile(r"rm\s+-[a-z]*r[a-z]*f?[a-z]*\s+(?:/|~|\$HOME|\.|\*)(?:\s|$)", re.I),
        "a recursive delete of a root, home, or working directory",
    ),
]
SQL_RULES = [
    (re.compile(r"\bdrop\s+(?:table|database|schema)\b", re.I), "DROP removes data for good"),
    (re.compile(r"\btruncate\b", re.I), "TRUNCATE removes all rows"),
    (re.compile(r"\bdelete\s+from\s+[\w.`\"]+\s*(?:;|$|\"|')", re.I), "DELETE without a WHERE removes every row"),
]


def deny(reason):
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": f"Blocked: {reason}. A human runs this, not an agent.",
            }
        },
        sys.stdout,
    )
    sys.exit(0)


def check(command, markers):
    for pattern, reason in RULES:
        if pattern.search(command):
            return reason
    if DB_CLIENT.search(command):
        for pattern, reason in SQL_RULES:
            if pattern.search(command):
                return reason
        for marker in markers:
            if re.search(re.escape(marker), command, re.I):
                return f"the command names a production target ('{marker}')"
    return None


def main():
    try:
        command = json.load(sys.stdin).get("tool_input", {}).get("command", "") or ""
    except Exception:
        return  # an unparsable payload is not this guard's business
    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    markers = load_config(root).get("production_markers", [])
    reason = check(command, markers)
    if reason:
        deny(reason)


if __name__ == "__main__":
    main()
