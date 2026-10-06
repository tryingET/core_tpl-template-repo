# Test-owned generation implementation; sourced, never a public selector.

generation_python_cohort() {
profile_phase python-cohort
# Executed L1 ownership lifecycle gates belong in the declared generation lane.
sh "$repo_root/tests/ci_unittest.sh" generation-main "$python_exec" tests/test_agent_template_v2.py tests/test_l1_template_ownership.py tests/test_render_l1.py tests/test_l0_check_timeouts.py tests/test_l1_template_company_ownership.py

}
