# Required L2 template directories
required_dirs="
copier-template/copier/tpl-agent-repo
copier-template/copier/tpl-org-repo
copier-template/copier/tpl-project-repo
copier-template/copier/tpl-monorepo
copier-template/copier/tpl-package
"

while IFS= read -r path; do
	[ -n "$path" ] || continue
	assert_dir "$path"
done <<EOF
$required_dirs
EOF

# L2 template required files (each template must have these)
for tpl in tpl-agent-repo tpl-org-repo tpl-project-repo tpl-monorepo tpl-package; do
	assert_file "copier-template/copier/$tpl/copier.yml"
	assert_file "copier-template/copier/$tpl/contracts/layer-contract.yml"
	assert_file "copier-template/copier/$tpl/AGENTS.md.j2"
	assert_file "copier-template/copier/$tpl/CODEOWNERS.j2"
	if [ "$tpl" != "tpl-package" ]; then
		assert_absent "copier-template/copier/$tpl/scripts/ak.sh"
		assert_absent "copier-template/copier/$tpl/scripts/cargo-operator.sh"
		assert_file "copier-template/copier/$tpl/scripts/lib/check-task-scope-snapshots.py"
		assert_file "copier-template/copier/$tpl/scripts/lib/copier-answers.sh"
		assert_file "copier-template/copier/$tpl/scripts/lib/repo-surface.sh.j2"
	fi
	if [ "$tpl" != "tpl-package" ]; then
		assert_file "copier-template/copier/$tpl/scripts/check-task-scope-snapshots.sh"
		assert_file "copier-template/copier/$tpl/scripts/preflight-repo-census.sh.j2"
		assert_exec "copier-template/copier/$tpl/scripts/check-task-scope-snapshots.sh"
	fi
	assert_file "copier-template/copier/$tpl/scripts/rocs.sh.j2"
	assert_contains "copier-template/copier/$tpl/contracts/layer-contract.yml" "layer: L2" "L2 template $tpl contract must declare layer L2"
	assert_contains "copier-template/copier/$tpl/contracts/layer-contract.yml" "L1 -> L2" "L2 template $tpl contract must include allowed L1 -> L2 transition"
	assert_contains "copier-template/copier/$tpl/contracts/layer-contract.yml" "L2 -> L1" "L2 template $tpl contract must include forbidden L2 -> L1 transition"
	assert_contains "copier-template/copier/$tpl/contracts/layer-contract.yml" "max_layer_depth: 2" "L2 template $tpl contract must cap layer depth"
	assert_file "copier-template/copier/$tpl/scripts/ci/smoke.sh"
	assert_file "copier-template/copier/$tpl/scripts/ci/full.sh"
	if [ "$tpl" = "tpl-agent-repo" ]; then
		assert_file "copier-template/copier/$tpl/agent.json.j2"
		assert_file "copier-template/copier/$tpl/contracts/template-ownership.yml"
		assert_file "copier-template/copier/$tpl/scripts/compile-system-prompt.py"
		assert_file "copier-template/copier/$tpl/scripts/lib/propagate_template.py"
		assert_file "copier-template/copier/$tpl/scripts/propagate-template.sh"
		assert_exec "copier-template/copier/$tpl/scripts/compile-system-prompt.py"
		assert_exec "copier-template/copier/$tpl/scripts/lib/propagate_template.py"
		assert_exec "copier-template/copier/$tpl/scripts/propagate-template.sh"
		assert_contains "copier-template/copier/$tpl/scripts/ci/full.sh" "compile-system-prompt.py --check" "tpl-agent-repo full CI must validate the manifest and compiled prompt"
		assert_contains "copier-template/copier/$tpl/contracts/template-ownership.yml" "template_owned:" "tpl-agent-repo ownership map must define template-owned paths"
		assert_contains "copier-template/copier/$tpl/contracts/template-ownership.yml" "agent_owned:" "tpl-agent-repo ownership map must define agent-owned paths"
	fi
	assert_file "copier-template/copier/$tpl/diary/README.md"
	assert_contains "copier-template/copier/$tpl/diary/README.md" "YYYY-MM-DD--type-scope-summary.md" "L2 template $tpl diary README should enforce descriptive filename convention"
	assert_absent "copier-template/copier/$tpl/docs/diary"
	assert_exec "copier-template/copier/$tpl/scripts/rocs.sh.j2"
done

for tpl in tpl-agent-repo tpl-org-repo; do
	assert_file "copier-template/copier/$tpl/governance/README.md"
	assert_contains "copier-template/copier/$tpl/governance/README.md" "check-task-scope-snapshots.sh" "L2 template $tpl governance README should document task-scope snapshot validation"
	assert_contains "copier-template/copier/$tpl/governance/README.md" "transitional scaffolding" "L2 template $tpl governance README should keep non-authoritative task-scope wording"
done
assert_contains "copier-template/copier/tpl-project-repo/README.md.j2" "governance/task-scopes/AK-<TASK-ID>.snapshot.json" "tpl-project-repo README should describe frozen AK task-scope snapshot exports"
assert_contains "copier-template/copier/tpl-project-repo/governance/README.md" "transitional scaffolding" "tpl-project-repo governance README should describe non-authoritative hand-authored task-scope files"
assert_contains "copier-template/copier/tpl-project-repo/next_session_prompt.md" "Refresh task-scope snapshot" "tpl-project-repo next-session prompt should document AK task-scope refresh"
assert_contains "copier-template/copier/tpl-monorepo/README.md.j2" "Packages/apps consume the monorepo-root snapshot" "tpl-monorepo README should keep member task-scope authority at the monorepo root"
assert_contains "copier-template/copier/tpl-monorepo/governance/README.md" "monorepo-root snapshot" "tpl-monorepo governance README should keep package/app consumers pointed at the root snapshot"
assert_contains "copier-template/copier/tpl-monorepo/AGENTS.md.j2" "packages/apps do not create standalone AK task-scope files" "tpl-monorepo AGENTS should forbid standalone member task-scope files"
assert_contains "copier-template/copier/tpl-package/README.md.j2" "inherit deferred-work and explicit task-scope authority from the parent monorepo root" "tpl-package README should point task-scope authority back to the monorepo root"
assert_contains "copier-template/copier/tpl-package/AGENTS.md.j2" "Deferred work and explicit task scope live at the monorepo root" "tpl-package AGENTS should keep task-scope authority at the monorepo root"
assert_contains "copier-template/copier/tpl-package/scripts/rocs.sh.j2" "ROCS commands should be run from the monorepo root." "tpl-package ROCS wrapper should remain a monorepo-root placeholder"
assert_contains "copier-template/copier/tpl-package/scripts/rocs.sh.j2" "Use: ../../scripts/rocs.sh <args>" "tpl-package ROCS wrapper should redirect to the monorepo-root launcher"
assert_absent "copier-template/copier/tpl-package/scripts/ak.sh"
# System4D context: agents read ontology/src/system4d.yaml, so it names the repo and never ships <...> tokens.
