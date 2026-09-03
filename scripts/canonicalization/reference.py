#!/usr/bin/env python3
"""Reference implementation for ai-society canonicalization/1.

Zero-dependency except the Python standard library. This is a conformance
implementation, not an authority or approval service.
"""
from __future__ import annotations

import hashlib
import json
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SAFE_INT = 9_007_199_254_740_991


class CanonicalizationError(ValueError):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code


def _strict_utf8(data: bytes) -> str:
    if data.startswith(b"\xef\xbb\xbf"):
        raise CanonicalizationError("bom_forbidden", "UTF-8 BOM is forbidden")
    try:
        text = data.decode("utf-8", "strict")
    except UnicodeDecodeError as exc:
        raise CanonicalizationError("invalid_utf8", str(exc)) from exc
    if any(0xD800 <= ord(ch) <= 0xDFFF for ch in text):
        raise CanonicalizationError("invalid_surrogate", "surrogate code point is forbidden")
    return text


@dataclass
class JsonParser:
    text: str
    pos: int = 0

    def parse(self) -> Any:
        value = self._value()
        self._ws()
        if self.pos != len(self.text):
            raise CanonicalizationError("trailing_data", "trailing JSON data")
        return value

    def _ws(self) -> None:
        while self.pos < len(self.text) and self.text[self.pos] in " \t\r\n":
            self.pos += 1

    def _value(self) -> Any:
        self._ws()
        if self.pos >= len(self.text):
            raise CanonicalizationError("unexpected_eof", "expected JSON value")
        ch = self.text[self.pos]
        if ch == '"':
            return self._string()
        if ch == "{":
            return self._object()
        if ch == "[":
            return self._array()
        if ch == "t" and self.text.startswith("true", self.pos):
            self.pos += 4
            return True
        if ch == "f" and self.text.startswith("false", self.pos):
            self.pos += 5
            return False
        if ch == "n" and self.text.startswith("null", self.pos):
            self.pos += 4
            return None
        if ch == "-" or ch.isdigit():
            return self._integer()
        raise CanonicalizationError("invalid_json", f"unexpected character at {self.pos}")

    def _string(self) -> str:
        self.pos += 1
        out: list[str] = []
        while self.pos < len(self.text):
            ch = self.text[self.pos]
            self.pos += 1
            if ch == '"':
                value = unicodedata.normalize("NFC", "".join(out))
                if any(0xD800 <= ord(c) <= 0xDFFF for c in value):
                    raise CanonicalizationError("invalid_surrogate", "unpaired surrogate")
                return value
            if ch == "\\":
                if self.pos >= len(self.text):
                    raise CanonicalizationError("unexpected_eof", "unterminated escape")
                esc = self.text[self.pos]
                self.pos += 1
                simple = {'"': '"', "\\": "\\", "/": "/", "b": "\b", "f": "\f", "n": "\n", "r": "\r", "t": "\t"}
                if esc in simple:
                    out.append(simple[esc])
                    continue
                if esc != "u":
                    raise CanonicalizationError("invalid_json", "invalid escape")
                code = self._hex4()
                if 0xD800 <= code <= 0xDBFF:
                    if not self.text.startswith("\\u", self.pos):
                        raise CanonicalizationError("invalid_surrogate", "high surrogate without low surrogate")
                    self.pos += 2
                    low = self._hex4()
                    if not 0xDC00 <= low <= 0xDFFF:
                        raise CanonicalizationError("invalid_surrogate", "invalid low surrogate")
                    out.append(chr(0x10000 + ((code - 0xD800) << 10) + (low - 0xDC00)))
                elif 0xDC00 <= code <= 0xDFFF:
                    raise CanonicalizationError("invalid_surrogate", "low surrogate without high surrogate")
                else:
                    out.append(chr(code))
                continue
            if ord(ch) < 0x20:
                raise CanonicalizationError("invalid_json", "unescaped control character")
            if 0xD800 <= ord(ch) <= 0xDFFF:
                raise CanonicalizationError("invalid_surrogate", "surrogate code point")
            out.append(ch)
        raise CanonicalizationError("unexpected_eof", "unterminated string")

    def _hex4(self) -> int:
        if self.pos + 4 > len(self.text):
            raise CanonicalizationError("unexpected_eof", "short unicode escape")
        raw = self.text[self.pos:self.pos + 4]
        self.pos += 4
        try:
            return int(raw, 16)
        except ValueError as exc:
            raise CanonicalizationError("invalid_json", "invalid unicode escape") from exc

    def _integer(self) -> int:
        start = self.pos
        if self.text[self.pos] == "-":
            self.pos += 1
            if self.pos >= len(self.text):
                raise CanonicalizationError("invalid_number", "minus without digits")
        if self.text[self.pos] == "0":
            self.pos += 1
            if self.pos < len(self.text) and self.text[self.pos].isdigit():
                raise CanonicalizationError("invalid_number", "leading zero")
        elif self.text[self.pos] in "123456789":
            while self.pos < len(self.text) and self.text[self.pos].isdigit():
                self.pos += 1
        else:
            raise CanonicalizationError("invalid_number", "invalid integer")
        if self.pos < len(self.text) and self.text[self.pos] in ".eE":
            raise CanonicalizationError("non_integer_number", "only integers are allowed")
        token = self.text[start:self.pos]
        if token == "-0":
            raise CanonicalizationError("negative_zero", "negative zero is forbidden")
        value = int(token)
        if abs(value) > SAFE_INT:
            raise CanonicalizationError("integer_out_of_range", "integer exceeds interoperable range")
        return value

    def _array(self) -> list[Any]:
        self.pos += 1
        result: list[Any] = []
        self._ws()
        if self.pos < len(self.text) and self.text[self.pos] == "]":
            self.pos += 1
            return result
        while True:
            result.append(self._value())
            self._ws()
            if self.pos >= len(self.text):
                raise CanonicalizationError("unexpected_eof", "unterminated array")
            ch = self.text[self.pos]
            self.pos += 1
            if ch == "]":
                return result
            if ch != ",":
                raise CanonicalizationError("invalid_json", "expected comma")

    def _object(self) -> dict[str, Any]:
        self.pos += 1
        result: dict[str, Any] = {}
        self._ws()
        if self.pos < len(self.text) and self.text[self.pos] == "}":
            self.pos += 1
            return result
        while True:
            self._ws()
            if self.pos >= len(self.text) or self.text[self.pos] != '"':
                raise CanonicalizationError("invalid_json", "object key must be string")
            key = self._string()
            if key in result:
                raise CanonicalizationError("duplicate_key", f"duplicate key after NFC: {key}")
            self._ws()
            if self.pos >= len(self.text) or self.text[self.pos] != ":":
                raise CanonicalizationError("invalid_json", "expected colon")
            self.pos += 1
            result[key] = self._value()
            self._ws()
            if self.pos >= len(self.text):
                raise CanonicalizationError("unexpected_eof", "unterminated object")
            ch = self.text[self.pos]
            self.pos += 1
            if ch == "}":
                return result
            if ch != ",":
                raise CanonicalizationError("invalid_json", "expected comma")


def _escape(value: str) -> str:
    value = unicodedata.normalize("NFC", value)
    out = ['"']
    escapes = {'"': '\\"', "\\": "\\\\", "\b": "\\b", "\f": "\\f", "\n": "\\n", "\r": "\\r", "\t": "\\t"}
    for ch in value:
        if ch in escapes:
            out.append(escapes[ch])
        elif ord(ch) < 0x20:
            out.append(f"\\u{ord(ch):04x}")
        elif 0xD800 <= ord(ch) <= 0xDFFF:
            raise CanonicalizationError("invalid_surrogate", "surrogate code point")
        else:
            out.append(ch)
    out.append('"')
    return "".join(out)


def encode_canonical(value: Any) -> str:
    if value is None:
        return "null"
    if value is True:
        return "true"
    if value is False:
        return "false"
    if isinstance(value, int) and not isinstance(value, bool):
        if abs(value) > SAFE_INT:
            raise CanonicalizationError("integer_out_of_range", "integer exceeds interoperable range")
        return str(value)
    if isinstance(value, str):
        return _escape(value)
    if isinstance(value, list):
        return "[" + ",".join(encode_canonical(v) for v in value) + "]"
    if isinstance(value, dict):
        normalized: dict[str, Any] = {}
        for key, val in value.items():
            if not isinstance(key, str):
                raise CanonicalizationError("invalid_key", "JSON object key must be string")
            nkey = unicodedata.normalize("NFC", key)
            if nkey in normalized:
                raise CanonicalizationError("duplicate_key", f"duplicate key after NFC: {nkey}")
            normalized[nkey] = val
        keys = sorted(normalized, key=lambda k: k.encode("utf-8"))
        return "{" + ",".join(_escape(k) + ":" + encode_canonical(normalized[k]) for k in keys) + "}"
    raise CanonicalizationError("unsupported_json_type", type(value).__name__)


def canonical_json_bytes(data: bytes) -> bytes:
    text = _strict_utf8(data)
    value = JsonParser(text).parse()
    return encode_canonical(value).encode("utf-8")


def _canonical_path(raw: str) -> str:
    if not isinstance(raw, str):
        raise CanonicalizationError("invalid_path", "path must be string")
    if "\\" in raw:
        raise CanonicalizationError("backslash_path", "backslash path separator is forbidden")
    if raw.startswith("/") or raw.startswith("~"):
        raise CanonicalizationError("absolute_path", "physical/absolute path is forbidden")
    if "\x00" in raw:
        raise CanonicalizationError("invalid_path", "NUL in path")
    path = unicodedata.normalize("NFC", raw)
    parts = path.split("/")
    if not parts or any(part in ("", ".", "..") for part in parts):
        raise CanonicalizationError("path_traversal", "empty, dot, and dot-dot segments are forbidden")
    if any(any(0xD800 <= ord(ch) <= 0xDFFF for ch in part) for part in parts):
        raise CanonicalizationError("invalid_surrogate", "surrogate in path")
    return "/".join(parts)


def _canonical_text(data: bytes) -> bytes:
    text = _strict_utf8(data)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = unicodedata.normalize("NFC", text)
    return text.encode("utf-8")


def canonical_tree(entries: list[dict[str, Any]]) -> tuple[dict[str, Any], str]:
    files: list[dict[str, Any]] = []
    exact: set[str] = set()
    folded: dict[str, str] = {}
    for entry in entries:
        kind = entry.get("kind")
        if kind == "directory":
            continue
        if kind != "file":
            raise CanonicalizationError("special_file_forbidden", f"kind {kind!r} is forbidden")
        path = _canonical_path(entry.get("path"))
        if path in exact:
            raise CanonicalizationError("path_collision", f"duplicate path: {path}")
        folded_key = path.casefold()
        if folded_key in folded and folded[folded_key] != path:
            raise CanonicalizationError("case_collision", f"casefold collision: {folded[folded_key]} vs {path}")
        exact.add(path)
        folded[folded_key] = path
        mode = entry.get("mode")
        if mode not in ("0644", "0755"):
            raise CanonicalizationError("invalid_mode", "mode must be 0644 or 0755")
        try:
            raw = bytes.fromhex(entry.get("content_hex", ""))
        except ValueError as exc:
            raise CanonicalizationError("invalid_hex", "content_hex is invalid") from exc
        encoding = entry.get("content_encoding")
        if encoding == "utf8-text-v1":
            content = _canonical_text(raw)
        elif encoding == "binary-exact-v1":
            content = raw
        else:
            raise CanonicalizationError("invalid_content_encoding", "unknown content encoding")
        files.append({
            "content_digest": "sha256:" + hashlib.sha256(content).hexdigest(),
            "content_encoding": encoding,
            "mode": mode,
            "path": path,
            "size": len(content),
        })
    files.sort(key=lambda item: item["path"].encode("utf-8"))
    manifest = {"entries": files, "schema": "ai-society.canonical-tree/1"}
    payload = encode_canonical(manifest).encode("utf-8")
    return manifest, "sha256:" + hashlib.sha256(payload).hexdigest()


def evaluate_vector(vector: dict[str, Any]) -> dict[str, Any]:
    try:
        if vector["kind"] == "json":
            canonical = canonical_json_bytes(bytes.fromhex(vector["input_hex"]))
            return {
                "status": "ok",
                "canonical_hex": canonical.hex(),
                "digest": "sha256:" + hashlib.sha256(canonical).hexdigest(),
            }
        manifest, digest = canonical_tree(vector["entries"])
        return {"status": "ok", "manifest": manifest, "digest": digest}
    except CanonicalizationError as exc:
        return {"status": "error", "code": exc.code}


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: reference.py VECTORS.json", file=sys.stderr)
        return 2
    vectors = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    results = []
    failed = False
    for vector in vectors["vectors"]:
        actual = evaluate_vector(vector)
        expected = vector["expected"]
        ok = actual == expected
        failed = failed or not ok
        results.append({"id": vector["id"], "ok": ok, "actual": actual, "expected": expected})
    print(json.dumps({"implementation": "python", "results": results}, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
