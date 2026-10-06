#!/usr/bin/env python3
"""Closed six-worker assignment preparation, not hosted parallel execution.

Only JSON dry-run output is available. No discovery, exclusion or execute switch.
validate_schedule and worker_commands are pure; route_to_spy requires an injected
callback and has NO process backend. Spy success is not command/coverage proof.
Frozen product methods come from independent inventory, never live collection.
ci_worker is a separate explicitly experimental execution backend, not this API.
Planning alone may defer its expected IDs until the parent freezes that cohort.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
if __package__:
    from . import ci_coverage as coverage
else:
    import ci_coverage as coverage

PLANNING = "guardrails-ci-planning"
OWNER = coverage.OWNER_METHOD
RENDERER = "tests.test_company_ontology_ref_inheritance.RendererTests."
OWNERSHIP = "tests.test_l1_template_ownership.L1TemplateOwnershipTests."
COMPANY = "tests.test_l1_template_company_ownership.CompanyOntologyTests."
SAFETY = {
    "mode": "dry-run-only",
    "source": "future captures require exact full candidate SHA and clean source",
    "cwd": "candidate repository root; no source writes or ambient AK",
    "environment": ["L0_TEMPLATE_ROOT=exact candidate root", "TMPDIR=private disjoint scratch",
                    "PYTHONDONTWRITEBYTECODE=1", "L0_PROFILE_DIR=private fresh report directory",
                    "L0_PROFILE_COHORT/L0_PROFILE_PARENT=unset for root units; nested UPG inherits parent"],
    "capture": "future shell receipts require l0.profile-command/1 exact command, complete output and clean teardown",
    "reports": "aggregate split reports by cohort,parent_cohort; nested upgrade stays bound to ownership parent",
    "runtime": "retain public-context python3 for generation-main; provision pinned copier runtimes separately",
    "authority": "no AK lifecycle, production/golden writes, hosted launch or public workflow changes",
}

# Literal closed selectors. Keep the original Gf modules: imported Reorder tests
# and load_tests' six reverse tests do not have interchangeable literal namespaces.
GF = [
    "tests.test_ci_profile", "tests.test_hosted_ci", "tests.test_ci_red_green",
    "tests.test_l1_template_transitions",
    COMPANY + "test_legacy_plans_stay_nonempty_and_map_v2_refuses_unknown_or_overlapping_classes",
    "tests.test_l2_template_source", "tests.test_l1_answer_template_legacy",
    "tests.test_l1_template_gitlink_retirements",
]
GENERATION_FAST = [
    # Existing literal selectors, frozen independently; never discovered at runtime.
    'tests.test_agent_template_v2.AgentTemplateV2Tests.test_compiler_validates_manifest_and_detects_staleness',
    'tests.test_agent_template_v2.AgentTemplateV2Tests.test_manifest_shell_and_six_canonical_persona_inputs',
    'tests.test_agent_template_v2.AgentTemplateV2Tests.test_propagation_refuses_ambiguous_map_and_symlinked_parent',
    'tests.test_agent_template_v2.AgentTemplateV2Tests.test_propagation_refuses_unknown_top_level_file',
    'tests.test_agent_template_v2.AgentTemplateV2Tests.test_propagation_renders_l1_plan_first_and_preserves_agent_bytes',
    'tests.test_l1_template_ownership.L1TemplateOwnershipTests.test_bootstrap_installs_only_map_and_census_attestation',
    'tests.test_l1_template_ownership.L1TemplateOwnershipTests.test_clean_target_ignores_ambient_status_config',
    'tests.test_l1_template_ownership.L1TemplateOwnershipTests.test_finalize_accepts_only_linked_worktree_of_canonical_task_repo',
    'tests.test_l1_template_ownership.L1TemplateOwnershipTests.test_first_refresh_consumes_attestation_and_establishes_state',
    'tests.test_l1_template_ownership.L1TemplateOwnershipTests.test_invalid_or_unclassified_render_fails_closed',
    'tests.test_l1_template_ownership.L1TemplateOwnershipTests.test_preview_rejects_symlinked_destination_before_reading',
    'tests.test_l1_template_ownership.L1TemplateOwnershipTests.test_retirement_revalidates_all_old_templates_after_copy_before_any_delete',
    'tests.test_render_l1.RenderL1Tests.test_owner_gitlink_target_renders_the_gitlink_layout',
    'tests.test_render_l1.RenderL1Tests.test_render_only_writes_output_and_leaves_target_untouched',
    'tests.test_render_l1.RenderL1Tests.test_usage_errors_exit_2',
    'tests.test_l0_check_timeouts.VerificationBudgetTests.test_base_and_per_leaf_environment_overrides_remain_effective',
    'tests.test_l0_check_timeouts.VerificationBudgetTests.test_defaults_are_finite_and_all_leaves_run',
    'tests.test_l0_check_timeouts.VerificationBudgetTests.test_invalid_overrides_fail_closed',
    'tests.test_l0_check_timeouts.VerificationBudgetTests.test_timeout_is_failure_and_aborts_later_checks',
    'tests.test_l1_template_company_ownership.CompanyOntologyTests.test_company_birth_and_refresh_preserve_all_ontology_and_never_seed_missing_file',
    'tests.test_l1_template_company_ownership.CompanyOntologyTests.test_inverse_source_must_exist_in_historical_base_not_just_current_head',
    'tests.test_l1_template_company_ownership.CompanyOntologyTests.test_legacy_plans_stay_nonempty_and_map_v2_refuses_unknown_or_overlapping_classes',
    'tests.test_l1_template_company_ownership.CompanyOntologyTests.test_ordinary_refresh_and_retirement_cannot_transfer_or_touch_company_ontology',
    'tests.test_l1_template_company_ownership.CompanyOntologyTests.test_planning_outputs_cannot_mutate_a_target_or_its_shared_git_metadata',
    'tests.test_l1_template_company_ownership.CompanyOntologyTests.test_preparation_refuses_dropping_existing_agent_claims',
    'tests.test_l1_template_company_ownership.CompanyOntologyTests.test_reverse_after_repeated_v3_refresh_preserves_other_map_changes',
    'tests.test_l1_template_company_ownership.CompanyOntologyTests.test_reverse_rechecks_census_and_rejects_forged_receipt_or_extra_ownership',
    'tests.test_l1_template_company_ownership.CompanyOntologyTests.test_reverse_refuses_birth_ownership_and_residual_ignored_content_or_seed_drift',
    'tests.test_l1_template_company_ownership.CompanyOntologyTests.test_v1_birth_relabel_cannot_erase_an_executed_ownership_transition',
    'tests.test_l1_template_company_ownership.CompanyOntologyTests.test_v3_birth_origin_and_applied_commit_forgery_do_not_bypass_wave_receipt',
    'tests.test_l1_template_company_ownership.CompanyOntologyTests.test_wrapper_cannot_grant_company_ownership_reseed_or_change_topology',
]


def python_spec(cohort, runtime, selectors, estimate):
    return {"kind": "python", "cohort": cohort, "runtime": runtime,
            "selectors": selectors, "estimate_ms": estimate}


def shell_spec(command, estimate):
    return {"kind": "shell", "cohort": None, "runtime": "shell",
            "selectors": [], "command": command, "estimate_ms": estimate}


# This map is an immutable-in-use authoring contract, not supplied by the plan.
SPECS = {
    "Gf": python_spec("guardrails-main", "pinned", GF, 50000),
    "Wrapper": python_spec("guardrails-main", "pinned",
                           ["tests.test_company_ontology_ref_inheritance.WrapperTests"], 116000),
    "Safety": python_spec("guardrails-main", "pinned",
                          ["tests.test_l1_answer_template_upgrade.UpgradeSafetyTests"], 138000),
    "SYS": python_spec("guardrails-system4d", "pinned", ["tests.test_l2_system4d_context"], 400),
    "seam": python_spec("guardrails-generation-units", "pinned-9.11.1",
                        ["tests.test_ci_generation_units"], 15000),
    "planning": python_spec(PLANNING, "pinned-9.11.1",
                            ["tests.test_ci_coverage", "tests.test_ci_schedule"], 15000),
    "static-contracts": python_spec("guardrails-ci-static", "pinned-9.11.1",
                                  ["tests.test_ci_guardrails"], 2000),
    "candidate-contracts": python_spec("guardrails-ci-candidate", "pinned-9.11.1",
                                     ["tests.test_ci_worker", "tests.test_ci_aggregate",
                                      "tests.test_ci_candidate_workflow"], 10000),
    "Mf": python_spec("generation-main", "python3", GENERATION_FAST, 31000),
    "UPG": python_spec("generation-main", "python3",
                       [OWNER], 438000),
    "APPLY": python_spec("generation-main", "python3",
                         [OWNERSHIP + "test_apply_updates_template_and_preserves_company_owned_bytes"], 152000),
    "PREP": python_spec("generation-main", "python3",
                        [COMPANY + "test_old_readers_upgrade_through_a_receipted_preparatory_refresh"], 348000),
    "REV": python_spec("generation-main", "python3",
                       [COMPANY + "test_real_forward_and_receipted_reverse_restore_ownership"], 304000),
    "FULL": python_spec("generation-main", "python3",
                        [COMPANY + "test_real_full_ci_binds_fixture_ak_without_ambient_runtime"], 151000),
    "R1": python_spec("guardrails-main", "pinned",
                      [RENDERER + "test_all_five_filename_transport_and_outer_custom_name_isolation"], 283000),
    "R2": python_spec("guardrails-main", "pinned",
                      [RENDERER + "test_company_entrypoint_alias_binds_physical_root_and_reruns_cleanly"], 17000),
    "R3": python_spec("guardrails-main", "pinned",
                      [RENDERER + "test_empty_default_and_custom_destination_answers"], 169000),
    "R4": python_spec("guardrails-main", "pinned",
                      [RENDERER + "test_external_native_uv_actual_pinned_source_birth_without_company_copies"], 17000),
    "R5": python_spec("guardrails-main", "pinned",
                      [RENDERER + "test_fresh_children_persist_and_reruns_preserve_choices"], 108000),
    "R6": python_spec("guardrails-main", "pinned",
                      [RENDERER + "test_real_completion_and_no_effect_operations"], 63000),
    "R7": python_spec("guardrails-main", "pinned",
                      [RENDERER + "test_real_render_rejects_unsafe_ref_without_mutating_destination"], 44000),
    "R8": python_spec("guardrails-main", "pinned",
                      [RENDERER + "test_tagged_parent_no_host_yaml_refuses_but_pinned_yaml_renders"], 22000),
    **{name: shell_spec(["sh", "tests/ci_generation_unit.sh", name], estimate)
       for name, estimate in [("sample-shell", 584000), ("profile-community", 156000),
                              ("profile-release", 161000), ("profile-vouch", 158000),
                              ("profile-compact", 158000)]},
    "adversarial": shell_spec(["sh", "scripts/check-l0-adversarial.sh"], 407000),
    "fixtures": shell_spec(["sh", "scripts/check-l0-fixtures.sh"], 104000),
    "guardrails-static": shell_spec(["sh", "tests/ci_guardrails_static.sh"], 1000),
    "doc-references": shell_spec(["sh", "scripts/check-doc-references.sh"], 1000),
    "session-checkpoint": shell_spec(["sh", "scripts/check-session-checkpoint.sh"], 1000),
    "supply-chain": shell_spec(["sh", "scripts/check-supply-chain.sh"], 1000),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def integer(value, minimum=0):
    return type(value) is int and value >= minimum


def expected_methods(inventory):
    """Reuse the unchanged checker for product inventory; allow one future cohort."""
    inventory = coverage.expand_inventory(inventory)
    require(isinstance(inventory, dict), "inventory object")
    original = deepcopy(inventory)
    rows = original.get("cohorts")
    require(isinstance(rows, list), "inventory cohorts")
    planning = [row for row in rows if isinstance(row, dict) and row.get("cohort") == PLANNING]
    require(len(planning) <= 1, "duplicate planning inventory cohort")
    if planning:
        row = planning[0]
        require(row.get("parent_cohort") is None and row.get("parent_method") is None,
                "planning cannot be nested")
        methods = row.get("methods")
        require(isinstance(methods, list) and bool(methods), "planning independent methods absent")
        for method in methods:
            require(isinstance(method, dict) and isinstance(method.get("id"), str)
                    and any(method["id"].startswith(s + ".") for s in SPECS["planning"]["selectors"])
                    and method.get("outcome") == "success" and method.get("subtests") == []
                    and method.get("origin") in original.get("inputs", {}), "planning inventory method")
        require(len({m["id"] for m in methods}) == len(methods), "duplicate planning method")
        require(integer(original.get("expected_root_count"), 1), "inventory root count")
        original["expected_root_count"] -= len(methods)
        original["cohorts"].remove(row)
    # Parent step3 may teach the checker the planning cohort. Respect its updated
    # closed cohort set without stripping a cohort it now requires.
    checker_input = inventory if (PLANNING, None) in coverage.COHORTS else original
    expected, owners, shell = coverage.inventory_counters(checker_input)
    counters = {key: value[0] for key, value in expected.items()}
    if planning:
        counters[(PLANNING, None)] = Counter(m["id"] for m in planning[0]["methods"])
    return counters, owners, shell


def canonical_command(spec):
    if spec["kind"] == "shell":
        return spec["command"][:]
    return ["sh", "tests/ci_unittest.sh", spec["cohort"], spec["runtime"], *spec["selectors"]]


def selector_owns(unit, method):
    selectors = SPECS[unit]["selectors"]
    if unit == "Gf" and method.startswith(("tests.test_ci_reorder.",
                                          "tests.test_l1_template_reverse_transitions.")):
        return True  # Imported class and original module load_tests, respectively.
    return any(method == s or method.startswith(s + ".") for s in selectors)


def _validate(plan, inventory):
    expected, owners, shell = expected_methods(inventory)
    require(isinstance(plan, dict) and plan.get("schema") == "l0.ci-schedule/1", "plan schema")
    require(plan.get("safety") == SAFETY, "future safety/capture contract drift")
    require(plan.get("ready_for_hosted") is False, "hosted readiness cannot be asserted")
    units, workers = plan.get("units"), plan.get("workers")
    require(isinstance(units, list) and isinstance(workers, list), "units/workers arrays")
    declared, actual = {}, defaultdict(Counter)
    pending = (PLANNING, None) not in expected
    for row in units:
        require(isinstance(row, dict) and set(row) == {
            "unit", "kind", "cohort", "parent_cohort", "runtime", "selectors", "command",
            "methods", "nested", "route", "estimate_ms"}, "unit fields")
        name = row["unit"]
        require(isinstance(name, str) and name in SPECS and name not in declared,
                "unknown/duplicate unit")
        spec = SPECS[name]
        for field in ("kind", "cohort", "runtime", "selectors"):
            require(row[field] == spec[field], f"{name}: {field} drift")
        require(row["parent_cohort"] is None, "top-level nested unit forbidden")
        require(row["command"] == canonical_command(spec), f"{name}: command drift")
        require(row["route"] == "planned", f"{name}: route drift")
        estimate = row["estimate_ms"]
        require(integer(estimate, 1), f"{name}: estimate integer")
        if name in {"seam", "planning"}:
            require(2000 <= estimate <= 15000, f"{name}: estimate outside proposed 2-15s")
        else:
            require(estimate == spec["estimate_ms"], f"{name}: historical estimate drift")
        if name == "planning":
            require(row["methods"] is None, "planning expected IDs must come from independent inventory")
            methods = list(expected.get((PLANNING, None), Counter()).elements())
        else:
            methods = row["methods"]
        require(isinstance(methods, list) and all(isinstance(m, str) and m for m in methods),
                f"{name}: method array")
        if spec["kind"] == "python":
            require(bool(methods) or (name == "planning" and pending), f"{name}: empty methods")
            require(all(selector_owns(name, m) for m in methods), f"{name}: selector/method ownership")
            actual[(spec["cohort"], None)].update(methods)
        else:
            require(methods == [] and row["nested"] == [], "shell cannot own python methods")
            require(name in shell and row["command"] == shell[name], "shell inventory command drift")
        nested = row["nested"]
        require(isinstance(nested, list), "nested array")
        if name == "UPG":
            require(len(nested) == 1 and isinstance(nested[0], dict), "UPG nested report missing")
            child = nested[0]
            require(set(child) == {"cohort", "parent_cohort", "parent_method", "methods"}, "nested fields")
            key = (child["cohort"], child["parent_cohort"])
            require(key == ("generation-upgrade", "generation-main")
                    and child["parent_method"] == owners.get(key) == OWNER
                    and Counter(methods)[OWNER] == 1, "nested parent binding")
            require(isinstance(child["methods"], list)
                    and all(isinstance(m, str) for m in child["methods"]), "nested methods")
            actual[key].update(child["methods"])
        else:
            require(nested == [], "nested upgrade belongs only to UPG whole parent")
        declared[name] = row
    require(set(declared) == set(SPECS), "missing unit(s)")
    # Empty unresolved planning isn't a candidate-derived expectation.
    if pending:
        actual.pop((PLANNING, None), None)
    require(set(actual) == set(expected), "unknown/missing cohort")
    for key, wanted in expected.items():
        require(actual[key] == wanted, f"{key}: missing/excess/duplicate method multiset")
    assignments, seen, budgets = Counter(), set(), []
    require(len(workers) == 6, "exactly six workers required")
    for worker in workers:
        require(isinstance(worker, dict) and set(worker) == {
            "worker", "assignments", "cold_setup_ms", "aggregation_ms", "budget_ms"}, "worker fields")
        number = worker["worker"]
        require(type(number) is int and number in range(1, 7) and number not in seen,
                "unknown/duplicate worker (integer 1..6 required)")
        seen.add(number)
        entries = worker["assignments"]
        require(isinstance(entries, list) and bool(entries), "worker assignments empty")
        cost = 0
        for index, entry in enumerate(entries, 1):
            require(isinstance(entry, dict) and set(entry) == {"order", "unit"}, "assignment fields")
            require(type(entry["order"]) is int and entry["order"] == index,
                    "order must be contiguous integer, not bool")
            name = entry["unit"]
            require(isinstance(name, str) and name in declared, "unknown assigned unit")
            assignments[name] += 1
            cost += declared[name]["estimate_ms"]
        for field in ("cold_setup_ms", "aggregation_ms", "budget_ms"):
            require(integer(worker[field], 1), f"{field}: positive integer proposed allowance")
        require(worker["budget_ms"] <= 900000, "worker budget cannot exceed the 900s target")
        require(worker["cold_setup_ms"] == 120000 and worker["aggregation_ms"] == 30000,
                "declared cold setup/aggregation allowances cannot be reduced or rewritten")
        total = cost + worker["cold_setup_ms"] + worker["aggregation_ms"]
        require(total <= worker["budget_ms"], f"worker {number}: cold/aggregation budget exceeded")
        budgets.append({"worker": number, "estimated_ms": total, "budget_ms": worker["budget_ms"]})
    require(assignments == Counter({name: 1 for name in SPECS}), "missing/double unit assignment")
    blockers = ["actual unit isolation/equivalence and candidate/hosted evidence still required"]
    if pending:
        blockers.append("parent must freeze guardrails-ci-planning expected IDs in independent inventory/checker")
    return {"planning_inventory_pending": pending, "root_methods_assigned": sum(
        sum(c.values()) for key, c in expected.items() if key[1] is None),
        "nested_methods_assigned": sum(sum(c.values()) for key, c in expected.items() if key[1] is not None),
        "shell_units_assigned": len(shell), "worker_estimates": sorted(budgets, key=lambda b: b["worker"]),
        "blockers": blockers}


def validate_schedule(plan, inventory):
    """Return accounting data, not execution or performance evidence."""
    packet = {"schema": "l0.ci-schedule-check/1", "valid": False, "errors": [],
              "ready_for_hosted": False, "performance_proven": False,
              "coverage_execution_proven": False, "mode": "dry-run-only"}
    try:
        packet.update(_validate(plan, inventory))
        packet["valid"] = True
    except (ValueError, TypeError, KeyError, AttributeError, OverflowError, RecursionError) as error:
        packet["errors"].append(str(error))
    return packet


def worker_commands(plan, inventory, worker):
    """Prepare fresh command descriptors only; no execution or readiness proof."""
    packet = validate_schedule(plan, inventory)
    require(packet["valid"], "; ".join(packet["errors"]))
    require(type(worker) is int and worker in range(1, 7), "worker must be integer 1..6")
    by_name = {u["unit"]: u for u in plan["units"]}
    chosen = next(w for w in plan["workers"] if w["worker"] == worker)
    commands = []
    for entry in chosen["assignments"]:
        row = deepcopy(by_name[entry["unit"]])
        row.update(worker=worker, order=entry["order"], safety=deepcopy(SAFETY))
        if row["unit"] == "planning":
            if packet["planning_inventory_pending"]:
                row["route"] = "inventory-pending"
            else:
                expected, _, _ = expected_methods(inventory)
                row["methods"] = list(expected[(PLANNING, None)].elements())
        commands.append(row)
    return commands


def route_to_spy(plan, inventory, worker, *, spy):
    """Inject a fake command spy (integer exit status). No default/real launcher.

    Stops BEFORE an unimplemented/pending route and AFTER the first failed call.
    Callback behavior is the caller's responsibility; this module never launches.
    """
    require(callable(spy), "fake spy callback required")
    calls = []
    for command in worker_commands(plan, inventory, worker):
        if command["route"] != "planned":
            return {"calls": calls, "stopped_at": command["unit"], "reason": command["route"],
                    "execution_proven": False}
        code = spy(deepcopy(command))
        require(type(code) is int, "spy must return integer exit status")
        calls.append({"unit": command["unit"], "exit_code": code})
        if code != 0:
            return {"calls": calls, "stopped_at": command["unit"], "reason": "spy-failure",
                    "execution_proven": False}
    return {"calls": calls, "stopped_at": None, "reason": "spy-only", "execution_proven": False}


def main(argv=None):
    try:
        parser = coverage.JsonArgumentParser(description=__doc__, add_help=False)
        parser.add_argument("--plan", default=str(Path(__file__).with_suffix(".json")))
        parser.add_argument("--inventory", default=str(Path(__file__).with_name("ci_coverage_inventory.json")))
        parser.add_argument("--worker", type=int, choices=range(1, 7))
        args = parser.parse_args(argv)
        with open(args.plan, encoding="utf-8") as stream:
            plan = coverage.load_json(stream)
        with open(args.inventory, encoding="utf-8") as stream:
            inventory = coverage.load_json(stream)
        packet = validate_schedule(plan, inventory)
        if packet["valid"]:
            packet["commands"] = {str(w): worker_commands(plan, inventory, w)
                                  for w in ([args.worker] if args.worker else range(1, 7))}
    except (OSError, ValueError, TypeError, KeyError, UnicodeError, RecursionError) as error:
        packet = {"schema": "l0.ci-schedule-check/1", "valid": False, "ready_for_hosted": False,
                  "mode": "dry-run-only", "errors": [str(error)]}
    print(json.dumps(packet, sort_keys=True, allow_nan=False))
    return 0 if packet["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
