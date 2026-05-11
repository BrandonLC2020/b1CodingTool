---
name: call-codex-within-claude
description: Execute tasks by delegating work to Codex. Use this when you are Claude Code and need to run Codex.
---

# Call Codex within Claude Code

This skill allows Claude Code to delegate tasks to Codex via the shell.

## Instructions

To call Codex, use your `Bash` tool to execute the `codex` CLI.
**Important Authentication Note:** To avoid conflicting with the user's default consumer subscription authentication, this skill uses a dedicated API key for automation managed via a `.env` file.

1. **Formulate the Prompt:** Create a clear, comprehensive prompt for Codex.
2. **Execute Codex:** Source the local `.env` file to load the automation keys, then use inline environment variable assignment to pass the API key.
   ```bash
   [ -f .env ] && source .env; OPENAI_API_KEY="$OPENAI_API_KEY_AUTOMATION" codex "Your comprehensive prompt here"
   ```
   *If the variable is not set, ask the user to provide their dedicated automation API key in the `.env` file.*
3. **Review Output:** Wait for the command to complete and review the output.
