# Adoption preview report — HoldingCo + SoftwareCo templates (2026-02-11)

## Scope
Preview L0 adoption impact on:
- `~/ai-society/holdingco/holdingco-templates`
- `~/ai-society/softwareco/softwareco-templates`

## Commands run
Baseline preview commands (as requested):

```bash
./scripts/preview-l1-diff.sh ~/ai-society/holdingco/holdingco-templates
./scripts/preview-l1-diff.sh ~/ai-society/softwareco/softwareco-templates
```

Because both target repos currently have local uncommitted changes, a second normalized comparison was run against each repo's committed `HEAD` snapshot (to reduce noise from `.git/*` and local edits):

- render L1 from current L0 defaults
- snapshot target repo with `git archive HEAD`
- compare rendered tree vs snapshot tree with `git diff --no-index --name-status`

## High-level results (normalized `HEAD` snapshot)

| Target repo | Added in target only (`A`) | Present in render only (`D`) | Modified overlap (`M`) |
|---|---:|---:|---:|
| `holdingco-templates` | 234 | 85 | 4 |
| `softwareco-templates` | 74 | 85 | 4 |

Interpretation:
- **85 render-only files in both repos**: current L0-generated `template-repo` baseline is not yet present in target repos.
- **Large target-only sets**: both targets implement different repo archetype layouts (`tpl-agent-repo`, `tpl-org-repo`, etc.), so full-file replacement is not a safe one-shot adoption path.
- **4 overlapping modified paths in both**: `.gitignore`, `README.md`, `scripts/check-template-ci.sh`, `scripts/new-repo-from-copier.sh`.

## Structural divergence summary

### HoldingCo
Major target-only areas:
- `copier/tpl-agent-repo`, `copier/tpl-org-repo`, `copier/tpl-project-repo`
- `templates/` mirrors of archetypes
- `tools/` (including vendored/auxiliary tooling)
- GitLab-oriented CI surfaces (`.gitlab-ci.yml` and templates)

### SoftwareCo
Major target-only areas:
- `copier/tpl-agent-repo`, `copier/tpl-org-repo`, `copier/tpl-owned-repo`
- softwareco-specific owned-repo archetype
- GitLab-oriented CI surfaces

## Recommended profile defaults per target repo

Using `docs/profile-governance-policy.md` bundles:

### `holdingco-templates`
Recommended default: **`internal-standard`**
- `l1_org_docs_profile=rich`
- `l2_org_docs_default=compact`
- `enable_community_pack=false`
- `enable_release_pack=false`
- `enable_vouch_gate=false`

Rationale:
- Internal governance-heavy template line; rich L1 org docs are useful.
- External/public intake is not the default operating mode.
- Release/vouch/community packs should be enabled only for specific externally exposed template surfaces.

### `softwareco-templates`
Recommended default: **`internal-standard`**
- `l1_org_docs_profile=rich`
- `l2_org_docs_default=compact`
- `enable_community_pack=false`
- `enable_release_pack=false`
- `enable_vouch_gate=false`

Rationale:
- Internal software delivery templates with org context needed at L1.
- Keep L2 product repos compact by default.
- Enable release/community/vouch selectively for specific public-facing or externally consumed repositories.

## Adoption guidance (safe path)

1. **Do not attempt full tree overwrite** from current L0 render into either target repo.
2. Land adoption in **focused slices** (policy/docs first, then script convergence, then optional scaffold files).
3. For each slice, validate in target repos with their existing CI expectations before broad roll-out.
4. Re-run preview after each slice to monitor convergence trend instead of aiming for immediate zero diff.
