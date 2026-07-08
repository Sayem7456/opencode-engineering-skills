#!/usr/bin/env bash

set -euo pipefail

REPO_SOURCE="Sayem7456/opencode-engineering-skills"
AGENT="opencode"
INSTALL_SCOPE="--global"

PLANNED_SKILLS="llm-app-security prompt-injection-defense rag-quality-review ai-evaluation model-serving-production"

# --------------------------------------------------
# Usage
# --------------------------------------------------

usage() {
    echo "Usage: $(basename "$0") <pack-name> [--yes]"
    echo ""
    echo "Available packs:"
    echo "  backend"
    echo "  frontend"
    echo "  review"
    echo "  production"
    echo "  ai-engineer"
    echo "  fullstack"
    echo ""
    echo "Examples:"
    echo "  $(basename "$0") backend"
    echo "  $(basename "$0") fullstack --yes"
    echo ""
    echo "Note: This installs skills only."
    echo "      Slash commands require: scripts/install-opencode.sh"
    exit 1
}

# --------------------------------------------------
# Resolve pack name to skill list
# --------------------------------------------------

resolve_pack() {
    local pack="$1"

    case "$pack" in
        backend)
            echo "python-quality fastapi-backend sqlalchemy-postgres testing-and-debugging security-review"
            ;;
        frontend)
            echo "nextjs-frontend ui-ux-design testing-and-debugging code-review security-review"
            ;;
        review)
            echo "code-review security-review testing-and-debugging production-readiness"
            ;;
        production)
            echo "production-readiness security-review sqlalchemy-postgres testing-and-debugging token-saver context-engineering"
            ;;
        ai-engineer)
            echo "python-quality testing-and-debugging token-saver context-engineering structured-output-reliability llm-app-security"
            ;;
        fullstack)
            echo "python-quality fastapi-backend sqlalchemy-postgres nextjs-frontend ui-ux-design testing-and-debugging security-review code-review production-readiness token-saver context-engineering repository-navigation"
            ;;
        *)
            echo ""
            ;;
    esac
}

# --------------------------------------------------
# Parse arguments
# --------------------------------------------------

PACK_NAME=""
YES_FLAG=""

for arg in "$@"; do
    if [[ "$arg" == "--yes" ]]; then
        YES_FLAG="--yes"
    elif [[ -z "$PACK_NAME" ]]; then
        PACK_NAME="$arg"
    else
        echo "Error: unexpected argument '$arg'" >&2
        usage
    fi
done

if [[ -z "$PACK_NAME" ]]; then
    usage
fi

# --------------------------------------------------
# Validate pack name
# --------------------------------------------------

SKILLS="$(resolve_pack "$PACK_NAME")"

if [[ -z "$SKILLS" ]]; then
    echo "Error: unknown pack '$PACK_NAME'" >&2
    echo "Valid packs: backend frontend review production ai-engineer fullstack" >&2
    exit 1
fi

# --------------------------------------------------
# Handle ai-engineer planned skills notice
# --------------------------------------------------

if [[ "$PACK_NAME" == "ai-engineer" ]]; then
    echo "Note: ai-engineer pack includes only currently available skills."
    echo "  The following skills are planned and not yet available:"
    for planned in $PLANNED_SKILLS; do
        echo "    - $planned"
    done
    echo ""
fi

# --------------------------------------------------
# Build and run npx command
# --------------------------------------------------

NPX_CMD=("npx" "skills" "add" "$REPO_SOURCE")

for skill in $SKILLS; do
    NPX_CMD+=("--skill" "$skill")
done

NPX_CMD+=("--agent" "$AGENT" "$INSTALL_SCOPE")

if [[ -n "$YES_FLAG" ]]; then
    NPX_CMD+=("$YES_FLAG")
fi

echo "Running: ${NPX_CMD[*]}"
echo ""
exec "${NPX_CMD[@]}"
