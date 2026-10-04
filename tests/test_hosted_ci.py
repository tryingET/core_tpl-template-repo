"""Hosted prerequisites and synthetic creation authority; no live AK or network."""
import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import yaml
from tests import test_company_ontology_ref_inheritance as wrappers
# unittest collects this imported class in the existing guardrail cohort. Only
# fast observer contracts are added; no owner check command/schedule is replaced.
from tests.test_ci_reorder import ReorderContractTests

ROOT = Path(__file__).resolve().parents[1]
AK = ROOT / "tests/fixtures/ak-creation-task.sh"
VENDOR = ROOT / "tools/agent-scripts"


class HostedCiTests(unittest.TestCase):
    def test_golden_births_bind_owner_instead_of_ambient_git_or_actor(self):
        """GIVEN golden outputs; WHEN fixtures render; THEN owner inputs are explicit."""
        for name in ("check-l0-fixtures.sh", "sync-l0-fixtures.sh"):
            source = (ROOT / "scripts" / name).read_text().replace("\\\n", " ")
            births = [shlex.split(line) for line in source.splitlines()
                      if line.strip().startswith("run_step ./scripts/new-repo-from-copier.sh")]
            owner_births = [args for args in births if args[2] in ("tpl-project-repo", "tpl-monorepo")]
            self.assertEqual(len(owner_births), 8, name)
            for args in owner_births:
                self.assertIn("project_owner_handle=@tryinget", args, name)

    def test_workflow_provisions_real_sandbox_and_history(self):
        workflow = yaml.safe_load((ROOT / ".github/workflows/l0-check.yml").read_text())
        self.assertEqual(workflow["permissions"], {"contents": "read"})
        steps = workflow["jobs"]["check"]["steps"]
        checkout = next(s for s in steps if s.get("uses", "").startswith("actions/checkout@"))
        self.assertEqual(checkout["with"]["fetch-depth"], 0)
        self.assertFalse(checkout["with"]["persist-credentials"])
        uv = next(s for s in steps if s.get("uses", "").startswith("astral-sh/setup-uv@"))
        self.assertEqual(uv["with"]["version"], "0.12.22")
        sandbox = next(s for s in steps if s["name"] == "Provision birth sandbox")["run"]
        self.assertIn("apt-get install --yes bubblewrap", sandbox)
        self.assertIn("bwrap --die-with-parent --unshare-pid --unshare-ipc --unshare-uts", sandbox)
        self.assertIn("profile ci-bwrap /usr/bin/bwrap", sandbox)
        self.assertNotIn("sysctl", sandbox)
        owner = next(s for s in steps if s["name"] == "Run L0 checks")
        self.assertEqual(owner["run"], "bash ./scripts/check-l0.sh")
        self.assertEqual(owner["env"]["L0_CHECK_VERBOSE"], "1")
        self.assertEqual(owner["env"]["TMPDIR"], "${{ runner.temp }}")
        core = next(s for s in steps if s["name"] == "Provision pinned ROCS core")["run"]
        self.assertIn("https://github.com/tryingET/rocs-cli.git", core)
        self.assertIn("ac75e95e30d66b3543abca27cb79d69a9dc01e93", core)
        self.assertIn('uv sync --project "$core" --frozen', core)
        self.assertEqual(owner["env"]["ROCS_CORE_PROJECT"], "${{ runner.temp }}/rocs-ci")

    def test_characterization_is_exact_branch_only_and_default_checks_are_unchanged(self):
        workflow = yaml.safe_load((ROOT / ".github/workflows/l0-check.yml").read_text())
        events = workflow.get("on", workflow.get(True))  # PyYAML YAML-1.1 boolean key
        self.assertEqual(events, {"pull_request": None, "push": {"branches": ["main", "perf/ak6586-l0-ci-15min"]}})
        self.assertEqual(set(workflow["jobs"]), {"check"})
        self.assertEqual(set(workflow["jobs"]["check"]), {"runs-on", "steps"})
        predicate = ("((github.event_name == 'push' && github.ref == 'refs/heads/perf/ak6586-l0-ci-15min') || "
                     "(github.event_name == 'pull_request' && github.head_ref == 'perf/ak6586-l0-ci-15min' && "
                     "github.event.pull_request.head.repo.full_name == github.repository))")
        steps = {s["name"]: s for s in workflow["jobs"]["check"]["steps"]}
        normalize = lambda value: " ".join(value.split())
        default = steps["Run L0 checks"]
        self.assertEqual(normalize(default["if"]), "!" + predicate)
        self.assertEqual(default["run"], "bash ./scripts/check-l0.sh")
        self.assertEqual(default["env"], {"TMPDIR": "${{ runner.temp }}", "L0_CHECK_VERBOSE": "1",
                                         "ROCS_CORE_PROJECT": "${{ runner.temp }}/rocs-ci"})
        prep = steps["Prepare hosted characterization"]
        self.assertEqual("(" + normalize(prep["if"]) + ")", predicate)
        self.assertIn("umask 077", prep["run"])
        self.assertIn('mktemp -d "$RUNNER_TEMP/l0-profile.XXXXXX"', prep["run"])
        self.assertIn('mktemp -d "$RUNNER_TEMP/l0-reorder-tmp.XXXXXX"', prep["run"])
        serial = steps["Observe unchanged serial L0 checks"]
        self.assertEqual(normalize(serial["if"]), predicate + " && steps.characterization.outputs.profile != ''")
        self.assertEqual(serial["run"], 'python3 -B tests/ci_reorder.py capture --out "$L0_PROFILE_DIR/command.json" -- bash ./scripts/check-l0.sh')
        self.assertEqual(serial["env"]["L0_PROFILE_CONDITION"], "serial")
        self.assertEqual(serial["env"]["L0_PROFILE_DIR"], "${{ steps.characterization.outputs.profile }}/serial")
        second = steps["Observe reversed-module unittest cohorts"]
        self.assertEqual(normalize(second["if"]), "always() && !cancelled() && " + predicate +
                         " && steps.characterization.outputs.profile != '' && steps.serial_profile.outcome == 'success'"
                         " && steps.serial_artifact.outcome == 'success'")
        self.assertEqual(second["env"]["TMPDIR"], "${{ steps.characterization.outputs.tmpdir }}")
        self.assertIn('reorder --serial-dir "$PROFILE_ROOT/serial"', second["run"])
        self.assertIn('--out-dir "$PROFILE_ROOT/reverse-modules" --tmpdir "$TMPDIR"', second["run"])

    def test_characterization_uploader_is_immutable_and_retains_failure_evidence(self):
        workflow = yaml.safe_load((ROOT / ".github/workflows/l0-check.yml").read_text())
        upload = next(s for s in workflow["jobs"]["check"]["steps"]
                      if s["name"] == "Retain characterization artifacts even on failure")
        self.assertEqual(upload["uses"], "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02")
        self.assertTrue(upload["if"].startswith("always() &&"))
        self.assertIn("github.ref == 'refs/heads/perf/ak6586-l0-ci-15min'", upload["if"])
        self.assertIn("github.head_ref == 'perf/ak6586-l0-ci-15min'", upload["if"])
        self.assertIn("steps.characterization.outputs.profile != ''", upload["if"])
        self.assertNotIn("serial_profile.outcome", upload["if"])
        self.assertNotIn("cancelled()", upload["if"])
        self.assertIn("github.event.pull_request.head.repo.full_name == github.repository", upload["if"])
        self.assertIn("Raw logs are unredacted", (ROOT / ".github/workflows/l0-check.yml").read_text())
        self.assertEqual(upload["with"]["path"], "${{ steps.characterization.outputs.profile }}")
        self.assertEqual(upload["with"]["if-no-files-found"], "error")
        self.assertEqual(upload["with"]["retention-days"], 7)

    def test_serial_evidence_upload_precedes_replay_and_final_upload(self):
        workflow = yaml.safe_load((ROOT / ".github/workflows/l0-check.yml").read_text())
        steps = workflow["jobs"]["check"]["steps"]
        names = [step["name"] for step in steps]
        before = next(s for s in steps if s["name"] == "Retain serial characterization before replay")
        final = next(s for s in steps if s["name"] == "Retain characterization artifacts even on failure")
        self.assertLess(names.index("Observe unchanged serial L0 checks"), names.index(before["name"]))
        self.assertLess(names.index(before["name"]), names.index("Observe reversed-module unittest cohorts"))
        self.assertLess(names.index("Observe reversed-module unittest cohorts"), names.index(final["name"]))
        self.assertEqual(" ".join(before["if"].split()), " ".join(final["if"].split()))
        self.assertEqual(before["uses"], final["uses"])
        self.assertEqual(before["id"], "serial_artifact")
        self.assertEqual(before["with"], {
            "name": "l0-serial-${{ github.run_id }}-${{ github.run_attempt }}",
            "path": "${{ steps.characterization.outputs.profile }}/serial",
            "if-no-files-found": "error", "retention-days": 7,
        })
        self.assertNotEqual(before["with"]["name"], final["with"]["name"])
        self.assertNotIn("continue-on-error", before)
        self.assertNotIn("continue-on-error", next(s for s in steps if s["name"] == "Observe unchanged serial L0 checks"))

    def test_characterization_cancel_and_fork_condition_truth_table(self):
        workflow = yaml.safe_load((ROOT / ".github/workflows/l0-check.yml").read_text())
        steps = {s["name"]: s for s in workflow["jobs"]["check"]["steps"]}
        branch = "perf/ak6586-l0-ci-15min"
        # Evaluate only the trusted, fixed condition expressions asserted above;
        # this checks predicates, not GitHub's runtime scheduling implementation.
        for event, head_repo, cancelled, outcome, upload, profile, expected in (
                ("push", "owner/repo", False, "success", "success", "ready", (False, True, True)),
                ("push", "owner/repo", False, "success", "failure", "ready", (False, False, True)),
                ("push", "owner/repo", False, "success", "skipped", "ready", (False, False, True)),
                ("push", "owner/repo", False, "failure", "success", "ready", (False, False, True)),
                ("push", "owner/repo", True, "cancelled", "success", "ready", (False, False, True)),
                ("push", "owner/repo", False, "cancelled", "success", "ready", (False, False, True)),
                ("push", "owner/repo", False, "skipped", "success", "ready", (False, False, True)),
                ("push", "owner/repo", False, "success", "success", "", (False, False, False)),
                ("pull_request", "owner/repo", False, "success", "success", "ready", (False, True, True)),
                ("pull_request", "fork/repo", False, "success", "success", "ready", (True, False, False))):
            with self.subTest(event=event, head_repo=head_repo, cancelled=cancelled, outcome=outcome, profile=profile):
                values = {"github.event_name": event, "github.ref": "refs/heads/" + branch,
                          "github.head_ref": branch, "github.repository": "owner/repo",
                          "github.event.pull_request.head.repo.full_name": head_repo,
                          "steps.characterization.outputs.profile": profile, "steps.serial_profile.outcome": outcome,
                          "steps.serial_artifact.outcome": upload}
                actual = []
                for name in ("Run L0 checks", "Observe reversed-module unittest cohorts",
                             "Retain characterization artifacts even on failure"):
                    condition = " ".join(steps[name]["if"].split())
                    for key in sorted(values, key=len, reverse=True):
                        condition = condition.replace(key, repr(values[key]))
                    condition = condition.replace("always()", "True").replace("cancelled()", repr(cancelled))
                    condition = re.sub(r"!(?!=)", "not ", condition).replace("&&", " and ").replace("||", " or ")
                    actual.append(eval(condition, {"__builtins__": {}}, {}))
                self.assertEqual(tuple(actual), expected)

    def test_vendored_owner_bytes_match_pinned_inventory(self):
        pin = json.loads((VENDOR / "source-pin.json").read_text())
        self.assertEqual(pin["repository"], "https://github.com/tryingET/agent-scripts")
        self.assertEqual(pin["commit"], "81fa62b9fcf312a9939f8b4e8f6270951f1dfab0")
        actual = {str(p.relative_to(VENDOR)) for p in (VENDOR / "scripts").rglob("*") if p.is_file()}
        self.assertEqual(actual, set(pin["files"]))
        for name, digest in pin["files"].items():
            self.assertEqual(hashlib.sha256((VENDOR / name).read_bytes()).hexdigest(), digest, name)

    def test_docs_tool_checks_real_tracked_and_missing_references(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as tmp:
            repo = Path(tmp)
            env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
            env["AI_SOCIETY_WORKSPACE"] = str(repo / "no-workspace")
            for key in ("DOC_REF_CHECK_SCRIPT", "AGENT_SCRIPTS_DOC_REF_CHECK"):
                env.pop(key, None)
            for args in [("init", "-q"), ("config", "maintenance.auto", "false")]:
                subprocess.run(["git", *args], cwd=repo, env=env, check=True, capture_output=True)
            doc = repo / "README.md"
            doc.write_text("[tracked](docs/ok.md)\n")
            (repo / "docs").mkdir()
            (repo / "docs/ok.md").write_text("ok\n")
            subprocess.run(["git", "add", "."], cwd=repo, env=env, check=True)
            (repo / "scripts").mkdir()
            wrapper = repo / "scripts/check-doc-references.sh"
            shutil.copy2(ROOT / "scripts/check-doc-references.sh", wrapper)
            shutil.copytree(VENDOR, repo / "tools/agent-scripts")
            command = ["sh", str(wrapper), "--path", str(doc)]
            result = subprocess.run(command, cwd=repo, env=env, text=True, capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            (repo / "docs/untracked.md").write_text("not in index\n")
            doc.write_text("[untracked](docs/untracked.md)\n")
            result = subprocess.run(command, cwd=repo, env=env, text=True, capture_output=True)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("not git-tracked", result.stdout + result.stderr)
            doc.write_text("[missing](docs/missing.md)\n")
            result = subprocess.run(command, cwd=repo, env=env, text=True, capture_output=True)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("missing.md", result.stdout + result.stderr)

    def test_missing_docs_tool_still_refuses_without_private_workspace(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as tmp:
            repo = Path(tmp)
            (repo / "scripts").mkdir()
            script = repo / "scripts/check-doc-references.sh"
            shutil.copy2(ROOT / "scripts/check-doc-references.sh", script)
            env = dict(os.environ, AI_SOCIETY_WORKSPACE=str(repo / "no-workspace"))
            for key in ("DOC_REF_CHECK_SCRIPT", "AGENT_SCRIPTS_DOC_REF_CHECK"):
                env.pop(key, None)
            result = subprocess.run(["sh", str(script)], env=env, text=True, capture_output=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn("could not resolve docs-ref-check", result.stderr)

    def test_creation_fixture_refuses_every_other_operation(self):
        valid = subprocess.run([str(AK), "task", "show", "5105"], capture_output=True)
        self.assertEqual(valid.returncode, 0)
        for args in [[], ["task", "show"], ["task", "show", "1"], ["task", "show", "999999999"],
                     ["task", "show", "5105", "--extra"], ["task", "complete", "5105"]]:
            with self.subTest(args=args):
                self.assertEqual(subprocess.run([str(AK), *args], capture_output=True).returncode, 97)

    def test_real_creation_gate_keeps_refusals_and_literal_argument_forms(self):
        harness = wrappers.WrapperTests()
        harness.setUp()
        self.addCleanup(harness.doCleanups)
        harness.env["AK_CMD"] = str(AK)
        base = ["sh", str(harness.l1 / "scripts/new-repo-from-copier.sh"), "tpl-agent-repo", str(harness.dest)]
        refusals = [
            ([], "exactly one creation_task_id"),
            (["-d", "creation_task_id=AK-5105"], "exactly one agent_role"),
            (["-d", "creation_task_id=AK-5105", "-d", "creation_task_id=AK-5105", "-d", "agent_role=x"], "exactly one creation_task_id"),
            (["-d", "creation_task_id=AK-5105", "-d", "agent_role=x", "-d", "agent_role=x"], "exactly one agent_role"),
            (["-d", "creation_task_id=AK-5105", "-d", "agent_role= \t"], "must be non-empty"),
        ]
        for task in ("AK-0", "AK-01", "AK-x", "invalid", "AK-999999999"):
            message = "not visible" if task == "AK-999999999" else ("positive integer" if task == "invalid" else "invalid AK creation task")
            refusals.append((["-d", "creation_task_id=" + task, "-d", "agent_role=x"], message))
        for args, message in refusals:
            with self.subTest(args=args):
                result = subprocess.run([*base, *args], cwd=harness.root, env=harness.env, text=True, capture_output=True)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertIn(message, result.stderr)
                self.assertFalse(harness.dest.exists(), "refused gate created destination")
        missing = dict(harness.env, AK_CMD=str(harness.root / "no-ak"))
        result = subprocess.run([*base, "-d", "creation_task_id=AK-5105", "-d", "agent_role=x"], env=missing, text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("requires installed", result.stderr)
        for args in [("-d", "creation_task_id=AK-5105", "-d", "agent_role=x"),
                     ("--data=creation_task_id=AK-5105", "--data", "agent_role=x"),
                     ("-dcreation_task_id=AK-5105", "-dagent_role=x")]:
            harness.invoke(*args, archetype="tpl-agent-repo")


if __name__ == "__main__":
    unittest.main()
