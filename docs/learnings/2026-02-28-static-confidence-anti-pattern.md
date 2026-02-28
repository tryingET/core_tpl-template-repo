# Static Confidence Anti-Pattern

**Discovered**: 2026-02-28
**Source**: Deep review of tpl-template-repo validation architecture
**Confidence**: High

## The Pattern

Guardrails that check **text** without executing **behavior** provide false confidence. A system can appear well-protected while actually being vulnerable.

## Example

```sh
# Static check passes - command exists in file
assert_contains "wrapper.sh" "copier==${VERSION}"

# But runtime behavior differs:
# - uvx might fail to install the pinned version
# - Script falls through to unpinned fallback
# - Only a warning is emitted (to stderr)
# - CI continues with exit code 0
```

## The Fix

1. **Execute, don't just assert**: Run the wrapper and check exit codes
2. **Fail fast on pinned runtime failure**: Exit with error, don't fall back silently
3. **Make warnings visible**: Ensure CI surfaces stderr warnings

## Detection Heuristics

- Checks use `grep -qF` but don't execute the code
- Wrappers have fallback branches with warnings instead of errors
- Error messages contain substrings that trigger assertion patterns

## Related TIPs

- TIP-0004: Executable Wrapper Contract Guardrails
- TIP-0006: Fail-Fast Timeout Conventions for Check Runners

## See Also

- `scripts/check-supply-chain.sh` — static assertions
- `scripts/new-l1-from-copier.sh` — fixed to exit on pinned runtime failure
