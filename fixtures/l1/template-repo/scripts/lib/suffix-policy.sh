#!/usr/bin/env sh

# Shared helpers for enforcing multi-pass Copier suffix boundaries.
# Intended to be sourced by guardrail scripts.

first_suffix_match() {
  search_root="$1"
  suffix_glob="$2"
  exclude_glob="${3:-}"

  if [ -n "$exclude_glob" ]; then
    find "$search_root" -type f -name "$suffix_glob" ! -path "$exclude_glob" ! -path '*/.git/*' | LC_ALL=C sort | awk 'NR==1{print;exit}'
    return
  fi

  find "$search_root" -type f -name "$suffix_glob" ! -path '*/.git/*' | LC_ALL=C sort | awk 'NR==1{print;exit}'
}

yaml_scalar_value() {
  yaml_file="$1"
  key="$2"

  awk -v key="$key" '
    {
      if ($0 ~ "^[[:space:]]*#") {
        next
      }

      if ($0 ~ "^[[:space:]]*" key "[[:space:]]*:") {
        value = substr($0, index($0, ":") + 1)
        sub(/^[[:space:]]+/, "", value)
        sub(/[[:space:]]+#.*$/, "", value)
        sub(/[[:space:]]+$/, "", value)

        if (value ~ /^".*"$/) {
          value = substr(value, 2, length(value) - 2)
        } else if (value ~ /^\047.*\047$/) {
          value = substr(value, 2, length(value) - 2)
        }

        print value
        exit
      }
    }
  ' "$yaml_file"
}

first_untemplated_jinja_match() {
  search_root="$1"
  template_suffix="$2"

  # Detect Jinja markers while ignoring common non-Jinja patterns like GitHub
  # expression syntax (${ {... }}) and vendored tools (Python f-string escapes {{ }}).
  find "$search_root" -type f ! -name "*${template_suffix}" ! -path '*/.git/*' ! -path '*/tools/*' \
    -exec grep -I -l -m 1 -E '(^|[^$])\{\{|(^|[^$])\{%|\{#' {} + 2>/dev/null \
    | LC_ALL=C sort \
    | awk 'NR==1{print;exit}'
}

self_test_untemplated_jinja_matcher() {
  tmp_dir="$(mktemp -d)"
  gh_expr_file="$tmp_dir/gh-expression.yml"
  jinja_file="$tmp_dir/jinja-template.txt"

  printf 'if: ${{ github.ref == "refs/heads/main" }}\n' > "$gh_expr_file"
  printf 'repo_slug: {{ repo_slug }}\n' > "$jinja_file"

  matched_file="$(first_untemplated_jinja_match "$tmp_dir" ".j2")"
  rm -rf "$tmp_dir"

  [ "$matched_file" = "$jinja_file" ]
}
