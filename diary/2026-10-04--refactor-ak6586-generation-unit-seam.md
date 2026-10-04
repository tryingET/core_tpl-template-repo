---
summary: "AK6586 recovery and bounded generation seam: closed source graph, owner-selected regression suite, no timing acceptance."
read_when:
  - "Continuing the generation-unit extraction or hosted equivalence work under AK6586."
type: "session"
task_id: 6586
---

# 2026-10-04 — AK6586 generation-unit seam

## Recovered goal and unfinished work

- jq-only analysis of a private snapshot of Pi session
  `01a0ffd7-c705-7ed4-87ea-1eb822a5bb16`, schema 3, recovered the original
  implementation request and last reviewer report. Audit: complete, no issues.
- Original request: repair PR10 CI and report exact pushed-head hosted results;
  no merge or task completion permission. Later operator request authorized the
  separately scoped AK6586 cold whole-workflow target <=900 seconds, at most six
  concurrent hosted jobs, runner minutes reported, coverage preserved (evidence13105).
- PR10 remains open at `f4713a901f288054c4b858df3bae1f6f355054d9`.
- The prior AK6586 lease expired overnight and was recorded as a broken commitment;
  after workspace DB preflight, the same session renewed its claim. Historical
  lapse evidence is not rewritten.

## Bounded slice and evidence

- Move generation implementation into test-owned shell helpers. Public generation
  retains the full serial schedule and ignored-argument behavior. A private entrypoint
  accepts six explicit units; no caching, discovery, exclusions or parallelism.
- Source map reconstructs all 1,150 pre-extraction lines from `5acfd49`, SHA-256
  `ab516ad1e3d80b2670f28a6e07a36a6375257ae679afa361dc59727b935f930c`,
  including 158 assertion/diagnostic anchors. Independent inspection verified this
  against the actual Git object, not only the map's own recorded digest.
- Previous review blockers repaired: the 19 fast seam contracts now run in a
  separately named owner cohort; closed executable-complement checks reject
  shadow definitions; command-level probes exercise actual wrappers' fail-stop
  prefixes and reject emptied/shadowed bodies. Private runner suppresses bytecode.
- The full replay manifest now requires the new cohort in both conditions and
  preserves its fixed Copier9.11.1 entry path. A regression demonstrates that
  matching omission from both conditions cannot pass full comparison.
- Parent narrow run: 95 tests passed in 14.038s under pinned Copier9.11.1,
  selecting `tests.test_ci_generation_units`, `tests.test_ci_reorder`,
  `tests.test_ci_profile`, `tests.test_hosted_ci`, `tests.test_l0_check_timeouts`.
- All extracted shell helpers and both modified entrypoints pass `sh -n` and
  `bash -n`; `git diff --check` and canonical docs-list strict check pass.

## Maintenance and limits

- `ci_generation_source_map.json` intentionally freezes the original assertion
  bodies; do not update its digests to conceal a behavior change. Legitimate
  future routing edits must update the explicit `GLUE`/private-runner digest and
  command witnesses together, retain the shadow/empty-body mutation tests, and
  obtain independent inspection plus actual execution evidence.
- Source mapping and synthetic command probes are not real owner equivalence.
  Complete serial exact-head hosted verification and real private-unit equality
  are still required before adopting a hosted scheduler. No <=15-minute claim.
- Local heavy-job admission previously failed with exit74. No owner-confirmed
  repair or waiver has been observed; no retry or bypass was attempted here.
  Required native wide validation remains outstanding, not waived.
- PR10/main, production templates, goldens, contracts, policy, ontology, fleet,
  AK6351/6160 completion and source-owner admission are untouched.

## Next verification and rollback

- Publish only the scoped performance branch, retain the exact-head full serial
  and fresh reversed-cohort artifacts, and inspect every outcome by identity and
  multiplicity, including the new 19-method cohort and nested upgrades.
- Then obtain actual serial/private-unit equality before parallel scheduler adoption.
- Revert only this seam commit on the isolated performance branch to roll back.
