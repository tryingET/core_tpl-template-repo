# Test-owned generation implementation; sourced, never a public selector.

generation_shell_matrix() {
profile_phase language-matrix
# Language-matrix smoke: project language cases plus monorepo member-language cases.
matrix_l1="$tmp_root/l1-template-matrix"
matrix_project_python="$tmp_root/l2-project-python-matrix"
matrix_project_node="$tmp_root/l2-project-node-matrix"
matrix_project_typescript="$tmp_root/l2-project-typescript-matrix"
matrix_project_rust="$tmp_root/l2-project-rust-matrix"
matrix_project_elixir="$tmp_root/l2-project-elixir-matrix"
matrix_agent="$tmp_root/l2-agent-matrix"
matrix_org="$tmp_root/l2-org-matrix"
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

	./scripts/new-repo-from-copier.sh tpl-project-repo "$matrix_project_node" \
		-d repo_slug=fixture-project-node \
		-d language=node \
		-d enable_software_pack=true \
		--defaults --overwrite >/dev/null

	./scripts/new-repo-from-copier.sh tpl-project-repo "$matrix_project_typescript" \
		-d repo_slug=fixture-project-typescript \
		-d language=typescript \
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

	assert_command_fails "tpl-agent-repo must require exactly one role" \
		./scripts/new-repo-from-copier.sh tpl-agent-repo "$tmp_root/l2-agent-missing-role" \
		-d repo_slug=agent-missing-role -d creation_task_id=AK-5105 --defaults --overwrite
	assert_command_fails "tpl-agent-repo must require an AK creation task" \
		./scripts/new-repo-from-copier.sh tpl-agent-repo "$tmp_root/l2-agent-missing-task" \
		-d repo_slug=agent-missing-task -d agent_role=fixture-role --defaults --overwrite
	assert_command_fails "tpl-agent-repo must reject an unknown AK creation task" \
		env AK_CMD="$repo_root/tests/fixtures/ak-creation-task.sh" \
		./scripts/new-repo-from-copier.sh tpl-agent-repo "$tmp_root/l2-agent-unknown-task" \
		-d repo_slug=agent-unknown-task -d agent_role=fixture-role \
		-d creation_task_id=AK-999999999 --defaults --overwrite
	assert_command_fails "tpl-agent-repo must reject conflicting AK creation tasks" \
		./scripts/new-repo-from-copier.sh tpl-agent-repo "$tmp_root/l2-agent-duplicate-task" \
		-d repo_slug=agent-duplicate-task -d agent_role=fixture-role \
		-d creation_task_id=AK-5105 -d creation_task_id=AK-999999999 \
		--defaults --overwrite
	assert_command_fails "tpl-agent-repo must reject multiple role overrides" \
		./scripts/new-repo-from-copier.sh tpl-agent-repo "$tmp_root/l2-agent-duplicate-role" \
		-d repo_slug=agent-duplicate-role -d agent_role=role-one -d agent_role=role-two \
		-d creation_task_id=AK-5105 --defaults --overwrite

	env AK_CMD="$repo_root/tests/fixtures/ak-creation-task.sh" \
	./scripts/new-repo-from-copier.sh tpl-agent-repo "$matrix_agent" \
		-d repo_slug=fixture-agent \
		-d agent_name=agent-fixture-manifest \
		-d agent_role=fixture-agent-role \
		-d creation_task_id=AK-5105 \
		-d skill_profile=fixture-profile \
		-d skill_extras='["fixture-extra"]' \
		-d agent_tools='["read","bash"]' \
		-d agent_extensions='["fixture-extension"]' \
		-d agent_model=fixture-model \
		-d agent_thinking=high \
		-d agent_scope='{"repos":["fixture/repo"],"forbidden":["secret"],"note":"advisory"}' \
		--defaults --overwrite >/dev/null

	./scripts/new-repo-from-copier.sh tpl-org-repo "$matrix_org" \
		-d repo_slug=fixture-org \
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

assert_file_contains "$matrix_agent/agent.json" '"name": "agent-fixture-manifest"' "agent manifest should render configured name"
assert_file_contains "$matrix_agent/agent.json" '"role": "fixture-agent-role"' "agent manifest should render exactly one role"
assert_file_contains "$matrix_agent/agent.json" '"profile": "fixture-profile"' "agent manifest should render skill profile"
assert_file_contains "$matrix_agent/agent.json" '"fixture-extra"' "agent manifest should render extra skills"
assert_file_contains "$matrix_agent/agent.json" '"fixture-extension"' "agent manifest should render extensions"
assert_file_contains "$matrix_agent/agent.json" '"model": "fixture-model"' "agent manifest should render model default"
assert_file_contains "$matrix_agent/agent.json" '"thinking": "high"' "agent manifest should render thinking default"
assert_file_contains "$matrix_agent/agent.json" '"fixture/repo"' "agent manifest should render scope"
"$matrix_agent/scripts/compile-system-prompt.py" --check >/dev/null

profile_phase toggle-matrix
toggle_contract_l1="$tmp_root/l1-template-toggle-contract"
toggle_agent_default="$tmp_root/l2-agent-toggle-default"
toggle_agent_enabled="$tmp_root/l2-agent-toggle-enabled"
toggle_org_default="$tmp_root/l2-org-toggle-default"
toggle_org_enabled="$tmp_root/l2-org-toggle-enabled"
toggle_project_default="$tmp_root/l2-project-toggle-default"
toggle_project_enabled="$tmp_root/l2-project-toggle-enabled"
toggle_monorepo_default="$tmp_root/l2-monorepo-toggle-default"
toggle_monorepo_enabled="$tmp_root/l2-monorepo-toggle-enabled"
"$repo_root/scripts/new-l1-from-copier.sh" "$toggle_contract_l1" \
	-d repo_slug=l1-template-toggle-contract \
	-d maintainer_handle=@template-owner \
	--defaults --overwrite >/dev/null
(
	cd "$toggle_contract_l1"
	env AK_CMD="$repo_root/tests/fixtures/ak-creation-task.sh" \
	./scripts/new-repo-from-copier.sh tpl-agent-repo "$toggle_agent_default" \
		-d repo_slug=fixture-agent-toggle-contract \
		-d agent_role=fixture-agent-toggle-role \
		-d creation_task_id=AK-5105 \
		-d enable_community_pack=false \
		-d enable_release_pack=false \
		-d enable_vouch_gate=false \
		--defaults --overwrite >/dev/null
	env AK_CMD="$repo_root/tests/fixtures/ak-creation-task.sh" \
	./scripts/new-repo-from-copier.sh tpl-agent-repo "$toggle_agent_enabled" \
		-d repo_slug=fixture-agent-toggle-contract \
		-d agent_role=fixture-agent-toggle-role \
		-d creation_task_id=AK-5105 \
		-d enable_community_pack=true \
		-d enable_release_pack=true \
		-d enable_vouch_gate=true \
		--defaults --overwrite >/dev/null

	./scripts/new-repo-from-copier.sh tpl-org-repo "$toggle_org_default" \
		-d repo_slug=fixture-org-toggle-contract \
		-d enable_community_pack=false \
		-d enable_release_pack=false \
		-d enable_vouch_gate=false \
		--defaults --overwrite >/dev/null
	./scripts/new-repo-from-copier.sh tpl-org-repo "$toggle_org_enabled" \
		-d repo_slug=fixture-org-toggle-contract \
		-d enable_community_pack=true \
		-d enable_release_pack=true \
		-d enable_vouch_gate=true \
		--defaults --overwrite >/dev/null

	./scripts/new-repo-from-copier.sh tpl-project-repo "$toggle_project_default" \
		-d repo_slug=fixture-project-toggle-contract \
		-d enable_community_pack=false \
		-d enable_release_pack=false \
		-d enable_vouch_gate=false \
		--defaults --overwrite >/dev/null
	./scripts/new-repo-from-copier.sh tpl-project-repo "$toggle_project_enabled" \
		-d repo_slug=fixture-project-toggle-contract \
		-d enable_community_pack=true \
		-d enable_release_pack=true \
		-d enable_vouch_gate=true \
		--defaults --overwrite >/dev/null

	./scripts/new-repo-from-copier.sh tpl-monorepo "$toggle_monorepo_default" \
		-d repo_slug=fixture-monorepo-toggle-contract \
		-d package_manager=uv \
		-d enable_community_pack=false \
		-d enable_release_pack=false \
		-d enable_vouch_gate=false \
		--defaults --overwrite >/dev/null
	./scripts/new-repo-from-copier.sh tpl-monorepo "$toggle_monorepo_enabled" \
		-d repo_slug=fixture-monorepo-toggle-contract \
		-d package_manager=uv \
		-d enable_community_pack=true \
		-d enable_release_pack=true \
		-d enable_vouch_gate=true \
		--defaults --overwrite >/dev/null
)

assert_file_contains "$toggle_agent_enabled/README.md" "metadata-only in \`tpl-agent-repo\`" "generated tpl-agent-repo README should describe profile toggles as metadata-only"
assert_file_contains "$toggle_org_enabled/README.md" "metadata-only in \`tpl-org-repo\`" "generated tpl-org-repo README should describe profile toggles as metadata-only"
assert_file_contains "$toggle_project_enabled/README.md" "metadata-only in \`tpl-project-repo\`" "generated tpl-project-repo README should describe profile toggles as metadata-only"
assert_file_contains "$toggle_monorepo_enabled/README.md" "metadata-only in \`tpl-monorepo\`" "generated tpl-monorepo README should describe profile toggles as metadata-only"
assert_trees_equal_without_answers "$toggle_agent_default" "$toggle_agent_enabled" "tpl-agent-repo profile toggles should remain metadata-only at L2"
assert_trees_equal_without_answers "$toggle_org_default" "$toggle_org_enabled" "tpl-org-repo profile toggles should remain metadata-only at L2"
assert_trees_equal_without_answers "$toggle_project_default" "$toggle_project_enabled" "tpl-project-repo profile toggles should remain metadata-only at L2"
assert_trees_equal_without_answers "$toggle_monorepo_default" "$toggle_monorepo_enabled" "tpl-monorepo profile toggles should remain metadata-only at L2"

}
