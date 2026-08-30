#!/usr/bin/env python3
"""External AK receipt and durable-state support for L1 contract refresh."""

from __future__ import annotations

import hashlib
import json
import os
import pwd
import re
import subprocess
from pathlib import Path
from typing import Any

MAP_PATH = Path("contracts/template-ownership.yml")
STATE_PATH = Path("contracts/template-ownership-state.json")
STATE_SCHEMA = "ai-society.template-ownership-state/1"
ADOPTION_PATH = Path("contracts/template-ownership-adoption.json")
L0_ROOT = Path(__file__).resolve().parents[2]


def ensure_clean_git_target(repo: Path) -> None:
    probe = subprocess.run(
        ["git", "-C", str(repo), "status", "--porcelain"], text=True, capture_output=True
    )
    if probe.returncode != 0:
        raise ValueError("apply target must be a Git repository")
    if probe.stdout:
        raise ValueError("apply target must have a clean worktree")


def ensure_safe_destinations(repo: Path, paths: list[str]) -> None:
    resolved_repo = repo.resolve()
    for path in paths:
        destination = repo / path
        if destination.is_symlink():
            raise ValueError(f"refusing symlink destination for {path}")
        cursor = repo
        for part in Path(path).parts[:-1]:
            cursor /= part
            if cursor.is_symlink():
                raise ValueError(f"refusing symlinked destination ancestor for {path}: {cursor}")
        try:
            destination.parent.resolve(strict=False).relative_to(resolved_repo)
        except ValueError as exc:
            raise ValueError(f"propagation destination resolves outside repository: {path}") from exc


def write_atomic(content: bytes, destination: Path, mode: int = 0o644) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp = destination.with_name(destination.name + ".l1-template-new")
    if temp.exists() or temp.is_symlink():
        temp.unlink()
    temp.write_bytes(content)
    temp.chmod(mode)
    os.replace(temp, destination)


def git_output(repo: Path, *args: str) -> str:
    probe = subprocess.run(["git", "-C", str(repo), *args], text=True, capture_output=True)
    if probe.returncode != 0:
        raise ValueError(f"git provenance check failed: {' '.join(args)}")
    return probe.stdout


def git_head(repo: Path) -> str:
    return git_output(repo, "rev-parse", "HEAD").strip()


def verify_wave_evidence(
    repo: Path,
    state: dict[str, object],
    task_id: int | None = None,
    ak_command: Path | None = None,
) -> dict[str, Any]:
    if task_id is None:
        raw_task = state.get("wave_task_id")
        if not isinstance(raw_task, int) or raw_task < 1:
            raise ValueError("established state lacks wave_task_id")
        task_id = raw_task
    account_home = Path(pwd.getpwuid(os.getuid()).pw_dir)
    ak_path = ak_command or (account_home / ".local/bin/ak")
    if not ak_path.is_absolute() or not ak_path.is_file() or not os.access(ak_path, os.X_OK):
        raise ValueError(f"authoritative AK launcher is unavailable: {ak_path}")
    ak_cmd = str(ak_path)
    task_probe = subprocess.run(
        [ak_cmd, "task", "show", str(task_id), "-F", "json"], text=True, capture_output=True
    )
    if task_probe.returncode != 0:
        raise ValueError(f"unable to read AK wave task {task_id}")
    try:
        task = json.loads(task_probe.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError("AK wave task returned invalid JSON") from exc
    task_repo = task.get("repo") if isinstance(task, dict) else None
    if not isinstance(task_repo, str) or Path(task_repo).resolve() != repo.resolve():
        raise ValueError("AK wave task is not bound to the target L1 repository")

    evidence_probe = subprocess.run(
        [ak_cmd, "evidence", "task", str(task_id), "-F", "json"],
        text=True,
        capture_output=True,
    )
    if evidence_probe.returncode != 0:
        raise ValueError(f"unable to read AK evidence for wave task {task_id}")
    try:
        records = json.loads(evidence_probe.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError("AK wave evidence returned invalid JSON") from exc
    if not isinstance(records, list):
        raise ValueError("AK wave evidence response must be a list")

    map_hash = hashlib.sha256((repo / MAP_PATH).read_bytes()).hexdigest()
    for record in records:
        if not isinstance(record, dict):
            continue
        details = record.get("details")
        if (
            record.get("check_type") != "l1_contract_refresh_v1"
            or record.get("result") != "pass"
            or record.get("repo") != str(repo.resolve())
            or record.get("repo_scope") != str(repo.resolve())
            or not isinstance(details, dict)
        ):
            continue
        applied_commit = details.get("applied_commit")
        source_l0_commit = details.get("source_l0_commit")
        validation = details.get("validation")
        if (
            details.get("target_repo") != str(repo.resolve())
            or details.get("ownership_map_sha256") != map_hash
            or details.get("plan_sha256") != state.get("plan_sha256")
            or source_l0_commit != state.get("source_l0_commit")
            or details.get("wave_id") != state.get("wave_id")
            or details.get("executor") != "template-propagator"
            or not isinstance(details.get("wave_id"), str)
            or not details.get("wave_id")
            or not isinstance(applied_commit, str)
            or re.fullmatch(r"[0-9a-f]{40}", applied_commit) is None
            or not isinstance(source_l0_commit, str)
            or re.fullmatch(r"[0-9a-f]{40}", source_l0_commit) is None
            or not isinstance(validation, dict)
        ):
            continue
        required_gates = ("check-template-ci.sh", "ci/full.sh")
        if any(
            not any(str(name).endswith(gate) and code == 0 for name, code in validation.items())
            for gate in required_gates
        ):
            continue
        target_commit = subprocess.run(
            ["git", "-C", str(repo), "cat-file", "-e", f"{applied_commit}^{{commit}}"],
            capture_output=True,
        )
        source_commit = subprocess.run(
            ["git", "-C", str(L0_ROOT), "cat-file", "-e", f"{source_l0_commit}^{{commit}}"],
            capture_output=True,
        )
        if target_commit.returncode == 0 and source_commit.returncode == 0:
            return record
    raise ValueError("no passing l1_contract_refresh_v1 AK evidence matches this target and plan")


def validate_established_provenance(
    repo: Path,
    state: dict[str, object],
    ak_command: Path | None = None,
    allow_uncommitted_birth_plan: bool = False,
) -> None:
    map_hash = hashlib.sha256((repo / MAP_PATH).read_bytes()).hexdigest()
    if state.get("ownership_map_sha256") != map_hash:
        raise ValueError("established ownership state does not match the active map")
    origin = state.get("origin")
    if origin == "copier-birth":
        try:
            additions = [
                line
                for line in git_output(
                    repo, "log", "--format=%H", "--diff-filter=A", "--", STATE_PATH.as_posix()
                ).splitlines()
                if line
            ]
            roots = set(git_output(repo, "rev-list", "--max-parents=0", "HEAD").splitlines())
        except ValueError:
            if allow_uncommitted_birth_plan:
                return
            raise
        if len(additions) != 1 or additions[0] not in roots:
            raise ValueError("copier-birth ownership state was not added by the repository root commit")
        birth_answers = git_output(repo, "show", f"{additions[0]}:.copier-answers.yml")
        if "_ownership_state: established_at_birth" not in birth_answers.splitlines():
            raise ValueError("copier-birth root commit lacks its ownership marker")
        return
    if origin != "contract-refresh":
        raise ValueError("established ownership state has invalid origin")
    record = verify_wave_evidence(repo, state, ak_command=ak_command)
    details = record["details"]
    applied_commit = details["applied_commit"]
    try:
        pending_state = json.loads(git_output(repo, "show", f"{applied_commit}:{STATE_PATH}"))
        applied_map = git_output(repo, "show", f"{applied_commit}:{MAP_PATH}").encode()
    except json.JSONDecodeError as exc:
        raise ValueError("applied commit contains invalid pending ownership state") from exc
    if (
        pending_state.get("schema") != STATE_SCHEMA
        or pending_state.get("kind") != "l1_contract_refresh_state"
        or pending_state.get("state") != "applied_pending_receipt"
    ):
        raise ValueError("AK evidence applied commit lacks applied_pending_receipt state")
    if hashlib.sha256(applied_map).hexdigest() != details.get("ownership_map_sha256"):
        raise ValueError("AK evidence applied commit map hash mismatch")
    for key in ("plan_sha256", "wave_id", "source_l0_commit", "ownership_map_sha256"):
        if state.get(key) != pending_state.get(key):
            raise ValueError(f"established state changed pending receipt field: {key}")
    if state.get("wave_task_id") != record.get("task_id") or state.get("evidence_id") != record.get("id"):
        raise ValueError("established state does not bind its AK wave evidence record")


def pending_state_bytes(
    rendered: Path, plan_sha256: str, wave_id: str, source_l0_commit: str
) -> bytes:
    if re.fullmatch(r"[0-9a-f]{64}", plan_sha256) is None:
        raise ValueError("apply requires --plan-sha256 as 64 lowercase hex")
    if not wave_id.strip():
        raise ValueError("apply requires non-empty --wave-id")
    if re.fullmatch(r"[0-9a-f]{40}", source_l0_commit) is None:
        raise ValueError("apply requires --source-l0-commit as full 40-hex sha")
    source_probe = subprocess.run(
        ["git", "-C", str(L0_ROOT), "cat-file", "-e", f"{source_l0_commit}^{{commit}}"],
        capture_output=True,
    )
    if source_probe.returncode != 0:
        raise ValueError("source L0 commit does not exist in L0 history")
    state = {
        "schema": STATE_SCHEMA,
        "kind": "l1_contract_refresh_state",
        "state": "applied_pending_receipt",
        "wave_id": wave_id.strip(),
        "source_l0_commit": source_l0_commit,
        "ownership_map_sha256": hashlib.sha256((rendered / MAP_PATH).read_bytes()).hexdigest(),
        "plan_sha256": plan_sha256,
    }
    return (json.dumps(state, indent=2, sort_keys=True) + "\n").encode()


def finalized_state_bytes(
    pending: dict[str, object], task_id: int, record: dict[str, Any]
) -> bytes:
    details = record["details"]
    state = dict(pending)
    state["state"] = "established"
    state["origin"] = "contract-refresh"
    state["wave_task_id"] = task_id
    state["evidence_id"] = record["id"]
    state["applied_commit"] = details["applied_commit"]
    return (json.dumps(state, indent=2, sort_keys=True) + "\n").encode()


def finalize(
    repo: Path,
    wave_task: str,
    plan_artifact: Path,
    ak_command: Path | None = None,
) -> int:
    ensure_safe_destinations(
        repo, [MAP_PATH.as_posix(), STATE_PATH.as_posix(), ADOPTION_PATH.as_posix()]
    )
    ensure_clean_git_target(repo)
    try:
        pending = json.loads((repo / STATE_PATH).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError("unable to read applied_pending_receipt state") from exc
    if (
        not isinstance(pending, dict)
        or pending.get("schema") != STATE_SCHEMA
        or pending.get("kind") != "l1_contract_refresh_state"
        or pending.get("state") != "applied_pending_receipt"
    ):
        raise ValueError("finalize requires applied_pending_receipt state")
    task_text = wave_task.removeprefix("AK-")
    if not task_text.isdigit() or int(task_text) < 1:
        raise ValueError("--finalize-task must be AK-<positive integer>")
    task_id = int(task_text)
    if not plan_artifact.is_file() or plan_artifact.is_symlink():
        raise ValueError("--plan-artifact must be a regular file")
    if hashlib.sha256(plan_artifact.read_bytes()).hexdigest() != pending.get("plan_sha256"):
        raise ValueError("plan artifact hash does not match applied_pending_receipt")
    map_hash = hashlib.sha256((repo / MAP_PATH).read_bytes()).hexdigest()
    if map_hash != pending.get("ownership_map_sha256"):
        raise ValueError("active ownership map does not match applied_pending_receipt")
    record = verify_wave_evidence(repo, pending, task_id, ak_command=ak_command)
    details = record["details"]
    applied_commit = details["applied_commit"]
    try:
        committed_pending = json.loads(git_output(repo, "show", f"{applied_commit}:{STATE_PATH}"))
        committed_map = git_output(repo, "show", f"{applied_commit}:{MAP_PATH}").encode()
    except json.JSONDecodeError as exc:
        raise ValueError("AK evidence applied commit has invalid pending state") from exc
    if committed_pending != pending:
        raise ValueError("AK evidence applied commit does not contain the live pending state")
    if hashlib.sha256(committed_map).hexdigest() != map_hash:
        raise ValueError("AK evidence applied commit does not contain the active map")
    write_atomic(finalized_state_bytes(pending, task_id, record), repo / STATE_PATH)
    adoption_path = repo / ADOPTION_PATH
    if adoption_path.exists():
        adoption_path.unlink()
    print(f"finalized ownership state from AK evidence:{record['id']}; review and commit state closeout")
    return 0
