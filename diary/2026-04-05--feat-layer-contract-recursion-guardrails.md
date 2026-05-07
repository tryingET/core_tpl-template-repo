---
summary: "Session note: 2026 04 05 Feat Layer Contract Recursion Guardrails."
read_when:
  - "Read when reconstructing repo-local session context for session note: 2026 04 05 feat layer contract recursion guardrails."
type: "reference"
---

# 2026-04-05 — Layer-contract recursion guardrails

## What I Did
- Claimed and completed repo-local AK task `#793`.
- Added machine-readable `contracts/layer-contract.yml` files to every L2 template surface (`tpl-agent-repo`, `tpl-org-repo`, `tpl-project-repo`, `tpl-monorepo`, `tpl-package`).
- Hardened `scripts/new-l1-from-copier.sh` so it verifies the current repo is really L0 and refuses to render into destinations that already declare a different layer.
- Hardened generated L1 `scripts/new-repo-from-copier.sh` with the same pattern for L1→L2 rendering.
- Updated generated `bootstrap-lane-root.sh` so lane baselines keep `contracts/` tracked instead of silently dropping the layer contract.
- Extended guardrail and generation tests to assert the new fail-closed behavior, then refreshed all L1/L2/matrix fixtures.

## What Surprised Me
- The generated L1 `new-repo-from-copier.sh` did not have a local `fail()` helper, so the first regression run surfaced that missing shell primitive immediately.
- Adding machine-readable contracts to L2 was not enough by itself; lane-root `.gitignore` policy also had to be widened or the new control-plane file would vanish from tracked baselines.

## Patterns
- If a boundary matters operationally, give it a machine-readable artifact and enforce it in the wrapper, not just in README/AGENTS prose.
- Compatibility-preserving guardrails are easiest when the wrapper fails closed for known mismatches but still tolerates older destinations that do not yet declare the new contract.

## Crystallization Candidates
- Potential future learning: brownfield migration path for older L1/L2 repos that still lack `contracts/layer-contract.yml`.
