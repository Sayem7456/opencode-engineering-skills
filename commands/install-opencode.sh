COMMAND_SOURCE_DIR="$REPO_ROOT/commands"
COMMAND_TARGET_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/opencode/commands"

if [[ -d "$COMMAND_SOURCE_DIR" ]]; then
    mkdir -p "$COMMAND_TARGET_DIR"

    for command_file in "$COMMAND_SOURCE_DIR"/*.md; do
        [[ -f "$command_file" ]] || continue

        command_name="$(basename "$command_file")"
        target="$COMMAND_TARGET_DIR/$command_name"

        if [[ -L "$target" || -e "$target" ]]; then
            rm -f "$target"
        fi

        ln -s "$command_file" "$target"
        echo "Installed command: /${command_name%.md}"
    done
fi