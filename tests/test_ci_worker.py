"""Fast synthetic contracts only; no product cohort is launched here."""
import copy
import json
import os
from pathlib import Path
import signal
import sys
import tempfile
import time
import unittest
from unittest import mock

from tests import ci_worker as worker

SHA = "1" * 40


def synthetic_capture(row):
    return {"schema": "l0.profile-command/1", "command": row["command"],
            "exit_code": 0, "child_exit_code": 0, "raw_child_returncode": 0,
            "interrupted_signal": None, "output_complete": True, "io_errors": [], "error": None,
            "teardown": {"process_group_gone": True, "final_drain_limited": False, "drain_errors": []},
            "timed_out": False, "timeout_seconds": worker.budget(row), "wall_seconds": 0.125,
            "condition": "candidate", "log": "capture.command.log"}


def synthetic_profiles(row, inventory):
    packets = []
    groups = [] if row["kind"] == "shell" else [(row["cohort"], None, row["methods"], row["selectors"])]
    groups += [(child["cohort"], child["parent_cohort"], child["methods"], ["nested-parent-only"])
               for child in row["nested"]]
    for cohort, parent, methods, selectors in groups:
        frozen = next(c for c in inventory["cohorts"] if (c["cohort"], c["parent_cohort"]) == (cohort, parent))
        by_method = {m["id"]: m for m in frozen["methods"]}
        packets.append({"schema": "l0.unittest-profile/1", "cohort": cohort, "parent_cohort": parent,
                        "condition": "candidate", "source_commit": SHA, "source_dirty": [],
                        "arguments": selectors, "collected_ids": methods[:], "tests_run": len(methods),
                        "exit_code": 0, "successful": True, "result_successful": True,
                        "events": [{"kind": "test", "test_id": method, "outcome": "success", "ordinal": n,
                                    "subtests": [{"test_id": method + suffix, "outcome": outcome}
                                                 for suffix, outcome in by_method[method]["subtests"]]}
                                   for n, method in enumerate(methods, 1)]})
    return packets


def write_synthetic_unit(out, row, inventory, plan_hash, inventory_hash):
    out.mkdir(mode=0o700)
    worker.initialize_profiles(out / "profiles")
    capture = synthetic_capture(row)
    worker.write_json(out / "capture.command.json", capture)
    with worker.open_artifact(out / "capture.command.log") as stream:
        stream.write("synthetic only\n")
    for n, packet in enumerate(synthetic_profiles(row, inventory)):
        worker.write_json(out / "profiles" / f"profile-{n}.json", packet)
    packet = {"schema": "l0.candidate-unit/1", "worker": row["worker"], "slot": row["order"],
              "unit": row["unit"], "run_id": 7, "attempt": 2, "source_commit": SHA, "source_dirty": [],
              "plan_sha256": plan_hash, "inventory_sha256": inventory_hash,
              "canonicalcommand": row["command"], "capture_filename": "capture.command.json",
              "capture": worker.file_index(out / "capture.command.json", "capture.command.json"),
              "log": worker.file_index(out / "capture.command.log", "capture.command.log"),
              "profiles": worker.profile_files(out / "profiles"), "exit_code": 0, "status": "success",
              "errors": [], **worker.FLAGS}
    worker.write_json(out / "unit.json", packet)
    return packet


class WorkerContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR"))
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.plan, self.inventory, self.ph, self.ih = worker.frozen_contract()
        self.rows = worker.assignments(self.plan, self.inventory)

    def fresh(self, name="out"):
        path = self.root / name
        path.mkdir(mode=0o700)
        return path

    def test_invalid_deadlines_refuse_before_launch_or_artifact_creation(self):
        for value in (0, -1, True, False, float("nan"), float("inf"), "1", [], 10 ** 500):
            with mock.patch.object(worker.ci_process.subprocess, "Popen") as spawn:
                with self.assertRaises(ValueError):
                    worker.ci_process.capture(["must-not-launch"], self.root / "capture.json", timeout_seconds=value)
                spawn.assert_not_called()
        self.assertEqual(list(self.root.iterdir()), [])

    def test_timeout_keeps_exact_command_and_kills_resistant_orphan_group(self):
        pids = self.root / "pids"
        source = ("import os,signal,time; from pathlib import Path; "
                  "signal.signal(signal.SIGTERM,signal.SIG_IGN); child=os.fork(); "
                  f"Path({str(pids)!r}+str(child==0)).write_text(str(os.getpid())); "
                  "print('partial',flush=True); time.sleep(10); print('finished',flush=True)")
        command = [sys.executable, "-B", "-c", source]
        handlers = {s: signal.getsignal(s) for s in (signal.SIGINT, signal.SIGTERM)}
        result = worker.ci_process.capture(command, self.root / "capture.json", timeout_seconds=0.3)
        self.assertEqual(result["command"], command)
        self.assertEqual(result["exit_code"], 124)
        self.assertTrue(result["timed_out"])
        self.assertTrue(result["teardown"]["process_group_gone"])
        self.assertTrue(result["teardown"]["escalated"])
        self.assertGreaterEqual(result["teardown"]["descendants_reaped"], 1)
        self.assertLess(result["wall_seconds"], 2)
        for suffix in ("True", "False"):
            self.assertFalse(Path("/proc/" + Path(str(pids) + suffix).read_text()).exists())
        self.assertIn("partial", (self.root / "capture.log").read_text())
        self.assertNotIn("finished", (self.root / "capture.log").read_text())
        self.assertIn("deadline", result["error"])
        self.assertEqual({s: signal.getsignal(s) for s in handlers}, handlers)

    def test_deadline_capture_cancellation_restores_signals_and_reaps(self):
        pump = worker.ci_process.Drain.pump
        calls = 0
        def cancel(drain, wait, **kwargs):
            nonlocal calls
            calls += 1
            if calls == 1:
                raise KeyboardInterrupt()
            return pump(drain, wait, **kwargs)
        with mock.patch.object(worker.ci_process.Drain, "pump", cancel):
            packet = worker.ci_process.capture([sys.executable, "-B", "-c", "import time; time.sleep(10)"],
                                               self.root / "capture.json", timeout_seconds=1)
        self.assertEqual(packet["exit_code"], 130)
        self.assertFalse(packet["timed_out"])
        self.assertTrue(packet["teardown"]["process_group_gone"])

    def test_default_capture_preserves_old_packet_exit_and_no_deadline_fields(self):
        packet = worker.ci_process.capture([sys.executable, "-B", "-c", "print('ok'); raise SystemExit(7)"],
                                           self.root / "capture.json")
        self.assertEqual(packet["exit_code"], 7)
        self.assertTrue(packet["output_complete"])
        self.assertNotIn("timed_out", packet)
        self.assertNotIn("timeout_seconds", packet)

    def test_descriptors_refuse_invalid_schedule_unknown_slot_and_unimplemented_route(self):
        for worker_id, slot in ((True, 1), (0, 1), (7, 1), (1, 0), (1, 99)):
            with self.assertRaises(ValueError):
                worker.descriptor(self.plan, self.inventory, worker_id, slot)
        static = next((key for key, row in self.rows.items() if row["unit"] == "guardrails-static"), None)
        self.assertIsNotNone(static)
        self.assertEqual(self.rows[static]["route"], "planned")
        bad_route = copy.deepcopy(self.plan)
        next(r for r in bad_route["units"] if r["unit"] == "guardrails-static")["route"] = "unimplemented"
        with self.assertRaisesRegex(ValueError, "route"):
            worker.descriptor(bad_route, self.inventory, *static)
        with mock.patch.object(Path, "is_file", return_value=False), \
                self.assertRaisesRegex(ValueError, "entrypoint"):
            worker.descriptor(self.plan, self.inventory, *static)
        bad = copy.deepcopy(self.plan)
        bad["units"][0]["command"] = ["sh", "arbitrary.sh"]
        with self.assertRaises(ValueError):
            worker.descriptor(bad, self.inventory, 1, 1)
        key = next(key for key, row in self.rows.items() if row["unit"] == "doc-references")
        with mock.patch.object(Path, "is_file", return_value=False), self.assertRaises(ValueError):
            worker.descriptor(self.plan, self.inventory, *key)

    def test_environment_preserves_cohort_context_pinned_rocs_and_finite_budgets(self):
        ambient = {"GIT_DIR": "/wrong", "GIT_CONFIG_COUNT": "2", "AK_CMD": "live-ak",
                   "L0_PROFILE_PARENT": "wrong", "L0_PROFILE_COHORT": "wrong",
                   "L0_TEMPLATE_ROOT": "/wrong", "ROCS_CORE_PROJECT": "/public-pin"}
        with mock.patch.dict(os.environ, ambient):
            for row in self.rows.values():
                env = worker.unit_env(row, self.root, self.root / "tmp")
                self.assertNotIn("GIT_DIR", env)
                self.assertNotIn("GIT_CONFIG_COUNT", env)
                self.assertNotIn("AK_CMD", env)
                self.assertNotIn("L0_PROFILE_PARENT", env)
                self.assertNotIn("L0_PROFILE_COHORT", env)
                self.assertEqual(env["ROCS_CORE_PROJECT"], "/public-pin")
                self.assertEqual(env["UV_OFFLINE"], "1")
                self.assertEqual("L0_TEMPLATE_ROOT" in env, worker.budget(row) == 3600)
                self.assertIn(worker.budget(row), (1800, 3600))

    def mock_execute(self, after=None, capture_error=None):
        key = next(key for key, row in self.rows.items() if row["unit"] == "doc-references")
        row = self.rows[key]
        out = self.fresh()
        calls = []
        def capture(command, target, **kwargs):
            current = os.umask(0o022)
            os.umask(current)
            self.assertEqual(current, 0o022)
            self.assertEqual(command, row["command"])
            self.assertEqual(kwargs["timeout_seconds"], 1800)
            self.assertTrue(Path(kwargs["env"]["TMPDIR"]).is_relative_to(out))
            calls.append(command)
            if capture_error:
                raise capture_error
            packet = synthetic_capture(row)
            worker.write_json(target, packet)
            with worker.open_artifact(target.with_suffix(".log")) as stream:
                stream.write("synthetic\n")
            return packet
        states = [(SHA, [])] + ([after] if after else [(SHA, [])])
        with mock.patch.object(worker, "source_state", side_effect=states) as state, mock.patch.object(
                worker.ci_process, "capture", side_effect=capture):
            packet = worker.execute(*key, out, SHA, 7, 2)
        self.assertEqual(state.call_count, 2)
        self.assertEqual(len(calls), 1)
        self.assertFalse(any(p.name.startswith("tmp-") for p in out.iterdir()))
        return out, packet

    def test_one_slot_preserves_command_receipt_private_io_and_restores_api_umask(self):
        old = os.umask(0o077)
        try:
            out, packet = self.mock_execute()
            restored = os.umask(0o077)
            self.assertEqual(restored, 0o077)
            self.assertEqual(packet["status"], "success")
            self.assertEqual(packet["capture_filename"], "capture.command.json")
            self.assertEqual(json.loads((out / "capture.command.json").read_text())["command"],
                             packet["canonicalcommand"])
            for name in ("unit.json", "capture.command.json", "capture.command.log"):
                self.assertEqual((out / name).stat().st_mode & 0o777, 0o600)
            marker = out / "profiles" / worker.CONTAINER_MARKER
            self.assertEqual(marker.read_bytes(), worker.CONTAINER_BYTES)
            self.assertEqual(marker.stat().st_mode & 0o777, 0o600)
            self.assertEqual(packet["profiles"], [worker.file_index(marker, worker.CONTAINER_MARKER)])
            with self.assertRaises(FileExistsError):
                worker.initialize_profiles(out / "profiles")
            with self.assertRaises(FileExistsError):
                with worker.open_artifact(marker):
                    self.fail("retained marker overwritten")
            self.assertTrue(all(packet[k] is False for k in worker.FLAGS))
        finally:
            os.umask(old)

    def test_dirty_after_execution_keeps_unit_red_and_no_clean_source_claim(self):
        _, packet = self.mock_execute(after=ValueError("source dirty after"))
        self.assertEqual(packet["status"], "failure")
        self.assertNotEqual(packet["exit_code"], 0)
        self.assertIsNone(packet["source_dirty"])

    def test_capture_io_failure_still_checks_after_source_and_emits_failure(self):
        out, packet = self.mock_execute(capture_error=OSError("synthetic IO failure"))
        self.assertEqual(packet["status"], "failure")
        self.assertTrue((out / "unit.json").exists())

    def test_source_queries_are_read_only_sanitized_and_mismatch_dirty_refuse(self):
        answers = [mock.Mock(stdout=SHA + "\n"), mock.Mock(stdout="")]
        with mock.patch.object(worker.subprocess, "run", side_effect=answers) as query:
            self.assertEqual(worker.source_state(SHA), (SHA, []))
            self.assertEqual(query.call_count, 2)
            self.assertTrue(all("GIT_DIR" not in c.kwargs["env"] for c in query.call_args_list))
            self.assertIn("rev-parse", query.call_args_list[0].args[0])
            self.assertIn("status", query.call_args_list[1].args[0])
        with mock.patch.object(worker.subprocess, "run", side_effect=[mock.Mock(stdout=SHA), mock.Mock(stdout=" M file")]):
            with self.assertRaises(ValueError):
                worker.source_state(SHA)
        with mock.patch.object(worker, "source_state", side_effect=ValueError("HEAD mismatch")), mock.patch.object(
                worker.ci_process, "capture") as capture:
            with self.assertRaises(ValueError):
                worker.execute(1, 1, self.fresh(), SHA, 7, 2)
            capture.assert_not_called()

    def test_output_refuses_source_symlinks_public_retained_and_linked_files(self):
        for value in (worker.ROOT, self.root / "missing"):
            with self.assertRaises(ValueError):
                worker.private_dir(value, fresh=True)
        public = self.fresh("public")
        public.chmod(0o755)
        with self.assertRaises(ValueError):
            worker.private_dir(public)
        alias = self.root / "alias"
        alias.symlink_to(self.root, target_is_directory=True)
        with self.assertRaises(ValueError):
            worker.private_dir(alias)
        worker.write_json(self.root / "retained.json", {})
        with self.assertRaises(ValueError):
            worker.private_dir(self.root, fresh=True)
        os.link(self.root / "retained.json", self.root / "linked.json")
        with self.assertRaises(ValueError):
            worker.read_bytes(self.root / "linked.json", 100)

    def test_expected_profiles_are_descriptor_frozen_nested_raw_and_exact(self):
        row = next(r for r in self.rows.values() if r["unit"] == "UPG")
        packets = synthetic_profiles(row, self.inventory)
        worker.validate_profiles(row, self.inventory, packets, SHA)
        bad = copy.deepcopy(packets)
        bad[-1]["parent_cohort"] = None
        with self.assertRaises(ValueError):
            worker.validate_profiles(row, self.inventory, bad, SHA)
        bad = copy.deepcopy(packets)
        bad[0]["collected_ids"] = []
        with self.assertRaises(ValueError):
            worker.validate_profiles(row, self.inventory, bad, SHA)
        bad = copy.deepcopy(packets)
        bad[0]["events"][0]["subtests"].append({
            "test_id": bad[0]["events"][0]["test_id"] + " (forged=1)", "outcome": "success"})
        with self.assertRaisesRegex(ValueError, "RAW subtests"):
            worker.validate_profiles(row, self.inventory, bad, SHA)
        bad = copy.deepcopy(packets)
        bad[0]["source_dirty"] = ["dirty"]
        with self.assertRaises(ValueError):
            worker.validate_profiles(row, self.inventory, bad, SHA)
        parent = copy.deepcopy(row)
        parent["nested"] = []
        with self.assertRaises(ValueError):
            worker.validate_profiles(parent, self.inventory, packets, SHA)


if __name__ == "__main__":
    unittest.main()
