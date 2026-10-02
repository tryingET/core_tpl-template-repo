"""Pinned-source staging, positive birth completion, and fail-closed provenance."""
import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml
from tests.l2_birth_test_support import stub_l0, company_seal, dump

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("l2_template_source", ROOT / "copier-template/scripts/lib/l2_template_source.py")
source = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(source)


class SourceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR"), prefix="l2-source-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.l0, self.pin = stub_l0(self.root, ROOT / "copier-template")
        self.company = self.root / "company"
        self.parent = {"company_slug": "otherco", "repo_slug": "source-test", "l0_source_sha": self.pin}
        dump(self.company / ".copier-answers.yml", self.parent)
        company_seal(self.company, self.pin, "source-test")
        self.child = self.root / "child"
        self.scratch = self.root / "scratch"
        self.scratch.mkdir(mode=0o700)
        self.patch = patch.dict(os.environ, {"L0_TEMPLATE_ROOT": str(self.l0)})
        self.patch.start(); self.addCleanup(self.patch.stop)

    def prepare(self, *args):
        source.prepare(self.company, "tpl-project-repo", self.child, self.scratch, list(args))
        return json.loads((self.scratch / "lineage.json").read_text())

    def test_without_copies_exact_pin_private_source_and_positive_completion(self):
        before = subprocess.check_output(["git", "-C", str(self.l0), "rev-parse", "HEAD"])
        meta = self.prepare()
        self.assertFalse((self.company / "copier").exists())
        self.assertEqual(meta["l0_commit"], self.pin)
        with self.assertRaisesRegex(ValueError, "positively complete"):
            source.record(self.scratch, self.child)  # no successful birth without answers
        self.assertFalse(self.child.exists())
        answers = self.child / ".copier-answers.yml"
        dump(answers, {"company_slug": "otherco", "_src_path": meta["template_path"]})
        answers.chmod(0o600)
        # Controlled unit completion signal; real Copier is covered separately.
        meta["copy_completed"] = True
        (self.scratch / "lineage.json").write_text(json.dumps(meta))
        source.record(self.scratch, self.child)
        value = yaml.safe_load(answers.read_text())
        self.assertEqual(value["_template_lineage"], {"company": "otherco", "template": "tpl-project-repo", "l0_commit": self.pin})
        self.assertEqual(value["_src_path"], "~/ai-society/otherco/copier/tpl-project-repo")
        self.assertEqual(answers.stat().st_mode & 0o777, 0o600)
        self.assertEqual(subprocess.check_output(["git", "-C", str(self.l0), "rev-parse", "HEAD"]), before)

    def test_only_explicit_no_effect_operations_may_omit_answers(self):
        self.prepare("--pretend")
        source.record(self.scratch, self.child)
        self.assertFalse(self.child.exists())

    def test_parent_pin_mismatch_is_refused_before_git_or_renderer(self):
        self.parent["l0_source_sha"] = "0" * 40
        dump(self.company / ".copier-answers.yml", self.parent)
        with patch.object(source, "run", side_effect=AssertionError("must not launch")):
            with self.assertRaisesRegex(ValueError, "pins disagree"):
                self.prepare()

    def test_company_override_and_traversing_answers_are_refused(self):
        for args in [("-d", "company_slug=foreignco"), ("-a", "../outside.yml"), ("--answers-file=/outside.yml",), ("-a", ""), ("-d", "malformed")]:
            with self.subTest(args=args), patch.object(source, "run", side_effect=AssertionError("must not launch")):
                with self.assertRaises(ValueError):
                    self.prepare(*args)

    def test_source_symlink_is_refused(self):
        alias = self.root / "alias"
        alias.symlink_to(self.l0, target_is_directory=True)
        with patch.dict(os.environ, {"L0_TEMPLATE_ROOT": str(alias)}):
            with self.assertRaisesRegex(ValueError, "symlinked"):
                self.prepare()

    def test_changed_parent_inputs_refuse_lineage_recording(self):
        meta = self.prepare()
        answers = self.child / ".copier-answers.yml"
        dump(answers, {"company_slug": "otherco", "_src_path": meta["template_path"]})
        before = answers.read_bytes()
        dump(self.company / ".copier-answers.yml", {**self.parent, "company_name": "changed"})
        with self.assertRaisesRegex(ValueError, "inputs changed"):
            source.record(self.scratch, self.child)
        self.assertEqual(answers.read_bytes(), before)

    def test_existing_birth_pin_is_not_replaced_by_new_company_pin(self):
        dump(self.child / ".copier-answers.yml", {"company_slug": "otherco", "_template_lineage": {
            "company": "otherco", "template": "tpl-project-repo", "l0_commit": self.pin}})
        (self.l0 / "new-release").write_text("new L0 commit")
        for args in [("add", "."), ("-c", "user.name=test", "-c", "user.email=test@example.org", "commit", "-qm", "new L0")]:
            subprocess.run(["git", "-C", str(self.l0), *args], check=True, capture_output=True)
        new_pin = subprocess.check_output(["git", "-C", str(self.l0), "rev-parse", "HEAD"], text=True).strip()
        dump(self.company / ".copier-answers.yml", {**self.parent, "l0_source_sha": new_pin})
        company_seal(self.company, new_pin, "source-test")
        self.assertEqual(self.prepare()["l0_commit"], self.pin)

    def test_existing_closed_lineage_cannot_change_company_or_template(self):
        for value in ({"company": "foreignco", "template": "tpl-project-repo", "l0_commit": self.pin},
                      {"company": "otherco", "template": "tpl-agent-repo", "l0_commit": self.pin},
                      {"company": "otherco", "template": "tpl-project-repo", "l0_commit": self.pin, "approval": True}):
            dump(self.child / ".copier-answers.yml", {"_template_lineage": value})
            with self.assertRaisesRegex(ValueError, "existing child lineage"):
                self.prepare()
            self.assertFalse((self.scratch / "l0").exists())

    def test_private_caller_umask_does_not_change_template_modes(self):
        previous = os.umask(0o077)
        try:
            self.prepare()
        finally:
            os.umask(previous)
        self.assertEqual((self.scratch / "l0/copier-template/copier/tpl-project-repo/copier.yml").stat().st_mode & 0o777, 0o644)
        self.assertEqual((self.scratch / "render/copier/tpl-project-repo/copier.yml").stat().st_mode & 0o777, 0o644)
        self.assertEqual(self.scratch.stat().st_mode & 0o777, 0o700)

    def test_git_company_metadata_has_private_mount_target(self):
        subprocess.run(["git", "-C", str(self.company), "init", "-q"], check=True)
        before = subprocess.check_output(["git", "-C", str(self.company), "status", "--porcelain"])
        self.prepare()
        self.assertTrue((self.scratch / "company-input/.git").is_dir())
        self.assertEqual(subprocess.check_output(["git", "-C", str(self.company), "status", "--porcelain"]), before)

    def test_custom_parent_locator_and_snapshot_are_sealed(self):
        custom = self.company / "answers dir/company.yml"
        custom.parent.mkdir(parents=True, exist_ok=True)
        (self.company / ".copier-answers.yml").rename(custom)
        seal_path = self.company / "contracts/provenance-seal.yml"
        seal = yaml.safe_load(seal_path.read_text())
        seal["render"]["answers_file"] = "answers dir/company.yml"
        dump(seal_path, seal)
        # A misleading default locator is not authority.
        dump(self.company / ".copier-answers.yml", {"company_slug": "wrongco"})
        meta = self.prepare()
        self.assertEqual(yaml.safe_load((self.scratch / "parent-answers.yml").read_text()), self.parent)
        self.assertEqual(meta["company"], "otherco")
        dump(custom, {**self.parent, "company_name": "changed"})
        with self.assertRaisesRegex(ValueError, "inputs changed"):
            source.check_before_copy(meta, self.child)

    def test_protected_destinations_fail_before_clone_or_render(self):
        for destination in (self.company, self.company.parent, self.l0, self.l0 / "child",
                            self.company / "copier/tpl-project-repo", self.company / "copier-overlay/test",
                            self.company / "contracts/test", self.company / ".git/test",
                            self.company / "ontology/test", self.company / "scripts/test"):
            with self.subTest(destination=destination):
                with patch.object(source, "verify_source"), patch.object(source, "run", side_effect=AssertionError("must not launch")):
                    with self.assertRaisesRegex(ValueError, "authority|protected"):
                        source.prepare(self.company, "tpl-project-repo", destination, self.scratch, [])
        self.assertEqual(source.destination_guard(self.company / "owned/child", self.company, self.l0), self.company / "owned/child")

    def test_parent_and_child_drift_rechecked_immediately_before_copy(self):
        dump(self.child / ".copier-answers.yml", {"company_slug": "otherco"})
        meta = self.prepare()
        source.check_before_copy(meta, self.child)
        for change in ("parent", "answers", "identity"):
            with self.subTest(change=change):
                if change == "parent":
                    dump(self.company / ".copier-answers.yml", {**self.parent, "company_name": "changed"})
                elif change == "answers":
                    dump(self.child / ".copier-answers.yml", {"company_slug": "otherco", "new": True})
                else:
                    self.child.rename(self.root / "old-child")
                    dump(self.child / ".copier-answers.yml", {"company_slug": "otherco"})
                with self.assertRaisesRegex(ValueError, "changed before"):
                    source.check_before_copy(meta, self.child)
                dump(self.company / ".copier-answers.yml", self.parent)
                if change == "answers":
                    dump(self.child / ".copier-answers.yml", {"company_slug": "otherco"})

    def test_data_files_precede_cli_regardless_of_argument_order(self):
        data = self.root / "data.yml"
        dump(data, {"company_slug": "wrongco", "value": "file"})
        for args in (["-d", "company_slug=otherco", "--data-file", str(data)],
                     ["--data-file=" + str(data), "--data=company_slug=otherco"]):
            answers, values, files, no_effect = source.arguments(args)
            self.assertEqual(values, {"company_slug": "otherco", "value": "file"})
            self.assertEqual(files, [str(data)])
            self.assertFalse(no_effect)
        self.assertFalse(source.arguments(["--exclude", "--pretend"])[3])

    def test_completion_cannot_bypass_source_or_lineage_checks(self):
        meta = self.prepare()
        meta["copy_completed"] = True
        (self.scratch / "lineage.json").write_text(json.dumps(meta))
        answers = self.child / ".copier-answers.yml"
        for child, message in (({"company_slug": "otherco", "_src_path": "foreign"}, "source contradicts"),
                               ({"company_slug": "wrongco"}, "company contradicts"),
                               ({"company_slug": "otherco", "_template_lineage": {}}, "lineage changed")):
            dump(answers, child)
            before = answers.read_bytes()
            with self.assertRaisesRegex(ValueError, message):
                source.record(self.scratch, self.child)
            self.assertEqual(answers.read_bytes(), before)
        # Same positive signal applies to templates whose answers omit _src_path.
        dump(answers, {"company_slug": "otherco"})
        source.record(self.scratch, self.child)
        self.assertEqual(yaml.safe_load(answers.read_text())["_template_lineage"]["l0_commit"], self.pin)

    def test_final_executor_checks_drift_before_any_process_or_directory_creation(self):
        spec = importlib.util.spec_from_file_location("l2_birth_execution", ROOT / "copier-template/scripts/lib/l2_birth_execution.py")
        execution = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(execution)
        meta = self.prepare()
        dump(self.company / ".copier-answers.yml", {**self.parent, "company_name": "changed"})
        with self.assertRaisesRegex(ValueError, "inputs changed"):
            execution.execute(meta, self.child, ["uvx", "--from", "copier==9.11.1", "copier", "copy", meta["template_path"], str(self.child)],
                              lambda *a, **k: self.fail("must not launch"), source.environment, source.check_before_copy, source.destination_guard)
        self.assertFalse(self.child.exists())


if __name__ == "__main__":
    unittest.main()
