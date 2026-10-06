#!/usr/bin/env python3
"""One closed candidate slot; experimental receipts are claims, not authenticated proof.

CLI: --worker 1..6 --slot N --out EXISTING_PRIVATE_EMPTY_EXTERNAL_DIR
     --source-sha FULL_SHA --run-id N --attempt N
API: execute(worker, slot, out, source_sha, run_id, attempt) -> unit packet.
No helper-owned discovery, install, promotion, Git mutation, or readiness assertion.
Prewarm the outer pinned runtime; nested births retain production network/sandbox policy.
"""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager
import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
if __package__:
    from . import ci_coverage as coverage, ci_schedule as schedule, ci_process
    from .ci_profile_io import checked_target, open_artifact
else:
    import ci_coverage as coverage
    import ci_schedule as schedule
    import ci_process
    from ci_profile_io import checked_target, open_artifact

ROOT = Path(__file__).resolve().parents[1]
JSON_CAP = 16 * 1024 * 1024
LOG_CAP = 64 * 1024 * 1024
TOTAL_CAP = 256 * 1024 * 1024
CONTAINER_MARKER = "container.marker"
CONTAINER_BYTES = b"l0.profile-container/1\n"
NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,159}\Z")
FLAGS = {"performance_proven": False, "host_authenticity_proven": False,
         "metadata_authenticated": False, "product_equivalence_proven": False,
         "owner_equivalence_proven": False, "ready_for_hosted": False,
         "assertion_execution_proven": False, "auto_promoted": False}
require = coverage.require


def identity(source_sha, run_id, attempt):
    require(coverage.digest(source_sha, 40), "exact full source SHA required")
    require(coverage.integer(run_id, 1) and coverage.integer(attempt, 1), "positive run/attempt required")


def clean_env():
    # Never let an ambient index, config injection, task executable or profile
    # parent select another source/context. Keep public pinned ROCS provisioning.
    return {k: v for k, v in os.environ.items() if not k.startswith(("GIT_", "AK_", "L0_PROFILE_",
            "L0_CHECK_TIMEOUT")) and k not in {"L0_TEMPLATE_ROOT", "PYTHONPATH", "PYTHONHOME"}}


def source_state(sha):
    env = clean_env()
    env["GIT_OPTIONAL_LOCKS"] = "0"
    def query(*args):
        result = subprocess.run(["git", "--no-optional-locks", "-c", "core.fsmonitor=false",
                                 "-c", "core.untrackedCache=false", *args], cwd=ROOT, env=env,
                                capture_output=True, text=True, timeout=10, check=True)
        return result.stdout
    actual = query("rev-parse", "HEAD").strip()
    dirty = query("status", "--porcelain", "--untracked-files=all").splitlines()
    require(actual == sha, "actual source HEAD mismatch")
    require(dirty == [], "source must be clean before and after execution")
    return actual, dirty


def private_dir(value, fresh=False):
    path = Path(value).absolute()
    require(path.is_dir(), "directory must already exist")
    checked_target(path / "privacy-probe")
    require(not fresh or not any(path.iterdir()), "directory must be fresh/empty")
    return path


def safe_name(value):
    require(isinstance(value, str) and NAME.fullmatch(value) is not None,
            "invalid artifact basename/path traversal")
    return value


def read_bytes(path, cap):
    path = Path(path)
    checked_target(path)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    with os.fdopen(fd, "rb") as stream:
        info = os.fstat(stream.fileno())
        require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and info.st_uid == os.getuid()
                and not info.st_mode & 0o077, "artifact must be private owned regular singly linked")
        require(info.st_size <= cap, "artifact size cap")
        data = stream.read(cap + 1)
        require(len(data) <= cap, "artifact size cap")
        return data


def parse_json(data):
    return coverage.load_json(io.StringIO(data.decode("utf-8")))


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, packet):
    with open_artifact(path) as stream:
        json.dump(packet, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")


def frozen_contract():
    # ONLY these source-owned inputs; never artifact-provided plans/inventories.
    paths = [ROOT / "tests" / name for name in ("ci_schedule.json", "ci_coverage_inventory.json")]
    data = []
    for path in paths:
        require(not path.is_symlink() and path.is_file() and path.stat().st_size <= JSON_CAP,
                "invalid source contract")
        data.append(path.read_bytes())
    plan, inventory = map(parse_json, data)
    check = schedule.validate_schedule(plan, inventory)
    require(check["valid"], "invalid schedule: " + "; ".join(check["errors"]))
    return plan, inventory, sha256(data[0]), sha256(data[1])


def assignments(plan, inventory):
    return {(w, row["order"]): row for w in range(1, 7)
            for row in schedule.worker_commands(plan, inventory, w)}


def descriptor(plan, inventory, worker, slot):
    require(type(worker) is int and worker in range(1, 7), "worker must be 1..6")
    require(coverage.integer(slot, 1), "slot must be a positive assigned index")
    rows = assignments(plan, inventory)
    require((worker, slot) in rows, "unassigned slot")
    row = rows[worker, slot]
    require(row["route"] == "planned", "route unavailable: " + row["route"])
    require(row["command"] == schedule.canonical_command(schedule.SPECS[row["unit"]]),
            "canonical command drift")
    script = ROOT / row["command"][1]
    require(script.is_file() and not script.is_symlink() and script.resolve().is_relative_to(ROOT),
            "closed entrypoint unavailable/untrusted")
    for parent in script.parents:
        require(not parent.is_symlink(), "linked entrypoint ancestry")
    return row


def budget(row):
    return 3600 if row["cohort"] == "generation-main" or row["unit"] in {
        "sample-shell", "profile-community", "profile-release", "profile-vouch", "profile-compact"} else 1800


def unit_env(row, out, tmp):
    # Offline applies to the prewarmed outer runtime only. Production birth
    # sanitizers drop these UV flags and retain their own sandbox/network policy.
    env = clean_env()
    env.update(TMPDIR=str(tmp), L0_PROFILE_DIR=str(out / "profiles"),
               L0_PROFILE_CONDITION="candidate", PYTHONDONTWRITEBYTECODE="1",
               COPIER_VERSION="9.11.1", UV_OFFLINE="1", UV_NO_MANAGED_PYTHON="1")
    if budget(row) == 3600:
        env["L0_TEMPLATE_ROOT"] = str(ROOT)
    return env


@contextmanager
def normal_umask():
    previous = os.umask(0o022)
    try:
        yield
    finally:
        os.umask(previous)


def file_index(path, filename):
    cap = LOG_CAP if filename.endswith(".log") else JSON_CAP
    data = read_bytes(path, cap)
    return {"filename": filename, "sha256": sha256(data)}


def initialize_profiles(directory):
    Path(directory).mkdir(mode=0o700)
    with open_artifact(Path(directory) / CONTAINER_MARKER) as stream:
        stream.write(CONTAINER_BYTES.decode("ascii"))


def profile_files(directory):
    private_dir(directory)
    result = []
    for path in sorted(directory.iterdir()):
        safe_name(path.name)
        require(path.name == CONTAINER_MARKER or path.suffix in {".json", ".tsv"},
                "unexpected profile file")
        if path.name == CONTAINER_MARKER:
            require(read_bytes(path, JSON_CAP) == CONTAINER_BYTES, "invalid profile container marker")
        result.append(file_index(path, path.name))
    require(sum(p["filename"] == CONTAINER_MARKER for p in result) == 1,
            "profile container marker required exactly once")
    require(len(result) <= 9, "too many unit profile files")
    return result


def validate_profiles(row, inventory, packets, sha):
    expected, owners, _ = coverage.inventory_counters(inventory)
    wanted = {}
    if row["kind"] == "python":
        wanted[(row["cohort"], None)] = (Counter(row["methods"]), None)
    for child in row["nested"]:
        key = (child["cohort"], child["parent_cohort"])
        require(child["parent_method"] == owners[key], "nested parent binding")
        wanted[key] = (Counter(child["methods"]), child["parent_method"])
    require(len(packets) == len(wanted), "missing/excess unit profiles")
    seen = set()
    for packet in packets:
        key, collected, ids, outcomes, subs = coverage.profile_counters(packet, sha)
        require(key in wanted and key not in seen, "profile cohort/parent assigned to another unit")
        seen.add(key)
        methods, _ = wanted[key]
        require(collected == ids == methods, "per-unit expected method multiset mismatch")
        _, all_outcomes, all_subs = expected[key]
        require(outcomes == Counter({k: v for k, v in all_outcomes.items() if k[0] in methods}),
                "per-unit method outcomes mismatch")
        require(subs == Counter({k: v for k, v in all_subs.items() if k[0] in methods}),
                "per-unit RAW subtests mismatch")
        require(packet.get("condition") == "candidate", "profile condition mismatch")
        if key[1] is None:
            require(packet["arguments"] == row["selectors"], "profile selectors drift")


def validate_capture(packet, row, sha):
    # Reuse the exact shell receipt checks for Python captures too, without
    # claiming Python is a shell obligation or normalizing command tokens.
    coverage.check_receipt({"unit": row["unit"], "source_commit": sha,
                            "source_dirty": [], "capture": packet},
                           {row["unit"]: row["command"]}, sha)
    require(packet.get("timed_out") is False and packet.get("timeout_seconds") == budget(row),
            "capture deadline missing/mismatched")
    require(packet.get("condition") == "candidate" and packet.get("log") == "capture.command.log",
            "capture condition/log mismatch")
    seconds = packet.get("wall_seconds")
    require(type(seconds) in (int, float) and 0 <= seconds <= sys.float_info.max
            and math.isfinite(seconds), "invalid capture duration")


def execute(worker, slot, out, source_sha, run_id, attempt):
    identity(source_sha, run_id, attempt)
    out = private_dir(out, fresh=True)
    source_state(source_sha)
    plan, inventory, plan_hash, inventory_hash = frozen_contract()
    row = descriptor(plan, inventory, worker, slot)
    initialize_profiles(out / "profiles")
    packet = {"schema": "l0.candidate-unit/1", "worker": worker, "slot": slot, "unit": row["unit"],
              "run_id": run_id, "attempt": attempt, "source_commit": source_sha, "source_dirty": [],
              "plan_sha256": plan_hash, "inventory_sha256": inventory_hash,
              "canonicalcommand": row["command"], "capture_filename": "capture.command.json",
              "capture": None, "log": None, "profiles": [], "exit_code": 1, "status": "failure",
              "errors": [], **FLAGS}
    try:
        try:
            with normal_umask(), tempfile.TemporaryDirectory(prefix="tmp-", dir=out) as tmp:
                capture = ci_process.capture(row["command"], out / "capture.command.json", root=ROOT,
                                             env=unit_env(row, out, tmp), timeout_seconds=budget(row))
            packet["exit_code"] = capture["exit_code"] or 1
        finally:
            # Includes capture/JSON IO failure and cancellation, not only success.
            source_state(source_sha)
        packet["capture"] = file_index(out / "capture.command.json", "capture.command.json")
        packet["log"] = file_index(out / "capture.command.log", "capture.command.log")
        packet["profiles"] = profile_files(out / "profiles")
        profiles = [parse_json(read_bytes(out / "profiles" / p["filename"], JSON_CAP))
                    for p in packet["profiles"] if p["filename"].endswith(".json")]
        validate_capture(capture, row, source_sha)
        validate_profiles(row, inventory, profiles, source_sha)
        packet.update(exit_code=0, status="success", wall_seconds=capture["wall_seconds"])
    except (OSError, ValueError, TypeError, KeyError, UnicodeError, RecursionError,
            subprocess.SubprocessError) as error:
        packet["errors"].append(str(error))
        # No positive clean-source assertion on any incomplete/dirty unit.
        packet["source_dirty"] = None
    write_json(out / "unit.json", packet)
    return packet


def main(argv=None):
    try:
        parser = coverage.JsonArgumentParser(description=__doc__)
        parser.add_argument("--worker", type=int, required=True, choices=range(1, 7))
        for name in ("slot", "run-id", "attempt"):
            parser.add_argument("--" + name, type=int, required=True)
        parser.add_argument("--out", required=True)
        parser.add_argument("--source-sha", required=True)
        args = parser.parse_args(argv)
        packet = execute(args.worker, args.slot, args.out, args.source_sha, args.run_id, args.attempt)
    except (OSError, ValueError, TypeError, KeyError, UnicodeError, RecursionError,
            subprocess.SubprocessError) as error:
        packet = {"schema": "l0.candidate-unit/1", "exit_code": 1, "status": "failure",
                  "errors": [str(error)], **FLAGS}
    print(json.dumps(packet, sort_keys=True, allow_nan=False))
    return packet["exit_code"]


if __name__ == "__main__":
    raise SystemExit(main())
