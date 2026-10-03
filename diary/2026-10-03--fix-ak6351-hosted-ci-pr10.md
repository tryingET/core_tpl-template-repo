---
summary: "AK6351 PR10 hosted CI root-cause repair startup, publication authorization, and focused proof."
read_when:
  - "Reconstructing the PR10 hosted CI repair continuation."
type: "receipt"
---

# 2026-10-03 — AK6351 hosted CI repair

## Rechecked facts and authority

- PR10 is open, head `45b01ec277a480ee6e71b1c756fb3abf87f9c83f`, branch
  `feat/ak6351-pinned-l0-births`, base main `a9d2125`.
- Full hosted run log downloaded for run 37091323548. Job `check` failed;
  guardrails, docs references, generation, adversarial and fixtures failed;
  session-checkpoint and supply-chain passed. The aggregate log truncates each
  failing leaf to its last 200 lines, so it is not a complete individual-test log.
- Live AK6351 is lawful Decision167 step2 and was unclaimed. After workspace DB
  preflight this session claimed it for 43200 seconds. The previous implementation
  owner explicitly confirmed no worktree/branch ownership conflict.
- No changes to canonical main, template-propagator, companies, AK lifecycle,
  PR merge/close state, historical evidence, or production birth implementation.

## Root causes and bounded repair

1. Hosted Ubuntu lacks Bubblewrap: three leaves report `[Errno 2] ... bwrap`.
   Install the real package, admit only its user namespaces through a binary-scoped
   AppArmor profile when Ubuntu restricts them, and probe the sandbox before checks.
2. Depth-one checkout cannot prove retirement/pinned historical-reader ancestry.
   Fetch full history, without persisting checkout credentials. The exact two
   hosted retirement assertion failures were reproduced on a depth-one local
   clone of the original head; both pass in the complete-history checkout.
3. Golden agent births relied on a private installed AK and task5105. Bind a strict
   test-only `task show 5105` executable per positive invocation (and the explicit
   unknown-task probe). Production validation and real pinned Copier remain intact.
4. Docs-ref-check is not installed on hosted CI. The owner repository is private;
   its unchanged seven-file minimal runtime closure is now vendored with commit
   and SHA-256 inventory. Operator explicitly authorized publishing this subset
   through interview; AK evidence12467 records that authorization. The supported
   existing wrapper chooses the bundle without a private workspace or credential.

The original-head full local reproduction retained the same five red leaves with
private AK/docs unavailable and shallow history, but the native sandbox was still
available through the explicitly bound runtime PATH. It also exposed the known
heavy-runner restrictive-umask placeholder refusal, not observed in hosted logs.
This is not an exact hosted-image replay. A separate real source-runner missing-PATH
probe reproduced the exact missing-bwrap exception. Native owner verification must
use normal creation umask022, while private staging remains0700 in production.

## Focused verified results

- `uvx --from copier==9.11.1 python -B -m unittest tests.test_hosted_ci` plus the two
  reported retirement methods: 8 tests, pass, 4.221s.
- `AI_SOCIETY_WORKSPACE=<absent> DOC_REF_CHECK_SCRIPT= AGENT_SCRIPTS_DOC_REF_CHECK=
  bash scripts/check-doc-references.sh`: pass, 4 files / 29 references.
- Seven vendor runtime files compared byte-for-byte with the exact owner Git object:
  pass; independent work-product inspection found no blocker. Suggested positive
  wrapper integration and existing-untracked-reference refusal tests were added.
- `node <agent-scripts>/scripts/docs-list.mjs --docs . --strict`: pass. Its default
  AK closure reconciliation is separately reported skipped, as in prior evidence.
  An additional live-AK-bound diagnostic failed on the pre-existing AK6133 handoff
  because task6133 is now done without its doc supersession marker. This unrelated
  owner-state issue is retained, not silently repaired under AK6351.
- Shell syntax and `git diff --check`: pass.

## Pending at this capture

Complete native owner checks on the committed candidate, final diff inspection,
push, and exact new hosted result. No hosted-green or task-completion claim yet.

## Native owner verification update — 04:59:56Z

On code commit `29be298f74e00274277dcf1235249999afa819ea`:

```text
heavy-job run --label ak6351-ci-native-owner-check --task 6351 -- bash -c \
  'umask 022; cd <PR-worktree>; time bash scripts/check-l0.sh'
exit 0; passed 7; failed 0; skipped 0; elapsed 3508.283s
```

Guardrails767s, docs0s, checkpoint0s, supply-chain0s, generation2290s,
adversarial355s, fixtures96s. The two warnings are existing Git re-init notices
for `--initial-branch=main` and `work`, not skipped/refused checks. Normal finite
1800s/3600s verification defaults and the production3600s bound are unchanged.
An initial timing-wrapper attempt lacked `/usr/bin/time` and exited127 before
any owner check; Bash's native `time` was used for the observed full run.

Strict docs, real docs references, clean status, and `git diff --check` were rechecked
again after the full run. Final work-product inspection found only the listed CI,
test-harness, approved byte-identical tooling, and capture changes. Native logs
are in `diary/ak6351-hosted-ci-native/`; this subsequent capture-only commit does
not change the verified code. Hosted verification remains pending at publication.

## Hosted feedback — 05:45:34Z

Run37098493655 on `dd067dd69445672ee3fad07bfb72b68403fe947d` finished red:
6/7 leaves pass, generation failed1544s. The original infrastructure fixes passed.
Verbose output exposed two remaining harness failures: company ownership forward/
reverse and old-reader preparatory refresh run the real L1 `ci/full.sh` without
binding their synthetic AK. The task-snapshot shell prerequisite then tries the
absent ambient `ak`. This failure is retained in AK evidence12610, not relabeled.

The follow-up binds `AK_CMD` only to the full-CI subprocess. The template-CI
subprocess explicitly unsets it because that entrypoint owns a different,
snapshot-capable fixture; independent inspection caught and corrected an initial
proposal that would incorrectly override both. Regression covers both real gates
under poisoned ambient AK, plus missing-AK and unsupported-export refusal.

The log also reports the pre-existing optional real-core ROCS probe's no-core
branch. Hosted provisioning now fetches the public owner commit
`ac75e95e30d66b3543abca27cb79d69a9dc01e93` (compatible0.4.6) with its frozen lock,
and explicitly binds `ROCS_CORE_PROJECT`, so final hosted proof will include that
same real integration contract rather than relying on machine-local state.
No checks, finite bounds, source pins or production protections are weakened.

Accepted the originating controller's bounded Decision167 coordination handoff:
finish/report6351 and hold6352/6353 in order despite empty runtime dependency
arrays. No new execution, merge, completion, fleet/deletion, Decision168 or Rust
work custody. Live API05:47Z still showed PR10 OPEN with no merge timestamp,
contrary to an unverified merge report; no merge authority is inferred.

Follow-up native and hosted verification remains pending at this capture.
