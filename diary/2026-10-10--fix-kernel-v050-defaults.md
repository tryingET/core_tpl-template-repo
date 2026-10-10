---
summary: "AK6936: isolated L0 default repin to immutable ontology-kernel v0.5.0; downstream waves remain separately governed."
read_when:
  - "Before continuing the ontology-kernel v0.5.0 consumer repin wave."
type: "reference"
task_id: 6936
---

# 2026-10-10 — ontology-kernel v0.5.0 defaults

## Authority and scope

Operator continuation of the AK6936 handoff; current AK6936 and standing owner decision AK6288 checked.
AK6659 records immutable release 409031456, tag v0.5.0 at
`60790d43ba0f4cfea946df9b07865b877432a7dd`. GitHub confirms immutability and a passing upstream `full` check.
This slice changes pins and their exact generated expectations only; no ontology definitions change.
The owner merges the L0 PR. Company refreshes must wait for that merge and retain their own admission checks.

## Work performed

- Isolated branch `feat/ak6936-kernel-v050` from L0 main `554ab5f` (its hosted check passed).
- Updated all three Copier kernel defaults, README defaults, native assertions and synthetic tag.
- Updated the one changed generation source-map block and reconstructed-source hash;
  the closed assertion graph and all other block hashes remain intact. Its 19 unit tests pass.
- Regenerated fixtures using the repo-owned synchronizer. L2 births bind committed L0 source,
  so synchronization must run again after the source pin commit; an uncommitted sync alone leaves L2 pins old.
- Validation and PR receipts are recorded in AK6936; this diary is not completion evidence.

## Downstream observations, not completion

Read-only readiness inspection found dirty/company-ownership blockers in the company L1 waves
AK6654–6657. Ordinary refresh must not silently transfer ontology ownership. Teachingco AK6652
has an older unpublished v0.4.0 candidate and requires an owner-declared branch/MR publication route.
The softwareco ontology integration and AK6663 work remain untouched.

## Crystallization candidate

Exact committed-source fixture regeneration matters for pin waves: a successful synchronization
before the source commit proves neither new L2 defaults nor full fixture convergence. Existing birth
and fixture checks are the deterministic verification surface; no new process is introduced here.
