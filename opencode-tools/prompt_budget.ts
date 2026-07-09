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
    const candidate = path.join(current, "tools", "prompt_budget.py")
    if (fs.existsSync(candidate)) return current
    const parent = path.dirname(current)
    if (parent === current) return null
    current = parent
  }
}

export default tool({
  description: "Estimate approximate context size (characters and tokens) and recommend a token-saving strategy.",
  args: {
    text: tool.schema.string().optional().describe("Inline text to estimate (passed via stdin)."),
    file: tool.schema.string().optional().describe("Path to a single file to analyze."),
    dir: tool.schema.string().optional().describe("Path to a directory to analyze (walks source files)."),
    top: tool.schema.number().optional().describe("Number of largest files to show (default: 20)."),
  },
  async execute(args) {
    const inputCount = (args.text !== undefined ? 1 : 0) + (args.file !== undefined ? 1 : 0) + (args.dir !== undefined ? 1 : 0)
    if (inputCount === 0) return "Error: Provide exactly one of --text, --file, or --dir."
    if (inputCount > 1) return "Error: Provide only one of --text, --file, or --dir, not multiple."

    const currentFile = fileURLToPath(import.meta.url)
    const currentDir = path.dirname(currentFile)
    const repoRoot = findRepoRoot(currentDir)
    if (!repoRoot) {
      return [
        "Tool configuration error:",
        "Could not locate tools/prompt_budget.py.",
        "Reinstall using scripts/install-opencode.sh.",
      ].join("\n")
    }

    const script = path.join(repoRoot, "tools", "prompt_budget.py")
    const cliArgs = [script]

    if (args.file) cliArgs.push("--file", args.file)
    else if (args.dir) cliArgs.push("--dir", args.dir)
    else cliArgs.push("--stdin")

    if (args.top !== undefined) cliArgs.push("--top", String(args.top))

    try {
      const result = await execFileAsync("python3", cliArgs, { input: args.text, maxBuffer: 1024 * 1024 * 4 })
      return result.stdout || "No output."
    } catch (error: unknown) {
      if (error instanceof Error) {
        return `prompt_budget tool failed: ${error.message}`
      }
      return "prompt_budget tool failed with an unknown error."
    }
  },
})