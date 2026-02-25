# 2026-02-24 — Tighten check aggregator warning signal

## What I Did
- Found warning-noise behavior in `scripts/check-l0.sh`: warning extraction matched any line containing `warning`, including code/diff content during failed checks.
- Tightened warning detection regex to explicit diagnostic prefixes (`warning:` / `warning[...]`) plus `DirtyLocalWarning` token.
- Re-ran full deterministic checks to confirm no regressions.

## What Surprised Me
- A too-broad warning matcher can amplify noisy failure output and hide real diagnostics in CI summaries.

## Patterns
- Aggregator parsers should match emitted diagnostic formats, not generic words.
- Log summarizers are control-plane components and need the same precision expectations as linters.

## Crystallization Candidates
- -> `docs/learnings/2026-02-24-warning-aggregators-should-match-diagnostic-prefixes.md`
- -> `tips/meta/` candidate: standardize warning/error prefix contracts for check scripts.
