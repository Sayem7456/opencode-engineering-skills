#!/usr/bin/env bash

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

SKILLS_SOURCE_DIR="$REPO_ROOT/skills"
COMMANDS_SOURCE_DIR="$REPO_ROOT/commands"
DOCS_SOURCE_DIR="$REPO_ROOT/docs"

OPENCODE_CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/opencode"
SKILLS_TARGET_DIR="$OPENCODE_CONFIG_DIR/skills"
COMMANDS_TARGET_DIR="$OPENCODE_CONFIG_DIR/commands"
DOCS_TARGET_DIR="$OPENCODE_CONFIG_DIR/docs"

installed_skills=0
installed_commands=0
installed_docs=0

if [[ ! -d "$SKILLS_SOURCE_DIR" ]]; then
    echo "Error: skills directory not found: $SKILLS_SOURCE_DIR" >&2
    exit 1
fi

mkdir -p "$SKILLS_TARGET_DIR"

for skill_dir in "$SKILLS_SOURCE_DIR"/*; do
    [[ -d "$skill_dir" ]] || continue

    skill_name="$(basename "$skill_dir")"
    skill_file="$skill_dir/SKILL.md"

    if [[ ! -f "$skill_file" ]]; then
        echo "Skipping skill $skill_name: SKILL.md not found"
        continue
    fi

    target="$SKILLS_TARGET_DIR/$skill_name"

    if [[ -L "$target" ]]; then
        echo "Replacing existing symlink: $skill_name"
        rm "$target"
    elif [[ -e "$target" ]]; then
        echo "Warning: $skill_name already exists and is not a symlink. Skipping."
        continue
    fi

    ln -s "$skill_dir" "$target"

    echo "Installed skill: $skill_name"
    installed_skills=$((installed_skills + 1))
done

if [[ -d "$COMMANDS_SOURCE_DIR" ]]; then
    mkdir -p "$COMMANDS_TARGET_DIR"

    for command_file in "$COMMANDS_SOURCE_DIR"/*.md; do
        [[ -f "$command_file" ]] || continue

        command_filename="$(basename "$command_file")"
        command_name="${command_filename%.md}"
        target="$COMMANDS_TARGET_DIR/$command_filename"

        if [[ -L "$target" ]]; then
            echo "Replacing existing symlink: /$command_name"
            rm "$target"
        elif [[ -e "$target" ]]; then
            echo "Warning: /$command_name already exists and is not a symlink. Skipping."
            continue
        fi

        ln -s "$command_file" "$target"

        echo "Installed command: /$command_name"
        installed_commands=$((installed_commands + 1))
    done
else
    echo "Commands directory not found. Skipping command installation."
fi

# --------------------------------------------------
# Install documentation
# --------------------------------------------------

if [[ -d "$DOCS_SOURCE_DIR" ]]; then
    mkdir -p "$DOCS_TARGET_DIR"

    for doc_file in "$DOCS_SOURCE_DIR"/*.md; do
        [[ -f "$doc_file" ]] || continue

        doc_filename="$(basename "$doc_file")"
        target="$DOCS_TARGET_DIR/$doc_filename"

        if [[ -L "$target" ]]; then
            echo "Replacing existing symlink: docs/$doc_filename"
            rm "$target"
        elif [[ -e "$target" ]]; then
            echo "Warning: docs/$doc_filename already exists and is not a symlink. Skipping."
            continue
        fi

        ln -s "$doc_file" "$target"

        echo "Installed doc: $doc_filename"
        installed_docs=$((installed_docs + 1))
    done
fi

echo
echo "Installation completed."
echo
echo "Skills installed:   $installed_skills"
echo "Commands installed: $installed_commands"
echo "Docs installed:     $installed_docs"
echo
echo "Skills location:"
echo "$SKILLS_TARGET_DIR"
echo
echo "Commands location:"
echo "$COMMANDS_TARGET_DIR"
echo
echo "Docs location:"
echo "$DOCS_TARGET_DIR"
echo
echo "Restart OpenCode or open a new session."
