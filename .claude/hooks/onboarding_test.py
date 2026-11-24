import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

HOOK = Path(__file__).parent / "onboarding.py"


def run_hook(config=None, raw_config=None, stdin=None):
    with tempfile.TemporaryDirectory() as root:
        if config is not None:
            Path(root, "harness.json").write_text(json.dumps(config))
        if raw_config is not None:
            Path(root, "harness.json").write_text(raw_config)
        if stdin is None:
            stdin = json.dumps(
                {"hook_event_name": "SessionStart", "source": "startup", "cwd": root}
            )
        env = {**os.environ, "CLAUDE_PROJECT_DIR": root}
        return subprocess.run(
            [sys.executable, str(HOOK)], input=stdin, capture_output=True, text=True, env=env
        )


class OnboardingTest(unittest.TestCase):
    def assertNudges(self, result):
        self.assertEqual(result.returncode, 0, result.stderr)
        out = json.loads(result.stdout)
        self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "SessionStart")
        self.assertIn(".claude/commands/setup.md", out["hookSpecificOutput"]["additionalContext"])
        self.assertIn("/setup", out["systemMessage"])

    def assertSilent(self, result):
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "")

    def test_fresh_template_is_nudged(self):
        self.assertNudges(run_hook({"onboarded": False, "build_command": ""}))

    def test_missing_harness_json_is_nudged(self):
        self.assertNudges(run_hook())

    def test_onboarded_project_hears_nothing(self):
        self.assertSilent(run_hook({"onboarded": True}))

    def test_unparsable_stdin_still_works(self):
        self.assertNudges(run_hook({"onboarded": False}, stdin="not json"))

    def test_own_errors_fail_open(self):
        self.assertSilent(run_hook(raw_config="{ broken"))
        self.assertSilent(run_hook(raw_config="[]"))

    def test_it_is_fast(self):
        started = time.monotonic()
        run_hook({"onboarded": True})
        self.assertLess(time.monotonic() - started, 2.0)


if __name__ == "__main__":
    unittest.main()
