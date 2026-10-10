"""Canonical ownership-transition plan schemas; legacy topology and ontology-only forms."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

import l1_template_company as company
from l1_template_transition_delta import validate_git_delta

PLAN_SCHEMA = "ai-society.template-ownership-transition-plan/1"
EXECUTOR_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/-]{2,127}\Z")
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
REQUIRED_VALIDATION = [
    {"id": "check-template-ci", "command": "bash scripts/check-template-ci.sh"},
    {"id": "ci-full", "command": "bash scripts/ci/full.sh"},
]


def canonical_bytes(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def semantic_delta(old: dict[str, list[str]], new: dict[str, list[str]]) -> dict[str, list[str]]:
    result = {
        "template_added": sorted(set(new["template"]) - set(old["template"])),
        "template_removed": sorted(set(old["template"]) - set(new["template"])),
        "agent_added": sorted(set(new["agent"]) - set(old["agent"])),
        "agent_removed": sorted(set(old["agent"]) - set(new["agent"])),
    }
    if old.get("company", []) != new.get("company", []):
        result.update(
            company_added=sorted(set(new.get("company", [])) - set(old.get("company", []))),
            company_removed=sorted(set(old.get("company", [])) - set(new.get("company", []))),
        )
    if not any(result.values()):
        raise ValueError("successor ownership map must change ownership semantics")
    return result


def plan_hash(plan: dict[str, Any]) -> str:
    body = dict(plan)
    body.pop("canonical_plan_sha256", None)
    return digest_bytes(canonical_bytes(body))


def validate_plan(plan: dict[str, Any]) -> dict[str, Any]:
    required = {
        "schema", "target_repo", "decision_id", "adr_commit", "transition_task_id",
        "executor", "base_commit", "predecessor_state_sha256", "predecessor_map_sha256",
        "next_map_sha256", "next_map_text", "map_delta", "git_delta", "validation",
        "rollback", "canonical_plan_sha256",
    }
    from l1_ontology_convergence import PLAN_SCHEMA as CONVERGENCE_SCHEMA, validate_model
    is_company = plan.get("schema") == company.PLAN_SCHEMA
    is_convergence = plan.get("schema") == CONVERGENCE_SCHEMA
    extra = {"ontology_convergence"} if is_convergence else ({"reverse_of"} if is_company else set())
    if set(plan) != required | extra or plan.get("schema") not in {PLAN_SCHEMA, company.PLAN_SCHEMA, CONVERGENCE_SCHEMA}:
        raise ValueError("transition plan has wrong schema or keys")
    target = plan.get("target_repo")
    if not isinstance(target, str) or not Path(target).is_absolute() or str(Path(target).resolve()) != target:
        raise ValueError("target_repo must be a canonical absolute path")
    if any(type(plan.get(key)) is not int or plan[key] < 1 for key in ("decision_id", "transition_task_id")):
        raise ValueError("decision_id and transition_task_id must be positive integers")
    if not isinstance(plan.get("executor"), str) or not EXECUTOR_RE.fullmatch(plan["executor"]):
        raise ValueError("invalid fixed executor")
    for key in ("base_commit", "adr_commit"):
        if not isinstance(plan.get(key), str) or not HEX40.fullmatch(plan[key]):
            raise ValueError(f"{key} must be full lowercase 40-hex")
    for key in ("predecessor_state_sha256", "predecessor_map_sha256", "next_map_sha256", "canonical_plan_sha256"):
        if not isinstance(plan.get(key), str) or not HEX64.fullmatch(plan[key]):
            raise ValueError(f"{key} must be lowercase sha256")
    if not isinstance(plan.get("next_map_text"), str) or digest_bytes(plan["next_map_text"].encode()) != plan["next_map_sha256"]:
        raise ValueError("next_map_text digest mismatch")
    delta = plan.get("map_delta")
    delta_keys = company.DELTA_KEYS if is_company or is_convergence else {"template_added", "template_removed", "agent_added", "agent_removed"}
    if not isinstance(delta, dict) or set(delta) != delta_keys or any(
        not isinstance(value, list) or value != sorted(set(value))
        or any(not isinstance(item, str) for item in value) for value in delta.values()
    ) or not any(delta.values()):
        raise ValueError("map_delta must use exact non-empty canonical semantic lists")
    if is_company:
        company.validate_model(plan)
    else:
        plan["git_delta"] = validate_git_delta(plan["git_delta"])
        if is_convergence:
            validate_model(plan)
        elif company.map_sections(plan["next_map_text"].encode()).get("company") and any(
            company.matches(entry["path"], company.ONTOLOGY) for entry in plan["git_delta"]
        ):
            raise ValueError("legacy plan /1 may not carry company ontology payload")
    if plan.get("validation") != REQUIRED_VALIDATION:
        raise ValueError("validation must contain the exact required L1 gate commands")
    if not isinstance(plan.get("rollback"), str) or not plan["rollback"].strip():
        raise ValueError("rollback must be non-empty")
    if plan_hash(plan) != plan["canonical_plan_sha256"]:
        raise ValueError("canonical transition plan hash mismatch")
    return plan
