#!/usr/bin/env python3
"""Hosted observation only: retain serial output, then replay its root unittest cohorts.

Only explicit selector order changes. Nested cohorts must recur through their parent,
not as extra executions. Raw subtest IDs are never normalized; a mismatch leaves
comparison uncertain/red rather than claiming a stable oracle or a timing guarantee.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import ctypes
import json
import os
from pathlib import Path
import shutil
import signal
import selectors
import subprocess
import sys
import time

if __package__:
    from . import ci_process
    from .ci_profile_io import checked_target, open_artifact
    from .ci_process import GRACE_SECONDS, KILL_WAIT_SECONDS, adopt_descendants, shell_status, teardown
else:
    import ci_process
    from ci_profile_io import checked_target, open_artifact
    from ci_process import GRACE_SECONDS, KILL_WAIT_SECONDS, adopt_descendants, shell_status, teardown

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    ("guardrails-main", None), ("guardrails-system4d", None),
    ("generation-main", None), ("generation-upgrade", "generation-main"),
}
ROOT_COHORT_ORDER = {"guardrails-main": 0, "guardrails-system4d": 1, "generation-main": 2}
FLAGS = {"-v", "--verbose", "-q", "--quiet", "-b", "--buffer", "-c", "--catch", "-f", "--failfast"}


def write_json(path, packet):
    with open_artifact(path) as output:
        json.dump(packet, output, indent=2, sort_keys=True)
        output.write("\n")


def private_directory(value, *, fresh=False):
    directory = Path(value).absolute()
    if not directory.is_dir():
        raise ValueError(f"directory must already exist: {directory}")
    checked_target(directory / "unused-privacy-probe")
    if fresh and any(directory.iterdir()):
        raise ValueError(f"directory must be fresh/empty: {directory}")
    return directory


def capture(command, target, *, env=None):
    """Keep the observer API and its artifact-writer seams after helper extraction."""
    return ci_process.capture(command, target, env=env, root=ROOT,
                              artifact_opener=open_artifact, packet_writer=write_json)


def reverse_arguments(arguments):
    """Keep flag positions and exact selectors; refuse discovery/filter inference."""
    if not isinstance(arguments, list) or not arguments:
        raise ValueError("explicit unittest arguments required")
    positions = []
    for index, argument in enumerate(arguments):
        if not isinstance(argument, str) or not argument:
            raise ValueError("invalid unittest selector")
        if argument in FLAGS:
            continue
        if argument.startswith("-") or argument == "discover":
            raise ValueError(f"unsupported unittest arguments; no inferred exclusion: {arguments}")
        positions.append(index)
    if not positions:
        raise ValueError("explicit unittest selectors required")
    result = list(arguments)
    for index, selector in zip(positions, reversed([arguments[i] for i in positions])):
        result[index] = selector
    return result


def profiles(directory):
    result = []
    for path in sorted(directory.glob("*.json")):
        packet = json.loads(path.read_text())
        if packet.get("schema") == "l0.unittest-profile/1":
            result.append((path.name, packet))
    return result


def counter_difference(left, right):
    def rows(counter):
        return [{"value": value, "count": count} for value, count in sorted(counter.items())]
    return {"serial_only": rows(left - right), "second_only": rows(right - left)}


def event_counts(packet, kind, *, outcomes=False):
    return Counter((event["test_id"], event["outcome"]) if outcomes else event["test_id"]
                   for event in packet.get("events", []) if event["kind"] == kind)


def subtest_counts(packet):
    return Counter((event["test_id"], subtest["test_id"], subtest["outcome"])
                   for event in packet.get("events", []) for subtest in event.get("subtests", []))


def validate_ledger(packet):
    """Equality of two partial/broken observers is not evidence of full execution."""
    errors, uncertainty = [], []
    collected, events = packet.get("collected_ids"), packet.get("events")
    text = lambda value: isinstance(value, str) and bool(value)
    shape = (isinstance(collected, list) and all(map(text, collected)) and isinstance(events, list))
    shape = shape and all(isinstance(e, dict) and text(e.get("test_id")) and text(e.get("outcome"))
                          and e.get("kind") in {"test", "fixture"} for e in events)
    if not shape:
        return {"valid": False, "shape_valid": False, "coverage_complete": False,
                "errors": ["missing/malformed collected IDs or events"], "uncertainty": []}
    tests = [e for e in events if e["kind"] == "test"]
    fixtures = [e for e in events if e["kind"] == "fixture"]
    allowed = {"success", "skip", "expected_failure", "unexpected_success", "failure", "error"}
    for index, event in enumerate(events):
        if event["outcome"] not in (allowed if event["kind"] == "test" else {"skip", "failure", "error"}):
            errors.append(f"invalid outcome at event {index}")
        subs = event.get("subtests", [])
        if not isinstance(subs, list) or not all(isinstance(s, dict) and text(s.get("test_id"))
                                               and text(s.get("outcome")) for s in subs):
            return {"valid": False, "shape_valid": False, "coverage_complete": False,
                    "errors": [f"malformed subtests at event {index}"], "uncertainty": []}
        if event["kind"] == "fixture" and subs:
            errors.append(f"fixture contains subtests at event {index}")
        for sub in subs:
            if not sub["test_id"].startswith(event["test_id"] + " "):
                errors.append(f"subtest parent identity mismatch at event {index}")
            if sub["outcome"] not in {"success", "skip", "failure", "error"}:
                errors.append(f"invalid subtest outcome at event {index}")
            if sub["outcome"] in {"failure", "error"} and event["outcome"] not in {sub["outcome"], "error"}:
                errors.append(f"subtest failure missing from parent outcome at event {index}")
    count = packet.get("tests_run")
    if type(count) is not int or count != len(tests):
        errors.append("tests_run does not equal recorded method executions")
    ordinals = [e.get("ordinal") for e in tests]
    if any(type(n) is not int for n in ordinals) or sorted(ordinals) != list(range(1, len(tests) + 1)):
        errors.append("method execution ordinals missing/duplicated/non-contiguous")
    executed = Counter(e["test_id"] for e in tests)
    missing, extra = Counter(collected) - executed, executed - Counter(collected)
    failed = any(e["outcome"] in {"failure", "error", "unexpected_success"} for e in events)
    if extra:
        errors.append("execution IDs/multiplicity exceed collection")
    if missing:
        uncertainty.append("Coverage incomplete: collected methods lack execution events; fixture failure/skip "
                           "or fail-fast may explain this, but no complete-execution claim is made.")
        if not fixtures and not (failed and any(a in {"-f", "--failfast"} for a in packet.get("arguments", []))):
            errors.append("unexplained missing method execution events")
    if not collected:
        uncertainty.append("Coverage incomplete: empty collection.")
    if fixtures:
        uncertainty.append("Fixture failure/skip recorded; full-cohort coverage is uncertain, not complete.")
    code = packet.get("exit_code")
    if type(code) is not int or code < 0 or type(packet.get("successful")) is not bool:
        errors.append("invalid exit_code/successful status")
    elif packet["successful"] != (code == 0) or code not in (
            {1} if failed and tests else {1, 5} if failed else {0} if tests else {0, 5}):
        errors.append("exit status inconsistent with observed outcomes")
    if type(packet.get("result_successful")) is not bool or packet["result_successful"] != (not failed):
        errors.append("result_successful inconsistent with observed outcomes")
    return {"valid": not errors, "shape_valid": True,
            "coverage_complete": bool(collected) and not missing and not errors and not fixtures,
            "collected_count": len(collected), "executed_count": len(tests),
            "errors": errors, "uncertainty": uncertainty}


def compare_packet(serial, second):
    checks = {"serial": validate_ledger(serial), "second": validate_ledger(second)}
    differences = {}
    uncertainty = [f"{label}: {note}" for label, check in checks.items() for note in check["uncertainty"]]
    if not all(check["shape_valid"] for check in checks.values()):
        return {"exact_match": False, "differences": differences, "ledger_checks": checks, "uncertainty": uncertainty}
    counters = {
        "collected_method_ids": (Counter(serial.get("collected_ids", [])), Counter(second.get("collected_ids", []))),
        "executed_method_ids": (event_counts(serial, "test"), event_counts(second, "test")),
        "method_ids_outcomes": (event_counts(serial, "test", outcomes=True), event_counts(second, "test", outcomes=True)),
        "fixture_ids_outcomes": (event_counts(serial, "fixture", outcomes=True), event_counts(second, "fixture", outcomes=True)),
        "raw_subtest_ids_outcomes": (subtest_counts(serial), subtest_counts(second)),
    }
    for name, (left, right) in counters.items():
        if left != right:
            differences[name] = counter_difference(left, right)
    for key in ("cohort", "parent_cohort", "tests_run", "exit_code", "successful", "result_successful",
                "python", "python_executable", "copier", "source_commit", "source_dirty"):
        if key not in serial or key not in second or serial[key] != second[key]:
            differences[key] = {"serial": serial.get(key), "second": second.get(key)}
    expected_arguments = reverse_arguments(serial["arguments"])
    if second["arguments"] != expected_arguments:
        differences["arguments"] = {"expected_second": expected_arguments, "second": second["arguments"]}
    if "raw_subtest_ids_outcomes" in differences:
        uncertainty.append("Raw subtest IDs/outcomes differ. Ephemeral directory parameters may differ; "
                           "no normalization or exclusions applied. Subtest equivalence is unproven.")
    return {"exact_match": not differences and all(c["coverage_complete"] for c in checks.values()),
            "differences": differences, "ledger_checks": checks, "uncertainty": uncertainty}


def grouped(packets):
    groups = defaultdict(list)
    for name, packet in packets:
        groups[(packet["cohort"], packet.get("parent_cohort"))].append((name, packet))
    return groups


def compare_manifests(serial, second, *, require_full=True):
    left, right = grouped(serial), grouped(second)
    comparisons, issues = [], []
    keys = set(left) | set(right) | (EXPECTED if require_full else set())
    for key in sorted(keys, key=lambda item: (item[0], item[1] or "")):
        first, other = left[key], right[key]
        if not first or len(first) != len(other):
            issues.append({"cohort": key[0], "parent_cohort": key[1],
                           "serial_count": len(first), "second_count": len(other)})
        for (serial_name, before), (second_name, after) in zip(first, other):
            comparisons.append({"serial_report": serial_name, "second_report": second_name,
                                "cohort": key[0], "parent_cohort": key[1], **compare_packet(before, after)})
    if require_full:
        for label, packets in (("serial", serial), ("second", second)):
            for cohort, needle in (("guardrails-main", "test_l1_template_reverse_transitions."),
                                   ("generation-upgrade", "test_l1_answer_template_upgrade.UpgradeTests.")):
                if not any(needle in test_id for _, packet in packets if packet["cohort"] == cohort
                           for test_id in packet.get("collected_ids", [])):
                    issues.append({"condition": label, "missing_collected_coverage": needle})
    return {"exact_match": bool(comparisons) and not issues and all(c["exact_match"] for c in comparisons),
            "manifest_issues": issues, "comparisons": comparisons}


def cohort_timeout(cohort):
    base = os.environ.get("L0_CHECK_TIMEOUT_SECONDS") or "1800"
    generation = os.environ.get("L0_CHECK_TIMEOUT_GENERATION_SECONDS") or (
        str(int(base) * 2) if os.environ.get("L0_CHECK_TIMEOUT_SECONDS") else "3600")
    value = generation if cohort == "generation-main" else base
    if not value.isdecimal():
        raise ValueError("timeout must be a non-negative integer")
    return int(value)


def reorder(serial_dir, out_dir, tmpdir):
    serial_dir = private_directory(serial_dir)
    out_dir = private_directory(out_dir, fresh=True)
    tmpdir = private_directory(tmpdir, fresh=True)
    if any(a == b or a.is_relative_to(b) or b.is_relative_to(a)
           for a, b in ((serial_dir, out_dir), (serial_dir, tmpdir), (out_dir, tmpdir))):
        raise ValueError("serial, second, and scratch directories must be disjoint")
    summary = {"schema": "l0.reorder-profile/1", "condition": "reverse-modules",
               "schedule": "serial root cohorts; reversed explicit selector order within each",
               "scope": "unittest cohorts only; not a second full seven-check workflow",
               "tmpdir": str(tmpdir), "commands": [], "execution_errors": [],
               "stable_oracle_proven": False, "cold_workflow_15min_proven": False}
    started = time.perf_counter()
    serial = profiles(serial_dir)
    roots = [(name, packet) for name, packet in serial if not packet.get("parent_cohort")]
    roots.sort(key=lambda item: ROOT_COHORT_ORDER.get(item[1]["cohort"], len(ROOT_COHORT_ORDER)))
    # An explicit manifest, never discovery, deduplication, sharding or nested replay.
    for index, (name, packet) in enumerate(roots, 1):
        try:
            args = reverse_arguments(packet["arguments"])
            env = dict(os.environ, L0_PROFILE_DIR=str(out_dir), L0_PROFILE_CONDITION="reverse-modules",
                       TMPDIR=str(tmpdir), PYTHONDONTWRITEBYTECODE="1")
            for key in ("L0_PROFILE_PARENT", "L0_PROFILE_COHORT"):
                env.pop(key, None)
            runtime = packet["python_executable"]
            if packet["cohort"] in {"guardrails-main", "guardrails-system4d"} and packet.get("copier"):
                # The original guardrail helper uses uvx, which also establishes
                # PATH/environment. A direct venv Python would add a confound.
                runtime = "pinned"
                env["COPIER_VERSION"] = packet["copier"]
            if packet["cohort"] == "generation-main":
                env["L0_TEMPLATE_ROOT"] = str(ROOT)
            command = ["sh", str(ROOT / "tests/ci_unittest.sh"), packet["cohort"], runtime, *args]
            seconds = cohort_timeout(packet["cohort"])
            if seconds:
                timeout = shutil.which("timeout") or shutil.which("gtimeout")
                if not timeout:
                    raise ValueError("timeout enforcement unavailable; refusing unbounded replay")
                command = [timeout, f"{seconds}s", *command]
            result = capture(command, out_dir / f"command-{index:03}.json", env=env)
            summary["commands"].append({"serial_report": name, **result})
            if result["interrupted_signal"]:
                summary["interrupted_signal"] = result["interrupted_signal"]
                break  # cancellation must not launch another expensive cohort
        except (KeyError, OSError, ValueError) as error:
            summary["execution_errors"].append({"serial_report": name, "error": str(error)})
    summary.update(compare_manifests(serial, profiles(out_dir)))
    summary["wall_seconds"] = time.perf_counter() - started
    write_json(out_dir / "comparison.json", summary)
    if summary.get("interrupted_signal"):
        return 128 + summary["interrupted_signal"]
    return 0 if summary["exact_match"] and not summary["execution_errors"] and all(
        c["exit_code"] == 0 for c in summary["commands"]) else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_subparsers(dest="mode", required=True)
    serial = modes.add_parser("capture")
    serial.add_argument("--out", required=True)
    serial.add_argument("command", nargs=argparse.REMAINDER)
    second = modes.add_parser("reorder")
    second.add_argument("--serial-dir", required=True)
    second.add_argument("--out-dir", required=True)
    second.add_argument("--tmpdir", required=True)
    args = parser.parse_args(argv)
    try:
        if args.mode == "capture":
            command = args.command[1:] if args.command[:1] == ["--"] else args.command
            if not command:
                raise ValueError("explicit command required")
            return capture(command, args.out)["exit_code"]
        return reorder(args.serial_dir, args.out_dir, args.tmpdir)
    except (OSError, ValueError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    raise SystemExit(main())
