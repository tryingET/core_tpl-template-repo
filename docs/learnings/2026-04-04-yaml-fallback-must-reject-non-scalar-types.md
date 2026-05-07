---
summary: "YAML Fallback Parsers Must Reject Non-Scalar Types."
read_when:
  - "Read when you need yaml fallback parsers must reject non-scalar types."
type: "reference"
---

# YAML Fallback Parsers Must Reject Non-Scalar Types

**Date:** 2026-04-04
**Trigger:** Deep adversarial review found copier-answers.sh awk fallback returned `|`, `>`, `[a, b]`, `&anchor value` as literal values instead of rejecting them

## Pattern
When implementing a narrow YAML fallback parser in awk/shell, the fallback must reject everything the primary parser (PyYAML) rejects. If the primary returns exit 2 for dicts, lists, block scalars, anchors, and tags, the fallback must do the same.

Otherwise you get split-brain behavior: developer machines (with PyYAML) and minimal CI (without) parse the same file differently.

## Rejection set for YAML scalars
- Block scalar markers: `|`, `>` (with or without trailing indicator)
- Flow collections: `[`, `{`
- Anchors: `&`
- Aliases: `*`
- Tags: `!!`

All of these must return status 2 (unsupported) rather than returning the raw syntax as a value.

## Heuristic
When the fallback parser encounters a value it cannot fully interpret, it must fail closed (status 2) rather than guessing. Silent misparse is worse than explicit failure.
