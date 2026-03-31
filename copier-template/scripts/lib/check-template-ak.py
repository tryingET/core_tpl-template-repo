#!/usr/bin/env python3
"""Deterministic AK test double for template CI.

This helper implements the narrow Agent Kernel surface exercised by
scripts/check-template-ci.sh so template regression coverage does not depend on
an ambient `ak` installation being present on PATH.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any


def die(message: str, code: int = 1) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(code)


def resolve_repo(path: str) -> str:
    return str(Path(path).resolve())


def write_json(path: str, payload: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = target.with_suffix(target.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=True)
        handle.write("\n")
    tmp_path.replace(target)


def init_db(path: str) -> None:
    write_json(
        path,
        {
            "next_task_id": 1,
            "repos": {},
            "tasks": {},
        },
    )


def load_db(path: str) -> dict[str, Any]:
    db_path = Path(path)
    if not db_path.exists():
        die(f"AK test DB not initialized: {path}")
    with db_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_db(path: str, payload: dict[str, Any]) -> None:
    write_json(path, payload)


def parse_global(argv: list[str]) -> tuple[str, list[str]]:
    db_path = os.environ.get("AK_DB")
    rest = list(argv)

    while rest:
        token = rest[0]
        if token == "-d":
            if len(rest) < 2:
                die("-d requires a DB path", code=2)
            db_path = rest[1]
            rest = rest[2:]
            continue
        if token.startswith("-d="):
            db_path = token[3:]
            rest = rest[1:]
            continue
        break

    if not rest:
        die("missing AK command", code=2)
    if not db_path:
        db_path = str(Path.cwd() / ".ak-test-double.json")
    return db_path, rest


def require_task(db: dict[str, Any], task_id: str) -> dict[str, Any]:
    task = db["tasks"].get(str(task_id))
    if task is None:
        die(f"unknown task id: {task_id}")
    return task


def parse_named_args(argv: list[str]) -> tuple[dict[str, str], list[str]]:
    parsed: dict[str, str] = {}
    extras: list[str] = []
    i = 0
    while i < len(argv):
        token = argv[i]
        if token.startswith("--"):
            if i + 1 >= len(argv):
                die(f"missing value for {token}", code=2)
            parsed[token] = argv[i + 1]
            i += 2
            continue
        extras.append(token)
        i += 1
    return parsed, extras


def cmd_repo(db_path: str, argv: list[str]) -> None:
    if not argv:
        die("missing repo subcommand", code=2)

    db = load_db(db_path)
    subcommand = argv[0]
    if subcommand == "show":
        if len(argv) != 2:
            die("usage: repo show <repo-path>", code=2)
        repo_path = resolve_repo(argv[1])
        repo = db["repos"].get(repo_path)
        if repo is None:
            raise SystemExit(1)
        print(json.dumps({"company": repo.get("company", ""), "repo": repo_path}, indent=2, sort_keys=True))
        return

    if subcommand == "register":
        parsed, extras = parse_named_args(argv[1:])
        if len(extras) != 1:
            die("usage: repo register <repo-path> --company <slug>", code=2)
        repo_path = resolve_repo(extras[0])
        company = parsed.get("--company", "")
        db["repos"][repo_path] = {"company": company}
        save_db(db_path, db)
        print(f"Registered repo: {repo_path}")
        return

    die(f"unsupported repo subcommand: {subcommand}", code=2)


def cmd_task(db_path: str, argv: list[str]) -> None:
    if not argv:
        die("missing task subcommand", code=2)

    db = load_db(db_path)
    subcommand = argv[0]

    if subcommand == "create":
        parsed, extras = parse_named_args(argv[1:])
        repo_value = parsed.get("--repo")
        if not repo_value or not extras:
            die("usage: task create --repo <repo-path> <title>", code=2)
        repo_path = resolve_repo(repo_value)
        if repo_path not in db["repos"]:
            die(f"repo not registered: {repo_path}")
        task_id = str(db["next_task_id"])
        db["next_task_id"] += 1
        title = " ".join(extras)
        db["tasks"][task_id] = {
            "id": int(task_id),
            "repo": repo_path,
            "scope": {"allowed": [], "required": []},
            "title": title,
        }
        save_db(db_path, db)
        print(f"Created task {task_id}: {title}")
        return

    if subcommand == "show":
        if len(argv) < 2:
            die("usage: task show <task-id> [-F json]", code=2)
        task = require_task(db, argv[1])
        payload = {
            "id": task["id"],
            "repo": task["repo"],
            "scope": task["scope"],
            "title": task["title"],
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return

    if subcommand == "scope":
        if len(argv) < 2:
            die("missing task scope subcommand", code=2)
        scope_subcommand = argv[1]

        if scope_subcommand == "set":
            if len(argv) < 3:
                die("usage: task scope set <task-id> [--allowed ...] [--required ...]", code=2)
            task = require_task(db, argv[2])
            allowed: list[str] = []
            required: list[str] = []
            target: list[str] | None = None
            for token in argv[3:]:
                if token == "--allowed":
                    target = allowed
                    continue
                if token == "--required":
                    target = required
                    continue
                if target is None:
                    die(f"unexpected token in task scope set: {token}", code=2)
                target.append(token)
            task["scope"] = {"allowed": allowed, "required": required}
            save_db(db_path, db)
            print(f"Updated task scope: {task['id']}")
            return

        if scope_subcommand == "export":
            if len(argv) != 3:
                die("usage: task scope export <task-id>", code=2)
            task = require_task(db, argv[2])
            payload = {
                "allowed": task["scope"].get("allowed", []),
                "commit_sha": "ak-test-double",
                "exported_at": "1970-01-01T00:00:00Z",
                "repo": task["repo"],
                "required": task["scope"].get("required", []),
                "schema_version": 1,
                "task_id": task["id"],
            }
            print(json.dumps(payload, indent=2, sort_keys=True))
            return

        die(f"unsupported task scope subcommand: {scope_subcommand}", code=2)

    die(f"unsupported task subcommand: {subcommand}", code=2)


def work_items_projection(repo_value: str, owner: str, project_name: str) -> dict[str, Any]:
    _ = resolve_repo(repo_value)
    return {
        "schema_version": 1,
        "updated_at": "1970-01-01",
        "owner": owner,
        "project_name": project_name,
        "milestones": [],
    }


def cmd_work_items(argv: list[str]) -> None:
    if not argv:
        die("missing work-items subcommand", code=2)

    subcommand = argv[0]
    parsed, extras = parse_named_args(argv[1:])
    if extras:
        die(f"unexpected work-items arguments: {' '.join(extras)}", code=2)

    repo_value = parsed.get("--repo")
    path_value = parsed.get("--path")
    owner = parsed.get("--owner", "")
    project_name = parsed.get("--project-name", "")
    if not repo_value or not path_value:
        die("work-items commands require --repo and --path", code=2)

    payload = work_items_projection(repo_value, owner, project_name)
    output_path = Path(path_value)

    if subcommand == "export":
        write_json(str(output_path), payload)
        print(f"Exported work-items projection: {output_path}")
        return

    if subcommand == "check":
        if not output_path.exists():
            die(f"work-items projection not found: {output_path}")
        with output_path.open("r", encoding="utf-8") as handle:
            current = json.load(handle)
        if current != payload:
            die(f"work-items projection drift detected: {output_path}")
        print(f"ok: work-items projection ({output_path})")
        return

    if subcommand == "import":
        if not output_path.exists():
            die(f"work-items projection not found: {output_path}")
        with output_path.open("r", encoding="utf-8") as handle:
            json.load(handle)
        print(f"Imported work-items projection: {output_path}")
        return

    die(f"unsupported work-items subcommand: {subcommand}", code=2)


def main(argv: list[str]) -> None:
    db_path, rest = parse_global(argv)
    command = rest[0]

    if command == "init":
        if len(rest) != 1:
            die("usage: init", code=2)
        init_db(db_path)
        print(f"Initialized AK test DB: {db_path}")
        return

    if command == "repo":
        cmd_repo(db_path, rest[1:])
        return

    if command == "task":
        cmd_task(db_path, rest[1:])
        return

    if command == "work-items":
        cmd_work_items(rest[1:])
        return

    die(f"unsupported AK command: {command}", code=2)


if __name__ == "__main__":
    main(sys.argv[1:])
