"""Structural historical predecessor proof; AK receipts remain the L0 verifier's job."""
from __future__ import annotations

import json
from typing import Callable

from l1_ontology_ownership import MAP, STATE, BINDING_KEYS, sha, structural_transfer


def structural_predecessor(git: Callable[..., str], anchor: str) -> None:
    raw = git("show", f"{anchor}:{STATE}").encode()
    state = json.loads(raw)
    mapping = git("show", f"{anchor}:{MAP}").encode()
    if state.get("state") != "established" or state.get("ownership_map_sha256") != sha(mapping):
        raise ValueError("convergence historical predecessor is not established/map-bound")
    schema = state.get("schema")
    if schema == "ai-society.template-ownership-state/3":
        binding = state.get("inherited_transition")
        if not isinstance(binding, dict) or set(binding) != BINDING_KEYS or state.get("origin") != "contract-refresh":
            raise ValueError("convergence predecessor /3 erased its inherited transition")
        final = binding["final_commit"]
        git("merge-base", "--is-ancestor", final, anchor)
        inherited_raw = git("show", f"{final}:{STATE}").encode()
        inherited = json.loads(inherited_raw)
        if sha(inherited_raw) != binding["state_sha256"] or any(inherited.get(k) != binding[k] for k in BINDING_KEYS - {"final_commit", "state_sha256"}):
            raise ValueError("convergence predecessor inherited binding drift")
        structural_predecessor(git, final)
        applied = state["applied_commit"]
        git("merge-base", "--is-ancestor", applied, anchor)
        pending = json.loads(git("show", f"{applied}:{STATE}"))
        if sha(git("show", f"{applied}:{MAP}").encode()) != state["ownership_map_sha256"]:
            raise ValueError("convergence predecessor /3 applied map drift")
        if pending.get("state") != "applied_pending_receipt" or any(pending.get(k) != state.get(k) for k in ("schema", "kind", "wave_id", "source_l0_commit", "plan_sha256", "ownership_map_sha256", "inherited_transition")):
            raise ValueError("convergence predecessor /3 wave/pending binding drift")
        return
    if schema != "ai-society.template-ownership-state/2" or state.get("origin") != "ownership-transition":
        raise ValueError("convergence predecessor requires receipted /2 or /3 history")
    base, applied = state["predecessor_commit"], state["applied_commit"]
    if git("rev-list", "--parents", "-n", "1", applied).split() != [applied, base]:
        raise ValueError("convergence predecessor topology ancestry drift")
    old_map = git("show", f"{base}:{MAP}").encode()
    old_state = git("show", f"{base}:{STATE}").encode()
    if sha(old_map) != state["predecessor_map_sha256"] or sha(old_state) != state["predecessor_state_sha256"]:
        raise ValueError("convergence predecessor historical bytes drift")
    if git("show", f"{applied}:{MAP}").encode() != mapping:
        raise ValueError("convergence predecessor /2 applied map drift")
    pending = json.loads(git("show", f"{applied}:{STATE}"))
    pending_keys = set(state) - {"origin", "evidence_id", "applied_commit"}
    if set(pending) != pending_keys or pending.get("state") != "ownership_transition_pending_receipt" or any(pending.get(k) != state.get(k) for k in pending_keys - {"state"}):
        raise ValueError("convergence predecessor pending binding drift")
    finals = [commit for commit in git("log", "--format=%H", anchor, "--", STATE).splitlines()
              if git("rev-list", "--parents", "-n", "1", commit).split() == [commit, applied]
              and git("diff-tree", "--no-commit-id", "--name-only", "-r", commit).splitlines() == [STATE]
              and git("show", f"{commit}:{STATE}").encode() == raw]
    if len(finals) != 1:
        raise ValueError("convergence predecessor lacks unique state-only final commit")
    structural_transfer(git, old_map, mapping, base, applied)
