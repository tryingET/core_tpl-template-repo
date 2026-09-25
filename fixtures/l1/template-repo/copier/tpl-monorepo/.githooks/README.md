# Git hooks

Enable in a new clone (new copies enable it automatically):

```bash
./scripts/install-hooks.sh
```

`pre-commit` runs the workspace `ubs-staged.sh` helper (UBS on staged files) when it
exists: `$UBS_STAGED`, else `~/ai-society/<company>/scripts/ubs-staged.sh`. A missing
helper or an unavailable scanner is reported and does not block the commit; UBS
critical findings do. It does not replace repo-specific checks you add later.
