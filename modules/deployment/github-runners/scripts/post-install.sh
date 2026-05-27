#!/bin/bash
set -e

# This script is executed from the project root.
# Located at .agent/modules/github-runners/scripts/post-install.sh after install.

RUNNERS_DIR="infrastructure/runners"

echo "Initializing self-hosted runner infrastructure structure..."

if [ ! -d "$RUNNERS_DIR" ]; then
    mkdir -p "$RUNNERS_DIR/systemd"
    mkdir -p "$RUNNERS_DIR/docker"
    mkdir -p "$RUNNERS_DIR/arc"
    echo "Created $RUNNERS_DIR directory structure."
else
    echo "$RUNNERS_DIR already exists, skipping creation."
fi

echo "github-runners module setup complete."
