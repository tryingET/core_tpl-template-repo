# TIP-0004: Executable Wrapper Contract Guardrails

## Metadata

```yaml
tip: 0004
kind: meta
title: Validate wrapper semantics (selection order + call contracts) with executable checks

provenance:
  source_agent: deep-review
  source_l1: core/tpl-template-repo
  discovered: 2026-02-24
  validated_days: 0
  implemented: 2026-02-24

evidence:
  before:
    pattern: "Checks asserted command presence but not runtime branch order/call semantics"
    problem: "Pinned tooling and helper wrappers could appear correct while executing wrong paths"
  after:
    pattern: "Ordering + runtime contract assertions encoded in deterministic gates"
    benefit: "CI fails on semantic drift, not only string drift"
  sample_size: multiple wrapper regressions in same session
  confidence: high

changes:
  - file: scripts/check-supply-chain.sh
    kind: modify
    patch: |
      Add line-order assertions (uvx -> uv -> copier) and fallback-warning assertions.

  - file: copier-template/scripts/check-template-ci.sh
    kind: modify
    patch: |
      Enforce pinned copier semantics in generated L1 wrappers.

  - file: scripts/check-l0-generation.sh
    kind: modify
    patch: |
      Execute preview-l1-diff runtime check and assert clean no-diff output for alias target.

  - file: scripts/check-l0-guardrails.sh
    kind: modify
    patch: |
      Assert wrapper contract checks are present and not silently removed.

review:
  status: accepted
  reviewers: []
```

## TRUE INTENT

**Guardrail quality depends on semantic checks, not only textual checks.**

If wrappers choose the wrong branch or pass wrong positional arguments, CI must fail immediately—even when command strings still exist in source.

## Rule

For every critical wrapper:
1. Assert **selection semantics** (branch order and fallback visibility).
2. Assert **call semantics** (positional contract correctness).
3. Add at least one **runtime execution path** in deterministic checks.
4. After topology changes, enforce both:
   - negative checks (legacy paths absent),
   - positive checks (new paths actively referenced).

## Residual limitations

- Runtime checks still cover representative paths, not exhaustive environment matrix.
- Non-shell wrapper ecosystems need equivalent guardrail patterns.
