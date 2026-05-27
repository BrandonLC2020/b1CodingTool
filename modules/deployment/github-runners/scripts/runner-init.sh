#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEMPLATE_DIR="$(dirname "$SCRIPT_DIR")/templates"
TARGET_BASE="${PWD}/infrastructure/runners"

force=false
if [[ "${1:-}" == "--force" ]]; then
    force=true
fi

echo "=== Self-Hosted Runner Setup ==="
echo "Select deployment style:"
echo "  1) systemd unit (long-lived runner on a Linux host)"
echo "  2) docker-compose (containerized runner, ephemeral)"
echo "  3) ephemeral workflow example (just-in-time runners)"
read -p "Selection (1, 2, or 3): " CHOICE

copy_template() {
    local src="$1"
    local dst="$2"
    mkdir -p "$(dirname "$dst")"
    if [ -f "$dst" ] && [ "$force" != "true" ]; then
        read -p "$dst already exists. Overwrite? (y/N) " OW
        [[ ! "$OW" =~ ^[Yy]$ ]] && { echo "Skipping."; return; }
    fi
    if [ ! -f "$src" ]; then
        echo "ERROR: template not found at $src" >&2
        exit 1
    fi
    cp "$src" "$dst"
    echo "Created $dst"
}

case "$CHOICE" in
    1)
        copy_template "$TEMPLATE_DIR/runner-systemd.service.tmpl" "$TARGET_BASE/systemd/github-runner.service"
        echo "Edit the service file to set the runner's user, URL, and registration token, then:"
        echo "  sudo cp $TARGET_BASE/systemd/github-runner.service /etc/systemd/system/"
        echo "  sudo systemctl daemon-reload && sudo systemctl enable --now github-runner"
        ;;
    2)
        copy_template "$TEMPLATE_DIR/runner-docker-compose.yml.tmpl" "$TARGET_BASE/docker/docker-compose.yml"
        echo "Set RUNNER_TOKEN and REPO_URL in your environment, then: docker compose up -d"
        ;;
    3)
        copy_template "$TEMPLATE_DIR/ephemeral-runner-workflow.yml.tmpl" "${PWD}/.github/workflows/ephemeral-runner-example.yml"
        ;;
    *)
        echo "Invalid selection." >&2
        exit 1
        ;;
esac

echo "Done."
