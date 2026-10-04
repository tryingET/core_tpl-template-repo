"""Synthetic aggregation only: accepted records never prove real execution.

The source schedule has planned static routing. All records here are synthetic;
test_real_unavailable_route_remains_red explicitly tampers the descriptor route.
"""
import copy
import io
import json
import os
from pathlib import Path
import shutil
import stat
import tempfile
import zipfile
import unittest
from unittest import mock

from tests import ci_aggregate as aggregate
from tests.test_ci_worker import SHA, write_synthetic_unit

worker = aggregate.worker


class AggregateContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=os.environ.get("TMPDIR"))
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.plan, self.inventory, self.ph, self.ih = worker.frozen_contract()
        self.real_rows = worker.assignments(self.plan, self.inventory)
        self.rows = copy.deepcopy(self.real_rows)
        self.inputs = self.root / "inputs"
        self.inputs.mkdir(mode=0o700)
        self.paths = {}
        for key, row in self.rows.items():
            path = self.inputs / f"worker-{key[0]}-slot-{key[1]}"
            write_synthetic_unit(path, row, self.inventory, self.ph, self.ih)
            self.paths[key] = path
        self.counter = 0

    def run_aggregate(self, result="success", real=False, source_error=None):
        self.counter += 1
        out = self.root / f"out-{self.counter}"
        out.mkdir(mode=0o700)
        with mock.patch.object(worker, "source_state", side_effect=source_error,
                               return_value=(SHA, [])), mock.patch.object(
                worker, "assignments", return_value=self.real_rows if real else self.rows):
            packet = aggregate.aggregate(self.inputs, out, SHA, 7, 2, result)
        self.assertEqual(json.loads((out / "aggregate.json").read_text()), packet)
        self.assertEqual((out / "aggregate.json").stat().st_mode & 0o777, 0o600)
        return packet

    def rewrite(self, path, packet):
        # Test-owned data only. Production writer never overwrites retained IO.
        path.write_text(json.dumps(packet, allow_nan=False))
        path.chmod(0o600)

    def unit(self, path):
        return json.loads((path / "unit.json").read_text())

    def edit_profile(self, path, mutate):
        unit = self.unit(path)
        entry = next(e for e in unit["profiles"] if e["filename"].endswith(".json"))
        file = path / "profiles" / entry["filename"]
        packet = json.loads(file.read_text())
        mutate(packet)
        self.rewrite(file, packet)
        entry["sha256"] = worker.sha256(file.read_bytes())
        self.rewrite(path / "unit.json", unit)

    def assert_red(self, packet, needle=None):
        self.assertFalse(packet["valid"], packet)
        self.assertTrue(packet["errors"])
        if needle:
            self.assertIn(needle, str(packet["errors"]))
        self.assertTrue(all(packet[k] is False for k in worker.FLAGS))

    def test_complete_synthetic_slots_exact_coverage_duration_sum_no_auth_or_timing_promotion(self):
        packet = self.run_aggregate()
        self.assertTrue(packet["valid"], packet["errors"])
        self.assertTrue(packet["coverage_valid"])
        self.assertEqual(packet["expected_slots"], len(self.rows))
        self.assertEqual(len(packet["units"]), len(self.rows))
        self.assertEqual(packet["sum_unit_wall_seconds"], len(self.rows) * 0.125)
        self.assertEqual(packet["coverage"]["receipts_received"], 11)
        self.assertEqual(packet["coverage"]["expected_root_count"], self.inventory["expected_root_count"])
        self.assertIsNone(packet["cold_workflow_seconds"])
        self.assertTrue(all(packet[k] is False for k in worker.FLAGS))

        # Artifact transport keeps FILES, not empty directories. Use only regular
        # files (no explicit directory ZIP entries), then restore CI privacy.
        shell = next(p for k, p in self.paths.items() if self.rows[k]["unit"] == "doc-references")
        self.assertEqual([p.name for p in (shell / "profiles").iterdir()], [worker.CONTAINER_MARKER])
        uploaded = {}
        archive_path = self.root / "file-only.zip"
        with zipfile.ZipFile(archive_path, "w") as archive:
            for path in sorted(self.inputs.rglob("*")):
                if path.is_dir():
                    continue
                self.assertFalse(path.is_symlink())
                self.assertTrue(stat.S_ISREG(path.stat().st_mode))
                name = path.relative_to(self.inputs).as_posix()
                uploaded[name] = worker.sha256(path.read_bytes())
                archive.write(path, name)
        downloaded = self.root / "downloaded"
        downloaded.mkdir(mode=0o700)
        with zipfile.ZipFile(archive_path) as archive:
            self.assertTrue(all(not info.is_dir() for info in archive.infolist()))
            self.assertIn((shell.relative_to(self.inputs) / "profiles" / worker.CONTAINER_MARKER).as_posix(),
                          archive.namelist())
            archive.extractall(downloaded)
        for path in downloaded.rglob("*"):
            path.chmod(0o700 if path.is_dir() else 0o600)
        self.assertEqual(uploaded, {p.relative_to(downloaded).as_posix(): worker.sha256(p.read_bytes())
                                    for p in downloaded.rglob("*") if p.is_file()})
        transported_shell = downloaded / shell.relative_to(self.inputs)
        original_inputs = self.inputs
        self.inputs = downloaded
        try:
            transported = self.run_aggregate(real=True)
            self.assertTrue(transported["valid"], transported["errors"])
            self.assertEqual(transported, packet)  # All correlation/coverage metadata preserved.
            original_unit = self.unit(transported_shell)
            marker = transported_shell / "profiles" / worker.CONTAINER_MARKER
            marker_entry = next(e for e in original_unit["profiles"]
                                if e["filename"] == worker.CONTAINER_MARKER)
            self.assertEqual(marker_entry["sha256"], worker.sha256(worker.CONTAINER_BYTES))

            unknown = marker.parent / "unknown.bin"
            with worker.open_artifact(unknown) as stream:
                stream.write("not a profile")
            self.assert_red(self.run_aggregate(), "unexpected profile file")
            unknown.unlink()
            changed = copy.deepcopy(original_unit)
            changed["profiles"][0]["sha256"] = "0" * 64
            self.rewrite(transported_shell / "unit.json", changed)
            self.assert_red(self.run_aggregate(), "hash mismatch")
            # Even a rehashed marker cannot redefine the literal container schema.
            marker.write_bytes(b"l0.profile-container/2\n")
            changed["profiles"][0]["sha256"] = worker.sha256(marker.read_bytes())
            self.rewrite(transported_shell / "unit.json", changed)
            self.assert_red(self.run_aggregate(), "invalid profile container marker")
            marker.write_bytes(worker.CONTAINER_BYTES)
            for entries, message in (([], "marker required exactly once"),
                                     ([marker_entry, marker_entry], "duplicate/unknown profile")):
                changed = copy.deepcopy(original_unit)
                changed["profiles"] = entries
                self.rewrite(transported_shell / "unit.json", changed)
                self.assert_red(self.run_aggregate(), message)
            self.rewrite(transported_shell / "unit.json", original_unit)
            marker.unlink()
            self.assert_red(self.run_aggregate(), "marker required exactly once")
            with worker.open_artifact(marker) as stream:
                stream.write(worker.CONTAINER_BYTES.decode("ascii"))
            self.assertTrue(self.run_aggregate()["valid"])
        finally:
            self.inputs = original_inputs

    def test_real_unavailable_route_remains_red(self):
        packet = self.run_aggregate(real=True)
        self.assertTrue(packet["valid"], packet["errors"])
        row = next(r for r in self.real_rows.values() if r["unit"] == "guardrails-static")
        self.assertEqual(row["route"], "planned")
        row["route"] = "unimplemented"  # explicit unavailable negative fixture
        self.assert_red(self.run_aggregate(real=True), "unavailable route")
        row = next(r for r in self.rows.values() if r["unit"] == "guardrails-static")
        row["route"] = "unknown"
        self.assert_red(self.run_aggregate(), "unavailable route")

    def test_failed_cancelled_skipped_controller_status_cannot_promote_complete_inputs(self):
        for result in ("failure", "cancelled", "skipped"):
            packet = self.run_aggregate(result)
            self.assert_red(packet, "worker-result must be success")
            self.assertTrue(packet["coverage_valid"], "coverage accounting is not job success")

    def test_missing_duplicate_and_unknown_slots_refuse_independent_expected_set(self):
        key = next(iter(self.paths))
        path = self.paths[key]
        saved = self.root / "saved"
        path.rename(saved)
        self.assert_red(self.run_aggregate(), "missing/failed expected")
        saved.rename(path)
        duplicate = self.inputs / "duplicate"
        shutil.copytree(path, duplicate)
        # More than exact number of slots is refused at collection, even before IDs.
        self.assert_red(self.run_aggregate(), "too many unit")
        # At exact file count, duplicate IDs are still rejected independently.
        other = next(p for p in self.paths.values() if p != path)
        other.rename(saved)
        self.assert_red(self.run_aggregate(), "duplicate worker-slot")
        shutil.rmtree(duplicate)
        saved.rename(other)
        packet = self.unit(path)
        packet["slot"] = 999
        self.rewrite(path / "unit.json", packet)
        self.assert_red(self.run_aggregate(), "unknown assignment")

    def test_run_attempt_source_plan_inventory_and_status_correlation_fail_closed(self):
        path = next(iter(self.paths.values()))
        original = self.unit(path)
        for field, value in (("run_id", 8), ("attempt", 3), ("source_commit", "2" * 40),
                             ("source_dirty", ["dirty"]), ("plan_sha256", "0" * 64),
                             ("inventory_sha256", "0" * 64), ("exit_code", True),
                             ("status", "failure"), ("metadata_authenticated", True)):
            packet = copy.deepcopy(original)
            packet[field] = value
            self.rewrite(path / "unit.json", packet)
            self.assert_red(self.run_aggregate(), field)
        self.rewrite(path / "unit.json", original)
        packet = copy.deepcopy(original)
        packet["canonicalcommand"] = ["sh", "must-not-launch.sh"]
        self.rewrite(path / "unit.json", packet)
        with mock.patch.object(worker.ci_process, "capture") as capture:
            self.assert_red(self.run_aggregate(), "canonicalcommand")
            capture.assert_not_called()

    def test_capture_log_and_profile_hash_corruption_each_refuses(self):
        path = next(p for k, p in self.paths.items() if self.rows[k]["kind"] == "python")
        unit = self.unit(path)
        targets = [path / "capture.command.json", path / "capture.command.log",
                   path / "profiles" / next(e["filename"] for e in unit["profiles"]
                                            if e["filename"].endswith(".json"))]
        for target in targets:
            original = target.read_bytes()
            target.write_bytes(original + b" ")
            self.assert_red(self.run_aggregate(), "hash mismatch")
            target.write_bytes(original)

    def test_json_path_traversal_duplicate_index_and_unclaimed_profile_json_refuse(self):
        path = next(p for k, p in self.paths.items() if self.rows[k]["kind"] == "python")
        original = self.unit(path)
        packet = copy.deepcopy(original)
        packet["capture"]["filename"] = "../escape.json"
        self.rewrite(path / "unit.json", packet)
        self.assert_red(self.run_aggregate(), "basename/path traversal")
        packet = copy.deepcopy(original)
        packet["profiles"].append(packet["profiles"][0])
        self.rewrite(path / "unit.json", packet)
        self.assert_red(self.run_aggregate(), "duplicate/unknown profile")
        self.rewrite(path / "unit.json", original)
        worker.write_json(path / "profiles" / "unclaimed.json", {})
        self.assert_red(self.run_aggregate(), "unclaimed")

    def test_symlinks_hardlinks_public_files_and_wrong_owner_refuse(self):
        path = next(iter(self.paths.values()))
        log = path / "capture.command.log"
        saved = self.root / "saved-log"
        log.rename(saved)
        log.symlink_to(saved)
        self.assert_red(self.run_aggregate(), "symlink")
        log.unlink()
        os.link(saved, log)
        self.assert_red(self.run_aggregate(), "singly linked")
        log.unlink()
        saved.rename(log)
        log.chmod(0o644)
        self.assert_red(self.run_aggregate(), "private owned")
        log.chmod(0o600)
        with mock.patch.object(worker.os, "getuid", return_value=os.getuid() + 1):
            with self.assertRaises(ValueError):
                self.run_aggregate()

    def test_size_file_count_depth_and_unknown_layout_are_bounded(self):
        with mock.patch.object(worker, "JSON_CAP", 128), mock.patch.object(worker, "frozen_contract",
                return_value=(self.plan, self.inventory, self.ph, self.ih)):
            self.assert_red(self.run_aggregate(), "size cap")
        path = next(iter(self.paths.values()))
        worker.write_json(path / "unexpected.json", {})
        self.assert_red(self.run_aggregate(), "unknown/missing unit path")
        (path / "unexpected.json").unlink()
        deep = self.inputs / "one" / "two" / "three" / "four"
        deep.mkdir(parents=True, mode=0o700)
        for parent in (deep.parent, deep.parent.parent, deep.parent.parent.parent):
            parent.chmod(0o700)
        worker.write_json(deep / "raw.json", {})
        self.assert_red(self.run_aggregate(), "depth cap")

    def test_rehashed_profiles_cannot_redefine_expected_methods_raw_subtests_or_nested_parent(self):
        path = next(p for k, p in self.paths.items() if self.rows[k]["unit"] == "UPG")
        original = {p: p.read_bytes() for p in (path / "profiles").iterdir()}
        unit_original = (path / "unit.json").read_bytes()
        def missing(packet):
            packet["events"] = []
            packet["collected_ids"] = []
            packet["tests_run"] = 0
        self.edit_profile(path, missing)
        self.assert_red(self.run_aggregate())
        for p, data in original.items():
            p.write_bytes(data)
        (path / "unit.json").write_bytes(unit_original)
        def raw(packet):
            event = packet["events"][0]
            event["subtests"].append({"test_id": event["test_id"] + " (forged=1)", "outcome": "success"})
        self.edit_profile(path, raw)
        self.assert_red(self.run_aggregate(), "RAW subtests")
        for p, data in original.items():
            p.write_bytes(data)
        (path / "unit.json").write_bytes(unit_original)
        unit = self.unit(path)
        entry = next(e for e in unit["profiles"] if e["filename"].endswith(".json") and json.loads(
            (path / "profiles" / e["filename"]).read_text())["parent_cohort"] is not None)
        nested = path / "profiles" / entry["filename"]
        packet = json.loads(nested.read_text())
        packet["parent_cohort"] = None
        self.rewrite(nested, packet)
        entry["sha256"] = worker.sha256(nested.read_bytes())
        self.rewrite(path / "unit.json", unit)
        self.assert_red(self.run_aggregate(), "cohort")

    def test_duplicate_json_keys_nonfinite_malformed_and_raw_root_json_refuse(self):
        path = next(iter(self.paths.values()))
        original = (path / "unit.json").read_bytes()
        for data in (b'{"schema":1,"schema":2}', b'{"value":NaN}', b'not JSON'):
            (path / "unit.json").write_bytes(data)
            self.assert_red(self.run_aggregate())
        (path / "unit.json").write_bytes(original)
        worker.write_json(self.inputs / "raw.json", {})
        self.assert_red(self.run_aggregate(), "unknown raw artifact path")

    def test_source_output_preflights_diagnostics_no_overwrite_and_cli_fail_closed(self):
        self.assert_red(self.run_aggregate(source_error=ValueError("HEAD mismatch")), "HEAD mismatch")
        out = self.root / "retained"
        out.mkdir(mode=0o700)
        worker.write_json(out / "aggregate.json", {"retained": True})
        with self.assertRaises(ValueError):
            aggregate.aggregate(self.inputs, out, SHA, 7, 2, "success")
        self.assertEqual(json.loads((out / "aggregate.json").read_text()), {"retained": True})
        with mock.patch.object(aggregate.sys, "stdout", io.StringIO()) as stdout:
            self.assertEqual(aggregate.main(["--worker-result", "success"]), 1)
            self.assertFalse(json.loads(stdout.getvalue())["valid"])
        with self.assertRaises(ValueError):
            aggregate.aggregate(self.inputs, worker.ROOT, SHA, 7, 2, "success")


if __name__ == "__main__":
    unittest.main()
