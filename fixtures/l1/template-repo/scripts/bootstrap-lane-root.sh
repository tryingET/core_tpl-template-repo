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

Lane names must match: [A-Za-z0-9][A-Za-z0-9._-]*
Reserved L1 control-plane paths (for example docs, scripts, copier,
governance, policy, ontology) cannot be bootstrapped as lanes.
EOF
}

say() { printf '%s\n' "$*"; }
die() {
	printf 'error: %s\n' "$*" >&2
	exit 2
}

need_cmd() {
	command -v "$1" >/dev/null 2>&1 || die "missing dependency: $1"
}

is_enabled() {
	case "$(printf '%s' "${1:-}" | tr '[:upper:]' '[:lower:]')" in
	1 | true | yes | on)
		return 0
		;;
	*)
		return 1
		;;
	esac
}

rewrite_line_matching() {
	file="$1"
	pattern="$2"
	replacement="$3"
	tmp_file="$(mktemp "${TMPDIR:-/tmp}/lane-bootstrap.XXXXXX")"

	awk -v pattern="$pattern" -v replacement="$replacement" '
    !done && $0 ~ pattern {
      print replacement
      done = 1
      next
    }
    { print }
  ' "$file" >"$tmp_file" || {
		rm -f "$tmp_file"
		die "unable to rewrite $file"
	}

	mv "$tmp_file" "$file"
}

drop_yaml_key() {
	file="$1"
	key="$2"
	tmp_file="$(mktemp "${TMPDIR:-/tmp}/lane-bootstrap.XXXXXX")"

	awk -v key="$key" '
    !done && $0 ~ "^[[:space:]]*" key ":[[:space:]]*" {
      done = 1
      next
    }
    { print }
  ' "$file" >"$tmp_file" || {
		rm -f "$tmp_file"
		die "unable to rewrite $file"
	}

	mv "$tmp_file" "$file"
}

yaml_key_present() {
	file="$1"
	key="$2"

	[ -f "$file" ] || return 1
	grep -q "^[[:space:]]*$key:[[:space:]]*" "$file"
}

json_string_value() {
	json_file="$1"
	key="$2"

	[ -f "$json_file" ] || return 1

	awk -v key="$key" '
    BEGIN {
      status = 1
      pattern = "\"" key "\"[[:space:]]*:[[:space:]]*\"[^\"]*\""
    }

    {
      if ($0 !~ pattern) {
        next
      }

      value = $0
      sub("^.*\"" key "\"[[:space:]]*:[[:space:]]*\"", "", value)
      sub("\".*$", "", value)
      print value
      status = 0
      exit
    }

    END {
      exit status
    }
  ' "$json_file"
}

lane_project_owner_handle_from_work_items() {
	lane_path="$1"
	work_items_path="$lane_path/governance/work-items.json"
	owner=""
	owner_status=0

	owner="$(json_string_value "$work_items_path" owner 2>/dev/null)" || owner_status=$?
	case "$owner_status" in
	0)
		printf '%s\n' "$owner"
		return 0
		;;
	1)
		return 1
		;;
	*)
		die "unable to parse owner from $work_items_path"
		;;
	esac
}

need_cmd awk
need_cmd git
need_cmd grep
need_cmd mktemp
need_cmd mv
need_cmd rsync

lane=""
init_lane_git=0

while [ "$#" -gt 0 ]; do
	case "$1" in
	--init-lane-git)
		init_lane_git=1
		;;
	-h | --help)
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

repo_root="$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)"
repo_surface_lib="$repo_root/scripts/lib/repo-surface.sh"
[ -f "$repo_surface_lib" ] || die "missing dependency: $repo_surface_lib"
# shellcheck source=/dev/null
. "$repo_surface_lib"
answers_lib="$repo_root/scripts/lib/copier-answers.sh"
[ -f "$answers_lib" ] || die "missing dependency: $answers_lib"
# shellcheck source=/dev/null
. "$answers_lib"
cd "$repo_root"

if ! repo_surface_lane_name_has_valid_syntax "$lane"; then
	die "lane name must match [A-Za-z0-9][A-Za-z0-9._-]* (got: $lane)"
fi

if ! repo_surface_lane_name_is_bootstrap_allowed "$lane"; then
	die "lane name is reserved for the L1 control plane (got: $lane)"
fi

[ -x "./scripts/new-repo-from-copier.sh" ] || die "missing executable wrapper: scripts/new-repo-from-copier.sh"

lane_dir="$repo_root/$lane"
existing_answers_file="$lane_dir/.copier-answers.yml"
preserve_missing_project_owner_handle=0
render_project_owner_handle="${PROJECT_OWNER_HANDLE:-}"
disable_project_owner_inference=0

if is_enabled "${PRESERVE_MISSING_PROJECT_OWNER_HANDLE:-}"; then
	preserve_missing_project_owner_handle=1
fi

if is_enabled "${DISABLE_PROJECT_OWNER_HANDLE_INFERENCE:-}"; then
	disable_project_owner_inference=1
fi

if [ -z "$render_project_owner_handle" ] && [ "$disable_project_owner_inference" = "0" ] && [ -f "$existing_answers_file" ]; then
	if yaml_key_present "$existing_answers_file" project_owner_handle; then
		owner_status=0
		render_project_owner_handle="$(copier_answers_try_scalar "$existing_answers_file" project_owner_handle 2>/dev/null)" || owner_status=$?
		[ "$owner_status" -eq 0 ] || die "unable to parse project_owner_handle from $existing_answers_file"
	else
		preserve_missing_project_owner_handle=1
	fi
fi

if [ -z "$render_project_owner_handle" ] && [ "$disable_project_owner_inference" = "0" ]; then
	render_project_owner_handle="$(lane_project_owner_handle_from_work_items "$lane_dir" 2>/dev/null || true)"
fi

if [ -z "$render_project_owner_handle" ] && [ "$preserve_missing_project_owner_handle" = "1" ]; then
	disable_project_owner_inference=1
fi

tmp_root="$(mktemp -d)"
trap 'rm -rf "$tmp_root"' EXIT

rendered_lane="$tmp_root/$lane"

if [ -n "$render_project_owner_handle" ]; then
	PROJECT_OWNER_HANDLE="$render_project_owner_handle" ./scripts/new-repo-from-copier.sh tpl-project-repo "$rendered_lane" \
		-d repo_slug="$lane" \
		-d location="$lane" \
		--defaults --overwrite >/dev/null
elif [ "$disable_project_owner_inference" = "1" ]; then
	DISABLE_PROJECT_OWNER_HANDLE_INFERENCE=1 ./scripts/new-repo-from-copier.sh tpl-project-repo "$rendered_lane" \
		-d repo_slug="$lane" \
		-d location="$lane" \
		--defaults --overwrite >/dev/null
else
	./scripts/new-repo-from-copier.sh tpl-project-repo "$rendered_lane" \
		-d repo_slug="$lane" \
		-d location="$lane" \
		--defaults --overwrite >/dev/null
fi

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
lane_src_path="$(repo_surface_lane_root_src_path)"
if [ -f "$answers_file" ]; then
	if grep -q '^_src_path:' "$answers_file"; then
		rewrite_line_matching "$answers_file" '^_src_path:.*$' "_src_path: $lane_src_path"
	else
		printf '_src_path: %s\n' "$lane_src_path" | cat - "$answers_file" >"$answers_file.tmp"
		mv "$answers_file.tmp" "$answers_file"
	fi

	if [ "$preserve_missing_project_owner_handle" = "1" ] && yaml_key_present "$answers_file" project_owner_handle; then
		drop_yaml_key "$answers_file" project_owner_handle
	fi
fi

# Lane-local ignore policy: track only lane baseline, ignore nested child repos by default.
cat >"$lane_dir/.gitignore" <<'EOF'
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

if ! grep -qxF "$lane/*" "$parent_gitignore"; then
	cat >>"$parent_gitignore" <<EOF

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
if ! grep -qxF "!$lane/.gitignore" "$parent_gitignore"; then
	printf '!%s/.gitignore\n' "$lane" >>"$parent_gitignore"
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
