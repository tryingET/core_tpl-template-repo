/**
summary: "Pure UTF-8, Markdown-reference, and local-path grammar for docs-ref-check."
read_when:
  - "You change docs-ref-check parsing, normalization, or encoding semantics."
*/

import { readFileSync } from 'node:fs';
import os from 'node:os';
import path from 'node:path';

import {
  extractMarkdownDestinationPath,
  extractMarkdownLinkTargets,
  normalizeScalar,
} from './list-core.mjs';

const CODE_SPAN_PATTERN = /`([^`\n]+)`/g;
const FENCE_PATTERN = /^((?: {0,3}>[ \t]?)*)(?: {0,3})(`{3,}|~{3,})(.*)$/;
const LOCAL_FILE_EXTENSIONS = new Set(['.md', '.markdown', '.toml', '.json', '.yaml', '.yml', '.cue', '.txt']);
const SKIP_PREFIXES = ['http:', 'https:', 'mailto:', 'tel:', 'data:', 'section:'];
const SKIP_CHARS = new Set(['*', '<', '>', '{', '}', '|']);
const UTF8_DECODER = new TextDecoder('utf-8', { fatal: true });

function decodeLocalReferencePath(value, { markdownEscapes = false } = {}) {
  const unescaped = markdownEscapes
    ? value.replace(/\\([!"#$%&'()*+,\-./:;<=>?@[\\\]^_`{|}~])/g, '$1')
    : value;
  try {
    const decoded = decodeURIComponent(unescaped);
    if (decoded.includes('\0')) {
      throw new TypeError(`NUL is not allowed in a local reference: ${value}`);
    }
    return decoded;
  } catch (error) {
    if (error instanceof TypeError) throw error;
    throw new URIError(`malformed percent-encoding in local reference: ${value}`);
  }
}

function unescapedFragmentIndex(value) {
  let escaped = false;
  for (let index = 0; index < value.length; index += 1) {
    const ch = value[index];
    if (escaped) {
      escaped = false;
    } else if (ch === '\\') {
      escaped = true;
    } else if (ch === '#') {
      return index;
    }
  }
  return -1;
}

function normalizeLinkTarget(rawTarget) {
  let value = extractMarkdownDestinationPath(rawTarget);
  if (!value) return null;
  if (value.startsWith('#')) return null;
  if (SKIP_PREFIXES.some((prefix) => value.toLowerCase().startsWith(prefix))) return null;

  const hashIndex = unescapedFragmentIndex(value);
  if (hashIndex >= 0) value = value.slice(0, hashIndex).trim();
  if (!value || value === '.') return null;
  if (SKIP_PREFIXES.some((prefix) => value.toLowerCase().startsWith(prefix))) return null;
  if (value.startsWith('<') || value.endsWith('>')) return null;
  if (value.includes('{{') || value.includes('}}')) return null;
  if ([...SKIP_CHARS].some((ch) => value.includes(ch))) return null;
  return decodeLocalReferencePath(value, { markdownEscapes: true });
}

function looksLikeLocalFileReference(rawValue) {
  const value = String(rawValue ?? '').trim();
  if (!value) return false;
  if (value.startsWith('#')) return false;
  if (SKIP_PREFIXES.some((prefix) => value.toLowerCase().startsWith(prefix))) return false;
  if (value.includes('{{') || value.includes('}}')) return false;
  if ([...SKIP_CHARS].some((ch) => value.includes(ch))) return false;
  if (value.startsWith('<') || value.endsWith('>')) return false;

  const tokens = value.split(/\s+/).filter(Boolean);
  if (tokens.length > 1) {
    const leadingToken = tokens[0];
    const leadingLooksLikePath = leadingToken.startsWith('./')
      || leadingToken.startsWith('../')
      || leadingToken.startsWith('~/')
      || path.isAbsolute(leadingToken)
      || leadingToken.includes('/');
    if (!leadingLooksLikePath) return false;
  }

  const hasPathSignal = value.startsWith('./')
    || value.startsWith('../')
    || value.startsWith('~/')
    || path.isAbsolute(value)
    || value.includes('/');
  if (!hasPathSignal) return false;

  const basename = path.basename(value);
  return [...LOCAL_FILE_EXTENSIONS].some((ext) => basename.toLowerCase().endsWith(ext));
}

function normalizeCodeSpanTarget(rawTarget) {
  let value = String(rawTarget ?? '').trim();
  if (!value) return null;
  if (value.startsWith('#')) return null;
  if (SKIP_PREFIXES.some((prefix) => value.toLowerCase().startsWith(prefix))) return null;

  const hashIndex = value.indexOf('#');
  if (hashIndex >= 0) value = value.slice(0, hashIndex).trim();
  if (!value || value === '.') return null;
  if (SKIP_PREFIXES.some((prefix) => value.toLowerCase().startsWith(prefix))) return null;
  if (value.includes('{{') || value.includes('}}')) return null;
  if ([...SKIP_CHARS].some((ch) => value.includes(ch))) return null;
  if (value.startsWith('<') || value.endsWith('>')) return null;
  return decodeLocalReferencePath(value);
}

function invalidReference(filePath, line, raw, error) {
  return {
    kind: 'invalid_reference',
    filePath,
    line,
    raw,
    reference: raw,
    invalidMessage: error instanceof Error ? error.message : String(error),
  };
}

export function extractReferences(filePath) {
  let content = '';
  try {
    content = UTF8_DECODER.decode(readFileSync(filePath)).replace(/^\uFEFF/, '');
  } catch (error) {
    const code = error && typeof error === 'object' && 'code' in error ? String(error.code) : 'read failed';
    return { refs: [], error: `unreadable file (${code})` };
  }

  const lines = content.split(/\r?\n/);
  const refs = [];
  const seen = new Set();
  let inFence = false;
  let fenceMarker = null;
  let fenceLength = 0;
  let fenceContainerDepth = 0;

  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    const fenceMatch = line.match(FENCE_PATTERN);
    if (fenceMatch) {
      const containerDepth = [...fenceMatch[1]].filter((ch) => ch === '>').length;
      const marker = fenceMatch[2][0];
      const markerLength = fenceMatch[2].length;
      const suffix = fenceMatch[3];
      if (!inFence) {
        inFence = true;
        fenceMarker = marker;
        fenceLength = markerLength;
        fenceContainerDepth = containerDepth;
        continue;
      }
      if (fenceContainerDepth === containerDepth && fenceMarker === marker && markerLength >= fenceLength && suffix.trim() === '') {
        inFence = false;
        fenceMarker = null;
        fenceLength = 0;
        fenceContainerDepth = 0;
      }
      continue;
    }
    if (inFence) continue;

    const markdownText = line.replace(CODE_SPAN_PATTERN, (span) => ' '.repeat(span.length));
    for (const raw of extractMarkdownLinkTargets(markdownText)) {
      let normalized;
      try {
        normalized = normalizeLinkTarget(raw);
      } catch (error) {
        refs.push(invalidReference(filePath, index + 1, raw, error));
        continue;
      }
      if (!normalized) continue;
      const key = `link:${index + 1}:${normalized}`;
      if (seen.has(key)) continue;
      seen.add(key);
      refs.push({ kind: 'markdown_link', filePath, line: index + 1, raw, reference: normalized });
    }

    for (const match of line.matchAll(CODE_SPAN_PATTERN)) {
      const raw = normalizeScalar(match[1]);
      if (!looksLikeLocalFileReference(raw)) continue;
      let normalized;
      try {
        normalized = normalizeCodeSpanTarget(raw);
      } catch (error) {
        refs.push(invalidReference(filePath, index + 1, raw, error));
        continue;
      }
      if (!normalized) continue;
      const key = `code:${index + 1}:${normalized}`;
      if (seen.has(key)) continue;
      seen.add(key);
      refs.push({ kind: 'code_span', filePath, line: index + 1, raw, reference: normalized });
    }
  }

  return { refs, error: null };
}

export function resolveReferenceTarget(reference, filePath) {
  if (reference.startsWith('~/')) return path.resolve(os.homedir(), reference.slice(2));
  if (path.isAbsolute(reference)) return path.resolve(reference);
  return path.resolve(path.dirname(filePath), reference);
}
