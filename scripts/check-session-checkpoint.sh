#!/usr/bin/env sh
set -eu

repo_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
prompt_file="$repo_root/next_session_prompt.md"

fail() {
  echo "error: $*" >&2
  exit 1
}

[ -f "$prompt_file" ] || fail "missing required file: $prompt_file"

checkpoint_block="$(awk '
  /^## SESSION CHECKPOINT \(UPDATE BEFORE \/commit\)/ { in_checkpoint=1; next }
  in_checkpoint && /^## / { in_checkpoint=0 }
  in_checkpoint { print }
' "$prompt_file")"

[ -n "$checkpoint_block" ] || fail "unable to locate SESSION CHECKPOINT block in next_session_prompt.md"

validation_lines="$(printf '%s\n' "$checkpoint_block" | awk '
  /^- Validation run:/ { in_validation=1; next }
  in_validation && /^- [A-Za-z]/ { in_validation=0 }
  in_validation { print }
')"

[ -n "$validation_lines" ] || fail "session checkpoint must include a Validation run block"

validation_commands="$(printf '%s\n' "$validation_lines" | awk '
  {
    start = index($0, "`")
    if (start == 0) next
    rest = substr($0, start + 1)
    stop = index(rest, "`")
    if (stop == 0) next
    print substr(rest, 1, stop - 1)
  }
')"

[ -n "$validation_commands" ] || fail "validation run must include backticked executable commands"

found_deterministic_gate=0

while IFS= read -r cmd; do
  [ -n "$cmd" ] || continue

  if printf '%s\n' "$cmd" | grep -Eq '(^|[;&|][[:space:]]*)cd[[:space:]]+[^"$~/]'; then
    fail "validation command uses non-root-safe cd target: $cmd"
  fi

  first_token="$(printf '%s\n' "$cmd" | awk '{print $1}')"
  case "$first_token" in
    */*)
      case "$first_token" in
        ./*|~/*|/*|\$*)
          ;;
        *)
          fail "validation command uses non-rooted executable path: $cmd"
          ;;
      esac
      ;;
  esac

  case "$cmd" in
    *"just fcos-check"*|*"bash ./scripts/check-l0.sh"*|*"./scripts/check-l0.sh"*)
      found_deterministic_gate=1
      ;;
  esac
done <<EOF
$validation_commands
EOF

[ "$found_deterministic_gate" -eq 1 ] || fail "validation run must include a deterministic gate command (e.g., just fcos-check or bash ./scripts/check-l0.sh)"

printf '%s\n' "$checkpoint_block" | grep -q '^- Rollback path' || fail "session checkpoint must declare rollback path"
printf '%s\n' "$checkpoint_block" | grep -q 'git restore -- next_session_prompt.md' || fail "rollback path must include git restore for session mirror"
printf '%s\n' "$checkpoint_block" | grep -q '^- KES crystallization flow:' || fail "session checkpoint must declare KES crystallization flow"
printf '%s\n' "$checkpoint_block" | grep -q 'diary/YYYY-MM-DD--type-scope-summary.md' || fail "KES flow must include diary capture path"
printf '%s\n' "$checkpoint_block" | grep -q 'docs/learnings/' || fail "KES flow must include docs/learnings crystallization step"
printf '%s\n' "$checkpoint_block" | grep -q 'tips/meta/' || fail "KES flow must include TIP propagation step"

echo "ok: session checkpoint guardrails"
