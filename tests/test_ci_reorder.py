"""Fast contracts for hosted observation; synthetic cohorts only, no rendering.

Run via ``uvx --from copier==9.11.1 python -B -m unittest tests.test_ci_reorder``.
The fixed-version generation-unit replay intentionally requires the same runtime
as its serial fixture; bare Python without Copier is not that condition.
"""
import copy
import errno
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

from tests import ci_reorder as observer

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "tests/ci_unittest.sh"
RUNNER = ROOT / "tests/ci_reorder.py"


def packet(ids=("sample.Cases.test_case",), arguments=("alpha", "beta")):
    return {
        "schema": "l0.unittest-profile/1", "cohort": "guardrails-main", "parent_cohort": None,
        "arguments": list(arguments), "collected_ids": list(ids), "tests_run": len(ids),
        "events": [{"kind": "test", "test_id": name, "outcome": "success", "subtests": [], "ordinal": ordinal}
                   for ordinal, name in enumerate(ids, 1)],
        "exit_code": 0, "successful": True, "result_successful": True,
        "python": "synthetic", "python_executable": sys.executable, "copier": "9.11.1",
        "source_commit": "synthetic", "source_dirty": [],
    }


def reversed_packet(before):
    after = copy.deepcopy(before)
    after["arguments"] = observer.reverse_arguments(before["arguments"])
    return after


class ReorderContractTests(unittest.TestCase):
    def test_only_selector_order_changes_and_unsupported_selection_is_refused(self):
        self.assertEqual(observer.reverse_arguments(["-v", "tests/a.py", "-b", "tests.beta.Cases"]),
                         ["-v", "tests.beta.Cases", "-b", "tests/a.py"])
        self.assertEqual(observer.reverse_arguments(["tests.upgrade.Cases"]), ["tests.upgrade.Cases"])
        for arguments in ([], ["-v"], ["discover", "-s", "tests"], ["-k", "case", "alpha"], [""]):
            with self.subTest(arguments=arguments), self.assertRaises(ValueError):
                observer.reverse_arguments(arguments)

    def test_collection_execution_and_outcome_counters_retain_multiplicity(self):
        before = packet(ids=("sample.test_duplicate",) * 2)
        after = reversed_packet(before)
        after["events"].reverse()
        self.assertTrue(observer.compare_packet(before, after)["exact_match"])
        after["collected_ids"].pop()
        after["events"].pop()
        difference = observer.compare_packet(before, after)["differences"]
        self.assertIn("collected_method_ids", difference)
        self.assertIn("executed_method_ids", difference)
        self.assertIn("method_ids_outcomes", difference)
        self.assertEqual(difference["collected_method_ids"]["serial_only"][0]["count"], 1)
        after = reversed_packet(before)
        after["events"][0]["outcome"] = "skip"
        self.assertIn("method_ids_outcomes", observer.compare_packet(before, after)["differences"])

    def test_raw_ephemeral_subtest_ids_are_not_normalized_or_excluded(self):
        before = packet()
        test_id = before["events"][0]["test_id"]
        before["events"][0]["subtests"] = [{"test_id": test_id + " (path='/scratch/one')", "outcome": "success"}]
        after = reversed_packet(before)
        after["events"][0]["subtests"][0]["test_id"] = test_id + " (path='/scratch/two')"
        result = observer.compare_packet(before, after)
        self.assertFalse(result["exact_match"])
        self.assertEqual(set(result["differences"]), {"raw_subtest_ids_outcomes"})
        self.assertIn("no normalization or exclusions", result["uncertainty"][0])
        self.assertIn("/scratch/one", str(result["differences"]))
        self.assertIn("/scratch/two", str(result["differences"]))

    def test_fixture_exit_runtime_parent_and_exact_arguments_are_checked(self):
        before = packet()
        before["events"].append({"kind": "fixture", "test_id": "setUpClass(sample.Cases)", "outcome": "error"})
        for key, value in (("exit_code", 5), ("parent_cohort", "different"), ("python", "different"),
                           ("copier", "different"), ("source_commit", "different"), ("arguments", ["beta"])):
            with self.subTest(key=key):
                after = reversed_packet(before)
                after[key] = value
                self.assertIn(key, observer.compare_packet(before, after)["differences"])
        after = reversed_packet(before)
        after["events"][-1]["outcome"] = "skip"
        self.assertIn("fixture_ids_outcomes", observer.compare_packet(before, after)["differences"])

    def test_nested_manifest_multiplicity_and_missing_dynamic_coverage_stay_visible(self):
        before = packet()
        child = packet(ids=("tests.test_l1_answer_template_upgrade.UpgradeTests.test_upgrade",), arguments=("upgrade",))
        child.update(cohort="generation-upgrade", parent_cohort="generation-main")
        serial = [("root.json", before), ("child.json", child), ("child2.json", child)]
        second = [("other.json", reversed_packet(before)), ("nested.json", reversed_packet(child))]
        result = observer.compare_manifests(serial, second, require_full=False)
        self.assertFalse(result["exact_match"])
        self.assertEqual(result["manifest_issues"][0]["serial_count"], 2)
        self.assertEqual(result["manifest_issues"][0]["parent_cohort"], "generation-main")
        result = observer.compare_manifests(serial, second)
        self.assertTrue(any("reverse_transitions" in issue.get("missing_collected_coverage", "")
                            for issue in result["manifest_issues"]))
        self.assertFalse(observer.compare_manifests([], [], require_full=False)["exact_match"])

    def test_generation_unit_cohort_cannot_be_omitted_from_both_full_conditions(self):
        serial = []
        for cohort, parent in sorted(observer.EXPECTED, key=lambda key: key[0]):
            ids = {
                "guardrails-main": ("tests.test_l1_template_reverse_transitions.ReverseTests.test_case",),
                "guardrails-generation-units": ("tests.test_ci_generation_units.GenerationSourceContracts.test_case",),
                "guardrails-ci-planning": ("tests.test_ci_coverage.IndependentCoverageTests.test_case",
                                           "tests.test_ci_schedule.ScheduleContractTests.test_case"),
                "generation-upgrade": ("tests.test_l1_answer_template_upgrade.UpgradeTests.test_case",),
            }.get(cohort, ("sample.Cases.test_case",))
            before = packet(ids=ids)
            before.update(cohort=cohort, parent_cohort=parent)
            serial.append((cohort + ".json", before))
        second = [(name, reversed_packet(before)) for name, before in serial]
        self.assertTrue(observer.compare_manifests(serial, second)["exact_match"])
        serial = [(name, before) for name, before in serial if before["cohort"] != "guardrails-generation-units"]
        second = [(name, before) for name, before in second if before["cohort"] != "guardrails-generation-units"]
        missing = observer.compare_manifests(serial, second)
        self.assertFalse(missing["exact_match"])
        self.assertTrue(any(issue.get("cohort") == "guardrails-generation-units"
                            for issue in missing["manifest_issues"]))
        self.assertTrue(any(issue.get("missing_collected_coverage") == "test_ci_generation_units."
                            for issue in missing["manifest_issues"]))

    def test_command_failure_retains_exact_output_exit_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as tmp:
            target = Path(tmp) / "command.json"
            command = [sys.executable, "-B", "-c", "import os; os.write(1, b'output\\xff\\n'); os.write(2, b'error\\n'); raise SystemExit(7)"]
            result = observer.capture(command, target)
            self.assertEqual(result["exit_code"], 7)
            self.assertEqual(target.with_suffix(".log").read_bytes(), b"output\xff\nerror\n")
            self.assertEqual(json.loads(target.read_text())["command"], command)
            self.assertEqual(target.stat().st_mode & 0o777, 0o600)
            self.assertEqual(target.with_suffix(".log").stat().st_mode & 0o777, 0o600)
            with self.assertRaises(ValueError):
                observer.capture(command, target)

    def test_identically_omitted_execution_is_not_exact_or_complete(self):
        before = packet(ids=("sample.Cases.test_one", "sample.Cases.test_two"))
        before["events"].pop()
        before["tests_run"] = 1
        result = observer.compare_packet(before, reversed_packet(before))
        self.assertFalse(result["exact_match"])
        self.assertEqual(result["differences"], {}, "cross-condition equality alone is insufficient")
        self.assertFalse(result["ledger_checks"]["serial"]["valid"])
        self.assertTrue(result["uncertainty"])
        self.assertFalse(observer.compare_manifests([("a.json", before)],
                         [("b.json", reversed_packet(before))], require_full=False)["exact_match"])

    def test_ledger_counts_identities_outcomes_and_exit_consistency_are_checked(self):
        mutations = [
            lambda p: p.update(tests_run=2),
            lambda p: p["events"][0].update(test_id="not.collected"),
            lambda p: p["events"][0].update(ordinal=2),
            lambda p: p["events"][0].update(outcome="unknown"),
            lambda p: p["events"][0].update(outcome="error"),
            lambda p: p.update(exit_code=1),
            lambda p: p.update(successful=False),
            lambda p: p.update(result_successful=False),
            lambda p: p["events"][0].update(subtests=[{"test_id": "other (x=1)", "outcome": "success"}]),
            lambda p: p["events"][0].update(subtests=[{"test_id": p["events"][0]["test_id"] + " (x=1)", "outcome": "error"}]),
            lambda p: p["events"][0].update(subtests=[None]),
        ]
        for index, mutate in enumerate(mutations):
            with self.subTest(index=index):
                before = packet()
                mutate(before)
                result = observer.compare_packet(before, reversed_packet(before))
                self.assertFalse(result["exact_match"])
                self.assertFalse(result["ledger_checks"]["serial"]["valid"])
        failed = packet()
        failed["events"][0]["outcome"] = "failure"
        failed.update(exit_code=1, successful=False, result_successful=False)
        self.assertTrue(observer.validate_ledger(failed)["valid"])
        for code in (0, 2, 5, 143):
            failed.update(exit_code=code, successful=code == 0)
            self.assertFalse(observer.validate_ledger(failed)["valid"])

    def test_legitimate_fixture_failure_skip_and_empty_suite_report_uncertainty(self):
        for outcome, code in (("error", 1), ("error", 5), ("skip", 0), ("skip", 5)):
            with self.subTest(outcome=outcome, code=code):
                before = packet()
                before.update(tests_run=0, exit_code=code, successful=code == 0, result_successful=outcome == "skip",
                              events=[{"kind": "fixture", "test_id": "setUpClass(sample.Cases)", "outcome": outcome}])
                result = observer.compare_packet(before, reversed_packet(before))
                self.assertFalse(result["exact_match"])
                self.assertTrue(result["ledger_checks"]["serial"]["valid"], result)
                self.assertFalse(result["ledger_checks"]["serial"]["coverage_complete"])
                self.assertEqual(result["differences"], {})
                self.assertTrue(result["uncertainty"])
        empty = packet(ids=())
        result = observer.compare_packet(empty, reversed_packet(empty))
        self.assertFalse(result["exact_match"])
        self.assertTrue(result["uncertainty"])

    def test_native_child_self_signals_have_shell_conventional_cli_status(self):
        for signum in (signal.SIGINT, signal.SIGTERM):
            with self.subTest(signum=signum), tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as tmp:
                target = Path(tmp) / "command.json"
                source = f"import os, signal; signal.signal({int(signum)}, signal.SIG_DFL); os.kill(os.getpid(), {int(signum)})"
                result = subprocess.run([sys.executable, "-B", str(RUNNER), "capture", "--out", str(target),
                                         "--", sys.executable, "-B", "-c", source], capture_output=True, timeout=4)
                self.assertEqual(result.returncode, 128 + signum, result.stderr)
                observed = json.loads(target.read_text())
                self.assertEqual(observed["raw_child_returncode"], -signum)
                self.assertEqual(observed["child_exit_code"], 128 + signum)
                self.assertIsNone(observed["interrupted_signal"])
                self.assertTrue(observed["teardown"]["process_group_gone"])

    def test_wrapper_interrupts_propagate_and_reap_descendants_with_bounded_escalation(self):
        for signum in (signal.SIGINT, signal.SIGTERM):
            for resistant in (False, True):
                with self.subTest(signum=signum, resistant=resistant), tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as tmp:
                    root = Path(tmp)
                    leaf = root / "leaf.py"
                    parent = root / "parent.py"
                    body = '''import os, signal, subprocess, sys, time
from pathlib import Path
root = Path(sys.argv[1])
role = sys.argv[2] if len(sys.argv) > 2 else 'leaf'
def receive(value, frame):
    (root / (role + '-signal')).write_text(str(value))
    if not RESISTANT: raise SystemExit(0)
for value in (signal.SIGINT, signal.SIGTERM): signal.signal(value, receive)
if role == 'leaf': subprocess.Popen([sys.executable, '-B', str(root / 'leaf.py'), str(root), 'grandchild'])
print(role + ' ready', flush=True)
(root / (role + '-pid')).write_text(str(os.getpid()))
while True: time.sleep(60)
'''.replace("RESISTANT", repr(resistant))
                    leaf.write_text(body)
                    parent.write_text('''import os, signal, subprocess, sys, time
from pathlib import Path
root = Path(sys.argv[1])
def receive(value, frame):
    (root / 'parent-signal').write_text(str(value))
    if not RESISTANT: raise SystemExit(128 + value)
for value in (signal.SIGINT, signal.SIGTERM): signal.signal(value, receive)
subprocess.Popen([sys.executable, '-B', str(root / 'leaf.py'), str(root)])
(root / 'parent-pid').write_text(str(os.getpid()))
while True: time.sleep(60)
'''.replace("RESISTANT", repr(resistant)))
                    target = root / "command.json"
                    wrapper = subprocess.Popen([sys.executable, "-B", str(RUNNER), "capture", "--out", str(target),
                                                "--", sys.executable, "-B", str(parent), str(root)],
                                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
                    try:
                        deadline = time.monotonic() + 4
                        names = ("parent-pid", "leaf-pid", "grandchild-pid")
                        while not all((root / name).exists() for name in names) and time.monotonic() < deadline and wrapper.poll() is None:
                            time.sleep(0.01)
                        self.assertTrue(all((root / name).exists() for name in names), "fixture never became ready")
                        pids = [int((root / name).read_text()) for name in names]
                        wrapper.send_signal(signum)
                        stdout, stderr = wrapper.communicate(timeout=4)
                        self.assertEqual(wrapper.returncode, 128 + signum, stderr)
                        observed = json.loads(target.read_text())
                        self.assertEqual(observed["interrupted_signal"], signum)
                        self.assertEqual(observed["exit_code"], 128 + signum)
                        self.assertEqual(observed["raw_child_returncode"], -signal.SIGKILL if resistant else 128 + signum)
                        self.assertEqual(observed["teardown"]["escalated"], resistant)
                        self.assertTrue(observed["teardown"]["process_group_gone"])
                        self.assertLess(observed["wall_seconds"], 3)
                        self.assertEqual((root / "parent-signal").read_text(), str(int(signum)))
                        self.assertEqual((root / "leaf-signal").read_text(), str(int(signum)))
                        self.assertEqual((root / "grandchild-signal").read_text(), str(int(signum)))
                        self.assertTrue(all(not Path(f"/proc/{pid}").exists() for pid in pids), "live or zombie fixture survived")
                        if resistant:
                            self.assertGreaterEqual(observed["teardown"]["descendants_reaped"], 2)
                        self.assertIn(b"leaf ready", target.with_suffix(".log").read_bytes())
                    finally:
                        if wrapper.poll() is None:
                            if (root / "parent-pid").exists():
                                try:
                                    os.killpg(int((root / "parent-pid").read_text()), signal.SIGKILL)
                                except ProcessLookupError:
                                    pass
                            wrapper.send_signal(signal.SIGTERM)
                            try:
                                wrapper.communicate(timeout=4)
                            except subprocess.TimeoutExpired:
                                wrapper.kill()
                                wrapper.communicate(timeout=4)

    def test_signal_handlers_are_restored_after_capture(self):
        handlers = {s: signal.getsignal(s) for s in (signal.SIGINT, signal.SIGTERM)}
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as tmp:
            observer.capture([sys.executable, "-B", "-c", "pass"], Path(tmp) / "command.json")
        self.assertEqual({s: signal.getsignal(s) for s in handlers}, handlers)

    def test_keyboard_interrupt_cleans_up_and_retains_evidence(self):
        select = observer.selectors.DefaultSelector.select
        interrupted = False

        def once(selector, timeout=None):
            nonlocal interrupted
            if not interrupted:
                interrupted = True
                raise KeyboardInterrupt()
            return select(selector, timeout)

        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as tmp:
            target = Path(tmp) / "command.json"
            with mock.patch.object(observer.selectors.DefaultSelector, "select", once):
                result = observer.capture([sys.executable, "-B", "-c", "import time; time.sleep(60)"], target)
            self.assertEqual(result["exit_code"], 130)
            self.assertTrue(result["teardown"]["process_group_gone"])
            self.assertEqual(json.loads(target.read_text())["interrupted_signal"], signal.SIGINT)

    def subreaper_setting(self):
        value = observer.ctypes.c_int()
        libc = observer.ctypes.CDLL(None, use_errno=True)
        self.assertEqual(libc.prctl(37, observer.ctypes.byref(value), 0, 0, 0), 0)
        return value.value

    def capture_io_fault(self, stage, *, fail_json=False):
        """Persistent failures, not a one-shot proxy; both fixture processes ignore TERM."""
        managed = observer.ci_process
        handlers = {s: signal.getsignal(s) for s in (signal.SIGINT, signal.SIGTERM)}
        subreaper = self.subreaper_setting()
        processes, logs, faults = [], [], []
        popen, read, opener = subprocess.Popen, os.read, observer.open_artifact
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as tmp:
            root = Path(tmp)
            source = root / "io-fixture.py"
            source.write_text('''import os, signal, subprocess, sys, time
from pathlib import Path
root = Path(sys.argv[1])
signal.signal(signal.SIGTERM, signal.SIG_IGN)
if len(sys.argv) > 2:
    (root / 'leaf-pid').write_text(str(os.getpid()))
else:
    subprocess.Popen([sys.executable, '-B', __file__, str(root), 'leaf'])
    (root / 'parent-pid').write_text(str(os.getpid()))
    while not (root / 'leaf-pid').exists(): time.sleep(0.005)
    print('IO fixture ready', flush=True)
while True: time.sleep(60)
''')

            def spawn(*args, **kwargs):
                process = popen(*args, **kwargs)
                processes.append(process)
                return process

            def failed_read(fd, count):
                if stage == "read" and processes and fd == processes[0].stdout.fileno():
                    faults.append("read")
                    raise OSError(errno.EIO, "persistent read failure")
                return read(fd, count)

            class LogProxy:
                def __init__(self, stream):
                    self.stream = stream
                    self.buffer = self

                def __enter__(self):
                    self.stream.__enter__()
                    return self

                def __exit__(self, *args):
                    return self.stream.__exit__(*args)

                def write(self, block):
                    if stage == "write":
                        faults.append("write")
                        raise OSError(errno.ENOSPC, "persistent log write failure")
                    return self.stream.buffer.write(block)

                def flush(self):
                    if stage == "flush":
                        faults.append("flush")
                        raise OSError(errno.ENOSPC, "persistent log flush failure")
                    return self.stream.buffer.flush()

            def artifacts(path):
                stream = opener(path)
                if Path(path).suffix == ".log":
                    logs.append(stream)
                    return LogProxy(stream)
                return stream

            target = root / "command.json"

            def failed_json(path, packet):
                self.assertTrue(packet["teardown"]["process_group_gone"])
                self.assertTrue(processes[0].stdout.closed)
                self.assertTrue(logs[0].closed)
                self.assertEqual(self.subreaper_setting(), subreaper)
                self.assertEqual({s: signal.getsignal(s) for s in handlers}, handlers)
                raise OSError(errno.ENOSPC, "JSON unavailable after cleanup")

            writer = mock.patch.object(observer, "write_json", side_effect=failed_json) if fail_json else mock.patch.object(
                observer, "write_json", wraps=observer.write_json)
            try:
                with mock.patch.object(managed.subprocess, "Popen", side_effect=spawn), mock.patch.object(
                        managed.os, "read", side_effect=failed_read), mock.patch.object(
                        observer, "open_artifact", side_effect=artifacts), writer:
                    command = [sys.executable, "-B", str(source), str(root)]
                    if fail_json:
                        with self.assertRaisesRegex(OSError, "JSON unavailable"):
                            observer.capture(command, target)
                        self.assertFalse(target.exists())
                    else:
                        result = observer.capture(command, target)
                        self.assertEqual(result["exit_code"], 1)
                        self.assertEqual(result["raw_child_returncode"], -signal.SIGKILL)
                        self.assertTrue(result["teardown"]["escalated"])
                        self.assertTrue(result["teardown"]["process_group_gone"])
                        self.assertGreaterEqual(result["teardown"]["descendants_reaped"], 1)
                        self.assertFalse(result["output_complete"])
                        self.assertEqual(json.loads(target.read_text())["io_errors"], result["io_errors"])
                        self.assertTrue(any(e["errno"] == (errno.EIO if stage == "read" else errno.ENOSPC)
                                            for e in result["io_errors"]))
                self.assertEqual(faults, [stage], "failed draining must be disabled, not retried forever")
                self.assertTrue(processes[0].stdout.closed)
                self.assertTrue(logs[0].closed)
                pids = [int((root / name).read_text()) for name in ("parent-pid", "leaf-pid")]
                self.assertTrue(all(not Path(f"/proc/{pid}").exists() for pid in pids), "live/zombie managed fixture")
            finally:
                for process in processes:
                    if process.poll() is None:
                        try:
                            os.killpg(process.pid, signal.SIGKILL)
                        except ProcessLookupError:
                            pass
                        process.wait(timeout=3)
                self.assertEqual(self.subreaper_setting(), subreaper)
                self.assertEqual({s: signal.getsignal(s) for s in handlers}, handlers)

    def test_persistent_read_log_write_and_flush_failures_do_not_block_cleanup(self):
        for stage in ("read", "write", "flush"):
            with self.subTest(stage=stage):
                self.capture_io_fault(stage)

    def test_json_failure_is_attempted_only_after_cleanup_and_global_restore(self):
        self.capture_io_fault("write", fail_json=True)

    def test_log_close_failure_still_attempts_json_after_cleanup(self):
        handlers = {s: signal.getsignal(s) for s in (signal.SIGINT, signal.SIGTERM)}
        subreaper = self.subreaper_setting()
        opener, popen = observer.open_artifact, subprocess.Popen
        processes = []

        class CloseFailure:
            def __init__(self, stream):
                self.stream = stream
                self.buffer = stream.buffer

            def __enter__(self):
                return self

            def __exit__(self, *args):
                self.stream.close()
                raise OSError(errno.ENOSPC, "log close failure")

        def artifacts(path):
            stream = opener(path)
            return CloseFailure(stream) if Path(path).suffix == ".log" else stream

        def spawn(*args, **kwargs):
            process = popen(*args, **kwargs)
            processes.append(process)
            return process

        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as tmp:
            target = Path(tmp) / "command.json"
            with mock.patch.object(observer, "open_artifact", side_effect=artifacts), mock.patch.object(
                    observer.ci_process.subprocess, "Popen", side_effect=spawn):
                result = observer.capture([sys.executable, "-B", "-c", "pass"], target)
            self.assertEqual(result["exit_code"], 1)
            self.assertTrue(result["teardown"]["process_group_gone"])
            self.assertTrue(processes[0].stdout.closed)
            self.assertEqual(json.loads(target.read_text())["io_errors"][0]["errno"], errno.ENOSPC)
            self.assertEqual(self.subreaper_setting(), subreaper)
            self.assertEqual({s: signal.getsignal(s) for s in handlers}, handlers)

    def test_teardown_disables_a_pump_that_keeps_raising(self):
        managed = observer.ci_process
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as tmp:
            ready = Path(tmp) / "ready"
            source = f"import signal,time; from pathlib import Path; signal.signal(signal.SIGTERM,signal.SIG_IGN); Path({str(ready)!r}).touch(); time.sleep(60)"
            process = subprocess.Popen([sys.executable, "-B", "-c", source], start_new_session=True)
            try:
                deadline = time.monotonic() + 3
                while not ready.exists() and time.monotonic() < deadline:
                    time.sleep(0.005)
                self.assertTrue(ready.exists())
                pump = mock.Mock(side_effect=OSError(errno.ENOSPC, "persistent teardown IO"))
                started = time.monotonic()
                result = observer.teardown(process, pump, signal.SIGTERM)
                self.assertLess(time.monotonic() - started, 2)
                self.assertTrue(result["escalated"])
                self.assertTrue(result["process_group_gone"])
                self.assertEqual(process.returncode, -signal.SIGKILL)
                self.assertEqual(pump.call_count, 1)
                self.assertEqual(result["drain_errors"][0]["errno"], errno.ENOSPC)
            finally:
                if process.poll() is None:
                    os.killpg(process.pid, signal.SIGKILL)
                process.wait(timeout=3)

    def test_final_drain_has_byte_iteration_and_time_caps(self):
        managed = observer.ci_process
        process = subprocess.Popen([sys.executable, "-B", "-c", "pass"], start_new_session=True)
        process.wait(timeout=3)
        for size, expected_limit in ((managed.READ_BYTES, "bytes"), (1, "iterations")):
            with self.subTest(limit=expected_limit):
                pump = mock.Mock()

                def bounded_fixture(_wait):
                    if pump.call_count > managed.FINAL_DRAIN_ITERATIONS + 1:
                        raise AssertionError("unbounded final-drain regression")
                    return size

                pump.side_effect = bounded_fixture
                started = time.monotonic()
                result = observer.teardown(process, pump, signal.SIGTERM)
                self.assertLess(time.monotonic() - started, 1)
                self.assertTrue(result["final_drain_limited"])
                self.assertLessEqual(result["final_drain_bytes"], managed.FINAL_DRAIN_BYTES)
                self.assertLessEqual(result["final_drain_iterations"], managed.FINAL_DRAIN_ITERATIONS)
                self.assertEqual(pump.call_count, managed.FINAL_DRAIN_BYTES // size if size > 1 else managed.FINAL_DRAIN_ITERATIONS)
        ticks = iter((0.0, 0.0, managed.FINAL_DRAIN_SECONDS + 1))
        pump = mock.Mock(return_value=1)
        with mock.patch.object(managed.time, "perf_counter", side_effect=lambda: next(ticks, 2.0)):
            result = observer.teardown(process, pump, signal.SIGTERM)
        self.assertTrue(result["final_drain_limited"])
        self.assertEqual(pump.call_count, 1)

    def test_escaped_session_writer_cannot_keep_capture_draining_forever(self):
        managed = observer.ci_process

        class Quiet:
            def write(self, text):
                return len(text)

            def flush(self):
                pass

        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as tmp, observer.adopt_descendants():
            root = Path(tmp)
            escaped_pid = root / "escaped-pid"
            escaped_source = (f"import os; from pathlib import Path; Path({str(escaped_pid)!r}).write_text(str(os.getpid())); "
                              "\nwhile True: os.write(1, b'x' * 65536)\n")
            source = ("import subprocess,sys,time; from pathlib import Path; "
                      f"subprocess.Popen([sys.executable, '-B', '-c', {escaped_source!r}], start_new_session=True); "
                      f"\nwhile not Path({str(escaped_pid)!r}).exists(): time.sleep(0.001)\n")
            escaped = None
            try:
                started = time.monotonic()
                with mock.patch.object(managed.sys, "stdout", Quiet()):
                    result = observer.capture([sys.executable, "-B", "-c", source], root / "command.json")
                self.assertLess(time.monotonic() - started, 2)
                escaped = int(escaped_pid.read_text())
                self.assertTrue(result["teardown"]["process_group_gone"])
                self.assertLessEqual(result["teardown"]["final_drain_bytes"], managed.FINAL_DRAIN_BYTES)
                self.assertLessEqual(result["teardown"]["final_drain_iterations"], managed.FINAL_DRAIN_ITERATIONS)
                self.assertFalse(result["output_complete"], "escaped session output is not a complete oracle")
                self.assertEqual(result["exit_code"], 1)
            finally:
                # The helper deliberately does not manage setsid escapes. This test
                # owns/adopts this exact PID and performs its own fixture cleanup.
                if escaped is None and escaped_pid.exists():
                    escaped = int(escaped_pid.read_text())
                if escaped is not None:
                    try:
                        os.kill(escaped, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    os.waitpid(escaped, 0)

    def test_process_extraction_preserves_api_and_repository_root(self):
        self.assertEqual(observer.ROOT, observer.ci_process.ROOT)
        self.assertIs(observer.teardown, observer.ci_process.teardown)
        self.assertIs(observer.adopt_descendants, observer.ci_process.adopt_descendants)
        self.assertEqual(observer.shell_status(-signal.SIGTERM), 143)

    def test_reorder_stops_after_interrupted_capture_but_retains_summary(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as tmp:
            serial, second, scratch = [Path(tmp) / name for name in ("serial", "second", "scratch")]
            for directory in (serial, second, scratch):
                directory.mkdir(mode=0o700)
            for index, cohort in enumerate(("guardrails-main", "guardrails-system4d")):
                before = packet()
                before["cohort"] = cohort
                observer.write_json(serial / f"{index}.json", before)
            interrupted = {"interrupted_signal": signal.SIGTERM, "exit_code": 143}
            with mock.patch.object(observer, "capture", return_value=interrupted) as capture:
                self.assertEqual(observer.reorder(serial, second, scratch), 143)
                self.assertEqual(capture.call_count, 1)
            summary = json.loads((second / "comparison.json").read_text())
            self.assertEqual(summary["interrupted_signal"], signal.SIGTERM)
            self.assertFalse(summary["exact_match"])

    def test_private_fresh_disjoint_directory_preflight(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as tmp:
            root = Path(tmp)
            public = root / "public"
            public.mkdir()
            public.chmod(0o755)
            with self.assertRaises(ValueError):
                observer.private_directory(public)
            alias = root / "alias"
            alias.symlink_to(root, target_is_directory=True)
            with self.assertRaises(ValueError):
                observer.private_directory(alias)
            with self.assertRaises(ValueError):
                observer.private_directory(ROOT)
            retained = root / "retained"
            retained.mkdir(mode=0o700)
            (retained / "old.json").write_text("retained")
            with self.assertRaises(ValueError):
                observer.private_directory(retained, fresh=True)
            serial, second, scratch = [root / name for name in ("serial", "second", "scratch")]
            for directory in (serial, second, scratch):
                directory.mkdir(mode=0o700)
            with self.assertRaises(ValueError):
                observer.reorder(serial, second, serial)
            self.assertEqual(list(second.iterdir()), [])

    def test_replay_budgets_match_existing_lane_defaults_and_overrides(self):
        keys = ("L0_CHECK_TIMEOUT_SECONDS", "L0_CHECK_TIMEOUT_GENERATION_SECONDS")
        env = {k: v for k, v in os.environ.items() if k not in keys}
        with mock.patch.dict(os.environ, env, clear=True):
            self.assertEqual(observer.cohort_timeout("guardrails-main"), 1800)
            self.assertEqual(observer.cohort_timeout("generation-main"), 3600)
            os.environ["L0_CHECK_TIMEOUT_SECONDS"] = "123"
            self.assertEqual(observer.cohort_timeout("generation-main"), 246)
            os.environ["L0_CHECK_TIMEOUT_GENERATION_SECONDS"] = "321"
            self.assertEqual(observer.cohort_timeout("generation-main"), 321)

    def test_synthetic_replay_uses_recorded_arguments_and_preserves_dynamic_nested_cohorts(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as tmp:
            root = Path(tmp)
            serial, second, scratch = [root / name for name in ("serial", "second", "scratch")]
            for directory in (serial, second, scratch):
                directory.mkdir(mode=0o700)
            (root / "alpha.py").write_text('''import unittest
class Cases(unittest.TestCase):
    def test_duplicate(self): pass
class Dynamic(unittest.TestCase):
    def id(self): return 'tests.test_l1_template_reverse_transitions.ReverseTransitionTests.test_dynamic'
    def test_dynamic(self): pass
def load_tests(loader, suite, pattern):
    return unittest.TestSuite([Cases('test_duplicate'), Cases('test_duplicate'), Dynamic('test_dynamic')])
''')
            (root / "beta.py").write_text('''import unittest
class Cases(unittest.TestCase):
    def test_subtests(self):
        with self.subTest(case='pass'): pass
        with self.subTest(case='skip'): self.skipTest('synthetic')
''')
            (root / "upgrade.py").write_text('''import unittest
class Upgrade(unittest.TestCase):
    def id(self): return 'tests.test_l1_answer_template_upgrade.UpgradeTests.test_upgrade'
    def test_upgrade(self): pass
''')
            (root / "owner.py").write_text(f'''import subprocess, sys, unittest
class Owner(unittest.TestCase):
    def test_nested(self):
        subprocess.run(['sh', {str(HELPER)!r}, 'generation-upgrade', sys.executable, 'upgrade'], check=True)
''')
            (root / "tail.py").write_text("import unittest\nclass Tail(unittest.TestCase):\n    def test_tail(self): pass\n")
            (root / "context.py").write_text("import unittest\nclass Context(unittest.TestCase):\n    def test_context(self): pass\n")
            (root / "units.py").write_text('''import unittest
class Units(unittest.TestCase):
    def id(self): return 'tests.test_ci_generation_units.GenerationSourceContracts.test_synthetic'
    def test_synthetic(self): pass
''')
            (root / "planning.py").write_text('''import unittest
class Planning(unittest.TestCase):
    def id(self):
        module = 'test_ci_coverage.IndependentCoverageTests' if self._testMethodName == 'test_coverage' else 'test_ci_schedule.ScheduleContractTests'
        return 'tests.' + module + '.test_synthetic'
    def test_coverage(self): pass
    def test_schedule(self): pass
''')
            env = {k: v for k, v in os.environ.items() if not k.startswith("L0_PROFILE_")}
            env.update(PYTHONPATH=str(root), L0_PROFILE_DIR=str(serial), L0_PROFILE_CONDITION="serial",
                       PYTHONDONTWRITEBYTECODE="1", UV_OFFLINE="1")
            for cohort, arguments in (("guardrails-main", ["alpha", "beta"]),
                                      ("guardrails-generation-units", ["units"]),
                                      ("guardrails-ci-planning", ["planning"]),
                                      ("guardrails-system4d", ["context"]), ("generation-main", ["owner", "tail"])):
                result = subprocess.run(["sh", str(HELPER), cohort, sys.executable, *arguments],
                                        cwd=ROOT, env=env, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            env.pop("L0_PROFILE_DIR")
            result = subprocess.run([sys.executable, "-B", str(RUNNER), "reorder", "--serial-dir", str(serial),
                                     "--out-dir", str(second), "--tmpdir", str(scratch)],
                                    cwd=ROOT, env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            summary = json.loads((second / "comparison.json").read_text())
            self.assertTrue(summary["exact_match"])
            self.assertEqual(len(summary["comparisons"]), 6)
            self.assertEqual(len(summary["commands"]), 5, "nested upgrade must not be replayed separately")
            self.assertEqual([c["command"][c["command"].index(str(HELPER)) + 1] for c in summary["commands"]],
                             ["guardrails-main", "guardrails-generation-units", "guardrails-ci-planning", "guardrails-system4d", "generation-main"])
            unit_command = summary["commands"][1]["command"]
            self.assertEqual(unit_command[unit_command.index(str(HELPER)) + 2], "pinned-9.11.1")
            serial_main = next(p for _, p in observer.profiles(serial) if p["cohort"] == "guardrails-main")
            first = summary["commands"][0]["command"]
            self.assertEqual(first[first.index(str(HELPER)) + 2],
                             "pinned" if serial_main["copier"] else sys.executable)
            self.assertEqual([c["tmpdir"] for c in summary["commands"]], [str(scratch)] * 5)
            reports = observer.profiles(second)
            nested = [p for _, p in reports if p["cohort"] == "generation-upgrade"]
            self.assertEqual(len(nested), 1)
            self.assertEqual(nested[0]["parent_cohort"], "generation-main")
            reverse = next(p for _, p in reports if p["cohort"] == "guardrails-main")
            self.assertEqual(reverse["arguments"], ["beta", "alpha"])
            self.assertEqual(reverse["collected_ids"].count("alpha.Cases.test_duplicate"), 2)
            self.assertFalse(summary["stable_oracle_proven"])
            self.assertFalse(summary["cold_workflow_15min_proven"])
            for comparison in summary["comparisons"]:
                self.assertTrue((serial / comparison["serial_report"]).is_file())
                self.assertTrue((second / comparison["second_report"]).is_file())

    def test_empty_or_incomplete_serial_evidence_cannot_be_green(self):
        with tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR")) as tmp:
            directories = [Path(tmp) / name for name in ("serial", "second", "scratch")]
            for directory in directories:
                directory.mkdir(mode=0o700)
            self.assertEqual(observer.reorder(*directories), 1)
            summary = json.loads((directories[1] / "comparison.json").read_text())
            self.assertFalse(summary["exact_match"])
            self.assertTrue(summary["manifest_issues"])
            self.assertEqual(summary["commands"], [])


if __name__ == "__main__":
    unittest.main()
