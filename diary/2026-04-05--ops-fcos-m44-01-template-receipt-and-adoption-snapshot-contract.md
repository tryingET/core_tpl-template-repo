# 2026-04-05 — FCOS-M44-01 template receipt + adoption snapshot contract

- Closed the template-side `FCOS-M44-01` follow-through packet by adding:
  - `governance/dist/managed-launcher-bundle.template-receipt.json` at the L0 repo root
  - `governance/dist/managed-launcher-bundle.adoption-snapshot.json` to generated L2 archetypes that ship `scripts/ak.sh` + `scripts/cargo-operator.sh`
- Updated governance READMEs so generated repos treat the adoption snapshot as a consumer-side contract, not launcher-bundle ownership.
- Extended `scripts/check-l0-generation.sh` and generated L1 `scripts/check-template-ci.sh` so the new receipt/snapshot surfaces fail closed.
- Re-synced fixtures with `bash ./scripts/sync-l0-fixtures.sh`.

## Validation
- `bash ./scripts/check-l0-generation.sh`
- `bash ./scripts/check-l0-fixtures.sh`
- `bash ./scripts/check-l0.sh`
- `bash ./scripts/check-session-checkpoint.sh`
