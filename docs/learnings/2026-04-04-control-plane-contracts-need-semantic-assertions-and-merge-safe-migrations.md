---
summary: "2026-04-04 — Control-plane contracts need semantic assertions and merge-safe migrations."
read_when:
  - "Read when you need 2026-04-04 — control-plane contracts need semantic assertions and merge-safe migrations."
type: "reference"
---

# 2026-04-04 — Control-plane contracts need semantic assertions and merge-safe migrations

## Context
A deep adversarial review of `core/tpl-template-repo` found a cluster of green-but-broken control-plane issues:

- fresh L1 renders emitted blank `l1_profile` / `l2_org_docs_default` values into `.copier-answers.yml`, `README.md`, and `contracts/provenance-seal.yml`
- `l2_org_docs_default` was treated as a real downstream policy knob, but descendant templates and checks only weakly enforced that claim
- `migrate-l1-structure.sh` preserved legacy answers by overwriting the freshly rendered staged answers file, which dropped new required provenance like `l0_source_sha`
- some conditional surfaces were being shipped as empty placeholder files instead of either real content or clean absence

## Evidence
Implemented and verified in this repo:
- L0 now exposes `l2_org_docs_default` explicitly in `copier.yml`
- L1 outputs derive a non-empty resolved profile label from the actual toggle bundle and persist it in answers/README/provenance
- generated L1 template CI now fails if profile/default values are blank or outside the governed set
- `tpl-project-repo` / `tpl-monorepo` now carry explicit compact vs rich `docs/org_context/` behavior instead of vague inheritance rhetoric
- `migrate-l1-structure.sh` now re-renders the staged repo with legacy profile flags first, then merges only approved legacy keys so newly required provenance survives
- adversarial checks now prove migration preserves `l0_source_sha` while also preserving legacy profile flags and release-pack surfaces
- `check-doc-references.sh` now fails clearly on missing `node`
- full verification passed with `bash ./scripts/check-l0.sh`

## Pattern
Template/control-plane regressions often hide in a three-step gap:

1. a field exists in docs or generated files
2. no source-of-truth question or derivation governs it tightly
3. CI checks presence but not meaning

The same gap appears in migrations when legacy preservation is implemented as file replacement instead of contract-aware merge.

## Guardrail
Use these rules for future template work:

- if a field appears in generated control-plane output, it must be either:
  - an explicit governed input in `copier.yml`, or
  - a deterministic derived value with CI assertions on the derived domain
- if a template advertises a downstream default/override, descendant renders must show a real surface difference and tests must prove it
- never preserve legacy `.copier-answers.yml` by wholesale overwrite; render staged output with preserved flags first, then merge only approved keys
- treat empty generated files as failures of the conditional contract unless the emptiness itself is explicitly meaningful and tested

## Propagation
- TIP candidate: yes — template/control-plane repos should adopt a standard adversarial checklist for blank metadata, dead knobs, merge-vs-overwrite migrations, and empty conditional outputs.
