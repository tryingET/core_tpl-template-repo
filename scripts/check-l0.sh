#!/usr/bin/env sh
set -eu

repo_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"

tmp_root="$(mktemp -d)"
trap 'rm -rf "$tmp_root"' EXIT

say() { printf '%s\n' "$*"; }
err() { printf '%s\n' "$*" >&2; }

is_enabled() {
  case "$(printf '%s' "${1:-}" | tr '[:upper:]' '[:lower:]')" in
    1|true|yes|on) return 0 ;;
    *) return 1 ;;
  esac
}

verbose=0
if is_enabled "${L0_CHECK_VERBOSE:-}"; then
  verbose=1
fi

check_timeout_seconds="${L0_CHECK_TIMEOUT_SECONDS:-180}"

is_non_negative_integer() {
  case "$1" in
    ''|*[!0-9]*) return 1 ;;
    *) return 0 ;;
  esac
}

if ! is_non_negative_integer "$check_timeout_seconds"; then
  err "error: L0_CHECK_TIMEOUT_SECONDS must be a non-negative integer (got: $check_timeout_seconds)"
  exit 2
fi

timeout_available=0
if [ "$check_timeout_seconds" -gt 0 ] && command -v timeout >/dev/null 2>&1; then
  timeout_available=1
fi

summary_file="$tmp_root/summary.tsv"
: > "$summary_file"

run_check_command() {
  script="$1"

  if [ "$check_timeout_seconds" -gt 0 ] && [ "$timeout_available" -eq 1 ]; then
    timeout "${check_timeout_seconds}s" "$script"
    return
  fi

  "$script"
}

run_check() {
  name="$1"
  script="$2"

  log_file="$tmp_root/$name.log"
  start_ts="$(date +%s)"

  if [ "$verbose" -eq 1 ]; then
    if run_check_command "$script"; then
      status=0
    else
      status=$?
    fi
  else
    if run_check_command "$script" >"$log_file" 2>&1; then
      status=0
    else
      status=$?
    fi
  fi

  end_ts="$(date +%s)"
  duration="$((end_ts - start_ts))"

  warning_count=0
  if [ "$verbose" -eq 0 ] && [ -f "$log_file" ]; then
    warnings_raw="$(grep -Ei '(^warning(:|\[)|\bdirtylocalwarning\b)' "$log_file" || true)"
    if [ -n "$warnings_raw" ]; then
      warnings="$(printf '%s\n' "$warnings_raw" | awk '!seen[$0]++')"
      warning_count="$(printf '%s\n' "$warnings" | awk 'END { print NR }')"
      err "warning[$name]:"
      err "$warnings"
    fi
  fi

  if [ "$status" -eq 0 ]; then
    printf '%s\t%s\t%s\t%s\n' "$name" "ok" "$duration" "$warning_count" >> "$summary_file"
    say "ok: $name (${duration}s, warnings: ${warning_count})"
    return 0
  fi

  timed_out=0
  if [ "$timeout_available" -eq 1 ] && [ "$check_timeout_seconds" -gt 0 ] && [ "$status" -eq 124 ]; then
    timed_out=1
  fi

  printf '%s\t%s\t%s\t%s\n' "$name" "failed" "$duration" "$warning_count" >> "$summary_file"
  if [ "$timed_out" -eq 1 ]; then
    err "error: $name timed out after ${check_timeout_seconds}s (${duration}s elapsed)"
  else
    err "error: $name failed (${duration}s)"
  fi

  if [ "$verbose" -eq 0 ] && [ -f "$log_file" ]; then
    err "---- $name output (last 200 lines) ----"
    tail -n 200 "$log_file" >&2 || true
    err "---- end $name output ----"
    err "hint: set L0_CHECK_VERBOSE=1 for live command output"
  fi

  return "$status"
}

failed=0

run_check "check-l0-guardrails" "$repo_root/scripts/check-l0-guardrails.sh" || failed=$((failed + 1))
run_check "check-session-checkpoint" "$repo_root/scripts/check-session-checkpoint.sh" || failed=$((failed + 1))
run_check "check-supply-chain" "$repo_root/scripts/check-supply-chain.sh" || failed=$((failed + 1))
run_check "check-l0-generation" "$repo_root/scripts/check-l0-generation.sh" || failed=$((failed + 1))
run_check "check-l0-fixtures" "$repo_root/scripts/check-l0-fixtures.sh" || failed=$((failed + 1))

passed="$(awk -F '\t' '$2 == "ok" { c++ } END { print c + 0 }' "$summary_file")"
failed_count="$(awk -F '\t' '$2 == "failed" { c++ } END { print c + 0 }' "$summary_file")"
warning_total="$(awk -F '\t' '{ c += $4 } END { print c + 0 }' "$summary_file")"

say "overview:"
say "  passed: $passed"
say "  failed: $failed_count"
say "  warnings: $warning_total"

awk -F '\t' '{ printf("  - %s: %s (%ss, warnings: %s)\n", $1, $2, $3, $4) }' "$summary_file"

if [ "$failed" -ne 0 ]; then
  exit 1
fi
