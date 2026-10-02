---
summary: "AK6351 authorized metadata repairs and finite measurement stopped at a new tagged-YAML generation blocker."
read_when:
  - "Continuing AK6351 owner verification after the operator-authorized followups."
type: reference
---

# AK6351 — authorized owner verification: stopped

## Authority and accepted boundaries

Continued only the existing owned `feat/ak6351-pinned-l0-births` branch from
`ca530ee`. The parent retains AK6351. Dispatch identifies the current-session
operator authorization as AK evidence 12202; this agent made no AK writes.

The operator accepted the four historical project-only birth omissions:
`.gitlab-ci.yml`, `gitlab/ci/rocs.yml`, `governance/work-items.cue`, and
`governance/work-items.json` (and resulting absent GitLab directories). This is
an explicit birth-parity exception, **not exact equivalence**. The historical
`2026-10-02--ak6351-holdingco-birth-equivalence.json` remains byte-identical and
`acceptance_satisfied=false`. No broader fleet/original-index proof is claimed.
No company catalog retirement, overlays, canonical L0/company writes, AK6352/3,
push, merge, PR, branch/worktree deletion, task completion or rollout occurred.

Approved engineering scope was finite verification-budget recalibration and
exactly eight Markdown metadata repairs, plus necessary source/fixture sync.
Production 3600s birth/execution timeout, process teardown, sandbox, immutable
lineage and the three residual safety fixes were not changed.

## Completed metadata repair

Commit `7413cbe` adds only missing metadata to the two old diary entries and
five divergent `tests/fixtures/l1-company-policy` documents. Their body bytes
are preserved. Fixture headers are data, not company policy instructions.

The eighth finding is the compiled agent system-prompt fixture. Its compiler
now emits a front-matter header, synchronized in the template, L1 fixture and
L2 fixture. The generated prompt's old body is unchanged. The existing agent
fixture test now checks the header, original compiled marker and compiler
source equality. No document exclusions were added.

Before fixture AGENTS edits, read canonical Pi `resource-loader.ts`:
`loadContextFileFromDir`, `findShadowedContextFile`, `loadProjectContextFiles`,
and `system-prompt.ts` context rendering. Discovery uses one candidate per
folder in AGENTS.override/AGENTS/CLAUDE order, session-cwd ancestry and global
agent context; rendered file blocks create no automatic precedence. Read the
canonical L0 AGENTS/CONTRIBUTING, owned-worktree instructions, engineering
adoption, and previous verification/residual diary before mutation.

## Exact commands, measurements and results

All commands ran from the owned worktree. Retained artifacts are under
`diary/ak6351-verification/`. `measure.py` records UTC timestamps, command argv,
return code and `time.monotonic_ns()` elapsed time. These are actual measured
values, not estimates. Measurement bounds were **7200s plus 30s kill escalation**
for temporary verification commands only; no production timeout was modified.

```bash
heavy-job run --label ak6351-measure-committed-lanes-$(date +%s) --task 6351 -- \
  bash -c '<generation measurement; adversarial only if generation succeeds>'
# Actual inner generation argv (generation.json):
python3 -B diary/ak6351-verification/measure.py \
  diary/ak6351-verification/generation.json \
  timeout --kill-after=30s 7200s bash scripts/check-l0-generation.sh
# Committed metadata source: 7413cbe.
# exit 1; 1919.824092874s; NOT timed out. Heavy-job cleanup: removed.
# Adversarial was not launched because generation failed.

node /home/tryinget/ai-society/core/agent-scripts/scripts/docs-list.mjs \
  --docs . --strict
# Before repair: exit 1, exactly eight findings (docs-before.log).
# After repair: exit 0, strict pass (docs-repaired.log/.exit).
```

The generation error is:

```text
error: generated L1 render should fail closed on tagged YAML answers when PyYAML is unavailable
```

The assertion at `scripts/check-l0-generation.sh:425` calls the generated L1
birth wrapper with a `company_name: !!str Holding Company` answers fixture and
the existing no-PyYAML PATH harness. The assertion reports that the command
succeeded instead of refusing. Root cause is **not diagnosed or waived**.
This is a genuinely new non-approved blocker beyond runtime recalibration and
metadata. Stopped engineering and further heavy checks as required.

Two earlier unsuccessful measurement attempts are retained, not hidden:

- `generation.log/.exit`: launch failed because `/usr/bin/time` is unavailable;
  no generation measurement occurred. Replaced only measurement instrumentation
  with the retained stdlib monotonic harness.
- `generation-initial.json/.log/.exit`: exit 1, 143.769837719s. Metadata compiler
  edits overlapped that measurement, causing the L1 rerender idempotency check
  to see uncommitted compiler/provenance changes. This is an invalid calibration
  attempt caused by this agent, not a source acceptance result. Restarted after
  committing the synchronized metadata; no source changes during the second run.

## Budgets and verification limits

Existing focused selection measurement remains 82 tests / 661.065s from the
prior diary; the residual proofs remain 36 / 57.005s and 2 / 189.404s.
No unrelated ad hoc suites were rerun. The new generation run failed at
1919.824092874s, so it does **not** establish a successful generation budget.
Adversarial has no new measurement. No calibrated defaults were committed:
`check-l0.sh` remains base/guardrails 300s, generation 600s, adversarial 300s,
fixtures 300s, with existing overrides and timeout wrapping unchanged.

`bash scripts/check-l0.sh` was **not rerun** after the new blocker. No full-owner
pass, finite-default acceptance, or passing adversarial/fixture gate is claimed.
The updated agent behavior assertions were not reached by the failed generation
run; final owner validation remains necessary after authorized blocker repair.
An unexecuted agent-owned draft timeout test was removed rather than committing
placeholder assertions. No validation checks were skipped to manufacture green.

Static residual integrity is retained in `residual-integrity.log`: four birth
libraries are byte-identical to `b0239ca` and their L1 fixtures (406, 87, 73,
35 lines, each <=500). The two residual test modules are unchanged from
`ca530ee` (374 and 455 lines, each <=1000); that commit intentionally added
proof assertions beyond b0239ca. The historical exact-delta report is unchanged.

Final docs strict, canonical clean-state and owned-process checks are retained
separately. Final evidence-only commit does not alter execution/source behavior.
Remaining blocker: obtain explicit authority for the tagged-YAML generation
failure, diagnose/repair it, then finish successful lane measurements, choose
finite defaults with margin, and run the complete owner contract on committed
clean source. Lifecycle and production rollout remain outside this task slice.

## Touched paths in this continuation

```text
copier-template/copier/tpl-agent-repo/scripts/compile-system-prompt.py
diary/2026-08-24--l0-baseline-gate-repairs.md
diary/2026-08-24--protected-ontology-pin-propagation.md
fixtures/l1/template-repo/copier/tpl-agent-repo/scripts/compile-system-prompt.py
fixtures/l2/tpl-agent-repo/docs/person/system-prompt.md
fixtures/l2/tpl-agent-repo/scripts/compile-system-prompt.py
tests/fixtures/l1-company-policy/AGENTS.md
tests/fixtures/l1-company-policy/CONTRIBUTING.md
tests/fixtures/l1-company-policy/README.md
tests/fixtures/l1-company-policy/docs/org/company-charter.md
tests/fixtures/l1-company-policy/docs/org/operating_model.md
tests/test_agent_template_v2.py
diary/2026-10-02--test-ak6351-authorized-owner-check-stop.md
diary/ak6351-verification/* (retained measurement/docs/integrity/process artifacts)
```
