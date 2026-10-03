---
summary: "AK6351 bounded caller-PATH pinned-runner portability and native verification evidence."
read_when:
  - "Read when assessing the AK6351 pinned runtime portability fix and its coverage limits."
type: "reference"
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
- Real Copier relocation/no-company-copy/completion tests and fresh native full
  check remain pending at this implementation checkpoint. Previous native full
  proofs are historical after execution code changes.

## Limits

Only task6351 portability, matching L1 library fixtures, tests and this evidence
are changed in the dispatched worktree. No AK/canonical checkout/publication/PR/
CI-infrastructure/credentials/history changes or check waivers. Hosted execution
of this fix is unverified; missing bwrap/owner tools/full history are separate
baseline coverage limits, not repaired here. Parent owns publication/admission.
