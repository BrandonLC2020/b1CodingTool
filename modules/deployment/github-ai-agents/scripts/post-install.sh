#!/bin/bash
set -e

AGENTS_DIR=".github/agents"

echo "Initializing GitHub AI agents structure..."

if [ ! -d "$AGENTS_DIR" ]; then
    mkdir -p "$AGENTS_DIR"
    echo "Created $AGENTS_DIR for reusable prompt files."
else
    echo "$AGENTS_DIR already exists, skipping creation."
fi

echo "github-ai-agents module setup complete."
