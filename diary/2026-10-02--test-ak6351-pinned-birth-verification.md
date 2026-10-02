---
summary: "AK6351 isolated branch verification: focused proofs, synchronized fixtures, owner timeout and exact equivalence blockers."
read_when:
  - "Inspecting AK6351 pinned L0 child births or reproducing this bounded verification slice."
type: "reference"
---

# 2026-10-02 — test(AK6351): pinned birth verification

## What I did

Only the existing `feat/ak6351-pinned-l0-births` worktree was edited. Parent retains
AK6351; no AK writes, company mutations, publication, push, merge or task closeout.
Fixture context files remained data. Loader discovery/rendering preflight was read
from Pi's canonical `loadProjectContextFiles` and `system-prompt.ts` before sync.

Reviewed inherited WIP and retained mutation boundaries, layer/creation/default
checks, exact pins, independent cloning, positive completion, sandboxing and
process-group timeout cleanup. Added regressions for custom sealed parent answers,
no company copies, immutable child pins, protected destinations, parent/child
snapshot drift, CLI-vs-file precedence and explicit no-effect operations.

Fixed three concrete failures discovered by those proofs: default inheritance now
uses one early frozen parent snapshot; L1 seals name the actual custom answers
locator; pinned older renderers receive that snapshot through a private input view
with read-only company Git topology. Precreated the Git mount target and disabled
helper bytecode writes. Supply-chain assertions now require refusal of unpinned
L2 execution rather than demanding the removed unsafe fallback. L0 fallback rules
were not changed. No overlays implemented; company catalogs were not retired.

The linked-worktree Copier source was not recognized as VCS for `-r BASE` in the
historical upgrade harness. An independent ordinary clone now binds that fixture
to its real historical commit, rather than silently rendering current files.

Mode-aware equivalence exposed a second issue: private runner umask 077 made
Git/Copier clones materialize templates as 0600/0700 instead of 0644/0755. Only
isolated Git and read-only-company/private-scratch L0-render subprocesses now use
022; the outer birth scratch stays 0700. Final execution retains its existing
sandbox and caller permissions. A restrictive-umask regression covers this.

## Exact final focused commands and observed results

All commands below ran from this worktree. `heavy-job` labels were unique and
used `--task 6351`; its owned scratch was removed on return. No arbitrary cap was
used for focused unittest commands. Explicit shell timeouts below equal the
owner's declared bounds, not relaxed substitutes.

```bash
heavy-job run --label ak6351-focused-all-final-<epoch> --task 6351 -- \
  uvx --from copier==9.11.1 python -B -m unittest \
  tests.test_l1_template_transitions \
  tests.test_company_ontology_ref_inheritance \
  tests.test_l2_template_source \
  tests.test_l1_answer_template_upgrade.UpgradeSafetyTests \
  tests.test_l1_answer_template_legacy \
  tests.test_l1_template_gitlink_retirements
# f08c784: exit 0; 82 tests passed in 661.065s.
# Includes all five real RendererTests and 16 source tests.
# This unbounded focused pass does NOT satisfy the owner's 300s guardrail.

heavy-job run --label ak6351-fixtures-mode-proof-<epoch> --task 6351 -- \
  timeout 300s bash scripts/check-l0-fixtures.sh
# f08c784: exit 0, fixtures pass.

bash scripts/check-doc-references.sh
# exit 0; 4 files / 28 references.
bash scripts/check-session-checkpoint.sh
# exit 0.
bash scripts/check-supply-chain.sh
# exit 0.
uvx --from copier==9.11.1 python -B -m unittest tests.test_l2_system4d_context
# exit 0; 4 tests passed in 0.091s.
bash scripts/check-l0-rocs-consumer.sh
# exit 0.

heavy-job run --label ak6351-owner-l0-final-<epoch> --task 6351 -- \
  bash scripts/check-l0.sh
# a774a30: exit 1; guardrails timeout 300s, 0 checks pass, 6 skipped.
# Prior 20246b6 attempt failed identically. Bounds stayed 300/600/300/300.
# The final mode-only implementation was subsequently verified by the focused
# 82-test run; the full final owner contract is still not established.

heavy-job run --label ak6351-generation-metadata-<epoch> --task 6351 -- \
  timeout 600s bash scripts/check-l0-generation.sh
# 0c6a54c: exit 124; generation exceeded 600s after multiple profile passes.
heavy-job run --label ak6351-adversarial-metadata-<epoch> --task 6351 -- \
  timeout 300s bash scripts/check-l0-adversarial.sh
# 0c6a54c: exit 124; adversarial exceeded 300s during migration coverage.
# Neither is a passing proof of the final full contract.

heavy-job run --label ak6351-fixture-final-mode-sync-<epoch> --task 6351 -- \
  bash scripts/sync-l0-fixtures.sh
# exit 0; all baseline and language-matrix fixtures synchronized.
# Sync also passed at each preceding source-helper correction.

heavy-job run --label ak6351-equivalence-private-mode-final-<epoch> --task 6351 -- \
  uvx --from copier==9.11.1 python -B tests/prove_l2_birth_equivalence.py \
  --company /home/tryinget/ai-society/holdingco \
  --output "$PWD/diary/2026-10-02--ak6351-holdingco-birth-equivalence.json"
# exit 0 means the report was produced; acceptance_satisfied=false.

node /home/tryinget/ai-society/core/agent-scripts/scripts/docs-list.mjs --docs . --strict
# exit 1; eight existing metadata issues, listed below.
node /home/tryinget/ai-society/core/agent-scripts/scripts/docs-list.mjs --docs docs --strict
# exit 0; changed architecture documentation's subtree passes.
```

Earlier focused diagnostics were superseded, not waived: initial WrapperTests+
SourceTests ran 17 tests with two failures (stale fixture and a fake test trying
to change archetype on one immutable child); both resolved. The 16-test source/
custom-parent slice passed. Real completion/no-effect passed immediately; the
all-five custom-parent matrix first failed due the seal locator, then passed in
241.790s after the actual locator and private render-view fixes. An intermediate
full birth module run passed 29 tests in 591.872s. Git mount creation and ignored
bytecode caused initial generation/adversarial/fixture failures; corrected before
bounded reruns. The 63-method guardrail selection initially had one historical
fixture setup error; the ordinary-clone correction yielded 13 passing upgrade
safety tests in 58.383s and finally the complete 82-test focused pass above.
Initial supply-chain assertion failure was corrected and its final run passed.

## Equivalence limits and acceptance blockers

The retained JSON compares every filesystem node (including empty directories),
kind, permission mode, symlink target and exact file bytes. Only these answer
provenance keys are normalized: `_src_path`, `_commit`, `_template_lineage`,
`template_source_sha`. No ordinary output file is excluded. Delta contents are
retained as base64, including the ignored plain ontology manifest input.

Holdingco pin: `c14dc59ba50bb3b3e3561cff496acf321b350ee8`. New births used no
company template copies. Legacy births used copied actual on-disk templates,
including ignored residue. This is an isolated copied-configuration comparison,
not an assertion about original company Git-index topology or other companies.

- Project is **not equivalent**: company-copy-only `.gitlab-ci.yml`,
  `gitlab/ci/rocs.yml`, `governance/work-items.cue`, `governance/work-items.json`,
  plus their two `gitlab` directories. All four files are tracked originals.
- Ignored `copier/tpl-project-repo/ontology/manifest.yaml` was copied without any
  exclusion. The templated manifest wins in the observed final birth; its input
  content/hash is retained in the report, not silently omitted.
- Agent, org, monorepo and package match except the declared provenance fields
  **within this isolated holdingco comparison only**.
- Birth-equivalence acceptance remains **unsatisfied**. Original-index/company
  fleet scope is unproved, and no migration or deletion is authorized here.
- Full L0 owner gate remains blocked by runtime bounds; focused success is not
  a substitute. Generation/adversarial need a within-bound final proof too.
- Repo-wide docs strict remains blocked by existing metadata: two 2026-08-24
  diary entries lacking `read_when`, agent fixture `docs/person/system-prompt.md`,
  and five `tests/fixtures/l1-company-policy` documents (AGENTS, CONTRIBUTING,
  company charter, operating model, README). They were not broadened into scope.

## Patterns / crystallization candidates

Private input snapshots must include the renderer's expected locator, not only
provenance validation. Git executable-bit truth must not be confused with
caller-umask artefact permissions. Preserve full deltas instead of using byte-only
or copied-configuration success as a fleet acceptance proxy. These remain raw
session observations; no knowledge promotion or AK lifecycle action performed.

## Local commits (before this evidence-only entry)

```text
7d9971b feat: stage sealed pinned L0 sources for AK6351 child births
d948f0f fix: render sealed custom parent answers through private input view
0cc6690 fix: seal the actual L1 answers locator for child births
10c9409 fix: serialize Copier answers path as a string in provenance
20246b6 test: synchronize AK6351 pinned-birth owner fixtures
f5ad980 test: align AK6351 runtime checks and isolate bytecode writes
06e4170 test: resynchronize pinned birth fixtures without bytecode
afbd69e fix: precreate read-only company Git topology mount target
0c6a54c test: synchronize Git topology staging fixture
2828fc5 test: retain AK6351 company-copy deltas and pinned supply-chain checks
a774a30 test: bind upgrade fixtures to historical commit in ordinary clone
05be3a8 fix: preserve canonical birth modes within private pinned staging
f08c784 test: synchronize deterministic private-render modes
```

## Complete touched-file manifest (relative to worktree)

```text
copier-template/contracts/provenance-seal.yml.jinja
copier-template/contracts/template-ownership-state.json
copier-template/contracts/template-ownership.yml
copier-template/scripts/check-template-ci.sh
copier-template/scripts/lib/company-ontology-ref.sh
copier-template/scripts/lib/l2_birth_completion.py
copier-template/scripts/lib/l2_birth_execution.py
copier-template/scripts/lib/l2_template_source.py
copier-template/scripts/new-repo-from-copier.sh
diary/2026-10-02--ak6351-holdingco-birth-equivalence.json
diary/2026-10-02--test-ak6351-pinned-birth-verification.md
docs/dev/architecture/layer-taxonomy-and-propagation-architecture.md
fixtures/l1/template-repo/contracts/template-ownership-state.json
fixtures/l1/template-repo/contracts/template-ownership.yml
fixtures/l1/template-repo/scripts/check-template-ci.sh
fixtures/l1/template-repo/scripts/lib/company-ontology-ref.sh
fixtures/l1/template-repo/scripts/lib/l2_birth_completion.py
fixtures/l1/template-repo/scripts/lib/l2_birth_execution.py
fixtures/l1/template-repo/scripts/lib/l2_template_source.py
fixtures/l1/template-repo/scripts/new-repo-from-copier.sh
fixtures/l2/tpl-agent-repo/.copier-answers.yml
fixtures/l2/tpl-monorepo/.copier-answers.yml
fixtures/l2/tpl-org-repo/.copier-answers.yml
fixtures/l2/tpl-package/.copier-answers.yml
fixtures/l2/tpl-project-repo/.copier-answers.yml
fixtures/matrix/tpl-monorepo/root/.copier-answers.yml
fixtures/matrix/tpl-monorepo/root/packages/fixture-elixir-core/.copier-answers.yml
fixtures/matrix/tpl-monorepo/root/packages/fixture-py-core/.copier-answers.yml
fixtures/matrix/tpl-monorepo/root/packages/fixture-rust-core/.copier-answers.yml
fixtures/matrix/tpl-monorepo/root/packages/fixture-ts-core/.copier-answers.yml
fixtures/matrix/tpl-project-repo/elixir/.copier-answers.yml
fixtures/matrix/tpl-project-repo/node/.copier-answers.yml
fixtures/matrix/tpl-project-repo/python/.copier-answers.yml
fixtures/matrix/tpl-project-repo/rust/.copier-answers.yml
fixtures/matrix/tpl-project-repo/typescript/.copier-answers.yml
scripts/check-l0-adversarial.sh
scripts/check-l0-fixtures.sh
scripts/check-l0-generation.sh
scripts/check-l0-guardrails.sh
scripts/check-supply-chain.sh
scripts/lib/fixture-normalization.sh
scripts/sync-l0-fixtures.sh
tests/l2_birth_test_support.py
tests/prove_l2_birth_equivalence.py
tests/test_company_ontology_ref_inheritance.py
tests/test_l1_answer_template_upgrade.py
tests/test_l2_template_source.py
```
