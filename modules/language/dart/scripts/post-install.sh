#!/bin/bash
set -e

# modules/language/dart/scripts/post-install.sh
# This script runs from the project root after module installation.

if [ -f "pubspec.yaml" ]; then
    echo "Dart project detected. Resolving dependencies..."
    if command -v flutter &> /dev/null && grep -q '^[[:space:]]*sdk:[[:space:]]*flutter' pubspec.yaml; then
        flutter pub get
    else
        dart pub get
    fi
fi
