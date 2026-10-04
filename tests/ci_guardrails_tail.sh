# ROCS consumer model (pinned-core launcher, CI gate, output ignores, LF attributes, ref defaults).
sh "$repo_root/scripts/check-l0-rocs-consumer.sh" || fail "ROCS consumer-model guardrails failed"

check_multi_pass_suffix_policy

required_exec="
scripts/preview-l1-diff.sh
scripts/propagate-l1-template.sh
scripts/lib/run-l1-template-refresh.sh
scripts/rocs.sh
scripts/check-session-checkpoint.sh
scripts/check-supply-chain.sh
scripts/check-l0-adversarial.sh
scripts/check-l0-fixtures.sh
scripts/check-l0-rocs-consumer.sh
scripts/sync-l0-fixtures.sh
copier-template/scripts/new-repo-from-copier.sh
copier-template/scripts/bootstrap-lane-root.sh
copier-template/scripts/check-task-scope-snapshots.sh
copier-template/scripts/rocs.sh
copier-template/scripts/check-template-ci.sh
copier-template/scripts/install-hooks.sh
copier-template/scripts/lib/check-template-ak.py
copier-template/scripts/lib/run-local-hook.sh
copier-template/scripts/ci/smoke.sh
copier-template/scripts/ci/full.sh
copier-template/scripts/release/check.sh
copier-template/scripts/release/publish.sh
copier-template/.githooks/pre-commit
copier-template/.githooks/pre-push
fixtures/l1/template-repo/scripts/bootstrap-lane-root.sh
"

while IFS= read -r path; do
	[ -n "$path" ] || continue
	assert_exec "$path"
done <<EOF
$required_exec
EOF

assert_files_equal "scripts/lib/copier-answers.sh" "copier-template/scripts/lib/copier-answers.sh" "L0 and L1 copier-answers helpers must stay identical"
for tpl in tpl-agent-repo tpl-org-repo tpl-project-repo tpl-monorepo; do
	assert_files_equal "scripts/lib/copier-answers.sh" "copier-template/copier/$tpl/scripts/lib/copier-answers.sh" "shared copier-answers helper must stay identical in $tpl"
done
assert_files_equal "scripts/lib/repo-surface.sh" "copier-template/scripts/lib/repo-surface.sh" "L0 and L1 repo-surface helpers must stay identical"
for tpl in tpl-agent-repo tpl-org-repo tpl-project-repo tpl-monorepo; do
	assert_files_equal "scripts/lib/repo-surface.sh" "copier-template/copier/$tpl/scripts/lib/repo-surface.sh.j2" "shared repo-surface helper must stay identical in $tpl"
done

# L0 copier.yml assertions
assert_contains "copier.yml" "_subdirectory: copier-template" "L0 copier source must target copier-template/"
assert_contains "copier.yml" "copier/tpl-agent-repo/" "L0 message must mention tpl-agent-repo template"
assert_contains "copier.yml" "copier/tpl-org-repo/" "L0 message must mention tpl-org-repo template"
assert_contains "copier.yml" "copier/tpl-project-repo/" "L0 message must mention tpl-project-repo template"
assert_contains "copier.yml" "copier/tpl-monorepo/" "L0 message must mention tpl-monorepo template"
assert_contains "copier.yml" "copier/tpl-package/" "L0 message must mention tpl-package template"
assert_contains "copier.yml" "l1_org_docs_profile" "L0 copier config must expose L1 org docs profile toggle"
assert_contains "copier.yml" "l2_org_docs_default" "L0 copier config must expose default L2 org-context profile toggle"
assert_contains "copier.yml" "enable_community_pack" "L0 copier config must expose community pack toggle"
assert_contains "copier.yml" "enable_release_pack" "L0 copier config must expose release pack toggle"
assert_contains "copier.yml" "enable_vouch_gate" "L0 copier config must expose vouch gate toggle"
assert_contains "copier.yml" "rm -rf copier/template-repo" "L0 must remove legacy template-repo in _tasks"

# Answers templates should use canonical Copier YAML emission.
assert_contains "copier-template/{{ _copier_conf.answers_file }}.jinja" "to_nice_yaml" "L1 answers template must use canonical Copier YAML emission"
for tpl in tpl-agent-repo tpl-org-repo tpl-project-repo tpl-monorepo tpl-package; do
	assert_contains "copier-template/copier/$tpl/{% raw %}{{ '.' ~ _copier_conf.sep ~ _copier_conf.answers_file }}{% endraw %}.j2" "to_nice_yaml" "L2 template $tpl answers template must use canonical Copier YAML emission"
done

# L2 template assertions (check tpl-project-repo as the primary example)
assert_contains "copier-template/copier/tpl-project-repo/copier.yml" "repo_slug:" "L2 copier config must have repo_slug"
assert_contains "copier-template/copier/tpl-project-repo/copier.yml" "company_slug:" "L2 copier config must have company_slug"
assert_contains "copier-template/copier/tpl-org-repo/copier.yml" "company_slug:" "L2 tpl-org-repo copier config must have company_slug"
assert_contains "copier-template/copier/tpl-agent-repo/copier.yml" "company_slug:" "L2 tpl-agent-repo copier config must have company_slug"
for field in agent_name agent_role creation_task_id system_prompt_file skill_profile skill_extras agent_tools agent_extensions agent_model agent_thinking agent_scope; do
	assert_contains "copier-template/copier/tpl-agent-repo/copier.yml" "$field:" "tpl-agent-repo copier config must expose manifest field $field"
done
assert_contains "copier-template/copier/tpl-agent-repo/agent.json.j2" '"schema": "ai-society.agent/1"' "tpl-agent-repo manifest must declare schema v1"
assert_contains "copier-template/copier/tpl-agent-repo/AGENTS.md.j2" "ai-society/agents/agent-<name>" "tpl-agent-repo AGENTS must declare fleet home"
assert_contains "copier-template/copier/tpl-agent-repo/AGENTS.md.j2" "AK is runtime authority" "tpl-agent-repo AGENTS must preserve AK runtime authority"
assert_contains "copier-template/copier/tpl-agent-repo/AGENTS.md.j2" "persona may narrow" "tpl-agent-repo persona may only narrow authority"
assert_contains "copier-template/copier/tpl-project-repo/copier.yml" "org_docs_profile" "L2 tpl-project-repo copier config must expose org-context profile toggle"
assert_contains "copier-template/copier/tpl-monorepo/copier.yml" "org_docs_profile" "L2 tpl-monorepo copier config must expose org-context profile toggle"
assert_contains "copier-template/copier/tpl-project-repo/copier.yml" "enable_community_pack" "L2 copier config must expose community pack toggle"
assert_contains "copier-template/copier/tpl-project-repo/copier.yml" "enable_release_pack" "L2 copier config must expose release pack toggle"
assert_contains "copier-template/copier/tpl-project-repo/copier.yml" "enable_vouch_gate" "L2 copier config must expose vouch gate toggle"

for tpl in tpl-agent-repo tpl-org-repo tpl-project-repo tpl-monorepo tpl-package; do
	assert_contains "copier-template/copier/$tpl/AGENTS.md.j2" "Deterministic tooling policy" "L2 template $tpl AGENTS should include deterministic tooling policy"
	assert_contains "copier-template/copier/$tpl/AGENTS.md.j2" "scripts/rocs.sh" "L2 template $tpl AGENTS should reference scripts/rocs.sh"
	assert_contains "copier-template/copier/$tpl/AGENTS.md.j2" "diary/" "L2 template $tpl AGENTS should reference repo-local diary"
	assert_contains "copier-template/copier/$tpl/README.md.j2" "ROCS command flow" "L2 template $tpl README should include ROCS command flow section"
	if [ "$tpl" = "tpl-project-repo" ]; then
		assert_file "copier-template/copier/$tpl/scripts/ci/fast.sh"
	fi
	if [ "$tpl" != "tpl-package" ]; then
		assert_contains "copier-template/copier/$tpl/README.md.j2" "check-task-scope-snapshots.sh" "L2 template $tpl README should document task-scope snapshot validation"
		assert_contains "copier-template/copier/$tpl/scripts/check-task-scope-snapshots.sh" "scripts/lib/check-task-scope-snapshots.py" "L2 template $tpl task-scope checker should use the shared parser-backed helper"
		assert_contains "copier-template/copier/$tpl/scripts/preflight-repo-census.sh.j2" "scripts/lib/repo-surface.sh" "L2 template $tpl repo census helper should source the shared repo-surface helper"
		assert_not_contains "copier-template/copier/$tpl/scripts/ci/full.sh" "crates/ak-cli/Cargo.toml" "L2 template $tpl full CI must not gate AK checks on vendored ak-cli"
		assert_contains "copier-template/copier/$tpl/scripts/ci/full.sh" "check-task-scope-snapshots.sh" "L2 template $tpl full CI should enforce task-scope snapshot checks"
	fi
	assert_contains "copier-template/copier/$tpl/scripts/ci/full.sh" "scripts/rocs.sh" "L2 template $tpl full CI should use scripts/rocs.sh when ontology is present"
done
assert_not_contains "copier-template/copier/tpl-project-repo/scripts/ci/full.sh" "uvx -n --from ./tools/rocs-cli rocs" "tpl-project-repo CI should not hardcode uvx vendored invocation"

# L1 wrapper script assertions
assert_contains "scripts/rocs.sh" "--doctor" "L0 ROCS wrapper should expose doctor mode"
assert_contains "scripts/rocs.sh" "deterministic resolution order" "L0 ROCS wrapper should document resolution order"
assert_contains "scripts/rocs.sh" "ROCS_ALLOW_PATH_FALLBACK=1" "L0 ROCS wrapper should require explicit opt-in before using ambient rocs on PATH"
assert_contains "scripts/new-l1-from-copier.sh" "COPIER_QUIET" "L0 L1 render wrapper must expose Copier quiet-mode toggle"
assert_contains "scripts/new-l1-from-copier.sh" "--quiet" "L0 L1 render wrapper must default Copier execution to quiet mode"
assert_contains "scripts/new-l1-from-copier.sh" "bootstrap-lane-root.sh" "L0 L1 render wrapper docs should include lane bootstrap workflow"
assert_contains "scripts/new-l1-from-copier.sh" "assert_repo_layer \"\$repo_root\" \"L0\"" "L0 wrapper should verify it is running from an L0 contract root"
assert_contains "scripts/new-l1-from-copier.sh" "destination already declares layer" "L0 wrapper should fail closed on destination layer mismatches"
assert_contains "scripts/lib/run-l1-template-refresh.sh" "\"\$repo_root/scripts/new-l1-from-copier.sh\" \"\$render_dir\"" "L1 refresh renderer must call new-l1 wrapper with render dir as first arg"
assert_contains "scripts/lib/run-l1-template-refresh.sh" ".copier-answers.yml" "L1 refresh renderer should infer repo_slug from target answers when available"
assert_contains "scripts/lib/run-l1-template-refresh.sh" "repo_slug_from_answers" "L1 refresh renderer should parse repo_slug from target answers file"
assert_contains "scripts/lib/run-l1-template-refresh.sh" "scripts/lib/copier-answers.sh" "L1 refresh renderer should source the shared copier answers helper"
assert_contains "scripts/lib/run-l1-template-refresh.sh" "scripts/lib/repo-surface.sh" "L1 refresh renderer should source the shared repo-surface helper"
assert_contains "scripts/preflight-repo-census.sh" "scripts/lib/repo-surface.sh" "repo census helper should source the shared repo-surface helper"
assert_contains "scripts/migrate-l1-structure.sh" "scripts/lib/repo-surface.sh" "migration helper should source the shared repo-surface helper"
assert_contains "copier-template/scripts/new-repo-from-copier.sh" "tpl-agent-repo" "L1 wrapper must list tpl-agent-repo template"
assert_contains "copier-template/scripts/new-repo-from-copier.sh" "tpl-org-repo" "L1 wrapper must list tpl-org-repo template"
assert_contains "copier-template/scripts/new-repo-from-copier.sh" "tpl-project-repo" "L1 wrapper must list tpl-project-repo template"
assert_contains "copier-template/scripts/new-repo-from-copier.sh" "tpl-monorepo" "L1 wrapper must list tpl-monorepo template"
assert_contains "copier-template/scripts/new-repo-from-copier.sh" "tpl-package" "L1 wrapper must list tpl-package template"
assert_contains "copier-template/scripts/new-repo-from-copier.sh" "COPIER_QUIET" "L1 wrapper must expose Copier quiet-mode toggle"
assert_contains "copier-template/scripts/new-repo-from-copier.sh" "--quiet" "L1 wrapper must default Copier execution to quiet mode"
assert_contains "copier-template/scripts/new-repo-from-copier.sh" "COPIER_VERSION" "L1 wrapper must pin Copier version"
assert_contains "copier-template/scripts/new-repo-from-copier.sh" "scripts/lib/copier-answers.sh" "L1 wrapper should source the shared copier answers helper"
assert_contains "copier-template/scripts/new-repo-from-copier.sh" 'task show "$task_id"' "L1 wrapper must verify the exact AK agent-creation task exists"
assert_contains "copier-template/scripts/new-repo-from-copier.sh" "uvx --from \"copier==\${COPIER_VERSION}\" copier" "L1 wrapper must include pinned uvx invocation"
assert_contains "copier-template/scripts/new-repo-from-copier.sh" "uv tool run --from \"copier==\${COPIER_VERSION}\" copier" "L1 wrapper must include pinned uv tool invocation"
assert_contains "copier-template/scripts/new-repo-from-copier.sh" "pinned-source births forbid unpinned copier fallback" "L1 birth wrapper must refuse unpinned Copier fallback"
assert_contains "copier-template/scripts/bootstrap-lane-root.sh" "--init-lane-git" "L1 lane bootstrap helper must support lane git initialization"
assert_contains "copier-template/scripts/bootstrap-lane-root.sh" "tpl-project-repo" "L1 lane bootstrap helper must render tpl-project-repo baseline"
assert_contains "copier-template/scripts/bootstrap-lane-root.sh" "scripts/lib/repo-surface.sh" "L1 lane bootstrap helper should source the shared repo-surface helper"
assert_contains "copier-template/scripts/bootstrap-lane-root.sh" "repo_surface_lane_root_src_path" "L1 lane bootstrap helper should derive a stable lane-root source path"
assert_contains "copier-template/scripts/bootstrap-lane-root.sh" "!contracts/**" "L1 lane bootstrap helper should track layer contracts in lane-root baselines"
assert_contains "copier-template/scripts/bootstrap-lane-root.sh" '!$lane/contracts/**' "L1 lane bootstrap helper should unignore lane-root contracts in parent gitignore"
assert_not_contains "copier-template/scripts/bootstrap-lane-root.sh" "sed -i" "L1 lane bootstrap helper must not rely on GNU sed -i"
assert_contains "copier-template/scripts/check-template-ci.sh" "L1 wrapper must pin Copier version" "L1 template CI must enforce copier pinning"
assert_contains "copier-template/scripts/check-template-ci.sh" "scripts/lib/copier-answers.sh" "L1 template CI should source the shared copier answers helper"
assert_contains "copier-template/scripts/check-template-ci.sh" "scripts/lib/repo-surface.sh" "L1 template CI should require the shared repo-surface helper"
assert_contains "copier-template/scripts/check-template-ci.sh" "L1 wrapper must try pinned runtimes before refusing unpinned copier" "L1 template CI must enforce copier runtime precedence"
for forbidden_policy_needle in \
	'AK CLI: `ak <ak args...>`' \
	'Organization docs profile' \
	'Setup uv (full lane)' \
	'!owned/.gitignore'; do
	assert_not_contains "copier-template/scripts/check-template-ci.sh" "$forbidden_policy_needle" "downstream L1 gate must not impose canonical content on agent-owned policy"
done
assert_contains "copier-template/scripts/check-template-ci.sh" "canonical birth wording" "downstream L1 gate must document its agent-owned content boundary"
assert_contains "tests/test_l1_template_ownership.py" "COMPANY_POLICY_FIXTURE" "ownership regression must overlay divergent company policy"
assert_contains "tests/test_l1_template_ownership.py" "scripts/check-template-ci.sh" "divergent company policy must pass generated L1 validation"
assert_contains "copier-template/scripts/check-task-scope-snapshots.sh" "scripts/lib/check-task-scope-snapshots.py" "L1 task-scope checker should use the shared parser-backed helper"
assert_contains "copier-template/scripts/rocs.sh" "--doctor" "L1 ROCS wrapper should expose doctor mode"
assert_contains "copier-template/scripts/rocs.sh" "No ephemeral-tool, PATH, or vendored fallbacks." "L1 ROCS wrapper should document that it only runs the pinned workspace core"
assert_not_contains "copier-template/scripts/rocs.sh" "ROCS_ALLOW_PATH_FALLBACK" "L1 ROCS wrapper must not fall back to an ambient rocs on PATH"
assert_contains "copier-template/scripts/ci/full.sh" "check-task-scope-snapshots.sh" "L1 full CI should enforce task-scope snapshot checks"
assert_not_contains "copier-template/scripts/ci/full.sh" "crates/ak-cli/Cargo.toml" "L1 full CI must not gate AK checks on vendored ak-cli"
assert_contains "copier-template/scripts/ci/full.sh" "scripts/rocs.sh" "L1 full CI should use scripts/rocs.sh when ontology is present"
assert_contains "copier-template/.github/workflows/ci.yml" "Setup uv (full lane)" "L1 CI workflow should provision uv in the full lane"
assert_contains "copier-template/.github/workflows/ci.yml" "Run full lane" "fresh L1 CI workflow should expose its full lane"
assert_not_contains "copier-template/scripts/install-hooks.sh" "copier/template-repo" "L1 install-hooks must not reference removed legacy template-repo path"
assert_contains "copier-template/scripts/install-hooks.sh" "scripts/bootstrap-lane-root.sh" "L1 install-hooks should normalize executable bit for lane bootstrap helper"
assert_contains "copier-template/scripts/install-hooks.sh" "scripts/rocs.sh" "L1 install-hooks should normalize executable bit for the L1 ROCS wrapper"
assert_contains "copier-template/scripts/install-hooks.sh" "scripts/check-task-scope-snapshots.sh" "L1 install-hooks should normalize executable bit for the L1 task-scope checker"
assert_contains "copier-template/scripts/install-hooks.sh" "scripts/lib/check-template-ak.py" "L1 install-hooks should normalize executable bit for the AK test double"
for tpl in tpl-agent-repo tpl-org-repo tpl-project-repo tpl-monorepo tpl-package; do
	if [ "$tpl" != "tpl-package" ]; then
		assert_contains "copier-template/scripts/install-hooks.sh" "copier/$tpl/scripts/check-task-scope-snapshots.sh" "L1 install-hooks should normalize executable bits for $tpl task-scope checker"
	fi
	assert_contains "copier-template/scripts/install-hooks.sh" "copier/$tpl/scripts/rocs.sh.j2" "L1 install-hooks should normalize executable bits for $tpl rocs wrapper"
	assert_contains "copier-template/scripts/install-hooks.sh" "copier/$tpl/scripts/ci/smoke.sh" "L1 install-hooks should normalize executable bits for $tpl smoke lane"
	if [ "$tpl" = "tpl-project-repo" ]; then
		assert_contains "copier-template/scripts/install-hooks.sh" "copier/$tpl/scripts/ci/fast.sh" "L1 install-hooks should normalize executable bits for $tpl fast lane"
	fi
	assert_contains "copier-template/scripts/install-hooks.sh" "copier/$tpl/scripts/ci/full.sh" "L1 install-hooks should normalize executable bits for $tpl full lane"
done
assert_not_contains "copier-template/scripts/ci/smoke.sh" "copier/template-repo/copier.yml" "L1 smoke lane must not lint removed legacy template-repo path"
assert_contains "copier-template/scripts/ci/smoke.sh" "copier.yml copier/*/copier.yml" "L1 smoke lane should lint root and nested copier configs"

# CODEOWNERS assertions
assert_contains "CODEOWNERS" "/copier-template/**" "CODEOWNERS must protect copier-template/"
assert_contains "AGENTS.md" "check-l0.sh" "AGENTS validation section should use consolidated L0 check"
assert_contains "AGENTS.md" "Deterministic tooling policy" "AGENTS should document deterministic tooling policy"
assert_contains "AGENTS.md" "scripts/rocs.sh" "AGENTS should reference scripts/rocs.sh"
assert_contains "AGENTS.md" "diary/" "AGENTS should require repo-local diary"
assert_contains "AGENTS.md" "Knowledge crystallization flow" "AGENTS should define crystallization flow"
assert_contains ".github/pull_request_template.md" "check-l0-guardrails.sh" "PR template must require guardrail checks"
assert_contains ".github/pull_request_template.md" "check-session-checkpoint.sh" "PR template must require session checkpoint check"
assert_contains ".github/pull_request_template.md" "check-l0-generation.sh" "PR template must require generation checks"
assert_contains ".github/pull_request_template.md" "check-l0-adversarial.sh" "PR template should require adversarial operator-surface checks"
assert_contains ".github/pull_request_template.md" "check-l0-fixtures.sh" "PR template should require fixture checks"
assert_contains ".github/pull_request_template.md" "check-supply-chain.sh" "PR template should require supply-chain checks"
assert_contains "CONTRIBUTING.md" "check-l0.sh" "L0 contributing guide should reference full L0 checks"
assert_contains "CONTRIBUTING.md" "check-l0-adversarial.sh" "L0 contributing guide should document the adversarial operator-surface suite"
assert_contains "CONTRIBUTING.md" "L0_CHECK_TIMEOUT_SECONDS" "L0 contributing guide should document fail-fast timeout control for full checks"
assert_contains "CONTRIBUTING.md" "scripts/rocs.sh --doctor" "L0 contributing guide should include deterministic ROCS wrapper usage"
assert_contains "CONTRIBUTING.md" "diary/" "L0 contributing guide should require repo-local diary"
assert_contains "CONTRIBUTING.md" "docs/learnings/" "L0 contributing guide should include crystallization destination"
assert_contains "CONTRIBUTING.md" "profile-governance-policy.md" "L0 contributing guide should link profile governance policy"
assert_contains "README.md" "Organization docs profiles" "README should document org docs profile behavior"
assert_contains "README.md" "Profile governance policy" "README should link profile governance policy"
assert_contains "README.md" "Community pack" "README should document optional community pack behavior"
assert_contains "README.md" "Release pack" "README should document optional release pack behavior"
assert_contains "README.md" "Structure baseline" "README should document baseline scaffold structure"
assert_contains "README.md" "L1 vs L2" "README baseline section should distinguish L1 and L2 output contracts"
assert_contains "README.md" "archetype/profile-specific" "README should document that L2 baseline is archetype/profile-specific"
assert_contains "README.md" "Deterministic ROCS launcher" "README should document deterministic ROCS launcher"
assert_contains "README.md" "Multi-pass template suffix policy" "README should document multi-pass suffix policy"
assert_contains "README.md" "Pass-boundary rule" "README should describe pass-boundary suffix rule"
assert_contains "README.md" "docs/learnings/" "README should describe KES crystallization destination"
assert_contains "README.md" "diary/" "README should document repo-local diary policy"
assert_contains "README.md" "docs/dev/README.md" "README should link setup+transition operator entrypoint"
assert_contains "README.md" "check-l0-adversarial.sh" "README should document the adversarial operator-surface suite"
assert_contains "README.md" "l2-transition-playbook.md" "README should link L2 transition playbook"
assert_contains "README.md" "tpl-project-repo-file-contract.md" "README should link the canonical tpl-project-repo file contract"
assert_contains "docs/dev/README.md" "Agent handoff line" "operator entrypoint should include explicit agent handoff guidance"
assert_contains "docs/dev/README.md" "docs/l2-transition-playbook.md" "operator entrypoint should link L2 transition playbook"
assert_contains "docs/dev/README.md" "bootstrap-lane-root.sh" "operator entrypoint should document lane bootstrap workflow"
assert_contains "docs/dev/README.md" "no in-place auto-migrator" "operator entrypoint should clarify migration limitation"
assert_contains "docs/l1-adoption-playbook.md" "docs/dev/README.md" "L1 adoption playbook should link operator entrypoint"
assert_contains "docs/l1-adoption-playbook.md" "docs/l2-transition-playbook.md" "L1 adoption playbook should link L2 migration playbook"
assert_contains "scripts/check-l0.sh" "check-session-checkpoint" "consolidated L0 check should run session checkpoint guardrails"
assert_contains "scripts/check-l0.sh" "check-l0-adversarial" "consolidated L0 check should run adversarial operator-surface checks"
assert_contains "scripts/check-l0.sh" "L0_CHECK_TIMEOUT_SECONDS" "consolidated L0 check should expose fail-fast timeout control"
assert_contains "scripts/check-l0-generation.sh" "tests/test_agent_template_v2.py" "generation gate must run agent template v2 behavior tests"
assert_contains "scripts/check-l0-generation.sh" "tests/test_l1_template_ownership.py" "generation gate must run L1 ownership behavior tests"
assert_contains "scripts/check-l0-adversarial.sh" "git worktree add --detach" "adversarial suite should exercise git worktree provenance"
assert_contains "scripts/check-l0-adversarial.sh" "preview-l1-diff.sh" "adversarial suite should exercise adoption preview filtering"
assert_contains "scripts/check-l0-adversarial.sh" "tracked lane drift" "adversarial suite should force tracked lane-root drift through preview"
assert_contains "scripts/check-l0-adversarial.sh" "migrate-l1-structure.sh" "adversarial suite should exercise migration portability"
assert_contains "scripts/check-l0-adversarial.sh" "preflight-repo-census.sh" "adversarial suite should exercise deep repo census coverage"
assert_contains "scripts/check-l0-adversarial.sh" "stable relative _src_path" "adversarial suite should exercise stable lane-root source paths"
assert_contains "scripts/check-l0-generation.sh" "preview-l1-diff.sh" "L0 generation checks should execute preview-l1-diff runtime coverage"
assert_contains "scripts/check-l0-generation.sh" "ok: no diff between rendered L1 and target" "L0 generation checks should assert clean preview no-diff output"
assert_contains "docs/learnings/README.md" "Session output" "L0 learnings README should define KES flow"
assert_contains "docs/learnings/README.md" "tips/meta/" "L0 learnings README should include TIP propagation target"
assert_contains "diary/README.md" "YYYY-MM-DD--type-scope-summary.md" "L0 diary README should enforce descriptive filename convention"
assert_contains "diary/README.md" "Session output" "L0 diary README should define crystallization flow"
assert_contains "diary/README.md" "docs/learnings/" "L0 diary README should include learnings destination"
assert_contains "diary/README.md" "tips/meta/" "L0 diary README should include TIP destination"
assert_contains "next_session_prompt.md" "Rollback path (mirror-only correction)" "session checkpoint should include rollback path"
assert_contains "next_session_prompt.md" "git restore -- next_session_prompt.md" "session checkpoint rollback path should include restore command"
assert_contains "next_session_prompt.md" "KES crystallization flow" "session checkpoint should include KES flow"
assert_contains "copier-template/diary/README.md.jinja" "YYYY-MM-DD--type-scope-summary.md" "L1 diary README template should enforce descriptive filename convention"

for doc in copier-template/README.md.jinja copier-template/AGENTS.md.jinja; do
	assert_contains "$doc" "Recursion policy" "generated L1 docs must include recursion policy section"
	assert_contains "$doc" "L1 -> L2" "generated L1 docs must allow L1 -> L2"
	assert_contains "$doc" "L1 -> L0" "generated L1 docs must forbid L1 -> L0"
	assert_contains "$doc" "L2 -> L1" "generated L1 docs must forbid L2 -> L1"
done
assert_contains "copier-template/AGENTS.md.jinja" "Deterministic tooling policy" "generated L1 AGENTS should include deterministic tooling policy"
assert_contains "copier-template/AGENTS.md.jinja" 'AK CLI: `ak <ak args...>`' "fresh L1 AGENTS should document canonical AK path"
assert_contains "copier-template/AGENTS.md.jinja" "scripts/rocs.sh" "generated L1 AGENTS should reference scripts/rocs.sh"
assert_contains "copier-template/AGENTS.md.jinja" "diary/" "generated L1 AGENTS should require repo-local diary"
assert_contains "copier-template/CONTRIBUTING.md" "scripts/rocs.sh --doctor" "generated L1 contributing guide should include deterministic ROCS wrapper usage"
assert_contains "copier-template/CONTRIBUTING.md" "check-template-ci.sh" "fresh L1 contributing guide should reference template checks"
assert_contains "copier-template/CONTRIBUTING.md" "diary/" "generated L1 contributing guide should require repo-local diary"
assert_contains "copier-template/README.md.jinja" "Organization docs profile" "generated L1 README should describe org docs profile"
assert_contains "copier-template/README.md.jinja" "Governance layering" "fresh L1 README should describe governance layering"
assert_contains "copier-template/README.md.jinja" "Community profile" "fresh L1 README should describe community profile"
assert_contains "copier-template/README.md.jinja" "Release profile" "fresh L1 README should describe release profile"
assert_contains "copier-template/README.md.jinja" "Baseline structure" "fresh L1 README should describe baseline structure"
assert_contains "copier-template/README.md.jinja" ".gitattributes" "fresh L1 README should mention git baseline attributes"
assert_contains "copier-template/README.md.jinja" "archetype/profile-specific" "generated L1 README should clarify archetype/profile-specific L2 baselines"
assert_contains "copier-template/README.md.jinja" "Deterministic ROCS launcher" "generated L1 README should describe deterministic ROCS launcher"
assert_contains "copier-template/README.md.jinja" "Agent Kernel command flow" "generated L1 README should describe plain ak command flow"
assert_contains "copier-template/README.md.jinja" "check-task-scope-snapshots.sh" "generated L1 README should document task-scope snapshot validation"
assert_contains "copier-template/README.md.jinja" "Multi-pass template suffix policy" "generated L1 README should describe multi-pass suffix policy"
assert_contains "copier-template/README.md.jinja" "repo-local diary" "generated L1 README should describe repo-local diary contract"
assert_contains "copier-template/README.md.jinja" "no automatic in-place migrator" "generated L1 README should document deterministic migration limitation"
assert_contains "copier-template/README.md.jinja" "tpl-project-repo-file-contract.md" "generated L1 README should link canonical tpl-project-repo file contract"
assert_contains "copier-template/README.md.jinja" "bootstrap-lane-root.sh" "generated L1 README should document lane bootstrap workflow"
assert_contains "copier-template/AGENTS.md.jinja" "L2 Templates" "generated L1 AGENTS should document L2 templates"
assert_contains "copier-template/AGENTS.md.jinja" "bootstrap-lane-root.sh" "generated L1 AGENTS should document lane bootstrap helper"
assert_contains "fixtures/l1/template-repo/diary/README.md" "YYYY-MM-DD--type-scope-summary.md" "L1 fixture diary README should enforce descriptive filename convention"
assert_not_contains "fixtures/l1/template-repo/README.md" '- Profile: ``' "fresh L1 README must not render an empty profile label"
assert_not_contains "fixtures/l1/template-repo/README.md" '- Default L2 project/monorepo org-context profile: ``' "fresh L1 README must not render an empty L2 org profile"
assert_contains "fixtures/l2/tpl-project-repo/diary/README.md" "YYYY-MM-DD--type-scope-summary.md" "L2 fixture diary README should enforce descriptive filename convention"
assert_file "fixtures/l2/tpl-agent-repo/contracts/layer-contract.yml"
assert_contains "fixtures/l2/tpl-agent-repo/contracts/layer-contract.yml" "layer: L2" "tpl-agent-repo fixture contract must declare layer L2"
assert_file "fixtures/l2/tpl-agent-repo/agent.json"
assert_file "fixtures/l2/tpl-agent-repo/contracts/template-ownership.yml"
assert_file "fixtures/l2/tpl-agent-repo/docs/person/system-prompt.md"
assert_exec "fixtures/l2/tpl-agent-repo/scripts/compile-system-prompt.py"
assert_exec "fixtures/l2/tpl-agent-repo/scripts/propagate-template.sh"
assert_contains "fixtures/l2/tpl-agent-repo/agent.json" '"schema": "ai-society.agent/1"' "tpl-agent-repo fixture manifest must declare schema v1"
assert_contains "fixtures/l2/tpl-agent-repo/docs/person/system-prompt.md" "<!-- compiled: do not edit -->" "tpl-agent-repo fixture prompt must carry the compiled marker"
assert_file "fixtures/l2/tpl-org-repo/contracts/layer-contract.yml"
assert_contains "fixtures/l2/tpl-org-repo/contracts/layer-contract.yml" "layer: L2" "tpl-org-repo fixture contract must declare layer L2"
assert_file "fixtures/l2/tpl-project-repo/contracts/layer-contract.yml"
assert_contains "fixtures/l2/tpl-project-repo/contracts/layer-contract.yml" "layer: L2" "tpl-project-repo fixture contract must declare layer L2"
assert_file "fixtures/l2/tpl-monorepo/contracts/layer-contract.yml"
assert_contains "fixtures/l2/tpl-monorepo/contracts/layer-contract.yml" "layer: L2" "tpl-monorepo fixture contract must declare layer L2"
assert_file "fixtures/l2/tpl-package/contracts/layer-contract.yml"
assert_contains "fixtures/l2/tpl-package/contracts/layer-contract.yml" "layer: L2" "tpl-package fixture contract must declare layer L2"
assert_contains "fixtures/l2/tpl-project-repo/README.md" "governance/task-scopes/AK-<TASK-ID>.snapshot.json" "tpl-project-repo fixture README should stay aligned with AK task-scope snapshot guidance"
assert_contains "fixtures/l2/tpl-project-repo/governance/README.md" "transitional scaffolding" "tpl-project-repo fixture governance README should keep non-authoritative task-scope wording"
assert_contains "fixtures/l2/tpl-project-repo/README.md" "check-task-scope-snapshots.sh" "tpl-project-repo fixture README should document task-scope snapshot validation"
assert_contains "fixtures/l2/tpl-monorepo/README.md" "Packages/apps consume the monorepo-root snapshot" "tpl-monorepo fixture README should keep member task-scope authority at the root"
assert_contains "fixtures/l2/tpl-monorepo/governance/README.md" "monorepo-root snapshot" "tpl-monorepo fixture governance README should keep package/app consumers pointed at the root snapshot"
assert_contains "fixtures/l2/tpl-monorepo/README.md" "check-task-scope-snapshots.sh" "tpl-monorepo fixture README should document task-scope snapshot validation"
assert_contains "fixtures/l2/tpl-package/README.md" "inherit deferred-work and explicit task-scope authority from the parent monorepo root" "tpl-package fixture README should point task-scope authority back to the monorepo root"
assert_contains "fixtures/l2/tpl-package/AGENTS.md" "Deferred work and explicit task scope live at the monorepo root" "tpl-package fixture AGENTS should keep task-scope authority at the monorepo root"
assert_contains "fixtures/l2/tpl-package/scripts/rocs.sh" "ROCS commands should be run from the monorepo root." "tpl-package fixture ROCS wrapper should remain a monorepo-root placeholder"
assert_contains "fixtures/l2/tpl-package/scripts/rocs.sh" "Use: ../../scripts/rocs.sh <args>" "tpl-package fixture ROCS wrapper should redirect to the monorepo-root launcher"
assert_absent "fixtures/l2/tpl-package/scripts/ak.sh"
assert_contains "fixtures/matrix/tpl-monorepo/root/packages/fixture-py-core/README.md" "inherit deferred-work and explicit task-scope authority from the parent monorepo root" "matrix monorepo fixture package README should inherit task-scope authority from the root"
assert_contains "fixtures/matrix/tpl-monorepo/root/packages/fixture-py-core/AGENTS.md" "Deferred work and explicit task scope live at the monorepo root" "matrix monorepo fixture package AGENTS should keep task-scope authority at the root"
assert_contains "fixtures/matrix/tpl-monorepo/root/packages/fixture-py-core/scripts/rocs.sh" "ROCS commands should be run from the monorepo root." "matrix monorepo fixture package ROCS wrapper should remain a monorepo-root placeholder"
assert_file "fixtures/matrix/tpl-monorepo/root/packages/fixture-py-core/contracts/layer-contract.yml"
assert_contains "fixtures/matrix/tpl-monorepo/root/packages/fixture-py-core/contracts/layer-contract.yml" "layer: L2" "matrix monorepo fixture package contract must declare layer L2"
assert_absent "fixtures/matrix/tpl-monorepo/root/packages/fixture-py-core/scripts/ak.sh"

contract="copier-template/contracts/layer-contract.yml"
assert_contains "$contract" "layer: L1" "generated L1 contract must declare layer L1"
assert_contains "$contract" "L0 -> L1" "generated L1 contract must include inbound transition"
assert_contains "$contract" "L1 -> L2" "generated L1 contract must include allowed outbound transition"
assert_contains "$contract" "L1 -> L0" "generated L1 contract must include forbidden reverse transition"
assert_contains "$contract" "L2 -> L1" "generated L1 contract must include forbidden reverse transition"
assert_contains "$contract" "nested_copier_tasks_allowed: false" "generated L1 contract must forbid nested copier tasks"
assert_contains "$contract" "max_layer_depth: 2" "generated L1 contract must cap layer depth"

assert_contains "copier-template/.github/workflows/vouch-check-pr.yml.jinja" "mitchellh/vouch/action/check-pr@5713ce1baedf75e2f830afa3dac813a9c48bff12" "L1 vouch-check workflow should pin action SHA"
assert_contains "copier-template/.github/workflows/vouch-manage.yml.jinja" "mitchellh/vouch/action/manage-by-issue@5713ce1baedf75e2f830afa3dac813a9c48bff12" "L1 vouch-manage workflow should pin action SHA"
assert_contains "copier-template/.github/workflows/release-please.yml" "googleapis/release-please-action@v4" "L1 release-please workflow should invoke release-please action"
assert_contains "copier-template/.github/workflows/publish.yml" "softprops/action-gh-release@v2" "L1 publish workflow should upload release artifacts"
assert_contains "copier-template/.gitignore" "!owned/.gitignore" "L1 parent .gitignore must unignore owned lane-root .gitignore"
assert_contains "copier-template/.gitignore" "!contrib/.gitignore" "L1 parent .gitignore must unignore contrib lane-root .gitignore"
assert_contains "copier-template/.gitignore" "!infra/.gitignore" "L1 parent .gitignore must unignore infra lane-root .gitignore"
assert_contains "copier-template/.gitignore" "!agents/.gitignore" "L1 parent .gitignore must unignore agents lane-root .gitignore"

# Ensure legacy template-repo is removed from generated L1
assert_absent "copier-template/copier/template-repo"

# Ensure legacy diary path is removed
assert_absent "copier-template/copier/tpl-agent-repo/docs/diary"
assert_absent "copier-template/copier/tpl-org-repo/docs/diary"
assert_absent "copier-template/copier/tpl-project-repo/docs/diary"
assert_absent "fixtures/l1/template-repo/copier/tpl-agent-repo/docs/diary"
assert_absent "fixtures/l1/template-repo/copier/tpl-org-repo/docs/diary"
assert_absent "fixtures/l1/template-repo/copier/tpl-project-repo/docs/diary"
assert_absent "fixtures/l2/tpl-project-repo/docs/diary"

# Ensure template sources never commit generated Python build/cache artifacts. An untracked,
# gitignored cache on disk is harmless: Copier's default _exclude drops __pycache__/*.py[co] from
# every render, and anything unignored (e.g. *.egg-info) makes L0 dirty, which renders refuse.
# tests/test_render_l1.py asserts the render itself carries none.
if git ls-files -- copier-template/copier | grep -E '(^|/)__pycache__/|\.py[co]$|\.egg-info(/|$)' | grep -q .; then
	fail "template source tracks generated python cache/metadata files"
fi
if find copier-template/copier -type d -path '*/tools/rocs-cli/build' | grep -q .; then
	fail "template source contains rocs-cli build output directory"
fi

# Ensure no nested copier invocations
if grep -nE 'copier[[:space:]]+(copy|update)' copier.yml >/dev/null 2>&1; then
	fail "nested copier invocations are not allowed in template config files"
fi

echo "ok: l0 guardrails"
