#!/usr/bin/env bash

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_DIR="$REPO_ROOT/skills"
TARGET_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/opencode/skills"

if [[ ! -d "$SOURCE_DIR" ]]; then
    echo "Error: skills directory not found: $SOURCE_DIR" >&2
    exit 1
fi

mkdir -p "$TARGET_DIR"

installed=0

for skill_dir in "$SOURCE_DIR"/*; do
    [[ -d "$skill_dir" ]] || continue

    skill_name="$(basename "$skill_dir")"
    skill_file="$skill_dir/SKILL.md"

    if [[ ! -f "$skill_file" ]]; then
        echo "Skipping $skill_name: SKILL.md not found"
        continue
    fi

    target="$TARGET_DIR/$skill_name"

    if [[ -L "$target" || -e "$target" ]]; then
        echo "Replacing existing installation: $skill_name"
        rm -rf "$target"
    fi

    ln -s "$skill_dir" "$target"

    echo "Installed: $skill_name"
    installed=$((installed + 1))
done

echo
echo "Installed $installed skills into:"
echo "$TARGET_DIR"
echo
echo "Restart OpenCode to refresh skill discovery."