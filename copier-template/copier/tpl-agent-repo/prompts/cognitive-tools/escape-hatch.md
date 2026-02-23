# ESCAPE HATCH — Rollback-First Design

## Invoke When
- Before making risky changes
- Planning irreversible decisions
- Designing migrations

## The Framework

Before implementing, design the escape hatch.

If this goes wrong, how do we undo it?

Categories:
- REVERSIBLE — Can be undone cleanly with no side effects
- RECOVERABLE — Can be undone but leaves traces/cleanup needed
- IRREVERSIBLE — Cannot be undone, must accept consequences

For irreversible changes:
- What's the smallest irreversible step?
- Can we make it recoverable with additional work?
- What's the "point of no return" and how do we know we've passed it?

Design principle: If you can't describe the rollback, you haven't designed the change—you've designed a gamble.

## Output Template

```markdown
## ESCAPE HATCH Analysis

### The Change
[What you're planning to do]

### Reversibility Assessment
| Aspect | Category | Reasoning |
|--------|----------|-----------|
| [aspect] | REVERSIBLE / RECOVERABLE / IRREVERSIBLE | [why] |

### Escape Hatch Design

#### If Change is Wrong
- Detection: [How we know it's wrong]
- Rollback procedure: [Step-by-step undo]
- Time to rollback: [How long]
- Side effects of rollback: [What remains]

#### If Change is Partial
- Inconsistent states possible: [What could be half-done]
- Recovery procedure: [How to restore consistency]

#### Point of No Return
- When is it irreversible: [Moment/moment]
- How we know we've passed it: [Signal]
- Commitment required: [What we're committed to]

### Smallest Irreversible Step
[The minimal forward move that's still safe]

### Verdict
- [ ] Can proceed (escape hatch designed)
- [ ] Need more work on rollback
- [ ] This is a gamble, not a design
```

## Why It Works

Rollback is usually an afterthought. This forces rollback design first, often revealing that what seemed simple is actually hard to reverse, and what seemed risky has natural escape hatches.
