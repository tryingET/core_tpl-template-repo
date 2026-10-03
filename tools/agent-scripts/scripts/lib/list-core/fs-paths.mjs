/**
summary: "Shared filesystem, repo-root, and directory-discovery helpers for list-style tools."
read_when:
  - "You are changing repo discovery, git-root fallback behavior, or shared directory traversal rules."
*/

import { execFileSync } from 'node:child_process';
import { readdirSync, realpathSync, statSync } from 'node:fs';
import path from 'node:path';

export const DEFAULT_EXCLUDED_DIRS = new Set([
  '.git',
  'node_modules',
  'archive',
  'research',
  '.venv',
  'venv',
  '__pycache__',
  'dist',
  'build',
  'out',
]);

const _warnedDirs = new Set();

export function toPosixPathSeparators(value) {
  return value.split(path.sep).join('/');
}

export function describeExecFailure(error) {
  const code = error && typeof error === 'object' && 'code' in error ? String(error.code) : null;
  const status = error && typeof error === 'object' && Number.isInteger(error.status) ? error.status : null;
  const stderrRaw = error && typeof error === 'object' && 'stderr' in error ? error.stderr : null;
  const stderr = Buffer.isBuffer(stderrRaw)
    ? stderrRaw.toString('utf8').trim()
    : typeof stderrRaw === 'string'
      ? stderrRaw.trim()
      : null;
  const message = error && typeof error === 'object' && 'message' in error ? String(error.message) : String(error);
  return { code, status, stderr, message };
}

export function createWarningCollector({ emitText = true } = {}) {
  const warnings = [];
  const logger = {
    warn(message, warning = { type: 'warning', message }) {
      warnings.push(warning);
      if (emitText) console.warn(message);
    },
  };
  return { warnings, logger };
}

/**
 * Log a directory-read warning, deduplicated per (dir, errorCode) pair.
 *
 * @param {string} dir
 * @param {object} err   Node SystemError (has .code)
 * @param {{ warn: (msg: string, warning?: object) => void }} [logger]  Defaults to console.
 */
export function warnReadDir(dir, err, logger = console) {
  const code = err?.code ?? 'UNKNOWN';
  const key = `\0${dir}\0${code}`; // null-separated to avoid path collisions
  if (_warnedDirs.has(key)) return null;
  _warnedDirs.add(key);
  const warning = {
    type: 'readdir_error',
    path: path.resolve(dir),
    code,
    message: `[fs-paths] readdirSync failed: ${dir} (${code})`,
  };
  logger.warn(warning.message, warning);
  return warning;
}

/** Reset the per-process dedup set (for test isolation). */
export function _resetWarnState() {
  _warnedDirs.clear();
}

/**
 * ReaddirSafe — read directory entries with observable error handling.
 *
 * Returns `{ entries: dirent[], error: null, warning: null }` on success,
 * or `{ entries: [], error: <error>, warning: <warning|null> }` on failure.
 *
 * @param {string} dir
 * @param {{ warn: (msg: string, warning?: object) => void }} [logger]
 */
export function readdirSafe(dir, logger = console) {
  try {
    return { entries: readdirSync(dir, { withFileTypes: true }), error: null, warning: null };
  } catch (err) {
    return { entries: [], error: err, warning: warnReadDir(dir, err, logger) };
  }
}

function hasProjectMarker(dir) {
  const markers = [
    path.join(dir, 'AGENTS.md'),
    path.join(dir, 'README.md'),
    path.join(dir, 'docs'),
    path.join(dir, 'scripts'),
  ];

  return markers.some((marker) => Boolean(safeStat(marker)));
}

function findNearestProjectRoot(cwd) {
  let current = path.resolve(cwd);

  while (true) {
    if (hasProjectMarker(current)) return current;
    const parent = path.dirname(current);
    if (parent === current) return path.resolve(cwd);
    current = parent;
  }
}

export function getGitRootState(cwd) {
  try {
    const out = execFileSync('git', ['rev-parse', '--show-toplevel'], {
      cwd,
      stdio: ['ignore', 'pipe', 'pipe'],
      encoding: 'utf8',
    });
    const root = out.trim();
    return root.length > 0 ? { kind: 'found', root, diagnostic: null } : { kind: 'not_repo', root: null, diagnostic: null };
  } catch (error) {
    const diagnostic = { command: 'git rev-parse --show-toplevel', cwd: path.resolve(cwd), ...describeExecFailure(error) };
    if (diagnostic.code === 'ENOENT') {
      return { kind: 'git_unavailable', root: null, diagnostic };
    }
    const failureText = `${diagnostic.stderr ?? ''}\n${diagnostic.message}`;
    if (diagnostic.status === 128 && /not a git repository \(or any of the parent directories\)/i.test(failureText)) {
      return { kind: 'not_repo', root: null, diagnostic };
    }
    return { kind: 'git_error', root: null, diagnostic };
  }
}

export function getGitRootOrNull(cwd) {
  const state = getGitRootState(cwd);
  return state.kind === 'found' ? state.root : null;
}

export function getRepoRoot(cwd) {
  return getGitRootOrNull(cwd) || findNearestProjectRoot(cwd);
}

export function safeStat(targetPath) {
  try {
    return statSync(targetPath);
  } catch {
    return null;
  }
}

export function canonicalPath(targetPath) {
  const resolved = path.resolve(targetPath);
  try {
    return typeof realpathSync.native === 'function' ? realpathSync.native(resolved) : realpathSync(resolved);
  } catch {
    return resolved;
  }
}

export function isDirectory(targetPath) {
  const stat = safeStat(targetPath);
  return Boolean(stat?.isDirectory());
}

export function isSameOrNestedPath(targetPath, basePath) {
  const normalizedTarget = canonicalPath(targetPath);
  const normalizedBase = canonicalPath(basePath);
  return normalizedTarget === normalizedBase || normalizedTarget.startsWith(`${normalizedBase}${path.sep}`);
}

export function isPathInside(basePath, targetPath) {
  const relative = path.relative(path.resolve(basePath), path.resolve(targetPath));
  return relative === '' || (!relative.startsWith('..') && !path.isAbsolute(relative));
}

export function repoRelativePathOrNull(repoRoot, targetPath) {
  if (!isPathInside(repoRoot, targetPath)) return null;
  const relative = path.relative(path.resolve(repoRoot), path.resolve(targetPath));
  return relative || path.basename(path.resolve(targetPath));
}

export function resolveInputPath(input, { cwd, repoRoot, accept = (candidate) => Boolean(safeStat(candidate)) } = {}) {
  if (path.isAbsolute(input)) return path.resolve(input);

  const fromCwd = path.resolve(cwd, input);
  if (accept(fromCwd)) return fromCwd;

  const fromRepoRoot = path.resolve(repoRoot, input);
  if (accept(fromRepoRoot)) return fromRepoRoot;

  return fromCwd;
}

export function walkFilesRecursive(
  dir,
  {
    baseDir = dir,
    visited = new Set(),
    logger = console,
    shouldSkipEntry = () => false,
    includeFile = () => true,
    mapFile = (fullPath) => fullPath,
  } = {}
) {
  const visitKey = canonicalPath(dir);
  if (visited.has(visitKey)) return [];
  visited.add(visitKey);

  const { entries } = readdirSafe(dir, logger);
  const files = [];

  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    const linkedStat = entry.isSymbolicLink() ? safeStat(fullPath) : null;
    const isDir = entry.isDirectory() || Boolean(linkedStat?.isDirectory());
    const isFile = entry.isFile() || Boolean(linkedStat?.isFile());

    if (shouldSkipEntry(entry, fullPath, { linkedStat, isDir, isFile })) continue;

    if (isDir) {
      files.push(...walkFilesRecursive(fullPath, { baseDir, visited, logger, shouldSkipEntry, includeFile, mapFile }));
      continue;
    }

    if (!isFile) continue;
    if (!includeFile(entry, fullPath, { linkedStat, isDir, isFile })) continue;
    files.push(mapFile(fullPath, { baseDir, entry, linkedStat }));
  }

  return files;
}

export function hasGitMarker(dir) {
  const marker = safeStat(path.join(dir, '.git'));
  if (!marker) return false;
  return marker.isDirectory() || marker.isFile();
}

export function dedupeSorted(paths) {
  const byCanonicalPath = new Map();

  for (const value of paths) {
    const resolved = path.resolve(value);
    const key = canonicalPath(resolved);
    if (!byCanonicalPath.has(key)) byCanonicalPath.set(key, resolved);
  }

  return [...byCanonicalPath.values()].sort((a, b) => a.localeCompare(b));
}

export function listSubdirectories(dir, excludedDirs = DEFAULT_EXCLUDED_DIRS, logger = console) {
  if (!isDirectory(dir)) return [];

  const { entries } = readdirSafe(dir, logger);

  return entries
    .filter((entry) => entry.isDirectory() && !entry.name.startsWith('.') && !excludedDirs.has(entry.name))
    .map((entry) => entry.name)
    .sort((a, b) => a.localeCompare(b));
}

export function findChildGitRepos(rootDir, excludedDirs = DEFAULT_EXCLUDED_DIRS, logger = console) {
  const repos = new Set();

  function walk(dir, isRoot = false) {
    if (!isRoot && hasGitMarker(dir)) {
      repos.add(path.resolve(dir));
      return;
    }

    const { entries } = readdirSafe(dir, logger);

    for (const entry of entries) {
      if (!entry.isDirectory()) continue;
      if (entry.name.startsWith('.')) continue;
      if (excludedDirs.has(entry.name)) continue;
      walk(path.join(dir, entry.name), false);
    }
  }

  walk(rootDir, true);
  return [...repos].sort((a, b) => a.localeCompare(b));
}
