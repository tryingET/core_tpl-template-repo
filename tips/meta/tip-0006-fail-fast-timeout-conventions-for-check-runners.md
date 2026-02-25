# TIP-0006: Fail-Fast Timeout Conventions for Check Runners

## Metadata

```yaml
tip: 0006
kind: meta
title: Standardize timeout controls for top-level check orchestrators

provenance:
  source_agent: deep-review + user feedback
  source_l1: core/tpl-template-repo
  discovered: 2026-02-24
  validated_days: 0
  implemented: 2026-02-24

evidence:
  before:
    pattern: "No per-subcheck timeout control"
    problem: "Long waits and ambiguous stuck states"
  after:
    pattern: "Configurable per-subcheck timeout with explicit failure messaging"
    benefit: "Faster feedback, clearer failure modes"
  sample_size: check-l0 runner
  confidence: high

changes:
  - file: scripts/check-l0.sh
    kind: modify
    patch: |
      Add `L0_CHECK_TIMEOUT_SECONDS` with timeout wrapping and explicit timeout status.

  - file: CONTRIBUTING.md
    kind: modify
    patch: |
      Document fail-fast timeout usage.

review:
  status: accepted
  reviewers: []
```

## TRUE INTENT

Top-level validation runners should fail fast under hangs/slow regressions without sacrificing deterministic gates.

## Convention

- Expose `*_CHECK_TIMEOUT_SECONDS` environment variable.
- Set safe default (e.g., 180s per subcheck).
- Treat `0` as disable-timeout mode.
- Emit explicit timeout diagnostics in aggregate summary.

## Residual limitations

- Depends on `timeout` availability on host platforms.
- Per-subcheck wall-clock caps do not replace root-cause performance work.
