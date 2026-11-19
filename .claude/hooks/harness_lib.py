"""Shared helpers for the stop gate and the review marker.

The fingerprint is a hash of the working-tree contents of every changed file that is
not documentation. The reviewer records it after a PASS; the stop gate compares it
with the current one. Editing code after the review changes the fingerprint, so a
stale PASS no longer counts.
"""
import hashlib
import json
import subprocess
from pathlib import Path

DOC_PREFIXES = ("docs/", ".harness/")
DOC_SUFFIXES = (".md",)


def run_git(root, *args):
    return subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, check=False
    ).stdout


def changed_paths(root):
    """Changed or untracked paths that are not documentation."""
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
        return json.loads((Path(root) / "harness.json").read_text())
    except (OSError, ValueError):
        return {}
