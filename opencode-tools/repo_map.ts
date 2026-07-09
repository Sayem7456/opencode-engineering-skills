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
    const candidate = path.join(current, "tools", "repo_map.py")
    if (fs.existsSync(candidate)) return current
    const parent = path.dirname(current)
    if (parent === current) return null
    current = parent
  }
}

export default tool({
  description: "Generate a compact repository map to reduce unnecessary context loading.",
  args: {
    path: tool.schema.string().optional().describe("Repository path to inspect."),
    maxFiles: tool.schema.number().optional().describe("Maximum number of files to inspect."),
  },
  async execute(args) {
    const currentFile = fileURLToPath(import.meta.url)
    const currentDir = path.dirname(currentFile)
    const repoRoot = findRepoRoot(currentDir)
    if (!repoRoot) {
      return [
        "Tool configuration error:",
        "Could not locate tools/repo_map.py.",
        "Reinstall using scripts/install-opencode.sh.",
      ].join("\n")
    }

    const script = path.join(repoRoot, "tools", "repo_map.py")
    const repositoryPath = args.path ?? "."
    const commandArgs = [script, repositoryPath]

    if (args.maxFiles !== undefined) {
      commandArgs.push("--max-files", String(args.maxFiles))
    }

    try {
      const result = await execFileAsync("python3", commandArgs, {
        cwd: repositoryPath,
        maxBuffer: 1024 * 1024 * 4,
      })
      return result.stdout || "No output."
    } catch (error: unknown) {
      if (error instanceof Error) {
        const msg = error.message
        return `repo_map tool failed: ${msg}`
      }
      return "repo_map tool failed with an unknown error."
    }
  },
})