import type { ExtensionAPI } from "@mariozechner/pi-coding-agent";
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";

const BUILTIN_COMMANDS = new Set([
	"settings",
	"model",
	"scoped-models",
	"export",
	"share",
	"copy",
	"name",
	"session",
	"changelog",
	"hotkeys",
	"fork",
	"tree",
	"login",
	"logout",
	"new",
	"compact",
	"resume",
	"reload",
	"quit",
]);

const CODE_SEGMENT_PATTERN = /(```[\s\S]*?```|`[^`\n]*`)/g;
const ESCAPED_PLACEHOLDER_PATTERN =
	/\\(\$\{@:\d+(?::\d+)?\}|\$\{ARGUMENTS\}|\$ARGUMENTS|\$\{\d+\}|\$\d+|\$@)/g;

function stripFrontmatter(markdown: string): string {
	const normalized = markdown.startsWith("\uFEFF") ? markdown.slice(1) : markdown;
	if (!normalized.startsWith("---")) return normalized;
	const match = normalized.match(/^---\r?\n[\s\S]*?\r?\n---\r?\n?/);
	return match ? normalized.slice(match[0].length) : normalized;
}

function parseCommandArgs(argsString: string): string[] {
	const args: string[] = [];
	let current = "";
	let inQuote: '"' | "'" | null = null;
	let quoteStartOffset = -1;
	let escapeNext = false;
	let tokenStarted = false;

	const flush = () => {
		if (!tokenStarted) return;
		args.push(current);
		current = "";
		tokenStarted = false;
		quoteStartOffset = -1;
	};

	for (let i = 0; i < argsString.length; i++) {
		const ch = argsString[i];

		if (escapeNext) {
			current += ch;
			tokenStarted = true;
			escapeNext = false;
			continue;
		}

		if (ch === "\\") {
			if (inQuote === "'") {
				current += ch;
				tokenStarted = true;
				continue;
			}
			escapeNext = true;
			tokenStarted = true;
			continue;
		}

		if (inQuote) {
			if (ch === inQuote) {
				inQuote = null;
				quoteStartOffset = -1;
				continue;
			}
			current += ch;
			tokenStarted = true;
			continue;
		}

		if (ch === '"' || ch === "'") {
			inQuote = ch;
			quoteStartOffset = current.length;
			tokenStarted = true;
			continue;
		}

		if (ch === " " || ch === "\t") {
			flush();
			continue;
		}

		current += ch;
		tokenStarted = true;
	}

	if (escapeNext) {
		current += "\\";
		tokenStarted = true;
	}

	if (inQuote && quoteStartOffset >= 0) {
		current = `${current.slice(0, quoteStartOffset)}${inQuote}${current.slice(quoteStartOffset)}`;
	}

	flush();
	return args;
}

function normalizeSliceIndex(value: string): number {
	const parsed = Number.parseInt(value, 10);
	if (!Number.isFinite(parsed)) return 0;
	return Math.max(0, parsed - 1);
}

function normalizeSliceLength(value: string | undefined): number | undefined {
	if (!value) return undefined;
	const parsed = Number.parseInt(value, 10);
	if (!Number.isFinite(parsed)) return 0;
	return Math.max(0, parsed);
}

function substituteArgsInPlainText(content: string, args: string[]): string {
	let result = content;

	// Slices: ${@:N} and ${@:N:L}
	result = result.replace(/(?<!\\)\$\{@:(\d+)(?::(\d+))?\}/g, (_, startStr: string, lenStr?: string) => {
		const start = normalizeSliceIndex(startStr);
		const len = normalizeSliceLength(lenStr);
		if (len === undefined) return args.slice(start).join(" ");
		return args.slice(start, start + len).join(" ");
	});

	// Positional: $1 and ${1}
	const replacePositional = (_: string, num: string): string => {
		const idx = normalizeSliceIndex(num);
		return args[idx] ?? "";
	};
	result = result.replace(/(?<!\\)\$\{(\d+)\}/g, replacePositional);
	result = result.replace(/(?<!\\)\$(\d+)/g, replacePositional);

	const all = args.join(" ");
	const replaceAllArgs = () => all;
	result = result.replace(/(?<!\\)\$\{ARGUMENTS\}/g, replaceAllArgs);
	result = result.replace(/(?<!\\)\$ARGUMENTS/g, replaceAllArgs);
	result = result.replace(/(?<!\\)\$@/g, replaceAllArgs);

	// Unescape placeholders meant to be literal (e.g. \$ARGUMENTS).
	result = result.replace(ESCAPED_PLACEHOLDER_PATTERN, "$1");
	return result;
}

function substituteArgs(content: string, args: string[]): string {
	let result = "";
	let lastIndex = 0;

	for (const match of content.matchAll(CODE_SEGMENT_PATTERN)) {
		const index = match.index ?? 0;
		result += substituteArgsInPlainText(content.slice(lastIndex, index), args);
		result += match[0];
		lastIndex = index + match[0].length;
	}

	result += substituteArgsInPlainText(content.slice(lastIndex), args);
	return result;
}

export default function (pi: ExtensionAPI) {
	pi.on("input", async (event, ctx) => {
		const text = event.text;
		if (!text.startsWith("/") || text.startsWith("/skill:")) {
			return { action: "continue" } as const;
		}

		const spaceIndex = text.indexOf(" ");
		const name = (spaceIndex === -1 ? text.slice(1) : text.slice(1, spaceIndex)).trim();
		if (!name || BUILTIN_COMMANDS.has(name)) {
			return { action: "continue" } as const;
		}

		const templatePath = join(ctx.cwd, ".pi", "prompts", `${name}.md`);
		if (!existsSync(templatePath)) {
			return { action: "continue" } as const;
		}

		try {
			const raw = readFileSync(templatePath, "utf-8");
			const body = stripFrontmatter(raw);
			const argsString = spaceIndex === -1 ? "" : text.slice(spaceIndex + 1);
			const args = parseCommandArgs(argsString);
			const expanded = substituteArgs(body, args);
			return { action: "transform", text: expanded } as const;
		} catch (err) {
			ctx.ui.notify(
				`project-prompts-first: failed to load ${templatePath} (${err instanceof Error ? err.message : String(err)})`,
				"warning",
			);
			return { action: "continue" } as const;
		}
	});
}
