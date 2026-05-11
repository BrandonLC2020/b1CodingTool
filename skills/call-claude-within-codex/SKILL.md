---
name: call-claude-within-codex
description: Execute tasks by delegating work to Claude Code. Use this when you are Codex and need to run Claude Code.
---

# Call Claude Code within Codex

This skill allows Codex to delegate tasks to Claude Code.

## Instructions

To call Claude Code, use your native shell tool to execute the `claude` CLI.
**Important Authentication Note:** To avoid conflicting with the user's default consumer subscription authentication, this skill uses a dedicated API key for automation managed via a `.env` file.

1. **Formulate the Prompt:** Create a clear, comprehensive prompt for Claude Code.
2. **Execute Claude Code:** Source the local `.env` file to load the automation keys, then use inline environment variable assignment to pass the API key.
   ```bash
   [ -f .env ] && source .env; ANTHROPIC_API_KEY="$CLAUDE_API_KEY_AUTOMATION" claude -p "Your comprehensive prompt here"
   ```
   *If the variable is not set, ask the user to provide their dedicated automation API key in the `.env` file.*
3. **Review Output:** Wait for the command to complete and review the output.
