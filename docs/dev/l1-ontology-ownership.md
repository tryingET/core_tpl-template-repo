---
summary: "L0-owned tree ontology capability: company class, old-reader preparation, and proof-bound receipted forward/reverse transitions. Consumer adoption is separately authorized."
read_when:
  - "Adopting or reversing the L1 tree-layout ontology ownership class."
  - "An existing L1 reader cannot check the new company ownership map."
type: "reference"
---

# L1 tree ontology ownership

## Contract and authority

Ownership map `ai-society.template-ownership/2` adds `company_owned`, currently
restricted to `ontology/**`. It includes `.gitkeep`: L0 renders only that empty
birth placeholder, but an ordinary refresh never replaces or recreates it. Company
vocabulary and outputs are neither refreshed nor retired. Incoming non-placeholder
ontology files, ownership changes, or dropped company/agent claims refuse.

Legacy map `/1`, nonempty topology plan `/1`, owner-gitlink layouts, and established
state `/2` and inherited refresh state `/3` remain supported. Gitlink layouts keep
`.gitmodules` and `ontology` agent-owned and render no ontology files. The new map
schema makes older readers refuse the company class instead of ignoring it.

AK owns task, decision, attribution and evidence authority. This is an L0 capability,
not adoption by holdingco, healthco or teachingco. No fold, identity retirement,
source-admission, live rollout or whole rollback rehearsal is supplied by L0 tests.
The missing-manifest gate is a separate capability (AK 6333).

A production transition needs an accepted repo-scoped decision/ADR, a linked
`post_adr_execution` task claimed by the fixed executor, and a clean canonical
repository or registered worktree of that repository. A separate clone does not
inherit its authority. Use installed `ak`; no production authority override exists.
Never edit a consumer's map/state/hash by hand to imitate a transition.

## Prepare old readers without transferring ownership

A pre-company L1 cannot check the new map yet. First install the new readers through
an ordinary **receipted preparatory refresh**, retaining template ontology ownership.
L0, not the consumer, derives this compatibility render. Its output is disposable;
the target remains unchanged. Existing agent claims missing from the incoming map
refuse preparation rather than disappearing.

From a clean, exact L0 revision, with separately authorized consumer work:

```bash
./scripts/render-l1.sh "$target" "$fresh"
python3 -B scripts/lib/l1_template_ownership.py --repo-root "$target" \
  --transition-action prepare-render --rendered "$fresh" \
  --transition-output "$prepared"
python3 -B scripts/lib/l1_template_ownership.py --repo-root "$target" \
  --rendered "$prepared"
```

`$fresh` and `$prepared` are absent, task-owned `$TMPDIR` paths, disjoint from the
consumer. Review the preparatory actions, obtain the controller's canonical plan,
then use the existing refresh lifecycle: explicit apply with plan hash, wave and
source L0 commit; commit pending state/files; execute both L1 checks; record the
exact `l1_contract_refresh_v1` evidence on the target wave task; finalize with the
canonical plan artifact; commit the state closeout. The Python ownership entrypoint
accepts `--rendered "$prepared"` with the existing refresh flags. This is not a
receipt bypass and does not grant company ownership.

Overwrite-copy is not an adoption route. It refuses template-to-company changes,
non-birth transition states, non-current source refs, and missing/customized seeds
or company content. An existing seed-only birth can be copied idempotently through
the pinned pre-write adapter; changing its ontology topology refuses before rendering.
Use owner-aware refresh for company-authored ontology.

## Forward: ontology-only transfer

Use the fresh L0-rendered company map as `next_map`. The existing eight-field spec
contains `decision_id`, full `adr_commit`, `transition_task_id`, fixed `executor`,
absolute regular `next_map`, `git_delta: []`, `validation`, and nonempty `rollback`.
Its exact required validation is:

```json
[
  {"id":"check-template-ci","command":"bash scripts/check-template-ci.sh"},
  {"id":"ci-full","command":"bash scripts/ci/full.sh"}
]
```

The new canonical plan `/2` permits empty payload **only** for the exact ontology
transfer. It contains the six semantic delta lists and `reverse_of: null`. Other
ownership changes and topology payloads cannot be hidden in this form.

```bash
python3 -B scripts/lib/l1_template_ownership.py --repo-root "$target" \
  --transition-action plan --transition-spec "$spec" --transition-output "$plan"
python3 -B scripts/lib/l1_template_ownership.py --repo-root "$target" \
  --transition-action apply --plan-artifact "$plan"
```

Apply writes only the map and `ownership_transition_pending_receipt` state. Commit
those two files as the direct child of the plan base. Execute both exact commands.
Record passing `l1_ownership_transition_v1` evidence with exactly `plan`,
`applied_commit`, and `validation_results` (`check-template-ci` and `ci-full`, both
integer zero). Evidence is target-repo scoped and must match the canonical plan.

```bash
python3 -B scripts/lib/l1_template_ownership.py --repo-root "$target" \
  --transition-action finalize --plan-artifact "$plan" --finalize-task "AK-$task"
```

Commit **state only**, directly after the pending commit. Later ordinary refreshes
carry the original transition binding into `/3`, re-proving it through pinned AK
evidence and Git history, including after the original task completes.

## Combined Softwareco gitlink-to-company-tree convergence

Plan `ai-society.template-ownership-transition-plan/3` is distinct from topology
`/1` and empty-payload ontology transfer `/2`. This first implementation consumes
only source-owner evidence14868/task5651 and the exact Softwareco source URL. It
requires established state `/2` or proven refresh `/3`, agent claims for `ontology`
and `.gitmodules`, and one exact ontology submodule declaration without ancillary
settings. Install these readers first through a separately receipted, gitlink-layout
preserving refresh. The combined payload cannot contain tooling upgrades.

The spec retains the eight normal authority fields but has a nonempty exact
`git_delta` and one additional `ontology_convergence` preflight object:

```json
{
  "source_repo": "/absolute/clean/source-worktree",
  "source_tree_manifest_sha256": "<sha256-of-canonical-complete-manifest>",
  "source_owner_evidence": {
    "task_id": 5651,
    "evidence_ref": "evidence:14868",
    "details_sha256": "<sha256-of-canonical-AK-evidence-details>"
  }
}
```

Canonical JSON is UTF-8, sorted keys, compact separators, `ensure_ascii=false`,
with one final newline. The complete manifest is path-sorted entries with exact
`path` (`ontology/` prefix), `mode` (`100644`/`100755`), blob `oid`, and
`content_sha256`. Planning independently inventories the source commit and requires
source HEAD to equal the parent's committed gitlink OID. It verifies every live
tracked file's type, bytes and executable mode, refuses unsafe index flags, dirty,
untracked and ignored files, symlinks and nested gitlinks, and compares the supplied
manifest digest. Preserve/dispose source WIP through its owner before this clean
preflight; a Git bundle does not capture uncommitted WIP.

The plan's exact convergence fields are `kind`, `predecessor_layout`,
`successor_layout`, `ontology_gitlink_oid`, `retained_files`, `source_commit_base64`,
`source_tree_oid`, `source_tree_manifest_sha256`, and `source_owner_evidence`.
The original source commit bytes plus reconstructed complete Git tree bind every
retained path and executable mode to the old OID. AK verification checks the pinned
accepted packet details and digest; this neither grants source admission nor proves
a writer fence. The delta deletes only the old gitlink and `.gitmodules`, adds every
source file byte/mode exact, and substitutes explicit `l1_ontology_layout: gitlink`
with `tree` without changing other answer bytes. Unrelated ownership claims survive.
Plan/apply/finalize require an unexpired live task lease; completed history uses
pinned evidence, not a recovered claimant.

Plan with the normal `--transition-action plan` entrypoint. Stage the exact payload
under the separately authorized source move; apply still writes only map and pending
state. Then create the mandatory immutable pending commit message:

```bash
python3 -B scripts/lib/l1_template_transitions.py --repo-root "$target" \
  commit-message --plan "$plan" --output "$message"
# Stage exact map/state controls along with the already reviewed payload.
git -C "$target" add contracts/template-ownership.yml contracts/template-ownership-state.json
git -C "$target" commit -F "$message"
```

`$message` is an external task-owned path. Its final
`L1-Ownership-Transition-Plan:` trailer contains the canonical plan as base64.
Do not amend or rewrite it. The generated checker binds this plan to the pending
state hash and exact applied tree, so fresh clones can prove complete retention
without private submodule objects or AK access. Missing, duplicate, substituted or
noncanonical trailers refuse. L0 additionally proves AK authority/evidence and
recursive predecessor history. No state-schema fields were added.

Execute both exact L1 commands, record the normal target-scoped transition receipt,
finalize, and commit state only as the direct child. Pending state cannot refresh;
interrupted writes require the plan-bound recovery/rollback procedure, never an
unqualified reset of a live worktree. Fixture inverse commits/rematerialization do
not discharge external source/WIP/identity rollback obligations.

After proven convergence, when a fresh render omits unrelated private agent claims,
use the same `prepare-render` command above to derive a company-tree refresh input.
This narrowly preserves those claims and company ontology after proving convergence
history; it does not adopt them into template ownership. Birth/map-only company
states do not qualify, and ordinary fresh-map dropped-claim refusal remains strict.
Use the prepared directory in the normal receipted refresh lifecycle. Repeat refresh
carries the original inherited binding and never overwrites company ontology or
recreates its absent/customized placeholder.

## Reverse: actual receipted action, not a symmetric edit

Revert company source effects through their owners first. For this narrowly supported
reverse, HEAD, index and working tree must contain only the original empty, regular,
mode-0644 `ontology/.gitkeep`. Extra company files, ignored outputs, empty directories,
symlinks, nested `.git`, caches, gitlinks and placeholder drift refuse. Planning,
apply and finalize recheck this condition. L0 never deletes company content for you.
An adoption whose original predecessor contained vocabulary does not qualify for
this placeholder-only reverse; stop and obtain an owner contract instead.

The reverse spec has exactly five fields: new `decision_id`, full `adr_commit`,
claimed `transition_task_id`, fixed `executor`, and `rollback`. These name separately
authorized reverse work; the operator cannot supply an arbitrary successor map or
invent a receipt binding.

```bash
python3 -B scripts/lib/l1_template_ownership.py --repo-root "$target" \
  --transition-action reverse-plan --transition-spec "$reverse_spec" \
  --transition-output "$reverse_plan"
```

L0 derives the inverse ontology claim from the **current** map, preserving unrelated
later map changes. `reverse_of` pins the actual forward task/decision/evidence,
canonical plan, executor, applied/final commits and state hash. Birth ownership or
an unrelated gitlink transition supplies no reverse authority. A `/3` predecessor
must prove its own refresh receipt and historical ancestry, not just the original
forward receipt; the forward grant must predate the inverse base, not a later merge.

Execute the same apply → direct-child pending commit → both checks → new exact AK
receipt → finalize → state-only final commit lifecycle, using `$reverse_plan` and the
reverse task. The resulting map restores predecessor ontology **ownership**, not
old tooling or unrelated map bytes. Ordinary refresh cannot re-grant company ontology
or silently reclaim it; any later transfer needs another explicit transition.

The generated checker supplies structural history checks; L0 additionally verifies
AK evidence and authority. Disposable fixture receipts are deliberately synthetic.
Executed fixture commands prove L0 behavior, not production receipts or discharge of
holdingco decision 168 O1/O2. The whole holdingco restore rehearsal remains AK 6458.
