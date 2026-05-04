#!/bin/bash
set -e

# This script is executed from the project root.
# The script itself is located in .agent/modules/antigravity/scripts/post-install.sh

MODULE_DIR=".agent/modules/antigravity"
IGNORE_FILE=".antigravityignore"

echo "Setting up Antigravity configurations..."

# Create .antigravityignore if it doesn't exist
if [ ! -f "$IGNORE_FILE" ]; then
    if [ -f "$MODULE_DIR/templates/.antigravityignore" ]; then
        cp "$MODULE_DIR/templates/.antigravityignore" "$IGNORE_FILE"
        echo "Initialized $IGNORE_FILE from template."
    else
        echo "Warning: Template $MODULE_DIR/templates/.antigravityignore not found."
    fi
else
    echo "$IGNORE_FILE already exists, skipping."
fi

echo "Antigravity setup complete."
