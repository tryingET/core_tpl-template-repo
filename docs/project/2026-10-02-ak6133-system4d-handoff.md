---
summary: "Handoff after AK 6133 (system4d.yaml rendered from copier answers): what landed in L0 and the L1s, where the L2 sweep (AK 6135) stands and who owns it, and the open L0 follow-ups."
read_when:
  - "Starting a session that continues the system4d.yaml work after AK 6133."
  - "Before touching AK 6135 or any generated repo's ontology/src/system4d.yaml."
type: "reference"
task_id: 6133
---

# Handoff 2026-10-02: system4d.yaml after AK 6133

From Claude session tpl-template-repo-aa (f5044d4b). AK is the authority; every fact below
names the AK record that holds it. Re-read those before acting, because they move.

## What landed

- **L0 (AK 6133, done, evidence 11679).** Commits d768fca and 5556a05, pushed 2026-09-30.
  - `tpl-project-repo` and `tpl-monorepo` render `ontology/src/system4d.yaml` from
    `system4d.yaml.j2`. Rendered: the name, the placement, the language or package manager, and
    the boundaries and dependencies every generated repo shares.
  - Every other value starts with `FILL IN` and names the repo's own sources to fill it from.
    The 33 literal `<...>` tokens are gone.
  - Regression test: `tests/test_l2_system4d_context.py`, run by `check-l0-guardrails`.
  - L1 retirement entries (`retired_by` d768fca) in `contracts/l1-template-retirements.json`.
  - Raw session notes: `diary/2026-09-30--feat-l2-system4d-context-from-answers.md`.
- **L1s (evidence 11889, 11936).** softwareco (AK 6315), holdingco (6317), teachingco (6316)
  and healthco (6308) carry both `system4d.yaml.j2` files and neither plain copy. L0 and all four
  L1s are at c14dc59. AK 6309, which this session created for the softwareco refresh,
  duplicated 6315 and is closed as completed by it.

## Where the L2 sweep stands (AK 6135, holdingco/infra/template-propagator)

- Pending, with active deferral 500.
- **Operator rollout authorization 12177.** It covers only exact-byte placeholders with
  verified lineage and no unresolved holds, each filled from its own repo's sources.
  - Excluded: held files, older placeholder variants and existing FILL IN renders.
  - Not authorized: closeout, provenance rewrite, push.
- **Render method proved in isolation (12194).**
- **Execution held (12195).** Whole-target snapshots collect nested and ignored owner data and
  reject local symlinks. Native acceptance needs Git and external owner surfaces that safe
  isolation does not have. Resume only after an owner-authorized snapshot/data-scope and
  native-validator integration proof resolve these holds.
- **Owner.** Pi session `01a0f6da-3230-7c97-aecf-ba0536c9757a` drove 6135 from
  template-propagator through 2026-10-02 (its log was last written 20:19 CEST). Treat 6135 as
  that session's work: do not claim it, run the sweep, or preview it in parallel. Ask the
  operator first.

## Open items (none is authorized yet; propose, then wait for the operator)

1. **L0 learning (this repo's mandatory diary -> docs/learnings flow).** The diary's
   crystallization candidate is still raw:
   - When an L2 template source that L1s already carry is renamed (plain file to `.j2`), it
     needs a retirement entry in a follow-up commit. Nothing else stops `X` and `X.j2` from
     rendering one L2 path, and a refresh deletes only paths in the retirement manifest.
   - `retired_by` must be an L0 ancestor, so a rebase before push means rewriting it.
   - Grep `scripts/` for the old path on any rename: `check-l0-rocs-consumer.sh` asserted the
     plain `tpl-monorepo` file, which surfaced only in the full `check-l0.sh` run.
   - Whether a deterministic check generalizes this (for example, every path dropped from
     `copier-template/copier/**` either has a retirement entry or was never shipped to an L1) is
     open. Propose it before building it.
2. **AK 6135.** Only on operator direction, coordinated with its owning session (above).
3. **Content pass for FILL IN renders.** Repos generated since 5556a05 start with FILL IN
   values that their generating agent was meant to complete. 12177 defers any pass over them
   to a separate proposal.

## Working rules in this checkout

- The validation contract is `bash ./scripts/check-l0.sh`: 7 checks, about 10 minutes. It
  needs a clean, committed tree, because L1 renders refuse a dirty L0. Run it after committing
  and push to main only on 7/7.
- The checkout is shared. Other sessions push here (ontology-kernel-de did on 2026-09-30), so
  fetch and rebase before pushing. Never leave uncommitted files behind: they block every L1
  refresh run from this checkout.
- After any change under `copier-template/`, regenerate the fixtures with
  `bash ./scripts/sync-l0-fixtures.sh`.
- Claim AK tasks as `session-$PI_SESSION_ID`.

## First steps

1. Read this file, `AGENTS.md`, and the 2026-09-30 diary entry.
2. Verify the state:
   - `git fetch && git status -sb`
   - `ak task show 6133`
   - `ak task show 6135`
   - `ak evidence task 6135 | tail -40`
3. Report what changed since this handoff, and which open item you recommend, to the operator.
   Mutate nothing until the operator picks one.
