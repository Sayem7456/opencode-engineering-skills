#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_DIR="$ROOT/skills"
COMMANDS_DIR="$ROOT/commands"

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
# Summary
# --------------------------------------------------

if [[ "$failed" -ne 0 ]]; then
    echo "Validation failed."
    exit 1
fi

echo "All validations passed."