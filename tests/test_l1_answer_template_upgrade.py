"""Actual base-to-candidate L1 refresh/copy upgrades, with synthetic authority only."""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import yaml  # This suite is run in the pinned Copier runtime, not host Python.

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts/lib"))
import l1_template_ownership as ownership
import l1_answer_template_upgrade as upgrade

BASE = "84d6c81e0b1146940ded9bf1bf6ede222acf67f8"
KEY = "company_ontology_ref"
SELECTED = "<repo:Example/ontology@v2>"
OTHER = "<repo:Deliberate/ontology@v3>"
STATE = Path("contracts/template-ownership-state.json")
SCRATCH = Path(os.environ.get("TMPDIR", str(ROOT)))


def snapshot(repo: Path) -> dict:
    result = {}
    for path in repo.rglob("*"):
        relative = path.relative_to(repo)
        if ".git" in relative.parts:
            continue
        if path.is_symlink():
            result[str(relative)] = ("link", os.readlink(path))
        elif path.is_file():
            result[str(relative)] = (path.stat().st_mode, hashlib.sha256(path.read_bytes()).hexdigest())
    return result


def answers(repo: Path, value) -> None:
    path = repo / ".copier-answers.yml"
    data = yaml.safe_load(path.read_text())
    if value is None:
        data.pop(KEY, None)
    else:
        data[KEY] = value
    path.write_text(yaml.safe_dump(data))


class UpgradeHarness(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory(dir=SCRATCH, prefix="l1-upgrade-")
        cls.root = Path(cls.temporary.name)
        bin_dir = cls.root / "bin"
        bin_dir.mkdir()
        ak = bin_dir / "ak"
        ak.write_text(f"#!{sys.executable}\nimport json, sys\n"
                      "if sys.argv[1:] != ['task', 'show', '123']: raise SystemExit(97)\n"
                      "print(json.dumps({'id': 123, 'status': 'claimed', 'repo': 'synthetic'}))\n")
        ak.chmod(0o755)
        # Route all child Python/YAML reads to this pinned interpreter as well.
        (bin_dir / "python3").symlink_to(sys.executable)
        cls.env = dict(os.environ, PATH=f"{bin_dir}:{os.environ['PATH']}", AK_CMD=str(ak),
                       PYTHONDONTWRITEBYTECODE="1", COPIER_ANSWERS_PYTHON=sys.executable,
                       DISABLE_PROJECT_OWNER_HANDLE_INFERENCE="1", COPIER_VCS_REF="HEAD")
        cls.base = cls.root / "base"
        cls.incoming = cls.root / "incoming"
        cls.checked("uvx", "--from", "copier==9.11.1", "copier", "copy", "--trust", "--quiet",
                    "-r", BASE, "--defaults", "--overwrite", "-d", "repo_slug=upgrade-test",
                    str(ROOT), str(cls.base))
        cls.checked("sh", str(ROOT / "scripts/new-l1-from-copier.sh"), str(cls.incoming),
                    "--defaults", "--overwrite", "-d", "repo_slug=upgrade-test")
        for old in upgrade.APPROVED:
            path = f"copier/{old}/{upgrade.OLD}"
            upgrade.record(cls.base, path, upgrade.APPROVED[old])
        cls.checked("git", "init", "--quiet", cwd=cls.base)
        cls.checked("git", "config", "user.name", "upgrade test", cwd=cls.base)
        cls.checked("git", "config", "user.email", "test@example.invalid", cwd=cls.base)
        cls.commit(cls.base)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    @classmethod
    def checked(cls, *args: str, cwd: Path | None = None, expected: int = 0):
        result = subprocess.run(args, cwd=cwd or cls.root, env=cls.env,
                                capture_output=True, text=True)
        if result.returncode != expected:
            raise AssertionError(f"{args}: {result.returncode} != {expected}\n{result.stdout}\n{result.stderr}")
        return result

    @classmethod
    def commit(cls, repo: Path) -> None:
        cls.checked("git", "add", ".", cwd=repo)
        cls.checked("git", "-c", "core.hooksPath=/dev/null", "commit", "--quiet", "--allow-empty",
                    "-m", "test state", cwd=repo)

    def setUp(self) -> None:
        self.local = tempfile.TemporaryDirectory(dir=self.root, prefix="case-")
        self.addCleanup(self.local.cleanup)
        self.parent = Path(self.local.name)
        self.repo = self.parent / "repo"
        shutil.copytree(self.base, self.repo)

    def plan(self):
        return upgrade.plan(self.repo, self.incoming, ownership.load_map(self.repo),
                            ownership.load_map(self.incoming), ownership.owner)

    def wrapper(self, *args: str, expected: int = 0):
        return self.checked("sh", str(ROOT / "scripts/new-l1-from-copier.sh"), str(self.repo),
                            "--defaults", "--overwrite", *args, expected=expected)

    def refresh(self, apply: bool = True, expected: int = 0):
        # Exercise the actual owner entrypoint and its answer-forwarding renderer.
        if apply:
            return self.checked("sh", str(ROOT / "scripts/propagate-l1-template.sh"), str(self.repo),
                                "--apply", "--plan-sha256", "1" * 64, "--wave-id", "synthetic-upgrade",
                                expected=expected)
        return self.checked("sh", str(ROOT / "scripts/preview-l1-diff.sh"), str(self.repo), expected=expected)

    def child(self, name: str, dest: Path, *args: str) -> None:
        identity = "package_name=upgrade-child" if name == "tpl-package" else "repo_slug=upgrade-child"
        agent = ("-d", "creation_task_id=AK-123", "-d", "agent_role=synthetic-role") if name == "tpl-agent-repo" else ()
        self.checked("sh", str(self.repo / "scripts/new-repo-from-copier.sh"), name, str(dest),
                     "--defaults", "--overwrite", "-r", "HEAD", "-d", identity, *agent, *args)

class UpgradeTests(UpgradeHarness):
    def test_actual_owner_refresh_preserves_selected_empty_and_missing_answers(self) -> None:
        for value in (SELECTED, "", None):
            with self.subTest(value=value):
                if self.repo.exists():
                    shutil.rmtree(self.repo)
                shutil.copytree(self.base, self.repo)
                answers(self.repo, value)
                sentinel = self.repo / "company-only.txt"
                sentinel.write_text("unrelated target-only bytes\n")
                readme = self.repo / "README.md"
                readme.write_text(readme.read_text() + "\ncompany owned policy\n")
                self.commit(self.repo)
                before = snapshot(self.repo)
                planned = self.refresh(apply=False)
                self.assertEqual(snapshot(self.repo), before)
                self.assertEqual(planned.stdout.count("retire: "), 5)
                self.refresh()
                current = yaml.safe_load((self.repo / ".copier-answers.yml").read_text())
                if value:
                    self.assertEqual(current[KEY], value)
                else:
                    self.assertNotIn(KEY, current)
                self.assertEqual(snapshot(self.repo)["README.md"], before["README.md"])
                self.assertEqual(sentinel.read_text(), "unrelated target-only bytes\n")
                self.assertEqual(json.loads((self.repo / STATE).read_text())["state"], "applied_pending_receipt")
                after = snapshot(self.repo)
                self.refresh(expected=2)  # A second apply cannot bypass the receipt membrane.
                self.assertEqual(snapshot(self.repo), after)

    def test_all_five_base_upgrades_emit_single_default_and_custom_answers(self) -> None:
        for route in ("owner", "wrapper"):
            with self.subTest(route=route):
                shutil.rmtree(self.repo)
                shutil.copytree(self.base, self.repo)
                answers(self.repo, SELECTED)
                self.commit(self.repo)
                if route == "owner":
                    self.refresh()
                else:
                    self.wrapper()
                self.commit(self.repo)  # Child wrapper defaults to committed L1 HEAD.
                for name in upgrade.APPROVED:
                    directory = self.repo / "copier" / name
                    self.assertFalse((directory / upgrade.OLD).exists())
                    self.assertTrue((directory / upgrade.NEW).is_file())
                    for custom in (False, True):
                        dest = self.parent / f"{route}-{name}-{custom}"
                        answer_path = "child answers/choice.yml" if custom else ".copier-answers.yml"
                        options = ("--answers-file", answer_path) if custom else ()
                        self.child(name, dest, *options)
                        data = yaml.safe_load((dest / answer_path).read_text())
                        if name in ("tpl-project-repo", "tpl-monorepo", "tpl-package"):
                            self.assertEqual(data[KEY], SELECTED)
                        if custom:
                            self.assertFalse((dest / ".copier-answers.yml").exists())
                            before = snapshot(dest)
                            self.child(name, dest, *options)
                            self.assertEqual(snapshot(dest), before)
                            if name in ("tpl-project-repo", "tpl-monorepo", "tpl-package"):
                                self.child(name, dest, *options, "-d", f"{KEY}={OTHER}")
                                self.assertEqual(yaml.safe_load((dest / answer_path).read_text())[KEY], OTHER)
                                self.child(name, dest, *options)
                                self.assertEqual(yaml.safe_load((dest / answer_path).read_text())[KEY], OTHER)
                                self.child(name, dest, *options, "-d", f"{KEY}=")
                                self.assertEqual(yaml.safe_load((dest / answer_path).read_text())[KEY], "")
                                self.child(name, dest, *options)
                                self.assertEqual(yaml.safe_load((dest / answer_path).read_text())[KEY], SELECTED)
                if route == "wrapper":
                    before = snapshot(self.repo)
                    self.wrapper()
                    self.assertEqual(snapshot(self.repo), before)

class UpgradeSafetyTests(UpgradeHarness):
    def test_dryrun_option_classification_matches_pinned_copier(self) -> None:
        from copier._cli import CopierCopySubApp

        for arguments in (("-n",), ("--pretend",), ("-f", "-n"), ("-f", "--pretend"),
                          ("-d", "company_name=-fn"), ("-dcompany_name=-n",),
                          ("--data=company_name=n",), ("-a", "-n"),
                          ("--answers-file", "=", "-n"), ("--answers-file=", "-n"),
                          ("--answers-file=-n",), ("-x", "-n"), ("--skip", "-n"),
                          ("-d", "company_name=n", "-n")):
            with self.subTest(arguments=arguments):
                parsed, _ = CopierCopySubApp("copier copy")._parse_args([*arguments, "src", "dst"])
                expected = any(info.swname in ("-n", "--pretend") for info in parsed.values())
                self.assertEqual(upgrade.copy_pretend(list(arguments)), expected)
        for grouped in ("-fn", "-nf", "-qn", "-nq", "-fqn"):
            parsed, _ = CopierCopySubApp("copier copy")._parse_args([grouped, "src", "dst"])
            self.assertTrue(any(info.swname == "-n" for info in parsed.values()))
            with self.assertRaisesRegex(ValueError, "grouped short options"):
                upgrade.copy_pretend([grouped])

    def test_grouped_and_standalone_dryruns_preserve_old_only_and_mixed_bytes_and_index(self) -> None:
        shadow = self.parent / "render-spy"
        shadow.mkdir()
        called = self.parent / "copier-called"
        spy = shadow / "uvx"
        spy.write_text(f"#!{sys.executable}\nfrom pathlib import Path\n"
                       f"Path({str(called)!r}).write_text('called')\nraise SystemExit(97)\n")
        spy.chmod(0o755)
        for mixed in (False, True):
            with self.subTest(mixed=mixed):
                if mixed:
                    for name in upgrade.APPROVED:
                        new = f"copier/{name}/{upgrade.NEW}"
                        shutil.copy2(self.incoming / new, self.repo / new)
                    self.commit(self.repo)
                before, index = snapshot(self.repo), (self.repo / ".git/index").read_bytes()
                for grouped in ("-fn", "-nf", "-qn", "-nq", "-fqn"):
                    result = self.checked("env", f"PATH={shadow}:{self.env['PATH']}", "sh",
                                          str(ROOT / "scripts/new-l1-from-copier.sh"),
                                          str(self.repo), grouped, expected=2)
                    self.assertIn("grouped short options", result.stderr)
                    self.assertFalse(called.exists(), "grouped switch reached Copier before rejection")
                    self.assertEqual(snapshot(self.repo), before)
                    self.assertEqual((self.repo / ".git/index").read_bytes(), index)
                for arguments in (("-n",), ("--pretend",), ("-f", "-n"), ("-f", "--pretend")):
                    self.wrapper(*arguments)
                    self.assertEqual(snapshot(self.repo), before)
                    self.assertEqual((self.repo / ".git/index").read_bytes(), index)

    def test_informational_exits_preserve_old_only_and_mixed_bytes_and_index(self) -> None:
        for mixed in (False, True):
            if mixed:
                for name in upgrade.APPROVED:
                    new = f"copier/{name}/{upgrade.NEW}"
                    shutil.copy2(self.incoming / new, self.repo / new)
                self.commit(self.repo)
            before, index = snapshot(self.repo), (self.repo / ".git/index").read_bytes()
            for arguments in (("--help",), ("-h",), ("--help-all",), ("--version",),
                              ("-v",), ("--completions", "bash"), ("--completions=bash",)):
                with self.subTest(mixed=mixed, arguments=arguments):
                    result = self.wrapper(*arguments)
                    # Compare unmodified Copier's informational output, not a help proxy.
                    native = self.checked("uvx", "--from", "copier==9.11.1", "copier", "copy",
                                          *arguments)
                    self.assertEqual(result.stdout, native.stdout)
                    self.assertEqual(result.stderr, native.stderr)
                    self.assertEqual(snapshot(self.repo), before)
                    self.assertEqual((self.repo / ".git/index").read_bytes(), index)

    def test_zero_exit_without_worker_completion_cannot_retire_or_reseal(self) -> None:
        shadow = self.parent / "no-copy"
        shadow.mkdir()
        called = self.parent / "copier-calls"
        spy = shadow / "uvx"
        spy.write_text(f"#!{sys.executable}\nfrom pathlib import Path\n"
                       f"with Path({str(called)!r}).open('a') as out: out.write('called\\n')\n")
        spy.chmod(0o755)
        for mixed in (False, True):
            with self.subTest(mixed=mixed):
                if mixed:
                    for name in upgrade.APPROVED:
                        new = f"copier/{name}/{upgrade.NEW}"
                        shutil.copy2(self.incoming / new, self.repo / new)
                    self.commit(self.repo)
                before, index = snapshot(self.repo), (self.repo / ".git/index").read_bytes()
                called.write_text("")
                self.checked("env", f"PATH={shadow}:{self.env['PATH']}", "sh",
                             str(ROOT / "scripts/new-l1-from-copier.sh"), str(self.repo),
                             "--defaults", "--overwrite")
                self.assertEqual(called.read_text(), "called\n", "no-render invocation resealed")
                self.assertEqual(snapshot(self.repo), before)
                self.assertEqual((self.repo / ".git/index").read_bytes(), index)

    def test_completion_signal_requires_worker_return_and_successful_cli_cleanup(self) -> None:
        from copier import _cli

        template = self.parent / "tiny-template"
        template.mkdir()
        (template / "copier.yml").write_text("{}\n")
        (template / "rendered.txt").write_text("actual render\n")
        completion = self.parent / "completion"
        dest = self.parent / "tiny-dest"
        args = ["copy", "--quiet", "--defaults", str(template), str(dest)]
        # A zero exit from inside the worker is not successful return from run_copy.
        completion.write_text("stale completion from an earlier invocation")
        with mock.patch.object(_cli.Worker, "run_copy", side_effect=SystemExit(0)):
            with self.assertRaises(SystemExit) as exit_info:
                upgrade.run_copy_cli(completion, args)
        self.assertEqual(exit_info.exception.code, 0)
        self.assertEqual(completion.read_text(), "")
        self.assertFalse(dest.exists())
        # Even successful rendering is insufficient if worker context cleanup fails.
        with mock.patch.object(_cli.Worker, "__exit__", side_effect=RuntimeError("cleanup failed")):
            with self.assertRaisesRegex(RuntimeError, "cleanup failed"):
                upgrade.run_copy_cli(completion, args)
        self.assertEqual((dest / "rendered.txt").read_text(), "actual render\n")
        self.assertEqual(completion.read_text(), "")
        with self.assertRaises(SystemExit) as exit_info:
            upgrade.run_copy_cli(completion, args)
        self.assertEqual(exit_info.exception.code, 0)
        self.assertEqual(completion.read_text(), "non-pretend-copy-completed\n")
        with self.assertRaises(SystemExit) as exit_info:
            upgrade.run_copy_cli(completion, [*args[:1], "--pretend", *args[1:]])
        self.assertEqual(exit_info.exception.code, 0)
        self.assertEqual(completion.read_text(), "")

    def test_option_values_containing_n_are_forwarded_as_data_not_dryruns(self) -> None:
        for mixed in (False, True):
            with self.subTest(mixed=mixed):
                if mixed:
                    shutil.rmtree(self.repo)
                    shutil.copytree(self.base, self.repo)
                    for name in upgrade.APPROVED:
                        new = f"copier/{name}/{upgrade.NEW}"
                        shutil.copy2(self.incoming / new, self.repo / new)
                    self.commit(self.repo)
                index = (self.repo / ".git/index").read_bytes()
                self.wrapper("-d", "company_name=-fn", "-drepo_slug=name-with-n",
                             "--exclude", "--help", "--exclude=--version")
                data = yaml.safe_load((self.repo / ".copier-answers.yml").read_text())
                self.assertEqual(data["company_name"], "-fn")
                self.assertEqual(data["repo_slug"], "name-with-n")
                for name, digest in upgrade.APPROVED.items():
                    self.assertFalse((self.repo / f"copier/{name}/{upgrade.OLD}").exists())
                    upgrade.record(self.repo, f"copier/{name}/{upgrade.NEW}", digest)
                self.assertEqual((self.repo / ".git/index").read_bytes(), index)
                # The second actual copy must reseal without the retired paths.
                self.assertEqual(upgrade.prepare_wrapper(self.repo, ROOT / "copier-template"), {})

    def test_existing_preview_dependency_and_multiline_diagnostics_are_preserved(self) -> None:
        shadow = self.parent / "blocked-python"
        shadow.mkdir()
        for name in ("python3", "python"):
            command = shadow / name
            command.write_text("#!/bin/sh\nexit 127\n")
            command.chmod(0o755)
        command = ("env", "-u", "COPIER_ANSWERS_PYTHON", "-u", "COPIER_ANSWERS_BASE_PYTHON",
                   f"PATH={shadow}:{self.env['PATH']}", "sh",
                   str(ROOT / "scripts/preview-l1-diff.sh"), str(self.repo))
        result = self.checked(*command, expected=2)
        self.assertIn("missing dependency: functional python3 or python", result.stderr)
        path = self.repo / ".copier-answers.yml"
        data = yaml.safe_load(path.read_text())
        data["company_name"] = "Line1\nLine2"
        path.write_text(yaml.safe_dump(data))
        before = snapshot(self.repo)
        result = self.checked(*command, expected=2)
        self.assertIn("unable to parse 'company_name'", result.stderr)
        self.assertEqual(snapshot(self.repo), before)

    def test_explicit_bootstrap_attests_old_paths_without_retiring_them(self) -> None:
        (self.repo / STATE).unlink()
        (self.repo / "contracts/template-ownership.yml").unlink()
        path = self.repo / ".copier-answers.yml"
        data = yaml.safe_load(path.read_text())
        data.pop("_ownership_state", None)
        path.write_text(yaml.safe_dump(data))
        self.commit(self.repo)
        self.checked("sh", str(ROOT / "scripts/propagate-l1-template.sh"), str(self.repo),
                     "--bootstrap-map", "--evidence-ref", "evidence:123", "--apply")
        adoption = json.loads((self.repo / "contracts/template-ownership-adoption.json").read_text())
        for name in upgrade.APPROVED:
            old = f"copier/{name}/{upgrade.OLD}"
            self.assertIn(old, adoption["existing_template_paths"])
            self.assertTrue((self.repo / old).exists())
        self.commit(self.repo)
        self.refresh()
        self.assertTrue(all(not (self.repo / f"copier/{name}/{upgrade.OLD}").exists()
                            for name in upgrade.APPROVED))
        self.assertEqual(json.loads((self.repo / STATE).read_text())["state"], "applied_pending_receipt")

    def test_modified_untracked_modes_symlinks_and_ownership_fail_before_copy(self) -> None:
        old = self.repo / "copier/tpl-agent-repo" / upgrade.OLD
        mutations = (
            lambda: old.write_text(old.read_text() + "# deliberately modified\n"),
            lambda: old.chmod(0o755),
            lambda: (old.unlink(), old.symlink_to(self.base / "copier/tpl-agent-repo" / upgrade.OLD)),
            lambda: (self.repo / "copier/tpl-agent-repo/.git").mkdir(),
        )
        for mutate in mutations:
            with self.subTest(mutation=mutate):
                shutil.rmtree(self.repo)
                shutil.copytree(self.base, self.repo)
                mutate()
                before = snapshot(self.repo)
                with self.assertRaises((ValueError, OSError)):
                    self.plan()
                self.wrapper(expected=2)
                self.assertEqual(snapshot(self.repo), before)
        shutil.rmtree(self.repo)
        shutil.copytree(self.base, self.repo)
        old.write_text(old.read_text() + "# committed customization\n")
        self.commit(self.repo)
        before = snapshot(self.repo)
        self.refresh(expected=2)
        self.assertEqual(snapshot(self.repo), before)
        self.checked("git", "rm", "--cached", str(old.relative_to(self.repo)), cwd=self.repo)
        with self.assertRaises(ValueError):
            self.plan()
        current = ownership.load_map(self.base)
        current["template"].remove("copier/**")
        current["agent"].append("copier/**")
        with self.assertRaisesRegex(ValueError, "prior and incoming"):
            upgrade.plan(self.base, self.incoming, current, ownership.load_map(self.incoming), ownership.owner)

    def test_unwritable_ancestor_refused_before_mutation(self) -> None:
        folder = self.repo / "copier/tpl-package"
        original_mode = folder.stat().st_mode & 0o777
        folder.chmod(0o500)
        try:
            before = snapshot(self.repo)
            result = self.wrapper(expected=2)
            self.assertIn("unwritable obsolete-template parent", result.stderr)
            self.assertEqual(snapshot(self.repo), before)
        finally:
            folder.chmod(original_mode)

    def test_adoption_stale_preflight_and_successor_checks(self) -> None:
        with self.assertRaisesRegex(ValueError, "unattested"):
            upgrade.plan(self.repo, self.incoming, ownership.load_map(self.repo),
                         ownership.load_map(self.incoming), ownership.owner, {"existing_template_paths": {}})
        entries = self.plan()
        self.assertEqual(len(entries), 5)
        forged = json.loads(json.dumps(entries))
        forged[next(iter(forged))]["record"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "fixed approved"):
            upgrade.revalidate(self.repo, forged)
        # No successor has yet been installed: retirement must not delete anything.
        before = snapshot(self.repo)
        with self.assertRaises(OSError):
            upgrade.retire(self.repo, entries)
        self.assertEqual(snapshot(self.repo), before)
        for entry in entries.values():
            shutil.copy2(self.incoming / entry["new"], self.repo / entry["new"])
        old = self.repo / next(iter(entries))
        old.write_text(old.read_text() + "# drift after plan\n")
        before = snapshot(self.repo)
        with self.assertRaises(ValueError):
            upgrade.retire(self.repo, entries)
        self.assertEqual(snapshot(self.repo), before)
        shutil.copy2(self.base / old.relative_to(self.repo), old)
        entries = self.plan()
        upgrade.retire(self.repo, entries)
        self.assertEqual(self.plan(), {})
        upgrade.retire(self.repo, {})

    def test_dryrun_failed_render_and_v2_copy_do_not_retire(self) -> None:
        for mixed in (False, True):
            if mixed:
                for name in upgrade.APPROVED:
                    new = f"copier/{name}/{upgrade.NEW}"
                    shutil.copy2(self.incoming / new, self.repo / new)
                self.commit(self.repo)
            before, index = snapshot(self.repo), (self.repo / ".git/index").read_bytes()
            for arguments, expected in ((("--pretend",), 0),
                                        (("-d", 'company_ontology_ref=unsafe"quote'), 2),
                                        (("--invalid-option",), 2), (("-r", BASE), 2)):
                with self.subTest(mixed=mixed, arguments=arguments):
                    self.wrapper(*arguments, expected=expected)
                    self.assertEqual(snapshot(self.repo), before)
                    self.assertEqual((self.repo / ".git/index").read_bytes(), index)
        state = json.loads((self.repo / STATE).read_text())
        state.update(schema="ai-society.template-ownership-state/2", kind="l1_ownership_transition_state")
        (self.repo / STATE).write_text(json.dumps(state))
        before = snapshot(self.repo)
        result = self.wrapper(expected=2)
        self.assertIn("v2 unsupported", result.stderr)
        self.assertEqual(snapshot(self.repo), before)

    def test_malformed_owner_answers_are_not_silently_emptied(self) -> None:
        path = self.repo / ".copier-answers.yml"
        for bad in ("company_ontology_ref: [broken", "company_ontology_ref: [not-a-string]", "- wrong-root"):
            path.write_text(bad)
            self.commit(self.repo)
            before = snapshot(self.repo)
            self.refresh(expected=2)
            self.assertEqual(snapshot(self.repo), before)


if __name__ == "__main__":
    unittest.main()
