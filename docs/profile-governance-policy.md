# Profile governance policy (internal vs public)

## Purpose
Map L0/L1 profile toggles to governance intent so teams can choose consistent defaults for **internal** vs **public** template lines.

This policy defines:
- recommended profile combinations,
- the governance rationale behind each combination,
- when consent/change-control must be stricter.

## Governance-relevant toggles

| Toggle | Governance meaning |
|---|---|
| `l1_org_docs_profile` (`rich`/`compact`) | How much organization-level policy/context is carried directly in generated L1 repos. |
| `l2_org_docs_default` (`compact`/`rich`) | Default org-docs burden for downstream L2 repos. |
| `enable_community_pack` | Whether the repo is prepared for public issue/PR intake and community interaction artifacts. |
| `enable_release_pack` | Whether release automation + release accountability artifacts are expected by default. |
| `enable_vouch_gate` | Whether contribution trust gating is enforced for public-risk surfaces. |

## Recommended profile combinations

Use these as baseline bundles, then override only with explicit rationale.

| Bundle | Typical use | `l1_org_docs_profile` | `l2_org_docs_default` | `enable_community_pack` | `enable_release_pack` | `enable_vouch_gate` |
|---|---|---:|---:|---:|---:|---:|
| `internal-lean` | Private/internal teams, low external intake and minimal org-doc overhead | `compact` | `compact` | `false` | `false` | `false` |
| `internal-standard` | **L0 default** for internal template lines with strong L1 governance and compact L2 docs | `rich` | `compact` | `false` | `false` | `false` |
| `internal-governed` | Internal teams needing stronger policy + release discipline | `rich` | `compact` | `false` | `true` | `false` |
| `public-collaboration` | Public repos with open collaboration and standard release operations | `rich` | `compact` | `true` | `true` | `false` |
| `public-trust-gated` | Public repos with higher abuse/supply-chain risk | `rich` | `compact` | `true` | `true` | `true` |
| `public-rich-org` | Public repos where each L2 must carry full org context locally | `rich` | `rich` | `true` | `true` | `true` |

## Consent and change-control expectations

Map profile decisions to consent tiers:

- **Core / Immutable tier** (highest):
  - changing L0 defaults in `copier.yml`,
  - changing this policy,
  - changing trust/release defaults that affect multiple template lines.
- **Org / Consent-gated tier**:
  - setting or changing defaults for a specific L1 template line,
  - enabling/disabling `enable_vouch_gate` for public-facing lines.
- **Project / Maintained tier**:
  - one-off L2 overrides (for example `-d org_docs_profile=rich` on a specific repo) when trust boundary is unchanged.

If a change moves a repo across trust boundaries (internal -> public, or ungated -> trust-gated), treat it at least as **Org / Consent-gated**.

## Decision rules

1. **Default to internal-safe** (`community=false`, `release=false`, `vouch=false`) unless explicit public/release requirements exist; prefer `internal-standard` unless lightweight internal operation justifies `internal-lean`.
2. If a repo accepts broad external contributions, set `enable_community_pack=true`.
3. If releases are contractual (consumers depend on versioned outputs), set `enable_release_pack=true`.
4. If contribution trust must be explicitly controlled, set `enable_vouch_gate=true`.
5. Keep `l2_org_docs_default=compact` unless each product repo must carry full org governance locally.

## Operational notes

- Always keep `.copier-answers.yml` committed so selected profile choices are auditable.
- Document non-standard combinations in repo `README.md` and/or `AGENTS.md`.
- Validate after profile changes:

```bash
bash ./scripts/check-l0-guardrails.sh
bash ./scripts/check-l0.sh
```
