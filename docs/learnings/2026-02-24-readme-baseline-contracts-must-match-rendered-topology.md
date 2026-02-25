# 2026-02-24 — README baseline contracts must match rendered topology

## Context
Deep review surfaced wording drift: documentation implied uniform baseline scaffolding across L1/L2 outputs, while actual L2 outputs vary by archetype/profile.

## Evidence
- Top-level `README.md` previously stated a single `L1/L2` baseline of folders + git assets.
- `copier-template/README.md.jinja` similarly implied generated repos share the same folder/git baseline.
- Rendered fixtures show L2 outputs are archetype-specific and profile-gated (e.g., GitHub assets controlled by community/release/vouch toggles).

## Pattern
Docs can overstate guarantees when they collapse multiple output contracts into one statement.

In template systems, contract language must mirror the actual render axes (layer + archetype + profile toggles).

## Guardrail
- Reworded baseline sections to explicitly distinguish:
  - L1 baseline guarantees,
  - L2 archetype/profile-specific outputs.
- Added assertions in `scripts/check-l0-guardrails.sh` requiring README language that preserves this distinction.

## Propagation
- Propagated: `tips/meta/tip-0007-readme-baseline-claims-must-map-to-render-axes.md`.
