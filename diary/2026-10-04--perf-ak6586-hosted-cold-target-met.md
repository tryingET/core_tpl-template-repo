---
summary: "AK6586 exact experimental candidate passed in13m26s with six concurrent workers; receipts independently retained, native/adoption obligations remain."
read_when:
  - "Checking the measured AK6586 cold hosted result or considering promotion of the experimental schedule."
type: "session"
task_id: 6586
---

# 2026-10-04 — Experimental candidate met the cold timing target

## Independently observed result

- Run: https://github.com/tryingET/core_tpl-template-repo/actions/runs/37230491078
- Tested commit: `fb26d63b22bc15aaee51aad4cd12b47382ca9fb3`, attempt1, branch
  `perf/ak6586-l0-ci-15min`. Six candidate workers and aggregation succeeded.
  The default serial job was correctly skipped only on this experimental branch.
- GitHub run creation20:01:21Z to terminal update20:14:47Z: **806 seconds /
  13 minutes26 seconds**, including queueing, provisioning and aggregation.
- Maximum concurrent non-skipped jobs: **6**. Total execution intervals:
  **3,974 seconds /66.2333 runner-minutes** (not billed-minute rounding).
- Thirty-three slot artifacts plus one aggregate artifact, all nonexpired at
  inspection. Slot counts4/4/5/6/5/9; no missing slots or failed steps.
- Aggregate `valid=true`, `coverage_valid=true`, no errors:282 expected root
  executions, two nested upgrades,23 profile packets and11 shell receipts.
- Parent independently fetched GitHub run/job data and downloaded the aggregate;
  observer messaging was not used as authority. The artifacts API default page
  contains30 items; `per_page=100` was used before checking the complete34-item set.

## Retained receipts

- [Run and job data](ak6586-hosted-candidate/run37230491078/run.json)
- [Artifact inventory](ak6586-hosted-candidate/run37230491078/artifacts.json)
- [Aggregate output](ak6586-hosted-candidate/run37230491078/aggregate.json)
- [Controller recomputed timing](ak6586-hosted-candidate/run37230491078/controller-metrics.json)

The controller recomputed cold elapsed time, summed job intervals and maximum
concurrency from the provider timestamps. Artifacts/metadata remain records of
this execution, not a general authenticity or future-performance guarantee.

## What this establishes—and what it does not

This exact cold hosted execution meets the operator's observed <=900s timing
and <=6-concurrency criteria. It has94 seconds of margin; one passing execution
is not a guarantee that every future workload/platform run stays below15 minutes.

The aggregate deliberately keeps performance, assertion execution, product/owner
equivalence, host authenticity and automatic-promotion flags false. Those input
accounting flags do not contradict externally measured GitHub timing, but they
must not be presented as an equivalence/admission/approval certificate.

The previous99a9483 attempt failed workflow admission before any jobs because
`runner.temp` was used in job-level environment expressions. That red remains
retained under evidence13823; fb26d63 sets the allocated paths through GITHUB_ENV.
No product failure was inferred from the admission error.

Native-wide verification still has no qualified published heavy-job route per
its5758 owner. It remains an unwaived obligation; no retry, deletion or bypass.
PR10 remains open at its frozen correctness head; no merge, main/default schedule
activation, task completion or fleet/source-owner promotion is authorized here.

This capture is saved locally only so preserving evidence does not launch another
hosted run. Subsequent adoption and remaining evidence are separate owner acts.
