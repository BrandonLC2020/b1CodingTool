#!/bin/bash
# post-install.sh: Resolve Swift dependencies after module install

if [ -f "Package.swift" ]; then
    echo "📦 Package.swift found. Resolving dependencies..."
    swift package resolve
else
    echo "ℹ️ No Package.swift found in root. Skipping resolution."
fi
