#!/usr/bin/env bash

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="$REPO_ROOT/skills"
TARGET_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills"

removed=0

for skill_dir in "$SOURCE_DIR"/*; do
    [[ -d "$skill_dir" ]] || continue

    skill_name="$(basename "$skill_dir")"
    target="$TARGET_DIR/$skill_name"

    if [[ -L "$target" ]]; then
        resolved_target="$(readlink -f "$target" 2>/dev/null || true)"
        resolved_source="$(readlink -f "$skill_dir" 2>/dev/null || true)"

        if [[ "$resolved_target" == "$resolved_source" ]]; then
            rm "$target"
            echo "Removed: $skill_name"
            removed=$((removed + 1))
        else
            echo "Skipped $skill_name: symlink belongs to another source"
        fi
    else
        echo "Skipped $skill_name: not installed by symlink"
    fi
done

echo
echo "Removed $removed skills."