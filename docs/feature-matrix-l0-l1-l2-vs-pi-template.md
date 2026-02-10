# Feature matrix — `core/tpl-template-repo` vs `pi-extensions/template`

Scope:
- AI Society meta-template: `~/ai-society/core/tpl-template-repo`
- Reference template: `~/programming/pi-extensions/template`

Legend:
- ✅ present
- ⚠️ partial / different shape
- ❌ absent

| Capability | Preferred AI-Society owner layer | `core/tpl-template-repo` | `pi-extensions/template` | Gap / decision for AI Society |
|---|---|---:|---:|---|
| Explicit recursion model (`L0 -> L1 -> L2`, reverse forbidden) | L0 | ✅ | ❌ | Keep as core differentiator of AI Society.
| Layer contract file in generated artifacts | L0 + L1 | ✅ (`contracts/layer-contract.yml`) | ❌ (uses different contract style) | Keep current contract DSL; do not regress.
| L0 guardrail checks | L0 | ✅ (`check-l0-guardrails.sh`) | ✅ (`template-guardrails.sh`, different intent) | Both have guardrails; semantics differ.
| L0 generation smoke + idempotency | L0 | ✅ (`check-l0-generation.sh`) | ✅ (`smoke-test-template.sh`, `idempotency-test-template.sh`) | Equivalent capability present in both.
| Deterministic golden fixtures | L0 | ✅ (`fixtures/` + `check-l0-fixtures.sh`) | ⚠️ (contract + matrix tests, no committed golden trees) | AI Society currently stronger on snapshot drift checks.
| Supply-chain check script for copier pin policy | L0 | ✅ (`check-supply-chain.sh`) | ⚠️ (policy/docs + validation checks, no equivalent L0 pin script) | Keep current L0 pin enforcement.
| Non-destructive adoption diff preview for existing templates | L0 rollout | ✅ (`preview-l1-diff.sh`) | ❌ | AI Society-specific rollout advantage.
| `.copier-answers.yml` committed in generated repos | L1 + L2 | ✅ | ✅ | Keep enforced in both ecosystems.
| Local hook baseline (`pre-commit` / `pre-push`) | L1 + L2 | ✅ | ✅ | Equivalent.
| Baseline folder skeleton (`docs/examples/external/ontology/policy/src/tests`) | L1 + L2 | ⚠️ (now seeded minimally with `.gitkeep`) | ✅ | AI Society keeps a lightweight starter shape; enrich per profile.
| CI baseline for generated repos | L1 + L2 | ✅ (minimal CI + template-check) | ✅ (CI + release + publish + trust gate) | AI Society CI is intentionally lean.
| Release automation (release-please + publish) | L1/L2 (public package repos) | ❌ | ✅ | Optional future port for public/open-source L2 repos.
| Community intake pack (issue templates + PR template + CoC + support + contributing) | L1/L2 public | ✅ (optional via `enable_community_pack`, default `false`) | ✅ | Keep optional-by-profile; enable for public/community-facing repos.
| Vouch trust gate (`VOUCHED.td`, PR/issue workflows) | L1/L2 public trust boundary | ⚠️ (baseline scaffolded; disabled by default via `enable_vouch_gate=false`) | ✅ | Keep optional-by-profile; enable for public repos.
| Docs discovery helper (`docs-list` wrapper) | L1/L2 | ❌ | ✅ | Optional productivity uplift.
| Startup interview flow (`.pi/extensions/startup-intake-router.ts`) | L2 | ❌ | ✅ | Domain-specific to extension repos, not required at L0.
| Generated-repo contract test (required/forbidden path scanner) | L0 + L1 | ⚠️ (layer + fixture checks, no JSON path contract) | ✅ (`contract/generated-repo.contract.json`) | Could add if path-level conformance becomes painful.
| CODEOWNERS protection | L0 + L1 + L2 | ✅ | ✅ | Keep; update owner handles to active account(s) as needed.
| Security/release docs (`SECURITY.md`, release checks) | L1/L2 public | ❌ | ✅ | Optional depending on repo exposure and package publishing goals.

## Interpretation for AI-Society L0/L1/L2

- **Strong in AI-Society L0 now**: recursion contracts, fixture drift checks, adoption rollout tooling.
- **Main remaining missing feature family** from `pi-extensions/template`: release automation/publishing stack and related public-package governance docs.
- **Recommended layering**:
  - Keep recursion/contract/drift controls in **L0**.
  - Add vouch/community/release features as **L1 profile options** (not forced for private/internal repos).
  - Enable full vouch enforcement mainly for **public L2 repos** accepting outside contributions.
