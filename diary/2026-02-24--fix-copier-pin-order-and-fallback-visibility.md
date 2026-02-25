# 2026-02-24 — Copier pin order + fallback visibility hardening

## What I Did
- Ran deep review against template generation wrappers using the prompt-snippets stack (INVERSION/TELESCOPIC/AUDIT/NEXUS).
- Found a supply-chain shadow bug: wrappers claimed pinned Copier but selected bare `copier` before `uv tool run` whenever both existed.
- Reordered runtime selection in:
  - `scripts/new-l1-from-copier.sh`
  - `copier-template/scripts/new-repo-from-copier.sh`
  so pinned runtimes are always preferred (`uvx` -> `uv tool run` -> bare `copier`).
- Added explicit warning when falling back to unpinned `copier`.
- Strengthened `scripts/check-supply-chain.sh` with ordering + fallback-warning assertions so this regression fails fast.
- Extended generated L1 validation (`copier-template/scripts/check-template-ci.sh`) to enforce pinned Copier semantics and runtime precedence in downstream template repos.
- Added L0 guardrail assertions (`scripts/check-l0-guardrails.sh`) so the new L1 supply-chain checks cannot silently disappear.
- Updated `docs/supply-chain-policy.md` to document deterministic execution order and fallback visibility.
- Fixed `scripts/preview-l1-diff.sh` wrapper invocation contract (dest dir argument order) that caused immediate runtime failure.
- Added L0 guardrail assertion to keep `preview-l1-diff.sh` aligned with `new-l1-from-copier.sh` argument contract.
- Improved `scripts/preview-l1-diff.sh` default repo slug resolution: read `repo_slug` from target `.copier-answers.yml` before basename fallback.
- Added runtime coverage in `scripts/check-l0-generation.sh` (sample case) to execute `preview-l1-diff.sh` with a copied alias directory name so slug-inference regressions fail deterministic checks.

## What Surprised Me
- Existing checks validated presence of pinned commands but not execution precedence, so CI could pass while runtime behaved non-deterministically.

## Patterns
- String-presence guardrails are necessary but insufficient for supply-chain integrity; precedence and branch selection need explicit assertions.
- “Prefer pinned toolchain” must be encoded as executable policy, not only prose.

## Crystallization Candidates
- -> `docs/learnings/2026-02-24-copier-pin-order-enforcement.md`
- -> `tips/meta/` candidate: when checking wrappers, lint branch order (selection semantics), not only command literals.
