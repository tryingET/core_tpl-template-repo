#!/usr/bin/env sh
set -eu

repo_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
workspace_root="${AI_SOCIETY_WORKSPACE:-$HOME/ai-society}"

resolve_override() {
  value="$1"
  [ -n "$value" ] || return 1

  case "$value" in
    /*) candidate="$value" ;;
    *) candidate="$repo_root/$value" ;;
  esac

  [ -f "$candidate" ] || {
    echo "error: docs-ref-check override points to missing file: $candidate" >&2
    exit 2
  }

  printf '%s\n' "$candidate"
  return 0
}

resolve_checker() {
  if path="$(resolve_override "${DOC_REF_CHECK_SCRIPT:-}" 2>/dev/null)"; then
    printf '%s\n' "$path"
    return 0
  fi

  if path="$(resolve_override "${AGENT_SCRIPTS_DOC_REF_CHECK:-}" 2>/dev/null)"; then
    printf '%s\n' "$path"
    return 0
  fi

  for candidate in \
    "$repo_root/tools/agent-scripts/scripts/docs-ref-check.mjs" \
    "$repo_root/vendor/agent-scripts/scripts/docs-ref-check.mjs" \
    "$workspace_root/core/agent-scripts/scripts/docs-ref-check.mjs"
  do
    if [ -f "$candidate" ]; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done

  return 1
}

checker="$(resolve_checker || true)"
[ -n "$checker" ] || {
  echo "error: could not resolve docs-ref-check script." >&2
  echo "hint: set DOC_REF_CHECK_SCRIPT or AGENT_SCRIPTS_DOC_REF_CHECK, vendor tools/agent-scripts, or clone $workspace_root/core/agent-scripts." >&2
  exit 2
}

if [ "$#" -gt 0 ]; then
  exec node "$checker" --require-tracked "$@"
fi

exec node "$checker" --require-tracked \
  --path "$repo_root/README.md" \
  --path "$repo_root/docs/dev/README.md" \
  --path "$repo_root/docs/l1-adoption-playbook.md" \
  --path "$repo_root/docs/l2-transition-playbook.md"
