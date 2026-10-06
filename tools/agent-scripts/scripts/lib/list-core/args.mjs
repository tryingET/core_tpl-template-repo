/**
summary: "Shared CLI argument parsing helpers for list-style tools."
read_when:
  - "You are changing shared flag parsing or validation semantics across docs-list or docs-ref-check."
*/

function buildKnownFlagMap(flagDefs = []) {
  const knownMap = new Map();
  for (const def of flagDefs) {
    knownMap.set(def.name, Boolean(def.takesValue));
  }
  return knownMap;
}

function splitFlagToken(token) {
  const eqIndex = token.indexOf('=');
  return {
    eqIndex,
    flagName: eqIndex === -1 ? token : token.slice(0, eqIndex),
  };
}

function isKnownFlagToken(token, knownMap) {
  if (!token || !token.startsWith('-')) return false;
  const { flagName } = splitFlagToken(token);
  return knownMap.has(flagName);
}

export function getArgValues(argv, flag, flagDefs = null) {
  const values = [];
  const prefix = `${flag}=`;
  const knownMap = flagDefs ? buildKnownFlagMap(flagDefs) : null;

  for (let i = 2; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === flag) {
      const value = argv[i + 1];
      if (!value) continue;
      if (knownMap ? isKnownFlagToken(value, knownMap) : value.startsWith('-')) continue;
      values.push(value);
      i += 1;
      continue;
    }
    if (arg.startsWith(prefix)) {
      const value = arg.slice(prefix.length).trim();
      if (value.length > 0) values.push(value);
    }
  }
  return values;
}

export function getLastArgValue(argv, flag, flagDefs = null) {
  const values = getArgValues(argv, flag, flagDefs);
  return values.length > 0 ? values[values.length - 1] : null;
}

export function hasFlag(argv, flag) {
  const prefix = `${flag}=`;
  return argv.includes(flag) || argv.some((arg) => arg.startsWith(prefix));
}

/**
 * Validate that all CLI flags (tokens starting with `-`) are known.
 *
 * @param {string[]} argv - process.argv (or equivalent)
 * @param {Array<{name: string, takesValue?: boolean}>} flagDefs
 *   Flag descriptor array. `takesValue` flags consume the next positional
 *   token so it is not mistaken for an unknown flag.
 * @returns {string[]} Unknown flag tokens (empty if all valid).
 */
export function validateFlags(argv, flagDefs) {
  const unknown = [];
  const knownMap = buildKnownFlagMap(flagDefs);

  for (let i = 2; i < argv.length; i += 1) {
    const token = argv[i];
    if (!token.startsWith('-')) continue;

    const { eqIndex, flagName } = splitFlagToken(token);
    const takesValue = knownMap.get(flagName);
    if (takesValue === undefined) {
      unknown.push(token);
    } else if (takesValue && eqIndex === -1) {
      const next = argv[i + 1];
      if (next && !isKnownFlagToken(next, knownMap)) {
        i += 1;
      }
    }
  }
  return unknown;
}

export function findMissingFlagValues(argv, flagDefs) {
  const missing = [];
  const knownMap = buildKnownFlagMap(flagDefs);

  for (let i = 2; i < argv.length; i += 1) {
    const token = argv[i];
    if (!token.startsWith('-')) continue;

    const { eqIndex, flagName } = splitFlagToken(token);
    const takesValue = knownMap.get(flagName);
    if (!takesValue) continue;

    if (eqIndex !== -1) {
      const value = token.slice(eqIndex + 1).trim();
      if (value.length === 0) missing.push(flagName);
      continue;
    }

    const next = argv[i + 1];
    if (!next || isKnownFlagToken(next, knownMap)) {
      missing.push(flagName);
      continue;
    }

    i += 1;
  }

  return missing;
}
