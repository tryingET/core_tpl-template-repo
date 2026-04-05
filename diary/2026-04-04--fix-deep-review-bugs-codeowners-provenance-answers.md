# Deep Review Bug Fix Batch

**Date:** 2026-04-04
**Type:** fix
**Scope:** copier-answers.sh, CODEOWNERS templates, package provenance

## What
Fixed 4 categories of bugs/smells/gaps from the full adversarial deep review:

1. **copier-answers.sh fallback rejects block-scalar markers** — The awk fallback parser previously returned `|`, `>`, `[a, b]`, `{x: 1}`, `&anchor`, `*alias` as literal values. Now it exits with status 2 (unsupported), matching the documented contract that says "fails closed for multi-line/escaped scalars."

2. **tpl-package CODEOWNERS uses real Copier variable** — Replaced hardcoded `@package-owners` with `{{ package_owner_handle }}`, added the variable to `tpl-package/copier.yml` and the answers template, and added automatic propagation from monorepo `project_owner_handle` in `new-repo-from-copier.sh`.

3. **CODEOWNERS templates cover governance, ontology, and root control-plane files** — All 4 L2 templates now include ownership lines for `governance/**`, `ontology/**`, `AGENTS.md`, and `README.md` (as appropriate per archetype).

4. **Package answers template includes `template_source_sha`** — The explicit dict construction in the package answers template now persists `template_source_sha` for provenance chain completeness.

## Verification
- `check-l0.sh`: 7/7 passed, 0 failures, 0 warnings
- Manual: copier-answers fallback rejects `|`, `>`, `[`, `{`, `&`, `*` with status 2
- Fixture snapshots regenerated and verified
