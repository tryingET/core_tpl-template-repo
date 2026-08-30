#!/usr/bin/env python3
"""Validate the structural L1 ownership lifecycle without imposing company policy."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAP = ROOT / "contracts/template-ownership.yml"
STATE = ROOT / "contracts/template-ownership-state.json"
ADOPTION = ROOT / "contracts/template-ownership-adoption.json"
ANSWERS = ROOT / ".copier-answers.yml"
STATE_SCHEMA = "ai-society.template-ownership-state/1"
STATE_KIND = "l1_contract_refresh_state"
ADOPTION_SCHEMA = "ai-society.template-ownership-adoption/1"
PENDING_KEYS = {
    "kind",
    "ownership_map_sha256",
    "plan_sha256",
    "schema",
    "source_l0_commit",
    "state",
    "wave_id",
}


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


def validate() -> None:
    try:
        map_hash = hashlib.sha256(MAP.read_bytes()).hexdigest()
    except OSError as exc:
        raise ValueError("unable to read template ownership map") from exc
    state, _ = read_json(STATE, "ownership state")
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
        if (
            evidence_ref != state.get("evidence_ref")
            or not isinstance(evidence_ref, str)
            or re.fullmatch(r"evidence:[1-9][0-9]*", evidence_ref) is None
        ):
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
