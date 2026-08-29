#!/usr/bin/env python3
"""Plan or apply a fresh template render to template-owned paths only."""

from __future__ import annotations

import argparse
import difflib
import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path

MAP_PATH = Path("contracts/template-ownership.yml")
SCHEMA = "ai-society.template-ownership/1"
IGNORED_PARTS = {".git", "__pycache__"}


def files(root: Path) -> set[str]:
    found: set[str] = set()
    for path in root.rglob("*"):
        rel = path.relative_to(root)
        if any(part in IGNORED_PARTS for part in rel.parts):
            continue
        if path.is_file() or path.is_symlink():
            found.add(rel.as_posix())
    return found


def matches(path: str, pattern: str) -> bool:
    if pattern.endswith("/**"):
        prefix = pattern[:-3].rstrip("/")
        return path == prefix or path.startswith(prefix + "/")
    return path == pattern


def patterns_overlap(left: str, right: str) -> bool:
    left_prefix = left[:-3].rstrip("/") if left.endswith("/**") else None
    right_prefix = right[:-3].rstrip("/") if right.endswith("/**") else None
    if left_prefix is None and right_prefix is None:
        return left == right
    if left_prefix is not None and right_prefix is not None:
        return (
            left_prefix == right_prefix
            or left_prefix.startswith(right_prefix + "/")
            or right_prefix.startswith(left_prefix + "/")
        )
    if left_prefix is not None:
        return right == left_prefix or right.startswith(left_prefix + "/")
    return left == right_prefix or left.startswith(right_prefix + "/")


def load_map(root: Path) -> dict[str, list[str]]:
    path = root / MAP_PATH
    schema = ""
    sections: dict[str, list[str]] = {"template_owned": [], "agent_owned": []}
    active: str | None = None
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if raw == line and line.startswith("schema:"):
            schema = line.split(":", 1)[1].strip()
            active = None
            continue
        if raw == line and line.endswith(":") and line[:-1] in sections:
            active = line[:-1]
            continue
        if active and raw.startswith("  - "):
            pattern = raw[4:].strip()
            if not pattern or pattern.startswith("/") or ".." in Path(pattern).parts:
                raise ValueError(f"invalid ownership pattern at {MAP_PATH}:{number}: {pattern!r}")
            sections[active].append(pattern)
            continue
        raise ValueError(f"unsupported ownership syntax at {MAP_PATH}:{number}")

    if schema != SCHEMA:
        raise ValueError(f"unsupported ownership schema in {MAP_PATH}")
    if not sections["template_owned"] or not sections["agent_owned"]:
        raise ValueError("ownership map requires non-empty template_owned and agent_owned lists")
    for section, patterns in sections.items():
        if len(patterns) != len(set(patterns)):
            raise ValueError(f"duplicate pattern in {section}")
    for template_pattern in sections["template_owned"]:
        for agent_pattern in sections["agent_owned"]:
            if patterns_overlap(template_pattern, agent_pattern):
                raise ValueError(
                    f"ambiguous ownership patterns: {template_pattern} and {agent_pattern}"
                )
    return {"template": sections["template_owned"], "agent": sections["agent_owned"]}


def owner(path: str, mapping: dict[str, list[str]]) -> str | None:
    kinds = [kind for kind, patterns in mapping.items() if any(matches(path, item) for item in patterns)]
    if len(kinds) > 1:
        raise ValueError(f"ambiguous ownership for {path}: {', '.join(kinds)}")
    return kinds[0] if kinds else None


def source_from_answers(path: Path) -> str:
    values = [raw.split(":", 1)[1].strip() for raw in path.read_text(encoding="utf-8").splitlines() if raw.startswith("_src_path:")]
    if len(values) != 1:
        raise ValueError(".copier-answers.yml must contain exactly one scalar _src_path")
    raw = values[0]
    if not raw or raw[0] in "!&*|>{[":
        raise ValueError(".copier-answers.yml _src_path uses unsupported YAML syntax")
    if raw.startswith('"'):
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError("invalid double-quoted _src_path") from exc
    elif raw.startswith("'"):
        if len(raw) < 2 or not raw.endswith("'"):
            raise ValueError("invalid single-quoted _src_path")
        value = raw[1:-1].replace("''", "'")
    else:
        if " #" in raw:
            raise ValueError("inline comments are unsupported for _src_path")
        value = raw
    if not isinstance(value, str) or not value:
        raise ValueError(".copier-answers.yml _src_path must be a non-empty string")
    return value


def copier_command() -> list[str]:
    if shutil.which("uvx"):
        return ["uvx", "--from", "copier==9.11.1", "copier"]
    if shutil.which("uv"):
        return ["uv", "tool", "run", "--from", "copier==9.11.1", "copier"]
    if shutil.which("copier"):
        print("warning: using unpinned copier from PATH", file=sys.stderr)
        return ["copier"]
    raise ValueError("missing copier (or uvx/uv)")


def render(repo: Path, source_override: str | None, destination: Path) -> None:
    answers = repo / ".copier-answers.yml"
    source_value = source_override or source_from_answers(answers)
    source_path = Path(source_value).expanduser()
    if not source_path.is_absolute():
        base = Path.cwd() if source_override else repo
        source_path = (base / source_path).resolve()
    if not source_path.is_dir():
        raise ValueError(f"template source is not a directory: {source_path}")

    shutil.copy2(answers, destination / ".copier-answers.yml")
    command = copier_command() + [
        "copy",
        "--skip-tasks",
        "--trust",
        "--defaults",
        "--overwrite",
        "--quiet",
        "-a",
        ".copier-answers.yml",
        str(source_path),
        str(destination),
    ]
    subprocess.run(command, check=True)


def same(left: Path, right: Path) -> bool:
    if left.is_symlink() or right.is_symlink():
        return left.is_symlink() and right.is_symlink() and os.readlink(left) == os.readlink(right)
    return left.read_bytes() == right.read_bytes() and stat.S_IMODE(left.stat().st_mode) == stat.S_IMODE(right.stat().st_mode)


def show_diff(path: str, old: Path | None, new: Path | None) -> None:
    if (old and old.is_symlink()) or (new and new.is_symlink()):
        before = os.readlink(old) if old and old.is_symlink() else ""
        after = os.readlink(new) if new and new.is_symlink() else ""
        print(f"symlink change: {path}: {before!r} -> {after!r}")
        return
    before = old.read_bytes() if old and old.is_file() else b""
    after = new.read_bytes() if new and new.is_file() else b""
    try:
        left = before.decode("utf-8").splitlines(keepends=True)
        right = after.decode("utf-8").splitlines(keepends=True)
    except UnicodeDecodeError:
        print(f"binary change: {path}")
        return
    sys.stdout.writelines(difflib.unified_diff(left, right, f"a/{path}", f"b/{path}"))


def copy_entry(source: Path, destination: Path) -> None:
    if source.is_symlink():
        raise ValueError(f"rendered template symlinks are unsupported: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() or destination.is_symlink():
        destination.unlink()
    shutil.copy2(source, destination)


def classify_all(paths: set[str], mapping: dict[str, list[str]], label: str) -> None:
    for path in sorted(paths):
        if owner(path, mapping) is None:
            top = path.split("/", 1)[0]
            raise ValueError(
                f"unclassified {label} path: {path} (top level: {top}); update {MAP_PATH} explicitly"
            )


def ensure_safe_destinations(repo: Path, actions: list[tuple[str, str]]) -> None:
    repo_resolved = repo.resolve()
    for _, path in actions:
        destination = repo / path
        try:
            destination.relative_to(repo)
        except ValueError as exc:
            raise ValueError(f"propagation destination escapes repository: {path}") from exc
        cursor = repo
        for part in Path(path).parts[:-1]:
            cursor /= part
            if cursor.is_symlink():
                raise ValueError(f"refusing symlinked destination ancestor for {path}: {cursor}")
        resolved_parent = destination.parent.resolve(strict=False)
        try:
            resolved_parent.relative_to(repo_resolved)
        except ValueError as exc:
            raise ValueError(f"propagation destination resolves outside repository: {path}") from exc


def propagate(repo: Path, rendered: Path, apply: bool) -> int:
    current_map = load_map(repo)
    next_map = load_map(rendered)
    current_files = files(repo)
    rendered_files = files(rendered)
    classify_all(current_files, current_map, "existing")
    classify_all(rendered_files, next_map, "rendered")
    for path in sorted(rendered_files):
        if (rendered / path).is_symlink():
            raise ValueError(f"rendered template symlinks are unsupported: {path}")

    for path in sorted(current_files):
        if owner(path, current_map) == "agent" and owner(path, next_map) != "agent":
            raise ValueError(f"refusing ownership change for agent-owned path: {path}")

    actions: list[tuple[str, str]] = []
    for path in sorted(rendered_files):
        if owner(path, next_map) != "template":
            continue
        if path in current_files and owner(path, current_map) != "template":
            raise ValueError(f"refusing to replace non-template-owned path: {path}")
        if path not in current_files:
            actions.append(("add", path))
        elif not same(repo / path, rendered / path):
            actions.append(("update", path))
    for path in sorted(current_files - rendered_files):
        if owner(path, current_map) == "template":
            actions.append(("delete", path))

    ensure_safe_destinations(repo, actions)

    if not actions:
        print("ok: template-owned paths are current")
        return 0

    print("APPLY" if apply else "PLAN (no files changed; pass --apply to apply)")
    for action, path in actions:
        print(f"{action}: {path}")
        show_diff(path, repo / path if path in current_files else None, rendered / path if path in rendered_files else None)
    if apply:
        for action, path in actions:
            destination = repo / path
            if action == "delete":
                destination.unlink()
            else:
                copy_entry(rendered / path, destination)
        print("applied template-owned changes; review the repository diff")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--source", help="override _src_path after moving the current L1 template repo")
    parser.add_argument("--rendered", type=Path, help="use an already-rendered tree (test/debug only)")
    parser.add_argument("--apply", action="store_true", help="apply the displayed template-owned changes")
    args = parser.parse_args()
    repo = args.repo_root.resolve()
    try:
        if args.rendered:
            return propagate(repo, args.rendered.resolve(), args.apply)
        scratch_parent = Path(os.environ.get("TMPDIR", str(repo.parent))).expanduser()
        scratch_parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=".agent-template-render-", dir=scratch_parent) as temp:
            rendered = Path(temp)
            render(repo, args.source, rendered)
            return propagate(repo, rendered, args.apply)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
