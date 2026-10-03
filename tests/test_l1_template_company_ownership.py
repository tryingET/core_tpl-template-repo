"""Ontology ownership lifecycle: real isolated Git/gates, fixture AK only, no live L1."""
from __future__ import annotations

import copy
import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from tests.test_l1_template_transitions import (
    Harness, ROOT, FIXTURE, SCRATCH, CHECKED_AT, COMPLETED_AT, TRANSITIONS, git, run, sha,
)
from tests import test_l1_template_gitlink_retirements as gitlink_fixtures
import l1_template_company as COMPANY
import l1_template_ownership as OWNERSHIP
import l1_template_receipts as RECEIPTS
import l1_template_transitions as LIVE

MAP = "contracts/template-ownership.yml"
STATE = "contracts/template-ownership-state.json"
CHECKER = "scripts/lib/check-l1-ownership-state.py"


def controls(repo: Path) -> tuple[bytes, bytes]:
    return (repo / MAP).read_bytes(), (repo / STATE).read_bytes()


def commit(repo: Path, message: str, *paths: str) -> str:
    run("git", "add", *paths, cwd=repo)
    run("git", "commit", "--quiet", "-m", message, cwd=repo)
    return git(repo, "rev-parse", "HEAD")


def bind_runtime_pin(repo: Path) -> None:
    """Golden fixture normalization is not a runtime birth/source pin."""
    pin = git(ROOT, "rev-parse", "HEAD")
    for relative, placeholder in (
        (".copier-answers.yml", "__VOLATILE_L0_SOURCE_SHA__"),
        ("contracts/provenance-seal.yml", "__VOLATILE_SOURCE_SHA__"),
    ):
        path = repo / relative
        raw = path.read_text()
        assert raw.count(placeholder) == 1
        path.write_text(raw.replace(placeholder, pin))


class CompanyHarness(Harness):
    def __init__(self, parent: Path):
        super().__init__(parent, legacy_schema=True)
        bind_runtime_pin(self.repo)
        self.base = commit(self.repo, "bind runtime fixture to exact L0 source",
                           ".copier-answers.yml", "contracts/provenance-seal.yml")
        self.next_map.write_text((self.repo / MAP).read_text().replace(
            "schema: ai-society.template-ownership/1", "schema: ai-society.template-ownership/2"
        ).replace("  - ontology/**\n", "") + "company_owned:\n  - ontology/**\n")
        self.spec.update(adr_commit=self.base, git_delta=[])
        self.spec_path.write_text(json.dumps(self.spec))
        self.original_task = None

    def run_gate(self, gate: dict):
        # Full CI needs this fixture's AK even for an empty snapshot directory.
        # Template CI owns a separate snapshot-capable fixture; do not override it.
        binding = ["env", f"AK_CMD={self.ak}"] if gate["id"] == "ci-full" else ["env", "-u", "AK_CMD"]
        return run(*binding, "bash", *gate["command"].split()[1:], cwd=self.repo)

    def finish(self, plan: dict, real_gates: bool = False) -> dict:
        previous = copy.deepcopy(self.evidence)
        with mock.patch.object(TRANSITIONS, "write_atomic", wraps=TRANSITIONS.write_atomic) as writes:
            TRANSITIONS.apply(self.repo, self.plan_path, self.ak)
        self.assert_controls_only(writes)
        applied = commit(self.repo, "pending company ontology ownership", MAP, STATE)
        results = {"check-template-ci": 0, "ci-full": 0}
        if real_gates:
            for gate in TRANSITIONS.REQUIRED_VALIDATION:
                result = self.run_gate(gate)
                results[gate["id"]] = result.returncode
        else:
            run("python3", "-I", "-S", "-B", CHECKER, cwd=self.repo)
        self.evidence = previous + [{
            "id": 901 + len(previous), "task_id": self.task["id"], "repo": str(self.repo.resolve()),
            "repo_scope": str(self.repo.resolve()), "check_type": "l1_ownership_transition_v1",
            "result": "pass", "checked_at": CHECKED_AT,
            "details": {"plan": plan, "applied_commit": applied, "validation_results": results},
        }]
        self.write_authority()
        TRANSITIONS.finalize(self.repo, self.plan_path, f"AK-{self.task['id']}", self.ak)
        commit(self.repo, "finalize company ontology receipt", STATE)
        state = json.loads((self.repo / STATE).read_text())
        TRANSITIONS.validate_v2_provenance(self.repo, state, self.ak)
        run("python3", "-I", "-S", "-B", CHECKER, cwd=self.repo)
        return state

    def assert_controls_only(self, writes) -> None:
        paths = [call.args[1] for call in writes.call_args_list]
        if paths != [self.repo / MAP, self.repo / STATE]:
            raise AssertionError(paths)

    def new_reverse_task(self) -> None:
        self.original_task = dict(self.task, status="done", claimed_by=None, completed_at=COMPLETED_AT)
        (self.parent / "forward-task.json").write_text(json.dumps(self.original_task))
        self.task.update(id=322)
        self.decision["linked_tasks"].append({"task_id": 322, "link_role": "post_adr_execution"})
        self.ak.write_text(
            "#!/bin/sh\ncase \"$1 $2\" in\n"
            f" 'task show') if [ \"$3\" = 321 ]; then cat '{self.parent / 'forward-task.json'}'; else cat '{self.task_json}'; fi ;;\n"
            f" 'decision get') cat '{self.decision_json}' ;;\n"
            f" 'evidence task') cat '{self.evidence_json}' ;;\n *) exit 2 ;;\nesac\n"
        )
        self.write_authority()

    def reverse(self) -> dict:
        spec = {k: self.spec[k] for k in ("decision_id", "adr_commit", "executor", "rollback")}
        spec["transition_task_id"] = self.task["id"]
        self.spec_path.write_text(json.dumps(spec))
        COMPANY.reverse_plan(self.repo, self.spec_path, self.plan_path, self.ak)
        return json.loads(self.plan_path.read_text())


class CompanyOntologyTests(unittest.TestCase):
    def test_real_full_ci_binds_fixture_ak_without_ambient_runtime(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH) as name:
            h = CompanyHarness(Path(name))
            refused = run("env", "AK_CMD=/definitely/missing-ak", "bash", "scripts/ci/full.sh",
                          cwd=h.repo, expect=1)
            self.assertIn("missing ak command", refused.stderr)
            with mock.patch.dict(os.environ, {"AK_CMD": "/definitely/missing-ak"}):
                for gate in TRANSITIONS.REQUIRED_VALIDATION:
                    result = h.run_gate(gate)
            # ci-full is last; template CI also passed with its own scoped fixture.
            self.assertIn("ok: no task-scope snapshots", result.stdout)
            self.assertIn("ok: ci full", result.stdout)
            # The authority double must still refuse any unsupported scope request.
            run(str(h.ak), "task", "scope", "export", "321", cwd=h.repo, expect=2)

    def test_real_forward_and_receipted_reverse_restore_ownership(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH) as name:
            h = CompanyHarness(Path(name))
            seed = (h.repo / "ontology/.gitkeep").read_bytes()
            before = controls(h.repo)
            plan = h.plan()
            self.assertEqual(plan["schema"], COMPANY.PLAN_SCHEMA)
            self.assertEqual(plan["git_delta"], [])
            self.assertIsNone(plan["reverse_of"])
            first_plan = h.plan_path.read_bytes()
            h.plan()
            self.assertEqual(first_plan, h.plan_path.read_bytes())
            self.assertEqual(controls(h.repo), before)
            h.finish(plan, real_gates=True)
            self.assertEqual(OWNERSHIP.owner("ontology/manifest.yaml", OWNERSHIP.load_map(h.repo)), "company")
            self.assertEqual((h.repo / "ontology/.gitkeep").read_bytes(), seed)
            h.new_reverse_task()
            reverse = h.reverse()
            self.assertEqual(reverse["reverse_of"]["transition_task_id"], 321)
            self.assertEqual(reverse["reverse_of"]["evidence_id"], 901)
            canonical = h.plan_path.read_bytes()
            h.reverse()
            self.assertEqual(canonical, h.plan_path.read_bytes())
            h.finish(reverse, real_gates=True)
            self.assertEqual(OWNERSHIP.owner("ontology/manifest.yaml", OWNERSHIP.load_map(h.repo)), "template")
            self.assertEqual(git(h.repo, "status", "--porcelain"), "")
            # Later ordinary work must not invalidate durable inverse provenance.
            (h.repo / "later.txt").write_text("later ordinary work\n")
            commit(h.repo, "later", "later.txt")
            TRANSITIONS.validate_v2_provenance(h.repo, json.loads((h.repo / STATE).read_text()), h.ak)

    def test_company_birth_and_refresh_preserve_all_ontology_and_never_seed_missing_file(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH) as name:
            parent = Path(name)
            repo, rendered = parent / "repo", parent / "rendered"
            shutil.copytree(FIXTURE, repo)
            shutil.copytree(FIXTURE, rendered)
            from tests.test_l1_template_transitions import init
            for root in (repo, rendered):
                raw = (root / MAP).read_bytes().replace(b"company_owned:\n  - ontology/**\n", b"company_owned:\n  # parsed formatting must not reimpose the seed\n  - ontology/**  \n")
                (root / MAP).write_bytes(raw)
                state = json.loads((root / STATE).read_text())
                state["ownership_map_sha256"] = sha(raw)
                (root / STATE).write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")
            init(repo)
            (repo / "ontology/.gitkeep").unlink()
            data = b"company vocabulary must remain byte exact\n"
            (repo / "ontology/README.md").write_bytes(data)
            commit(repo, "company owns seed and vocabulary", "ontology")
            full = rendered / "scripts/ci/full.sh"
            full.write_text(full.read_text() + "\n# incoming L0 update\n")
            OWNERSHIP.refresh(repo, rendered, True, "a" * 64, "company-test", git(ROOT, "rev-parse", "HEAD"))
            self.assertEqual((repo / "ontology/README.md").read_bytes(), data)
            self.assertFalse((repo / "ontology/.gitkeep").exists())
            run("python3", "-I", "-S", "-B", CHECKER, cwd=repo)
            # Landed6333 correctly rejects this deliberately manifest-less vocabulary;
            # it must not instead reimpose the L0 seed or change company bytes.
            gate = run("bash", "scripts/check-template-ci.sh", cwd=repo, expect=1)
            self.assertIn("ontology manifest is missing", gate.stderr)
            self.assertNotIn("ontology/.gitkeep", gate.stderr)

    def test_ordinary_refresh_and_retirement_cannot_transfer_or_touch_company_ontology(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH) as name:
            parent = Path(name)
            h = CompanyHarness(parent)
            rendered = parent / "rendered"
            shutil.copytree(FIXTURE, rendered)
            before = controls(h.repo)
            for apply in (False, True):
                with self.assertRaisesRegex(ValueError, "receipted ownership transition"):
                    OWNERSHIP.refresh(h.repo, rendered, apply)
            self.assertEqual(controls(h.repo), before)
            h.finish(h.plan())
            with mock.patch.object(LIVE, "authoritative_ak", return_value=h.ak):
                before = controls(h.repo)
                extra = rendered / "ontology/L0-new.md"
                extra.write_text("must refuse\n")
                with self.assertRaisesRegex(ValueError, "birth placeholder"):
                    OWNERSHIP.refresh(h.repo, rendered, False)
                extra.unlink()
                from l1_template_retirements import plan as retirement_plan
                from l1_template_gitlinks import index_entries
                manifest = gitlink_fixtures.manifest(h.parent, gitlink_fixtures.rule("ontology/**"))
                with self.assertRaisesRegex(ValueError, "template ownership"):
                    retirement_plan(h.repo, index_entries(h.repo), set(), OWNERSHIP.load_map(h.repo), OWNERSHIP.load_map(rendered), OWNERSHIP.owner, manifest)
                self.assertEqual(controls(h.repo), before)

    def test_reverse_refuses_birth_ownership_and_residual_ignored_content_or_seed_drift(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH) as name:
            h = CompanyHarness(Path(name))
            h.finish(h.plan())
            h.new_reverse_task()
            before = controls(h.repo)
            with (h.repo / ".git/info/exclude").open("a") as exclude:
                exclude.write("\n/ontology/**\n")
            for rel, kind in (("ontology/dist", "dir"), ("ontology/.git", "dir"), ("ontology/__pycache__", "dir"), ("ontology/ignored", "file"), ("ontology/link", "link")):
                path = h.repo / rel
                if kind == "dir": path.mkdir()
                elif kind == "link": path.symlink_to(h.parent)
                else: path.write_text("ignored company bytes\n")
                # Git excludes hide all these paths; the filesystem census must stop them.
                self.assertEqual(git(h.repo, "status", "--porcelain", "--untracked-files=all"), "")
                with self.assertRaisesRegex(ValueError, "residual ontology"):
                    h.reverse()
                if kind == "dir": path.rmdir()
                else: path.unlink()
                self.assertEqual(controls(h.repo), before)
            seed = h.repo / "ontology/.gitkeep"
            for mode in (0o600, 0o755):
                seed.chmod(mode)
                with self.assertRaisesRegex(ValueError, "mode drift|clean worktree"):
                    h.reverse()
                seed.chmod(0o644)
            seed.write_text("dirty seed\n")
            with self.assertRaisesRegex(ValueError, "bytes/type/mode drift|clean worktree"):
                h.reverse()
            seed.write_bytes(b"")
            # No actual forward receipt means no reverse authority, even at valid birth.
            state = json.loads((h.repo / STATE).read_text())
            with self.assertRaisesRegex(ValueError, "not birth ownership"):
                COMPANY.source_binding(h.repo, {"schema": "ai-society.template-ownership-state/1", "state": "established"}, b"{}", h.ak)
            self.assertEqual(json.loads((h.repo / STATE).read_text()), state)

    def test_reverse_rechecks_census_and_rejects_forged_receipt_or_extra_ownership(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH) as name:
            h = CompanyHarness(Path(name))
            h.finish(h.plan())
            h.new_reverse_task()
            reverse = h.reverse()
            before = controls(h.repo)
            extra = h.repo / "ontology/dist"
            extra.mkdir()
            with self.assertRaisesRegex(ValueError, "residual ontology"):
                TRANSITIONS.apply(h.repo, h.plan_path, h.ak)
            extra.rmdir()
            for key, value in (("evidence_id", 999), ("executor", "other"), ("final_commit", h.base)):
                forged = copy.deepcopy(reverse)
                forged["reverse_of"][key] = value
                forged["canonical_plan_sha256"] = TRANSITIONS.plan_hash(forged)
                h.plan_path.write_text(json.dumps(forged))
                with self.assertRaisesRegex(ValueError, "actual forward receipt"):
                    TRANSITIONS.apply(h.repo, h.plan_path, h.ak)
                self.assertEqual(controls(h.repo), before)
            forged = copy.deepcopy(reverse)
            forged["next_map_text"] = forged["next_map_text"].replace("  - docs/org/**\n", "")
            forged["next_map_sha256"] = sha(forged["next_map_text"].encode())
            forged["canonical_plan_sha256"] = TRANSITIONS.plan_hash(forged)
            h.plan_path.write_text(json.dumps(forged))
            with self.assertRaisesRegex(ValueError, "semantic map delta|only ontology"):
                TRANSITIONS.apply(h.repo, h.plan_path, h.ak)
            self.assertEqual(controls(h.repo), before)

    def test_reverse_after_repeated_v3_refresh_preserves_other_map_changes(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH) as name:
            parent = Path(name)
            h = CompanyHarness(parent)
            h.finish(h.plan())
            rendered = parent / "rendered"
            shutil.copytree(FIXTURE, rendered)
            # A harmless new template claim must not disappear when ontology reverses.
            raw = (h.repo / MAP).read_text().replace("template_owned:\n", "template_owned:\n  - future/**\n")
            (rendered / MAP).write_text(raw)
            full = rendered / "scripts/ci/full.sh"
            full.write_text(full.read_text() + "\n# refresh one\n")
            real_wave = RECEIPTS.verify_wave_evidence
            wave = lambda repo, state, task_id=None, ak_command=None, **kwargs: real_wave(repo, state, task_id, h.ak, **kwargs)
            with mock.patch.object(LIVE, "authoritative_ak", return_value=h.ak), mock.patch.object(RECEIPTS, "verify_wave_evidence", wave):
                first = gitlink_fixtures.V2OwnerGitlinkTests().receipt(h, rendered)
                full.write_text(full.read_text() + "# refresh two\n")
                second = gitlink_fixtures.V2OwnerGitlinkTests().receipt(h, rendered)
                self.assertEqual(first["inherited_transition"], second["inherited_transition"])
                run("python3", "-I", "-S", "-B", CHECKER, cwd=h.repo)
                h.new_reverse_task()
                reverse = h.reverse()
                self.assertIn("  - future/**\n", reverse["next_map_text"])
                h.finish(reverse)

    def test_old_readers_upgrade_through_a_receipted_preparatory_refresh(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH) as name:
            h = CompanyHarness(Path(name))
            # Actual pre-AK6328 readers from published main, not a private local ref.
            for rel in (CHECKER, "scripts/check-template-ci.sh", "scripts/new-repo-from-copier.sh",
                        "scripts/lib/company-ontology-ref.sh"):
                original = TRANSITIONS.git_bytes(ROOT, "show", f"72828add2ec38e3a41aacd7fa0c6b4232a7595a3:copier-template/{rel}")
                (h.repo / rel).write_bytes(original)
            (h.repo / "scripts/lib/l1_ontology_ownership.py").unlink()
            commit(h.repo, "pre-company reader generation", "scripts")
            run("bash", "scripts/check-template-ci.sh", cwd=h.repo)
            incoming = h.parent / "incoming"
            shutil.copytree(FIXTURE, incoming)
            bind_runtime_pin(incoming)
            prepared = h.parent / "prepared"
            before = controls(h.repo)
            run("python3", str(ROOT / "scripts/lib/l1_template_ownership.py"), "--repo-root", str(h.repo),
                "--transition-action", "prepare-render", "--rendered", str(incoming),
                "--transition-output", str(prepared), cwd=ROOT)
            self.assertEqual(controls(h.repo), before)
            self.assertEqual(git(h.repo, "status", "--porcelain"), "")
            self.assertEqual(OWNERSHIP.owner("ontology/manifest.yaml", OWNERSHIP.load_map(prepared)), "template")
            real_finalize = RECEIPTS.finalize

            def checked_finalize(*args):
                for gate in TRANSITIONS.REQUIRED_VALIDATION:
                    h.run_gate(gate)
                return real_finalize(*args)

            with mock.patch.object(RECEIPTS, "finalize", side_effect=checked_finalize):
                gitlink_fixtures.V2OwnerGitlinkTests().receipt(h, prepared)
            # The new class can now be admitted without changing any reader in its map-only commit.
            real_wave = RECEIPTS.verify_wave_evidence
            with mock.patch.object(RECEIPTS, "verify_wave_evidence", side_effect=lambda repo, state, task_id=None, ak_command=None: real_wave(repo, state, task_id, h.ak)):
                h.finish(h.plan(), real_gates=True)
            self.assertEqual(OWNERSHIP.owner("ontology/manifest.yaml", OWNERSHIP.load_map(h.repo)), "company")

    def test_wrapper_cannot_grant_company_ownership_reseed_or_change_topology(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH) as name:
            parent = Path(name)
            h = CompanyHarness(parent)
            before = controls(h.repo)
            rejected = run("sh", str(ROOT / "scripts/new-l1-from-copier.sh"), str(h.repo),
                           "--defaults", "--overwrite", cwd=ROOT, expect=2)
            self.assertIn("cannot change company ontology ownership", rejected.stderr)
            self.assertEqual(controls(h.repo), before)
            company = parent / "company-birth"
            shutil.copytree(FIXTURE, company)
            from tests.test_l1_template_transitions import init
            init(company)
            for content in (None, b"company-customized seed\n"):
                seed = company / "ontology/.gitkeep"
                if content is None: seed.unlink()
                else: seed.write_bytes(content)
                snapshot = controls(company)
                rejected = run("sh", str(ROOT / "scripts/new-l1-from-copier.sh"), str(company),
                               "--defaults", "--overwrite", cwd=ROOT, expect=2)
                self.assertIn("ownership reverse", rejected.stderr)
                self.assertEqual(controls(company), snapshot)
                self.assertEqual(seed.read_bytes() if seed.exists() else None, content)
            (company / "ontology/.gitkeep").write_bytes(b"")
            rejected = run("sh", str(ROOT / "scripts/new-l1-from-copier.sh"), str(company),
                           "-d", "l1_ontology_layout=gitlink", "--defaults", "--overwrite", cwd=ROOT, expect=2)
            self.assertIn("cannot change company ontology topology", rejected.stderr)
            self.assertEqual((company / "ontology/.gitkeep").read_bytes(), b"")

    def test_preparation_refuses_dropping_existing_agent_claims(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH) as name:
            h = CompanyHarness(Path(name))
            raw = (h.repo / MAP).read_bytes() + b"  - bespoke/**\n"
            (h.repo / MAP).write_bytes(raw)
            state = json.loads((h.repo / STATE).read_text())
            state["ownership_map_sha256"] = sha(raw)
            (h.repo / STATE).write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")
            run("git", "add", MAP, STATE, cwd=h.repo)
            run("git", "commit", "--amend", "--no-edit", "--quiet", cwd=h.repo)
            incoming = h.parent / "incoming"
            shutil.copytree(FIXTURE, incoming)
            output = h.parent / "prepared"
            before = controls(h.repo)
            with self.assertRaisesRegex(ValueError, "dropping company-owned patterns: bespoke"):
                COMPANY.prepare_render(h.repo, incoming, output)
            self.assertFalse(output.exists())
            self.assertEqual(controls(h.repo), before)

    def test_inverse_source_must_exist_in_historical_base_not_just_current_head(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH) as name:
            h = CompanyHarness(Path(name))
            state = h.finish(h.plan())
            with self.assertRaisesRegex(ValueError, "provenance check failed"):
                COMPANY.source_binding(h.repo, state, (h.repo / STATE).read_bytes(), h.ak, anchor=h.base)

    def test_v3_birth_origin_and_applied_commit_forgery_do_not_bypass_wave_receipt(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH) as name:
            h = CompanyHarness(Path(name))
            h.finish(h.plan())
            incoming = h.parent / "incoming"
            shutil.copytree(FIXTURE, incoming)
            (incoming / MAP).write_bytes((h.repo / MAP).read_bytes())
            full = incoming / "scripts/ci/full.sh"
            full.write_text(full.read_text() + "\n# inherited refresh\n")
            real_wave = RECEIPTS.verify_wave_evidence
            wave = lambda repo, state, task_id=None, ak_command=None, **kwargs: real_wave(repo, state, task_id, h.ak, **kwargs)
            with mock.patch.object(LIVE, "authoritative_ak", return_value=h.ak), mock.patch.object(RECEIPTS, "verify_wave_evidence", wave):
                state = gitlink_fixtures.V2OwnerGitlinkTests().receipt(h, incoming)
                for forged in (dict(state, origin="copier-birth"), dict(state, applied_commit=h.base)):
                    (h.repo / STATE).write_text(json.dumps(forged, indent=2, sort_keys=True) + "\n")
                    with self.assertRaisesRegex(ValueError, "copier-birth origin|evidence applied commit"):
                        RECEIPTS.validate_established_provenance(h.repo, forged, ak_command=h.ak)
                    with self.assertRaisesRegex(ValueError, "origin|predecessor state"):
                        COMPANY.source_binding(h.repo, forged, (h.repo / STATE).read_bytes(), h.ak)

    def test_v1_birth_relabel_cannot_erase_an_executed_ownership_transition(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH) as name:
            h = CompanyHarness(Path(name))
            birth = json.loads(TRANSITIONS.git_bytes(h.repo, "show", f"{h.base}:{STATE}"))
            birth_map = TRANSITIONS.git_bytes(h.repo, "show", f"{h.base}:{MAP}")
            h.finish(h.plan())
            company_map = (h.repo / MAP).read_bytes()
            for raw in (company_map, birth_map):
                forged = dict(birth, ownership_map_sha256=sha(raw))
                (h.repo / MAP).write_bytes(raw)
                (h.repo / STATE).write_text(json.dumps(forged, indent=2, sort_keys=True) + "\n")
                commit(h.repo, "forged lifecycle relabel (negative fixture only)", MAP, STATE)
                with self.assertRaisesRegex(ValueError, "root ownership|discard a receipted transition"):
                    RECEIPTS.validate_established_provenance(h.repo, forged, ak_command=h.ak)
                from l1_answer_template_upgrade import prepare_wrapper
                with self.assertRaisesRegex(ValueError, "root ownership|discard a receipted transition"):
                    prepare_wrapper(h.repo, ROOT / "copier-template")

    def test_planning_outputs_cannot_mutate_a_target_or_its_shared_git_metadata(self) -> None:
        with tempfile.TemporaryDirectory(dir=SCRATCH) as name:
            h = CompanyHarness(Path(name))
            linked = h.parent / "linked"
            run("git", "worktree", "add", "--quiet", "--detach", str(linked), h.base, cwd=h.repo)
            before = controls(h.repo)
            for output in (h.repo / "plan.json", h.repo / ".git/plan.json", linked / "plan.json"):
                with self.assertRaisesRegex(ValueError, "outside all target worktrees"):
                    TRANSITIONS.create_plan(h.repo, h.spec_path, output, h.ak)
                self.assertFalse(output.exists())
                self.assertEqual(controls(h.repo), before)
            run("git", "worktree", "remove", str(linked), cwd=h.repo)

    def test_legacy_plans_stay_nonempty_and_map_v2_refuses_unknown_or_overlapping_classes(self) -> None:
        with self.assertRaisesRegex(ValueError, "non-empty"):
            TRANSITIONS.validate_git_delta([])
        raw = (FIXTURE / MAP).read_bytes()
        for invalid in (
            raw.replace(b"/2\n", b"/1\n", 1),
            raw.replace(b"company_owned:", b"unknown_owned:"),
            raw.replace(b"template_owned:\n", b"template_owned:\n  - ontology/**\n"),
            raw + b"company_owned:\n",
        ):
            with self.assertRaises(ValueError):
                COMPANY.map_sections(invalid)


if __name__ == "__main__":
    unittest.main()
