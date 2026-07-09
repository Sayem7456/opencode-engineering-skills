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
    "Compress logs, stack traces, notes, or session context while preserving exact errors, file paths, function names, commands, test results, and uncertainty. Use--text for inline content or --file for a path.",
  args: {
    text: tool.schema
      .string()
      .optional()
      .describe("Inline text to compress (passed via stdin to Python script)"),
    file: tool.schema
      .string()
      .optional()
      .describe("Path to a text file to compress"),
    maxLines: tool.schema
      .number()
      .optional()
      .describe("Target maximum output lines (default: 60)"),
    preserveErrors: tool.schema
      .boolean()
      .optional()
      .describe("Preserve error lines verbatim (default: true)"),
    preservePaths: tool.schema
      .boolean()
      .optional()
      .describe("Preserve file path lines verbatim (default: true)"),
  },
  async execute(args) {
    const scriptPath = resolveScriptPath("context_compressor.py");
    if (!scriptPath) {
      return "ERROR: Could not locate tools/context_compressor.py. Reinstall the package using scripts/install-opencode.sh.";
    }

    if (args.text === undefined && args.file === undefined) {
      return "ERROR: Provide --text (inline content) or --file (path to file). Neither was given.";
    }

    if (args.text !== undefined && args.file !== undefined) {
      return "ERROR: Provide only one of --text or --file, not both.";
    }

    const cliArgs = [scriptPath];

    if (args.file !== undefined) {
      cliArgs.push("--file", args.file);
    } else {
      cliArgs.push("--stdin");
    }

    if (args.maxLines !== undefined) {
      cliArgs.push("--max-lines", String(args.maxLines));
    }
    if (args.preserveErrors !== undefined) {
      cliArgs.push("--preserve-errors");
    }
    if (args.preservePaths !== undefined) {
      cliArgs.push("--preserve-paths");
    }

    return new Promise<string>((resolvePromise) => {
      const proc = execFile("python3", cliArgs, { timeout: 30000 }, (error, stdout, stderr) => {
        if (error) {
          if ((error as NodeJS.ErrnoException).code === "ENOENT") {
            resolvePromise("ERROR: Python not found. Install python3.");
          } else {
            const msg = stderr.trim() || error.message;
            resolvePromise(`ERROR: context_compressor.py failed: ${msg}`);
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
