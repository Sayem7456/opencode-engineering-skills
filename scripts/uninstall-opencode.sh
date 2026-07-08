#!/usr/bin/env bash

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

SKILLS_SOURCE_DIR="$REPO_ROOT/skills"
COMMANDS_SOURCE_DIR="$REPO_ROOT/commands"

OPENCODE_CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/opencode"
SKILLS_TARGET_DIR="$OPENCODE_CONFIG_DIR/skills"
COMMANDS_TARGET_DIR="$OPENCODE_CONFIG_DIR/commands"

removed_skills=0
removed_commands=0

resolve_path() {
    local path="$1"

    python3 - "$path" <<'PY'
import os
import sys

print(os.path.realpath(sys.argv[1]))
PY
}

# --------------------------------------------------
# Remove skills
# --------------------------------------------------

if [[ -d "$SKILLS_SOURCE_DIR" ]]; then
    for skill_dir in "$SKILLS_SOURCE_DIR"/*; do
        [[ -d "$skill_dir" ]] || continue

        skill_name="$(basename "$skill_dir")"
        target="$SKILLS_TARGET_DIR/$skill_name"

        if [[ ! -L "$target" ]]; then
            echo "Skipped skill $skill_name: not installed by this symlink installer"
            continue
        fi

        resolved_target="$(resolve_path "$target")"
        resolved_source="$(resolve_path "$skill_dir")"

        if [[ "$resolved_target" == "$resolved_source" ]]; then
            rm "$target"
            echo "Removed skill: $skill_name"
            removed_skills=$((removed_skills + 1))
        else
            echo "Skipped skill $skill_name: symlink belongs to another source"
        fi
    done
else
    echo "Skills source directory not found. Skipping skill removal."
fi

# --------------------------------------------------
# Remove slash commands
# --------------------------------------------------

if [[ -d "$COMMANDS_SOURCE_DIR" ]]; then
    for command_file in "$COMMANDS_SOURCE_DIR"/*.md; do
        [[ -f "$command_file" ]] || continue

        command_filename="$(basename "$command_file")"
        command_name="${command_filename%.md}"
        target="$COMMANDS_TARGET_DIR/$command_filename"

        if [[ ! -L "$target" ]]; then
            echo "Skipped command /$command_name: not installed by this symlink installer"
            continue
        fi

        resolved_target="$(resolve_path "$target")"
        resolved_source="$(resolve_path "$command_file")"

        if [[ "$resolved_target" == "$resolved_source" ]]; then
            rm "$target"
            echo "Removed command: /$command_name"
            removed_commands=$((removed_commands + 1))
        else
            echo "Skipped command /$command_name: symlink belongs to another source"
        fi
    done
else
    echo "Commands source directory not found. Skipping command removal."
fi

# --------------------------------------------------
# Remove empty directories
# --------------------------------------------------

if [[ -d "$SKILLS_TARGET_DIR" ]] && [[ -z "$(ls -A "$SKILLS_TARGET_DIR")" ]]; then
    rmdir "$SKILLS_TARGET_DIR"
    echo "Removed empty directory: $SKILLS_TARGET_DIR"
fi

if [[ -d "$COMMANDS_TARGET_DIR" ]] && [[ -z "$(ls -A "$COMMANDS_TARGET_DIR")" ]]; then
    rmdir "$COMMANDS_TARGET_DIR"
    echo "Removed empty directory: $COMMANDS_TARGET_DIR"
fi

echo
echo "Uninstallation completed."
echo
echo "Skills removed:  $removed_skills"
echo "Commands removed: $removed_commands"
echo
echo "Only symlinks created from this repository were removed."
