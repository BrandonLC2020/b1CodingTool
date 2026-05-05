#!/bin/bash
set -e

# This script is executed from the project root.
# The script itself is located in .agent/modules/framework/flutter/scripts/post-install.sh

echo "Initializing Flutter project environment..."

if [ -f "pubspec.yaml" ]; then
    echo "Found pubspec.yaml. Running 'flutter pub get'..."
    flutter pub get
else
    echo "Warning: No pubspec.yaml found at project root. Skipping 'flutter pub get'."
fi

echo "Flutter module setup complete."
