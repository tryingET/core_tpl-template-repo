# TIP-0005: Diagnostic Prefix Contracts for Check Aggregators

## Metadata

```yaml
tip: 0005
kind: meta
title: Check aggregators must parse explicit diagnostic prefixes

provenance:
  source_agent: deep-review
  source_l1: core/tpl-template-repo
  discovered: 2026-02-24
  validated_days: 0
  implemented: 2026-02-24

evidence:
  before:
    pattern: "Broad keyword warning parsing"
    problem: "False warning summaries from diff/source text containing the token 'warning'"
  after:
    pattern: "Prefix-based warning parsing"
    benefit: "Higher signal-to-noise in consolidated check output"
  sample_size: check-l0 aggregator path
  confidence: high

changes:
  - file: scripts/check-l0.sh
    kind: modify
    patch: |
      Replace broad warning matcher with prefix/schema-aware regex.

review:
  status: accepted
  reviewers: []
```

## TRUE INTENT

Consolidated check output is a control-plane interface. It must report diagnostics with high precision.

## Rule

1. Check scripts should emit structured prefixes (`warning:`, `error:`).
2. Aggregators should parse those prefixes (or known runtime warning tokens), not free-text keywords.
3. Any new warning format requires updating aggregator parsing and tests/guardrails.

## Residual limitations

- Existing scripts may still contain mixed diagnostic styles.
- Full standardization requires incremental adoption across all wrappers/checkers.
