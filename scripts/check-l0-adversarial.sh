#!/usr/bin/env sh
set -eu

repo_root="$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)"
cd "$repo_root"

need_cmd() {
	command -v "$1" >/dev/null 2>&1 || {
		echo "error: missing dependency: $1" >&2
		exit 2
	}
}

need_cmd bash
need_cmd find
need_cmd git
need_cmd grep
need_cmd ln
need_cmd mktemp
need_cmd rm
need_cmd tail

answers_lib="$repo_root/scripts/lib/copier-answers.sh"
[ -f "$answers_lib" ] || {
	echo "error: missing dependency: $answers_lib" >&2
	exit 2
}
# shellcheck source=/dev/null
. "$answers_lib"

fail() {
	echo "error: $*" >&2
	exit 1
}

yaml_scalar_value() {
	answers_file="$1"
	key="$2"

	copier_answers_scalar "$answers_file" "$key"
}

render_l1() {
	dest_dir="$1"
	repo_slug="$2"
	company_slug="$3"
	company_name="$4"

	"$repo_root/scripts/new-l1-from-copier.sh" "$dest_dir" \
		-d repo_slug="$repo_slug" \
		-d company_slug="$company_slug" \
		-d company_name="$company_name" \
		-d maintainer_handle=@template-owner \
		--defaults --overwrite >/dev/null
}

init_git_repo() {
	repo_dir="$1"
	commit_message="$2"

	(
		cd "$repo_dir"
		git init -b main >/dev/null
		git config user.name "tpl-template-repo adversarial" >/dev/null
		git config user.email "ci@tpl-template-repo.local" >/dev/null
		git add . >/dev/null
		git commit -m "$commit_message" >/dev/null
	)
}

init_seed_repo() {
	repo_dir="$1"
	commit_message="$2"

	mkdir -p "$repo_dir"
	(
		cd "$repo_dir"
		git init -b main >/dev/null
		git config user.name "tpl-template-repo adversarial" >/dev/null
		git config user.email "ci@tpl-template-repo.local" >/dev/null
		printf 'seed\n' >README.md
		git add README.md >/dev/null
		git commit -m "$commit_message" >/dev/null
	)
}

tmp_root="$(mktemp -d)"
worktree_dir=""
cleanup() {
	if [ -n "$worktree_dir" ]; then
		git worktree remove --force "$worktree_dir" >/dev/null 2>&1 || true
	fi
	rm -rf "$tmp_root"
}
trap cleanup EXIT INT TERM

# 1) Worktree renders must preserve L0 provenance.
expected_l0_sha="$(git -C "$repo_root" rev-parse HEAD)"
worktree_dir="$tmp_root/l0-worktree"
worktree_render="$tmp_root/l1-from-worktree"
git worktree add --detach "$worktree_dir" HEAD >/dev/null
cp "$repo_root/scripts/new-l1-from-copier.sh" "$worktree_dir/scripts/new-l1-from-copier.sh"
(
	cd "$worktree_dir"
	./scripts/new-l1-from-copier.sh "$worktree_render" \
		-d repo_slug=fixture-worktree \
		-d company_slug=fixtureworktree \
		-d company_name="Fixture Worktree" \
		--defaults --overwrite >/dev/null
)
actual_l0_sha="$(yaml_scalar_value "$worktree_render/.copier-answers.yml" l0_source_sha)"
[ "$actual_l0_sha" = "$expected_l0_sha" ] || fail "worktree render must preserve l0_source_sha (expected $expected_l0_sha, got $actual_l0_sha)"
git worktree remove --force "$worktree_dir" >/dev/null
worktree_dir=""

# 2) Adoption preview must compare canonical lane baselines while ignoring nested child repos.
preview_l1="$tmp_root/l1-preview"
render_l1 "$preview_l1" previewco previewco "Preview Co"
init_git_repo "$preview_l1" "initial render"
(
	cd "$preview_l1"
	./scripts/bootstrap-lane-root.sh owned >/dev/null
	git add .gitignore owned >/dev/null
	git commit -m "bootstrap owned lane" >/dev/null
	mkdir -p owned/service-a
	(
		cd owned/service-a
		git init -b main >/dev/null
		printf 'hello\n' >README.md
	)
)
preview_output="$("$repo_root/scripts/preview-l1-diff.sh" "$preview_l1")"
printf '%s\n' "$preview_output" | grep -qF "ok: no diff between rendered L1 and target" || {
	printf '%s\n' "$preview_output" >&2
	fail "preview-l1-diff should stay clean for canonical lane baselines plus nested child repos"
}
printf '%s\n' "$preview_output" | grep -qF "materialized canonical lane-root baselines" || {
	printf '%s\n' "$preview_output" >&2
	fail "preview-l1-diff should materialize canonical lane-root baselines"
}
printf '%s\n' "$preview_output" | grep -qF "ignored nested child repos" || {
	printf '%s\n' "$preview_output" >&2
	fail "preview-l1-diff should report ignored nested child repos"
}
(
	cd "$preview_l1"
	printf '\ntracked lane drift\n' >>owned/README.md
)
drift_output="$("$repo_root/scripts/preview-l1-diff.sh" "$preview_l1" 2>&1 || true)"
printf '%s\n' "$drift_output" | grep -qF "info: differences detected (expected during adoption)" || {
	printf '%s\n' "$drift_output" >&2
	fail "preview-l1-diff should surface tracked lane-root drift"
}
if printf '%s\n' "$drift_output" | grep -qF "ok: no diff between rendered L1 and target"; then
	printf '%s\n' "$drift_output" >&2
	fail "preview-l1-diff must not hide tracked lane-root drift"
fi

# 3) Migration must stay portable when sed -i is unavailable and old template repos live in a worktree.
workspace_root="$tmp_root/workspace"
company_slug="demo"
old_company_dir="$workspace_root/$company_slug"
old_templates_dir="$old_company_dir/${company_slug}-templates"
stage_dir="$workspace_root/${company_slug}-stage"
seed_templates_repo="$tmp_root/${company_slug}-templates-seed"
mkdir -p "$old_company_dir"
render_l1 "$seed_templates_repo" "${company_slug}-templates" "$company_slug" "Demo Co"
init_git_repo "$seed_templates_repo" "initial render"
git -C "$seed_templates_repo" remote add origin git@example.com:demo/demo-templates.git >/dev/null
git -C "$seed_templates_repo" worktree add "$old_templates_dir" >/dev/null
fake_bsd_bin="$tmp_root/fake-bsd-bin"
mkdir -p "$fake_bsd_bin"
cat >"$fake_bsd_bin/sed" <<'EOF'
#!/usr/bin/env sh
if [ "${1:-}" = "-i" ]; then
  echo "error: migrate-l1-structure.sh must not rely on sed -i" >&2
  exit 99
fi
exec /usr/bin/sed "$@"
EOF
chmod +x "$fake_bsd_bin/sed"
if ! AI_SOCIETY_WORKSPACE="$workspace_root" PATH="$fake_bsd_bin:$PATH" bash "$repo_root/scripts/migrate-l1-structure.sh" "$company_slug" "Demo Co" >"$tmp_root/migrate.log" 2>&1; then
	tail -n 200 "$tmp_root/migrate.log" >&2 || true
	fail "migrate-l1-structure.sh should support worktree-backed source repos and remain portable when sed -i is unavailable"
fi
[ -d "$stage_dir" ] || fail "migration should create the staged L1 repo"
stage_repo_slug="$(yaml_scalar_value "$stage_dir/.copier-answers.yml" repo_slug)"
[ "$stage_repo_slug" = "$company_slug" ] || fail "migration should normalize repo_slug to company-root naming (expected $company_slug, got $stage_repo_slug)"
git -C "$stage_dir" rev-parse --git-dir >/dev/null 2>&1 || fail "migration should preserve git history in the staged repo"
stage_head_subject="$(git -C "$stage_dir" log -1 --pretty=%s 2>/dev/null || true)"
[ "$stage_head_subject" = "initial render" ] || fail "migration should preserve source git history in the staged repo"
stage_origin_url="$(git -C "$stage_dir" remote get-url origin 2>/dev/null || true)"
[ "$stage_origin_url" = "git@example.com:demo/demo-templates.git" ] || fail "migration should preserve source remotes instead of cloning a local path (got $stage_origin_url)"

# 4) Repo census fallback must see deep repos and git worktrees in both L0 and rendered descendants.
census_l1="$tmp_root/l1-census"
render_l1 "$census_l1" censusco censusco "Census Co"
project_census_repo="$tmp_root/tpl-project-census"
(
	cd "$census_l1"
	./scripts/new-repo-from-copier.sh tpl-project-repo "$project_census_repo" \
		-d repo_slug=probe-project \
		--defaults --overwrite >/dev/null
)

census_root="$tmp_root/census"
shallow_repo="$census_root/shallow"
deep_repo="$census_root/a/b/c/d/e/f/deep"
worktree_repo="$census_root/worktree"
init_seed_repo "$shallow_repo" "shallow init"
init_seed_repo "$deep_repo" "deep init"
git -C "$shallow_repo" worktree add --detach "$worktree_repo" >/dev/null

root_census_output="$("$repo_root/scripts/preflight-repo-census.sh" "$census_root")"
printf '%s\n' "$root_census_output" | grep -qF "repos: 3" || {
	printf '%s\n' "$root_census_output" >&2
	fail "root preflight-repo-census should count deep repos plus git worktrees"
}
for expected_repo in "$shallow_repo" "$deep_repo" "$worktree_repo"; do
	printf '%s\n' "$root_census_output" | grep -qF "$expected_repo" || {
		printf '%s\n' "$root_census_output" >&2
		fail "root preflight-repo-census should list $expected_repo"
	}
done

generated_census_output="$("$project_census_repo/scripts/preflight-repo-census.sh" "$census_root")"
printf '%s\n' "$generated_census_output" | grep -qF "repos: 3" || {
	printf '%s\n' "$generated_census_output" >&2
	fail "generated preflight-repo-census should count deep repos plus git worktrees"
}
for expected_repo in "$shallow_repo" "$deep_repo" "$worktree_repo"; do
	printf '%s\n' "$generated_census_output" | grep -qF "$expected_repo" || {
		printf '%s\n' "$generated_census_output" >&2
		fail "generated preflight-repo-census should list $expected_repo"
	}
done

# 5) Lane bootstrap should keep _src_path stable across alternate checkout paths.
stable_l1="$tmp_root/l1-stable-src"
render_l1 "$stable_l1" stableco stableco "Stable Co"
init_git_repo "$stable_l1" "initial render"
(
	cd "$stable_l1"
	./scripts/bootstrap-lane-root.sh owned >/dev/null
	git add .gitignore owned >/dev/null
	git commit -m "bootstrap owned lane" >/dev/null
)
stable_link="$tmp_root/l1-stable-link"
ln -s "$stable_l1" "$stable_link"
(
	cd "$stable_link"
	./scripts/bootstrap-lane-root.sh owned >/dev/null
)
stable_src_path="$(yaml_scalar_value "$stable_l1/owned/.copier-answers.yml" _src_path)"
[ "$stable_src_path" = "../copier/tpl-project-repo" ] || fail "lane bootstrap should persist a stable relative _src_path (got $stable_src_path)"
if [ -n "$(git -C "$stable_l1" status --porcelain owned/.copier-answers.yml)" ]; then
	git -C "$stable_l1" status --short owned/.copier-answers.yml >&2 || true
	fail "lane bootstrap should not dirty tracked answers when rerun through a symlinked checkout"
fi

echo "ok: l0 adversarial operator-surface checks"
