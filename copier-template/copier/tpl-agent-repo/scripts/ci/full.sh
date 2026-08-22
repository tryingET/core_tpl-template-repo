#!/bin/sh
set -eu

script_dir="$(cd "$(dirname "$0")" && pwd)"
"$script_dir/smoke.sh"

repo_root="$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "error: not a git repo" >&2; exit 1; }
AK_CMD="${AK_CMD:-ak}"
cd "$repo_root"

if [ -x "./scripts/check-task-scope-snapshots.sh" ]; then
  ./scripts/check-task-scope-snapshots.sh
fi

fi

if [ -x "./scripts/rocs.sh" ] && [ -f "./ontology/manifest.yaml" ]; then
  ./scripts/rocs.sh version
  ./scripts/rocs.sh validate --repo . --resolve-refs
fi
