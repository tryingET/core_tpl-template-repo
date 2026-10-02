---
summary: "AK6351 bounded residual fixes: descriptor binds/lineage, tracked control-plane intersections, and Copier short flags."
read_when:
  - "Inspecting the three residual AK6351 fixes and their focused proof."
type: "reference"
---

# AK6351 residual safety fixes

Only the existing owned worktree/branch changed, starting at `0cb18ad`.
Canonical source AGENTS and applicable global/target instructions were read.
No AK writes, canonical L0/company changes, push, merge, PR, worktree deletion,
or owner timeout changes. No AGENTS/CLAUDE fixture writes were needed.

## Bounded patch

- Final child bind uses available Bubblewrap `--bind-fd`/`--ro-bind-fd`, with
  inherited `pass_fds`. Each directory component is opened relative to its
  parent with `O_DIRECTORY|O_NOFOLLOW`; root identity comes from `fstat` and is
  compared with the pre-copy snapshot. Post-copy identity is securely reopened.
- Lineage reads, temporary-file creation, mode preservation and atomic rename
  use pinned parent descriptors and no-follow access. Swapped roots/ancestors
  cannot redirect these writes to canonical paths. Existing process-group
  teardown/timeout behavior is retained; descriptors close after `run` returns.
- Company index intersections reject destinations that contain/descend from
  tracked control-plane files. Gitlink roots are protected, their contents stay
  opaque, and ignored child repos/lane children remain eligible.
- Standalone `-n` is no-effect. Grouped short boolean switches fail in prepare
  before clone/render/destination creation; valued option arguments, including
  option-looking values and attached values, retain their interpretation.
- Existing completion adapter is unchanged: actual Copier `Worker.pretend`
  remains the positive-completion authority. Catalog pins, sealed snapshots,
  private input view, immutable lineage and existing exact-delta evidence remain.

Production/library fixtures changed only:
`l2_template_source.py`, `l2_birth_execution.py`, new `l2_birth_safety.py` under
`copier-template/scripts/lib/` and `fixtures/l1/template-repo/scripts/lib/`.
Tests: `tests/test_l2_template_source.py` and
`tests/test_company_ontology_ref_inheritance.py`.
Production patch commit: `b0239ca`.

## Exact focused proof

From the owned worktree, all test runs used `heavy-job --task 6351`.

```bash
heavy-job run --label ak6351-residual-final-focused --task 6351 -- \
  uvx --from copier==9.11.1 python -B -m unittest -v \
  tests.test_l2_template_source \
  tests.test_company_ontology_ref_inheritance.WrapperTests
# exit 0: 36 tests, 57.005s, OK.

heavy-job run --label ak6351-residual-real-copier --task 6351 -- \
  uvx --from copier==9.11.1 python -B -m unittest -v \
  tests.test_company_ontology_ref_inheritance.RendererTests.test_real_completion_and_no_effect_operations \
  tests.test_company_ontology_ref_inheritance.RendererTests.test_empty_default_and_custom_destination_answers
# b0239ca: exit 0: 2 tests, 189.404s, OK.
```

The source tests include a real Bubblewrap last-moment destination symlink swap:
only the original descriptor-pinned child receives the proof file; the synthetic
canonical company remains unchanged. Other tests cover replaced-root `fstat`
refusal, no-follow ancestors/answers, nested-parent/final-file swaps, read-only
pretend descriptor binds, tracked GitLab paths (including missing working-tree
files), ignored lane children and gitlink-contained packages/apps.
Real Copier covers absent/existing destinations for `-n` and other no-effect
options, positive lineage completion, nested custom answers, project/mono/package
choices and unchanged rerun trees. Library fixture identity and 500-line budgets
are asserted; test files remain below 1000 lines.

Initial unit diagnostic: 24 tests, one error because a tracked regular file used
as a path ancestor correctly raised `NotADirectoryError` before index checking.
The fixture now removes that indexed working-tree file to specifically exercise
tracked intersection refusal; no production check was weakened. A subsequent
35-test source/wrapper run passed in 56.891s before the final added inode/fixture
checks above. Runner scratch cleanup reported success after the final runs.

## Coverage limits / unresolved acceptance

No full owner battery or equivalence rerun. Prior full owner gate still times out;
holdingco project equivalence remains explicitly false due its tracked GitLab
and work-items deltas. Existing exact-delta JSON was not changed or normalized.
These focused passes are not acceptance, fleet proof, or a broad security audit.
No specific residual-fix blocker remains from these focused tests.
