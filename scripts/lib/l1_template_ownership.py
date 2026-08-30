#!/usr/bin/env python3
"""Plan or apply an L0-rendered L1 contract refresh without touching company-owned paths."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from l1_template_receipts import (  # noqa: E402
    ADOPTION_PATH,
    MAP_PATH,
    STATE_PATH,
    STATE_SCHEMA,
    ensure_clean_git_target,
    ensure_safe_destinations,
    finalize,
    git_head,
    pending_state_bytes,
    validate_established_provenance,
    write_atomic,
)

SCHEMA = "ai-society.template-ownership/1"
ADOPTION_SCHEMA = "ai-society.template-ownership-adoption/1"
EVIDENCE_REF = re.compile(r"evidence:[1-9][0-9]*\Z")
IGNORED_PARTS = {".git", "__pycache__"}


def files(root: Path) -> set[str]:
    found: set[str] = set()
    for path in root.rglob("*"):
        rel = path.relative_to(root)
        if any(part in IGNORED_PARTS for part in rel.parts):
            continue
        if path.is_file() or path.is_symlink():
            found.add(rel.as_posix())
    return found


def matches(path: str, pattern: str) -> bool:
    if pattern.endswith("/**"):
        prefix = pattern[:-3]
        return path == prefix or path.startswith(prefix + "/")
    return path == pattern


def pattern_kind(pattern: str) -> tuple[str, str]:
    if not pattern or pattern.startswith("/") or pattern.endswith("/"):
        raise ValueError(f"invalid ownership pattern: {pattern!r}")
    if ".." in Path(pattern).parts:
        raise ValueError(f"ownership pattern may not traverse: {pattern}")
    if "/**" in pattern and not pattern.endswith("/**"):
        raise ValueError(f"ownership subtree wildcard must be a suffix: {pattern}")
    if pattern == "**" or "*" in pattern.removesuffix("/**"):
        raise ValueError(f"unsupported ownership wildcard: {pattern}")
    if pattern.endswith("/**"):
        prefix = pattern[:-3]
        if not prefix:
            raise ValueError("ownership subtree pattern requires a directory")
        return "subtree", prefix
    return "exact", pattern


def patterns_overlap(left: str, right: str) -> bool:
    left_kind, left_value = pattern_kind(left)
    right_kind, right_value = pattern_kind(right)
    if left_kind == right_kind == "exact":
        return left_value == right_value
    if left_kind == right_kind == "subtree":
        return (
            left_value == right_value
            or left_value.startswith(right_value + "/")
            or right_value.startswith(left_value + "/")
        )
    if left_kind == "subtree":
        return right_value == left_value or right_value.startswith(left_value + "/")
    return left_value == right_value or left_value.startswith(right_value + "/")


def load_map(root: Path) -> dict[str, list[str]]:
    path = root / MAP_PATH
    schema = ""
    sections: dict[str, list[str]] = {"template_owned": [], "agent_owned": []}
    active: str | None = None
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if raw == line and line.startswith("schema:"):
            schema = line.split(":", 1)[1].strip()
            active = None
            continue
        if raw == line and line.endswith(":") and line[:-1] in sections:
            active = line[:-1]
            continue
        if active and raw.startswith("  - "):
            pattern = raw[4:].strip()
            pattern_kind(pattern)
            sections[active].append(pattern)
            continue
        raise ValueError(f"unsupported ownership syntax at {MAP_PATH}:{number}")

    if schema != SCHEMA:
        raise ValueError(f"ownership schema must be exactly {SCHEMA}")
    if not sections["template_owned"] or not sections["agent_owned"]:
        raise ValueError("ownership map requires non-empty template_owned and agent_owned lists")
    for section, patterns in sections.items():
        if len(patterns) != len(set(patterns)):
            raise ValueError(f"duplicate ownership pattern in {section}")
    for template_pattern in sections["template_owned"]:
        for agent_pattern in sections["agent_owned"]:
            if patterns_overlap(template_pattern, agent_pattern):
                raise ValueError(
                    f"ambiguous ownership patterns: {template_pattern} and {agent_pattern}"
                )
    return {"template": sections["template_owned"], "agent": sections["agent_owned"]}


def owner(path: str, mapping: dict[str, list[str]]) -> str | None:
    kinds = [kind for kind, patterns in mapping.items() if any(matches(path, item) for item in patterns)]
    if len(kinds) > 1:
        raise ValueError(f"ambiguous ownership for {path}: {', '.join(kinds)}")
    return kinds[0] if kinds else None


def same(left: Path, right: Path) -> bool:
    if left.is_symlink() or right.is_symlink():
        return left.is_symlink() and right.is_symlink() and os.readlink(left) == os.readlink(right)
    return left.read_bytes() == right.read_bytes() and stat.S_IMODE(left.stat().st_mode) == stat.S_IMODE(right.stat().st_mode)


def show_diff(path: str, old: Path | None, new: Path) -> None:
    before = old.read_bytes() if old and old.is_file() and not old.is_symlink() else b""
    after = new.read_bytes()
    try:
        left = before.decode("utf-8").splitlines(keepends=True)
        right = after.decode("utf-8").splitlines(keepends=True)
    except UnicodeDecodeError:
        print(f"binary change: {path}")
        return
    sys.stdout.writelines(difflib.unified_diff(left, right, f"a/{path}", f"b/{path}"))


def copy_atomic(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp = destination.with_name(destination.name + ".l1-template-new")
    if temp.exists() or temp.is_symlink():
        temp.unlink()
    shutil.copy2(source, temp)
    os.replace(temp, destination)


def file_record(path: Path) -> dict[str, object]:
    return {
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "mode": stat.S_IMODE(path.stat().st_mode),
    }


def bootstrap(repo: Path, rendered: Path, apply: bool, evidence_ref: str | None) -> int:
    if not evidence_ref or not EVIDENCE_REF.fullmatch(evidence_ref.strip()):
        raise ValueError("bootstrap requires --evidence-ref evidence:<positive integer>")
    source_map = rendered / MAP_PATH
    source_state = rendered / STATE_PATH
    if source_map.is_symlink() or source_state.is_symlink():
        raise ValueError("rendered ownership control files may not be symlinks")
    mapping = load_map(rendered)
    rendered_files = files(rendered)
    for path in sorted(rendered_files):
        if (rendered / path).is_symlink():
            raise ValueError(f"rendered template symlinks are unsupported: {path}")
        if owner(path, mapping) is None:
            raise ValueError(f"unclassified rendered path: {path}; update {MAP_PATH}")
    target_map = repo / MAP_PATH
    target_state = repo / STATE_PATH
    target_adoption = repo / ADOPTION_PATH
    if any(path.exists() or path.is_symlink() for path in (target_map, target_state, target_adoption)):
        raise ValueError("bootstrap refused: target already has ownership state")

    template_paths = [path for path in sorted(rendered_files) if owner(path, mapping) == "template"]
    ensure_safe_destinations(
        repo, template_paths + [ADOPTION_PATH.as_posix(), STATE_PATH.as_posix()]
    )
    existing = {
        path: file_record(repo / path)
        for path in template_paths
        if (repo / path).is_file()
    }
    adoption = {
        "schema": ADOPTION_SCHEMA,
        "evidence_ref": evidence_ref.strip(),
        "target_head": git_head(repo),
        "ownership_map_sha256": hashlib.sha256(source_map.read_bytes()).hexdigest(),
        "existing_template_paths": existing,
    }
    adoption_bytes = (json.dumps(adoption, indent=2, sort_keys=True) + "\n").encode()
    state = {
        "schema": STATE_SCHEMA,
        "kind": "l1_contract_refresh_state",
        "state": "adopting",
        "evidence_ref": evidence_ref.strip(),
        "ownership_map_sha256": adoption["ownership_map_sha256"],
        "adoption_sha256": hashlib.sha256(adoption_bytes).hexdigest(),
    }
    state_bytes = (json.dumps(state, indent=2, sort_keys=True) + "\n").encode()

    print("BOOTSTRAP APPLY" if apply else "BOOTSTRAP PLAN (map + durable adoption state; no files changed)")
    print(f"add: {MAP_PATH}")
    print(f"add: {ADOPTION_PATH} ({len(existing)} existing template path attestations; {evidence_ref})")
    print(f"add: {STATE_PATH} (state: adopting)")
    show_diff(MAP_PATH.as_posix(), None, source_map)
    if apply:
        ensure_clean_git_target(repo)
        copy_atomic(source_map, target_map)
        write_atomic(adoption_bytes, target_adoption)
        write_atomic(state_bytes, target_state)
        print("installed map, durable adoption state, and census attestation; commit all three before refresh")
    return 0


def refresh(
    repo: Path,
    rendered: Path,
    apply: bool,
    plan_sha256: str | None = None,
    wave_id: str | None = None,
    source_l0_commit: str | None = None,
) -> int:
    map_path = repo / MAP_PATH
    state_path = repo / STATE_PATH
    adoption_path = repo / ADOPTION_PATH
    ensure_safe_destinations(
        repo, [MAP_PATH.as_posix(), STATE_PATH.as_posix(), ADOPTION_PATH.as_posix(), ".copier-answers.yml"]
    )
    if not state_path.is_file():
        raise ValueError(f"missing durable ownership state: {STATE_PATH}")
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError("invalid durable ownership state JSON") from exc
    if (
        not isinstance(state, dict)
        or state.get("schema") != STATE_SCHEMA
        or state.get("kind") != "l1_contract_refresh_state"
    ):
        raise ValueError(f"ownership state must use {STATE_SCHEMA} / l1_contract_refresh_state")
    state_name = state.get("state")
    if state_name == "applied_pending_receipt":
        raise ValueError("applied_pending_receipt requires external AK evidence and explicit finalize")
    if state_name not in {"adopting", "established"}:
        raise ValueError("ownership state must be adopting, applied_pending_receipt, or established")

    adoption = None
    if state_name == "adopting":
        if not adoption_path.is_file():
            raise ValueError("adopting ownership state requires its census attestation")
        try:
            adoption_bytes = adoption_path.read_bytes()
            adoption = json.loads(adoption_bytes)
        except json.JSONDecodeError as exc:
            raise ValueError("invalid ownership adoption attestation JSON") from exc
        if not isinstance(adoption, dict) or adoption.get("schema") != ADOPTION_SCHEMA:
            raise ValueError(f"ownership adoption attestation schema must be {ADOPTION_SCHEMA}")
        if state.get("adoption_sha256") != hashlib.sha256(adoption_bytes).hexdigest():
            raise ValueError("durable ownership state does not match the census attestation")
        map_hash = hashlib.sha256(map_path.read_bytes()).hexdigest()
        if adoption.get("ownership_map_sha256") != map_hash or state.get("ownership_map_sha256") != map_hash:
            raise ValueError("ownership adoption state does not match the active map")
        if adoption.get("evidence_ref") != state.get("evidence_ref"):
            raise ValueError("ownership adoption evidence references disagree")
        if not EVIDENCE_REF.fullmatch(str(adoption.get("evidence_ref", ""))):
            raise ValueError("ownership adoption evidence reference is invalid")
        if not isinstance(adoption.get("existing_template_paths"), dict):
            raise ValueError("ownership adoption attestation lacks existing_template_paths")
        ancestor = subprocess.run(
            ["git", "-C", str(repo), "merge-base", "--is-ancestor", str(adoption.get("target_head", "")), "HEAD"],
            capture_output=True,
        )
        if ancestor.returncode != 0:
            raise ValueError("ownership census target HEAD is not in this repository lineage")
    elif adoption_path.exists():
        raise ValueError("established ownership state may not retain an adoption attestation")
    if state_name == "established":
        validate_established_provenance(
            repo, state, allow_uncommitted_birth_plan=not apply
        )
        answers = repo / ".copier-answers.yml"
        if not answers.is_file() or "_ownership_state: established_at_birth" not in answers.read_text(encoding="utf-8").splitlines():
            raise ValueError("established ownership state lacks its Copier birth/refresh marker")

    current_map = load_map(repo)
    next_map = load_map(rendered)
    rendered_files = files(rendered)

    for path in sorted(rendered_files):
        if (rendered / path).is_symlink():
            raise ValueError(f"rendered template symlinks are unsupported: {path}")
        if owner(path, next_map) is None:
            raise ValueError(f"unclassified rendered path: {path}; update {MAP_PATH}")
    for current_agent in current_map["agent"]:
        for next_template in next_map["template"]:
            if patterns_overlap(current_agent, next_template):
                raise ValueError(
                    f"refusing agent-to-template ownership change: {current_agent} -> {next_template}"
                )

    template_paths = [path for path in sorted(rendered_files) if owner(path, next_map) == "template"]
    ensure_safe_destinations(repo, template_paths)
    if adoption is not None:
        records = adoption["existing_template_paths"]
        record_paths = list(records)
        if any(not isinstance(path, str) for path in record_paths):
            raise ValueError("ownership adoption path keys must be strings")
        ensure_safe_destinations(repo, record_paths)
        for path, record in records.items():
            if owner(path, current_map) != "template" or not isinstance(record, dict):
                raise ValueError(f"invalid attested template path: {path}")
            destination = repo / path
            if not destination.is_file() or record != file_record(destination):
                raise ValueError(f"existing template path drifted after ownership census: {path}")
        for path in template_paths:
            destination = repo / path
            if (
                destination.exists()
                and path not in records
                and path not in {MAP_PATH.as_posix(), STATE_PATH.as_posix()}
            ):
                raise ValueError(f"unattested template-path collision after ownership census: {path}")

    actions: list[tuple[str, str]] = []
    preserved = 0
    for path in sorted(rendered_files):
        next_owner = owner(path, next_map)
        destination = repo / path
        if next_owner == "agent":
            preserved += 1
            continue
        if path == STATE_PATH.as_posix():
            continue
        if destination.exists() or destination.is_symlink():
            current_owner = owner(path, current_map)
            if current_owner != "template":
                raise ValueError(f"refusing template update without prior template ownership: {path}")
            if not same(destination, rendered / path):
                actions.append(("update", path))
        else:
            actions.append(("add", path))

    if not actions:
        print(f"ok: template-owned L1 paths are current; preserved agent-owned paths: {preserved}")
        return 0

    pending = None
    if apply:
        pending = pending_state_bytes(
            rendered,
            plan_sha256 or "",
            wave_id or "",
            source_l0_commit or "",
        )

    print("APPLY" if apply else "PLAN (no files changed; pass --apply to apply)")
    if adoption is not None:
        print(f"adoption evidence: {adoption.get('evidence_ref', '<missing>')}")
    print(f"preserve: {preserved} rendered agent-owned path(s)")
    print("note: target-only paths are outside this add/update refresh and are never deleted")
    for action, path in actions:
        print(f"{action}: {path}")
        show_diff(path, repo / path if (repo / path).exists() else None, rendered / path)

    if apply:
        ensure_clean_git_target(repo)
        ensure_safe_destinations(repo, [path for _, path in actions])
        for _, path in actions:
            copy_atomic(rendered / path, repo / path)
        if pending is None:
            raise ValueError("internal error: pending state was not prevalidated")
        write_atomic(pending, state_path)
        print("applied template-owned actions; commit applied_pending_receipt, run gates, record AK evidence, then finalize")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--rendered", type=Path)
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--bootstrap-map", action="store_true")
    parser.add_argument("--evidence-ref")
    parser.add_argument("--plan-sha256")
    parser.add_argument("--wave-id")
    parser.add_argument("--source-l0-commit")
    parser.add_argument("--finalize-task")
    parser.add_argument("--plan-artifact", type=Path)
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    try:
        if args.finalize_task:
            if args.apply or args.bootstrap_map or args.plan_artifact is None:
                raise ValueError("finalize requires --finalize-task and --plan-artifact only")
            return finalize(repo, args.finalize_task, args.plan_artifact.resolve())
        if args.rendered is None:
            raise ValueError("plan/apply requires --rendered")
        rendered = args.rendered.resolve()
        if args.bootstrap_map:
            return bootstrap(repo, rendered, args.apply, args.evidence_ref)
        return refresh(
            repo,
            rendered,
            args.apply,
            args.plan_sha256,
            args.wave_id,
            args.source_l0_commit,
        )
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
