"""Small independent fixtures; no candidate collection or unittest.subTest.

Fast STEP3 contracts for STEP1's independently frozen checker.
Synthetic acceptance establishes accounting behavior, not product execution.
"""
from copy import deepcopy
import contextlib
import io
import json
import unittest
from unittest import mock

from tests import ci_coverage as checker

SHA = "1" * 40
OWNER = ("tests.test_l1_template_ownership.L1TemplateOwnershipTests."
         "test_base_to_candidate_answer_template_upgrade_suite")
SHARED = "example.Case.test_shared"
RAW = " (path='/scratch/literal', callback=<function f.<locals>.<lambda> at 0xABC>)"
# Hand-authored expected command literals, independent of the implementation map.
COMMANDS = [
    ("guardrails-static", ["sh", "tests/ci_guardrails_static.sh"]),
    ("doc-references", ["sh", "scripts/check-doc-references.sh"]),
    ("session-checkpoint", ["sh", "scripts/check-session-checkpoint.sh"]),
    ("supply-chain", ["sh", "scripts/check-supply-chain.sh"]),
    ("profile-community", ["sh", "tests/ci_generation_unit.sh", "profile-community"]),
    ("profile-release", ["sh", "tests/ci_generation_unit.sh", "profile-release"]),
    ("profile-vouch", ["sh", "tests/ci_generation_unit.sh", "profile-vouch"]),
    ("profile-compact", ["sh", "tests/ci_generation_unit.sh", "profile-compact"]),
    ("sample-shell", ["sh", "tests/ci_generation_unit.sh", "sample-shell"]),
    ("adversarial", ["sh", "scripts/check-l0-adversarial.sh"]),
    ("fixtures", ["sh", "scripts/check-l0-fixtures.sh"]),
]


def row(method, subs=None):
    return {"id": method, "outcome": "success", "origin": "independent",
            "subtests": [] if subs is None else subs}


def manifest():
    # Expectations are literals written independently, never from packet collection.
    return {
        "schema": "l0.coverage-inventory/1", "fixture_count": 0,
        "expected_root_count": 6, "expected_nested_count": 1,
        "inputs": {"independent": {"path": "frozen/synthetic.json",
                                   "sha256": "a" * 64, "source_commit": "b" * 40}},
        "cohorts": [
            {"cohort": "guardrails-main", "parent_cohort": None, "parent_method": None,
             "methods": [row(SHARED), row("example.Case.test_raw", [[RAW, "success"], [" (case='skip')", "skip"]])]},
            {"cohort": "guardrails-system4d", "parent_cohort": None, "parent_method": None,
             "methods": [row(SHARED)]},
            {"cohort": "guardrails-generation-units", "parent_cohort": None, "parent_method": None,
             "methods": [row("example.Seam.test_route")]},
            {"cohort": "guardrails-ci-planning", "parent_cohort": None, "parent_method": None,
             "methods": [row("example.Planning.test_route")]},
            {"cohort": "generation-main", "parent_cohort": None, "parent_method": None,
             "methods": [row(OWNER)]},
            {"cohort": "generation-upgrade", "parent_cohort": "generation-main", "parent_method": OWNER,
             "methods": [row("example.Upgrade.test_render")]},
        ],
        "shell_units": [{"unit": unit, "command": command[:]} for unit, command in COMMANDS],
    }


def event(method, ordinal=1, subs=None):
    return {"kind": "test", "test_id": method, "ordinal": ordinal, "outcome": "success",
            "subtests": [] if subs is None else subs}


def profile(cohort, ids, events, parent=None):
    return {"schema": "l0.unittest-profile/1", "cohort": cohort, "parent_cohort": parent,
            "source_commit": SHA, "source_dirty": [], "arguments": ["example"],
            "collected_ids": ids, "events": events, "tests_run": len(events),
            "exit_code": 0, "successful": True, "result_successful": True}


def packets():
    # Explicit execution data; this helper does not read or derive from manifest().
    return [
        profile("guardrails-main", [SHARED, "example.Case.test_raw"],
                [event(SHARED), event("example.Case.test_raw", 2, [
                    {"test_id": "example.Case.test_raw" + RAW, "outcome": "success"},
                    {"test_id": "example.Case.test_raw (case='skip')", "outcome": "skip"}])]),
        profile("guardrails-system4d", [SHARED], [event(SHARED)]),
        profile("guardrails-generation-units", ["example.Seam.test_route"], [event("example.Seam.test_route")]),
        profile("guardrails-ci-planning", ["example.Planning.test_route"], [event("example.Planning.test_route")]),
        profile("generation-main", [OWNER], [event(OWNER)]),
        profile("generation-upgrade", ["example.Upgrade.test_render"],
                [event("example.Upgrade.test_render")], "generation-main"),
    ]


def receipts():
    return [{"unit": unit, "source_commit": SHA, "source_dirty": [],
             "capture": {"schema": "l0.profile-command/1", "command": command[:],
                         "exit_code": 0, "child_exit_code": 0, "raw_child_returncode": 0,
                         "interrupted_signal": None, "output_complete": True, "io_errors": [],
                         "error": None, "teardown": {"process_group_gone": True,
                         "final_drain_limited": False, "drain_errors": []}}}
            for unit, command in COMMANDS]


class IndependentCoverageTests(unittest.TestCase):
    def check(self, profiles=None, shell=None, inventory=None, sha=SHA):
        return checker.validate_coverage(manifest() if inventory is None else inventory,
                                         packets() if profiles is None else profiles,
                                         receipts() if shell is None else shell,
                                         expected_source_commit=sha)

    def test_literal_independent_coverage_accepts_split_and_crosscohort_multiplicity(self):
        data = packets()
        first = data.pop(0)
        a, b = deepcopy(first), deepcopy(first)
        a.update(collected_ids=[SHARED], events=[event(SHARED)], tests_run=1)
        b.update(collected_ids=["example.Case.test_raw"], events=[deepcopy(first["events"][1])], tests_run=1)
        b["events"][0]["ordinal"] = 1
        data.extend([b, a])
        result = self.check(data)
        self.assertTrue(result["valid"], result)
        self.assertTrue(result["unittest_coverage_valid"])
        self.assertTrue(result["shell_receipts_valid"])
        for flag in ("performance_proven", "product_equivalence_proven", "host_authenticity_proven", "assertion_execution_proven"):
            self.assertIs(result[flag], False)
        self.assertTrue(checker.validate_shell_receipts(manifest(), receipts(), expected_source_commit=SHA)["valid"])
        # A trusted explicit repeated-method obligation must not be deduplicated.
        inv, repeated = manifest(), packets()
        inv["expected_root_count"] = 7
        inv["cohorts"][0]["methods"].append(row(SHARED))
        repeated[0]["collected_ids"].append(SHARED)
        repeated[0]["events"].append(event(SHARED, 3))
        repeated[0]["tests_run"] = 3
        self.assertTrue(self.check(repeated, inventory=inv)["valid"])
        self.assertFalse(self.check(inventory=inv)["valid"])

    def test_matching_omission_and_empty_profiles_never_define_expected_coverage(self):
        omitted = packets()[1:]
        # Even two identical incomplete conditions each fail the independent oracle.
        for condition in (omitted, deepcopy(omitted), [], packets()[:-1]):
            self.assertFalse(self.check(condition)["valid"])
        data = packets()
        data[0].update(collected_ids=[SHARED], events=[event(SHARED)], tests_run=1)
        self.assertFalse(self.check(data)["valid"])
        data = packets() + [profile("guardrails-main", [], [])]
        self.assertFalse(self.check(data)["valid"])

    def test_extra_duplicate_unknown_methods_and_logical_cohort_parent_are_red(self):
        for kind in ("extra", "duplicate", "unknown-method", "unknown-cohort", "wrong-parent", "duplicate-report"):
            data = packets()
            if kind == "duplicate-report":
                data.append(deepcopy(data[0]))
            elif kind in ("extra", "duplicate"):
                method = SHARED if kind == "duplicate" else "example.Case.test_extra"
                data[0]["collected_ids"].append(method)
                data[0]["events"].append(event(method, 3))
                data[0]["tests_run"] = 3
            elif kind == "unknown-method":
                data[1]["collected_ids"] = ["unknown.Case.test_case"]
                data[1]["events"] = [event("unknown.Case.test_case")]
            elif kind == "unknown-cohort":
                data[0]["cohort"] = "unknown"
            else:
                data[5]["parent_cohort"] = None
            self.assertFalse(self.check(data)["valid"], kind)
        # Removing only one of the intentional cross-cohort occurrences is red.
        self.assertFalse(self.check(packets()[:1] + packets()[2:])["valid"])

    def test_raw_subtest_identity_outcome_multiplicity_and_parent_are_exact(self):
        for kind in ("path", "lambda", "missing", "extra", "duplicate", "outcome", "parent", "malformed", "failure", "error", "unknown-outcome", "missing-outcome"):
            data = packets()
            subs = data[0]["events"][1]["subtests"]
            if kind in ("path", "lambda"):
                subs[0]["test_id"] = subs[0]["test_id"].replace("/scratch/literal", "/scratch/other") if kind == "path" else subs[0]["test_id"].replace("0xABC", "0xDEF")
            elif kind == "missing":
                subs.pop()
            elif kind in ("extra", "duplicate"):
                subs.append({"test_id": "example.Case.test_raw (extra=True)", "outcome": "success"} if kind == "extra" else deepcopy(subs[0]))
            elif kind == "outcome":
                subs[0]["outcome"] = "skip"
            elif kind == "parent":
                subs[0]["test_id"] = SHARED + RAW
            elif kind in ("failure", "error", "unknown-outcome"):
                subs[0]["outcome"] = kind
            elif kind == "missing-outcome":
                del subs[0]["outcome"]
            else:
                data[0]["events"][1]["subtests"] = None
            self.assertFalse(self.check(data)["valid"], kind)

    def test_schema_counts_ordinals_collection_exit_fixture_and_method_outcomes(self):
        cases = [("schema", "other"), ("tests_run", 1), ("tests_run", True),
                 ("exit_code", -1), ("exit_code", 1), ("exit_code", False),
                 ("successful", 1), ("result_successful", False), ("collected_ids", []),
                 ("collected_ids", None), ("events", {}), ("arguments", None), ("arguments", [])]
        for field, value in cases:
            data = packets(); data[0][field] = value
            self.assertFalse(self.check(data)["valid"], field)
        for ordinal in (0, 1, 3, True, None):
            data = packets(); data[0]["events"][1]["ordinal"] = ordinal
            self.assertFalse(self.check(data)["valid"])
        for outcome in ("skip", "failure", "error", "expected_failure", "unexpected_success", [], None):
            data = packets(); data[0]["events"][0]["outcome"] = outcome
            self.assertFalse(self.check(data)["valid"])
        for outcome in ("skip", "failure", "error"):
            data = packets(); data[0]["events"].append({"kind": "fixture", "test_id": "setUpClass (example.Case)", "outcome": outcome, "subtests": []})
            self.assertFalse(self.check(data)["valid"])
        data = packets(); del data[0]["parent_cohort"]
        self.assertFalse(self.check(data)["valid"])

    def test_exact_candidate_source_required_for_every_profile_and_receipt(self):
        for sha in (None, "", "1" * 7, "G" * 40, SHA.upper().replace("1", "A"), [], False):
            self.assertFalse(self.check(sha=sha)["valid"])
        for target in ("profile", "receipt"):
            for field, value in (("source_commit", "2" * 40), ("source_commit", None),
                                 ("source_dirty", ["?? changed"]), ("source_dirty", None), ("source_dirty", False)):
                data, shell = packets(), receipts()
                (data if target == "profile" else shell)[0][field] = value
                self.assertFalse(self.check(data, shell)["valid"], (target, field))

    def test_nested_upgrade_requires_executed_bound_ownership_method(self):
        data = packets(); data[4] = profile("generation-main", [OWNER], [])
        self.assertFalse(self.check(data)["valid"])
        data = packets(); data[4] = profile("generation-main", ["other.Owner.test_case"], [event("other.Owner.test_case")])
        self.assertFalse(self.check(data)["valid"])
        data = packets(); data[5]["parent_cohort"] = "guardrails-main"
        self.assertFalse(self.check(data)["valid"])
        inv = manifest(); inv["cohorts"][5]["parent_method"] = "other.Owner.test_case"
        self.assertFalse(self.check(inventory=inv)["valid"])

    def test_shell_receipts_are_separate_required_exact_once_and_command_bound(self):
        missing = self.check(shell=[])
        self.assertFalse(missing["valid"])
        self.assertTrue(missing["unittest_coverage_valid"])
        self.assertFalse(missing["shell_receipts_valid"])
        for kind in ("missing", "duplicate", "unknown", "command", "absolute", "wrapper", "extra-field"):
            shell = receipts()
            if kind == "missing": shell.pop(0)  # Planned guardrails-static is NOT waived.
            elif kind == "duplicate": shell.append(deepcopy(shell[0]))
            elif kind == "unknown": shell[0]["unit"] = "source-hash-spy"
            elif kind == "command": shell[0]["capture"]["command"] = ["sh", "true"]
            elif kind == "absolute": shell[0]["capture"]["command"][1] = "/repo/tests/ci_guardrails_static.sh"
            elif kind == "wrapper": shell[0]["capture"]["command"].insert(0, "timeout")
            else: shell[0]["synthetic_spy_passed"] = True
            self.assertFalse(self.check(shell=shell)["valid"], kind)
            self.assertFalse(checker.validate_shell_receipts(manifest(), shell, expected_source_commit=SHA)["valid"])

    def test_capture_rejects_failure_cancellation_truncation_orphans_and_missing_fields(self):
        mutations = [("schema", "wrong"), ("exit_code", -1), ("exit_code", False),
                     ("child_exit_code", 1), ("raw_child_returncode", -15),
                     ("interrupted_signal", 15), ("interrupted_signal", 0),
                     ("output_complete", False), ("output_complete", 1),
                     ("io_errors", ["read failed"]), ("error", "cancelled"),
                     ("teardown", None)]
        for field, value in mutations:
            shell = receipts(); shell[0]["capture"][field] = value
            self.assertFalse(self.check(shell=shell)["valid"], field)
        for field, value in (("process_group_gone", False), ("process_group_gone", 1),
                             ("final_drain_limited", True), ("final_drain_limited", 0), ("drain_errors", ["orphan"])):
            shell = receipts(); shell[0]["capture"]["teardown"][field] = value
            self.assertFalse(self.check(shell=shell)["valid"], field)
        for level in ("receipt", "capture", "teardown"):
            template = receipts()[0]
            fields = template if level == "receipt" else template["capture"] if level == "capture" else template["capture"]["teardown"]
            for field in fields:
                shell = receipts()
                obj = shell[0] if level == "receipt" else shell[0]["capture"] if level == "capture" else shell[0]["capture"]["teardown"]
                del obj[field]
                self.assertFalse(self.check(shell=shell)["valid"], (level, field))

    def test_incomplete_malformed_inventory_and_packets_return_data_not_exceptions(self):
        for kind in ("schema", "cohort", "duplicate-cohort", "method", "suffix", "outcome", "origin",
                     "digest", "source", "counts", "fixture", "shell", "duplicate-shell", "command"):
            inv = manifest()
            if kind == "schema": inv["schema"] = "draft"
            elif kind == "cohort": inv["cohorts"].pop()
            elif kind == "duplicate-cohort": inv["cohorts"][1] = deepcopy(inv["cohorts"][0])
            elif kind == "method": inv["cohorts"][0]["methods"].pop()
            elif kind == "suffix": inv["cohorts"][0]["methods"][1]["subtests"] = [["normalized", "success"]]
            elif kind == "outcome": inv["cohorts"][0]["methods"][0]["outcome"] = "skip"
            elif kind == "origin": inv["cohorts"][0]["methods"][0]["origin"] = "unknown"
            elif kind == "digest": inv["inputs"]["independent"]["sha256"] = "x"
            elif kind == "source": inv["inputs"]["independent"]["source_commit"] = "x"
            elif kind == "counts": inv["expected_root_count"] = True
            elif kind == "fixture": inv["fixture_count"] = False
            elif kind == "shell": inv["shell_units"].pop()
            elif kind == "duplicate-shell": inv["shell_units"][1] = deepcopy(inv["shell_units"][0])
            else: inv["shell_units"][0]["command"] = ["true"]
            self.assertFalse(self.check(inventory=inv)["valid"], kind)
        for malformed in (None, [], "bad", 1, {"schema": "l0.coverage-inventory/1"}):
            self.assertFalse(checker.validate_coverage(malformed, packets(), receipts(), expected_source_commit=SHA)["valid"])
        for malformed in (None, [], "bad", 1, {"cohort": []}):
            self.assertFalse(self.check(profiles=[malformed])["valid"])
            self.assertFalse(self.check(shell=[malformed])["valid"])
        self.assertFalse(self.check(profiles={})["valid"])
        self.assertFalse(self.check(shell={})["valid"])

    def test_readonly_json_cli_emits_accounting_and_malformed_input_failures(self):
        request = {"expected_source_commit": SHA, "profiles": packets(), "receipts": receipts()}
        for raw, valid in ((json.dumps(request), True), ("{", False), ("[]", False),
                           ('{"profiles":[],"profiles":[]}', False), ('{"x":NaN}', False),
                           (json.dumps({"profiles": packets(), "receipts": receipts()}), False)):
            output = io.StringIO()
            with mock.patch("builtins.open", return_value=io.StringIO(json.dumps(manifest()))) as reader, \
                    mock.patch.object(checker.sys, "stdin", io.StringIO(raw)), \
                    contextlib.redirect_stdout(output):
                code = checker.main(["--inventory", "independent.json"])
            packet = json.loads(output.getvalue())
            self.assertEqual(packet["valid"], valid, packet)
            self.assertEqual(code, 0 if valid else 1)
            reader.assert_called_once_with("independent.json", encoding="utf-8")
        for flag in ("--unknown-option", "--help", "--execute"):
            with contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(checker.main([flag]), 1)
            self.assertFalse(json.loads(output.getvalue())["valid"])


if __name__ == "__main__":
    unittest.main()
