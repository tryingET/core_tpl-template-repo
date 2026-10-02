"""Budget regressions use isolated synthetic leaves, not an owner-proof proxy."""
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAMES = (
    "check-l0-guardrails", "check-doc-references", "check-session-checkpoint",
    "check-supply-chain", "check-l0-generation", "check-l0-adversarial", "check-l0-fixtures",
)


class VerificationBudgetTests(unittest.TestCase):
    def invoke(self, overrides=None, slow=False):
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as temporary:
            root = Path(temporary)
            scripts = root / "scripts"
            scripts.mkdir()
            shutil.copyfile(ROOT / "scripts/check-l0.sh", scripts / "check-l0.sh")
            for name in NAMES:
                leaf = scripts / (name + ".sh")
                leaf.write_text("#!/bin/sh\n" + ("sleep 60\n" if slow and name == NAMES[0] else "exit 0\n"))
                leaf.chmod(0o755)
            environment = {key: value for key, value in os.environ.items()
                           if not key.startswith("L0_CHECK_")}
            environment.update(overrides or {})
            return subprocess.run(["bash", str(scripts / "check-l0.sh")],
                                  cwd=root, env=environment, text=True, capture_output=True)

    def test_defaults_are_finite_and_all_leaves_run(self):
        result = self.invoke()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("base=1800s generation=3600s adversarial=1800s fixtures=1800s", result.stdout)
        self.assertIn("passed: 7", result.stdout)
        self.assertIn("skipped: 0", result.stdout)

    def test_base_and_per_leaf_environment_overrides_remain_effective(self):
        result = self.invoke({"L0_CHECK_TIMEOUT_SECONDS": "7"})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("base=7s generation=14s adversarial=7s fixtures=7s", result.stdout)
        result = self.invoke({"L0_CHECK_TIMEOUT_SECONDS": "7",
                              "L0_CHECK_TIMEOUT_GENERATION_SECONDS": "11",
                              "L0_CHECK_TIMEOUT_ADVERSARIAL_SECONDS": "13",
                              "L0_CHECK_TIMEOUT_FIXTURES_SECONDS": "17"})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("base=7s generation=11s adversarial=13s fixtures=17s", result.stdout)

    def test_invalid_overrides_fail_closed(self):
        for variable in ("L0_CHECK_TIMEOUT_SECONDS", "L0_CHECK_TIMEOUT_GENERATION_SECONDS",
                         "L0_CHECK_TIMEOUT_ADVERSARIAL_SECONDS", "L0_CHECK_TIMEOUT_FIXTURES_SECONDS"):
            with self.subTest(variable=variable):
                result = self.invoke({variable: "invalid"})
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn(variable + " must be a non-negative integer", result.stderr)

    def test_timeout_is_failure_and_aborts_later_checks(self):
        result = self.invoke({"L0_CHECK_TIMEOUT_SECONDS": "1"}, slow=True)
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("timed_out_after_1s", result.stdout)
        self.assertIn("failed: 1", result.stdout)
        self.assertIn("skipped: 6", result.stdout)
        self.assertIn("aborting remaining checks after timeout", result.stderr)


if __name__ == "__main__":
    unittest.main()
