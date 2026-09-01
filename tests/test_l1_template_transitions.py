from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures/l1/template-repo"
ENGINE = ROOT / "scripts/lib/l1_template_transitions.py"
SCRATCH = Path(os.environ.get("TMPDIR", str(ROOT)))
SPEC = importlib.util.spec_from_file_location("l1_template_transitions", ENGINE)
assert SPEC and SPEC.loader
TRANSITIONS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(TRANSITIONS)


def run(*args: str, cwd: Path, expect: int = 0, input: str | None = None) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, cwd=cwd, text=True, input=input, capture_output=True)
    if result.returncode != expect:
        raise AssertionError(f"{args}: {result.returncode} != {expect}\n{result.stdout}\n{result.stderr}")
    return result


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def git(repo: Path, *args: str) -> str:
    return run("git", *args, cwd=repo).stdout.strip()


def init(repo: Path) -> None:
    run("git", "init", "--quiet", cwd=repo)
    run("git", "config", "user.name", "transition test", cwd=repo)
    run("git", "config", "user.email", "test@example.invalid", cwd=repo)
    run("git", "add", ".", cwd=repo)
    run("git", "commit", "--quiet", "-m", "root with accepted ADR", cwd=repo)


class Harness:
    def __init__(self, parent: Path):
        self.parent = parent
        self.source = parent / "ontology-source"
        self.source.mkdir()
        (self.source / "README.md").write_text("ontology source\n", encoding="utf-8")
        init(self.source)
        self.gitlink_oid = git(self.source, "rev-parse", "HEAD")
        self.repo = parent / "canonical"
        shutil.copytree(FIXTURE, self.repo)
        adr = self.repo / "docs/decisions/ownership.md"
        adr.parent.mkdir(parents=True, exist_ok=True)
        adr.write_text("# Accepted ownership transition\n", encoding="utf-8")
        init(self.repo)
        self.base = git(self.repo, "rev-parse", "HEAD")
        self.executor = "transition-executor"
        self.task = {
            "id": 321, "repo": str(self.repo.resolve()), "status": "claimed",
            "claimed_by": self.executor,
        }
        self.decision = {
            "decision": {
                "id": 77, "scope": "repo", "repo_scope": str(self.repo.resolve()),
                "outcome": "accepted", "adr_ref": "docs/decisions/ownership.md",
            },
            "linked_tasks": [{"task_id": 321, "link_role": "post_adr_execution"}],
        }
        self.evidence: list[dict[str, object]] = []
        self.task_json = parent / "task.json"
        self.decision_json = parent / "decision.json"
        self.evidence_json = parent / "evidence.json"
        self.ak = parent / "ak"
        self.write_authority()
        self.ak.write_text(
            "#!/bin/sh\n"
            "case \"$1 $2\" in\n"
            f" 'task show') cat '{self.task_json}' ;;\n"
            f" 'decision get') cat '{self.decision_json}' ;;\n"
            f" 'evidence task') cat '{self.evidence_json}' ;;\n"
            " *) exit 2 ;;\n"
            "esac\n",
            encoding="utf-8",
        )
        self.ak.chmod(0o755)
        old = (self.repo / "contracts/template-ownership.yml").read_text(encoding="utf-8")
        self.next_map = parent / "next-map.yml"
        self.next_map.write_text(
            old.replace("  - ontology/**\n", "").replace(
                "agent_owned:\n", "agent_owned:\n  - .gitmodules\n  - ontology\n"
            ),
            encoding="utf-8",
        )
        self.gitmodules = f"[submodule \"ontology\"]\n\tpath = ontology\n\turl = {self.source}\n"
        old_line = git(self.repo, "ls-files", "-s", "ontology/.gitkeep").split()
        module_oid = run("git", "hash-object", "--stdin", cwd=self.repo, input=self.gitmodules).stdout.strip()
        self.delta = [
            {"path": ".gitmodules", "old_mode": "000000", "new_mode": "100644", "old_oid": None,
             "new_oid": module_oid, "content_sha256": sha(self.gitmodules.encode())},
            {"path": "ontology", "old_mode": "000000", "new_mode": "160000", "old_oid": None,
             "new_oid": self.gitlink_oid, "content_sha256": None},
            {"path": "ontology/.gitkeep", "old_mode": old_line[0], "new_mode": "000000",
             "old_oid": old_line[1], "new_oid": None, "content_sha256": None},
        ]
        self.spec_path = parent / "spec.json"
        self.plan_path = parent / "plan.json"
        self.spec = {
            "decision_id": 77, "adr_commit": self.base, "transition_task_id": 321,
            "executor": self.executor, "next_map": str(self.next_map.resolve()),
            "git_delta": self.delta,
            "validation": [
                {"id": "check-template-ci", "command": "bash scripts/check-template-ci.sh"},
                {"id": "ci-full", "command": "bash scripts/ci/full.sh"},
            ],
            "rollback": "git revert final state commit, then pending topology commit",
        }
        self.spec_path.write_text(json.dumps(self.spec), encoding="utf-8")

    def write_authority(self) -> None:
        self.task_json.write_text(json.dumps(self.task), encoding="utf-8")
        self.decision_json.write_text(json.dumps(self.decision), encoding="utf-8")
        self.evidence_json.write_text(json.dumps(self.evidence), encoding="utf-8")

    def plan(self) -> dict[str, object]:
        TRANSITIONS.create_plan(self.repo, self.spec_path, self.plan_path, self.ak)
        return json.loads(self.plan_path.read_text(encoding="utf-8"))

    def stage_payload(self) -> None:
        run("git", "rm", "--quiet", "ontology/.gitkeep", cwd=self.repo)
        run("git", "-c", "protocol.file.allow=always", "submodule", "add", "--quiet", str(self.source), "ontology", cwd=self.repo)

    def pending_commit(self, plan: dict[str, object]) -> str:
        TRANSITIONS.apply(self.repo, self.plan_path, self.ak)
        run("git", "add", "contracts/template-ownership.yml", "contracts/template-ownership-state.json", cwd=self.repo)
        run("git", "commit", "--quiet", "-m", "pending ownership topology", cwd=self.repo)
        applied = git(self.repo, "rev-parse", "HEAD")
        details = {
            "plan": plan, "applied_commit": applied,
            "validation_results": {"check-template-ci": 0, "ci-full": 0},
        }
        self.evidence = [{
            "id": 901, "task_id": 321, "repo": str(self.repo.resolve()),
            "repo_scope": str(self.repo.resolve()), "check_type": "l1_ownership_transition_v1",
            "result": "pass", "details": details,
        }]
        self.write_authority()
        return applied


class TransitionTests(unittest.TestCase):
    def test_regular_tree_to_gitlink_two_commit_transition(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH) as raw:
            h = Harness(Path(raw))
            plan = h.plan()
            self.assertEqual(plan["schema"], "ai-society.template-ownership-transition-plan/1")
            self.assertEqual(plan["git_delta"], h.delta)
            h.stage_payload()
            applied = h.pending_commit(plan)
            pending = json.loads((h.repo / "contracts/template-ownership-state.json").read_text())
            self.assertEqual(pending["schema"], "ai-society.template-ownership-state/2")
            self.assertEqual(pending["state"], "ownership_transition_pending_receipt")
            TRANSITIONS.finalize(h.repo, h.plan_path, "AK-321", h.ak)
            run("git", "add", "contracts/template-ownership-state.json", cwd=h.repo)
            run("git", "commit", "--quiet", "-m", "finalize ownership evidence", cwd=h.repo)
            state = json.loads((h.repo / "contracts/template-ownership-state.json").read_text())
            self.assertEqual(state["origin"], "ownership-transition")
            self.assertEqual(state["applied_commit"], applied)
            TRANSITIONS.validate_v2_provenance(h.repo, state, h.ak)
            run("python3", "-I", "-S", "-B", "scripts/lib/check-l1-ownership-state.py", cwd=h.repo)
            saved_evidence = json.loads(json.dumps(h.evidence))
            h.evidence[0]["details"] = {"plan": plan, "applied_commit": applied, "validation_results": {}}
            h.write_authority()
            with self.assertRaisesRegex(ValueError, "exactly one"):
                TRANSITIONS.validate_v2_provenance(h.repo, state, h.ak)
            h.evidence = saved_evidence; h.write_authority()
            (h.repo / "later.txt").write_text("ordinary later work\n", encoding="utf-8")
            run("git", "add", "later.txt", cwd=h.repo)
            run("git", "commit", "--quiet", "-m", "ordinary later commit", cwd=h.repo)
            TRANSITIONS.validate_v2_provenance(h.repo, state, h.ak)
            run("python3", "-I", "-S", "-B", "scripts/lib/check-l1-ownership-state.py", cwd=h.repo)

    def test_plan_is_canonical_and_rejects_dirty_target(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH) as raw:
            h = Harness(Path(raw))
            first = h.plan()
            before = h.plan_path.read_bytes()
            h.plan()
            self.assertEqual(before, h.plan_path.read_bytes())
            self.assertEqual(first["canonical_plan_sha256"], TRANSITIONS.plan_hash(first))
            (h.repo / "operator.txt").write_text("drift\n")
            with self.assertRaisesRegex(ValueError, "clean worktree"):
                h.plan()

    def test_plan_rejects_control_traversal_duplicate_and_ancestor_ambiguity(self) -> None:
        good = {"path": "payload", "old_mode": "000000", "new_mode": "100644", "old_oid": None,
                "new_oid": "a" * 40, "content_sha256": "b" * 64}
        for bad, message in [
            (dict(good, path=".git"), "control|unsafe"),
            (dict(good, path="../escape"), "unsafe"),
            ([good, good], "duplicate"),
            ([good, dict(good, path="payload/child")], "ancestor-ambiguous"),
        ]:
            value = bad if isinstance(bad, list) else [bad]
            with self.assertRaisesRegex(ValueError, message):
                TRANSITIONS.validate_git_delta(value)

    def test_apply_rejects_wrong_staged_payload_and_untracked_drift(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH) as raw:
            h = Harness(Path(raw)); h.plan()
            (h.repo / "wrong").write_text("wrong\n")
            run("git", "add", "wrong", cwd=h.repo)
            with self.assertRaisesRegex(ValueError, "exactly match"):
                TRANSITIONS.apply(h.repo, h.plan_path, h.ak)
            run("git", "reset", "--hard", "HEAD", cwd=h.repo)
            h.stage_payload(); (h.repo / "untracked").write_text("drift\n")
            with self.assertRaisesRegex(ValueError, "unstaged, untracked"):
                TRANSITIONS.apply(h.repo, h.plan_path, h.ak)

    def test_apply_rejects_predecessor_and_plan_drift(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH) as raw:
            h = Harness(Path(raw)); h.plan(); h.stage_payload()
            plan = json.loads(h.plan_path.read_text()); plan["base_commit"] = "a" * 40
            plan["canonical_plan_sha256"] = TRANSITIONS.plan_hash(plan)
            h.plan_path.write_text(json.dumps(plan))
            with self.assertRaisesRegex(ValueError, "base commit drifted"):
                TRANSITIONS.apply(h.repo, h.plan_path, h.ak)
            plan["canonical_plan_sha256"] = "b" * 64
            h.plan_path.write_text(json.dumps(plan))
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                TRANSITIONS.apply(h.repo, h.plan_path, h.ak)

    def test_authority_rejects_decision_task_executor_and_repo_drift(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH) as raw:
            h = Harness(Path(raw))
            cases = [
                (lambda: h.decision["decision"].update(outcome="rejected"), "Decision/ADR"),
                (lambda: h.decision.update(linked_tasks=[]), "Decision/ADR"),
                (lambda: h.task.update(claimed_by="other"), "executor"),
                (lambda: h.task.update(repo=str((h.parent / "other").resolve())), "Git repository|registered worktree|provenance check"),
            ]
            for mutate, message in cases:
                original_task = dict(h.task); original_decision = json.loads(json.dumps(h.decision))
                mutate(); h.write_authority()
                with self.assertRaisesRegex((ValueError, OSError), message):
                    h.plan()
                h.task = original_task; h.decision = original_decision; h.write_authority()

    def test_finalize_rejects_duplicate_evidence_wrong_parent_and_worktree_drift(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH) as raw:
            h = Harness(Path(raw)); plan = h.plan(); h.stage_payload(); h.pending_commit(plan)
            h.evidence.append(dict(h.evidence[0], id=902)); h.write_authority()
            with self.assertRaisesRegex(ValueError, "exactly one"):
                TRANSITIONS.finalize(h.repo, h.plan_path, "AK-321", h.ak)
            h.evidence = h.evidence[:1]; h.write_authority()
            (h.repo / "drift").write_text("x")
            with self.assertRaisesRegex(ValueError, "clean worktree"):
                TRANSITIONS.finalize(h.repo, h.plan_path, "AK-321", h.ak)
            (h.repo / "drift").unlink()
            with self.assertRaisesRegex(ValueError, "does not match"):
                TRANSITIONS.finalize(h.repo, h.plan_path, "AK-999", h.ak)

    def test_plan_derivations_and_required_gates_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH) as raw:
            h = Harness(Path(raw)); plan = h.plan(); h.stage_payload()
            for mutate, message in [
                (lambda value: value.update(map_delta={"template_added": []}), "map_delta"),
                (lambda value: value.update(target_repo=str((h.parent / "other").resolve())), "target_repo"),
                (lambda value: value.update(validation=[{"id": "fake", "command": "true"}]), "required L1 gate"),
            ]:
                forged = json.loads(json.dumps(plan)); mutate(forged)
                forged["canonical_plan_sha256"] = TRANSITIONS.plan_hash(forged)
                h.plan_path.write_text(json.dumps(forged), encoding="utf-8")
                with self.assertRaisesRegex(ValueError, message):
                    TRANSITIONS.apply(h.repo, h.plan_path, h.ak)

    def test_binary_blob_hash_and_malformed_or_weakened_evidence_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH) as raw:
            parent = Path(raw); repo = parent / "binary"; repo.mkdir()
            (repo / "seed").write_text("seed\n", encoding="utf-8"); init(repo)
            payload = b"\xff\x00\r\nbytes\n"; (repo / "payload.bin").write_bytes(payload)
            run("git", "add", "payload.bin", cwd=repo)
            delta = TRANSITIONS.index_delta(repo)
            self.assertEqual(delta[0]["content_sha256"], sha(payload))
            transition_parent = parent / "transition"; transition_parent.mkdir()
            h = Harness(transition_parent); plan = h.plan(); h.stage_payload(); h.pending_commit(plan)
            valid = json.loads(json.dumps(h.evidence[0]))
            for malformed in [
                None,
                dict(valid, id=True),
                dict(valid, details=dict(valid["details"], validation_results={"check-template-ci": False, "ci-full": 0})),
            ]:
                h.evidence = [malformed]; h.write_authority()
                with self.assertRaisesRegex(ValueError, "exactly one"):
                    TRANSITIONS.finalize(h.repo, h.plan_path, "AK-321", h.ak)

    def test_git_replace_objects_cannot_rewrite_provenance(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH) as raw:
            repo = Path(raw) / "repo"; repo.mkdir()
            (repo / "seed").write_text("real\n", encoding="utf-8"); init(repo)
            head = git(repo, "rev-parse", "HEAD")
            (repo / "seed").write_text("forged\n", encoding="utf-8")
            run("git", "add", "seed", cwd=repo); tree = git(repo, "write-tree")
            run("git", "reset", "--hard", "HEAD", cwd=repo)
            replacement = run("git", "commit-tree", tree, "-p", head, cwd=repo, input="replacement\n").stdout.strip()
            run("git", "replace", head, replacement, cwd=repo)
            self.assertEqual(git(repo, "show", f"{head}:seed"), "forged")
            self.assertEqual(TRANSITIONS.git_bytes(repo, "show", f"{head}:seed"), b"real\n")

    def test_registered_linked_worktree_and_git_environment_hardening(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH) as raw:
            h = Harness(Path(raw)); linked = h.parent / "linked"
            run("git", "worktree", "add", "--quiet", "--detach", str(linked), h.base, cwd=h.repo)
            h.task["repo"] = str(h.repo.resolve()); h.write_authority()
            with mock.patch.dict(os.environ, {"GIT_DIR": str(h.repo / ".git"), "GIT_WORK_TREE": str(h.repo)}):
                TRANSITIONS.verify_authority(linked, 77, 321, h.executor, h.base, h.ak)
            alias = h.parent / "alias"
            shutil.copytree(h.repo, alias, ignore=shutil.ignore_patterns(".git"))
            (alias / ".git").write_text(f"gitdir: {(h.repo / '.git').resolve()}\n")
            with self.assertRaisesRegex(ValueError, "registered worktree"):
                TRANSITIONS.verify_authority(alias, 77, 321, h.executor, h.base, h.ak)
            run("git", "worktree", "remove", "--force", str(linked), cwd=h.repo)


if __name__ == "__main__":
    unittest.main()
