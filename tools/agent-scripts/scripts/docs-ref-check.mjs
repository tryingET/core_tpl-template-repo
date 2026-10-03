#!/usr/bin/env node

/**
summary: "Check repository-local documentation references for resolvable and optionally tracked file targets."
read_when:
  - "You need a deterministic dead-reference check for canonical docs, READMEs, or generated projections."
  - "You want docs path integrity before merging or regenerating templates/projections."
*/

import { execFileSync } from 'node:child_process';
import { statSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

import {
  DEFAULT_EXCLUDED_DIRS,
  applyCliOutcome,
  compactStrings,
  createCliOutcome,
  createWarningCollector,
  describeExecFailure,
  emitMissingFlagValuesError,
  emitUnknownFlagsError,
  findMissingFlagValues,
  getArgValues,
  getGitRootState,
  getRepoRoot,
  hasFlag,
  isDirectory,
  resolveInputPath,
  safeStat,
  toPosixPathSeparators,
  validateFlags,
  walkFilesRecursive,
  writeJsonResult,
} from './lib/list-core.mjs';
import { extractReferences, resolveReferenceTarget } from './lib/docs-ref-check-core.mjs';

const DEFAULT_FILE_PATTERN = /\.(md|markdown)(\.[A-Za-z0-9._-]+)?$/i;

function usage() {
  console.log(`Usage: node scripts/docs-ref-check.mjs [options]

Options:
  --path <file-or-dir>   File or directory to scan (repeatable)
  --repo-root <dir>      Working repo root for default path resolution
  --require-tracked      Fail when a resolved target exists but is not git-tracked
  --json                 Output JSON
  -h, --help             Show this help

Exit codes:
  0 success
  1 validation failure / unresolved refs
  2 usage error
  3 unhandled runtime error

Defaults:
  If --path is omitted, scan README.md and docs/ under the detected repo root.

Reference kinds checked:
  - markdown links: [label](path/to/file.md)
  - inline code spans that look like local file paths:
    docs/dev/decision-lifecycle.md, ../README.md, ~/ai-society/.../file.md

Ignored by design:
  - fenced code blocks
  - URLs / anchors / mailto / section: links
  - template placeholders and wildcard paths (for example {{ ... }}, <repo:...>, foo/**)
  - command snippets with spaces (for example: bash scripts/check.sh)
`);
}

function collectFilesFromPath(targetPath, files, seen, logger = console) {
  const resolved = path.resolve(targetPath);
  const stat = safeStat(resolved);
  if (!stat) return;

  if (stat.isFile()) {
    if (DEFAULT_FILE_PATTERN.test(path.basename(resolved))) files.push(resolved);
    return;
  }

  if (!stat.isDirectory()) return;

  files.push(...walkFilesRecursive(resolved, {
    visited: seen,
    logger,
    shouldSkipEntry: (entry, _fullPath, { isDir }) => {
      if (entry.name.startsWith('.') && entry.name !== '.github') return true;
      return isDir && DEFAULT_EXCLUDED_DIRS.has(entry.name);
    },
    includeFile: (entry) => DEFAULT_FILE_PATTERN.test(entry.name),
    mapFile: (fullPath) => fullPath,
  }));
}

const gitRootStateCache = new Map();
const trackedCache = new Map();

export function clearCaches() {
  gitRootStateCache.clear();
  trackedCache.clear();
}

function findGitRootStateForPath(targetPath) {
  const dir = isDirectory(targetPath) ? targetPath : path.dirname(targetPath);
  if (gitRootStateCache.has(dir)) return gitRootStateCache.get(dir);

  const state = getGitRootState(dir);
  gitRootStateCache.set(dir, state);
  return state;
}

function getTrackedFileState(targetPath) {
  const gitRootState = findGitRootStateForPath(targetPath);
  if (gitRootState.kind === 'not_repo') {
    return {
      kind: 'untracked',
      repoRoot: null,
      reason: 'target exists but is not inside a git repo',
      diagnostic: gitRootState.diagnostic,
    };
  }

  if (gitRootState.kind !== 'found') {
    return {
      kind: 'unknown',
      repoRoot: null,
      reason: `unable to determine git root (${gitRootState.kind})`,
      diagnostic: gitRootState.diagnostic,
    };
  }

  const repoRoot = gitRootState.root;
  const relPath = toPosixPathSeparators(path.relative(repoRoot, targetPath));
  const cacheKey = `${repoRoot}::${relPath}`;
  if (trackedCache.has(cacheKey)) return trackedCache.get(cacheKey);

  try {
    execFileSync('git', ['--literal-pathspecs', '-C', repoRoot, 'ls-files', '--error-unmatch', '--', relPath], {
      stdio: ['ignore', 'ignore', 'pipe'],
    });
    const result = { kind: 'tracked', repoRoot, reason: null, diagnostic: null };
    trackedCache.set(cacheKey, result);
    return result;
  } catch (error) {
    const diagnostic = {
      command: 'git ls-files --error-unmatch',
      cwd: repoRoot,
      ...describeExecFailure(error),
    };
    const result = diagnostic.status === 1
      ? { kind: 'untracked', repoRoot, reason: 'target exists but is not git-tracked', diagnostic }
      : { kind: 'unknown', repoRoot, reason: 'git tracked-state check failed', diagnostic };
    trackedCache.set(cacheKey, result);
    return result;
  }
}

function relativeOutput(baseDir, targetPath) {
  const relative = toPosixPathSeparators(path.relative(baseDir, targetPath));
  return relative === '' ? '.' : relative;
}

const FLAG_DEFS = [
  { name: '-h' },
  { name: '--help' },
  { name: '--path', takesValue: true },
  { name: '--repo-root', takesValue: true },
  { name: '--require-tracked' },
  { name: '--json' },
];

function main() {
  const unknown = validateFlags(process.argv, FLAG_DEFS);
  if (unknown.length > 0) {
    emitUnknownFlagsError('docs-ref-check', unknown, process.argv, usage);
    return;
  }

  const missingValues = findMissingFlagValues(process.argv, FLAG_DEFS);
  if (missingValues.length > 0) {
    emitMissingFlagValuesError('docs-ref-check', missingValues, process.argv, usage);
    return;
  }

  if (hasFlag(process.argv, '-h') || hasFlag(process.argv, '--help')) {
    usage();
    return;
  }

  const cwd = process.cwd();
  const defaultRepoRoot = getRepoRoot(cwd);
  const repoRootArg = compactStrings(getArgValues(process.argv, '--repo-root', FLAG_DEFS)).at(-1);
  const repoRoot = repoRootArg ? path.resolve(cwd, repoRootArg) : defaultRepoRoot;
  const requireTracked = hasFlag(process.argv, '--require-tracked');
  const json = hasFlag(process.argv, '--json');
  const { warnings: scanWarnings, logger: warnLogger } = createWarningCollector({ emitText: !json });

  const inputPaths = compactStrings(getArgValues(process.argv, '--path', FLAG_DEFS));
  const targets = inputPaths.length > 0
    ? inputPaths.map((value) => resolveInputPath(value, {
      cwd,
      repoRoot,
      accept: (candidate) => Boolean(safeStat(candidate)),
    }))
    : [path.join(repoRoot, 'README.md'), path.join(repoRoot, 'docs')];

  const missingInputs = [];
  const files = [];
  const seenFiles = new Set();
  for (const target of targets) {
    const stat = safeStat(target);
    if (!stat) {
      missingInputs.push(target);
      continue;
    }
    collectFilesFromPath(target, files, seenFiles, warnLogger);
  }

  const sortedFiles = [...files].sort((a, b) => (a < b ? -1 : a > b ? 1 : 0));
  const extractResults = sortedFiles.map((filePath) => ({ filePath, ...extractReferences(filePath) }));
  const readErrors = extractResults.filter((r) => r.error).map((r) => ({
    type: 'read_error',
    path: relativeOutput(repoRoot, r.filePath),
    message: r.error,
  }));
  const scanIssues = scanWarnings.map((warning) => ({
    type: 'scan_error',
    path: warning.path,
    message: warning.message,
    code: warning.code,
  }));
  const references = extractResults.flatMap((r) => r.refs);
  const issues = [...scanIssues, ...readErrors];

  for (const ref of references) {
    if (ref.kind === 'invalid_reference') {
      issues.push({
        type: 'invalid_reference',
        path: relativeOutput(repoRoot, ref.filePath),
        line: ref.line,
        reference: ref.reference,
        resolvedTarget: null,
        message: ref.invalidMessage,
      });
      continue;
    }

    const resolvedTarget = resolveReferenceTarget(ref.reference, ref.filePath);
    let targetStat;
    try {
      targetStat = statSync(resolvedTarget);
    } catch (error) {
      const code = error && typeof error === 'object' && 'code' in error ? String(error.code) : null;
      const missing = code === 'ENOENT' || code === 'ENOTDIR';
      issues.push({
        type: missing ? 'missing_target' : 'target_stat_error',
        path: relativeOutput(repoRoot, ref.filePath),
        line: ref.line,
        reference: ref.reference,
        resolvedTarget,
        message: missing ? 'reference target does not exist' : `reference target state is indeterminate (${code ?? 'stat failed'})`,
        ...(missing ? {} : { diagnostic: { code, message: error instanceof Error ? error.message : String(error) } }),
      });
      continue;
    }

    if (targetStat.isDirectory()) {
      issues.push({
        type: 'directory_target',
        path: relativeOutput(repoRoot, ref.filePath),
        line: ref.line,
        reference: ref.reference,
        resolvedTarget,
        message: 'reference target is a directory, expected file',
      });
      continue;
    }

    if (!targetStat.isFile()) {
      issues.push({
        type: 'non_file_target',
        path: relativeOutput(repoRoot, ref.filePath),
        line: ref.line,
        reference: ref.reference,
        resolvedTarget,
        message: 'reference target is not a file',
      });
      continue;
    }

    if (requireTracked) {
      const tracked = getTrackedFileState(resolvedTarget);
      if (tracked.kind !== 'tracked') {
        issues.push({
          type: tracked.kind === 'untracked' ? 'untracked_target' : 'tracked_check_error',
          path: relativeOutput(repoRoot, ref.filePath),
          line: ref.line,
          reference: ref.reference,
          resolvedTarget,
          repoRoot: tracked.repoRoot,
          message: tracked.reason,
          diagnostic: tracked.diagnostic,
        });
      }
    }
  }

  const ok = missingInputs.length === 0 && issues.length === 0;
  const payload = {
    cwd,
    repoRoot,
    requireTracked,
    scannedFiles: sortedFiles.map((filePath) => relativeOutput(repoRoot, filePath)),
    missingInputs,
    referenceCount: references.length,
    scanWarnings,
    issues,
  };
  const finalOutcome = createCliOutcome(ok ? 'success' : 'failure');

  if (json) {
    writeJsonResult(payload, finalOutcome);
    return;
  }

  console.log(`docs-ref-check: scanned ${sortedFiles.length} file(s), ${references.length} reference(s)`);

  if (missingInputs.length > 0) {
    for (const missing of missingInputs) {
      console.log(`- missing input: ${missing}`);
    }
  }

  if (issues.length === 0 && missingInputs.length === 0) {
    console.log('docs-ref-check: pass');
    return;
  }

  const totalIssues = issues.length + missingInputs.length;
  console.log(`docs-ref-check: fail (${totalIssues} issue(s))`);
  for (const issue of issues) {
    if (issue.line) {
      console.log(`- ${issue.path}:${issue.line} ${issue.reference} -> ${issue.message} (${issue.resolvedTarget})`);
    } else {
      console.log(`- ${issue.path} -> ${issue.message}`);
    }
  }
  applyCliOutcome(finalOutcome);
}

export function runCli() {
  try {
    main();
  } catch (error) {
    const msg = error && typeof error === 'object' && 'message' in error ? String(error.message) : String(error);
    if (hasFlag(process.argv, '--json')) {
      process.stdout.write(`${JSON.stringify({ ok: false, error: `unhandled: ${msg}` }, null, 2)}\n`);
    } else {
      console.error(`docs-ref-check: unhandled error: ${msg}`);
    }
    process.exitCode = 3;
  }
}

const invokedPath = process.argv[1] ? path.resolve(process.argv[1]) : null;
if (invokedPath === path.resolve(fileURLToPath(import.meta.url))) runCli();
