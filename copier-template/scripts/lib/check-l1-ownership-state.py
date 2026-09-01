#!/usr/bin/env python3
"""Validate the structural L1 ownership lifecycle without imposing company policy."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAP = ROOT / "contracts/template-ownership.yml"
STATE = ROOT / "contracts/template-ownership-state.json"
ADOPTION = ROOT / "contracts/template-ownership-adoption.json"
ANSWERS = ROOT / ".copier-answers.yml"
STATE_SCHEMA = "ai-society.template-ownership-state/1"
STATE_SCHEMA_V2 = "ai-society.template-ownership-state/2"
STATE_KIND = "l1_contract_refresh_state"
STATE_KIND_V2 = "l1_ownership_transition_state"
ADOPTION_SCHEMA = "ai-society.template-ownership-adoption/1"
PENDING_KEYS = {
    "kind", "ownership_map_sha256", "plan_sha256", "schema",
    "source_l0_commit", "state", "wave_id",
}
V2_PENDING_KEYS = {
    "schema", "kind", "state", "decision_id", "transition_task_id", "executor",
    "predecessor_commit", "predecessor_state_sha256", "predecessor_map_sha256",
    "ownership_map_sha256", "plan_sha256", "adr_commit",
}
V2_FINAL_KEYS = V2_PENDING_KEYS | {"origin", "evidence_id", "applied_commit"}
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
EXECUTOR = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/-]{2,127}\Z")


def read_json(path: Path, label: str) -> tuple[dict[str, object], bytes]:
    try:
        raw = path.read_bytes()
        value = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid {label}: {path}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value, raw


def has_birth_marker() -> bool:
    try:
        return "_ownership_state: established_at_birth" in ANSWERS.read_text(
            encoding="utf-8"
        ).splitlines()
    except OSError as exc:
        raise ValueError("unable to read .copier-answers.yml") from exc


def git(*args: str) -> str:
    environment = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    environment.update(GIT_NO_REPLACE_OBJECTS="1", GIT_GRAFT_FILE=os.devnull)
    probe = subprocess.run(
        ["git", "--no-replace-objects", "-C", str(ROOT), *args],
        text=True, capture_output=True, env=environment,
    )
    if probe.returncode != 0:
        raise ValueError(f"Git ownership provenance check failed: {' '.join(args)}")
    return probe.stdout


def map_sections(raw: bytes) -> dict[str, list[str]]:
    sections = {"template_owned": [], "agent_owned": []}
    active = None
    for line in raw.decode("utf-8").splitlines():
        if line in ("template_owned:", "agent_owned:"):
            active = line[:-1]
        elif active and line.startswith("  - "):
            sections[active].append(line[4:].strip())
    return sections


def matches(path: str, pattern: str) -> bool:
    return path == pattern[:-3] or path.startswith(pattern[:-3] + "/") if pattern.endswith("/**") else path == pattern


def validate_v2(state: dict[str, object], state_raw: bytes, map_hash: str) -> None:
    lifecycle = state.get("state")
    expected = V2_PENDING_KEYS if lifecycle == "ownership_transition_pending_receipt" else V2_FINAL_KEYS
    if lifecycle not in {"ownership_transition_pending_receipt", "established"} or set(state) != expected:
        raise ValueError("v2 ownership transition state has unsupported lifecycle or keys")
    if any(type(state.get(key)) is not int or state[key] < 1 for key in ("decision_id", "transition_task_id")):
        raise ValueError("v2 ownership decision/task IDs must be positive integers")
    if lifecycle == "established" and (type(state.get("evidence_id")) is not int or state["evidence_id"] < 1):
        raise ValueError("v2 ownership evidence ID must be a positive integer")
    if not isinstance(state.get("executor"), str) or EXECUTOR.fullmatch(state["executor"]) is None:
        raise ValueError("v2 ownership executor format is invalid")
    for key in ("predecessor_state_sha256", "predecessor_map_sha256", "ownership_map_sha256", "plan_sha256"):
        if not isinstance(state.get(key), str) or HEX64.fullmatch(state[key]) is None:
            raise ValueError(f"v2 ownership {key} must be lowercase sha256")
    if not isinstance(state.get("adr_commit"), str) or HEX40.fullmatch(state["adr_commit"]) is None:
        raise ValueError("v2 ownership adr_commit must be a full lowercase Git OID")
    if state.get("ownership_map_sha256") != map_hash or ADOPTION.exists():
        raise ValueError("v2 ownership state/map/adoption binding mismatch")
    predecessor = state.get("predecessor_commit")
    if not isinstance(predecessor, str) or HEX40.fullmatch(predecessor) is None:
        raise ValueError("v2 ownership predecessor commit is invalid")
    old_map = git("show", f"{predecessor}:contracts/template-ownership.yml").encode()
    old_state = git("show", f"{predecessor}:contracts/template-ownership-state.json").encode()
    if hashlib.sha256(old_map).hexdigest() != state.get("predecessor_map_sha256") or hashlib.sha256(old_state).hexdigest() != state.get("predecessor_state_sha256"):
        raise ValueError("v2 ownership state does not bind predecessor bytes")
    old, new = map_sections(old_map), map_sections(MAP.read_bytes())
    for agent_pattern in old["agent_owned"]:
        if any(matches(agent_pattern.removesuffix("/**"), pattern) or matches(pattern.removesuffix("/**"), agent_pattern) for pattern in new["template_owned"]):
            raise ValueError("ordinary successor validation refuses agent-to-template ownership adoption")
    applied = git("rev-parse", "HEAD").strip() if lifecycle == "ownership_transition_pending_receipt" else state.get("applied_commit")
    if not isinstance(applied, str) or HEX40.fullmatch(applied) is None:
        raise ValueError("v2 ownership applied commit is invalid")
    parents = git("rev-list", "--parents", "-n", "1", applied).split()
    if len(parents) != 2 or parents[1] != predecessor:
        raise ValueError("pending ownership topology commit must directly follow predecessor")
    applied_state_raw = git("show", f"{applied}:contracts/template-ownership-state.json").encode()
    applied_map = git("show", f"{applied}:contracts/template-ownership.yml").encode()
    try:
        applied_state = json.loads(applied_state_raw)
    except json.JSONDecodeError as exc:
        raise ValueError("applied ownership state is invalid JSON") from exc
    if set(applied_state) != V2_PENDING_KEYS or applied_state.get("state") != "ownership_transition_pending_receipt" or any(applied_state.get(key) != state.get(key) for key in V2_PENDING_KEYS - {"state"}) or hashlib.sha256(applied_map).hexdigest() != map_hash:
        raise ValueError("applied commit does not preserve exact pending v2 bindings")
    if lifecycle == "ownership_transition_pending_receipt":
        if applied_state_raw != state_raw:
            raise ValueError("live pending ownership state differs from applied commit")
        return
    if state.get("origin") != "ownership-transition":
        raise ValueError("established v2 state has wrong origin")
    finals = []
    for commit in git("log", "--format=%H", "--", "contracts/template-ownership-state.json").splitlines():
        commit_parents = git("rev-list", "--parents", "-n", "1", commit).split()
        changed = git("diff-tree", "--no-commit-id", "--name-only", "-r", commit).splitlines()
        if len(commit_parents) == 2 and commit_parents[1] == applied and changed == ["contracts/template-ownership-state.json"] and git("show", f"{commit}:contracts/template-ownership-state.json").encode() == state_raw:
            finals.append(commit)
    if len(finals) != 1:
        raise ValueError("v2 ownership requires one state-only final commit directly after applied commit")

def validate() -> None:
    try:
        map_hash = hashlib.sha256(MAP.read_bytes()).hexdigest()
    except OSError as exc:
        raise ValueError("unable to read template ownership map") from exc
    state, state_raw = read_json(STATE, "ownership state")
    if state.get("schema") == STATE_SCHEMA_V2 and state.get("kind") == STATE_KIND_V2:
        validate_v2(state, state_raw, map_hash)
        return
    if state.get("schema") != STATE_SCHEMA or state.get("kind") != STATE_KIND:
        raise ValueError("ownership state schema/kind mismatch")
    lifecycle = state.get("state")
    if lifecycle not in {"adopting", "applied_pending_receipt", "established"}:
        raise ValueError("unsupported ownership lifecycle state")
    if state.get("ownership_map_sha256") != map_hash:
        raise ValueError("ownership state does not bind the active map")
    if lifecycle == "adopting":
        adoption, adoption_raw = read_json(ADOPTION, "ownership adoption attestation")
        if adoption.get("schema") != ADOPTION_SCHEMA:
            raise ValueError("ownership adoption schema mismatch")
        if adoption.get("ownership_map_sha256") != map_hash:
            raise ValueError("ownership adoption does not bind the active map")
        if state.get("adoption_sha256") != hashlib.sha256(adoption_raw).hexdigest():
            raise ValueError("ownership state does not bind the adoption attestation")
        evidence_ref = adoption.get("evidence_ref")
        if evidence_ref != state.get("evidence_ref") or not isinstance(evidence_ref, str) or re.fullmatch(r"evidence:[1-9][0-9]*", evidence_ref) is None:
            raise ValueError("ownership adoption evidence binding mismatch")
        if not isinstance(adoption.get("existing_template_paths"), dict):
            raise ValueError("ownership adoption lacks existing_template_paths")
        return
    if not has_birth_marker():
        raise ValueError(f"{lifecycle} ownership state lacks the Copier refresh marker")
    if lifecycle == "applied_pending_receipt" and set(state) != PENDING_KEYS:
        raise ValueError("applied_pending_receipt must use the exact seven-field schema")
    if lifecycle == "established" and ADOPTION.exists():
        raise ValueError("established ownership state may not retain adoption attestation")


def main() -> int:
    try:
        validate()
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print("ok: L1 ownership lifecycle structure")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
