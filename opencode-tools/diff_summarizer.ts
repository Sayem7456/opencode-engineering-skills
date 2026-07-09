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
    "Summarize a git diff with per-file analysis: line counts, risk category, detected symbols, suggested skills, and suggested test commands.",
  args: {
    path: tool.schema
      .string()
      .optional()
      .describe("Working directory to run git diff in (default: current directory)"),
    diffFile: tool.schema
      .string()
      .optional()
      .describe("Path to an existing diff file to analyze"),
    useStdinText: tool.schema
      .string()
      .optional()
      .describe("Inline diff text to analyze (passed via stdin to Python script)"),
  },
  async execute(args) {
    const scriptPath = resolveScriptPath("diff_summarizer.py");
    if (!scriptPath) {
      return "ERROR: Could not locate tools/diff_summarizer.py. Reinstall the package using scripts/install-opencode.sh.";
    }

    if (args.useStdinText !== undefined) {
      const cliArgs = [scriptPath, "--stdin"];
      return new Promise<string>((resolvePromise) => {
        const proc = execFile("python3", cliArgs, { timeout: 30000 }, (error, stdout, stderr) => {
          if (error) {
            if ((error as NodeJS.ErrnoException).code === "ENOENT") {
              resolvePromise("ERROR: Python not found. Install python3.");
            } else {
              const msg = stderr.trim() || error.message;
              resolvePromise(`ERROR: diff_summarizer.py failed: ${msg}`);
            }
            return;
          }
          resolvePromise(stdout.trimEnd());
        });
        if (proc.stdin) {
          proc.stdin.write(args.useStdinText);
          proc.stdin.end();
        }
      });
    }

    if (args.diffFile !== undefined) {
      const cliArgs = [scriptPath, "--file", args.diffFile];
      return new Promise<string>((resolvePromise) => {
        execFile("python3", cliArgs, { timeout: 30000 }, (error, stdout, stderr) => {
          if (error) {
            if ((error as NodeJS.ErrnoException).code === "ENOENT") {
              resolvePromise("ERROR: Python not found. Install python3.");
            } else {
              const msg = stderr.trim() || error.message;
              resolvePromise(`ERROR: diff_summarizer.py failed: ${msg}`);
            }
            return;
          }
          resolvePromise(stdout.trimEnd());
        });
      });
    }

    // Default: run git diff in the specified or current directory
    const cwd = args.path ?? ".";
    const cliArgs = [scriptPath];
    return new Promise<string>((resolvePromise) => {
      execFile("python3", cliArgs, { cwd, timeout: 30000 }, (error, stdout, stderr) => {
        if (error) {
          if ((error as NodeJS.ErrnoException).code === "ENOENT") {
            resolvePromise("ERROR: Python not found. Install python3.");
          } else {
            const msg = stderr.trim() || error.message;
            resolvePromise(`ERROR: diff_summarizer.py failed: ${msg}`);
          }
          return;
        }
        resolvePromise(stdout.trimEnd());
      });
    });
  },
});
