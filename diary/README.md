# Diary

Repo-local session capture for KES (Knowledge Evolution System).

## Rule

Use `./diary/` in this repository as the canonical raw session log.

- Entry file: `YYYY-MM-DD--type-scope-summary.md`
- Multiple sessions/day: `YYYY-MM-DD--type-scope-summary--2.md`
- Crystallize to: `docs/learnings/` and TIPs when patterns generalize

Filename convention:
- Start from a commit-style header: `type(scope): summary`
- Slug it into filename-safe form: `type-scope-summary`

## Entry template

```markdown
# YYYY-MM-DD — [Session Focus]

## What I Did
- [Actions]

## What Surprised Me
- [Unexpected outcomes]

## Patterns
- [Repeated structures]

## Crystallization Candidates
- → docs/learnings/
- → tips/meta/
```
