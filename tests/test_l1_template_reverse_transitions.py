"""Reverse topology proofs use local Git repositories and fixture AK authority only."""

from __future__ import annotations

import copy
import itertools
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tests.test_l1_template_transitions import Harness, ROOT, SCRATCH, TRANSITIONS, git, run, sha

MAP = "contracts/template-ownership.yml"
STATE = "contracts/template-ownership-state.json"
CHECKER = "scripts/lib/check-l1-ownership-state.py"
FILES = {
    "ontology/README.md": (b"ordinary ontology files\n", "100644"),
    "ontology/nested/payload.bin": (b"\xff\x00\r\nbinary\n", "100644"),
    "ontology/nested/run.sh": (b"#!/bin/sh\nexit 0\n", "100755"),
}


def entry(path: str, old: str = "000000", new: str = "100644") -> dict[str, object]:
    return {
        "path": path, "old_mode": old, "new_mode": new,
        "old_oid": None if old == "000000" else "a" * 40,
        "new_oid": None if new == "000000" else "b" * 40,
        "content_sha256": "c" * 64 if new in {"100644", "100755", "120000"} else None,
    }


def controls(repo: Path) -> tuple[bytes, bytes]:
    return (repo / MAP).read_bytes(), (repo / STATE).read_bytes()


def commit(repo: Path, message: str, *paths: str) -> str:
    run("git", "add", *paths, cwd=repo)
    run("git", "commit", "--quiet", "-m", message, cwd=repo)
    return git(repo, "rev-parse", "HEAD")


def check_history(repo: Path, expect: int = 0) -> str:
    return run("python3", "-I", "-S", "-B", CHECKER, cwd=repo, expect=expect).stderr


class ReverseHarness(Harness):
    def __init__(self, parent: Path):
        super().__init__(parent)
        # Establish a real v2 predecessor through the existing forward lifecycle.
        forward = self.plan()
        super().stage_payload()
        super().pending_commit(forward)
        TRANSITIONS.finalize(self.repo, self.plan_path, "AK-321", self.ak)
        self.reverse_base = commit(self.repo, "finalize forward receipt", STATE)
        check_history(self.repo)
        self.forward_controls = controls(self.repo)
        self.next_map.write_bytes(self.forward_controls[0].replace(
            b"  - ontology\n", b"  - ontology/**\n"
        ))
        self.delta = []
        for path in (".gitmodules", "ontology"):
            mode, oid, *_ = git(self.repo, "ls-files", "-s", path).split()
            self.delta.append(dict(entry(path, mode, "000000"), old_oid=oid))
        for path, (raw, mode) in FILES.items():
            oid = subprocess.run(
                ["git", "hash-object", "--stdin"], cwd=self.repo,
                input=raw, capture_output=True, check=True,
            ).stdout.decode().strip()
            self.delta.append(dict(entry(path, new=mode), new_oid=oid, content_sha256=sha(raw)))
        self.spec["git_delta"] = self.delta
        self.spec["rollback"] = "Revert the state-only final commit, then the pending topology commit."
        self.spec_path.write_text(json.dumps(self.spec))

    def stage_payload(self) -> None:
        run("git", "submodule", "deinit", "--force", "ontology", cwd=self.repo)
        run("git", "rm", "--force", "ontology", cwd=self.repo)
        run("git", "rm", "--force", ".gitmodules", cwd=self.repo)
        for path, (raw, mode) in FILES.items():
            target = self.repo / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            target.chmod(0o755 if mode == "100755" else 0o644)
        run("git", "add", "ontology", cwd=self.repo)

    def pending_commit(self, plan: dict[str, object]) -> str:
        previous = copy.deepcopy(self.evidence)
        with mock.patch.object(TRANSITIONS, "write_atomic", wraps=TRANSITIONS.write_atomic) as writer:
            applied = super().pending_commit(plan)
        destinations = [call.args[1] for call in writer.call_args_list]
        if destinations != [self.repo / MAP, self.repo / STATE]:
            raise AssertionError(f"apply wrote outside its two control files: {destinations}")
        self.evidence[0]["id"] = max(record["id"] for record in previous) + 1
        self.evidence = previous + self.evidence
        self.write_authority()
        return applied

    def finish(self, plan: dict[str, object]) -> tuple[str, str]:
        applied = self.pending_commit(plan)
        check_history(self.repo)
        TRANSITIONS.finalize(self.repo, self.plan_path, "AK-321", self.ak)
        final = commit(self.repo, "finalize reverse receipt", STATE)
        self.validate()
        return applied, final

    def validate(self) -> None:
        state = json.loads((self.repo / STATE).read_bytes())
        TRANSITIONS.validate_v2_provenance(self.repo, state, self.ak)
        check_history(self.repo)


class ReverseTransitionTests(unittest.TestCase):
    def test_full_reverse_lifecycle_and_inverse_rollback(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH) as raw:
            h = ReverseHarness(Path(raw))
            # Execute the generated checker, not a validator-only substitute.
            self.assertEqual((ROOT / "copier-template" / CHECKER).read_bytes(),
                             (h.repo / CHECKER).read_bytes())
            before = controls(h.repo)
            plan = h.plan()
            canonical = h.plan_path.read_bytes()
            h.plan()
            self.assertEqual(canonical, h.plan_path.read_bytes())
            self.assertEqual(controls(h.repo), before)
            self.assertEqual(git(h.repo, "status", "--porcelain"), "")
            self.assertEqual(plan["base_commit"], h.reverse_base)
            self.assertEqual(plan["predecessor_state_sha256"], sha(before[1]))
            self.assertEqual(plan["predecessor_map_sha256"], sha(before[0]))
            h.stage_payload()
            self.assertEqual(TRANSITIONS.index_delta(h.repo), plan["git_delta"])
            applied, final = h.finish(plan)
            self.assertEqual(git(h.repo, "rev-parse", f"{applied}^"), h.reverse_base)
            self.assertEqual(git(h.repo, "rev-parse", f"{final}^"), applied)
            self.assertEqual(git(h.repo, "diff-tree", "--no-commit-id", "--name-only", "-r", final), STATE)
            for path, (content, mode) in FILES.items():
                self.assertEqual((h.repo / path).read_bytes(), content)
                self.assertEqual(git(h.repo, "ls-files", "-s", path).split()[0], mode)
            self.assertFalse((h.repo / ".gitmodules").exists())
            self.assertNotIn("160000", git(h.repo, "ls-files", "-s", "ontology"))
            self.assertEqual(git(h.repo, "status", "--porcelain"), "")
            # Rollback is an actual inverse Git history, not an English instruction.
            run("git", "revert", "--no-edit", final, cwd=h.repo)
            run("git", "revert", "--no-edit", applied, cwd=h.repo)
            self.assertEqual(git(h.repo, "rev-parse", "HEAD^{tree}"),
                             git(h.repo, "rev-parse", f"{h.reverse_base}^{{tree}}"))
            self.assertEqual(controls(h.repo), h.forward_controls)
            h.validate()

    def test_receipted_forward_inverse_after_reverse(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH) as raw:
            h = ReverseHarness(Path(raw))
            plan = h.plan()
            h.stage_payload()
            h.finish(plan)
            # Reverse every payload entry and restore the predecessor ownership map.
            inverse = []
            for item in plan["git_delta"]:
                content = None
                if item["old_mode"] in {"100644", "100755"}:
                    content = sha(TRANSITIONS.git_bytes(h.repo, "cat-file", "blob", item["old_oid"]))
                inverse.append({
                    "path": item["path"], "old_mode": item["new_mode"], "new_mode": item["old_mode"],
                    "old_oid": item["new_oid"], "new_oid": item["old_oid"], "content_sha256": content,
                })
            h.spec["git_delta"] = inverse
            h.next_map.write_bytes(h.forward_controls[0])
            h.spec_path.write_text(json.dumps(h.spec))
            inverse_plan = h.plan()
            run("git", "rm", "-r", "ontology", cwd=h.repo)
            (h.repo / ".gitmodules").write_text(h.gitmodules)
            run("git", "add", ".gitmodules", cwd=h.repo)
            run("git", "update-index", "--add", "--cacheinfo", "160000", h.gitlink_oid,
                "ontology", cwd=h.repo)
            run("git", "-c", "protocol.file.allow=always", "submodule", "update", "--init",
                "--", "ontology", cwd=h.repo)
            h.finish(inverse_plan)
            self.assertEqual(git(h.repo, "ls-files", "-s", "ontology").split()[:2],
                             ["160000", h.gitlink_oid])
            self.assertEqual((h.repo / MAP).read_bytes(), h.forward_controls[0])
            (h.repo / "later.txt").write_text("later ordinary work\n")
            commit(h.repo, "ordinary descendant", "later.txt")
            h.validate()

    def test_reverse_exception_is_order_independent_and_regular_files_only(self) -> None:
        parent = entry("ontology", "160000", "000000")
        children = [entry("ontology/a"), entry("ontology/deep/b", new="100755")]
        expected = sorted([parent, *children], key=lambda item: item["path"])
        for permutation in itertools.permutations(expected):
            self.assertEqual(TRANSITIONS.validate_git_delta(list(permutation)), expected)
        for bad_parent in [entry("ontology", "100644", "000000"),
                           entry("ontology", "120000", "000000"),
                           entry("ontology", "160000", "100644"),
                           entry("ontology", "160000", "160000")]:
            self.assert_rejected_pair(bad_parent, children[0], "ancestor-ambiguous")
        for bad_child in [entry("ontology/a", "100644", "100644"),
                          entry("ontology/a", "100644", "000000"),
                          entry("ontology/a", new="120000"),
                          entry("ontology/a", new="160000"),
                          entry("ontology/a", new="040000")]:
            self.assert_rejected_pair(parent, bad_child, "ancestor-ambiguous|unsupported Git mode")
        # A legitimate parent removal must not excuse ambiguity between descendants.
        with self.assertRaisesRegex(ValueError, "ancestor-ambiguous"):
            TRANSITIONS.validate_git_delta([parent, entry("ontology/a"), entry("ontology/a/b")])
        with self.assertRaisesRegex(ValueError, "ancestor-ambiguous"):
            TRANSITIONS.validate_git_delta([parent, entry("other"), entry("other/child")])

    def assert_rejected_pair(self, parent: dict, child: dict, message: str) -> None:
        for pair in ([parent, child], [child, parent]):
            with self.subTest(pair=pair), self.assertRaisesRegex(ValueError, message):
                TRANSITIONS.validate_git_delta(pair)

    def test_reverse_rejects_malformed_schema_paths_and_bindings(self) -> None:
        parent = entry("ontology", "160000", "000000")
        child = entry("ontology/a")
        for bad, message in [
            (dict(parent, old_oid=None), "full Git OID"),
            (dict(parent, new_oid="a" * 40), "null OID"),
            (dict(parent, content_sha256="c" * 64), "must be null"),
            (dict(child, old_oid="a" * 40), "null OID"),
            (dict(child, new_oid="A" * 40), "full Git OID"),
            (dict(child, content_sha256=None), "content_sha256"),
            (dict(child, extra=True), "six-field"),
        ]:
            with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, message):
                TRANSITIONS.validate_git_delta([bad])
        for path in ("ontology/../escape", "ontology/.git/config", "ontology//a",
                     "ontology/./a", "ontology/a/", "/escape", "ontology\\a", MAP, STATE):
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, "path"):
                TRANSITIONS.validate_git_delta([dict(child, path=path)])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            TRANSITIONS.validate_git_delta([parent, child, child])

    def test_apply_rejections_leave_control_files_unchanged(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH) as raw:
            h = ReverseHarness(Path(raw))
            plan = h.plan()
            h.stage_payload()
            before = controls(h.repo)
            for key, value in (("old_oid", "a" * 40), ("new_oid", "b" * 40),
                               ("content_sha256", "c" * 64), ("new_mode", "100755")):
                forged = copy.deepcopy(plan)
                target = next(item for item in forged["git_delta"] if item["path"] == "ontology/README.md")
                if key == "old_oid":
                    target = next(item for item in forged["git_delta"] if item["path"] == "ontology")
                target[key] = value
                forged["canonical_plan_sha256"] = TRANSITIONS.plan_hash(forged)
                h.plan_path.write_text(json.dumps(forged))
                with self.subTest(key=key), self.assertRaisesRegex(ValueError, "exactly match"):
                    TRANSITIONS.apply(h.repo, h.plan_path, h.ak)
                self.assertEqual(controls(h.repo), before)
            h.plan_path.write_text(json.dumps(plan))
            extra = h.repo / "outside-plan.txt"
            extra.write_text("unscoped\n")
            for staged in (False, True):
                if staged:
                    run("git", "add", extra.name, cwd=h.repo)
                with self.assertRaisesRegex(ValueError, "untracked|exactly match"):
                    TRANSITIONS.apply(h.repo, h.plan_path, h.ak)
                self.assertEqual(controls(h.repo), before)
            run("git", "rm", "--force", extra.name, cwd=h.repo)
            payload = h.repo / "ontology/README.md"
            payload.unlink()
            payload.symlink_to(h.parent / "outside")
            run("git", "add", "ontology/README.md", cwd=h.repo)
            with self.assertRaisesRegex(ValueError, "ancestor-ambiguous"):
                TRANSITIONS.apply(h.repo, h.plan_path, h.ak)
            self.assertEqual(controls(h.repo), before)

    def test_reverse_receipt_and_history_rejections(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH) as raw:
            h = ReverseHarness(Path(raw))
            plan = h.plan()
            h.stage_payload()
            applied = h.pending_commit(plan)
            before = controls(h.repo)
            valid = copy.deepcopy(h.evidence)
            for mutate in (
                lambda: h.evidence.pop(),
                lambda: h.evidence.append(dict(h.evidence[-1], id=999)),
                lambda: h.evidence[-1]["details"]["validation_results"].update({"ci-full": 1}),
                lambda: h.evidence[-1]["details"]["plan"].update(rollback="forged"),
            ):
                h.evidence = copy.deepcopy(valid)
                mutate()
                h.write_authority()
                with self.assertRaisesRegex(ValueError, "exactly one"):
                    TRANSITIONS.finalize(h.repo, h.plan_path, "AK-321", h.ak)
                self.assertEqual(controls(h.repo), before)
            h.evidence = valid
            h.write_authority()
            check_history(h.repo)
            # Generated structural checking must still reject agent-to-template adoption.
            (h.repo / MAP).write_bytes(h.forward_controls[0].replace(
                b"  - ontology\n", b""
            ).replace(b"template_owned:\n", b"template_owned:\n  - ontology/**\n"))
            forged = json.loads(before[1])
            forged["ownership_map_sha256"] = sha((h.repo / MAP).read_bytes())
            (h.repo / STATE).write_text(json.dumps(forged))
            self.assertIn("agent-to-template", check_history(h.repo, expect=2))
            (h.repo / MAP).write_bytes(before[0])
            (h.repo / STATE).write_bytes(before[1])
            # Extra committed writes cannot be hidden behind a valid receipt.
            (h.repo / "unplanned").write_text("unplanned\n")
            run("git", "add", "unplanned", cwd=h.repo)
            run("git", "commit", "--amend", "--no-edit", "--quiet", cwd=h.repo)
            h.evidence[-1]["details"]["applied_commit"] = git(h.repo, "rev-parse", "HEAD")
            h.write_authority()
            with self.assertRaisesRegex(ValueError, "exactly match plan plus control"):
                TRANSITIONS.finalize(h.repo, h.plan_path, "AK-321", h.ak)
            self.assertEqual(controls(h.repo), before)
            run("git", "reset", "--hard", applied, cwd=h.repo)
            h.evidence[-1]["details"]["applied_commit"] = applied
            h.write_authority()
            TRANSITIONS.finalize(h.repo, h.plan_path, "AK-321", h.ak)
            # A final commit with unrelated writes is not a state-only receipt commit.
            (h.repo / "unplanned").write_text("unplanned\n")
            commit(h.repo, "bad final commit", STATE, "unplanned")
            with self.assertRaisesRegex(ValueError, "state-only final commit"):
                TRANSITIONS.validate_v2_provenance(h.repo, json.loads((h.repo / STATE).read_bytes()), h.ak)
            self.assertIn("state-only final commit", check_history(h.repo, expect=2))


if __name__ == "__main__":
    unittest.main()
