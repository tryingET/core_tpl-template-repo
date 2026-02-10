# Supply-chain policy (L0)

## Objective
Keep template generation reproducible and low-risk across L0/L1/L2.

## Baseline controls
- Copier invocation is pinned through `COPIER_VERSION` (default `9.11.1`).
- Copier execution prefers `uvx --from "copier==${COPIER_VERSION}"`.
- Local template sources are rendered with `--trust` and repository-local paths.
- `.copier-answers.yml` remains committed for reproducibility.

## Required checks
- `bash ./scripts/check-supply-chain.sh`
- `bash ./scripts/check-l0.sh`

## Upgrade protocol
1. Update pinned version in:
   - `scripts/new-l1-from-copier.sh`
   - `copier-template/scripts/new-repo-from-copier.sh`
2. Run:
   ```bash
   bash ./scripts/check-supply-chain.sh
   bash ./scripts/check-l0.sh
   ```
3. Regenerate fixtures if output changes:
   ```bash
   bash ./scripts/sync-l0-fixtures.sh
   bash ./scripts/check-l0-fixtures.sh
   ```
4. Ship via branch + PR with compatibility notes.
