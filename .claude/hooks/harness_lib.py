"""Shared helpers for the hooks and the review marker.

The fingerprint is a hash of the working-tree contents of every changed file that is
not documentation, in this repository and in the repositories listed in harness.json
"review_repos". The reviewer records it after a PASS; the stop gate compares it with
the current one. Editing code after the review changes the fingerprint, so a stale
PASS no longer counts.
"""
import hashlib
import json
import os
import subprocess
from pathlib import Path

DOC_PREFIXES = ("docs/", ".harness/")
DOC_SUFFIXES = (".md",)


def run_git(root, *args):
    return subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, check=False
    ).stdout


def repo_changes(root):
    """Changed or untracked paths in one repository that are not documentation."""
    raw = run_git(root, "status", "--porcelain", "-z", "--untracked-files=all")
    paths = []
    entries = raw.split("\0")
    i = 0
    while i < len(entries):
        entry = entries[i]
        i += 1
        if len(entry) < 4:
            continue
        status, path = entry[:2], entry[3:]
        if status[0] in "RC":  # renames carry the old path in the next entry
            i += 1
        if path.startswith(DOC_PREFIXES) or path.endswith(DOC_SUFFIXES):
            continue
        paths.append(path)
    return paths


def changed_paths(root):
    """Changed paths here and in each review repo, the latter prefixed with its path.

    A review repo that is not checked out on this machine is skipped.
    """
    paths = repo_changes(root)
    for repo in config_list(load_config(root), "review_repos"):
        prefix = os.path.expanduser(repo).rstrip("/")
        repo_dir = Path(root) / prefix
        if (repo_dir / ".git").exists():
            paths += [f"{prefix}/{path}" for path in repo_changes(repo_dir)]
    return sorted(set(paths))


def fingerprint(root, paths):
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.encode())
        target = Path(root) / path
        digest.update(target.read_bytes() if target.is_file() else b"<deleted>")
    return digest.hexdigest()


def load_config(root):
    try:
        config = json.loads((Path(root) / "harness.json").read_text())
    except (OSError, ValueError):
        return {}
    return config if isinstance(config, dict) else {}


def config_list(config, key, default=()):
    """A list of non-empty strings from harness.json; a single string counts as one."""
    value = config.get(key, list(default))
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list):
        return list(default)
    return [item for item in value if isinstance(item, str) and item.strip()]
