/**
summary: "Compatibility barrel for shared helpers used by docs-list and docs-ref-check."
read_when:
  - "You are changing shared list-tool helpers and need the stable import surface."
  - "You want the focused submodule layout behind scripts/lib/list-core/*.mjs."
*/

export {
  findMissingFlagValues,
  getArgValues,
  getLastArgValue,
  hasFlag,
  validateFlags,
} from './list-core/args.mjs';

export {
  DEFAULT_EXCLUDED_DIRS,
  _resetWarnState,
  canonicalPath,
  createWarningCollector,
  dedupeSorted,
  describeExecFailure,
  findChildGitRepos,
  getGitRootOrNull,
  getGitRootState,
  getRepoRoot,
  hasGitMarker,
  isDirectory,
  isPathInside,
  isSameOrNestedPath,
  listSubdirectories,
  readdirSafe,
  repoRelativePathOrNull,
  resolveInputPath,
  safeStat,
  toPosixPathSeparators,
  walkFilesRecursive,
  warnReadDir,
} from './list-core/fs-paths.mjs';

export {
  compactStrings,
  extractMarkdownDestinationPath,
  extractMarkdownLinkTargets,
  normalizeScalar,
  parseInlineList,
  stripOuterQuotes,
} from './list-core/text-parse.mjs';

export {
  applyCliOutcome,
  createCliOutcome,
  emitMissingFlagValuesError,
  emitUnknownFlagsError,
  writeJsonResult,
} from './list-core/cli-output.mjs';
