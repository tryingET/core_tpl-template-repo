#!/usr/bin/env sh
# Private closed experiment entrypoint. Not the public owner-verification command.
set -eu
export PYTHONDONTWRITEBYTECODE=1

if [ "$#" -ne 1 ]; then
	echo "error: expected exactly one generation unit" >&2
	exit 2
fi
case "$1" in
	profile-community|profile-release|profile-vouch|profile-compact|sample-shell|generation-python) ;;
	*)
		echo "error: unknown generation unit: $1 (valid: profile-community profile-release profile-vouch profile-compact sample-shell generation-python)" >&2
		exit 2
		;;
esac

repo_root="$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)"
. "$repo_root/tests/ci_generation_schedule.sh"
generation_context
case "$1" in
	profile-community)
		generation_profile_fixtures
		profile_phase profiles
		render_l1_case "l1-template-community" true false false rich
		;;
	profile-release)
		generation_profile_fixtures
		profile_phase profiles
		render_l1_case "l1-template-release" false true false rich
		;;
	profile-vouch)
		generation_profile_fixtures
		profile_phase profiles
		render_l1_case "l1-template-vouch" false false true rich
		;;
	profile-compact)
		generation_profile_fixtures
		profile_phase profiles
		render_l1_case "l1-template-compact-org" false false false compact
		generation_compact_docs
		;;
	sample-shell)
		generation_preprofile_probes
		generation_profile_fixtures
		profile_phase profiles
		render_l1_case "l1-template-sample" false false false rich
		generation_rich_docs
		generation_other_shell
		;;
	generation-python)
		generation_python_cohort
		;;
esac
profile_phase complete
