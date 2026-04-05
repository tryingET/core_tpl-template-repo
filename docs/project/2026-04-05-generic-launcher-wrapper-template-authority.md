---
summary: "Bounded task-851 note codifying tpl-template-repo as the canonical distribution authority for generic launcher wrappers without transferring runtime ownership away from agent-kernel."
read_when:
  - "You are executing or reviewing AK task 851."
  - "You need the M45 authority split for scripts/ak.sh and scripts/cargo-operator.sh."
  - "You need to know whether a wrapper change belongs in agent-kernel, tpl-template-repo, or template-propagator."
type: "note"
---

# Generic launcher wrapper template authority

Task `851` codifies one narrow authority boundary for the generic launcher wrappers `scripts/ak.sh` and `scripts/cargo-operator.sh`.
It does **not** transfer runtime/reference ownership away from `softwareco/owned/agent-kernel`, and it does **not** claim that live downstream rollout proof already exists everywhere.

## Authority split

For the current M45 foundation packet:

- `softwareco/owned/agent-kernel` remains the **runtime/reference owner** of the launcher-bundle contract.
  - Canonical bundle membership, normalized fingerprints, and owner-side drift checks live there.
  - If wrapper behavior or bundle membership changes, the owner-side contract must change first.
- `core/tpl-template-repo` is the **canonical distribution authority** for the generic launcher wrappers.
  - This repo carries the template-side receipt `governance/dist/managed-launcher-bundle.template-receipt.json`.
  - This repo distributes the managed wrapper copies through `copier-template/` and fixture mirrors.
  - Governance docs in generated templates must preserve the owner/distribution/reporting split instead of implying local ownership.
- `holdingco/infra/template-propagator` remains the **rollout/proof reporting authority** for live downstream alignment.
  - If an operator needs proof that rollout reached downstream repos, that proof belongs there, not in this repo.

## Operator routing rule

Use the authority boundary like this:

1. **Change wrapper logic or the launcher-bundle contract** → start in `softwareco/owned/agent-kernel`.
2. **Distribute approved wrappers into templates/fixtures or codify generated-repo guidance** → do that in `core/tpl-template-repo`.
3. **Prove live downstream rollout or reporting alignment** → do that in `holdingco/infra/template-propagator`.

## Non-goals

This note is intentionally bounded.
It does **not** mean that:

- `core/tpl-template-repo` now owns the runtime/reference contract for the launcher bundle
- generated repos may silently fork `scripts/ak.sh` / `scripts/cargo-operator.sh` and still claim canonical ownership
- template-side receipts or generated adoption snapshots are sufficient proof of global downstream rollout

Generated repos remain consumer-only unless an explicit waiver says otherwise.
Copied wrappers are managed distribution artifacts, not authority transfer.

## Validation

The template-authority codification for task `851` should stay covered by:

```bash
bash ./scripts/check-l0-generation.sh
bash ./scripts/check-l0-fixtures.sh
node ~/ai-society/core/agent-scripts/scripts/docs-list.mjs --docs . --strict
```
