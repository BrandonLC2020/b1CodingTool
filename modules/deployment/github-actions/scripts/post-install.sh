#!/bin/bash
set -e

# This script is executed from the project root.
# The script itself is located in .agent/modules/deployment/github-actions/scripts/post-install.sh

GITHUB_DIR=".github/workflows"

echo "Initializing GitHub Actions structure..."

if [ ! -d "$GITHUB_DIR" ]; then
    mkdir -p "$GITHUB_DIR"
    echo "Created $GITHUB_DIR directory."
fi

echo "GitHub Actions module setup complete."
