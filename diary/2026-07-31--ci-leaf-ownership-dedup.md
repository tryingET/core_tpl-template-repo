---
summary: "Remove nested L0 validation leaf execution and enforce aggregate single ownership."
read_when:
  - "Auditing why check-l0 no longer runs guardrails or session-checkpoint through nested leaf scripts."
type: "diary"
---

# CI leaf ownership deduplication

## Observation

`scripts/check-l0.sh` declared seven validation leaves, but two leaves also executed sibling leaves:

- `check-l0-generation.sh` executed `check-l0-guardrails.sh`
- `check-l0-guardrails.sh` executed `check-session-checkpoint.sh`

One aggregate run therefore executed guardrails twice and session-checkpoint twice. The repeated invocations used the same repository state and proof target, so they added runtime without a distinct proof dimension.

## Change

- `scripts/check-l0.sh` is the sole aggregate owner of the leaf manifest.
- Nested sibling invocations were removed.
- The aggregate validates that check names and script paths are unique and that no declared leaf directly invokes another declared leaf as an unqualified top-level command.
- Explicit negative/adversarial harnesses may invoke a sibling with altered inputs or environment because they prove a different failure mode.
- The sibling-call check is intentionally a bounded lexical defense against unqualified top-level calls, not a claim to parse every possible shell indirection.

## Evidence plan

Focused guardrails and session-checkpoint checks passed. Scratch dogfood executed all seven stub leaves exactly once, then injected an unqualified sibling call and confirmed rejection before any leaf executed. The real full aggregate passed all seven declared leaves once; its generation leaf also retained altered-environment negative calls to `check-doc-references.sh` as distinct failure-mode proofs.

## Authority boundary

This is template-internal defense-in-depth. It does not claim that the template caused duplicate pytest or UI-build execution in consumer repositories; consumer Justfiles remain repository-owned.
