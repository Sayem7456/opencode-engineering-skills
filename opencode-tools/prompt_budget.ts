import { tool } from "@opencode-ai/plugin";
import { execFile } from "child_process";
import { fileURLToPath } from "url";
import { dirname, resolve, sep } from "path";
import { existsSync } from "fs";

/**
 * Walk up from the installed tool's real path to find the repository root
 * containing tools/<scriptName>. Handles symlinked installations.
 */
function resolveScriptPath(scriptName: string): string {
  const currentFile = fileURLToPath(import.meta.url);
  let dir = resolve(dirname(currentFile));
  const parts = dir.split(sep);
  for (let i = parts.length; i > 1; i--) {
    const candidate = parts.slice(0, i).join(sep);
    const scriptPath = resolve(candidate, "tools", scriptName);
    if (existsSync(scriptPath)) {
      return scriptPath;
    }
  }
  return "";
}

export default tool({
  description:
    "Estimate approximate context size (characters and tokens) and recommend a token-saving strategy. Use --text, --file, or --dir (exactly one).",
  args: {
    text: tool.schema
      .string()
      .optional()
      .describe("Inline text to estimate (passed via stdin to Python script)"),
    file: tool.schema
      .string()
      .optional()
      .describe("Path to a single file to analyze"),
    dir: tool.schema
      .string()
      .optional()
      .describe("Path to a directory to analyze (walks source files)"),
    top: tool.schema
      .number()
      .optional()
      .describe("Number of largest files to show (default: 20)"),
  },
  async execute(args) {
    const scriptPath = resolveScriptPath("prompt_budget.py");
    if (!scriptPath) {
      return "ERROR: Could not locate tools/prompt_budget.py. Reinstall the package using scripts/install-opencode.sh.";
    }

    const inputCount =
      (args.text !== undefined ? 1 : 0) +
      (args.file !== undefined ? 1 : 0) +
      (args.dir !== undefined ? 1 : 0);

    if (inputCount === 0) {
      return "ERROR: Provide exactly one of --text, --file, or --dir.";
    }
    if (inputCount > 1) {
      return "ERROR: Provide only one of --text, --file, or --dir, not multiple.";
    }

    const cliArgs = [scriptPath];

    if (args.file !== undefined) {
      cliArgs.push("--file", args.file);
    } else if (args.dir !== undefined) {
      cliArgs.push("--dir", args.dir);
    } else {
      cliArgs.push("--stdin");
    }

    if (args.top !== undefined) {
      cliArgs.push("--top", String(args.top));
    }

    return new Promise<string>((resolvePromise) => {
      const proc = execFile("python3", cliArgs, { timeout: 30000 }, (error, stdout, stderr) => {
        if (error) {
          if ((error as NodeJS.ErrnoException).code === "ENOENT") {
            resolvePromise("ERROR: Python not found. Install python3.");
          } else {
            const msg = stderr.trim() || error.message;
            resolvePromise(`ERROR: prompt_budget.py failed: ${msg}`);
          }
          return;
        }
        resolvePromise(stdout.trimEnd());
      });
      if (args.text !== undefined && proc.stdin) {
        proc.stdin.write(args.text);
        proc.stdin.end();
      }
    });
  },
});
