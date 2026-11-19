#!/usr/bin/env python3
"""Record that the current changes passed review.

Run by the reviewer agent only, and only after it found nothing blocking.
Anything that edits the code afterwards invalidates the mark.
"""
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root / ".claude" / "hooks"))
from harness_lib import changed_paths, fingerprint  # noqa: E402

paths = changed_paths(root)
if not paths:
    print("No non-documentation changes to mark.")
    sys.exit(0)

marker = root / ".harness" / "review.pass"
marker.parent.mkdir(exist_ok=True)
marker.write_text(fingerprint(root, paths) + "\n")
print(f"Review PASS recorded for {len(paths)} changed file(s).")
