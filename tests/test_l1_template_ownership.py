from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures/l1/template-repo"
COMPANY_POLICY_FIXTURE = ROOT / "tests/fixtures/l1-company-policy"
ENGINE = ROOT / "scripts/lib/l1_template_ownership.py"
ADOPTION = "contracts/template-ownership-adoption.json"
STATE = "contracts/template-ownership-state.json"
SCRATCH_PARENT = Path(os.environ.get("TMPDIR", str(ROOT)))
PLAN_BYTES = b'{"kind":"l1-contract-refresh-plan","version":1}\n'
PLAN_SHA256 = hashlib.sha256(PLAN_BYTES).hexdigest()
L0_HEAD = subprocess.run(
    ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True, capture_output=True, check=True
).stdout.strip()
_SPEC = importlib.util.spec_from_file_location("l1_template_ownership", ENGINE)
assert _SPEC is not None and _SPEC.loader is not None
OWNERSHIP = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(OWNERSHIP)
AGENT_PATHS = (
    "AGENTS.md",
    "README.md",
    "CONTRIBUTING.md",
    ".gitignore",
    ".github/workflows/ci.yml",
    "docs/org/company-charter.md",
    "docs/org/operating_model.md",
)


def run(*args: str, cwd: Path, expect: int = 0) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, cwd=cwd, text=True, capture_output=True)
    if result.returncode != expect:
        raise AssertionError(
            f"command returned {result.returncode}, expected {expect}: {args}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def init_commit(repo: Path) -> None:
    run("git", "init", "--quiet", cwd=repo)
    run("git", "config", "user.name", "l1 ownership test", cwd=repo)
    run("git", "config", "user.email", "test@example.invalid", cwd=repo)
    # No detached auto-maintenance repacking into .git while the temp dir is removed.
    run("git", "config", "gc.auto", "0", cwd=repo)
    run("git", "config", "maintenance.auto", "false", cwd=repo)
    run("git", "add", ".", cwd=repo)
    run("git", "commit", "--quiet", "-m", "fixture", cwd=repo)


def remove_birth_marker(repo: Path) -> None:
    answers = repo / ".copier-answers.yml"
    lines = [line for line in answers.read_text(encoding="utf-8").splitlines() if not line.startswith("_ownership_state:")]
    answers.write_text("\n".join(lines) + "\n", encoding="utf-8")


def make_ak_mock(
    parent: Path,
    repo: Path,
    applied_commit: str,
    wave_id: str,
    authority_repo: Path | None = None,
) -> Path:
    map_hash = digest(repo / "contracts/template-ownership.yml")
    canonical_repo = (authority_repo or repo).resolve()
    task = {"id": 123, "repo": str(canonical_repo), "status": "done"}
    evidence = [{
        "id": 456,
        "task_id": 123,
        "repo": str(canonical_repo),
        "repo_scope": str(canonical_repo),
        "check_type": "l1_contract_refresh_v1",
        "result": "pass",
        "details": {
            "target_repo": str(canonical_repo),
            "applied_commit": applied_commit,
            "source_l0_commit": L0_HEAD,
            "ownership_map_sha256": map_hash,
            "plan_sha256": PLAN_SHA256,
            "wave_id": wave_id,
            "executor": "template-propagator",
            "validation": {"check-template-ci.sh": 0, "ci/full.sh": 0},
        },
    }]
    (parent / "task.json").write_text(json.dumps(task), encoding="utf-8")
    (parent / "evidence.json").write_text(json.dumps(evidence), encoding="utf-8")
    mock = parent / "ak-mock"
    mock.write_text(
        "#!/bin/sh\n"
        f"touch '{parent / 'ak-called'}'\n"
        "case \"$1 $2\" in\n"
        f"  'task show') cat '{parent / 'task.json'}' ;;\n"
        f"  'evidence task') cat '{parent / 'evidence.json'}' ;;\n"
        "  *) exit 2 ;;\n"
        "esac\n",
        encoding="utf-8",
    )
    mock.chmod(0o755)
    return mock


class L1TemplateOwnershipTests(unittest.TestCase):
    def test_base_to_candidate_answer_template_upgrade_suite(self) -> None:
        # Keep real upgrade rendering in the declared 600s generation lane rather
        # than adding its render matrix to the already bounded 300s guardrail lane.
        run("uvx", "--from", "copier==9.11.1", "python", "-B", "-m", "unittest",
            "tests.test_l1_answer_template_upgrade.UpgradeTests", cwd=ROOT)

    def copy_fixture(self, parent: Path, name: str) -> Path:
        target = parent / name
        shutil.copytree(FIXTURE, target)
        return target

    def test_apply_updates_template_and_preserves_company_owned_bytes(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH_PARENT) as temp:
            parent = Path(temp)
            target = self.copy_fixture(parent, "target")
            rendered = self.copy_fixture(parent, "rendered")
            init_commit(target)
            shutil.rmtree(target / "docs/org")
            for source in COMPANY_POLICY_FIXTURE.rglob("*"):
                if not source.is_file():
                    continue
                destination = target / source.relative_to(COMPANY_POLICY_FIXTURE)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)

            for index, rel in enumerate(AGENT_PATHS):
                path = target / rel
                path.parent.mkdir(parents=True, exist_ok=True)
                with path.open("ab") as stream:
                    stream.write(f"\ncompany-owned-{index}\n".encode())
            local_only = target / "docs/project/company-only.md"
            local_only.parent.mkdir(parents=True, exist_ok=True)
            local_only.write_text("outside rendered surface\n", encoding="utf-8")
            run("git", "add", ".", cwd=target)
            run("git", "commit", "--quiet", "-m", "company policy", cwd=target)
            before = {rel: digest(target / rel) for rel in AGENT_PATHS}

            template_file = rendered / "scripts/ci/full.sh"
            template_file.write_text(
                template_file.read_text(encoding="utf-8") + "\n# template refresh sentinel\n",
                encoding="utf-8",
            )
            plan = run(
                "python3",
                str(ENGINE),
                "--repo-root",
                str(target),
                "--rendered",
                str(rendered),
                cwd=ROOT,
            )
            self.assertIn("PLAN (no files changed", plan.stdout)
            self.assertNotIn("company-owned", plan.stdout)
            self.assertNotIn("company-only.md", plan.stdout)
            target_template_before = digest(target / "scripts/ci/full.sh")
            invalid_apply = run(
                "python3", str(ENGINE), "--repo-root", str(target), "--rendered", str(rendered),
                "--apply", "--plan-sha256", "bad", "--wave-id", "wave-bad",
                "--source-l0-commit", L0_HEAD, cwd=ROOT, expect=2,
            )
            self.assertIn("plan-sha256", invalid_apply.stderr)
            self.assertEqual(target_template_before, digest(target / "scripts/ci/full.sh"))
            self.assertIn('"state": "established"', (target / STATE).read_text())

            run(
                "python3",
                str(ENGINE),
                "--repo-root",
                str(target),
                "--rendered",
                str(rendered),
                "--apply",
                "--plan-sha256", PLAN_SHA256,
                "--wave-id", "wave-established-test",
                "--source-l0-commit", L0_HEAD,
                cwd=ROOT,
            )
            self.assertIn("template refresh sentinel", (target / "scripts/ci/full.sh").read_text())
            self.assertEqual(before, {rel: digest(target / rel) for rel in AGENT_PATHS})
            self.assertEqual(local_only.read_text(), "outside rendered surface\n")
            gate = run("bash", "scripts/check-template-ci.sh", cwd=target)
            self.assertNotIn("error:", gate.stderr.lower())

    def test_retirement_revalidates_all_old_templates_after_copy_before_any_delete(self) -> None:
        from l1_answer_template_upgrade import APPROVED, OLD, NEW

        with tempfile.TemporaryDirectory(dir=SCRATCH_PARENT) as temp:
            parent = Path(temp)
            target = self.copy_fixture(parent, "target")
            rendered = self.copy_fixture(parent, "rendered")
            old_paths = []
            for name in APPROVED:
                folder = target / "copier" / name
                shutil.copy2(folder / NEW, folder / OLD)
                old_paths.append(folder / OLD)
            init_commit(target)
            state_before = (target / STATE).read_bytes()
            changed = rendered / "scripts/ci/full.sh"
            changed.write_text(changed.read_text() + "\n# refresh change\n")
            original_copy = OWNERSHIP.copy_atomic

            def concurrent_drift(source, destination):
                original_copy(source, destination)
                old_paths[-1].write_text(old_paths[-1].read_text() + "# late drift\n")

            with mock.patch.object(OWNERSHIP, "copy_atomic", side_effect=concurrent_drift):
                with self.assertRaisesRegex(ValueError, "modified or unapproved"):
                    OWNERSHIP.refresh(target, rendered, True, PLAN_SHA256, "test-retirement", L0_HEAD)
            self.assertTrue(all(path.is_file() for path in old_paths))
            self.assertEqual((target / STATE).read_bytes(), state_before)

    def test_bootstrap_installs_only_map_and_census_attestation(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH_PARENT) as temp:
            parent = Path(temp)
            target = self.copy_fixture(parent, "target")
            rendered = self.copy_fixture(parent, "rendered")
            (target / "contracts/template-ownership.yml").unlink()
            (target / STATE).unlink()
            remove_birth_marker(target)
            init_commit(target)
            before = {
                path.relative_to(target).as_posix(): digest(path)
                for path in target.rglob("*")
                if path.is_file() and ".git" not in path.relative_to(target).parts
            }

            missing = run(
                "python3", str(ENGINE), "--repo-root", str(target), "--rendered", str(rendered),
                cwd=ROOT, expect=2,
            )
            self.assertIn("missing durable ownership state", missing.stderr)
            run(
                "python3", str(ENGINE), "--repo-root", str(target), "--rendered", str(rendered),
                "--bootstrap-map", "--evidence-ref", "evidence:7917", "--apply", cwd=ROOT,
            )
            after = {
                path.relative_to(target).as_posix(): digest(path)
                for path in target.rglob("*")
                if path.is_file() and ".git" not in path.relative_to(target).parts
                and path.relative_to(target).as_posix()
                not in {"contracts/template-ownership.yml", ADOPTION, STATE}
            }
            self.assertEqual(before, after)
            self.assertTrue((target / "contracts/template-ownership.yml").is_file())
            self.assertTrue((target / ADOPTION).is_file())
            self.assertTrue((target / STATE).is_file())
            run(
                "python3", "-I", "-S", "-B", "scripts/lib/check-l1-ownership-state.py",
                cwd=target,
            )

            run("git", "add", ".", cwd=target)
            run("git", "commit", "--quiet", "-m", "ownership bootstrap", cwd=target)
            (target / ADOPTION).unlink()
            run("git", "add", ".", cwd=target)
            run("git", "commit", "--quiet", "-m", "remove required attestation", cwd=target)
            missing_attestation = run(
                "python3", str(ENGINE), "--repo-root", str(target), "--rendered", str(rendered),
                cwd=ROOT, expect=2,
            )
            self.assertIn("requires its census attestation", missing_attestation.stderr)

            run("git", "reset", "--hard", "HEAD^", cwd=target)
            (target / "scripts/ci/full.sh").unlink()
            run("git", "add", ".", cwd=target)
            run("git", "commit", "--quiet", "-m", "delete path after census", cwd=target)
            drift = run(
                "python3", str(ENGINE), "--repo-root", str(target), "--rendered", str(rendered),
                cwd=ROOT, expect=2,
            )
            self.assertIn("drifted after ownership census", drift.stderr)

    def test_first_refresh_consumes_attestation_and_establishes_state(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH_PARENT) as temp:
            parent = Path(temp)
            target = self.copy_fixture(parent, "target")
            rendered = self.copy_fixture(parent, "rendered")
            (target / "contracts/template-ownership.yml").unlink()
            (target / STATE).unlink()
            remove_birth_marker(target)
            with (target / "README.md").open("a", encoding="utf-8") as stream:
                stream.write("\ncompany README sentinel\n")
            with (target / "scripts/ci/full.sh").open("a", encoding="utf-8") as stream:
                stream.write("\n# censused template drift\n")
            init_commit(target)
            readme_hash = digest(target / "README.md")
            plan_artifact = parent / "01-plan.json"
            plan_artifact.write_bytes(PLAN_BYTES)
            wave_id = "wave-first-refresh"

            run(
                "python3", str(ENGINE), "--repo-root", str(target), "--rendered", str(rendered),
                "--bootstrap-map", "--evidence-ref", "evidence:7917", "--apply", cwd=ROOT,
            )
            adoption_hash = digest(target / ADOPTION)
            run("git", "add", ".", cwd=target)
            run("git", "commit", "--quiet", "-m", "ownership bootstrap", cwd=target)
            run(
                "python3", str(ENGINE), "--repo-root", str(target), "--rendered", str(rendered),
                "--apply", "--plan-sha256", PLAN_SHA256, "--wave-id", wave_id,
                "--source-l0-commit", L0_HEAD, cwd=ROOT,
            )
            pending_state = (target / STATE).read_text(encoding="utf-8")
            self.assertIn('"state": "applied_pending_receipt"', pending_state)
            pending_payload = json.loads(pending_state)
            self.assertEqual(
                set(pending_payload),
                {"schema", "kind", "state", "wave_id", "source_l0_commit", "ownership_map_sha256", "plan_sha256"},
            )
            self.assertTrue((target / ADOPTION).exists())
            self.assertEqual(adoption_hash, digest(target / ADOPTION))
            self.assertEqual(readme_hash, digest(target / "README.md"))
            self.assertNotIn("censused template drift", (target / "scripts/ci/full.sh").read_text())
            run("git", "add", ".", cwd=target)
            run("git", "commit", "--quiet", "-m", "applied pending receipt", cwd=target)
            applied_commit = run("git", "rev-parse", "HEAD", cwd=target).stdout.strip()
            ak_mock = make_ak_mock(parent, target, applied_commit, wave_id)
            forged_state = json.loads((target / STATE).read_text(encoding="utf-8"))
            forged_state.update(
                state="established", origin="contract-refresh", wave_task_id=123,
                evidence_id=456, applied_commit=applied_commit,
            )
            (target / STATE).write_text(
                json.dumps(forged_state, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            (target / ADOPTION).unlink()
            run("git", "add", ".", cwd=target)
            run("git", "commit", "--quiet", "-m", "premature local establishment", cwd=target)
            fake_home_bin = parent / "fake-home/.local/bin"
            fake_home_bin.mkdir(parents=True)
            (fake_home_bin / "ak").symlink_to(ak_mock)
            run(
                "env", f"HOME={parent / 'fake-home'}", f"AK_CMD={ak_mock}", "python3", str(ENGINE),
                "--repo-root", str(target), "--rendered", str(rendered), cwd=ROOT, expect=2,
            )
            self.assertFalse((parent / "ak-called").exists())
            run("git", "reset", "--hard", applied_commit, cwd=target)
            OWNERSHIP.finalize(target, "AK-123", plan_artifact, ak_mock)
            self.assertTrue((parent / "ak-called").exists())
            state = (target / STATE).read_text(encoding="utf-8")
            self.assertIn('"state": "established"', state)
            self.assertFalse((target / ADOPTION).exists())
            run("git", "add", ".", cwd=target)
            run("git", "commit", "--quiet", "-m", "ownership evidence closeout", cwd=target)
            established_payload = json.loads((target / STATE).read_text(encoding="utf-8"))
            OWNERSHIP.validate_established_provenance(target, established_payload, ak_mock)

    def test_finalize_accepts_only_linked_worktree_of_canonical_task_repo(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH_PARENT) as temp:
            parent = Path(temp)
            target = self.copy_fixture(parent, "canonical")
            init_commit(target)
            plan_artifact = parent / "01-plan.json"
            plan_artifact.write_bytes(PLAN_BYTES)
            wave_id = "wave-linked-worktree"
            (target / STATE).write_bytes(
                OWNERSHIP.pending_state_bytes(target, PLAN_SHA256, wave_id, L0_HEAD)
            )
            run("git", "add", STATE, cwd=target)
            run("git", "commit", "--quiet", "-m", "applied pending receipt", cwd=target)
            applied_commit = run("git", "rev-parse", "HEAD", cwd=target).stdout.strip()

            linked = parent / "linked"
            run("git", "worktree", "add", "--quiet", "--detach", str(linked), applied_commit, cwd=target)
            ak_mock = make_ak_mock(
                parent, linked, applied_commit, wave_id, authority_repo=target
            )
            with mock.patch.dict(
                os.environ,
                {"GIT_DIR": str(target / ".git"), "GIT_WORK_TREE": str(target)},
            ):
                OWNERSHIP.finalize(linked, "AK-123", plan_artifact, ak_mock)
            established_payload = json.loads((linked / STATE).read_text(encoding="utf-8"))
            self.assertEqual(established_payload["state"], "established")
            OWNERSHIP.validate_established_provenance(linked, established_payload, ak_mock)
            self.assertEqual(
                json.loads((target / STATE).read_text(encoding="utf-8"))["state"],
                "applied_pending_receipt",
            )

            unregistered = parent / "unregistered-common-dir"
            shutil.copytree(target, unregistered, ignore=shutil.ignore_patterns(".git"))
            (unregistered / ".git").write_text(
                f"gitdir: {(target / '.git').resolve()}\n", encoding="utf-8"
            )
            self.assertEqual(
                Path(
                    run("git", "rev-parse", "--git-common-dir", cwd=unregistered).stdout.strip()
                ).resolve(),
                (target / ".git").resolve(),
            )
            with self.assertRaisesRegex(ValueError, "same Git repository"):
                OWNERSHIP.finalize(unregistered, "AK-123", plan_artifact, ak_mock)

            shared_clone = parent / "shared-clone"
            run("git", "clone", "--quiet", "--shared", str(target), str(shared_clone), cwd=parent)
            alternates = shared_clone / ".git/objects/info/alternates"
            self.assertTrue(alternates.is_file())
            self.assertIn(str((target / ".git/objects").resolve()), alternates.read_text())
            with self.assertRaisesRegex(ValueError, "same Git repository"):
                OWNERSHIP.finalize(shared_clone, "AK-123", plan_artifact, ak_mock)

            clone = parent / "separate-clone"
            run("git", "clone", "--quiet", "--no-local", str(target), str(clone), cwd=parent)
            with self.assertRaisesRegex(ValueError, "same Git repository"):
                OWNERSHIP.finalize(clone, "AK-123", plan_artifact, ak_mock)

            run("git", "worktree", "remove", "--force", str(linked), cwd=target)

    def test_clean_target_ignores_ambient_status_config(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH_PARENT) as temp:
            parent = Path(temp)
            target = self.copy_fixture(parent, "target")
            init_commit(target)
            (target / "untracked-by-operator.txt").write_text("must remain visible\n")
            with mock.patch.dict(
                os.environ, {"GIT_CONFIG_PARAMETERS": "'status.showUntrackedFiles=no'"}
            ):
                hidden = subprocess.run(
                    ["git", "-C", str(target), "status", "--porcelain"],
                    text=True,
                    capture_output=True,
                    check=True,
                )
                self.assertEqual(hidden.stdout, "")
                with self.assertRaisesRegex(ValueError, "clean worktree"):
                    OWNERSHIP.ensure_clean_git_target(target)

    def test_invalid_or_unclassified_render_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH_PARENT) as temp:
            parent = Path(temp)
            target = self.copy_fixture(parent, "target")
            rendered = self.copy_fixture(parent, "rendered")
            forged = self.copy_fixture(parent, "forged-established")
            remove_birth_marker(forged)
            init_commit(forged)
            init_commit(target)
            forged_result = run(
                "python3", str(ENGINE), "--repo-root", str(forged), "--rendered", str(rendered),
                cwd=ROOT, expect=2,
            )
            self.assertIn("root commit lacks its ownership marker", forged_result.stderr)
            (rendered / "new-unclassified-root.txt").write_text("unknown\n", encoding="utf-8")
            result = run(
                "python3", str(ENGINE), "--repo-root", str(target), "--rendered", str(rendered),
                cwd=ROOT, expect=2,
            )
            self.assertIn("unclassified rendered path", result.stderr)

            (rendered / "new-unclassified-root.txt").unlink()
            ownership = rendered / "contracts/template-ownership.yml"
            ownership.write_text(
                ownership.read_text(encoding="utf-8") + "  - scripts/**\n",
                encoding="utf-8",
            )
            ambiguous = run(
                "python3", str(ENGINE), "--repo-root", str(target), "--rendered", str(rendered),
                cwd=ROOT, expect=2,
            )
            self.assertIn("ambiguous ownership patterns", ambiguous.stderr)

    def test_preview_rejects_symlinked_destination_before_reading(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH_PARENT) as temp:
            parent = Path(temp)
            target = self.copy_fixture(parent, "target")
            rendered = self.copy_fixture(parent, "rendered")
            init_commit(target)
            external = parent / "external"
            external.mkdir()
            (external / "ci").mkdir()
            secret = "external-secret-must-not-be-disclosed"
            (external / "ci/full.sh").write_text(secret, encoding="utf-8")
            shutil.rmtree(target / "scripts")
            (target / "scripts").symlink_to(external, target_is_directory=True)
            result = run(
                "python3", str(ENGINE), "--repo-root", str(target), "--rendered", str(rendered),
                cwd=ROOT, expect=2,
            )
            self.assertIn("symlinked destination ancestor", result.stderr)
            self.assertNotIn(secret, result.stdout + result.stderr)

            control_target = self.copy_fixture(parent, "control-target")
            init_commit(control_target)
            control_external = parent / "control-external"
            control_external.mkdir()
            (control_external / "template-ownership.yml").write_text(secret, encoding="utf-8")
            shutil.rmtree(control_target / "contracts")
            (control_target / "contracts").symlink_to(control_external, target_is_directory=True)
            control_result = run(
                "python3", str(ENGINE), "--repo-root", str(control_target),
                "--rendered", str(rendered), cwd=ROOT, expect=2,
            )
            self.assertIn("symlinked destination ancestor", control_result.stderr)
            self.assertNotIn(secret, control_result.stdout + control_result.stderr)


if __name__ == "__main__":
    unittest.main()
