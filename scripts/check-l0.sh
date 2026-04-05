#!/usr/bin/env sh
set -eu

repo_root="$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)"

tmp_root="$(mktemp -d)"
trap 'rm -rf "$tmp_root"' EXIT

say() { printf '%s\n' "$*"; }
err() { printf '%s\n' "$*" >&2; }

is_enabled() {
	case "$(printf '%s' "${1:-}" | tr '[:upper:]' '[:lower:]')" in
	1 | true | yes | on) return 0 ;;
	*) return 1 ;;
	esac
}

is_non_negative_integer() {
	case "$1" in
	'' | *[!0-9]*) return 1 ;;
	*) return 0 ;;
	esac
}

resolve_timeout_command() {
	if command -v timeout >/dev/null 2>&1; then
		printf '%s\n' "timeout"
		return 0
	fi

	if command -v gtimeout >/dev/null 2>&1; then
		printf '%s\n' "gtimeout"
		return 0
	fi

	return 1
}

resolve_timeout_seconds() {
	var_name="$1"
	fallback="$2"
	eval "value=\${$var_name:-}"
	if [ -z "$value" ]; then
		value="$fallback"
	fi

	if ! is_non_negative_integer "$value"; then
		err "error: $var_name must be a non-negative integer (got: $value)"
		exit 2
	fi

	printf '%s\n' "$value"
}

verbose=0
if is_enabled "${L0_CHECK_VERBOSE:-}"; then
	verbose=1
fi

base_check_timeout_seconds="$(resolve_timeout_seconds "L0_CHECK_TIMEOUT_SECONDS" "300")"

generation_timeout_default="$base_check_timeout_seconds"
if [ "$base_check_timeout_seconds" -gt 0 ]; then
	generation_timeout_default="$((base_check_timeout_seconds * 2))"
fi

generation_timeout_seconds="$(resolve_timeout_seconds "L0_CHECK_TIMEOUT_GENERATION_SECONDS" "$generation_timeout_default")"
adversarial_timeout_seconds="$(resolve_timeout_seconds "L0_CHECK_TIMEOUT_ADVERSARIAL_SECONDS" "$base_check_timeout_seconds")"
fixtures_timeout_seconds="$(resolve_timeout_seconds "L0_CHECK_TIMEOUT_FIXTURES_SECONDS" "$base_check_timeout_seconds")"

timeout_cmd=""
timeout_available=0
if timeout_cmd="$(resolve_timeout_command 2>/dev/null || true)" && [ -n "$timeout_cmd" ]; then
	timeout_available=1
fi

if [ "$base_check_timeout_seconds" -gt 0 ] && [ "$timeout_available" -eq 0 ]; then
	if is_enabled "${CI:-}" || is_enabled "${GITHUB_ACTIONS:-}"; then
		err "error: timeout enforcement requested but neither timeout nor gtimeout is available on this CI runner"
		exit 2
	fi

	err "warning: timeout enforcement requested (${base_check_timeout_seconds}s base) but neither timeout nor gtimeout is available; continuing without wall-clock caps"
fi

say "timeout policy: base=${base_check_timeout_seconds}s generation=${generation_timeout_seconds}s adversarial=${adversarial_timeout_seconds}s fixtures=${fixtures_timeout_seconds}s runner=${timeout_cmd:-none}"

summary_file="$tmp_root/summary.tsv"
: >"$summary_file"

timed_out_check=""
timeout_abort_announced=0

check_timeout_for() {
	case "$1" in
	check-l0-generation)
		printf '%s\n' "$generation_timeout_seconds"
		;;
	check-l0-adversarial)
		printf '%s\n' "$adversarial_timeout_seconds"
		;;
	check-l0-fixtures)
		printf '%s\n' "$fixtures_timeout_seconds"
		;;
	*)
		printf '%s\n' "$base_check_timeout_seconds"
		;;
	esac
}

record_summary() {
	printf '%s\t%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "$4" "$5" >>"$summary_file"
}

run_check_command() {
	script="$1"
	timeout_seconds="$2"

	if [ "$timeout_seconds" -gt 0 ] && [ "$timeout_available" -eq 1 ]; then
		"$timeout_cmd" "${timeout_seconds}s" "$script"
		return
	fi

	"$script"
}

skip_check() {
	name="$1"
	reason="$2"
	record_summary "$name" "skipped" "0" "0" "$reason"
	say "skip: $name ($reason)"
}

run_check() {
	name="$1"
	script="$2"
	timeout_seconds="$(check_timeout_for "$name")"

	log_file="$tmp_root/$name.log"
	start_ts="$(date +%s)"

	if [ "$verbose" -eq 1 ]; then
		if run_check_command "$script" "$timeout_seconds"; then
			status=0
		else
			status=$?
		fi
	else
		if run_check_command "$script" "$timeout_seconds" >"$log_file" 2>&1; then
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
		record_summary "$name" "ok" "$duration" "$warning_count" ""
		say "ok: $name (${duration}s, warnings: ${warning_count}, timeout: ${timeout_seconds}s)"
		return 0
	fi

	timed_out=0
	if [ "$timeout_available" -eq 1 ] && [ "$timeout_seconds" -gt 0 ] && [ "$status" -eq 124 ]; then
		timed_out=1
		timed_out_check="$name"
	fi

	failure_note=""
	if [ "$timed_out" -eq 1 ]; then
		failure_note="timed_out_after_${timeout_seconds}s"
		record_summary "$name" "failed" "$duration" "$warning_count" "$failure_note"
		err "error: $name timed out after ${timeout_seconds}s (${duration}s elapsed)"
	else
		record_summary "$name" "failed" "$duration" "$warning_count" ""
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

while IFS="$(printf '\t')" read -r name script; do
	[ -n "$name" ] || continue

	if [ -n "$timed_out_check" ]; then
		if [ "$timeout_abort_announced" -eq 0 ]; then
			err "error: aborting remaining checks after timeout in $timed_out_check"
			timeout_abort_announced=1
		fi
		skip_check "$name" "aborted_after_timeout_in_${timed_out_check}"
		continue
	fi

	run_check "$name" "$script" || failed=$((failed + 1))
done <<EOF
check-l0-guardrails	$repo_root/scripts/check-l0-guardrails.sh
check-doc-references	$repo_root/scripts/check-doc-references.sh
check-session-checkpoint	$repo_root/scripts/check-session-checkpoint.sh
check-supply-chain	$repo_root/scripts/check-supply-chain.sh
check-l0-generation	$repo_root/scripts/check-l0-generation.sh
check-l0-adversarial	$repo_root/scripts/check-l0-adversarial.sh
check-l0-fixtures	$repo_root/scripts/check-l0-fixtures.sh
EOF

passed="$(awk -F '\t' '$2 == "ok" { c++ } END { print c + 0 }' "$summary_file")"
failed_count="$(awk -F '\t' '$2 == "failed" { c++ } END { print c + 0 }' "$summary_file")"
skipped_count="$(awk -F '\t' '$2 == "skipped" { c++ } END { print c + 0 }' "$summary_file")"
warning_total="$(awk -F '\t' '{ c += $4 } END { print c + 0 }' "$summary_file")"

say "overview:"
say "  passed: $passed"
say "  failed: $failed_count"
say "  skipped: $skipped_count"
say "  warnings: $warning_total"

awk -F '\t' '{
	if ($5 != "") {
		printf("  - %s: %s (%ss, warnings: %s; %s)\n", $1, $2, $3, $4, $5)
		next
	}
	printf("  - %s: %s (%ss, warnings: %s)\n", $1, $2, $3, $4)
}' "$summary_file"

if [ "$failed" -ne 0 ]; then
	exit 1
fi
