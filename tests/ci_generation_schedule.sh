# Definitions only. Both entrypoints bind repo_root before sourcing this library.
# No discovery, exclusions, caching, parallelism, or environment unit selector.
. "$repo_root/tests/ci_generation_common.sh"
. "$repo_root/tests/ci_generation_profiles.sh"
. "$repo_root/tests/ci_generation_shell_transport.sh"
. "$repo_root/tests/ci_generation_shell_matrix.sh"
. "$repo_root/tests/ci_generation_shell_launchers.sh"
. "$repo_root/tests/ci_generation_shell_metadata.sh"
. "$repo_root/tests/ci_generation_python.sh"

generation_other_shell() {
	generation_shell_transport
	generation_shell_matrix
	generation_shell_launchers
	generation_shell_metadata
}
