#!/usr/bin/env sh
set -eu

repo_root="$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)"
AK_CMD="${AK_CMD:-ak}"
cd "$repo_root"

fail() {
  echo "error: $*" >&2
  exit 1
}

deep=0
case "${1:-}" in
  "") ;;
  --deep) deep=1 ;;
  *)
    echo "usage: full.sh [--deep]" >&2
    exit 2
    ;;
esac

"$repo_root/scripts/ci/smoke.sh"

if [ -f "$repo_root/scripts/check-task-scope-snapshots.sh" ]; then
  "$repo_root/scripts/check-task-scope-snapshots.sh"
fi

if [ "$deep" -eq 1 ]; then
  "$repo_root/scripts/check-template-ci.sh"
fi

# ROCS gate: cleanup -> validate -> build (validate before build; never wipe outputs first).
# Outputs land in ontology/dist unless the company sets ROCS_OUTPUT_ROOT (for example in
# local/rocs.env, which scripts/rocs.sh sources; see docs/dev/l1-local-extensions.md).
[ ! -L ontology/manifest.yaml ] || fail "ontology manifest may not be a symlink"
if [ ! -f ontology/manifest.yaml ] && [ "$(git ls-files -s -- ontology 2>/dev/null | cut -c1-6)" = "160000" ]; then
  fail "ontology is not materialized: ontology/ is a declared gitlink without ontology/manifest.yaml"
fi
if [ -f ontology/manifest.yaml ]; then
  [ -x ./scripts/rocs.sh ] || fail "missing executable scripts/rocs.sh (run ./scripts/install-hooks.sh)"
  ./scripts/rocs.sh version
  rocs_ref_mode_args=""
  case "${ROCS_CI_PROFILE:-}" in
  main-strict | branch-ci) rocs_ref_mode_args="--workspace-ref-mode strict" ;;
  esac
  ./scripts/rocs.sh cleanup --repo .
  # shellcheck disable=SC2086
  ./scripts/rocs.sh validate --repo . --resolve-refs $rocs_ref_mode_args
  # shellcheck disable=SC2086
  ./scripts/rocs.sh build --repo . --resolve-refs $rocs_ref_mode_args
fi

# Company-owned extension point (never touched by template refresh).
./scripts/lib/run-local-hook.sh local/ci/full.sh "$@"

echo "ok: ci full"
