---
summary: "Normalized tpl-template-repo markdown frontmatter coverage so docs-list strict passes across repo docs, template source surfaces, generated fixtures, diary entries, prompt docs, and reference docs."
read_when:
  - "Read when reconstructing the frontmatter debt cleanup for tpl-template-repo task 822."
type: "reference"
---

# 2026-05-07 — docs frontmatter debt normalization

## Context

The operator asked to fix the remaining `docs-list --strict` frontmatter debt after the AK-native direction template posture change.

Task used: `#822` — `Normalize docs strict front matter coverage across template and fixture docs`.

## What changed

- Added `summary`, `read_when`, and `type` frontmatter to markdown files that `docs-list --strict` reported as missing metadata.
- Added matching frontmatter to markdown-producing L0/L1/L2 template sources where generated fixtures otherwise lost metadata on regeneration.
- Regenerated fixtures with `bash ./scripts/sync-l0-fixtures.sh`.
- Preserved generated fixture parity after metadata normalization.

## Validation

Passed:

```bash
node ~/ai-society/core/agent-scripts/scripts/docs-list.mjs --docs . --strict
bash ./scripts/check-l0-fixtures.sh
bash ./scripts/check-l0-generation.sh
bash ./scripts/check-doc-references.sh
bash ./scripts/check-l0.sh
```

AK evidence recorded:

- `#1400 docs_strict_frontmatter pass`
- `#1401 l0_template_validation pass`

## Note

The earlier downstream `template-propagator` AGENTS/product-posture change was a bounded manual carry-down after the source-template edit, not an execution through the template-propagator propagation engine.
