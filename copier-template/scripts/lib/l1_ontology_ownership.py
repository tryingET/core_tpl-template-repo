"""Shared strict map parsing and structural proofs for ontology-only ownership transfers.

No AK authority is supplied here: L0 additionally verifies immutable owner receipts.
"""
from __future__ import annotations

import hashlib
import json
import stat
from pathlib import Path
from typing import Callable

MAP = "contracts/template-ownership.yml"
STATE = "contracts/template-ownership-state.json"
ONTOLOGY = "ontology/**"
PLACEHOLDER = "ontology/.gitkeep"
EMPTY_OID = "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391"
BINDING_KEYS = {
    "transition_task_id", "decision_id", "evidence_id", "plan_sha256", "executor",
    "applied_commit", "final_commit", "state_sha256",
}


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def matches(path: str, pattern: str) -> bool:
    return path == pattern[:-3] or path.startswith(pattern[:-3] + "/") if pattern.endswith("/**") else path == pattern


def pattern_kind(pattern: str) -> tuple[str, str]:
    if not pattern or pattern.startswith("/") or "\\" in pattern:
        raise ValueError(f"invalid ownership pattern: {pattern!r}")
    plain = pattern.removesuffix("/**")
    if any(part in {"", ".", "..", ".git"} for part in plain.split("/")) or "*" in plain:
        raise ValueError(f"unsupported or unsafe ownership pattern: {pattern}")
    return ("subtree", plain) if pattern.endswith("/**") else ("exact", plain)


def patterns_overlap(left: str, right: str) -> bool:
    lk, lv = pattern_kind(left)
    rk, rv = pattern_kind(right)
    return lv == rv or (lk == "subtree" and rv.startswith(lv + "/")) or (rk == "subtree" and lv.startswith(rv + "/"))


def map_sections(raw: bytes) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    active = None
    schema = None
    names = {"template_owned": "template", "agent_owned": "agent", "company_owned": "company"}
    for number, line in enumerate(raw.decode("utf-8").splitlines(), 1):
        if not line.strip() or line.strip().startswith("#"):
            continue
        if line.startswith("schema:") and schema is None and not sections:
            schema = line.split(":", 1)[1].strip()
        elif line.endswith(":") and line[:-1] in names:
            active = names[line[:-1]]
            if active in sections:
                raise ValueError("duplicate ownership section")
            sections[active] = []
        elif active and line.startswith("  - "):
            pattern = line[4:].strip()
            pattern_kind(pattern)
            sections[active].append(pattern)
        else:
            raise ValueError(f"unsupported ownership syntax at {MAP}:{number}")
    required = {"template", "agent"} if schema == "ai-society.template-ownership/1" else {"template", "agent", "company"}
    if schema not in {"ai-society.template-ownership/1", "ai-society.template-ownership/2"} or set(sections) != required:
        raise ValueError("ownership schema/sections mismatch")
    if not sections["template"] or not sections["agent"]:
        raise ValueError("ownership map requires non-empty template_owned and agent_owned lists")
    if sections.get("company", []) not in ([], [ONTOLOGY]):
        raise ValueError("company_owned currently supports only ontology/**")
    for kind, patterns in sections.items():
        if len(patterns) != len(set(patterns)):
            raise ValueError(f"duplicate ownership pattern in {kind}")
        for other, candidates in sections.items():
            if kind < other and any(patterns_overlap(a, b) for a in patterns for b in candidates):
                raise ValueError("ambiguous ownership patterns")
    return sections


def map_text(mapping: dict[str, list[str]]) -> str:
    lines = ["schema: ai-society.template-ownership/2"]
    for kind in ("template", "agent", "company"):
        lines.append(f"{kind}_owned:")
        lines.extend(f"  - {pattern}" for pattern in mapping.get(kind, []))
    raw = "\n".join(lines) + "\n"
    map_sections(raw.encode())
    return raw


def transfer_direction(old_raw: bytes, new_raw: bytes) -> str | None:
    old, new = map_sections(old_raw), map_sections(new_raw)
    before, after = old.get("company", []), new.get("company", [])
    if before == after:
        return None
    forward = before == [] and after == [ONTOLOGY]
    reverse = before == [ONTOLOGY] and after == []
    source, target = (old, new) if forward else (new, old)
    if not (forward or reverse) or ONTOLOGY not in source["template"] or (
        set(target["template"]) != set(source["template"]) - {ONTOLOGY}
        or set(target["agent"]) != set(source["agent"])
    ):
        raise ValueError("company ownership transfer must change only ontology/**")
    return "forward" if forward else "reverse"


def placeholder_tree(git: Callable[..., str], commit: str) -> None:
    entries = git("ls-tree", "-r", commit, "--", "ontology").splitlines()
    if entries != [f"100644 blob {EMPTY_OID}\t{PLACEHOLDER}"]:
        raise ValueError("ownership reverse requires the original empty regular ontology/.gitkeep only")


def placeholder_live(repo: Path, git: Callable[..., str]) -> None:
    placeholder_tree(git, "HEAD")
    if git("ls-files", "-s", "--", "ontology").splitlines() != [f"100644 {EMPTY_OID} 0\t{PLACEHOLDER}"]:
        raise ValueError("ownership reverse placeholder index drift")
    placeholder_files(repo)


def placeholder_files(repo: Path) -> None:
    root = repo / "ontology"
    if root.is_symlink() or not root.is_dir() or sorted(p.name for p in root.iterdir()) != [".gitkeep"]:
        raise ValueError("ownership reverse refuses residual ontology content (including ignored content)")
    seed = root / ".gitkeep"
    if not stat.S_ISREG(seed.lstat().st_mode) or stat.S_IMODE(seed.stat().st_mode) != 0o644 or seed.read_bytes() != b"":
        raise ValueError("ownership reverse placeholder bytes/type/mode drift")


def forward_source(git: Callable[..., str], state: dict[str, object], raw: bytes, anchor: str = "HEAD") -> dict[str, object]:
    """Pin and structurally reconstruct the actual forward source, including v3 lineage."""
    if state.get("state") != "established":
        raise ValueError("ownership reverse needs an established forward receipt")
    if state.get("schema") == "ai-society.template-ownership-state/3":
        if state.get("origin") != "contract-refresh":
            raise ValueError("ownership reverse inherited source must have contract-refresh origin")
        binding = state.get("inherited_transition")
        if not isinstance(binding, dict) or set(binding) != BINDING_KEYS:
            raise ValueError("ownership reverse lacks inherited forward binding")
        final = binding["final_commit"]
        raw = git("show", f"{final}:{STATE}").encode()
        source = json.loads(raw)
        if sha(raw) != binding["state_sha256"] or any(source.get(k) != binding[k] for k in BINDING_KEYS - {"final_commit", "state_sha256"}):
            raise ValueError("ownership reverse inherited forward binding drift")
    elif state.get("schema") == "ai-society.template-ownership-state/2":
        source = state
        applied = source["applied_commit"]
        finals = [commit for commit in git("log", "--format=%H", "--", STATE).splitlines()
                  if git("rev-list", "--parents", "-n", "1", commit).split() == [commit, applied]
                  and git("diff-tree", "--no-commit-id", "--name-only", "-r", commit).splitlines() == [STATE]
                  and git("show", f"{commit}:{STATE}").encode() == raw]
        if len(finals) != 1:
            raise ValueError("ownership reverse lacks unique forward final commit")
        final = finals[0]
        binding = {k: source[k] for k in BINDING_KEYS - {"final_commit", "state_sha256"}}
        binding.update(final_commit=final, state_sha256=sha(raw))
    else:
        raise ValueError("ownership reverse requires an actual receipted forward transition, not birth ownership")
    if source.get("schema") != "ai-society.template-ownership-state/2" or source.get("state") != "established" or source.get("origin") != "ownership-transition":
        raise ValueError("ownership reverse source is not an established transition")
    git("merge-base", "--is-ancestor", final, anchor)
    base, applied = source["predecessor_commit"], source["applied_commit"]
    old_map = git("show", f"{base}:{MAP}").encode()
    old_state = git("show", f"{base}:{STATE}").encode()
    new_map = git("show", f"{final}:{MAP}").encode()
    if sha(old_map) != source["predecessor_map_sha256"] or sha(old_state) != source["predecessor_state_sha256"] or sha(new_map) != source["ownership_map_sha256"]:
        raise ValueError("ownership reverse source predecessor hashes drift")
    if transfer_direction(old_map, new_map) != "forward":
        raise ValueError("ownership reverse source is not an ontology-only forward transfer")
    if git("rev-list", "--parents", "-n", "1", applied).split() != [applied, base] or git("rev-list", "--parents", "-n", "1", final).split() != [final, applied]:
        raise ValueError("ownership reverse source history drift")
    if git("diff-tree", "--no-commit-id", "--name-only", "-r", applied).splitlines() != sorted([MAP, STATE]) or git("diff-tree", "--no-commit-id", "--name-only", "-r", final).splitlines() != [STATE]:
        raise ValueError("ownership reverse source was not map-only with a state-only final commit")
    placeholder_tree(git, base)
    placeholder_tree(git, applied)
    placeholder_tree(git, final)
    return binding


def structural_transfer(git: Callable[..., str], old_raw: bytes, new_raw: bytes, base: str, applied: str) -> None:
    from l1_ontology_convergence import retention_direction, structural_convergence
    if retention_direction(old_raw, new_raw):
        structural_convergence(git, old_raw, new_raw, base, applied)
        from l1_transition_history import structural_predecessor
        structural_predecessor(git, base)
        return
    direction = transfer_direction(old_raw, new_raw)
    if direction is None:
        return
    if git("diff-tree", "--no-commit-id", "--name-only", "-r", applied).splitlines() != sorted([MAP, STATE]):
        raise ValueError("company ownership transition must be map-only")
    if direction == "reverse":
        state_raw = git("show", f"{base}:{STATE}").encode()
        forward_source(git, json.loads(state_raw), state_raw, base)
        placeholder_tree(git, base)
        placeholder_tree(git, applied)


def bind_birth_map() -> None:
    """Copier task: bind the generated layout's map, before any Git history exists."""
    root = Path.cwd()
    raw = (root / MAP).read_bytes()
    map_sections(raw)
    path = root / STATE
    state = json.loads(path.read_bytes())
    if state.get("origin") != "copier-birth" or state.get("state") != "established":
        raise ValueError("birth map binding refuses non-birth ownership state")
    state["ownership_map_sha256"] = sha(raw)
    path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    import sys
    if sys.argv[1:] == ["--bind-birth-map"]:
        bind_birth_map()
    elif sys.argv[1:] == ["--template-placeholder-required"]:
        raise SystemExit(1 if map_sections(Path(MAP).read_bytes()).get("company") else 0)
    else:
        raise SystemExit("usage: l1_ontology_ownership.py --bind-birth-map|--template-placeholder-required")
