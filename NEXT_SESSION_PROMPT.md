# NEXT_SESSION_PROMPT.md — `core/tpl-template-repo`

## Decision (locked)
Use `~/ai-society/core/tpl-template-repo` as the home of the meta-template.
Rationale: this is core infra (cross-org template kernel), so ownership belongs in `core/`.

---

## Session kickoff prompt
Build `tpl-template-repo` as the L0 meta-template that scaffolds L1 template repos (e.g. `holdingco-templates`, `softwareco-templates`) with opinionated CI/hook/contracts.

Use these reasoning passes in order:
1. **Abductive**: infer required meta-template scope from current `holdingco-templates` + `softwareco-templates` state.
2. **Deductive**: write strict DoD + artifact list before implementation.
3. **Contrapositive**: enumerate recursion/drift/supply-chain failure modes and encode guards.
4. **DSL scaffolding**: define layer contract language (`L0/L1/L2`, allowed transitions, answers-file policy).
5. **Inductive**: implement smallest validated slice first, then expand.

---

## Current known state
- GitHub workflow + custom githooks baseline has already been ported into:
  - `~/ai-society/holdingco/holdingco-templates`
  - `~/ai-society/softwareco/softwareco-templates`
- Both template check scripts pass:
  - `bash ./scripts/check-template-ci.sh`
- Technique reference docs exist at:
  - `~/programming/ralph-intent-kit/intent/intentOS_prompting_techniques_injection_v2.md`
  - `~/programming/rik-depdiet/intent/intentOS_prompting_techniques_injection_v2.md`
  - `~/programming/rik-depviz/intent/intentOS_prompting_techniques_injection_v2.md`

---

## Bounded recursion contract (must enforce)
- **L0**: meta-template (`tpl-template-repo`)
- **L1**: template repos (`holdingco-templates`, `softwareco-templates`, future org template repos)
- **L2**: generated product repos (`tpl-agent-repo`, `tpl-org-repo`, `tpl-project-repo`, `tpl-owned-repo` outputs)

Allowed edges:
- `L0 -> L1`
- `L1 -> L2`

Forbidden edges:
- `L1 -> L0`
- `L2 -> L1`
- any cycle

---

## Definition of Done (L0 slice)
Create a minimal but usable `tpl-template-repo` source with:
1. `copier.yml`
2. `copier-template/` containing:
   - baseline `README.md.jinja`
   - baseline `AGENTS.md`
   - `scripts/new-repo-from-copier.sh`
   - `scripts/check-template-ci.sh`
   - `scripts/install-hooks.sh`
   - `.github/workflows/template-check.yml`
   - `.githooks/pre-commit`, `.githooks/pre-push`
3. contract file for generated L1 repos
4. smoke + idempotency checks for L0 generation
5. explicit recursion policy section in generated README/AGENTS

Validation required:
- L0 guardrail script passes
- generated L1 sample passes `scripts/check-template-ci.sh`
- idempotency test passes

---

## First implementation sequence (smallest safe path)
1. Scaffold `core/tpl-template-repo` as Copier source.
2. Add only one generated target profile first (generic `template-repo` profile).
3. Generate a temp repo from L0 and run its checks.
4. Add org flavors after first slice is stable.

---

## Non-goals (for first slice)
- No deep feature packs yet.
- No template-of-template-of-template beyond L0.
- No automatic nested Copier runs in `_tasks`.

---

## End condition for this next session
Deliver a working L0 meta-template in `~/ai-society/core/tpl-template-repo` that can generate one valid L1 template repo with CI + hooks + checks prewired.
