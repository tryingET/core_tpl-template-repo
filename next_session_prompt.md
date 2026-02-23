# next_session_prompt.md — `core/tpl-template-repo`

## Session state (current)
- Repo: `~/ai-society/core/tpl-template-repo`
- Branch: `main`
- Working tree: **clean**
- HEAD: `17137ad` (`docs: add P1.5 and P3`)
- Validation: **passes** (`bash ./scripts/check-l0.sh`)

---

## Session Summary (this run)

### Completed
- **P0**: L0 architecture fix - embedded tpl-*-repo templates, removed generic template-repo
- **P1**: Regenerated healthco-templates from L0
- **Created**: agent-psychotherapist, agent-nutritionist, health-records from new templates
- **Updated**: All validation scripts for new template structure

### Key Commits
```
17137ad docs: add P1.5 (transition physiotherapist) and P3 (domain prompts + learnings loop)
e173677 docs: update session prompt - P0 and P1 complete
323af81 docs: update session prompt - P0 complete
b680a8f feat: replace archetype approach with tpl-*-repo templates
```

---

## Next Session

### P1.5: Transition agent-physiotherapist (5 min)
Regenerate from new template, preserve existing customizations.

### P3: Domain Activity Prompts + Learnings Loop (45 min)
1. Create physiotherapy.md, psychotherapy.md, nutrition.md domain prompts
2. Add `extract-learnings-to-prompt.sh` script
3. Test compound improvement workflow

### P2: Document softwareco integration (later)

---

## Repo States

| Repo | Status |
|------|--------|
| `core/tpl-template-repo` | ✅ Clean |
| `healthco-templates` | ✅ tpl-*-repo/ |
| `healthco/agents/*` | ⚠️ physiotherapist needs transition |
| `softwareco-templates` | ✅ Registry style |

---

## Validation
```bash
cd ~/ai-society/core/tpl-template-repo && bash ./scripts/check-l0.sh
```
