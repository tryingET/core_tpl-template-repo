---
summary: "Session note: 2026 03 30 Review Adversarial Stack Template Controls."
read_when:
  - "Read when reconstructing repo-local session context for session note: 2026 03 30 review adversarial stack template controls."
type: "reference"
---

# 2026-03-30 — Adversarial review of template control-plane surfaces

## What I Did
- Ran the consolidated L0 validation lane: `bash ./scripts/check-l0.sh`.
- Performed adversarial static review of copier wrappers, CI scripts, release helpers, and answer-file templates.
- Reproduced concrete edge-case failures for:
  - invalid YAML when rendered values contain apostrophes,
  - quote-stripping during L1 -> L2 answer inheritance,
  - false-green ROCS doctor/which behavior with bad `ROCS_BIN`,
  - release baseline checks after a version bump,
  - silent AK coverage skips when `ak` is absent.

## What Surprised Me
- The repo’s happy-path checks are green, but several shipped control-plane scripts still fail under ordinary lifecycle or operator-error conditions.
- The same repo that carefully validates `AK_BIN` lets `ROCS_BIN` bypass validation and report success.
- Release validation is pinned to the bootstrap version (`0.1.0`), so the first successful release turns the checker into a permanent failure source.
- AK-backed template regression coverage is conditional on `ak` being on PATH, while the template-check workflow does not provision it.

## Patterns
- Hand-rolled YAML and ad-hoc string parsing are creating correctness debt.
- Validation scripts are optimized for bootstrap snapshots, not for post-bootstrap lifecycle evolution.
- Several guardrails verify file presence/content, but not the failure modes operators actually hit.

## Crystallization Candidates
- → docs/learnings/: stop hand-rolling answer-file YAML when Copier can emit canonical YAML.
- → docs/learnings/: deterministic wrappers should validate explicit binary overrides before reporting doctor/which success.
- → tips/meta/: CI guardrails must fail closed when required external tooling is absent instead of silently skipping critical coverage.
