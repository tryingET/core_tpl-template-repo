# TIP-0008: Fixture Coverage Must Match Template Catalog

## Metadata

```yaml
tip: 0008
kind: meta
title: Ensure fixture validation covers all L2 templates, not just primary

provenance:
  source_agent: deep-review
  source_l1: core/tpl-template-repo
  discovered: 2026-02-28
  validated_days: 0
  implemented: 2026-02-28

evidence:
  before:
    pattern: "Only tpl-project-repo had L2 fixture coverage"
    problem: "tpl-monorepo and tpl-package could break without detection"
  after:
    pattern: "All 5 L2 templates have fixture generation and comparison"
    benefit: "Complete coverage of template catalog in CI"
  sample_size: check-l0-fixtures runner
  confidence: high

changes:
  - file: scripts/check-l0-fixtures.sh
    kind: modify
    patch: |
      Add monorepo and package fixture generation and comparison.

  - file: scripts/sync-l0-fixtures.sh
    kind: modify
    patch: |
      Add monorepo and package fixture synchronization.

  - file: fixtures/l2/tpl-monorepo/
    kind: add
    patch: |
      New fixture directory for monorepo L2 output.

  - file: fixtures/l2/tpl-package/
    kind: add
    patch: |
      New fixture directory for package L2 output.

review:
  status: accepted
  reviewers: []
```

## TRUE INTENT

Fixture coverage should be **complete**, not **representative**. If a template exists in the catalog, it must have fixture validation.

## Rule

For every L2 template in `copier-template/copier/`:
1. `scripts/check-l0-fixtures.sh` must generate and compare it
2. `scripts/sync-l0-fixtures.sh` must sync it
3. `fixtures/l2/{template}/` must exist

## Detection

Run this check after adding new templates:
```bash
# Verify fixture coverage matches template catalog
for tpl in copier-template/copier/tpl-*/; do
  name=$(basename "$tpl")
  [ -d "fixtures/l2/$name" ] || echo "MISSING: fixtures/l2/$name"
done
```

## Residual limitations

- Fixture generation increases CI duration (~20-40s per additional template)
- Fixture comparison uses normalization which can mask structural issues
