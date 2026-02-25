#!/usr/bin/env sh
set -eu

usage() {
  cat <<'EOF' >&2
usage: new-repo-from-copier.sh <template-name> <dest-dir> [copier args...]

Templates:
  tpl-agent-repo       AI agent repositories (personas, learnings, activities)
  tpl-org-repo         Organization handbooks (governance, policies)
  tpl-project-repo     Project repositories (products, services)
  tpl-individual-repo  Individual repositories (personal execution lanes)

Example:
  ./scripts/new-repo-from-copier.sh tpl-agent-repo /tmp/my-agent \
    -d repo_slug=my-agent --defaults --overwrite

  ./scripts/new-repo-from-copier.sh tpl-project-repo /tmp/my-product \
    -d repo_slug=my-product --defaults --overwrite

  ./scripts/new-repo-from-copier.sh tpl-individual-repo /tmp/my-individual \
    -d repo_slug=my-individual --defaults --overwrite

Notes:
  - Copier is pinned by default via COPIER_VERSION (default: 9.11.1).
  - Wrapper runs Copier in quiet mode by default; set `COPIER_QUIET=0` to show Copier progress logs.
  - `enable_vouch_gate`, `enable_community_pack`, and `enable_release_pack`
    are inherited from this L1 repo `.copier-answers.yml` unless overridden.
  - `template_source_sha` is auto-injected from this L1 git HEAD unless
    overridden with `-d template_source_sha=<git-sha>`.
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
  if command -v copier >/dev/null 2>&1; then
    PYTHONWARNINGS="$pythonwarnings" copier "$@"
    return
  fi
  if command -v uv >/dev/null 2>&1; then
    PYTHONWARNINGS="$pythonwarnings" uv tool run --from "copier==${COPIER_VERSION}" copier "$@"
    return
  fi
  echo "error: missing dependency: copier (or uvx/uv)" >&2
  exit 2
}

template_name="${1:-}"
dest_dir="${2:-}"
shift 2 2>/dev/null || true

if [ -z "$template_name" ] || [ -z "$dest_dir" ]; then
  usage
  exit 2
fi

case "$template_name" in
  tpl-agent-repo|tpl-org-repo|tpl-project-repo|tpl-individual-repo)
    # Valid archetype template
    ;;
  *)
    echo "error: unknown template: $template_name" >&2
    echo "hint: available templates: tpl-agent-repo, tpl-org-repo, tpl-project-repo, tpl-individual-repo" >&2
    exit 2
    ;;
esac

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

has_data_override() {
  key="$1"
  shift

  expect_data_value=0
  for arg in "$@"; do
    if [ "$expect_data_value" = "1" ]; then
      case "$arg" in
        "$key="*) return 0 ;;
      esac
      expect_data_value=0
      continue
    fi

    case "$arg" in
      -d|--data)
        expect_data_value=1
        ;;
      -d"$key="*|--data="$key="*)
        return 0
        ;;
    esac
  done

  return 1
}

read_inherited_value() {
  answers_file="$1"
  key="$2"

  [ -f "$answers_file" ] || return 1

  awk -F':' -v key="$key" '
    $1 ~ "^" key "$" {
      v=$2
      gsub(/[ \t"]/, "", v)
      gsub(/\047/, "", v)
      print tolower(v)
      exit
    }
  ' "$answers_file"
}

repo_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
answers_file="$repo_root/.copier-answers.yml"

for key in enable_vouch_gate enable_community_pack enable_release_pack; do
  if has_data_override "$key" "$@"; then
    continue
  fi

  inherited_value="$(read_inherited_value "$answers_file" "$key" || true)"
  case "$inherited_value" in
    true|false)
      set -- -d "$key=$inherited_value" "$@"
      ;;
  esac
done

if ! has_data_override org_docs_profile "$@"; then
  inherited_org_profile="$(read_inherited_value "$answers_file" l2_org_docs_default || true)"
  case "$inherited_org_profile" in
    compact|rich)
      set -- -d "org_docs_profile=$inherited_org_profile" "$@"
      ;;
  esac
fi

if ! has_data_override template_source_sha "$@"; then
  template_source_sha="$(git -C "$repo_root" rev-parse HEAD 2>/dev/null || true)"
  [ -n "$template_source_sha" ] || template_source_sha="unknown"
  set -- -d "template_source_sha=$template_source_sha" "$@"
fi

template_dir="$repo_root/copier/$template_name"

[ -d "$template_dir" ] || {
  echo "error: missing copier template: $template_dir" >&2
  exit 2
}

if ! has_vcs_ref_override "$@"; then
  if git -C "$template_dir" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    set -- -r "$COPIER_VCS_REF" "$@"
  fi
fi

if is_enabled "$COPIER_QUIET" && ! has_quiet_override "$@"; then
  set -- --quiet "$@"
fi

run_copier copy --trust "$@" "$template_dir" "$dest_dir"
