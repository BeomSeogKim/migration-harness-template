import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

GUARD = Path(__file__).parent / "guard.py"


def run_guard(command, config=None):
    with tempfile.TemporaryDirectory() as root:
        if config is not None:
            Path(root, "harness.json").write_text(json.dumps(config))
        env = {**os.environ, "CLAUDE_PROJECT_DIR": root}
        result = subprocess.run(
            [sys.executable, str(GUARD)],
            input=json.dumps({"tool_input": {"command": command}}),
            capture_output=True,
            text=True,
            env=env,
        )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout) if result.stdout.strip() else None


class GuardTest(unittest.TestCase):
    def assertDenied(self, command, config=None):
        out = run_guard(command, config)
        self.assertIsNotNone(out, f"expected a deny for: {command}")
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "deny")

    def assertAllowed(self, command, config=None):
        self.assertIsNone(run_guard(command, config), f"expected allow for: {command}")

    def test_force_push_is_denied(self):
        self.assertDenied("git push --force origin feature")
        self.assertDenied("git push -f origin feature")
        self.assertDenied("git push origin +feature")

    def test_push_to_default_branch_is_denied(self):
        self.assertDenied("git push origin main")
        self.assertDenied("git push origin HEAD:master")

    def test_normal_push_is_allowed(self):
        self.assertAllowed("git push origin feature/ticket-1")
        self.assertAllowed("git status")

    def test_destructive_sql_is_denied(self):
        self.assertDenied('mysql -e "DROP TABLE orders"')
        self.assertDenied('psql -c "TRUNCATE orders"')
        self.assertDenied('mysql -e "DELETE FROM orders;"')

    def test_scoped_sql_is_allowed(self):
        self.assertAllowed('mysql -e "DELETE FROM orders WHERE id = 1"')
        self.assertAllowed('psql -c "SELECT count(*) FROM orders"')

    def test_production_target_is_denied(self):
        config = {"production_markers": ["prod", "db.example.com"]}
        self.assertDenied("psql -h db.example.com -c 'select 1'", config)
        self.assertDenied("mysql -h orders-prod -e 'select 1'", config)
        self.assertAllowed("psql -h localhost -c 'select 1'", config)

    def test_recursive_delete_of_home_is_denied(self):
        self.assertDenied("rm -rf ~")
        self.assertDenied("rm -rf /")
        self.assertAllowed("rm -rf build/")


if __name__ == "__main__":
    unittest.main()
