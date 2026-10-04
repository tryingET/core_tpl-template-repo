self_test_checkout_full_history

suffix_policy_lib="$repo_root/copier-template/scripts/lib/suffix-policy.sh"
[ -f "$suffix_policy_lib" ] || fail "missing required file: $suffix_policy_lib"
# shellcheck source=/dev/null
. "$suffix_policy_lib"

check_multi_pass_suffix_policy() {
	self_test_untemplated_jinja_matcher || fail "suffix-policy matcher regression: expected to ignore GitHub expressions and detect unsuffixed Jinja markers"

	l0_suffix="$(yaml_scalar_value "copier.yml" "_templates_suffix")"
	[ "$l0_suffix" = ".jinja" ] || fail "L0 copier config must use .jinja suffix (found ${l0_suffix:-<missing>})"

	for tpl in tpl-agent-repo tpl-org-repo tpl-project-repo tpl-monorepo tpl-package; do
		tpl_suffix="$(yaml_scalar_value "copier-template/copier/$tpl/copier.yml" "_templates_suffix")"
		[ "$tpl_suffix" = ".j2" ] || fail "L2 template $tpl copier config must use .j2 suffix (found ${tpl_suffix:-<missing>})"
	done

	nested_jinja="$(first_suffix_match "copier-template/copier" "*.jinja")"
	[ -z "$nested_jinja" ] || fail "pass-boundary suffix policy violated: nested L2 templates must not use .jinja (found $nested_jinja)"

	outer_j2="$(first_suffix_match "copier-template" "*.j2" "copier-template/copier/*")"
	[ -z "$outer_j2" ] || fail "pass-boundary suffix policy violated: outer L1 template surface must not use .j2 outside copier-template/copier/ (found $outer_j2)"

	nested_untemplated_jinja="$(first_untemplated_jinja_match "copier-template/copier" ".j2")"
	[ -z "$nested_untemplated_jinja" ] || fail "pass-boundary suffix policy violated: nested L2 template file contains Jinja markers but is not suffixed .j2 (found $nested_untemplated_jinja)"
}

list_template_files() {
	template_dir="$1"

	find "$template_dir" -type f | while IFS= read -r abs_path; do
		rel_path="${abs_path#"$template_dir"/}"
		case "$rel_path" in
		*/__pycache__/* | *.pyc)
			continue
			;;
		esac
		printf '%s\n' "$rel_path"
	done | LC_ALL=C sort
}

# end of preserved guardrail source range
