---
summary: "AK6586 observational timing safety net and condition-bound oracle startup; no scheduling optimization yet."
read_when:
  - "Reconstructing the AK6586 CI performance work and its profiling safety net."
type: "receipt"
---

# AK6586 — instrument before restructuring

- Operator explicitly authorized this runtime and deferral release, separate branch
  from green PR10 head f4713a9, cold whole-workflow <=15min, up to6 concurrent hosted
  jobs and reporting total runner minutes. AK evidence13105 records the grant.
- After workspace DB preflights, deferral554 was released and this session claimed
  6586 for43200s (expires2026-10-04T03:25:02Z). PR10/6351 remain untouched.
- Worktree: `ak6586-ci-01a0ffd7-c705-7ed4-87ea-1eb822a5bb16`, branch
  `perf/ak6586-l0-ci-15min`, base exact hosted-green f4713a9/evidence13036.

## Read-only findings

Two independent scouts found hidden reverse-suite `load_tests`, nested UpgradeTests,
stateful rerender histories, class fixture reuse, module/global mocks and shared Git
common-directory hazards. Threads sharing an interpreter are not safe scheduling
units. Simple leaf-level parallelism cannot meet15min: generation alone is45min.
Six-way arithmetic is only a lower bound, not measured feasibility.

## Safety-net implementation and verification

Opt-in `L0_PROFILE_DIR` observes the existing standard unittest schedules and generation
phase boundaries. Default runner commands stay equivalent. JSON retains collection
IDs and existing multiplicity, test/subtest outcomes, times, class-fixture errors,
source commit/dirty paths, condition and parent cohort. The nested upgrade invocation
is independently captured. No assertion, real lifecycle path, template, fixture
output, timeout or scheduler was removed/restructured.

Independent inspection caught two early observer defects before any long baseline:
script execution lacked `-m unittest`'s invocation-cwd import path, and computing
exit solely from `wasSuccessful()` incorrectly converted Python3.14's empty-suite
exit5 to0. Both have causal contract tests now. The observer delegates actual exit
policy to standard unittest, preserves empty/skipped/error/CLI cases, and restores
module invocation's import-path entry. JSON and TSV use shared source-external,
private-owned, no-follow/singly-linked/nonblocking/exclusive-creation artifact IO.
This is trusted-scratch IO, not an adversarial filesystem-race sandbox.

- Pinned Copier9.11.1 / Python3.14.7 narrow cohort:21 tests passed,6.410s.
- Independent reviewer:10 observer contract tests passed; ordinary/profiled System4D
  identity/order matched4 methods and16 subtests; empty5/skipped-class0/error1/CLI2
  matched; symlink/hardlink/FIFO/public/retained outputs refused without blocking.
- Shell syntax, strict docs and `git diff --check` pass. Default AK closure check
  is separately disclosed. Python3.12 and actual reverse/nested execution are not
  yet established by these narrow checks.

## Next legal step

Commit the observational-only slice, verify each committed path on this branch,
then run full serial characterization in a clean ordinary clone/private hosted-like
scratch with complete pinned prerequisites. Capture a second condition and compare
exact IDs/outcomes (including nested/reverse coverage) before any restructuring.
Overhead not attributed to methods is explicitly called unattributed overhead;
no exact class-setup time or <=15min result is claimed yet.
