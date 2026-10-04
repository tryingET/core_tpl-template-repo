---
summary: "AK6586 hosted seam attempt lost runner and artifacts; retain serial evidence before replay."
read_when:
  - "Investigating run37198379861 or continuing AK6586 exact-head characterization."
type: "session"
task_id: 6586
---

# 2026-10-04 — Keep the first condition before starting the second

## Observed failure, not a harmless-flake verdict

- Bounded seam commit `9df7138a86978fe9bac79c2287723d9c74f10a50` was pushed
  only to `perf/ak6586-l0-ci-15min`; all 16 paths passed landed checks.
- Run https://github.com/tryingET/core_tpl-template-repo/actions/runs/37198379861
  failed; job111424829241 ran from11:20:08Z to13:54:18Z (9,250 seconds /
  154.167 runner minutes). This is not a <=15-minute result.
- The serial step was marked failure at12:30:08Z after starting11:20:27Z.
  Reverse replay started then; its step still had no final outcome when the
  hosted runner lost communication. The failure annotation names runner loss,
  but does not explain the earlier serial failure.
- Artifact API returned zero artifacts; run/job log retrieval returned404.
  No test identity/outcome ledger or serial exit/log survived in available
  owner surfaces. Product equivalence is unknown, not green. No scheduler
  adoption is admitted on this missing evidence.
- AK evidence13619 retains narrow/landing proof; evidence13620 retains this
  failed hosted attempt honestly. No merge/task completion permission inferred.

## Evidence-retention repair

- Upload the serial directory immediately after serial execution and before
  replay, using the same immutable uploader and exact performance-branch /
  same-repository PR predicate. Give it a distinct per-run/attempt artifact name.
- Replay requires both successful serial execution and successful checkpoint
  upload. Failed serial checks or uploads remain failures: no continue-on-error
  or passing substitution. The final uploader still runs on failure.
- Default main/PR10 checks and complete serial owner checks remain unchanged.
  Skipping the second condition after a failed first condition is an honest
  stop with unresolved oracle proof, not omission of owner-product coverage.
- Fast workflow tests cover ordering, immutable uploader, distinct artifact names,
  cancellation/fork predicates, failed serial/failed upload refusal, and red
  preservation. Actual artifact-service execution remains to be demonstrated.
- No local heavy-job retry, workaround, production/golden mutation or merge.

## Next step

Publish this evidence-only repair, inspect the next exact-head serial artifact
before diagnosing its failure or proceeding with any scheduler work. Even if
that run is green, real serial/private-unit equality and native wide proof are
still separate obligations. Rollback is the scoped repair commit only.
