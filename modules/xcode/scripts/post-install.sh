#!/bin/bash
# post-install.sh: Generate Xcode project via Tuist after module install

if [ -f "Project.swift" ]; then
    echo "🏗️ Project.swift found. Generating Xcode project via Tuist..."
    if command -v tuist &> /dev/null; then
        tuist generate
    else
        echo "⚠️ Tuist not found. Please install Tuist to generate the project."
    fi
else
    echo "ℹ️ No Project.swift found in root. Skipping project generation."
fi
