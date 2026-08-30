---
summary: "AK 5187 implementation record for ownership-governed L0-to-L1 contract refresh."
read_when:
  - "Reviewing L1 ownership bootstrap, refresh, or external AK receipt finalization."
type: "diary"
---

# AK 5187 — L1 template ownership and governed refresh

## Scope

Extended `ai-society.template-ownership/1` from agent repositories to the generated L1 meta-template, grounded in AK 5186 evidence 7917. The five pre-existing operator-owned docs-list removal files remained untouched and excluded from staging.

## Ownership judgment

Company-authored L1 policy is agent-owned and preserved byte-for-byte: root `AGENTS.md`, `README.md`, `CONTRIBUTING.md`, `.gitignore`, `.github/workflows/ci.yml`, and `docs/org/**`. The README/contribution files carry company voice, while both observed `.gitignore` files carry genuine lane/local-runtime policy; classifying them template-owned would destroy valid local control-plane behavior. Every incoming rendered path outside those exceptions is explicitly template-owned.

## Safety flow

- `preview-l1-diff.sh` is structurally incapable of apply and delegates to one private renderer/planner.
- Brownfield bootstrap installs only the map, durable `adopting` state, and a target-specific census attestation bound to typed AK evidence, target Git lineage, map hash, and existing rendered template-path hashes/modes.
- Add/update refresh preserves agent-owned and target-only paths, rejects unknown/ambiguous maps, ownership widening, symlinks, containment escapes, census drift, and unrecorded collisions.
- Apply validates all receipt inputs before its first write and stops at the exact seven-field `applied_pending_receipt` state agreed with template-propagator AK 5189.
- Establishment is a separate phase. It resolves the authoritative `ak` launcher from the OS account database (not HOME/PATH/AK_CMD), verifies a per-target wave task and controller-defined `l1_contract_refresh_v1` pass evidence against target/applied/source commits, map/plan hashes, wave, executor, and both L1 gates, then establishes state and retires the adoption attestation.
- Target-only files are outside the add/update projection and are never deleted; nested child repositories remain diagnostic/excluded surfaces.

## Focused evidence before commit

- `python3 -m unittest tests/test_l1_template_ownership.py` — five tests passed.
- `bash ./scripts/check-l0-generation.sh` — passed, including ten ownership/agent behavior tests.
- `bash ./scripts/check-l0-adversarial.sh` — passed.
- `bash ./scripts/check-l0-guardrails.sh` — passed.
- Independent review iterated through bootstrap provenance, symlink disclosure, preview mutation, local receipt forgery, authority substitution, and pre-write validation findings; final review reported no blockers.
- Template-propagator AK 5189 landed byte-compatible receipt emission at commits `9053f18` and `78b92ff`; production execution remains gated on this task's clean commit and completion.

## Rollback

Revert the scoped AK 5187 commit. No softwareco or healthco L1 repository was mutated.
