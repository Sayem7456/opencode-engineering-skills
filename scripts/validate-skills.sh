#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_DIR="$ROOT/skills"
COMMANDS_DIR="$ROOT/commands"
DOCS_DIR="$ROOT/docs"
TOOLS_DIR="$ROOT/opencode-tools"
PYTHON_TOOLS_DIR="$ROOT/tools"

failed=0

# --------------------------------------------------
# Extract frontmatter text from a file
# --------------------------------------------------
extract_frontmatter() {
    awk '
        BEGIN { in_fm = 0 }
        NR == 1 && $0 == "---" { in_fm = 1; next }
        in_fm && $0 == "---" { exit }
        in_fm { print }
    ' "$1"
}

# --------------------------------------------------
# Extract body text (content after the closing ---)
# --------------------------------------------------
extract_body() {
    awk '
        BEGIN { count = 0 }
        /^---$/ { count++; next }
        count >= 2 { print }
    ' "$1"
}

# --------------------------------------------------
# Validate skills
# --------------------------------------------------

echo "=== Validating skills ==="
echo ""

for directory in "$SKILLS_DIR"/*; do
    [[ -d "$directory" ]] || continue

    folder_name="$(basename "$directory")"
    skill_file="$directory/SKILL.md"

    echo "Checking $folder_name..."

    if [[ ! -f "$skill_file" ]]; then
        echo "  ERROR: SKILL.md is missing"
        failed=1
        continue
    fi

    # Extract entire frontmatter block
    frontmatter="$(extract_frontmatter "$skill_file")"

    if [[ -z "$frontmatter" ]]; then
        echo "  ERROR: frontmatter is missing or malformed"
        failed=1
        continue
    fi

    # name
    declared_name="$(
        echo "$frontmatter" \
        | awk -F':[[:space:]]*' '
            $1 == "name" {
                gsub(/^["'\'' ]+|["'\'' ]+$/, "", $2)
                gsub(/[[:space:]]+$/, "", $2)
                print $2
                exit
            }
        '
    )"

    if [[ -z "$declared_name" ]]; then
        echo "  ERROR: name is missing from frontmatter"
        failed=1
    elif [[ "$declared_name" != "$folder_name" ]]; then
        echo "  ERROR: frontmatter name '$declared_name' does not match folder '$folder_name'"
        failed=1
    fi

    if [[ ! "$folder_name" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
        echo "  ERROR: invalid skill name '$folder_name'"
        failed=1
    fi

    # description
    if ! echo "$frontmatter" | grep -q '^description:[[:space:]]*[^[:space:]]'; then
        echo "  ERROR: description is missing from frontmatter"
        failed=1
    fi

    # license
    license_value="$(
        echo "$frontmatter" \
        | awk -F':[[:space:]]*' '
            $1 == "license" {
                gsub(/^[[:space:]]+|[[:space:]]+$/, "", $2)
                print $2
                exit
            }
        '
    )"

    if [[ -z "$license_value" ]]; then
        echo "  ERROR: license is missing from frontmatter"
        failed=1
    elif [[ "$license_value" != "MIT" ]]; then
        echo "  ERROR: license must be 'MIT', found '$license_value'"
        failed=1
    fi

    # compatibility
    compat_value="$(
        echo "$frontmatter" \
        | awk -F':[[:space:]]*' '
            $1 == "compatibility" {
                gsub(/^[[:space:]]+|[[:space:]]+$/, "", $2)
                print $2
                exit
            }
        '
    )"

    if [[ -z "$compat_value" ]]; then
        echo "  ERROR: compatibility is missing from frontmatter"
        failed=1
    elif [[ "$compat_value" != "opencode" ]]; then
        echo "  ERROR: compatibility must be 'opencode', found '$compat_value'"
        failed=1
    fi

    # metadata section
    if ! echo "$frontmatter" | grep -q '^metadata:'; then
        echo "  ERROR: metadata is missing from frontmatter"
        failed=1
    fi

    # metadata.category (indented line under metadata)
    meta_category="$(
        echo "$frontmatter" \
        | awk '
            /^metadata:/ { found = 1; next }
            found && /^[[:space:]]+category:[[:space:]]*[^[:space:]]/ {
                sub(/^[[:space:]]+category:[[:space:]]*/, "")
                gsub(/[[:space:]]+$/, "")
                print
                exit
            }
        '
    )"

    if [[ -z "$meta_category" ]]; then
        echo "  ERROR: metadata.category is missing or empty"
        failed=1
    fi

    # metadata.stack
    meta_stack="$(
        echo "$frontmatter" \
        | awk '
            /^metadata:/ { found = 1; next }
            found && /^[[:space:]]+stack:[[:space:]]*[^[:space:]]/ {
                sub(/^[[:space:]]+stack:[[:space:]]*/, "")
                gsub(/[[:space:]]+$/, "")
                print
                exit
            }
        '
    )"

    if [[ -z "$meta_stack" ]]; then
        echo "  ERROR: metadata.stack is missing or empty"
        failed=1
    fi

    # metadata.version
    meta_version="$(
        echo "$frontmatter" \
        | awk '
            /^metadata:/ { found = 1; next }
            found && /^[[:space:]]+version:[[:space:]]*[^[:space:]]/ {
                sub(/^[[:space:]]+version:[[:space:]]*/, "")
                gsub(/[[:space:]]+$/, "")
                print
                exit
            }
        '
    )"

    if [[ -z "$meta_version" ]]; then
        echo "  ERROR: metadata.version is missing or empty"
        failed=1
    fi

    # body is not empty
    body="$(extract_body "$skill_file" | tr -d '[:space:]')"

    if [[ -z "$body" ]]; then
        echo "  ERROR: skill body is empty"
        failed=1
    fi

    echo ""
done

# --------------------------------------------------
# Warn about directories without SKILL.md
# --------------------------------------------------

for directory in "$SKILLS_DIR"/*; do
    [[ -d "$directory" ]] || continue

    if [[ ! -f "$directory/SKILL.md" ]]; then
        folder_name="$(basename "$directory")"
        echo "  WARNING: directory '$folder_name' exists but has no SKILL.md"
    fi
done

echo ""

# --------------------------------------------------
# Validate commands
# --------------------------------------------------

echo "=== Validating commands ==="
echo ""

if [[ -d "$COMMANDS_DIR" ]]; then
    for command_file in "$COMMANDS_DIR"/*.md; do
        [[ -f "$command_file" ]] || continue

        command_filename="$(basename "$command_file")"
        command_name="${command_filename%.md}"

        echo "Checking /$command_name..."

        # Command name follows the same naming convention
        if [[ ! "$command_name" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
            echo "  ERROR: command name must contain lowercase letters, numbers, and hyphens only"
            failed=1
        fi

        frontmatter="$(extract_frontmatter "$command_file")"

        if [[ -z "$frontmatter" ]]; then
            echo "  ERROR: frontmatter is missing or malformed"
            failed=1
            continue
        fi

        # description
        if ! echo "$frontmatter" | grep -q '^description:[[:space:]]*[^[:space:]]'; then
            echo "  ERROR: description is missing from frontmatter"
            failed=1
        fi

        # body is not empty
        body="$(extract_body "$command_file" | tr -d '[:space:]')"

        if [[ -z "$body" ]]; then
            echo "  ERROR: command body is empty"
            failed=1
        fi

        # $ARGUMENTS presence
        if ! grep -q '\$ARGUMENTS' "$command_file"; then
            echo "  WARNING: command does not reference \$ARGUMENTS"
        fi

        echo ""
    done
else
    echo "  Commands directory not found."
    echo ""
fi

# --------------------------------------------------
# Validate recommended documentation
# --------------------------------------------------

echo "=== Validating documentation ==="
echo ""

if [[ -d "$DOCS_DIR" ]]; then
    for doc_name in "skill-orchestration-design.md" "skill-routing-matrix.md"; do
        doc_path="$DOCS_DIR/$doc_name"
        echo "Checking $doc_name..."
        if [[ ! -f "$doc_path" ]]; then
            echo "  WARNING: Recommended documentation '$doc_name' is missing"
        fi
        echo ""
    done
else
    echo "  WARNING: Docs directory does not exist."
    echo ""
fi

# --------------------------------------------------
# Validate TypeScript custom tool wrappers
# --------------------------------------------------

echo "=== Validating TypeScript custom tool wrappers ==="
echo ""

if [[ -d "$TOOLS_DIR" ]]; then
    for tool_file in "$TOOLS_DIR"/*.ts; do
        [[ -f "$tool_file" ]] || continue

        tool_filename="$(basename "$tool_file")"
        tool_name="${tool_filename%.ts}"

        echo "Checking $tool_filename..."

        # Check filename: lowercase with underscores only
        if [[ ! "$tool_name" =~ ^[a-z][a-z0-9_]*$ ]]; then
            echo "  ERROR: filename must be lowercase with underscores only"
            failed=1
        fi

        # Check for built-in name collision
        case "$tool_name" in
            bash|read|write|edit|grep|glob)
                echo "  WARNING: '$tool_name' collides with a likely built-in tool name"
                ;;
        esac

        # Check for required import
        if ! grep -q 'import { tool } from "@opencode-ai/plugin"' "$tool_file"; then
            echo "  ERROR: missing import of tool from @opencode-ai/plugin"
            failed=1
        fi

        # Check for required export
        if ! grep -q "export default tool(" "$tool_file"; then
            echo "  ERROR: missing export default tool(...)"
            failed=1
        fi

        # Check for required properties
        if ! grep -qE '^\s*description\s*:' "$tool_file"; then
            echo "  ERROR: missing description property"
            failed=1
        fi

        if ! grep -q '^[[:space:]]*args:' "$tool_file"; then
            echo "  ERROR: missing args property"
            failed=1
        fi

        if ! grep -qE '^\s*(async\s+)?execute\s*[:(]' "$tool_file"; then
            echo "  ERROR: missing execute property"
            failed=1
        fi

        # Check file is non-empty
        if [[ ! -s "$tool_file" ]]; then
            echo "  ERROR: file is empty"
            failed=1
        fi

        echo ""
    done
else
    echo "  WARNING: opencode-tools directory does not exist."
    echo ""
fi

# --------------------------------------------------
# Validate Python tool backend scripts
# --------------------------------------------------

echo "=== Validating Python tool backend scripts ==="
echo ""

if [[ -d "$PYTHON_TOOLS_DIR" ]]; then
    for py_file in repo_map.py diff_summarizer.py context_compressor.py prompt_budget.py; do
        py_path="$PYTHON_TOOLS_DIR/$py_file"
        if [[ ! -f "$py_path" ]]; then
            echo "  ERROR: required Python tool script '$py_file' is missing"
            failed=1
        elif [[ ! -s "$py_path" ]]; then
            echo "  ERROR: '$py_file' is empty"
            failed=1
        else
            echo "  OK: $py_file"
        fi
    done
else
    echo "  WARNING: tools directory does not exist."
fi

echo ""

# --------------------------------------------------
# Summary
# --------------------------------------------------

if [[ "$failed" -ne 0 ]]; then
    echo "Validation failed."
    exit 1
fi

echo "All validations passed."