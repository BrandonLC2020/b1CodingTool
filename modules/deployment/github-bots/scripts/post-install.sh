#!/bin/bash
set -e

GH_DIR=".github"

echo "Initializing GitHub bots structure..."

if [ ! -d "$GH_DIR" ]; then
    mkdir -p "$GH_DIR/workflows"
    echo "Created $GH_DIR/."
else
    echo "$GH_DIR already exists, skipping creation."
fi

echo "github-bots module setup complete."
