---
summary: "Wrapper Trust Boundaries Must Be Uniform Across Siblings."
read_when:
  - "Read when you need wrapper trust boundaries must be uniform across siblings."
type: "reference"
---

# Wrapper Trust Boundaries Must Be Uniform Across Siblings

**Date:** 2026-04-04
**Trigger:** Deep adversarial review found rocs.sh had no PATH consent gate while ak.sh did (40-day gap)

## Pattern
When a repository ships multiple launcher/wrapper scripts that follow the same resolution pattern (override → vendored → workspace → PATH), a security hardening applied to one wrapper **must** be applied to all sibling wrappers in the same commit.

## Anti-pattern
Hardening `ak.sh` to require `AK_ALLOW_PATH_FALLBACK=1` while leaving `rocs.sh` to fall back to PATH unconditionally creates an asymmetric attack surface. An attacker only needs to find the weakest sibling.

## Heuristic
After adding a security gate to any wrapper in a set, immediately audit all wrappers that share the same `select_runner()` pattern. If they share the resolution architecture, they share the trust boundary.

## Enforcement
Add a deterministic check: `check-l0-guardrails.sh` should verify that all wrappers that touch PATH use an `*_ALLOW_PATH_FALLBACK` gate or equivalent. This prevents the same class of regression.
