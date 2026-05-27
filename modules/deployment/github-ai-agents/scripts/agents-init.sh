#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_DIR="$(dirname "$SCRIPT_DIR")/templates"
WORKFLOWS_DIR="${PWD}/.github/workflows"
DOCS_DIR="${PWD}/docs"

force=false
if [[ "${1:-}" == "--force" ]]; then
    force=true
fi

echo "=== GitHub AI Agents Setup ==="
echo "Select an agent to scaffold:"
echo "  1) Claude Code Action (@claude mention handler)"
echo "  2) Codex / generic agent workflow"
echo "  3) PR reviewer (label-gated)"
echo "  4) All three + AGENT_PERMISSIONS.md policy doc"
read -p "Selection (1-4): " CHOICE

mkdir -p "$WORKFLOWS_DIR"

copy_template() {
    local src="$1"
    local dst="$2"
    mkdir -p "$(dirname "$dst")"
    if [ -f "$dst" ] && [ "$force" != "true" ]; then
        read -p "$dst already exists. Overwrite? (y/N) " OW
        [[ ! "$OW" =~ ^[Yy]$ ]] && { echo "Skipping $dst."; return; }
    fi
    if [ ! -f "$src" ]; then
        echo "ERROR: template not found at $src" >&2
        exit 1
    fi
    cp "$src" "$dst"
    echo "Created $dst"
}

add_claude() {
    copy_template "$TEMPLATE_DIR/claude-code-action.yml.tmpl" "$WORKFLOWS_DIR/claude-code.yml"
}
add_codex() {
    copy_template "$TEMPLATE_DIR/codex-action.yml.tmpl" "$WORKFLOWS_DIR/codex-action.yml"
}
add_reviewer() {
    copy_template "$TEMPLATE_DIR/agent-pr-review.yml.tmpl" "$WORKFLOWS_DIR/agent-pr-review.yml"
}
add_policy() {
    mkdir -p "$DOCS_DIR"
    copy_template "$TEMPLATE_DIR/AGENT_PERMISSIONS.md.tmpl" "$DOCS_DIR/AGENT_PERMISSIONS.md"
}

case "$CHOICE" in
    1) add_claude ;;
    2) add_codex ;;
    3) add_reviewer ;;
    4) add_claude; add_codex; add_reviewer; add_policy ;;
    *) echo "Invalid selection." >&2; exit 1 ;;
esac

echo "Done. Remember to set the required secrets (e.g., ANTHROPIC_API_KEY) in repo settings."
