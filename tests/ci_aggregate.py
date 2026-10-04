#!/usr/bin/env python3
"""Fail-closed candidate accounting, never an execution/authentication controller.

CLI: --inputs PRIVATE_DOWNLOAD_ROOT --out PRIVATE_EMPTY_EXTERNAL_DIR
     --source-sha FULL_SHA --run-id N --attempt N
     --worker-result success|failure|cancelled|skipped
API: aggregate(inputs, out, source_sha, run_id, attempt, worker_result).
Writes aggregate.json once. Each leaf unit directory contains only unit.json,
capture.command.json, capture.command.log and profiles/{container.marker,*.json,*.tsv}.
The literal, indexed marker preserves even empty shell profile containers. At most
three container levels, private/owned regular singly-linked files, finite caps.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
if __package__:
    from . import ci_worker as worker
else:
    import ci_worker as worker

coverage = worker.coverage
require = coverage.require


def collect(inputs, limit):
    units, total, files, directories = [], 0, 0, 0

    def visit(path, depth):
        nonlocal total, files, directories
        directories += 1
        require(directories <= limit * 4 + 1, "artifact directory count cap")
        worker.private_dir(path)
        entries = list(path.iterdir())
        require(bool(entries), "empty artifact container")
        require(len(entries) <= limit + 4, "artifact directory entry cap")
        names = {p.name for p in entries}
        for entry in entries:
            worker.safe_name(entry.name)
        if "unit.json" in names:
            require(names == {"unit.json", "capture.command.json", "capture.command.log", "profiles"},
                    "unknown/missing unit path")
            worker.private_dir(path / "profiles")
            worker.profile_files(path / "profiles")  # Require literal marker and closed filenames.
            profiles = list((path / "profiles").iterdir())
            require(len(profiles) <= 9, "unit profile file count cap")
            for item in [path / n for n in names if n != "profiles"] + profiles:
                worker.safe_name(item.name)
                cap = worker.LOG_CAP if item.name == "capture.command.log" else worker.JSON_CAP
                # Read safely even unclaimed files; no linked/malformed paths accepted.
                data = worker.read_bytes(item, cap)
                total += len(data)
                files += 1
                require(total <= worker.TOTAL_CAP and files <= limit * 12, "download size/file cap")
            units.append(path)
            require(len(units) <= limit, "too many unit artifacts")
        else:
            require(depth < 3, "artifact container depth cap")
            for entry in sorted(entries):
                require(entry.is_dir() and not entry.is_symlink(), "unknown raw artifact path")
                visit(entry, depth + 1)
    visit(inputs, 0)
    return units


def indexed(path, entry, expected=None):
    require(isinstance(entry, dict) and set(entry) == {"filename", "sha256"}, "file index shape")
    name = worker.safe_name(entry["filename"])
    require(expected is None or name == expected, "indexed filename mismatch")
    require(coverage.digest(entry["sha256"], 64), "file hash shape")
    data = worker.read_bytes(path / name, worker.LOG_CAP if name.endswith(".log") else worker.JSON_CAP)
    require(worker.sha256(data) == entry["sha256"], "artifact hash mismatch: " + name)
    return data


def read_unit(path, rows, inventory, sha, run_id, attempt, plan_hash, inventory_hash):
    packet = worker.parse_json(worker.read_bytes(path / "unit.json", worker.JSON_CAP))
    require(isinstance(packet, dict) and packet.get("schema") == "l0.candidate-unit/1", "unit schema")
    require(coverage.integer(packet.get("worker"), 1) and coverage.integer(packet.get("slot"), 1),
            "unit worker/slot shape")
    key = packet["worker"], packet["slot"]
    require(key in rows, "unknown assignment")
    row = rows[key]
    require(row["route"] == "planned", "artifact for unavailable route")
    for field, value in {"unit": row["unit"], "source_commit": sha, "source_dirty": [],
                         "run_id": run_id, "attempt": attempt, "plan_sha256": plan_hash,
                         "inventory_sha256": inventory_hash, "canonicalcommand": row["command"],
                         "capture_filename": "capture.command.json", "status": "success",
                         "exit_code": 0, "errors": [], **worker.FLAGS}.items():
        require(field in packet and type(packet[field]) is type(value) and packet[field] == value,
                "unit correlation/status/authority mismatch: " + field)
    capture = worker.parse_json(indexed(path, packet.get("capture"), "capture.command.json"))
    indexed(path, packet.get("log"), "capture.command.log")
    worker.validate_capture(capture, row, sha)
    profile_index = packet.get("profiles")
    require(isinstance(profile_index, list) and len(profile_index) <= 9, "profile index shape")
    names, profiles = set(), []
    for entry in profile_index:
        require(isinstance(entry, dict), "profile index entry shape")
        name = worker.safe_name(entry.get("filename"))
        require(name not in names and (name == worker.CONTAINER_MARKER
                or Path(name).suffix in {".json", ".tsv"}), "duplicate/unknown profile filename")
        names.add(name)
        data = indexed(path / "profiles", entry)
        if name == worker.CONTAINER_MARKER:
            require(data == worker.CONTAINER_BYTES, "invalid profile container marker")
        elif name.endswith(".json"):
            profiles.append(worker.parse_json(data))
    require(worker.CONTAINER_MARKER in names, "profile container marker required exactly once in index")
    require(names == {p.name for p in (path / "profiles").iterdir()}, "unclaimed profile/raw JSON")
    worker.validate_profiles(row, inventory, profiles, sha)
    receipt = None if row["kind"] == "python" else {
        "unit": row["unit"], "source_commit": sha, "source_dirty": [], "capture": capture}
    return key, profiles, receipt, {"worker": key[0], "slot": key[1], "unit": row["unit"],
                                   "wall_seconds": capture["wall_seconds"]}


def aggregate(inputs, out, source_sha, run_id, attempt, worker_result):
    # Invalid output directories never receive a diagnostic (including retained IO).
    out = worker.private_dir(out, fresh=True)
    packet = {"schema": "l0.candidate-aggregate/1", "valid": False, "coverage_valid": False,
              "worker_result": worker_result, "source_commit": source_sha, "run_id": run_id,
              "attempt": attempt, "errors": [], "units": [], "sum_unit_wall_seconds": 0,
              "duration_scope": "accepted correlated captures only; excludes rejected/missing units",
              "cold_workflow_seconds": None, "coverage": None, **worker.FLAGS}
    try:
        worker.identity(source_sha, run_id, attempt)
        require(worker_result in {"success", "failure", "cancelled", "skipped"}, "invalid worker result")
        inputs = worker.private_dir(inputs)
        require(not (inputs == out or inputs.is_relative_to(out) or out.is_relative_to(inputs)),
                "inputs/output must be disjoint")
        worker.source_state(source_sha)
        plan, inventory, plan_hash, inventory_hash = worker.frozen_contract()
        rows = worker.assignments(plan, inventory)
        packet.update(plan_sha256=plan_hash, inventory_sha256=inventory_hash, expected_slots=len(rows))
        units = collect(inputs, len(rows))
        seen, profiles, receipts = set(), [], []
        for path in units:
            try:
                key, reports, receipt, duration = read_unit(path, rows, inventory, source_sha,
                    run_id, attempt, plan_hash, inventory_hash)
                require(key not in seen, "duplicate worker-slot artifact")
                seen.add(key)
                profiles.extend(reports)
                if receipt is not None:
                    receipts.append(receipt)
                packet["units"].append(duration)
            except (OSError, ValueError, TypeError, KeyError, UnicodeError, RecursionError) as error:
                packet["errors"].append(f"{path.relative_to(inputs)}: {error}")
        total_seconds = sum(float(u["wall_seconds"]) for u in packet["units"])
        require(worker.math.isfinite(total_seconds), "non-finite duration sum")
        packet["sum_unit_wall_seconds"] = total_seconds
        packet["coverage"] = json.loads(json.dumps(coverage.validate_coverage(
            inventory, profiles, receipts, expected_source_commit=source_sha), allow_nan=False))
        packet["coverage_valid"] = packet["coverage"]["valid"]
        worker.source_state(source_sha)
        require(set(rows) == seen, "missing/failed expected worker-slot artifacts")
        require(packet["coverage_valid"], "independent coverage check failed")
        require(worker_result == "success", "worker-result must be success (no partial-job promotion)")
        packet["valid"] = not packet["errors"]
    except (OSError, ValueError, TypeError, KeyError, UnicodeError, RecursionError,
            worker.subprocess.SubprocessError) as error:
        packet["errors"].append(str(error))
    worker.write_json(out / "aggregate.json", packet)
    return packet


def main(argv=None):
    try:
        parser = coverage.JsonArgumentParser(description=__doc__)
        for name in ("inputs", "out", "source-sha"):
            parser.add_argument("--" + name, required=True)
        for name in ("run-id", "attempt"):
            parser.add_argument("--" + name, required=True, type=int)
        parser.add_argument("--worker-result", required=True, choices=("success", "failure", "cancelled", "skipped"))
        args = parser.parse_args(argv)
        packet = aggregate(args.inputs, args.out, args.source_sha, args.run_id, args.attempt, args.worker_result)
    except (OSError, ValueError, TypeError, KeyError, UnicodeError, RecursionError) as error:
        packet = {"schema": "l0.candidate-aggregate/1", "valid": False, "errors": [str(error)], **worker.FLAGS}
    print(json.dumps(packet, sort_keys=True, allow_nan=False))
    return 0 if packet["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
