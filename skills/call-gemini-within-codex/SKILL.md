---
name: call-gemini-within-codex
description: Execute tasks by delegating work to Gemini CLI. Use this when you are Codex and need to run Gemini CLI.
---

# Call Gemini CLI within Codex

This skill allows Codex to delegate tasks to Gemini CLI.

## Instructions

To call Gemini CLI, use your native shell tool to execute the `gemini` CLI.
**Important Authentication Note:** To avoid conflicting with the user's default consumer subscription authentication, this skill uses a dedicated API key for automation managed via a `.env` file.

1. **Formulate the Prompt:** Create a clear, comprehensive prompt for Gemini CLI.
2. **Execute Gemini CLI:** Source the local `.env` file to load the automation keys, then use inline environment variable assignment to pass the API key.
   ```bash
   [ -f .env ] && source .env; GEMINI_API_KEY="$GEMINI_API_KEY_AUTOMATION" gemini --prompt "Your comprehensive prompt here"
   ```
   *If the variable is not set, ask the user to provide their dedicated automation API key in the `.env` file.*
3. **Review Output:** Wait for the command to complete and review the output.
