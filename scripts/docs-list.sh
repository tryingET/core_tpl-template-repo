#!/usr/bin/env sh
set -eu

repo_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
workspace_root="${AI_SOCIETY_WORKSPACE:-$HOME/ai-society}"
quiet_success=0

if [ "${1:-}" = "--quiet-success" ]; then
  quiet_success=1
  shift
fi

contains_help_arg() {
  for arg in "$@"; do
    case "$arg" in
      -h|--help)
        return 0
        ;;
    esac
  done
  return 1
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    echo "error: missing dependency: $1" >&2
    exit 2
  }
}

resolve_override() {
  value="$1"
  [ -n "$value" ] || return 1

  case "$value" in
    /*) candidate="$value" ;;
    *) candidate="$repo_root/$value" ;;
  esac

  [ -f "$candidate" ] || {
    echo "error: docs-list override points to missing file: $candidate" >&2
    exit 2
  }

  printf '%s\n' "$candidate"
  return 0
}

resolve_docs_list_script() {
  if path="$(resolve_override "${DOCS_LIST_SCRIPT:-}" 2>/dev/null)"; then
    printf '%s\n' "$path"
    return 0
  fi

  if path="$(resolve_override "${AGENT_SCRIPTS_DOCS_LIST:-}" 2>/dev/null)"; then
    printf '%s\n' "$path"
    return 0
  fi

  for candidate in \
    "$repo_root/tools/agent-scripts/scripts/docs-list.mjs" \
    "$repo_root/vendor/agent-scripts/scripts/docs-list.mjs" \
    "$workspace_root/core/agent-scripts/scripts/docs-list.mjs"
  do
    if [ -f "$candidate" ]; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done

  return 1
}

need_cmd node

docs_list_script="$(resolve_docs_list_script || true)"
[ -n "$docs_list_script" ] || {
  echo "error: could not resolve docs-list script." >&2
  echo "hint: set DOCS_LIST_SCRIPT or AGENT_SCRIPTS_DOCS_LIST, vendor tools/agent-scripts, or clone $workspace_root/core/agent-scripts." >&2
  exit 2
}

if [ "$quiet_success" -ne 1 ] || contains_help_arg "$@"; then
  exec node "$docs_list_script" "$@"
fi

need_cmd mktemp
output_file="$(mktemp)"
cleanup() {
  rm -f "$output_file"
}
trap cleanup EXIT INT TERM HUP

if node "$docs_list_script" "$@" >"$output_file" 2>&1; then
  cleanup
  trap - EXIT INT TERM HUP
  printf 'ok: docs-list\n'
  exit 0
fi

status=$?
cat "$output_file" >&2
exit "$status"
