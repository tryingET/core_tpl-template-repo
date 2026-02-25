# TIP-0007: README Baseline Claims Must Map to Render Axes

## Metadata

```yaml
tip: 0007
kind: meta
title: Baseline documentation must state layer/archetype/profile variability explicitly

provenance:
  source_agent: deep-review
  source_l1: core/tpl-template-repo
  discovered: 2026-02-24
  validated_days: 0
  implemented: 2026-02-24

evidence:
  before:
    pattern: "Collapsed L1/L2 baseline wording"
    problem: "Overstated guarantees for L2 outputs"
  after:
    pattern: "Explicit L1 baseline + L2 archetype/profile variability wording"
    benefit: "Docs align with rendered contract and toggles"
  sample_size: README + generated README template path
  confidence: high

changes:
  - file: README.md
    kind: modify
    patch: |
      Distinguish L1 vs L2 baseline guarantees and point to fixture-based contract checks.

  - file: copier-template/README.md.jinja
    kind: modify
    patch: |
      Clarify L2 outputs are archetype/profile-specific.

  - file: scripts/check-l0-guardrails.sh
    kind: modify
    patch: |
      Assert the L1-vs-L2 distinction language remains encoded.

review:
  status: accepted
  reviewers: []
```

## TRUE INTENT

Docs are part of the control plane. Baseline claims must match actual render behavior, including all variability axes.

## Rule

Whenever baseline behavior is documented:
1. State **which layer** the guarantee applies to.
2. State **archetype/profile toggles** that alter output.
3. Add an executable guardrail assertion tying the wording to checks.

## Residual limitations

- This does not automatically validate every prose sentence in all docs.
- Additional doc assertions should be added incrementally where drift risk is high.
