#!/usr/bin/env bash

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SKILLS_DIR="$ROOT/skills"

failed=0

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

    declared_name="$(
        awk '
            BEGIN { in_frontmatter = 0 }
            NR == 1 && $0 == "---" {
                in_frontmatter = 1
                next
            }
            in_frontmatter && $0 == "---" {
                exit
            }
            in_frontmatter && /^name:[[:space:]]*/ {
                sub(/^name:[[:space:]]*/, "")
                gsub(/^["'\'']|["'\'']$/, "")
                print
                exit
            }
        ' "$skill_file"
    )"

    if [[ -z "$declared_name" ]]; then
        echo "  ERROR: name is missing from frontmatter"
        failed=1
    elif [[ "$declared_name" != "$folder_name" ]]; then
        echo "  ERROR: name '$declared_name' does not match folder '$folder_name'"
        failed=1
    fi

    if [[ ! "$folder_name" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
        echo "  ERROR: invalid skill name"
        failed=1
    fi

    if ! grep -q '^description:[[:space:]]*[^[:space:]]' "$skill_file"; then
        echo "  ERROR: description is missing"
        failed=1
    fi
done

if [[ "$failed" -ne 0 ]]; then
    echo
    echo "Skill validation failed."
    exit 1
fi

echo
echo "All skills are valid."