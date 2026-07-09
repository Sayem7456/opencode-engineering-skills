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
    "Generate a compact repository map showing languages, frameworks, config files, backend/frontend/db/test groupings, and suggested next reads.",
  args: {
    path: tool.schema
      .string()
      .default(".")
      .describe("Repository path (default: current directory)"),
    maxFiles: tool.schema
      .number()
      .optional()
      .describe("Maximum files to list per category (default: 300)"),
  },
  async execute(args) {
    const scriptPath = resolveScriptPath("repo_map.py");
    if (!scriptPath) {
      return "ERROR: Could not locate tools/repo_map.py. Reinstall the package using scripts/install-opencode.sh.";
    }

    const cliArgs = [scriptPath, args.path];
    if (args.maxFiles !== undefined) {
      cliArgs.push("--max-files", String(args.maxFiles));
    }

    return new Promise<string>((resolvePromise) => {
      execFile("python3", cliArgs, { timeout: 30000 }, (error, stdout, stderr) => {
        if (error) {
          if ((error as NodeJS.ErrnoException).code === "ENOENT") {
            resolvePromise("ERROR: Python not found. Install python3.");
          } else {
            const msg = stderr.trim() || error.message;
            resolvePromise(`ERROR: repo_map.py failed: ${msg}`);
          }
          return;
        }
        resolvePromise(stdout.trimEnd());
      });
    });
  },
});
