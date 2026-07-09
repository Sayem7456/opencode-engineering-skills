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
    const candidate = path.join(current, "tools", "context_compressor.py")
    if (fs.existsSync(candidate)) return current
    const parent = path.dirname(current)
    if (parent === current) return null
    current = parent
  }
}

export default tool({
  description: "Compress logs, stack traces, notes, or session context while preserving exact errors, file paths, function names, commands, test results, and uncertainty.",
  args: {
    text: tool.schema.string().optional().describe("Inline text to compress (passed via stdin)."),
    file: tool.schema.string().optional().describe("Path to a text file to compress."),
    maxLines: tool.schema.number().optional().describe("Target maximum output lines (default: 60)."),
    preserveErrors: tool.schema.boolean().optional().describe("Preserve error lines verbatim (default: true)."),
    preservePaths: tool.schema.boolean().optional().describe("Preserve file path lines verbatim (default: true)."),
  },
  async execute(args) {
    if (!args.text && !args.file) {
      return "Error: Provide --text (inline content) or --file (path to file). Neither was given."
    }
    if (args.text && args.file) {
      return "Error: Provide only one of --text or --file, not both."
    }

    const currentFile = fileURLToPath(import.meta.url)
    const currentDir = path.dirname(currentFile)
    const repoRoot = findRepoRoot(currentDir)
    if (!repoRoot) {
      return [
        "Tool configuration error:",
        "Could not locate tools/context_compressor.py.",
        "Reinstall using scripts/install-opencode.sh.",
      ].join("\n")
    }

    const script = path.join(repoRoot, "tools", "context_compressor.py")
    const cliArgs = [script]

    if (args.file) {
      cliArgs.push("--file", args.file)
    } else {
      cliArgs.push("--stdin")
    }
    if (args.maxLines !== undefined) cliArgs.push("--max-lines", String(args.maxLines))
    if (args.preserveErrors !== undefined) cliArgs.push("--preserve-errors")
    if (args.preservePaths !== undefined) cliArgs.push("--preserve-paths")

    try {
      const result = await execFileAsync("python3", cliArgs, { input: args.text, maxBuffer: 1024 * 1024 * 4 })
      return result.stdout || "No output."
    } catch (error: unknown) {
      if (error instanceof Error) {
        return `context_compressor tool failed: ${error.message}`
      }
      return "context_compressor tool failed with an unknown error."
    }
  },
})