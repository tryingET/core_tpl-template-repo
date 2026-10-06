"""The observer must preserve unittest semantics, including dynamic and fixture cases."""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tests/ci_profile.py"


class ProfileContractTests(unittest.TestCase):
    def invoke(self, source, args=("sample",)):
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as tmp:
            root = Path(tmp)
            (root / "sample.py").write_text(source)
            report = root / "profile.json"
            env = dict(os.environ, PYTHONPATH=str(root), PYTHONDONTWRITEBYTECODE="1")
            command = [sys.executable, "-B", str(RUNNER), "--cohort", "synthetic", "--out", str(report), "--", *args]
            plain = subprocess.run([sys.executable, "-B", "-m", "unittest", *args],
                                   cwd=root, env=env, capture_output=True, text=True)
            observed = subprocess.run(command, cwd=root, env=env, capture_output=True, text=True)
            return plain, observed, json.loads(report.read_text())

    def test_pass_skip_expected_failure_and_dynamic_load_tests(self):
        source = '''import unittest
class Cases(unittest.TestCase):
    def test_pass(self): self.assertEqual(1, 1)
    @unittest.skip('intentional instrument fixture')
    def test_skip(self): pass
    @unittest.expectedFailure
    def test_expected(self): self.fail('expected')
class Extra(unittest.TestCase):
    def test_dynamic(self): self.assertTrue(True)
def load_tests(loader, suite, pattern):
    return unittest.TestSuite([loader.loadTestsFromTestCase(Cases), Extra('test_dynamic')])
'''
        plain, observed, report = self.invoke(source)
        self.assertEqual(plain.returncode, observed.returncode)
        self.assertEqual(observed.returncode, 0, observed.stderr)
        self.assertEqual(report["tests_run"], 4)
        self.assertEqual(len(report["collected_ids"]), 4)
        self.assertEqual({e["outcome"] for e in report["events"]}, {"success", "skip", "expected_failure"})
        self.assertIn("sample.Extra.test_dynamic", report["collected_ids"])
        self.assertIn("skipped=1, expected failures=1", plain.stderr)
        self.assertIn("skipped=1, expected failures=1", observed.stderr)
        self.assertTrue(all(e["seconds"] >= 0 for e in report["events"]))

    def test_subtest_failure_error_and_unexpected_success_stay_red(self):
        source = '''import unittest
class Cases(unittest.TestCase):
    def test_subtests(self):
        for number in (1, 2):
            with self.subTest(number=number): self.assertEqual(number, 1)
    def test_error(self): raise RuntimeError('instrument error fixture')
    @unittest.expectedFailure
    def test_unexpected(self): pass
'''
        plain, observed, report = self.invoke(source)
        self.assertEqual(plain.returncode, observed.returncode)
        self.assertEqual(observed.returncode, 1)
        self.assertFalse(report["successful"])
        self.assertEqual(report["tests_run"], 3)
        events = {event["test_id"]: event for event in report["events"]}
        subtests = events["sample.Cases.test_subtests"]
        self.assertEqual(subtests["outcome"], "failure")
        self.assertEqual([s["outcome"] for s in subtests["subtests"]], ["success", "failure"])
        self.assertEqual(events["sample.Cases.test_error"]["outcome"], "error")
        self.assertEqual(events["sample.Cases.test_unexpected"]["outcome"], "unexpected_success")

    def test_class_fixture_failure_is_not_a_passing_empty_suite(self):
        """A fixture error is evidence, never a successful zero-test profile."""
        source = '''import unittest
class Cases(unittest.TestCase):
    @classmethod
    def setUpClass(cls): raise RuntimeError('class setup fixture')
    def test_not_run(self): pass
'''
        plain, observed, report = self.invoke(source)
        self.assertEqual(plain.returncode, observed.returncode)
        # Some stdlib patch releases report no-tests (5) before fixture-error
        # status (1). Preserve the actual reference policy, never green either.
        self.assertNotEqual(observed.returncode, 0)
        self.assertFalse(report["successful"])
        self.assertEqual(report["tests_run"], 0)
        self.assertEqual(report["collected_ids"], ["sample.Cases.test_not_run"])
        self.assertEqual(report["events"][0]["kind"], "fixture")
        self.assertEqual(report["events"][0]["outcome"], "error")
        self.assertIn("setUpClass", report["events"][0]["test_id"])

    def test_duplicate_id_multiplicity_is_retained(self):
        """Existing duplicate executions are not silently deduplicated."""
        source = '''import unittest
class Cases(unittest.TestCase):
    def test_case(self): pass
def load_tests(loader, suite, pattern):
    return unittest.TestSuite([Cases('test_case'), Cases('test_case')])
'''
        _, observed, report = self.invoke(source)
        self.assertEqual(observed.returncode, 0)
        self.assertEqual(report["collected_ids"], ["sample.Cases.test_case"] * 2)
        self.assertEqual([e["ordinal"] for e in report["events"]], [1, 2])

    def test_skipped_subtest_is_retained_without_changing_parent_semantics(self):
        source = '''import unittest
class Cases(unittest.TestCase):
    def test_subtests(self):
        with self.subTest(case='skip'): self.skipTest('intentional fixture')
        with self.subTest(case='pass'): self.assertTrue(True)
'''
        plain, observed, report = self.invoke(source)
        self.assertEqual(plain.returncode, observed.returncode)
        self.assertEqual(observed.returncode, 0)
        self.assertEqual(report["events"][0]["outcome"], "success")
        self.assertEqual([s["outcome"] for s in report["events"][0]["subtests"]], ["skip", "success"])
        self.assertIn("skipped=1", observed.stderr)

    def test_helper_imports_real_repo_cohort_without_pythonpath(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as tmp:
            env = dict(os.environ, L0_PROFILE_DIR=tmp, PYTHONDONTWRITEBYTECODE="1")
            env.pop("PYTHONPATH", None)
            # A real cheap repo cohort reproduces the script-versus-module path edge.
            command = ["sh", str(ROOT / "tests/ci_unittest.sh"), "helper-smoke", sys.executable,
                       "tests.test_l2_system4d_context"]
            profiled = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True)
            self.assertEqual(profiled.returncode, 0, profiled.stderr)
            report = json.loads(next(Path(tmp).glob("helper-smoke-*.json")).read_text())
            env.pop("L0_PROFILE_DIR")
            plain = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True)
            self.assertEqual(plain.returncode, 0, plain.stderr)
            self.assertEqual(report["tests_run"], 4)
            self.assertEqual(len(report["collected_ids"]), 4)
            self.assertNotIn("_FailedTest", " ".join(report["collected_ids"]))

    def test_empty_dynamic_suite_is_identified_as_empty_not_hidden_coverage(self):
        source = '''import unittest
def load_tests(loader, suite, pattern): return unittest.TestSuite()
'''
        plain, observed, report = self.invoke(source)
        self.assertEqual(plain.returncode, observed.returncode)
        self.assertEqual(report["tests_run"], 0)
        self.assertEqual(report["collected_ids"], [])
        self.assertEqual(report["events"], [])
        self.assertEqual(report["successful"], plain.returncode == 0)

    def test_skipped_class_and_invalid_arguments_follow_standard_exit_policy(self):
        source = '''import unittest
class Cases(unittest.TestCase):
    @classmethod
    def setUpClass(cls): raise unittest.SkipTest('intentional class fixture')
    def test_case(self): pass
'''
        plain, observed, report = self.invoke(source)
        self.assertEqual(plain.returncode, observed.returncode)
        self.assertEqual(report["tests_run"], 0)
        self.assertEqual(report["events"][0]["outcome"], "skip")
        plain, observed, report = self.invoke(source, ("--not-a-unittest-flag", "sample"))
        self.assertEqual(plain.returncode, observed.returncode)
        self.assertEqual(observed.returncode, 2)
        self.assertFalse(report["successful"])

    def test_phase_artifacts_refuse_source_retained_or_linked_outputs(self):
        io = ROOT / "tests/ci_profile_io.py"
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as tmp:
            root = Path(tmp)
            phase = root / "phase.tsv"
            command = [sys.executable, "-B", str(io)]
            created = subprocess.run([*command, "--initialize", str(phase), "start"], capture_output=True)
            self.assertEqual(created.returncode, 0, created.stderr)
            before = phase.read_bytes()
            refused = subprocess.run([*command, "--initialize", str(phase), "start"], capture_output=True)
            self.assertEqual(refused.returncode, 2)
            self.assertEqual(phase.read_bytes(), before)
            appended = subprocess.run([*command, str(phase), "finish"], capture_output=True)
            self.assertEqual(appended.returncode, 0, appended.stderr)
            self.assertEqual(len(phase.read_text().splitlines()), 2)
            link = root / "alias.tsv"
            link.symlink_to(phase)
            for path in (ROOT / "must-not-create.tsv", link):
                result = subprocess.run([*command, "--initialize", str(path), "start"], capture_output=True)
                self.assertEqual(result.returncode, 2)
            self.assertFalse((ROOT / "must-not-create.tsv").exists())
            public = root / "public"
            public.mkdir(mode=0o755)
            public.chmod(0o755)
            result = subprocess.run([*command, "--initialize", str(public / "phase.tsv"), "start"], capture_output=True)
            self.assertEqual(result.returncode, 2)

    def test_output_refuses_source_tree_or_retained_report(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as tmp:
            occupied = Path(tmp) / "retained.json"
            occupied.write_text("historical bytes")
            for path in (ROOT / "profile-must-not-exist.json", occupied):
                command = [sys.executable, "-B", str(RUNNER), "--cohort", "fixture", "--out", str(path), "--", "unittest"]
                result = subprocess.run(command, capture_output=True, text=True)
                self.assertEqual(result.returncode, 2, result.stderr)
            self.assertEqual(occupied.read_text(), "historical bytes")
            self.assertFalse((ROOT / "profile-must-not-exist.json").exists())


if __name__ == "__main__":
    unittest.main()
