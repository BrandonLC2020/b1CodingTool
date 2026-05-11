---
name: call-codex-within-gemini
description: Execute tasks by delegating work to Codex. Use this when a task requires Codex's specific capabilities, or when requested to "use codex".
---

# Call Codex within Gemini CLI

This skill allows Gemini CLI to delegate tasks to Codex by executing it as a sub-process via the shell.

## Instructions

To call Codex, use your `run_shell_command` tool to execute the `codex` CLI.
**Important Authentication Note:** To avoid conflicting with the user's default consumer subscription authentication, this skill uses a dedicated API key for automation managed via a `.env` file.

1. **Formulate the Prompt:** Create a clear, comprehensive prompt for Codex.
2. **Execute Codex:** Source the local `.env` file to load the automation keys, then use inline environment variable assignment to pass the API key.
   ```bash
   [ -f .env ] && source .env; OPENAI_API_KEY="$OPENAI_API_KEY_AUTOMATION" codex "Your comprehensive prompt here"
   ```
   *If the variable is not set, ask the user to provide their dedicated automation API key in the `.env` file.*
3. **Review Output:** Wait for the command to complete and review the output.
