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

need_cmd awk
need_cmd cp
need_cmd find
need_cmd mkdir
need_cmd mktemp
need_cmd mv
need_cmd rm
need_cmd tail

SYNC_VERBOSE="${SYNC_VERBOSE:-0}"

run_step() {
	if [ "$SYNC_VERBOSE" = "1" ]; then
		"$@"
		return
	fi

	log_file="$(mktemp)"
	if "$@" >"$log_file" 2>&1; then
		rm -f "$log_file"
		return
	fi

	echo "error: command failed: $*" >&2
	echo "--- last 200 lines ---" >&2
	tail -n 200 "$log_file" >&2 || true
	rm -f "$log_file"
	return 1
}

fixture_normalization_lib="$repo_root/scripts/lib/fixture-normalization.sh"
[ -f "$fixture_normalization_lib" ] || {
	echo "error: missing required helper: $fixture_normalization_lib" >&2
	exit 1
}
# shellcheck source=/dev/null
. "$fixture_normalization_lib"

tmp_root="$(mktemp -d)"
trap 'rm -rf "$tmp_root"' EXIT

l1_render="$tmp_root/l1-template-repo"
l2_render_agent="$tmp_root/l2-tpl-agent-repo"
l2_render_org="$tmp_root/l2-tpl-org-repo"
l2_render_project="$tmp_root/l2-tpl-project-repo"
l2_render_monorepo="$tmp_root/l2-tpl-monorepo"
l2_render_package="$tmp_root/l2-tpl-package"
matrix_render_project_python="$tmp_root/matrix-tpl-project-repo-python"
matrix_render_project_node="$tmp_root/matrix-tpl-project-repo-node"
matrix_render_project_typescript="$tmp_root/matrix-tpl-project-repo-typescript"
matrix_render_project_rust="$tmp_root/matrix-tpl-project-repo-rust"
matrix_render_project_elixir="$tmp_root/matrix-tpl-project-repo-elixir"
matrix_render_monorepo="$tmp_root/matrix-tpl-monorepo-root"

run_step "$repo_root/scripts/new-l1-from-copier.sh" "$l1_render" \
	-d repo_slug=fixture-template-repo \
	-d company_slug=holdingco \
	-d company_name="Holding Company" \
	-d maintainer_handle=@template-owner \
	-d l1_org_docs_profile=rich \
	-d enable_community_pack=false \
	-d enable_release_pack=false \
	-d enable_vouch_gate=false \
	--defaults --overwrite

(
	cd "$l1_render"

	# Baseline L2 fixtures (one per template archetype)
	run_step ./scripts/new-repo-from-copier.sh tpl-agent-repo "$l2_render_agent" \
		-d repo_slug=fixture-agent \
		-d enable_community_pack=false \
		-d enable_release_pack=false \
		-d enable_vouch_gate=false \
		--defaults --overwrite

	run_step ./scripts/new-repo-from-copier.sh tpl-org-repo "$l2_render_org" \
		-d repo_slug=fixture-org \
		-d enable_community_pack=false \
		-d enable_release_pack=false \
		-d enable_vouch_gate=false \
		--defaults --overwrite

	run_step ./scripts/new-repo-from-copier.sh tpl-project-repo "$l2_render_project" \
		-d repo_slug=fixture-product-repo \
		-d enable_community_pack=false \
		-d enable_release_pack=false \
		-d enable_vouch_gate=false \
		--defaults --overwrite

	run_step ./scripts/new-repo-from-copier.sh tpl-monorepo "$l2_render_monorepo" \
		-d repo_slug=fixture-monorepo \
		-d package_manager=uv \
		-d enable_community_pack=false \
		-d enable_release_pack=false \
		-d enable_vouch_gate=false \
		--defaults --overwrite

	run_step ./scripts/new-repo-from-copier.sh tpl-package "$l2_render_package" \
		-d package_name=fixture-core \
		-d package_type=library \
		-d language=python \
		--defaults --overwrite

	# Language matrix: tpl-project-repo varies by project language.
	run_step ./scripts/new-repo-from-copier.sh tpl-project-repo "$matrix_render_project_python" \
		-d repo_slug=fixture-project-python \
		-d language=python \
		-d enable_software_pack=true \
		-d enable_community_pack=false \
		-d enable_release_pack=false \
		-d enable_vouch_gate=false \
		--defaults --overwrite

	run_step ./scripts/new-repo-from-copier.sh tpl-project-repo "$matrix_render_project_node" \
		-d repo_slug=fixture-project-node \
		-d language=node \
		-d enable_software_pack=true \
		-d enable_community_pack=false \
		-d enable_release_pack=false \
		-d enable_vouch_gate=false \
		--defaults --overwrite

	run_step ./scripts/new-repo-from-copier.sh tpl-project-repo "$matrix_render_project_typescript" \
		-d repo_slug=fixture-project-typescript \
		-d language=typescript \
		-d enable_software_pack=true \
		-d enable_community_pack=false \
		-d enable_release_pack=false \
		-d enable_vouch_gate=false \
		--defaults --overwrite

	run_step ./scripts/new-repo-from-copier.sh tpl-project-repo "$matrix_render_project_rust" \
		-d repo_slug=fixture-project-rust \
		-d language=rust \
		-d enable_software_pack=true \
		-d enable_community_pack=false \
		-d enable_release_pack=false \
		-d enable_vouch_gate=false \
		--defaults --overwrite

	run_step ./scripts/new-repo-from-copier.sh tpl-project-repo "$matrix_render_project_elixir" \
		-d repo_slug=fixture-project-elixir \
		-d language=elixir \
		-d enable_software_pack=true \
		-d enable_community_pack=false \
		-d enable_release_pack=false \
		-d enable_vouch_gate=false \
		--defaults --overwrite

	# Language matrix: tpl-monorepo varies through member packages, not root archetype.
	run_step ./scripts/new-repo-from-copier.sh tpl-monorepo "$matrix_render_monorepo" \
		-d repo_slug=fixture-monorepo-matrix \
		-d package_manager=uv \
		-d enable_community_pack=false \
		-d enable_release_pack=false \
		-d enable_vouch_gate=false \
		--defaults --overwrite

	run_step ./scripts/new-repo-from-copier.sh tpl-package "$matrix_render_monorepo/packages/fixture-py-core" \
		-d package_name=fixture-py-core \
		-d package_type=library \
		-d language=python \
		--defaults --overwrite

	run_step ./scripts/new-repo-from-copier.sh tpl-package "$matrix_render_monorepo/packages/fixture-ts-core" \
		-d package_name=fixture-ts-core \
		-d package_type=library \
		-d language=typescript \
		--defaults --overwrite

	run_step ./scripts/new-repo-from-copier.sh tpl-package "$matrix_render_monorepo/packages/fixture-rust-core" \
		-d package_name=fixture-rust-core \
		-d package_type=library \
		-d language=rust \
		--defaults --overwrite

	run_step ./scripts/new-repo-from-copier.sh tpl-package "$matrix_render_monorepo/packages/fixture-elixir-core" \
		-d package_name=fixture-elixir-core \
		-d package_type=library \
		-d language=elixir \
		--defaults --overwrite
)

fixtures_root="$repo_root/fixtures"
fixture_l1="$fixtures_root/l1/template-repo"
fixture_l2_agent="$fixtures_root/l2/tpl-agent-repo"
fixture_l2_org="$fixtures_root/l2/tpl-org-repo"
fixture_l2_project="$fixtures_root/l2/tpl-project-repo"
fixture_l2_monorepo="$fixtures_root/l2/tpl-monorepo"
fixture_l2_package="$fixtures_root/l2/tpl-package"
fixture_matrix_root="$fixtures_root/matrix"
fixture_matrix_project_python="$fixture_matrix_root/tpl-project-repo/python"
fixture_matrix_project_node="$fixture_matrix_root/tpl-project-repo/node"
fixture_matrix_project_typescript="$fixture_matrix_root/tpl-project-repo/typescript"
fixture_matrix_project_rust="$fixture_matrix_root/tpl-project-repo/rust"
fixture_matrix_project_elixir="$fixture_matrix_root/tpl-project-repo/elixir"
fixture_matrix_monorepo_root="$fixture_matrix_root/tpl-monorepo/root"

rm -rf \
	"$fixture_l1" \
	"$fixture_l2_agent" \
	"$fixture_l2_org" \
	"$fixture_l2_project" \
	"$fixture_l2_monorepo" \
	"$fixture_l2_package" \
	"$fixture_matrix_root"
mkdir -p \
	"$fixture_l1" \
	"$fixture_l2_agent" \
	"$fixture_l2_org" \
	"$fixture_l2_project" \
	"$fixture_l2_monorepo" \
	"$fixture_l2_package" \
	"$fixture_matrix_project_python" \
	"$fixture_matrix_project_node" \
	"$fixture_matrix_project_typescript" \
	"$fixture_matrix_project_rust" \
	"$fixture_matrix_project_elixir" \
	"$fixture_matrix_monorepo_root"

cp -R "$l1_render/." "$fixture_l1/"
cp -R "$l2_render_agent/." "$fixture_l2_agent/"
cp -R "$l2_render_org/." "$fixture_l2_org/"
cp -R "$l2_render_project/." "$fixture_l2_project/"
cp -R "$l2_render_monorepo/." "$fixture_l2_monorepo/"
cp -R "$l2_render_package/." "$fixture_l2_package/"
cp -R "$matrix_render_project_python/." "$fixture_matrix_project_python/"
cp -R "$matrix_render_project_node/." "$fixture_matrix_project_node/"
cp -R "$matrix_render_project_typescript/." "$fixture_matrix_project_typescript/"
cp -R "$matrix_render_project_rust/." "$fixture_matrix_project_rust/"
cp -R "$matrix_render_project_elixir/." "$fixture_matrix_project_elixir/"
cp -R "$matrix_render_monorepo/." "$fixture_matrix_monorepo_root/"

normalize_fixture_tree_volatiles "$fixture_l1"
normalize_fixture_tree_volatiles "$fixture_l2_agent"
normalize_fixture_tree_volatiles "$fixture_l2_org"
normalize_fixture_tree_volatiles "$fixture_l2_project"
normalize_fixture_tree_volatiles "$fixture_l2_monorepo"
normalize_fixture_tree_volatiles "$fixture_l2_package"
normalize_fixture_tree_volatiles "$fixture_matrix_root"

echo "ok: fixtures synchronized"
echo "  - $fixture_l1"
echo "  - $fixture_l2_agent"
echo "  - $fixture_l2_org"
echo "  - $fixture_l2_project"
echo "  - $fixture_l2_monorepo"
echo "  - $fixture_l2_package"
echo "  - $fixture_matrix_project_python"
echo "  - $fixture_matrix_project_node"
echo "  - $fixture_matrix_project_typescript"
echo "  - $fixture_matrix_project_rust"
echo "  - $fixture_matrix_project_elixir"
echo "  - $fixture_matrix_monorepo_root"
