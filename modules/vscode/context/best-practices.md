# Visual Studio Code: Best Practices

## Performance
- **Extension Leanliness:** Only enable necessary extensions for the current project. Use Workspace Recommendations to manage extensions per project.
- **Search Exclusions:** Use `files.exclude` and `search.exclude` in `.vscode/settings.json` to keep search and file navigation fast by ignoring `node_modules`, `venv`, `build`, etc.

## Workflow
- **Auto Save:** Use `files.autoSave: "onFocusChange"` or `"afterDelay"` to minimize manual save overhead.
- **Format on Save:** Enable `editor.formatOnSave` to ensure consistent code styling without manual intervention.
- **Multi-root Workspaces:** Use `.code-workspace` files when working on multiple related repositories (e.g., frontend and backend) simultaneously.

## Debugging
- **Launch Configurations:** Always commit `.vscode/launch.json` to the repository if it contains project-wide debugging configurations.
- **Variable Substitution:** Use `${workspaceFolder}`, `${file}`, and other predefined variables in launch configurations for portability.

## Extensions
- **Recommendations:** Use `.vscode/extensions.json` to recommend essential extensions for the project. This ensures a consistent developer experience for all team members.
