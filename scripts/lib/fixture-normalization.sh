#!/usr/bin/env sh
set -eu

# Normalize volatile render metadata so fixture snapshots stay stable across runs.

normalize_fixture_tree_volatiles() {
  tree="$1"

  find "$tree" -type f -name '.copier-answers.yml' | while IFS= read -r answers_file; do
    normalized_file="${answers_file}.normalized"
    awk '
      /^_commit:/ {
        print "_commit: __VOLATILE_COMMIT__"
        next
      }
      /^_src_path:/ {
        print "_src_path: __VOLATILE_SRC_PATH__"
        next
      }
      /^l0_source_sha:/ {
        print "l0_source_sha: __VOLATILE_L0_SOURCE_SHA__"
        next
      }
      /^template_source_sha:/ {
        print "template_source_sha: __VOLATILE_TEMPLATE_SOURCE_SHA__"
        next
      }
      {
        print
      }
    ' "$answers_file" > "$normalized_file"
    mv "$normalized_file" "$answers_file"
  done

  find "$tree" -type f -name 'provenance-seal.yml' | while IFS= read -r seal_file; do
    normalized_file="${seal_file}.normalized"
    awk '
      /^[[:space:]]*source_sha:/ {
        sub(/source_sha:.*/, "source_sha: \"__VOLATILE_SOURCE_SHA__\"")
        print
        next
      }
      /^[[:space:]]*content_hash_sha256:/ {
        sub(/content_hash_sha256:.*/, "content_hash_sha256: \"__VOLATILE_CONTENT_HASH_SHA256__\"")
        print
        next
      }
      {
        print
      }
    ' "$seal_file" > "$normalized_file"
    mv "$normalized_file" "$seal_file"
  done
}
