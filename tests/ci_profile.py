#!/usr/bin/env python3
"""Observe standard unittest collection/outcomes/timing without changing scheduling."""
from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
import time
import unittest
from ci_profile_io import checked_target, open_artifact
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def identities(suite):
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            yield from identities(test)
        else:
            yield test.id()


class TimedResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.events = []
        self.active = {}
        self.ordinal = 0

    def startTest(self, test):
        super().startTest(test)
        self.ordinal += 1
        self.active[id(test)] = {
            "ordinal": self.ordinal, "test_id": test.id(), "kind": "test",
            "started": time.perf_counter(), "outcome": "success", "subtests": [],
        }

    def outcome(self, test, value):
        entry = self.active.get(id(test))
        if entry is None:
            self.events.append({"kind": "fixture", "test_id": test.id(), "outcome": value})
        else:
            # A later successful subtest cannot erase an earlier failure/error.
            if value == "error" or entry["outcome"] == "success":
                entry["outcome"] = value

    def stopTest(self, test):
        entry = self.active.pop(id(test))
        entry["seconds"] = time.perf_counter() - entry.pop("started")
        self.events.append(entry)
        super().stopTest(test)

    def addSuccess(self, test):
        super().addSuccess(test)

    def addFailure(self, test, error):
        self.outcome(test, "failure")
        super().addFailure(test, error)

    def addError(self, test, error):
        self.outcome(test, "error")
        super().addError(test, error)

    def addSkip(self, test, reason):
        parent = self.active.get(id(getattr(test, "test_case", None)))
        if parent is None:
            self.outcome(test, "skip")
        else:
            parent["subtests"].append({"test_id": test.id(), "outcome": "skip"})
        super().addSkip(test, reason)

    def addExpectedFailure(self, test, error):
        self.outcome(test, "expected_failure")
        super().addExpectedFailure(test, error)

    def addUnexpectedSuccess(self, test):
        self.outcome(test, "unexpected_success")
        super().addUnexpectedSuccess(test)

    def addSubTest(self, test, subtest, error):
        status = "success"
        if error is not None:
            status = "failure" if issubclass(error[0], test.failureException) else "error"
            self.outcome(test, status)
        self.active[id(test)]["subtests"].append({"test_id": subtest.id(), "outcome": status})
        super().addSubTest(test, subtest, error)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True)
    parser.add_argument("--cohort", required=True)
    parser.add_argument("tests", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    test_args = args.tests[1:] if args.tests[:1] == ["--"] else args.tests
    if not test_args:
        parser.error("explicit unittest arguments required")
    try:
        target = checked_target(args.out)
        if target.exists():
            raise ValueError("profile output already exists; use a fresh condition directory")
    except (OSError, ValueError) as error:
        parser.error(str(error))
    # `python -m unittest` puts the invocation cwd on sys.path; a script in
    # tests/ does not. Restore that collection behavior, not an ambient PYTHONPATH.
    sys.path[0] = os.getcwd()
    observed = {}
    started = time.perf_counter()

    class RecordingRunner(unittest.TextTestRunner):
        resultclass = TimedResult

        def run(self, suite):
            observed["collected_ids"] = list(identities(suite))
            observed["collection_seconds"] = time.perf_counter() - started
            suite_start = time.perf_counter()
            result = super().run(suite)
            observed["suite_seconds"] = time.perf_counter() - suite_start
            observed["events"] = result.events
            observed["tests_run"] = result.testsRun
            observed["result_successful"] = result.wasSuccessful()
            observed["unattributed_overhead_seconds"] = max(
                0.0, observed["suite_seconds"] - sum(event.get("seconds", 0) for event in result.events)
            )
            return result

    # Capture the standard library's own exit policy, including Python 3.14's
    # no-tests exit 5 and skipped-class behavior; wasSuccessful() alone is weaker.
    try:
        unittest.main(module=None, argv=["python -m unittest", *test_args],
                      testRunner=RecordingRunner, exit=True)
    except SystemExit as outcome:
        if outcome.code is None:
            code = 0
        elif isinstance(outcome.code, int):
            code = int(outcome.code)
        else:
            print(outcome.code, file=sys.stderr)
            code = 1
    else:
        raise RuntimeError("unittest did not apply its requested exit policy")
    observed["successful"] = code == 0
    git = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True)
    try:
        copier = importlib.metadata.version("copier")
    except importlib.metadata.PackageNotFoundError:
        copier = None
    dirty = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True)
    packet = {
        "schema": "l0.unittest-profile/1", "cohort": args.cohort,
        "parent_cohort": os.environ.get("L0_PROFILE_PARENT") or None,
        "condition": os.environ.get("L0_PROFILE_CONDITION") or None,
        "source_dirty": dirty.stdout.splitlines() if dirty.returncode == 0 else None,
        "source_commit": git.stdout.strip() if git.returncode == 0 else None,
        "python": platform.python_version(), "python_executable": sys.executable,
        "copier": copier, "arguments": test_args,
        "exit_code": code, "wall_seconds": time.perf_counter() - started, **observed,
    }
    # Never overwrite retained evidence; privacy/type/link checks apply to all IO.
    with open_artifact(target) as output:
        json.dump(packet, output, indent=2, sort_keys=True)
        output.write("\n")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
