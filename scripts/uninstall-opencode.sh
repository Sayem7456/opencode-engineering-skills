#!/usr/bin/env bash

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

SKILLS_SOURCE_DIR="$REPO_ROOT/skills"
COMMANDS_SOURCE_DIR="$REPO_ROOT/commands"
DOCS_SOURCE_DIR="$REPO_ROOT/docs"
TOOLS_SOURCE_DIR="$REPO_ROOT/opencode-tools"

OPENCODE_CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/opencode"
SKILLS_TARGET_DIR="$OPENCODE_CONFIG_DIR/skills"
COMMANDS_TARGET_DIR="$OPENCODE_CONFIG_DIR/commands"
DOCS_TARGET_DIR="$OPENCODE_CONFIG_DIR/docs"
TOOLS_TARGET_DIR="$OPENCODE_CONFIG_DIR/tools"

removed_skills=0
removed_commands=0
removed_docs=0
removed_tools=0

resolve_path() {
    local path="$1"

    if command -v python3 &>/dev/null; then
        python3 -c "import os; print(os.path.realpath('$path'))"
    elif command -v python &>/dev/null; then
        python -c "import os; print(os.path.realpath('$path'))"
    elif [[ -L "$path" ]]; then
        readlink "$path"
    else
        echo "$path"
    fi
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
# Remove documentation
# --------------------------------------------------

if [[ -d "$DOCS_SOURCE_DIR" ]]; then
    for doc_file in "$DOCS_SOURCE_DIR"/*.md; do
        [[ -f "$doc_file" ]] || continue

        doc_filename="$(basename "$doc_file")"
        target="$DOCS_TARGET_DIR/$doc_filename"

        if [[ ! -L "$target" ]]; then
            echo "Skipped doc $doc_filename: not installed by this symlink installer"
            continue
        fi

        resolved_target="$(resolve_path "$target")"
        resolved_source="$(resolve_path "$doc_file")"

        if [[ "$resolved_target" == "$resolved_source" ]]; then
            rm "$target"
            echo "Removed doc: $doc_filename"
            removed_docs=$((removed_docs + 1))
        else
            echo "Skipped doc $doc_filename: symlink belongs to another source"
        fi
    done
fi

# --------------------------------------------------
# Remove tools
# --------------------------------------------------

if [[ -d "$TOOLS_SOURCE_DIR" ]]; then
    for tool_file in "$TOOLS_SOURCE_DIR"/*.ts; do
        [[ -f "$tool_file" ]] || continue

        tool_filename="$(basename "$tool_file")"
        tool_name="${tool_filename%.ts}"
        target="$TOOLS_TARGET_DIR/$tool_filename"

        if [[ ! -L "$target" ]]; then
            echo "Skipped tool $tool_name: not installed by this symlink installer"
            continue
        fi

        resolved_target="$(resolve_path "$target")"
        resolved_source="$(resolve_path "$tool_file")"

        if [[ "$resolved_target" == "$resolved_source" ]]; then
            rm "$target"
            echo "Removed tool: $tool_name"
            removed_tools=$((removed_tools + 1))
        else
            echo "Skipped tool $tool_name: symlink belongs to another source"
        fi
    done
else
    echo "Tools source directory not found. Skipping tool removal."
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

if [[ -d "$DOCS_TARGET_DIR" ]] && [[ -z "$(ls -A "$DOCS_TARGET_DIR")" ]]; then
    rmdir "$DOCS_TARGET_DIR"
    echo "Removed empty directory: $DOCS_TARGET_DIR"
fi

if [[ -d "$TOOLS_TARGET_DIR" ]] && [[ -z "$(ls -A "$TOOLS_TARGET_DIR")" ]]; then
    rmdir "$TOOLS_TARGET_DIR"
    echo "Removed empty directory: $TOOLS_TARGET_DIR"
fi

echo
echo "Uninstallation completed."
echo
echo "Skills removed:   $removed_skills"
echo "Commands removed: $removed_commands"
echo "Docs removed:     $removed_docs"
echo "Tools removed:    $removed_tools"
echo
echo "Only symlinks created from this repository were removed."
