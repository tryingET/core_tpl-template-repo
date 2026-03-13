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

need_cmd cp
need_cmd git
need_cmd grep
need_cmd mktemp

"$repo_root/scripts/check-l0-guardrails.sh"

tmp_root="$(mktemp -d)"
trap 'rm -rf "$tmp_root"' EXIT

render_l1_case() {
  case_name="$1"
  enable_community_pack="$2"
  enable_release_pack="$3"
  enable_vouch_gate="$4"
  l1_org_docs_profile="$5"
  l1_dir="$tmp_root/$case_name"

  "$repo_root/scripts/new-l1-from-copier.sh" "$l1_dir" \
    -d repo_slug="$case_name" \
    -d maintainer_handle=@template-owner \
    -d l1_org_docs_profile="$l1_org_docs_profile" \
    -d enable_community_pack="$enable_community_pack" \
    -d enable_release_pack="$enable_release_pack" \
    -d enable_vouch_gate="$enable_vouch_gate" \
    --defaults --overwrite >/dev/null

  (
    cd "$l1_dir"
    git init -b main >/dev/null
    git config user.name "tpl-template-repo ci" >/dev/null
    git config user.email "ci@tpl-template-repo.local" >/dev/null
    ./scripts/install-hooks.sh >/dev/null
    ./scripts/ci/smoke.sh >/dev/null
    ./scripts/check-template-ci.sh
    git add .
    git commit -m "initial render ($case_name)" >/dev/null
  )

  "$repo_root/scripts/new-l1-from-copier.sh" "$l1_dir" \
    -d repo_slug="$case_name" \
    -d maintainer_handle=@template-owner \
    -d l1_org_docs_profile="$l1_org_docs_profile" \
    -d enable_community_pack="$enable_community_pack" \
    -d enable_release_pack="$enable_release_pack" \
    -d enable_vouch_gate="$enable_vouch_gate" \
    --defaults --overwrite >/dev/null

  (
    cd "$l1_dir"
    if [ -n "$(git status --porcelain)" ]; then
      echo "error: non-idempotent L0 -> L1 generation ($case_name)" >&2
      git status --short >&2
      exit 1
    fi
  )

  if [ "$case_name" = "l1-template-sample" ]; then
    preview_target="$tmp_root/l1-preview-target"
    "$repo_root/scripts/new-l1-from-copier.sh" "$preview_target" \
      -d repo_slug="$case_name" \
      --defaults --overwrite >/dev/null

    alias_target="$tmp_root/l1-preview-alias"
    rm -rf "$alias_target"
    cp -R "$preview_target" "$alias_target"

    preview_output="$("$repo_root/scripts/preview-l1-diff.sh" "$alias_target")"
    printf '%s\n' "$preview_output" | grep -qF "ok: no diff between rendered L1 and target" || {
      echo "error: preview-l1-diff did not produce clean no-diff output for sample alias target" >&2
      printf '%s\n' "$preview_output" >&2
      exit 1
    }
  fi

  if [ "$case_name" = "l1-template-release" ]; then
    preview_output="$("$repo_root/scripts/preview-l1-diff.sh" "$l1_dir")"
    printf '%s\n' "$preview_output" | grep -qF "ok: no diff between rendered L1 and target" || {
      echo "error: preview-l1-diff did not preserve non-default profile settings for release case" >&2
      printf '%s\n' "$preview_output" >&2
      exit 1
    }
  fi
}

render_l1_case "l1-template-sample" false false false rich
render_l1_case "l1-template-community" true false false rich
render_l1_case "l1-template-release" false true false rich
render_l1_case "l1-template-vouch" false false true rich
render_l1_case "l1-template-compact-org" false false false compact

# Regression check: inherited string values must preserve colons.
colon_l1="$tmp_root/l1-template-colon"
colon_l2="$tmp_root/l2-template-colon"
"$repo_root/scripts/new-l1-from-copier.sh" "$colon_l1" \
  -d repo_slug=l1-template-colon \
  -d maintainer_handle=@template-owner \
  -d company_name='Foo: Labs' \
  --defaults --overwrite >/dev/null
(
  cd "$colon_l1"
  ./scripts/new-repo-from-copier.sh tpl-project-repo "$colon_l2" \
    -d repo_slug=l2-template-colon \
    --defaults --overwrite >/dev/null
)
colon_company_name="$(awk '
  $0 ~ "^[[:space:]]*company_name[[:space:]]*:" {
    v = $0
    sub("^[[:space:]]*company_name[[:space:]]*:[[:space:]]*", "", v)
    gsub(/^"|"$/, "", v)
    gsub(/^\047|\047$/, "", v)
    print v
    exit
  }
' "$colon_l2/.copier-answers.yml")"
[ "$colon_company_name" = "Foo: Labs" ] || {
  echo "error: inherited company_name should preserve colon characters (expected 'Foo: Labs', got '$colon_company_name')" >&2
  exit 1
}

# Language-matrix smoke: project language cases plus monorepo member-language cases.
matrix_l1="$tmp_root/l1-template-matrix"
matrix_project_python="$tmp_root/l2-project-python-matrix"
matrix_project_rust="$tmp_root/l2-project-rust-matrix"
matrix_project_elixir="$tmp_root/l2-project-elixir-matrix"
matrix_monorepo="$tmp_root/l2-monorepo-matrix"
"$repo_root/scripts/new-l1-from-copier.sh" "$matrix_l1" \
  -d repo_slug=l1-template-matrix \
  -d maintainer_handle=@template-owner \
  --defaults --overwrite >/dev/null
(
  cd "$matrix_l1"
  ./scripts/new-repo-from-copier.sh tpl-project-repo "$matrix_project_python" \
    -d repo_slug=fixture-project-python \
    -d language=python \
    -d enable_software_pack=true \
    --defaults --overwrite >/dev/null

  ./scripts/new-repo-from-copier.sh tpl-project-repo "$matrix_project_rust" \
    -d repo_slug=fixture-project-rust \
    -d language=rust \
    -d enable_software_pack=true \
    --defaults --overwrite >/dev/null

  ./scripts/new-repo-from-copier.sh tpl-project-repo "$matrix_project_elixir" \
    -d repo_slug=fixture-project-elixir \
    -d language=elixir \
    -d enable_software_pack=true \
    --defaults --overwrite >/dev/null

  ./scripts/new-repo-from-copier.sh tpl-monorepo "$matrix_monorepo" \
    -d repo_slug=fixture-monorepo-matrix \
    -d package_manager=uv \
    --defaults --overwrite >/dev/null

  ./scripts/new-repo-from-copier.sh tpl-package "$matrix_monorepo/packages/fixture-py-core" \
    -d package_name=fixture-py-core \
    -d package_type=library \
    -d language=python \
    --defaults --overwrite >/dev/null

  ./scripts/new-repo-from-copier.sh tpl-package "$matrix_monorepo/packages/fixture-ts-core" \
    -d package_name=fixture-ts-core \
    -d package_type=library \
    -d language=typescript \
    --defaults --overwrite >/dev/null

  ./scripts/new-repo-from-copier.sh tpl-package "$matrix_monorepo/packages/fixture-rust-core" \
    -d package_name=fixture-rust-core \
    -d package_type=library \
    -d language=rust \
    --defaults --overwrite >/dev/null

  ./scripts/new-repo-from-copier.sh tpl-package "$matrix_monorepo/packages/fixture-elixir-core" \
    -d package_name=fixture-elixir-core \
    -d package_type=library \
    -d language=elixir \
    --defaults --overwrite >/dev/null
)

for required_file in \
  "$matrix_project_python/policy/stack-lane.json" \
  "$matrix_project_python/docs/tech-stack.local.md" \
  "$matrix_project_rust/policy/stack-lane.json" \
  "$matrix_project_rust/docs/tech-stack.local.md" \
  "$matrix_project_elixir/mix.exs" \
  "$matrix_project_elixir/policy/stack-lane.json" \
  "$matrix_project_elixir/docs/tech-stack.local.md" \
  "$matrix_monorepo/docs/tech-stack.local.md" \
  "$matrix_monorepo/packages/fixture-py-core/policy/stack-lane.json" \
  "$matrix_monorepo/packages/fixture-py-core/docs/tech-stack.local.md" \
  "$matrix_monorepo/packages/fixture-ts-core/policy/stack-lane.json" \
  "$matrix_monorepo/packages/fixture-ts-core/docs/tech-stack.local.md" \
  "$matrix_monorepo/packages/fixture-rust-core/policy/stack-lane.json" \
  "$matrix_monorepo/packages/fixture-rust-core/docs/tech-stack.local.md" \
  "$matrix_monorepo/packages/fixture-elixir-core/policy/stack-lane.json" \
  "$matrix_monorepo/packages/fixture-elixir-core/docs/tech-stack.local.md"
 do
  [ -s "$required_file" ] || {
    echo "error: expected non-empty stack contract artifact in language matrix: $required_file" >&2
    exit 1
  }
 done

for generated_policy in \
  "$matrix_project_python/policy/stack-lane.json" \
  "$matrix_project_rust/policy/stack-lane.json" \
  "$matrix_project_elixir/policy/stack-lane.json" \
  "$matrix_monorepo/packages/fixture-py-core/policy/stack-lane.json" \
  "$matrix_monorepo/packages/fixture-ts-core/policy/stack-lane.json" \
  "$matrix_monorepo/packages/fixture-rust-core/policy/stack-lane.json" \
  "$matrix_monorepo/packages/fixture-elixir-core/policy/stack-lane.json"
 do
  grep -qF '"ref": "workspace-local-unpinned"' "$generated_policy" || {
    echo "error: expected workspace-local-unpinned stack provenance in $generated_policy" >&2
    exit 1
  }
  if grep -qF -- "--prefer-repo" "$generated_policy"; then
    echo "error: generated stack policy should not pin repo-preferred lane resolution: $generated_policy" >&2
    exit 1
  fi
 done

for generated_doc in \
  "$matrix_project_python/docs/tech-stack.local.md" \
  "$matrix_project_rust/docs/tech-stack.local.md" \
  "$matrix_project_elixir/docs/tech-stack.local.md" \
  "$matrix_monorepo/packages/fixture-py-core/docs/tech-stack.local.md" \
  "$matrix_monorepo/packages/fixture-ts-core/docs/tech-stack.local.md" \
  "$matrix_monorepo/packages/fixture-rust-core/docs/tech-stack.local.md" \
  "$matrix_monorepo/packages/fixture-elixir-core/docs/tech-stack.local.md"
 do
  grep -qF "tech_stack_core.command" "$generated_doc" || {
    echo "error: generated stack override doc should point to the pinned lane command: $generated_doc" >&2
    exit 1
  }
  if grep -qF -- "--prefer-repo" "$generated_doc"; then
    echo "error: generated stack override doc should not hardcode repo-preferred lane resolution: $generated_doc" >&2
    exit 1
  fi
 done

grep -qF "policy/stack-lane.json" "$matrix_monorepo/docs/tech-stack.local.md" || {
  echo "error: monorepo stack doc should point packages/apps at policy/stack-lane.json" >&2
  exit 1
}
if grep -qF -- "--prefer-repo" "$matrix_monorepo/docs/tech-stack.local.md"; then
  echo "error: monorepo stack doc should not hardcode repo-preferred lane resolution" >&2
  exit 1
fi

echo "ok: l0 generation smoke + idempotency"
