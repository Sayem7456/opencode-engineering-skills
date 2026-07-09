import { tool } from "@opencode-ai/plugin"
import { execFile } from "node:child_process"
import { fileURLToPath } from "node:url"
import path from "node:path"
import fs from "node:fs"
import { promisify } from "node:util"

const execFileAsync = promisify(execFile)

function findRepoRoot(startDir: string): string | null {
  let current = startDir
  while (true) {
    const candidate = path.join(current, "tools", "diff_summarizer.py")
    if (fs.existsSync(candidate)) return current
    const parent = path.dirname(current)
    if (parent === current) return null
    current = parent
  }
}

export default tool({
  description: "Summarize a git diff with per-file analysis: line counts, risk category, detected symbols, suggested skills, and suggested test commands.",
  args: {
    path: tool.schema.string().optional().describe("Working directory to run git diff in (default: current directory)."),
    diffFile: tool.schema.string().optional().describe("Path to an existing diff file to analyze."),
    useStdinText: tool.schema.string().optional().describe("Inline diff text to analyze (passed via stdin)."),
  },
  async execute(args) {
    const currentFile = fileURLToPath(import.meta.url)
    const currentDir = path.dirname(currentFile)
    const repoRoot = findRepoRoot(currentDir)
    if (!repoRoot) {
      return [
        "Tool configuration error:",
        "Could not locate tools/diff_summarizer.py.",
        "Reinstall using scripts/install-opencode.sh.",
      ].join("\n")
    }

    const script = path.join(repoRoot, "tools", "diff_summarizer.py")

    try {
      if (args.diffFile) {
        const result = await execFileAsync("python3", [script, "--file", args.diffFile], { maxBuffer: 1024 * 1024 * 4 })
        return result.stdout || "No output."
      }

      if (args.useStdinText !== undefined) {
        const result = await execFileAsync("python3", [script, "--stdin"], { input: args.useStdinText, maxBuffer: 1024 * 1024 * 4 })
        return result.stdout || "No output."
      }

      const cwd = args.path ?? "."
      const result = await execFileAsync("python3", [script], { cwd, maxBuffer: 1024 * 1024 * 4 })
      return result.stdout || "No output."
    } catch (error: unknown) {
      if (error instanceof Error) {
        return `diff_summarizer tool failed: ${error.message}`
      }
      return "diff_summarizer tool failed with an unknown error."
    }
  },
})