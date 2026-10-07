---
summary: "AK6690 P07: isolated candidate verified; owner-scoped fixture fixes with red/green proof, dogfood render, and the declared L0 gate green on 8f8a91a. Landing remains separate."
read_when:
  - "Inspecting or continuing the exact isolated P07 candidate without implying source landing or D167 route qualification."
type: "reference"
task_id: 6690
as_of: "2026-10-06"
---
# P07 conformance candidate — verified result

## Final checkpoint — 2026-10-06 (evening)

The owner chose option A (evidence 14137). The one-line fix in
`tests/test_l1_template_company_ownership.py` (commit 8f8a91a) passes at umask 077 and 022
(14154). One full gate on clean 8f8a91a, at the AK6658 hosted budgets of 900 s and
1800 s, passed all seven leaves with exit 0 (14155). The candidate is still isolated on
`fix/ak6690-agent-instruction-conformance`. Landing, publication, company adoption and
birth are separate acts and have not happened. See
[fixture-and-gate-20261006.md](fixture-and-gate-20261006.md).

## Checkpoint — 2026-10-06 (morning)

The owner docket of 2026-10-06 (evidence 14025) added
`tests/test_l1_answer_template_upgrade.py` to the scope. That fixture failed for two
causes, a linked-worktree BASE render and the runner's umask 0077, and both are fixed with
red/green proof (14057). The dogfood render passes (14070). On subject d65900e the declared
gate passes guardrails, doc-references, session-checkpoint, supply-chain, adversarial and
fixtures (14083, 14100). Generation fails for two reasons, neither caused by this
candidate: the 600 s default budget, and one umask-sensitive test in
`tests/test_l1_template_company_ownership.py`, which is outside scope. Details, logs and the
causal controls are in [fixture-and-gate-20261006.md](fixture-and-gate-20261006.md). The task
is still **not complete**: a green gate needs the owner's choice on that test and on the
generation budget.

## Checkpoint — 2026-10-05

The [executed full-gate record](full-gate-20261005.md) supersedes only the historical
pre-execution blocker below. Native AK5758 delivery and AK6715 follow-up permit the
ordinary stock route; the exact retained candidate dafd202 full gate ran once:
evidence13895 **FAIL**, exit1, five leaves passed/two failed/none skipped.
The951 LOC regression and generation chmod/0077 interaction have admitted two-file
repairs retained as a patch; mechanism evidence13899 is not a repaired full-gate pass.
Changed-subject focused verification was refused before execution for actual concurrent
capacity, evidence13900 **SKIP**, exit74 (89741MiB free <102400MiB floor).
The missing rendered answers-template failure remains unresolved; exact additional
source-owner scope for `tests/test_l1_answer_template_upgrade.py` is requested,
not granted. No retry, source acceptance/landing, adoption, birth or private-route
qualification occurred. See the new record for identities, logs and minimum scope.

## Historical candidate preparation and pre-execution refusal — 2026-10-04

Actual owner admission: governance receipt16277, current L0 source owner explicitly
confirmed in native interview. Own controller claim is session-01a10760-fd27-7413-8a88-a8dded527f50.
Exact base: `a9d2125e3d004cee3cafe2f2e57459f732d58dc0` (current main, not the
canonical checkout's unrelated6658 branch). Source commit234a9a5 and targeted
fixture commit64e09cd are isolated on `fix/ak6690-agent-instruction-conformance`.
No merge, push/publication, company pin/adoption, birth or activation performed.

## Actual change and causal proof

Six source/test/fixture paths only: canonical agent AGENTS.md.j2, guardrail
assertions, generation lane test binding, new instruction regression, matching
L1 AGENTS.md.j2 and L2 AGENTS.md fixture outputs. No Copier answers, persona,
manifest, wrapper/authority service or owner role-card changed.

The source no longer imposes MR-only ordinary work or an unconditional root
fleet destination. Actual owner-admitted workflow/placement must resolve; normal
admitted work is main-first. Unappointed agents remain advisory, persona cannot
issue grants, role exclusions remain, each target needs current owner rights and
exact tasks, birth/appointment/activation and publication remain separate.
No custom policy boolean or AGENTS.override.md is introduced.

`uvx --from copier==9.11.1 python -B -m unittest tests.test_agent_instruction_conformance`:
- Before source repair, exact basea9d2125:3 tests,6 company subcase failures,
  exit1,4.654s. Actual wrapper-rendered text causes failure, not an absent tool.
- After source commit234a9a5:3 tests,6 company subcases, exit0,4.615s.
- Both holdingco/softwareco use the real new-l1 and rendered new-repo wrappers,
  pinned Copier9.11.1, exact committed source revision and temporary isolated
  output. A closed fixture AK_CMD accepts only task show5105: fixture construction,
  **not native authentication, appointment or birth permission proof**.
- Generated instruction checks are textual source/render conformance, not proof
  of owner enforcement, R1 admission, V05 custody or a running Principal.

Fixture provenance: real `./scripts/new-l1-from-copier.sh <scratch>/l1` with
fixture-template-repo/holdingco/company name/maintainer/rich/disabled optional packs;
then rendered `new-repo-from-copier.sh tpl-agent-repo <scratch>/l2` with fixture-agent,
fixture-agent-role and creation_task_idAK-5105. Both exited0; only the two AGENTS
outputs copied to their exact existing fixture paths. Scratch path and command
output remain local alongside red/green logs. This actual task lookup is a syntax
prerequisite for test fixture rendering, not production-creation authority.

## Required AGENTS/CLAUDE loader preflight

Inspected canonical Pi source in
`softwareco/contrib/pi-mono/packages/coding-agent/src/core/resource-loader.ts`
(loadContextFileFromDir and loadProjectContextFiles, lines71–158), plus
`src/core/system-prompt.ts` context rendering (lines25–64 and145–159).
One context file per directory: AGENTS.override.md, AGENTS.md, AGENTS.MD,
CLAUDE.md, CLAUDE.MD in order; configured agent-dir first then root→cwd ancestors,
cwd-bound discovery. Nested linked worktree shadow handling avoids duplicate
main-root context. Rendering uses project_context/project_instructions, with no
machine precedence grant. Shell cd does not project owner policies.

Applicable L0/global/workspace instruction chain was explicitly read. Worktree
root AGENTS matches the canonical L0 bytes; no deeper candidate context file was
found under the source/tests parents. Scratch ancestry had none. No loader source
was changed and no runtime context-discovery effect is claimed by this preflight.

## Full owner check — blocked, not failed tests

Actual command:

```sh
heavy-job run --label ak6690-p07-owner-gate --task 6690 -- \
  bash -c 'cd "$1"; bash ./scripts/check-l0.sh' bash <exact-worktree>
```

Heavy-job exited74 before child execution. Its retained-run enforcement cannot
complete reference inspection because one kernel-protected current-uid process
is outside inspection. Five existing scratch-run paths were reported. The actual
log is retained; no check-l0 leaf ran, no passing owner-gate claim follows.
Do not bypass the heavy-job runner, delete retained state, kill unowned processes,
or change admission policy to make the check appear green.

Owner: workstation heavy-job/scratch admission. Needed act: establish safely complete
reference inspection or an actual owner-supported admitted route for this exact
resource-heavy check, preserving retained unknown state. This infra block does not
prevent documentation/profile preparation under the independently admitted6691.
No routine short worker cutoff was added; native source check policy was unchanged.

## Remaining evidence and exact follow-through

Existing-peer session-01a1052c-34bc-7950-839c-37dd319477a6 statically inspected
exact64e09cd againsta9d2125: no blocking material defect, six scoped paths,
source/L1 fixture identical, L2 corresponding output and diff-check pass. It did
not execute tests or owner gate. Two cautions were incorporated: D68 is now
explicitly SoftwareCo-only where applicable; tests require the pinned uvx/uv
runtime and force COPIER_VERSION9.11.1 against ambient overrides. Actual follow-up
atbe50dc5 with ambient COPIER_VERSION9.11.3:3 tests/6 subcases pass, exit0,4.608s.
Corresponding fixture regeneration yields latest source candidate
`d53cda40552d6e4e11a68bee7f57d98122bbe131`. No independent final-head test execution
or full owner-gate pass is inferred from that earlier static inspection.
Owner gate must run under actual heavy-job admission. Subject-specific composition
with unmerged AK6351 route-A work is still unqualified; no6351 source changed or
claimed. Source landing and exact company pin/answers adoption require their separate
acts and full downstream checks. Therefore AK6690/6672 are **not complete**.

Rollback is the isolated candidate patch only: do not change main, companies or
other worktrees. No birth right was issued/consumed or provider disclosure made;
source revert cannot retrospectively supply or reverse those acts. Preserve local
red/green/fixture/admission-failure logs and unknown retained scratch state.
