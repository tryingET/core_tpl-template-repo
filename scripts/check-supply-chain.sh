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

assert_contains ".github/workflows/l0-check.yml" "setup-uv" "L0 CI must provision uv"
assert_contains ".github/workflows/l0-check.yml" "bash ./scripts/check-l0.sh" "L0 CI must run full L0 checks"

echo "ok: supply-chain checks"
