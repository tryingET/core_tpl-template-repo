---
summary: "AK6351 bounded caller-PATH pinned-runner portability and native verification evidence."
read_when:
  - "Read when assessing the AK6351 pinned runtime portability fix and its coverage limits."
type: "reference"
task_id: 6351
---

# AK6351 — pinned-runner portability

## Bounded change

The hosted PR10 run 37084477226 failed the new owner-render preflight because
setup-uv's executables were outside the fixed system PATH. This change discovers
only caller-PATH uvx/uv, resolves executable files, and mounts them read-only at
explicit private aliases (and original paths to protect writable overlap).
Native uvx also binds exactly its adjacent native uv. Recognized system-interpreter
scripts use only the existing read-only system runtime; unknown external
interpreters/dependencies fail closed. A small private uvx interface shim keeps
uv-only discovery from silently selecting system uvx.

Owner preflight and rendering share one sandbox/mount and therefore one actual
bound binary. Final-child execution uses the same binding helper and fixed private
PATH. Private HOME/cache, Copier 9.11.1 owner rendering, immutable source/lineage
pins, parent/child snapshots, protected destinations, descriptor-root bindings,
positive completion, stripped GIT/LD environment, and process-group kills remain.
No surrounding installation/HOME/host-root/socket directory is newly exposed.

## Observed coverage

- SourceTests + WrapperTests: 45 passing tests, including relocated actual uv/uvx,
  uv-only binding, missing/unavailable runners, same-sandbox preflight failure,
  interpreter refusal, controlled completion and read-only bindings. SourceTests
  use a stub owner renderer; WrapperTests are argv/completion transport doubles,
  not proof of actual Copier birth.
- Real Copier focused tests: **2/2 passed** (66.008s):
  `RendererTests.test_external_native_uv_actual_pinned_source_birth_without_company_copies`
  and `RendererTests.test_real_completion_and_no_effect_operations`. They use
  actual Copier 9.11.1, validate closed immutable lineage, and cover rerender and
  no-effect behavior; the relocated-runner birth has no company template copies.
- Fresh native `bash ./scripts/check-l0.sh`: **7/7 passed**, exit **0**, on clean
  implementation commit `44d43b11f656fdb16dee43a28618a9e5c8a45030`, through
  `heavy-job run --label ak6351-portable-pinned-runtime-native022 --task 6351`.
  Native umask 022 follows the existing integration verification recipe;
  base/adversarial/fixtures **1800s**, generation **3600s**, no exclusions.
  Elapsed **3362.13s** (56m02s); user 636.08s, system 375.10s.
  Leaves: guardrails 739s (105 behavior tests), docs references 0s, session
  checkpoint 0s, supply chain 1s, generation 2181s, adversarial 349s, fixtures 92s.
  Two existing generation warnings: Git re-init ignores initial-branch main/work.
- The first attempt inherited heavy-job's private umask 077 and reproduced the
  documented ownership reverse-placeholder mode refusals (23 guardrail failures).
  It was stopped, all 13 observed owned processes were terminated/reaped, and
  heavy-job reported failure 143 with scratch removed. It is **not** a full proof
  or a waived check. No source changes or weakened assertions were used to rerun.
- Evidence was written **outside** the worktree throughout execution at
  `/home/tryinget/.local/state/pi-quests/tmp/ak6351-portability-native022-01a0f678-716c-785f-a310-9a0d2ff48667`
  (initial/focused evidence at the sibling `ak6351-portability-proof-01a0f678-716c-785f-a310-9a0d2ff48667`).
  Completed aggregate logs, measurements, subject and timestamps are now retained
  in `ak6351-pinned-runner-portability/`. Heavy-job reported success with scratch
  removed; no verification processes remain.
- Docs strict passes. The final commit adds evidence only; the native full proof
  applies to its identical execution/test/fixture code, not a rerun of the later
  evidence tree. Previous native full proofs remain historical.

## Limits

Only task6351 portability, matching L1 library fixtures, tests and this evidence
are changed in the dispatched worktree. No AK/canonical checkout/publication/PR/
CI-infrastructure/credentials/history changes or check waivers. Hosted execution
of this fix is unverified; missing bwrap/owner tools/full history are separate
baseline coverage limits, not repaired here. Parent owns publication/admission.
