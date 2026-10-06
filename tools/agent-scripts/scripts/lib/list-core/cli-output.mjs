/**
summary: "Shared CLI outcome and JSON-or-text error emission helpers for list-style tools."
read_when:
  - "You are changing exit-code handling or shared --json error output behavior."
*/

import { hasFlag } from './args.mjs';

const CLI_OUTCOME_EXIT_CODES = {
  success: 0,
  failure: 1,
  usage_error: 2,
  runtime_error: 3,
};

export function createCliOutcome(kind = 'success') {
  const normalizedKind = String(kind ?? 'success');
  if (!Object.hasOwn(CLI_OUTCOME_EXIT_CODES, normalizedKind)) {
    throw new Error(`unknown CLI outcome kind: ${normalizedKind}`);
  }

  return {
    kind: normalizedKind,
    ok: normalizedKind === 'success',
    exitCode: CLI_OUTCOME_EXIT_CODES[normalizedKind],
  };
}

export function applyCliOutcome(outcome) {
  if (outcome.exitCode !== 0) process.exitCode = outcome.exitCode;
  return outcome;
}

export function writeJsonResult(payload, outcome) {
  const jsonPayload = { ...payload, ok: outcome.ok };
  process.stdout.write(`${JSON.stringify(jsonPayload, null, 2)}\n`);
  applyCliOutcome(outcome);
  return outcome;
}

/**
 * Emit an unknown-flags error using the standard CLI outcome system.
 * Respects --json mode (from argv) for structured output.
 *
 * @param {string} toolName - e.g. 'docs-list'
 * @param {string[]} unknown - Unknown flag tokens
 * @param {string[]} argv - process.argv
 * @param {Function} usageFn - Prints usage text
 */
export function emitUnknownFlagsError(toolName, unknown, argv, usageFn) {
  const outcome = createCliOutcome('usage_error');
  if (hasFlag(argv, '--json')) {
    writeJsonResult({ error: `unknown flag(s): ${unknown.join(', ')}` }, outcome);
  } else {
    console.error(`${toolName}: unknown flag(s): ${unknown.join(', ')}`);
    usageFn();
    applyCliOutcome(outcome);
  }

  return outcome;
}

export function emitMissingFlagValuesError(toolName, missing, argv, usageFn) {
  const outcome = createCliOutcome('usage_error');
  const message = `missing value for flag(s): ${missing.join(', ')}`;
  if (hasFlag(argv, '--json')) {
    writeJsonResult({ error: message }, outcome);
  } else {
    console.error(`${toolName}: ${message}`);
    usageFn();
    applyCliOutcome(outcome);
  }

  return outcome;
}
