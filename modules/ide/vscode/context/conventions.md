# Visual Studio Code: Conventions

## File Naming
- **Settings:** Always use `.vscode/settings.json`.
- **Extensions:** Always use `.vscode/extensions.json`.
- **Launch:** Always use `.vscode/launch.json`.
- **Tasks:** Always use `.vscode/tasks.json`.

## Code Style
- **Indentation:** Prefer spaces over tabs. Default to 2 or 4 spaces depending on the language module guidelines.
- **Line Length:** Adhere to the `editor.rulers` defined in the workspace settings.
- **Trailing Whitespace:** Enable `files.trimTrailingWhitespace` to keep files clean.
- **Final Newline:** Enable `files.insertFinalNewline` for POSIX compliance.

## Keybindings
- **Conflicts:** Avoid overriding core VS Code keybindings unless essential for productivity.
- **Extensions:** Use `when` clauses in keybindings to scope them to relevant file types or contexts.

## Terminal
- **Shell:** Use a consistent shell across the team (e.g., `zsh` or `bash` on macOS/Linux).
- **Automation:** Use `.vscode/tasks.json` to define common terminal-based workflows like builds, tests, or linting.
