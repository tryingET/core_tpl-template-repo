#!/usr/bin/env python3
"""Declarative, fail-closed retirement of template files that L0 no longer renders.

The L0-owned manifest ``contracts/l1-template-retirements.json`` lists path patterns
together with the L0 commit and reason that retired them. A refresh plans a
``retire`` action for every target path that matches an entry, and apply deletes
exactly those paths. Nothing outside the manifest is ever deleted. Every candidate
must be template-owned by both the active and the incoming map, lie inside the
target (no symlinked ancestors), be a tracked regular file whose index and
worktree bytes equal HEAD, and must not be rendered again by L0. Untracked, dirty,
symlinked, gitlink or unclassified matches refuse the whole refresh.
"""

from __future__ import annotations

import hashlib
import json
import re
import stat
from pathlib import Path
from typing import Callable

from l1_template_gitlinks import inside
from l1_template_receipts import (
    ADOPTION_PATH, L0_ROOT, MAP_PATH, STATE_PATH, ensure_safe_destinations, git_run,
)

MANIFEST_PATH = L0_ROOT / "contracts/l1-template-retirements.json"
SCHEMA = "ai-society.l1-template-retirements/1"
ENTRY_KEYS = {"pattern", "retired_by", "reason"}
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
PROTECTED = {MAP_PATH.as_posix(), STATE_PATH.as_posix(), ADOPTION_PATH.as_posix(), ".copier-answers.yml", ".gitmodules"}
Classifier = Callable[[str, dict[str, list[str]]], "str | None"]


def compile_pattern(pattern: object) -> re.Pattern[str]:
    """``*`` matches within one path segment; a final ``/**`` matches one or more segments."""
    if not isinstance(pattern, str) or not pattern or pattern.startswith("/") or pattern.endswith("/"):
        raise ValueError(f"invalid retirement pattern: {pattern!r}")
    segments = pattern.split("/")
    subtree = segments[-1] == "**"
    if subtree:
        segments = segments[:-1]
    if not segments:
        raise ValueError(f"retirement subtree requires a directory: {pattern}")
    parts = []
    for segment in segments:
        if segment in {"", ".", "..", ".git"} or "**" in segment or any(char in segment for char in "?[]\\"):
            raise ValueError(f"unsupported retirement pattern segment in {pattern}: {segment!r}")
        parts.append("[^/]*".join(re.escape(piece) for piece in segment.split("*")))
    return re.compile("/".join(parts) + ("/.+" if subtree else "") + r"\Z")


def load_manifest(path: Path = MANIFEST_PATH) -> list[dict[str, object]]:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"retirement manifest must be a regular file: {path}")
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError("invalid retirement manifest JSON") from exc
    if not isinstance(manifest, dict) or set(manifest) != {"schema", "retirements"} or manifest["schema"] != SCHEMA:
        raise ValueError(f"retirement manifest must use exactly schema {SCHEMA} and retirements")
    entries = manifest["retirements"]
    if not isinstance(entries, list):
        raise ValueError("retirement manifest retirements must be a list")
    seen: set[str] = set()
    result = []
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != ENTRY_KEYS:
            raise ValueError("each retirement must use exactly pattern, retired_by and reason")
        pattern, commit, reason = entry["pattern"], entry["retired_by"], entry["reason"]
        regex = compile_pattern(pattern)
        if pattern in seen:
            raise ValueError(f"duplicate retirement pattern: {pattern}")
        seen.add(pattern)
        if any(regex.match(control) for control in PROTECTED):
            raise ValueError(f"retirement pattern may not match a control path: {pattern}")
        if not isinstance(commit, str) or not HEX40.fullmatch(commit):
            raise ValueError(f"retired_by must be a full lowercase L0 commit: {pattern}")
        if git_run(L0_ROOT, "merge-base", "--is-ancestor", commit, "HEAD").returncode != 0:
            raise ValueError(f"retired_by is not an L0 ancestor commit: {pattern}")
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError(f"retirement reason must be non-empty: {pattern}")
        result.append({"pattern": pattern, "retired_by": commit, "reason": reason.strip(), "regex": regex})
    return result


def dirty_paths(repo: Path) -> dict[str, str]:
    probe = git_run(repo, "status", "--porcelain=v1", "-z", "--untracked-files=all", "--ignore-submodules=none", "--no-renames")
    if probe.returncode != 0:
        raise ValueError("retirement requires a Git repository target")
    return {record[3:]: record[:2] for record in probe.stdout.split("\0") if len(record) > 3}


def head_entries(repo: Path) -> dict[str, tuple[str, str]]:
    probe = git_run(repo, "ls-tree", "-r", "-z", "--full-tree", "HEAD")
    if probe.returncode != 0:
        raise ValueError("retirement requires a committed HEAD")
    result = {}
    for record in probe.stdout.split("\0"):
        if record:
            meta, _, path = record.partition("\t")
            mode, _, oid = meta.split()
            result[path] = (mode, oid)
    return result


def blob_oid(path: Path, oid: str) -> str:
    data = path.read_bytes()
    algorithm = "sha1" if len(oid) == 40 else "sha256"
    return hashlib.new(algorithm, b"blob %d\0" % len(data) + data).hexdigest()


def plan(
    repo: Path,
    entries: dict[str, tuple[str, str]],
    rendered_paths: set[str],
    current_map: dict[str, list[str]],
    next_map: dict[str, list[str]],
    classify: Classifier,
    manifest: list[dict[str, object]] | None = None,
) -> dict[str, dict[str, str]]:
    """Return ``{path: {pattern, retired_by, reason, mode, oid}}``; sorted and deterministic."""
    manifest = load_manifest() if manifest is None else manifest
    if not manifest:
        return {}

    def entry_for(path: str) -> dict[str, object] | None:
        found = [item for item in manifest if item["regex"].match(path)]
        if len(found) > 1:
            raise ValueError(f"ambiguous retirement entries for {path}")
        return found[0] if found else None

    for path in sorted(rendered_paths):
        item = entry_for(path)
        if item is not None:
            raise ValueError(f"L0 still renders retired path {path} ({item['pattern']})")
    dirty = dirty_paths(repo)
    for path, code in sorted(dirty.items()):
        if entry_for(path) is not None:
            raise ValueError(f"refusing retirement of untracked or dirty path: {path} ({code.strip()})")
    head = head_entries(repo)
    candidates: dict[str, dict[str, str]] = {}
    for path in sorted(entries):
        item = entry_for(path)
        if item is None:
            continue
        mode, oid = entries[path]
        if mode not in {"100644", "100755"}:
            raise ValueError(f"retirement matches a non-regular tracked entry ({mode}): {path}")
        if head.get(path) != (mode, oid):
            raise ValueError(f"retirement path is staged differently from HEAD: {path}")
        if classify(path, current_map) != "template" or classify(path, next_map) != "template":
            raise ValueError(f"retirement requires active and incoming template ownership: {path}")
        candidates[path] = {
            "pattern": str(item["pattern"]), "retired_by": str(item["retired_by"]),
            "reason": str(item["reason"]), "mode": mode, "oid": oid,
        }
    ensure_safe_destinations(repo, list(candidates))
    for path, record in candidates.items():
        verify_file(repo, path, record)
    return candidates


def verify_file(repo: Path, path: str, record: dict[str, str]) -> None:
    destination = repo / path
    info = destination.lstat()
    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        raise ValueError(f"retirement path is not a single-link regular file: {path}")
    expected = 0o755 if record["mode"] == "100755" else 0o644
    if bool(info.st_mode & 0o111) != bool(expected & 0o111) or blob_oid(destination, record["oid"]) != record["oid"]:
        raise ValueError(f"retirement path drifted from its tracked bytes: {path}")


def retire(repo: Path, planned: dict[str, dict[str, str]]) -> None:
    """Delete the planned paths; each is re-verified immediately before unlinking."""
    ensure_safe_destinations(repo, list(planned))
    for path, record in planned.items():
        verify_file(repo, path, record)
    parents: set[Path] = set()
    for path in sorted(planned):
        (repo / path).unlink()
        parents.update((repo / path).parents)
    root = repo.resolve()
    for directory in sorted(parents, key=lambda item: len(item.parts), reverse=True):
        if directory.resolve() == root or not inside(directory.resolve().as_posix(), root.as_posix()):
            continue
        if directory.is_dir() and not directory.is_symlink() and not any(directory.iterdir()):
            directory.rmdir()


def report(planned: dict[str, dict[str, str]]) -> list[str]:
    """Deterministic plan lines: one ``retire-rule`` per manifest entry, then each path."""
    return summary(planned) + [
        f"retire: {path} (L0 {record['retired_by'][:12]}; {record['pattern']})" for path, record in planned.items()
    ]


def summary(planned: dict[str, dict[str, str]]) -> list[str]:
    counts: dict[tuple[str, str, str], int] = {}
    for record in planned.values():
        key = (record["pattern"], record["retired_by"], record["reason"])
        counts[key] = counts.get(key, 0) + 1
    return [
        f"retire-rule: {pattern} -> {count} path(s) (L0 {commit[:12]}: {reason})"
        for (pattern, commit, reason), count in sorted(counts.items())
    ]
