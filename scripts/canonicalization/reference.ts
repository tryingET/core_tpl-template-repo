#!/usr/bin/env node
/* Reference implementation for ai-society canonicalization/1.
 * Zero runtime dependencies. This is conformance evidence, not authority.
 */
declare const require: (name: string) => any;
declare const process: { argv: string[]; exitCode?: number };
const crypto = require("node:crypto");
const fs = require("node:fs");
const SAFE_INT = 9_007_199_254_740_991;

class CanonicalizationError extends Error {
  code: string;
  constructor(code: string, message: string) {
    super(message);
    this.code = code;
  }
}

function strictUtf8(data: Uint8Array): string {
  if (data.length >= 3 && data[0] === 0xef && data[1] === 0xbb && data[2] === 0xbf) {
    throw new CanonicalizationError("bom_forbidden", "UTF-8 BOM is forbidden");
  }
  let text: string;
  try {
    text = new TextDecoder("utf-8", { fatal: true }).decode(data);
  } catch (error) {
    throw new CanonicalizationError("invalid_utf8", String(error));
  }
  for (let i = 0; i < text.length; i += 1) {
    const code = text.charCodeAt(i);
    if (code >= 0xd800 && code <= 0xdfff) {
      const next = text.charCodeAt(i + 1);
      if (code <= 0xdbff && next >= 0xdc00 && next <= 0xdfff) {
        i += 1;
      } else {
        throw new CanonicalizationError("invalid_surrogate", "unpaired surrogate");
      }
    }
  }
  return text;
}

class JsonParser {
  text: string;
  pos = 0;
  constructor(text: string) { this.text = text; }
  parse(): unknown {
    const value = this.value();
    this.ws();
    if (this.pos !== this.text.length) throw new CanonicalizationError("trailing_data", "trailing JSON data");
    return value;
  }
  ws(): void { while (this.pos < this.text.length && " \t\r\n".includes(this.text[this.pos])) this.pos += 1; }
  value(): unknown {
    this.ws();
    if (this.pos >= this.text.length) throw new CanonicalizationError("unexpected_eof", "expected JSON value");
    const ch = this.text[this.pos];
    if (ch === '"') return this.string();
    if (ch === "{") return this.object();
    if (ch === "[") return this.array();
    if (this.text.startsWith("true", this.pos)) { this.pos += 4; return true; }
    if (this.text.startsWith("false", this.pos)) { this.pos += 5; return false; }
    if (this.text.startsWith("null", this.pos)) { this.pos += 4; return null; }
    if (ch === "-" || /[0-9]/.test(ch)) return this.integer();
    throw new CanonicalizationError("invalid_json", `unexpected character at ${this.pos}`);
  }
  string(): string {
    this.pos += 1;
    let out = "";
    while (this.pos < this.text.length) {
      const ch = this.text[this.pos++];
      if (ch === '"') return out.normalize("NFC");
      if (ch === "\\") {
        if (this.pos >= this.text.length) throw new CanonicalizationError("unexpected_eof", "unterminated escape");
        const esc = this.text[this.pos++];
        const simple: Record<string, string> = { '"': '"', "\\": "\\", "/": "/", b: "\b", f: "\f", n: "\n", r: "\r", t: "\t" };
        if (Object.prototype.hasOwnProperty.call(simple, esc)) { out += simple[esc]; continue; }
        if (esc !== "u") throw new CanonicalizationError("invalid_json", "invalid escape");
        const high = this.hex4();
        if (high >= 0xd800 && high <= 0xdbff) {
          if (!this.text.startsWith("\\u", this.pos)) throw new CanonicalizationError("invalid_surrogate", "high surrogate without low surrogate");
          this.pos += 2;
          const low = this.hex4();
          if (low < 0xdc00 || low > 0xdfff) throw new CanonicalizationError("invalid_surrogate", "invalid low surrogate");
          out += String.fromCodePoint(0x10000 + ((high - 0xd800) << 10) + (low - 0xdc00));
        } else if (high >= 0xdc00 && high <= 0xdfff) {
          throw new CanonicalizationError("invalid_surrogate", "low surrogate without high surrogate");
        } else {
          out += String.fromCodePoint(high);
        }
        continue;
      }
      if (ch.charCodeAt(0) < 0x20) throw new CanonicalizationError("invalid_json", "unescaped control character");
      const code = ch.charCodeAt(0);
      if (code >= 0xd800 && code <= 0xdfff) {
        const next = this.text.charCodeAt(this.pos);
        if (code <= 0xdbff && next >= 0xdc00 && next <= 0xdfff) {
          out += ch + this.text[this.pos++];
        } else {
          throw new CanonicalizationError("invalid_surrogate", "unpaired surrogate");
        }
      } else out += ch;
    }
    throw new CanonicalizationError("unexpected_eof", "unterminated string");
  }
  hex4(): number {
    if (this.pos + 4 > this.text.length) throw new CanonicalizationError("unexpected_eof", "short unicode escape");
    const raw = this.text.slice(this.pos, this.pos + 4);
    this.pos += 4;
    if (!/^[0-9a-fA-F]{4}$/.test(raw)) throw new CanonicalizationError("invalid_json", "invalid unicode escape");
    return Number.parseInt(raw, 16);
  }
  integer(): number {
    const start = this.pos;
    if (this.text[this.pos] === "-") { this.pos += 1; if (this.pos >= this.text.length) throw new CanonicalizationError("invalid_number", "minus without digits"); }
    if (this.text[this.pos] === "0") {
      this.pos += 1;
      if (this.pos < this.text.length && /[0-9]/.test(this.text[this.pos])) throw new CanonicalizationError("invalid_number", "leading zero");
    } else if (/[1-9]/.test(this.text[this.pos])) {
      while (this.pos < this.text.length && /[0-9]/.test(this.text[this.pos])) this.pos += 1;
    } else throw new CanonicalizationError("invalid_number", "invalid integer");
    if (this.pos < this.text.length && ".eE".includes(this.text[this.pos])) throw new CanonicalizationError("non_integer_number", "only integers are allowed");
    const token = this.text.slice(start, this.pos);
    if (token === "-0") throw new CanonicalizationError("negative_zero", "negative zero is forbidden");
    const value = Number(token);
    if (!Number.isSafeInteger(value)) throw new CanonicalizationError("integer_out_of_range", "integer exceeds interoperable range");
    return value;
  }
  array(): unknown[] {
    this.pos += 1; const result: unknown[] = []; this.ws();
    if (this.text[this.pos] === "]") { this.pos += 1; return result; }
    while (true) {
      result.push(this.value()); this.ws();
      if (this.pos >= this.text.length) throw new CanonicalizationError("unexpected_eof", "unterminated array");
      const ch = this.text[this.pos++];
      if (ch === "]") return result;
      if (ch !== ",") throw new CanonicalizationError("invalid_json", "expected comma");
    }
  }
  object(): Record<string, unknown> {
    this.pos += 1; const result: Record<string, unknown> = {}; this.ws();
    if (this.text[this.pos] === "}") { this.pos += 1; return result; }
    while (true) {
      this.ws(); if (this.text[this.pos] !== '"') throw new CanonicalizationError("invalid_json", "object key must be string");
      const key = this.string();
      if (Object.prototype.hasOwnProperty.call(result, key)) throw new CanonicalizationError("duplicate_key", `duplicate key after NFC: ${key}`);
      this.ws(); if (this.text[this.pos] !== ":") throw new CanonicalizationError("invalid_json", "expected colon");
      this.pos += 1; result[key] = this.value(); this.ws();
      if (this.pos >= this.text.length) throw new CanonicalizationError("unexpected_eof", "unterminated object");
      const ch = this.text[this.pos++];
      if (ch === "}") return result;
      if (ch !== ",") throw new CanonicalizationError("invalid_json", "expected comma");
    }
  }
}

function escapeString(value: string): string {
  value = value.normalize("NFC");
  let out = '"';
  const escapes: Record<string, string> = { '"': '\\"', "\\": "\\\\", "\b": "\\b", "\f": "\\f", "\n": "\\n", "\r": "\\r", "\t": "\\t" };
  for (const ch of value) {
    if (Object.prototype.hasOwnProperty.call(escapes, ch)) out += escapes[ch];
    else if (ch.codePointAt(0)! < 0x20) out += `\\u${ch.codePointAt(0)!.toString(16).padStart(4, "0")}`;
    else out += ch;
  }
  return out + '"';
}

function encodeCanonical(value: unknown): string {
  if (value === null) return "null";
  if (value === true) return "true";
  if (value === false) return "false";
  if (typeof value === "number") {
    if (!Number.isSafeInteger(value)) throw new CanonicalizationError("integer_out_of_range", "integer exceeds interoperable range");
    if (Object.is(value, -0)) throw new CanonicalizationError("negative_zero", "negative zero is forbidden");
    return String(value);
  }
  if (typeof value === "string") return escapeString(value);
  if (Array.isArray(value)) return `[${value.map(encodeCanonical).join(",")}]`;
  if (typeof value === "object") {
    const normalized: Record<string, unknown> = {};
    for (const [key, val] of Object.entries(value as Record<string, unknown>)) {
      const nkey = key.normalize("NFC");
      if (Object.prototype.hasOwnProperty.call(normalized, nkey)) throw new CanonicalizationError("duplicate_key", `duplicate key after NFC: ${nkey}`);
      normalized[nkey] = val;
    }
    const keys = Object.keys(normalized).sort((a, b) => Buffer.from(a, "utf8").compare(Buffer.from(b, "utf8")));
    return `{${keys.map((key) => `${escapeString(key)}:${encodeCanonical(normalized[key])}`).join(",")}}`;
  }
  throw new CanonicalizationError("unsupported_json_type", typeof value);
}

function sha256(data: Uint8Array): string { return "sha256:" + crypto.createHash("sha256").update(data).digest("hex"); }
function fromHex(raw: string): Uint8Array {
  if (raw.length % 2 !== 0 || !/^[0-9a-fA-F]*$/.test(raw)) throw new CanonicalizationError("invalid_hex", "content hex is invalid");
  return Buffer.from(raw, "hex");
}
function canonicalJsonBytes(data: Uint8Array): Uint8Array { return Buffer.from(encodeCanonical(new JsonParser(strictUtf8(data)).parse()), "utf8"); }
function canonicalPath(raw: unknown): string {
  if (typeof raw !== "string") throw new CanonicalizationError("invalid_path", "path must be string");
  if (raw.includes("\\")) throw new CanonicalizationError("backslash_path", "backslash separator is forbidden");
  if (raw.startsWith("/") || raw.startsWith("~")) throw new CanonicalizationError("absolute_path", "physical/absolute path is forbidden");
  if (raw.includes("\0")) throw new CanonicalizationError("invalid_path", "NUL in path");
  const value = raw.normalize("NFC");
  const parts = value.split("/");
  if (parts.length === 0 || parts.some((part) => part === "" || part === "." || part === "..")) throw new CanonicalizationError("path_traversal", "empty/dot segments forbidden");
  return parts.join("/");
}
function canonicalText(data: Uint8Array): Uint8Array { return Buffer.from(strictUtf8(data).replace(/\r\n/g, "\n").replace(/\r/g, "\n").normalize("NFC"), "utf8"); }

type TreeInput = { kind: string; path?: string; mode?: string; content_hex?: string; content_encoding?: string };
function canonicalTree(entries: TreeInput[]): { manifest: unknown; digest: string } {
  const files: Array<Record<string, unknown>> = [];
  const exact = new Set<string>(); const folded = new Map<string, string>();
  for (const entry of entries) {
    if (entry.kind === "directory") continue;
    if (entry.kind !== "file") throw new CanonicalizationError("special_file_forbidden", `kind ${entry.kind} is forbidden`);
    const path = canonicalPath(entry.path);
    if (exact.has(path)) throw new CanonicalizationError("path_collision", `duplicate path: ${path}`);
    const fold = path.toLocaleLowerCase("und").normalize("NFC");
    if (folded.has(fold) && folded.get(fold) !== path) throw new CanonicalizationError("case_collision", `case collision: ${folded.get(fold)} vs ${path}`);
    exact.add(path); folded.set(fold, path);
    if (entry.mode !== "0644" && entry.mode !== "0755") throw new CanonicalizationError("invalid_mode", "mode must be 0644 or 0755");
    const raw = fromHex(entry.content_hex ?? "");
    let content: Uint8Array;
    if (entry.content_encoding === "utf8-text-v1") content = canonicalText(raw);
    else if (entry.content_encoding === "binary-exact-v1") content = raw;
    else throw new CanonicalizationError("invalid_content_encoding", "unknown content encoding");
    files.push({ content_digest: sha256(content), content_encoding: entry.content_encoding, mode: entry.mode, path, size: content.length });
  }
  files.sort((a, b) => Buffer.from(a.path as string, "utf8").compare(Buffer.from(b.path as string, "utf8")));
  const manifest = { entries: files, schema: "ai-society.canonical-tree/1" };
  return { manifest, digest: sha256(Buffer.from(encodeCanonical(manifest), "utf8")) };
}

function evaluate(vector: any): any {
  try {
    if (vector.kind === "json") {
      const canonical = canonicalJsonBytes(fromHex(vector.input_hex));
      return { status: "ok", canonical_hex: Buffer.from(canonical).toString("hex"), digest: sha256(canonical) };
    }
    const result = canonicalTree(vector.entries);
    return { status: "ok", manifest: result.manifest, digest: result.digest };
  } catch (error) {
    if (error instanceof CanonicalizationError) return { status: "error", code: error.code };
    throw error;
  }
}

function stable(value: unknown): string { return encodeCanonical(value); }
function main(): number {
  if (process.argv.length !== 3) { console.error("usage: reference.ts VECTORS.json"); return 2; }
  const vectors = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
  let failed = false;
  const results = vectors.vectors.map((vector: any) => {
    const actual = evaluate(vector); const expected = vector.expected; const ok = stable(actual) === stable(expected); failed ||= !ok;
    return { id: vector.id, ok, actual, expected };
  });
  console.log(JSON.stringify({ implementation: "typescript", results }));
  return failed ? 1 : 0;
}
process.exitCode = main();
