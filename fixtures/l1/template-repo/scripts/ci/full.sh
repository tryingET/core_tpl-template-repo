#!/usr/bin/env sh
set -eu

repo_root="$(CDPATH= cd -- "$(dirname -- "$0")/../.." && pwd)"

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

if [ -f "$repo_root/governance/work-items.json" ]; then
  "$repo_root/scripts/ak.sh" work-items check --repo . --path "./governance/work-items.json"
fi

if [ -f "$repo_root/scripts/check-task-scope-snapshots.sh" ]; then
  "$repo_root/scripts/check-task-scope-snapshots.sh"
fi

if [ "$deep" -eq 1 ]; then
  "$repo_root/scripts/check-template-ci.sh"
fi

if [ -x "$repo_root/scripts/rocs.sh" ] && [ -f "$repo_root/ontology/manifest.yaml" ]; then
  "$repo_root/scripts/rocs.sh" version
  "$repo_root/scripts/rocs.sh" validate --repo . --resolve-refs
fi

echo "ok: ci full"
