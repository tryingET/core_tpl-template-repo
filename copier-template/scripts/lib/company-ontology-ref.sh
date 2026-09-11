#!/usr/bin/env sh
# Answer/default handling for the L1 -> L2 wrapper. Never evaluate answer text.

yaml_scalar_from_answers() {
  answers_file="$1"
  key="$2"
  value=""
  status=0

  value="$(copier_answers_try_scalar "$answers_file" "$key" 2>/dev/null)" || status=$?

  if [ "$status" -eq 0 ]; then
    printf '%s\n' "$value"
    return 0
  fi

  echo "error: unable to parse '$key' from $answers_file; install python3/python with PyYAML for multiline or escaped Copier answers" >&2
  return "$status"
}

read_inherited_value() {
  answers_file="$1"
  key="$2"

  value="$(yaml_scalar_from_answers "$answers_file" "$key")"
  [ -n "$value" ] || return 0

  printf '%s\n' "$value" | tr '[:upper:]' '[:lower:]'
}

read_inherited_string() {
  answers_file="$1"
  key="$2"

  yaml_scalar_from_answers "$answers_file" "$key"
}

company_ontology_python() {
  if python_bin="$(copier_answers__python_with_yaml)"; then
    "$python_bin" "$@"
  elif command -v uvx >/dev/null 2>&1; then
    uvx --from "copier==${COPIER_VERSION}" python "$@"
  elif command -v uv >/dev/null 2>&1; then
    uv tool run --from "copier==${COPIER_VERSION}" python "$@"
  else
    echo "error: reading company ontology defaults requires Python with PyYAML or the pinned Copier runtime" >&2
    return 2
  fi
}

company_ontology_ref_default() {
  # Validate CLI values too, but leave explicit -d/--data-file precedence to Copier.
  company_ontology_python - "$answers_file" "$dest_dir" \
    "$repo_root/copier/$template_name/copier.yml" "$@" <<'PY'
import sys
from pathlib import Path
import yaml

key = "company_ontology_ref"
l1, destination, template, *args = sys.argv[1:]
answers = ".copier-answers.yml"
data_files = []
cli_data = {}


def validate(value, source):
    if value is not None and not isinstance(value, str):
        raise ValueError(f"{source}: {key} must be a string")
    # The existing project manifest emits a double-quoted YAML scalar. Single
    # quotes and shell metacharacters are literal; escapes/control bytes are not.
    if isinstance(value, str) and ('"' in value or "\\" in value or (value and not value.isprintable())):
        raise ValueError(f"{source}: {key} must be printable, without double quotes or backslashes")


def load(path, optional=False):
    path = Path(path)
    if optional and not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"{path}: answers must be a mapping")
    validate(data.get(key), path)
    return data


try:
    # Consume option values so a value resembling an option is never reinterpreted.
    options = iter(args)
    for arg in options:
        if arg in ("-a", "--answers-file", "--data-file"):
            value = next(options)
            if not value or value.startswith("-"):
                raise ValueError(f"{arg} requires a path")
            if arg == "--data-file":
                data_files.append(value)
            else:
                answers = value
        elif arg.startswith("--answers-file="):
            answers = arg.split("=", 1)[1]
        elif arg.startswith("-a"):
            answers = arg[2:]
        elif arg.startswith("--data-file="):
            data_files.append(arg.split("=", 1)[1])
        elif arg in ("-d", "--data") or arg.startswith(("-d", "--data=")):
            value = next(options) if arg in ("-d", "--data") else (
                arg[2:] if arg.startswith("-d") else arg.split("=", 1)[1]
            )
            name, value = value.split("=", 1)
            cli_data[name] = value
        elif arg in ("-r", "--vcs-ref", "-s", "--skip", "-x", "--exclude"):
            next(options)
    if not answers:
        raise ValueError("--answers-file requires a path")
    # Data files are explicit CLI input too, including a deliberately empty value.
    explicit = {}
    for path in data_files:
        explicit.update(load(path))
    explicit.update(cli_data)
    validate(explicit.get(key), "CLI input")
    if key not in explicit:
        stored = load(Path(destination) / answers, optional=True)
        selected = stored.get(key) or load(l1, optional=True).get(key)
        emit = bool(selected) or key in stored
        if not selected:
            # Copier otherwise retains an empty stored answer under --defaults.
            # Read (do not change or duplicate) the existing archetype fallback.
            config = yaml.safe_load(Path(template).read_text(encoding="utf-8"))
            slug = cli_data.get("company_slug", explicit.get(
                "company_slug", stored.get("company_slug", config["company_slug"]["default"])
            ))
            selected = config[key]["default"].replace("{{ company_slug }}", str(slug))
            if "{{" in selected or "{%" in selected:
                raise ValueError("unsupported archetype ontology default expression")
        validate(selected, "resolved default")
        if emit:
            sys.stdout.write(selected)
except (OSError, ValueError, yaml.YAMLError, StopIteration) as exc:
    print(f"error: unable to resolve {key}: {exc}", file=sys.stderr)
    raise SystemExit(2)
PY
}
