"""AK6663: source-native Git lifecycles; synthetic AK only, never a live consumer."""
from __future__ import annotations

import copy
import contextlib
import io
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from contextlib import ExitStack
from pathlib import Path
from unittest import mock

from tests.test_l1_template_transitions import Harness, ROOT, SCRATCH, TRANSITIONS, git, run, sha, CHECKED_AT, COMPLETED_AT
from tests.test_l1_template_company_ownership import bind_runtime_pin, CompanyHarness, commit
from tests import test_l1_template_gitlink_retirements as GITLINK_FIXTURES
from tests.test_l1_template_gitlink_retirements import rendered_copy
from tests.test_l1_template_reverse_transitions import check_history
import l1_template_transitions as LIVE
import l1_template_receipts as RECEIPTS
import l1_template_company as COMPANY
import l1_template_ownership as OWNERSHIP
import l1_template_fold as FOLD
import l1_ontology_convergence as CONVERGENCE

MAP = CONVERGENCE.MAP
STATE = CONVERGENCE.STATE
ANSWERS = CONVERGENCE.ANSWERS
READERS = ("l1_ontology_ownership.py", "l1_ontology_convergence.py", "l1_transition_history.py", "check-l1-ownership-state.py")
FILES = {
    "README.md": (b"retained ontology\n", "100644"),
    "manifest.yaml": (b"rocs:\n  layers:\n    - name: repo\n      path: ontology/src\n", "100644"),
    "src/system4d.yaml": (b'ontology:\n  system4d:\n    name: retained-test-ontology\n    version: "0.1"\n    container:\n      constraints:\n        - Complete tracked source retention\n', "100644"),
    "nested/payload.bin": (b"\xff\x00\r\nbinary\n", "100644"),
    "nested/run.sh": (b"#!/bin/sh\nexit 0\n", "100755"),
}


def copier_render(parent: Path, name: str, layout: str) -> Path:
    rendered = parent / name
    run("sh", str(ROOT / "scripts/new-l1-from-copier.sh"), str(rendered), "--defaults", "--overwrite",
        "-d", "repo_slug=fixture-template-repo", "-d", "company_slug=holdingco", "-d", "company_name=Holding Company",
        "-d", "maintainer_handle=@template-owner", "-d", f"l1_ontology_layout={layout}", cwd=ROOT)
    return rendered


def readers(repo: Path) -> None:
    for name in READERS:
        shutil.copy2(ROOT / "copier-template/scripts/lib" / name, repo / "scripts/lib" / name)


class ConvergenceHarness(Harness):
    def __init__(self, parent: Path, legacy: bool = False, refresh: bool = False, private_agent: bool = False):
        super().__init__(parent, legacy)
        if private_agent:
            self.next_map.write_text(self.next_map.read_text().replace("agent_owned:\n", "agent_owned:\n  - private-agent/**\n"))
        for path, (raw, mode) in FILES.items():
            target = self.source / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            target.chmod(0o755 if mode == "100755" else 0o644)
        commit(self.source, "valid retained source with binary and executable", ".")
        self.gitlink_oid = git(self.source, "rev-parse", "HEAD")
        self.delta[1]["new_oid"] = self.gitlink_oid
        bind_runtime_pin(self.repo)
        answers = (self.repo / ANSWERS).read_text() + "l1_ontology_layout: gitlink\n"
        (self.repo / ANSWERS).write_text(answers)
        readers(self.repo)
        self.base = commit(self.repo, "fixture reader preinstallation and explicit layout", ANSWERS, "contracts/provenance-seal.yml", "scripts/lib")
        self.gitmodules = self.gitmodules.replace(str(self.source), FOLD.SOURCE.removesuffix(" main"))
        self.delta[0].update(new_oid=CONVERGENCE.object_oid("blob", self.gitmodules.encode()), content_sha256=sha(self.gitmodules.encode()))
        self.spec.update(adr_commit=self.base, git_delta=self.delta)
        self.spec_path.write_text(json.dumps(self.spec))
        plan = self.plan()
        Harness.stage_payload(self)
        (self.repo / ".gitmodules").write_text(self.gitmodules)
        run("git", "add", ".gitmodules", cwd=self.repo)
        Harness.pending_commit(self, plan)
        TRANSITIONS.finalize(self.repo, self.plan_path, "AK-321", self.ak)
        commit(self.repo, "old transition final", STATE)
        self.complete()
        self.old_task = copy.deepcopy(self.task)
        (parent / "old-task.json").write_text(json.dumps(self.old_task))
        self.task.update(id=322, status="claimed", claimed_by=self.executor, lease_expires_at="2099-01-01T00:00:00Z")
        self.task.pop("completed_at", None)
        self.decision["linked_tasks"].append(dict(task_id=322, link_role="post_adr_execution"))
        self.packet_details = dict(owner="Holding Owner", retained_source_packet=FOLD.PACKET)
        self.packet = dict(id=14868, task_id=5651, check_type="source_owner_packet", result="pass", details=self.packet_details)
        self.packet_json = parent / "packet.json"
        self.packet_json.write_text(json.dumps([self.packet]))
        self.ak.write_text("#!/bin/sh\ncase \"$1 $2\" in\n"
            f" 'task show') if [ \"$3\" = 321 ]; then cat '{parent / 'old-task.json'}'; else cat '{self.task_json}'; fi ;;\n"
            f" 'decision get') cat '{self.decision_json}' ;;\n"
            f" 'evidence task') if [ \"$3\" = 5651 ]; then cat '{self.packet_json}'; else cat '{self.evidence_json}'; fi ;;\n *) exit 2 ;;\nesac\n")
        self.write_authority()
        if refresh:
            incoming = rendered_copy(parent, "reader-preparation", True)
            bind_runtime_pin(incoming)
            readers(incoming)
            (incoming / MAP).write_bytes((self.repo / MAP).read_bytes())
            (incoming / ANSWERS).write_bytes((self.repo / ANSWERS).read_bytes())
            with self.authority():
                GITLINK_FIXTURES.V2OwnerGitlinkTests().receipt(self, incoming)
        self.predecessor = git(self.repo, "rev-parse", "HEAD")
        self.before_controls = ((self.repo / MAP).read_bytes(), (self.repo / STATE).read_bytes())
        mapping = COMPANY.map_sections(self.before_controls[0])
        mapping["agent"] = [p for p in mapping["agent"] if p not in {"ontology", ".gitmodules"}]
        mapping["company"] = ["ontology/**"]
        self.next_map.write_text(COMPANY.map_text(mapping))
        files = []
        for path, (raw, mode) in sorted(FILES.items()):
            files.append(dict(path="ontology/" + path, mode=mode,
                oid=CONVERGENCE.object_oid("blob", raw), content_sha256=sha(raw)))
        self.delta = FOLD.expected_delta(self.repo, self.predecessor, files)
        self.spec.update(transition_task_id=322, git_delta=self.delta, ontology_convergence={
            "source_repo": str(self.source), "source_tree_manifest_sha256": sha(CONVERGENCE.canonical(files)),
            "source_owner_evidence": dict(task_id=5651, evidence_ref="evidence:14868", details_sha256=sha(CONVERGENCE.canonical(self.packet_details))),
        })
        self.spec_path.write_text(json.dumps(self.spec))

    def authority(self):
        stack = ExitStack()
        real = RECEIPTS.verify_wave_evidence
        stack.enter_context(mock.patch.object(LIVE, "authoritative_ak", return_value=self.ak))
        stack.enter_context(mock.patch.object(RECEIPTS, "verify_wave_evidence", lambda repo, state, task_id=None, ak_command=None, **kw: real(repo, state, task_id, self.ak, **kw)))
        return stack

    def stage_payload(self):
        run("git", "submodule", "deinit", "--force", "ontology", cwd=self.repo)
        run("git", "rm", "--force", "ontology", ".gitmodules", cwd=self.repo)
        for path, (raw, mode) in FILES.items():
            target = self.repo / "ontology" / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            target.chmod(0o755 if mode == "100755" else 0o644)
        (self.repo / ANSWERS).write_bytes(CONVERGENCE.answers_successor((self.repo / ANSWERS).read_bytes()))
        run("git", "add", "ontology", ANSWERS, cwd=self.repo)

    def commit_pending(self, plan: dict) -> str:
        message = self.parent / "pending-message.txt"
        FOLD.commit_message(self.repo, self.plan_path, message)
        run("git", "add", MAP, STATE, cwd=self.repo)
        run("git", "commit", "--quiet", "-F", str(message), cwd=self.repo)
        return git(self.repo, "rev-parse", "HEAD")

    def pending(self, plan: dict, real_gates: bool = False):
        TRANSITIONS.apply(self.repo, self.plan_path, self.ak)
        applied = self.commit_pending(plan)
        check_history(self.repo)
        results = {"check-template-ci": 0, "ci-full": 0}
        if real_gates:
            for gate in reversed(TRANSITIONS.REQUIRED_VALIDATION):
                with mock.patch.dict(os.environ, {"ROCS_OUTPUT_ROOT": str(self.repo / ".tmp/rocs-output")}):
                    try:
                        result = CompanyHarness.run_gate(self, gate)
                    except AssertionError as exc:
                        trace = subprocess.run(["bash", "-x", *gate["command"].split()[1:]], cwd=self.repo, text=True, capture_output=True)
                        raise AssertionError(str(exc) + "\n" + trace.stderr[-12000:]) from exc
                results[gate["id"]] = result.returncode
        self.evidence.append(dict(id=990, task_id=322, repo=str(self.repo), repo_scope=str(self.repo), check_type="l1_ownership_transition_v1", result="pass", checked_at=CHECKED_AT,
            details=dict(plan=plan, applied_commit=applied, validation_results=results)))
        self.write_authority()
        return applied

    def finish(self):
        TRANSITIONS.finalize(self.repo, self.plan_path, "AK-322", self.ak)
        final = commit(self.repo, "convergence final", STATE)
        state = json.loads((self.repo / STATE).read_bytes())
        TRANSITIONS.validate_v2_provenance(self.repo, state, self.ak)
        check_history(self.repo)
        return final, state

    def restore_source(self):
        # Fixture-only rematerialization from preserved source, without network access.
        run("git", "config", "submodule.ontology.url", str(self.source), cwd=self.repo)
        run("git", "-c", "protocol.file.allow=always", "submodule", "update", "--init", "ontology", cwd=self.repo)


class ConvergenceTests(unittest.TestCase):
    def test_native_map_and_state_matrix_and_inverse_rematerialization(self):
        for legacy in (False, True):
            for refresh in (False, True):
                with self.subTest(map1=legacy, state3=refresh), tempfile.TemporaryDirectory(dir=SCRATCH) as raw:
                    h = ConvergenceHarness(Path(raw), legacy, refresh)
                    plan = h.plan()
                    self.assertEqual(plan["schema"], CONVERGENCE.PLAN_SCHEMA)
                    self.assertEqual(plan["ontology_convergence"]["source_tree_oid"], git(h.source, "rev-parse", "HEAD^{tree}"))
                    before = h.plan_path.read_bytes(); h.plan(); self.assertEqual(before, h.plan_path.read_bytes())
                    self.assertEqual(git(h.repo, "status", "--porcelain"), "")
                    h.stage_payload()
                    self.assertEqual(TRANSITIONS.index_delta(h.repo), plan["git_delta"])
                    applied = h.pending(plan)
                    final, state = h.finish()
                    self.assertEqual(state["schema"], TRANSITIONS.STATE_SCHEMA_V2)
                    h.complete()
                    TRANSITIONS.validate_v2_provenance(h.repo, state, h.ak)
                    run("git", "revert", "--no-edit", final, cwd=h.repo)
                    run("git", "revert", "--no-edit", applied, cwd=h.repo)
                    self.assertEqual(git(h.repo, "rev-parse", "HEAD^{tree}"), git(h.repo, "rev-parse", f"{h.predecessor}^{{tree}}"))
                    h.restore_source()
                    self.assertEqual(git(h.repo / "ontology", "rev-parse", "HEAD"), h.gitlink_oid)
                    self.assertEqual(git(h.repo, "status", "--porcelain"), "")

    def test_retention_packet_manifest_and_old_schema_smuggling_refuse(self):
        with tempfile.TemporaryDirectory(dir=SCRATCH) as raw:
            h = ConvergenceHarness(Path(raw)); plan = h.plan()
            original = copy.deepcopy(plan)
            for mutate in (
                lambda p: p["ontology_convergence"]["retained_files"].pop(),
                lambda p: p["ontology_convergence"].update(source_tree_manifest_sha256="0" * 64),
                lambda p: p["ontology_convergence"].update(source_commit_base64="YQ=="),
                lambda p: p["ontology_convergence"]["retained_files"][0].update(path="ontology/../bad"),
                lambda p: p["ontology_convergence"]["retained_files"][0].update(mode="120000"),
                lambda p: p["ontology_convergence"].update(extra=True),
                lambda p: p.update(schema=TRANSITIONS.PLAN_SCHEMA),
                lambda p: p.update(schema=COMPANY.PLAN_SCHEMA, reverse_of=None),
            ):
                forged = copy.deepcopy(original); mutate(forged); forged["canonical_plan_sha256"] = TRANSITIONS.plan_hash(forged)
                with self.assertRaises(ValueError): TRANSITIONS.validate_plan(forged)
            legacy = copy.deepcopy(original)
            legacy.update(schema=TRANSITIONS.PLAN_SCHEMA)
            legacy.pop("ontology_convergence")
            legacy["map_delta"] = {k: v for k, v in legacy["map_delta"].items() if not k.startswith("company_")}
            legacy["canonical_plan_sha256"] = TRANSITIONS.plan_hash(legacy)
            with self.assertRaisesRegex(ValueError, "legacy plan /1"):
                TRANSITIONS.validate_plan(legacy)
            # Rehashing an incomplete caller inventory still cannot count as full retention.
            forged = copy.deepcopy(original)
            obj = forged["ontology_convergence"]; removed = obj["retained_files"].pop()
            forged["git_delta"] = [e for e in forged["git_delta"] if e["path"] != removed["path"]]
            obj["source_tree_manifest_sha256"] = sha(CONVERGENCE.canonical(obj["retained_files"]))
            obj["source_tree_oid"] = CONVERGENCE.retained_tree(obj["retained_files"])
            forged["canonical_plan_sha256"] = TRANSITIONS.plan_hash(forged)
            with self.assertRaisesRegex(ValueError, "complete retained tree"): TRANSITIONS.validate_plan(forged)
            for packets in ([], [h.packet, h.packet], [dict(h.packet, result="fail")], [dict(h.packet, details=dict(h.packet_details, owner="other"))]):
                h.packet_json.write_text(json.dumps(packets))
                with self.assertRaisesRegex(ValueError, "source-owner"): h.plan()
            h.packet_json.write_text(json.dumps([h.packet]))
            h.spec["ontology_convergence"]["source_tree_manifest_sha256"] = "0" * 64
            h.spec_path.write_text(json.dumps(h.spec))
            with self.assertRaisesRegex(ValueError, "manifest digest"): h.plan()

    def test_historical_v3_and_done_task_proofs_cannot_be_erased(self):
        with tempfile.TemporaryDirectory(dir=SCRATCH) as raw:
            h = ConvergenceHarness(Path(raw), refresh=True)
            original = copy.deepcopy(h.evidence)
            before = ((h.repo / MAP).read_bytes(), (h.repo / STATE).read_bytes(), git(h.repo, "rev-parse", "HEAD"))
            for kind in ("l1_ownership_transition_v1", "l1_contract_refresh_v1"):
                h.evidence = [r for r in original if r["check_type"] != kind]; h.write_authority()
                with self.assertRaises(ValueError): h.plan()
            h.evidence = original; h.write_authority()
            old = h.parent / "old-task.json"
            old.write_text(json.dumps(dict(h.old_task, claimed_by="substituted-claimant")))
            with self.assertRaisesRegex(ValueError, "different claimant"): h.plan()
            old.write_text(json.dumps(dict(h.old_task, completed_at="2026-09-01T04:20:43.171183529+00:00")))
            with self.assertRaisesRegex(ValueError, "recorded after"): h.plan()
            old.write_text(json.dumps(h.old_task))
            self.assertEqual(before, ((h.repo / MAP).read_bytes(), (h.repo / STATE).read_bytes(), git(h.repo, "rev-parse", "HEAD")))
            plan = h.plan()
            for mutate in (
                lambda p: p.update(next_map_text=p["next_map_text"].replace("  - AGENTS.md\n", "")),
                lambda p: p["git_delta"].append(dict(path="unrelated", old_mode="000000", old_oid=None, new_mode="100644", new_oid="1" * 40, content_sha256="2" * 64)),
            ):
                forged = copy.deepcopy(plan); mutate(forged)
                forged["next_map_sha256"] = sha(forged["next_map_text"].encode())
                forged["canonical_plan_sha256"] = TRANSITIONS.plan_hash(forged)
                with self.assertRaises(ValueError): FOLD.verify(h.repo, forged, h.ak)

    def test_apply_and_finalize_refusals_keep_controls_and_receipt_lineage(self):
        with tempfile.TemporaryDirectory(dir=SCRATCH) as raw:
            h = ConvergenceHarness(Path(raw), refresh=True); plan = h.plan(); h.stage_payload()
            before = ((h.repo / MAP).read_bytes(), (h.repo / STATE).read_bytes())
            residual = h.repo / "ontology/.gitkeep"; residual.write_text("ignored or untracked")
            with self.assertRaises(ValueError): TRANSITIONS.apply(h.repo, h.plan_path, h.ak)
            residual.unlink()
            h.task["claimed_by"] = "lease-lost"; h.write_authority()
            with self.assertRaisesRegex(ValueError, "claimant"): TRANSITIONS.apply(h.repo, h.plan_path, h.ak)
            h.task["claimed_by"] = h.executor; h.write_authority()
            self.assertEqual(before, ((h.repo / MAP).read_bytes(), (h.repo / STATE).read_bytes()))
            applied = h.pending(plan)
            evidence = copy.deepcopy(h.evidence)
            for mutate in (
                lambda: h.evidence.pop(),
                lambda: h.evidence.append(copy.deepcopy(h.evidence[-1])),
                lambda: h.evidence[-1]["details"]["validation_results"].update(**{"ci-full": False}),
                lambda: h.evidence[-1]["details"]["validation_results"].update(**{"ci-full": 1}),
                lambda: h.evidence[-1]["details"].update(applied_commit=h.predecessor),
            ):
                mutate(); h.write_authority()
                with self.assertRaises(ValueError): TRANSITIONS.finalize(h.repo, h.plan_path, "AK-322", h.ak)
                h.evidence = copy.deepcopy(evidence); h.write_authority()
            with h.authority(), self.assertRaises(ValueError): OWNERSHIP.refresh(h.repo, rendered_copy(h.parent, "pending-incoming", False), False)
            with self.assertRaises(ValueError): h.plan()
            # Pending-only inverse restores exact predecessor; no evidence is invented.
            run("git", "revert", "--no-edit", applied, cwd=h.repo)
            self.assertEqual(git(h.repo, "rev-parse", "HEAD^{tree}"), git(h.repo, "rev-parse", f"{h.predecessor}^{{tree}}"))
            h.restore_source()

    def test_applied_and_final_commit_shape_refusals(self):
        for extra, non_direct in ((True, False), (False, True)):
            with self.subTest(extra=extra, non_direct=non_direct), tempfile.TemporaryDirectory(dir=SCRATCH) as raw:
                h = ConvergenceHarness(Path(raw)); plan = h.plan()
                if non_direct:
                    run("git", "commit", "--allow-empty", "--quiet", "-m", "unbound intermediate", cwd=h.repo)
                    # Reproduce an unauthorized pending commit without re-running apply at a new base.
                    h.stage_payload()
                    (h.repo / MAP).write_bytes(plan["next_map_text"].encode())
                    (h.repo / STATE).write_bytes(TRANSITIONS.pending_bytes(plan))
                    applied = h.commit_pending(plan)
                    h.evidence.append(dict(id=990, task_id=322, repo=str(h.repo), repo_scope=str(h.repo), check_type="l1_ownership_transition_v1", result="pass", checked_at=CHECKED_AT,
                        details=dict(plan=plan, applied_commit=applied, validation_results={"ci-full": 0, "check-template-ci": 0})))
                else:
                    h.stage_payload(); h.pending(plan)
                    (h.repo / "extra.txt").write_text("unauthorized applied payload")
                    run("git", "add", "extra.txt", cwd=h.repo)
                    run("git", "commit", "--amend", "--no-edit", "--quiet", cwd=h.repo)
                    h.evidence[-1]["details"]["applied_commit"] = git(h.repo, "rev-parse", "HEAD")
                h.write_authority()
                with self.assertRaises(ValueError): TRANSITIONS.finalize(h.repo, h.plan_path, "AK-322", h.ak)
                check_history(h.repo, expect=2)
        with tempfile.TemporaryDirectory(dir=SCRATCH) as raw:
            h = ConvergenceHarness(Path(raw)); plan = h.plan(); h.stage_payload(); h.pending(plan)
            TRANSITIONS.finalize(h.repo, h.plan_path, "AK-322", h.ak)
            (h.repo / "extra.txt").write_text("not a state-only final")
            commit(h.repo, "invalid final shape", STATE, "extra.txt")
            with self.assertRaisesRegex(ValueError, "state-only final"):
                TRANSITIONS.validate_v2_provenance(h.repo, json.loads((h.repo / STATE).read_bytes()), h.ak)
            check_history(h.repo, expect=2)

    def test_interruption_at_control_writes_and_uncommitted_finalize(self):
        for failure in (1, 2):
            with self.subTest(write=failure), tempfile.TemporaryDirectory(dir=SCRATCH) as raw:
                h = ConvergenceHarness(Path(raw)); h.plan(); h.stage_payload()
                real = TRANSITIONS.write_atomic; calls = 0
                def interrupted(content, destination):
                    nonlocal calls
                    calls += 1
                    if calls == failure: raise OSError("injected interruption")
                    real(content, destination)
                with mock.patch.object(TRANSITIONS, "write_atomic", side_effect=interrupted), self.assertRaises(OSError):
                    TRANSITIONS.apply(h.repo, h.plan_path, h.ak)
                self.assertEqual(git(h.repo, "rev-parse", "HEAD"), h.predecessor)
                self.assertTrue(h.plan_path.is_file())
                self.assertEqual((h.repo / STATE).read_bytes(), h.before_controls[1])
                if failure == 2:
                    self.assertEqual((h.repo / MAP).read_bytes(), h.next_map.read_bytes())
                    with self.assertRaisesRegex(ValueError, "map drifted"): TRANSITIONS.apply(h.repo, h.plan_path, h.ak)
                    # Explicit fixture-only bound control recovery, not unqualified hard reset.
                    (h.repo / MAP).write_bytes(h.before_controls[0])
                TRANSITIONS.apply(h.repo, h.plan_path, h.ak)
        with tempfile.TemporaryDirectory(dir=SCRATCH) as raw:
            h = ConvergenceHarness(Path(raw)); plan = h.plan(); h.stage_payload(); h.pending(plan)
            pending = (h.repo / STATE).read_bytes()
            with mock.patch.object(TRANSITIONS, "write_atomic", side_effect=OSError("finalize interrupted")), self.assertRaises(OSError):
                TRANSITIONS.finalize(h.repo, h.plan_path, "AK-322", h.ak)
            self.assertEqual((h.repo / STATE).read_bytes(), pending)
            TRANSITIONS.finalize(h.repo, h.plan_path, "AK-322", h.ak)
            with self.assertRaises(ValueError): TRANSITIONS.validate_v2_provenance(h.repo, json.loads((h.repo / STATE).read_bytes()), h.ak)
            with self.assertRaisesRegex(ValueError, "clean worktree"): TRANSITIONS.finalize(h.repo, h.plan_path, "AK-322", h.ak)
            commit(h.repo, "state-only final recovery", STATE)
            TRANSITIONS.validate_v2_provenance(h.repo, json.loads((h.repo / STATE).read_bytes()), h.ak)

    def test_source_worktree_and_answers_drift_refuse(self):
        with tempfile.TemporaryDirectory(dir=SCRATCH) as raw:
            h = ConvergenceHarness(Path(raw))
            dirty = h.source / "README.md"; old = dirty.read_bytes(); dirty.write_bytes(b"drift")
            with self.assertRaisesRegex(ValueError, "clean worktree"): h.plan()
            dirty.write_bytes(old)
            ignored = h.source / ".git/info/exclude"; ignored.write_text("ignored\n")
            (h.source / "ignored").write_text("not retained")
            with self.assertRaisesRegex(ValueError, "ignored content"): h.plan()
            (h.source / "ignored").unlink()
            (h.source / "untracked").write_text("not retained")
            with self.assertRaisesRegex(ValueError, "clean worktree"): h.plan()
            (h.source / "untracked").unlink()
            plan = h.plan(); h.stage_payload()
            answers = h.repo / ANSWERS; answers.write_bytes(answers.read_bytes() + b"pin: changed\n")
            run("git", "add", ANSWERS, cwd=h.repo)
            with self.assertRaisesRegex(ValueError, "exactly match"): TRANSITIONS.apply(h.repo, h.plan_path, h.ak)

    def test_real_copier_refresh_after_completion_and_fresh_overwrite_refusal(self):
        with tempfile.TemporaryDirectory(dir=SCRATCH) as raw:
            parent = Path(raw)
            fresh = copier_render(parent, "fresh", "tree")
            self.assertEqual(COMPANY.map_sections((fresh / MAP).read_bytes())["company"], ["ontology/**"])
            self.assertEqual(sorted(p.name for p in (fresh / "ontology").iterdir()), [".gitkeep"])
            self.assertEqual((fresh / "ontology/.gitkeep").read_bytes(), b"")
            for name in READERS:
                self.assertEqual((fresh / "scripts/lib" / name).read_bytes(), (ROOT / "copier-template/scripts/lib" / name).read_bytes())
            hp = parent / "history"; hp.mkdir()
            h = ConvergenceHarness(hp)
            incoming = parent / "gitlink-preparation"
            run("env", f"L1_RENDER_ONLY_OUT={incoming}", "sh", str(ROOT / "scripts/lib/run-l1-template-refresh.sh"), str(h.repo), cwd=ROOT)
            (incoming / MAP).write_bytes((h.repo / MAP).read_bytes())
            with h.authority():
                before_oid = git(h.repo, "ls-files", "-s", "ontology")
                before_modules = (h.repo / ".gitmodules").read_bytes()
                GITLINK_FIXTURES.V2OwnerGitlinkTests().receipt(h, incoming)
                self.assertEqual(before_oid, git(h.repo, "ls-files", "-s", "ontology"))
                self.assertEqual(before_modules, (h.repo / ".gitmodules").read_bytes())
                with self.assertRaisesRegex(ValueError, "receipted ownership transition"):
                    OWNERSHIP.refresh(h.repo, fresh, False)
            h.predecessor = git(h.repo, "rev-parse", "HEAD")
            h.delta = FOLD.expected_delta(h.repo, h.predecessor, [dict(path="ontology/" + path, mode=mode, oid=CONVERGENCE.object_oid("blob", data), content_sha256=sha(data)) for path, (data, mode) in sorted(FILES.items())])
            h.spec["git_delta"] = h.delta; h.spec_path.write_text(json.dumps(h.spec))
            plan = h.plan(); h.stage_payload(); h.pending(plan); _, state = h.finish(); h.complete()
            binding = TRANSITIONS.carry_forward_transition(h.repo, state, h.ak)
            retained = git(h.repo, "ls-files", "-s", "ontology")
            incoming_tree = parent / "post-convergence-tree"
            run("env", f"L1_RENDER_ONLY_OUT={incoming_tree}", "sh", str(ROOT / "scripts/lib/run-l1-template-refresh.sh"), str(h.repo), cwd=ROOT)
            # Existing renderer omits the default tree answer; do not change refresh semantics.
            self.assertNotIn("l1_ontology_layout: gitlink", (incoming_tree / ANSWERS).read_text())
            self.assertEqual(COMPANY.map_sections((incoming_tree / MAP).read_bytes())["company"], ["ontology/**"])
            self.assertTrue((incoming_tree / "ontology/.gitkeep").is_file())
            with h.authority():
                first = GITLINK_FIXTURES.V2OwnerGitlinkTests().receipt(h, incoming_tree)
                self.assertEqual(first["inherited_transition"], binding)
                RECEIPTS.validate_established_provenance(h.repo, first, ak_command=h.ak)
                check_history(h.repo)
                # A second real render and refresh preserve all company bytes/modes;
                # control receipt state changes, while template payload is unchanged.
                second_render = parent / "repeat-tree"
                run("env", f"L1_RENDER_ONLY_OUT={second_render}", "sh", str(ROOT / "scripts/lib/run-l1-template-refresh.sh"), str(h.repo), cwd=ROOT)
                before_head = git(h.repo, "rev-parse", "HEAD")
                before_state = (h.repo / STATE).read_bytes()
                previews = []
                for _ in range(2):
                    out = io.StringIO()
                    with contextlib.redirect_stdout(out):
                        OWNERSHIP.refresh(h.repo, second_render, False)
                    previews.append(out.getvalue())
                self.assertEqual(previews[0], previews[1])
                with contextlib.redirect_stdout(io.StringIO()):
                    OWNERSHIP.refresh(h.repo, second_render, True, "b" * 64, "repeat-wave", git(ROOT, "rev-parse", "HEAD"))
                self.assertEqual(before_state, (h.repo / STATE).read_bytes())
                self.assertEqual(before_head, git(h.repo, "rev-parse", "HEAD"))
                self.assertEqual(git(h.repo, "status", "--porcelain"), "")
                RECEIPTS.validate_established_provenance(h.repo, first, ak_command=h.ak)
                check_history(h.repo)
            self.assertEqual(retained, git(h.repo, "ls-files", "-s", "ontology"))
            self.assertFalse((h.repo / "ontology/.gitkeep").exists())
            self.assertFalse((h.repo / ".gitmodules").exists())
            (h.repo / "ontology/.gitkeep").write_bytes(b"company-customized seed\n")
            commit(h.repo, "later company-owned seed customization", "ontology/.gitkeep")
            with h.authority(), contextlib.redirect_stdout(io.StringIO()):
                OWNERSHIP.refresh(h.repo, second_render, True, "c" * 64, "customized-seed-wave", git(ROOT, "rev-parse", "HEAD"))
            self.assertEqual((h.repo / "ontology/.gitkeep").read_bytes(), b"company-customized seed\n")
            self.assertEqual(json.loads((h.repo / STATE).read_bytes())["inherited_transition"], binding)
            rejected = run("sh", str(ROOT / "scripts/new-l1-from-copier.sh"), str(h.repo), "--defaults", "--overwrite", cwd=ROOT, expect=2)
            self.assertIn("use owner refresh/transition", rejected.stderr)

    def test_actual_retained_ontology_gates(self):
        # Actual commands, valid ROCS ontology, no stubbed gate results or ROCS launcher.
        for legacy in (False, True):
            for refresh in (False, True):
                with self.subTest(map1=legacy, state3=refresh), tempfile.TemporaryDirectory(dir=SCRATCH) as raw:
                    h = ConvergenceHarness(Path(raw), legacy, refresh); plan = h.plan(); h.stage_payload()
                    h.pending(plan, real_gates=True)
                    h.finish()


if __name__ == "__main__":
    unittest.main()
