#!/bin/sh
set -eu

say() { printf '%s\n' "$*"; }
err() { printf '%s\n' "$*" >&2; }

script_dir="$(cd "$(dirname "$0")" && pwd)"
repo_root="$(git rev-parse --show-toplevel 2>/dev/null)" || { echo "error: not a git repo" >&2; exit 1; }
cd "$repo_root"

say "==> fast"
"$script_dir/fast.sh"

log_dir="$(mktemp -d "${TMPDIR:-/tmp}/tpl-project-full.XXXXXX")"
cleanup() {
  rm -rf "$log_dir"
}
trap cleanup EXIT INT TERM

run_work_items() {
  if [ -f "./governance/work-items.json" ]; then
    ./scripts/ak.sh work-items check --repo . --path "./governance/work-items.json"
  fi
}

run_task_scope_snapshots() {
  if [ -x "./scripts/check-task-scope-snapshots.sh" ]; then
    ./scripts/check-task-scope-snapshots.sh
  fi
}

run_rocs() {
  if [ -x "./scripts/rocs.sh" ] && [ -f "./ontology/manifest.yaml" ]; then
    ./scripts/rocs.sh version
    ./scripts/rocs.sh build --repo . --resolve-refs --clean
    ./scripts/rocs.sh validate --repo . --resolve-refs
  fi
}

say "==> work-items + task-scope snapshots + rocs (parallel when they apply)"
(
  run_work_items >"$log_dir/work-items.log" 2>&1
) &
work_items_pid=$!
(
  run_task_scope_snapshots >"$log_dir/task-scopes.log" 2>&1
) &
task_scopes_pid=$!
(
  run_rocs >"$log_dir/rocs.log" 2>&1
) &
rocs_pid=$!

work_items_status=0
task_scopes_status=0
rocs_status=0
if wait "$work_items_pid"; then
  work_items_status=0
else
  work_items_status=$?
fi
if wait "$task_scopes_pid"; then
  task_scopes_status=0
else
  task_scopes_status=$?
fi
if wait "$rocs_pid"; then
  rocs_status=0
else
  rocs_status=$?
fi

say "--- work-items output ---"
cat "$log_dir/work-items.log"
say "--- task-scope output ---"
cat "$log_dir/task-scopes.log"
say "--- rocs output ---"
cat "$log_dir/rocs.log"

if [ "$work_items_status" -ne 0 ] || [ "$task_scopes_status" -ne 0 ] || [ "$rocs_status" -ne 0 ]; then
  err "error: full.sh failed"
  [ "$work_items_status" -eq 0 ] || err "- work-items exit=$work_items_status"
  [ "$task_scopes_status" -eq 0 ] || err "- task-scope snapshots exit=$task_scopes_status"
  [ "$rocs_status" -eq 0 ] || err "- rocs exit=$rocs_status"
  exit 1
fi

say "ok: full"
