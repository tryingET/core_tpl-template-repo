# TIP-0009: Profile-Aware Preview and Contract-Safe Answers Parsing

## Metadata

```yaml
tip: 0009
kind: meta
title: Rehydrate profile inputs for preview and avoid delimiter-based YAML parsing

provenance:
  source_agent: deep-review
  source_l1: core/tpl-template-repo
  discovered: 2026-02-28
  validated_days: 0
  implemented: 2026-02-28

evidence:
  before:
    pattern: "Preview render only forwarded repo_slug; answers parsing used awk -F':'"
    problem: "False-positive adoption diffs and truncation of colon-containing values"
  after:
    pattern: "Preview rehydrates key answers; inherited values parse by key-prefix stripping"
    benefit: "Accurate preview diffs and robust metadata inheritance"
  sample_size: check-l0 + targeted repros for release profile and colon-containing company_name
  confidence: high

changes:
  - file: scripts/preview-l1-diff.sh
    kind: modify
    patch: |
      Rehydrate render args from target answers and exclude .git from compare trees.

  - file: copier-template/scripts/new-repo-from-copier.sh
    kind: modify
    patch: |
      Replace awk -F':' inherited value parsing with key-prefix stripping.

  - file: scripts/check-l0-generation.sh
    kind: modify
    patch: |
      Add release-profile preview no-diff and colon-preservation regression checks.

  - file: copier-template/.github/workflows/ci.yml
    kind: modify
    patch: |
      Add uv setup step for full lane before possible ROCS usage.

  - file: copier-template/scripts/check-template-ci.sh
    kind: modify
    patch: |
      Assert full-lane uv setup contract in ci workflow.

review:
  status: accepted
  reviewers: []
```

## TRUE INTENT
Preview/adoption tools must reconstruct the target's actual profile contract, not implicit defaults. Parsing contract files must preserve valid scalar content.

## Rule
1. If a script consumes `.copier-answers.yml`, parse by key-prefix extraction (or proper YAML parser), not delimiter splitting.
2. Preview renderers must replay profile/toggle answers from the target whenever possible.
3. Tree diffs for generated repos should ignore `.git/` unless the check explicitly targets VCS state.

## Detection
```bash
# Non-default profile preview should still be no-diff when source == target
bash ./scripts/check-l0-generation.sh

# Full suite (includes fixtures + guardrails)
bash ./scripts/check-l0.sh
```

## Residual limitations
- Parsing is still shell/awk-based, not a dedicated YAML parser library.
- Only selected keys are currently rehydrated for preview; new high-impact keys must be added intentionally.
