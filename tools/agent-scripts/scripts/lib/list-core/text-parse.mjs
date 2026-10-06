/**
summary: "Shared text and markdown parsing helpers for list-style tools."
read_when:
  - "You are changing scalar normalization, inline-list parsing, or markdown link target extraction."
*/

export function compactStrings(values) {
  const result = [];
  for (const value of values) {
    if (value === null || value === undefined) continue;
    const normalized = String(value).trim();
    if (normalized.length > 0) result.push(normalized);
  }
  return result;
}

export function stripOuterQuotes(value) {
  const trimmed = String(value ?? '').trim();
  if ((trimmed.startsWith('"') && trimmed.endsWith('"')) || (trimmed.startsWith("'") && trimmed.endsWith("'"))) {
    return trimmed.slice(1, -1).trim();
  }
  return trimmed;
}

export function normalizeScalar(value) {
  return stripOuterQuotes(String(value ?? '')).replace(/\s+/g, ' ').trim();
}

export function parseInlineList(rawValue) {
  const trimmed = String(rawValue ?? '').trim();
  if (!(trimmed.startsWith('[') && trimmed.endsWith(']'))) return [];

  const inner = trimmed.slice(1, -1).trim();
  if (!inner) return [];

  const parts = [];
  let current = '';
  let quote = null;
  let escaped = false;

  for (const ch of inner) {
    if (escaped) {
      current += ch;
      escaped = false;
      continue;
    }

    if (ch === '\\') {
      current += ch;
      escaped = true;
      continue;
    }

    if (quote) {
      if (ch === quote) quote = null;
      current += ch;
      continue;
    }

    if (ch === '"' || ch === "'") {
      quote = ch;
      current += ch;
      continue;
    }

    if (ch === ',') {
      parts.push(current);
      current = '';
      continue;
    }

    current += ch;
  }

  parts.push(current);
  return compactStrings(parts.map((part) => normalizeScalar(part)));
}

function findMatchingMarkdownLabelEnd(text, openIndex) {
  let depth = 0;
  let escaped = false;

  for (let index = openIndex; index < text.length; index += 1) {
    const ch = text[index];

    if (escaped) {
      escaped = false;
      continue;
    }

    if (ch === '\\') {
      escaped = true;
      continue;
    }

    if (ch === '[') {
      depth += 1;
      continue;
    }

    if (ch === ']') {
      depth -= 1;
      if (depth === 0) return index;
    }
  }

  return -1;
}

function parseMarkdownLinkDestination(text, startIndex) {
  let depth = 1;
  let destination = '';
  let escaped = false;
  let inAngle = false;

  for (let index = startIndex; index < text.length; index += 1) {
    const ch = text[index];

    if (escaped) {
      destination += ch;
      escaped = false;
      continue;
    }

    if (ch === '\\') {
      destination += ch;
      escaped = true;
      continue;
    }

    if (inAngle) {
      destination += ch;
      if (ch === '>') inAngle = false;
      continue;
    }

    if (destination.trim().length === 0 && /\s/.test(ch)) {
      continue;
    }

    if (destination.length === 0 && ch === '<') {
      destination += ch;
      inAngle = true;
      continue;
    }

    if (ch === '(') {
      depth += 1;
      destination += ch;
      continue;
    }

    if (ch === ')') {
      depth -= 1;
      if (depth === 0) {
        return {
          destination: destination.trim(),
          endIndex: index,
        };
      }
      destination += ch;
      continue;
    }

    destination += ch;
  }

  return null;
}

export function extractMarkdownDestinationPath(rawTarget) {
  const raw = String(rawTarget ?? '').trim();
  if (!raw) return '';

  if (raw.startsWith('<')) {
    let escaped = false;
    for (let index = 1; index < raw.length; index += 1) {
      const ch = raw[index];
      if (escaped) {
        escaped = false;
        continue;
      }
      if (ch === '\\') {
        escaped = true;
        continue;
      }
      if (ch === '>') {
        return raw.slice(1, index).trim();
      }
    }
  }

  const whitespaceIndex = raw.search(/\s/);
  if (whitespaceIndex >= 0) return raw.slice(0, whitespaceIndex).trim();
  return raw;
}

export function extractMarkdownLinkTargets(text) {
  const targets = [];

  for (let start = 0; start < text.length; start += 1) {
    const openIndex = text.indexOf('[', start);
    if (openIndex === -1) break;
    if (openIndex > 0 && text[openIndex - 1] === '!') {
      start = openIndex;
      continue;
    }

    const labelEnd = findMatchingMarkdownLabelEnd(text, openIndex);
    if (labelEnd === -1 || text[labelEnd + 1] !== '(') {
      start = openIndex;
      continue;
    }

    const parsed = parseMarkdownLinkDestination(text, labelEnd + 2);
    if (!parsed) {
      start = openIndex;
      continue;
    }

    if (parsed.destination) targets.push(parsed.destination);
    start = parsed.endIndex;
  }

  return targets;
}
