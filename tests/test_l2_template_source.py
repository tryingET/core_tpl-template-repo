"""Pinned-source staging, positive birth completion, and fail-closed provenance."""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml
from tests.l2_birth_test_support import stub_l0, company_seal, dump

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "copier-template/scripts/lib"))
import l2_birth_execution as execution
import l2_birth_safety as safety

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


    def test_pretend_alias_and_grouped_switches_before_launch(self):
        self.assertTrue(source.arguments(["-n"])[3])
        for flag in ("-qn", "-nq", "-fq", "-hn", "-nrHEAD"):
            with self.subTest(flag=flag), patch.object(source, "run", side_effect=AssertionError("must not launch")):
                with self.assertRaisesRegex(ValueError, "grouped short"):
                    self.prepare(flag)
                self.assertFalse(self.child.exists())
        for option in ("--exclude", "-x", "--skip", "-s", "--vcs-ref", "-r"):
            for value in ("-n", "-qn", "--pretend"):
                self.assertFalse(source.arguments([option, value])[3])
        for value in ("-x-n", "-s-qn", "-r--pretend", "-dvalue=-n"):
            self.assertFalse(source.arguments([value])[3])

    def test_tracked_company_intersections_and_opaque_child_boundaries(self):
        subprocess.run(["git", "-C", str(self.company), "init", "-q"], check=True)
        for path in ("gitlab/ci/pipeline.yml", "owned/AGENTS.md", "company handbook/README.md"):
            target = self.company / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("company control plane")
        (self.company / ".gitignore").write_text("owned/*/\n")
        subprocess.run(["git", "-C", str(self.company), "add", "."], check=True)
        subprocess.run(["git", "-C", str(self.company), "update-index", "--add", "--cacheinfo",
                        "160000," + self.pin + ",owned/mono"], check=True)
        # Even a missing working-tree file remains company index authority.
        (self.company / "gitlab/ci/pipeline.yml").unlink()
        for relative in ("gitlab", "gitlab/ci", "gitlab/ci/pipeline.yml/child", "owned", "owned/mono", "company handbook"):
            with self.subTest(relative=relative), self.assertRaisesRegex(ValueError, "tracked company"):
                source.destination_guard(self.company / relative, self.company, self.l0)
        for relative in ("owned/project", "agents/agent-new", "new-handbook", "owned/mono/packages/new", "owned/mono/apps/new"):
            with self.subTest(relative=relative):
                self.assertEqual(source.destination_guard(self.company / relative, self.company, self.l0), self.company / relative)

    def test_descriptor_bind_survives_last_moment_destination_swap(self):
        meta = self.prepare()
        old_child = self.root / "original-child"
        def swapped_run(cmd, *, env, pass_fds):
            self.assertEqual(len(pass_fds), 1)
            fd = pass_fds[0]
            self.assertEqual(meta["execution_root_identity"], safety.identity(fd))
            self.assertIn(["--bind-fd", str(fd), str(self.child)], [cmd[i:i+3] for i in range(len(cmd))])
            self.assertNotIn(["--bind", str(self.child), str(self.child)], [cmd[i:i+3] for i in range(len(cmd))])
            self.child.rename(old_child)
            self.child.symlink_to(self.company, target_is_directory=True)
            # Real Bubblewrap must write only to the inode already opened.
            cut = cmd.index("--chdir") + 2
            source.run([*cmd[:cut], "/bin/sh", "-c", "printf safe > descriptor-proof"], env=env, pass_fds=pass_fds)
            (self.scratch / "copy-completed.txt").write_text("non-pretend-copy-completed\n")
        before = {str(p): p.read_bytes() for p in self.company.rglob("*") if p.is_file()}
        with self.assertRaises((OSError, ValueError)):
            execution.execute(meta, self.child, ["uvx", "--from", "copier==9.11.1", "copier", "copy", meta["template_path"], str(self.child)],
                              swapped_run, source.environment, source.check_before_copy, source.destination_guard)
        self.assertEqual((old_child / "descriptor-proof").read_text(), "safe")
        self.assertFalse((self.company / "descriptor-proof").exists())
        self.assertEqual(before, {str(p): p.read_bytes() for p in self.company.rglob("*") if p.is_file()})

    def test_readonly_descriptor_bind_for_missing_pretend_child(self):
        meta = self.prepare("-n")
        def observed_run(cmd, *, env, pass_fds):
            fd, = pass_fds
            self.assertEqual(safety.identity(fd), meta["execution_root_identity"])
            self.assertIn(["--ro-bind-fd", str(fd), str(self.child)], [cmd[i:i+3] for i in range(len(cmd))])
        execution.execute(meta, self.child, ["uvx", "--from", "copier==9.11.1", "copier", "copy", "-n", meta["template_path"], str(self.child)],
                          observed_run, source.environment, source.check_before_copy, source.destination_guard)
        self.assertFalse(self.child.exists())
        source.record(self.scratch, self.child)

    def test_lineage_root_swap_after_open_stays_descriptor_relative(self):
        meta = self.prepare()
        dump(self.child / ".copier-answers.yml", {"company_slug": "otherco"})
        with safety.directory(self.child) as fd:
            meta.update(copy_completed=True, execution_root_identity=safety.identity(fd))
        (self.scratch / "lineage.json").write_text(json.dumps(meta))
        old = self.root / "old-child"
        def swap(fd, relative, update):
            self.child.rename(old)
            self.child.symlink_to(self.company, target_is_directory=True)
            safety.record_answers(fd, relative, update)
        before = (self.company / ".copier-answers.yml").read_bytes()
        with patch.object(source, "record_answers", side_effect=swap):
            source.record(self.scratch, self.child)
        self.assertEqual((self.company / ".copier-answers.yml").read_bytes(), before)
        self.assertEqual(yaml.safe_load((old / ".copier-answers.yml").read_text())["_template_lineage"]["l0_commit"], self.pin)

    def test_lineage_refuses_swapped_root_or_symlinked_answers_components(self):
        meta = self.prepare()
        dump(self.child / ".copier-answers.yml", {"company_slug": "otherco"})
        with safety.directory(self.child) as fd:
            meta.update(copy_completed=True, execution_root_identity=safety.identity(fd))
        (self.scratch / "lineage.json").write_text(json.dumps(meta))
        self.child.rename(self.root / "old-child")
        dump(self.child / ".copier-answers.yml", {"company_slug": "otherco"})
        with self.assertRaisesRegex(ValueError, "identity changed"):
            source.record(self.scratch, self.child)
        before = (self.company / ".copier-answers.yml").read_bytes()
        with safety.directory(self.child) as fd:
            for relative in ("linked.yml", "linked-dir/.copier-answers.yml"):
                (self.child / relative.split("/")[0]).symlink_to(
                    self.company if "/" in relative else self.company / ".copier-answers.yml")
                with self.subTest(relative=relative), self.assertRaises(OSError):
                    safety.record_answers(fd, relative, lambda child: child.update(unsafe=True))
        self.assertEqual((self.company / ".copier-answers.yml").read_bytes(), before)

    def test_lineage_nested_parent_and_final_file_swap_cannot_follow_links(self):
        dump(self.child / "answers/child.yml", {"company_slug": "otherco"})
        dump(self.company / "child.yml", {"canonical": True})
        canonical = (self.company / "child.yml").read_bytes()
        old = self.child / "old-answers"
        def swap(child):
            (self.child / "answers").rename(old)
            (self.child / "answers").symlink_to(self.company, target_is_directory=True)
            (old / "child.yml").unlink()
            (old / "child.yml").symlink_to(self.company / "child.yml")
            child["lineage"] = "safe"
        with safety.directory(self.child) as fd:
            safety.record_answers(fd, "answers/child.yml", swap)
        self.assertEqual((self.company / "child.yml").read_bytes(), canonical)
        self.assertFalse((old / "child.yml").is_symlink())
        self.assertEqual(yaml.safe_load((old / "child.yml").read_text())["lineage"], "safe")

    def test_directory_walk_refuses_swapped_ancestor(self):
        parent = self.root / "container"
        parent.mkdir()
        child = parent / "new-child"
        original = safety.os.open
        def raced_open(path, flags, *args, **kwargs):
            if path == "container":
                parent.rename(self.root / "old-container")
                parent.symlink_to(self.company, target_is_directory=True)
            return original(path, flags, *args, **kwargs)
        with patch.object(safety.os, "open", side_effect=raced_open), self.assertRaises(OSError):
            with safety.directory(child, create=True):
                self.fail("must not follow swapped ancestor")
        self.assertFalse((self.company / "new-child").exists())


if __name__ == "__main__":
    unittest.main()
