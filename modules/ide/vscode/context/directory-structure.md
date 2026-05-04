# Visual Studio Code: Directory Structure

## Workspace Metadata
```
.vscode/
├── settings.json       # Workspace settings (overrides user settings)
├── extensions.json     # Recommended extensions for the project
├── launch.json         # Debugging configurations
├── tasks.json          # Task definitions (build, test, etc.)
└── snippets/           # Project-specific code snippets
    └── python.json
```

## Global vs. Workspace
- **.vscode/**: Contains settings that apply ONLY to this workspace. This directory SHOULD be committed to version control.
- **.gitignore**: Ensure that private/local VS Code files (like `*.code-workspace` if specific to your machine) are ignored, but `.vscode/*.json` should generally be tracked.
