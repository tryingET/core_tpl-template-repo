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

function stripFrontmatter(markdown: string): string {
	if (!markdown.startsWith("---")) return markdown;
	const match = markdown.match(/^---\r?\n[\s\S]*?\r?\n---\r?\n?/);
	return match ? markdown.slice(match[0].length) : markdown;
}

function parseCommandArgs(argsString: string): string[] {
	const args: string[] = [];
	let current = "";
	let inQuote: '"' | "'" | null = null;

	for (let i = 0; i < argsString.length; i++) {
		const ch = argsString[i];
		if (inQuote) {
			if (ch === inQuote) inQuote = null;
			else current += ch;
			continue;
		}
		if (ch === '"' || ch === "'") {
			inQuote = ch;
			continue;
		}
		if (ch === " " || ch === "\t") {
			if (current) {
				args.push(current);
				current = "";
			}
			continue;
		}
		current += ch;
	}

	if (current) args.push(current);
	return args;
}

function substituteArgs(content: string, args: string[]): string {
	let result = content;

	// Positional first
	result = result.replace(/\$(\d+)/g, (_, num: string) => {
		const i = Number.parseInt(num, 10) - 1;
		return args[i] ?? "";
	});

	// Slices: ${@:N} and ${@:N:L}
	result = result.replace(/\$\{@:(\d+)(?::(\d+))?\}/g, (_, startStr: string, lenStr?: string) => {
		let start = Number.parseInt(startStr, 10) - 1;
		if (start < 0) start = 0;
		if (lenStr) {
			const len = Number.parseInt(lenStr, 10);
			return args.slice(start, start + len).join(" ");
		}
		return args.slice(start).join(" ");
	});

	const all = args.join(" ");
	result = result.replace(/\$ARGUMENTS/g, all);
	result = result.replace(/\$@/g, all);
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
