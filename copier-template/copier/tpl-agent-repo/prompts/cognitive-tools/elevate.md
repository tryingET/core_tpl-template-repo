# ELEVATE — Document Transcendence

## Invoke When
- Writing important documentation
- Refining AGENTS.md, README, specs
- Documents feel bloated or unclear

## The Framework

Take the target document through three transformations:

1. **SURFACE** → What does it explicitly say? Make every word justify its existence.
2. **SUBTEXT** → What is it trying to achieve but not stating? Make the implicit explicit.
3. **SHADOW** → What is it avoiding? What failure modes does it enable? Make the avoided faced.

Then apply the compression test:
- Can you remove anything without weakening it?
- Can you add anything without diluting it?
- Would a stranger grasp it on first read?
- Does it improve with use or decay with use?

Iterate until it feels inevitable rather than constructed.

Not polished. Inevitable.

## Output Template

```markdown
## ELEVATE Analysis

### SURFACE (Explicit)
- What it says: [summary]
- Words that don't earn their existence: [list]
- Redundancies: [list]

### SUBTEXT (Implicit)
- What it's trying to achieve: [hidden goals]
- Assumptions not stated: [list]
- Implicit knowledge assumed: [list]

### SHADOW (Avoided)
- What it's avoiding: [uncomfortable truths]
- Failure modes enabled: [how it could go wrong]
- Edge cases not addressed: [gaps]

### Compression Test Results
| Question | Answer | Action |
|----------|--------|--------|
| Can remove without weakening? | [yes/no] | [what to cut] |
| Can add without diluting? | [yes/no] | [what to add] |
| Stranger grasps on first read? | [yes/no] | [clarification needed] |
| Improves with use? | [yes/no] | [how to make it age well] |

### ELEVATED Form
[The refined document]

### RESIDUAL DEBT
[What's still imperfect and may never be perfect]
```

## Why It Works

Documents usually improve by addition. This improves by subtraction and revelation of what's hidden. The "residual debt" acknowledgment prevents false completeness.
