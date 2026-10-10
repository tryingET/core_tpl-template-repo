"""Narrow agent-gitlink to company-tree structural contract (no AK authority)."""
from __future__ import annotations

import base64
import hashlib
import json
import re
import os
import subprocess
from pathlib import Path
from typing import Callable

from l1_ontology_ownership import MAP, STATE, ONTOLOGY, map_sections

PLAN_SCHEMA = "ai-society.template-ownership-transition-plan/3"
KIND = "agent-gitlink-to-company-tree"
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")
KEYS = {"kind", "predecessor_layout", "successor_layout", "ontology_gitlink_oid",
        "retained_files", "source_commit_base64", "source_tree_oid",
        "source_tree_manifest_sha256", "source_owner_evidence"}
EVIDENCE_KEYS = {"task_id", "evidence_ref", "details_sha256"}
ANSWERS = ".copier-answers.yml"


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode()


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def object_oid(kind: str, raw: bytes) -> str:
    return hashlib.sha1(kind.encode() + b" " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def retention_direction(old_raw: bytes, new_raw: bytes) -> bool:
    old, new = map_sections(old_raw), map_sections(new_raw)
    if old.get("company", []) or new.get("company") != [ONTOLOGY]:
        return False
    return (set(old["agent"]) >= {"ontology", ".gitmodules"}
            and set(new["agent"]) == set(old["agent"]) - {"ontology", ".gitmodules"}
            and set(old["template"]) == set(new["template"]))


def retained_tree(files: object) -> str:
    """Reconstruct the complete Git tree, including directory names and executable modes."""
    if not isinstance(files, list) or not files:
        raise ValueError("retained_files must be a nonempty canonical complete tree manifest")
    paths = []
    root: dict = {}
    for entry in files:
        if not isinstance(entry, dict) or set(entry) != {"path", "mode", "oid", "content_sha256"}:
            raise ValueError("retained file has wrong keys")
        path = entry["path"]
        if (not isinstance(path, str) or not path.startswith("ontology/") or "\\" in path
                or any(p in {"", ".", "..", ".git"} for p in path.split("/"))
                or any(ord(c) < 32 or ord(c) == 127 for c in path)):
            raise ValueError("unsafe retained file path")
        if entry["mode"] not in {"100644", "100755"} or not isinstance(entry["oid"], str) or not HEX40.fullmatch(entry["oid"]):
            raise ValueError("retained file mode/OID mismatch")
        if not isinstance(entry["content_sha256"], str) or not HEX64.fullmatch(entry["content_sha256"]):
            raise ValueError("retained file hash mismatch")
        paths.append(path)
        node = root
        parts = path.split("/")[1:]
        for part in parts[:-1]:
            node = node.setdefault(part, {})
            if not isinstance(node, dict):
                raise ValueError("retained ancestor ambiguity")
        if parts[-1] in node:
            raise ValueError("duplicate or ancestor-ambiguous retained path")
        node[parts[-1]] = (entry["mode"], entry["oid"])
    if paths != sorted(set(paths)):
        raise ValueError("retained_files must be path-sorted and unique")
    def tree(node: dict) -> str:
        raw = b""
        for name, child in sorted(node.items(), key=lambda pair: pair[0].encode() + (b"/" if isinstance(pair[1], dict) else b"")):
            mode, oid = ("40000", tree(child)) if isinstance(child, dict) else child
            raw += mode.encode() + b" " + name.encode() + b"\0" + bytes.fromhex(oid)
        return object_oid("tree", raw)
    return tree(root)


def validate_model(plan: dict) -> None:
    obj = plan["ontology_convergence"]
    if not isinstance(obj, dict) or set(obj) != KEYS or (obj["kind"], obj["predecessor_layout"], obj["successor_layout"]) != (KIND, "gitlink", "tree"):
        raise ValueError("ontology_convergence has wrong schema or layouts")
    tree = retained_tree(obj["retained_files"])
    try:
        commit = base64.b64decode(obj["source_commit_base64"], validate=True)
    except (ValueError, TypeError) as exc:
        raise ValueError("invalid retained source commit bytes") from exc
    if (object_oid("commit", commit) != obj["ontology_gitlink_oid"]
            or commit.split(b"\n", 1)[0] != b"tree " + tree.encode()
            or tree != obj["source_tree_oid"]
            or sha(canonical(obj["retained_files"])) != obj["source_tree_manifest_sha256"]):
        raise ValueError("complete retained tree does not bind source gitlink commit/manifest")
    evidence = obj["source_owner_evidence"]
    if (not isinstance(evidence, dict) or set(evidence) != EVIDENCE_KEYS
            or type(evidence["task_id"]) is not int or evidence["task_id"] != 5651
            or evidence["evidence_ref"] != "evidence:14868"
            or not isinstance(evidence["details_sha256"], str) or not HEX64.fullmatch(evidence["details_sha256"])):
        raise ValueError("retained source requires the accepted source-owner evidence binding")
    additions = [{"path": e["path"], "mode": e["new_mode"], "oid": e["new_oid"], "content_sha256": e["content_sha256"]}
                 for e in plan["git_delta"] if e["path"].startswith("ontology/") and e["old_mode"] == "000000"]
    if additions != obj["retained_files"]:
        raise ValueError("retained inventory differs from ontology additions")


def answers_successor(raw: bytes) -> bytes:
    # Exact byte substitution only: no YAML rewriting, implicit layout, duplicate key or pin change.
    lines = raw.splitlines(keepends=True)
    candidates = [i for i, line in enumerate(lines) if re.match(rb"\s*l1_ontology_layout\s*:", line)]
    if raw.count(b"l1_ontology_layout") != 1 or len(candidates) != 1 or lines[candidates[0]].rstrip(b"\r\n") != b"l1_ontology_layout: gitlink":
        raise ValueError("old answers must explicitly and uniquely bind gitlink layout")
    i = candidates[0]
    lines[i] = lines[i].replace(b": gitlink", b": tree", 1)
    return b"".join(lines)


def base_layout(git: Callable[..., str], base: str) -> str:
    if git("ls-tree", base, "--", "ontology").split()[:2] != ["160000", "commit"]:
        raise ValueError("convergence predecessor must be an ontology gitlink")
    oid = git("ls-tree", base, "--", "ontology").split()[2]
    entries = git("config", "--blob", f"{base}:.gitmodules", "--list").splitlines()
    # Ancillary settings and additional modules require another contract.
    if len(entries) != 2 or sorted(e.split("=", 1)[0] for e in entries) != ["submodule.ontology.path", "submodule.ontology.url"] or "submodule.ontology.path=ontology" not in entries:
        raise ValueError("convergence requires the sole exact ontology submodule declaration")
    if git("ls-tree", base, "--", ".gitmodules").split()[0] != "100644":
        raise ValueError("gitmodules must be regular 100644")
    return oid


TRAILER = "L1-Ownership-Transition-Plan: "
PLAN_KEYS = {"schema", "target_repo", "decision_id", "adr_commit", "transition_task_id", "executor",
             "base_commit", "predecessor_state_sha256", "predecessor_map_sha256", "next_map_sha256",
             "next_map_text", "map_delta", "git_delta", "validation", "rollback", "canonical_plan_sha256", "ontology_convergence"}


def plan_message(plan: dict) -> bytes:
    return ("Pending retained ontology ownership convergence\n\n" + TRAILER
            + base64.b64encode(canonical(plan)).decode("ascii") + "\n").encode()


def trailer_plan(git: Callable[..., str], applied: str) -> dict:
    message = git("show", "-s", "--format=%B", applied).rstrip("\n")
    lines = message.splitlines()
    if message.count(TRAILER.rstrip()) != 1 or not lines or not lines[-1].startswith(TRAILER) or len(lines) < 2 or lines[-2] != "":
        raise ValueError("convergence requires exactly one final canonical plan trailer")
    encoded = lines[-1][len(TRAILER):]
    try:
        raw = base64.b64decode(encoded, validate=True)
        plan = json.loads(raw)
        if not isinstance(plan, dict) or set(plan) != PLAN_KEYS or plan["schema"] != PLAN_SCHEMA or raw != canonical(plan) or encoded != base64.b64encode(raw).decode("ascii"):
            raise ValueError("noncanonical convergence plan trailer")
        body = dict(plan); body.pop("canonical_plan_sha256")
        if sha(canonical(body)) != plan["canonical_plan_sha256"]:
            raise ValueError("convergence trailer canonical plan hash mismatch")
        for key in ("base_commit", "adr_commit"):
            if not isinstance(plan[key], str) or not HEX40.fullmatch(plan[key]):
                raise ValueError("invalid convergence trailer commit binding")
        for key in ("predecessor_state_sha256", "predecessor_map_sha256", "next_map_sha256"):
            if not isinstance(plan[key], str) or not HEX64.fullmatch(plan[key]):
                raise ValueError("invalid convergence trailer digest binding")
        if (any(type(plan[k]) is not int or plan[k] < 1 for k in ("decision_id", "transition_task_id"))
                or not isinstance(plan["executor"], str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:/-]{2,127}", plan["executor"])
                or not isinstance(plan["target_repo"], str) or not Path(plan["target_repo"]).is_absolute() or str(Path(plan["target_repo"]).resolve()) != plan["target_repo"]
                or not isinstance(plan["rollback"], str) or not plan["rollback"].strip()
                or plan["validation"] != [{"id": "check-template-ci", "command": "bash scripts/check-template-ci.sh"}, {"id": "ci-full", "command": "bash scripts/ci/full.sh"}]):
            raise ValueError("invalid convergence trailer authority/validation fields")
        validate_model(plan)
        return plan
    except (ValueError, TypeError, KeyError, AttributeError) as exc:
        raise ValueError(f"invalid convergence plan trailer: {exc}") from exc


def binary_git(git: Callable[..., str], *args: str) -> bytes:
    environment = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    environment.update(GIT_NO_REPLACE_OBJECTS="1", GIT_GRAFT_FILE=os.devnull)
    result = subprocess.run(["git", "--no-replace-objects", "-C", git("rev-parse", "--show-toplevel").strip(), *args], capture_output=True, env=environment)
    if result.returncode:
        raise ValueError("binary convergence Git proof failed")
    return result.stdout


def expected_delta(git: Callable[..., str], base: str, files: list) -> list:
    delta = []
    for path in (".gitmodules", "ontology"):
        mode, _, oid = git("ls-tree", base, "--", path).split("\t", 1)[0].split()
        delta.append(dict(path=path, old_mode=mode, old_oid=oid, new_mode="000000", new_oid=None, content_sha256=None))
    for entry in files:
        delta.append(dict(path=entry["path"], old_mode="000000", old_oid=None, new_mode=entry["mode"], new_oid=entry["oid"], content_sha256=entry["content_sha256"]))
    mode, _, oid = git("ls-tree", base, "--", ANSWERS).split("\t", 1)[0].split()
    if mode != "100644":
        raise ValueError("predecessor answers must have mode 100644")
    successor = answers_successor(binary_git(git, "show", f"{base}:{ANSWERS}"))
    delta.append(dict(path=ANSWERS, old_mode=mode, old_oid=oid, new_mode=mode, new_oid=object_oid("blob", successor), content_sha256=sha(successor)))
    return sorted(delta, key=lambda entry: entry["path"])


def structural_convergence(git: Callable[..., str], old_raw: bytes, new_raw: bytes, base: str, applied: str) -> None:
    plan = trailer_plan(git, applied)
    obj = plan["ontology_convergence"]
    if not retention_direction(old_raw, new_raw) or base_layout(git, base) != obj["ontology_gitlink_oid"]:
        raise ValueError("convergence must bind exact ownership transfer and source gitlink")
    if git("rev-list", "--parents", "-n", "1", applied).split() != [applied, base] or plan["base_commit"] != base:
        raise ValueError("convergence trailer base/ancestry mismatch")
    old_state_raw = binary_git(git, "show", f"{base}:{STATE}")
    old_state = json.loads(old_state_raw)
    if old_state.get("schema") not in {"ai-society.template-ownership-state/2", "ai-society.template-ownership-state/3"} or old_state.get("state") != "established":
        raise ValueError("convergence requires an established receipted predecessor")
    if (sha(old_raw) != plan["predecessor_map_sha256"] or sha(old_state_raw) != plan["predecessor_state_sha256"]
            or new_raw != plan["next_map_text"].encode() or sha(new_raw) != plan["next_map_sha256"]
            or binary_git(git, "show", f"{applied}:{MAP}") != new_raw):
        raise ValueError("convergence trailer predecessor/successor bytes drift")
    old, new = map_sections(old_raw), map_sections(new_raw)
    semantic = {f"{kind}_{action}": sorted(set(right.get(kind, [])) - set(left.get(kind, [])))
                for kind in ("template", "agent", "company") for action, left, right in (("added", old, new), ("removed", new, old))}
    if semantic != plan["map_delta"] or expected_delta(git, base, obj["retained_files"]) != plan["git_delta"]:
        raise ValueError("convergence trailer map/payload derivation drift")
    bindings = {"schema": "ai-society.template-ownership-state/2", "kind": "l1_ownership_transition_state", "state": "ownership_transition_pending_receipt",
                "predecessor_commit": base, "ownership_map_sha256": plan["next_map_sha256"], "plan_sha256": plan["canonical_plan_sha256"]}
    bindings.update({k: plan[k] for k in ("decision_id", "transition_task_id", "executor", "adr_commit", "predecessor_state_sha256", "predecessor_map_sha256")})
    pending = (json.dumps(bindings, indent=2, sort_keys=True) + "\n").encode()
    if binary_git(git, "show", f"{applied}:{STATE}") != pending:
        raise ValueError("convergence trailer does not bind exact pending state/plan hash")
    raw = binary_git(git, "diff", "--raw", "--no-renames", "-z", "--full-index", "--abbrev=40", base, applied).split(b"\0")
    actual, controls = [], []
    for i in range(0, len(raw) - 1, 2):
        old_mode, new_mode, old_oid, new_oid, _ = raw[i].decode("ascii").split()
        old_mode = old_mode[1:]; path = raw[i + 1].decode("utf-8")
        entry = dict(path=path, old_mode=old_mode, new_mode=new_mode, old_oid=None if old_mode == "000000" else old_oid,
                     new_oid=None if new_mode == "000000" else new_oid, content_sha256=sha(binary_git(git, "cat-file", "blob", new_oid)) if new_mode in {"100644", "100755", "120000"} else None)
        (controls if path in {MAP, STATE} else actual).append(entry)
    if ({e["path"] for e in controls} != {MAP, STATE} or any(e["old_mode"] != "100644" or e["new_mode"] != "100644" for e in controls)
            or sorted(actual, key=lambda e: e["path"]) != plan["git_delta"]):
        raise ValueError("convergence applied delta differs from complete retained source plan")
