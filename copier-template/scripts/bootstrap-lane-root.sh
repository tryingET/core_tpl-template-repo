#!/usr/bin/env sh
set -eu

usage() {
  cat <<'EOF' >&2
usage: bootstrap-lane-root.sh <lane-name> [--init-lane-git]

Create/refresh a lane-root baseline (project-template control plane) while
keeping nested child repositories ignored by lane-local .gitignore.

Two-phase workflow (recommended):
  1) Materialize lane baseline in parent repo
  2) Commit parent repo changes
  3) Initialize lane-root git repo with an initial baseline commit

Examples:
  ./scripts/bootstrap-lane-root.sh owned
  git add .gitignore owned
  git commit -m "chore: bootstrap owned lane baseline"
  ./scripts/bootstrap-lane-root.sh owned --init-lane-git

  # Custom lane
  ./scripts/bootstrap-lane-root.sh data
  git add .gitignore data
  git commit -m "chore: bootstrap data lane baseline"
  ./scripts/bootstrap-lane-root.sh data --init-lane-git
EOF
}

say() { printf '%s\n' "$*"; }
die() { printf 'error: %s\n' "$*" >&2; exit 2; }

need_cmd() {
  command -v "$1" >/dev/null 2>&1 || die "missing dependency: $1"
}

need_cmd git
need_cmd grep
need_cmd mktemp
need_cmd rsync
need_cmd sed

lane=""
init_lane_git=0

while [ "$#" -gt 0 ]; do
  case "$1" in
    --init-lane-git)
      init_lane_git=1
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      if [ -z "$lane" ]; then
        lane="$1"
      else
        die "unexpected argument: $1"
      fi
      ;;
  esac
  shift
done

[ -n "$lane" ] || {
  usage
  exit 2
}

case "$lane" in
  */*|.|..)
    die "lane name must be a single path segment (got: $lane)"
    ;;
esac

repo_root="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$repo_root"

[ -x "./scripts/new-repo-from-copier.sh" ] || die "missing executable wrapper: scripts/new-repo-from-copier.sh"

lane_dir="$repo_root/$lane"
tmp_root="$(mktemp -d)"
trap 'rm -rf "$tmp_root"' EXIT

rendered_lane="$tmp_root/$lane"

./scripts/new-repo-from-copier.sh tpl-project-repo "$rendered_lane" \
  -d repo_slug="$lane" \
  --defaults --overwrite >/dev/null

mkdir -p "$lane_dir"

# Overlay project-template control plane while preserving any existing child repos.
rsync -a "$rendered_lane/" "$lane_dir/" \
  --exclude '.git' \
  --exclude '.gitignore' \
  --exclude '.gitlab' \
  --exclude '.gitlab-ci.yml' \
  --exclude 'gitlab'

# Lane roots should not carry GitLab surface.
rm -rf "$lane_dir/.gitlab" "$lane_dir/gitlab"
rm -f "$lane_dir/.gitlab-ci.yml"

# Normalize copier-chain metadata for lane-root baseline.
answers_file="$lane_dir/.copier-answers.yml"
if [ -f "$answers_file" ]; then
  if grep -q '^_src_path:' "$answers_file"; then
    sed -i "s|^_src_path:.*|_src_path: $repo_root/copier/tpl-project-repo|" "$answers_file"
  else
    printf '_src_path: %s/copier/tpl-project-repo\n' "$repo_root" | cat - "$answers_file" > "$answers_file.tmp"
    mv "$answers_file.tmp" "$answers_file"
  fi

  if grep -q '^location:' "$answers_file"; then
    sed -i "s|^location:.*|location: $lane|" "$answers_file"
  else
    printf '\nlocation: %s\n' "$lane" >> "$answers_file"
  fi
fi

readme_file="$lane_dir/README.md"
if [ -f "$readme_file" ]; then
  sed -i "s|\*\*Location\*\*: .*|**Location**: $lane|" "$readme_file" || true
fi

# Lane-local ignore policy: track only lane baseline, ignore nested child repos by default.
cat > "$lane_dir/.gitignore" <<'EOF'
# Track lane baseline only.
# Ignore child repositories and ad-hoc lane entries by default.
*
!.gitignore
!.copier-answers.yml
!AGENTS.md
!CODEOWNERS
!README.md
!next_session_prompt.md
!diary/
!diary/**
!docs/
!docs/**
!governance/
!governance/**
!ontology/
!ontology/**
!policy/
!policy/**
!scripts/
!scripts/**
!src/
!src/**
!tests/
!tests/**
!tools/
!tools/**
EOF

parent_gitignore="$repo_root/.gitignore"
if [ ! -f "$parent_gitignore" ]; then
  die "missing parent .gitignore: $parent_gitignore"
fi

if ! grep -q "^$lane/\\*$" "$parent_gitignore"; then
  cat >> "$parent_gitignore" <<EOF

# Lane root: $lane
# Track lane baseline only; ignore nested child repositories by default.
$lane/*
!$lane/.gitignore
!$lane/.copier-answers.yml
!$lane/AGENTS.md
!$lane/CODEOWNERS
!$lane/README.md
!$lane/next_session_prompt.md
!$lane/diary/
!$lane/diary/**
!$lane/docs/
!$lane/docs/**
!$lane/governance/
!$lane/governance/**
!$lane/ontology/
!$lane/ontology/**
!$lane/policy/
!$lane/policy/**
!$lane/scripts/
!$lane/scripts/**
!$lane/src/
!$lane/src/**
!$lane/tests/
!$lane/tests/**
!$lane/tools/
!$lane/tools/**
# End lane root: $lane
EOF
fi

# Ensure lane .gitignore is unignored in parent policy (older lane blocks may miss this).
if ! grep -q "^!$lane/\\.gitignore$" "$parent_gitignore"; then
  printf '!%s/.gitignore\n' "$lane" >> "$parent_gitignore"
fi

if [ "$init_lane_git" = "1" ]; then
  if ! git -C "$repo_root" ls-files --error-unmatch "$lane/.gitignore" >/dev/null 2>&1; then
    die "parent repo does not track $lane/.gitignore yet. Commit lane baseline in parent first, then rerun with --init-lane-git"
  fi

  if [ ! -d "$lane_dir/.git" ]; then
    git -C "$lane_dir" init -b main >/dev/null 2>&1 || git -C "$lane_dir" init >/dev/null 2>&1
  fi

  if ! git -C "$lane_dir" rev-parse --verify HEAD >/dev/null 2>&1; then
    git -C "$lane_dir" config user.name >/dev/null 2>&1 || git -C "$lane_dir" config user.name "lane-bootstrap bot"
    git -C "$lane_dir" config user.email >/dev/null 2>&1 || git -C "$lane_dir" config user.email "lane-bootstrap@local"

    git -C "$lane_dir" add .
    if [ -n "$(git -C "$lane_dir" status --porcelain)" ]; then
      git -C "$lane_dir" commit -m "chore: initialize $lane lane baseline" >/dev/null
    fi
  fi

  say "ok: lane root git initialized: $lane_dir"
  say "ok: nested child repos remain ignored by $lane/.gitignore"
  exit 0
fi

say "ok: lane baseline materialized: $lane_dir"
say "next (parent repo):"
say "  git add .gitignore $lane"
say "  git commit -m \"chore: bootstrap $lane lane baseline\""
say "then initialize lane root git:"
say "  ./scripts/bootstrap-lane-root.sh $lane --init-lane-git"
