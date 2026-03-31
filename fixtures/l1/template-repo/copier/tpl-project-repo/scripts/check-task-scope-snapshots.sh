#!/usr/bin/env sh
set -eu

repo_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$repo_root"

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "error: missing dependency: $1" >&2
    exit 2
  }
}

need_cmd awk
need_cmd diff
need_cmd find
need_cmd git
need_cmd mktemp
need_cmd sed
need_cmd sort

fail() {
  echo "error: $*" >&2
  exit 1
}

normalize_snapshot() {
  src="$1"
  dst="$2"
  sed '/^[[:space:]]*"exported_at"[[:space:]]*:/d; /^[[:space:]]*"commit_sha"[[:space:]]*:/d' "$src" > "$dst"
}

extract_task_repo() {
  awk '
    /^[[:space:]]*"repo"[[:space:]]*:/ {
      line = $0
      sub(/^[[:space:]]*"repo"[[:space:]]*:[[:space:]]*"/, "", line)
      sub(/".*/, "", line)
      print line
      exit
    }
  ' "$1"
}

[ -x "./scripts/ak.sh" ] || fail "missing executable: ./scripts/ak.sh"

snapshots_dir="./governance/task-scopes"
if [ ! -d "$snapshots_dir" ]; then
  echo "ok: no task-scope snapshots"
  exit 0
fi

snapshot_list="$(find "$snapshots_dir" -type f -name 'AK-*.snapshot.json' | LC_ALL=C sort)"
if [ -z "$snapshot_list" ]; then
  echo "ok: no task-scope snapshots"
  exit 0
fi

tmp_root="$(mktemp -d "${TMPDIR:-/tmp}/ak-task-scopes.XXXXXX")"
cleanup() {
  rm -rf "$tmp_root"
}
trap cleanup EXIT INT TERM

checked=0
while IFS= read -r snapshot_path; do
  [ -n "$snapshot_path" ] || continue
  checked=$((checked + 1))

  snapshot_name="${snapshot_path##*/}"
  task_id="${snapshot_name#AK-}"
  task_id="${task_id%.snapshot.json}"
  case "$task_id" in
    ''|*[!0-9]*)
      fail "task-scope snapshot filename must use a numeric task id: $snapshot_path"
      ;;
  esac

  task_json="$tmp_root/task-$task_id.json"
  if ! ./scripts/ak.sh task show "$task_id" -F json >"$task_json" 2>/dev/null; then
    fail "unable to load AK task $task_id for snapshot $snapshot_path"
  fi

  task_repo="$(extract_task_repo "$task_json")"
  [ -n "$task_repo" ] || fail "unable to extract repo for AK task $task_id"
  [ "$task_repo" = "$repo_root" ] || fail "snapshot $snapshot_path belongs to repo $task_repo, expected $repo_root"

  exported_snapshot="$tmp_root/AK-$task_id.expected.json"
  if ! ./scripts/ak.sh task scope export "$task_id" >"$exported_snapshot"; then
    fail "unable to export AK task scope for task $task_id"
  fi

  actual_normalized="$tmp_root/AK-$task_id.actual.normalized.json"
  expected_normalized="$tmp_root/AK-$task_id.expected.normalized.json"
  normalize_snapshot "$snapshot_path" "$actual_normalized"
  normalize_snapshot "$exported_snapshot" "$expected_normalized"

  if ! diff -u "$expected_normalized" "$actual_normalized" >/dev/null; then
    echo "error: task-scope snapshot drift detected: $snapshot_path" >&2
    diff -u "$expected_normalized" "$actual_normalized" >&2 || true
    echo "hint: refresh with ./scripts/ak.sh task scope export $task_id > governance/task-scopes/AK-$task_id.snapshot.json" >&2
    exit 1
  fi
done <<EOF
$snapshot_list
EOF

echo "ok: task-scope snapshots ($checked checked)"
