"""Fast STEP3 routing contracts; run through pinned Copier9.11.1 Python.

Use uvx --from copier==9.11.1 python -B -m unittest tests.test_ci_schedule.
Synthetic mutation/spy checks establish preparation behavior only. The last
check collects actual literal selectors, preserving imports and load_tests, but
never runs a product body or fixture. No unittest.subTest or real processes.
"""
from collections import Counter, defaultdict
from copy import deepcopy
import contextlib
import io
import json
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest import mock

sys.dont_write_bytecode = True
from tests import ci_schedule as schedule

ROOT = Path(__file__).resolve().parents[1]
SHARED = ("tests.test_l1_template_company_ownership.CompanyOntologyTests."
          "test_legacy_plans_stay_nonempty_and_map_v2_refuses_unknown_or_overlapping_classes")
SYNTHETIC_PLANNING = "tests.test_ci_schedule.SyntheticCase.test_contract"


def frozen_inputs():
    # Independent frozen data, NOT loader/candidate-derived expectations.
    plan = json.loads((ROOT / "tests/ci_schedule.json").read_text())
    inventory = json.loads((ROOT / "tests/ci_coverage_inventory.json").read_text())
    return plan, inventory


def synthetic_inputs():
    plan, inventory = frozen_inputs()
    # Replace only the parent-owned future planning expectation with one literal
    # synthetic ID. This isn't an assertion that this synthetic case is importable.
    previous = [c for c in inventory["cohorts"] if c["cohort"] == schedule.PLANNING]
    if previous:
        inventory["expected_root_count"] -= len(previous[0]["methods"])
        inventory["cohorts"].remove(previous[0])
    inventory["inputs"]["synthetic-planning"] = {
        "path": "independent/synthetic-planning.json", "sha256": "a" * 64, "source_commit": "b" * 40}
    inventory["expected_root_count"] += 1
    inventory["cohorts"].append({"cohort": "guardrails-ci-planning", "parent_cohort": None,
        "parent_method": None, "methods": [{"id": SYNTHETIC_PLANNING,
        "outcome": "success", "subtests": [], "origin": "synthetic-planning"}]})
    return plan, inventory


def unit(plan, name):
    return next(u for u in plan["units"] if u["unit"] == name)


def collected_ids(suite):
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            yield from collected_ids(test)
        else:
            yield test.id()


class ScheduleContractTests(unittest.TestCase):
    def assert_rejected(self, plan, inventory):
        packet = schedule.validate_schedule(plan, inventory)
        self.assertFalse(packet["valid"], packet)
        self.assertTrue(packet["errors"])
        self.assertIs(packet["ready_for_hosted"], False)
        with self.assertRaises(ValueError):
            schedule.worker_commands(plan, inventory, 1)

    def test_closed_assignment_preserves_independent_multisets_and_nested_parent(self):
        plan, inventory = synthetic_inputs()
        saved = deepcopy((plan, inventory))
        result = schedule.validate_schedule(plan, inventory)
        self.assertTrue(result["valid"], result)
        self.assertEqual(result["root_methods_assigned"], 213)
        self.assertEqual(result["nested_methods_assigned"], 2)
        self.assertEqual(result["shell_units_assigned"], 11)
        self.assertIs(result["planning_inventory_pending"], False)
        self.assertIs(result["ready_for_hosted"], False)
        self.assertIs(result["performance_proven"], False)
        self.assertIs(result["coverage_execution_proven"], False)
        assigned = Counter(a["unit"] for w in plan["workers"] for a in w["assignments"])
        self.assertEqual(len(assigned), 31)
        self.assertEqual(set(assigned.values()), {1})
        self.assertEqual(len(unit(plan, "Gf")["methods"]), 121)
        self.assertEqual(len(unit(plan, "Mf")["methods"]), 31)
        self.assertIn(SHARED, unit(plan, "Gf")["methods"])
        self.assertIn(SHARED, unit(plan, "Mf")["methods"])
        self.assertEqual(unit(plan, "UPG")["nested"][0]["parent_method"], schedule.OWNER)
        for worker in range(1, 7):
            self.assertTrue(schedule.worker_commands(plan, inventory, worker))
        self.assertEqual((plan, inventory), saved)

    def test_missing_excess_double_and_unknown_units_or_assignments_are_rejected(self):
        for kind in ("missing-unit", "extra-unit", "duplicate-unit", "unknown-unit",
                     "missing-assignment", "double-assignment", "unknown-assignment", "intact-python"):
            plan, inventory = synthetic_inputs()
            if kind == "missing-unit": plan["units"].pop()
            elif kind == "extra-unit":
                extra = deepcopy(plan["units"][0]); extra["unit"] = "extra"; plan["units"].append(extra)
            elif kind == "duplicate-unit": plan["units"].append(deepcopy(plan["units"][0]))
            elif kind in ("unknown-unit", "intact-python"):
                plan["units"][0]["unit"] = "unknown" if kind == "unknown-unit" else "generation-python"
            elif kind == "missing-assignment": plan["workers"][0]["assignments"].pop()
            else:
                plan["workers"][0]["assignments"][0]["unit"] = "UPG" if kind == "double-assignment" else "unknown"
            self.assert_rejected(plan, inventory)

    def test_worker_membership_and_order_are_strict_integers_not_booleans(self):
        for value in (True, False, 0, 7, "1", 1.0, None):
            plan, inventory = synthetic_inputs(); plan["workers"][0]["worker"] = value
            self.assert_rejected(plan, inventory)
            with self.assertRaises(ValueError): schedule.worker_commands(*synthetic_inputs(), value)
        for value in (True, False, 0, 2, "1", 1.0, None):
            plan, inventory = synthetic_inputs(); plan["workers"][0]["assignments"][0]["order"] = value
            self.assert_rejected(plan, inventory)
        for kind in ("missing", "extra", "duplicate", "reordered"):
            plan, inventory = synthetic_inputs()
            if kind == "missing": plan["workers"].pop()
            elif kind == "extra": plan["workers"].append(deepcopy(plan["workers"][0]))
            elif kind == "duplicate": plan["workers"][0]["worker"] = 2
            else: plan["workers"][0]["assignments"].reverse()
            self.assert_rejected(plan, inventory)

    def test_selector_runtime_command_and_cohort_swaps_are_rejected(self):
        for field, value in (("selectors", ["tests.test_ci_reorder"]),
                             ("selectors", ["discover", "-s", "tests"]),
                             ("runtime", "python3"), ("cohort", "generation-main"),
                             ("parent_cohort", "generation-main"),
                             ("command", ["sh", "scripts/check-l0.sh"]),
                             ("kind", "shell"), ("route", "implemented")):
            plan, inventory = synthetic_inputs(); unit(plan, "Gf")[field] = value
            self.assert_rejected(plan, inventory)
        for name in ("UPG", "seam", "planning", "SYS"):
            plan, inventory = synthetic_inputs(); unit(plan, name)["runtime"] = "pinned-9.11.1" if name == "UPG" else "python3"
            self.assert_rejected(plan, inventory)
        plan, inventory = synthetic_inputs()
        unit(plan, "sample-shell")["command"] = ["sh", "tests/ci_generation_unit.sh", "profile-community"]
        self.assert_rejected(plan, inventory)

    def test_method_omissions_duplicates_unknown_and_intra_cohort_swaps_are_rejected(self):
        for kind in ("missing", "duplicate", "unknown", "swap", "crosscohort"):
            plan, inventory = synthetic_inputs()
            if kind == "missing": unit(plan, "Mf")["methods"].pop()
            elif kind == "duplicate": unit(plan, "Mf")["methods"].append(unit(plan, "Mf")["methods"][0])
            elif kind == "unknown": unit(plan, "Gf")["methods"].append("tests.test_ci_profile.Unknown.test_extra")
            elif kind == "crosscohort": unit(plan, "Mf")["methods"].remove(SHARED)
            else:
                a, b = unit(plan, "R1"), unit(plan, "R3")
                a["methods"], b["methods"] = b["methods"], a["methods"]
            self.assert_rejected(plan, inventory)

    def test_nested_upgrade_is_only_report_bound_to_whole_history_parent(self):
        for kind in ("missing", "duplicate", "parent", "owner", "method-missing", "method-extra", "independent"):
            plan, inventory = synthetic_inputs(); upg = unit(plan, "UPG")
            if kind == "missing": upg["nested"] = []
            elif kind == "duplicate": upg["nested"].append(deepcopy(upg["nested"][0]))
            elif kind == "parent": upg["nested"][0]["parent_cohort"] = "guardrails-main"
            elif kind == "owner": upg["nested"][0]["parent_method"] = SHARED
            elif kind == "method-missing": upg["nested"][0]["methods"].pop()
            elif kind == "method-extra": upg["nested"][0]["methods"].append(upg["nested"][0]["methods"][0])
            else: unit(plan, "Mf")["nested"] = deepcopy(upg["nested"])
            self.assert_rejected(plan, inventory)

    def test_cold_setup_aggregation_and_estimate_budget_accounting_is_not_speed_proof(self):
        for field, value in (("cold_setup_ms", 1200000), ("aggregation_ms", 1200000),
                             ("budget_ms", 700000), ("cold_setup_ms", 0),
                             ("cold_setup_ms", True), ("aggregation_ms", -1),
                             ("budget_ms", 1200000.0), ("budget_ms", 1200000),
                             ("cold_setup_ms", 1), ("aggregation_ms", 1)):
            plan, inventory = synthetic_inputs(); plan["workers"][0][field] = value
            self.assert_rejected(plan, inventory)
        for name, value in (("UPG", 1), ("seam", 1999), ("planning", 15001), ("SYS", True)):
            plan, inventory = synthetic_inputs(); unit(plan, name)["estimate_ms"] = value
            self.assert_rejected(plan, inventory)
        plan, inventory = synthetic_inputs()
        result = schedule.validate_schedule(plan, inventory)
        self.assertEqual([w["estimated_ms"] for w in result["worker_estimates"]],
                         [857400, 863000, 848000, 861000, 841000, 843000])
        self.assertIs(result["performance_proven"], False)
        # Reviewer's counterexample: an overloaded worker cannot be made feasible
        # by replacing declared setup/aggregation allowances with one millisecond.
        overloaded, independent = synthetic_inputs()
        moved = overloaded["workers"][0]["assignments"].pop(1)
        for index, entry in enumerate(overloaded["workers"][0]["assignments"], 1):
            entry["order"] = index
        moved["order"] = len(overloaded["workers"][1]["assignments"]) + 1
        overloaded["workers"][1]["assignments"].append(moved)
        self.assert_rejected(overloaded, independent)
        for worker in overloaded["workers"]:
            worker["cold_setup_ms"] = worker["aggregation_ms"] = 1
        self.assert_rejected(overloaded, independent)

    def test_planning_placeholder_accepts_only_independent_future_inventory(self):
        plan, inventory = synthetic_inputs()
        row = inventory["cohorts"].pop()
        inventory["expected_root_count"] -= 1
        # The present checker hasn't landed planning yet. Future checker expects
        # it, so pending validation uses that explicit pre-step3 closed cohort set.
        with mock.patch.object(schedule.coverage, "COHORTS", set(schedule.coverage.COHORTS) - {(schedule.PLANNING, None)}):
            result = schedule.validate_schedule(plan, inventory)
            self.assertTrue(result["valid"], result)
            self.assertIs(result["planning_inventory_pending"], True)
            self.assertEqual(schedule.worker_commands(plan, inventory, 1)[-1]["route"], "inventory-pending")
        self.assertEqual(row["methods"][0]["id"], SYNTHETIC_PLANNING)
        for kind in ("plan-literals", "inventory-empty", "inventory-duplicate", "inventory-unknown"):
            plan, inventory = synthetic_inputs()
            if kind == "plan-literals": unit(plan, "planning")["methods"] = [SYNTHETIC_PLANNING]
            elif kind == "inventory-empty": inventory["cohorts"][-1]["methods"] = []
            elif kind == "inventory-duplicate": inventory["cohorts"].append(deepcopy(inventory["cohorts"][-1]))
            else: inventory["cohorts"][-1]["methods"][0]["id"] = "unknown.Case.test_extra"
            self.assert_rejected(plan, inventory)

    def test_spy_exact_call_order_and_first_failure_aborts_subsequent_units(self):
        plan, inventory = synthetic_inputs(); calls = []
        def spy(command):
            calls.append(command)
            return 0
        result = schedule.route_to_spy(plan, inventory, 3, spy=spy)
        self.assertEqual([c["unit"] for c in calls], ["adversarial", "profile-compact", "Wrapper", "R4"])
        self.assertEqual([c["command"] for c in calls], [
            ["sh", "scripts/check-l0-adversarial.sh"],
            ["sh", "tests/ci_generation_unit.sh", "profile-compact"],
            ["sh", "tests/ci_unittest.sh", "guardrails-main", "pinned",
             "tests.test_company_ontology_ref_inheritance.WrapperTests"],
            ["sh", "tests/ci_unittest.sh", "guardrails-main", "pinned",
             "tests.test_company_ontology_ref_inheritance.RendererTests.test_external_native_uv_actual_pinned_source_birth_without_company_copies"]])
        self.assertEqual([c["order"] for c in calls], [1, 2, 3, 4])
        self.assertIs(result["execution_proven"], False)
        calls.clear()
        def failing(command):
            calls.append(command["unit"])
            return 3 if len(calls) == 2 else 0
        result = schedule.route_to_spy(plan, inventory, 3, spy=failing)
        self.assertEqual(calls, ["adversarial", "profile-compact"])
        self.assertEqual(result["stopped_at"], "profile-compact")
        with self.assertRaises(ValueError): schedule.route_to_spy(plan, inventory, 3, spy=lambda c: True)
        with self.assertRaises(ValueError): schedule.route_to_spy(plan, inventory, 3, spy=None)

    def test_unimplemented_guardstatics_blocks_route_and_readiness_without_skip(self):
        plan, inventory = synthetic_inputs(); calls = []
        def spy(command):
            calls.append(command["unit"])
            return 0
        result = schedule.route_to_spy(plan, inventory, 6, spy=spy)
        self.assertEqual(calls, ["R1", "R3", "APPLY", "R6", "R8"])
        self.assertEqual(result["stopped_at"], "guardrails-static")
        self.assertEqual(result["reason"], "unimplemented")
        descriptor = schedule.worker_commands(plan, inventory, 6)[5]
        self.assertEqual(descriptor["command"], ["sh", "tests/ci_guardrails_static.sh"])
        for field, value in (("route", "planned"), ("command", ["sh", "true"])):
            changed = deepcopy(plan); unit(changed, "guardrails-static")[field] = value
            self.assert_rejected(changed, inventory)
        for change in ("readiness", "safety"):
            changed = deepcopy(plan)
            if change == "readiness": changed["ready_for_hosted"] = True
            else: changed["safety"]["mode"] = "execute"
            self.assert_rejected(changed, inventory)

    def test_json_only_cli_has_no_execute_skip_discovery_or_process_backend(self):
        plan, inventory = synthetic_inputs()
        with mock.patch("builtins.open", side_effect=[io.StringIO(json.dumps(plan)), io.StringIO(json.dumps(inventory))]), \
                mock.patch("subprocess.Popen", side_effect=AssertionError("no process")), \
                contextlib.redirect_stdout(io.StringIO()) as output:
            code = schedule.main(["--worker", "3"])
        packet = json.loads(output.getvalue())
        self.assertEqual(code, 0)
        self.assertTrue(packet["valid"], packet)
        self.assertEqual(set(packet["commands"]), {"3"})
        self.assertIs(packet["ready_for_hosted"], False)
        for flag in ("--execute", "--skip", "--discover", "--help"):
            with contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(schedule.main([flag]), 1)
            self.assertFalse(json.loads(output.getvalue())["valid"])
        for malformed in (None, [], {}, {"schema": "l0.ci-schedule/1"}):
            self.assert_rejected(malformed, inventory)

    def test_repository_selector_collection_matches_inventory(self):
        plan, inventory = frozen_inputs()
        expected, _, _ = schedule.expected_methods(inventory)
        # Parent must freeze planning IDs first; never use this collection as truth.
        self.assertIn(("guardrails-ci-planning", None), expected,
                      "step3 prerequisite: freeze planning IDs in independent inventory/checker")
        actual = defaultdict(Counter)
        loader = unittest.TestLoader()
        def import_probe(args, **kwargs):
            # Source-inspected import-time metadata probe, not a test body. Fake
            # SHA has no effect on collection and is NEVER candidate evidence.
            if args == ["git", "-C", str(ROOT), "rev-parse", "HEAD"]:
                self.assertEqual(kwargs, {"text": True, "capture_output": True, "check": True})
            else:
                # test_l1_template_gitlink_retirements imports the transitions
                # helper, which reads HEAD with cwd instead of Git's -C form.
                self.assertEqual(args, ("git", "rev-parse", "HEAD"))
                self.assertEqual(kwargs, {"cwd": ROOT, "text": True, "input": None, "capture_output": True})
            return SimpleNamespace(stdout="b" * 40 + "\n", stderr="", returncode=0)
        # Restore module/package caches and sys.path so synthetic import metadata
        # cannot leak into any later real ownership execution in this process.
        with mock.patch.dict(sys.modules), mock.patch.dict(vars(sys.modules["tests"])), \
                mock.patch.object(sys, "path", sys.path[:]), \
                mock.patch("subprocess.run", side_effect=import_probe), \
                mock.patch("subprocess.Popen", side_effect=AssertionError("collection must not launch")), \
                mock.patch("os.system", side_effect=AssertionError("collection must not launch")), \
                mock.patch.object(unittest.TestCase, "run", side_effect=AssertionError("no test bodies")), \
                mock.patch.object(unittest.TestSuite, "run", side_effect=AssertionError("no fixtures")):
            for row in plan["units"]:
                if row["kind"] != "python":
                    continue
                suite = loader.loadTestsFromNames(row["selectors"])
                self.assertEqual(loader.errors, [], row["unit"])
                ids = Counter(collected_ids(suite))
                wanted = expected[(schedule.PLANNING, None)] if row["unit"] == "planning" else Counter(row["methods"])
                self.assertEqual(ids, wanted, row["unit"])
                actual[(row["cohort"], None)].update(ids)
        self.assertEqual(loader.errors, [])
        # Nested methods aren't top-level selectors; only UPG's parent executes them.
        for key, wanted in expected.items():
            if key[1] is None:
                self.assertEqual(actual[key], wanted, key)
        self.assertEqual(actual[("guardrails-main", None)][SHARED], 1)
        self.assertEqual(actual[("generation-main", None)][SHARED], 1)
        self.assertEqual(len(unit(plan, "UPG")["nested"][0]["methods"]), 2)


if __name__ == "__main__":
    unittest.main()
