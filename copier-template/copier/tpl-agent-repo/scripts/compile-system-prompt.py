#!/usr/bin/env python3
"""Validate agent.json and compile the system prompt from canonical inputs."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

PERSONA_FILES = (
    "README.md",
    "identity.md",
    "reason.md",
    "main_task.md",
    "dream_goal.md",
    "behavior_rules.md",
)
OUTPUT = Path("docs/person/system-prompt.md")
SCHEMA = "ai-society.agent/1"
AK_TASK = re.compile(r"AK-[1-9][0-9]*\Z")


def require_nonempty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"agent.json {field} must be one non-empty string")
    return value


def require_string_list(value: Any, field: str) -> None:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        raise ValueError(f"agent.json {field} must be an array of non-empty strings")


def validate_manifest(manifest: Any) -> dict[str, Any]:
    if not isinstance(manifest, dict):
        raise ValueError("agent.json root must be an object")
    if manifest.get("schema") != SCHEMA:
        raise ValueError(f"agent.json schema must be {SCHEMA}")

    require_nonempty_string(manifest.get("name"), "name")
    require_nonempty_string(manifest.get("role"), "role")
    require_nonempty_string(manifest.get("version"), "version")
    creation_task = require_nonempty_string(manifest.get("creation_task"), "creation_task")
    if not AK_TASK.fullmatch(creation_task):
        raise ValueError("agent.json creation_task must match AK-<positive integer>")
    if manifest.get("system_prompt_file") != OUTPUT.as_posix():
        raise ValueError(f"agent.json system_prompt_file must be {OUTPUT}")

    skills = manifest.get("skills")
    if not isinstance(skills, dict):
        raise ValueError("agent.json skills must be an object")
    profile = skills.get("profile")
    if profile is not None and (not isinstance(profile, str) or not profile):
        raise ValueError("agent.json skills.profile must be null or a non-empty string")
    require_string_list(skills.get("extra"), "skills.extra")
    require_string_list(manifest.get("tools"), "tools")
    require_string_list(manifest.get("extensions"), "extensions")
    require_string_list(manifest.get("activities"), "activities")

    defaults = manifest.get("defaults")
    if not isinstance(defaults, dict):
        raise ValueError("agent.json defaults must be an object")
    model = defaults.get("model")
    if model is not None and (not isinstance(model, str) or not model):
        raise ValueError("agent.json defaults.model must be null or a non-empty string")
    require_nonempty_string(defaults.get("thinking"), "defaults.thinking")
    if not isinstance(manifest.get("scope"), dict):
        raise ValueError("agent.json scope must be an object")
    return manifest


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid agent.json: {exc}") from exc
    return validate_manifest(manifest)


def compile_prompt(root: Path) -> bytes:
    person_dir = root / "docs/person"
    manifest_path = root / "agent.json"
    missing = [str(person_dir / name) for name in PERSONA_FILES if not (person_dir / name).is_file()]
    if not manifest_path.is_file():
        missing.append(str(manifest_path))
    if missing:
        raise ValueError("missing canonical input(s): " + ", ".join(missing))

    manifest = load_manifest(manifest_path)
    parts = [
        "<!-- compiled: do not edit -->\n",
        "# Agent system prompt\n\n",
        "## Manifest\n\n",
        "```json\n",
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False),
        "\n```\n",
    ]
    for name in PERSONA_FILES:
        text = (person_dir / name).read_text(encoding="utf-8").rstrip("\n")
        parts.extend((f"\n## Persona source: {name}\n\n", text, "\n"))
    return "".join(parts).encode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if the compiled prompt is stale")
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        expected = compile_prompt(args.repo_root)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    output = args.repo_root / OUTPUT
    if args.check:
        actual = output.read_bytes() if output.is_file() else None
        if actual != expected:
            print(f"error: stale compiled prompt: {OUTPUT}", file=sys.stderr)
            print("hint: run ./scripts/compile-system-prompt.py", file=sys.stderr)
            return 1
        print("ok: manifest valid and compiled system prompt is current")
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(expected)
    print(f"wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
