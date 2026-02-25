#!/usr/bin/env sh
set -eu

usage() {
  cat <<'EOF' >&2
usage: new-l1-from-copier.sh <dest-dir> [copier args...]

Example:
  ./scripts/new-l1-from-copier.sh /tmp/holdingco-templates \
    -d repo_slug=holdingco-templates \
    -d l1_org_docs_profile=rich \
    -d enable_community_pack=false \
    -d enable_release_pack=false \
    -d enable_vouch_gate=false \
    --defaults --overwrite

Notes:
  - Generates L1 with all embedded templates:
    - copier/tpl-agent-repo/      (AI agent repos)
    - copier/tpl-org-repo/        (Organization handbooks)
    - copier/tpl-project-repo/    (Project repos)
    - copier/tpl-individual-repo/ (Individual repos)
  - Copier is pinned by default via COPIER_VERSION (default: 9.11.1).
  - Wrapper runs Copier in quiet mode by default; set `COPIER_QUIET=0` to show Copier progress logs.
  - Set `-d l1_org_docs_profile=rich|compact` to choose L1 org docs depth.
  - Set `-d enable_community_pack=true` for public/community-facing collaboration intake.
  - Set `-d enable_release_pack=true` for release-please/publish automation baseline.
  - Set `-d enable_vouch_gate=true` for trust-gated/public contribution templates.
EOF
}

COPIER_VERSION="${COPIER_VERSION:-9.11.1}"
COPIER_WARN_FILTER="${COPIER_WARN_FILTER:-ignore:Dirty template changes included automatically.:Warning}"
COPIER_VCS_REF="${COPIER_VCS_REF:-HEAD}"
COPIER_QUIET="${COPIER_QUIET:-1}"

run_copier() {
  pythonwarnings="$COPIER_WARN_FILTER"
  if [ -n "${PYTHONWARNINGS:-}" ]; then
    pythonwarnings="$pythonwarnings,${PYTHONWARNINGS}"
  fi

  if command -v uvx >/dev/null 2>&1; then
    PYTHONWARNINGS="$pythonwarnings" uvx --from "copier==${COPIER_VERSION}" copier "$@"
    return
  fi
  if command -v uv >/dev/null 2>&1; then
    PYTHONWARNINGS="$pythonwarnings" uv tool run --from "copier==${COPIER_VERSION}" copier "$@"
    return
  fi
  if command -v copier >/dev/null 2>&1; then
    echo "warning: uvx/uv not found; falling back to unpinned copier on PATH" >&2
    PYTHONWARNINGS="$pythonwarnings" copier "$@"
    return
  fi
  echo "error: missing dependency: copier (or uvx/uv)" >&2
  exit 2
}

dest_dir="${1:-}"
shift 1 2>/dev/null || true

if [ -z "$dest_dir" ]; then
  usage
  exit 2
fi

have_answers=0
for arg in "$@"; do
  case "$arg" in
    -a|--answers-file|--answers-file=*) have_answers=1; break ;;
  esac
done

if [ "$have_answers" = "0" ]; then
  set -- -a .copier-answers.yml "$@"
fi

has_vcs_ref_override() {
  expect_ref_value=0
  for arg in "$@"; do
    if [ "$expect_ref_value" = "1" ]; then
      return 0
    fi

    case "$arg" in
      -r|--vcs-ref)
        expect_ref_value=1
        ;;
      -r*|--vcs-ref=*)
        return 0
        ;;
    esac
  done

  return 1
}

has_quiet_override() {
  for arg in "$@"; do
    case "$arg" in
      -q|--quiet)
        return 0
        ;;
    esac
  done

  return 1
}

is_enabled() {
  case "$(printf '%s' "${1:-}" | tr '[:upper:]' '[:lower:]')" in
    1|true|yes|on)
      return 0
      ;;
    *)
      return 1
      ;;
  esac
}

repo_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"

# Inject L0 source SHA for provenance tracking
l0_sha="unknown"
if [ -d "$repo_root/.git" ]; then
  l0_sha="$(git -C "$repo_root" rev-parse HEAD 2>/dev/null || echo unknown)"
fi

if ! has_vcs_ref_override "$@"; then
  if git -C "$repo_root" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    set -- -r "$COPIER_VCS_REF" "$@"
  fi
fi

if is_enabled "$COPIER_QUIET" && ! has_quiet_override "$@"; then
  set -- --quiet "$@"
fi

run_copier copy --trust -d l0_source_sha="$l0_sha" "$@" "$repo_root" "$dest_dir"
