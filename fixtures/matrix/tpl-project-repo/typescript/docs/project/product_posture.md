---
summary: "Product posture snapshot: current maturity, target product experience, major gaps, and proof signals."
read_when:
  - "When deciding where the project stands relative to its durable vision"
  - "When selecting or reviewing work from product maturity rather than task history"
  - "When checking whether active work converges on the intended product experience"
type: "reference"
---

# Product Posture

## Purpose

This file is the product-maturity bridge below durable vision.

It captures where the product stands, what target experience it is converging toward, which gaps matter most, and what proof would close those gaps.

It does **not** replace:

- shipped runtime/source truth in code, tests, READMEs, architecture docs, or generated artifacts
- AK task, direction, evidence, or decision authority
- `docs/project/vision.md` as durable product direction
- a repo-local owner decision, packet, or runtime source of truth

Use this file only when a product-wide maturity snapshot helps strategy. Do not turn it into a task log, release log, changelog, roadmap, operating plan, or queue mirror. Do not recreate `strategic_goals.md`, `tactical_goals.md`, `operating_plan.md`, or `operational_plan.md` as planning authority in AK-native repos.

## Posture in one sentence

> Replace this with one sentence that states what is real now, what target product experience the repo is converging toward, and the main maturity gap.

## Product maturity map

| Area | Current posture | Target posture | Main gap | Proof of closure |
|---|---|---|---|---|
| Core capability | What works now, grounded in shipped truth. | What should be true for the intended product experience. | The most important capability gap. | Observable evidence that the gap is closed. |
| Operator / user experience | How a real operator or user experiences the product today. | The intended end-to-end experience. | The experience gap that most affects adoption or trust. | A concrete walkthrough, artifact, or acceptance signal. |
| Evidence / artifact contract | Which docs, outputs, tests, or runtime artifacts currently carry truth. | A coherent artifact story with clear authority boundaries. | Any mismatch between prose, runtime behavior, and generated outputs. | Machine-stable and human-readable artifacts tell the same story. |
| Adoption / integration | Current setup, rollout, or integration posture. | The intended repeatable adoption path. | The highest-friction adoption or migration step. | A fresh operator can follow documented steps without hidden repo memory. |

## Current strengths

- <Strength grounded in shipped code, docs, tests, artifacts, or authoritative runtime state.>
- <Strength that makes the target product experience plausible.>

## Current gaps

- <Product maturity gap that affects strategy, not just one task.>
- <Gap where current posture is often confused with target-state ambition.>

## Target product experience

Describe the intended user, operator, or system journey in concrete terms:

1. <What the user/operator can do.>
2. <What evidence or feedback they receive.>
3. <What decision or outcome becomes easier, safer, or more truthful.>

## Near-term convergence path

1. <Highest-leverage move that closes a product maturity gap.>
2. <Next move that improves coherence between docs, runtime, artifacts, and operator experience.>
3. <Proof, adoption, or validation move that shows the posture changed.>

## Hard rules for status language

- Say what is shipped, observable, or otherwise authoritative today; do not describe target-state ambition as current fact.
- Say “target posture” or “intended experience” when proof has not landed yet.
- Say “proof of closure” only when the cited code, artifact, test, runtime evidence, or owner decision exists.
- Keep product-wide posture here; task-level current truth belongs in AK and the repo's active execution surface.
- Use current-vs-target language inside this file when useful, but reserve separate `current-vs-target` boundary docs for seam-specific transitions.

## Authority map

- Durable ambition: `docs/project/vision.md`
- Product posture: this file
- Shipped runtime/source truth: README, architecture/configuration docs, source code, tests, and generated artifacts owned by the repo
- Durable product direction: `docs/project/vision.md`
- Live execution truth: repo-local AK tasks, direction rows where present, evidence, and decisions
- Raw session evidence: `diary/`
- Crystallized learning: `docs/learnings/`
