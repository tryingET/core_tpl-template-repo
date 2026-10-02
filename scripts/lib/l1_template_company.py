"""Ontology-only map transition extension; legacy topology plans remain unchanged."""
from __future__ import annotations

import json
import hashlib
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "copier-template/scripts/lib"))
from l1_ontology_ownership import (  # noqa: E402
    BINDING_KEYS, MAP, STATE, ONTOLOGY, forward_source, map_sections,
    matches, pattern_kind, patterns_overlap, placeholder_live, placeholder_tree,
    structural_transfer, transfer_direction, placeholder_files, map_text,
)

PLAN_SCHEMA = "ai-society.template-ownership-transition-plan/2"
DELTA_KEYS = {"template_added", "template_removed", "agent_added", "agent_removed", "company_added", "company_removed"}


def parse_map_bytes(raw: bytes, parent: Path) -> dict[str, list[str]]:
    return map_sections(raw)


def plan_path_parent(repo: Path) -> Path:
    import os
    parent = Path(os.environ.get("TMPDIR", str(repo.parent))).resolve()
    if not parent.is_dir():
        raise ValueError("TMPDIR for map validation must be an existing directory")
    return parent


def verify_historical_maps(repo: Path, plan: dict[str, Any], ak: Path | None) -> None:
    from l1_template_receipts import git_output
    from l1_template_transition_plan import semantic_delta
    old_map = git_output(repo, "show", f"{plan['base_commit']}:{MAP}").encode()
    old_state = git_output(repo, "show", f"{plan['base_commit']}:{STATE}").encode()
    if hashlib.sha256(old_map).hexdigest() != plan["predecessor_map_sha256"] or hashlib.sha256(old_state).hexdigest() != plan["predecessor_state_sha256"]:
        raise ValueError("transition predecessor hashes do not match historical bytes")
    if semantic_delta(map_sections(old_map), map_sections(plan["next_map_text"].encode())) != plan["map_delta"]:
        raise ValueError("transition semantic delta does not match historical maps")
    verify_transfer(repo, plan, ak)


def validate_model(plan: dict[str, Any]) -> None:
    if plan["git_delta"] != [] or set(plan["map_delta"]) != DELTA_KEYS:
        raise ValueError("ontology-only plan requires an empty payload and exact company semantic delta")
    if map_sections(plan["next_map_text"].encode()).get("company") is None:
        raise ValueError("ontology-only successor map requires ownership schema /2")
    binding = plan["reverse_of"]
    if binding is not None and (not isinstance(binding, dict) or set(binding) != BINDING_KEYS):
        raise ValueError("ownership reverse requires exact forward receipt binding")


def source_binding(repo: Path, state: dict[str, Any], raw: bytes, ak: Path | None, anchor: str = "HEAD") -> dict[str, Any]:
    import l1_template_transitions as transition
    from l1_template_receipts import git_output

    git = lambda *args: git_output(repo, *args)
    binding = forward_source(git, state, raw, anchor)
    if state.get("schema") == "ai-society.template-ownership-state/3":
        from l1_template_receipts import validate_established_provenance
        validate_established_provenance(repo, state, ak_command=ak, proof_commit=anchor)
    transition.validate_inherited_transition(repo, binding, ak)
    return binding


def configure_plan(repo: Path, plan: dict[str, Any], ak: Path | None) -> None:
    """Discriminate the new map-only form, never weaken a legacy payload plan."""
    from l1_template_receipts import git_output

    old = git_output(repo, "show", f"{plan['base_commit']}:{MAP}").encode()
    direction = transfer_direction(old, plan["next_map_text"].encode())
    if direction is None:
        if not plan["git_delta"]:
            raise ValueError("empty payload is supported only for an ontology-only ownership transfer")
        return
    if plan["git_delta"]:
        raise ValueError("company ontology ownership transfer must be map-only")
    plan["schema"] = PLAN_SCHEMA
    plan["reverse_of"] = None
    if direction == "reverse":
        raw = (repo / STATE).read_bytes()
        plan["reverse_of"] = source_binding(repo, json.loads(raw), raw, ak)
        placeholder_live(repo, lambda *args: git_output(repo, *args))


def verify_transfer(repo: Path, plan: dict[str, Any], ak: Path | None, live: bool = False) -> None:
    from l1_template_receipts import git_output

    old = git_output(repo, "show", f"{plan['base_commit']}:{MAP}").encode()
    direction = transfer_direction(old, plan["next_map_text"].encode())
    if plan["schema"] != PLAN_SCHEMA:
        if direction is not None:
            raise ValueError("company ownership changes require the ontology-only plan schema /2")
        return
    validate_model(plan)
    if direction is None:
        raise ValueError("ontology-only plan lacks an exact ownership transfer")
    if direction == "forward":
        if plan["reverse_of"] is not None:
            raise ValueError("forward ontology transfer may not carry reverse authority")
        return
    raw = git_output(repo, "show", f"{plan['base_commit']}:{STATE}").encode()
    if source_binding(repo, json.loads(raw), raw, ak, plan["base_commit"]) != plan["reverse_of"]:
        raise ValueError("ownership reverse does not bind its actual forward receipt")
    git = lambda *args: git_output(repo, *args)
    placeholder_tree(git, plan["base_commit"])
    if live:
        placeholder_live(repo, git)


def reverse_plan(repo: Path, spec_path: Path, output: Path, ak: Path | None = None) -> int:
    """Derive the exact successor map from a verified forward receipt and current map.

    Spec contains only new decision/ADR/task/executor authority and rollback text;
    the operator cannot substitute a map or invent a reverse-source binding.
    """
    import tempfile
    import l1_template_transitions as transition
    from l1_template_receipts import ensure_clean_git_target

    ensure_clean_git_target(repo)
    spec = transition.load_object(spec_path, "ownership reverse spec")
    if set(spec) != {"decision_id", "adr_commit", "transition_task_id", "executor", "rollback"}:
        raise ValueError("ownership reverse spec must contain exactly five authority/rollback fields")
    raw = (repo / STATE).read_bytes()
    from l1_template_receipts import validate_established_provenance
    validate_established_provenance(repo, json.loads(raw), ak_command=ak)
    source_binding(repo, json.loads(raw), raw, ak)
    current = (repo / MAP).read_bytes()
    mapping = map_sections(current)
    if mapping.get("company") != [ONTOLOGY]:
        raise ValueError("ownership reverse requires the active company ontology claim")
    mapping["company"] = []
    mapping["template"] = [ONTOLOGY, *mapping["template"]]
    successor = map_text(mapping)
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="ontology-reverse-", dir=output.parent) as name:
        root = Path(name)
        next_map = root / "next-map.yml"
        next_map.write_text(successor)
        expanded = dict(spec, next_map=str(next_map.resolve()), git_delta=[], validation=transition.REQUIRED_VALIDATION)
        expanded_path = root / "spec.json"
        expanded_path.write_text(json.dumps(expanded))
        return transition.create_plan(repo, expanded_path, output, ak)


def prepare_render(repo: Path, rendered: Path, output: Path) -> int:
    """Produce a compatibility refresh input, never change target ownership.

    Old readers must be upgraded through the ordinary receipted refresh lifecycle
    before the map-only ownership transition can pass their required L1 gates.
    The L0 producer derives the preparatory map; no consumer hand-edits authority.
    """
    import shutil
    from l1_template_receipts import ensure_clean_git_target, ensure_safe_destinations, validate_established_provenance

    ensure_clean_git_target(repo)
    raw = (repo / STATE).read_bytes()
    ensure_safe_destinations(repo, [MAP, STATE])
    ensure_safe_destinations(rendered, [MAP, STATE])
    validate_established_provenance(repo, json.loads(raw))
    current = map_sections((repo / MAP).read_bytes())
    incoming = map_sections((rendered / MAP).read_bytes())
    if current.get("company", []) or ONTOLOGY not in current["template"] or incoming.get("company") != [ONTOLOGY]:
        raise ValueError("prepare render requires template-owned tree ontology and incoming company ontology")
    if output.exists() or output.is_symlink():
        raise ValueError("prepare render output must be absent")
    target = output.resolve()
    for protected in (repo.resolve(), rendered.resolve()):
        if target == protected or target.is_relative_to(protected) or protected.is_relative_to(target):
            raise ValueError("prepare render output must be disjoint from target and input")
    dropped = sorted(set(current["agent"]) - set(incoming["agent"]))
    if dropped:
        raise ValueError(f"prepare render refuses dropping company-owned patterns: {', '.join(dropped)}")
    incoming["company"] = []
    incoming["template"] = [ONTOLOGY, *incoming["template"]]
    successor = map_text(incoming)
    prepared = map_sections(successor.encode())
    if prepared.get("company", []) != current.get("company", []):
        raise ValueError("prepare render may not change company ontology ownership")
    shutil.copytree(rendered, output, symlinks=True)
    (output / MAP).write_text(successor)
    state = json.loads((output / STATE).read_bytes())
    state["ownership_map_sha256"] = hashlib.sha256(successor.encode()).hexdigest()
    (output / STATE).write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")
    print(f"prepared compatibility render at {output}; target unchanged; refresh receipt required")
    return 0
