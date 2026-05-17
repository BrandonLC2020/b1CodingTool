#!/bin/bash
# modules/language/dart/scripts/post-install.sh

if [ -f "pubspec.yaml" ]; then
    echo "Dart project detected. Resolving dependencies..."
    if command -v flutter &> /dev/null && grep -q "sdk: flutter" pubspec.yaml; then
        flutter pub get
    else
        dart pub get
    fi
fi
