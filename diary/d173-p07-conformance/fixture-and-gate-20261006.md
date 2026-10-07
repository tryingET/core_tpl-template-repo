---
summary: "AK6690 2026-10-06: owner-widened fixture repairs (linked-worktree BASE render, runner umask), causal red/green, dogfood render, and the declared L0 gate green on 8f8a91a."
read_when:
  - "Continuing or reviewing AK6690 after the owner docket of 2026-10-06."
type: "reference"
task_id: 6690
as_of: "2026-10-06"
---
# Fixture repair and gate — 2026-10-06

## Authority

Owner docket 2026-10-06, item `tpl-template-test-fixture` = A ("Test-only fix, then one
full gate"), decided 2026-10-06T01:08:40Z, relayed by claude-session-c7cf30a7. Recorded as
AK evidence 14025; AK6690 scope now allows `tests/test_l1_answer_template_upgrade.py`.
Controller: claude-session-35a9e2cb-b0ec-4a37-9df6-4aaae7531439, same isolated worktree
as before. No helper or template path changed; no AK6351 work imported beyond the
identical fixture hunk named below.

## Commits on `fix/ak6690-agent-instruction-conformance`

| Commit | Paths | What |
| --- | --- | --- |
| 5475a40 | scripts/check-l0-guardrails.sh, scripts/check-l0-generation.sh | the retained 2026-10-05 repairs, byte-identical to patch 7278f25a… (951-line cap kept; `chmod a-x`) |
| 821df16 | diary/d173-p07-conformance/ | the previous controller's executed-gate record and patch, unchanged |
| 91d8f3d | tests/test_l1_answer_template_upgrade.py | render BASE from an ordinary `--no-local` clone detached at BASE |
| d65900e | tests/test_l1_answer_template_upgrade.py | build that historical base under umask 022 |
| 8f8a91a | tests/test_l1_template_company_ownership.py | one line: reset the re-emptied seed to 0644 (owner decision 14137) |

## Two causes, each shown red then green

All runs below used the stock heavy-job runner. Its child umask is 0077.

1. **Linked worktree.** Copier does not treat a worktree's `.git` file as a VCS source, so
   `copier copy -r BASE <worktree>` silently renders HEAD. BASE 84d6c81 names the answers
   template `{{ _copier_conf.answers_file }}.j2`; HEAD uses the new name. Red: setUpClass
   `FileNotFoundError …/copier/tpl-agent-repo/.copier-answers.yml.j2`, 0 tests ran
   ([red.log](20261006/red.log)). Fix 91d8f3d is the same hunk the AK6351 branch carries (a774a30),
   without that branch's `L0_TEMPLATE_ROOT` env.
2. **Runner umask.** On clean 91d8f3d, 16 tests ran and 24 subcases failed. Every one failed
   with `ownership reverse placeholder bytes/type/mode drift`
   ([focused-clean.log](20261006/focused-clean.log)). Both clones (the fixture's and Copier's own)
   check BASE out as 0600, and Copier copies those modes. The product's reverse-ownership
   guard then correctly refuses a 0600 `ontology/.gitkeep`. Causal control: the same subject
   with only `umask 022` in the child gave 16 OK ([focused-umask022.log](20261006/focused-umask022.log)).
   Fix d65900e builds only the base (clone, checkout, render) under umask 022. The wrappers
   under test keep the ambient umask.

Green on clean d65900e under umask 0077: UpgradeSafetyTests, UpgradeTests and
`WrapperTests.test_source_fixture_copies_and_budgets`, 16 tests OK
([focused-green.log](20261006/focused-green.log)). `bash -n` passed on both scripts; the guardrail
script has 951 lines. AK evidence 14057.

## Dogfood — AK evidence 14070

From d65900e, the real `new-l1-from-copier.sh` (softwareco) and then the rendered
`new-repo-from-copier.sh tpl-agent-repo … -d creation_task_id=AK-6690` both exited 0. The
lookup used the real installed `ak` (read-only `task show 6690`), not the fixture shim.
The generated AGENTS.md (sha256 386f7f3a…) contains each of the 11 required instructions
once. It contains neither the MR-only rule nor the root-fleet rule. The render went to
scratch only and was deleted afterwards. Nothing was born, registered or activated.

## Declared gate on d65900e — AK evidence 14083 (FAIL, budget)

`heavy-job run --label ak6690-p07-owner-gate --task 6690 -- bash -c 'cd "$1"; bash ./scripts/check-l0.sh' bash <worktree>`

- Attempt 1: runner exit 75. The child never started: scratch free was 51706 MiB, below the
  61440 MiB floor, after the runner's 1800 s wait.
- Attempt 2 (finished 06:00:26Z, default budgets 300 s/600 s): guardrails passed in 273 s,
  and doc-references, session-checkpoint and supply-chain passed. **check-l0-generation hit
  its 600 s budget** in its final unittest batch, after five "template ci / ci smoke" passes
  and with no assertion failure in its output. Adversarial and fixtures were skipped by the
  abort. ([full-gate.log](20261006/full-gate.log))

The budget shortfall predates this candidate. The L0 owner's own AK6658 commit f858356
(unmerged) raises the hosted budgets to 900 s and 1800 s because "full-history proofs exceed
the local 300s default". AK6351's full runs needed 1628–2502 s for generation under a 3600 s
cap. This candidate adds the ~5 s conformance test, and the extra `--no-local` clone takes
0.24 s.

## Leaves the timeout cut off

AK evidence 14100 (FAIL, one pre-existing test). These are the AGENTS.md-declared focused
runs on the same d65900e, through heavy-job (umask 0077), without the orchestrator cap,
so no second full gate was run. Two earlier attempts ended with runner exit 75 on capacity
([leaves-attempt1-exit75.log](20261006/leaves-attempt1-exit75.log),
[generation-attempt1-exit75.log](20261006/generation-attempt1-exit75.log)).

| Leaf | Result |
| --- | --- |
| check-l0-adversarial | PASS, 122 s |
| check-l0-fixtures | PASS, 20 s |
| check-l0-generation | FAIL, exit 1 after 665 s. Every step before the final unittest batch passed. In the batch, 33 of 34 tests passed ([generation-unittests.out](20261006/generation-unittests.out)) |

([leaves.log](20261006/leaves.log)). The one failure is
`test_l1_template_company_ownership.CompanyOntologyTests.test_wrapper_cannot_grant_company_ownership_reseed_or_change_topology`.
It expects `cannot change company ontology topology` and gets
`ownership reverse placeholder bytes/type/mode drift`. The test recreates
`ontology/.gitkeep` with `write_bytes` under the ambient umask, so the file is 0600 at
0077, and its line 334 empties the file but keeps that mode. The reverse guard then refuses
the mode before it reaches the topology check. Causal control: the single test, same
subject, failed at umask 077 and passed at umask 022
([company-077.out](20261006/company-077.out), [company-022.out](20261006/company-022.out)).
The file is unchanged since base a9d2125, and hosted CI runs with umask 022. This is the
same runner-umask class as the fixture fixed above, in a file outside AK6690's scope.

Light local probes under umask 077 (not heavy): `test_agent_template_v2`,
`test_agent_instruction_conformance` and `test_render_l1` gave 11 tests OK.

This left two things for the owner to decide (request 14102): the out-of-scope test, and a
generation budget above the 600 s default.

## Owner decision A and the green gate — evidence 14137, 14154, 14155

The owner said "do A" (14137). That added `tests/test_l1_template_company_ownership.py` to the
scope for a one-line test fix, followed by one full gate at the AK6658 hosted budgets.

- Red on 5c236e3 at umask 077, the failure above
  ([company-red-077.out](20261006/company-red-077.out)).
- Fix 8f8a91a: after the loop empties `ontology/.gitkeep`, chmod it back to 0644. The
  assertion is unchanged.
- Green: the single test passes at umask 077 and at umask 022
  ([077](20261006/company-green-077.out), [022](20261006/company-green-022.out)).

The full gate on clean 8f8a91a ran through heavy-job (child umask 0077) with
`L0_CHECK_VERBOSE=1 L0_CHECK_TIMEOUT_SECONDS=900 L0_CHECK_TIMEOUT_GENERATION_SECONDS=1800 bash ./scripts/check-l0.sh`.
It was admitted immediately and finished at 18:06:15Z with exit 0; the tree was still clean
afterwards. Verbose mode only streams leaf output; the same leaves and limits run.

| Leaf | Result |
| --- | --- |
| check-l0-guardrails | ok, 275 s |
| check-doc-references | ok |
| check-session-checkpoint | ok |
| check-supply-chain | ok |
| check-l0-generation | ok, 682 s (limit 1800 s) |
| check-l0-adversarial | ok, 124 s |
| check-l0-fixtures | ok, 20 s |

([full-gate-a.log](20261006/full-gate-a.log), [full-gate-a-verbose.out](20261006/full-gate-a-verbose.out))

## Limits

No landing, merge, push, company pin or adoption, birth, role-card change or cleanup of
foreign state. Rollback means reverting the branch commits above. Nothing outside the
isolated worktree changed.
