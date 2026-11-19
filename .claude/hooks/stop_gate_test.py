import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HOOKS = Path(__file__).parent
GATE = HOOKS / "stop_gate.py"
MARK = HOOKS.parent.parent / "scripts" / "mark_review_pass.py"


def git(root, *args):
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


class StopGateTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        git(self.root, "init", "-q", "-b", "main")
        git(self.root, "config", "user.email", "test@example.com")
        git(self.root, "config", "user.name", "test")
        (self.root / "app.py").write_text("print('v1')\n")
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "init")
        # the marker script lives in this repo; copy it into the fixture
        (self.root / "scripts").mkdir()
        (self.root / "scripts" / "mark_review_pass.py").write_text(MARK.read_text())
        (self.root / ".claude" / "hooks").mkdir(parents=True)
        (self.root / ".claude" / "hooks" / "harness_lib.py").write_text(
            (HOOKS / "harness_lib.py").read_text()
        )

    def tearDown(self):
        self._tmp.cleanup()

    def gate(self):
        env = {**os.environ, "CLAUDE_PROJECT_DIR": str(self.root)}
        return subprocess.run(
            [sys.executable, str(GATE)], input="{}", capture_output=True, text=True, env=env
        )

    def mark_pass(self):
        subprocess.run(
            [sys.executable, str(self.root / "scripts" / "mark_review_pass.py")],
            check=True,
            capture_output=True,
        )

    def test_clean_tree_may_stop(self):
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "fixture")
        self.assertEqual(self.gate().returncode, 0)

    def test_unreviewed_change_blocks(self):
        (self.root / "app.py").write_text("print('v2')\n")
        result = self.gate()
        self.assertEqual(result.returncode, 2)
        self.assertIn("no passing review", result.stderr)

    def test_reviewed_change_may_stop(self):
        (self.root / "app.py").write_text("print('v2')\n")
        self.mark_pass()
        self.assertEqual(self.gate().returncode, 0)

    def test_edit_after_review_blocks_again(self):
        (self.root / "app.py").write_text("print('v2')\n")
        self.mark_pass()
        (self.root / "app.py").write_text("print('v3')\n")
        self.assertEqual(self.gate().returncode, 2)

    def test_documentation_only_change_may_stop(self):
        git(self.root, "add", ".")
        git(self.root, "commit", "-qm", "fixture")
        (self.root / "notes.md").write_text("hello\n")
        self.assertEqual(self.gate().returncode, 0)

    def test_failing_build_blocks_even_when_reviewed(self):
        (self.root / "harness.json").write_text(json.dumps({"build_command": "exit 1"}))
        (self.root / "app.py").write_text("print('v2')\n")
        self.mark_pass()
        result = self.gate()
        self.assertEqual(result.returncode, 2)
        self.assertIn("build failed", result.stderr)

    def test_skip_file_lets_work_in_progress_stop(self):
        (self.root / "app.py").write_text("print('v2')\n")
        (self.root / ".harness").mkdir()
        (self.root / ".harness" / "skip").write_text("")
        self.assertEqual(self.gate().returncode, 0)


if __name__ == "__main__":
    unittest.main()
