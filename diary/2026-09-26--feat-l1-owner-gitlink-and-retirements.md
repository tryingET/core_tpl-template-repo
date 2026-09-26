---
summary: "Owner-gitlink ontology refresh layout and the declarative L1 retirement manifest; softwareco preview result and remaining AK blocker."
read_when:
  - "Refreshing an L1 whose ontology is a company-owned submodule."
  - "Adding or reviewing entries in contracts/l1-template-retirements.json."
type: "reference"
---

# 2026-09-26 — feat: L1 owner-gitlink ontology and retirement manifest

## Why
- softwareco (HEAD 2766c2d) could not be refreshed: its receipted v2 map agent-owns
  exact `ontology` (a gitlink) while the L0 map template-owns `ontology/**`, and the
  engine never deleted template files L0 had dropped (vendored rocs-cli bundle,
  `copier/*/.githooks/pre-commit`).

## What changed
- `l1_ontology_layout: tree|gitlink` Copier answer. The gitlink layout renders no
  `ontology/` and rewrites the rendered map to the exact bytes the receipted
  transition installs (verified byte-identical to softwareco's map). The refresh
  wrapper derives the layout from the target index; a contradicting recorded
  answer refuses.
- `scripts/lib/l1_template_gitlinks.py`: gitlinks stay opaque; gitlink layout is
  admitted only when the provenance-validated active map already agent-owns
  `ontology` and `.gitmodules`, the gitlink is committed, and `.gitmodules`
  declares exactly one submodule at `ontology`.
- An established v2 state may now be replaced by an ordinary refresh receipt, but
  only if every company-owned pattern survives in the incoming map.
- `contracts/l1-template-retirements.json` + `scripts/lib/l1_template_retirements.py`:
  pattern + L0 commit + reason; plan prints `retire-rule:`/`retire:`; apply deletes
  only tracked, clean, template-owned regular files that L0 no longer renders.

## Softwareco (scratch clone only)
- `preview-l1-diff.sh` on a clone stops at `target must be a registered worktree of
  the canonical task repository` (clones can never satisfy it).
- With only that check relaxed in a diagnostic harness, v2 provenance refuses:
  `transition task executor does not match its fixed claimant` because AK task 5283
  is `done` with `claimed_by: null`. Needs an authority decision; not faked.
- Component analysis (read-only): gitlink `ontology` preserved, no agent/template
  overlap, 586 manifest retirements (581 rocs-cli, 2 pre-commit, 3 placeholders),
  5 fixed answer-template retirements, 23 add / 35 update.

## Validation
- Unit suites green; full `scripts/check-l0.sh` 7/7 from a clean branch clone.
