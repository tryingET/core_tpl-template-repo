---
summary: "Focused AK6351 repair proves raw parent bytes preserve the tagged-YAML refusal boundary."
read_when:
  - "Continuing AK6351 after the tagged-YAML generation blocker repair."
type: reference
---

# AK6351 — raw parent snapshot repair

## Change and cause

The parent-provided staging repair returns captured raw parent bytes as the fifth
`parent_snapshot` element and writes those bytes to the frozen answers. Previously
`yaml.safe_dump(parent)` stripped explicit `!!str` tags before the wrapper's narrow
no-host-PyYAML parser inspected its input, allowing a formerly refused input.
Safe parsing still uses `yaml.safe_load`; input digests and drift checks are unchanged.
The L1 library fixture was synchronized by exact source bytes only.

## Focused proof

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest \
  tests.test_l2_template_source.SourceTests \
  tests.test_company_ontology_ref_inheritance.RendererTests.test_tagged_parent_no_host_yaml_refuses_but_pinned_yaml_renders -v
# PASS: 28 tests, 19.857s (27 SourceTests plus one real-generation test).
cmp copier-template/scripts/lib/l2_template_source.py \
  fixtures/l1/template-repo/scripts/lib/l2_template_source.py
# PASS: exact source equality.
git diff --check
# PASS.
node /home/tryinget/ai-society/core/agent-scripts/scripts/docs-list.mjs --docs . --strict
# PASS: exit 0.
```

New unit proofs cover the five-element tuple, tags, quoting, comments, CRLF and
both frozen copies, plus rejection of unsafe Python-object YAML before launch.
The real test uses exactly the generation script's failing `python3`/`python`
PATH harness and checks `unable to parse 'company_name'`, nonzero exit and no
child creation. The pinned Copier 9.11.1 PyYAML path then completes a real birth;
the ordinary host-PyYAML rerun also passes. Parent/child answer roots are mappings,
the source pin is 40 lowercase hex characters naming a real Git commit, the
closed lineage matches that pin, and the child declares L2. Parent bytes remain
unchanged. No pre-existing test expectation was changed.

The first standalone real-test attempt reached successful rendering but failed a
new assertion for `child['template_source_sha']`: that field is not persisted by
the project template. Removed only that incorrect new assertion; retained the
valid source-pin input and closed-lineage checks. Final combined run above passes.

## Coverage limits

Only this owned worktree/branch was changed. No full generation, full owner check,
AK writes, canonical-repo mutations, push/merge/PR, fixture AGENTS edits, timeout
or budget changes occurred. Historical exact-equivalence reports and acceptance
claims were not rewritten. This focused pass is not full-suite or rollout proof.
