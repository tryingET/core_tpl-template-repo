from __future__ import annotations

import yaml


LEGACY_ROCS_INCLUDE_PATH = "gitlab/ci/rocs.yml"


def ensure_trailing_newline(text: str) -> str:
    return text if text.endswith("\n") else text + "\n"


def _normalize_ci_include(value: object) -> list[object]:
    if value is None:
        return []
    if isinstance(value, list):
        return list(value)
    if isinstance(value, (dict, str)):
        return [value]
    raise ValueError("invalid .gitlab-ci.yml: top-level include must be a string, mapping, or list")


def _ci_include_has_rocs(entries: list[object]) -> bool:
    for entry in entries:
        if isinstance(entry, dict) and str(entry.get("local") or "") == LEGACY_ROCS_INCLUDE_PATH:
            return True
        if isinstance(entry, str) and entry.strip().strip("\"'") == LEGACY_ROCS_INCLUDE_PATH:
            return True
    return False


def _is_rocs_include_scalar(value: str) -> bool:
    return value.strip().strip("\"'") == LEGACY_ROCS_INCLUDE_PATH


def _render_inline_include(entries: list[object]) -> str:
    rendered = yaml.safe_dump(entries, sort_keys=False, default_flow_style=True).strip()
    return f"include: {rendered}"


def _filter_inline_include_value(value: str) -> tuple[str | None, bool]:
    stripped = value.strip()
    if not stripped:
        return None, False
    if _is_rocs_include_scalar(stripped):
        return None, True
    if not stripped.startswith(("[", "{")):
        return None, False
    try:
        loaded = yaml.safe_load(stripped)
    except yaml.YAMLError:
        return None, False
    if isinstance(loaded, dict):
        if _ci_include_has_rocs([loaded]):
            return None, True
        return None, False
    if not isinstance(loaded, list):
        return None, False
    filtered = [entry for entry in loaded if not _ci_include_has_rocs([entry])]
    if len(filtered) == len(loaded):
        return None, False
    if not filtered:
        return None, True
    return _render_inline_include(filtered), True


def _leading_spaces(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


def _remove_rocs_include_textually(text: str) -> str | None:
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    changed = False

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if _leading_spaces(line) == 0 and stripped.startswith("include:"):
            inline_value = stripped[len("include:") :].strip()
            if inline_value:
                rewritten, handled = _filter_inline_include_value(inline_value)
                if handled:
                    changed = True
                    if rewritten is not None:
                        newline = "\n" if line.endswith("\n") else ""
                        out.append(rewritten + newline)
                    i += 1
                    continue
                out.append(line)
                i += 1
                continue

            j = i + 1
            block: list[str] = []
            while j < len(lines):
                current = lines[j]
                if current.strip() and _leading_spaces(current) == 0:
                    break
                block.append(current)
                j += 1

            kept: list[str] = []
            k = 0
            while k < len(block):
                current = block[k]
                stripped_current = current.strip()
                if not stripped_current:
                    if kept:
                        kept.append(current)
                    k += 1
                    continue
                if stripped_current.startswith("#"):
                    kept.append(current)
                    k += 1
                    continue

                if stripped_current.startswith("-"):
                    entry_lines = [current]
                    entry_indent = _leading_spaces(current)
                    k += 1
                    while k < len(block):
                        nxt = block[k]
                        nxt_stripped = nxt.strip()
                        nxt_indent = _leading_spaces(nxt)
                        if nxt_stripped and nxt_indent == entry_indent and nxt_stripped.startswith("-"):
                            break
                        entry_lines.append(nxt)
                        k += 1

                    first = stripped_current[1:].strip()
                    remove_entry = _is_rocs_include_scalar(first)
                    if not remove_entry and first.startswith("local:"):
                        remove_entry = _is_rocs_include_scalar(first.split(":", 1)[1])
                    if not remove_entry:
                        for entry_line in entry_lines[1:]:
                            entry_line_stripped = entry_line.strip()
                            if entry_line_stripped.startswith("local:") and _is_rocs_include_scalar(
                                entry_line_stripped.split(":", 1)[1]
                            ):
                                remove_entry = True
                                break
                    if remove_entry:
                        changed = True
                        continue
                    kept.extend(entry_lines)
                    continue

                if stripped_current.startswith("local:"):
                    if _is_rocs_include_scalar(stripped_current.split(":", 1)[1]):
                        changed = True
                        k += 1
                        continue

                kept.append(current)
                k += 1

            while kept and not kept[0].strip():
                kept.pop(0)
            while kept and not kept[-1].strip():
                kept.pop()

            if kept:
                out.append(line)
                out.extend(kept)
                if j < len(lines) and out and not out[-1].endswith("\n"):
                    out[-1] += "\n"
            else:
                changed = True
            i = j
            continue

        out.append(line)
        i += 1

    result = "".join(out)
    if not result.strip():
        return None
    return ensure_trailing_newline(result if changed else text)


def remove_rocs_include(text: str) -> str | None:
    if not text.strip():
        return None
    if LEGACY_ROCS_INCLUDE_PATH not in text:
        return ensure_trailing_newline(text)

    try:
        loaded = yaml.safe_load(text) or {}
    except yaml.YAMLError as exc:
        updated = _remove_rocs_include_textually(text)
        if updated == ensure_trailing_newline(text):
            raise ValueError(f"invalid .gitlab-ci.yml: {exc}") from exc
        return updated
    if not isinstance(loaded, dict):
        raise ValueError("invalid .gitlab-ci.yml: root must be a mapping")

    include_entries = _normalize_ci_include(loaded.get("include"))
    filtered = [entry for entry in include_entries if not _ci_include_has_rocs([entry])]
    if len(filtered) == len(include_entries):
        return ensure_trailing_newline(text)

    if filtered:
        loaded["include"] = filtered
    else:
        loaded.pop("include", None)

    if not loaded:
        return None
    return ensure_trailing_newline(yaml.safe_dump(loaded, sort_keys=False, allow_unicode=True))
