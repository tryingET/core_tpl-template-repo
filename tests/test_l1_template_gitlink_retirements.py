"""Owner-gitlink ontology refresh and declarative L0 retirements (local Git fixtures only)."""

from __future__ import annotations

import contextlib
import hashlib
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tests.test_l1_template_transitions import CHECKED_AT, FIXTURE, ROOT, SCRATCH, TRANSITIONS, Harness, git, init, run

sys.path.insert(0, str(ROOT / "scripts/lib"))
import l1_template_ownership as OWNERSHIP  # noqa: E402
import l1_template_receipts as RECEIPTS  # noqa: E402
import l1_template_retirements as RETIREMENTS  # noqa: E402
import l1_template_transitions as LIVE_TRANSITIONS  # noqa: E402

MAP = "contracts/template-ownership.yml"
STATE = "contracts/template-ownership-state.json"
L0_HEAD = git(ROOT, "rev-parse", "HEAD")
PLAN_SHA256 = "a" * 64
ROCS = "copier/tpl-project-repo/tools/rocs-cli"
LEGACY = {
    f"{ROCS}/rocs.py": b"print('vendored')\n",
    f"{ROCS}/runtime/deep/module.py": b"x = 1\n",
    "copier/tpl-monorepo/.githooks/pre-commit": b"#!/bin/sh\nexit 0\n",
}


def gitlink_layout(map_text: str) -> str:
    """Mirror of the copier.yml gitlink-layout task."""
    return map_text.replace("  - ontology/**\n", "").replace(
        "agent_owned:\n", "agent_owned:\n  - .gitmodules\n  - ontology\n"
    )


def rendered_copy(parent: Path, name: str, gitlink: bool) -> Path:
    rendered = parent / name
    shutil.copytree(FIXTURE, rendered)
    if gitlink:
        shutil.rmtree(rendered / "ontology")
        (rendered / MAP).write_text(gitlink_layout((rendered / MAP).read_text()), encoding="utf-8")
    full = rendered / "scripts/ci/full.sh"
    full.write_text(full.read_text() + "\n# refresh sentinel\n", encoding="utf-8")
    return rendered


def birth_target(parent: Path, gitlink_map: bool = False) -> Path:
    target = parent / "target"
    shutil.copytree(FIXTURE, target)
    if gitlink_map:
        raw = gitlink_layout((target / MAP).read_text()).encode()
        (target / MAP).write_bytes(raw)
        state = json.loads((target / STATE).read_text())
        state["ownership_map_sha256"] = hashlib.sha256(raw).hexdigest()
        (target / STATE).write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    init(target)
    return target


def add_files(repo: Path, files: dict[str, bytes], message: str = "legacy template files") -> None:
    for rel, data in files.items():
        path = repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        if data.startswith(b"#!"):
            path.chmod(0o755)
    run("git", "add", *files, cwd=repo)
    run("git", "commit", "--quiet", "-m", message, cwd=repo)


def fake_gitlink(repo: Path, path: str, modules: str | None = None) -> None:
    (repo / path).mkdir(parents=True, exist_ok=True)
    run("git", "update-index", "--add", "--cacheinfo", f"160000,{'1' * 40},{path}", cwd=repo)
    if modules is not None:
        (repo / ".gitmodules").write_text(modules, encoding="utf-8")
        run("git", "add", ".gitmodules", cwd=repo)
    run("git", "commit", "--quiet", "-m", f"gitlink {path}", cwd=repo)


def preview(target: Path, rendered: Path, **kwargs: object) -> str:
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        OWNERSHIP.refresh(target, rendered, False, **kwargs)
    return out.getvalue()


def apply(target: Path, rendered: Path, **kwargs: object) -> str:
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        OWNERSHIP.refresh(target, rendered, True, PLAN_SHA256, "wave-test", L0_HEAD, **kwargs)
    return out.getvalue()


def tree(repo: Path) -> dict[str, str]:
    return {
        path.relative_to(repo).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in repo.rglob("*")
        if path.is_file() and ".git" not in path.relative_to(repo).parts
    }


def manifest(parent: Path, *entries: dict[str, str], schema: str = RETIREMENTS.SCHEMA) -> list[dict[str, object]]:
    path = parent / "retirements.json"
    path.write_text(json.dumps({"schema": schema, "retirements": list(entries)}), encoding="utf-8")
    return RETIREMENTS.load_manifest(path)


def rule(pattern: str, commit: str = L0_HEAD) -> dict[str, str]:
    return {"pattern": pattern, "retired_by": commit, "reason": "test retirement"}


class V2OwnerGitlinkTests(unittest.TestCase):
    """The softwareco shape: established v2 transition to a company-owned ontology gitlink."""

    def established(self, parent: Path) -> Harness:
        h = Harness(parent)
        h.v2_state_raw = h.established() and (h.repo / STATE).read_bytes()
        h.final_commit = git(h.repo, "rev-parse", "HEAD")
        add_files(h.repo, LEGACY)
        return h

    def expected_binding(self, h: Harness) -> dict[str, object]:
        v2 = json.loads(h.v2_state_raw)
        return {
            **{key: v2[key] for key in ("transition_task_id", "decision_id", "evidence_id", "plan_sha256", "executor", "applied_commit")},
            "final_commit": h.final_commit, "state_sha256": hashlib.sha256(h.v2_state_raw).hexdigest(),
        }

    def receipt(self, h: Harness, rendered: Path) -> dict[str, object]:
        """Apply a refresh, commit it, record wave evidence, finalize: a v3 established state."""
        artifact = h.parent / f"refresh-plan-{len(h.evidence)}.json"
        artifact.write_text(f"refresh plan {len(h.evidence)}\n", encoding="utf-8")
        plan_sha = hashlib.sha256(artifact.read_bytes()).hexdigest()
        with contextlib.redirect_stdout(io.StringIO()):
            OWNERSHIP.refresh(h.repo, rendered, True, plan_sha, "wave-test", L0_HEAD)
        run("git", "add", "-A", cwd=h.repo)
        run("git", "commit", "--quiet", "-m", "applied refresh receipt", cwd=h.repo)
        applied = git(h.repo, "rev-parse", "HEAD")
        h.evidence.append({
            "id": 950 + len(h.evidence), "task_id": 321, "check_type": "l1_contract_refresh_v1", "result": "pass",
            "repo": str(h.repo.resolve()), "repo_scope": str(h.repo.resolve()), "checked_at": CHECKED_AT,
            "details": {
                "target_repo": str(h.repo.resolve()), "applied_commit": applied, "plan_sha256": plan_sha,
                "ownership_map_sha256": hashlib.sha256((h.repo / MAP).read_bytes()).hexdigest(),
                "source_l0_commit": L0_HEAD, "wave_id": "wave-test", "executor": "template-propagator",
                "validation": {"scripts/check-template-ci.sh": 0, "scripts/ci/full.sh": 0},
            },
        })
        h.write_authority()
        with contextlib.redirect_stdout(io.StringIO()):
            RECEIPTS.finalize(h.repo, "AK-321", artifact, h.ak)
        run("git", "add", "-A", cwd=h.repo)
        run("git", "commit", "--quiet", "-m", "refresh evidence closeout", cwd=h.repo)
        return json.loads((h.repo / STATE).read_text())

    def test_gitlink_layout_previews_and_applies_without_touching_the_gitlink(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH) as raw:
            parent = Path(raw)
            h = self.established(parent)
            rendered = rendered_copy(parent, "rendered", gitlink=True)
            self.assertEqual((rendered / MAP).read_bytes(), (h.repo / MAP).read_bytes())
            link_before = git(h.repo, "ls-files", "-s", "ontology")
            modules_before = (h.repo / ".gitmodules").read_bytes()
            submodule_before = tree(h.repo / "ontology")
            before = tree(h.repo)
            with mock.patch.object(LIVE_TRANSITIONS, "authoritative_ak", return_value=h.ak):
                first = preview(h.repo, rendered)
                self.assertEqual(first, preview(h.repo, rendered))  # deterministic
                self.assertIn("preserve-gitlink: ontology", first)
                self.assertNotIn(": ontology/", first)
                for rel in LEGACY:
                    self.assertIn(f"retire: {rel} (L0 ", first)
                self.assertIn(f"retire-rule: copier/*/tools/rocs-cli/** -> 2 path(s)", first)
                self.assertEqual(before, tree(h.repo))
                apply(h.repo, rendered)
            after = tree(h.repo)
            self.assertEqual(set(before) - set(after), set(LEGACY))
            self.assertFalse((h.repo / ROCS).exists())
            self.assertEqual(git(h.repo, "ls-files", "-s", "ontology"), link_before)
            self.assertEqual((h.repo / ".gitmodules").read_bytes(), modules_before)
            self.assertEqual(tree(h.repo / "ontology"), submodule_before)
            self.assertIn("refresh sentinel", (h.repo / "scripts/ci/full.sh").read_text())
            state = json.loads((h.repo / STATE).read_text())
            self.assertEqual((state["schema"], state["state"]), ("ai-society.template-ownership-state/3", "applied_pending_receipt"))
            self.assertEqual(state["ownership_map_sha256"], hashlib.sha256((h.repo / MAP).read_bytes()).hexdigest())
            self.assertEqual(state["inherited_transition"], self.expected_binding(h))
            carried = json.dumps(self.expected_binding(h), sort_keys=True, separators=(",", ":"))
            self.assertIn(f"carry-forward: inherited_transition into ai-society.template-ownership-state/3 {carried}", first)

    def test_tree_layout_render_and_dropped_claims_refuse(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH) as raw:
            parent = Path(raw)
            h = self.established(parent)
            before = tree(h.repo)
            tree_render = rendered_copy(parent, "tree", gitlink=False)
            dropped = rendered_copy(parent, "dropped", gitlink=True)
            (dropped / MAP).write_text((dropped / MAP).read_text().replace("  - .gitmodules\n", ""), encoding="utf-8")
            with mock.patch.object(LIVE_TRANSITIONS, "authoritative_ak", return_value=h.ak):
                with self.assertRaisesRegex(ValueError, "receipted ownership transition"):
                    preview(h.repo, tree_render)
                with self.assertRaisesRegex(ValueError, "dropping company-owned patterns: .gitmodules"):
                    apply(h.repo, dropped)
            self.assertEqual(before, tree(h.repo))

    def test_completed_transition_task_is_proven_by_its_pinned_evidence(self) -> None:
        # AK clears claimed_by when a task completes; the pinned evidence then binds it.
        with tempfile.TemporaryDirectory(dir=SCRATCH) as raw:
            parent = Path(raw)
            h = self.established(parent)
            rendered = rendered_copy(parent, "rendered", gitlink=True)
            h.complete()
            with mock.patch.object(LIVE_TRANSITIONS, "authoritative_ak", return_value=h.ak):
                self.assertIn("carry-forward: inherited_transition", preview(h.repo, rendered))
                h.complete(completed_at="2026-09-01T04:00:00Z")
                with self.assertRaisesRegex(ValueError, "recorded after the transition task completed"):
                    preview(h.repo, rendered)

    def test_carried_transition_survives_repeated_refreshes_and_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH) as raw:
            parent = Path(raw)
            h = self.established(parent)
            rendered = rendered_copy(parent, "rendered", gitlink=True)
            expected = self.expected_binding(h)
            real_wave = RECEIPTS.verify_wave_evidence

            def wave(repo: Path, state: dict[str, object], task_id: int | None = None, ak_command: Path | None = None) -> dict[str, object]:
                return real_wave(repo, state, task_id, h.ak)
            with mock.patch.object(LIVE_TRANSITIONS, "authoritative_ak", return_value=h.ak), \
                    mock.patch.object(RECEIPTS, "verify_wave_evidence", wave):
                first = self.receipt(h, rendered)
                self.assertEqual((first["schema"], first["state"], first["origin"]), ("ai-society.template-ownership-state/3", "established", "contract-refresh"))
                self.assertEqual(first["inherited_transition"], expected)
                RECEIPTS.validate_established_provenance(h.repo, first)
                run("python3", "-I", "-S", "-B", "scripts/lib/check-l1-ownership-state.py", cwd=h.repo)
                full = h.repo / "scripts/ci/full.sh"
                (rendered / "scripts/ci/full.sh").write_text(full.read_text() + "# second refresh\n", encoding="utf-8")
                h.complete()  # the transition task completes between refreshes
                second = self.receipt(h, rendered)
                self.assertEqual(second["inherited_transition"], expected)  # carried verbatim
                RECEIPTS.validate_established_provenance(h.repo, second)
                run("python3", "-I", "-S", "-B", "scripts/lib/check-l1-ownership-state.py", cwd=h.repo)

                (rendered / "scripts/ci/full.sh").write_text(full.read_text() + "# third refresh\n", encoding="utf-8")
                old_checker = h.parent / "old-check.py"
                old_checker.write_text(git(ROOT, "show", "d7b073c:copier-template/scripts/lib/check-l1-ownership-state.py") + "\n")
                shutil.copy(old_checker, h.repo / "scripts/lib/old-check.py")
                refused = run("python3", "-I", "-S", "-B", "scripts/lib/old-check.py", cwd=h.repo, expect=2)
                self.assertIn("schema/kind mismatch", refused.stderr)  # pre-v3 readers refuse, never misread
                (h.repo / "scripts/lib/old-check.py").unlink()

                saved = (h.repo / STATE).read_bytes()
                for key, value in (("executor", "other-executor"), ("plan_sha256", "c" * 64), ("final_commit", h.base), ("state_sha256", "d" * 64)):
                    forged = dict(second, inherited_transition=dict(expected, **{key: value}))
                    (h.repo / STATE).write_text(json.dumps(forged, indent=2, sort_keys=True) + "\n", encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, "inherited transition|pending inherited"):
                        RECEIPTS.validate_established_provenance(h.repo, forged)
                    run("python3", "-I", "-S", "-B", "scripts/lib/check-l1-ownership-state.py", cwd=h.repo, expect=2)
                for forged in (dict(second, schema="ai-society.template-ownership-state/1"), {k: v for k, v in second.items() if k != "inherited_transition"} | {"schema": "ai-society.template-ownership-state/3"}):
                    (h.repo / STATE).write_text(json.dumps(forged, indent=2, sort_keys=True) + "\n", encoding="utf-8")
                    with self.assertRaisesRegex(ValueError, "inherited.transition"):
                        RECEIPTS.validate_established_provenance(h.repo, forged)
                    run("python3", "-I", "-S", "-B", "scripts/lib/check-l1-ownership-state.py", cwd=h.repo, expect=2)
                (h.repo / STATE).write_bytes(saved)
                h.evidence[0]["details"]["plan"]["executor"] = "other-executor"; h.write_authority()
                with self.assertRaisesRegex(ValueError, "canonical transition plan hash mismatch"):
                    preview(h.repo, rendered)


class BirthGitlinkTests(unittest.TestCase):
    def test_gitlink_claims_require_receipted_map_topology_and_declaration(self) -> None:
        modules = '[submodule "ontology"]\n\tpath = ontology\n\turl = https://example.invalid/o.git\n'
        with tempfile.TemporaryDirectory(dir=SCRATCH) as raw:
            parent = Path(raw)
            gitlink_render = rendered_copy(parent, "gitlink", gitlink=True)
            cases = (
                (False, modules, "requires a receipted ownership transition"),
                (True, None, "requires a committed gitlink at ontology"),
                (True, modules.replace("path = ontology", "path = other"), "declare exactly one submodule"),
            )
            for index, (gitlink_map, declared, message) in enumerate(cases):
                case = parent / f"case-{index}"
                case.mkdir()
                target = birth_target(case, gitlink_map)
                run("git", "rm", "--quiet", "-r", "ontology", cwd=target)
                run("git", "commit", "--quiet", "-m", "drop in-tree ontology", cwd=target)
                if declared is not None:
                    fake_gitlink(target, "ontology", declared)
                with self.assertRaisesRegex(ValueError, message):
                    preview(target, gitlink_render)

    def test_gitlink_inside_template_subtree_is_opaque_and_refused(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH) as raw:
            parent = Path(raw)
            target = birth_target(parent)
            fake_gitlink(target, "examples/vendor")
            with self.assertRaisesRegex(ValueError, "target gitlink examples/vendor is template-owned"):
                preview(target, rendered_copy(parent, "rendered", gitlink=False))


class RetirementTests(unittest.TestCase):
    def test_real_manifest_is_valid_and_not_rendered(self) -> None:
        entries = RETIREMENTS.load_manifest()
        self.assertTrue(any(item["pattern"] == "copier/*/tools/rocs-cli/**" for item in entries))
        rendered = OWNERSHIP.files(FIXTURE)
        self.assertFalse([p for p in rendered for item in entries if item["regex"].match(p)])

    def test_manifest_validation_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH) as raw:
            parent = Path(raw)
            for entries, message in (
                ((rule("copier/../x"),), "unsupported retirement pattern"),
                ((rule("contracts/**"),), "control path"),
                ((rule("copier/a?/x"),), "unsupported retirement pattern"),
                ((rule("copier/x", "f" * 40),), "not an L0 ancestor"),
                ((rule("copier/x", "abc"),), "full lowercase"),
                ((rule("copier/x"), rule("copier/x")), "duplicate"),
                (({"pattern": "copier/x", "retired_by": L0_HEAD},), "exactly pattern"),
            ):
                with self.assertRaisesRegex(ValueError, message):
                    manifest(parent, *entries)
            with self.assertRaisesRegex(ValueError, "schema"):
                manifest(parent, rule("copier/x"), schema="other/1")

    def test_apply_deletes_exactly_the_planned_paths(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH) as raw:
            parent = Path(raw)
            target = birth_target(parent)
            keep = {"copier/tpl-project-repo/tools/keep.txt": b"company kept\n", "docs/project/legacy.md": b"x\n"}
            add_files(target, {**LEGACY, **keep})
            rendered = rendered_copy(parent, "rendered", gitlink=False)
            before = tree(target)
            plan = preview(target, rendered)
            self.assertEqual(plan, preview(target, rendered))
            self.assertIn("retire-rule: copier/*/.githooks/pre-commit -> 1 path(s) (L0 6dcbc01f0590", plan)
            apply(target, rendered)
            after = tree(target)
            self.assertEqual(set(before) - set(after), set(LEGACY))
            self.assertTrue(all(after[path] == before[path] for path in keep))
            self.assertFalse((target / ROCS).exists())
            self.assertTrue((target / "copier/tpl-project-repo/tools").is_dir())

    def test_dirty_untracked_staged_and_unowned_matches_refuse(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH) as raw:
            parent = Path(raw)
            rendered = rendered_copy(parent, "rendered", gitlink=False)
            scenarios = {
                "dirty": lambda t: (t / f"{ROCS}/rocs.py").write_text("edited\n"),
                "untracked": lambda t: (t / f"{ROCS}/new.py").write_text("new\n"),
                "staged": lambda t: ((t / f"{ROCS}/rocs.py").write_text("staged\n"), run("git", "add", "-A", cwd=t)),
            }
            for name, mutate in scenarios.items():
                case = parent / name
                case.mkdir()
                target = birth_target(case)
                add_files(target, LEGACY)
                mutate(target)
                before = tree(target)
                with self.assertRaisesRegex(ValueError, "untracked or dirty"):
                    apply(target, rendered)
                self.assertEqual(before, tree(target))
            target = birth_target(parent / "unowned-root")
            add_files(target, {"docs/org/old.md": b"company\n"})
            with self.assertRaisesRegex(ValueError, "active and incoming template ownership"):
                preview(target, rendered, retirement_manifest=manifest(parent, rule("docs/org/old.md")))
            with self.assertRaisesRegex(ValueError, "L0 still renders retired path scripts/ci/full.sh"):
                preview(target, rendered, retirement_manifest=manifest(parent, rule("scripts/ci/full.sh")))

    def test_symlink_and_gitlink_matches_refuse_and_ancestor_swap_is_caught(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH) as raw:
            parent = Path(raw)
            rendered = rendered_copy(parent, "rendered", gitlink=False)
            target = birth_target(parent)
            link = target / "copier/tpl-project-repo/tools/rocs-cli/link.py"
            link.parent.mkdir(parents=True)
            link.symlink_to("../../README.md.j2")
            run("git", "add", str(link.relative_to(target)), cwd=target)
            run("git", "commit", "--quiet", "-m", "symlink", cwd=target)
            with self.assertRaisesRegex(ValueError, r"non-regular tracked entry \(120000\)"):
                preview(target, rendered)
            second = birth_target(parent / "gitlink")
            fake_gitlink(second, f"{ROCS}/vendored")
            with self.assertRaisesRegex(ValueError, f"target gitlink {ROCS}/vendored is template-owned"):
                preview(second, rendered)
            second_map = OWNERSHIP.load_map(second)
            with self.assertRaisesRegex(ValueError, r"non-regular tracked entry \(160000\)"):
                RETIREMENTS.plan(
                    second, OWNERSHIP.gitlinks.index_entries(second), set(), second_map, second_map, OWNERSHIP.owner
                )

            third = birth_target(parent / "swap")
            add_files(third, LEGACY)
            index = OWNERSHIP.gitlinks.index_entries(third)
            maps = OWNERSHIP.load_map(third)
            planned = RETIREMENTS.plan(third, index, OWNERSHIP.files(rendered), maps, maps, OWNERSHIP.owner)
            outside = parent / "outside"
            shutil.copytree(third / "copier/tpl-project-repo/tools", outside)
            shutil.rmtree(third / "copier/tpl-project-repo/tools")
            (third / "copier/tpl-project-repo/tools").symlink_to(outside, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "symlinked destination ancestor"):
                RETIREMENTS.retire(third, planned)
            self.assertTrue((outside / "rocs-cli/rocs.py").is_file())
            self.assertTrue((third / "copier/tpl-monorepo/.githooks/pre-commit").is_file())


if __name__ == "__main__":
    unittest.main()
