"""Plan/3 complete retained-source preflight and immutable historical proof."""
from __future__ import annotations

import base64
from pathlib import Path

from l1_ontology_convergence import (
    PLAN_SCHEMA, KIND, EVIDENCE_KEYS, ANSWERS, MAP, STATE, canonical, sha,
    retained_tree, retention_direction, base_layout, validate_model,
)

SOURCE = "https://github.com/tryingET/softwareco-ontology.git main"
PACKET = {
    "source": SOURCE,
    "oid": "bound at the move preflight (main was 6f6ae61bc70d8cf4dbd0f0c2b9b44609b736b74e on 2026-10-10)",
    "retained": "every tracked path, bytes and modes unchanged",
    "excluded": "none tracked; untracked and ignored state is not moved but preserved by a fresh full-ref bundle and the archived remote",
}


def verify_source_owner(binding: dict, ak: Path | None) -> None:
    import l1_template_transitions as transition
    records = transition.ak_json(transition.authoritative_ak(ak), "evidence", "task", str(binding["task_id"]), "-F", "json")
    records = [r for r in records if isinstance(r, dict) and r.get("id") == 14868] if isinstance(records, list) else []
    if len(records) != 1:
        raise ValueError("retained packet lacks unique accepted source-owner evidence")
    record = records[0]
    details = record.get("details")
    if (record.get("task_id") != 5651 or record.get("check_type") != "source_owner_packet"
            or record.get("result") != "pass" or not isinstance(details, dict)
            or details.get("owner") != "Holding Owner" or details.get("retained_source_packet") != PACKET
            or sha(canonical(details)) != binding["details_sha256"]):
        raise ValueError("accepted retained source-owner packet details/digest drift")


def predecessor(repo: Path, plan: dict, ak: Path | None) -> None:
    import json
    import l1_template_transitions as transition
    from l1_template_receipts import validate_established_provenance
    base = plan["base_commit"]
    raw = transition.git_bytes(repo, "show", f"{base}:{STATE}")
    mapping = transition.git_bytes(repo, "show", f"{base}:{MAP}")
    state = json.loads(raw)
    if state.get("schema") == transition.STATE_SCHEMA_V2:
        transition.verify_v2_transition(repo, state, raw, mapping, ak)
    elif state.get("schema") == "ai-society.template-ownership-state/3":
        validate_established_provenance(repo, state, ak_command=ak, proof_commit=base)
        strict_wave(repo, state, ak)
    else:
        raise ValueError("convergence requires established /2 or proven /3 predecessor")


def expected_delta(repo: Path, base: str, files: list) -> list:
    from l1_template_receipts import git_output
    from l1_ontology_convergence import expected_delta as derive
    return derive(lambda *args: git_output(repo, *args), base, files)


def configure(repo: Path, plan: dict, spec: object, ak: Path | None) -> None:
    import l1_template_transitions as transition
    from l1_template_receipts import git_output, ensure_clean_git_target, git_top
    if not isinstance(spec, dict) or set(spec) != {"source_repo", "source_owner_evidence", "source_tree_manifest_sha256"}:
        raise ValueError("convergence preflight spec has wrong keys")
    binding = spec["source_owner_evidence"]
    if not isinstance(binding, dict) or set(binding) != EVIDENCE_KEYS or binding["task_id"] != 5651 or binding["evidence_ref"] != "evidence:14868":
        raise ValueError("convergence requires accepted evidence:14868/task5651")
    verify_source_owner(binding, ak)
    source = Path(spec["source_repo"])
    if not source.is_absolute() or source != source.resolve() or source.is_symlink() or git_top(source) != source.resolve():
        raise ValueError("source_repo must be an absolute Git worktree root")
    reject_index_flags(source)
    ensure_clean_git_target(source)
    if git_output(source, "ls-files", "--others", "--ignored", "--exclude-standard"):
        raise ValueError("source preflight refuses ignored content; preserve/dispose it with source owner first")
    base = plan["base_commit"]
    git = lambda *args: git_output(repo, *args)
    oid = base_layout(git, base)
    if git_output(source, "rev-parse", "HEAD").strip() != oid:
        raise ValueError("preflight source HEAD differs from committed ontology gitlink OID")
    if git("config", "--blob", f"{base}:.gitmodules", "--get", "submodule.ontology.url").strip() != SOURCE.removesuffix(" main"):
        raise ValueError("gitlink source URL differs from accepted retained source packet")
    files = []
    for record in transition.git_bytes(source, "ls-tree", "-rz", "--full-tree", oid).split(b"\0"):
        if not record:
            continue
        fields, path = record.split(b"\t", 1)
        mode, kind, blob = fields.decode("ascii").split()
        if kind != "blob" or mode not in {"100644", "100755"}:
            raise ValueError("source retained tree refuses symlinks or nested gitlinks")
        files.append(dict(path="ontology/" + path.decode("utf-8"), mode=mode, oid=blob,
                          content_sha256=sha(transition.git_bytes(source, "cat-file", "blob", blob))))
    files.sort(key=lambda entry: entry["path"])
    tree = retained_tree(files)
    verify_source_worktree(source, files)
    digest = sha(canonical(files))
    if digest != spec["source_tree_manifest_sha256"]:
        raise ValueError("explicit preflight source tree manifest digest mismatch")
    plan["schema"] = PLAN_SCHEMA
    plan["ontology_convergence"] = dict(kind=KIND, predecessor_layout="gitlink", successor_layout="tree",
        ontology_gitlink_oid=oid, retained_files=files, source_tree_oid=tree,
        source_commit_base64=base64.b64encode(transition.git_bytes(source, "cat-file", "commit", oid)).decode("ascii"),
        source_tree_manifest_sha256=digest, source_owner_evidence=binding)
    verify(repo, plan, ak, live=True)


def verify(repo: Path, plan: dict, ak: Path | None, live: bool = False) -> None:
    import l1_template_transitions as transition
    from l1_template_receipts import git_output
    validate_model(plan)
    if live:
        verify_live_lease(plan, ak)
    base = plan["base_commit"]
    old = transition.git_bytes(repo, "show", f"{base}:{MAP}")
    if not retention_direction(old, plan["next_map_text"].encode()):
        raise ValueError("convergence must preserve unrelated ownership claims exactly")
    git = lambda *args: git_output(repo, *args)
    obj = plan["ontology_convergence"]
    if base_layout(git, base) != obj["ontology_gitlink_oid"]:
        raise ValueError("retained source differs from predecessor gitlink")
    if git("config", "--blob", f"{base}:.gitmodules", "--get", "submodule.ontology.url").strip() != SOURCE.removesuffix(" main"):
        raise ValueError("historical gitlink source differs from accepted retained source packet")
    if expected_delta(repo, base, obj["retained_files"]) != plan["git_delta"]:
        raise ValueError("convergence delta must be exact retained tree, gitlink/modules deletion and answers update")
    verify_source_owner(obj["source_owner_evidence"], ak)
    predecessor(repo, plan, ak)


def current_instant() -> tuple:
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    return now.replace(microsecond=0), now.microsecond * 1000


def verify_live_lease(plan: dict, ak: Path | None) -> None:
    import l1_template_transitions as transition
    task = transition.ak_json(transition.authoritative_ak(ak), "task", "show", str(plan["transition_task_id"]), "-F", "json")
    if (not isinstance(task, dict) or task.get("status") != "claimed"
            or task.get("claimed_by") != plan["executor"]
            or transition.ak_instant(task.get("lease_expires_at"), "transition lease expiry") <= current_instant()):
        raise ValueError("convergence requires an unexpired live task lease")


def strict_wave(repo: Path, state: dict, ak: Path | None) -> None:
    """Narrow convergence proof: never accept the legacy receipt verifier's bool/first match."""
    import l1_template_transitions as transition
    launcher = transition.authoritative_ak(ak)
    task_id = state["wave_task_id"]
    task = transition.ak_json(launcher, "task", "show", str(task_id), "-F", "json")
    records = transition.ak_json(launcher, "evidence", "task", str(task_id), "-F", "json")
    if type(task_id) is not int or task_id < 1 or not isinstance(task, dict) or type(task.get("id")) is not int or task.get("id") != task_id or task.get("status") not in {"claimed", "done"} or not isinstance(records, list):
        raise ValueError("strict predecessor wave task/evidence is malformed")
    target = str(Path(task.get("repo", "")).resolve())
    matches = []
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get("details"), dict):
            continue
        details = record["details"]
        if (record.get("task_id") == task_id and record.get("check_type") == "l1_contract_refresh_v1"
                and record.get("result") == "pass" and record.get("repo") == target and record.get("repo_scope") == target
                and details.get("target_repo") == target and details.get("executor") == "template-propagator"
                and all(details.get(k) == state.get(k) for k in ("applied_commit", "plan_sha256", "ownership_map_sha256", "source_l0_commit", "wave_id"))):
            matches.append(record)
    if (len(matches) != 1 or type(state.get("evidence_id")) is not int or state["evidence_id"] < 1
            or type(matches[0].get("id")) is not int or type(matches[0].get("task_id")) is not int
            or matches[0].get("id") != state["evidence_id"]
            or sum(r.get("id") == state["evidence_id"] for r in records if isinstance(r, dict)) != 1):
        raise ValueError("strict predecessor wave requires one unique pinned matching evidence record")
    record = matches[0]; validation = record["details"].get("validation")
    if (not isinstance(validation, dict) or not validation
            or any(type(code) is not int or code != 0 for code in validation.values())
            or any(sum(isinstance(key, str) and key.endswith(gate) for key in validation) != 1 for gate in ("check-template-ci.sh", "ci/full.sh"))):
        raise ValueError("strict predecessor wave requires actual integer-zero validation results")
    checked = transition.ak_instant(record.get("checked_at"), "wave evidence checked_at")
    if task["status"] == "done" and checked > transition.ak_instant(task.get("completed_at"), "wave task completed_at"):
        raise ValueError("wave evidence was recorded after the wave task completed")


def reject_index_flags(source: Path) -> None:
    import l1_template_transitions as transition
    entries = transition.git_bytes(source, "ls-files", "-v", "-z").split(b"\0")
    if any(entry and (entry[:1].islower() or entry[:1] == b"S") for entry in entries):
        raise ValueError("source preflight refuses assume-unchanged/skip-worktree index flags")


def verify_source_worktree(source: Path, files: list) -> None:
    import stat
    from l1_template_receipts import ensure_safe_destinations
    paths = [entry["path"].removeprefix("ontology/") for entry in files]
    ensure_safe_destinations(source, paths)
    for entry, rel in zip(files, paths):
        path = source / rel
        try:
            mode = path.lstat().st_mode
            if not stat.S_ISREG(mode) or stat.S_IMODE(mode) & 0o111 != (0o111 if entry["mode"] == "100755" else 0) or sha(path.read_bytes()) != entry["content_sha256"]:
                raise ValueError("source tracked worktree type/content/executable mode differs from retained manifest")
        except OSError as exc:
            raise ValueError("source tracked worktree file is unavailable") from exc


def proven_convergence(repo: Path, state: dict, ak: Path | None = None) -> None:
    """Authorize only ownership-preserving render preparation from a proven /3 convergence."""
    import l1_template_transitions as transition
    from l1_template_receipts import validate_established_provenance, git_output
    from l1_ontology_convergence import trailer_plan
    validate_established_provenance(repo, state, ak_command=ak)
    if state.get("schema") == transition.STATE_SCHEMA_V2:
        applied = state["applied_commit"]
    elif state.get("schema") == "ai-society.template-ownership-state/3":
        strict_wave(repo, state, ak)
        applied = state["inherited_transition"]["applied_commit"]
    else:
        raise ValueError("company-tree preparation requires proven convergence, not birth/map-only ownership")
    git = lambda *args: git_output(repo, *args)
    trailer_plan(git, applied)
    if git("ls-tree", "HEAD", "--", "ontology").split()[:2] != ["040000", "tree"]:
        raise ValueError("company-tree preparation requires committed ordinary ontology tree")
    answers = (repo / ANSWERS).read_text().splitlines()
    layout = [line for line in answers if "l1_ontology_layout" in line]
    if layout not in ([], ["l1_ontology_layout: tree"]):
        raise ValueError("company-tree preparation refuses answers/layout drift")


def commit_message(repo: Path, plan_path: Path, output: Path) -> int:
    import l1_template_transitions as transition
    from l1_template_company import external_output
    from l1_ontology_convergence import plan_message
    plan = transition.validate_plan(transition.load_object(plan_path, "transition plan"))
    if plan["schema"] != PLAN_SCHEMA:
        raise ValueError("canonical plan trailer is only required/supported for convergence /3")
    transition.verify_registered_target(repo, Path(plan["target_repo"]))
    external_output(repo, output)
    transition.write_atomic(plan_message(plan), output)
    print(f"wrote pending commit message to {output}; use git commit -F after staging exact controls")
    return 0


def verify_live(repo: Path, plan: dict) -> None:
    """Refuse residual ignored files, symlinks and byte/mode drift in staged retention."""
    import stat
    from l1_template_receipts import ensure_safe_destinations
    files = plan["ontology_convergence"]["retained_files"]
    paths = [entry["path"] for entry in files]
    ensure_safe_destinations(repo, paths)
    root = repo / "ontology"
    if root.is_symlink() or not root.is_dir():
        raise ValueError("retained ontology root must be an ordinary directory")
    actual = []
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ValueError("retained ontology refuses symlinked paths")
        if not path.is_dir():
            actual.append(path.relative_to(repo).as_posix())
    if sorted(actual) != paths:
        raise ValueError("retained ontology contains missing or residual untracked/ignored files")
    for entry in files:
        path = repo / entry["path"]
        mode = path.lstat().st_mode
        expected = 0o755 if entry["mode"] == "100755" else 0o644
        if not stat.S_ISREG(mode) or stat.S_IMODE(mode) != expected or sha(path.read_bytes()) != entry["content_sha256"]:
            raise ValueError("retained worktree bytes/type/mode drift")
