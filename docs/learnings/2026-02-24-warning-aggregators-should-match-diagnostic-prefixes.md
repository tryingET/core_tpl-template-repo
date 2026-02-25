# 2026-02-24 — Warning aggregators should match diagnostic prefixes, not generic tokens

## Context
Deep review found warning noise in consolidated check output when a sub-check failed.

## Evidence
- `scripts/check-l0.sh` previously used a broad warning matcher (`warning|dirtylocalwarning`).
- Failure logs containing source/diff lines with the word `warning` triggered unrelated warning summaries.

## Pattern
Observability tooling can create false positives when it parses by generic keywords instead of diagnostic schema.

## Guardrail
- Updated `scripts/check-l0.sh` warning extraction to match explicit warning prefixes (`warning:` / `warning[...]`) and `DirtyLocalWarning` token.
- Kept deterministic validation through `bash ./scripts/check-l0.sh`.

## Propagation
- Propagated: `tips/meta/tip-0005-diagnostic-prefix-contracts-for-check-aggregators.md`.
