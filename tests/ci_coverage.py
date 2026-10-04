#!/usr/bin/env python3
"""Independent, read-only coverage accounting; never execute a command.

CLI: python3 -B tests/ci_coverage.py [--inventory FILE] [--input FILE|-]
Input JSON: {"expected_source_commit": "<full candidate SHA>", "profiles":
[<l0.unittest-profile/1 packets>], "receipts": [<receipts below>]}.
Output is one l0.coverage-check/1 JSON object on stdout; exit 0 iff valid.
The inventory is a trusted, independently frozen input, NOT candidate discovery.
Split reports are aggregated by logical (cohort, parent_cohort), never filename.

Each shell receipt has exactly these fields (no implicit defaults):
{"unit": "<inventory shell unit>", "source_commit": "<candidate SHA>",
 "source_dirty": [], "capture": {"schema": "l0.profile-command/1",
 "command": ["sh", "<repo-relative script>", "<optional literal unit>"],
 "exit_code": 0, "child_exit_code": 0, "raw_child_returncode": 0,
 "interrupted_signal": null, "output_complete": true, "io_errors": [],
 "error": null, "teardown": {"process_group_gone": true,
 "final_drain_limited": false, "drain_errors": []}}}.
Commands must be the inventory's exact canonical tokens; no absolute-path or
wrapper normalization. Extra capture/teardown diagnostic fields are permitted.
Receipts are INPUT ASSERTIONS, not host-authenticity or assertion-execution proof.
Synthetic acceptance proves only accounting logic. Performance and product
equivalence remain unproven, even on acceptance. guardrails-static is planned;
missing its receipt is red, not waived by a source hash or synthetic spy.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import json
from pathlib import Path
import sys

# Imports must not create source-tree bytecode, including dependencies.
sys.dont_write_bytecode = True
if __package__:
    from .ci_reorder import validate_ledger
else:
    from ci_reorder import validate_ledger

OWNER_METHOD = ("tests.test_l1_template_ownership.L1TemplateOwnershipTests."
                "test_base_to_candidate_answer_template_upgrade_suite")
COHORTS = {("guardrails-main", None), ("guardrails-system4d", None),
           ("guardrails-generation-units", None), ("guardrails-ci-planning", None), ("generation-main", None),
           ("generation-upgrade", "generation-main"),
           ("guardrails-ci-static", None), ("guardrails-ci-candidate", None)}
SHELL_COMMANDS = {
    "guardrails-static": ["sh", "tests/ci_guardrails_static.sh"],
    "doc-references": ["sh", "scripts/check-doc-references.sh"],
    "session-checkpoint": ["sh", "scripts/check-session-checkpoint.sh"],
    "supply-chain": ["sh", "scripts/check-supply-chain.sh"],
    "adversarial": ["sh", "scripts/check-l0-adversarial.sh"],
    "fixtures": ["sh", "scripts/check-l0-fixtures.sh"],
    **{unit: ["sh", "tests/ci_generation_unit.sh", unit] for unit in
       ("profile-community", "profile-release", "profile-vouch", "profile-compact", "sample-shell")},
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def text(value):
    return isinstance(value, str) and bool(value)


def digest(value, length):
    return (isinstance(value, str) and len(value) == length
            and all(c in "0123456789abcdef" for c in value))


def integer(value, minimum=0):
    return type(value) is int and value >= minimum


def result(errors, **fields):
    return {"schema": "l0.coverage-check/1", "valid": not errors, "errors": errors,
            "performance_proven": False, "product_equivalence_proven": False,
            "host_authenticity_proven": False, "assertion_execution_proven": False,
            "scope": "independent frozen coverage and explicit receipt assertions only", **fields}


def expand_inventory(inventory):
    """Lossless explicit origin-reference bundles; no ID or raw-suffix rewriting.

    Every alias supplies all three required method fields. Rows may override only
    subtests with their explicit literal array. No implicit success/empty defaults.
    The expanded manifest retains the original strict field/type checks below.
    """
    if not isinstance(inventory, dict) or "origin_references" not in inventory:
        return inventory
    inventory = deepcopy(inventory)
    references = inventory.pop("origin_references")
    inputs = inventory.get("inputs")
    require(isinstance(references, dict) and bool(references)
            and isinstance(inputs, dict), "inventory origin reference table")
    for alias, fields in references.items():
        require(text(alias) and alias.startswith("@") and alias not in inputs
                and isinstance(fields, dict) and set(fields) == {"origin", "outcome", "subtests"},
                "inventory origin reference fields")
        require(text(fields["origin"]) and fields["origin"] in inputs
                and fields["outcome"] == "success" and fields["subtests"] == []
                and type(fields["subtests"]) is list, "inventory origin reference values")
    cohorts = inventory.get("cohorts")
    require(isinstance(cohorts, list), "inventory reference cohorts")
    used = set()
    for cohort in cohorts:
        require(isinstance(cohort, dict) and isinstance(cohort.get("methods"), list),
                "inventory reference methods")
        for row in cohort["methods"]:
            require(isinstance(row, dict), "inventory reference method shape")
            origin = row.get("origin")
            if isinstance(origin, str) and origin.startswith("@"):
                require(origin in references and set(row) in ({"id", "origin"},
                        {"id", "origin", "subtests"}), "inventory unknown/malformed origin reference")
                used.add(origin)
                explicit = {k: v for k, v in row.items() if k != "origin"}
                row.clear()
                row.update(deepcopy(references[origin]))
                row.update(explicit)
    require(used == set(references), "inventory unused origin reference")
    return inventory


def inventory_counters(inventory):
    """Check the complete manifest before trusting any candidate packet."""
    inventory = expand_inventory(inventory)
    require(isinstance(inventory, dict), "inventory must be an object")
    require(inventory.get("schema") == "l0.coverage-inventory/1", "inventory schema")
    require(inventory.get("fixture_count") == 0 and type(inventory.get("fixture_count")) is int,
            "inventory must explicitly require zero fixtures")
    for key in ("expected_root_count", "expected_nested_count"):
        require(integer(inventory.get(key), 1), f"inventory {key}")
    inputs = inventory.get("inputs")
    require(isinstance(inputs, dict) and bool(inputs), "inventory input provenance missing")
    for name, source in inputs.items():
        require(text(name) and isinstance(source, dict), "inventory input shape")
        require(text(source.get("path")) and digest(source.get("sha256"), 64)
                and digest(source.get("source_commit"), 40), f"inventory input provenance: {name}")
    cohorts = inventory.get("cohorts")
    require(isinstance(cohorts, list) and len(cohorts) == len(COHORTS), "inventory cohorts incomplete")
    expected, nested_owners = {}, {}
    roots = nested = 0
    for cohort in cohorts:
        require(isinstance(cohort, dict), "inventory cohort shape")
        require(text(cohort.get("cohort")) and "parent_cohort" in cohort
                and (cohort["parent_cohort"] is None or text(cohort["parent_cohort"])),
                "inventory cohort/parent shape")
        key = (cohort["cohort"], cohort["parent_cohort"])
        require(key in COHORTS and key not in expected, "inventory unknown/duplicate cohort or parent")
        rows = cohort.get("methods")
        require(isinstance(rows, list) and bool(rows), f"inventory methods absent: {key}")
        ids, outcomes, subs = Counter(), Counter(), Counter()
        for row in rows:
            require(isinstance(row, dict) and text(row.get("id")), "inventory method shape")
            require(row.get("outcome") == "success", "inventory method outcome must be success")
            require(text(row.get("origin")) and row["origin"] in inputs, "inventory method provenance")
            method = row["id"]
            ids[method] += 1
            outcomes[method, row["outcome"]] += 1
            suffixes = row.get("subtests")
            require(isinstance(suffixes, list), "inventory raw suffix expectations missing")
            for sub in suffixes:
                require(isinstance(sub, list) and len(sub) == 2 and text(sub[0])
                        and sub[0].startswith(" ") and sub[1] in {"success", "skip"},
                        "inventory raw suffix/outcome shape")
                subs[method, method + sub[0], sub[1]] += 1
        expected[key] = (ids, outcomes, subs)
        if key[1] is None:
            roots += len(rows)
            require("parent_method" in cohort and cohort["parent_method"] is None,
                    "root inventory parent_method must be null")
        else:
            nested += len(rows)
            require(cohort.get("parent_method") == OWNER_METHOD, "nested ownership method binding")
            nested_owners[key] = cohort["parent_method"]
    require(set(expected) == COHORTS, "inventory cohort set incomplete")
    require(roots == inventory["expected_root_count"] and nested == inventory["expected_nested_count"],
            "inventory declared counts do not match frozen methods")
    require(expected[("generation-main", None)][0][OWNER_METHOD] == 1,
            "inventory ownership parent method absent/duplicated")
    shell = inventory.get("shell_units")
    require(isinstance(shell, list) and len(shell) == len(SHELL_COMMANDS), "inventory shell units incomplete")
    commands = {}
    for row in shell:
        require(isinstance(row, dict) and text(row.get("unit")), "inventory shell unit shape")
        unit = row["unit"]
        require(unit in SHELL_COMMANDS and unit not in commands, "inventory shell unit unknown/duplicate")
        require(row.get("command") == SHELL_COMMANDS[unit], f"inventory shell command: {unit}")
        commands[unit] = row["command"]
    return expected, nested_owners, commands


def profile_counters(packet, sha):
    require(isinstance(packet, dict), "profile must be an object")
    require(packet.get("schema") == "l0.unittest-profile/1", "profile schema")
    require(text(packet.get("cohort")) and "parent_cohort" in packet
            and (packet["parent_cohort"] is None or text(packet["parent_cohort"])), "profile cohort/parent shape")
    key = (packet["cohort"], packet["parent_cohort"])
    require(key in COHORTS, "unknown profile cohort/parent")
    require(packet.get("source_commit") == sha and packet.get("source_dirty") == [],
            "profile source identity/dirty mismatch")
    require(isinstance(packet.get("arguments"), list) and bool(packet["arguments"])
            and all(text(a) for a in packet["arguments"]), "profile arguments shape")
    require(type(packet.get("exit_code")) is int and packet["exit_code"] == 0
            and packet.get("successful") is True and packet.get("result_successful") is True,
            "profile exit/success status")
    require(isinstance(packet.get("events"), list), "profile events shape")
    ids, outcomes, subs = Counter(), Counter(), Counter()
    for event in packet["events"]:
        require(isinstance(event, dict) and event.get("kind") == "test", "fixture or malformed event")
        require(text(event.get("test_id")) and event.get("outcome") == "success", "method identity/outcome")
        require(integer(event.get("ordinal"), 1), "method ordinal shape")
        require(isinstance(event.get("subtests"), list), "raw subtests missing/malformed")
        method = event["test_id"]
        ids[method] += 1
        outcomes[method, event["outcome"]] += 1
        for sub in event["subtests"]:
            require(isinstance(sub, dict) and text(sub.get("test_id"))
                    and sub["test_id"].startswith(method + " ")
                    and sub.get("outcome") in {"success", "skip"}, "raw subtest identity/outcome")
            subs[method, sub["test_id"], sub["outcome"]] += 1
    ledger = validate_ledger(packet)
    require(ledger["valid"] and ledger["coverage_complete"], f"invalid/incomplete ledger: {ledger}")
    return key, Counter(packet["collected_ids"]), ids, outcomes, subs


def check_receipt(receipt, commands, sha):
    require(isinstance(receipt, dict) and set(receipt) == {"unit", "source_commit", "source_dirty", "capture"},
            "receipt fields malformed/missing")
    unit = receipt["unit"]
    require(text(unit) and unit in commands, "unknown shell receipt unit")
    require(receipt["source_commit"] == sha and receipt["source_dirty"] == [], "receipt source identity/dirty mismatch")
    capture = receipt["capture"]
    require(isinstance(capture, dict) and capture.get("schema") == "l0.profile-command/1", "receipt capture schema")
    require(capture.get("command") == commands[unit], "receipt command mismatch")
    for key in ("exit_code", "child_exit_code", "raw_child_returncode"):
        require(type(capture.get(key)) is int and capture[key] == 0, f"receipt {key} must be integer zero")
    for key, wanted in (("interrupted_signal", None), ("output_complete", True),
                        ("io_errors", []), ("error", None)):
        require(key in capture and type(capture[key]) is type(wanted) and capture[key] == wanted,
                f"receipt {key} missing/non-success")
    teardown = capture.get("teardown")
    require(isinstance(teardown, dict), "receipt teardown missing")
    for key, wanted in (("process_group_gone", True), ("final_drain_limited", False), ("drain_errors", [])):
        require(key in teardown and type(teardown[key]) is type(wanted) and teardown[key] == wanted,
                f"receipt teardown {key} missing/non-success")
    return unit


def difference(expected, actual):
    def rows(counter):
        return [{"value": key, "count": count} for key, count in sorted(counter.items())]
    return {"missing": rows(expected - actual), "extra": rows(actual - expected)}


def receipt_accounting(receipts, commands, sha):
    errors, units = [], Counter()
    require(isinstance(receipts, list), "receipts must be an array")
    for index, receipt in enumerate(receipts):
        try:
            units[check_receipt(receipt, commands, sha)] += 1
        except (ValueError, TypeError, KeyError, AttributeError, OverflowError) as error:
            errors.append(f"receipt[{index}]: {error}")
    wanted = Counter({unit: 1 for unit in commands})
    differences = []
    if units != wanted:
        errors.append("shell receipt multiset mismatch (each obligation required exactly once)")
        differences.append({"kind": "shell_receipts", **difference(wanted, units)})
    return errors, differences


def validate_shell_receipts(inventory, receipts, *, expected_source_commit=None):
    """Separately account shell obligations; never substitute unittest/source evidence."""
    try:
        require(digest(expected_source_commit, 40), "required exact full candidate source SHA")
        _, _, commands = inventory_counters(inventory)
        errors, differences = receipt_accounting(receipts, commands, expected_source_commit)
        return result(errors, differences=differences)
    except (ValueError, TypeError, KeyError, AttributeError, OverflowError, RecursionError) as error:
        return result([f"invalid input/inventory: {error}"], differences=[])


def validate_coverage(inventory, profiles, receipts, *, expected_source_commit=None):
    """Return failure data for malformed inputs; no live source, AK or process access.

    Inventory methods contain id, outcome, origin (an inputs key), and subtests
    [[literal RAW suffix, outcome], ...]. Only concatenation reconstructs raw IDs.
    Counts preserve multiplicity within each cohort and across distinct cohorts.
    Caller must supply a trusted complete manifest and an exact full candidate SHA.
    """
    errors, differences = [], []
    try:
        require(digest(expected_source_commit, 40), "required exact full candidate source SHA")
        expected, owners, commands = inventory_counters(inventory)
        require(isinstance(profiles, list) and isinstance(receipts, list), "profiles/receipts must be arrays")
        actual = defaultdict(lambda: [Counter(), Counter(), Counter(), Counter()])
        for index, packet in enumerate(profiles):
            try:
                key, *counters = profile_counters(packet, expected_source_commit)
                for aggregate, counts in zip(actual[key], counters):
                    aggregate.update(counts)
            except (ValueError, TypeError, KeyError, AttributeError, OverflowError) as error:
                errors.append(f"profile[{index}]: {error}")
        for key, (ids, outcomes, subs) in sorted(expected.items(), key=lambda item: item[0][0]):
            for label, wanted, got in zip(("collected", "executed", "method_outcomes", "raw_subtests"),
                                          (ids, ids, outcomes, subs), actual[key]):
                if wanted != got:
                    errors.append(f"{key[0]} / {key[1]}: {label} multiset mismatch")
                    differences.append({"cohort": key[0], "parent_cohort": key[1], "kind": label,
                                        **difference(wanted, got)})
        for key, owner in owners.items():
            if actual[(key[1], None)][2][owner, "success"] != 1:
                errors.append("nested cohort ownership parent method not present/executed exactly once")
        unittest_valid = not errors
        shell_errors, shell_differences = receipt_accounting(receipts, commands, expected_source_commit)
        errors.extend(shell_errors)
        differences.extend(shell_differences)
        return result(errors, differences=differences, unittest_coverage_valid=unittest_valid,
                      shell_receipts_valid=not shell_errors, expected_source_commit=expected_source_commit,
                      expected_root_count=inventory["expected_root_count"],
                      expected_nested_count=inventory["expected_nested_count"],
                      profiles_received=len(profiles), receipts_received=len(receipts))
    except (ValueError, TypeError, KeyError, AttributeError, OverflowError, RecursionError) as error:
        errors.append(f"invalid input/inventory: {error}")
        return result(errors, differences=differences)


def unique_object(pairs):
    obj = {}
    for key, value in pairs:
        require(key not in obj, f"duplicate JSON object key: {key}")
        obj[key] = value
    return obj


def load_json(stream):
    def nonfinite(value):
        raise ValueError(f"non-finite JSON number: {value}")
    value = json.load(stream, object_pairs_hook=unique_object, parse_constant=nonfinite)
    if isinstance(value, dict) and value.get("schema") == "l0.coverage-inventory/1":
        value = expand_inventory(value)
    return value


class JsonArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ValueError(message)


def main(argv=None):
    try:
        parser = JsonArgumentParser(description=__doc__, add_help=False)
        parser.add_argument("--inventory", default=str(Path(__file__).with_name("ci_coverage_inventory.json")))
        parser.add_argument("--input", default="-", help="JSON input file, or stdin")
        args = parser.parse_args(argv)
        with open(args.inventory, encoding="utf-8") as stream:
            inventory = load_json(stream)
        if args.input == "-":
            request = load_json(sys.stdin)
        else:
            with open(args.input, encoding="utf-8") as stream:
                request = load_json(stream)
        require(isinstance(request, dict) and set(request) == {"expected_source_commit", "profiles", "receipts"},
                "input must contain exactly expected_source_commit, profiles, receipts")
        packet = validate_coverage(inventory, request["profiles"], request["receipts"],
                                   expected_source_commit=request["expected_source_commit"])
    except (OSError, ValueError, TypeError, KeyError, UnicodeError, RecursionError) as error:
        packet = result([f"input error: {error}"])
    print(json.dumps(packet, sort_keys=True, allow_nan=False))
    return 0 if packet["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
