#!/bin/sh
# repo_capability:begin
# {
#   "schema_version": 1,
#   "slug": "cargo.operator",
#   "summary": "Run cargo/rustc through the repo's explicit nightly operator contract instead of guessing toolchain state.",
#   "kind": "cargo-wrapper",
#   "when_to_use": "Use for build, test, clippy, fmt, install, and other cargo-driven repo operations when the checked-in nightly operator path should stay authoritative.",
#   "scope": "repo",
#   "lifecycle_state": "canonical",
#   "risk_class": "repo-and-runtime-mutation",
#   "receipt_mode": "observational",
#   "inputs": [
#     {
#       "name": "cargo_args",
#       "kind": "argv",
#       "required": false,
#       "summary": "Arguments forwarded to cargo after the nightly toolchain runner is selected."
#     }
#   ],
#   "outputs": [
#     {
#       "kind": "process-exit",
#       "summary": "Delegated cargo exit status plus the wrapped command's console output."
#     }
#   ],
#   "composition_eligibility": "manual-only",
#   "summary_visibility": "default"
# }
# repo_capability:end
set -eu

TOOLCHAIN="${AK_RUSTUP_TOOLCHAIN:-nightly}"

say() { printf '%s\n' "$*"; }
err() { printf '%s\n' "$*" >&2; }
die() { err "error: $*"; exit 1; }

has_cmd() {
  command -v "$1" >/dev/null 2>&1
}

resolve_rustup() {
  if has_cmd rustup; then
    command -v rustup
    return 0
  fi

  if [ -n "${HOME:-}" ] && [ -x "$HOME/.cargo/bin/rustup" ]; then
    printf '%s\n' "$HOME/.cargo/bin/rustup"
    return 0
  fi

  return 1
}

nightly_available() {
  rustup_bin="$(resolve_rustup 2>/dev/null || true)"
  [ -n "$rustup_bin" ] \
    && "$rustup_bin" run "$TOOLCHAIN" cargo --version >/dev/null 2>&1 \
    && "$rustup_bin" which --toolchain "$TOOLCHAIN" rustc >/dev/null 2>&1 \
    && "$rustup_bin" which --toolchain "$TOOLCHAIN" rustdoc >/dev/null 2>&1
}

tool_path_or_missing() {
  if has_cmd "$1"; then
    command -v "$1"
  else
    printf 'missing\n'
  fi
}

tool_version_or_unknown() {
  if has_cmd "$1"; then
    "$1" --version 2>/dev/null || printf 'unknown\n'
  else
    printf 'missing\n'
  fi
}

path_is_nightly() {
  has_cmd cargo && has_cmd rustc && has_cmd rustdoc \
    && cargo --version 2>/dev/null | grep -qi nightly \
    && rustc --version 2>/dev/null | grep -qi nightly \
    && rustdoc --version 2>/dev/null | grep -qi nightly
}

path_nightly_reason() {
  if ! has_cmd cargo; then
    printf 'cargo is missing on PATH\n'
    return 0
  fi

  if ! has_cmd rustc; then
    printf 'rustc is missing on PATH\n'
    return 0
  fi

  if ! has_cmd rustdoc; then
    printf 'rustdoc is missing on PATH\n'
    return 0
  fi

  cargo_version="$(cargo --version 2>/dev/null || printf 'unknown')"
  if ! printf '%s\n' "$cargo_version" | grep -qi nightly; then
    printf 'cargo on PATH is not nightly (%s)\n' "$cargo_version"
    return 0
  fi

  rustc_version="$(rustc --version 2>/dev/null || printf 'unknown')"
  if ! printf '%s\n' "$rustc_version" | grep -qi nightly; then
    printf 'rustc on PATH is not nightly (%s)\n' "$rustc_version"
    return 0
  fi

  rustdoc_version="$(rustdoc --version 2>/dev/null || printf 'unknown')"
  if ! printf '%s\n' "$rustdoc_version" | grep -qi nightly; then
    printf 'rustdoc on PATH is not nightly (%s)\n' "$rustdoc_version"
    return 0
  fi

  printf 'PATH nightly toolchain is unavailable for an unknown reason\n'
}

usage() {
  cat <<EOF
Canonical cargo launcher for repos whose AK wrapper needs an explicit nightly operator toolchain.

Usage:
  ./scripts/cargo-operator.sh --doctor
  ./scripts/cargo-operator.sh --available
  ./scripts/cargo-operator.sh <cargo args...>

Resolution order:
  1) rustup on PATH
  2) ~/.cargo/bin/rustup fallback
  3) cargo on PATH only when cargo, rustc, and rustdoc already report nightly

This wrapper fails closed rather than silently using a stable cargo/rustc pair.
EOF
}

case "${1:-}" in
  -h|--help)
    usage
    exit 0
    ;;
  --available)
    if nightly_available || path_is_nightly; then
      exit 0
    fi
    exit 1
    ;;
  --doctor)
    say "cargo operator doctor"
    say "- toolchain: $TOOLCHAIN"
    if nightly_available; then
      rustup_bin="$(resolve_rustup)"
      say "- selected runner: rustup run $TOOLCHAIN cargo"
      say "- rustup: $rustup_bin"
      say "- cargo: $($rustup_bin run "$TOOLCHAIN" cargo --version)"
      say "- rustc: $($rustup_bin run "$TOOLCHAIN" rustc --version)"
      say "- rustdoc: $($rustup_bin run "$TOOLCHAIN" rustdoc --version)"
      exit 0
    fi
    if path_is_nightly; then
      say "- selected runner: cargo on PATH"
      say "- cargo path: $(tool_path_or_missing cargo)"
      say "- rustc path: $(tool_path_or_missing rustc)"
      say "- rustdoc path: $(tool_path_or_missing rustdoc)"
      say "- cargo: $(tool_version_or_unknown cargo)"
      say "- rustc: $(tool_version_or_unknown rustc)"
      say "- rustdoc: $(tool_version_or_unknown rustdoc)"
      exit 0
    fi
    say "- selected runner: unavailable"
    say "- cargo path: $(tool_path_or_missing cargo)"
    say "- cargo on PATH: $(tool_version_or_unknown cargo)"
    say "- rustc path: $(tool_path_or_missing rustc)"
    say "- rustc on PATH: $(tool_version_or_unknown rustc)"
    say "- rustdoc path: $(tool_path_or_missing rustdoc)"
    say "- rustdoc on PATH: $(tool_version_or_unknown rustdoc)"
    if rustup_bin="$(resolve_rustup 2>/dev/null || true)" && [ -n "$rustup_bin" ]; then
      say "- rustup: $rustup_bin"
    else
      say "- rustup: missing"
    fi
    say "- path nightly reason: $(path_nightly_reason)"
    exit 1
    ;;
  "")
    usage
    exit 2
    ;;
esac

if nightly_available; then
  rustup_bin="$(resolve_rustup)"
  RUSTC_BIN="$($rustup_bin which --toolchain "$TOOLCHAIN" rustc)"
  RUSTDOC_BIN="$($rustup_bin which --toolchain "$TOOLCHAIN" rustdoc)"
  TOOLCHAIN_BIN_DIR="$(dirname "$RUSTC_BIN")"
  exec env \
    PATH="$TOOLCHAIN_BIN_DIR:$PATH" \
    RUSTUP_TOOLCHAIN="$TOOLCHAIN" \
    RUSTC="$RUSTC_BIN" \
    RUSTDOC="$RUSTDOC_BIN" \
    "$rustup_bin" run "$TOOLCHAIN" cargo "$@"
fi

if path_is_nightly; then
  exec cargo "$@"
fi

reason="$(path_nightly_reason)"
die "this repo's AK wrapper requires an explicit nightly operator cargo; $reason. Install rustup nightly (PATH or ~/.cargo/bin/rustup) or provide nightly cargo/rustc/rustdoc on PATH"
