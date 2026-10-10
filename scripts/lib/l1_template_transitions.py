#!/usr/bin/env python3
"""Plan, apply, and finalize receipted successor L1 ownership transitions."""

from __future__ import annotations

import json
import os
import pwd
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from l1_template_ownership import load_map  # noqa: E402
from l1_template_transition_delta import validate_git_delta, validate_rel  # noqa: E402
import l1_template_company as company  # noqa: E402
from l1_template_company import parse_map_bytes, plan_path_parent  # noqa: E402
from l1_template_receipts import (  # noqa: E402
    MAP_PATH,
    STATE_PATH,
    ensure_clean_git_target,
    ensure_safe_destinations,
    git_common_dir,
    git_head,
    git_output,
    git_run,
    git_top,
    registered_worktrees,
    sanitized_git_environment,
    validate_established_provenance,
    write_atomic,
)
# Legacy ai-society.template-ownership-transition-plan/1 remains supported.
from l1_template_transition_plan import (  # noqa: E402
    PLAN_SCHEMA, EXECUTOR_RE, HEX40, HEX64, REQUIRED_VALIDATION,
    canonical_bytes, digest_bytes, semantic_delta, plan_hash, validate_plan,
)
STATE_SCHEMA_V2 = "ai-society.template-ownership-state/2"
STATE_KIND = "l1_ownership_transition_state"
PENDING_STATE = "ownership_transition_pending_receipt"
EVIDENCE_TYPE = "l1_ownership_transition_v1"
AK_INSTANT = re.compile(r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})(?:\.(\d{1,9}))?(Z|[+-]\d{2}:\d{2})\Z")
PENDING_KEYS = {
    "schema", "kind", "state", "decision_id", "transition_task_id", "executor",
    "predecessor_commit", "predecessor_state_sha256", "predecessor_map_sha256",
    "ownership_map_sha256", "plan_sha256", "adr_commit",
}
FINAL_KEYS = PENDING_KEYS | {"origin", "evidence_id", "applied_commit"}
# Binding an ordinary refresh carries forward from the established v2 state it replaces.
INHERITED_KEYS = {
    "transition_task_id", "decision_id", "evidence_id", "plan_sha256", "executor",
    "applied_commit", "final_commit", "state_sha256",
}


def load_object(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file() or path.is_symlink():
        raise ValueError(f"{label} must be a regular file")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid {label} JSON") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value
def verify_registered_target(repo: Path, canonical: Path) -> None:
    if (
        git_top(canonical) != canonical.resolve()
        or git_top(repo) != repo.resolve()
        or git_common_dir(canonical) != git_common_dir(repo)
        or repo.resolve() not in registered_worktrees(canonical)
    ):
        raise ValueError("target must be a registered worktree of the canonical task repository")


def ak_json(ak: Path, *args: str) -> Any:
    probe = subprocess.run([str(ak), *args], text=True, capture_output=True)
    if probe.returncode != 0:
        raise ValueError(f"AK query failed: {' '.join(args)}")
    try:
        return json.loads(probe.stdout)
    except json.JSONDecodeError as exc:
        raise ValueError("AK returned invalid JSON") from exc


def authoritative_ak(override: Path | None = None) -> Path:
    # ``override`` is an internal dependency-injection seam; production CLIs never expose it.
    path = override or (Path(pwd.getpwuid(os.getuid()).pw_dir) / ".local/bin/ak")
    if not path.is_absolute() or not path.is_file() or not os.access(path, os.X_OK):
        raise ValueError(f"authoritative AK launcher is unavailable: {path}")
    return path
def ak_instant(value: object, label: str) -> tuple[datetime, int]:
    match = AK_INSTANT.fullmatch(value) if isinstance(value, str) else None
    if match is None:
        raise ValueError(f"{label} must be an RFC 3339 timestamp with an explicit offset")
    offset = "+00:00" if match[3] == "Z" else match[3]
    whole = datetime.fromisoformat(match[1] + offset).astimezone(timezone.utc)
    return whole, int((match[2] or "").ljust(9, "0"))


def verify_completion_evidence(
    ak: Path, task: dict[str, Any], executor: str, evidence_id: int, plan_sha256: str,
) -> dict[str, Any]:
    """Bind a done transition task to the immutable evidence recorded while it was live."""
    records = ak_json(ak, "evidence", "task", str(task["id"]), "-F", "json")
    pinned = [
        record for record in records if isinstance(record, dict) and record.get("id") == evidence_id
    ] if isinstance(records, list) and type(evidence_id) is int and evidence_id > 0 else []
    if len(pinned) != 1:
        raise ValueError("done transition task lacks its unique pinned evidence record")
    record = pinned[0]
    details = record.get("details")
    if (
        record.get("task_id") != task["id"] or record.get("check_type") != EVIDENCE_TYPE
        or record.get("result") != "pass" or not isinstance(details, dict)
        or not isinstance(details.get("plan"), dict)
    ):
        raise ValueError("pinned evidence is not a passing l1_ownership_transition_v1 record for the done task")
    plan = validate_plan(json.loads(json.dumps(details["plan"])))
    if plan["executor"] != executor or plan["transition_task_id"] != task["id"]:
        raise ValueError("pinned evidence plan executor does not match the transition executor")
    if plan["canonical_plan_sha256"] != plan_sha256:
        raise ValueError("pinned evidence plan hash does not match the transition plan_sha256")
    if ak_instant(record.get("checked_at"), "evidence checked_at") > ak_instant(task.get("completed_at"), "task completed_at"):
        raise ValueError("pinned evidence was recorded after the transition task completed")
    return record


def verify_authority(
    repo: Path, decision_id: int, task_id: int, executor: str, adr_commit: str,
    ak_command: Path | None = None, completed_binding: tuple[int, str] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Verify AK authority for a transition.

    Plan/apply/finalize pass no ``completed_binding`` and so require the live claim:
    status ``claimed`` with ``claimed_by`` equal to the fixed executor. AK clears
    ``claimed_by`` when a task completes (and keeps no completing actor), so after
    completion the provenance is the immutable evidence record pinned by the state:
    a ``done`` task verifies only through ``completed_binding`` (evidence_id,
    plan_sha256), and that evidence must predate ``completed_at``.
    """
    ak = authoritative_ak(ak_command)
    task = ak_json(ak, "task", "show", str(task_id), "-F", "json")
    packet = ak_json(ak, "decision", "get", str(decision_id), "-F", "json")
    if not isinstance(task, dict) or not isinstance(packet, dict):
        raise ValueError("AK authority payload is malformed")
    canonical = Path(str(task.get("repo", ""))).resolve()
    verify_registered_target(repo, canonical)
    if task.get("id") != task_id or task.get("status") not in {"claimed", "done"}:
        raise ValueError("transition task is not active or done")
    if task["status"] == "claimed":
        if task.get("claimed_by") != executor:
            raise ValueError("transition task executor does not match its fixed claimant")
    elif completed_binding is None:
        raise ValueError("done transition task is verifiable only through its pinned evidence record")
    elif task.get("claimed_by") not in {None, executor}:
        raise ValueError("done transition task names a different claimant")
    else:
        verify_completion_evidence(ak, task, executor, *completed_binding)
    decision = packet.get("decision")
    links = packet.get("linked_tasks")
    if (
        not isinstance(decision, dict)
        or decision.get("id") != decision_id
        or decision.get("scope") != "repo"
        or Path(str(decision.get("repo_scope", ""))).resolve() != canonical
        or decision.get("outcome") != "accepted"
        or not isinstance(decision.get("adr_ref"), str)
        or not isinstance(links, list)
        or not any(
            isinstance(link, dict) and link.get("task_id") == task_id
            and link.get("link_role") == "post_adr_execution" for link in links
        )
    ):
        raise ValueError("accepted repo-scoped Decision/ADR does not authorize the transition task")
    if not HEX40.fullmatch(adr_commit):
        raise ValueError("adr_commit must be full lowercase 40-hex")
    if git_run(repo, "cat-file", "-e", f"{adr_commit}^{{commit}}").returncode != 0:
        raise ValueError("ADR commit does not exist in target history")
    if git_run(repo, "merge-base", "--is-ancestor", adr_commit, "HEAD").returncode != 0:
        raise ValueError("ADR commit is not an ancestor of the transition base")
    if git_run(repo, "cat-file", "-e", f"{adr_commit}:{decision['adr_ref']}").returncode != 0:
        raise ValueError("accepted ADR path is absent from the bound ADR commit")
    return task, packet

def create_plan(repo: Path, spec_path: Path, output: Path, ak_command: Path | None = None) -> int:
    ensure_clean_git_target(repo)
    company.external_output(repo, output)
    spec = load_object(spec_path, "transition spec")
    required = {"decision_id", "adr_commit", "transition_task_id", "executor", "next_map", "git_delta", "validation", "rollback"}
    convergence = "ontology_convergence" in spec
    if set(spec) != required | ({"ontology_convergence"} if convergence else set()):
        raise ValueError("transition spec must use exact authority fields and optional convergence preflight")
    executor = spec["executor"]
    if not isinstance(executor, str) or not EXECUTOR_RE.fullmatch(executor):
        raise ValueError("invalid fixed executor")
    verify_authority(repo, spec["decision_id"], spec["transition_task_id"], executor, spec["adr_commit"], ak_command)
    next_map_path = Path(spec["next_map"])
    if not next_map_path.is_absolute() or not next_map_path.is_file() or next_map_path.is_symlink():
        raise ValueError("next_map must be an absolute regular file")
    next_raw = next_map_path.read_bytes()
    output.parent.mkdir(parents=True, exist_ok=True)
    next_mapping = parse_map_bytes(next_raw, output.parent)
    delta = semantic_delta(load_map(repo), next_mapping)
    state_raw = (repo / STATE_PATH).read_bytes()
    state = json.loads(state_raw)
    validate_established_provenance(repo, state, ak_command=ak_command)
    plan: dict[str, Any] = {
        "schema": PLAN_SCHEMA,
        "target_repo": str(Path(str(ak_json(authoritative_ak(ak_command), "task", "show", str(spec["transition_task_id"]), "-F", "json")["repo"])).resolve()),
        "decision_id": spec["decision_id"], "adr_commit": spec["adr_commit"],
        "transition_task_id": spec["transition_task_id"], "executor": executor,
        "base_commit": git_head(repo), "predecessor_state_sha256": digest_bytes(state_raw),
        "predecessor_map_sha256": digest_bytes((repo / MAP_PATH).read_bytes()),
        "next_map_sha256": digest_bytes(next_raw), "next_map_text": next_raw.decode("utf-8"),
        "map_delta": delta, "git_delta": validate_git_delta(spec["git_delta"], allow_empty=True),
        "validation": spec["validation"], "rollback": spec["rollback"],
    }
    if convergence:
        import l1_template_fold as fold
        fold.configure(repo, plan, spec["ontology_convergence"], ak_command)
    else:
        company.configure_plan(repo, plan, ak_command)
    plan["canonical_plan_sha256"] = plan_hash(plan)
    validate_plan(plan)
    write_atomic(canonical_bytes(plan), output)
    print(f"planned ownership transition {plan['canonical_plan_sha256']} (no repository files changed)")
    return 0
def git_bytes(repo: Path, *args: str) -> bytes:
    probe = subprocess.run(
        ["git", "--no-replace-objects", "-C", str(repo), *args], capture_output=True,
        env=sanitized_git_environment(),
    )
    if probe.returncode != 0:
        raise ValueError(f"binary Git provenance check failed: {' '.join(args)}")
    return probe.stdout
def decode_delta(repo: Path, raw: bytes, allow_controls: bool = False) -> list[dict[str, Any]]:
    tokens = raw.split(b"\0"); result: list[dict[str, Any]] = []
    for index in range(0, len(tokens) - 1, 2):
        if not tokens[index]:
            continue
        try:
            fields = tokens[index].decode("ascii").split()
            path = tokens[index + 1].decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError("Git transition paths must be UTF-8") from exc
        if len(fields) != 5:
            raise ValueError("unsupported Git delta record")
        old_mode, new_mode = fields[0][1:], fields[1]
        old_oid, new_oid = fields[2], fields[3]
        content = digest_bytes(git_bytes(repo, "cat-file", "blob", new_oid)) if new_mode in {"100644", "100755", "120000"} else None
        result.append({
            "path": path, "old_mode": old_mode, "new_mode": new_mode,
            "old_oid": None if old_mode == "000000" else old_oid,
            "new_oid": None if new_mode == "000000" else new_oid,
            "content_sha256": content,
        })
    return validate_git_delta(result, allow_controls, allow_empty=True)
def index_delta(repo: Path) -> list[dict[str, Any]]:
    return decode_delta(repo, git_bytes(
        repo, "diff", "--cached", "--raw", "--no-renames", "-z", "--full-index", "--abbrev=40"
    ))


def index_from_commit(repo: Path, base: str, applied: str) -> list[dict[str, Any]]:
    return decode_delta(repo, git_bytes(
        repo, "diff", "--raw", "--no-renames", "-z", "--full-index", "--abbrev=40", base, applied
    ), allow_controls=True)


def pending_bytes(plan: dict[str, Any]) -> bytes:
    state = {
        "schema": STATE_SCHEMA_V2, "kind": STATE_KIND, "state": PENDING_STATE,
        "decision_id": plan["decision_id"], "transition_task_id": plan["transition_task_id"],
        "executor": plan["executor"], "predecessor_commit": plan["base_commit"],
        "predecessor_state_sha256": plan["predecessor_state_sha256"],
        "predecessor_map_sha256": plan["predecessor_map_sha256"],
        "ownership_map_sha256": plan["next_map_sha256"],
        "plan_sha256": plan["canonical_plan_sha256"], "adr_commit": plan["adr_commit"],
    }
    return (json.dumps(state, indent=2, sort_keys=True) + "\n").encode()


def bind_plan(repo: Path, plan: dict[str, Any], ak_command: Path | None) -> None:
    if git_head(repo) != plan["base_commit"]:
        raise ValueError("transition base commit drifted")
    task, _ = verify_authority(
        repo, plan["decision_id"], plan["transition_task_id"], plan["executor"],
        plan["adr_commit"], ak_command,
    )
    if Path(task["repo"]).resolve() != Path(plan["target_repo"]).resolve():
        raise ValueError("transition plan target_repo does not match canonical AK task repository")
    state_raw = (repo / STATE_PATH).read_bytes(); map_raw = (repo / MAP_PATH).read_bytes()
    if digest_bytes(state_raw) != plan["predecessor_state_sha256"] or digest_bytes(map_raw) != plan["predecessor_map_sha256"]:
        raise ValueError("predecessor ownership state or map drifted")
    if semantic_delta(load_map(repo), parse_map_bytes(plan["next_map_text"].encode(), plan_path_parent(repo))) != plan["map_delta"]:
        raise ValueError("transition plan semantic map delta is not derived from its bound maps")
    validate_established_provenance(repo, json.loads(state_raw), ak_command=ak_command)
    company.verify_transfer(repo, plan, ak_command, live=True)

def apply(repo: Path, plan_path: Path, ak_command: Path | None = None) -> int:
    plan = validate_plan(load_object(plan_path, "transition plan")); bind_plan(repo, plan, ak_command)
    status = git_run(repo, "status", "--porcelain", "--untracked-files=all", "--ignore-submodules=none").stdout.splitlines()
    if any(not line.startswith(("M ", "A ", "D ")) for line in status):
        raise ValueError("apply refuses unstaged, untracked, conflicted, or submodule worktree drift")
    if index_delta(repo) != plan["git_delta"]:
        raise ValueError("staged Git topology does not exactly match transition plan")
    ensure_safe_destinations(repo, [MAP_PATH.as_posix(), STATE_PATH.as_posix()])
    write_atomic(plan["next_map_text"].encode(), repo / MAP_PATH)
    write_atomic(pending_bytes(plan), repo / STATE_PATH)
    print("applied successor map and ownership_transition_pending_receipt; stage control files and commit")
    if "ontology_convergence" in plan:
        print("convergence /3 requires commit-message --plan <plan> --output <external-file>, then git commit -F <external-file>")
    return 0


def matching_evidence(repo: Path, plan: dict[str, Any], ak_command: Path | None = None) -> dict[str, Any]:
    records = ak_json(
        authoritative_ak(ak_command), "evidence", "task", str(plan["transition_task_id"]), "-F", "json"
    )
    if not isinstance(records, list):
        raise ValueError("AK transition evidence response must be a list")
    result_ids = {gate["id"] for gate in REQUIRED_VALIDATION}; canonical = plan["target_repo"]
    matches = [record for record in records if (
        isinstance(record, dict) and type(record.get("id")) is int and record["id"] > 0
        and record.get("task_id") == plan["transition_task_id"]
        and record.get("check_type") == EVIDENCE_TYPE and record.get("result") == "pass"
        and record.get("repo") == canonical and record.get("repo_scope") == canonical
        and isinstance(record.get("details"), dict)
        and set(record["details"]) == {"plan", "applied_commit", "validation_results"}
        and record["details"].get("plan") == plan
        and isinstance(record["details"].get("applied_commit"), str)
        and HEX40.fullmatch(record["details"]["applied_commit"])
        and isinstance(record["details"].get("validation_results"), dict)
        and set(record["details"]["validation_results"]) == result_ids
        and all(type(value) is int and value == 0 for value in record["details"]["validation_results"].values())
    )]
    if len(matches) != 1:
        raise ValueError("exactly one passing l1_ownership_transition_v1 evidence record must match the plan")
    return matches[0]


def verify_applied(repo: Path, plan: dict[str, Any], applied: str, pending_raw: bytes) -> None:
    parents = git_output(repo, "rev-list", "--parents", "-n", "1", applied).split()
    if len(parents) != 2 or parents[1] != plan["base_commit"]:
        raise ValueError("pending topology commit must be the direct child of transition base")
    if "ontology_convergence" in plan:
        from l1_ontology_convergence import trailer_plan
        if trailer_plan(lambda *args: git_output(repo, *args), applied) != plan:
            raise ValueError("applied convergence commit trailer differs from exact canonical plan")
    committed_state = git_bytes(repo, "show", f"{applied}:{STATE_PATH}")
    committed_map = git_bytes(repo, "show", f"{applied}:{MAP_PATH}")
    if committed_state != pending_raw or committed_map != plan["next_map_text"].encode():
        raise ValueError("evidence applied commit does not contain exact pending state and map")
    actual = index_from_commit(repo, plan["base_commit"], applied)
    controls = [entry for entry in actual if entry["path"] in {MAP_PATH.as_posix(), STATE_PATH.as_posix()}]
    if (
        {entry["path"] for entry in controls} != {MAP_PATH.as_posix(), STATE_PATH.as_posix()}
        or any(entry["old_mode"] != "100644" or entry["new_mode"] != "100644" for entry in controls)
        or actual != sorted(plan["git_delta"] + controls, key=lambda entry: entry["path"])
    ):
        raise ValueError("pending topology commit delta does not exactly match plan plus control files")


def finalize(repo: Path, plan_path: Path, task_text: str, ak_command: Path | None = None) -> int:
    ensure_clean_git_target(repo); plan = validate_plan(load_object(plan_path, "transition plan"))
    if task_text != f"AK-{plan['transition_task_id']}":
        raise ValueError("finalize task does not match transition plan")
    task, _ = verify_authority(repo, plan["decision_id"], plan["transition_task_id"], plan["executor"], plan["adr_commit"], ak_command)
    if Path(task["repo"]).resolve() != Path(plan["target_repo"]).resolve():
        raise ValueError("transition plan target_repo does not match canonical AK task repository")
    pending_raw = (repo / STATE_PATH).read_bytes()
    if pending_raw != pending_bytes(plan) or digest_bytes((repo / MAP_PATH).read_bytes()) != plan["next_map_sha256"]:
        raise ValueError("live pending v2 state or successor map does not exactly match transition plan")
    record = matching_evidence(repo, plan, ak_command); applied = record["details"]["applied_commit"]
    if git_head(repo) != applied:
        raise ValueError("finalize requires HEAD at the exact evidence applied commit")
    verify_applied(repo, plan, applied, pending_raw)
    company.verify_transfer(repo, plan, ak_command, live=True)
    final = dict(json.loads(pending_raw), state="established", origin="ownership-transition", evidence_id=record["id"], applied_commit=applied)
    if set(final) != FINAL_KEYS:
        raise ValueError("internal final v2 state schema error")
    write_atomic((json.dumps(final, indent=2, sort_keys=True) + "\n").encode(), repo / STATE_PATH)
    print(f"finalized successor ownership state from AK evidence:{record['id']}; commit state only")
    return 0


def find_final_commit(repo: Path, applied: str, state_raw: bytes) -> str:
    matches = []
    for commit in git_output(repo, "log", "--format=%H", "--", STATE_PATH.as_posix()).splitlines():
        parents = git_output(repo, "rev-list", "--parents", "-n", "1", commit).split()
        changed = git_output(repo, "diff-tree", "--no-commit-id", "--name-only", "-r", commit).splitlines()
        if len(parents) == 2 and parents[1] == applied and changed == [STATE_PATH.as_posix()]:
            if git_bytes(repo, "show", f"{commit}:{STATE_PATH}") == state_raw:
                matches.append(commit)
    if len(matches) != 1:
        raise ValueError("ownership transition requires one state-only final commit directly after applied commit")
    return matches[0]


def verify_v2_transition(
    repo: Path, state: dict[str, Any], state_raw: bytes, map_raw: bytes, ak_command: Path | None = None,
) -> str:
    """Prove an established v2 state from its bytes, AK authority, evidence and history.

    Returns the state-only final commit that introduced ``state_raw``.
    """
    if set(state) != FINAL_KEYS or state.get("schema") != STATE_SCHEMA_V2 or state.get("kind") != STATE_KIND or state.get("state") != "established" or state.get("origin") != "ownership-transition" or type(state.get("evidence_id")) is not int or state["evidence_id"] < 1:
        raise ValueError("established successor state must use exact v2 schema")
    try:
        if json.loads(state_raw) != state:
            raise ValueError("established successor state does not match its bytes")
    except json.JSONDecodeError as exc:
        raise ValueError("established successor state bytes are invalid JSON") from exc
    if digest_bytes(map_raw) != state.get("ownership_map_sha256"):
        raise ValueError("established successor state does not bind active map")
    records = ak_json(authoritative_ak(ak_command), "evidence", "task", str(state["transition_task_id"]), "-F", "json")
    plans = [record["details"]["plan"] for record in records if (
        isinstance(record, dict) and record.get("id") == state["evidence_id"]
        and isinstance(record.get("details"), dict) and isinstance(record["details"].get("plan"), dict)
    )] if isinstance(records, list) else []
    if len(plans) != 1:
        raise ValueError("established successor state lacks its unique plan-bearing AK evidence")
    plan = validate_plan(plans[0]); bind_state = json.loads(pending_bytes(plan))
    if any(state.get(key) != value for key, value in bind_state.items() if key != "state"):
        raise ValueError("established successor state changed a pending plan binding")
    record = matching_evidence(repo, plan, ak_command)
    if record["id"] != state["evidence_id"] or record["details"]["applied_commit"] != state["applied_commit"]:
        raise ValueError("established successor state does not bind its exact AK evidence")
    task, _ = verify_authority(
        repo, plan["decision_id"], plan["transition_task_id"], plan["executor"], plan["adr_commit"],
        ak_command, completed_binding=(state["evidence_id"], state["plan_sha256"]),
    )
    if Path(task["repo"]).resolve() != Path(plan["target_repo"]).resolve():
        raise ValueError("durable transition plan target does not match canonical AK task repository")
    verify_applied(repo, plan, state["applied_commit"], pending_bytes(plan))
    company.verify_historical_maps(repo, plan, ak_command)
    final_commit = find_final_commit(repo, state["applied_commit"], state_raw)
    if git_run(repo, "merge-base", "--is-ancestor", final_commit, "HEAD").returncode != 0:
        raise ValueError("ownership transition final commit is outside current history")
    return final_commit


def validate_v2_provenance(repo: Path, state: dict[str, Any], ak_command: Path | None = None) -> None:
    verify_v2_transition(repo, state, (repo / STATE_PATH).read_bytes(), (repo / MAP_PATH).read_bytes(), ak_command)


def carry_forward_transition(repo: Path, state: dict[str, Any], ak_command: Path | None = None) -> dict[str, Any]:
    """Build the binding an ordinary refresh must carry when it replaces established v2 state."""
    state_raw = (repo / STATE_PATH).read_bytes()
    final_commit = verify_v2_transition(repo, state, state_raw, (repo / MAP_PATH).read_bytes(), ak_command)
    binding = {key: state[key] for key in INHERITED_KEYS - {"final_commit", "state_sha256"}}
    binding.update(final_commit=final_commit, state_sha256=digest_bytes(state_raw))
    validate_inherited_transition(repo, binding, ak_command)
    return binding


def validate_inherited_transition(repo: Path, binding: object, ak_command: Path | None = None) -> None:
    """Re-prove a carried-forward v2 transition from the historical state bytes it pins."""
    if not isinstance(binding, dict) or set(binding) != INHERITED_KEYS:
        raise ValueError("inherited transition binding must use the exact carried-forward schema")
    if not isinstance(binding.get("final_commit"), str) or not HEX40.fullmatch(binding["final_commit"]):
        raise ValueError("inherited transition final_commit must be full lowercase 40-hex")
    if not isinstance(binding.get("state_sha256"), str) or not HEX64.fullmatch(binding["state_sha256"]):
        raise ValueError("inherited transition state_sha256 must be lowercase sha256")
    final_commit = binding["final_commit"]
    state_raw = git_bytes(repo, "show", f"{final_commit}:{STATE_PATH}")
    if digest_bytes(state_raw) != binding["state_sha256"]:
        raise ValueError("inherited transition final commit does not hold the pinned v2 state bytes")
    try:
        state = json.loads(state_raw)
    except json.JSONDecodeError as exc:
        raise ValueError("inherited transition state bytes are invalid JSON") from exc
    if not isinstance(state, dict) or any(
        state.get(key) != binding[key] for key in INHERITED_KEYS - {"final_commit", "state_sha256"}
    ):
        raise ValueError("inherited transition binding disagrees with its pinned v2 state")
    map_raw = git_bytes(repo, "show", f"{final_commit}:{MAP_PATH}")
    if verify_v2_transition(repo, state, state_raw, map_raw, ak_command) != final_commit:
        raise ValueError("inherited transition final commit is not the unique v2 final commit")


def main() -> int:
    from l1_template_transition_cli import main as run_cli
    return run_cli()


if __name__ == "__main__":
    raise SystemExit(main())
