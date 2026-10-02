#!/usr/bin/env sh
# Exercise the actual L1 full.sh entrypoint; stub unrelated checks and ROCS only.
set -eu

# A hook caller may export its own repository/index; every Git operation stays in probes.
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_OBJECT_DIRECTORY GIT_ALTERNATE_OBJECT_DIRECTORIES

repo_root="$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)"
probe_root="$(mktemp -d)"
trap 'rm -rf "$probe_root"' EXIT

fail() {
	echo "error: $*" >&2
	exit 1
}

new_probe() {
	probe="$probe_root/$1"
	mkdir -p "$probe/scripts/ci" "$probe/scripts/lib" "$probe/ontology"
	cp "$repo_root/copier-template/scripts/ci/full.sh" "$probe/scripts/ci/full.sh"
	for helper in scripts/ci/smoke.sh scripts/check-task-scope-snapshots.sh scripts/check-template-ci.sh scripts/lib/run-local-hook.sh; do
		printf '#!/bin/sh\nexit 0\n' >"$probe/$helper"
		chmod +x "$probe/$helper"
	done
	cat >"$probe/scripts/rocs.sh" <<'ROCS'
#!/bin/sh
printf '%s\n' "$1" >> ontology-gate-calls.log
exit 0
ROCS
	chmod +x "$probe/scripts/rocs.sh"
	env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE git -C "$probe" init -q
}

run_probe() {
	(cd "$probe" && env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE sh ./scripts/ci/full.sh) >"$probe.log" 2>&1
}

expect_skip() {
	run_probe || fail "$1 should permit the empty L1 ontology skeleton: $(cat "$probe.log")"
	[ ! -e "$probe/ontology-gate-calls.log" ] || fail "$1 must not invoke ROCS without a manifest"
}

expect_refusal() {
	if run_probe; then
		fail "$1 unexpectedly passed full.sh"
	fi
	grep -qF "$2" "$probe.log" || fail "$1 failed for the wrong reason: $(cat "$probe.log")"
	[ ! -e "$probe/ontology-gate-calls.log" ] || fail "$1 must refuse before invoking ROCS"
}

new_probe empty
expect_skip empty

new_probe placeholder
: >"$probe/ontology/.gitkeep"
git -C "$probe" add ontology/.gitkeep
expect_skip placeholder

new_probe untracked
printf 'untracked\n' >"$probe/ontology/local.yaml"
expect_skip untracked

for case_name in content deleted-manifest renamed-manifest spaced-path staged-deletion actual-rename gitkeep-directory; do
	new_probe "$case_name"
	mkdir -p "$probe/ontology/src"
	printf 'source\n' >"$probe/ontology/src/concept.yaml"
	case "$case_name" in
		staged-deletion | actual-rename)
			printf 'manifest\n' >"$probe/ontology/manifest.yaml"
			git -C "$probe" add ontology
			if [ "$case_name" = staged-deletion ]; then
				rm "$probe/ontology/manifest.yaml"
				git -C "$probe" add -u -- ontology/manifest.yaml
			else
				git -C "$probe" mv ontology/manifest.yaml ontology/renamed.yaml
			fi
			;;
		gitkeep-directory)
			rm "$probe/ontology/src/concept.yaml"
			rmdir "$probe/ontology/src"
			mkdir "$probe/ontology/.gitkeep"
			printf 'source\n' >"$probe/ontology/.gitkeep/concept.yaml"
			git -C "$probe" add ontology
			;;
		deleted-manifest)
			printf 'manifest\n' >"$probe/ontology/manifest.yaml"
			git -C "$probe" add ontology
			rm "$probe/ontology/manifest.yaml"
			;;
		renamed-manifest)
			printf 'manifest\n' >"$probe/ontology/manifest.yml"
			git -C "$probe" add ontology
			;;
		spaced-path)
			mv "$probe/ontology/src/concept.yaml" "$probe/ontology/src/a concept.yaml"
			git -C "$probe" add ontology
			;;
		*) git -C "$probe" add ontology ;;
	esac
	expect_refusal "$case_name" 'ontology manifest is missing: tracked ontology content requires ontology/manifest.yaml'
done

new_probe valid
printf 'manifest\n' >"$probe/ontology/manifest.yaml"
git -C "$probe" add ontology
run_probe || fail "materialized tree should run the ROCS gate: $(cat "$probe.log")"
printf 'version\ncleanup\nvalidate\nbuild\n' >"$probe.expected"
cmp -s "$probe.expected" "$probe/ontology-gate-calls.log" || fail "materialized tree must run ROCS version, cleanup, validate, build in order"

new_probe symlink
printf 'manifest\n' >"$probe/manifest.yaml"
ln -s ../manifest.yaml "$probe/ontology/manifest.yaml"
git -C "$probe" add ontology
expect_refusal symlink 'ontology manifest may not be a symlink'

new_probe gitlink
# A real commit object is needed to admit a gitlink into this disposable index.
git -C "$probe" -c user.name=Fixture -c user.email=fixture@example.invalid -c core.hooksPath=/dev/null -c commit.gpgsign=false commit --allow-empty -qm fixture
commit="$(git -C "$probe" rev-parse HEAD)"
git -C "$probe" update-index --add --cacheinfo "160000,$commit,ontology"
expect_refusal gitlink 'ontology is not materialized'

new_probe non-repository
mv "$probe/.git" "$probe.saved-git"
expect_refusal non-repository 'could not inspect tracked ontology content'

new_probe corrupt-index
printf 'invalid index\n' >"$probe/.git/index"
expect_refusal corrupt-index 'could not inspect tracked ontology content'

echo "ok: l1 ontology manifest gate (15 cases)"
