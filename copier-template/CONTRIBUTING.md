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

## Optional trust gate

If your org enables vouch-based trust gating in this template family, maintain:
- `.github/VOUCHED.td`
- `.github/workflows/vouch-check-pr.yml`
- `.github/workflows/vouch-manage.yml`
