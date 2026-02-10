# Contributing (L1 generated repo)

This repository is an **L1 template repo** generated from AI Society L0.

## Workflow

1. Create a branch.
2. Keep diffs small and reviewable.
3. Run template checks:
   ```bash
   bash ./scripts/check-template-ci.sh
   ```
4. Open PR with validation output.

## Required guardrails

- Keep recursion contract bounded (`L0 -> L1 -> L2`).
- Keep `.copier-answers.yml` committed.
- Do not add nested Copier invocations in template `_tasks`.
- Keep `contracts/layer-contract.yml` aligned with README/AGENTS recursion sections.
- Preserve baseline skeleton folders for generated repos (`docs/`, `examples/`, `external/`, `ontology/`, `policy/`, `src/`, `tests/`) unless explicitly changed by policy.
- Preserve git baseline files (`.github/`, `.githooks/`, `.gitignore`, `.gitattributes`).

## Optional community pack

If your org enables the community collaboration pack for this template line, maintain:
- `.github/ISSUE_TEMPLATE/`
- `.github/pull_request_template.md`
- `CODE_OF_CONDUCT.md`
- `SUPPORT.md`

## Optional release pack

If your org enables release automation in this template family, maintain:
- `.github/workflows/release-please.yml`
- `.github/workflows/release-check.yml`
- `.github/workflows/publish.yml`
- `.release-please-config.json`, `.release-please-manifest.json`
- `CHANGELOG.md`, `SECURITY.md`
- `scripts/release/check.sh`, `scripts/release/publish.sh`

## Optional trust gate

If your org enables vouch-based trust gating in this template family, maintain:
- `.github/VOUCHED.td`
- `.github/workflows/vouch-check-pr.yml`
- `.github/workflows/vouch-manage.yml`
