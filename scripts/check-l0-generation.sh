#!/usr/bin/env sh
set -eu

repo_root="$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)"
# Full serial public entrypoint; arguments retain their historical ignored behavior.
# Linked runtime proofs: preview-l1-diff.sh asserts "ok: no diff between rendered L1 and target"
# in ci_generation_profiles.sh and ci_generation_shell_transport.sh; Python cohort:
# tests/test_agent_template_v2.py tests/test_l1_template_ownership.py tests/test_render_l1.py
# tests/test_l0_check_timeouts.py tests/test_l1_template_company_ownership.py
. "$repo_root/tests/ci_generation_schedule.sh"
generation_context
generation_preprofile_probes
generation_profile_fixtures

profile_phase profiles

render_l1_case "l1-template-sample" false false false rich
render_l1_case "l1-template-community" true false false rich
render_l1_case "l1-template-release" false true false rich
render_l1_case "l1-template-vouch" false false true rich
render_l1_case "l1-template-compact-org" false false false compact

rich_l1="$tmp_root/l1-template-sample"
compact_l1="$tmp_root/l1-template-compact-org"
for org_doc in purpose.md mission.md vision.md strategic_objectives.md values_ethics.md governance.md glossary.md; do
	generation_rich_org_doc
	generation_compact_org_doc
done

generation_compact_operating_model

generation_other_shell
generation_python_cohort

profile_phase complete
echo "ok: l0 generation smoke + idempotency + ownership-aware template propagation"
