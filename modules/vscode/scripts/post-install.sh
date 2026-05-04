#!/bin/bash
set -e

# This script is executed from the project root.
# The script itself is located in .agent/modules/vscode/scripts/post-install.sh

MODULE_DIR=".agent/modules/vscode"
VSCODE_DIR=".vscode"

echo "Setting up VS Code configurations..."

if [ ! -d "$VSCODE_DIR" ]; then
    mkdir -p "$VSCODE_DIR"
    echo "Created $VSCODE_DIR directory."
fi

# Copy templates if they don't exist
for template in settings.json extensions.json; do
    if [ ! -f "$VSCODE_DIR/$template" ]; then
        if [ -f "$MODULE_DIR/templates/$template" ]; then
            cp "$MODULE_DIR/templates/$template" "$VSCODE_DIR/$template"
            echo "Initialized $VSCODE_DIR/$template from template."
        else
            echo "Warning: Template $MODULE_DIR/templates/$template not found."
        fi
    else
        echo "$VSCODE_DIR/$template already exists, skipping."
    fi
done

echo "VS Code setup complete."
