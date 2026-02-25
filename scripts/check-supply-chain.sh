#!/usr/bin/env sh
set -eu

repo_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$repo_root"

fail() {
  echo "error: $*" >&2
  exit 1
}

assert_file() {
  path="$1"
  [ -f "$path" ] || fail "missing file: $path"
}

assert_contains() {
  path="$1"
  needle="$2"
  label="$3"
  grep -qF -- "$needle" "$path" || fail "$label (missing '$needle' in $path)"
}

assert_not_contains() {
  path="$1"
  needle="$2"
  label="$3"
  if grep -qF -- "$needle" "$path"; then
    fail "$label (unexpected '$needle' in $path)"
  fi
}

assert_line_precedes() {
  path="$1"
  first="$2"
  second="$3"
  label="$4"

  first_line="$(grep -nF -- "$first" "$path" | awk -F ':' 'NR == 1 { print $1 }')"
  second_line="$(grep -nF -- "$second" "$path" | awk -F ':' 'NR == 1 { print $1 }')"

  [ -n "$first_line" ] || fail "$label (missing '$first' in $path)"
  [ -n "$second_line" ] || fail "$label (missing '$second' in $path)"
  [ "$first_line" -lt "$second_line" ] || fail "$label (expected '$first' before '$second' in $path)"
}

assert_file "scripts/new-l1-from-copier.sh"
assert_file "copier-template/scripts/new-repo-from-copier.sh"
assert_file ".github/workflows/l0-check.yml"
assert_file "docs/supply-chain-policy.md"

expected_pin='COPIER_VERSION="${COPIER_VERSION:-9.11.1}"'
assert_contains "scripts/new-l1-from-copier.sh" "$expected_pin" "L0 copier wrapper must pin Copier version"
assert_contains "copier-template/scripts/new-repo-from-copier.sh" "$expected_pin" "L1 copier wrapper must pin Copier version"

expected_uvx='uvx --from "copier==${COPIER_VERSION}" copier'
expected_uvtool='uv tool run --from "copier==${COPIER_VERSION}" copier'
assert_contains "scripts/new-l1-from-copier.sh" "$expected_uvx" "L0 copier wrapper must use pinned uvx invocation"
assert_contains "scripts/new-l1-from-copier.sh" "$expected_uvtool" "L0 copier wrapper must use pinned uv tool invocation"
assert_contains "copier-template/scripts/new-repo-from-copier.sh" "$expected_uvx" "L1 copier wrapper must use pinned uvx invocation"
assert_contains "copier-template/scripts/new-repo-from-copier.sh" "$expected_uvtool" "L1 copier wrapper must use pinned uv tool invocation"

assert_not_contains "scripts/new-l1-from-copier.sh" "uvx copier" "L0 copier wrapper must not call unpinned uvx copier"
assert_not_contains "copier-template/scripts/new-repo-from-copier.sh" "uvx copier" "L1 copier wrapper must not call unpinned uvx copier"

uvx_guard='if command -v uvx >/dev/null 2>&1; then'
uv_guard='if command -v uv >/dev/null 2>&1; then'
copier_guard='if command -v copier >/dev/null 2>&1; then'

assert_line_precedes "scripts/new-l1-from-copier.sh" "$uvx_guard" "$uv_guard" "L0 copier wrapper must prefer uvx before uv tool run"
assert_line_precedes "scripts/new-l1-from-copier.sh" "$uv_guard" "$copier_guard" "L0 copier wrapper must prefer pinned runtimes before unpinned copier"
assert_line_precedes "copier-template/scripts/new-repo-from-copier.sh" "$uvx_guard" "$uv_guard" "L1 copier wrapper must prefer uvx before uv tool run"
assert_line_precedes "copier-template/scripts/new-repo-from-copier.sh" "$uv_guard" "$copier_guard" "L1 copier wrapper must prefer pinned runtimes before unpinned copier"

fallback_warning='warning: uvx/uv not found; falling back to unpinned copier on PATH'
assert_contains "scripts/new-l1-from-copier.sh" "$fallback_warning" "L0 copier wrapper must surface unpinned fallback warning"
assert_contains "copier-template/scripts/new-repo-from-copier.sh" "$fallback_warning" "L1 copier wrapper must surface unpinned fallback warning"

assert_contains ".github/workflows/l0-check.yml" "setup-uv" "L0 CI must provision uv"
assert_contains ".github/workflows/l0-check.yml" "bash ./scripts/check-l0.sh" "L0 CI must run full L0 checks"

echo "ok: supply-chain checks"
