# 2026-02-24 — Align README baseline claims with rendered L1/L2 reality

## What I Did
- Ran another deep-review pass for doc/implementation consistency.
- Found baseline claims that implied uniform L1+L2 folder/git scaffolds, while rendered L2 outputs are archetype/profile-specific.
- Updated `README.md` baseline section to distinguish L1 vs L2 contracts.
- Updated `copier-template/README.md.jinja` so generated L1 docs stop over-claiming uniform L2 git/folder baselines.
- Added guardrail assertions in `scripts/check-l0-guardrails.sh` to keep the L1-vs-L2 distinction explicit and prevent drift.
- Synced fixtures and re-ran full deterministic checks.

## What Surprised Me
- Strong deterministic checks existed for files and scripts, but wording-level contract drift still persisted in top-level README language.

## Patterns
- Documentation drift is a control-plane risk: over-claiming guarantees can be as harmful as missing checks.
- Baseline contracts should be described at the same granularity as render-time toggles (profile-gated features).

## Crystallization Candidates
- -> `docs/learnings/2026-02-24-readme-baseline-contracts-must-match-rendered-topology.md`
- -> `tips/meta/` candidate: for each “baseline” claim in docs, add at least one executable guardrail assertion anchoring the claim language.
