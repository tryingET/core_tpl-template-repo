"""Strict Git delta schema and narrowly admissible topology overlaps."""

from __future__ import annotations

import re
from typing import Any

from l1_template_receipts import MAP_PATH, STATE_PATH

CONTROL_PATHS = {MAP_PATH.as_posix(), STATE_PATH.as_posix(), ".git"}
REGULAR_MODES = {"100644", "100755"}
MODES = {"000000", "100644", "100755", "120000", "160000"}
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")


def validate_rel(path: object, allow_controls: bool = False) -> str:
    if not isinstance(path, str) or not path or path.startswith("/") or "\\" in path:
        raise ValueError(f"invalid repository path: {path!r}")
    if any(part in {"", ".", "..", ".git"} for part in path.split("/")):
        raise ValueError(f"unsafe repository path: {path}")
    if path in CONTROL_PATHS and not allow_controls:
        raise ValueError(f"transition payload may not include control path: {path}")
    return path


def topology_overlap(parent: dict[str, Any], child: dict[str, Any]) -> bool:
    """Called only for strictly ancestor-related, individually validated entries."""
    if parent["new_mode"] == "160000" and child["new_mode"] == "000000":
        return True  # Existing tree-to-gitlink collapse.
    return (
        parent["old_mode"] == "160000"
        and parent["new_mode"] == "000000"
        and child["old_mode"] == "000000"
        and child["new_mode"] in REGULAR_MODES
    )


def validate_git_delta(value: object, allow_controls: bool = False) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise ValueError("git_delta must be a non-empty list")
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in value:
        if not isinstance(item, dict) or set(item) != {
            "path", "old_mode", "new_mode", "old_oid", "new_oid", "content_sha256"
        }:
            raise ValueError("each git_delta entry must use the exact six-field schema")
        path = validate_rel(item["path"], allow_controls)
        if path in seen:
            raise ValueError(f"duplicate git_delta path: {path}")
        seen.add(path)
        old_mode, new_mode = item["old_mode"], item["new_mode"]
        if old_mode not in MODES or new_mode not in MODES or old_mode == new_mode == "000000":
            raise ValueError(f"unsupported Git mode transition for {path}")
        for mode, oid in ((old_mode, item["old_oid"]), (new_mode, item["new_oid"])):
            if mode == "000000":
                if oid is not None:
                    raise ValueError(f"absent side must use null OID for {path}")
            elif not isinstance(oid, str) or not HEX40.fullmatch(oid):
                raise ValueError(f"present side requires full Git OID for {path}")
        content = item["content_sha256"]
        if new_mode in {"100644", "100755", "120000"}:
            if not isinstance(content, str) or not HEX64.fullmatch(content):
                raise ValueError(f"file/symlink delta requires content_sha256 for {path}")
        elif content is not None:
            raise ValueError(f"gitlink/deletion content_sha256 must be null for {path}")
        for prior in result:
            if path.startswith(prior["path"] + "/"):
                parent, child = prior, item
            elif prior["path"].startswith(path + "/"):
                parent, child = item, prior
            else:
                continue
            if not topology_overlap(parent, child):
                raise ValueError(f"ancestor-ambiguous git_delta paths: {prior['path']}, {path}")
        result.append(dict(item, path=path))
    return sorted(result, key=lambda item: item["path"])
