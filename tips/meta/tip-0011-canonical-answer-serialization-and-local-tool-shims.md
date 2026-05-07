---
summary: "TIP-0011: Canonical Answer Serialization and Local Tool Shims."
read_when:
  - "Read when you need tip-0011: canonical answer serialization and local tool shims."
type: "reference"
---

# TIP-0011: Canonical Answer Serialization and Local Tool Shims

## Metadata

```yaml
tip: 0011
kind: meta
title: Prefer canonical answer-file serialization and bounded local tool shims in template/control-plane CI

provenance:
  source_agent: deep-review-remediation
  source_l1: core/tpl-template-repo
  discovered: 2026-03-30
  validated_days: 0
  implemented: 2026-03-30

evidence:
  before:
    pattern: "Hand-written answer files and optional ambient CLI dependencies in template CI"
    problem: "Valid strings break on quoting edges, inherited metadata drifts, and CI can go green while critical regressions never execute"
  after:
    pattern: "Canonical YAML emission for stable answer fields plus a narrow repo-local CLI test double for CI-only coverage"
    benefit: "Serialization stays valid, special characters survive fan-out, and CI coverage becomes deterministic instead of PATH-dependent"
  sample_size: tpl-template-repo L0/L1/L2 control-plane remediation
  confidence: high

changes:
  - file: docs/learnings/2026-03-30-canonical-answer-serialization-and-local-tool-shims.md
    kind: add
    patch: |
      Crystallize the control-plane learning from adversarial review and remediation.

  - file: tips/meta/tip-0011-canonical-answer-serialization-and-local-tool-shims.md
    kind: add
    patch: |
      Promote the reusable rule for future template repos and CI control planes.

review:
  status: accepted
  reviewers: []
```

## TRUE INTENT
Template/control-plane code should optimize for **stable reproduction under hostile inputs and absent ambient tooling**, not just happy-path generation.

## Rule
1. Do not hand-roll answer-file YAML when the templating system can emit canonical YAML.
2. Keep answer files limited to the stable fields you actually intend to persist.
3. If template CI depends on an external CLI for a narrow validation slice, prefer a bounded local test double over optional PATH detection.
4. Make diagnostics fail closed when explicit binary overrides are invalid.
5. Encode the sharp-edge regression in deterministic checks immediately after fixing it.

## Detection
Use this checklist when reviewing scaffolding repos, template repos, or meta-control planes:

- Are answer files built with manual quoting/string concatenation instead of canonical serialization?
- Can apostrophes, embedded quotes, or colon-heavy values corrupt persisted answers?
- Does CI silently skip a critical validation branch when a tool is missing on PATH?
- Does `doctor`/`which` claim success even when an explicit override points to a bad binary?
- Are release checks pinned to bootstrap literals instead of current lifecycle state?

If yes, the repo likely needs canonical serialization, fail-closed diagnostics, or a local deterministic shim.

## Residual limitations
- A local test double must stay intentionally narrow; it should cover only the CI slice you actually validate.
- If the real CLI semantics change materially, the shim and regression tests must be updated together.
- Canonical serialization does not remove the need for stable-field selection; emitting volatile internal fields can still break idempotency.
