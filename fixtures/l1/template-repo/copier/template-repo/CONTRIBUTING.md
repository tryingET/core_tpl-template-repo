# Contributing (L2 generated repo)

This repository is an **L2 product repo** generated from an L1 template.

## Workflow

1. Work on a branch.
2. Install hooks (once):
   ```bash
   ./scripts/install-hooks.sh
   ```
3. Run checks:
   ```bash
   ./scripts/ci/smoke.sh
   ./scripts/ci/full.sh
   ```
4. Open PR with concise rationale.

## Guardrails

- Respect recursion bounds (`L2` must not generate `L1`/`L0`).
- Keep `.copier-answers.yml` committed for reproducibility.
- Keep `contracts/layer-contract.yml` policy-aligned.
- Keep baseline structure coherent (`docs/`, `examples/`, `external/`, `ontology/`, `policy/`, `src/`, `tests/`).
- Keep git baseline files (`.github/`, `.githooks/`, `.gitignore`, `.gitattributes`).

## Optional community pack

If enabled by your template policy, maintain:
- `.github/ISSUE_TEMPLATE/`
- `.github/pull_request_template.md`
- `CODE_OF_CONDUCT.md`
- `SUPPORT.md`

## Optional release pack

If enabled by your template policy, maintain:
- `.github/workflows/release-please.yml`
- `.github/workflows/release-check.yml`
- `.github/workflows/publish.yml`
- `.release-please-config.json`, `.release-please-manifest.json`
- `CHANGELOG.md`, `SECURITY.md`
- `scripts/release/check.sh`, `scripts/release/publish.sh`

## Optional trust gate

If enabled by your template policy, maintain the vouch files:
- `.github/VOUCHED.td`
- `.github/workflows/vouch-check-pr.yml`
- `.github/workflows/vouch-manage.yml`
