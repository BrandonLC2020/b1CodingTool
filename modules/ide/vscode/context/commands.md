# Visual Studio Code: Commands

While b1CodingTool manages global context, these commands are recommended for agents to help manage the VS Code workspace directly.

## Recommended Agent Commands
- **Setup Workspace:** Ensure the `.vscode` directory and standard files exist.
- **Manage Extensions:** Add or remove extension recommendations in `.vscode/extensions.json`.
- **Manage Settings:** Update workspace-specific settings in `.vscode/settings.json`.

## Integration with b1
When the `vscode` module is installed, the following actions are available:
- `b1 install vscode`: Automatically initializes the `.vscode` directory with project-standard templates.
- `b1 pair`: Ensures that VS Code-specific guidelines are synchronized across all agent-specific instruction files (`CLAUDE.md`, `GEMINI.md`, etc.).
