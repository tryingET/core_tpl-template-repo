"""Independent inspection blockers: strict receipts, hidden WIP, durable proofs, claim retention."""
from __future__ import annotations

import base64
import copy
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tests.test_l1_template_transitions import ROOT, SCRATCH, TRANSITIONS, CHECKED_AT, git, run
from tests.test_l1_template_transitions_convergence import ConvergenceHarness, MAP, STATE, LIVE, FOLD, COMPANY, OWNERSHIP, CONVERGENCE, RECEIPTS, GITLINK_FIXTURES
from tests.test_l1_template_reverse_transitions import check_history
from tests.test_l1_template_company_ownership import CompanyHarness, commit


class InspectionBlockerTests(unittest.TestCase):
    def test_live_lease_boundary_uses_matching_nanosecond_representation(self):
        with tempfile.TemporaryDirectory(dir=SCRATCH) as raw:
            h = ConvergenceHarness(Path(raw)); plan = h.plan()
            expiry = LIVE.ak_instant("2099-01-01T00:00:00.900000000Z", "fixture")
            h.task["lease_expires_at"] = "2099-01-01T00:00:00.900000000Z"; h.write_authority()
            with mock.patch.object(FOLD, "current_instant", return_value=(expiry[0], 100000000)):
                FOLD.verify_live_lease(plan, h.ak)
            for fraction in (900000000, 900000001):
                with self.subTest(nanoseconds=fraction), mock.patch.object(FOLD, "current_instant", return_value=(expiry[0], fraction)), self.assertRaisesRegex(ValueError, "unexpired"):
                    FOLD.verify_live_lease(plan, h.ak)

    def test_expired_or_missing_live_lease_refuses_plan_apply_and_finalize(self):
        with tempfile.TemporaryDirectory(dir=SCRATCH) as raw:
            h = ConvergenceHarness(Path(raw))
            valid = h.task["lease_expires_at"]
            for expiry in ("2000-01-01T00:00:00Z", None, "invalid"):
                h.task["lease_expires_at"] = expiry; h.write_authority()
                with self.subTest(expiry=expiry), self.assertRaises(ValueError): h.plan()
            h.task["lease_expires_at"] = valid; h.write_authority()
            plan = h.plan(); h.stage_payload()
            before = ((h.repo / MAP).read_bytes(), (h.repo / STATE).read_bytes())
            h.task["lease_expires_at"] = "2000-01-01T00:00:00Z"; h.write_authority()
            with self.assertRaisesRegex(ValueError, "unexpired"):
                TRANSITIONS.apply(h.repo, h.plan_path, h.ak)
            self.assertEqual(before, ((h.repo / MAP).read_bytes(), (h.repo / STATE).read_bytes()))
            h.task["lease_expires_at"] = valid; h.write_authority(); h.pending(plan)
            pending = (h.repo / STATE).read_bytes()
            h.task["lease_expires_at"] = "2000-01-01T00:00:00Z"; h.write_authority()
            with self.assertRaisesRegex(ValueError, "unexpired"):
                TRANSITIONS.finalize(h.repo, h.plan_path, "AK-322", h.ak)
            self.assertEqual(pending, (h.repo / STATE).read_bytes())
            h.task["lease_expires_at"] = valid; h.write_authority(); h.finish(); h.complete()
            # Historical proof does not require a renewed lease after completion.
            LIVE.validate_v2_provenance(h.repo, json.loads((h.repo / STATE).read_bytes()), h.ak)

    def test_predecessor_wave_requires_unique_pin_integer_zero_and_timely_evidence(self):
        with tempfile.TemporaryDirectory(dir=SCRATCH) as raw:
            h = ConvergenceHarness(Path(raw), refresh=True)
            original = copy.deepcopy(h.evidence)
            wave = next(r for r in h.evidence if r["check_type"] == "l1_contract_refresh_v1")
            before = ((h.repo / MAP).read_bytes(), (h.repo / STATE).read_bytes(), git(h.repo, "rev-parse", "HEAD"))
            for case in ("boolean", "duplicate", "late", "missing-time", "unpinned", "duplicate-pin"):
                h.evidence = copy.deepcopy(original)
                record = next(r for r in h.evidence if r["id"] == wave["id"])
                if case == "boolean": record["details"]["validation"]["scripts/ci/full.sh"] = False
                elif case == "duplicate": h.evidence.append(dict(copy.deepcopy(record), id=record["id"] + 1))
                elif case == "late": record["checked_at"] = "2099-01-01T00:00:00Z"
                elif case == "missing-time": record.pop("checked_at")
                elif case == "unpinned": record["id"] += 1
                else: h.evidence.append(dict(id=record["id"], check_type="unrelated"))
                h.write_authority()
                with self.subTest(case=case), self.assertRaises(ValueError): h.plan()
                self.assertEqual(before, ((h.repo / MAP).read_bytes(), (h.repo / STATE).read_bytes(), git(h.repo, "rev-parse", "HEAD")))
            h.evidence = original; h.write_authority(); h.plan()
            # Also require strict historical proof during finalize, after planning succeeded.
            plan = h.plan(); h.stage_payload(); h.pending(plan)
            wave = next(r for r in h.evidence if r["check_type"] == "l1_contract_refresh_v1")
            wave["details"]["validation"]["scripts/ci/full.sh"] = False; h.write_authority()
            with self.assertRaisesRegex(ValueError, "integer-zero"):
                TRANSITIONS.finalize(h.repo, h.plan_path, "AK-322", h.ak)

    def test_source_hidden_index_wip_and_filemode_false_refuse(self):
        with tempfile.TemporaryDirectory(dir=SCRATCH) as raw:
            h = ConvergenceHarness(Path(raw)); plan = h.plan()
            path = h.source / "README.md"; original = path.read_bytes()
            for flag in ("assume-unchanged", "skip-worktree"):
                run("git", "update-index", f"--{flag}", "README.md", cwd=h.source)
                path.write_bytes(b"hidden tracked WIP\n")
                self.assertEqual(git(h.source, "status", "--porcelain"), "")
                with self.subTest(flag=flag), self.assertRaisesRegex(ValueError, "index flags"): h.plan()
                path.write_bytes(original)
                run("git", "update-index", f"--no-{flag}", "README.md", cwd=h.source)
            run("git", "config", "core.filemode", "false", cwd=h.source)
            executable = h.source / "nested/run.sh"; executable.chmod(0o644)
            self.assertEqual(git(h.source, "status", "--porcelain"), "")
            with self.assertRaisesRegex(ValueError, "executable mode"): h.plan()
            executable.chmod(0o755)
            path.chmod(0o654)
            self.assertEqual(git(h.source, "status", "--porcelain"), "")
            with self.assertRaisesRegex(ValueError, "executable mode"): h.plan()
            path.chmod(0o644)
            inventory = plan["ontology_convergence"]["retained_files"]
            path.write_bytes(b"hidden byte drift")
            with self.assertRaisesRegex(ValueError, "content"):
                FOLD.verify_source_worktree(h.source, inventory)
            path.write_bytes(original)
            path.unlink(); path.symlink_to(h.source / "manifest.yaml")
            with self.assertRaises(ValueError): FOLD.verify_source_worktree(h.source, inventory)
            path.unlink(); path.write_bytes(original); h.plan()

    def test_cli_message_and_fresh_clone_prove_complete_source_without_submodule_objects(self):
        with tempfile.TemporaryDirectory(dir=SCRATCH) as raw:
            h = ConvergenceHarness(Path(raw)); plan = h.plan()
            message = h.parent / "cli-message.txt"
            run("python3", "-B", str(ROOT / "scripts/lib/l1_template_transitions.py"), "--repo-root", str(h.repo), "commit-message", "--plan", str(h.plan_path), "--output", str(message), cwd=ROOT)
            self.assertEqual(message.read_bytes(), CONVERGENCE.plan_message(plan))
            run("python3", "-B", str(ROOT / "scripts/lib/l1_template_transitions.py"), "--repo-root", str(h.repo), "commit-message", "--plan", str(h.plan_path), "--output", str(h.repo / "forbidden-message"), cwd=ROOT, expect=2)
            self.assertFalse((h.repo / "forbidden-message").exists())
            h.stage_payload(); h.pending(plan)
            clone = h.parent / "fresh-clone"
            run("git", "clone", "--quiet", "--no-hardlinks", str(h.repo), str(clone), cwd=h.parent)
            self.assertFalse((clone / ".git/modules/ontology").exists())
            run("git", "cat-file", "-e", h.gitlink_oid, cwd=clone, expect=1)
            check_history(clone)
            h.finish()
            final_clone = h.parent / "final-clone"
            run("git", "clone", "--quiet", "--no-hardlinks", str(h.repo), str(final_clone), cwd=h.parent)
            check_history(final_clone)

    def test_generated_checker_and_l0_refuse_missing_duplicate_forged_and_omitted_payload_proofs(self):
        for case in ("missing", "duplicate", "noncanonical", "substituted", "omitted", "forged-retention", "hash-drift"):
            with self.subTest(case=case), tempfile.TemporaryDirectory(dir=SCRATCH) as raw:
                h = ConvergenceHarness(Path(raw)); plan = h.plan(); h.stage_payload(); h.pending(plan)
                message = CONVERGENCE.plan_message(plan)
                if case == "missing": message = b"no retained proof\n"
                elif case == "duplicate": message += b"\n" + message
                elif case == "noncanonical":
                    message = ("Pending\n\n" + CONVERGENCE.TRAILER + base64.b64encode(json.dumps(plan).encode()).decode() + "\n").encode()
                elif case == "substituted":
                    changed = copy.deepcopy(plan); changed["rollback"] = "different immutable plan"
                    changed["canonical_plan_sha256"] = TRANSITIONS.plan_hash(changed)
                    message = CONVERGENCE.plan_message(changed)
                elif case in {"omitted", "forged-retention"}:
                    run("git", "rm", "ontology/nested/payload.bin", cwd=h.repo)
                    if case == "forged-retention":
                        changed = copy.deepcopy(plan); obj = changed["ontology_convergence"]
                        obj["retained_files"] = [e for e in obj["retained_files"] if e["path"] != "ontology/nested/payload.bin"]
                        changed["git_delta"] = [e for e in changed["git_delta"] if e["path"] != "ontology/nested/payload.bin"]
                        obj["source_tree_oid"] = CONVERGENCE.retained_tree(obj["retained_files"])
                        obj["source_tree_manifest_sha256"] = CONVERGENCE.sha(CONVERGENCE.canonical(obj["retained_files"]))
                        changed["canonical_plan_sha256"] = TRANSITIONS.plan_hash(changed)
                        message = CONVERGENCE.plan_message(changed)
                else:
                    (h.repo / "ontology/nested/payload.bin").write_bytes(b"substituted payload")
                    run("git", "add", "ontology/nested/payload.bin", cwd=h.repo)
                path = h.parent / "bad-message.txt"; path.write_bytes(message)
                run("git", "commit", "--amend", "--quiet", "-F", str(path), cwd=h.repo)
                h.evidence[-1]["details"]["applied_commit"] = git(h.repo, "rev-parse", "HEAD"); h.write_authority()
                check_history(h.repo, expect=2)
                with self.assertRaises(ValueError): TRANSITIONS.finalize(h.repo, h.plan_path, "AK-322", h.ak)
                clone = h.parent / "bad-fresh-clone"
                run("git", "clone", "--quiet", "--no-hardlinks", str(h.repo), str(clone), cwd=h.parent)
                check_history(clone, expect=2)

    def test_merged_pending_commit_with_valid_trailer_refuses(self):
        with tempfile.TemporaryDirectory(dir=SCRATCH) as raw:
            h = ConvergenceHarness(Path(raw)); plan = h.plan(); h.stage_payload()
            TRANSITIONS.apply(h.repo, h.plan_path, h.ak)
            run("git", "add", MAP, STATE, cwd=h.repo)
            tree = git(h.repo, "write-tree")
            other = run("git", "commit-tree", f"{h.predecessor}^{{tree}}", "-p", h.predecessor, cwd=h.repo, input="other parent\n").stdout.strip()
            merged = run("git", "commit-tree", tree, "-p", h.predecessor, "-p", other, cwd=h.repo, input=CONVERGENCE.plan_message(plan).decode()).stdout.strip()
            run("git", "update-ref", "HEAD", merged, h.predecessor, cwd=h.repo)
            self.assertEqual(git(h.repo, "status", "--porcelain"), "")
            self.assertEqual(CONVERGENCE.trailer_plan(lambda *args: RECEIPTS.git_output(h.repo, *args), merged), plan)
            h.evidence.append(dict(id=990, task_id=322, repo=str(h.repo), repo_scope=str(h.repo), check_type="l1_ownership_transition_v1", result="pass", checked_at=CHECKED_AT,
                details=dict(plan=plan, applied_commit=merged, validation_results={"check-template-ci": 0, "ci-full": 0})))
            h.write_authority()
            with self.assertRaisesRegex(ValueError, "direct child"):
                TRANSITIONS.finalize(h.repo, h.plan_path, "AK-322", h.ak)
            check_history(h.repo, expect=2)

    def test_copier_company_preparation_preserves_private_agent_claim_and_lineage(self):
        with tempfile.TemporaryDirectory(dir=SCRATCH) as raw:
            h = ConvergenceHarness(Path(raw), private_agent=True)
            plan = h.plan(); h.stage_payload(); h.pending(plan); _, state = h.finish(); h.complete()
            binding = TRANSITIONS.carry_forward_transition(h.repo, state, h.ak)
            private = h.repo / "private-agent/secret.txt"; private.parent.mkdir(); private.write_bytes(b"fixture agent-owned bytes\n")
            commit(h.repo, "ordinary agent-owned work", "private-agent/secret.txt")
            retained = git(h.repo, "ls-files", "-s", "ontology")
            incoming = h.parent / "fresh-tree"
            run("env", f"L1_RENDER_ONLY_OUT={incoming}", "sh", str(ROOT / "scripts/lib/run-l1-template-refresh.sh"), str(h.repo), cwd=ROOT)
            with h.authority():
                with self.assertRaisesRegex(ValueError, "dropping"):
                    OWNERSHIP.refresh(h.repo, incoming, False)
                output = h.parent / "prepared"
                before = git(h.repo, "rev-parse", "HEAD"), (h.repo / MAP).read_bytes(), private.read_bytes()
                COMPANY.prepare_render(h.repo, incoming, output)
                self.assertEqual(before, (git(h.repo, "rev-parse", "HEAD"), (h.repo / MAP).read_bytes(), private.read_bytes()))
                mapping = COMPANY.map_sections((output / MAP).read_bytes())
                self.assertIn("private-agent/**", mapping["agent"])
                self.assertNotIn("private-agent/**", mapping["template"])
                real_finalize = RECEIPTS.finalize
                def checked_finalize(*args, **kwargs):
                    results = {}
                    for gate in TRANSITIONS.REQUIRED_VALIDATION:
                        with mock.patch.dict(os.environ, {"ROCS_OUTPUT_ROOT": str(h.repo / ".tmp/rocs-output")}):
                            results[gate["command"].removeprefix("bash ")] = CompanyHarness.run_gate(h, gate).returncode
                    h.evidence[-1]["details"]["validation"] = results; h.write_authority()
                    return real_finalize(*args, **kwargs)
                with mock.patch.object(RECEIPTS, "finalize", side_effect=checked_finalize):
                    first = GITLINK_FIXTURES.V2OwnerGitlinkTests().receipt(h, output)
                self.assertEqual(first["inherited_transition"], binding)
                RECEIPTS.validate_established_provenance(h.repo, first, ak_command=h.ak)
                again = h.parent / "repeat-prepared"
                COMPANY.prepare_render(h.repo, incoming, again)
                self.assertEqual((output / MAP).read_bytes(), (again / MAP).read_bytes())
                before_repeat = git(h.repo, "rev-parse", "HEAD"), (h.repo / STATE).read_bytes()
                OWNERSHIP.refresh(h.repo, again, True, "d" * 64, "repeat-prepared", git(ROOT, "rev-parse", "HEAD"))
                self.assertEqual(before_repeat, (git(h.repo, "rev-parse", "HEAD"), (h.repo / STATE).read_bytes()))
            self.assertEqual(retained, git(h.repo, "ls-files", "-s", "ontology"))
            self.assertEqual(private.read_bytes(), b"fixture agent-owned bytes\n")
            check_history(h.repo)
            clone = h.parent / "history-clone"
            run("git", "clone", "--quiet", "--no-hardlinks", str(h.repo), str(clone), cwd=h.parent)
            check_history(clone)
            # Fresh template claim over private-agent is never silently filtered/adopted.
            (incoming / MAP).write_text((incoming / MAP).read_text().replace("template_owned:\n", "template_owned:\n  - private-agent/**\n"))
            with h.authority(), self.assertRaisesRegex(ValueError, "ambiguous ownership"):
                COMPANY.prepare_render(h.repo, incoming, h.parent / "adoption-refused")
            self.assertFalse((h.parent / "adoption-refused").exists())

    def test_company_preparation_refuses_birth_and_map_only_company_transfer(self):
        with tempfile.TemporaryDirectory(dir=SCRATCH) as raw:
            parent = Path(raw); h = CompanyHarness(parent); plan = h.plan(); h.finish(plan)
            incoming = parent / "incoming"; shutil.copytree(h.repo, incoming, ignore=shutil.ignore_patterns(".git"))
            with mock.patch.object(LIVE, "authoritative_ak", return_value=h.ak):
                with self.assertRaisesRegex(ValueError, "plan trailer"):
                    COMPANY.prepare_render(h.repo, incoming, parent / "refused")
            self.assertFalse((parent / "refused").exists())
            fresh = parent / "birth"; shutil.copytree(ROOT / "fixtures/l1/template-repo", fresh)
            from tests.test_l1_template_transitions import init
            init(fresh)
            with self.assertRaisesRegex(ValueError, "proven convergence"):
                COMPANY.prepare_render(fresh, incoming, parent / "birth-refused")


if __name__ == "__main__":
    unittest.main()
