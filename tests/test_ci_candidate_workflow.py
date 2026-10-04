"""Fast hosted wiring contracts; no product cohorts, network or live CI execution."""
import hashlib
import os
from pathlib import Path
import re
import shlex
import stat
import subprocess
import tempfile
import unittest

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/l0-check.yml"
BRANCH = "perf/ak6586-l0-ci-15min"
PREDICATE = ("((github.event_name == 'push' && github.ref == 'refs/heads/" + BRANCH + "') || "
             "(github.event_name == 'pull_request' && github.head_ref == '" + BRANCH + "' && "
             "github.event.pull_request.head.repo.full_name == github.repository))")
UPLOAD = "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02"
DOWNLOAD = "actions/download-artifact@d3f86a106a0bac45b974a628896c90dbdf5c8093"
ROCS = "ac75e95e30d66b3543abca27cb79d69a9dc01e93"
MATRIX = [{"worker": worker, "slots": slots}
          for worker, slots in enumerate((4, 4, 5, 6, 5, 9), 1)]


def evaluate(condition, values, *, success=True, cancelled=False):
    """Evaluate only fixed, asserted workflow expressions, not runner scheduling."""
    for key in sorted(values, key=len, reverse=True):
        condition = condition.replace(key, repr(values[key]))
    condition = condition.replace("always()", "True").replace("success()", repr(success))
    condition = condition.replace("cancelled()", repr(cancelled))
    condition = re.sub(r"!(?!=)", "not ", condition).replace("&&", " and ").replace("||", " or ")
    return eval(condition.strip(), {"__builtins__": {}}, {})


class CandidateWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.source = WORKFLOW.read_text()
        self.workflow = yaml.safe_load(self.source)
        self.jobs = self.workflow["jobs"]
        self.worker_steps = {s["name"]: s for s in self.jobs["candidate"]["steps"]}
        self.aggregate_steps = {s["name"]: s for s in self.jobs["aggregate"]["steps"]}

    def test_exact_six_worker_matrix_and_closed_33_slots(self):
        self.assertEqual(set(self.jobs), {"check", "candidate", "aggregate"})
        self.assertEqual(self.jobs["candidate"]["strategy"], {
            "fail-fast": False, "max-parallel": 6, "matrix": {"include": MATRIX}})
        self.assertEqual(sum(row["slots"] for row in MATRIX), 33)
        self.assertEqual(self.jobs["candidate"]["timeout-minutes"], 60)
        self.assertNotIn("needs", self.jobs["candidate"])
        self.assertEqual(self.jobs["aggregate"]["needs"], "candidate")

    def test_each_eligible_slot_has_one_capture_then_immutable_upload(self):
        steps = self.jobs["candidate"]["steps"]
        names = [s["name"] for s in steps]
        runs = [s for s in steps if "tests/ci_worker.py" in s.get("run", "")]
        self.assertEqual(len(runs), 9)
        artifact_names = set()
        for row in MATRIX:
            for slot in range(1, row["slots"] + 1):
                run = self.worker_steps[f"Run slot {slot}"]
                upload = self.worker_steps[f"Retain slot {slot}"]
                index = names.index(run["name"])
                self.assertEqual(steps[index + 1], upload)
                if slot < 9:
                    self.assertEqual(steps[index + 2]["name"], f"Run slot {slot + 1}")
                command = run["run"].splitlines()[-1].replace("${{ matrix.worker }}", str(row["worker"]))
                self.assertEqual(shlex.split(command), [
                    "python3", "-B", "tests/ci_worker.py", "--worker", str(row["worker"]),
                    "--slot", str(slot), "--out", f"$OUTPUT_ROOT/slot{slot}",
                    "--source-sha", "$GITHUB_SHA", "--run-id", "$GITHUB_RUN_ID",
                    "--attempt", "$GITHUB_RUN_ATTEMPT"])
                self.assertEqual(run["run"].count("tests/ci_worker.py"), 1)
                self.assertEqual(upload["uses"], UPLOAD)
                expected = "l0-candidate-${{ github.run_id }}-${{ github.run_attempt }}-worker${{ matrix.worker }}-slot" + str(slot)
                self.assertEqual(upload["with"], {
                    "name": expected, "path": "${{ steps.prepare.outputs.root }}/slot" + str(slot),
                    "if-no-files-found": "error", "retention-days": 7})
                artifact_names.add(expected.replace("${{ matrix.worker }}", str(row["worker"])))
        self.assertEqual(len(artifact_names), 33)
        self.assertNotIn("for ", "\n".join(s["run"] for s in runs))

    def test_failed_slot_stops_later_calls_but_retains_completed_evidence(self):
        for row in MATRIX:
            values = {"matrix.slots": row["slots"], "steps.prepare.outputs.root": "/private"}
            for failed_slot in range(1, row["slots"] + 1):
                called, retained = [], []
                success = True
                for slot in range(1, 10):
                    run = self.worker_steps[f"Run slot {slot}"]
                    upload = self.worker_steps[f"Retain slot {slot}"]
                    self.assertEqual(run["if"], f"success() && matrix.slots >= {slot}")
                    self.assertEqual(upload["if"], f"always() && !cancelled() && matrix.slots >= {slot} && steps.prepare.outputs.root != ''")
                    if evaluate(run["if"], values, success=success):
                        called.append(slot)
                        success = slot != failed_slot
                    if evaluate(upload["if"], values, success=success):
                        retained.append(slot)
                    self.assertFalse(evaluate(upload["if"], values, cancelled=True))
                    self.assertFalse(evaluate(upload["if"], dict(values, **{"steps.prepare.outputs.root": ""})))
                self.assertEqual(called, list(range(1, failed_slot + 1)))
                # Later missing paths fail their uploads; they cannot erase earlier artifacts.
                self.assertEqual(retained, list(range(1, row["slots"] + 1)))

    def test_default_full_serial_path_has_no_candidate_execution_or_prewarm(self):
        check = self.jobs["check"]
        self.assertEqual(set(check), {"if", "runs-on", "steps"})
        self.assertEqual(check["runs-on"], "ubuntu-latest")
        self.assertEqual(check["if"], "!" + PREDICATE)
        self.assertEqual([s["name"] for s in check["steps"]], [
            "Checkout", "Setup uv", "Provision birth sandbox", "Provision pinned ROCS core", "Run L0 checks"])
        owner = check["steps"][-1]
        self.assertEqual(owner, {"name": "Run L0 checks", "env": {
            "TMPDIR": "${{ runner.temp }}", "L0_CHECK_VERBOSE": "1",
            "ROCS_CORE_PROJECT": "${{ runner.temp }}/rocs-ci"}, "run": "bash ./scripts/check-l0.sh"})
        self.assertEqual(self.source.count("bash ./scripts/check-l0.sh"), 1)
        for obsolete in ("ci_reorder.py", "reverse-modules", "serial_profile", "L0_PROFILE_CONDITION"):
            self.assertNotIn(obsolete, self.source)

    def test_independent_full_history_pinned_uv_rocs_and_real_sandbox(self):
        for name in ("check", "candidate", "aggregate"):
            steps = self.jobs[name]["steps"]
            checkout = [s for s in steps if s.get("uses", "").startswith("actions/checkout@")]
            self.assertEqual(len(checkout), 1)
            self.assertEqual(checkout[0]["with"], {"fetch-depth": 0, "persist-credentials": False})
            self.assertEqual(self.jobs[name]["runs-on"], "ubuntu-latest")
        for name in ("check", "candidate"):
            steps = {s["name"]: s for s in self.jobs[name]["steps"]}
            self.assertEqual(steps["Setup uv"], {"name": "Setup uv", "uses": "astral-sh/setup-uv@v5",
                                               "with": {"version": "0.12.22", "enable-cache": False}})
            sandbox = steps["Provision birth sandbox"]["run"]
            for required in ("sudo apt-get install --yes bubblewrap", "profile ci-bwrap /usr/bin/bwrap",
                             "sudo apparmor_parser -r /etc/apparmor.d/ci-bwrap",
                             "bwrap --die-with-parent --unshare-pid --unshare-ipc --unshare-uts",
                             "--ro-bind / / --dev /dev --proc /proc /usr/bin/true"):
                self.assertIn(required, sandbox)
            for bypass in ("sysctl", "systemctl stop", "--no-sandbox"):
                self.assertNotIn(bypass, sandbox)
            core = steps["Provision pinned ROCS core"]["run"]
            self.assertIn("https://github.com/tryingET/rocs-cli.git", core)
            self.assertEqual(core.count(ROCS), 2)
            self.assertIn('test "$(git -C "$core" rev-parse HEAD)" = ' + ROCS, core)
            self.assertIn('uv sync --project "$core" --frozen', core)
            self.assertIn('uv run --project "$core" --frozen rocs version', core)
        self.assertEqual(self.worker_steps["Provision pinned ROCS core"]["run"],
                         self.jobs["check"]["steps"][3]["run"])

    def test_cold_prewarm_is_exact_copier_before_offline_units(self):
        prewarm = self.worker_steps["Prewarm pinned outer Copier"]
        self.assertEqual(prewarm["env"], {"UV_NO_MANAGED_PYTHON": "1"})
        self.assertEqual(prewarm["run"].splitlines(), [
            'uvx --from copier==9.11.1 python -B -c \'import importlib.metadata as m; assert m.version("copier") == "9.11.1"\'',
            "python3 -B -c 'import yaml'"])
        self.assertNotIn("UV_OFFLINE", self.jobs["candidate"]["env"])
        names = list(self.worker_steps)
        self.assertLess(names.index(prewarm["name"]), names.index("Run slot 1"))
        self.assertEqual(self.source.count("uvx --from"), 1)
        self.assertNotIn("pip install", self.source)

    def test_private_fresh_roots_source_identity_and_run_scoped_download(self):
        prep = self.worker_steps["Prepare private worker output"]
        self.assertEqual(prep["id"], "prepare")
        for job in self.jobs.values():
            for value in job.get("env", {}).values():
                self.assertNotIn("runner.", str(value))
        self.assertEqual(self.jobs["candidate"]["env"], {
            "L0_CHECK_VERBOSE": "1", "PYTHONDONTWRITEBYTECODE": "1"})
        self.assertIn('printf \'TMPDIR=%s\\nROCS_CORE_PROJECT=%s/rocs-ci\\n\' "$RUNNER_TEMP" "$RUNNER_TEMP" >>"$GITHUB_ENV"', prep["run"])
        names = list(self.worker_steps)
        for name in ("Provision birth sandbox", "Provision pinned ROCS core", "Run slot 1"):
            self.assertLess(names.index(prep["name"]), names.index(name))
        self.assertIn('test "$(git rev-parse HEAD)" = "$GITHUB_SHA"', prep["run"])
        self.assertIn('mktemp -d "$RUNNER_TEMP/l0-candidate.XXXXXX"', prep["run"])
        self.assertIn('case "$root/" in "$GITHUB_WORKSPACE/"*) exit 1 ;; esac', prep["run"])
        self.assertIn('chmod 0700 "$root"', prep["run"])
        self.assertIn("umask 077", prep["run"])
        for slot in range(1, 10):
            run = self.worker_steps[f"Run slot {slot}"]
            self.assertEqual(run["env"], {"OUTPUT_ROOT": "${{ steps.prepare.outputs.root }}"})
            self.assertEqual(run["run"].splitlines()[:2], ["umask 077", f'mkdir -m 0700 "$OUTPUT_ROOT/slot{slot}"'])
        prep = self.aggregate_steps["Prepare private aggregate roots"]
        for required in ('test "$(git rev-parse HEAD)" = "$GITHUB_SHA"', "umask 077",
                         'mktemp -d "$RUNNER_TEMP/l0-incoming.XXXXXX"',
                         'mktemp -d "$RUNNER_TEMP/l0-aggregate.XXXXXX"', 'chmod 0700 "$inputs" "$out"',
                         'case "$inputs/" in "$GITHUB_WORKSPACE/"*) exit 1 ;; esac',
                         'case "$out/" in "$GITHUB_WORKSPACE/"*) exit 1 ;; esac',
                         "python3 -B -c 'import yaml'"):
            self.assertIn(required, prep["run"])
        download = self.aggregate_steps["Download this run and attempt only"]
        self.assertEqual(download["uses"], DOWNLOAD)
        self.assertEqual(download["with"], {
            "pattern": "l0-candidate-${{ github.run_id }}-${{ github.run_attempt }}-worker*-slot*",
            "merge-multiple": False, "path": "${{ steps.prepare.outputs.inputs }}"})

    def transport(self, inputs):
        step = self.aggregate_steps["Refuse unsafe transport then restore private modes"]
        self.assertEqual(step["env"], {"INPUTS": "${{ steps.prepare.outputs.inputs }}"})
        return subprocess.run(["bash", "-e", "-c", step["run"]], cwd=ROOT,
                              env=dict(os.environ, INPUTS=str(inputs)), text=True, capture_output=True, timeout=10)

    def test_download_modes_restore_without_changing_artifact_bytes(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as tmp:
            incoming = Path(tmp) / "incoming"
            profile = incoming / "artifact" / "profiles"
            profile.mkdir(parents=True)
            packet = profile / "unit.json"
            data = b'{"immutable":true}\n'
            packet.write_bytes(data)
            for path in (incoming, incoming / "artifact", profile):
                path.chmod(0o755)
            packet.chmod(0o644)
            before = hashlib.sha256(packet.read_bytes()).hexdigest()
            result = self.transport(incoming)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(hashlib.sha256(packet.read_bytes()).hexdigest(), before)
            self.assertEqual(packet.read_bytes(), data)
            self.assertEqual(stat.S_IMODE(packet.stat().st_mode), 0o600)
            for path in (incoming, incoming / "artifact", profile):
                self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o700)

    def test_transport_rejects_links_nonregular_and_multilink_before_any_chmod(self):
        script = self.aggregate_steps["Refuse unsafe transport then restore private modes"]["run"]
        self.assertIn("info.st_uid != os.getuid()", script)
        self.assertIn("path.lstat()", script)
        self.assertLess(script.index('raise ValueError("transport must contain'), script.index("os.chmod"))
        self.assertIn("follow_symlinks=False", script)
        for kind in ("file-link", "directory-link", "hardlink", "fifo", "root-link"):
            with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as tmp:
                root = Path(tmp)
                incoming = root / "incoming"
                incoming.mkdir()
                incoming.chmod(0o755)
                outside = root / "outside"
                outside.mkdir()
                outside.chmod(0o755)
                target = outside / "retained"
                target.write_bytes(b"untouched")
                target.chmod(0o644)
                bad = incoming / "bad"
                if kind == "file-link":
                    bad.symlink_to(target)
                elif kind == "directory-link":
                    bad.symlink_to(outside, target_is_directory=True)
                elif kind == "hardlink":
                    os.link(target, bad)
                elif kind == "fifo":
                    os.mkfifo(bad)
                else:
                    alias = root / "alias"
                    alias.symlink_to(incoming, target_is_directory=True)
                result = self.transport(alias if kind == "root-link" else incoming)
                self.assertNotEqual(result.returncode, 0, kind)
                self.assertEqual(stat.S_IMODE(incoming.stat().st_mode), 0o755, kind)
                self.assertEqual(stat.S_IMODE(target.stat().st_mode), 0o644, kind)
                self.assertEqual(target.read_bytes(), b"untouched", kind)
                self.assertEqual(stat.S_IMODE(outside.stat().st_mode), 0o755, kind)

    def test_aggregation_accepts_failed_worker_status_without_promoting_it(self):
        aggregate = self.jobs["aggregate"]
        self.assertEqual(aggregate["needs"], "candidate")
        self.assertEqual(aggregate["if"], "always() && !cancelled() && " + PREDICATE)
        step = self.aggregate_steps["Aggregate correlated unit evidence"]
        self.assertEqual(step["if"], "always() && !cancelled() && steps.transport.outcome == 'success' && steps.prepare.outputs.out != ''")
        self.assertEqual(step["env"], {"INPUTS": "${{ steps.prepare.outputs.inputs }}",
                                      "OUT": "${{ steps.prepare.outputs.out }}",
                                      "WORKER_RESULT": "${{ needs.candidate.result }}"})
        self.assertEqual(shlex.split(step["run"]), ["python3", "-B", "tests/ci_aggregate.py",
            "--inputs", "$INPUTS", "--out", "$OUT", "--source-sha", "$GITHUB_SHA",
            "--run-id", "$GITHUB_RUN_ID", "--attempt", "$GITHUB_RUN_ATTEMPT", "--worker-result", "$WORKER_RESULT"])
        for outcome in ("success", "failure", "skipped", "cancelled"):
            values = {"steps.transport.outcome": "success", "steps.prepare.outputs.out": "/private",
                      "needs.candidate.result": outcome}
            self.assertTrue(evaluate(step["if"], values, success=False))
            self.assertFalse(evaluate(step["if"], dict(values, **{"steps.transport.outcome": "failure"})))
        upload = self.aggregate_steps["Retain aggregate even on failure"]
        self.assertEqual(upload["if"], "always() && !cancelled() && steps.prepare.outputs.out != ''")
        self.assertEqual(upload["uses"], UPLOAD)
        self.assertEqual(upload["with"], {
            "name": "l0-candidate-aggregate-${{ github.run_id }}-${{ github.run_attempt }}",
            "path": "${{ steps.prepare.outputs.out }}/aggregate.json",
            "if-no-files-found": "error", "retention-days": 7})
        for forbidden in ("ci_worker.py", "-m unittest", "check-l0.sh", "performance_proven", "|| true"):
            self.assertNotIn(forbidden, str(aggregate))

    def test_exact_branch_fork_and_cancellation_pipeline_predicates(self):
        self.assertEqual(self.jobs["check"]["if"], "!" + PREDICATE)
        self.assertEqual(self.jobs["candidate"]["if"], PREDICATE)
        for event, ref, head, repo, cancelled, expected in (
            ("push", "refs/heads/" + BRANCH, "", "owner/repo", False, (False, True, True)),
            ("push", "refs/heads/main", BRANCH, "owner/repo", False, (True, False, False)),
            ("push", "refs/tags/" + BRANCH, BRANCH, "owner/repo", False, (True, False, False)),
            ("pull_request", "refs/pull/1/merge", BRANCH, "owner/repo", False, (False, True, True)),
            ("pull_request", "refs/pull/1/merge", BRANCH, "fork/repo", False, (True, False, False)),
            ("pull_request", "refs/pull/1/merge", "feature", "owner/repo", False, (True, False, False)),
            ("pull_request_target", "refs/heads/main", BRANCH, "owner/repo", False, (True, False, False)),
            ("push", "refs/heads/" + BRANCH, "", "owner/repo", True, (False, True, False))):
            values = {"github.event_name": event, "github.ref": ref, "github.head_ref": head,
                      "github.repository": "owner/repo", "github.event.pull_request.head.repo.full_name": repo}
            actual = tuple(evaluate(self.jobs[name]["if"], values, cancelled=cancelled)
                           for name in ("check", "candidate", "aggregate"))
            self.assertEqual(actual, expected, (event, ref, head, repo, cancelled))
        events = self.workflow.get("on", self.workflow.get(True))
        self.assertEqual(events, {"pull_request": None, "push": {"branches": ["main", BRANCH]}})

    def test_read_only_no_source_effects_secrets_or_timeout_inflation(self):
        self.assertEqual(self.workflow["permissions"], {"contents": "read"})
        for forbidden in ("secrets.", "GITHUB_TOKEN", "continue-on-error", "git push", "git commit",
                          "ak task", "gh pr", "permissions: write", "pull_request_target:",
                          "L0_CHECK_TIMEOUT", "L0_BIRTH_TIMEOUT", "persist-credentials: true"):
            self.assertNotIn(forbidden, self.source)
        for job in self.jobs.values():
            self.assertNotIn("permissions", job)
            self.assertNotIn("continue-on-error", job)
            for step in job["steps"]:
                self.assertNotIn("continue-on-error", step)
        self.assertEqual(self.source.count("timeout-minutes:"), 1)
        self.assertLess(len(self.source.splitlines()), 450)
        self.assertLess(len(self.source.encode()), 50_000)


if __name__ == "__main__":
    unittest.main()
