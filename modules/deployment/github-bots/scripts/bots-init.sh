#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_DIR="$(dirname "$SCRIPT_DIR")/templates"
GH_DIR="${PWD}/.github"
WORKFLOWS_DIR="${GH_DIR}/workflows"

force=false
if [[ "${1:-}" == "--force" ]]; then
    force=true
fi

echo "=== GitHub Bots Setup ==="
echo "Select a bot to scaffold:"
echo "  1) Dependabot (.github/dependabot.yml)"
echo "  2) release-please (.github/workflows/release-please.yml)"
echo "  3) Triage labeler (.github/workflows/triage-labeler.yml + .github/labeler.yml)"
echo "  4) All three"
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

add_dependabot() {
    copy_template "$TEMPLATE_DIR/dependabot.yml.tmpl" "$GH_DIR/dependabot.yml"
}
add_release_please() {
    copy_template "$TEMPLATE_DIR/release-please.yml.tmpl" "$WORKFLOWS_DIR/release-please.yml"
}
add_triage() {
    copy_template "$TEMPLATE_DIR/triage-labeler.yml.tmpl" "$WORKFLOWS_DIR/triage-labeler.yml"
    # Also drop a starter labeler.yml the workflow expects
    if [ ! -f "$GH_DIR/labeler.yml" ] || [ "$force" = "true" ]; then
        cat > "$GH_DIR/labeler.yml" <<'EOF'
# actions/labeler v5 config. Edit to match your repo's areas.
area:docs:
  - changed-files:
      - any-glob-to-any-file: ['docs/**', '**/*.md']
area:tests:
  - changed-files:
      - any-glob-to-any-file: ['tests/**']
EOF
        echo "Created $GH_DIR/labeler.yml"
    fi
}

case "$CHOICE" in
    1) add_dependabot ;;
    2) add_release_please ;;
    3) add_triage ;;
    4) add_dependabot; add_release_please; add_triage ;;
    *) echo "Invalid selection." >&2; exit 1 ;;
esac

echo "Done."
